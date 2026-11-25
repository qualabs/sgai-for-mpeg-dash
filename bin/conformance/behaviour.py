"""The behaviour battery (phase 11): the reference Player against the
behaviour tests of spec-source/behaviour/ and the UC vectors of
spec-source/scenarios/. Reached only from
`check-dash-conformance.py --behaviour` (ADR 0087).

How a run works:

1. The vectors are selected (`--only`, `--vector`) and expanded into jobs,
   one per vector x variant (the main run, then each variant) x class.
2. Test content: bin/conformance/players.py's ffmpeg content and local
   server, unchanged, with two settings of this process only: CONTENT_S is
   60 s (so 3 s segments divide it as 4 s ones do), and /reference/ serves
   reference-player/src/. The content is kept across runs (CachedContent):
   under ~/.cache/cto-tmp/sgai-behaviour-content/<key>/, mode 0700, where the
   key hashes everything the content is generated from (CONTENT_S, the frame
   rate, the generating code of players.Content, the ffmpeg version), so a
   change to any of them generates it anew. `--clear-content-cache` deletes
   the cache before the run; SGAI_BEHAVIOUR_CONTENT_CACHE=0 generates the
   content in the run's temporary directory, removed with it. Each fixture MPD with media is rewritten (only its
   BaseURLs, as players.rewrite proves) to compute where its segments sit on
   the local server; the page receives the fixture untouched, and the runner
   maps the external media URL onto the local one.
3. bin/players/behaviour.mjs plays each job on the `sgai` adapter (ADR 0081):
   the fixtures at the URLs the vector declares, the `aps` answers as Playwright
   routes (ADR 0079), the viewer's actions at their session times, the class
   as a profile (ADR 0080). It measures; it decides nothing.
4. behaviour_compare.py turns each job into a verdict per expected field.

The session clock (spec-source/scenarios/README.md) is kept by the adapter
(bin/players/adapters/sgai-clock.js) and advances with what is presented, so a
page that plays slower than real time is judged on what it presented, not on
how late. `--clock wall` keeps the earlier clock (wall time since the first
frame), to compare the two; `--cpu-throttle N` slows every page's main thread
N times (CDP), the check that the presentation clock does not judge the
machine. The clock holds through a transition with nothing on screen, up to
a bound; the full log notes each job's longest such hold (a note, not a
verdict).

A vector's fixture is read from the source directory, or, when it is not
there, relative to the vector's own file: a vector kept outside
spec-source/ (reference-player/test/edges/) brings its documents beside it.
A live entry (MPD@type dynamic) is joined at `play_from`: the UTC time the
Player synchronises to is its availabilityStartTime plus `play_from` at
load(), plus the observation span at the fastest rate the actions set (so
that a viewer watching faster than real time stays behind the live edge).

Selection, files and output: see `--help` of check-dash-conformance.py.
"""
from __future__ import annotations

import contextlib
import fcntl
import hashlib
import inspect
import json
import math
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit
from xml.etree import ElementTree as ET

from . import players
from .behaviour_compare import Fixtures, compare, fields_of, same_url
from .model import Outcome, Report, Result

ROOT = Path(__file__).resolve().parent.parent.parent
REFERENCE_SRC = ROOT / "reference-player" / "src"
CONTENT_S = 60
ENTRY_HOST = "https://sgai-entry.invalid/"
JOB_MARGIN_MS = 60000
D = players.D
CACHE_ROOT = Path.home() / ".cache" / "cto-tmp" / "sgai-behaviour-content"


USAGE = """    check-dash-conformance.py --behaviour [--source DIR] [--only ID ...] [--class C ...]
                              [--vector FILE ...] [--concurrency N]
                              [--clock presentation|wall] [--cpu-throttle N]
                              [--reference DIR]
                              [--out-json FILE] [--save-raw FILE] [--replay FILE]
                              [--clear-content-cache] [--log-dir DIR] [--verbose]"""
CLOCKS = ("presentation", "wall")
# How much longer than its observation a job may take in wall time: a page
# playing at a third of real time still finishes.
WALL_FACTOR = {"presentation": 4, "wall": 1}


# --------------------------------------------------------------------------- selection

def discover(source: Path, only: list, vectors: list) -> tuple[list, list]:
    """(vector files, unknown --only tokens). --only takes UC-NN or R<n>.<m>
    (every test of that criterion); --vector adds files as they are."""
    ucs = sorted((source / "scenarios").glob("UC-*.yaml"))
    crit = sorted((source / "behaviour").glob("R*.yaml"))
    files, unknown = [], []
    if only:
        for tok in only:
            if re.fullmatch(r"UC-\d{2}", tok):
                hit = [f for f in ucs if f.stem == tok]
            elif re.fullmatch(r"R\d+\.\d+", tok):
                hit = [f for f in crit if re.fullmatch(re.escape(tok) + r"(-\d+)?", f.stem)]
            else:
                hit = []
            if not hit:
                unknown.append(tok)
            files += [f for f in hit if f not in files]
    elif not vectors:
        files = crit + ucs
    files += [Path(v) for v in vectors]
    return files, unknown


