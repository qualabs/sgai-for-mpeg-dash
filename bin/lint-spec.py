#!/usr/bin/env python3
"""Is an assembled spec document editorially clean?

Usage:
  bin/lint-spec.py <document.md> [--json]

<document.md> is an assembled spec (dist/sgai-spec.md, or a candidate
output/v<N>-sgai-spec.md). Every finding is printed with its rule id, its
line and the offending text; --json prints the same as one JSON object.

Rules:
  L-REF      A bare `§n`, `§n.m…` or `§A.n` (one not prefixed by another
             standard) names a heading of this document. The prefix is the
             word right before the `§`, which may sit at the end of the
             previous line because the document wraps ("(DASH\\n§5.10.2.1)").
             Prefixes: DASH, ISO, IEC, IAB, SCTE, RFC, CTA, SVTA, ETSI, HLS,
             W3C, VAST, VMAP, CMAF, and a bare standard number (23009,
             23009-1, 2053, 8216 …). "DASH §5.16.3–DASH §5.16.5" carries the
             prefix on both ends. Resolution is EXACT: a reference resolves
             only to a heading with that very number. A reference deeper than
             any heading (`§5.1.3.2` when the deepest heading under 5.1.3 is
             5.1.3) does NOT resolve: the reader has nowhere to land, and
             accepting the parent would let a typo of any depth pass.
  L-ID       PUB-n, PLY-n, APS-n, DOC-n, ADS-n are each defined once (a list
             item opening `- **PUB-14.**`) and every mention anywhere in the
             document, code included, names a defined id.
  L-NS       In every ```xml block, every element or attribute name prefix is
             declared by an xmlns:<prefix> in that same block. `xml` (bound by
             the Namespaces in XML recommendation) and `xmlns` (reserved) are
             the only exceptions; `xs` gets none — the schema block declares
             it like any other prefix. XML comments are ignored.
  L-DRAFT    No TODO, TBD, FIXME or XXX as uppercase words, anywhere: prose,
             inline code and code blocks alike, because a TODO in an example
             is as unfinished as one in prose.
  L-COMMENT  No HTML comment `<!-- … -->` outside code. An unterminated
             `<!--` is a finding too. Comments inside fenced code blocks and
             inline code spans are content of the code (an XML comment in an
             example), not HTML comments, and are not flagged.
  L-GAPS     No heading containing "Refinement gaps", at any level.

Exits:
  0   clean: every rule ran and found nothing.
  1   findings.
  2   cannot tell: file unreadable or not UTF-8, not a spec (no `## 1.`
      heading), or a code fence left open (the rules would read the rest
      of the document as code and find nothing there).
  64  wrong command line.

What a green covers: the six rules above, as written, on this one file.
What it does NOT cover: whether a reference points to the RIGHT section,
whether a prefixed reference (`DASH §n`) exists in the other standard,
whether an id is used where it should be, QName values in attributes
(`type="xs:string"`, `base="svta:…"`) — only element and attribute
names are checked —, namespace URIs, XML well-formedness, comments
inside code, and anything about the content of the spec.
"""
import json
import re
import sys

EXIT_OK, EXIT_FINDINGS, EXIT_UNKNOWN, EXIT_USAGE = 0, 1, 2, 64

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)\.?\s")
ANNEX = re.compile(r"^Annex\s+([A-Z])\b")
LETTERED = re.compile(r"^([A-Z](?:\.\d+)+)\.?\s")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")
REF = re.compile(r"§((?:\d+|[A-Z])(?:\.\d+)*)")
PREFIX_WORDS = {"DASH", "ISO", "IEC", "ISO/IEC", "IAB", "SCTE", "RFC", "CTA",
                "SVTA", "ETSI", "HLS", "W3C", "VAST", "VMAP", "CMAF"}
