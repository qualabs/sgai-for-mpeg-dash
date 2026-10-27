# David's SVTA2053 v3 work (2026-10-22/23) against `context/`

Date: 2026-10-27. Question: what of David Hassoun's latest work on the HLS demo is
missing from `context/`, stated differently, or contradicts it, so as to decide
which requirements to bring into this project.

**Sources.**
- `hls-non-linear-ads-demo`, the 13 commits by David Hassoun since 2026-10-20,
  merged into main by 0739c38. Seven carry substance (d2c1631, b975d0e, 081d36e,
  e0ba6fc, 1e8c4b5, 855b88a, 7eed979) and one records a decision (b20ebd4); the
  other five are merges, ADR renumbering and one frontmatter fix.
- That repo's ADRs 0104 to 0115. ADR 0104, 0105 and 0106 quote the tracked
  changes David made to the `v3-DRAFT` on 2026-10-20 (5.3.3 "Device
  capabilities", "Asset load failure", Table 5); those quotes are the only
  source here for that text. PRE, POST, ONCE, `?adclass=` and "the linear wins"
  are David's decisions of 2026-10-22/23 sent through the coordinator (ADR 0110
  to 0115), not draft text.
- The Qualabs draft of v3, `sandbox/sgai/2026-10-02-svta-doc-update/borrador.md`
  (dated 2026-10-04, before the 2026-10-20 changes: it still says `options` and
  `SlotOption`), §4, §5.3 and §6.6.
- `context/` at HEAD 7e3b33c.

**How "nothing" was established.** Every "nothing" cites a term searched with
`/usr/bin/grep -rci` over all ten files of `context/` (case-insensitive):

```
first request 0   timeout 0   fingerprint 0   privacy 0   personal data 0
multiview 0       multi-view 0   rewind 0     preroll 0   postroll 0
skipTiming 0      playout 0   "the APS SHOULD" 0
seek 1      (only OOS-7, @noJump)
preserve 6  (none about skipped candidates: R4, R21, 05 ListMPD order)
once-per-session 3  (all R34, pause family)
```

**The two layers.** `context/` is the WHAT. A row whose difference is only the
attribute, key or parameter that carries something is classed "carrier only" and
is not a missing requirement.

---

## 1. The 2026-09-28 analysis: what of its 17 points entered `context/`

All the "bring" points entered in commit 622b204 (2026-09-28); the "do not
bring" points stayed out, except the macros, which went the other way.

| # | Point | State in `context/` today |
|---|---|---|
| 1 | Audio of ad and content | **In**, as proposed: R41 (seven criteria) and R29.9 `sgai-ad-audio`; UC-18. |
| 2 | Occurrence beacons (skip, pause, mute, error) | **In**: R42. |
| 3 | Beacons per option | **In**: R13.6. |
| 4 | Slot beacons and mid-slot join | **In**: R13.7. |
| 5 | Macros in beacon URLs | **Rejected**: OOS-10 says the opposite, *"This specification defines none, for the beacons of any carrier"*; the APS writes the complete URL. |
| 6 | Verification | **In**: R44. |
| 7 | Who decides options are interchangeable | **In**, reworded: R5.8 puts it on the advertiser (*"The advertiser is expected to allow only the formats it wants"*), and R5's "several options is the form…" sentence is gone. |
| 8 | Capability under DRM | **In**: R29.10, UC-19; 04 "Device classes" rewritten. |
| 9 | Guard against degrading the content | **In**: R1.6. |
| 10 | Creative identifier | **In**: R23.2; `06` names `AssetIdentifier` (§5.8.4.10) as the first carrier; the `05` `<UniversalAdId>` row is rewritten. |
| 11 | Squeezeback Frame | **In**: `squeezeback-frame` in R12 and R12.2; R27 applies to it. |
| 12-13, 15-17 | Named progress events, `$remote`, numeric volume, probing/tiers, HLS/SSAI bindings | **Out**, as recommended. |
| 14 | Free geometry, several assets per option, `multiView` | **Out** of `context/`; `multiView` is now the roadmap item `multiview` (status `designing`, returned to design on 2026-10-27 to wait for this analysis). See row 21. |

