#!/usr/bin/env python3
"""One deliberate break per rule of the summary; each must turn
bin/test_behaviour_summary.py red. Restores behaviour.py byte for byte."""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[6]
F = ROOT / "bin/conformance/behaviour.py"
MUT = [
    ("counts: NOT_VERIFIABLE not shown", 'for k in ("FAIL", "NOT_VERIFIABLE"):', 'for k in ("FAIL",):'),
    ("FAIL line: class dropped", 'FAIL {cut(test, width)} {cls} ', 'FAIL {cut(test, width)} '),
    ("FAIL line: observed not cut", '| observed: {cut(obs, width)}', '| observed: {obs}'),
    ("cut: off by one", 's[:n - 3] + "..."', 's[:n - 2] + "..."'),
    ("cut: newlines kept", 's = " ".join(str(s).split())', 's = str(s)'),
    ("log pointer: 0-based", 'enumerate(report.results, 1)', 'enumerate(report.results)'),
    ("PASS listed too", 'if r.outcome is not Outcome.FAIL:', 'if r.outcome is Outcome.NOT_VERIFIABLE:'),
    ("cannot tell dropped", 'out += [f"cannot tell: {cut(x, width)}" for x in report.cannot]', 'pass'),
    ("exit line: exit code missing", 'out.append(f"exit {report.exit_code()}; wall', 'out.append(f"exit; wall'),
    ("split: no observed seam", '(_OBSERVED, _NOT_OBSERVED)', '(_NOT_OBSERVED,)'),
    ("subject: variant lost", 'm["test"] + (m["variant"] or "")', 'm["test"]'),
    ("log dir: not unique", '+ "-" + secrets.token_hex(3)', ''),
]
orig = F.read_bytes()
bad = 0
try:
    for name, a, b in MUT:
        s = orig.decode()
        assert s.count(a) == 1, name
        F.write_text(s.replace(a, b))
        r = subprocess.run([sys.executable, str(ROOT / "bin/test_behaviour_summary.py")], capture_output=True, text=True)
        red = r.returncode != 0
        bad += not red
        print(f"{'RED  ' if red else 'GREEN'} {name}")
finally:
    F.write_bytes(orig)
print(f"{len(MUT) - bad}/{len(MUT)} mutations caught")
sys.exit(1 if bad else 0)
