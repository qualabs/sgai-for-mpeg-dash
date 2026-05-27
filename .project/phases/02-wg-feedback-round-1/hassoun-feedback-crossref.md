# Cross-reference: David Hassoun's feedback ↔ state of the SGAI spec

**Date:** 2026-05-27 (v2 — updated source)
**Author:** CTO assistant (report — NO change was applied to the spec)
**Scope:** cross-reference David Hassoun's **actual** feedback (the 3 files he edited / commented and uploaded to `#wg-comcast` on 2026-05-20) against the current state of the SGAI spec (`projects/sgai-for-mpeg-dash/context/`) after the large revision of 2026-05-27 (commit `fb30314`).

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

David left **10 pieces of feedback** in total, all as inline `//` comments (plus 2 text renames in `02-actors`). Breakdown:

- ✅ **Already addressed (4):** Publisher rename (`02#L15`), ADS→APS rename / naming conflict (`02#L9`+`L38`), expansion of "ADS" on first reference (`02#L9`), Player "select" — the `02#L98` ISSUE is now covered by the atomised R5/R7 chain.
- 🔧 **Change per feedback (3):** background-image below the video in an L-box layout (`02` layout-per-device `02#L26` + `04` UC-03 `#L242` + UC-04 D3 `#L423`), UC-08 "pause-ad can be a partial overlay" (`04#L702`), UC-04 D2 "CONFUSING" (`04#L419`) — wording to clarify.
- ❓ **Open for discussion / conflict (3):** UC-02 "why limit to 1 vs combine with UC-06?" (`04#L170`) — David pushes in the OPPOSITE direction to Nicolas's decision to keep them separate; UC-07 "this is bad, should use the old ad experience" (`04#L653`) — David objects to the legacy-player behaviour; layout-per-device as an open question (`02#L26`).

**What requires action from Nicolas** are the 3 🔧 points (wording / documentation) and the 3 ❓ points (decisions), detailed in section 3.

---

## 2. Cross-reference by file

### 2a. `02-actors.md` — 2 edits + 4 comments

