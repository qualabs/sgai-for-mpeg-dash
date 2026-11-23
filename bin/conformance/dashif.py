"""The DASH-IF Conformance tool as a second, non-blocking auditor (ADR 0053).

It runs the tool's MPD-level modules (Global Module = schematron + XSD, and
IOP MPD) on the given documents and on ISO's 6th-edition examples, and returns
per-document findings in three buckets:

  xsd       the tool's XSD modules. They validate against DASH5th.xsd (and two
            legacy XSDs), i.e. not the 6th edition: reported, and discarded.
  baseline  findings the tool also raises on at least one of ISO's examples:
            the tool's own false-positive baseline, not ours.
  ours      findings raised only on our documents: candidates for a real
            issue, for a person to look at.

A finding is identified by (module, test): the schematron's assertion text,
the IOP check's sentence, or, when the tool aborts on a document instead of
reporting, the exception's location. Messages are kept for reading but are not
part of the identity, because they carry line numbers.

This auditor never decides PASS or FAIL of our checks: it informs. When docker
or the image is not there, run() says so and returns {"ran": False, ...}.

The image is built by bin/dashif/build.sh, pinned in bin/dashif/UPSTREAM, and
run by bin/dashif/run.sh. The baseline is cached per image id and ISO zip
under the same cache directory as the ISO schema (never in the repository).
"""
from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import subprocess
import time
from pathlib import Path

from . import iso

DASHIF_DIR = Path(__file__).resolve().parent.parent / "dashif"
MODULES = ("Global Module", "IOP MPD")
MPD_KINDS = ("mpd", "list-mpd", "sps-mpd")
REPORTED_STATES = ("FAIL", "WARN", "ERROR")
SECONDS_PER_DOCUMENT = 60


def _upstream() -> dict:
    out = {}
    for line in (DASHIF_DIR / "UPSTREAM").read_text().splitlines():
        m = re.match(r"^(\w+)=(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def _image_id(image: str) -> str | None:
    if not shutil.which("docker"):
        return None
    try:
        r = subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", image],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def _scratch() -> Path:
    base = os.environ.get("XDG_RUNTIME_DIR") or os.environ.get("TMPDIR") or "/tmp"
    d = Path(base) / "cto" / f"dashif-{time.strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3)}"
    d.mkdir(parents=True, mode=0o700)
    return d


def _findings(raw: str) -> list[dict]:
    """Every non-PASS, non-SKIP check of one report; a tool abort is one ERROR."""
    if "{" not in raw:
        text = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        where = next((ln for ln in text if ln.startswith("In ") and " line " in ln),
                     next((ln for ln in text if ln.startswith("exit ")), "no output"))
        detail = " ".join(ln for ln in text if not ln.startswith("In "))[:300]
        return [{"module": "tool error", "section": "", "test": where.rstrip(":"),
                 "state": "ERROR", "messages": [detail] if detail else []}]
    data = json.loads(raw[raw.index("{"):])
    out = []

    def walk(node, path):
        if not isinstance(node, dict):
            return
        if "state" in node and "messages" in node:
            if node["state"] in REPORTED_STATES:
                out.append({"module": path[1] if len(path) > 1 else path[0],
                            "section": path[2] if len(path) > 2 else "",
                            "test": path[-1], "state": node["state"],
                            "messages": [str(m)[:300] for m in node["messages"]]})
            return
        for k, v in node.items():
            walk(v, path + [k])

    walk(data, [])
    return out


def _key(f: dict) -> str:
    return f"{f['module']} | {f['test']}"


def _is_xsd(f: dict) -> bool:
    return f["module"].endswith("- XSD")


def _rejects_5th(fs: list[dict]) -> bool:
    """The tool's DASH 5th XSD (module "Global - XSD") reports a FAIL."""
    return any(f["module"] == "Global - XSD" and f["state"] == "FAIL" for f in fs)


def _run_batch(docs: dict[str, str]) -> dict[str, list[dict]]:
    """docs: name -> MPD text. Returns name -> findings."""
    work = _scratch()
    try:
        (work / "in").mkdir()
        (work / "out").mkdir()
        for name, text in docs.items():
            (work / "in" / f"{name}.mpd").write_text(text, encoding="utf-8")
        subprocess.run([str(DASHIF_DIR / "run.sh"), str(work / "in"), str(work / "out")],
                       check=True, capture_output=True, text=True,
                       timeout=60 + SECONDS_PER_DOCUMENT * len(docs))
        out = {}
        for name in docs:
            raw = ""
            for ext in ("json", "err"):   # .err carries a timeout or abort note
                p = work / "out" / f"{name}.{ext}"
                if p.exists() and (ext == "json" or "{" not in raw):
                    raw += p.read_text(encoding="utf-8", errors="replace")
            out[name] = _findings(raw)
        return out
    finally:
        shutil.rmtree(work, ignore_errors=True)


def baseline(isodir: Path, image: str, image_id: str) -> dict[str, list[dict]]:
    """The tool's findings on each of ISO's examples, cached per image and zip."""
    cache = iso.cache_dir() / f"dashif-baseline-{image_id.split(':')[-1][:12]}-{Path(isodir).name}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    docs = {p.stem: p.read_text(encoding="utf-8") for p in iso.examples(Path(isodir))}
    result = _run_batch(docs)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(result, indent=1, ensure_ascii=False))
    return result