Beyond the 17: R47 (viewability) and R48 (regulatory disclosure) also entered.
The 2026-09-28 finding that `05` mapped VAST `pause`/`mute` to timed callbacks is
fixed: row `05:449` now maps only events *"bound to a media time"*.

---

## 2. The new differences

Class: **missing** (`context/` says nothing), **stated differently**,
**contradicts**, **carrier only**.

### Capabilities

| # | David | `context/` today | Class | Recommendation |
|---|---|---|---|---|
| 1 | The app sets the capability in the Player library's configuration, which *"SHALL contain at least … concurrentVideo (uint) … concurrentImage (Boolean)"*; the request parameters keep their names (ADR 0104, quoting v3 5.3.3; d2c1631). | R29.1 defines the axes as request parameters; informative note: *"whoever implements the Player for a given device is expected to fix them for that device"*. | Carrier only | **Do not bring.** Same axes, same parameter names; the configuration names are the library's. |
| 2 | `concurrentVideo` is any integer above 0; no HTML axis (ADR 0104: *"Sigue sin haber eje HTML"*). | R29.1: `sgai-video-decoders` is `1`, `2`, `3` (`3` = three or more), plus `sgai-html-over-video`, `sgai-custom-layout`, `sgai-ad-audio`. | Carrier only | **Do not bring.** A value domain; ours is a superset in axes. |
| 3 | Sending is OPTIONAL, and *"Because capability values add to the information that can be used to fingerprint a device or a viewer, a Player SHOULD send them only where the security and personal data policies that apply to the implementer allow it; where those policies allow it, sending them is RECOMMENDED"* (ADR 0104, v3 5.3.3). | R29.2: *"Sending a reserved parameter is OPTIONAL"*, with no guidance. Searched `fingerprint` 0, `privacy` 0, `personal data` 0. | Stated differently | **Adapt R29.2.** Add the SHOULD/RECOMMENDED pair and its reason: it is real guidance an implementer needs, and the WG text already says it. |
| 4 | *"A capability that is not configured discards nothing"*: the Player filters on what is configured and attempts the rest, relying on the load failover (ADR 0104; row 7). | R5.6 checks options against *"device capabilities"*, and R3.3: *"A Player MUST NOT attempt to render an ad form … that its device class cannot render"*. R29.7 makes absence "undetermined" only at the APS. | Stated differently | **Do not bring.** Our Player is the authority on its own device (R5); not knowing is a configuration gap of an implementation, not a state the spec needs. |
| 5 | APS side: *"It is RECOMMENDED that the APS not return any layoutOption the declared capabilities do not support … When they are not sent, the APS SHOULD answer with all the layoutOptions of each slot. Whatever the APS answers, the Player selects the option it presents"* (ADR 0105, v3 5.3.3). | R5.4: no capability view is required of the APS. R29.7: *"This specification does not define how an APS resolves an undetermined value; that is the APS's decision, and two APSs that resolve it differently are both conformant."* UC-13 shows an APS narrowing to one option. Searched `the APS SHOULD` 0. | Stated differently | **Adapt R29.7.** Add the SHOULD for the undetermined case: an APS that narrows for a device it knows nothing about loses the devices that could have rendered the others (DP-3), and the Player still filters. This reverses R29.7's last sentence, which is a deliberate position (no ADR records it). The RECOMMENDED half (omit what the declared capability excludes) fits R29.1 as is and needs nothing. |

### Presentation options and their failure

