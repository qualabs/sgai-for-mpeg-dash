# DASH Linear SGAI — Interfaces and Reference Flows

> Component roles are defined in [`02-actors.md`](02-actors.md). The
> DASH constructs cited below are part of the MPEG-DASH 6th edition
> baseline (ISO/IEC 23009-1, §5.16 and §8.14). Terminology follows
> [`99-glossary.md`](99-glossary.md).

**This document is informative.** It records how the deployed ecosystem
works today; it constrains no implementation and defines no semantics.
Everything normative lives in [`03-requirements.md`](03-requirements.md)
and [`08-dash-extension-rules.md`](08-dash-extension-rules.md). It is
here, and not in an annex, because the build reads it as an input: the
VAST-to-ListMPD mapping below is what an APS does in production, and a
specification written without it would be designing against a market
that does not exist.

This document is the **reference** for how SGAI is implemented today
for **linear ads** in **MPEG-DASH 6th edition** (ISO/IEC 23009-1,
§5.16 *Alternative MPD Insertion / Replacement Events* and §8.14
*List MPD profile*). It inventories the interfaces between the
actors, walks through the end-to-end message flow, gives concrete
MPD and ListMPD examples grounded in the spec, and lays out the
VAST → ListMPD adapter mapping that an APS performs in production
(converting the VAST the ADS emits into the ListMPD the Player
reads).

Spec attribute notation in this document follows the standard
DASH convention: `@attr` denotes an XML attribute, element names
appear capitalised. Inline citations like *(§5.16.4)* refer to
ISO/IEC 23009-1 6th edition.

## Component inventory

The table summarises the producer/consumer role of each actor on each
interface. Responsibilities are pulled verbatim from
[`02-actors.md`](02-actors.md); this is a wiring view, not a
re-definition.

| Actor     | Emits                                                                 | Consumes                                                                 | Notes |
|-----------|-----------------------------------------------------------------------|--------------------------------------------------------------------------|-------|
| Publisher | Main MPD with SGAI events (`InsertPresentation`, `ReplacePresentation`) | Nothing at runtime (authoring-time only)                                | Owns the screen; declares slot constraints inside the SGAI event element (§5.16). The event `@uri` resolves to the APS. |
| Player    | MPD fetch request; APS resolution request at event activation; tracking beacons | Main MPD; `ListMPD` (or single-period alt MPD) from APS; ad media segments | Enforces R2 / R4: validates the APS-returned resolution document against MPD constraints; caps slot duration. Talks only to the APS, never to the ADS directly. |
| APS       | `ListMPD` (or single-period alt MPD) in response to the Player's resolution request | Player's resolution request; VAST response from the ADS | The Player-facing adapter: returns candidates with one or more renderable forms — several is the form R5 asks for, and an APS with a view of the device narrows the list and MAY send a single form, the choice then sitting with it — and the Player picks per device capabilities (R5 in [`03-requirements.md`](03-requirements.md)). Converts the ADS's VAST into the resolution document (see §VAST → ListMPD below). |
| ADS       | VAST 4.x (the ad decision) in response to the APS's request | The APS's ad request | The ad-decisioning authority: selects which ads, how many, in what order; owns the tracking schedule. Outputs VAST; does NOT produce the DASH-native resolution document (that is the APS). |

## Publisher slot-mechanism choice — Insert vs Replace

The Publisher declares a linear slot via one of two MPEG-DASH 6th
edition mechanisms:

- **`InsertPresentation`** introduces the ad as new content that
  does NOT consume any of the primary timeline. After the ad,
  primary content continues from where it was. **ONLY applicable to
  VOD content** — per MPEG-DASH 6th edition §5.16.3, the event
  "shall not appear if the MPD type is `dynamic`". It is intended
  for an operation where the playhead can be stopped for an
  indefinite period, which can typically only happen in an
  on-demand or pre-recorded operation.
- **`ReplacePresentation`** substitutes a bounded span of the
  primary timeline with the ad. The primary content under the ad
  span is effectively skipped. Per §5.16.4 it *"can be used with both
  static and dynamic MPDs"*, so it is the mechanism for live
  content: §5.16.1 describes it as replacing *"a portion of the
  timeline in a main live presentation"*.

