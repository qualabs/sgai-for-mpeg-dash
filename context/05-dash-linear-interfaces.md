# DASH Linear SGAI — Interfaces and Reference Flows

> Component roles are defined in [`02-actors.md`](02-actors.md); the
> DASH constructs cited below are introduced in
> [`../analysis/dash-gap-analysis.md`](../analysis/dash-gap-analysis.md). Terminology
> follows [`99-glossary.md`](99-glossary.md).

This document is the **reference** for how SGAI is implemented today
for **linear ads** in **MPEG-DASH 6th edition** (ISO/IEC 23009-1,
§5.16 *Alternative MPD Insertion / Replacement Events* and §8.14
*List MPD profile*). It inventories the interfaces between the three
actors, walks through the end-to-end message flow, gives concrete
MPD and ListMPD examples grounded in the spec, and lays out the
VAST → ListMPD adapter mapping that an ADS performs in production.

Spec attribute notation in this document follows the standard
DASH convention: `@attr` denotes an XML attribute, element names
appear capitalised. Inline citations like *(§5.16.4)* refer to
ISO/IEC 23009-1 6th edition.

## Component inventory

The table summarises the producer/consumer role of each actor on each
interface. Responsibilities are pulled verbatim from
[`02-actors.md`](02-actors.md); this is a wiring view, not a
re-definition.

| Actor       | Emits                                                                 | Consumes                                                                 | Notes |
|-------------|-----------------------------------------------------------------------|--------------------------------------------------------------------------|-------|
| Broadcaster | Main MPD with SGAI events (`InsertPresentation`, `ReplacePresentation`) | Nothing at runtime (authoring-time only)                                | Owns the screen; declares slot constraints inside the SGAI event element (§5.16). |
| Player      | MPD fetch request; ADS resolution request at event activation; tracking beacons | Main MPD; `ListMPD` (or single-period alt MPD) from ADS; ad media segments | Enforces R2 / R4: validates ADS response against MPD constraints; caps slot duration. |
| ADS         | `ListMPD` (or single-period alt MPD) in response to the Player's resolution request | Player's resolution request; upstream VAST response from internal ad decisioning | Device-agnostic per the kickoff summary section "Device-aware ad selection" in [`00-kickoff-summary.md`](../.project/decisions/00-kickoff-summary.md). Often acts as an adapter over a VAST-based ad decisioning backend (see §VAST → ListMPD below). |

## Linear SGAI message flow

Once the Player has fetched the main MPD and is playing primary
content, the SGAI linear flow is timeline-triggered: an
`InsertPresentation` or `ReplacePresentation` event scheduled at a
`presentationTime` activates as the playhead approaches it. The
Player resolves the event's `@url` against the ADS, receives back
either a `ListMPD` or a single-period alternative MPD describing one
or more ad MPDs, and plays them according to the event semantics
(insert or replace). `@maxDuration` on the event bounds the slot;
the Player enforces the cap (R4).

```
                                            primary content (Broadcaster's CDN)
                                                       ^
                                                       | (3) GET segments
                                                       |
   +-------------+   (1) GET main MPD     +----------+ | (5) GET ad segments
   | Broadcaster |<-----------------------|          |-+--------------------------> ad CDN
   | (encoder +  |                        |          |
   |  packager + |---(2) MPD (XML) ------>|  Player  |   On ADS response, the Player:
   |   CDN)      |        with            |          |     (6) validates vs MPD constraints
   +-------------+        SGAI event      |          |     (7) enforces @maxDuration (R4)
                                          |          |     (8) fires tracking beacons
                                          +----+-----+
                                            |    ^
                            (4a) GET        |    |  (4b) 200 OK
                          <event @url>?<q>  |    |  ListMPD (XML)
                                            v    |
                                          +----------+   (4c) ad decisioning
                                          |   ADS    |<-----------------------> upstream
                                          | adapter  |   (e.g. VAST 4.x XML)    ad decisioning
                                          +----------+
```

Numbered steps:

1. Player issues `GET` for the main MPD (HTTP, response = DASH XML).
2. Broadcaster serves the MPD, including one or more SGAI events
   inside an `EventStream`. Each `<Event>` carries a child element —
   `<InsertPresentation>` or `<ReplacePresentation>` — that holds
   the SGAI attributes (`@url`, `@maxDuration`,
   `@earliestResolutionTimeOffset`; plus `@returnOffset`,
   `@clipDuration`, `@startWithOffset` on `ReplacePresentation`
   only).
