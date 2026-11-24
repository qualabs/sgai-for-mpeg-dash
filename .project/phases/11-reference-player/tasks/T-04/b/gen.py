"""Writes the behaviour fixtures of T-04 part B. Run from the project root."""
from pathlib import Path

ROOT = Path("spec-source/behaviour/fixtures")

MPD = """<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT2M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/behaviour/</BaseURL>
  <Period id="main" start="PT0S">
{comment}    <EventStream schemeIdUri="urn:svta:dash:sgai-{scheme}:2026" timescale="1000">
{events}    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" bandwidth="3000000" width="1280" height="720"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
{metrics}</MPD>
"""

METRICS = """  <Metrics metrics="PlayList">
    <Reporting schemeIdUri="urn:example:reporting:2026" value="collector-1"/>
  </Metrics>
"""


def esc(s):
    return s.replace("&", "&amp;")


def overlay(eid, t, d, uri, cap=None, **attrs):
    a = [f'uri="{esc(uri)}"', f'durationCap="{cap if cap is not None else d}"']
    for k, v in attrs.items():
        a.append(f'{k}="{v}"')
    body = ("\n" + " " * 12).join(a)
    return (f'      <Event id="{eid}" presentationTime="{t}" duration="{d}">\n'
            f'        <svta:OverlayPresentation\n            {body}/>\n'
            f'      </Event>\n')


def pause(eid, t, d, uri, **attrs):
    a = [f'uri="{esc(uri)}"', f'durationCap="{d}"']
    for k, v in attrs.items():
        a.append(f'{k}="{v}"')
    body = ("\n" + " " * 12).join(a)
    return (f'      <Event id="{eid}" presentationTime="{t}" duration="{d}">\n'
            f'        <svta:PauseAdPresentation\n            {body}/>\n'
            f'      </Event>\n')


def mpd(scheme, events, comment=""):
    c = "".join(f"    <!-- {line} -->\n" for line in comment.splitlines()) if comment else ""
    return MPD.format(scheme=scheme, events="".join(events), comment=c,
                      metrics=METRICS if scheme == "pause-trigger" else "")


def opt(src, mime, layout, dur=None, rect=None):
    a = [f'src="{src}"', f'mimeType="{mime}"']
    if dur:
        a.append(f'duration="{dur}"')
    a.append(f'layout="{layout}"')
    if rect:
        a.append(f'rect="{rect}"')
    return "    <svta:RenderableAsset " + ("\n" + " " * 26).join(a) + "/>\n"


def ad(opts, imp, title):
    return ("  <svta:Ad>\n" + "".join(opts) +
            '    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"\n'
            '                   timescale="1000">\n'
            f'      <Event presentationTime="0" id="1">https://t.example.com/imp?cr={imp}</Event>\n'
            '    </svta:Tracking>\n'
            '    <svta:AdSystem>ExampleAds</svta:AdSystem>\n'
            f'    <svta:AdTitle>{title}</svta:AdTitle>\n'
            "  </svta:Ad>\n")


def olist(family, ads, **attrs):
    a = [f'family="{family}"']
    if family == "pause":
        a.append(f'onExhausted="{attrs.pop("onExhausted", "stop")}"')
    a.append(f'dismissAfter="{attrs.pop("dismissAfter", "never")}"')
    for k, v in attrs.items():
        a.append(f'{k}="{v}"')
    head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"\n'
            '                  xmlns:svta="urn:svta:dash:sgai:2026"\n'
            '                  ' + ("\n" + " " * 18).join(a))
    if not ads:
        return head + "/>\n"
    return head + ">\n" + "".join(ads) + "</svta:OverlayList>\n"


SUB = """<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/behaviour/R5.6/</BaseURL>
  <Period id="cr561v" duration="PT5S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="1000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="lt540" bandwidth="1200000" width="960" height="540"/>
    </AdaptationSet>
  </Period>
</MPD>
"""

CDN = "https://ads-cdn.example.com/behaviour"
APS = "https://aps.example.com/behaviour"


def img(crit, name, layout, dur="PT5S", rect=None, mime="image/png"):
    return opt(f"{CDN}/{crit}/{name}", mime, layout, dur, rect)