| # | David | `context/` today | Class | Recommendation |
|---|---|---|---|---|
| 6 | `options` renamed `layoutOptions`, `SlotOption` renamed `LayoutOption`; a layout directly in the slot is a single option (ADR 0105; Table 31). | R5.1: *"one or more renderable presentation options"*; names are the build's. | Carrier only | **Do not bring.** |
| 7 | **Asset load failure.** *"Before it presents an option, the Player makes the first request for each of its assets … If the first request for any asset of the option fails, with an HTTP error status such as 404, or with a network error or timeout, the option cannot be presented, and the Player continues with the next layoutOption that fits. Only the first request for an asset governs this"*; then the linear default, *"If the first request for that URI also fails, the asset is skipped"* (ADR 0106, v3 5.3.3 and 6.6.4). The demo does it in the renderer, always on; a failure after the window opened mounts the next option late, at the programme's second, with no fade (ADR 0107; d2c1631). No timeout value (the library uses 10 s). | R5.6 walks options only against capability and allowed layouts. R1.4: on *"a decode error, a malformed candidate, or a mid-ad network loss"* the Player *"MUST abort that ad"*, and then the next **candidate** (R20.1). Searched `first request` 0, `timeout` 0; `404` 1 (R30, about the APS response). | Stated differently | **Bring, as R5.9, and adjust R1.4.** An option whose asset does not answer on its first request is not satisfiable, and the Player moves to the next option, as R5.6 does for capability; only the first request counts, a later failure is R1.4's. Today we drop a whole candidate whose next option would have rendered, which DP-3 forbids (*"an opportunity is given up only after every way of filling it … has been tried"*). Do not fix a timeout value. |
| 8 | Optional up-front pre-validation (`preValidateAssets`, default off), `GET`/`HEAD`, the 403 of signed URLs (ADR 0107; d2c1631). | Nothing. | Carrier only (implementation) | **Do not bring.** How a Player learns that an asset loads is its own; row 7 states only the outcome. |
| 9 | Each asset carries a **linear default** (its `URI` and `DURATION`), played full frame when no option fits or loads, over the asset's window while the programme keeps running underneath; without `URI` the asset is skipped (borrador §5.3.3, §6.6.4 Table 30; ADR 0107 `Experience.fallback`). | The linear fallback is one more option in the list: UC-09 option 4, *"a linear-style video ad that replaces the primary content for the slot, played sequentially (primary stops, ad plays, primary resumes)"*. R38.1: an overlay slot that declares nothing *"does not admit the `linear` full-screen takeover"*. | Stated differently | **Do not bring.** Ours keeps the Publisher in control of whether an overlay slot may turn linear. The timeline effect differs (ours inserts, David's covers the window); worth one sentence in UC-09 if a reader compares the two. |
| 10 | `skipTiming`: a skipped asset takes no time (`collapse`, default) or keeps its window with only the programme shown (`preserve`) (borrador §6.6.3, Table 29). | R14.1: candidates play *"each starting when the previous one ends"*, so a dropped one takes no time, implicitly. Searched `skipTiming` 0; `preserve` 6, none about this. | Stated differently | **Do not bring `preserve`** (DP-1.1, no case). **Adapt R14.1** in one clause so that a candidate dropped under R5.3 takes no time is said, not inferred. |

### Timing and repetition