def index_entries(source: Path, only: list) -> list[Result]:
    """The criteria with no test (behaviour/index.yaml), NOT_VERIFIABLE with
    their reason, when the run covers them."""
    import yaml
    p = source / "behaviour" / "index.yaml"
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    out = []
    for e in data.get("not_verifiable", []) or []:
        if only and e.get("criterion") not in only:
            continue
        out.append(Result("criterion", Outcome.NOT_VERIFIABLE, e.get("criterion", "?"),
                          detail=f"no test (behaviour/index.yaml): {e.get('reason', '')}"))
    return out


def vector_name(v: dict, path: Path) -> str:
    """UC-NN for a UC vector (with its file's name when that differs: a copy
    run with --vector), the file's name for a behaviour test."""
    if v.get("uc"):
        return v["uc"] if path.stem == v["uc"] else f"{v['uc']} ({path.stem})"
    return path.stem


def runs_of(v: dict, classes: list) -> list[tuple]:
    """[(variant id or None, class, actions, outcome)]."""
    out = []
    for cls, outcome in (v.get("outcomes") or {}).items():
        if not classes or cls in classes:
            out.append((None, cls, v.get("actions") or [], outcome))
    for var in v.get("variants") or []:
        for cls, outcome in (var.get("outcomes") or {}).items():
            if not classes or cls in classes:
                out.append((var["id"], cls, var.get("actions") or [], outcome))
    return out


def subject_of(name: str, cls: str, variant: str | None) -> str:
    return f"{name} {cls}" + (f" [{variant}]" if variant else "")


# --------------------------------------------------------------------------- documents and media

def content_type(path: str) -> str:
    return {".mpd": "application/dash+xml", ".xml": "application/xml"}.get(Path(path).suffix, "text/plain")


def fixture_file(path: str, source: Path, base: Path | None = None) -> Path:
    """Where a vector's fixture path is read from: under the source directory,
    else (a vector kept outside it) relative to the vector's own directory
    `base`. The source wins when both exist."""
    p = source / path
    if base is not None and not p.exists() and (base / path).exists():
        return base / path
    return p


def fixtures_of(v: dict, source: Path, base: Path | None = None) -> Fixtures:
    """URL of every fixture (the entry: its declared URL, else one under
    ENTRY_HOST) and every text the vector names, the `.http` included. `base`
    is the vector file's directory (see fixture_file)."""
    urls, texts = {}, {}
    read = lambda p: fixture_file(p, source, base).read_text(encoding="utf-8")  # noqa: E731
    for f in v["fixtures"]:
        texts[f["path"]] = read(f["path"])
        if f.get("url"):
            urls[f["path"]] = f["url"]
    if v["entry"] not in urls:
        urls[v["entry"]] = ENTRY_HOST + v["entry"]
        texts.setdefault(v["entry"], read(v["entry"]))
    for outcome in _all_outcomes(v):
        for r in outcome.get("requests") or []:
            if r.get("matches") and r["matches"] not in texts and fixture_file(r["matches"], source, base).exists():
                texts[r["matches"]] = read(r["matches"])
    return Fixtures(urls, texts)


def _all_outcomes(v: dict):
    yield from (v.get("outcomes") or {}).values()
    for var in v.get("variants") or []:
        yield from (var.get("outcomes") or {}).values()


def _is_media_mpd(text: str) -> bool:
    try:
        root = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError:
        return False
    return root.tag == D + "MPD" and root.find(f"{D}Period/{D}AdaptationSet") is not None


def media_prefixes(text: str, url: str) -> list[str]:
    """The external prefixes a document's segments are requested under: its
    absolute BaseURLs, and its own directory when it has none at MPD level."""
    root = ET.fromstring(text.encode("utf-8"))
    out = [b.text.strip() for b in root.iter(D + "BaseURL")
           if b.text and urlsplit(b.text.strip()).scheme]
    top = root.find(D + "BaseURL")
    if top is None or not urlsplit((top.text or "").strip()).scheme:
        out.append(url.rsplit("/", 1)[0] + "/")
    return list(dict.fromkeys(out))


