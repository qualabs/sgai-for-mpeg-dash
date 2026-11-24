#!/bin/bash
L=$XDG_RUNTIME_DIR/cto/t08a-logs
S=$HOME/.cache/cto-tmp/t08a-5qmQ34
LIVE=/home/nicolas/Develop/ai_workspace/cto-assistant/projects/sgai-for-mpeg-dash/reference-player/src
B=spec-source/behaviour
cd $S
for m in M3-R13.3-trim-ignored:R13.3-1 M4-R13.3-dismiss-flushes:R13.3-2 M5-R13.3-resume-flushes:R13.3-3 M6-R6.5-no-dedup:R6.5-1; do
  n=${m%%:*}; v=${m##*:}
  rsync -a $LIVE/ $S/reference-player/src/; python3 $L/mutate.py $n $S/reference-player/src/sgai-nonlinear.js >/dev/null
  echo "== $n ($v) exact beacon set"
  mkdir -p $L/mx-$n
  timeout 600 python3 bin/check-dash-conformance.py --behaviour --clock presentation --vector $B/$v.yaml --concurrency 1 --log-dir $L/mx-$n --save-raw $L/mx-$n/raw.json 2>&1 | grep -E "PASS|^exit" | cut -c1-200
  python3 $L/beacon_set.py $L/mx-$n/raw.json spec-source; echo "beacon_set exit $?"
done
rsync -a $LIVE/ $S/reference-player/src/
echo "== FINAL mine + edges"
mkdir -p $L/final-mine
timeout 1500 python3 bin/check-dash-conformance.py --behaviour --clock presentation --only R6.4,R6.5,R13.1,R13.3,R13.6 --vector $B/T08-E1.yaml --vector $B/T08-E2.yaml --concurrency 1 --log-dir $L/final-mine --save-raw $L/final-mine/raw.json 2>&1 | tail -12 | cut -c1-400
python3 $L/beacon_set.py $L/final-mine/raw.json spec-source; echo "beacon_set exit $?"
echo "== FINAL T-07 list"
mkdir -p $L/final-t07
timeout 2400 python3 bin/check-dash-conformance.py --behaviour --clock presentation --only R17.1,R17.2,R19.1,R19.3,R22.1,R31.2,R35.4,R40.4,R40.5,R40.9 --concurrency 1 --log-dir $L/final-t07 --save-raw $L/final-t07/raw.json 2>&1 | tail -20 | cut -c1-400
python3 $L/beacon_set.py $L/final-t07/raw.json spec-source; echo "beacon_set exit $?"
echo final-done
