"""Level 3a: legacy Players play the specification's MPDs and ignore the extension.

Criterion (context/07 §5, UC-07; ADR 0051): every main MPD of the
specification, with its media pointed at local test content, starts, advances
ADVANCE_S seconds of media time with no fatal error, and the Player sends no
request to a URI carried by a construct of our namespace. In Shaka, also, a
6th-edition InsertPresentation is recognised.

How a run works:

1. Test content is generated with ffmpeg (H.264 + AAC, fragmented MP4) into a
   private temporary directory: one master per picture size, cut into the
   segment durations the MPDs declare.
2. Each MPD is rewritten: only its absolute BaseURLs change (or one is added
   at MPD level when there is none), pointing at this run's local server.
   Everything else — EventStreams, foreign elements and attributes, timing —
   is byte-identical, and `rewrite` proves it by comparing the two trees.
3. A local HTTP server serves the harness page, the pinned Players, the
   rewritten MPDs and the segments. A segment number past the end of the
   content wraps around, and its `tfdt` is moved to where that number sits on
   the MPD's timeline, so a live MPD whose availabilityStartTime is weeks ago
   plays at its live edge without touching its timing.
4. bin/players/run.mjs drives headless Chromium (Playwright) through one
   adapter per Player and reports what it measured; this module turns those
   numbers into results. Requests leaving the local server are recorded and
   aborted.

What a green says: each Player, unmodified, played the primary content of
each main MPD for ADVANCE_S seconds without a fatal error and without
requesting a URI of our constructs. It does NOT say what happens at a break
or window later in the timeline, nor anything about the ad documents (List
MPD, SPS), which a legacy Player never requests and are not loaded as main.
"""
from __future__ import annotations

import http.server
import json
import math
import os
import re
import secrets
import shutil
import signal
import struct
import subprocess
import threading
import time
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree as ET

from .model import Outcome, Result, Rule

DASH = "urn:mpeg:dash:schema:mpd:2011"
D = "{%s}" % DASH
SGAI_NS = "urn:svta:dash:sgai:2026"
INSERT_SCHEME = "urn:mpeg:dash:event:alternativeMPD:insert:2025"
REPLACE_SCHEME = "urn:mpeg:dash:event:alternativeMPD:replace:2025"

PLAYERS_DIR = Path(__file__).resolve().parent.parent / "players"
PLAYERS = ("dashjs", "shaka")
PINNED = {"dashjs": "5.3.0", "shaka-player": "5.3.6", "playwright": "1.61.1"}

ADVANCE_S = 8.0          # media seconds the primary content must advance
JOB_TIMEOUT_S = 45.0     # wall seconds a Player gets to start and advance
CONTENT_S = 32           # length of the generated content before it wraps
FPS = 10
CONCURRENCY = int(os.environ.get("SGAI_PLAYERS_CONCURRENCY", "4"))

UC07 = ("context/07 §5 (UC-07)",
        "The expected behaviour: silent skip of C + no tracking beacon for C.")
RULES = [
    Rule("P-LEGACY-dashjs", 3, *UC07, ("mpd",),
         notes=f"dash.js upstream {PINNED['dashjs']}: starts, advances {ADVANCE_S:g} s, no fatal "
               "error, no request to a URI of our namespace"),
    Rule("P-LEGACY-shaka", 3, *UC07, ("mpd",),
         notes=f"Shaka {PINNED['shaka-player']}: same criterion"),
    Rule("P-INSERT-shaka", 3, "ADR 0051",
         "In Shaka, also that a 6th-edition `InsertPresentation` is recognised.", ("mpd",),
         notes="observable: the AdManager's 'ad-cue-points-changed' event carries a cue point at "
               "the Event's presentation time"),
]
RULE = {r.id: r for r in RULES}


# --------------------------------------------------------------------------- prerequisites

