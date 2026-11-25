"""One deliberate break per rule of live_utc_at_load / player_live_delay;
each must turn the tests that cover it red. Restores the file after each."""
import subprocess
from pathlib import Path

F = Path("bin/conformance/behaviour.py")
TESTS = ["Jobs.test_live_now", "Jobs.test_live_now_at_play_from_zero", "Jobs.test_live_delay_follows_dash_js_order"]
M = [
    ("L1", "now has no live delay", "(play_from_s + player_live_delay(root) + lead_s)", "(play_from_s + lead_s)"),
    ("L2", "the lead is the whole span at the rate (the old rule)", "observe / 1000 * (rate - 1))", "observe / 1000 * rate)"),
    ("L3", "the lead is dropped", "observe / 1000 * (rate - 1))", "0)"),
    ("L4", "suggestedPresentationDelay ignored", "    if spd > 0:\n        return spd\n", ""),
    ("L5", "a zero suggestedPresentationDelay taken", "if spd > 0:", "if spd >= 0:"),
    ("L6", "S@d ignored", ' + [float(s.get("d") or 0) for s in t.iter(D + "S")]', ""),
    ("L7", "segment factor 4 -> 1", "        return 4 * seg", "        return seg"),
    ("L8", "minBufferTime fallback dropped", '    return 4 * players._dur(root.get("minBufferTime"))', "    return 0.0"),
    ("L9", "timescale ignored", "ds = [float", "ts = 1; ds = [float"),
]
orig = F.read_text()
try:
    for mid, what, a, b in M:
        assert orig.count(a) == 1, (mid, orig.count(a))
        F.write_text(orig.replace(a, b))
        p = subprocess.run(["python3", "bin/test_behaviour_harness.py", *TESTS], capture_output=True, text=True)
        failed = [l for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        print(f"{mid} {'CAUGHT ' if p.returncode else 'MISSED '} {what}  -> {'; '.join(failed) or 'all green'}")
finally:
    F.write_text(orig)