3. Player fetches primary segments and plays the main timeline.
4. As the playhead approaches an event's `presentationTime` minus
   `@earliestResolutionTimeOffset` (the *Earliest Resolution Time*,
   ERT), the Player picks a randomised instant between the ERT and
   the event's `presentationTime` and resolves the ADS:
   (4a) `GET <event @url>` augmented with the query parameters
   declared by the `UrlParamInfo` descriptor on the MPD (§I.4) — see
   the example below for the wiring.
   (4b) ADS replies `200 OK` with a `ListMPD` body (or a single-period
   alt MPD for single-ad slots). The response is the **resolution
   document**.
   (4c) Internally, the ADS adapter typically talks to an upstream
   ad-decisioning system in **VAST**; see VAST → ListMPD section.
5. Player fetches the ad MPDs' segments from the ad CDN(s).
6. Player **validates** each ad candidate against the MPD-declared
   slot constraints (R2). For linear today the relevant checks are
   `@maxDuration` and, where applicable, declared codecs / DRM
   compatibility. Candidates that violate constraints are discarded.
7. Player **enforces** the cumulative duration cap (R4): if the sum
   of the candidates it chose exceeds `@maxDuration`, the Player
   terminates the last ad at the cap (the spec mandates trim,
   §5.16.5).
8. Player fires tracking beacons via callback events
   (`urn:mpeg:dash:event:callback:2015`) embedded inside the ad MPD,
   and/or VAST tracking events translated into callback events by
   the ADS — see VAST → ListMPD section.

At the end of the alternative presentation the Player resumes the
main timeline per the event's semantics: `InsertPresentation`
resumes where the main timeline was paused; `ReplacePresentation`
resumes at the playhead position determined by `@returnOffset`,
because main media time kept advancing while the ad played
(§5.16.4).

R1 graceful degradation applies throughout: a legacy Player that
does not understand the SGAI event scheme ignores the event and
plays the primary content uninterrupted (UC-07).

## Reference XML: main MPD with SGAI events

The main MPD below is the **broadcaster's side** of the contract. It
contains one primary content Period with one AdaptationSet, one
`InsertPresentation` event (pre-roll style, `presentationTime=0`)
and one `ReplacePresentation` event (live mid-roll style,
`presentationTime=PT6M`). At the MPD level, a `UrlParamInfo`
descriptor (§I.4) wires up the query parameters the Player will
append to the ADS resolution request.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns:up="urn:mpeg:dash:schema:urlparam:2025"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd
                         urn:mpeg:dash:schema:urlparam:2025 DASH-MPD-UP.xsd"
     type="dynamic"
     minimumUpdatePeriod="PT2S"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:advanced-linear:2025">

  <!-- §I.4: Extended URL parameterisation for ADS requests -->
  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">
    <up:UrlParamInfo includeInRequests="altmpd"
                     queryTemplate="video_profile=$urn:mpeg:dash:state:video$&amp;session_id=$urn:mpeg:dash:state:cmcd#sid$"/>
  </EssentialProperty>

  <Period id="1" start="PT0S">

    <!-- §5.16.3: InsertPresentation — pre-roll at the start of the timeline -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="101" presentationTime="0" duration="15000">
        <InsertPresentation url="https://ads.example.com/decision/preroll"
                            earliestResolutionTimeOffset="0"
                            maxDuration="15000"/>
      </Event>
    </EventStream>

    <!-- §5.16.4: ReplacePresentation — mid-roll on live -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="102" presentationTime="360000" duration="30000">
        <ReplacePresentation url="https://ads.example.com/decision/midroll"
                             earliestResolutionTimeOffset="60000"
                             maxDuration="30000"
                             returnOffset="0"
                             clipDuration="30000"
                             startWithOffset="false"/>
      </Event>
    </EventStream>

    <!-- Primary content -->
    <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4D401F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>

  </Period>