def _as_docs(blocks) -> tuple[dict[str, dict], list[str]]:
    docs, skipped = {}, []
    for i, b in enumerate(blocks, 1):
        if isinstance(b, tuple):
            name, text, meta = b[0], b[1], {"ref": b[0]}
        else:
            kind = getattr(b, "kind", "mpd")
            ref = getattr(b, "ref", f"block {i}")
            if kind not in MPD_KINDS:
                skipped.append(f"{ref}: kind {kind}")
                continue
            name = f"xml{getattr(b, 'index', i):03d}"
            text = b.text
            meta = {"ref": ref, "kind": kind, "line": getattr(b, "line", None)}
        docs[name] = {"text": text, **meta}
    return docs, skipped


def run(blocks, isodir) -> dict:
    up = _upstream()
    image = os.environ.get("SGAI_DASHIF_IMAGE") or up.get("image", "")
    tool = {k: up.get(k) for k in ("repo", "tag", "commit")} | {"image": image}
    if not shutil.which("docker"):
        return {"ran": False, "reason": "docker is not on PATH", "tool": tool}
    image_id = _image_id(image)
    if not image_id:
        return {"ran": False, "reason": f"image {image} not available; run bin/dashif/build.sh",
                "tool": tool}
    tool["image_id"] = image_id
    docs, skipped = _as_docs(blocks)
    try:
        base = baseline(Path(isodir), image, image_id)
        ours_raw = _run_batch({n: d["text"] for n, d in docs.items()}) if docs else {}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
        detail = getattr(e, "stderr", "") or str(e)
        return {"ran": False, "reason": f"tool run failed: {str(detail).strip()[:500]}", "tool": tool}

    base_keys: dict[str, list[str]] = {}
    for ex, fs in base.items():
        for f in fs:
            if not _is_xsd(f):
                base_keys.setdefault(_key(f), []).append(ex)

    documents = []
    for name, d in docs.items():
        fs = ours_raw.get(name, [])
        entry = {"name": name, "ref": d["ref"], "kind": d.get("kind"), "line": d.get("line"),
                 "xsd": [], "baseline": [], "ours": []}
        for f in fs:
            f = dict(f, key=_key(f))
            if _is_xsd(f):
                entry["xsd"].append(f)
            elif f["key"] in base_keys:
                entry["baseline"].append(dict(f, iso_examples=sorted(base_keys[f["key"]])))
            else:
                entry["ours"].append(f)
        documents.append(entry)

    return {
        "ran": True,
        "tool": tool,
        "modules": list(MODULES),
        "not_run": "segment-level modules (no GPAC in the image)",
        "discarded": "XSD modules: they validate against DASH5th.xsd and legacy XSDs, not the 6th edition",
        "informs_only": True,
        "skipped_blocks": skipped,
        "baseline": {
            "iso_examples": len(base),
            "keys": {k: sorted(v) for k, v in sorted(base_keys.items())},
            "xsd5_rejected": sorted(ex for ex, fs in base.items() if _rejects_5th(fs)),
            "per_example": base,
        },
        "documents": documents,
        "summary": {
            "documents": len(documents),
            "with_ours": sum(1 for d in documents if d["ours"]),
            "with_baseline_only": sum(1 for d in documents if d["baseline"] and not d["ours"]),
            "xsd5_rejected": sum(1 for d in documents if _rejects_5th(d["xsd"])),
            "ours_keys": sorted({f["key"] for d in documents for f in d["ours"]}),
        },
    }
