set -u
cd /home/nicolas/Develop/ai_workspace/cto-assistant/projects/sgai-for-mpeg-dash
E=.project/phases/11-reference-player/tasks/T-08/linear-callback; D=/run/user/1000/cto/t08-lincb-1795560301-21285; F=reference-player/src/sgai-linear.js
run() { name=$1; old=$2; new=$3; cp $D/linear.final $F
  if [ -n "$old" ]; then python3 -c "import sys;p=sys.argv[1];s=open(p).read();assert s.count(sys.argv[2])==1;open(p,'w').write(s.replace(sys.argv[2],sys.argv[3]))" $F "$old" "$new" || { echo "$name: patch failed"; return; }; fi
  timeout 900 python3 reference-player/test/edges/run-edges.py E3 E12 E13 > $E/mutant-$name.log 2>&1; echo "== $name exit=$?"; grep -E "PASS|^FAIL" $E/mutant-$name.log | cut -c1-230; }
run baseline "" ""
run M1-no-end-tolerance "reached >= cur.duration - Math.max(EPS, alt.lag) ? cur.duration : reached" "reached"
run M2-always-part-end "reached >= cur.duration - Math.max(EPS, alt.lag) ? cur.duration : reached" "cur.duration"
run M3-crossing-always "const lag = crossed ? PRTA - E.PRT : 0;" "const lag = PRTA - E.PRT;"
run M4-lag-dropped "Math.max(EPS, alt.lag)" "EPS"
cp $D/linear.final $F; cmp $F $D/linear.final && echo restored