</MPD>
```

What the Player does with this manifest:

- The two `EventStream` elements expose the SGAI opportunities. The
  scheme URIs `urn:mpeg:dash:event:alternativeMPD:insert:2025` and
  `urn:mpeg:dash:event:alternativeMPD:replace:2025` (§5.16) declare
  the event semantics; a Player that recognises them will resolve
  them, a Player that does not will ignore them (R1).
- For event `101` (`InsertPresentation`), the Player stops the main
  timeline at `presentationTime=0` and switches to the alternative
  presentation returned by the ADS. When the alternative ends, the
  main timeline resumes from the position where it paused (§5.16.3).
- For event `102` (`ReplacePresentation`), the Player computes the
  Earliest Resolution Time as `presentationTime − earliestResolutionTimeOffset`
  = `360000 − 60000 = 300000 ms`. At a randomised instant between the
  ERT and the event's `presentationTime`, the Player issues the ADS
  request. When the ad plays, main media time keeps advancing in
  the background, and at the end the Player resumes at the playhead
  position determined by `@returnOffset` (§5.16.4).
- `@clipDuration` on `ReplacePresentation` ensures that even if the
  event executes late, the ad does not exceed `@maxDuration`
  (§5.16.4). `@startWithOffset` controls whether a delayed ad
  starts from its first frame or skips into the corresponding offset
  to stay aligned with the wall clock.
- The MPD-level `UrlParamInfo` descriptor (§I.4) is consulted at
  resolution time: the Player substitutes the state-vocabulary
  variables (`$urn:mpeg:dash:state:video$`,
  `$urn:mpeg:dash:state:cmcd#sid$`) with live values and appends the
  resulting query string to the `@url`. `@includeInRequests="altmpd"`
  is what scopes this descriptor to the ADS request.

> **Spec attribute pin**: `InsertPresentation` and
> `ReplacePresentation` share `@url`, `@maxDuration`,
> `@earliestResolutionTimeOffset`. The attributes `@returnOffset`,
> `@clipDuration` and `@startWithOffset` are **exclusive to
> `ReplacePresentation`** (§5.16.4 / §5.16.5).

## Reference XML: ListMPD returned by the ADS

The ListMPD below is the **ADS's side** of the contract for a pod of
two ads. It uses the `urn:mpeg:dash:profile:list:2024` profile and
`MPD@type="list"` (§8.14). Each `Period` references a per-ad
sub-MPD via `<ImportedMPD>`. The Player plays the periods
back-to-back in declared order (a ListMPD is a *playlist of MPDs*,
not a candidate set — selection happens upstream, inside the ADS).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     profiles="urn:mpeg:dash:profile:list:2024"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-05-11T16:00:00Z">

  <BaseURL>https://ads.example.com/delivery/</BaseURL>

  <!-- First ad in the pod -->
  <Period id="ad_01" duration="PT15S">
    <ImportedMPD uri="creative_101.mpd" earliestResolutionTimeOffset="0"/>
  </Period>

  <!-- Second ad in the pod -->
  <Period id="ad_02" duration="PT30S">
    <ImportedMPD uri="creative_102.mpd" earliestResolutionTimeOffset="15"/>
  </Period>

</MPD>
```

And the per-ad sub-MPD that the first `ImportedMPD` resolves to,
with the callback `EventStream` carrying VAST-equivalent tracking
beacons (Impression at offset 0, plus start / quartiles / complete
along the 15 s ad):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     profiles="urn:mpeg:dash:profile:sps:2024"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-05-11T16:00:00Z">

  <!-- Single-Period Static Profile (SPS): Period@duration mandatory -->
  <Period id="1" duration="PT15S" start="PT0S">

    <!-- Callback events translated from VAST tracking events.
         timescale=1000 → presentationTime in milliseconds. -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="10">https://tracker.example.com/impression?ad=101</Event>
      <Event presentationTime="0"     id="11">https://tracker.example.com/start?ad=101</Event>
      <Event presentationTime="3750"  id="12">https://tracker.example.com/firstQuartile?ad=101</Event>
      <Event presentationTime="7500"  id="13">https://tracker.example.com/midpoint?ad=101</Event>
      <Event presentationTime="11250" id="14">https://tracker.example.com/thirdQuartile?ad=101</Event>
      <Event presentationTime="15000" id="15">https://tracker.example.com/complete?ad=101</Event>
    </EventStream>

    <AdaptationSet mimeType="video/mp4" codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <Representation id="v1" bandwidth="2500000" width="1280" height="720">
        <BaseURL>media/video_101.mp4</BaseURL>
        <SegmentBase indexRange="0-850"/>
      </Representation>
    </AdaptationSet>
  </Period>
</MPD>
```

What the Player does with these documents:

