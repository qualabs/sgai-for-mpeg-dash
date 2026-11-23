#!/usr/bin/env python3
"""Tests for level 3a (bin/conformance/players.py): the legacy Players.

One spec MPD (the one carrying a 6th-edition InsertPresentation, an overlay
window and a pause window) must PASS in dash.js and Shaka, and Shaka must
recognise its InsertPresentation. The same MPD with its video AdaptationSet
pointed at segments that do not exist must FAIL in both: a harness that
passes it does not measure playback.

The Player run needs node, ffmpeg and `npm ci` in bin/players; without them
the Player tests are skipped and say why. The rewrite tests always run.

Run:  python3 -m unittest bin/test_conformance_players.py   (from the project root)
"""
import os
import re
import sys
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)

from conformance import extract, players  # noqa: E402
from conformance.model import Outcome, Report  # noqa: E402

SPEC = os.path.join(os.path.dirname(BIN), "dist", "sgai-spec.md")


def spec_mpd():
    """The first main MPD with an InsertPresentation, an overlay window and a
    pause window — chosen by content, not by position."""
    with open(SPEC, encoding="utf-8") as f:
        text = f.read()
    for b in extract.blocks(text):
        if b.kind == "mpd" and all(s in b.text for s in (
                players.INSERT_SCHEME, "urn:svta:dash:sgai-overlay:2026",
                "urn:svta:dash:sgai-pause-trigger:2026", "<svta:")):
            return b
    raise AssertionError("no main MPD in the spec carries all three constructs")


def broken(text):
    """The video AdaptationSet gets a BaseURL outside the served content, so
    every one of its segments is a 404."""
    new, n = re.subn(r'(<AdaptationSet\b[^>]*contentType="video"[^>]*>)',
                     r"\1\n      <BaseURL>/missing/</BaseURL>", text, count=1)
    assert n == 1
    return new


class Rewrite(unittest.TestCase):
    def test_only_baseurl_changes(self):
        b = spec_mpd()
        new, changes = players.rewrite(b.text, "http://127.0.0.1:1/c/x/")
        self.assertEqual(len(changes), 1, changes)
        self.assertIn("<BaseURL>http://127.0.0.1:1/c/x/</BaseURL>", new)
        for keep in re.findall(r"<(?:svta:\w+|EventStream|Event|InsertPresentation)\b[^>]*>", b.text):
            self.assertIn(keep, new)

    def test_other_change_is_refused(self):
        with self.assertRaises(ValueError):
            players._same_but_baseurl(
                players.ET.fromstring('<MPD xmlns="%s"><Period id="a"/></MPD>' % players.DASH),
                players.ET.fromstring('<MPD xmlns="%s"><Period id="b"/></MPD>' % players.DASH))

    def test_broken_segments_are_not_served(self):
        new, _ = players.rewrite(broken(spec_mpd().text), "http://127.0.0.1:1/c/x/")
        p = players.plan(new, "http://127.0.0.1:1/c/x/")
        kinds = {info[0][0] for info in p["inits"].values()}
        self.assertEqual(kinds, {"audio"}, "the video init must fall outside the served content")


MISSING = players.missing_prerequisites()


@unittest.skipIf(MISSING, "level 3a cannot run here: " + "; ".join(MISSING))
class Players(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = spec_mpd()
        cls.ok_ref, cls.bad_ref = b.ref, b.ref + " broken"
        cls.report = Report()
        cls.results = players.run_documents(
            [(cls.ok_ref, b.text), (cls.bad_ref, broken(b.text))], cls.report)
        for r in cls.results:
            print(f"\n  {r.rule} {r.outcome.value} {r.subject}: {r.detail}", end="")
        print()

    def outcome(self, rule, subject):
        got = [r for r in self.results if r.rule == rule and r.subject == subject]
        self.assertEqual(len(got), 1, f"{rule} on {subject}: {got}")
        return got[0]

    def test_run_could_tell(self):
        self.assertEqual(self.report.cannot, [])

    def test_spec_mpd_passes(self):
        for rule in ("P-LEGACY-dashjs", "P-LEGACY-shaka", "P-INSERT-shaka"):
            r = self.outcome(rule, self.ok_ref)
            self.assertIs(r.outcome, Outcome.PASS, r.detail)

    def test_broken_mpd_fails(self):
        for rule in ("P-LEGACY-dashjs", "P-LEGACY-shaka"):
            r = self.outcome(rule, self.bad_ref)
            self.assertIs(r.outcome, Outcome.FAIL, r.detail)


if __name__ == "__main__":
    unittest.main()
