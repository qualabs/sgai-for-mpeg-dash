"""lxml is the one dependency outside the standard library. When it is not
importable, the entry scripts re-run themselves under `uv run --with` the
pinned version, so the command a person types stays the same."""
import os
import shutil
import sys

LXML = "lxml==6.1.3"


def ensure_lxml(script: str, argv: list[str]) -> None:
    try:
        import lxml  # noqa: F401
        return
    except ImportError:
        pass
    uv = shutil.which("uv")
    if os.environ.get("SGAI_CONFORMANCE_REEXEC") or not uv:
        sys.stderr.write(f"cannot tell: lxml is not importable and `uv` is not available to run with {LXML}\n")
        raise SystemExit(2)
    env = dict(os.environ, SGAI_CONFORMANCE_REEXEC="1")
    os.execve(uv, [uv, "run", "-q", "--no-project", "--with", LXML, "python", "-I", script, *argv], env)