files = {}

# R2.3 — a candidate outside the window's allowed layouts is not rendered.
files["R2.3/main.mpd"] = mpd("overlay", [overlay(1, 5000, 10000, f"{APS}/r2-3?w=1", allowedLayouts="overlay-corner")],
                             "5 s to 15 s; the window admits overlay-corner only.")
files["R2.3/overlay-list.xml"] = olist("overlay", [
    ad([img("R2.3", "lt.png", "overlay-lower-third")], "231", "Not admitted"),
    ad([img("R2.3", "corner.png", "overlay-corner")], "232", "Admitted")])

# R5.3 — a candidate none of whose options the device can render is skipped.
files["R5.3/main.mpd"] = mpd("overlay", [overlay(1, 5000, 10000, f"{APS}/r5-3?w=1")],
                             "5 s to 15 s, declaring nothing beyond its cap.")
files["R5.3/overlay-list.xml"] = olist("overlay", [
    ad([opt(f"{CDN}/R5.3/banner.html", "text/html", "overlay-lower-third", "PT5S")], "531", "HTML only"),
    ad([img("R5.3", "lt.png", "overlay-lower-third")], "532", "Image only")])

# R5.6 — options checked against capability and against the admitted layouts.
files["R5.6/main-capability.mpd"] = mpd("overlay", [overlay(1, 5000, 5000, f"{APS}/r5-6?w=1")],
                                        "5 s to 10 s, declaring nothing beyond its cap.")
files["R5.6/forms.xml"] = olist("overlay", [ad([
    opt(f"{CDN}/R5.6/cr561v.mpd", "application/dash+xml", "overlay-lower-third"),
    opt(f"{CDN}/R5.6/banner.html", "text/html", "overlay-lower-third", "PT5S"),
    img("R5.6", "banner.png", "overlay-lower-third")], "561", "Three forms")])
files["R5.6/cr561v.mpd"] = SUB
files["R5.6/main-declared.mpd"] = mpd("overlay", [overlay(1, 5000, 5000, f"{APS}/r5-6?w=2", allowedLayouts="overlay-corner")],
                                      "5 s to 10 s; the window admits overlay-corner only.")
files["R5.6/layouts.xml"] = olist("overlay", [ad([
    img("R5.6", "lt.png", "overlay-lower-third"),
    img("R5.6", "corner.png", "overlay-corner")], "562", "Two layouts")])
files["R5.6/main-default.mpd"] = mpd("overlay", [overlay(1, 5000, 5000, f"{APS}/r5-6?w=3")],
                                     "5 s to 10 s, no allowed layouts: the family default, which excludes custom.")
files["R5.6/custom-first.xml"] = olist("overlay", [ad([
    img("R5.6", "bug.png", "custom", rect="0 0 20 20"),
    img("R5.6", "corner.png", "overlay-corner")], "563", "Custom first")])

# R5.9 — the first request for an option's resource fails.
files["R5.9/main.mpd"] = mpd("overlay", [overlay(1, 5000, 5000, f"{APS}/r5-9?w=1")],
                             "5 s to 10 s, declaring nothing beyond its cap.")
files["R5.9/overlay-list.xml"] = olist("overlay", [ad([
    img("R5.9", "missing.png", "overlay-lower-third"),
    img("R5.9", "lt.png", "overlay-lower-third")], "591", "First image fails")])

# Empty overlay resolution, for the request tests.
EMPTY_O = olist("overlay", [])
EMPTY_P = olist("pause", [], validFor="PT10M")

# R29.2 — slot parameters sent when, and only when, declared.
files["R29.2/main.mpd"] = mpd("overlay", [
    overlay(1, 3000, 2000, f"{APS}/r29-2?w=1", earliestResolutionTimeOffset="0",
            allowedLayouts="custom overlay-corner", customRegion="50 0 50 50"),
    overlay(2, 6000, 2000, f"{APS}/r29-2?w=2", earliestResolutionTimeOffset="0", allowedLayouts="overlay-corner"),
    overlay(3, 9000, 2000, f"{APS}/r29-2?w=3", earliestResolutionTimeOffset="0")],
    "Three windows resolved when they fire: both slot values declared,\nallowed layouts only, nothing.")