class Media:
    """External media prefix -> local base on the content server, shared by
    every vector of the run."""

    def __init__(self, server, origin: str):
        self.server, self.origin = server, origin
        self.prefix_key: dict[str, str] = {}

    def add(self, text: str, url: str) -> list[dict]:
        prefixes = media_prefixes(text, url)
        key = next((self.prefix_key[p] for p in prefixes if p in self.prefix_key), None)
        if key is None:
            key = f"k{len(set(self.prefix_key.values())) + 1}"
        local = f"{self.origin}/c/{key}/"
        new, _ = players.rewrite(text, local)
        plan = players.plan(new, local)
        for info in list(plan["inits"].values()) + [m[1] for m in plan["medias"]]:
            self.server.content.prepare(info[0], info[1])
        if key in self.server.mpds:
            old = self.server.mpds[key][1]
            plan = {"prefix": old["prefix"], "inits": {**old["inits"], **plan["inits"]},
                    "medias": old["medias"] + plan["medias"]}
        self.server.mpds[key] = (new, plan)
        for p in prefixes:
            self.prefix_key[p] = key
        return [{"prefix": p, "local": local, "key": key} for p in prefixes]

    def segments(self, key: str) -> list[str]:
        """The local paths the content server answers under `key`, as regular
        expressions (the inits exactly, the media templates with their number)."""
        plan = self.server.mpds[key][1]
        return ["^" + re.escape(p) + "$" for p in plan["inits"]] + [rx.pattern for rx, _ in plan["medias"]]

    def is_segment(self, url: str, media_map: list) -> bool:
        """Whether `url` is a segment some fixture MPD of the vector declares
        (its path, under a media prefix, one the content server answers)."""
        for m in media_map:
            if not url.startswith(m["prefix"]):
                continue
            local = urlsplit(m["local"] + url[len(m["prefix"]):].split("?")[0]).path
            if any(re.match(x, local) for x in self.segments(m["key"])):
                return True
        return False


def creatives_of(fx: Fixtures) -> set:
    """Every creative URL the fixtures declare: a `src` (a RenderableAsset)
    or a `background` attribute."""
    out = set()
    for text in fx.texts.values():
        try:
            root = ET.fromstring(text.encode("utf-8"))
        except ET.ParseError:
            continue
        for e in root.iter():
            for k, val in e.attrib.items():
                if k.split("}")[-1] in ("src", "background") and urlsplit(val).scheme in ("http", "https"):
                    out.add(val)
    return out


def live_utc_at_load(entry_text: str, play_from_s: float, span_s: float) -> float | None:
    """For a live entry (MPD@type dynamic with an availabilityStartTime): the
    UTC time, in ms since the epoch, the Player is told it is at load(): the
    availabilityStartTime plus `play_from`, plus `span_s` (the observation
    at the fastest rate the actions set), so that the live edge stays ahead of
    where playback is for the whole observation. None for a static one."""
    try:
        root = ET.fromstring(entry_text.encode("utf-8"))
    except ET.ParseError:
        return None
    if root.tag != D + "MPD" or root.get("type") != "dynamic" or not root.get("availabilityStartTime"):
        return None
    ast = datetime.fromisoformat(root.get("availabilityStartTime").replace("Z", "+00:00"))
    if ast.tzinfo is None:
        ast = ast.replace(tzinfo=timezone.utc)
    return ast.timestamp() * 1000 + (play_from_s + span_s) * 1000


def document_routes(outcome: dict | None, fx: Fixtures, source: Path, base: Path | None = None) -> list:
    """Which fixture answers each document request of a job, as its outcome's
    `requests` declare it: per URL (as the pointing document writes it), the
    `answered_by` of its requests in order, so the runner answers the n-th
    request to that URL with the n-th of them and every later one with the
    last. Requests with no `answered_by` (an `aps` entry answers them) take no
    place in the list. A URL whose fixtures share it with others is thereby
    answered with the class's, the variant's or the n-th one, which is the one
    the comparison attributes (served_fixture). URLs the outcome does not list
    are left to the fixture whose URL it is. The routes are ordered most
    specific first (more declared query parameters), so the runner, which
    takes the first that covers a request, never lets a shorter URL take a
    longer one's request."""
    order: list = []
    answers: dict = {}
    for r in (outcome or {}).get("requests") or []:
        if not r.get("answered_by"):
            continue
        key = next((u for u in order if same_url(u, r["url"])), None)
        if key is None:
            key = r["url"]
            order.append(key)
            answers[key] = []
        answers[key].append(r["answered_by"])
    text = lambda p: fx.texts[p] if p in fx.texts else fixture_file(p, source, base).read_text(encoding="utf-8")  # noqa: E731
    routes = [{"url": u, "answers": [{"path": p, "body": text(p), "contentType": content_type(p)} for p in answers[u]]}
              for u in order]
    routes.sort(key=lambda r: -len(parse_qsl(urlsplit(r["url"]).query, keep_blank_values=True)))
    return routes


