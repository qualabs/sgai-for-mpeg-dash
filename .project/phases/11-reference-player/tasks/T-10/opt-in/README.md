# T-10 — the opt-in guard (ADR 0087): `bin/test_behaviour_opt_in.py`

11 tests, ~8 s, no Chromium (`test-run.out`). The executor is
`conformance.behaviour.run/drive/main` and `bin/players/behaviour.mjs`.

- **Runtime.** `check-dash-conformance.py` runs in process in every mode but
  `--behaviour` (document, `--source`, `--demo`, `--players --dashif` with the
  Players and the DASH-IF tool stubbed, the 64 paths) with the executor
  replaced by traps (a `BaseException`, so no `except Exception` hides it) and
  `subprocess.Popen` refusing any command carrying `--behaviour` or
  `behaviour.mjs`. `promote.py` runs its whole gate sequence, dry and real
  into a scratch dist, with its command runner replaced by a recorder; each
  recorded conformance command is then run in process under the traps. The
  prompts are read by what they invoke: every `check-dash-conformance.py`
  command of a fenced block (4 today: build-all Step 8.0, apply-context-delta
  ×3) runs in process under the traps.
- **Static.** No `.prompt` under `prompts/` or `.github-ai/prompts/` mentions
  the flag, the runner or `conformance.behaviour`. `bin/` (scripts and the
  suite's tests, by syntax tree; other text files by text) never imports the
  executor by name, never calls it on the module, never carries the flag or
  the runner in a string; docstrings are prose and are skipped, the helper
  import (`fixtures_of`) is allowed. Exempt: the battery's own files.
- **Controls.** `--behaviour` reaches the trap; the scan finds the entry in
  `check-dash-conformance.py` (lines 90, 95, 96) and the runner in
  `behaviour.py` (258, 269); 13 snippet cases of the scanner rules.

Evidence:

- `mutation-campaign.out` (`mutate.py`, on a scratch copy, never the repo):
  9 breaks, 9 red, baseline and after-restore green. M1 `--behaviour` on
  build-all's Step 8.0; M2 `node behaviour.mjs` in apply-context-delta (the
  incremental's apply step); M3 a promote gate shelling out with `--behaviour`;
  M4 promote calling `behaviour.run` in process; M5/M6 the document and
  `--source` modes of check-dash-conformance calling the executor (caught by
  runtime only, since that file is exempt from the scan); M7 a helper module
  (`conformance/runner.py`); M8 a test of the suite; M9 `run.mjs` spawning
  `behaviour.mjs`.
- `independent-check.out`: a plain `grep` over `bin/` and the prompts agrees
  with the scanner (outside the exempt files only `test_behaviour_compare.py`'s
  docstring and its helper import), and the 4 fenced commands grep finds are
  the 4 the reader extracts.
- `suite.out`: the whole `bin/test_*.py` suite once with a logging `node`
  shim on PATH. All OK but `test_check_behaviour.py` (9 failures, the
  live-tree ones another worker is fixing). `node` ran 3 times, all from
  `test_conformance_players.py` (level 3a, `run.mjs`): never `behaviour.mjs`.

Not covered: level 3a picking the `sgai` adapter by name (its run is stubbed
here); an invocation outside `bin/` and the prompts, or built dynamically.
