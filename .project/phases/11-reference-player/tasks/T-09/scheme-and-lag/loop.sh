#!/bin/bash
# usage: loop.sh tag N throttle
T=/run/user/1000/cto/sgai11-scheme-lag-1795571048-14807
cd /home/nicolas/Develop/ai_workspace/cto-assistant/projects/sgai-for-mpeg-dash
fails=0
for i in $(seq 1 $2); do
  n=$1-$i; mkdir -p $T/$n
  python3 reference-player/test/edges/run-edges.py E14 --clock presentation --cpu-throttle $3 --save-raw $T/$n.raw.json --log-dir $T/$n > $T/$n.out 2>&1; rc=$?
  cr=$(python3 $T/xlog.py $T/$n.raw.json | grep crossing | sed -E "s/.*'crossed': ([A-Za-z]+).*'dphp': ([0-9.]+), 'dwall': ([0-9.]+).*/crossed=\1 dphp=\2 dwall=\3/")
  [ $rc -ne 0 ] && fails=$((fails+1))
  echo "$n exit=$rc $(head -1 $T/$n.out) | $cr | $(grep '^FAIL' $T/$n.out | cut -c1-140 | tr '\n' ' ')"
done
echo "$1: $fails of $2 runs failed"
