"""The base standard's schema: ISO's 6th-edition zip, pinned by content.

The zip is not committed (its licence points at the ISO/IEC Directives and
does not grant redistribution). It is fetched once into a cache outside the
repository and checked against its sha256 every time it is used; a file that
does not match is not used. xlink.xsd and xml.xsd, which the schema imports
over the network, are pinned and resolved locally the same way.
"""
from __future__ import annotations

import hashlib
import io
import os
import urllib.request
import zipfile
from pathlib import Path

ZIP_URL = "https://standards.iso.org/iso-iec/23009/-1/ed-6/en/DASHSchema-6th-Ed.zip"
ZIP_SHA256 = "43b62f3d80a2cfca99d7530e8c092d032bf65736eb1ce176ae6bc8454feb1d28"
W3C = {
    "xlink.xsd": ("https://www.w3.org/XML/2008/06/xlink.xsd",
                  "c83df86c7fdc16eb9c862b83dfb53fc1b1a4bcafd6e1d1217199e0188b82f24a"),
    "xml.xsd": ("https://www.w3.org/2001/xml.xsd",
                "61960fb3131e38022caad5360e2f33a3382578ab3c80cd58bd74320ede61b20c"),
}
SCHEMAS = ("DASH-MPD.xsd", "DASH-MPD-UP.xsd")


class Unavailable(Exception):
    """The pinned schema cannot be had: the run cannot tell (exit 2)."""


def cache_dir() -> Path:
    d = os.environ.get("SGAI_CONFORMANCE_CACHE") or os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "sgai-conformance")
    return Path(d)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _fetch(url: str) -> bytes:
    try:
        return urllib.request.urlopen(url, timeout=60).read()
    except OSError as e:
        raise Unavailable(f"cannot fetch {url}: {e}") from e


def _pinned(path: Path, url: str, sha: str, offline: bool) -> bytes:
    if path.exists():
        data = path.read_bytes()
        if _sha(data) == sha:
            return data
        raise Unavailable(f"{path} does not match its pinned sha256 {sha[:12]}…; delete it to refetch")
    if offline:
        raise Unavailable(f"{path} is not cached and SGAI_CONFORMANCE_OFFLINE is set")
    data = _fetch(url)
    if _sha(data) != sha:
        raise Unavailable(f"{url} served content whose sha256 is {_sha(data)[:12]}…, not the pinned {sha[:12]}…")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def materialise() -> Path:
    """Directory holding DASH-MPD.xsd, its imports and ISO's example MPDs, all
    verified. Raises Unavailable when that cannot be guaranteed."""
    offline = bool(os.environ.get("SGAI_CONFORMANCE_OFFLINE"))
    root = cache_dir()
    raw = _pinned(root / "DASHSchema-6th-Ed.zip", ZIP_URL, ZIP_SHA256, offline)
    out = root / ZIP_SHA256[:12]
    marker = out / ".complete"
    if not marker.exists():
        out.mkdir(parents=True, exist_ok=True)
        (out / "examples").mkdir(exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for info in z.infolist():
                name = info.filename
                if name.startswith("__MACOSX") or name.endswith("/"):
                    continue
                base = os.path.basename(name)
                if base in SCHEMAS:
                    (out / base).write_bytes(z.read(info))
                elif base.endswith(".mpd"):
                    (out / "examples" / base).write_bytes(z.read(info))
        for name, (url, sha) in W3C.items():
            data = _pinned(root / name, url, sha, offline)
            if name == "xlink.xsd":   # resolve its xml.xsd import locally
                data = data.replace(b'schemaLocation="http://www.w3.org/2001/xml.xsd"',
                                    b'schemaLocation="xml.xsd"')
            (out / name).write_bytes(data)
        marker.write_text(ZIP_SHA256 + "\n")
    return out


def examples(out: Path) -> list[Path]:
    return sorted((out / "examples").glob("*.mpd"))