The choice is captured in the slot's MPD declaration and is
Publisher-decided per content type and intent. The Use Cases in
[`04-use-cases.md`](04-use-cases.md) describe observable behaviour
and are agnostic to the mechanism; both produce a linear ad from
the user's perspective.

## Linear SGAI message flow

Once the Player has fetched the main MPD and is playing primary
content, the SGAI linear flow is timeline-triggered: an
`InsertPresentation` or `ReplacePresentation` event scheduled at a
`presentationTime` activates as the playhead approaches it. The
Player resolves the event's `@uri` against the APS, receives back
either a `ListMPD` or a single-period alternative MPD describing one
or more ad MPDs, and plays them according to the event semantics
(insert or replace). Behind the APS, the ADS performs the ad
decisioning and returns VAST; the APS converts that VAST into the
resolution document the Player reads. `@maxDuration` on the event
bounds the slot; the Player enforces the cap (R4).

```
                                            primary content (Publisher's CDN)
                                                       ^
                                                       | (3) GET segments
                                                       |
   +-------------+   (1) GET main MPD     +----------+ | (5) GET ad segments
   | Publisher   |<-----------------------|          |-+--------------------------> ad CDN
   | (encoder +  |                        |          |
   |  packager + |---(2) MPD (XML) ------>|  Player  |   On APS response, the Player:
   |   CDN)      |        with            |          |     (6) validates vs MPD constraints
   +-------------+        SGAI event      |          |     (7) enforces @maxDuration (R4)
                                          |          |     (8) fires tracking beacons
                                          +----+-----+
                                            |    ^
                            (4a) GET        |    |  (4b) 200 OK
                          <event @uri>?<q>  |    |  ListMPD (XML)
                                            v    |
                                          +----------+   (4c) ad decisioning
                                          |   APS    |<-----------------------> ADS
                                          | (adapter)|   (e.g. VAST 4.x XML)
                                          +----------+
```

Numbered steps:

1. Player issues `GET` for the main MPD (HTTP, response = DASH XML).
2. Publisher serves the MPD, including one or more SGAI events
   inside an `EventStream`. Each `<Event>` carries a child element —
   `<InsertPresentation>` or `<ReplacePresentation>` — that holds
   the SGAI attributes (`@uri`, `@maxDuration`,
   `@earliestResolutionTimeOffset`; plus `@returnOffset`,
   `@clip`, `@startWithOffset` on `ReplacePresentation`
   only). The `@uri` resolves to the APS.
3. Player fetches primary segments and plays the main timeline.
4. As the playhead approaches an event's `presentationTime` minus
   `@earliestResolutionTimeOffset` (the *Earliest Resolution Time*,
   ERT), the Player picks a randomised instant between the ERT and
   the event's `presentationTime` and resolves the APS:
   (4a) `GET <event @uri>` augmented with the query parameters
   declared by a `RequestParam` element (Annex I.3) — see the
   example below for the wiring.
   (4b) APS replies `200 OK` with a `ListMPD` body (or a single-period
   alt MPD for single-ad slots). The response is the **resolution
   document**.
   (4c) Internally, the APS typically talks to the ADS — an upstream
   ad-decisioning system that responds in **VAST**; see
   VAST → ListMPD section.
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
   i.e. the ADS's VAST tracking events translated into callback
   events by the APS — see VAST → ListMPD section.

At the end of the alternative presentation the Player resumes the
main timeline per the event's semantics: `InsertPresentation`
resumes where the main timeline was paused; `ReplacePresentation`
resumes at the playhead position determined by `@returnOffset`,
because main media time kept advancing while the ad played
(§5.16.4).

R1 graceful degradation applies throughout: a legacy Player that
does not understand the SGAI event scheme ignores the event and
plays the primary content uninterrupted (UC-07).

## Resolution document timing baseline