def build_job(jid: str, v: dict, fx: Fixtures, media_map: list, cls: str, actions: list, source: Path,
              media: "Media | None" = None, clock: str = "presentation", base: Path | None = None,
              outcome: dict | None = None) -> dict:
    """One job of bin/players/behaviour.mjs. An `aps` entry whose URL is a
    segment of the vector's media or a creative its fixtures declare, and that
    answers no document, is marked `media`: its requests are not document
    requests. `base` is the vector file's directory (fixture_file). `outcome`
    is the job's (its class's, in its variant): which fixture answers each
    document request (document_routes); without it a URL is answered with the
    first fixture declared at it."""
    ts = v["timescale"]
    ms = lambda t: t * 1000.0 / ts  # noqa: E731
    caps = (v.get("player_capabilities") or {}).get(cls)
    creatives = creatives_of(fx)
    aps = []
    for a in v.get("aps") or []:
        is_media = not a.get("document") and (
            any(same_url(a["url"], c) for c in creatives)
            or (media is not None and media.is_segment(a["url"], media_map)))
        aps.append({"url": a["url"], "nth": a.get("nth"), "status": a.get("status"),
                    "path": a.get("document"), "contentType": content_type(a["document"]) if a.get("document") else None,
                    "body": fixture_file(a["document"], source, base).read_text(encoding="utf-8")
                    if a.get("document") else "",
                    "delayMs": ms(a["delay"]) if a.get("delay") else 0, "noResponse": bool(a.get("no_response")),
                    "media": is_media})
    observe = ms(v["observe_until"])
    rate = max([1.0] + [float(a.get("rate") or 1) for a in actions if a.get("do") == "rate"])
    utc = live_utc_at_load(fx.texts[v["entry"]], v["play_from"] / ts, observe / 1000 * rate)
    return {
        "id": jid, "mode": "legacy" if cls == "legacy" else "sgai", "klass": cls,
        "capabilities": caps if cls != "legacy" else None,
        "sendsCapabilities": list(v.get("sends_capabilities") or []) if cls != "legacy" else [],
        "startTime": v["play_from"] / ts if v["play_from"] else None,
        "clock": clock, "utcAtLoad": utc,
        "entryUrl": fx.urls[v["entry"]], "observeMs": observe,
        "wallLimitMs": observe * WALL_FACTOR[clock] + JOB_MARGIN_MS,
        "actions": [{"atMs": ms(a["at"]), "do": a["do"], "to": a["to"] / ts if "to" in a else None,
                     "rate": a.get("rate")} for a in actions],
        "documents": [{"url": u, "path": p, "body": fx.texts[p], "contentType": content_type(p)}
                      for p, u in fx.urls.items()],
        "routes": document_routes(outcome, fx, source, base),
        "aps": aps,
        "media": [{"prefix": m["prefix"], "local": m["local"],
                   "segments": media.segments(m["key"]) if media is not None else []} for m in media_map],
    }


# --------------------------------------------------------------------------- content cache

def content_key() -> str:
    """What the content is generated from: if any of it changes, the cached
    content is not that content."""
    try:
        v = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.splitlines()[0]
    except (OSError, IndexError):
        v = "ffmpeg ?"
    parts = [str(players.CONTENT_S), str(players.FPS), v,
             inspect.getsource(players.Content._master), inspect.getsource(players.Content.prepare)]
    return hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()[:16]


