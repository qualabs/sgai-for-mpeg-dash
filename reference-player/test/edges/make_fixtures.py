"""Writes the fixtures of the edge vectors (fixtures/). Run once; the
output is committed with the vectors. Media follows the behaviour fixtures'
pattern (2 s segments, mapped by the harness onto its local content)."""
from pathlib import Path

OUT = Path(__file__).parent / "fixtures"
AS_MAIN = """    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
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
    </AdaptationSet>"""
AS_AD = """    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v" bandwidth="1500000" width="960" height="540"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>"""


def main_mpd(name, event):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT2M" minBufferTime="PT2S">
  <BaseURL>https://content.example.com/t05/{name}/</BaseURL>
  <Period id="main" start="PT0S">
{event}
{AS_MAIN}
  </Period>
</MPD>
"""


def ad_mpd(name, secs, beacons, first_id=1):
    evs = "\n".join(f'      <Event presentationTime="{t}" id="{i}">https://t.example.com/t05/{name}/{label}</Event>'
                    for i, (t, label) in enumerate(beacons, first_id))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/t05/{name}/</BaseURL>
  <Period id="{name}" duration="PT{secs}S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
{evs}
    </EventStream>
{AS_AD}
  </Period>
</MPD>
"""


def stream(scheme, eid, pt, dur, child):
    tag = "InsertPresentation" if scheme == "insert" else "ReplacePresentation"
    return f"""    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:{scheme}:2025" timescale="1000">
      <Event id="{eid}" presentationTime="{pt}" duration="{dur}">
        <{tag} {child}/>
      </Event>
    </EventStream>"""


def live_mpd(name):
    """A live alternative (MPD@type "dynamic") with no end: no
    @mediaPresentationDuration, no Period@duration, no MPD update. Its
    availabilityStartTime is long past, so its live edge is wherever the
    machine's clock puts it (a static main gets no utcAtLoad)."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="dynamic"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     availabilityStartTime="2026-01-01T00:00:00Z" publishTime="2026-01-01T00:00:00Z"
     timeShiftBufferDepth="PT30S" minBufferTime="PT2S">
  <BaseURL>https://live-cdn.example.com/t05/{name}/</BaseURL>
  <Period id="{name}" start="PT0S">
{AS_AD}
  </Period>
</MPD>
"""


FILES = {
    # an insertion with no @executeOnce
    "ins-many-main.mpd": main_mpd("ins-many", stream("insert", 1, 2000, 1000,
        'uri="https://aps.example.com/t05/ins-many" earliestResolutionTimeOffset="2000"')),
    # replacements, 8 s alternative, at PRT 2 s, active 10 s
    "rep-noclip-main.mpd": main_mpd("rep-noclip", stream("replace", 1, 2000, 10000,
        'uri="https://aps.example.com/t05/rep" earliestResolutionTimeOffset="2000" maxDuration="6000" clip="false"')),
    "rep-clip-main.mpd": main_mpd("rep-clip", stream("replace", 1, 2000, 10000,
        'uri="https://aps.example.com/t05/rep" earliestResolutionTimeOffset="2000" maxDuration="6000"')),
    "rep-swo-main.mpd": main_mpd("rep-swo", stream("replace", 1, 2000, 10000,
        'uri="https://aps.example.com/t05/rep" earliestResolutionTimeOffset="2000" maxDuration="6000" startWithOffset="true"')),
    "rep-ro-main.mpd": main_mpd("rep-ro", stream("replace", 1, 2000, 10000,
        'uri="https://aps.example.com/t05/rep" earliestResolutionTimeOffset="2000" maxDuration="4000" returnOffset="9000"')),
    "rep-zero-main.mpd": main_mpd("rep-zero", stream("replace", 1, 2000, 10000,
        'uri="https://aps.example.com/t05/rep" earliestResolutionTimeOffset="0" maxDuration="3000"')),
    "rep.mpd": ad_mpd("rep", 8, [(0, "b0"), (2000, "b2"), (5000, "b5")]),
    "ins.mpd": ad_mpd("ins", 4, [(0, "imp")]),
    # a replacement whose @maxDuration equals its 6 s alternative, @clip absent (true),
    # with a callback at the alternative's own end
    "rep-end-main.mpd": main_mpd("rep-end", stream("replace", 1, 2000, 10000,
        'uri="https://aps.example.com/t05/rep-end" earliestResolutionTimeOffset="2000" maxDuration="6000"')),
    "rep-end.mpd": ad_mpd("rep-end", 6, [(0, "start"), (6000, "complete")]),
    # a List MPD whose middle Linked Period does not resolve
    "list-hole-main.mpd": main_mpd("list-hole", stream("insert", 1, 2000, 1000,
        'uri="https://aps.example.com/t05/list-hole" earliestResolutionTimeOffset="2000" executeOnce="true"')),
    "list-hole.mpd": """<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="list"
     profiles="urn:mpeg:dash:profile:list:2024" minBufferTime="PT2S">
  <Period id="la" duration="PT4S">
    <ImportedMPD earliestResolutionTimeOffset="0">https://ads-cdn.example.com/t05/la.mpd</ImportedMPD>
  </Period>
  <Period id="lb" duration="PT4S">
    <ImportedMPD earliestResolutionTimeOffset="2">https://ads-cdn.example.com/t05/lb.mpd</ImportedMPD>
  </Period>
  <Period id="lc" duration="PT4S">
    <ImportedMPD earliestResolutionTimeOffset="4">https://ads-cdn.example.com/t05/lc.mpd</ImportedMPD>
  </Period>
</MPD>
""",
    "la.mpd": ad_mpd("la", 4, [(0, "imp")]),
    # @id 2: the Periods of a List are one presentation, where an @id is not repeated (§5.10.2.4)
    "lc.mpd": ad_mpd("lc", 4, [(0, "imp")], first_id=2),
    # a live alternative (MPD@type "dynamic", no end), replaced or inserted at PRT 2 s
    "live.mpd": live_mpd("live"),
    "rep-live-max-main.mpd": main_mpd("rep-live-max", stream("replace", 1, 2000, 10000,
        'uri="https://aps.example.com/t05/live" earliestResolutionTimeOffset="2000" maxDuration="6000"')),
    "rep-live-swo-main.mpd": main_mpd("rep-live-swo", stream("replace", 1, 2000, 10000,
        'uri="https://aps.example.com/t05/live" earliestResolutionTimeOffset="2000" maxDuration="6000" startWithOffset="true"')),
    "rep-live-nomax-main.mpd": main_mpd("rep-live-nomax", stream("replace", 1, 2000, 10000,
        'uri="https://aps.example.com/t05/live" earliestResolutionTimeOffset="2000"')),
    "ins-live-max-main.mpd": main_mpd("ins-live-max", stream("insert", 1, 2000, 1000,
        'uri="https://aps.example.com/t05/live" earliestResolutionTimeOffset="2000" maxDuration="4000" executeOnce="true"')),
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, text in FILES.items():
        (OUT / name).write_text(text, encoding="utf-8")
    print("\n".join(sorted(FILES)))
