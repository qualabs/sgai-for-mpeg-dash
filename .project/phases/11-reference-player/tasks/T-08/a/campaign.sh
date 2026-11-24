#!/bin/bash
set -u
L=$XDG_RUNTIME_DIR/cto/t08a-logs
S=$HOME/.cache/cto-tmp/t08a-5qmQ34
LIVE=/home/nicolas/Develop/ai_workspace/cto-assistant/projects/sgai-for-mpeg-dash/reference-player/src
B=spec-source/behaviour
run() { # name vectors...
  local m=$1; shift
  rsync -a $LIVE/ $S/reference-player/src/
  python3 $L/mutate.py $m $S/reference-player/src/sgai-nonlinear.js >/dev/null || { echo "$m: mutation did not apply"; return; }
  local args=(); for v in "$@"; do args+=(--vector $B/$v.yaml); done
  echo "== $m ($*)"
  (cd $S && timeout 900 python3 bin/check-dash-conformance.py --behaviour --clock presentation "${args[@]}" --concurrency 1 --log-dir $L/mut-$m 2>&1 | grep -E "PASS|^FAIL .* beacons|^exit" | cut -c1-330)
}
run M1-R13.1-window-timebase R13.1
run M2-R13.6-first-option-only R13.6
run M3-R13.3-trim-ignored R13.3-1
run M4-R13.3-dismiss-flushes R13.3-2
run M5-R13.3-resume-flushes R13.3-3
run M6-R6.5-no-dedup R6.5-1
run M7-R6.5-document-scope R6.5-1
run M8-R6.4-drop-foreign-attr-events R6.4
run M9-slot-not-anchored-at-PT R19.1
rsync -a $LIVE/ $S/reference-player/src/
echo campaign-done
