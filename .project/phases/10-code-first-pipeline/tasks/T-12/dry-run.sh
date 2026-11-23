#!/usr/bin/env bash
# T-12 dry run: the incremental and the minor of the new pipeline, with no
# LLM. Hand-written patches stand in for the agents; every other step is
# the command the prompts give. Runs on a scratch copy of the project
# (~/.cache/cto-tmp/t12-dry-<random>), removed at the end; the real tree is
# only read.
#
#   bash .project/phases/10-code-first-pipeline/tasks/T-12/dry-run.sh
#
# Order: (b) incremental v12.6 -> v12.7 first, because the first build on the
# new pipeline is the one that applies the one-time cleanup; then (a) a minor
# v12.7 -> v12.8 and its rollback.
set -u
REAL="$(cd "$(dirname "$0")/../../../../.." && pwd)"
HERE="$REAL/.project/phases/10-code-first-pipeline/tasks/T-12"
mkdir -p "$HOME/.cache/cto-tmp" && chmod 700 "$HOME/.cache/cto-tmp"
S="$(mktemp -d "$HOME/.cache/cto-tmp/t12-dry-XXXXXX")"
trap 'rm -rf "$S"' EXIT
PY=(uv run -q --with lxml==6.1.3 --with pyyaml==6.0.3 --with jsonschema==4.25.1 python3)

run() {  # print the command, its output and its exit
  echo "\$ $*"
  "$@" 2>&1 | sed 's/^/  /'
  local e=${PIPESTATUS[0]}
  echo "  [exit $e]"
  return 0
}
run_tail() {  # the same, keeping the last two lines of the output
  echo "\$ $*"
  "$@" > "$W/out.txt" 2>&1
  local e=$?
  tail -2 "$W/out.txt" | sed 's/^/  /'
  echo "  [exit $e]"
}

rsync -a --exclude bin/players --exclude .worktrees --exclude '__pycache__' "$REAL/" "$S/"
cd "$S"
git config user.email dry-run@example.invalid; git config user.name dry-run
# The trace left by the incremental that ended MAJOR RECOMMENDED has no
# candidate; the dry run writes its own v12.7.
rm -f output-analysis/v12.7-context-delta.md
W="$S/.w"; mkdir -p "$W"

echo "=================== (b) INCREMENTAL v12.6 -> v12.7 ==================="
echo "--- Stage 0: preconditions"
run python3 bin/assemble-spec.py --check output/v12.6-sgai-spec.md
run python3 bin/check-incremental.py anchor v12.6
ANCHOR=$(python3 bin/check-incremental.py anchor v12.6 2>/dev/null)
# The scratch's own context commit: the delta this dry run places.
sed -i 's/first-window-wins with fallback\./first window wins, the next one is the fallback./' context/03-requirements.md
git add context/03-requirements.md && git commit -qm "dry-run: R20 title reworded"
HEAD=$(git rev-parse HEAD)
run git log --format='%h %s' -1 -- context/

echo "--- apply-context-delta §0: the base, recorded"
run python3 bin/assemble-spec.py --version v12.6 --out "$W/base.md" --manifest "$W/base.sha256"
run cmp "$W/base.md" output/v12.6-sgai-spec.md
find spec-source -type f -not -path 'spec-source/syntax/tables/*' | sort | xargs sha256sum > "$W/base-files.sha256"
find spec-source -type f | sort | xargs sha256sum > "$W/base-all.sha256"
run "${PY[@]}" bin/check-dash-conformance.py --source spec-source --out-json "$W/conf-base.json" --out-md "$W/conf-base.md"
run_tail "${PY[@]}" bin/check-scenarios.py --source spec-source

echo "--- §1: the one-time cleanup"
run "${PY[@]}" bin/strip-legacy-annotations.py --out output-analysis/v12.7-delta-patch-0.json
run python3 bin/apply-spec-patch.py output-analysis/v12.7-delta-patch-0.json --record output-analysis/v12.7-delta-patch-0.json
run "${PY[@]}" bin/gen-syntax-tables.py --write
run "${PY[@]}" bin/strip-legacy-annotations.py --out "$W/again.json"

echo "--- §4: artefacts first (patch 1: a fixture and syntax.yaml), then the code loop"
cp "$HERE/patches/v12.7-delta-patch-1.json" output-analysis/
run python3 bin/apply-spec-patch.py output-analysis/v12.7-delta-patch-1.json --record output-analysis/v12.7-delta-patch-1.json --max-fraction 0.30
run "${PY[@]}" bin/gen-syntax-tables.py --write
run "${PY[@]}" bin/check-dash-conformance.py --source spec-source --out-json "$W/conf.json" --out-md "$W/conf.md"
run_tail "${PY[@]}" bin/check-scenarios.py --source spec-source

