"""Writes the fixtures of T-04 part C under spec-source/behaviour/fixtures/ (run: python3 gen-fixtures.py spec-source/behaviour/fixtures)."""
import os, sys

ROOT = sys.argv[1]  # spec-source/behaviour/fixtures
APS = "https://aps.example.com/beh"
CDN = "https://ads-cdn.example.com/beh"

ADAPT = """    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
"""


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)


def attrs(d):
    return "".join(f'\n{" " * 30}{k}="{v}"' for k, v in d.items())


def overlay_window(eid, pt, dur, uri, cap, **extra):
    a = {"uri": uri, "durationCap": cap}
    a.update({k.replace("_", ""): v for k, v in extra.items()})
    a = {_name(k): v for k, v in a.items()}
    return (f'    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">\n'
            f'      <Event id="{eid}" presentationTime="{pt}" duration="{dur}">\n'
            f'        <svta:OverlayPresentation{attrs(a)}/>\n'
            f'      </Event>\n    </EventStream>\n')


def pause_window(eid, pt, dur, uri, cap, **extra):
    a = {"uri": uri, "durationCap": cap}
    a.update(extra)
    a = {_name(k): v for k, v in a.items()}
    return (f'    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026" timescale="1000">\n'
            f'      <Event id="{eid}" presentationTime="{pt}" duration="{dur}">\n'
            f'        <svta:PauseAdPresentation{attrs(a)}/>\n'
            f'      </Event>\n    </EventStream>\n')


def _name(k):
    return {"ERTO": "earliestResolutionTimeOffset", "allowed": "allowedLayouts",
            "relation": "linearRelation"}.get(k, k)


def linear_event(kind, eid, pt, dur, uri, **extra):
    a = {"uri": uri}
    a.update(extra)
    a = {_name(k): v for k, v in a.items()}
    el = "InsertPresentation" if kind == "insert" else "ReplacePresentation"
    return (f'    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:{kind}:2025"\n'
            f'                 timescale="1000">\n'
            f'      <Event id="{eid}" presentationTime="{pt}" duration="{dur}">\n'
            f'        <{el}{attrs(a)}/>\n'
            f'      </Event>\n    </EventStream>\n')


def metrics(streams):
    if any("sgai-pause-trigger" in x for x in streams):
        return ('  <Metrics metrics="PlayList">\n'
                '    <Reporting schemeIdUri="urn:example:reporting:2026" value="collector-1"/>\n'
                '  </Metrics>\n')
    return ""


def main_mpd(slug, streams, comment, duration="PT2M"):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- {comment} -->
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="{duration}"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/beh/{slug}/</BaseURL>
  <Period id="main" start="PT0S">
{''.join(streams)}{ADAPT}  </Period>
{metrics(streams)}</MPD>
"""


def live_mpd(slug, streams, comment, tsbd="PT5M"):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- {comment} -->
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="dynamic"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     availabilityStartTime="2026-09-26T20:00:00Z"
     publishTime="2026-09-26T20:01:00Z"
     minimumUpdatePeriod="PT2S"
     timeShiftBufferDepth="{tsbd}"
     minBufferTime="PT2S">
  <BaseURL>https://live.example.com/beh/{slug}/</BaseURL>
  <Period id="live" start="PT0S">
{''.join(streams)}{ADAPT}  </Period>
{metrics(streams)}</MPD>
"""


def sps(slug, name, seconds, beacons=()):
    ev = ""
    if beacons:
        lines = "".join(f'      <Event presentationTime="{t}" id="{i}">{u}</Event>\n'
                        for i, (t, u) in enumerate(beacons, 1))
        ev = ('    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"\n'
              '                 timescale="1000">\n' + lines + '    </EventStream>\n')
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>{CDN}/{slug}/{name}/</BaseURL>
  <Period id="{name}" duration="PT{seconds}S">
{ev}    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
"""


def list_mpd(slug, period_id, seconds, sub_url):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="list"
     profiles="urn:mpeg:dash:profile:list:2024"
     minBufferTime="PT2S">
  <Period id="{period_id}" duration="PT{seconds}S">
    <ImportedMPD earliestResolutionTimeOffset="10">{sub_url}</ImportedMPD>
  </Period>
</MPD>
"""