- The ListMPD declares the **playback order** of the pod: the
  Player plays `ad_01` then `ad_02`, back-to-back. There is no
  candidate selection step at the Player — the ADS already decided
  which ads to deliver and in what order. `Period@duration` is
  declared at the ListMPD level so the Player knows the slot
  arithmetic without first having to fetch each sub-MPD.
- `@earliestResolutionTimeOffset` on each `ImportedMPD` lets the
  Player pre-fetch the sub-MPD ahead of its scheduled position
  inside the pod, smoothing CDN load.
- The Player enforces R4 against the **sum** of the periods'
  durations versus `@maxDuration` on the parent SGAI event:
  15 + 30 = 45 s in this example. If the sum exceeded the parent
  cap, the spec mandates that the Player terminates playback at the
  cap (§5.16.5).
- Inside each sub-MPD, the `EventStream` of scheme
  `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5) instructs
  the Player to fire an HTTP GET to the URL embedded in each
  `<Event>` at the corresponding `presentationTime`. The Player
  treats the response body as a beacon ack — it discards it.

> **Spec note on ListMPD content**: §8.14 does **not** force a
> ListMPD's Periods to use `ImportedMPD`. A ListMPD may also contain
> regular Periods inline (validated against the 6th edition source
> via NotebookLM). The pattern shown above — Periods that delegate to
> per-ad sub-MPDs — is the one this project targets for the linear
> SGAI baseline, because it lets the ADS keep ad metadata sharded
> per creative.

The interfaces above are sufficient for **linear** SGAI, where the
ad's renderable asset is an ISO-BMFF presentation by construction:
the `<ImportedMPD>`-reached sub-MPD is SPS-conformant under §8.15
and therefore bound by RFC 4337 on every Representation's
`@mimeType` (DR-1 in
[`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).
Below this point in the design space, the AdaptationSet /
Representation axis is closed for non-MP4 carriers: per DR-5,
ListMPD-level Periods inherit the CMAF-extension profile and
therefore inherit the same RFC 4337 restriction; per DR-1, sub-MPDs
inherit SPS. The non-linear chapters of the spec MUST therefore
carry non-AV asset URLs (HTML, image, other) outside the
AdaptationSet axis, via one of the carriers enumerated in DR-6.

## VAST → ListMPD conversion

The Player-facing interface in DASH 6th edition is `ListMPD`, but
the de-facto industry ad-decisioning protocol on the upstream side
is **IAB VAST 4.x** (Video Ad Serving Template, XML). Most ADSs in
production today receive ad responses as VAST from one or more
upstream sources (DSPs, ad servers, exchanges). To plug into a DASH
6th edition Player, the ADS must **transform** the upstream VAST
response into a `ListMPD`. This transformation is the central
responsibility of the ADS adapter on linear SGAI integrations.

```
   +----------+   VAST request (HTTP, query params + macros)   +-----------------+
   |   ADS    |----------------------------------------------->|    Upstream     |
   | adapter  |                                                | ad decisioning  |
   |          |<-----------------------------------------------|   (DSP / SSP /  |
   |          |   VAST response (XML, VAST 4.x):               |   ad server)    |
   |          |     - <Ad> (Inline | Wrapper)                  +-----------------+
   |          |     - <Creatives>/<Linear>/<MediaFiles>
   |          |     - <Duration>
   |          |     - <TrackingEvents>, <Impression>,
   |          |       <ClickThrough>
   |          |
   |  TRANSFORM:
   |   * resolve <Wrapper> chains (VAST redirects) until <Inline>
   |   * for each <Ad>, build one ad MPD (or reuse one if pre-conditioned)
   |   * map <MediaFile> -> Representation in an AdaptationSet
   |   * map <Duration> -> Period@duration
   |   * map tracking events -> callback events in the ad MPD
   |   * assemble ImportedMPD entries into a ListMPD (§8.14)
   |
   |          |---ListMPD (XML, DASH 6th ed)----------------------> Player
   +----------+
```

Field-level mapping (subset relevant to linear SGAI; full coverage of
VAST 4.x is out of scope of this document):