echo "--- §5: the prose by section (patch 2: the R20 change and the lint finding the base carried)"
cp "$HERE/patches/v12.7-delta-patch-2.json" output-analysis/
run python3 bin/apply-spec-patch.py output-analysis/v12.7-delta-patch-2.json --record output-analysis/v12.7-delta-patch-2.json --max-fraction 0.30

echo "--- §6: assemble and check"
run "${PY[@]}" bin/gen-syntax-tables.py --check
run python3 bin/assemble-spec.py --version v12.7 --out output/v12.7-sgai-spec.md --manifest output-analysis/v12.7-source.sha256
run python3 bin/lint-spec.py output/v12.7-sgai-spec.md
run "${PY[@]}" bin/check-dash-conformance.py --source spec-source --out-json "$W/conf.json" --out-md "$W/conf.md"
run_tail "${PY[@]}" bin/check-scenarios.py --source spec-source

echo "--- §7: which sections changed, from the records, the manifests and {{version}} (code)"
"${PY[@]}" "$HERE/sections-changed.py" v12.6 v12.7 "$W/base.sha256" > "$W/rows.md"
run cat "$W/rows.md"
run diff "$W/base.sha256" output-analysis/v12.7-source.sha256
find spec-source -type f -not -path 'spec-source/syntax/tables/*' | sort | xargs sha256sum > "$W/head-files.sha256"
run diff "$W/base-files.sha256" "$W/head-files.sha256"

echo "--- §8: the trace"
{
  echo "# v12.7 — context delta applied to v12.6"; echo
  echo "- Mode: incremental"
  echo "- Base candidate: \`output/v12.6-sgai-spec.md\`"
  echo "- Context base: \`$ANCHOR\` (from \`bin/check-incremental.py anchor v12.6\`)"
  echo "- Context head: \`$HEAD\`"
  echo "- Patches: \`output-analysis/v12.7-delta-patch-0.json\` … \`-2.json\`"
  echo "- Delta: dry run — only the scratch commit is placed (stand-in for the agent)"
  echo; echo "## Commits"; echo; echo "| Commit | Subject |"; echo "|--------|---------|"
  echo "| ${HEAD:0:7} | dry-run: R20 title reworded |"
  echo; echo "## Changes placed"; echo
  echo "| # | Commit | Context unit | Change | Spec section(s) | Artefact(s) | Edit |"
  echo "|---|--------|--------------|--------|-----------------|-------------|------|"
  echo "| 1 | ${HEAD:0:7} | R20 | reworded | 7.12 | examples/annex-a/A.2-1.mpd, syntax/syntax.yaml | dry-run edits |"
  echo; echo "## No spec effect"; echo; echo "| # | Commit | Context unit | Change | Why |"; echo "|---|---|---|---|---|"
  echo; echo "## Not placed"; echo; echo "| # | Commit | Context unit | Change | Class | Why |"; echo "|---|---|---|---|---|---|"
  echo; echo "## Artefacts changed"; echo; echo "| File | Change | Rows |"; echo "|------|--------|------|"
  echo "| examples/annex-a/A.2-1.mpd | modified | 1 |"; echo "| syntax/syntax.yaml | modified | 1 |"
  echo; cat "$W/rows.md"
} > output-analysis/v12.7-context-delta.md
run python3 bin/check-incremental.py scope v12.6 v12.7
run python3 bin/check-incremental.py anchor v12.7
echo "--- negative: a recorded section left out of the table is REJECT"
sed '/^| 5\.1\.3 |/d' output-analysis/v12.7-context-delta.md > "$W/t.md"; cp output-analysis/v12.7-context-delta.md "$W/keep.md"; cp "$W/t.md" output-analysis/v12.7-context-delta.md
run python3 bin/check-incremental.py scope v12.6 v12.7
cp "$W/keep.md" output-analysis/v12.7-context-delta.md

echo "--- Step 6.1 and the identity"
run "${PY[@]}" bin/emit-extension-xsd.py output/v12.7-sgai-spec.md
run cmp output/v12.7-sgai-extension.xsd spec-source/syntax/sgai-extension.xsd
run python3 bin/assemble-spec.py --check output/v12.7-sgai-spec.md

echo "--- check-trace: the v12.6 trace, made literal (T-08's population), carried to v12.7"
"${PY[@]}" "$HERE/carry-trace.py" base output-analysis/v12.6-trace.json output/v12.6-sgai-spec.md \
  .project/phases/10-code-first-pipeline/tasks/T-08/population-924afcb.tsv output-analysis/v12.6-trace.literal.json
