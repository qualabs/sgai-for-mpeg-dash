#!/usr/bin/env python3
"""check-promotable: a detail-review flag routed to 5.a blocks. Its id is a
number (`flag 3`), which the finding-id pattern does not match; before the
FLAG pattern a flag routed to 5.a never blocked.
Run: python3 bin/test_check_promotable_flags.py
"""
import importlib.util
import os
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cp", os.path.join(BIN, "check-promotable.py"))
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

SIDE = """## Disposition of findings

### 5.a Actionable TODOs (1)

| # | Finding ref | Edit |
|---|---|---|
| T1 | flag 3 | rename X |

### 5.b Flagged for review (1)

| # | Finding ref | Why |
|---|---|---|
| f-1 | flag-4, A-2 | needs a person |
"""


class Flags(unittest.TestCase):
    def test_flag_ids_are_routed(self):
        d = cp.dispositions(SIDE)
        self.assertEqual(d.get("flag 3"), "5.a")
        self.assertEqual(d.get("flag 4"), "5.b")
        self.assertEqual(d.get("A-2"), "5.b")
        self.assertIn(d.get("flag 3"), cp.KNOWN_FIX)


if __name__ == "__main__":
    unittest.main()
