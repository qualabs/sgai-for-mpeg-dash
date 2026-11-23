#!/usr/bin/env python3
"""Write the extension schema of a candidate specification as a file.

    emit-extension-xsd.py SPEC.md [OUT.xsd]

The schema is the spec's §5.10.1 block, the single ```xml block whose root is
xs:schema with targetNamespace urn:svta:dash:sgai:2026. It is copied byte for
byte, so file and block are identical by construction (ADR 0047). OUT defaults
to v<N>-sgai-extension.xsd beside v<N>-sgai-spec.md.

Exit codes:
  0   written, and it compiles together with ISO's 6th-edition DASH-MPD.xsd
  1   the block does not compile together with DASH-MPD.xsd (E-1); nothing written
  2   cannot tell: no such block, more than one, or ISO's pinned schema unavailable
  64  wrong command line
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from conformance.deps import ensure_lxml  # noqa: E402


def main(argv):
    if not argv or argv[0] in ("-h", "--help") or len(argv) > 2 or argv[0].startswith("-"):
        print(__doc__)
        return 0 if argv and argv[0] in ("-h", "--help") else 64
    ensure_lxml(os.path.abspath(__file__), argv)
    from pathlib import Path
    from conformance import ext, extract, iso

    spec = Path(argv[0])
    if not spec.exists():
        sys.stderr.write(f"specification not found: {spec}\n")
        return 64
    if len(argv) == 2:
        out = Path(argv[1])
    else:
        name = spec.name
        stem = name[: -len("-sgai-spec.md")] if name.endswith("-sgai-spec.md") else spec.stem
        out = spec.with_name(f"{stem}-sgai-extension.xsd")
    blocks = extract.extension_schema(extract.blocks(spec.read_text(encoding="utf-8")))
    if len(blocks) != 1:
        print(f"cannot tell: {len(blocks)} extension schema blocks in {spec}; exactly one is needed")
        return 2
    try:
        isodir = iso.materialise()
    except iso.Unavailable as e:
        print(f"cannot tell: {e}")
        return 2
    schema, err = ext.compile_extension(blocks[0].text, isodir)
    if schema is None:
        print(f"FAIL: {blocks[0].ref} does not compile together with DASH-MPD.xsd: {err}")
        return 1
    out.write_bytes(blocks[0].text.encode("utf-8"))
    print(f"wrote {out} from {blocks[0].ref}; compiles together with ISO 6th-edition DASH-MPD.xsd")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
