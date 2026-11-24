"""Runs T-05's edge vectors on the reference: composes a source directory
(spec-source/'s entries linked, plus this folder's fixtures/ as t05/) under
$XDG_RUNTIME_DIR/cto/, runs `check-dash-conformance.py --behaviour --source
<it> --vector E*.yaml --class D1`, and removes it. Extra arguments are passed
through (e.g. --out-json, --save-raw, --concurrency); positional names pick
vectors (E3 E5 ...). Exit: the check's."""
import contextlib, os, secrets, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


@contextlib.contextmanager
def edge_source():
    base = Path(os.environ.get("XDG_RUNTIME_DIR") or "/tmp") / "cto"
    base.mkdir(mode=0o700, exist_ok=True)
    d = base / f"t05-src-{secrets.token_hex(4)}"
    d.mkdir(mode=0o700)
    try:
        for e in (ROOT / "spec-source").iterdir():
            (d / e.name).symlink_to(e)
        (d / "t05").symlink_to(HERE / "fixtures")
        yield d
    finally:
        shutil.rmtree(d)


def edge_args(src, names=()):
    files = sorted(HERE.glob("E*.yaml"))
    if names:
        files = [f for f in files if any(f.name.startswith(n + "-") for n in names)]
    return ["--source", str(src)] + [a for f in files for a in ("--vector", str(f))]


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("-") and a[:1] == "E" and a[1:].isdigit()]
    rest = [a for a in sys.argv[1:] if a not in names]
    with edge_source() as src:
        cmd = ["python3", "bin/check-dash-conformance.py", "--behaviour", "--class", "D1"] + edge_args(src, names) + rest
        sys.exit(subprocess.run(cmd, cwd=ROOT).returncode)