def missing_prerequisites() -> list[str]:
    out = []
    node = shutil.which("node")
    if not node:
        out.append("node is not on PATH (needed to drive the Players)")
    if not shutil.which("ffmpeg"):
        out.append("ffmpeg is not on PATH (needed to generate the test content)")
    nm = PLAYERS_DIR / "node_modules"
    for pkg, want in PINNED.items():
        pj = nm / pkg / "package.json"
        if not pj.exists():
            out.append(f"{pkg} is not installed: run `npm ci` in {PLAYERS_DIR}")
            continue
        got = json.loads(pj.read_text()).get("version")
        if got != want:
            out.append(f"{pkg} installed is {got}, pinned is {want}: run `npm ci` in {PLAYERS_DIR}")
    if node and not out:
        try:
            p = subprocess.run([node, "--input-type=module", "-e",
                                "import {chromium} from 'playwright';"
                                "console.log(chromium.executablePath())"],
                               cwd=PLAYERS_DIR, capture_output=True, text=True, timeout=60)
            exe = p.stdout.strip()
            if p.returncode != 0 or not exe or not Path(exe).exists():
                out.append(f"the Chromium of playwright {PINNED['playwright']} is not installed "
                           f"({exe or p.stderr.strip()[:200]})")
        except (OSError, subprocess.TimeoutExpired) as e:
            out.append(f"cannot ask playwright for its Chromium: {e}")
    return out


# --------------------------------------------------------------------------- the MPD