STD_NUMBER = re.compile(r"^\d{3,5}(?:-\d+)*(?::\d{4})?$")
ID = re.compile(r"\b((?:PUB|PLY|APS|DOC|ADS)-\d+)\b")
ID_DEF = re.compile(r"^\s*[-*]\s+\*\*((?:PUB|PLY|APS|DOC|ADS)-\d+)\.?\*\*")
DRAFT = re.compile(r"\b(TODO|TBD|FIXME|XXX)\b")
COMMENT = re.compile(r"<!--.*?-->", re.S)
XML_COMMENT = re.compile(r"<!--.*?-->", re.S)
XML_TAG = re.compile(r"<(/?)([A-Za-z_][\w.-]*(?::[A-Za-z_][\w.-]*)?)((?:[^<>\"']|\"[^\"]*\"|'[^']*')*)>")
XML_ATTR = re.compile(r"([A-Za-z_][\w.-]*(?::[A-Za-z_][\w.-]*)?)\s*=")
NS_EXEMPT = {"xml", "xmlns"}


class CannotTell(Exception):
    pass


def finding(rule, line, text):
    return {"rule": rule, "line": line, "text": text}


def split_code(lines):
    """Return (blocks, prose) where blocks is [(lang, start_line, [lines])]
    and prose is the document with fenced code lines blanked."""
    blocks, prose = [], []
    open_fence = None
    for no, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if open_fence is None:
            if m:
                open_fence = (m.group(1), m.group(2).strip(), no, [])
                prose.append("")
            else:
                prose.append(line)
        else:
            fence = open_fence[0]
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not m.group(2).strip():
                blocks.append((open_fence[1], open_fence[2], open_fence[3]))
                open_fence = None
            else:
                open_fence[3].append(line)
            prose.append("")
    if open_fence is not None:
        raise CannotTell(f"code fence opened at line {open_fence[2]} is never closed")
    return blocks, prose


def mask_inline_code(text):
    """Blank inline code spans (they may wrap lines, never paragraphs),
    keeping every newline so line numbers survive."""
    out, i, n = [], 0, len(text)
    while i < n:
        if text[i] == "`":
            j = i
            while j < n and text[j] == "`":
                j += 1
            ticks = text[i:j]
            k = text.find(ticks, j)
            while k != -1 and (k + len(ticks) < n and text[k + len(ticks)] == "`"):
                k = text.find(ticks, k + len(ticks) + 1)
            if k != -1 and "\n\n" not in text[j:k]:
                end = k + len(ticks)
                out.append(re.sub(r"[^\n]", " ", text[i:end]))
                i = end
                continue
            out.append(ticks)
            i = j
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def headings(prose):
    found = []
    for no, line in enumerate(prose, 1):
        m = HEADING.match(line)
        if m:
            found.append((no, len(m.group(1)), m.group(2)))
    return found


def section_numbers(heads):
    nums = set()
    for _, _, title in heads:
        for pat in (NUMBERED, ANNEX, LETTERED):
            m = pat.match(title + " ")
            if m:
                nums.add(m.group(1))
                break
    return nums


def is_prefix(word):
    word = word.strip("([{*_\"'")
    if "–" in word or "—" in word:
        word = re.split(r"[–—]", word)[-1]
    return word in PREFIX_WORDS or bool(STD_NUMBER.match(word))


def rule_ref(masked, nums):
    out = []
    for m in REF.finditer(masked):
        before = masked[:m.start()]
        tail = before.rsplit("\n", 1)[-1]
        if not tail.strip():
            # Nothing before the § on its line: the prefix, if any, ends the
            # previous line.
            head = before[:len(before) - len(tail)].rstrip("\n")
            tail = head.rsplit("\n", 1)[-1] if head else ""
        words = tail.split()
        if words and is_prefix(words[-1]):
            continue
        if m.group(1) not in nums:
            out.append(finding("L-REF", line_of(masked, m.start()),
                               f"§{m.group(1)} names no heading of this document"))
    return out


def rule_id(lines):
    out, defined = [], {}
    for no, line in enumerate(lines, 1):
        m = ID_DEF.match(line)
        if m:
            defined.setdefault(m.group(1), []).append(no)
    for ident, where in sorted(defined.items()):
        for no in where[1:]:
            out.append(finding("L-ID", no, f"{ident} defined again (first at line {where[0]})"))
    for no, line in enumerate(lines, 1):
        for m in ID.finditer(line):
            if m.group(1) not in defined:
                out.append(finding("L-ID", no, f"{m.group(1)} is referenced and never defined"))
    return out, len(defined)


