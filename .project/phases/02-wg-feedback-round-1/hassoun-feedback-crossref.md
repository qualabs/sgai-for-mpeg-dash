# Cross-reference: David Hassoun's feedback ↔ state of the SGAI spec

**Date:** 2026-05-27 (v3 — refreshed after the ordered-fallback / R26 edits + UC-09 / UC-10)
**Author:** CTO assistant (report — the `context/` edits are committed + pushed to `main`, 2026-05-27)
**Scope:** cross-reference David Hassoun's **actual** feedback (the 3 files he edited / commented and uploaded to `#wg-comcast` on 2026-05-20) against the current state of the SGAI spec (`projects/sgai-for-mpeg-dash/context/`) after the 2026-05-27 revisions: the positional ordered-fallback rewrite (R5 + R5.1/R5.2/R5.5/R5.6/R5.7), the R26 side-by-side background-fill requirement (R26 + R26.1/.2/.3), the UC-03 L-shape-as-layout + UC-04 D2 / D3 wording rewrites, and the two new use cases **UC-09** (worked ordered-fallback example across device classes) and **UC-10** (side-by-side three-element R26 illustration). All these `context/` changes were validated by the owner and committed + pushed to `main` on 2026-05-27.

---

## ⚠️ Source change relative to v1

The **v1 of this report was based on the minutes** of the Comcast WG (an inference of what David said on the call). This **v2 is based on the 3 files David actually edited and commented on** — the precise source, not the inferred one. The files are:

- `02-actors.md` — 2 text edits + 4 inline `//ISSUE` comments
- `04-use-cases.md` — 6 inline comments (no text edits)
- `03-requirements.md` — **untouched** (David neither commented nor edited anything)

David's feedback was extracted via a **3-way diff**:
1. **BASE** = what David received, the state of `context/` at commit `c983ff7` (parent of `fb30314`, the three-actor Broadcaster / ADS / Player model, without R19–R25).
2. **DAVID** = BASE + his edits / comments.
3. **CURRENT** = the state of `context/` post `fb30314` (four-actor Publisher / ADS / APS / Player, +R19–R25).

Where v1 and v2 differ, **v2 wins** (it is the direct source). See section 6 for the explicit contrast.

---

## 1. Executive summary

David left **10 pieces of feedback** in total, all as inline `//` comments (plus 2 text renames in `02-actors`). Current status after the 2026-05-27 edits (ordered fallback R5.x, R26 side-by-side, UC-03 / UC-04 rewrites, new UC-09 / UC-10):