files["R29.2/empty.xml"] = EMPTY_O

# R29.4 — the Player adds no parameter outside the reserved names unprefixed.
files["R29.4/main.mpd"] = mpd("overlay", [
    overlay(1, 3000, 2000, f"{APS}/r29-4?title=beh294&device=tv", earliestResolutionTimeOffset="0",
            allowedLayouts="overlay-corner")],
    "The Publisher's own unprefixed parameters (title, device) are in the URI.")
files["R29.4/empty.xml"] = EMPTY_O

# R32.1 / R32.2 — exhaustion inside a pause.
PAUSE_MAIN = mpd("pause-trigger", [pause(1, 0, 60000, f"{APS}/pause?w=1")],
                 "A pause window over the first 60 s.")
files["R32.1/main.mpd"] = PAUSE_MAIN
files["R32.1/repeat.xml"] = olist("pause", [ad([img("R32.1", "full-r.png", "pause-fullscreen", "PT3S")], "3211", "Repeat")],
                                  onExhausted="repeat")
files["R32.1/request-again.xml"] = olist("pause", [ad([img("R32.1", "full-a.png", "pause-fullscreen", "PT3S")], "3212", "First document")],
                                         onExhausted="request-again")
files["R32.1/second.xml"] = olist("pause", [ad([img("R32.1", "full-b.png", "pause-fullscreen", "PT3S")], "3213", "Second document")],
                                  onExhausted="stop")
files["R32.1/stop.xml"] = olist("pause", [ad([img("R32.1", "full-s.png", "pause-fullscreen", "PT3S")], "3214", "Stop")],
                                onExhausted="stop")
files["R32.2/main.mpd"] = PAUSE_MAIN
files["R32.2/request-again.xml"] = olist("pause", [ad([img("R32.2", "full.png", "pause-fullscreen", "PT3S")], "3221", "First document")],
                                         onExhausted="request-again")
files["R32.2/empty.xml"] = olist("pause", [], onExhausted="request-again")

# R34.1 / R34.3 — a once-per-session pause window.
ONCE_MAIN = mpd("pause-trigger", [pause(1, 0, 60000, f"{APS}/pause-once?w=1", executeOnce="true")],
                "A once-per-session pause window over the first 60 s.")
files["R34.1/main.mpd"] = ONCE_MAIN
files["R34.1/pause-list.xml"] = olist("pause", [ad([img("R34.1", "full.png", "pause-fullscreen", "PT3S")], "3411", "Once")])
files["R34.3/main.mpd"] = ONCE_MAIN
files["R34.3/empty.xml"] = olist("pause", [], validFor="PT5S")
files["R34.3/pause-list.xml"] = olist("pause", [ad([img("R34.3", "full.png", "pause-fullscreen", "PT3S")], "3431", "Second pause")])

# R34.6 — every entry into a window that is not once-per-session is an execution.
files["R34.6/main.mpd"] = mpd("overlay", [overlay(1, 5000, 5000, f"{APS}/r34-6?w=1", earliestResolutionTimeOffset="0")],
                              "5 s to 10 s, resolved when it fires.")
files["R34.6/first.xml"] = olist("overlay", [ad([img("R34.6", "a.png", "overlay-lower-third")], "346a", "A")], validFor="PT2S")
files["R34.6/second.xml"] = olist("overlay", [ad([img("R34.6", "b.png", "overlay-lower-third")], "346b", "B")])

# R34.9 — a late execution starts from the first candidate.
files["R34.9/main.mpd"] = mpd("overlay", [overlay(1, 10000, 20000, f"{APS}/r34-9?w=1")],
                              "10 s to 30 s; no declaration that a late execution starts with an offset.")
files["R34.9/overlay-list.xml"] = olist("overlay", [
    ad([img("R34.9", "a.png", "overlay-lower-third", "PT10S")], "349a", "A"),
    ad([img("R34.9", "b.png", "overlay-lower-third", "PT10S")], "349b", "B")])

