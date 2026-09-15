I'm stopping the pipeline before Step 6 and bringing this to you. Stage 1 is complete and on disk; Step 6 is blocked on a decision only you can make.

## Why I stopped

The fact-check against the primary source came back worse than "one source is wrong":

**MPEG-DASH 6th edition spells these attributes two different ways in two different clauses, and never acknowledges the mismatch.**

| | Prose (§5.16.4/§5.16.5) | Normative XML schema (§5.16.6) |
|---|---|---|
| URL attribute | `@url` | `uri` |
| Clip attribute | `@clip` | `clipDuration` |

An instance document validates against the **schema**, so `url=` gets rejected by a validator. Our `context/` currently follows the prose in examples — meaning every XML example we ship would be schema-invalid.

And one finding that isn't an editorial choice at all:

> **`clipDuration` is `xs:boolean`, default `true`** — "specifies *whether* the maximum duration … will be altered". Our example at `context/05-dash-linear-interfaces.md:209` writes `clipDuration="30000"`, i.e. a duration in ms. That is schema-invalid under *either* spelling.

I verified the local side myself. There's also an internal inconsistency we introduced independently of the standard: the same file uses `uri=` on `ImportedMPD` (lines 289, 294) and `url=` on Insert/ReplacePresentation (195, 205). And `earliestResolutionTimeOffset` appears as `0`, `15`, and `60000` across three examples — three different unit conventions in one file, which corroborates a third prose/schema mismatch (schema says `xs:double` default `60.0`; prose says units of timescale; our value is ms). That one is **unverified** — it needs its own query before I'd act on it.

**Good news:** all three of our clause numbers (§5.16.3 / §5.16.4 / §5.16.5) are **correct**, and our scheme URNs match the standard exactly. The earlier Step-1 report that said §5.16.2/§5.16.3 was the wrong one.

## Why this blocks rather than gets reported-and-passed

Normally an execution-time finding is mine to resolve. This one isn't, for two reasons. The fix lives in `context/`, which is human-authored canonical input — and by this project's own rules a `context/` edit is a **major iteration trigger**, not something to slip in mid-build. Second, building now bakes invalid XML into a ~160 KB spec and then refines on top of it up to five times; Step 8 would flag it, but the refine loop can't reach back into `context/`, so v8 would regenerate the same error.

## What I recommend

Follow the **schema**, and record the defect rather than quietly picking a side:

1. XML examples → `uri=`, and `clipDuration="true"` (or omit — `true` is the default). Three lines: `context/05:195`, `:205`, `:209`.
2. Prose → rename `@url` to `@uri` (10 occurrences: 8 in `05`, 1 in `02-actors.md:112`, 1 in `99-glossary.md:79`) with a one-line footnote that §5.16.5 prose spells it `@url` while the §5.16.6 schema spells it `uri`, and we follow the schema because that is what validates.
3. Reword `context/05:246`, which describes `@clipDuration` as though it were a duration.
4. Separately: query the notebook on `earliestResolutionTimeOffset` units before touching those values — a wrong call there shifts them by 1000×.

Items 1 and 3 are factual corrections. Item 2 is the one genuine editorial choice, and it's plausibly worth a defect report to the WG.

## Where the build stands

```
[BUILT] analyze-dash-gap              → context-analysis/dash-gap-analysis.md      (41934 B, GROUNDED_BY=notebooklm)
[BUILT] build-uc-coverage-matrix      → context-analysis/uc-coverage-matrix.md     ( 9953 B, GROUNDED_BY=spec-only)
[BUILT] build-error-semantics         → context-analysis/error-semantics.md        (15668 B, GROUNDED_BY=spec-only)
[BUILT] extract-conformance-assertions→ context-analysis/conformance-assertions.md (39621 B, GROUNDED_BY=spec-only)
[BUILT] analyze-iab-ad-templates      → context-analysis/iab-ad-templates.md       (11102 B, GROUNDED_BY=iab-live-link)
[BLOCKED] build-spec (N=7) — awaiting the attribute-naming decision
```

All five Stage-1 artifacts regenerated against the current `context/`, each independently verified with a check proven able to fail first. Nothing committed, nothing pushed.

Say which way on the naming and I'll apply items 1/3 (+2 as you direct), then run Steps 6 → 7 → 7.5 → 8 and the refine loop straight through. If you'd rather have v7 now and correct in v8, say so and I'll resume immediately — it's your call, I just didn't want to spend the run without flagging it.

**Also queued, not blocking** (all the same species — September's `context/` rewrite left stale references behind it):
- `prompts/1-pre-spec/*.prompt` still say `R1..R7`/`R1..R10` and name the retired **Broadcaster** actor. Three workers each caught and compensated independently — correct output, but correctness currently rests on each worker noticing.
- `extract-conformance-assertions.prompt` targets 40–80 assertions; reality is 129. Next run either truncates or fires a false duplication signal.
- `context/03-requirements.md:745,802` cite the IAB doc as a Dec 2025 draft; it's Final Release May 2026. `:374` cites a private Google Doc where R12.1 wants the public IAB URL.
- Two load-bearing obligations sit outside the R-set entirely: the "MPD must still validate after stripping foreign-namespace nodes" rule (`08-dash-extension-rules.md:41`) and the 15-item backward-compat checklist.

Separately: the `cto-channel` MCP is down this session, so none of this reached you by the usual channel — transcript only.
