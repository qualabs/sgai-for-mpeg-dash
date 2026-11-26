#!/bin/bash
# Each FAIL job of run2, alone (concurrency 1), twice: r1 then r2.
cd /home/nicolas/Develop/ai_workspace/cto-assistant/projects/sgai-for-mpeg-dash || exit 64
EV=.project/phases/11-reference-player/tasks/T-09/final/repeats
for r in r1 r2; do
  { date -Is; uptime; } > $EV/$r.start.txt
  PYTHONDONTWRITEBYTECODE=1 python3 -B bin/check-dash-conformance.py --behaviour --clock presentation --concurrency 1 \
    --log-dir $EV/$r-log --vector $EV/vectors/*.yaml > $EV/$r.summary.txt 2> $EV/$r.stderr.txt
  { date -Is; uptime; } > $EV/$r.end.txt
done
