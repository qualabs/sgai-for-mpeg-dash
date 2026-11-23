#!/usr/bin/env python3
"""T-12 mutation campaign: one deliberate break per rule the task's code owns,
running only the tests that cover that rule. A break that stays green is a
finding.

Works on a private mirror of the project ($XDG_RUNTIME_DIR/cto/t12-mut-*):
bin/ copied (without bin/players), everything else symlinked and only read.
Run with lxml and PyYAML importable:
  uv run --with lxml==6.1.3 --with pyyaml==6.0.3 python3 .project/phases/10-code-first-pipeline/tasks/T-12/mutation-campaign.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

REAL = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))

M = [
    # (rule, file, old, new, test module, tests)
    ("reverse: refuses when the prose moved after the patch", "apply-spec-patch.py",
     "if sha256(cur) != want_after:", "if False:",
     "test_apply_spec_patch", ["Reverse.test_edit_after_the_patch_in_a_changed_section_is_refused"]),
    ("reverse: refuses when a changed file moved after the patch", "apply-spec-patch.py",
     "if sha256(current_files[rel]) != want:", "if False:",
     "test_apply_spec_patch", ["Reverse.test_edit_after_the_patch_in_a_changed_file_is_refused"]),
    ("reverse: the rebuilt prose must have sha256 before", "apply-spec-patch.py",
     "if sha256(old) != want_before:", "if False:",
     "test_apply_spec_patch", ["Reverse.test_tampered_record_is_refused"]),
    ("reverse: files are restored", "apply-spec-patch.py",
     "for rel, body in files_before.items():", "for rel, body in {}.items():",
     "test_apply_spec_patch", ["Reverse.test_every_op_kind_comes_back_byte_for_byte"]),
    ("reverse: sections come back in the order before", "apply-spec-patch.py",
     "    for k in order:\n", "    for k in list(now):\n",
     "test_apply_spec_patch", ["Reverse.test_every_op_kind_comes_back_byte_for_byte"]),
    ("reverse: --dry-run writes nothing", "apply-spec-patch.py",
     "    if not dry:\n        if old != cur:", "    if True:\n        if old != cur:",
     "test_apply_spec_patch", ["Reverse.test_dry_run_writes_nothing"]),
    ("reverse: a record without reverse data is exit 2", "apply-spec-patch.py",
     'rev = rec["reverse"]',
     'rev = rec.get("reverse") or {"order_before": [], "sections_before": {}, "files_before": {}, "files_sha256_after": {}}',
     "test_apply_spec_patch", ["Reverse.test_record_without_reverse_data_cannot_tell"]),
    ("version: the v is dropped", "assemble-spec.py",
     "                version = m.group(1)", "                version = v",
     "test_assemble_spec", ["Version.test_version_fills_the_token_without_its_v"]),
    ("version: taken from the file name", "assemble-spec.py",
     "version = m.group(1) if m else None", "version = None",
     "test_assemble_spec", ["Version.test_version_from_the_out_name", "Version.test_check_takes_the_version_from_the_name"]),
    ("version: read from the document, one value at every place", "assemble-spec.py",
     "text = text.replace(TOKEN, found)", "text = doc",
     "test_assemble_spec", ["Version.test_two_places_must_carry_the_same_version"]),
    ("version: read from an unversioned document", "assemble-spec.py",
     "found = version_in(doc, text)", "found = None",
     "test_assemble_spec", ["Version.test_check_reads_the_version_from_an_unversioned_document"]),
    ("version: --out with no version is exit 2", "assemble-spec.py",
     "        if tokens and version is None:\n            print(f\"exit 2", "        if False:\n            print(f\"exit 2",
     "test_assemble_spec", ["Version.test_no_version_anywhere_is_refused_on_out"]),
    ("version: a malformed --version is exit 64", "assemble-spec.py",
     "                if not m:\n                    usage(f\"--version", "                if False:\n                    usage(f\"--version",
     "test_assemble_spec", ["Version.test_bad_version_is_a_command_line_error"]),
    ("version: never replaced inside an included file", "assemble-spec.py",
     "        out.append(body)\n", "        out.append(body.replace(TOKEN, version) if version else body)\n",
     "test_assemble_spec", ["Version.test_token_in_an_included_file_is_not_replaced"]),
    ("scope: a row may name its section by key", "check-incremental.py",
     "return {h, ss.key_of(h)}", "return {h}",
     "test_check_incremental", ["Scope.test_rows_by_key"]),
    ("scope: a recorded section must be declared", "check-incremental.py",
     "if undeclared or phantom or unrecorded:", "if undeclared or phantom:",
     "test_check_incremental", ["Scope.test_recorded_section_must_be_declared"]),
    ("scope: an unreadable record is exit 2", "check-incremental.py",
     "        except (OSError, ValueError, KeyError, TypeError) as exc:\n            raise CannotTell(\"no puedo",
     "        except (OSError, ValueError, KeyError, TypeError) as exc:\n            continue\n            raise CannotTell(\"no puedo",
     "test_check_incremental", ["Scope.test_unreadable_record_cannot_tell"]),
    ("scope: cleanup/version rows do not count toward the cap", "check-incremental.py",
     "return bool(kinds) and kinds <= UNCOUNTED", "return False",
     "test_check_incremental", ["Scope.test_cleanup_does_not_count_toward_the_fraction"]),
    ("scope: a section both cleaned and edited counts", "check-incremental.py",
     "return bool(kinds) and kinds <= UNCOUNTED", "return bool(kinds & UNCOUNTED)",
     "test_check_incremental", ["Scope.test_a_section_both_cleaned_and_edited_counts"]),
    ("scope: a declared row that did not change is rejected", "check-incremental.py",
     "phantom = sorted(set(declared) - hit)", "phantom = []",
     "test_check_incremental", ["Scope.test_cleanup_row_that_did_not_change_is_phantom"]),
    ("scope: deleting the last section leaves the previous one unchanged", "check-incremental.py",
     "for line in text.splitlines(keepends=True):", "for line in (text + \"\\n\").splitlines(keepends=True):",
     "test_check_incremental", ["Scope.test_deleting_the_last_section_leaves_the_one_before_unchanged"]),
    ("anchor: a major's own trace is its anchor", "check-incremental.py",
     "range(int(minor or 0), -1, -1)", "range(int(minor or 0), 0, -1)",
     "test_check_incremental", ["Anchor.test_major_trace_is_its_anchor"]),
    ("strip: a line left empty is dropped whole", "strip-legacy-annotations.py",
     "    if removed and not out.strip():", "    if False:",
     "test_strip_legacy_annotations", ["Unit.test_comment_only_after_a_space_or_before_one", "Unit.test_each_mark_and_only_marks"]),
    ("strip: one adjacent space goes with the comment", "strip-legacy-annotations.py",
     '        if a > 0 and out[a - 1] == " ":', "        if False:",
     "test_strip_legacy_annotations", ["Unit.test_comment_only_after_a_space_or_before_one"]),
    ("strip: fenced code is left", "strip-legacy-annotations.py",
     "        if fence:\n            out.append(line)", "        if False:\n            out.append(line)",
     "test_strip_legacy_annotations", ["Unit.test_each_mark_and_only_marks"]),
    ("strip: inline code is left", "strip-legacy-annotations.py",
     'return line.count("`", 0, pos) % 2 == 1', "return False",
     "test_strip_legacy_annotations", ["Unit.test_each_mark_and_only_marks"]),
    ("strip: only refine/delta comments", "strip-legacy-annotations.py",
     r'LEGACY = re.compile(r"<!--\s*(?:refine|delta)\b.*?-->")', r'LEGACY = re.compile(r"<!--.*?-->")',
     "test_strip_legacy_annotations", ["Unit.test_comment_only_after_a_space_or_before_one", "Unit.test_each_mark_and_only_marks"]),
    ("strip: the Refinement gaps section is deleted", "strip-legacy-annotations.py",
     'if "refinement gaps" in sec.heading.lower():', "if False:",
     "test_strip_legacy_annotations", ["Unit.test_each_mark_and_only_marks"]),
    ("strip: a gaps section holding a directive is exit 2", "strip-legacy-annotations.py",
     'raise ValueError(f"section {sec.key!r} holds a directive")', "pass",
     "test_strip_legacy_annotations", ["Unit.test_gaps_with_directive_cannot_tell"]),
    ("strip: the status line gets {{version}}", "strip-legacy-annotations.py",
     'if m and "{{version}}" not in new:', "if False:",
     "test_strip_legacy_annotations", ["Unit.test_status_with_v_prefix", "Unit.test_each_mark_and_only_marks"]),
    ("strip: a v-prefixed iteration is matched", "strip-legacy-annotations.py",
     r"build iteration )v?\d+", r"build iteration )\d+",
     "test_strip_legacy_annotations", ["Unit.test_status_with_v_prefix"]),
    ("strip: nothing found is exit 0 and no file", "strip-legacy-annotations.py",
     "    if not ops:\n", "    if ops is None:\n",
     "test_strip_legacy_annotations", ["Unit.test_idempotent"]),
    ("strip: a redundant override is dropped, not stripped", "strip-legacy-annotations.py",
     "        if where_in_yaml(lines, i) in drop:", "        if False:",
     "test_strip_legacy_annotations", ["OnTheSource.test_redundant_override_is_dropped_not_stripped"]),
]


def main():
    base = os.environ.get("XDG_RUNTIME_DIR")
    base = os.path.join(base, "cto") if base else None
    if base:
        os.makedirs(base, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="t12-mut-", dir=base)
    try:
        proj = os.path.join(tmp, "proj")
        os.makedirs(proj)
        for name in os.listdir(REAL):
            if name == "bin":
                continue
            os.symlink(os.path.join(REAL, name), os.path.join(proj, name))
        shutil.copytree(os.path.join(REAL, "bin"), os.path.join(proj, "bin"),
                        ignore=shutil.ignore_patterns("players", "__pycache__"))
        stayed = 0
        for rule, f, old, new, mod, tests in M:
            path = os.path.join(proj, "bin", f)
            with open(path) as fh:
                pristine = fh.read()
            n = pristine.count(old)
            if n != 1:
                print(f"BAD MUTATION ({n} matches): {rule}")
                stayed += 1
                continue
            with open(path, "w") as fh:
                fh.write(pristine.replace(old, new))
            p = subprocess.run([sys.executable, "-W", "ignore", "-m", "unittest", *[f"{mod}.{t}" for t in tests]],
                               cwd=os.path.join(proj, "bin"), capture_output=True, text=True)
            with open(path, "w") as fh:
                fh.write(pristine)
            caught = p.returncode != 0
            stayed += not caught
            last = [l for l in p.stderr.splitlines() if l.startswith(("FAILED", "OK"))]
            print(f"{'CAUGHT' if caught else 'STAYED GREEN'}\t{rule}\t{f}\t{', '.join(tests)}\t{last[-1] if last else ''}")
        # And the pristine copy is green on the same tests.
        mods = sorted({m[4] for m in M})
        p = subprocess.run([sys.executable, "-W", "ignore", "-m", "unittest", *mods],
                           cwd=os.path.join(proj, "bin"), capture_output=True, text=True)
        print(f"pristine: {p.stderr.strip().splitlines()[-1]}")
        print(f"{len(M)} mutations, {len(M) - stayed} caught, {stayed} stayed green")
        return 1 if stayed else 0
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    sys.exit(main())