All `<Event @presentationTime>` values authored by the APS within
the resolution document (`ListMPD` or single-period alt MPD) are
expressed **relative to the start of the ad break** (slot start),
not relative to wall-clock or to the primary content timeline. A
callback event scheduled for the very start of the break declares
`@presentationTime="0"`. Quartile beacons for a 30-second slot are
authored at 7500ms, 15000ms, 22500ms (per the ADS's chosen
schedule, which the APS transcribes into the resolution document).
The Player applies these relative timings against the
slot window the Publisher declared in the MPD event.

## Reference XML: main MPD with SGAI events

The main MPD below is the **Publisher's side** of the contract for a
**live** service. It contains one primary content Period with one
AdaptationSet and two `ReplacePresentation` events: a first break at
`presentationTime=PT2M` and a mid-roll at `presentationTime=PT6M`.
Both are replacement events because the MPD is `type="dynamic"`: an
`InsertPresentation` *"shall not appear if the MPD type is
"dynamic""* (§5.16.3), while the replacement event *"can be used
with both static and dynamic MPDs"* (§5.16.4). The two events share
one `EventStream`, because a Period holds *"at most one EventStream
element with the same value of the @schemeIdUri attribute and the
value of the @value attribute"* (§5.10.2.1). A `RequestParam` on
that `EventStream` wires up the query parameters the Player will
append to the APS resolution request (Annex I.3).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="dynamic"
     minimumUpdatePeriod="PT2S"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:advanced-linear:2025">

  <Period id="1" start="PT0S">

    <!-- §5.16.4: ReplacePresentation — the only alternative-MPD event a dynamic MPD admits -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="101" presentationTime="120000" duration="15000">
        <ReplacePresentation uri="https://ads.example.com/decision/break-1"
                             earliestResolutionTimeOffset="30000"
                             maxDuration="15000"/>
      </Event>
      <Event id="102" presentationTime="360000" duration="30000">
        <ReplacePresentation uri="https://ads.example.com/decision/midroll"
                             earliestResolutionTimeOffset="60000"
                             maxDuration="30000"
                             returnOffset="0"
                             clip="true"
                             startWithOffset="false"/>
      </Event>
      <!-- Annex I.3: URL parameters for the APS resolution request -->
      <RequestParam includeInRequests="altmpd"
                    queryTemplate="video_profile=$urn:mpeg:dash:state:video$&amp;session_id=$urn:mpeg:dash:state:cmcd#sid$"/>
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

  <!-- Annex I.3.1: the URL-parameter scheme, declared with no content -->
  <SupplementalProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>
</MPD>
```

What the Player does with this manifest:

- The `EventStream` exposes the SGAI opportunities. The scheme URI
  `urn:mpeg:dash:event:alternativeMPD:replace:2025` (§5.16.4)
  declares the event semantics; a Player that recognises it will
  resolve the events, a Player that does not will ignore them (R1).
- For each event the Player computes the Earliest Resolution Time as
  `presentationTime − earliestResolutionTimeOffset`: `120000 − 30000
  = 90000 ms` for event `101`, `360000 − 60000 = 300000 ms` for event
  `102`. At a randomised instant between the ERT and the event's
  `presentationTime`, the Player issues the APS request. While the ad
  plays, main media time keeps advancing in the background, and at the
  end the Player resumes at the playhead position determined by
  `@returnOffset` (§5.16.4).
- `@clip` on `ReplacePresentation` is a boolean, default `true`: when
  set, an ad whose event executes late is trimmed so that it does not
  exceed `@maxDuration` (§5.16.4). It carries no duration of its own.
  `@startWithOffset` controls whether a delayed ad starts from its
  first frame or skips into the corresponding offset to stay aligned
  with the wall clock.
- The `RequestParam` element (Annex I.3, of type
  `ExtendedUrlInfoType`) is consulted at resolution time: the Player
  substitutes the state-vocabulary variables of Annex I.4
  (`$urn:mpeg:dash:state:video$`, `$urn:mpeg:dash:state:cmcd#sid$`)
  with live values and appends the resulting query string to the
  `@uri`. `@includeInRequests="altmpd"` is what scopes it to the APS
  resolution request, and the Advanced Linear profile admits it on an
  `EventStream` carrying alternative-MPD events (§8.13.2.4).
  `RequestParam` is defined in the main DASH schema, so it needs no
  namespace of its own. The MPD-level descriptor names the scheme and
  has no content (Annex I.3.1); it is a `SupplementalProperty` so that
  a Player that does not recognise the scheme drops the descriptor and
  not the MPD (see [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md)).
