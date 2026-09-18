#!/usr/bin/env python3
"""Step 0.6 of the build: does `context/` hold its own vocabulary and its
own normative force?

Its brother `check-context-coherence.py` answers the structural axis —
identifiers defined, nothing defined twice, links resolving — and on
today's `context/` it finds nothing, because the identifiers do line up.
This one asks the other question over the same files: are the words and
the modals doing what the requirements say they must.

WHAT THIS CATCHES:

  * a value used as a member of a closed vocabulary that the requirement
    declaring that vocabulary never enumerates;
  * an enumerated item with no token to write it with, in a requirement
    that says the accepted values are exactly the enumerated ones;
  * a mention of a term that a requirement confines to illustrative
    material, sitting outside any material marked as illustrative;
  * an RFC 2119 modal in a construction where it cannot bind anyone
    ("Neither ... MUST", "MUST be required");
  * a file that declares itself normative and carries no obligation;
  * a multi-word term used at least TERM_FREQUENCY_THRESHOLD times
    with no glossary entry;
  * an open question stated in the text and absent from the register of
    questions the specification declares deliberately open.

Every rule above is read off `context/` itself: the closed vocabulary is
whatever a requirement enumerates, the confined term is whatever a
requirement confines, the register is whatever the register holds. There
is no list in this file of what today's `context/` happens to say, and a
green means nothing was found rather than that everything was excused.

WHAT THIS DOES NOT CATCH, and the distinction matters more than the
check does:

  * a term defined in the glossary whose definition says the wrong
    thing, or defines one word with two meanings;
  * a vocabulary value that is enumerated and still wrong for the place
    it is used;
  * an obligation whose modal is well formed and lands on an actor this
    specification does not govern;
  * a requirement that contradicts another requirement, which is the
    class that costs the most and has no syntactic signature at all;
  * a term used below the frequency threshold, or in one word — the
    threshold is a guess about attention, not a measurement of
    importance, and single words carry too much ordinary English to
    separate the technical ones mechanically;
  * an open question phrased in words the marker list does not contain;
  * a value of a closed vocabulary named in running prose rather than in
    a list of values. Only a list is inspected, because a paragraph that
    mentions layouts and is mined for nouns reports every word in it,
    and a check that reports everything is read as reporting nothing;
  * a chapter that carries the confined term and gets marked
    "illustrative" without a word of it changing. The check trusts the
    marking, which is what makes it mechanical: whether the material
    really is illustrative is a judgement, and it is the one the
    requirement asks a person to make.

Two checks the blind audit asked for are deliberately absent, because
neither could be made to fire only on real defects: counting `MUST NOT`
against the design principle that says the specification does not
enumerate prohibitions (the count is true and says nothing about whether
any one of them is wrong), and identifier ranges gone stale ("R1-R10"
where R34 exists), which needs to tell a range of identifiers from a
version number, a clause number and a year.

A green here means the vocabulary closes and the modals are well formed.
It does not mean `context/` is correct.

Usage:  bin/check-context-vocabulary.py [--quiet] [--dir DIR] [--help]
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTX = os.path.join(ROOT, "context")

# ---------------------------------------------------------------- constants
# Everything this check is tuned by lives here, named, rather than inside
# the code that uses it.

# A term must appear at least this many times before its absence from the
# glossary is reported. The number is a judgement about attention, not a
# measurement: below it the report fills with ordinary noun phrases and
# stops being read, which is the failure mode that makes a check useless.
# At 40, on the context/ this was written against, it reports four terms,
# two of which a human auditor had found by hand.
TERM_FREQUENCY_THRESHOLD = 40

# A term is only a candidate if it is at least this many words long. One
# word is almost always ordinary English here ("ad", "document", "slot")
# and separating the technical ones needs judgement this check does not
# have.
TERM_MIN_WORDS = 2
TERM_MAX_WORDS = 3

# A file that declares itself normative carries at least this many
# obligation-bearing modals. MAY does not count: it grants permission,
# and a document made only of permissions obliges no one.
MIN_OBLIGATIONS_IN_NORMATIVE_FILE = 1

# How a requirement says "this enumeration is the whole vocabulary".
CLOSED_SET_DECLARATION = re.compile(
    r"are exactly (?:those|the values) enumerated"
    r"|MUST NOT accept a value outside the enumeration"
    r"|MUST use names drawn from the enumerated set", re.I)

# How a requirement confines a term to illustrative material. The term it
# names is the one this check then hunts for; group 1 is that term.
#
# Two formulations, because a requirement can confine a term in two ways
# and the difference is what the requirement means, not how it is phrased:
# the strict one bars every mention outside illustrative material, and the
# permissive one bars DEPENDING on the term while letting a normative
# sentence name it as the typical case. Which one a requirement uses is
# read off its own text.
CONFINED_TERM_DECLARATION = re.compile(
    r"[Aa]ny reference to ([A-Z][A-Za-z0-9.+-]*)\b[^.]{0,240}?"
    r"MUST be in an annex or in a non-normative note")

CONFINED_TERM_UNLESS_UNBOUND = re.compile(
    # The span between the two halves crosses a sentence boundary, so it
    # cannot be written as "anything but a full stop" the way the strict
    # formulation's is.
    r"MUST NOT require ([A-Z][A-Za-z0-9.+-]*)\b[\s\S]{0,400}?"
    r"[Nn]aming \1 as the typical case is permitted where the same "
    r"sentence states that the actor is not bound to it")

# What, inside the SAME sentence, releases a mention under the permissive
# formulation: the sentence itself saying the actor is not tied to the term.
# Anything vaguer would let "typically VAST" stand alone, which is the
# phrasing every binding mention already used before it was rewritten.
NOT_BOUND_CLAUSE = re.compile(
    r"\bnot bound to\b|\bor otherwise\b|\bor any other\b"
    r"|\bMAY emit another\b|\b[A-Za-z]+-agnostic\b"
    r"|\bregardless of whether\b|\bopaque to this spec\b", re.I)

# How a FILE declares that all of it is illustrative. Narrower than the
# generic mark below on purpose: the subject has to be the document, so a
# passing mention of an annex does not silence a whole file.
SELF_DECLARED_ILLUSTRATIVE = re.compile(
    r"\bthis (?:document|clause|chapter|file|annex) is\b[^.]{0,40}?"
    r"\b(?:illustrative|informative|non-normative)\b", re.I)

# What marks material as illustrative, so a confined term may live in it.
ILLUSTRATIVE_MARK = re.compile(
    r"\b(?:illustrative|non-normative|informative|annex)\b", re.I)

# Where a closed vocabulary gets used: the phrases that introduce a set of
# values drawn from it. A sentence without one of these is not declaring
# a set and is not inspected.
VOCABULARY_ANCHOR = re.compile(
    r"allowed[ -]layouts?\b|layout set\b|allowedLayouts\b", re.I)

# Inside such a sentence, where the list of values starts.
LIST_OPENER = re.compile(
    r"\be\.g\.|\bfor example\b|\bsuch as\b|\bincludes?\b|\bincluding\b"
    r"|\brestricted to\b|\bnamely\b|—")

# The openers above that promise the values themselves rather than a
# clause about them. After one of these, a single item is still a list.
EXEMPLIFIER = re.compile(
    r"\be\.g\.|\bfor example\b|\bsuch as\b|\bincludes?\b|\bincluding\b"
    r"|\bnamely\b")

# What separates one value from the next inside that list.
LIST_SEPARATOR = re.compile(r",|;|\band\b|\bor\b")

# A list of values is short and made of short items. Prose that happens to
# contain one of the openers above is not a list, and these two numbers
# are what tells them apart: without them the check reports every noun in
# every paragraph that mentions layouts, which is a report nobody reads.
MAX_LIST_REGION_CHARS = 100
MAX_ITEM_WORDS = 4

# Constructions where an RFC 2119 modal cannot bind anyone.
MALFORMED_MODAL = [
    (re.compile(r"\bNeither\b[^.]{0,160}?\b(?:MUST|SHALL|SHOULD)\b"),
     "un modal bajo 'Neither' no obliga a nadie: la negacion se escribe "
     "sin el modal, o como obligacion sobre el documento"),
    (re.compile(r"\bMUST be (?:required|expected|assumed)\b"),
     "'MUST be required/expected' no es una construccion de RFC 2119: "
     "se lee como prohibicion sobre quien requiere o espera, que no es "
     "un actor"),
]

# How a file says its own content is normative.
NORMATIVE_SELF_DECLARATION = re.compile(
    r"\b(?:is|are|remains?) normative\b"
    r"|\bthis document is (?:the )?(?:canonical|normative)\b", re.I)

OBLIGATION_MODAL = re.compile(
    r"\bMUST\b|\bSHALL\b|\bSHOULD\b|\bREQUIRED\b|\bRECOMMENDED\b")

# How the text says a question is still open.
OPEN_QUESTION_MARKER = re.compile(
    r"\bis an open\b|\bopen question\b|\bopen design decision\b"
    r"|\bmust pick one\b|\bis provisional\b|\bThis position is provisional\b"
    r"|\bremains? open\b|\bleft open\b|\bnot settled\b|\bundecided\b"
    r"|\bTBD\b|\bTODO\b|\bFIXME\b")

# The register those questions must reach.
OPEN_REGISTER_HEADING = re.compile(r"^#+\s+Deliberately open\b", re.M)

# Ordinary English that carries no vocabulary. It exists because the
# lexicons this check compares against are harvested from context/ and a
# harvest never contains every function word; it is not a list of
# exceptions for any particular context/.
STOPWORDS = set("""
a an the this that these those and or but not no nor of in on at to for from
by with without as is are was were be been being it its they them their there
here which who whom whose what when where how why if then than so such each
every any all both some one two three other another same own more most less
least much many few several very can could may might must shall should will
would do does did done have has had having into over under between within
during before after above below up down out off again further once only just
also even still yet per via across through about against among upon while
because until unless otherwise rather instead however therefore thus hence
etc vs possibly typically optionally always never often sometimes usually
likely merely simply purely already still per-device
""".split())


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def collapse(text):
    return re.sub(r"\s+", " ", text).strip()


def words_of(text):
    """Lowercased word-ish tokens. A hyphenated compound stays whole:
    `side-by-side` is one value of a layout vocabulary, not three."""
    return [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9-]*", text)]


def list_values(region, exemplified):
    """The words offered as values by a stretch of text, or nothing if
    that stretch is not a list of values.

    A list of values is short and made only of values; a paragraph that
    happens to contain "including" is neither, and one long item is
    enough to say the stretch is a clause about the values rather than
    the values. A dash inside the stretch ends it for the same reason:
    what follows a dash is commentary on the list.

    Two values are needed before a stretch counts as a list, unless the
    opener promised examples outright, where one is a list of one.
    """
    region = region.split("—")[0]
    if len(region) > MAX_LIST_REGION_CHARS:
        return []
    items = [i.strip() for i in LIST_SEPARATOR.split(region)]
    items = [i for i in items if words_of(i)]
    if not items or (len(items) < 2 and not exemplified):
        return []
    if any(len(words_of(i)) > MAX_ITEM_WORDS for i in items):
        return []
    values = []
    for item in items:
        values.extend(words_of(item))
    return values


# ------------------------------------------------------------------ parsing

class Context(object):
    """`context/` as this check needs to see it."""

    def __init__(self, directory):
        self.dir = directory
        self.files = sorted(glob.glob(os.path.join(directory, "*.md")))
        self.text = {f: read(f) for f in self.files}
        self.lines = {f: self.text[f].split("\n") for f in self.files}
        self.blocks = self._requirement_blocks()

    def name(self, path):
        return os.path.basename(path)

    def _requirement_blocks(self):
        """Every top-level requirement bullet, with the lines it owns.

        Found positionally, the way the coherence check finds definitions:
        a requirement opens with `- **RNN.` at column zero and owns
        everything up to the next one or the next heading.
        """
        blocks = {}
        opener = re.compile(r"^- \*\*(R\d+)\.")
        for path in self.files:
            current = None
            for n, line in enumerate(self.lines[path]):
                m = opener.match(line)
                if m:
                    current = m.group(1)
                    blocks[current] = {"file": path, "start": n, "end": n}
                    continue
                if current is None:
                    continue
                if opener.match(line) or line.startswith("#"):
                    current = None
                    continue
                blocks[current]["end"] = n
        for ident, b in blocks.items():
            b["lines"] = self.lines[b["file"]][b["start"]:b["end"] + 1]
            b["text"] = "\n".join(b["lines"])
        return blocks

    def units(self, path):
        """The file split into units of prose: a list item with its
        continuation lines, or a paragraph. Returns (first_line_no, text)."""
        out = []
        buf = []
        first = 0
        bullet = re.compile(r"^\s*[-*] ")
        for n, line in enumerate(self.lines[path]):
            if not line.strip():
                if buf:
                    out.append((first, "\n".join(buf)))
                    buf = []
                continue
            if bullet.match(line) and buf:
                out.append((first, "\n".join(buf)))
                buf = []
            if not buf:
                first = n
            buf.append(line)
        if buf:
            out.append((first, "\n".join(buf)))
        return out

    def marked_illustrative(self, path):
        """Line numbers that sit in material flagged as illustrative:
        the whole file when it declares itself so, or under a heading
        that says so, or in a paragraph that says so.

        The whole-file case is the one a document actually uses. A file
        whose opening declares that it is informative has declared it
        about itself, not about its first section — and a mark that
        stopped at the next heading would report the other 500 lines of
        a document nobody claims is normative. What counts as the
        opening is the text before the first subheading, which is where
        a document says what it is.
        """
        marked = set()
        lines = self.lines[path]
        if self._declares_itself_illustrative(lines):
            return set(range(len(lines)))
        section_ok = False
        for n, line in enumerate(lines):
            if line.startswith("#"):
                section_ok = bool(ILLUSTRATIVE_MARK.search(line))
            if section_ok:
                marked.add(n)
        # paragraph level
        para = []
        for n, line in enumerate(lines + [""]):
            if line.strip():
                para.append((n, line))
                continue
            if para:
                body = " ".join(l for _, l in para)
                if ILLUSTRATIVE_MARK.search(body):
                    marked.update(i for i, _ in para)
                para = []
        return marked

    @staticmethod
    def _declares_itself_illustrative(lines):
        """Does the file's opening say the FILE is illustrative?

        Only the text above the first subheading counts, and only a
        sentence whose subject is the document. "This document is
        informative" declares it; a paragraph that merely mentions an
        annex does not, which is why the generic mark is not enough here.
        """
        opening = []
        for line in lines:
            if line.startswith("##"):
                break
            opening.append(line)
        text = " ".join(opening)
        return bool(SELF_DECLARED_ILLUSTRATIVE.search(text))


# ------------------------------------------------------------------- checks

def check_closed_vocabulary(ctx, finding, cannot_tell):
    """A value used as a member of a closed vocabulary that the
    requirement declaring that vocabulary never names.

    The lexicon is every word the declaring requirement uses. That is the
    point: a word the requirement never writes cannot be a value it
    enumerated, and building the lexicon this way means the check has no
    opinion of its own about which words are allowed.
    """
    owner = None
    for ident in sorted(ctx.blocks):
        if CLOSED_SET_DECLARATION.search(collapse(ctx.blocks[ident]["text"])):
            owner = ident
            break
    if owner is None:
        cannot_tell.append(
            "ningun requerimiento declara un vocabulario cerrado con las "
            "formulas que conozco, asi que no busque usos fuera de la "
            "enumeracion. Cero hallazgos aca no dice nada.")
        return
    block = ctx.blocks[owner]
    lexicon = set(words_of(block["text"]))

    for path in ctx.files:
        for first, unit in ctx.units(path):
            if path == block["file"] and block["start"] <= first <= block["end"]:
                continue
            flat = collapse(unit)
            anchor = VOCABULARY_ANCHOR.search(flat)
            if not anchor:
                continue
            # Every opener after the anchor opens a candidate list, and
            # each is judged on its own: a sentence can introduce its
            # values twice ("restricted to a subset ... (e.g. ...)") and
            # only the inner one is the list.
            values = set()
            for opener in LIST_OPENER.finditer(flat, anchor.end()):
                region = flat[opener.end():]
                cut = re.search(r"\.\s+[A-Z]", region)
                if cut:
                    region = region[:cut.start()]
                values.update(list_values(
                    region, bool(EXEMPLIFIER.match(opener.group(0)))))
            for w in sorted(values):
                if len(w) >= 3 and w not in lexicon and w not in STOPWORDS:
                    finding("vocabulario-cerrado",
                            "`%s` se usa como valor de layout y %s no lo "
                            "enumera" % (w, owner),
                            "%s:%d" % (ctx.name(path), first + 1))


def check_enumeration_tokens(ctx, finding, cannot_tell):
    """A requirement that says the accepted values are exactly the
    enumerated ones, and an enumerated item with no token to write it
    with. Each item names the external definition it maps to; the ones
    that carry no token cannot be written into a document."""
    owner = None
    for ident in sorted(ctx.blocks):
        if CLOSED_SET_DECLARATION.search(collapse(ctx.blocks[ident]["text"])):
            owner = ident
            break
    if owner is None:
        return  # already reported by check_closed_vocabulary
    block = ctx.blocks[owner]

    # The enumerated items are the nested bullets of the block that are
    # not its own conformance criteria. Prose paragraphs (the out-of-scope
    # note, the reference line) are not items and are not inspected.
    criterion = re.compile(r"^\s*-\s+\*\*R\d+\.\d+\*\*")
    nested = re.compile(r"^\s{2,}-\s+")
    items = []
    buf = None
    for n, line in enumerate(block["lines"]):
        if nested.match(line):
            if buf:
                items.append(buf)
            buf = None if criterion.match(line) else \
                {"line": block["start"] + n, "text": line}
            continue
        if buf is not None:
            if not line.strip():
                items.append(buf)
                buf = None
            elif len(line) - len(line.lstrip()) >= 4:
                buf["text"] += " " + line
            else:
                items.append(buf)
                buf = None
    if buf:
        items.append(buf)

    if not items:
        cannot_tell.append(
            "%s declara un conjunto cerrado pero no le encontre los items "
            "enumerados, asi que no pude contar los que no tienen token"
            % owner)
        return

    seen = 0
    for item in items:
        flat = collapse(item["text"])
        for m in re.finditer(r"\(([^()]*\bIAB\b[^()]*)\)", flat):
            seen += 1
            if "`" not in m.group(1):
                finding("enumeracion-sin-token",
                        "%s enumera un valor sin token: %s"
                        % (owner, m.group(0)[:90]),
                        "%s:%d" % (ctx.name(block["file"]), item["line"] + 1))
    if not seen:
        cannot_tell.append(
            "no encontre en %s ninguna cita a la definicion externa de un "
            "valor, que es contra lo que se mide si falta el token" % owner)


ITEM_START = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|\|)")


def sentence_around(lines, n, pattern):
    """Every sentence on line `n`'s BLOCK that mentions the term, joined.

    Two boundaries, and each one was found by a control that failed:

    A markdown paragraph is hard-wrapped at no particular place, so the
    releasing clause — "though the ADS is not bound to VAST" — lands on
    the next line as often as on the same one. Reading a line alone
    reported two mentions whose release was one line below.

    And a block ends at the next list item, not at the next blank line.
    Bullets in a list have no blank lines between them, so a paragraph
    boundary swallowed the whole list: a bullet saying the ADS is not
    bound released a DIFFERENT bullet that demanded VAST parsing. That
    mutation went undetected until this boundary was added.
    """
    start = n
    while start > 0 and lines[start].strip() and not ITEM_START.match(lines[start]):
        start -= 1
    end = n
    while (end + 1 < len(lines) and lines[end + 1].strip()
           and not ITEM_START.match(lines[end + 1])):
        end += 1
    block = " ".join(l.strip() for l in lines[start:end + 1])
    parts = re.split(r"(?<=[.;])\s+", block)
    hit = [part for part in parts if pattern.search(part)]
    return hit if hit else [block]


def check_confined_term(ctx, finding, cannot_tell):
    """A term a requirement confines to illustrative material, used
    outside it. The requirement writes the rule of its own check."""
    confined = []
    for ident in sorted(ctx.blocks):
        text = collapse(ctx.blocks[ident]["text"])
        m = CONFINED_TERM_DECLARATION.search(text)
        if m:
            confined.append((m.group(1), ident, False))
            continue
        m = CONFINED_TERM_UNLESS_UNBOUND.search(text)
        if m:
            confined.append((m.group(1), ident, True))
    if not confined:
        cannot_tell.append(
            "ningun requerimiento confina un termino a material ilustrativo "
            "con la formula que conozco, asi que no busque menciones fuera "
            "de anexo. Cero hallazgos aca no dice nada.")
        return

    for term, owner, unbound_ok in confined:
        block = ctx.blocks[owner]
        # The requirement's own statement of the rule is not a use of the
        # term, and neither is its row in the summary table.
        index_row = re.compile(r"^\|\s*%s\s*\|" % owner)
        pattern = re.compile(r"\b%s\b" % re.escape(term))
        hits = collections.OrderedDict()
        total = 0
        for path in ctx.files:
            marked = ctx.marked_illustrative(path)
            for n, line in enumerate(ctx.lines[path]):
                if path == block["file"] and block["start"] <= n <= block["end"]:
                    continue
                if index_row.match(line):
                    continue
                if n in marked:
                    continue
                if unbound_ok and all(
                        NOT_BOUND_CLAUSE.search(sent) for sent in
                        sentence_around(ctx.lines[path], n, pattern)):
                    # The requirement permits naming the term as the typical
                    # case when the same sentence says the actor is not tied
                    # to it. The sentence, not the line: the release and the
                    # mention routinely sit on different lines of the same
                    # wrapped paragraph.
                    continue
                count = len(pattern.findall(line))
                if count:
                    total += count
                    hits.setdefault(ctx.name(path), []).append(n + 1)
        verb = ("prohibe depender de" if unbound_ok
                else "confina toda mencion de")
        for name, places in hits.items():
            shown = ", ".join(str(p) for p in places[:6])
            if len(places) > 6:
                shown += " ..."
            finding("termino-confinado",
                    "%s %s %s fuera de material ilustrativo; %s lo hace en "
                    "%d linea/s sin decir que no se esta atado"
                    % (owner, verb, term, name, len(places)),
                    "%s:%s" % (name, shown))
        if total:
            finding("termino-confinado",
                    "total: %d mencion/es de %s fuera de material marcado"
                    % (total, term), "context/")


def check_malformed_modals(ctx, finding, _cannot_tell):
    for path in ctx.files:
        for first, unit in ctx.units(path):
            flat = collapse(unit)
            for pattern, why in MALFORMED_MODAL:
                for m in pattern.finditer(flat):
                    finding("modal-malformado",
                            "%s -- %s" % (m.group(0)[:80], why),
                            "%s:%d" % (ctx.name(path), first + 1))


def check_normative_force(ctx, finding, _cannot_tell):
    for path in ctx.files:
        text = ctx.text[path]
        if ctx._declares_itself_illustrative(ctx.lines[path]):
            # A file that declares itself informative has answered this
            # question about itself, and the answer is the one that
            # resolves the finding. Without this, a sentence explaining
            # HOW the file is not normative — "the separation described
            # here is normative only through the requirements" — trips
            # the very check that sentence exists to satisfy.
            continue
        m = NORMATIVE_SELF_DECLARATION.search(text)
        if not m:
            continue
        obligations = len(OBLIGATION_MODAL.findall(text))
        if obligations < MIN_OBLIGATIONS_IN_NORMATIVE_FILE:
            line = text[:m.start()].count("\n") + 1
            finding("normativo-sin-fuerza",
                    "%s se declara normativo (\"%s\") y no tiene ningun "
                    "MUST / SHOULD / SHALL: lo que manda y lo que describe "
                    "no se distinguen"
                    % (ctx.name(path), collapse(m.group(0))),
                    "%s:%d" % (ctx.name(path), line))


def check_glossary_coverage(ctx, finding, cannot_tell):
    """A multi-word term used above the threshold with no glossary entry."""
    glossary = None
    for path in ctx.files:
        if re.search(r"^#\s+Glossary\b", ctx.text[path], re.M | re.I):
            glossary = path
            break
    if glossary is None:
        cannot_tell.append(
            "no encontre el glosario, asi que no pude cruzar los terminos "
            "de alta frecuencia contra el. Cero hallazgos aca no dice nada.")
        return

    def normalise(word):
        if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            return word[:-1]
        return word

    defined = set()
    for m in re.finditer(r"^- \*\*(.+?)\*\*", ctx.text[glossary], re.M):
        head = re.sub(r"\(([^)]*)\)", r"/\1", m.group(1)).replace("*", "")
        for part in head.split("/"):
            part = part.strip().lower()
            if part:
                defined.add(" ".join(normalise(w) for w in part.split()))
    if not defined:
        cannot_tell.append(
            "el glosario no tiene entradas que sepa leer, asi que todo "
            "termino contaria como no definido")
        return

    counts = collections.Counter()
    for path in ctx.files:
        if path == glossary:
            continue
        body = re.sub(r"```.*?```", " ", ctx.text[path], flags=re.S)
        keep = []
        for line in body.split("\n"):
            s = line.strip()
            if s.startswith("#") or s.startswith("|"):
                continue
            # A bold run opening a line is a label, not prose.
            keep.append(re.sub(r"^[-*]?\s*\*\*[^*]+\*\*:?", " ", s))
        body = "\n".join(keep)
        body = re.sub(r"`[^`]*`", " ", body)
        body = re.sub(r"https?://\S+", " ", body)
        toks = words_of(body)
        for size in range(TERM_MIN_WORDS, TERM_MAX_WORDS + 1):
            for i in range(len(toks) - size + 1):
                gram = toks[i:i + size]
                if any(w in STOPWORDS or len(w) < 3 for w in gram):
                    continue
                counts[" ".join(normalise(w) for w in gram)] += 1

    candidates = [(g, c) for g, c in counts.items()
                  if c >= TERM_FREQUENCY_THRESHOLD and g not in defined]
    candidates.sort(key=lambda gc: -gc[1])
    for gram, count in candidates:
        # A longer phrase built on a term already reported says the same
        # thing twice.
        if any(other != gram and other in gram and c >= count
               for other, c in candidates):
            continue
        finding("termino-sin-glosario",
                "\"%s\" aparece %d veces y no tiene entrada de glosario"
                % (gram, count), ctx.name(glossary))


def check_open_questions(ctx, finding, cannot_tell):
    """A question the text states as open, absent from the register the
    specification keeps for exactly that."""
    register_file = None
    rows = []
    for path in ctx.files:
        m = OPEN_REGISTER_HEADING.search(ctx.text[path])
        if not m:
            continue
        register_file = path
        start = ctx.text[path][:m.start()].count("\n")
        end = len(ctx.lines[path])
        for n in range(start + 1, len(ctx.lines[path])):
            if ctx.lines[path][n].startswith("#"):
                end = n
                break
        for line in ctx.lines[path][start:end]:
            s = line.strip()
            if not s.startswith("|") or re.match(r"^\|[-\s|:]+\|$", s):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and cells[0].lower() not in ("unit", ""):
                rows.append(cells[0])
        register = (start, end)
        break
    if register_file is None:
        cannot_tell.append(
            "no encontre el registro de preguntas abiertas, asi que no pude "
            "cruzar contra el las preguntas sueltas del texto")
        return

    recorded = set()
    for row in rows:
        recorded.update(re.findall(r"R\d+(?:\.\d+)?|UC-\d+|DP-[\d.]+", row))

    unit_id = re.compile(
        r"^\s*-\s+\*\*(R\d+(?:\.\d+)?)[.*]|^#{2,4}\s+(UC-\d+)|^- \*\*(R\d+)\.")
    for path in ctx.files:
        current = None
        for n, line in enumerate(ctx.lines[path]):
            m = unit_id.match(line)
            if m:
                current = m.group(1) or m.group(2) or m.group(3)
            if path == register_file and register[0] <= n < register[1]:
                continue
            s = line.strip()
            if re.match(r"^\*\*[^*]+\*\*:?$", s):
                continue  # a label announcing a section, not a question
            hit = OPEN_QUESTION_MARKER.search(line)
            if not hit:
                continue
            if current and current in recorded:
                continue
            finding("pregunta-fuera-del-registro",
                    "pregunta abierta en %s sin fila en el registro: \"%s\""
                    % (current or "unidad desconocida", collapse(s)[:90]),
                    "%s:%d" % (ctx.name(path), n + 1))


CHECKS = [
    check_closed_vocabulary,
    check_enumeration_tokens,
    check_confined_term,
    check_malformed_modals,
    check_normative_force,
    check_glossary_coverage,
    check_open_questions,
]

HELP = """bin/check-context-vocabulary.py — the vocabulary and normative-force
axis of context/, next to the structural axis its brother
check-context-coherence.py answers.