def _dur(s: str | None) -> float:
    if not s:
        return 0.0
    m = re.fullmatch(r"-?P(?:(\d+(?:\.\d+)?)D)?(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?"
                     r"(?:(\d+(?:\.\d+)?)S)?)?", s.strip())
    if not m:
        return 0.0
    d, h, mi, se = (float(x) if x else 0.0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se


BASEURL = re.compile(r"(<BaseURL\b[^>]*>)([^<]*)(</BaseURL>)")


def rewrite(text: str, base: str) -> tuple[str, list[str]]:
    """Point the MPD at `base`: every absolute BaseURL becomes `base`; with no
    BaseURL at MPD level, one is inserted as the first child. Returns the new
    text and the list of changes. Raises ValueError if anything other than
    BaseURL changed (the trees are compared after the substitution)."""
    changes = []

    def sub(m):
        value = m.group(2).strip()
        if urlsplit(value).scheme:
            changes.append(f"BaseURL {value} -> {base}")
            return m.group(1) + base + m.group(3)
        return m.group(0)

    new = BASEURL.sub(sub, text)
    root = ET.fromstring(text.encode("utf-8"))
    if root.find(D + "BaseURL") is None:
        m = re.search(r"<MPD\b[^>]*>", new)
        new = new[:m.end()] + f"\n  <BaseURL>{base}</BaseURL>" + new[m.end():]
        changes.append(f"BaseURL {base} inserted at MPD level")
    _same_but_baseurl(root, ET.fromstring(new.encode("utf-8")))
    return new, changes


def _same_but_baseurl(a, b) -> None:
    def norm(e):
        kids = [k for k in e if not (isinstance(k.tag, str) and k.tag == D + "BaseURL")]
        return (e.tag, sorted(e.attrib.items()),
                (e.text or "").strip() if e.tag != D + "BaseURL" else "", [norm(k) for k in kids])
    if norm(a) != norm(b):
        raise ValueError("the rewrite changed something other than BaseURL")


class Unservable(Exception):
    pass


def _template(*elems) -> dict:
    out = {}
    for e in elems:
        if e is None:
            continue
        st = e.find(D + "SegmentTemplate")
        if st is not None:
            if st.find(D + "SegmentTimeline") is not None:
                raise Unservable("SegmentTimeline is not supported by the test content")
            out.update(st.attrib)
    return out


def _base(cur: str, e) -> str:
    b = e.find(D + "BaseURL")
    return urljoin(cur, b.text.strip()) if b is not None and b.text else cur


def plan(text: str, base: str) -> dict:
    """What the server answers for one rewritten MPD: absolute URL path ->
    (track, segment duration, startNumber, PTO seconds) for init and media.
    Only URLs under `base` are served; anything else is a 404, which is how an
    MPD pointing at segments that do not exist fails."""
    root = ET.fromstring(text.encode("utf-8"))
    mbase = _base(base, root)
    inits, medias = {}, []
    for period in root.findall(D + "Period"):
        pbase = _base(mbase, period)
        for aset in period.findall(D + "AdaptationSet"):
            abase = _base(pbase, aset)
            ctype = aset.get("contentType") or (aset.get("mimeType") or "").split("/")[0]
            for rep in aset.findall(D + "Representation"):
                ctype_r = ctype or (rep.get("mimeType") or "").split("/")[0]
                rbase = _base(abase, rep)
                t = _template(period, aset, rep)
                if not t.get("media") or not t.get("duration"):
                    raise Unservable(f"Representation {rep.get('id')} has no SegmentTemplate "
                                     "with @media and @duration")
                ts = float(t.get("timescale", "1"))
                segdur = float(t["duration"]) / ts
                if segdur != int(segdur) or CONTENT_S % int(segdur):
                    raise Unservable(f"segment duration {segdur:g} s does not divide the "
                                     f"{CONTENT_S} s of test content")
                if ctype_r == "video":
                    track = ("video", int(rep.get("width") or aset.get("width") or 1280),
                             int(rep.get("height") or aset.get("height") or 720))
                elif ctype_r == "audio":
                    track = ("audio",)
                else:
                    raise Unservable(f"Representation {rep.get('id')}: content type {ctype_r!r} "
                                     "has no test content")
                info = (track, int(segdur), int(t.get("startNumber", "1")),
                        float(t.get("presentationTimeOffset", "0")) / ts)

                def fill(tpl):
                    if "$Time$" in tpl:
                        raise Unservable("$Time$ templates are not supported by the test content")
                    s = tpl.replace("$$", "$").replace("$RepresentationID$", rep.get("id", ""))
                    s = s.replace("$Bandwidth$", rep.get("bandwidth", ""))
                    return re.sub(r"\$Number(?:%0\d+d)?\$", "SGAINUMBER", s)

                if t.get("initialization"):
                    inits[urlsplit(urljoin(rbase, fill(t["initialization"]))).path] = info
                path = urlsplit(urljoin(rbase, fill(t["media"]))).path
                rx = re.escape(path).replace("SGAINUMBER", "(\\d+)", 1)
                medias.append((re.compile("^" + rx + "$"), info))
    prefix = urlsplit(base).path
    return {"prefix": prefix,
            "inits": {k: v for k, v in inits.items() if k.startswith(prefix)},
            "medias": [(rx, v) for rx, v in medias if rx.pattern.startswith("^" + re.escape(prefix))]}


def uris(text: str) -> tuple[list, list, list]:
    """(InsertPresentation cue starts in seconds, 6th-edition alternative-MPD
    URIs, URIs carried by our namespace)."""
    root = ET.fromstring(text.encode("utf-8"))
    starts, alt, ours = [], [], []
    for period in root.findall(D + "Period"):
        pstart = _dur(period.get("start"))
        for es in period.findall(D + "EventStream"):
            scheme = es.get("schemeIdUri")
            ts = float(es.get("timescale", "1"))
            pto = float(es.get("presentationTimeOffset", "0"))
            for ev in es.findall(D + "Event"):
                for child in ev:
                    if scheme in (INSERT_SCHEME, REPLACE_SCHEME) and child.tag in (
                            D + "InsertPresentation", D + "ReplacePresentation"):
                        if child.get("uri"):
                            alt.append(child.get("uri"))
                        if scheme == INSERT_SCHEME and child.tag == D + "InsertPresentation":
                            starts.append(pstart + (float(ev.get("presentationTime", "0")) - pto) / ts)
    for e in root.iter():
        own = isinstance(e.tag, str) and e.tag.startswith("{%s}" % SGAI_NS)
        for k, v in e.attrib.items():
            if (own or k.startswith("{%s}" % SGAI_NS)) and urlsplit(v).scheme in ("http", "https"):
                ours.append(v)
    return starts, alt, ours


def _same_resource(a: str, b: str) -> bool:
    x, y = urlsplit(a), urlsplit(b)
    return (x.netloc, x.path) == (y.netloc, y.path)


# --------------------------------------------------------------------------- content

class Content:
    """Test content in `root`, generated on demand: a master per picture size
    and one for audio, cut into each segment duration asked for."""

    def __init__(self, root: Path):
        self.root = root
        self.lock = threading.Lock()
        self.cut = {}      # (track, segdur) -> (dir, K, track timescale, {n: tfdt})
        self.log = []

    def _ffmpeg(self, *args):
        t0 = time.monotonic()
        p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {p.stderr.strip()[:500]}")
        self.log.append(round(time.monotonic() - t0, 1))

    def _master(self, track) -> Path:
        if track[0] == "video":
            f = self.root / f"master-{track[1]}x{track[2]}.mp4"
            if not f.exists():
                self._ffmpeg("-f", "lavfi", "-i", f"testsrc2=size={track[1]}x{track[2]}:rate={FPS}",
                             "-t", str(CONTENT_S), "-c:v", "libx264", "-preset", "veryfast",
                             "-profile:v", "high", "-pix_fmt", "yuv420p", "-g", str(FPS),
                             "-keyint_min", str(FPS), "-sc_threshold", "0", "-b:v", "800k", "-an",
                             str(f))
        else:
            f = self.root / "master-audio.mp4"
            if not f.exists():
                self._ffmpeg("-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
                             "-t", str(CONTENT_S), "-c:a", "aac", "-b:a", "128k", "-ac", "2", str(f))
        return f

    def prepare(self, track, segdur: int):
        with self.lock:
            key = (track, segdur)
            if key in self.cut:
                return self.cut[key]
            master = self._master(track)
            d = self.root / ("-".join(map(str, track)) + f"-{segdur}s")
            d.mkdir()
            self._ffmpeg("-i", str(master), "-c", "copy", "-f", "dash", "-seg_duration", str(segdur),
                         "-use_template", "1", "-use_timeline", "0", "-init_seg_name", "init.mp4",
                         "-media_seg_name", "$Number$.m4s", str(d / "m.mpd"))
            k = CONTENT_S // segdur
            ts = _mdhd_timescale((d / "init.mp4").read_bytes())
            for n in range(1, k + 1):
                if not (d / f"{n}.m4s").exists():
                    raise RuntimeError(f"ffmpeg produced fewer than {k} segments in {d.name}")
            self.cut[key] = (d, k, ts)
            return self.cut[key]


def _boxes(b: bytes, off: int = 0, end: int | None = None):
    end = len(b) if end is None else end
    while off + 8 <= end:
        size, typ = struct.unpack(">I4s", b[off:off + 8])
        if size < 8:
            raise ValueError("unsupported box size")
        yield off, size, typ.decode("latin-1")
        off += size


def _mdhd_timescale(init: bytes) -> int:
    def walk(off, end):
        for o, s, t in _boxes(init, off, end):
            if t == "mdhd":
                v = init[o + 8]
                return struct.unpack(">I", init[o + 20:o + 24] if v == 0 else init[o + 28:o + 32])[0]
            if t in ("moov", "trak", "mdia"):
                r = walk(o + 8, o + s)
                if r:
                    return r
        return None
    ts = walk(0, len(init))
    if not ts:
        raise RuntimeError("no mdhd in init segment")
    return ts


def shifted_segment(data: bytes, shift: int) -> bytes:
    """The segment without its sidx, with every tfdt moved by `shift` (track
    timescale units). Nothing else in the segment changes."""
    out = bytearray()
    for o, s, t in _boxes(data):
        if t == "sidx":
            continue
        box = bytearray(data[o:o + s])
        if t == "moof":
            for to, ts_, tt in _boxes(box, 8, s):
                if tt != "traf":
                    continue
                for fo, fs, ft in _boxes(box, to + 8, to + ts_):
                    if ft == "tfdt":
                        if box[fo + 8] == 1:
                            v = struct.unpack(">Q", box[fo + 12:fo + 20])[0] + shift
                            box[fo + 12:fo + 20] = struct.pack(">Q", v)
                        else:
                            v = struct.unpack(">I", box[fo + 12:fo + 16])[0] + shift
                            if v >= 2 ** 32:
                                raise ValueError("tfdt version 0 cannot hold the shifted time")
                            box[fo + 12:fo + 16] = struct.pack(">I", v)
        out += box
    return bytes(out)


# --------------------------------------------------------------------------- server

class _Server(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, content: Content):
        super().__init__(("127.0.0.1", 0), _Handler)
        self.content = content
        self.mpds = {}     # key -> (text, plan)


STATIC = {
    "/harness.html": PLAYERS_DIR / "harness.html",
}
PREFIXES = {
    "/adapters/": PLAYERS_DIR / "adapters",
    "/lib/dashjs/": PLAYERS_DIR / "node_modules" / "dashjs" / "dist" / "modern" / "umd",
    "/lib/shaka/": PLAYERS_DIR / "node_modules" / "shaka-player" / "dist",
}
TYPES = {".html": "text/html", ".js": "application/javascript", ".mpd": "application/dash+xml",
         ".mp4": "video/mp4", ".m4s": "video/iso.segment", ".map": "application/json"}


class _Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body=b"", ctype="text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        try:
            body, ctype = self._route(path)
        except FileNotFoundError:
            return self._send(404, b"not found")
        except Exception as e:  # a defect of the harness, visible as a 500 in the run
            return self._send(500, str(e).encode())
        self._send(200, body, ctype)

    def _route(self, path):
        if path in STATIC:
            return STATIC[path].read_bytes(), TYPES[".html"]
        for pre, d in PREFIXES.items():
            if path.startswith(pre):
                f = (d / path[len(pre):]).resolve()
                if d.resolve() not in f.parents or not f.is_file():
                    raise FileNotFoundError(path)
                return f.read_bytes(), TYPES.get(f.suffix, "application/octet-stream")
        m = re.fullmatch(r"/m/([\w-]+)\.mpd", path)
        if m and m.group(1) in self.server.mpds:
            return self.server.mpds[m.group(1)][0].encode("utf-8"), TYPES[".mpd"]
        m = re.match(r"/c/([\w-]+)/", path)
        if m and m.group(1) in self.server.mpds:
            p = self.server.mpds[m.group(1)][1]
            if path in p["inits"]:
                track, segdur, _, _ = p["inits"][path]
                d, _, _ = self.server.content.prepare(track, segdur)
                return (d / "init.mp4").read_bytes(), TYPES[".mp4"]
            for rx, (track, segdur, start, pto) in p["medias"]:
                mm = rx.match(path)
                if mm:
                    d, k, ts = self.server.content.prepare(track, segdur)
                    i = int(mm.group(1)) - start
                    if i < 0:
                        raise FileNotFoundError(path)
                    src = i % k + 1
                    shift = (i // k) * CONTENT_S * ts + round(pto * ts)
                    return shifted_segment((d / f"{src}.m4s").read_bytes(), shift), TYPES[".m4s"]
        raise FileNotFoundError(path)


# --------------------------------------------------------------------------- run

def _tmpdir() -> Path:
    base = os.environ.get("XDG_RUNTIME_DIR") or os.environ.get("TMPDIR") or "/tmp"
    d = Path(base) / "cto" / f"players-{time.strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3)}"
    d.mkdir(parents=True, mode=0o700)
    return d


def _drive(origin: str, jobs: list, timeout: float) -> dict:
    """Run bin/players/run.mjs in its own process group, and stop that group by
    the id kept here if it overruns."""
    proc = subprocess.Popen(["node", "run.mjs"], cwd=PLAYERS_DIR, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    payload = json.dumps({"origin": origin, "advance": ADVANCE_S, "timeoutMs": JOB_TIMEOUT_S * 1000,
                          "concurrency": CONCURRENCY, "jobs": jobs})
    try:
        out, err = proc.communicate(payload, timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        raise RuntimeError(f"the Player run did not finish in {timeout:.0f} s")
    if proc.returncode != 0:
        raise RuntimeError(f"run.mjs exited {proc.returncode}: {err.strip()[-800:]}")
    return json.loads(out)


def run(ctx, report) -> list[Result]:
    docs = [(b.ref, b.text) for b in ctx.by_kind("mpd")]
    if not docs:
        return [RULE[r].result(Outcome.NOT_VERIFIABLE, "specification",
                               detail="no main MPD in the specification") for r in RULE]
    return run_documents(docs, report)


def run_documents(docs: list, report, raw: dict | None = None) -> list[Result]:
    """docs: [(subject, MPD text)]. Appends to report.cannot when the run cannot
    tell; never returns PASS for a Player it did not see play. `raw`, if given,
    receives what the Players reported."""
    missing = missing_prerequisites()
    if missing:
        report.cannot.extend(f"level 3a (Players): {m}" for m in missing)
        return [RULE[r].result(Outcome.NOT_VERIFIABLE, s, detail="; ".join(missing))
                for s, _ in docs for r in RULE]

    tmp = _tmpdir()
    server = None
    out: list[Result] = []
    try:
        server = _Server(Content(tmp))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f"http://127.0.0.1:{server.server_address[1]}"
        jobs, meta = [], {}
        for n, (subject, text) in enumerate(docs, 1):
            key = f"d{n}"
            base = f"{origin}/c/{key}/"
            try:
                new, changes = rewrite(text, base)
                p = plan(new, base)
                for info in list(p["inits"].values()) + [m[1] for m in p["medias"]]:
                    server.content.prepare(info[0], info[1])
            except (Unservable, ValueError) as e:
                for r in ("P-LEGACY-dashjs", "P-LEGACY-shaka"):
                    out.append(RULE[r].result(Outcome.NOT_VERIFIABLE, subject,
                                              detail=f"cannot point this MPD at test content: {e}"))
                continue
            server.mpds[key] = (new, p)
            meta[key] = (subject, changes, *uris(text))
            for player in PLAYERS:
                jobs.append({"id": key, "player": player, "mpd": f"{origin}/m/{key}.mpd"})
        if not jobs:
            return out
        timeout = 120 + math.ceil(len(jobs) / max(1, CONCURRENCY)) * (JOB_TIMEOUT_S + 15)
        got = _drive(origin, jobs, timeout)
        if raw is not None:
            raw.update(got)
            raw["ffmpeg_seconds"] = server.content.log
            raw["rewrites"] = {k: {"subject": v[0], "changes": v[1]} for k, v in meta.items()}
        results = {(r["id"], r["player"]): r for r in got["results"]}
        browser = got.get("browser", "")
        for key, (subject, changes, starts, alt, ours) in meta.items():
            for player in PLAYERS:
                r = results.get((key, player))
                out.append(_legacy(player, subject, r, alt, ours, browser, report))
            if starts:
                out.append(_insert(subject, results.get((key, "shaka")), starts))
        return out
    except RuntimeError as e:
        report.cannot.append(f"level 3a (Players): {e}")
        return out + [RULE[r].result(Outcome.NOT_VERIFIABLE, s, detail=str(e))
                      for s, _ in docs for r in ("P-LEGACY-dashjs", "P-LEGACY-shaka")]
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        shutil.rmtree(tmp, ignore_errors=True)


def _legacy(player, subject, r, alt, ours, browser, report) -> Result:
    rule = RULE[f"P-LEGACY-{player}"]
    if r is None or not r.get("ok"):
        why = "no result from the harness" if r is None else r.get("harnessError", "harness error")
        report.cannot.append(f"level 3a (Players): {player} on {subject}: {why}")
        return rule.result(Outcome.NOT_VERIFIABLE, subject, detail=why)
    st = r["state"]
    ext = [x["url"] for x in r["external"]]
    to_ours = [u for u in ext if any(_same_resource(u, o) for o in ours)]
    to_alt = [u for u in ext if any(_same_resource(u, a) for a in alt)]
    other = [u for u in ext if u not in to_ours and u not in to_alt]
    start = f"{r['startMs']} ms" if r["startMs"] is not None else "never"
    detail = (f"{r.get('version', '?')} on {browser}: start {start}; advanced {r['advanced']:.1f} s "
              f"in {r['wallMs']} ms wall; errors {st['errorCount']}"
              + (f" (first {st['errors'][0]['code']}: {st['errors'][0]['message'][:120]})"
                 if st["errors"] else "")
              + f"; segment responses {r['segmentResponses']}, local 4xx/5xx {r['localErrorCount']}"
              + (f" (e.g. {r['localErrors'][0]['status']} {r['localErrors'][0]['url']})"
                 if r["localErrors"] else "")
              + f"; requests to our namespace's URIs {len(to_ours)}"
              + f", to 6th-ed. alternative-MPD URIs {len(to_alt)}, other external {len(other)}"
              + (f" ({', '.join(sorted(set(other))[:3])})" if other else ""))
    if st["fatal"]:
        return rule.result(Outcome.FAIL, subject,
                           detail=f"fatal error {st['fatal']['code']}: {st['fatal']['message'][:200]}. "
                                  + detail)
    if not r["started"]:
        return rule.result(Outcome.FAIL, subject,
                           detail=f"playback did not start within {JOB_TIMEOUT_S:g} s. " + detail)
    if r["advanced"] < ADVANCE_S:
        return rule.result(Outcome.FAIL, subject,
                           detail=f"advanced {r['advanced']:.1f} s < {ADVANCE_S:g} s. " + detail)
    if to_ours:
        return rule.result(Outcome.FAIL, subject,
                           detail=f"requested a URI of our namespace: {to_ours[0]}. " + detail)
    return rule.result(Outcome.PASS, subject, detail=detail)


def _insert(subject, r, starts) -> Result:
    rule = RULE["P-INSERT-shaka"]
    if r is None or not r.get("ok"):
        return rule.result(Outcome.NOT_VERIFIABLE, subject, detail="no result from the Shaka run")
    insp = (r["state"].get("inspect") or {})
    seen = sorted({round(c["start"], 3) for cps in insp.get("cuepoints", []) for c in cps})
    missing = [s for s in starts if not any(abs(s - c) < 0.01 for c in seen)]
    ads = insp.get("ads", {})
    regions = [x for x in insp.get("regions", []) if x.get("schemeIdUri") == INSERT_SCHEME]
    detail = (f"InsertPresentation at {', '.join(f'{s:g}' for s in starts)} s; "
              f"ad-cue-points-changed cue starts seen {seen}; insert-scheme timeline regions "
              f"{len(regions)}; ad events {ads or 'none'}")
    if missing:
        return rule.result(Outcome.FAIL, subject,
                           detail=f"no cue point at {', '.join(f'{s:g}' for s in missing)} s. " + detail)
    return rule.result(Outcome.PASS, subject, detail=detail)