class CachedContent(players.Content):
    """players.Content whose masters and cuts survive the run. A file or a cut
    is reused only when its completion marker exists, written after ffmpeg
    finished; anything else found is partial and is generated again. Two
    runs sharing the cache serialise on a lock file."""

    def __init__(self, root: Path):
        super().__init__(root)
        self.lock = threading.RLock()     # prepare() holds it while the parent's prepare takes it again
        self.hits = 0

    @contextlib.contextmanager
    def _flock(self):
        with open(self.root / ".lock", "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def _master(self, track) -> Path:
        name = f"master-{track[1]}x{track[2]}.mp4" if track[0] == "video" else "master-audio.mp4"
        f, ok = self.root / name, self.root / (name + ".ok")
        if f.exists() and ok.exists():
            return f
        f.unlink(missing_ok=True)
        out = super()._master(track)
        ok.touch()
        return out

    def prepare(self, track, segdur: int):
        with self.lock, self._flock():
            key = (track, segdur)
            if key in self.cut:
                return self.cut[key]
            d = self.root / ("-".join(map(str, track)) + f"-{segdur}s")
            ok = d.with_name(d.name + ".ok")
            if d.is_dir() and ok.exists():
                k = players.CONTENT_S // segdur
                self.cut[key] = (d, k, players._mdhd_timescale((d / "init.mp4").read_bytes()))
                self.hits += 1
                return self.cut[key]
            if d.exists():
                shutil.rmtree(d)
            ok.unlink(missing_ok=True)
            out = super().prepare(track, segdur)
            ok.touch()
            return out


def content_root(tmp: Path, clear: bool) -> tuple[Path, bool]:
    """(where the content goes, whether it is the cache)."""
    if os.environ.get("SGAI_BEHAVIOUR_CONTENT_CACHE", "1") == "0":
        return tmp, False
    if clear and CACHE_ROOT.exists():
        shutil.rmtree(CACHE_ROOT)
    for d in (CACHE_ROOT.parent, CACHE_ROOT):
        d.mkdir(mode=0o700, exist_ok=True)
        os.chmod(d, 0o700)
    root = CACHE_ROOT / content_key()
    root.mkdir(mode=0o700, exist_ok=True)
    return root, True


# --------------------------------------------------------------------------- running

@contextlib.contextmanager
def serving(reference: Path = REFERENCE_SRC):
    """players.py's server and content with this battery's two settings, set
    for the duration of the run and restored after it. `reference` is the
    directory served as /reference/ (the module under test)."""
    saved = (players.CONTENT_S, dict(players.PREFIXES))
    players.CONTENT_S = CONTENT_S
    players.PREFIXES["/reference/"] = reference
    try:
        yield
    finally:
        players.CONTENT_S = saved[0]
        players.PREFIXES.clear()
        players.PREFIXES.update(saved[1])


def _tmpdir() -> Path:
    base = os.environ.get("XDG_RUNTIME_DIR") or os.environ.get("TMPDIR") or "/tmp"
    d = Path(base) / "cto" / f"behaviour-{time.strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3)}"
    d.mkdir(parents=True, mode=0o700)
    return d


def drive(origin: str, jobs: list, concurrency: int, cpu_throttle: float = 1) -> dict:
    """bin/players/behaviour.mjs in its own process group, stopped by the id
    kept here if it overruns."""
    longest = max(j["wallLimitMs"] for j in jobs) / 1000
    timeout = 120 + math.ceil(len(jobs) / max(1, concurrency)) * (longest + 30)
    proc = subprocess.Popen(["node", "behaviour.mjs"], cwd=players.PLAYERS_DIR, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    try:
        out, err = proc.communicate(json.dumps({"origin": origin, "concurrency": concurrency,
                                                "cpuThrottle": cpu_throttle, "jobs": jobs}), timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        raise RuntimeError(f"the behaviour run did not finish in {timeout:.0f} s")
    if proc.returncode != 0:
        raise RuntimeError(f"behaviour.mjs exited {proc.returncode}: {err.strip()[-800:]}")
    return json.loads(out)


def load_vectors(files: list, report: Report) -> list:
    import yaml
    out = []
    for f in files:
        try:
            v = yaml.safe_load(f.read_text(encoding="utf-8"))
            if not isinstance(v, dict) or "outcomes" not in v:
                raise ValueError("not a vector")
            out.append((f, v))
        except (OSError, ValueError, yaml.YAMLError) as e:
            report.cannot.append(f"{f}: cannot be read as a vector ({str(e)[:200]})")
            report.add([Result("vector", Outcome.NOT_VERIFIABLE, str(f), detail=str(e)[:300])])
    return out


def plan_jobs(source: Path, files: list, classes: list, report: Report) -> list:
    """[(job id, path, vector, fx, variant, class, actions, outcome)]. A
    selection that yields no job is a cannot-tell in `report`: zero results
    is also what a battery that never ran looks like."""
    vectors = load_vectors(files, report)
    plans = []
    for path, v in vectors:
        name = vector_name(v, path)
        try:
            fx = fixtures_of(v, source, path.resolve().parent)
        except (OSError, KeyError) as e:
            report.cannot.append(f"{name}: its fixtures cannot be read ({e})")
            continue
        for variant, cls, actions, outcome in runs_of(v, classes):
            plans.append((f"j{len(plans) + 1}", path, v, fx, variant, cls, actions, outcome))
    if not plans:
        report.cannot.append(f"no job selected ({len(files)} vector file(s)"
                             + (f", class {', '.join(classes)}" if classes else "") + ")")
    return plans


def run(source: Path, files: list, classes: list, concurrency: int, report: Report,
        raw_out: dict | None = None, clear_cache: bool = False, clock: str = "presentation",
        cpu_throttle: float = 1, reference: Path = REFERENCE_SRC) -> None:
    plans = plan_jobs(source, files, classes, report)
    if not plans:
        return
    missing = players.missing_prerequisites()
    if missing:
        report.cannot.extend(f"behaviour: {m}" for m in missing)
        for jid, path, v, fx, variant, cls, actions, outcome in plans:
            report.add(_all_nv(v, outcome, subject_of(vector_name(v, path), cls, variant), "; ".join(missing)))
        return
    tmp = _tmpdir()
    server = None
    try:
        with serving(reference):
            croot, cached = content_root(tmp, clear_cache)
            server = players._Server(CachedContent(croot) if cached else players.Content(croot))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            origin = f"http://127.0.0.1:{server.server_address[1]}"
            media = Media(server, origin)
            jobs, runnable, maps = [], [], {}
            t_content = time.monotonic()
            for plan in plans:
                jid, path, v, fx, variant, cls, actions, outcome = plan
                subject = subject_of(vector_name(v, path), cls, variant)
                try:
                    if id(v) not in maps:
                        mm = []
                        for p, u in fx.urls.items():
                            if _is_media_mpd(fx.texts[p]):
                                mm += media.add(fx.texts[p], u)
                        maps[id(v)] = mm
                except (players.Unservable, ValueError, RuntimeError) as e:
                    maps[id(v)] = e
                if isinstance(maps[id(v)], Exception):
                    why = f"cannot serve this vector's media: {maps[id(v)]}"
                    report.cannot.append(f"{subject}: {why}")
                    report.add(_all_nv(v, outcome, subject, why))
                    continue
                jobs.append(build_job(jid, v, fx, maps[id(v)], cls, actions, source, media, clock,
                                      path.resolve().parent, outcome))
                runnable.append(plan)
            content_s = time.monotonic() - t_content
            if not jobs:
                return
            t_run = time.monotonic()
            got = drive(origin, jobs, concurrency, cpu_throttle)
            run_s = time.monotonic() - t_run
        results = {r["id"]: r for r in got["results"]}
        if raw_out is not None:
            raw_out.update({"browser": got.get("browser"), "content_seconds": round(content_s, 1),
                            "run_seconds": round(run_s, 1), "ffmpeg_seconds": server.content.log,
                            "content_cache": str(croot) if cached else None,
                            "content_cache_hits": getattr(server.content, "hits", 0),
                            "source": _rel(source), "clock": clock, "cpu_throttle": cpu_throttle,
                            "reference": _rel(reference)})
            # Every record first, so --save-raw keeps the whole run even when
            # a comparison raises.
            raw_out["jobs"] = [{"vector": _rel(p[1]), "variant": p[4], "class": p[5], "raw": results.get(p[0])}
                               for p in runnable]
        for jid, path, v, fx, variant, cls, actions, outcome in runnable:
            judge(report, path, v, fx, variant, cls, actions, outcome, results.get(jid))
    except RuntimeError as e:
        report.cannot.append(f"behaviour: {e}")
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        shutil.rmtree(tmp, ignore_errors=True)


def judge(report, path, v, fx, variant, cls, actions, outcome, r) -> None:
    subject = subject_of(vector_name(v, path), cls, variant)
    report.__dict__.setdefault("notes", [])
    if not r or not r.get("ok"):
        report.cannot.append(f"{subject}: {(r or {}).get('harnessError', 'no result from the harness')}")
    report.add(compare(v, outcome, r, fx, subject, actions))
    if r and r.get("ok"):
        notes = []
        if r.get("pageErrors"):
            notes.append(f"page errors: {r['pageErrors'][:3]}")
        if r.get("mediaErrors"):
            notes.append(f"media errors: {r['mediaErrors'][:3]}")
        if r.get("timedOut"):
            notes.append("timed out before observe_until")
        log = (r.get("observation") or {}).get("moduleLog", [])
        errs = [e for e in log if e["type"].endswith(":error") or e["type"] == "profile:problem"]
        if errs:
            notes.append(f"module log: {errs[:3]}")
        hold = longest_hold(r.get("observation"))
        if hold:
            notes.append(hold)
        if notes:
            report.notes.append(f"{subject}: " + "; ".join(notes))


def longest_hold(observation: dict | None) -> str | None:
    """The longest transition the session clock held (sgai-clock.js case 4:
    nothing on screen between one presentation and the next), as a note for
    the full log, or None when there was none. A note, never a verdict: the
    bound already turns a long blank into lateness on the clock."""
    holds = ((observation or {}).get("clock") or {}).get("holds") or []
    if not holds:
        return None
    wall, st, held, length = max(holds, key=lambda h: (h[3], h[2]))
    return (f"longest transition hold: {round(length)} ms with nothing on screen at session {round(st)} ms, "
            f"{round(held)} ms held ({len(holds)} transition(s))")


def replay(raw: dict, report: Report) -> None:
    """The comparison again, on a recorded run (--save-raw), without a browser."""
    import yaml
    source = _abs(raw["source"])
    cache = {}
    for j in raw["jobs"]:
        path = _abs(j["vector"])
        if path not in cache:
            v = yaml.safe_load(path.read_text(encoding="utf-8"))
            cache[path] = (v, fixtures_of(v, source, path.parent))
        v, fx = cache[path]
        hit = [(var, cls, a, o) for var, cls, a, o in runs_of(v, [j["class"]]) if var == j["variant"]]
        if not hit:
            report.cannot.append(f"{path}: no outcome for {j['class']} {j['variant']}")
            continue
        variant, cls, actions, outcome = hit[0]
        judge(report, path, v, fx, variant, cls, actions, outcome, j["raw"])


def _rel(p: Path) -> str:
    """A path as a record keeps it: relative to the project when inside it."""
    p = Path(p).resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def _abs(s: str) -> Path:
    p = Path(s)
    return p if p.is_absolute() else ROOT / p


def _all_nv(v, outcome, subject, why) -> list[Result]:
    return [Result(f, Outcome.NOT_VERIFIABLE, subject, detail=why) for f in fields_of(outcome)]


# --------------------------------------------------------------------------- output

SUMMARY_WIDTH = 200
_SUBJECT = re.compile(r"^(?P<test>.+?) (?P<cls>D[1-5]|legacy)(?P<variant> \[.*\])?$")
_OBSERVED = re.compile(r"[;,]\s+(?=(?:none\s+)?observed\b)")
_NOT_OBSERVED = re.compile(r":\s+(?=not observed\b)")


def default_log_dir() -> Path:
    """$XDG_RUNTIME_DIR/cto/behaviour-logs/<timestamp>-<random>/ (else
    $TMPDIR, else /tmp): private RAM, gone with the session."""
    base = os.environ.get("XDG_RUNTIME_DIR") or os.environ.get("TMPDIR") or "/tmp"
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S") + "-" + secrets.token_hex(3)
    return Path(base) / "cto" / "behaviour-logs" / stamp


def cut(s: str, n: int = SUMMARY_WIDTH) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[:n - 3] + "..."


def split_subject(subject: str) -> tuple[str, str]:
    """(test id with its variant, class) of a job's subject (subject_of)."""
    m = _SUBJECT.match(subject)
    if not m:
        return subject, "-"
    return m["test"] + (m["variant"] or ""), m["cls"]


def split_detail(detail: str) -> tuple[str, str]:
    """(expected, observed) of a FAIL's detail, at its first `; observed` /
    `, observed` / `: not observed`. A detail with no such seam (an unexpected
    request, nothing on screen) is all observed. For a person scanning the
    summary only: the log has the detail whole."""
    for rx in (_OBSERVED, _NOT_OBSERVED):
        m = rx.search(detail)
        if m:
            return detail[:m.start()], detail[m.end():]
    return "(see log)", detail


def full_lines(report: Report, wall: float, raw: dict | None) -> list[str]:
    """Everything a run says, one result per line: the log, or --verbose."""
    out = [f"{r.outcome.value:15} {r.subject:28} {r.rule:13} {r.detail}" for r in report.results]
    out += [f"note: {n}" for n in getattr(report, "notes", [])]
    out += [f"cannot tell: {x}" for x in report.cannot]
    c = report.counts()
    timing = ""
    if raw and raw.get("run_seconds") is not None:
        timing = (f"; content {raw['content_seconds']} s ({len(raw.get('ffmpeg_seconds') or [])} ffmpeg runs, "
                  f"{raw.get('content_cache_hits', 0)} cuts from the cache), players {raw['run_seconds']} s")
    out.append(f"exit {report.exit_code()}: PASS {c['PASS']}  FAIL {c['FAIL']}  NOT_VERIFIABLE "
               f"{c['NOT_VERIFIABLE']}; wall {wall:.1f} s{timing}")
    return out


def summary_lines(report: Report, wall: float, log_file: Path | None, width: int = SUMMARY_WIDTH) -> list[str]:
    """What stdout gets: the counts; per FAIL its test, class, field,
    expected, observed (each cut to `width`) and where its full line is in the
    log (path:line, the line of full_lines); per job that could not run, why;
    then the exit, the wall clock and the log."""
    c = report.counts()
    head = f"{c['PASS']} PASS"
    for k in ("FAIL", "NOT_VERIFIABLE"):
        if c[k]:
            head += f", {c[k]} {k}"
    out = [head]
    for i, r in enumerate(report.results, 1):
        if r.outcome is not Outcome.FAIL:
            continue
        test, cls = split_subject(r.subject)
        exp, obs = split_detail(r.detail)
        out.append(f"FAIL {cut(test, width)} {cls} {cut(r.rule, width)} | expected: {cut(exp, width)} "
                   f"| observed: {cut(obs, width)} | log: {log_file}:{i}")
    out += [f"cannot tell: {cut(x, width)}" for x in report.cannot]
    notes = len(getattr(report, "notes", []))
    out.append(f"exit {report.exit_code()}; wall {wall:.1f} s"
               + (f"; {notes} note(s) in the log" if notes else "") + f"; full log: {log_file}")
    return out


# --------------------------------------------------------------------------- command line

def main(argv: list, default_source: Path) -> int:
    lists = {"--only": [], "--class": [], "--vector": []}
    opts = {"--source": None, "--concurrency": None, "--out-json": None, "--save-raw": None, "--replay": None,
            "--clock": None, "--cpu-throttle": None, "--reference": None, "--log-dir": None}
    args = list(argv)
    clear_cache = verbose = False
    while args:
        a = args.pop(0)
        if a == "--clear-content-cache":
            clear_cache = True
        elif a == "--verbose":
            verbose = True
        elif a in lists or a in opts:
            if not args or args[0].startswith("--"):
                sys.stderr.write(f"{a} needs a value\n{USAGE}\n")
                return 64
            if a in lists:
                while args and not args[0].startswith("--"):
                    lists[a] += [x for x in args.pop(0).split(",") if x]
            else:
                opts[a] = args.pop(0)
        else:
            sys.stderr.write(f"--behaviour takes no {a}\n{USAGE}\n")
            return 64
    for c in lists["--class"]:
        if c not in ("D1", "D2", "D3", "D4", "D5", "legacy"):
            sys.stderr.write(f"unknown class {c}\n{USAGE}\n")
            return 64
    try:
        conc = int(opts["--concurrency"]) if opts["--concurrency"] else int(
            os.environ.get("SGAI_BEHAVIOUR_CONCURRENCY", "2"))
        if conc < 1:
            raise ValueError
    except ValueError:
        sys.stderr.write(f"--concurrency takes a positive integer\n{USAGE}\n")
        return 64
    clock = opts["--clock"] or "presentation"
    if clock not in CLOCKS:
        sys.stderr.write(f"--clock takes {' or '.join(CLOCKS)}\n{USAGE}\n")
        return 64
    try:
        throttle = float(opts["--cpu-throttle"]) if opts["--cpu-throttle"] else 1.0
        if not throttle >= 1:
            raise ValueError
    except ValueError:
        sys.stderr.write(f"--cpu-throttle takes a number >= 1\n{USAGE}\n")
        return 64
    reference = Path(opts["--reference"]) if opts["--reference"] else REFERENCE_SRC
    if not (reference / "sgai-reference.js").is_file():
        sys.stderr.write(f"--reference: no sgai-reference.js in {reference}\n{USAGE}\n")
        return 64
    report = Report()
    report.notes = []
    t0 = time.monotonic()
    raw: dict | None = None
    if opts["--replay"]:
        if (lists["--only"] or lists["--vector"] or lists["--class"] or opts["--save-raw"] or clear_cache
                or opts["--clock"] or opts["--cpu-throttle"] or opts["--reference"]):
            sys.stderr.write(f"--replay takes no --only, --class, --vector, --save-raw, --clock, --cpu-throttle, "
                             f"--reference or --clear-content-cache\n{USAGE}\n")
            return 64
        try:
            raw = json.loads(Path(opts["--replay"]).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.stderr.write(f"cannot read {opts['--replay']}: {e}\n")
            return 64
        replay(raw, report)
    else:
        source = Path(opts["--source"]) if opts["--source"] else default_source
        if not source.is_dir():
            sys.stderr.write(f"source directory not found: {source}\n{USAGE}\n")
            return 64
        for v in lists["--vector"]:
            if not Path(v).is_file():
                sys.stderr.write(f"vector not found: {v}\n{USAGE}\n")
                return 64
        files, unknown = discover(source, lists["--only"], lists["--vector"])
        if unknown:
            sys.stderr.write(f"--only names no vector: {', '.join(unknown)}\n{USAGE}\n")
            return 64
        crit = [t for t in lists["--only"] if t.startswith("R")]
        if not lists["--vector"] and (crit or not lists["--only"]):
            report.add(index_entries(source, crit))
        raw = {}
        try:
            run(source, files, lists["--class"], conc, report, raw, clear_cache, clock, throttle, reference)
        finally:
            if opts["--save-raw"] and raw:
                Path(opts["--save-raw"]).write_text(json.dumps(raw, indent=1) + "\n", encoding="utf-8")
    wall = time.monotonic() - t0
    if opts["--out-json"]:
        Path(opts["--out-json"]).write_text(json.dumps({
            "results": [r.as_dict() for r in report.results], "cannot": report.cannot,
            "notes": report.notes, "wall_seconds": round(wall, 1),
            "timings": {k: raw.get(k) for k in ("content_seconds", "run_seconds", "browser")} if raw else None,
        }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    full = full_lines(report, wall, raw)
    log = Path(opts["--log-dir"]) if opts["--log-dir"] else default_log_dir()
    log_file = log / "behaviour.log"
    try:
        log.mkdir(parents=True, exist_ok=True, mode=0o700)
        log_file.write_text("\n".join(full) + "\n", encoding="utf-8")
    except OSError as e:
        sys.stderr.write(f"cannot write the log {log_file}: {e}; the full output follows\n")
        verbose, log_file = True, None
    lines = full if verbose else summary_lines(report, wall, log_file)
    print("\n".join(lines))
    return report.exit_code()