WHAT IT ASKS
  Values used outside the closed enumeration that declares them;
  enumerated items with no token; a term confined to illustrative
  material used outside it; RFC 2119 modals that cannot bind; a file
  that calls itself normative and obliges no one; frequent multi-word
  terms with no glossary entry; open questions missing from the
  register. Every rule is read off context/ itself.

OPTIONS
  --quiet         print nothing when nothing is found
  --dir DIR       check this directory instead of context/ — used for
                  testing this script
  --help          this text

EXIT CODES
  0   nothing found
  1   findings — the list says what and where
  2   cannot tell: an anchor this check reads its rules from is missing
      (no closed enumeration declared, no glossary, no register of open
      questions). 2 wins over 1 and 1 over 0, because zero findings is
      also what a check that never ran its rule looks like. On a 2 the
      findings it did make are still printed, marked as a partial list.
  64  the command line was wrong. Deliberately outside 0/1/2 so a typo
      can never be read as a verdict about context/.
"""


def main(args):
    if "--help" in args or "-h" in args:
        sys.stdout.write(HELP)
        return 0

    quiet = False
    directory = CTX
    i = 0
    while i < len(args):
        if args[i] == "--quiet":
            quiet = True
        elif args[i] == "--dir":
            if i + 1 >= len(args):
                sys.stderr.write("check-context-vocabulary: --dir necesita un "
                                 "directorio\n")
                return 64
            i += 1
            directory = os.path.abspath(args[i])
            if not os.path.isdir(directory):
                sys.stderr.write("check-context-vocabulary: no existe el "
                                 "directorio %s\n" % args[i])
                return 64
        else:
            sys.stderr.write(
                "check-context-vocabulary: no conozco el argumento %s\n"
                "    No corri nada, a proposito: un veredicto que contesta\n"
                "    otra pregunta es peor que ninguno.\n"
                "    bin/check-context-vocabulary.py --help\n" % args[i])
            return 64
        i += 1

    ctx = Context(directory)
    if not ctx.files:
        sys.stderr.write("check-context-vocabulary: no hay archivos .md en "
                         "%s\n" % directory)
        return 2

    findings = []
    cannot_tell = []

    def finding(kind, message, where):
        findings.append((kind, message, where))

    for check in CHECKS:
        check(ctx, finding, cannot_tell)

    code = 2 if cannot_tell else (1 if findings else 0)

    if code == 0 and quiet:
        return 0

    print("context/: %d archivos, %d requerimientos"
          % (len(ctx.files), len(ctx.blocks)))

    if cannot_tell:
        print("\nNO SE PUEDE SABER — %d motivo(s)" % len(cannot_tell))
        for reason in cannot_tell:
            print("  · %s" % reason)
        if findings:
            print("\n  Lo que igual se encontro (lista PARCIAL, %d):"
                  % len(findings))
    elif findings:
        print("\nFALLA: %d hallazgo(s) de vocabulario o fuerza normativa."
              % len(findings))
    else:
        print("\nOK: nada fuera de la enumeracion, ningun modal malformado, "
              "ningun termino frecuente sin glosario,")
        print("    ninguna pregunta abierta fuera del registro.")

    by_kind = collections.OrderedDict()
    for kind, message, where in findings:
        by_kind.setdefault(kind, []).append((message, where))
    for kind, rows in by_kind.items():
        print("\n  %s (%d)" % (kind, len(rows)))
        for message, where in rows:
            print("    %-28s %s" % (where, message))

    print("\n  Lo que un verde de aca NO dice")
    print("    que un termino definido este bien definido, que un valor")
    print("    enumerado sea el correcto para donde se usa, ni que dos")
    print("    requerimientos no se contradigan. Eso no tiene firma")
    print("    sintactica y no lo encuentra ningun script.")

    print("\nHALLAZGOS=%d TIPOS=%d SIN_RESOLVER=%d"
          % (len(findings), len(by_kind), len(cannot_tell)))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