| # | David | `context/` today | Class | Recommendation |
|---|---|---|---|---|
| 11 | Asset-lists requested on demand, when hls.js would: when the programme is buffered up to the break, or when playback or a seek lands in it; no eager mode; the programme never waits for a list, and a late list enters at the programme's second (ADR 0108, 0109; d2c1631). | R36: the Player MAY resolve up to the declared offset ahead, 60 s by default (R36.1), and *"Resolving early is a permission and never an obligation"* (R36.7). | Stated differently | **Do not bring.** David's rule is one Player strategy inside our window (a 30 s buffer is within 60 s), and the base already carries the offset. |
| 12 | **`CUE="PRE"`** on a non-linear window: its list is requested at load and it is placed where playback starts, not at its START-DATE; on live, at the live join point; one first seen after playback joined is not presented (ADR 0110; d2c1631, b975d0e). | Pre-roll is linear only: UC-01 *"Slot at start of session"*. R40: an overlay window *"is anchored to the media-time range it declares"*. Searched `preroll` 0. | Missing | **Do not bring now.** There is no base construct for "wherever playback starts" on a non-linear window, and `04` admits only real cases; if a real one appears (a sponsor bug at session start), it is a sub-criterion of R40. |
| 13 | **`CUE="POST"`**: a non-linear post-roll is never presented as non-linear; it plays its linear default after the programme or is skipped; its list is requested when the programme is buffered to its end; on live it waits for ENDLIST (ADR 0111; 081d36e). | `04` "Out of scope": *"Post-roll slots — candidate for a future phase"*; glossary: *"post-roll is out of scope for this edition"*. | Stated differently | **Do not bring**; post-roll stays out. David's rule confirms that a non-linear post-roll does not exist, which is consistent with keeping it out. |
| 14 | **`CUE="ONCE"`** on a non-linear window: once playback entered it and left it (not necessarily completed), it leaves the experiences and the bar for good, so a seek back neither redraws it nor fires its tracking again; a seek over it does not spend it; a ONCE post-roll is not replayed (ADR 0112; e0ba6fc). | R34 gives once-per-session to the **pause** family only (`once-per-session` 3, all in R34). Nothing for overlay or squeezeback windows. The base has `@executeOnce` for linear events (R30.2). | Missing | **Bring, as an extension of R34 to overlay windows.** Same capability, same counting rule (R34.3: consumed when it begins rendering, which is the base's `E.c`), and `06` already requires reusing the base construct. |
| 15 | Without ONCE, a seek back into a window already presented **redraws it and fires its tracking again**, and a seek into an ad starts it at the second of the seek (ADR 0110: *"Un seek de vuelta adentro de su ventana lo vuelve a dibujar, como a cualquier break"*; d2c1631 `onTracking`). | Nothing on re-entering a presented window. Searched `seek` 1 (OOS-7 only), `rewind` 0. R13.7 covers joining a slot after its start for the slot beacon only. | Missing | **Bring, with row 14.** The default (re-present, as the base re-executes an event without `@executeOnce`) and what a seek into the middle does to the time beacons already passed. R3.2 makes undefined behaviour non-conforming, and this one is undefined today. |

### Two classes in one stream

| # | David | `context/` today | Class | Recommendation |
|---|---|---|---|---|
| 16 | One set of tags per stream; each client picks the class of every break with `?adclass=` and `EXT-X-DEFINE:QUERYPARAM`, so a stock player reads the break as a linear interstitial and ours as concurrent (ADR 0113; 1e8c4b5). | The same need, one manifest for a legacy Player and an SGAI Player, is met by R1 (the legacy Player ignores the window) and R40 supersede (the linear break is the legacy fallback; UC-07, UC-17). | Carrier only | **Do not bring.** An HLS mechanism; DASH has no URL-variable substitution in the event, and R40 already gives the outcome. |
| 17 | Classes may mix in a stream but **must not overlap in time** (ADR 0113, decision (a)). | R40 allows overlap and makes the Publisher declare it: supersede or on top; UC-04 (hybrid break) is an overlay on top of a linear ad. ADR 0020. | Contradicts | **Do not bring.** The prohibition comes from hls.js, which cannot composite over its own interstitial; ADR 0020 records why DASH needs the overlap (UC-07 fallback, hybrid break). |
| 18 | If they overlap anyway, **the linear wins**: while hls.js plays its interstitial nothing of ours is drawn or counted, *"y si al volver el programa la ventana nuestra sigue abierta, se retoma"* (ADR 0114, David's decision of 2026-10-23; b20ebd4, 855b88a). | R40.4 (default relation): the form is presented only over the declaring presentation, and *"A form on screen when an alternative presentation begins ends there, and the window presents nothing further."* | Contradicts | **Adapt R40.4, recorded in an ADR.** "Linear wins" is already our default; the difference is the resume. Resuming uses the rest of a window the Publisher sold (DP-3) and does not bring back the two-ads case ADR 0020 removes, because it happens after the linear ends. It matters mostly for insertion, where the primary resumes at the same position; after a replacement the window has usually passed. This changes an accepted requirement. |
| 19 | Both classes in one player: the market's linear interstitial plays with the base machinery on, and the library draws its own (ADR 0114; 855b88a, 7eed979). | R40.4: the Player executes every inherited linear event *"with its base semantics"*; R1. | — | Already the same; listed so it is not looked for again. |

### Other parts of v3

| # | David | `context/` today | Class | Recommendation |
|---|---|---|---|---|
| 20 | A presentation ends at the end of its assets or at `X-PLAYOUT-LIMIT`; an all-image one at its `DURATION` (borrador §5.3.1). | R4 cap bounds the cumulative duration and is enforced against actual length (R4.5); R19.4 gives image and HTML a duration on the presentation timeline. Searched `playout` 0. | Carrier only | **Do not bring.** |
| 21 | `multiView`: a fixed layout of several concurrent contents, no ad semantics, **viewports declared by the author**, with suggested layouts for 2, 3 and 4 views; carried as a concurrent presentation; PRE and ONCE apply to it (borrador Table 2, §5.3.2, §5.3.4; d2c1631, 1e8c4b5). | Nothing (`multiview` 0, `multi-view` 0). The roadmap item `multiview` (T-01-PLAN, ADR 0003) designs **fixed named `multiview-*` presets**, agnostic of multi-decoder vs tiles. | Missing (and against the roadmap design) | **Decide it in the `multiview` item, not here.** The conflict to settle there: David's free viewports are a layout system (R10.2), and the roadmap design chose presets precisely to avoid that. |
| 22 | Several additional assets per option, each with `viewport`, `zDepth`, `volume` (e.g. the two-bar L-shape, three decoders) (borrador §4.4.7-4.4.8, §5.3.2). | R27.1: an L-shape carries *"exactly one ad creative"*; R22: one non-linear form at a time; R10.2: no layout standard; R41.7: one audio source. | Contradicts | **Do not bring.** Point 14 of 2026-09-28, already decided. |

---

## 3. What to bring, in order

1. **Row 7, option failover on the first request** (new R5.9, R1.4 adjusted).
   Today a dead asset costs the whole candidate; DP-3 says it should cost one
   option.
2. **Rows 14 and 15, repetition of a non-linear window** (R34 extended to
   overlay windows, plus the default on seek back). Today the behaviour is
   undefined, which R3.2 does not admit, and it decides whether an impression is
   counted twice.
3. **Row 18, resume after a linear break** (R40.4 adapted, with an ADR).
4. **Row 5, the APS answer when no capability was sent** (R29.7 adapted).
5. **Row 3, fingerprinting guidance on sending capabilities** (R29.2 adapted).
6. **Row 10, the skipped candidate takes no time** (one clause in R14.1).

Rows 12 and 13 (PRE, POST) stay out for now; row 21 goes to the `multiview`
roadmap item.

## 4. Counts

22 rows: **missing 4** (12, 14, 15, 21), **stated differently 8** (3, 4, 5, 7,
9, 10, 11, 13), **contradicts 3** (17, 18, 22), **carrier only 6** (1, 2, 6, 8,
16, 20), and one row (19) that is the same.

## 5. What was not verified

- The 2026-10-20 v3 text itself: only the quotes inside ADRs 0104 to 0106 were
  read; the `.docx` with David's tracked changes was not opened.
- Whether PRE, POST, ONCE, `?adclass=` and "linear wins" are going into the v3
  draft or remain demo decisions: the ADRs record them as David's decisions sent
  through the coordinator.
- No base-specification clause was checked for this analysis; the R1.5 readings
  above (`@executeOnce` re-execution on seek back) come from what `context/`
  already quotes (R30, R34), and the PDF was not opened.