| # | Location (David) | What David did | Category | State in the CURRENT spec |
| --- | --- | --- | --- | --- |
| A1 | L9 (intro paragraph) | **Edited the text**: expanded "the ADS provides" → "the **Ad Decision Server (ADS)** provides" (spell out the acronym on first reference) | ✅ Already addressed | The CURRENT spec uses "Ad Decision Server (ADS)" on the first reference in the intro (L11) and additionally defines ADS and APS in the header blockquote (L5-6). Covered and exceeded. |
| A2 | L15 (heading "Broadcaster / Content Owner") | Commented `//ISSUE - naming - maybe publisher?` | ✅ Already addressed | The CURRENT spec renamed the actor to **Publisher** throughout the doc (heading L19, entire body). Exactly what David suggested. |
| A3 | L26 (layout-templates bullet) | Commented `//ISSUE - what about diff devices supporting different layouts?` | 🔧 / ❓ | The device-class model (R3 + UC D1-D5) answers *how* a layout degrades per device, but the spec keeps the allowed layouts as a **device-agnostic** declaration by the Publisher (the Player intersects with the device's capability, R5.6). David asks whether the Publisher should be able to declare *different layouts per device class*. The spec does NOT allow this today. Remains an open design question. |
| A4 | L38 (heading "Ad Decision Server (ADS)") | **Edited the heading** → "Ad Presentation Server (APS)" + commented `//ISSUE - conflict of naming` | ✅ Already addressed | The CURRENT spec **split the monolithic actor in two**: ADS (decisioning, outputs VAST) + APS (converts VAST→resolution document). The APS term David proposed now exists as its own actor (`02#L90`). The split resolves the "conflict of naming" by going beyond the rename. Worth confirming with David that the split is what he expected (likely yes). |

Note on A2+A4: in David's file the ADS heading ended up labelled "Ad Presentation Server (APS)" — David overwrote the actor name to APS. The CURRENT spec did not do the literal rename (which would have left a single actor called APS), but instead separated the two responsibilities into two actors. This honours the intent without the 1:1 rename.

### 2b. `04-use-cases.md` — 6 inline comments (no text edits)

| # | Location (David) | David's comment | Category | State in the CURRENT spec |
| --- | --- | --- | --- | --- |
| U1 | L170 (heading UC-02) | `//Why limit this to 1 vs combine w UC6?` | ❓ Conflict | David questions why UC-02 (single mid-roll) is separate from UC-06 (multi-ad break) and suggests combining them. This goes in the **OPPOSITE direction** to Nicolas's decision (recorded in v1) to keep them separate, because the agentic test-generation workflow needs both cases discrete. The CURRENT spec keeps them separate. A real conflict between David's feedback and Nicolas's decision. |
| U2 | L242 (heading UC-03) | `//WHAT ABOUT BG IMAGE BELOW VIDEO L-BOX` | 🔧 Change | David asks for the **background-image-below-video L-box** case (the video shrinks into an L shape and a background image fills the rest of the screen). The CURRENT spec covers side-by-side and overlays *on top of* the video, but NOT a background-image *below* / behind the shrunk video. Missing documentation. (Same point as A3 and U4.) |
| U3 | L419 (UC-04, D2 sub-bullet "only HTML/image forms") | `//CONFUSING` | 🔧 Change | David flags the wording of "the experience collapses to UC-02" as confusing, for when the overlay candidate has only HTML/image forms in D2. This is a **wording-clarity** problem, not a design one. Rewrite that sub-bullet so the outcome (full-screen linear ad, no overlay) is explicit without sending the reader back to UC-02. |
| U4 | L423 (UC-04, heading D3) | `//WHAT ABOUT BG IMAGE BELOW VIDEO L-BOX` | 🔧 Change | Same request as U2, now in the D3 context (single-decoder image+HTML). David wants the L-box-with-background-image case handled here too. Reinforces U2: background-image-below-video is a case David expects to see across multiple UCs. |
| U5 | L653 (heading UC-07) | `//THis is bad - should use old ad exp` | ❓ Conflict | David objects to the **legacy-player** behaviour: he says that instead of "silent skip + continue primary content" (what the spec defines via R1 ignore-if-unknown), the legacy player **should fall back to the old ad experience** (the SGAI/linear one that already exists in DASH 6th). This is a design objection about graceful degradation. The CURRENT spec does skip-and-continue, not fallback to the old ad. We need to discuss whether UC-07 should contemplate a fallback to the pre-existing linear mechanism. |
| U6 | L702 (heading UC-08) | `//Pause ad experience can be an partial overlay` | 🔧 / ❓ | David points out that the pause-ad **need not be fullscreen** — it can be a partial overlay on the paused frame. The CURRENT spec (UC-08 + R16/R17) treats the pause-ad as a surface that takes priority and suspends the overlay, but assumes a fullscreen-ish composition of the pause-ad. (In v1 there was an "R21 fullscreen" mentioned — verify; David explicitly pushes toward a partial pause-ad.) Adjust UC-08 / R17 to admit the pause-ad as a partial overlay coexisting with the paused frame. |

### 2c. `03-requirements.md` — **no feedback**

David **neither edited nor commented anything** in `03-requirements.md`. The only `//` in the file (L315) is the pre-existing URL of the IAB reference in R12, present identically in BASE. It is not a comment from David. **Zero pieces of feedback in requirements.**

---

## 3. Next steps (prioritised)

**High — require a decision from Nicolas (the ❓):**

1. **(U5 / UC-07) Resolve the legacy-player objection.** David says the legacy player should not simply skip the new constructs but **fall back to the old ad experience** (the linear SGAI of DASH 6th). This contradicts the current design (R1 ignore-if-unknown → continue primary content). A material design decision: should UC-07 contemplate a fallback to the pre-existing linear mechanism, or is the silent skip correct? Discuss with David — likely touches R1 and UC-07.
2. **(U1 / UC-02) Resolve the UC-02 vs UC-06 conflict.** David wants to combine single-ad and multi-ad break; Nicolas separated them on purpose (the test-generation workflow needs them discrete). A direct conflict. Decide whether to keep the separation (and communicate the rationale to David) or combine them.
3. **(A3 / `02#L26`) Layouts per device class.** Should the Publisher be able to declare different allowed layouts per device class, or is the device-agnostic model + intersection in the Player (R5.6) sufficient? Open design question.

**Medium — documentation / wording work (the 🔧):**

4. **(U2 + U4 / UC-03 + UC-04 D3) Document background-image below the video in an L-box.** David asked for it twice. The case is: video shrunk into an L (or a window), a background image filling the rest of the screen *behind* / around the video. Today the spec only covers overlays on top of the video and side-by-side. Add the L-box-with-background-image case. Connects to point #4 of the v1 report (3-asset layout / Z-depth).
5. **(U6 / UC-08) Allow pause-ad as a partial overlay.** David says the pause-ad need not be fullscreen. Adjust UC-08 / R17 to allow the pause-ad as a partial overlay on the paused frame.
6. **(U3 / UC-04 D2) Clarify the "CONFUSING" wording.** Rewrite the D2 sub-bullet (overlay candidate with only HTML/image) so the outcome is explicit without referring back to UC-02. Pure wording.

**No action (the ✅):**

7. **(A1, A2, A4)** already closed: ADS expanded on first reference, Broadcaster→Publisher applied, ADS→APS resolved via the split. Worth **confirming with David** that the ADS+APS split works for him (A4) — the only lightweight follow-up.

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