def rule_ns(blocks):
    out, count = [], 0
    for lang, start, body in blocks:
        if lang.split()[0:1] != ["xml"]:
            continue
        count += 1
        text = "\n".join(body)
        clean = XML_COMMENT.sub(lambda c: re.sub(r"[^\n]", " ", c.group(0)), text)
        declared = set(re.findall(r"\bxmlns:([A-Za-z_][\w.-]*)\s*=", clean))
        seen = set()
        for t in XML_TAG.finditer(clean):
            names = [t.group(2)] + XML_ATTR.findall(t.group(3))
            for name in names:
                if ":" not in name:
                    continue
                prefix = name.split(":", 1)[0]
                if prefix in NS_EXEMPT or prefix in declared or prefix in seen:
                    continue
                seen.add(prefix)
                no = start + line_of(clean, t.start())
                out.append(finding("L-NS", no,
                                   f"prefix '{prefix}' ({name}) not declared in the xml block opened at line {start}"))
    return out, count


def rule_draft(lines):
    out = []
    for no, line in enumerate(lines, 1):
        for m in DRAFT.finditer(line):
            out.append(finding("L-DRAFT", no, line.strip()[:120]))
    return out


def rule_comment(masked):
    out = []
    for m in COMMENT.finditer(masked):
        out.append(finding("L-COMMENT", line_of(masked, m.start()),
                           " ".join(m.group(0).split())[:120]))
    stripped = COMMENT.sub(lambda c: " " * len(c.group(0)), masked)
    pos = stripped.find("<!--")
    if pos != -1:
        out.append(finding("L-COMMENT", line_of(masked, pos), "unterminated <!--"))
    return out


def rule_gaps(heads):
    return [finding("L-GAPS", no, "#" * lvl + " " + title)
            for no, lvl, title in heads if "refinement gaps" in title.lower()]


def lint(text):
    lines = text.split("\n")
    blocks, prose = split_code(lines)
    heads = headings(prose)
    if not any(lvl == 2 and NUMBERED.match(t + " ") and NUMBERED.match(t + " ").group(1) == "1"
               for _, lvl, t in heads):
        raise CannotTell("no `## 1.` heading: not an assembled spec")
    masked = mask_inline_code("\n".join(prose))
    nums = section_numbers(heads)
    ids, n_ids = rule_id(lines)
    ns, n_xml = rule_ns(blocks)
    findings = (rule_ref(masked, nums) + ids + ns + rule_draft(lines)
                + rule_comment(masked) + rule_gaps(heads))
    findings.sort(key=lambda f: (f["line"], f["rule"]))
    stats = {"headings_numbered": len(nums), "ids_defined": n_ids,
             "xml_blocks": n_xml, "code_blocks": len(blocks)}
    return findings, stats


def main(argv):
    args = argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        return EXIT_OK
    as_json = "--json" in args
    rest = [a for a in args if a != "--json"]
    if len(rest) != 1 or rest[0].startswith("-"):
        print("usage: bin/lint-spec.py <document.md> [--json]", file=sys.stderr)
        return EXIT_USAGE
    path = rest[0]
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        findings, stats = lint(text)
    except (OSError, UnicodeDecodeError, CannotTell) as exc:
        if as_json:
            print(json.dumps({"document": path, "verdict": "CANNOT TELL", "reason": str(exc)}))
        else:
            print(f"CANNOT TELL: {path}: {exc}")
        return EXIT_UNKNOWN
    verdict = "FINDINGS" if findings else "CLEAN"
    if as_json:
        counts = {}
        for f in findings:
            counts[f["rule"]] = counts.get(f["rule"], 0) + 1
        print(json.dumps({"document": path, "verdict": verdict, "counts": counts,
                          "stats": stats, "findings": findings}, indent=2, ensure_ascii=False))
    else:
        for f in findings:
            print(f"{f['rule']}\t{f['line']}\t{f['text']}")
        by = {}
        for f in findings:
            by[f["rule"]] = by.get(f["rule"], 0) + 1
        summary = ", ".join(f"{k} {v}" for k, v in sorted(by.items())) or "none"
        print(f"{verdict}: {path}: {len(findings)} finding(s) ({summary}); "
              f"{stats['headings_numbered']} numbered headings, {stats['ids_defined']} ids, "
              f"{stats['xml_blocks']} xml blocks. A green covers the six rules only; see --help.")
    return EXIT_FINDINGS if findings else EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))
