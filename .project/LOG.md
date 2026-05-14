# Project log

## 2026-05-11 — Initial iteration of spec and repo

Set up the repo scaffold, drafted the initial spec, and prepared
the build pipeline. Subsequent iterations of the spec / analysis /
norm output will append entries here as work progresses.

## 2026-05-14 — DP-1 expand (DP-1.1 + DP-1.2) + R13 rewrite

Feedback de Nicolás:

- DP-1 needed sub-rules. Two new bullets added:
  - DP-1.1 "No future-flexibility placeholders" — closes the bug
    that introduced @maxConcurrent in v4 with a fixed value of 1.
  - DP-1.2 "Single source of truth" — closes the bug of duration
    being declared in svta:RenderableAsset@duration AND in the
    last Event's @presentationTime.
- R13 rewritten — moved from "spec prescribes quartiles" to
  "ADS supplies the tracking schedule, Player executes". Removes
  the hardcoded 25/50/75/100, makes the ADS the authority over
  beacon timing, keeps the DASH baseline callback mechanism as
  the carrier.

## 2026-05-14 — R13.5 removed, ADS tracking authority moved to actors

After back-and-forth feedback on whether R13.5 (the prohibition on
hardcoded tracking fractions) should remain as a specific
requirement or be generalised:

- **R13.5 removed** from context/03-requirements.md. The specific
  prohibition was too narrow for the requirements layer.
- **The generalisation lives in context/02-actors.md** instead, as
  a new responsibility bullet for the ADS: "Tracking schedule
  authority". The actor model already separates mechanism from
  policy by design — codifying that the ADS owns the tracking
  schedule there is the right home, not as a forbidden-fraction
  rule in R13.
- DP-2 ("Mechanism over policy") proposed earlier in the
  conversation is NOT introduced — actors already covers it.

R13 itself remains as rewritten in fda6b5f (ADS-directed
callbacks; no hardcoded quartiles in the spec text). Only R13.5
is removed.
