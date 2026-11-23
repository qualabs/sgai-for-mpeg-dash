#!/usr/bin/env python3
"""Tests of the conformance core: extraction, the extension XSD as a file,
E-1..E-4 and the committed negative cases of E (fixtures/negative/core-*).

Run from the project root:
  uv run -q --no-project --with lxml==6.1.3 python -I bin/test_conformance_core.py
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent
ROOT = BIN.parent
sys.path.insert(0, str(BIN))

from conformance import ext, extract, fixtures, iso, runner  # noqa: E402
from conformance.model import Outcome, Report  # noqa: E402

DIST = ROOT / "dist" / "sgai-spec.md"


def base_ctx():
    rep = Report()
    ctx = runner.load(DIST, ROOT / "context", rep)
    assert ctx is not None and not rep.cannot, rep.cannot
    return ctx


class Extract(unittest.TestCase):
    def test_counts_on_published_spec(self):
        bs = extract.blocks(DIST.read_text())
        self.assertEqual(len(bs), 84)
        s = extract.summary(bs)
        self.assertEqual(s.get("mpd", 0) + s.get("list-mpd", 0) + s.get("sps-mpd", 0), 52)
        self.assertEqual(s["overlay-list"], 23)
        self.assertEqual(s["ext-xsd"], 1)
        self.assertEqual(s["vast"], 2)
        self.assertEqual(s["fragment"], 6)

    def test_lines_point_at_the_block(self):
        lines = DIST.read_text().splitlines()
        for b in extract.blocks(DIST.read_text()):
            self.assertEqual(lines[b.line - 2].strip(), "```xml", b.ref)

    def test_requests(self):
        rs = extract.requests(DIST.read_text())
        self.assertEqual(len(rs), 12)
        first = dict(rs[0].params)
        self.assertEqual(first["sgai-allowed-layouts"], "overlay-lower-third squeezeback-l-shape-upper-left")

    def test_malformed_is_classified(self):
        b = extract.Block(1, 1, "<MPD")
        extract.classify(b)
        self.assertEqual(b.kind, "malformed")


class Emitter(unittest.TestCase):
    def run_emit(self, *args):
        p = subprocess.run([sys.executable, str(BIN / "emit-extension-xsd.py"), *args],
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def test_exit_codes_and_identity(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("XDG_RUNTIME_DIR")) as d:
            spec = Path(d) / "v1-sgai-spec.md"
            text = DIST.read_text()
            spec.write_text(text)
            rc, out = self.run_emit(str(spec))
            self.assertEqual(rc, 0, out)
            xsd = Path(d) / "v1-sgai-extension.xsd"
            block = extract.extension_schema(extract.blocks(text))[0]
            self.assertEqual(xsd.read_bytes(), block.text.encode())
            self.assertEqual(ext.identity(xsd, block)[0].outcome, Outcome.PASS)
            xsd.write_bytes(xsd.read_bytes() + b" ")
            self.assertEqual(ext.identity(xsd, block)[0].outcome, Outcome.FAIL)
            # no block -> 2
            spec.write_text(text.replace('targetNamespace="urn:svta:dash:sgai:2026"', 'targetNamespace="urn:x"'))
            self.assertEqual(self.run_emit(str(spec))[0], 2)
            # two blocks -> 2
            spec.write_text(text + "\n```xml\n" + block.text + "```\n")
            self.assertEqual(self.run_emit(str(spec))[0], 2)
            # does not compile -> 1, nothing written
            xsd.unlink()
            spec.write_text(text.replace("dash:EventStreamType", "dash:EventStreamTypo", 1))
            self.assertEqual(self.run_emit(str(spec))[0], 1)
            self.assertFalse(xsd.exists())
            self.assertEqual(self.run_emit()[0], 64)


class Level1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = base_ctx()

    def test_published_extension_passes_e1_e2(self):
        self.assertEqual([r.outcome for r in ext.e1(self.ctx.ext_text, self.ctx.isodir)], [Outcome.PASS])
        self.assertEqual([r.outcome for r in ext.e2(self.ctx.ext_text)], [Outcome.PASS])

    def test_iso_examples_pass_e3_e4(self):
        """Reference independent of us: ISO's own 6th-edition examples."""
        globals_ = ext.global_elements([self.ctx.ext_text, (self.ctx.isodir / "DASH-MPD.xsd").read_text()])
        ex = iso.examples(self.ctx.isodir)
        self.assertEqual(len(ex), 41)
        bs = []
        for i, p in enumerate(ex, 1):
            b = extract.Block(i, 1, p.read_text())
            extract.classify(b)
            bs.append(b)
        bad = [r for r in ext.e3(bs, self.ctx.combined, globals_) + ext.e4(bs, self.ctx.iso)
               if r.outcome is Outcome.FAIL]
        self.assertEqual(bad, [])

    def test_iso_schema_alone_misses_extension_errors(self):
        """Why the extension XSD is loaded: lax accepts what it does not know."""
        case = fixtures.NEG / "core-E3-bogus-attr-on-clickthrough.xml"
        b = extract.Block(1, 1, case.read_text())
        extract.classify(b)
        from lxml import etree
        self.assertTrue(self.ctx.iso.validate(etree.XML(b.text.encode())))
        self.assertFalse(self.ctx.combined.validate(etree.XML(b.text.encode())))


class Negatives(unittest.TestCase):
    """Every committed negative is caught by its rule. Core cases here; the
    catalogs' own test files run theirs, and test_negatives_all runs all."""

    @classmethod
    def setUpClass(cls):
        cls.ctx = base_ctx()

    def test_core_negatives(self):
        for p in fixtures.negatives():
            if not p.name.startswith("core-"):
                continue
            with self.subTest(p.name):
                v = fixtures.evaluate(p, self.ctx, runner.run_all)
                self.assertTrue(v["caught"], f"{v['name']}: {v['expected']['rule']} did not FAIL; other fails {v['other_fails']}")


if __name__ == "__main__":
    unittest.main()