- ✅ **Covered (6):** Publisher rename (A2), ADS→APS split (A4, pending only David's confirmation), ADS expanded on first reference (A1), Player "select" via the atomised R5/R7 chain (the `02#L98` ISSUE), **layout-per-device-class (A3)** — now resolved by the positional ordered fallback (R5.x) + R26 and *illustrated* by **UC-09**, and **background-image L-box (U2 / U4)** — now covered by R26 + the UC-03 L-shape-as-layout option + UC-04 D3/D4 + **UC-09 option 2** + **UC-10**.
- ✅ **Wording fixed (1):** UC-04 D2 "CONFUSING" (U3) — the "collapses to UC-02" sub-bullet rewritten to an explicit outcome.
- ❓ **Still open (3):** UC-07 "should use the old ad experience" (U5) — legacy-player design objection, undecided; UC-08 "pause-ad can be a partial overlay" (U6) — conflicts with R21 (pause-ad fullscreen), not addressed by this session's edits; UC-02 vs UC-06 "combine?" (U1) — **parked by owner** (keep separate per the v1 decision), conflict with David acknowledged but deferred.

**What requires action from Nicolas** is now narrower: the 3 ❓ points (U5 decision, U6 decision, U1 already parked) plus the lightweight A4 confirmation with David. The 🔧 documentation points (A3 / U2 / U4 / U3) are done. Details in section 3.

---

## 2. Cross-reference by file

### 2a. `02-actors.md` — 2 edits + 4 comments

| # | Location (David) | What David did | Category | State in the CURRENT spec |
| --- | --- | --- | --- | --- |
| A1 | L9 (intro paragraph) | **Edited the text**: expanded "the ADS provides" → "the **Ad Decision Server (ADS)** provides" (spell out the acronym on first reference) | ✅ Already addressed | The CURRENT spec uses "Ad Decision Server (ADS)" on the first reference in the intro (L11) and additionally defines ADS and APS in the header blockquote (L5-6). Covered and exceeded. |
| A2 | L15 (heading "Broadcaster / Content Owner") | Commented `//ISSUE - naming - maybe publisher?` | ✅ Already addressed | The CURRENT spec renamed the actor to **Publisher** throughout the doc (heading L19, entire body). Exactly what David suggested. |
| A3 | L26 (layout-templates bullet) | Commented `//ISSUE - what about diff devices supporting different layouts?` | ✅ **Covered** | **Decided + illustrated.** The Publisher does NOT declare layouts per device class — by decision (T-04, 2026-05-27). The same per-class outcome is achieved Player-side via the **positional ordered fallback** (R5 + R5.1/R5.2/R5.5/R5.6/R5.7): the Publisher declares ONE device-agnostic allowed-layout set, the ADS emits ONE ordered list of presentation options identically to every viewer, and each Player renders the first option its hardware can satisfy. This keeps device capability as the Player's sole authority (R5.4) and preserves DP-1. **UC-09** is the worked example proving the per-class layout emerges from one list (D1 → side-by-side, D3/D4 → L-shape, D2/D5 → takeover). Rationale + IAB citation in `.project/LOG.md`. |
| A4 | L38 (heading "Ad Decision Server (ADS)") | **Edited the heading** → "Ad Presentation Server (APS)" + commented `//ISSUE - conflict of naming` | ✅ Already addressed | The CURRENT spec **split the monolithic actor in two**: ADS (decisioning, outputs VAST) + APS (converts VAST→resolution document). The APS term David proposed now exists as its own actor (`02#L90`). The split resolves the "conflict of naming" by going beyond the rename. Worth confirming with David that the split is what he expected (likely yes). |

Note on A2+A4: in David's file the ADS heading ended up labelled "Ad Presentation Server (APS)" — David overwrote the actor name to APS. The CURRENT spec did not do the literal rename (which would have left a single actor called APS), but instead separated the two responsibilities into two actors. This honours the intent without the 1:1 rename.

### 2b. `04-use-cases.md` — 6 inline comments (no text edits)

| # | Location (David) | David's comment | Category | State in the CURRENT spec |
| --- | --- | --- | --- | --- |
| U1 | L170 (heading UC-02) | `//Why limit this to 1 vs combine w UC6?` | ❓ Conflict | David questions why UC-02 (single mid-roll) is separate from UC-06 (multi-ad break) and suggests combining them. This goes in the **OPPOSITE direction** to Nicolas's decision (recorded in v1) to keep them separate, because the agentic test-generation workflow needs both cases discrete. The CURRENT spec keeps them separate. A real conflict between David's feedback and Nicolas's decision. |
| U2 | L242 (heading UC-03) | `//WHAT ABOUT BG IMAGE BELOW VIDEO L-BOX` | ✅ **Covered** | **Resolved with the corrected model.** The case David flagged is now disambiguated into the two distinct layouts: (a) **L-shape / squeezeback** — the ad is full-frame with a cutout for the shrunk primary content, so the ad already covers the whole screen and there is **no background fill** (documented in UC-03 ad-response + UC-09 option 2; it is a layout per R5, NOT an R26 case); (b) **side-by-side / double-box** — the genuine three-element case where a background image fills the bands the two boxes leave uncovered, now normatively **R26** (+R26.1/.2/.3) and illustrated by **UC-10**. The "background image below the video" intent is the side-by-side R26 case; the L-box is the no-background full-frame case. Both are now explicit. (Same point as A3 / U4.) |
| U3 | L419 (UC-04, D2 sub-bullet "only HTML/image forms") | `//CONFUSING` | ✅ **Covered (wording fixed)** | The UC-04 D2 sub-bullet no longer says the experience "collapses to UC-02". It now states the outcome explicitly: D2 cannot composite non-video surfaces on top of video, so the overlay portion is declined per R5/R3 while the linear ad still plays — the user sees a full-screen linear ad of bounded duration with no overlay, and primary content resumes on completion. No back-reference to UC-02. |
| U4 | L423 (UC-04, heading D3) | `//WHAT ABOUT BG IMAGE BELOW VIDEO L-BOX` | ✅ **Covered** | Same as U2, now handled in the D3 / D4 contexts. UC-04 D3 and D4 were rewritten so the L-shape / squeezeback is a presentation option per R5 (full-frame image-or-HTML ad with a cutout; one decoder for the shrunk primary content plus an image/HTML surface; a video full-frame form needs two decoders and is not satisfiable on a single-decoder device). The same L-shape vs side-by-side distinction is illustrated across device classes in **UC-09** and the side-by-side three-element case in **UC-10**. |
| U5 | L653 (heading UC-07) | `//THis is bad - should use old ad exp` | ❓ Conflict | David objects to the **legacy-player** behaviour: he says that instead of "silent skip + continue primary content" (what the spec defines via R1 ignore-if-unknown), the legacy player **should fall back to the old ad experience** (the SGAI/linear one that already exists in DASH 6th). This is a design objection about graceful degradation. The CURRENT spec does skip-and-continue, not fallback to the old ad. We need to discuss whether UC-07 should contemplate a fallback to the pre-existing linear mechanism. |
| U6 | L702 (heading UC-08) | `//Pause ad experience can be an partial overlay` | 🔧 / ❓ | David points out that the pause-ad **need not be fullscreen** — it can be a partial overlay on the paused frame. The CURRENT spec (UC-08 + R16/R17) treats the pause-ad as a surface that takes priority and suspends the overlay, but assumes a fullscreen-ish composition of the pause-ad. (In v1 there was an "R21 fullscreen" mentioned — verify; David explicitly pushes toward a partial pause-ad.) Adjust UC-08 / R17 to admit the pause-ad as a partial overlay coexisting with the paused frame. |

### 2c. `03-requirements.md` — **no feedback**

David **neither edited nor commented anything** in `03-requirements.md`. The only `//` in the file (L315) is the pre-existing URL of the IAB reference in R12, present identically in BASE. It is not a comment from David. **Zero pieces of feedback in requirements.**

---

## 3. Next steps (prioritised)

**Still open — require a decision from Nicolas (the ❓):**

1. **(U5 / UC-07) Resolve the legacy-player objection. — STILL OPEN.** David says the legacy player should not simply skip the new constructs but **fall back to the old ad experience** (the linear SGAI of DASH 6th). This contradicts the current design (R1 ignore-if-unknown → continue primary content). A material design decision: should UC-07 contemplate a fallback to the pre-existing linear mechanism, or is the silent skip correct? Not touched by the 2026-05-27 edits. Discuss with David — likely touches R1 and UC-07. (TASKS T-02.)
2. **(U6 / UC-08) Allow pause-ad as a partial overlay. — STILL OPEN.** David says the pause-ad need not be fullscreen. This conflicts with **R21** (pause-ad MUST be fullscreen) and was **not** addressed by the 2026-05-27 edits. Resolving it means either adjusting R21 / R17 to admit a partial pause-ad or declining David's point with a rationale. (TASKS T-06.)
3. **(U1 / UC-02 vs UC-06) — PARKED by owner.** David wants to combine single-ad and multi-ad break; Nicolás decided to keep them separate (the test-generation workflow needs them discrete) and **parked** the conflict on 2026-05-27 ("por ahora no hacer nada"). The disagreement with David is acknowledged but deferred; spec keeps them separate. (TASKS T-03.)

**Done this round (the 🔧 + the layout question):**

4. **(A3 / `02#L26`) Layouts per device class — DONE.** Decided: no per-device-class declaration by the Publisher; the positional ordered fallback (R5.x) + R26 produce the per-class layout Player-side. Illustrated by **UC-09**. (TASKS T-04.)
5. **(U2 + U4 / UC-03 + UC-04 D3/D4) Background-image L-box — DONE.** Disambiguated into L-shape (full-frame, no background, a layout per R5) vs side-by-side (three-element R26 background fill). Covered by R26 + UC-03 + UC-04 D3/D4 + **UC-09** + **UC-10**. (TASKS T-05.)
6. **(U3 / UC-04 D2) "CONFUSING" wording — DONE.** D2 sub-bullet rewritten with an explicit outcome, no back-reference to UC-02. (TASKS T-07.)

**Lightweight follow-up (the ✅):**

7. **(A1, A2, A4)** closed: ADS expanded on first reference, Broadcaster→Publisher applied, ADS→APS resolved via the split. Still worth **confirming with David** that the ADS+APS split works for him (A4). (TASKS T-08.)

---

## 4. Provenance

Each point cites: David's file + line number in the version he delivered (the 3 files of 2026-05-20, local paths in `~/.claude/channels/telegram/inbox/`).

- **02-actors** (`1779891894706-AgADmgkAAmZHuUQ.md`): A1=L9, A2=L15, A3=L26, A4=L9+L38.
- **04-use-cases** (`1779891907088-AgADmwkAAmZHuUQ.md`): U1=L170, U2=L242, U3=L419, U4=L423, U5=L653, U6=L702.
- **03-requirements** (`1779891910480-AgADnAkAAmZHuUQ.md`): no feedback (verified by diff against BASE).
- **BASE** = `context/` at commit `c983ff7` (parent of `fb30314`).
- **CURRENT** = `context/02-actors.md`, `context/04-use-cases.md`, `context/03-requirements.md` post `fb30314` (four-actor Publisher / ADS / APS / Player).

Method: `git show c983ff7:context/<file>` for BASE; word-level diff (normalising line endings — David's files come with CRLF) against David's files; extraction of `//` comments and text edits.

---

## 5. Heads-up on sources

- **David commented, did not edit (except 2 renames in 02).** His 10 feedback pieces are inline `//ISSUE` / `//` comments, consistent with what he flagged in the minutes (action item #9: "couldn't edit directly, would call-out recommendations via Slack"). The only text edits are the 2 renames in `02-actors` (expand ADS on L9, overwrite the ADS heading to APS on L38).
- **`03-requirements` received no feedback at all.** Verified by diff: David uploaded it untouched. Nothing was invented — if a file does not differ from the base, that is stated.
- **Clean, unambiguous diff.** David's files had CRLF; after normalising line endings, the diff isolates exactly his comments and the 2 renames. No ambiguity.

---

## 6. Differences vs the v1 report (based on the minutes)

The **actual** feedback from the files revealed and corrected several things the minutes had wrong or incomplete:

- **NEW (not in v1): U5 / UC-07 "should use old ad exp".** David's objection to the legacy-player behaviour did NOT appear in the minutes. It is a material design point that only shows up in his file. It is probably the most important finding of v2.
- **NEW: U3 / UC-04 D2 "CONFUSING".** The confusing-wording flag was not in the minutes. Small but actionable.
- **NEW: U6 / UC-08 "pause-ad can be a partial overlay".** The minutes had pause-ads but not this nuance (partial vs fullscreen). David asks for it explicitly.
- **REFINED: the background-image L-box (U2+U4).** The minutes (v1 point #4) spoke generically of "background images / side-by-side / 3-asset / Z-depth". The files show that what David actually flagged, twice, is specifically **background-image below the video in an L-box** — more concrete than the fuzzy list in the minutes.
- **REFINED: UC-02 vs UC-06 (U1) is a CONFLICT, not a clean dismissal.** v1 (point #7) had it as "resolved against Hassoun" (Nicolas decided to keep them separate). The file shows that David **left the comment asking to combine them** — i.e. the disagreement is still alive in his version, it was not settled. Reclassified from ✅ to ❓.
- **CONTRADICTION with the minutes: "8 points" → actually 10 pieces in the files.** The minutes captured ~7 spec points; the files have 10 concrete comments, with a different distribution (3 in actors beyond the rename, 6 in use-cases). The minutes did not mention the UC-04 / UC-07 / UC-08 comments.
- **DROPPED from v1: point #8 (MPEG-DASH coordinates from the DM).** It came from the Slack DM, not from these files. It does not appear in David's 3 files, so it falls out of the file cross-reference. If still alive, it goes via another channel (the DM), not via the spec feedback.
- **CONFIRMED from v1: Publisher rename (A2), ADS/APS split (A4), Player no-reorder.** These were correct in v1 and the files confirm them. The "no-reorder / R7.4" from v1 has NO comment from David in the files (David did not touch `03-requirements`) — it was an inference from the minutes; left out of the file cross-reference table for rigour (no evidence in the 3 files), although it remains true that the spec satisfies it.