# R34.10 — a resolution that arrives after its window ended.
files["R34.10/main.mpd"] = mpd("overlay", [overlay(1, 5000, 5000, f"{APS}/r34-10?w=1", earliestResolutionTimeOffset="0")],
                               "5 s to 10 s, resolved when it fires.")
files["R34.10/overlay-list.xml"] = olist("overlay", [ad([img("R34.10", "lt.png", "overlay-lower-third")], "3410", "Late")])

# R36.1 — the earliest a resolution may be requested.
files["R36.1/main-declared.mpd"] = mpd("overlay", [overlay(1, 10000, 2000, f"{APS}/r36-1?w=1", earliestResolutionTimeOffset="3000")],
                                       "10 s to 12 s, resolvable from 3 s before its start.")
files["R36.1/main-zero.mpd"] = mpd("overlay", [overlay(1, 10000, 2000, f"{APS}/r36-1?w=2", earliestResolutionTimeOffset="0")],
                                   "10 s to 12 s, resolvable only when it fires.")
files["R36.1/main-default.mpd"] = mpd("overlay", [overlay(1, 65000, 2000, f"{APS}/r36-1?w=3")],
                                      "65 s to 67 s, no offset declared: the default 60 s.")
files["R36.1/empty.xml"] = EMPTY_O

# R36.5 — the held resolution is checked when the opportunity fires.
files["R36.5/main.mpd"] = PAUSE_MAIN
files["R36.5/first.xml"] = olist("pause", [ad([img("R36.5", "a.png", "pause-fullscreen", "PT2S")], "365a", "A")], validFor="PT20S")
files["R36.5/second.xml"] = olist("pause", [ad([img("R36.5", "b.png", "pause-fullscreen", "PT2S")], "365b", "B")], validFor="PT10M")
files["R36.5/empty.xml"] = EMPTY_P

# R38.2 — the declared set, unchanged; nothing when none is declared.
files["R38.2/main.mpd"] = mpd("overlay", [
    overlay(1, 3000, 2000, f"{APS}/r38-2?w=1", earliestResolutionTimeOffset="0",
            allowedLayouts="overlay-corner squeezeback-double-box overlay-lower-third"),
    overlay(2, 6000, 2000, f"{APS}/r38-2?w=2", earliestResolutionTimeOffset="0")],
    "A declared set in an order that is not the tokens' own, then a window\ndeclaring none.")
files["R38.2/empty.xml"] = EMPTY_O

# R39.3 — the custom region goes with the allowed layouts.
files["R39.3/main.mpd"] = mpd("overlay", [
    overlay(1, 3000, 2000, f"{APS}/r39-3?w=1", earliestResolutionTimeOffset="0",
            allowedLayouts="overlay-lower-third custom", customRegion="60 5 35 30")],
    "A window admitting custom inside a region.")
files["R39.3/empty.xml"] = EMPTY_O

# R39.5 — a custom rectangle outside the region is not rendered.
files["R39.5/main-region.mpd"] = mpd("overlay", [
    overlay(1, 5000, 5000, f"{APS}/r39-5?w=1", allowedLayouts="custom overlay-corner", customRegion="50 50 50 50")],
    "5 s to 10 s; custom admitted inside the lower-right quarter.")
files["R39.5/region.xml"] = olist("overlay", [ad([
    img("R39.5", "outside.png", "custom", rect="45 60 20 20"),
    img("R39.5", "inside.png", "custom", rect="60 60 40 40"),
    img("R39.5", "corner.png", "overlay-corner")], "395", "Three placements")])
files["R39.5/main-viewport.mpd"] = mpd("overlay", [
    overlay(1, 5000, 5000, f"{APS}/r39-5?w=2", allowedLayouts="custom overlay-corner")],
    "5 s to 10 s; custom admitted, no region: the region is the viewport.")
files["R39.5/viewport.xml"] = olist("overlay", [ad([
    img("R39.5", "edge.png", "custom", rect="80 0 20 20"),
    img("R39.5", "corner.png", "overlay-corner")], "3952", "Edge of the viewport")])

for rel, text in files.items():
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print(p)
