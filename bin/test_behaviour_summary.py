#!/usr/bin/env python3
"""Tests for what the behaviour battery prints (bin/conformance/behaviour.py,
summary_lines / full_lines / split_detail / split_subject). On synthetic
reports only: no browser, no server, no Player (ADR 0087).

What a green says: stdout's summary has the counts line, one line per FAIL
with test, class, field, expected, observed (each cut to the width) and the
log line that FAIL is on, one line per job that could not run, and a last
line with the exit, wall clock and log path; nothing else of the full output
reaches it. It says nothing about the run itself.

Run:  python3 bin/test_behaviour_summary.py
"""
import os
import sys
import unittest
from pathlib import Path

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)

from conformance import behaviour  # noqa: E402
from conformance.model import Outcome, Report, Result  # noqa: E402

LOG = Path("/run/user/0/cto/behaviour-logs/x/behaviour.log")
BEACON_FAIL = ("beacons[0] https://ads.example/imp (@id 1) expected at 10; observed at 13.4")


def report(*results, cannot=(), notes=()):
    r = Report()
    r.notes = list(notes)
    r.add(list(results))
    r.cannot.extend(cannot)
    return r


def ok(subject="R4.9-insert D1", field="presentation"):
    return Result(field, Outcome.PASS, subject, detail="3 segment(s) as expected")


def fail(subject="R4.9-insert D1", field="beacons", detail=BEACON_FAIL):
    return Result(field, Outcome.FAIL, subject, detail=detail)


def nv(subject="R4.9-insert D1", field="audio"):
    return Result(field, Outcome.NOT_VERIFIABLE, subject, detail="what is heard is not recorded")


class Summary(unittest.TestCase):
    def lines(self, rep, wall=12.34):
        return behaviour.summary_lines(rep, wall, LOG)

    def test_zero_fails(self):
        out = self.lines(report(ok(), ok(field="requests")))
        self.assertEqual(out[0], "2 PASS")
        self.assertEqual(len(out), 2)
        self.assertEqual(out[-1], f"exit 0; wall 12.3 s; full log: {LOG}")

    def test_all_fail(self):
        rep = report(fail(), fail(subject="UC-03 D2 [seek]", field="presentation",
                                  detail="presentation[1] 0..5 expected main; observed ad from 0 to 5"))
        out = self.lines(rep)
        self.assertEqual(out[0], "0 PASS, 2 FAIL")
        self.assertEqual(len(out), 4)
        self.assertEqual(out[1], "FAIL R4.9-insert D1 beacons | expected: beacons[0] https://ads.example/imp "
                                 f"(@id 1) expected at 10 | observed: observed at 13.4 | log: {LOG}:1")
        self.assertTrue(out[2].startswith("FAIL UC-03 [seek] D2 presentation | expected: presentation[1] 0..5 "
                                          "expected main | observed: observed ad from 0 to 5"))
        self.assertTrue(out[2].endswith(f"log: {LOG}:2"))
        self.assertTrue(out[-1].startswith("exit 1; wall 12.3 s"))

    def test_log_line_points_at_the_fail_in_the_full_output(self):
        rep = report(ok(), nv(), fail(), ok())
        out = self.lines(rep)
        line_no = int(out[1].rsplit(":", 1)[1])
        full = behaviour.full_lines(rep, 1.0, None)
        self.assertTrue(full[line_no - 1].startswith("FAIL"))
        self.assertIn(BEACON_FAIL, full[line_no - 1])

    def test_very_long_observed_is_cut(self):
        long_obs = "x" * 5000
        rep = report(fail(detail=f"geometry[0] at 3 expected full; observed {long_obs}"))
        out = self.lines(rep)
        self.assertEqual(len(out), 3)
        obs = out[1].split("| observed: ", 1)[1].split(" | log: ", 1)[0]
        self.assertEqual(len(obs), behaviour.SUMMARY_WIDTH)
        self.assertTrue(obs.endswith("..."))
        self.assertLess(len(out[1]), 3 * behaviour.SUMMARY_WIDTH + 200)
        # a detail exactly at the width is not cut
        exact = "y" * (behaviour.SUMMARY_WIDTH - len("observed "))
        out = self.lines(report(fail(detail=f"a expected b; observed {exact}")))
        obs = out[1].split("| observed: ", 1)[1].split(" | log: ", 1)[0]
        self.assertEqual(len(obs), behaviour.SUMMARY_WIDTH)
        self.assertFalse(obs.endswith("..."))

    def test_newlines_do_not_break_the_one_line_per_fail(self):
        out = self.lines(report(fail(detail="a expected b;\nobserved c\nd")))
        self.assertEqual(len("\n".join(out).splitlines()), 3)

    def test_not_verifiable_is_counted_not_listed(self):
        rep = report(ok(), nv(), nv(field="criterion", subject="R7.2"))
        out = self.lines(rep)
        self.assertEqual(out, ["1 PASS, 2 NOT_VERIFIABLE", f"exit 0; wall 12.3 s; full log: {LOG}"])

    def test_cannot_tell_is_listed_and_exits_2(self):
        rep = report(ok(), cannot=["R4.9-insert D1: harness error " + "z" * 500], notes=["n1", "n2"])
        out = self.lines(rep)
        self.assertEqual(len(out), 3)
        self.assertTrue(out[1].startswith("cannot tell: R4.9-insert D1: harness error"))
        self.assertEqual(len(out[1]), len("cannot tell: ") + behaviour.SUMMARY_WIDTH)
        self.assertEqual(out[-1], f"exit 2; wall 12.3 s; 2 note(s) in the log; full log: {LOG}")

    def test_no_log(self):
        out = self.lines(report(ok()))
        self.assertNotIn("None", out[-1])
        out = behaviour.summary_lines(report(ok()), 0.0, None)
        self.assertEqual(out[-1], "exit 0; wall 0.0 s; full log: None")