run "${PY[@]}" bin/check-trace.py output-analysis/v12.6-trace.literal.json --population .project/phases/10-code-first-pipeline/tasks/T-08/population-924afcb.tsv --summary
run "${PY[@]}" bin/check-trace.py stale output-analysis/v12.6-trace.literal.json --old output/v12.6-sgai-spec.md --new output/v12.7-sgai-spec.md
"${PY[@]}" bin/check-trace.py stale output-analysis/v12.6-trace.literal.json --old output/v12.6-sgai-spec.md --new output/v12.7-sgai-spec.md > "$W/stale.json"
"${PY[@]}" "$HERE/carry-trace.py" carry output-analysis/v12.6-trace.literal.json output/v12.7-sgai-spec.md "$W/stale.json" output-analysis/v12.7-trace.json
run "${PY[@]}" bin/check-trace.py output-analysis/v12.7-trace.json --population .project/phases/10-code-first-pipeline/tasks/T-08/population-924afcb.tsv --summary

echo "--- the restore of a failed incremental (patches 2, 1, 0 reversed), on a copy"
cp -a spec-source "$W/src-copy"
for k in 2 1 0; do run python3 bin/apply-spec-patch.py --reverse output-analysis/v12.7-delta-patch-$k.json --source "$W/src-copy/sgai-spec.src.md"; done
run "${PY[@]}" bin/gen-syntax-tables.py --source "$W/src-copy" --findings "$W/f.md" --write
run python3 bin/assemble-spec.py --source "$W/src-copy" --check output/v12.6-sgai-spec.md
(cd "$W" && find src-copy -type f | sort | xargs sha256sum | sed 's# src-copy/# spec-source/#' > "$W/restored-all.sha256")
run diff "$W/base-all.sha256" "$W/restored-all.sha256"

echo "=================== (a) MINOR v12.7 -> v12.8, and its rollback ==================="
run python3 bin/assemble-spec.py --check output/v12.7-sgai-spec.md
find spec-source -type f | sort | xargs sha256sum > "$W/before-minor.sha256"
cp "$HERE/patches/v12.8-patch.json" output-analysis/
echo "--- 9.1 refine (the hand-written patch stands in for refine-spec)"
run python3 bin/apply-spec-patch.py output-analysis/v12.8-patch.json --record output-analysis/v12.8-patch.json
echo "--- 9.2 assemble, lint, Step 6.1"
run "${PY[@]}" bin/gen-syntax-tables.py --write
run python3 bin/assemble-spec.py --version v12.8 --out output/v12.8-sgai-spec.md --manifest output-analysis/v12.8-source.sha256
run python3 bin/lint-spec.py output/v12.8-sgai-spec.md
run "${PY[@]}" bin/emit-extension-xsd.py output/v12.8-sgai-spec.md
run cmp output/v12.8-sgai-extension.xsd spec-source/syntax/sgai-extension.xsd
run python3 bin/assemble-spec.py --check output/v12.8-sgai-spec.md
echo "--- 9.3 conformance tests over the source"
run "${PY[@]}" bin/check-dash-conformance.py --source spec-source --out-md output-analysis/v12.8-conformance-tests.md --out-json output-analysis/v12.8-conformance-tests.json
echo "--- 9.4 validation scope: check-trace stale, and the carried trace checked"
run "${PY[@]}" bin/check-trace.py stale output-analysis/v12.7-trace.json --old output/v12.7-sgai-spec.md --new output/v12.8-sgai-spec.md
"${PY[@]}" bin/check-trace.py stale output-analysis/v12.7-trace.json --old output/v12.7-sgai-spec.md --new output/v12.8-sgai-spec.md > "$W/stale8.json"
"${PY[@]}" "$HERE/carry-trace.py" carry output-analysis/v12.7-trace.json output/v12.8-sgai-spec.md "$W/stale8.json" output-analysis/v12.8-trace.json
run "${PY[@]}" bin/check-trace.py output-analysis/v12.8-trace.json --population .project/phases/10-code-first-pipeline/tasks/T-08/population-924afcb.tsv --summary
echo "--- 9.4a names: the code half"
run "${PY[@]}" bin/gen-syntax-tables.py --check
run "${PY[@]}" bin/name-candidates.py
echo "--- 9.7 WORSE: the restore"
run python3 bin/apply-spec-patch.py --reverse output-analysis/v12.8-patch.json
run "${PY[@]}" bin/gen-syntax-tables.py --write
run python3 bin/assemble-spec.py --check output/v12.7-sgai-spec.md
find spec-source -type f | sort | xargs sha256sum > "$W/after-rollback.sha256"
run diff "$W/before-minor.sha256" "$W/after-rollback.sha256"
echo "  spec-source sha256 of the file list: before $(sha256sum < "$W/before-minor.sha256" | cut -c1-16)  after $(sha256sum < "$W/after-rollback.sha256" | cut -c1-16)"
echo "--- a second --reverse is refused, nothing written"
run python3 bin/apply-spec-patch.py --reverse output-analysis/v12.8-patch.json
echo "=================== the real tree's invariant ==================="
cd "$REAL"
run python3 bin/assemble-spec.py --check dist/sgai-spec.md