def option(src, mime, layout, duration=None, background=None):
    a = {"src": src, "mimeType": mime}
    if duration is not None:
        a["duration"] = f"PT{duration}S"
    a["layout"] = layout
    if background:
        a["background"] = background
    return f'    <svta:RenderableAsset{attrs(a)}/>\n'


def ad(options, beacons=()):
    tr = ""
    if beacons:
        lines = "".join(f'      <Event presentationTime="{t}" id="{i}">{u}</Event>\n'
                        for i, (t, u) in enumerate(beacons, 1))
        tr = ('    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"\n'
              '                   timescale="1000">\n' + lines + '    </svta:Tracking>\n')
    return "  <svta:Ad>\n" + "".join(options) + tr + "  </svta:Ad>\n"


def overlay_list(family, ads, **extra):
    a = {"family": family}
    a.update(extra)
    head = "".join(f'\n                  {k}="{v}"' for k, v in a.items())
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"{head}>
{''.join(ads)}</svta:OverlayList>
"""


def img(slug, name):
    return f"{CDN}/{slug}/{name}.png"


def html(slug, name):
    return f"{CDN}/{slug}/{name}.html"


def t(slug, what):
    return f"https://t.example.com/{slug}/{what}"


# ---------------------------------------------------------------- R12.5
s = "r12-5"
write("R12.5/main.mpd", main_mpd(s, [overlay_window(1, 2000, 20000, f"{APS}/{s}/overlay", 20000)],
      "R12.5: one overlay window, 2 s to 22 s, family default layouts"))
write("R12.5/overlay.xml", overlay_list("overlay", [
    ad([option(img(s, "overlay"), "image/png", "overlay", 4)]),
    ad([option(img(s, "l-upper-left"), "image/png", "squeezeback-l-shape-upper-left", 4)]),
    ad([option(img(s, "l-upper-right"), "image/png", "squeezeback-l-shape-upper-right", 4)]),
    ad([option(img(s, "double-box"), "image/png", "squeezeback-double-box", 4)]),
    ad([option(img(s, "double-box-bg"), "image/png", "squeezeback-double-box-background", 4,
               background=img(s, "background"))]),
], dismissAfter="never"))
write("R12.5/main-pause.mpd", main_mpd(s, [pause_window(1, 0, 60000, f"{APS}/{s}/pause", 60000)],
      "R12.5: a pause window over the first minute"))
write("R12.5/pause-fullscreen.xml", overlay_list("pause", [
    ad([option(img(s, "pause-full"), "image/png", "pause-fullscreen", 10)])],
    dismissAfter="never", onExhausted="stop"))
write("R12.5/pause-partial.xml", overlay_list("pause", [
    ad([option(img(s, "pause-partial"), "image/png", "pause-partial", 10)])],
    dismissAfter="never", onExhausted="stop"))
write("R12.5/main-takeover.mpd", main_mpd(s, [overlay_window(1, 2000, 10000, f"{APS}/{s}/takeover", 10000,
                                                             allowed="linear")],
      "R12.5: an overlay window admitting only the full-screen takeover"))
write("R12.5/takeover.xml", overlay_list("overlay", [
    ad([option(f"{CDN}/{s}/takeover.mpd", "application/dash+xml", "linear")])], dismissAfter="never"))
write("R12.5/takeover.mpd", sps(s, "takeover", 4))

# ---------------------------------------------------------------- R16.1
s = "r16-1"
write("R16.1/main.mpd", main_mpd(s, [pause_window(1, 0, 60000, f"{APS}/{s}/pause", 60000)],
      "R16.1: a pause window over the first minute"))
write("R16.1/pause.xml", overlay_list("pause", [
    ad([option(img(s, "pause"), "image/png", "pause-fullscreen", 20)])],
    dismissAfter="never", onExhausted="stop"))

# ---------------------------------------------------------------- R17.1 / R17.2
for crit, s, pl in (("R17.1", "r17-1", "pause-partial"), ("R17.2", "r17-2", "pause-fullscreen")):
    write(f"{crit}/main.mpd", main_mpd(s, [
        overlay_window(1, 2000, 10000, f"{APS}/{s}/overlay", 10000),
        pause_window(2, 0, 60000, f"{APS}/{s}/pause", 60000)],
        f"{crit}: an overlay window 2 s to 12 s inside a pause window over the first minute"))
    write(f"{crit}/overlay.xml", overlay_list("overlay", [
        ad([option(img(s, "lower-third"), "image/png", "overlay-lower-third", 10)],
           [(0, t(s, "ov-imp")), (5000, t(s, "ov-mid")), (10000, t(s, "ov-complete"))])],
        dismissAfter="never"))
    write(f"{crit}/pause.xml", overlay_list("pause", [
        ad([option(img(s, "pause"), "image/png", pl, 20)])],
        dismissAfter="never", onExhausted="stop"))

# ---------------------------------------------------------------- R17.5
s = "r17-5"
write("R17.5/main.mpd", main_mpd(s, [
    linear_event("insert", 1, 3000, 1000, f"{APS}/{s}/break", ERTO=3000, maxDuration=10000),
    pause_window(2, 0, 60000, f"{APS}/{s}/pause", 60000, relation="on-top")],
    "R17.5: a 10 s insertion at 3 s, inside an on-top pause window"))
write("R17.5/list.mpd", list_mpd(s, "ad-1", 10, f"{CDN}/{s}/ad.mpd"))
write("R17.5/ad.mpd", sps(s, "ad", 10, [(0, t(s, "imp")), (5000, t(s, "mid")), (10000, t(s, "complete"))]))
write("R17.5/pause.xml", overlay_list("pause", [
    ad([option(img(s, "pause"), "image/png", "pause-fullscreen", 20)])],
    dismissAfter="never", onExhausted="stop"))

# ---------------------------------------------------------------- R19.1
s = "r19-1"
write("R19.1/main.mpd", main_mpd(s, [
    overlay_window(1, 4000, 8000, f"{APS}/{s}/overlay", 8000),
    linear_event("insert", 2, 20000, 1000, f"{APS}/{s}/break", ERTO=10000, maxDuration=8000)],
    "R19.1: a video overlay window 4 s to 12 s, an 8 s insertion at 20 s"))
write("R19.1/overlay.xml", overlay_list("overlay", [
    ad([option(f"{CDN}/{s}/overlay-ad.mpd", "application/dash+xml", "overlay-lower-third")],
       [(0, t(s, "ov-imp")), (4000, t(s, "ov-mid")), (8000, t(s, "ov-complete"))])],
    dismissAfter="never"))
write("R19.1/overlay-ad.mpd", sps(s, "overlay-ad", 8))
write("R19.1/list.mpd", list_mpd(s, "ad-1", 8, f"{CDN}/{s}/break-ad.mpd"))
write("R19.1/break-ad.mpd", sps(s, "break-ad", 8, [(0, t(s, "imp")), (4000, t(s, "mid")), (8000, t(s, "complete"))]))

# ---------------------------------------------------------------- R19.3
s = "r19-3"
write("R19.3/main.mpd", main_mpd(s, [overlay_window(1, 4000, 20000, f"{APS}/{s}/overlay", 8000)],
      "R19.3: an overlay window 4 s to 24 s with a cap of 8 s"))
write("R19.3/overlay.xml", overlay_list("overlay", [
    ad([option(img(s, "a"), "image/png", "overlay-lower-third", 8)],
       [(0, t(s, "a-imp")), (4000, t(s, "a-mid")), (8000, t(s, "a-complete"))]),
    ad([option(img(s, "b"), "image/png", "overlay-lower-third", 8)],
       [(0, t(s, "b-imp"))])], dismissAfter="never"))

# ---------------------------------------------------------------- R22.1
s = "r22-1"
write("R22.1/main.mpd", main_mpd(s, [overlay_window(1, 2000, 12000, f"{APS}/{s}/overlay", 12000)],
      "R22.1: one overlay window, 2 s to 14 s"))
write("R22.1/overlay.xml", overlay_list("overlay", [
    ad([option(img(s, "a"), "image/png", "overlay-lower-third", 4)],
       [(0, t(s, "a-imp")), (4000, t(s, "a-complete"))]),
    ad([option(img(s, "b"), "image/png", "overlay-corner", 4)],
       [(0, t(s, "b-imp")), (4000, t(s, "b-complete"))])], dismissAfter="never"))

# ---------------------------------------------------------------- R25.1
s = "r25-1"
write("R25.1/live.mpd", live_mpd(s, [
    pause_window(1, 60000, 30000, f"{APS}/{s}/pause", 60000, ERTO=0)],
    "R25.1: a live channel with a pause window from 60 s to 90 s of its timeline"))
write("R25.1/pause.xml", overlay_list("pause", [
    ad([option(img(s, "pause"), "image/png", "pause-partial", 20)])],
    dismissAfter="never", onExhausted="stop"))

# ---------------------------------------------------------------- R26.1
s = "r26-1"
write("R26.1/main.mpd", main_mpd(s, [overlay_window(1, 2000, 8000, f"{APS}/{s}/overlay", 8000)],
      "R26.1: one overlay window, 2 s to 10 s"))
write("R26.1/overlay.xml", overlay_list("overlay", [
    ad([option(img(s, "box"), "image/png", "squeezeback-double-box", 4)]),
    ad([option(img(s, "box-bg"), "image/png", "squeezeback-double-box-background", 4,
               background=img(s, "background"))])], dismissAfter="never"))

# ---------------------------------------------------------------- R26.3
s = "r26-3"
write("R26.3/main.mpd", main_mpd(s, [overlay_window(1, 2000, 4000, f"{APS}/{s}/overlay", 4000)],
      "R26.3: one overlay window, 2 s to 6 s"))
write("R26.3/overlay.xml", overlay_list("overlay", [
    ad([option(f"{CDN}/{s}/box-ad.mpd", "application/dash+xml", "squeezeback-double-box-background",
               background=img(s, "background")),
        option(f"{CDN}/{s}/box-ad.mpd", "application/dash+xml", "squeezeback-double-box"),
        option(img(s, "box"), "image/png", "squeezeback-double-box-background", 4,
               background=img(s, "background"))])], dismissAfter="never"))
write("R26.3/box-ad.mpd", sps(s, "box-ad", 4))

# ---------------------------------------------------------------- R27.1
s = "r27-1"
write("R27.1/main.mpd", main_mpd(s, [overlay_window(1, 2000, 4000, f"{APS}/{s}/overlay", 4000)],
      "R27.1: one overlay window, 2 s to 6 s"))
write("R27.1/overlay.xml", overlay_list("overlay", [
    ad([option(html(s, "l-shape"), "text/html", "squeezeback-l-shape-upper-right", 4)])],
    dismissAfter="never"))

# ---------------------------------------------------------------- R27.3
s = "r27-3"
write("R27.3/main.mpd", main_mpd(s, [overlay_window(1, 2000, 4000, f"{APS}/{s}/overlay", 4000)],
      "R27.3: one overlay window, 2 s to 6 s"))
write("R27.3/overlay.xml", overlay_list("overlay", [
    ad([option(f"{CDN}/{s}/l-shape-ad.mpd", "application/dash+xml", "squeezeback-l-shape-upper-left"),
        option(html(s, "l-shape"), "text/html", "squeezeback-l-shape-upper-left", 4),
        option(img(s, "l-shape"), "image/png", "squeezeback-l-shape-upper-left", 4)])],
    dismissAfter="never"))
write("R27.3/l-shape-ad.mpd", sps(s, "l-shape-ad", 4))

# ---------------------------------------------------------------- R31.2
s = "r31-2"
write("R31.2/main.mpd", main_mpd(s, [pause_window(1, 0, 60000, f"{APS}/{s}/pause", 2000)],
      "R31.2: a pause window over the first minute, with a cap of 2 s"))
write("R31.2/pause.xml", overlay_list("pause", [
    ad([option(img(s, "pause"), "image/png", "pause-partial", 6)],
       [(0, t(s, "imp")), (3000, t(s, "mid")), (6000, t(s, "complete"))])],
    dismissAfter="never", onExhausted="stop"))

# ---------------------------------------------------------------- R35.4
s = "r35-4"
write("R35.4/main.mpd", main_mpd(s, [overlay_window(1, 2000, 12000, f"{APS}/{s}/overlay", 12000)],
      "R35.4: one overlay window, 2 s to 14 s"))
write("R35.4/overlay.xml", overlay_list("overlay", [
    ad([option(img(s, "a"), "image/png", "overlay-lower-third", 6)],
       [(0, t(s, "a-imp")), (3000, t(s, "a-mid")), (6000, t(s, "a-complete"))]),
    ad([option(img(s, "b"), "image/png", "overlay-lower-third", 6)],
       [(0, t(s, "b-imp")), (6000, t(s, "b-complete"))])], dismissAfter="PT0S"))
write("R35.4/main-pause.mpd", main_mpd(s, [pause_window(1, 0, 60000, f"{APS}/{s}/pause", 60000)],
      "R35.4: a pause window over the first minute"))
write("R35.4/pause.xml", overlay_list("pause", [
    ad([option(img(s, "pa"), "image/png", "pause-partial", 4)],
       [(0, t(s, "pa-imp")), (2000, t(s, "pa-mid"))]),
    ad([option(img(s, "pb"), "image/png", "pause-partial", 4)],
       [(0, t(s, "pb-imp"))])], dismissAfter="PT0S", onExhausted="request-again"))

# ---------------------------------------------------------------- R35.5
s = "r35-5"
write("R35.5/main.mpd", main_mpd(s, [overlay_window(1, 2000, 10000, f"{APS}/{s}/overlay", 10000,
                                                    allowed="linear")],
      "R35.5: an overlay window admitting only the full-screen takeover, 2 s to 12 s"))
write("R35.5/overlay.xml", overlay_list("overlay", [
    ad([option(f"{CDN}/{s}/takeover.mpd", "application/dash+xml", "linear")])], dismissAfter="PT0S"))
write("R35.5/takeover.mpd", sps(s, "takeover", 8))

# ---------------------------------------------------------------- R37.2
s = "r37-2"
write("R37.2/main.mpd", main_mpd(s, [pause_window(1, 0, 60000, f"{APS}/{s}/pause", 60000)],
      "R37.2: a pause window over the first minute"))
write("R37.2/pause.xml", overlay_list("pause", [
    ad([option(img(s, "pause"), "image/png", "pause-fullscreen", 10)])],
    dismissAfter="never", onExhausted="stop"))

# ---------------------------------------------------------------- R40.4
s = "r40-4"
write("R40.4/main.mpd", main_mpd(s, [
    overlay_window(1, 2000, 20000, f"{APS}/{s}/overlay", 20000),
    linear_event("insert", 2, 6000, 1000, f"{APS}/{s}/break", ERTO=4000, maxDuration=6000)],
    "R40.4: an overlay window 2 s to 22 s, no relation; a 6 s insertion at 6 s"))
write("R40.4/overlay.xml", overlay_list("overlay", [
    ad([option(img(s, "a"), "image/png", "overlay-lower-third", 8)],
       [(0, t(s, "a-imp")), (2000, t(s, "a-2s")), (8000, t(s, "a-complete"))]),
    ad([option(img(s, "b"), "image/png", "overlay-lower-third", 8)],
       [(0, t(s, "b-imp")), (8000, t(s, "b-complete"))])], dismissAfter="never"))
write("R40.4/list.mpd", list_mpd(s, "ad-1", 6, f"{CDN}/{s}/ad.mpd"))
write("R40.4/ad.mpd", sps(s, "ad", 6, [(0, t(s, "imp")), (6000, t(s, "complete"))]))
write("R40.4/main-replace.mpd", main_mpd(s, [
    overlay_window(1, 2000, 6000, f"{APS}/{s}/overlay-r", 6000),
    linear_event("replace", 2, 4000, 1000, f"{APS}/{s}/replace", ERTO=4000, maxDuration=6000)],
    "R40.4: an overlay window 2 s to 8 s, no relation; a 6 s replacement at 4 s that returns at 10 s"))
write("R40.4/overlay-r.xml", overlay_list("overlay", [
    ad([option(img(s, "r"), "image/png", "overlay-lower-third", 6)],
       [(0, t(s, "r-imp")), (6000, t(s, "r-complete"))])], dismissAfter="never"))

# ---------------------------------------------------------------- R40.5
s = "r40-5"
write("R40.5/main-cap.mpd", main_mpd(s, [
    linear_event("insert", 1, 4000, 1000, f"{APS}/{s}/break", ERTO=4000, maxDuration=10000),
    overlay_window(2, 4000, 10000, f"{APS}/{s}/overlay", 6000, relation="on-top")],
    "R40.5: a 10 s insertion at 4 s under an on-top overlay window 4 s to 14 s, cap 6 s"))
write("R40.5/overlay.xml", overlay_list("overlay", [
    ad([option(img(s, "a"), "image/png", "overlay-lower-third", 15)],
       [(0, t(s, "a-imp")), (3000, t(s, "a-3s")), (9000, t(s, "a-9s"))])], dismissAfter="never"))
write("R40.5/list.mpd", list_mpd(s, "ad-1", 10, f"{CDN}/{s}/ad.mpd"))
write("R40.5/ad.mpd", sps(s, "ad", 10, [(0, t(s, "imp")), (10000, t(s, "complete"))]))
write("R40.5/main-end.mpd", main_mpd(s, [
    linear_event("insert", 1, 4000, 1000, f"{APS}/{s}/break-short", ERTO=4000, maxDuration=6000),
    overlay_window(2, 2000, 4000, f"{APS}/{s}/overlay", 20000, relation="on-top")],
    "R40.5: a 6 s insertion at 4 s under an on-top overlay window 2 s to 6 s, cap 20 s"))
write("R40.5/list-short.mpd", list_mpd(s, "ad-2", 6, f"{CDN}/{s}/ad-short.mpd"))
write("R40.5/ad-short.mpd", sps(s, "ad-short", 6, [(0, t(s, "short-imp")), (6000, t(s, "short-complete"))]))

# ---------------------------------------------------------------- R40.6
s = "r40-6"
write("R40.6/main.mpd", main_mpd(s, [
    linear_event("insert", 1, 2000, 1000, f"{APS}/{s}/alt", ERTO=2000, maxDuration=10000)],
    "R40.6: a 10 s insertion at 2 s whose alternative MPD declares an overlay window"))
write("R40.6/alt.mpd", main_mpd(s + "/alt", [overlay_window(1, 2000, 4000, f"{APS}/{s}/overlay", 4000)],
      "R40.6: the alternative presentation, 10 s, with its own overlay window 2 s to 6 s",
      duration="PT10S"))
write("R40.6/overlay.xml", overlay_list("overlay", [
    ad([option(img(s, "a"), "image/png", "overlay-lower-third", 4)],
       [(0, t(s, "a-imp")), (4000, t(s, "a-complete"))])], dismissAfter="never"))

# ---------------------------------------------------------------- R40.9
s = "r40-9"
write("R40.9/main-anchor.mpd", main_mpd(s, [
    overlay_window(1, 2000, 4000, f"{APS}/{s}/overlay", 10000),
    pause_window(2, 10000, 4000, f"{APS}/{s}/pause", 60000, ERTO=0)],
    "R40.9: an overlay window 2 s to 6 s, cap 10 s; a pause window 10 s to 14 s"))
write("R40.9/overlay.xml", overlay_list("overlay", [
    ad([option(img(s, "a"), "image/png", "overlay-lower-third", 10)],
       [(0, t(s, "a-imp")), (3000, t(s, "a-3s")), (5000, t(s, "a-5s"))])], dismissAfter="never"))
write("R40.9/pause.xml", overlay_list("pause", [
    ad([option(img(s, "pause"), "image/png", "pause-fullscreen", 10)])],
    dismissAfter="never", onExhausted="stop"))
write("R40.9/main-supersede.mpd", main_mpd(s, [
    overlay_window(1, 2000, 10000, f"{APS}/{s}/overlay-s", 10000, relation="supersede"),
    linear_event("insert", 2, 6000, 1000, f"{APS}/{s}/break", ERTO=0, maxDuration=6000)],
    "R40.9: a superseding overlay window 2 s to 12 s over a 6 s insertion at 6 s"))
write("R40.9/overlay-s.xml", overlay_list("overlay", [
    ad([option(img(s, "s"), "image/png", "overlay-lower-third", 10)],
       [(0, t(s, "s-imp")), (10000, t(s, "s-complete"))])], dismissAfter="never"))
write("R40.9/list.mpd", list_mpd(s, "ad-1", 6, f"{CDN}/{s}/ad.mpd"))
write("R40.9/ad.mpd", sps(s, "ad", 6, [(0, t(s, "imp")), (6000, t(s, "complete"))]))
print("ok")