| VAST 4.x element                          | ListMPD / ad MPD target                                | Notes |
|-------------------------------------------|--------------------------------------------------------|-------|
| `<Ad>` (Inline)                           | one `<Period>` containing one `<ImportedMPD>` entry in the ListMPD | One Period per Inline ad in the pod. |
| `<Ad>` (Wrapper)                          | resolved recursively; not directly mapped              | Wrapper chains terminate when an Inline is reached or the wrapper limit is hit; depth handling is an ADS adapter concern. |
| `<Creatives>/<Linear>/<Duration>`         | `Period@duration` on the ListMPD-level Period, and `Period@duration` on the sub-MPD | Drives the Player's pre-validation against `@maxDuration` on the parent event. |
| `<MediaFile>` (one per encoding profile)  | one `Representation` inside an `AdaptationSet` of the sub-MPD | `@type`, `@bitrate`, `@width`, `@height`, `@codec` map onto `Representation` attributes. Multiple `<MediaFile>` entries collapse to an ABR ladder. |
| `<TrackingEvents>/<Tracking event="X">`   | inline `EventStream` of scheme `urn:mpeg:dash:event:callback:2015` inside the sub-MPD | Standard VAST event names (`start`, `firstQuartile`, `midpoint`, `thirdQuartile`, `complete`, `pause`, `mute`, …) map to callback events scheduled at the matching media times (§4.7, §5.10.4.5). |
| `<Impression>`                            | callback event at offset `0` inside the sub-MPD        | Fires when ad playback starts. |
| `<ClickThrough>`, `<ClickTracking>`       | no native carrier — sidecar or vendor namespace        | DASH 6th edition defines **no native field** inside ListMPD or the ad MPD for click-through metadata. Validated against the 6th edition source: "The MPEG-DASH 6th edition standard does not define any carrier fields within the MPD for application-level VAST metadata such as Click-through URLs." Production ADS adapters convey clicks via a vendor-namespaced extension element or a sidecar JSON returned alongside the ListMPD; DASH clients are instructed to safely ignore unknown namespaces. |
| `<AdSystem>`, `<AdTitle>`, `<Advertiser>` | no native carrier — sidecar or vendor namespace        | Same conclusion as `<ClickThrough>`: §8.14 confines the spec's tracking footprint to the callback event scheme; AdSystem / AdTitle / Advertiser have no normative slot. Carried as vendor-namespaced attributes / elements or sidecar data. |
| `<UniversalAdId>`                         | no native carrier — sidecar or vendor namespace        | Same conclusion as above: DASH 6th edition defines no `UniversalAdId` carrier on `ImportedMPD` or anywhere else in the ListMPD; in practice ADS adapters carry it as a vendor attribute or sidecar entry. |
| `<Error>`                                 | translated by ADS into an error response               | If the ADS cannot produce a valid `ListMPD`, it returns an HTTP error and/or an empty `ListMPD`; the Player falls through to primary content (R1). |

Edge cases worth flagging:

- **Ad pods (multiple `<Ad>` in one VAST response)**: each Inline
  becomes one `<Period>` (with one `<ImportedMPD>`) in the
  `ListMPD`. Sequence order is preserved. The Broadcaster's
  `@maxDuration` on the parent event caps the **sum** of the pod
  (§5.16.5, §8.14); the Player trims at the cap per R4.
- **Wrapper chains**: resolution happens inside the ADS adapter
  before the Player ever sees the response. The Player has no
  visibility into wrapper hops; this preserves the
  one-request-per-slot contract on the Player ↔ ADS interface.
- **Tracking-only VAST `<Ad>` (no `<MediaFile>`)**: the ADS adapter
  cannot synthesise an ad MPD with no media. The
  industry-convention question — *skip silently vs emit VAST Error
  code 403* — could not be resolved against the 6th edition source
  consulted via NotebookLM (the sources do not cover this). Treat
  this as an ADS-internal policy until a normative reference
  emerges; the resulting `ListMPD` simply omits the entry under the
  silent-skip policy.
- **Empty / no-fill response**: the ADS returns either an empty
  `ListMPD` or an HTTP error; either way the Player falls through to
  primary content (R1 graceful degradation; UC-07-adjacent behaviour
  applies).
- **VAST `<UniversalAdId>`**: lost in translation as far as DASH
  6th edition is concerned (see the field mapping above). ADS
  adapters that need to carry it preserve it on a vendor-namespaced
  attribute / element on the corresponding `ImportedMPD` (or on a
  sidecar payload).

## Interface contracts

