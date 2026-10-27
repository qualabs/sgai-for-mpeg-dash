#!/usr/bin/env python3
"""Tests for check-context-interfaces.py and for the retired-identifier
rule of check-context-coherence.py.

Each test copies context/ to a private temporary directory, breaks one
thing on purpose and runs the check against the copy with --context. A
break that leaves the check green is a failing test.

Run all:   python3 -m unittest bin/test_check_context_interfaces.py
Run one:   python3 -m unittest bin.test_check_context_interfaces.Interfaces.test_row_to_missing_criterion
           (from the project root; or `python3 bin/test_check_context_interfaces.py Interfaces.<name>`)
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
CTX = os.path.join(os.path.dirname(BIN), "context")
INTERFACES = os.path.join(BIN, "check-context-interfaces.py")
COHERENCE = os.path.join(BIN, "check-context-coherence.py")
REQ = "03-requirements.md"
UC = "04-use-cases.md"


def run(script, *args):
    p = subprocess.run([sys.executable, "-I", script, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir=os.environ.get("XDG_RUNTIME_DIR"))
        self.ctx = os.path.join(self.tmp, "context")
        shutil.copytree(CTX, self.ctx)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def edit(self, name, old, new):
        path = os.path.join(self.ctx, name)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        self.assertEqual(text.count(old), 1, f"fixture text not found once in {name}: {old!r}")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text.replace(old, new))

    def interfaces(self):
        return run(INTERFACES, "--context", self.ctx)

    def coherence(self):
        return run(COHERENCE, "--context", self.ctx)


class Interfaces(Base):
    def test_green_on_the_real_context(self):
        code, out = self.interfaces()
        self.assertEqual(code, 0, out)
        self.assertIn("OK: 75 index rows", out)

    def test_row_to_missing_criterion(self):
        self.edit(REQ, "| A document with no candidates | R30.1 |", "| A document with no candidates | R30.99 |")
        code, out = self.interfaces()
        self.assertEqual(code, 1, out)
        self.assertIn("points to R30.99, which is not a criterion", out)

    def test_element_twice_in_one_interface(self):
        self.edit(REQ, "| Custom region | R39.2 |\n", "| Custom region | R39.2 |\n| Custom region | R39.2 |\n")
        code, out = self.interfaces()
        self.assertEqual(code, 1, out)
        self.assertIn("element in two rows: 'Custom region' (I-MPD and I-MPD)", out)

    def test_element_in_two_interfaces(self):
        self.edit(REQ, "| Regulatory disclosure | R48.1 |\n",
                  "| Regulatory disclosure | R48.1 |\n| Ad-audio allowance | R41.3 |\n")
        code, out = self.interfaces()
        self.assertEqual(code, 1, out)
        self.assertIn("element in two rows: 'Ad-audio allowance' (I-MPD and I-RES)", out)

    def test_row_to_a_criterion_its_writer_does_not_hold(self):
        # R5.3 is a Player criterion; I-RES is written by the APS.
        self.edit(REQ, "| Order of the candidates | R7.1 |", "| Order of the candidates | R5.3 |")
        code, out = self.interfaces()
        self.assertEqual(code, 1, out)
        self.assertIn("points to R5.3 (Player), not held by the party that writes I-RES", out)

    def test_a_player_criterion_is_the_writer_of_the_request(self):
        # The reference case of the one above: I-REQ is written by the Player.
        code, out = self.interfaces()
        self.assertEqual(code, 0, out)
        self.assertNotIn("R29.3", out)

    def test_row_with_two_ids(self):
        self.edit(REQ, "| Custom region | R39.2 |", "| Custom region | R39.2, R39.3 |")
        code, out = self.interfaces()
        self.assertEqual(code, 1, out)
        self.assertIn("must point to exactly one criterion id", out)

    def test_retired_id_cited_in_a_use_case(self):
        self.edit(UC, "lacks: not satisfiable, the Player skips to the next option per R5.6.\n",
                  "lacks: not satisfiable, the Player skips to the next option per R5.7.\n")
        code, out = self.interfaces()
        self.assertEqual(code, 1, out)
        self.assertIn("retired R5.7 cited at 04-use-cases.md", out)

    def test_retired_id_cited_in_03_outside_its_row(self):
        self.edit(REQ, "  - **R5.3** (Player): A candidate none", "  - **R5.3** (Player): (R5.7) A candidate none")
        code, out = self.interfaces()
        self.assertEqual(code, 1, out)
        self.assertIn("retired R5.7 cited at 03-requirements.md", out)

    def test_retired_id_defined_again(self):
        self.edit(REQ, "  - **R5.3** (Player): A candidate none",
                  "  - **R5.7** (Player): reused.\n  - **R5.3** (Player): A candidate none")
        code, out = self.interfaces()
        self.assertEqual(code, 1, out)
        self.assertIn("R5.7 is in the retired table and still defined as a criterion", out)

    def test_vanished_id_not_in_the_retired_table(self):
        self.edit(REQ, "| R5.7 | R5.3 |\n", "")
        code, out = self.interfaces()
        self.assertEqual(code, 1, out)
        self.assertIn("R5.7 existed at 44cfff4, is gone, and the retired table does not list it", out)

    def test_no_interfaces_section_cannot_tell(self):
        self.edit(REQ, "## Interfaces\n", "## Interface list\n")
        code, out = self.interfaces()
        self.assertEqual(code, 2, out)
        self.assertIn('no "## Interfaces" section', out)

    def test_no_retired_section_cannot_tell(self):
        self.edit(REQ, "## Retired identifiers\n", "## Former identifiers\n")
        code, out = self.interfaces()
        self.assertEqual(code, 2, out)

    def test_interface_with_no_rows_cannot_tell(self):
        path = os.path.join(self.ctx, REQ)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        head, rest = text.split("### I-REQ", 1)
        table_end = rest.index("### I-RES")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(head + "### I-REQ — empty\n\n" + rest[table_end:])
        code, out = self.interfaces()
        self.assertEqual(code, 2, out)
        self.assertIn("the I-REQ table has no rows", out)

    def test_wrong_command_line(self):
        code, out = run(INTERFACES, "--bogus")
        self.assertEqual(code, 64, out)

    def test_help_states_the_exits(self):
        code, out = run(INTERFACES, "--help")
        self.assertEqual(code, 0, out)
        for line in ("0   nothing found", "1   findings", "2   cannot tell", "64  wrong command line"):
            self.assertIn(line, out)


class CoherenceRetired(Base):
    def test_green_on_the_real_context(self):
        code, out = self.coherence()
        self.assertEqual(code, 0, out)

    def test_retired_row_counts_as_defined(self):
        # Without the row, a citation of R5.7 is a reference to nothing.
        self.edit(REQ, "| R5.7 | R5.3 |\n", "")
        self.edit(UC, "lacks: not satisfiable, the Player skips to the next option per R5.6.\n",
                  "lacks: not satisfiable, the Player skips to the next option per R5.7.\n")
        code, out = self.coherence()
        self.assertEqual(code, 1, out)
        self.assertIn("R5.7 se referencia pero no se define", out)

    def test_retired_id_defined_again_is_defined_twice(self):
        self.edit(REQ, "  - **R5.3** (Player): A candidate none",
                  "  - **R5.7** (Player): reused.\n  - **R5.3** (Player): A candidate none")
        code, out = self.coherence()
        self.assertEqual(code, 1, out)
        self.assertIn("R5.7 esta definido 2 veces", out)


if __name__ == "__main__":
    unittest.main()
