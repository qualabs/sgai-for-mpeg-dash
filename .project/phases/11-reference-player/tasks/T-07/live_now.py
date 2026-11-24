"""R25.1 on a live channel that can actually be joined at its `play_from`.

The fixture's availabilityStartTime is 2026-09-26, so its live edge is weeks
of media time away and 62 s left the 5-minute time-shift buffer long ago:
dash.js starts at the live edge and the pause window (60 s to 90 s) is never
reached (T-05's "dynamic MPDs cannot be joined at play_from"). This copies
the source to WORK, moves availabilityStartTime and publishTime of
behaviour/fixtures/R25.1/live.mpd to LEAD seconds before now, and runs the
unchanged R25.1 test on that source. Nothing else of the fixture changes.

Usage: live_now.py PROJECT WORK [LEAD=80] [extra check-dash-conformance args]"""
import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

proj, work = Path(sys.argv[1]), Path(sys.argv[2])
lead = int(sys.argv[3]) if len(sys.argv) > 3 else 80
src = work / "spec-source"
if src.exists():
    shutil.rmtree(src)
shutil.copytree(proj / "spec-source", src)
mpd = src / "behaviour/fixtures/R25.1/live.mpd"
now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
ast = (now - datetime.timedelta(seconds=lead)).strftime("%Y-%m-%dT%H:%M:%SZ")
text = mpd.read_text()
text = re.sub(r'availabilityStartTime="[^"]*"', f'availabilityStartTime="{ast}"', text)
text = re.sub(r'publishTime="[^"]*"', f'publishTime="{now.strftime("%Y-%m-%dT%H:%M:%SZ")}"', text)
mpd.write_text(text)
print(f"availabilityStartTime {ast} (now - {lead} s)", flush=True)
cmd = ["python3", "bin/check-dash-conformance.py", "--behaviour", "--source", str(src), "--only", "R25.1",
       "--concurrency", "1", *sys.argv[4:]]
sys.exit(subprocess.run(cmd, cwd=proj).returncode)