class Splits(unittest.TestCase):
    def test_subject(self):
        self.assertEqual(behaviour.split_subject("R4.9-insert D1"), ("R4.9-insert", "D1"))
        self.assertEqual(behaviour.split_subject("UC-01 (copy) legacy [seek]"), ("UC-01 (copy) [seek]", "legacy"))
        self.assertEqual(behaviour.split_subject("R7.2"), ("R7.2", "-"))

    def test_detail(self):
        self.assertEqual(behaviour.split_detail("requests[0] u at 3: not observed"),
                         ("requests[0] u at 3", "not observed"))
        self.assertEqual(behaviour.split_detail("presentation[1] expected a change at 4 to ad; none observed within 0.5"),
                         ("presentation[1] expected a change at 4 to ad", "none observed within 0.5"))
        self.assertEqual(behaviour.split_detail("presentation[2] primary from expected 30, observed 31"),
                         ("presentation[2] primary from expected 30", "observed 31"))
        self.assertEqual(behaviour.split_detail("unexpected beacon u at 3"), ("(see log)", "unexpected beacon u at 3"))
        self.assertEqual(behaviour.split_detail("presentation: nothing was ever shown on screen"),
                         ("(see log)", "presentation: nothing was ever shown on screen"))


class FullOutput(unittest.TestCase):
    def test_full_lines_is_todays_output(self):
        rep = report(ok(), fail(), nv(), cannot=["c"], notes=["n"])
        full = behaviour.full_lines(rep, 2.0, {"run_seconds": 5, "content_seconds": 1, "ffmpeg_seconds": [1],
                                               "content_cache_hits": 2})
        self.assertEqual(len(full), 6)
        self.assertEqual(full[3], "note: n")
        self.assertEqual(full[4], "cannot tell: c")
        self.assertEqual(full[5], "exit 2: PASS 1  FAIL 1  NOT_VERIFIABLE 1; wall 2.0 s; content 1 s "
                                  "(1 ffmpeg runs, 2 cuts from the cache), players 5 s")

    def test_default_log_dir(self):
        old = os.environ.get("XDG_RUNTIME_DIR")
        os.environ["XDG_RUNTIME_DIR"] = "/run/user/42"
        try:
            a, b = behaviour.default_log_dir(), behaviour.default_log_dir()
        finally:
            if old is None:
                del os.environ["XDG_RUNTIME_DIR"]
            else:
                os.environ["XDG_RUNTIME_DIR"] = old
        self.assertEqual(a.parent, Path("/run/user/42/cto/behaviour-logs"))
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
