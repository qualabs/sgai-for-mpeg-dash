# T-09 routing fix: which fixture answers a document request

**Defect.** Several fixtures at one URL: the runner answered every request with
the first (`job.documents.find`), so a class's, a variant's or a second answer
never reached the Player (55 FAILs, 19 jobs, UC-05/12/13/15).

**Fix.** `conformance/behaviour.py:document_routes` builds, from the job's
outcome `requests[].answered_by`, per URL the ordered answers (most specific
URL first); the runner (`players/routing.mjs:routeAnswer`) answers the n-th
request to a route with the n-th answer, the last one from then on. URLs the
outcome does not list keep the old answer (the first fixture declared there).

## Rerun of the 19 jobs (presentation clock, concurrency 2, one-job-set copies)

`summary.txt`, `full-log/`: 66 PASS, 10 FAIL (before: 55 FAIL on these jobs).

| Job | Before (FAIL fields) | After |
|---|---|---|
| UC-05 D1, D2 | req, sel, pres, beac | 4 FAIL in the rerun; 4 PASS each on a reference snapshot (control) |
| UC-05 D3, D4 | req, sel, pres, beac | 4 PASS |
| UC-12 path-2 D1-D4 | req, sel, pres, beac | 4 PASS |
| UC-12 path-2 D5, path-4 D3-D5 | req | 4 PASS |
| UC-13 D2, D5 | req, sel, pres, beac | 4 PASS |
| UC-13 D3, D4 | req, sel, pres, beac | requests FAIL, rest PASS |
| UC-15 D2, D5, non-conforming-aps D2 | req | 4 PASS |

**UC-05 D1/D2 in the rerun** — instrument (environment): the reference was
being edited during the run (it is served live from disk, per job). In those
two jobs it fetched the pause APS at load and again at the pause; the second
answer is the empty E.7.1-1, so nothing showed. Control (`control/`): the same
snapshot of `reference-player/src`, the same one-job vector, HEAD's harness vs
this one: D1 HEAD 0 PASS / 4 FAIL (the original defect), this one 4 PASS; D2
this one 4 PASS.

**UC-13 D3/D4 requests** — test (vector): the expected query follows M.3 (D3
omits the HTML axis, D4 sends no capability), but `sends_capabilities` is one
list for the whole vector, so the harness discloses all three axes for every
class. Masked before by the routing defect.