- In a **static** (on-demand) MPD the same breaks could be authored as
  `InsertPresentation` events under
  `urn:mpeg:dash:event:alternativeMPD:insert:2025` (§5.16.3). The
  Player then stops the main timeline at the event's
  `presentationTime`, plays the alternative presentation, and resumes
  the main timeline from the position where it paused.

> **Spec attribute pin**: `InsertPresentation` and
> `ReplacePresentation` share `@uri`, `@maxDuration`,
> `@earliestResolutionTimeOffset`. The attributes `@returnOffset`,
> `@clip` and `@startWithOffset` are **exclusive to
> `ReplacePresentation`** (§5.16.4 / §5.16.5).

## Reference XML: ListMPD returned by the APS

The ListMPD below is the **APS's side** of the contract for a pod of
two ads (the APS produced it from the ADS's VAST). It uses the
`urn:mpeg:dash:profile:list:2024` profile and `MPD@type="list"`
(§8.14). Each `Period` references a per-ad sub-MPD via
`<ImportedMPD>`. The Player plays the periods back-to-back in
declared order (a ListMPD is a *playlist of MPDs*, not a candidate
set — the ad selection and ordering happened upstream, inside the
ADS, and the APS transcribed them into this document).

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
    <ImportedMPD earliestResolutionTimeOffset="0">creative_101.mpd</ImportedMPD>
  </Period>

  <!-- Second ad in the pod -->
  <Period id="ad_02" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="15">creative_102.mpd</ImportedMPD>
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
> ListMPD's Periods to use `ImportedMPD`. Its rule 4 says so directly:
> *"List MPDs may contain one or more Linked Periods (see 5.3.2.6),
> however it may also contain regular Periods."* The pattern shown
> above — Periods that delegate to
> per-ad sub-MPDs — is the one this project targets for the linear
> SGAI baseline, because it lets the APS keep ad metadata sharded
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
is **IAB VAST 4.x** (Video Ad Serving Template, XML). The ADS
decides which ads to serve and responds in VAST; it may itself
front one or more upstream sources (DSPs, ad servers, exchanges). To
plug into a DASH 6th edition Player, the **APS** must **transform**
the ADS's VAST response into a `ListMPD`. This transformation is the
central responsibility of the APS on linear SGAI integrations.

```
   +----------+   VAST request (HTTP, query params + macros)   +-----------------+
   |   APS    |----------------------------------------------->|      ADS        |
   | (adapter)|                                                | ad decisioning  |
   |          |<-----------------------------------------------|   (may front    |
   |          |   VAST response (XML, VAST 4.x):               |   DSP / SSP /   |
   |          |     - <Ad> (Inline | Wrapper)                  |   ad server)    |
   |          |     - <Creatives>/<Linear>/<MediaFiles>        +-----------------+
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
| `<Ad>` (Wrapper)                          | resolved recursively; not directly mapped              | Wrapper chains terminate when an Inline is reached or the wrapper limit is hit; depth handling is an APS concern. |
| `<Creatives>/<Linear>/<Duration>`         | `Period@duration` on the ListMPD-level Period, and `Period@duration` on the sub-MPD | Drives the Player's pre-validation against `@maxDuration` on the parent event. |
| `<MediaFile>` (one per encoding profile)  | one `Representation` inside an `AdaptationSet` of the sub-MPD | `@type`, `@bitrate`, `@width`, `@height`, `@codec` map onto `Representation` attributes. Multiple `<MediaFile>` entries collapse to an ABR ladder. |
| `<TrackingEvents>/<Tracking event="X">`   | inline `EventStream` of scheme `urn:mpeg:dash:event:callback:2015` inside the sub-MPD | Standard VAST event names (`start`, `firstQuartile`, `midpoint`, `thirdQuartile`, `complete`, `pause`, `mute`, …) map to callback events scheduled at the matching media times (§4.7, §5.10.4.5). |
| `<Impression>`                            | callback event at offset `0` inside the sub-MPD        | Fires when ad playback starts. |
| `<ClickThrough>`, `<ClickTracking>`       | normative ClickThrough carrier defined by this spec (R28); ClickThrough URL and its click-tracking URL(s) carried together in that carrier; click-tracking fired on user click, not via the callback timeline | DASH 6th edition defines **no native field** inside ListMPD or the ad MPD for click-through metadata. Validated against the 6th edition source: "The MPEG-DASH 6th edition standard does not define any carrier fields within the MPD for application-level VAST metadata such as Click-through URLs." This spec closes that gap: R28 requires a **normative, interoperable** carrier that holds the ClickThrough URL together with its associated `<ClickTracking>` URL(s), so every Player conformant to this specification reads them the same way. The click-tracking is NOT carried by the callback event scheme: a ClickThrough activation is a user interaction with no presentation time, and DASH defines no user-triggered event (DASH events are timeline-scheduled and the callback fires its HTTP GET at the scheduled presentation time, ISO/IEC 23009-1 §5.10.1; §5.10.4.5.3 / Table 47). A Player conformant to this specification therefore fires the click-tracking when the viewer activates the ClickThrough. DASH follows the same split in its interactive nonlinear-playback scheme (`urn:mpeg:dash:nonlinearplayback:2020`), where the event is anchored to the timeline while the user interaction is handled outside the timeline trigger. This is deliberately stronger than the best-effort carrier used for generic metadata (R23): a Player conformant to this specification MUST read the ClickThrough carrier, where it MAY ignore the R23 metadata. |
| `<AdSystem>`, `<AdTitle>`, `<Advertiser>` | no native carrier — best-effort SVTA-namespaced carrier (R23) | DASH 6th edition defines no native slot for these generic metadata fields, and §8.14 confines the spec's tracking footprint to the callback event scheme. They fall under the best-effort carrier of R23: carried as SVTA Ads WG namespaced attributes / elements that a Player MAY safely ignore. Unlike `<ClickThrough>` (R28), no interoperable carrier is mandated for them — dropping them breaks nothing in the ad presentation. |
| `<UniversalAdId>`                         | out of scope of the DASH carrier — stays VAST / ADS side | DASH 6th edition defines no `UniversalAdId` carrier, and this spec deliberately does not add one. The universal ad identifier is used for ad tracking and reconciliation on the ADS / VAST side; that tracking is handled by VAST, not by the DASH resolution document. It is therefore intentionally left in the VAST / ADS domain and is out of scope of the DASH carrier defined by this spec. An APS that still wants to propagate it MAY do so on a best-effort SVTA-namespaced attribute (R23), but the spec mandates no carrier for it. |
| `<Error>`                                 | no ListMPD carrier                                     | How the APS reacts to an error signalled by the ADS belongs to the APS-to-ADS contract, which this spec does not define (R18). What the Player observes is that the opportunity yields no creatives, and it continues with the primary content (R1). |

Edge cases worth flagging:

- **Ad pods (multiple `<Ad>` in one VAST response)**: each Inline
  becomes one `<Period>` (with one `<ImportedMPD>`) in the
  `ListMPD`. Sequence order is preserved. The Publisher's
  `@maxDuration` on the parent event caps the **sum** of the pod
  (§5.16.5, §8.14); the Player trims at the cap per R4.
- **Wrapper chains**: resolution happens inside the APS before the
  Player ever sees the response. The Player has no visibility into
  wrapper hops; this preserves the one-request-per-slot contract on
  the Player ↔ APS interface.
- **Tracking-only VAST `<Ad>` (no `<MediaFile>`)**: the APS cannot
  synthesise an ad MPD with no media. The industry-convention
  question — *skip silently vs emit VAST Error code 403* — could not
  be resolved against the 6th edition source consulted via
  NotebookLM (the sources do not cover this). Treat this as an
  APS-internal policy until a normative reference emerges; the
  resulting `ListMPD` simply omits the entry under the silent-skip
  policy.
- **Empty / no-fill response**: when the decision carries no ads, the
  APS returns a resolution document with no candidates (R30). For the
  Player that attempt produced no ad, so it is a failed execution and
  the next overlapping window is attempted if the Publisher declared
  one (R20.1); with none, the primary content continues.
- **VAST `<UniversalAdId>`**: intentionally left on the VAST / ADS
  side and out of scope of the DASH carrier defined by this spec (see
  the field mapping above). The universal ad identifier serves ad
  tracking and reconciliation, which VAST already handles on the ADS
  side; this spec does not replicate that carrier in the DASH
  resolution document. An APS that still needs to propagate it MAY
  preserve it on a best-effort SVTA-namespaced attribute / element on
  the corresponding `ImportedMPD` (R23), but no carrier is mandated for
  it. This is distinct from `<ClickThrough>`, which this spec DOES
  carry normatively (R28) because every Player conformant to this
  specification must be able to fire the click.

## Interface contracts

| Source           | Target              | Transport      | Format                            | Direction         | Error semantics |
|------------------|---------------------|----------------|-----------------------------------|-------------------|-----------------|
| Player           | Publisher CDN     | HTTP/HTTPS     | DASH MPD (XML)                    | request / response (pull) | HTTP status codes; on 4xx/5xx Player retries or aborts session. |
| Player           | Publisher CDN     | HTTP/HTTPS     | media segments (ISOBMFF, CMAF, …) | request / response (pull) | HTTP status codes; segment-level retry per DASH-IF guidelines. |
| Player           | APS                 | HTTP/HTTPS     | request: query params (Annex I.3); response: `ListMPD` (XML) | request / response (pull, sync) | HTTP status codes; every attempt that produces no ad triggers the fallback window if one is declared (R20.1) — a 4xx/5xx, no response, a `200` whose body does not parse, and a `200` carrying a well-formed resolution document with no candidates (R30) are alike in this. With no fallback declared, all of them end with the Player on the primary content. |
| Player           | Ad CDN              | HTTP/HTTPS     | media segments                    | request / response (pull) | Same as Publisher CDN; failure of an ad segment skips that ad or aborts the break per Player policy. |
| Player           | Tracking endpoints  | HTTP/HTTPS     | callback beacons (HTTP GET, body-less) | fire-and-forget (push) | Errors are best-effort logged by the Player; not surfaced to viewer. |
| APS              | ADS                 | HTTP/HTTPS     | VAST 4.x (XML) request / response | request / response (pull) | VAST `<Error>` element + HTTP status; the APS translates errors into HTTP errors or empty `ListMPD` toward the Player. |

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

- **MPEG-DASH 6th edition** — *Information technology — Dynamic
  adaptive streaming over HTTP (DASH) — Part 1: Media presentation
  description and segment formats*. The edition this specification is
  written against, and the copy used to verify claims about it, are
  declared in [`00-normative-base.md`](./00-normative-base.md) and are
  not restated here. Canonical:
  <https://standards.iso.org/iso-iec/23009/-1/ed-6/en>. Sections
  cited above: §5.16 Alternative MPD Insertion / Replacement
  Events (§5.16.3 `InsertPresentation`, §5.16.4
  `ReplacePresentation`, §5.16.5 `@maxDuration` trimming rule);
  §8.14 List MPD profile (`urn:mpeg:dash:profile:list:2024`);
  §5.10 EventStream and callback event scheme
  (`urn:mpeg:dash:event:callback:2015`, §4.7 / §5.10.4.5); Annex I.3
  Extended HTTP GET parametrisation and Annex I.4 state vocabulary;
  §8.13 Advanced Linear profile.
- **IAB Tech Lab, VAST 4.x** (Video Ad Serving Template). The exact
  4.x version pin used by current industry practice (4.0 / 4.1 /
  4.2 / 4.3) could not be confirmed against the NotebookLM source
  consulted in this pass; the source material references VAST v3.0
  directly and only mentions 4.2 / 4.3 as placeholders inside the
  CMCD v2 draft. Pin against the IAB Tech Lab spec page on the
  next revision.
- [`02-actors.md`](02-actors.md) — actor definitions.
- [`03-requirements.md`](03-requirements.md) — R1, R2, R4 cited above.
- [`99-glossary.md`](99-glossary.md) — terminology.
