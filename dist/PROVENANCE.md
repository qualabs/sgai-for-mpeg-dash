# What is published here, and where it came from

| | |
|---|---|
| **Candidate promoted** | `v7.2` |
| **Promoted on** | 2026-09-17 |
| **Promoted by** | manual — no criterion was applied |

The files in this directory are `output/v7.2-sgai-spec.md` and its three
`output-analysis/v7.2-*` sidecars, renamed without the version prefix.

**This record exists for two readers.**

A person asking "which build is this?" — the unversioned filenames are
deliberate, so the answer is not in the name, and git history alone does
not distinguish a promotion from an edit.

And the build orchestrator, which numbers the next candidate. It scans
`output/` for `v<N>-sgai-spec.md` and takes `max(N) + 1`. `output/` is
emptied on promotion, so without this record the counter restarts at 1
and reuses names that git history already holds for unrelated documents.
The next candidate is numbered from the value above.

**It was promoted without a criterion.** No check decided that `v7.2`
had earned publication: the restructure that created this directory had
to put something in it, and `v7.2` was the newest candidate. The
promotion criterion is `bin/check-promotable.py`, and run against what
is published here it exits `2` — the sidecars predate the per-criterion
coverage map, so it cannot tell. That is the honest state and it is
recorded rather than left to be discovered.
