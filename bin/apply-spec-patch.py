#!/usr/bin/env python3
"""Apply a patch to the spec's prose, and refuse what a patch may not do
(ADR 0066).

Every edit of `spec-source/sgai-spec.src.md` — a refine, an increment, a
major — is a JSON patch:

  {"ops": [
     {"section": "5.1.3", "find": "<text>", "replace": "<text>", "reason": "<issue id>"},
     {"section": "A.5", "replace_section": "<heading line + body>", "reason": "…"},
     {"insert_after": "5.1.7", "section_text": "<heading line + body>", "reason": "…"},
     {"delete_section": "8.13", "reason": "…"},
     {"file": "examples/annex-c/C.2-1.mpd", "find": "…", "replace": "…", "reason": "…"}
  ]}

A `file` op edits an artefact of spec-source/ (a fixture, the XSD,
syntax.yaml, a scenario), path relative to the directory of --source, with
the same `find`-once rule. Generated files (`syntax/tables/`) and the prose
itself are refused as `file` targets: regenerate the first, patch the
second by section.

Rules, each refused with exit 1 and the op it concerns:
- `find` occurs exactly once in its section;
- no op edits or removes an existing directive line (`{{example:…}}`,
  `{{xsd}}`, `{{include:…}}`): an example or a table is fixed in its source
  file, not in the prose. A new directive line may be added;
- `replace_section` and `section_text` start with a heading line, and keep
  the section's key (replace) or bring a key not in the document (insert);
- every op has a non-empty `reason`;
- two ops do not touch the same section's text in conflicting ways (they are
  applied in order; a later `find` must still be found).
After applying, the sections that changed must be exactly the sections the
patch declares (a scope check by construction: an undeclared change cannot
happen, and a declared one that changed nothing is refused).

Usage:
  bin/apply-spec-patch.py PATCH.json [--source FILE] [--dry-run]
                                     [--max-fraction F] [--record FILE]
  bin/apply-spec-patch.py --reverse RECORD.json [--source FILE] [--dry-run]

--source defaults to spec-source/sgai-spec.src.md. --dry-run applies in
memory and reports. --max-fraction F fails (exit 1, MAJOR) when the changed
sections exceed F of the document's lines. --record copies the patch, with
the sha256 of the source before and after, to FILE (the trace that replaces
inline `<!-- refine -->` annotations). The record also carries what undoing
it needs (`reverse`): the order of the sections before, the text before of
every section it changed, and the content before and the sha256 after of
every file it changed.

--reverse RECORD undoes a recorded patch (the rollback of a refine round
that came out worse). It refuses, writing nothing, unless the prose's
sha256 is the record's `source_sha256_after` and every changed file's is
its recorded sha256 after — so an edit made after the patch is never
silently discarded —, and unless the prose it rebuilds has the record's
`source_sha256_before`. A record written without `reverse` (before this
mode existed) cannot be undone: exit 2. Files the patch did not touch
(generated tables, a file created by hand) are not this mode's business:
regenerate the tables, and check the result with `bin/assemble-spec.py
--check` against the previous candidate.

What a green says: the prose changed exactly where the patch says, nothing
else, and no directive was touched; with --reverse, the prose and the files
are byte for byte what they were before the patch. What it does not say:
that the new text is right.

Exit codes: 0 applied (or undone) · 1 refused (nothing written) · 2
unreadable patch, record or source · 64 wrong command line.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_sections as ss  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(ROOT, "spec-source", "sgai-spec.src.md")


class Refused(Exception):
    pass


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


def directive_lines(text):
    return [l for l in text.splitlines() if ss.DIRECTIVE.match(l.strip())]


def first_heading_key(text, where):
    first = text.splitlines()[0] if text else ""
    m = ss.HEADING.match(first)
    if not m:
        raise Refused(f"{where}: must start with a heading line")
    return ss.key_of(m.group(2))


def apply(text, ops):
    """Return (new_text, declared_keys). Raises Refused."""
    secs = ss.split(text)
    declared = []
    for n, op in enumerate(ops, 1):
        where = f"op {n}"
        if not isinstance(op, dict) or not str(op.get("reason", "")).strip():
            raise Refused(f"{where}: every op needs a reason")
        idx = {s.key: i for i, s in enumerate(secs)}
        if "find" in op or "replace" in op:
            key = op.get("section")
            if key not in idx:
                raise Refused(f"{where}: no section {key!r}")
            body = secs[idx[key]].text
            find, repl = op.get("find"), op.get("replace")
            if not isinstance(find, str) or not isinstance(repl, str) or not find:
                raise Refused(f"{where}: find and replace must be non-empty / strings")
            count = body.count(find)
            if count != 1:
                raise Refused(f"{where}: find occurs {count} times in section {key}, must be once")
            if any(d in find for d in directive_lines(body)):
                raise Refused(f"{where}: edits a directive line in section {key}; fix its source file instead")
            new = body.replace(find, repl, 1)
            parts = ss.split(new)
            if len(parts) != 1 or parts[0].key != key:
                raise Refused(f"{where}: the replacement adds or changes a heading; use replace_section or insert_after")
            secs[idx[key]] = parts[0]
            declared.append(key)
        elif "replace_section" in op:
            key = op.get("section")
            if key not in idx:
                raise Refused(f"{where}: no section {key!r}")
            new = op["replace_section"]
            if not new.endswith("\n"):
                new += "\n"
            if first_heading_key(new, where) != key or len(ss.split(new)) != 1:
                raise Refused(f"{where}: replace_section must be one section keeping key {key}")
            old_d = directive_lines(secs[idx[key]].text)
            if [d for d in old_d if d not in directive_lines(new)]:
                raise Refused(f"{where}: removes a directive line of section {key}")
            secs[idx[key]] = ss.split(new)[0]
            declared.append(key)
        elif "insert_after" in op:
            after = op["insert_after"]
            if after not in idx:
                raise Refused(f"{where}: no section {after!r} to insert after")
            new = op.get("section_text", "")
            if not new.endswith("\n"):
                new += "\n"
            parts = ss.split(new)
            for p in parts:
                if p.key in idx:
                    raise Refused(f"{where}: section {p.key} already exists")
            if not ss.HEADING.match(new.splitlines()[0]):
                raise Refused(f"{where}: section_text must start with a heading line")
            secs[idx[after] + 1:idx[after] + 1] = parts
            declared += [p.key for p in parts]
        elif "delete_section" in op:
            key = op["delete_section"]
            if key not in idx:
                raise Refused(f"{where}: no section {key!r}")
            if directive_lines(secs[idx[key]].text):
                raise Refused(f"{where}: section {key} holds directives; retire their source files in the same change and move them first")
            del secs[idx[key]]
            declared.append(key)
        else:
            raise Refused(f"{where}: unknown op {sorted(op)}")
    return ss.join(secs), declared


GENERATED = ("syntax/tables/",)


def apply_files(srcdir, prose_name, ops):
    """Apply `file` ops in memory. Returns {relpath: (old, new)}. Raises Refused."""
    out = {}
    for n, op in enumerate(ops, 1):
        where = f"file op {n}"
        if not str(op.get("reason", "")).strip():
            raise Refused(f"{where}: every op needs a reason")
        rel = op.get("file", "")
        full = os.path.normpath(os.path.join(srcdir, rel))
        if not rel or os.path.isabs(rel) or not full.startswith(os.path.normpath(srcdir) + os.sep):
            raise Refused(f"{where}: {rel!r} is not a file of spec-source/")
        if rel == prose_name:
            raise Refused(f"{where}: the prose is patched by section, not as a file")
        if rel.startswith(GENERATED):
            raise Refused(f"{where}: {rel} is generated; change its source and regenerate")
        if not os.path.isfile(full):
            raise Refused(f"{where}: {rel} does not exist")
        if rel not in out:
            with open(full, encoding="utf-8", newline="") as fh:
                body = fh.read()
            out[rel] = (body, body)
        find, repl = op.get("find"), op.get("replace")
        if not isinstance(find, str) or not find or not isinstance(repl, str):
            raise Refused(f"{where}: find and replace must be non-empty / strings")
        cur = out[rel][1]
        if cur.count(find) != 1:
            raise Refused(f"{where}: find occurs {cur.count(find)} times in {rel}, must be once")
        out[rel] = (out[rel][0], cur.replace(find, repl, 1))
    return out


def changed_keys(old, new):
    a = {s.key: s.text for s in ss.split(old)}
    b = {s.key: s.text for s in ss.split(new)}
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k)), a, b


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def reverse_data(old, new, changed, srcdir, files):
    """What --reverse needs, kept in the record (only additive to it)."""
    before = {s.key: s.text for s in ss.split(old)}
    return {
        "format": "sgai-patch-reverse/1",
        "order_before": [s.key for s in ss.split(old)],
        "sections_before": {k: before[k] for k in changed if k in before},
        "files_before": {rel: a for rel, (a, _) in sorted(files.items())},
        "files_sha256_after": {rel: sha256(b) for rel, (_, b) in sorted(files.items())},
    }


def reverse(record_path, source, dry):
    try:
        with open(record_path, encoding="utf-8") as fh:
            rec = json.load(fh)
        with open(source, encoding="utf-8", newline="") as fh:
            cur = fh.read()
        rev = rec["reverse"]
        want_after, want_before = rec["source_sha256_after"], rec["source_sha256_before"]
        order, sec_before = rev["order_before"], rev["sections_before"]
        files_before, files_after = rev["files_before"], rev["files_sha256_after"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"exit 2: {record_path} cannot be undone: {e!r}")
        return 2
    srcdir = os.path.dirname(os.path.abspath(source))
    moved = []
    if sha256(cur) != want_after:
        moved.append(os.path.basename(source))
    current_files = {}
    for rel, want in files_after.items():
        full = os.path.join(srcdir, rel)
        try:
            with open(full, encoding="utf-8", newline="") as fh:
                current_files[rel] = fh.read()
        except OSError:
            moved.append(rel + " (missing)")
            continue
        if sha256(current_files[rel]) != want:
            moved.append(rel)
    if moved:
        print(f"REFUSED: the source moved since the patch was applied: {moved}; nothing undone")
        return 1
    try:
        now = ss.by_key(ss.split(cur))
    except ss.SectionError as e:
        print(f"exit 2: {e}")
        return 2
    rebuilt = []
    for k in order:
        if k in sec_before:
            rebuilt.append(sec_before[k])
        elif k in now:
            rebuilt.append(now[k].text)
        else:
            print(f"REFUSED: section {k!r} of the record is neither kept nor recorded; nothing undone")
            return 1
    old = "".join(rebuilt)
    if sha256(old) != want_before:
        print("REFUSED: the rebuilt prose does not have the record's source_sha256_before; nothing undone")
        return 1
    if not dry:
        if old != cur:
            with open(source, "w", encoding="utf-8", newline="") as fh:
                fh.write(old)
        for rel, body in files_before.items():
            with open(os.path.join(srcdir, rel), "w", encoding="utf-8", newline="") as fh:
                fh.write(body)
    print(f"{'would undo' if dry else 'undone'}: {os.path.basename(record_path)}; sections restored "
          f"{sorted(sec_before)}, sections removed {sorted(set(now) - set(order))}; files restored "
          f"{sorted(files_before)}; prose sha256 now {want_before}")
    return 0


def main(argv):
    args = list(argv)
    if "--reverse" in args:
        rest = list(args)
        rest.remove("--reverse")
        source, dry, pos = DEFAULT, False, []
        i = 0
        while i < len(rest):
            if rest[i] == "--source":
                if i + 1 >= len(rest):
                    usage("--source needs a value")
                source = rest[i + 1]
                i += 2
            elif rest[i] == "--dry-run":
                dry = True
                i += 1
            elif rest[i].startswith("--"):
                usage(f"--reverse takes RECORD.json [--source FILE] [--dry-run], not {rest[i]}")
            else:
                pos.append(rest[i])
                i += 1
        if len(pos) != 1:
            usage("--reverse needs one RECORD.json")
        return reverse(pos[0], source, dry)
    opts = {"--source": DEFAULT, "--max-fraction": None, "--record": None}
    dry = False
    pos = []
    i = 0
    while i < len(args):
        a = args[i]
        if a in opts:
            if i + 1 >= len(args):
                usage(f"{a} needs a value")
            opts[a] = args[i + 1]
            i += 2
        elif a == "--dry-run":
            dry = True
            i += 1
        elif a.startswith("--"):
            usage(f"unknown flag {a}")
        else:
            pos.append(a)
            i += 1
    if len(pos) != 1:
        usage("one PATCH.json is required")
    try:
        with open(pos[0], encoding="utf-8") as fh:
            patch = json.load(fh)
        with open(opts["--source"], encoding="utf-8", newline="") as fh:
            old = fh.read()
        ops = patch["ops"]
        if not isinstance(ops, list) or not ops:
            raise ValueError("ops must be a non-empty list")
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"exit 2: {e}")
        return 2
    file_ops = [o for o in ops if isinstance(o, dict) and "file" in o]
    prose_ops = [o for o in ops if not (isinstance(o, dict) and "file" in o)]
    srcdir = os.path.dirname(os.path.abspath(opts["--source"]))
    try:
        new, declared = apply(old, prose_ops) if prose_ops else (old, [])
        files = apply_files(srcdir, os.path.basename(opts["--source"]), file_ops)
    except (Refused, ss.SectionError) as e:
        print(f"REFUSED: {e}")
        return 1
    idle_files = sorted(r for r, (a, b) in files.items() if a == b)
    if idle_files:
        print(f"REFUSED: scope — declared and unchanged: {idle_files}")
        return 1
    changed, a, b = changed_keys(old, new)
    undeclared = sorted(set(changed) - set(declared))
    idle = sorted(set(declared) - set(changed))
    if undeclared or idle:
        print("REFUSED: scope — "
              + (f"changed without being declared: {undeclared}; " if undeclared else "")
              + (f"declared and unchanged: {idle}" if idle else ""))
        return 1
    total = old.count("\n") or 1
    touched = sum(b.get(k, a.get(k, "")).count("\n") for k in changed)
    frac = touched / total
    if opts["--max-fraction"] is not None and frac > float(opts["--max-fraction"]):
        print(f"REFUSED: MAJOR — changed sections are {frac:.1%} of the document, above {float(opts['--max-fraction']):.0%}")
        return 1
    if not dry:
        if new != old:
            with open(opts["--source"], "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
        for rel, (_, body) in files.items():
            with open(os.path.join(srcdir, rel), "w", encoding="utf-8", newline="") as fh:
                fh.write(body)
        if opts["--record"]:
            rec = dict(patch)
            rec["source_sha256_before"] = hashlib.sha256(old.encode()).hexdigest()
            rec["source_sha256_after"] = hashlib.sha256(new.encode()).hexdigest()
            rec["sections_changed"] = changed
            rec["files_changed"] = sorted(files)
            rec["reverse"] = reverse_data(old, new, changed, srcdir, files)
            with open(opts["--record"], "w", encoding="utf-8") as fh:
                json.dump(rec, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
    print(f"{'would apply' if dry else 'applied'}: {len(ops)} op(s); sections changed {changed}; files changed {sorted(files)} "
          f"({frac:.1%} of the document's lines); every change declared")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
