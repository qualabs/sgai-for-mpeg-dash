"""One break per rule of the fix, each run against test-seekable.mjs.
Usage: python3 mutate-unit.py <path to reference-player/src/sgai-linear.js> <tmp dir>"""
import subprocess, sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text(); tmp = pathlib.Path(sys.argv[2])
here = pathlib.Path(__file__).parent
M = {
  'M1 old guard (window end >= RT)': ("      if (!this.seekable(RT).holds) return;\n",
     "      if (this.player.isDynamic && this.player.isDynamic()) {\n        const w = this.player.getDvrWindow && this.player.getDvrWindow();\n        if (!w || !(w.end >= RT)) return;\n      }\n"),
  'M2 live delay ignored': ("const last = w.end - (delay > 0 ? delay : 0);", "const last = w.end;"),
  'M3 threshold exclusive': ("if (t > last + 0.001)", "if (t >= last)"),
  'M4 start of the buffer ignored': ("if (t < w.start - 0.001)", "if (false)"),
  'M5 clipped return not reported': ("if (!s.holds) this.log('linear:return-clipped'", "if (false) this.log('linear:return-clipped'"),
  'M6 no window counted as holding': ("if (!w || !isFinite(w.end)) return { holds: false", "if (!w || !isFinite(w.end)) return { holds: true"),
}
caught = 0
for name, (a, b) in M.items():
    assert src.count(a) == 1, name
    f = tmp / 'sgai-linear.mut.js'; f.write_text(src.replace(a, b))
    r = subprocess.run(['node', str(here / 'test-seekable.mjs'), str(f)], capture_output=True, text=True)
    red = r.returncode != 0; caught += red
    print(f"{'CAUGHT' if red else 'MISSED'} {name}: {r.stdout.strip().splitlines()[-1]}")
print(f"{caught}/{len(M)} caught")
sys.exit(0 if caught == len(M) else 1)