| Source           | Target              | Transport      | Format                            | Direction         | Error semantics |
|------------------|---------------------|----------------|-----------------------------------|-------------------|-----------------|
| Player           | Broadcaster CDN     | HTTP/HTTPS     | DASH MPD (XML)                    | request / response (pull) | HTTP status codes; on 4xx/5xx Player retries or aborts session. |
| Player           | Broadcaster CDN     | HTTP/HTTPS     | media segments (ISOBMFF, CMAF, …) | request / response (pull) | HTTP status codes; segment-level retry per DASH-IF guidelines. |
| Player           | ADS                 | HTTP/HTTPS     | request: query params (§I.4); response: `ListMPD` (XML) | request / response (pull, sync) | HTTP status codes; empty `ListMPD` or 4xx/5xx -> Player falls through to primary content. |
| Player           | Ad CDN              | HTTP/HTTPS     | media segments                    | request / response (pull) | Same as Broadcaster CDN; failure of an ad segment skips that ad or aborts the break per Player policy. |
| Player           | Tracking endpoints  | HTTP/HTTPS     | callback beacons (HTTP GET, body-less) | fire-and-forget (push) | Errors are best-effort logged by the Player; not surfaced to viewer. |
| ADS              | Upstream ad decisioning | HTTP/HTTPS | VAST 4.x (XML) request / response | request / response (pull) | VAST `<Error>` element + HTTP status; ADS adapter translates errors into HTTP errors or empty `ListMPD` toward the Player. |

All transport is over HTTPS in production. Authentication, DRM, and
token exchange are out of scope of this document; they layer on top
of HTTPS per DASH-IF guidelines.

## Out of scope (this document)

- Non-linear ad flows. This document is the linear-only baseline.
- Player implementation details (ABR ladder selection, buffer
  policies, segment-level retry, decoder management).
- Auth / DRM / encryption / token-exchange flows — assumed handled
  by HTTPS + DASH-IF / CDN guidance.
- Comprehensive coverage of VAST 4.x. This document covers the
  subset relevant to linear `ListMPD` conversion. Features such as
  VAST verification (`<AdVerifications>`, OMID), companion ads, and
  interactive ad creatives are not enumerated here.

## References

- **FDIS ISO/IEC 23009-1:2025(E), MPEG-DASH 6th edition** —
  *Information technology — Dynamic adaptive streaming over HTTP
  (DASH) — Part 1: Media presentation description and segment
  formats* (currently at FDIS, Final Draft International Standard,
  stage). Canonical:
  <https://standards.iso.org/iso-iec/23009/-1/ed-6/en>. Sections
  cited above: §5.16 Alternative MPD Insertion / Replacement
  Events (§5.16.3 `InsertPresentation`, §5.16.4
  `ReplacePresentation`, §5.16.5 `@maxDuration` trimming rule);
  §8.14 List MPD profile (`urn:mpeg:dash:profile:list:2024`);
  §5.10 EventStream and callback event scheme
  (`urn:mpeg:dash:event:callback:2015`, §4.7 / §5.10.4.5); §I.4
  Extended HTTP GET parametrisation.
- **IAB Tech Lab, VAST 4.x** (Video Ad Serving Template). The exact
  4.x version pin used by current industry practice (4.0 / 4.1 /
  4.2 / 4.3) could not be confirmed against the NotebookLM source
  consulted in this pass; the source material references VAST v3.0
  directly and only mentions 4.2 / 4.3 as placeholders inside the
  CMCD v2 draft. Pin against the IAB Tech Lab spec page on the
  next revision.
  <!-- TODO: pin exact VAST 4.x version against the IAB Tech Lab page; NotebookLM source did not specify it. -->
- [`02-actors.md`](02-actors.md) — actor definitions.
- [`03-requirements.md`](03-requirements.md) — R1, R2, R4 cited above.
- [`../analysis/dash-gap-analysis.md`](../analysis/dash-gap-analysis.md) — DASH
  constructs cited (`InsertPresentation`, `ReplacePresentation`,
  `ListMPD`, `@maxDuration`, callback events, §I.4 vocabulary).
- [`99-glossary.md`](99-glossary.md) — terminology.
- [`00-kickoff-summary.md`](../.project/decisions/00-kickoff-summary.md)
  — kickoff summary; the sections "Three-actor model" and
  "Device-aware ad selection" anchor the Player ↔ ADS contract
  assumed by this document. Original ADRs preserved under
  `.project/decisions/_archive/`.
