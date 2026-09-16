# Recommended changes to `context/` from the 2026-08-19 SVTA Ads WG call

Written 2026-09-14. Input: the T-03 verdicts
([`tasks/T-03/verdicts.md`](tasks/T-03/verdicts.md)), the agreements extract
([`svta-wg-2026-08-19-agreements.md`](svta-wg-2026-08-19-agreements.md)), and the
literal text of `context/` read at every line cited below.

**This was a list of recommendations, not an edit.** The recommendations have
since been decided and, where a decision required it, applied to `context/`. The
*Where it landed* column of the summary names the task and commit for each one;
`TASKS.md` T-06..T-13 carries the full record. What is still open is in
*Decisions outstanding*. The verification section at the end is a **dated
record** of the state before any of that landed, not the state today.

Every item is classified **DRAFTING** or **DESIGN**, because the two need
different decisions:

- **DRAFTING** — the spec already permits what the WG wants; the text does not
  say so. Nothing conformant today becomes non-conformant, or vice versa.
  Deciding these costs a read of the proposed wording.
- **DESIGN** — the change alters what the spec permits. Deciding these means
  accepting or rejecting a WG position, and in two cases it means retiring a
  use case.

## Summary

| # | WG item | Where | Class | Decision needed | Where it landed |
|---|---|---|---|---|---|
| D-1 | A2 | `02-actors.md:128–133` | DRAFTING | Approve wording | **Applied** — T-08 (`4304208`) |
| D-2 | A2 | `03-requirements.md:391–393` | DRAFTING | Approve wording | **Applied** — T-08 (`4304208`) |
| D-3 | A2 | `03-requirements.md:389` | DRAFTING | Approve wording | **Applied** — T-08 (`4304208`) |
| D-4 | A2 | `03-requirements.md:89` | DRAFTING | Approve wording | **Applied** — T-08 (`4304208`) |
| D-5 | A2 | `99-glossary.md:48–54` | DRAFTING | Approve wording | **Applied** — T-08 (`4304208`) |
| D-6 | A2 | `03-requirements.md` R18.2 + a new requirement | **DESIGN** | Publisher-gated or Player-gated | **Applied — Player-gated.** R18.2 + R29 in T-07 (`8fe9bd3`); R29 rebound to R3's device classes in T-09 (`3a0823c`) |
| N-1 | A2 | `02-actors.md:192` | NO CHANGE | Confirm | Confirmed — no change |
| N-2 | A2 | `04-use-cases.md` UC-09 | NO CHANGE here | Belongs to T-05 | **Open** — T-05 is *partly landed*; the paired use case remains |
| G-1 | A6 | R22 + UC-04 + coverage table | **DESIGN** | Adopt A6 or not — costs UC-04 | **Open — David (WG)** |
| G-2 | A7 | R17 + UC-08 + coverage table | **DESIGN** | Adopt A7 or not — costs UC-08; blocked | **Open — Zach Kava, via David** |
| G-3 | A8 | new requirement + "dismiss" vocabulary + glossary | **DESIGN** (addition) | Adopted; **blocked on the WG** — the slot question went out as an issue | **Open — the WG**, via issue 7 on the public repo |
| D-7 | A2 | the new requirement's carrier | **DESIGN** | Query string by default; header admissible | **Applied** — inside R29, T-07 / T-09 |
| X-1 | — | numbering | **SETTLED** | — | **Applied** — `.project/PROJECT.md` |

Five drafting items, four design items, and two confirmations that nothing
changes. Seven of the thirteen are applied; the four that remain are all waiting
on someone outside this project, plus the T-05 use case.

**Four further changes landed that have no row above**, because they were raised
and decided after this table was drawn. They are recorded in `TASKS.md`: the APS
may omit options from what the ADS returned with the order preserved (T-10,
`ff528d7`); the two out-of-scope declarations OOS-5 and OOS-6 (T-11, `730c468`);
R30 and ADR 0005, an empty resolution being distinguishable from a failed one
(T-12, `cac233f`); and the `<Error>` mapping row no longer describing APS
internals (T-13, `624585a`).

## Decisions outstanding — three, all external

The items above are not one request. Each line below is a **separate answer**,
and none of them implies any other:

| # | Question | Answers it | Blocks | Status |
|---|---|---|---|---|
| 1 | Approve the proposed wording of **D-1 … D-5**? One answer covers the five: they are the same correction at five sites, and D-1 is the one that carries the rest. | Nicolás | Five drafting edits | **Answered — approved, and applied in T-08** |
| 2 | **D-6**: is the reserved parameter set **Publisher-gated** (what Annex I gives: the Publisher declares the template) or **Player-gated** (the Player decides what to disclose — not provided by Annex I, separate cost)? | Nicolás | R18.2's rewording and the new requirement | **Answered — Player-gated.** R29.2 makes sending a reserved parameter OPTIONAL, R29.3 omits rather than sends empty, and R29.5 obliges the APS to tolerate the absence. Applied in T-07 / T-09 |
| 3 | **A8 (a)**: does a viewer dismissal end the slot, or fall through to the next form under R14? Recommendation: it ends the slot. | ~~Nicolás~~ → **the WG** | The A8 requirement text | **Open.** It was not decided here: the current draft answers it by accident through R14.1, so the question went out to the WG as issue 7 rather than being settled on a drafting artefact. See §A8 |
| 4 | **A6**: does "one ad experience at a time" contemplate a Publisher-declared hybrid break, or only the narrower case Yasser asked about? | David (WG) | UC-04's fate and R22's rewording | **Open** |
| 5 | **A7**: does the "running ad owns the pause" practice hold? | Zach Kava, via David | R17's inversion and UC-08 | **Open** |

Nicolás's two answers are in and applied. **What remains is external in all three
cases** — the WG on the A8 slot question, David on A6, Zach Kava via David on
A7 — so nothing here is waiting on a decision this project can take by itself.

---

## A2 — DRAFTING. Six wording sites; nothing normative moves

T-03's verdict: every normative clause of R5 already permits the arrangement A2
describes. R5.1 requires "one or more" options, R5.5 makes several a MAY, R5.2
is a rule for *resolving* a choice rather than an obligation to *offer* one, and
R5.4 declines to mandate a device view rather than forbidding one. What fails is
the prose. A WG reader has only the words, and the words read as prescribing
client-side selection — this project's own extract read them that way.

### D-1 — `context/02-actors.md`, lines 128–133. The sharpest site

This is the one to fix first: it is not a permission phrased tightly, it is a
**stated premise about the interface** that A2 denies head-on.

**Today:**

> - **Produce candidates with renderable presentation options.**
>   Because the Player is device-agnostic on the APS interface, the APS
>   emits each ad candidate carrying one or more renderable presentation
>   options (form + layout) as an ordered list whose document order is
>   the preference order, and the Player renders the first option it can
>   satisfy per device capabilities and the Publisher's allowed layouts.

**Proposed:**

> - **Produce candidates with renderable presentation options.**
>   The APS emits each ad candidate carrying one or more renderable
>   presentation options (form + layout). When a candidate carries more
>   than one, they form an ordered list whose document order is the
>   preference order, and the Player renders the first option it can
>   satisfy per device capabilities and the Publisher's allowed layouts.
>   How many options a candidate carries is the APS's call: an APS that
>   holds its own view of the device MAY carry exactly one, and the
>   choice then sits at the APS; an APS that holds no such view carries
>   the full ordered set and the outcome emerges at the Player. Both are
>   conformant under R5, and the Player-visible interface is identical in
>   either case.

The load-bearing edit is deleting *"Because the Player is device-agnostic on the
APS interface"*. A reader cannot reconcile that clause with an implementation
that sends capabilities up to the APS without being told the clause described one
implementation rather than the interface.

**Drags:** nothing normative. `02-actors.md` has no conformance criteria. The APS
glossary entry (`99-glossary.md:70–83`) does not repeat the premise — checked.

### D-2 — `context/03-requirements.md`, lines 391–393. "Sole authority"

**Today:**

> The Player is the sole
> authority on device capability — neither the ADS nor the APS needs
> a device-class matrix or a per-Player view.

Read alone, the headline phrase excludes the APS from knowing anything about the
device, which is precisely what A2 has it doing. The em-dash clause that follows
narrows it correctly, but the headline is what carries.

**Proposed:**

> The Player is the authority on what its own device can render: no
> presentation option reaches the screen without passing the Player's
> capability check. This specification therefore requires no device-class
> matrix and no per-Player capability view at the ADS or the APS. An
> implementation whose APS does hold such a view is equally conformant —
> it simply arrives at a shorter option list, and the Player's check is
> unchanged.

**Drags:** none. R5.4 (lines 437–439) already says the same thing normatively and
stays as is.

### D-3 — `context/03-requirements.md`, line 389. The R5 gist

The gist line is what a reader skims.

**Today:** *Gist: Each candidate carries renderable presentation options in preference order, and the Player renders the first one its device can satisfy, skipping candidates with none.*

**Proposed:** *Gist: Each candidate carries one or more renderable presentation options; where there are several, document order is the preference order and the Player renders the first one its device can satisfy, skipping candidates with none.*

### D-4 — `context/03-requirements.md`, line 89. The core-invariant table

Line 89 sits in the eight lines the spec itself tells a new reader to start from
(lines 77–82), so the plural reading lands before anything qualifies it.

**Today:** `| R5 | Candidates list renderable options in preference order; the Player renders the first its device can satisfy. |`

**Proposed:** `| R5 | Candidates carry one or more renderable options; where there are several, the Player renders the first its device can satisfy. |`

### D-5 — `context/99-glossary.md`, lines 48–50 and 51–54

Both entries repeat the plural-as-default reading. Not found by T-03's audit,
which stopped at `03-requirements.md` and `02-actors.md`.

**Today (`Presentation option`, 51–54):**

> a (form + layout) pairing offered for an ad candidate. The resolution document
> lists the options in an ordered list; document order is the preference order
> the Player follows (R5).

**Proposed:**

> a (form + layout) pairing offered for an ad candidate. A candidate carries one
> or more; when it carries several they appear as an ordered list, and document
> order is the preference order the Player follows (R5).

**Today (`ListMPD`, 48–50):** *"The presentation options an ad offers appear in the ListMPD as an ordered list; document order is the Player's preference order (R5)."*

**Proposed:** *"The presentation options an ad offers appear in the ListMPD; when an ad offers more than one, they appear as an ordered list whose document order is the Player's preference order (R5)."*

### D-6 — The scope sentence is not clarified; it is narrowed

The two options this item once offered — a cross-reference from R5 to R18, or a
sentence declaring the event URL's contents bilateral — are both overtaken. The
position to design against is that the spec **reserves parameter names** on the
Player→APS leg, optional to send, with declared room for vendor extensions. The
second option would have written down the opposite of that.

**Verified against the norm** (DASH 6th, Annex I, queried 2026-09-14):

- The carrier exists and this project already documents it:
  `05-dash-linear-interfaces.md:114–116, 167–169, 183–187, 251–256` — the
  MPD-level `UrlParamInfo` descriptor (§I.4), scoped to the APS resolution
  request by `@includeInRequests="altmpd"`.
- The state-variable vocabulary **is extensible**: Annex I accommodates custom
  URNs (its own example is `$urn:example:gps$`), signalled by an
  `EssentialProperty` / `SupplementalProperty` carrying the custom
  `@schemeIdUri`. Reserving parameters therefore means **defining URNs**, not
  inventing a mechanism — R9 is satisfied by reuse.
- The **content author declares the template, and the client cannot append
  parameters the template did not declare.** Optionality sits with the
  Publisher, not the Player.
- The two-tier naming this needs is already written:
  `06-naming-and-namespaces.md:18–61` — `urn:svta:dash:<construct>:<year>` for
  spec-defined, `urn:qualabs:<feature>:<year>` for vendor-private.
- **No existing state variable covers what is wanted**, so every reserved name is
  a new URN. There is none for concurrent-decoder capacity, none for the
  device's codec-support profile, and none for which streaming format the client
  can play.

  **The trap — read this before concluding that `video` already solves it.**
  Annex I's definition of the `video` state variable says that *"in case
  multiple representations are being simultaneously decoded (e.g. scalable
  video), comma-separated values for the base layer are followed by a comma and
  a comma-separated list of dependent (e.g. enhancement layer) codec and
  bandwidth values"*. Anyone searching this vocabulary for decoder capability
  finds that sentence, sees simultaneous decoding described in the standard
  itself, and stops. It does not solve the case: it reports **what is being
  decoded right now**, not **what the device is able to decode**. A stream
  carrying one video says nothing about whether a second decoder exists. The
  same holds for `audio` and `video` generally — they carry the `@codecs` and
  `@bandwidth` of the Representation currently playing, which is playback state,
  not device capability. They look like they fit, and they do not.
- **Withholding a value is expressible, and it is two mechanisms rather than
  one.** A client that understands a variable but has no value, or declines to
  give one, substitutes the **sentinel defined for that variable** in Table I.5
  (`lang#` → `"und"`, `execution-delta#` → `"0"`, `expected-duration#` → `"-1"`,
  `execution-count#` → `"-1"`, `previous-state` → `"normal"`), and an **empty
  string** where no sentinel is prescribed (Tables I.1 / I.2). A client that does
  not understand the scheme substitutes the literal `"<null>"` (clauses I.2.3.3,
  I.4.3). The two are therefore distinguishable on the wire: **withholding and
  ignorance do not look alike to the APS.**

**The privacy argument is SUSPENDED, and a Player-initiated design dissolves the
question rather than answering it: `@sameOriginOnly` is an Annex I attribute on
a Publisher-declared descriptor, so it does not govern parameters the Player
appends outside that mechanism.** The blocker is gone; the underlying question
returns in a different form — what protects the viewer when a Player discloses
device capability to an ad server on its own initiative — and CMCD's answer
there is "trusted endpoints" plus player-side configuration, not a manifest
attribute. That is a new conversation, not a reformulation of this one. What
follows is the state of the original question, kept because it is what was
verified: What is established: `@sameOriginOnly` states that *"parameters shall
only be sent to the same origin they were instantiated from"*, origins compared
per IETF RFC 6454, and **its default is `false`**. What is not established is
whether it can be used here at all: the resolution request goes to the APS,
which sits on a different origin from the MPD, and retrieval against the ISO
text defines the instantiating origin for parameters taken from the MPD, the MPD
URL or an HTTP header — **but not for a value computed client-side, which is
exactly our case.** Until that is read in the PDF, the honest statement is: *the
standard has an origin-control attribute; how it interacts with an APS on
another origin is unresolved.* Nothing stronger.

**The mechanism worth remembering, because it will recur: a control that guards
against leaking to third parties does not protect a feature whose intended
recipient is a third party — it switches it off.** `@sameOriginOnly` exists to
stop parameters reaching an origin the Publisher did not intend. The APS is an
origin the Publisher did intend, and a different one from the MPD. When a
security control's trigger condition coincides with the feature's normal
operation, turning it on is not hardening; it is disabling.

**The gate is the Player, not the Publisher.** That decision changes what this
item costs, because Annex I cannot carry it: its template is declared by the
content author and *"the client cannot append un-templated query parameters"*.
A Player that adds parameters on its own initiative is doing something Annex I
does not provide for. **This is therefore a parallel mechanism, not an extension
of Annex I** — and that has to be said out loud to the WG as design, not as
clarification.

**The precedent makes it defensible, and it is the one Nicolás named.** CTA-5004
(CMCD) already does exactly this shape, verbatim:

- **Client-initiated, no declaration required.** *"The player attaches CMCD data
  to each media object request, using either query arguments or request
  headers."* Nothing has to authorise it first.
- **Reserved set plus vendor extension.** *"The key names described in Table 1
  are reserved"*; *"Custom key names may be used, but they MUST carry a
  hyphenated prefix to ensure that there will not be a namespace collision with
  future revisions to this specification."* That is our two-tier naming, already
  proven in a shipped standard.
- **Optional by default.** *"All keys are OPTIONAL except for 'v' which is now
  required as of version 2."*
- **Omission, not a sentinel.** *"A player MUST NOT send a value for an optional
  CMCD parameter if its value is unknown or undefined. Instead, the key MUST be
  omitted entirely from the data transmission."*
- **And a manifest may configure without gating.** *"If the content has metadata
  defining CMCD configuration, the player SHOULD apply this configuration by
  default"* — covering version, transport mode, which requests carry data, the
  key list and filters. `SHOULD`, not `MUST`: the content side advises, the
  client decides. That is the shape that gives the Publisher influence without
  making the Publisher a required actor.
- **Coexistence is the client's job.** *"If there are CMCD keys specified in a
  manifest as part of segment request URLs, care should be taken to
  remove/overwrite or merge them with future CMCD reports ideally based on
  configuration options."* Two routes to the same data already coexist in
  practice, and neither is authoritative: the client reconciles.

**What changes in `context/`, grouped by what happens to each item:**

**Stays as written**

- **R18's gist** — *"The spec defines only the Player-visible interface; the
  APS-to-ADS and ADS-side APIs are out of scope and agreed bilaterally."* Still
  exactly true: the resolution request is the Player-visible interface.
- **R18's opening sentence** — *"This specification does NOT define the URL
  syntax, parameter names, request payload, response payload, or any other
  aspect of the APS-to-ADS API, nor of the ADS-side API."* Scoped to the APS-ADS
  side throughout.
- **R18.1** — *"The specification documents the MPD event URL pattern
  (Player-visible input, served by the APS) and the resolution document format
  (Player-visible output, produced by the APS)."* Already the hook the new
  material hangs from.
- **R2 and R2.1–R2.4** — the four-actor contract is untouched; resolving the APS
  URL is already the Player's role.
- **R11.2** — *"The Player never talks to the ADS directly; it reads only the
  resolution document the APS produces."*

**Narrowed**

- **R18.2.** Today: *"The bilateral contracts — Publisher-to-APS for the event
  URL and APS-to-ADS for ad decisioning invocation — are established and
  maintained by those parties directly, outside this specification."*
  Would say: *"The APS-to-ADS contract for ad decisioning invocation is
  established and maintained by those parties directly, outside this
  specification. The Publisher's arrangement with the APS for the event URL
  remains bilateral, except for the parameters this specification defines on the
  Player's resolution request."*

**Changes**

- **R18's title.** Today: *"ADS / APS API contracts are not defined by this
  spec."* Would say: *"The APS-to-ADS and ADS-side API contracts are not defined
  by this spec."*
- **OOS-2.** Today: *"The proposal only specifies the contract between the MPD
  event and the resolution document the APS returns."* Would say: *"…the
  contract between the MPD event, the Player's resolution request, and the
  resolution document the APS returns."* The rest of the item is unchanged.
- **The APS's Player-facing endpoint, in the actor model.** Today: *"The
  Publisher can encode slot constraints (for example, a slot-duration hint) as
  query parameters on that URL — this is the APS's runtime input."* Would add
  that the Player may also attach the parameters this specification defines.
- **The Player's responsibilities, in the actor model.** Today the Player
  *"Resolve[s] the APS URL when the playhead reaches an event and receive[s] the
  list of ad candidates as the resolution document."* Would gain: *"Attach the
  parameters it chooses to send. Which of them travel is the Player's decision;
  a parameter whose value it does not have, or does not wish to disclose, is
  omitted rather than sent empty."*
- **The boundary summary, in the actor model.** Gains one line: *"What the
  Player discloses about its device — **Player**."*

**Added**

- **One new requirement: the parameters the Player may send on the resolution
  request.** It defines the reserved names; that sending any of them is the
  Player's choice; that a parameter with no value, or one the Player does not
  wish to disclose, is omitted entirely rather than sent empty; that
  vendor-specific parameters carry a distinct prefix so they cannot collide with
  names this specification adds later; and that they travel as query parameters
  on that request. Its number is assigned when the text lands.
- **One glossary term** for those parameters.

**Removed**

- Nothing. No requirement falls.

**What this costs, stated without softening.** It is new normative machinery: a
parameter set carried on a request that DASH already describes, by a party DASH
does not authorise to add to it. R9 obliges us to document why the existing
construct was not reused, and the honest reason is that Annex I's construct is
gated by the wrong actor for this purpose. Implementers using strict
DASH-conformant tooling may not expect client-appended parameters. And the WG
will read it as a new mechanism, because it is one — the CMCD precedent makes it
familiar, not smaller.

**What today's Annex I research is now worth.** The nine state variables, their
sentinels and the five-to-four convention describe **the route we are not
taking**. They are not wasted: they are the evidence that the Annex I route is
Publisher-gated and therefore cannot serve this decision. But they stop being
load-bearing for the new requirement, and the sentinel obligation is **replaced**
by CMCD's omission rule.

**What does not change: R18's gist, its prose and R18.1 all stand.** The gist
scopes out-of-scope to the APS-to-ADS and ADS-side APIs. The prose's opening
sentence attaches *"URL syntax, parameter names, request payload, response
payload"* to **the APS-to-ADS API**. Its second sentence — *"The specification
documents only the Player-visible interface — the MPD event URL referenced by
the Publisher"* — plays in favour, because reserving parameters on that URL is
documenting more of exactly that interface. R18.1 already commits the spec to
documenting the event URL pattern.

**Open, and it decides how the new requirement is worded:** Annex I puts the
switch in the Publisher's hand. If the intent is that the **Player** decides what
to disclose, Annex I does not provide that, and it is a separate cost.

### N-1 — `context/02-actors.md`, line 192. No change

> *Selecting the ad to render* from validated candidates — **Player**.

Leave it. It is true in both implementations: with a single option the Player
still validates it and either renders it or skips it (R5.3 / R5.7). Softening it
would suggest an APS can bypass Player validation, which nobody proposed and
which would be a design change.

### N-2 — `context/04-use-cases.md` UC-09. No change *here*

UC-09 survives intact — its own premise is that the ADS is unaware of the device
class (line 1018), so it illustrates one implementation R5 permits rather than
the only one. Its lines 979–985 do repeat *"device capability is the Player's sole
authority"*, but as the stated intent of that scenario, which is legitimate.

Editing UC-09 so it reads as one of a pair — rather than as the canonical path —
is **T-05's** job, not a correction to make here, and it only makes sense
alongside the companion case. Flagged so it does not get done twice.

---

## A6 — DESIGN. "One ad experience at a time" deletes UC-04

**The decision:** adopt the WG's cross-family rule, or hold UC-04.

**Not contradicted:** R22 (line 899) bounds simultaneity *within* the non-linear
family — narrower than A6, consistent with it. The extract's framing that A6 vs
R22 is the collision is wrong.

**Contradicted:** **UC-04 — Hybrid linear + concurrent overlay**
(`04-use-cases.md:421–541`) models exactly what A6 forbids: *"a linear ad takes
over the screen and a non-linear overlay is composited on top of it during the
same break"*, specified against all five device classes. Its D1 expected
behaviour (lines 456–459) is Yasser's question answered the other way.

### Changes if A6 is adopted

| Site | Change |
|---|---|
| `03-requirements.md:899–936` (R22) | Widen from "one non-linear form" to "one ad experience". Title, gist, prose, **and the rationale**: today it is decoder-budget-based (lines 909–920), and that argument does not reach a linear ad plus an overlay — it is one decoder each, which the budget allows. A widened R22 needs a second ground, and the WG's ground is brand conflict and ad-delivery practice [37:29], not decoders. |
| `03-requirements.md:93` | Core-invariant table line for R22. |
| `04-use-cases.md:421–541` | UC-04 **superseded**, not deleted — the file's own rule at lines 23–25 says existing cases are never deleted, only marked superseded. |
| `04-use-cases.md:78` | Coverage-table row for UC-04, and with it the "Mixed" category, which no other row uses (verified). |
| `04-use-cases.md:528–541` | UC-04's two "Notes / open questions" become moot and go with it. |
| `context-analysis/` | `uc-coverage-matrix.md` (rows 21, 36, 131, 143) and `dash-gap-analysis.md` regenerate from the prompts — do not hand-patch. |

**Reached but not blocked:** phase `04-multiview`. It grounds its device-class
reasoning on the R22/R3 decoder-budget argument (`PHASE.md:142`,
`T-01-PLAN.md:132, 182, 213`, `TASKS.md:17`). If R22's rationale changes, that
phase reads against a moved requirement. **Verified correction:** phase
`04-multiview` contains zero references to R5 or to ordered fallback — the risk
register's claim that A2 reaches it is wrong; **A6 is what reaches it.** Phase
`03-custom-layout` is the one that leans on R5 (`T-01-PLAN.md:36, 86, 92, 95,
118, 140`), and since A2 is drafting-only, it is unblocked.

**Not reached:** R17 (already legislates one cross-family case consistently with
A6), R20 (same-family overlap, independent).

### Unresolved — do not decide this by inference

1. **David reviewed UC-04 and did not object to its premise.** In round 1
   (2026-05-20) he marked up `04-use-cases.md` inline and his UC-04 comment was
   `//CONFUSING` on the **D2 sub-bullet wording** (item U3 in
   `phases/02-wg-feedback-round-1/hassoun-feedback-crossref.md:57`) — a phrasing
   fix, which was made. He read the hybrid-break case and objected to a sentence
   in it, not to its existence. Three months later he states a rule that deletes
   it. **That is a question for David, not a contradiction to resolve here:** did
   A6 contemplate a Publisher-declared hybrid break, or was it answering the
   narrower case Yasser asked about (an *unplanned* non-linear ad landing during
   a linear ad)? The answer changes whether UC-04 dies or survives with a
   tightened Publisher-intent clause.
2. **§4.10 — the outer boundary of the rule.** Your *"not two ad experiences
   inside the player, controlled by this mechanism"* [42:42]. Verified as **not**
   rescuing UC-04: both of its portions are Publisher-declared and APS-resolved,
   i.e. inside the mechanism. It bounds only the edges (an application-drawn
   banner outside the SGAI flow), so it affects one scoping sentence of a
   reworded R22 and nothing else. T-02 item.

---

## A7 — DESIGN. Inverts R17 and costs UC-08. Currently blocked

**The decision:** adopt the WG's rule that a running ad owns the pause, or hold
R17.

**Contradicted:**

- **R17** (`03-requirements.md:806–845`), and R17.4 most sharply: *"The
  specification carries no construct that lets the Publisher, the ADS, or the APS
  invert this priority."* The spec has hard-coded the direction A7 reverses.
- **UC-08 — Overlay window crosses a pause-ad window**
  (`04-use-cases.md:831–961`), whole, across all five device classes. It is the
  state you described at [40:41] resolved the other way.

**Half of A7 is already ours.** Your restatement at [41:55] — no pause-ad *plus*
L-shape at the same time — is exactly what R17 does today (it suspends the
overlay so nothing composes simultaneously). What contradicts is David's half:
**which of the two wins.**

### Changes if A7 is adopted

| Site | Change |
|---|---|
| `03-requirements.md:821–830` | R17 prose: the arbitration is gated upstream — no pause-ad is raised while an ad is presenting. |
| `03-requirements.md:833–836` | R17.1 reverses. |
| `03-requirements.md:843–845` | R17.4 — the non-invertibility clause now protects the opposite direction. |
| `04-use-cases.md:831–961` | UC-08 superseded or rewritten to the opposite outcome (same supersede-not-delete rule). |
| `04-use-cases.md:80` | Coverage-table row for UC-08. |
| `03-requirements.md:600–610, 619–621` | R21's cross-refs to R17 — re-reference only, not contradicted. |
| `context-analysis/` | Regenerate (UC-08 is the densest row in the matrix, 17 Rs). |

**Verified correction to the phase's enumeration:** the extract lists "R17, R21,
R25, UC-05 and UC-08" and `TASKS.md` adds R16. **R16, R25 and UC-05 are not
reached.** They govern the pause-ad's lifecycle, its live-content time freeze and
the plain pause-with-no-overlay case; A7 adds a gating condition upstream of them
and changes nothing about how a pause-ad behaves once raised. R21 is
re-referenced, not contradicted.

### Two things A7 does not answer, and the spec would have to

Both are real design questions, not drafting:

1. **What counts as "an ad presenting"?** An overlay only, or also a linear ad
   inside a break? David's words are about an ad *break*; R17's state is about an
   *overlay*. Under A6 they collapse into one category, but only if A6 lands.
2. **What happens to the pause-ad opportunity?** Is it lost, or deferred to the
   next pause outside the ad? R25's presentation-time freeze assumes the window
   is anchored to the frozen clock, which gives a natural answer (the window
   survives the pause and the pause-ad can be raised on a later pause inside it)
   — but nothing says so, and it is a decision.

### Blocked

A7's own status in the room was *"agreed in substance, with a confirmation with
Zach Kava pending"* — you asked for it at [41:55], David accepted at [40:28]. The
contradiction is real as stated; whether the WG's statement holds is what the
confirmation is for.

**Recommendation: do not touch `context/` on A7 until Zach Kava confirms.** The
edit is cheap to make later and expensive to undo — UC-08 is the densest use case
in the set, and rewriting it twice costs more than waiting.

---

## A8 — DESIGN (an addition). Viewer-initiated dismissal is absent

**Adopted, and now waiting on the Working Group.** It is an addition, not a
conflict, and David put it as a MUST-support rather than a MAY. The carrier and
the eligibility gating are settled. **What happens to the slot went to the WG as
an issue rather than being decided here**, because the current draft answers it
by accident: R14.1 says each form starts when the previous one ends, and a
viewer dismissal is a form ending early, so the text already implies falling
through to the next form. That default is an artefact of drafting, not a
position anyone took.

**The requirement does not land until the WG answers**, because the answer
decides one of its conformance criteria. This is blocked externally, not pending
on our side. **No number is held for it**: per the allocation rule, the next
requirement to land takes R30, whether it comes from this item or another.

**Verified:** every occurrence of "dismiss" in `context/03-requirements.md`
(lines 531, 535, 544, 551, 640, 826, 838) is **the Player** acting on a state
transition, and every "skip" is the Player skipping an unrenderable candidate. A
grep across all of `context/` for a viewer-initiated skip, close or dismissal
returns nothing. Nothing forbids it either: DP-2 makes silence permissive, and
R28's ClickThrough (lines 1065–1080) already fires on a viewer action, so
viewer-initiated events are not foreign to the model.

**One nuance the extract under-reports:** David's *"we need to support it"*
[34:42] makes this a **MUST-support** capability with market-determined use, not
a MAY. The variants he named (premium tier always offers it; a timer gate) were
options, i.e. not spec.

### What the addition reaches

| Site | Change |
|---|---|
| `03-requirements.md`, "Interaction & composition rules" (753–937) | **New requirement**: the Player MUST support viewer-initiated dismissal of a non-linear ad form, with its conformance criteria. Number blocked — see X-1. |
| `03-requirements.md`: 531, 535, 544, 551, 640, 826, 838 | The verb "dismiss" acquires a second agent. Either the new construct uses a distinct verb, or "dismiss" is qualified at each site. |
| `04-use-cases.md`: 550, 561, 581, 587, 602, 618, 629, 643, 842, 872, 898, 920, 939 | **Thirteen more occurrences of the same verb**, which T-03's audit did not count — it stopped at `03-requirements.md`. Whatever vocabulary decision is taken applies here too. |
| `99-glossary.md` | A term for the new interaction. |
| `03-requirements.md:55–62` (DP-3) | One sentence so the new requirement does not read as contradicting *"maximize the ad opportunity"* — a viewer ending an ad is not the Player failing to use the opportunity. |

**Not reached:** R12 (lines 267–351). Dismissal is an interaction on existing ad
types, not a new type or placement — no widening of the closed set.

### Three sub-decisions inside it

1. **What happens to the slot on dismissal?** Does the slot end, or does the
   Player fall through to the next form under R14 (lines 761–804)? R14 sequences
   forms *"each form starting when the previous one ends"* — a dismissal is a
   form ending early, so R14 read literally advances the sequence. **My
   recommendation: the slot ends.** A viewer who dismissed one ad being handed
   the next one is a worse experience than no ad, and it is also what
   "dismissal" means to a viewer. **Open** — this is the one with the most
   revenue in it, and it is Nicolás's call.
2. **Which carrier reports it?** R6 (in-band callback events, line 944) or R13
   (ADS-directed callbacks, line 983). This overlaps the WG's own open item O2,
   where the tracking signal for a skipped break is unresolved. **Settled: we
   define our side and offer it to the WG, as with O5** — we have a modelled
   tracking carrier and the SVTA side does not.
3. **Is eligibility gated?** A timer ("as long as you've seen this for 5
   seconds"), a premium tier. David named these as market behaviour, not spec.
   **Settled: out of the requirement**, mentioned as non-normative context at
   most.

---

## D-7 — The carrier: query string, not HTTP header

Annex I defines **two output modes**: *"Query parameters: parameters are written
as key-value pairs in HTTP GET requests issued by the DASH Client"* and *"HTTP
header: parameters are written as a list of key-value pairs in a DASH-specific
HTTP header"*. Which one applies is decided per element by `@header` — *"specifies
the name of the HTTP header to which the final query string will be written. If
absent, the output is written into a query parameter."* So this is a real choice
the new requirement has to make rather than inherit.

**Recommendation: the query string as the default, with the header admissible.**
This is a weaker claim than an earlier reading of it supported — see below.

**The argument against the header is weaker than it first looked, and the reason
matters.** It rested on silent stripping destroying the distinction between *"the
Player understood and withheld"* (a sentinel) and *"the Player did not
understand"* (`<null>`) — a distinction that only exists in the Annex I design.
Under a Player-initiated set following CMCD, an absent value is simply **omitted**
and carries no signal, so a stripped header destroys nothing that was being
said. The objection was contingent on a design we are no longer taking, and it
does not survive the change.

What survives is smaller and still real: in a browser, a custom header on a
cross-origin request triggers a **CORS preflight**, an extra round trip on a
request that runs against the earliest-resolution-time budget. The resolution
request is latency-sensitive by construction.

**And the precedent does both.** CMCD defines a query argument
(`CMCD=<URL-encoded key-value pairs>`) *and* four `CMCD-*` request headers, with
the transport selectable by configuration. So the precedent does not settle this
either — it shows both are workable.

**The obvious argument against the query string was examined and does not
hold.** Putting capability values in the URL puts them in the cache key, which
would normally cost CDN hit rate. It does not bite here: the resolution request
in this project's own reference already carries a session identifier
(`05-dash-linear-interfaces.md:186`), so it is unique per session and its cache
key is already maximally fragmented; the APS resolves a per-viewer ad decision,
which is not cacheable in the first place; and the added cardinality is small —
decoder count takes two or three values, a format capability is binary. What
remains is a smaller, real residue: values in the URL appear in proxy and access
logs.

**They can coexist** — `finalQueryString` concatenates across hierarchy levels,
so different levels may use different modes; the either/or is per element.

## X-1 — Numbering. Settled: the number is taken at execution, not at proposal

The state that made this a blocker:

| Number | Status when raised |
|---|---|
| R28 | Highest **landed** requirement in `context/03-requirements.md`. |
| R29 | Proposed by phase `03-custom-layout`. Not executed. |
| R30 | Proposed by phase `04-multiview`. Not executed. |
| UC-13 | Proposed by **both** phases as "next free UC number". Highest landed is UC-12. |

**The rule:** a number named in an unexecuted phase's plan is a placeholder,
never a reservation. Whoever lands text in `context/` first takes the next free
identifier; the remaining phases re-read the then-current `context/` when their
turn comes. Once landed, a number is stable and never changes — that part was
already the convention (`context/03-requirements.md`, lines 66–73); this rule
governs only the moment of allocation.

**Applied:**

- The rule is written in one place, `.project/PROJECT.md`, under *"Requirement
  and use-case numbering across phases"*.
- Both phases' plans point at it instead of fixing an integer:
  `03-custom-layout/T-01-PLAN.md` (the R29 line, the UC line, the Numbering
  bullet) and its `TASKS.md`; `04-multiview/T-01-PLAN.md` (the R30 line, the
  Numbering bullet) and its `TASKS.md`.

**Allocated so far: R29 and R30.** R29 is taken by the Player
capability-parameter requirement and R30 by the empty-resolution requirement,
both landed in `context/03-requirements.md` on 2026-09-14. R30 is the rule
working exactly as written: A8's viewer-dismissal requirement was the one queued
for that number, but it is blocked on the Working Group, and a number is never
held for an item that has not landed — so the empty-resolution requirement, which
was ready, took it.

**R31, R32 and R33 are now taken as well**, by the pause opportunity window,
the exhausted-pause-candidates rule and the pause-delivery metric, all landed
in `context/03-requirements.md` on 2026-09-16. **R34 is free**: the next
requirement to land takes it, whichever item it comes from, and phases
`03-custom-layout` and `04-multiview` re-read `context/` when they execute,
which is what the rule exists for.

**UC-13 is taken** by the Player-declared-capabilities case, which landed in
`context/04-use-cases.md`. Phases `03-custom-layout` and `04-multiview` both
named UC-13 in their unexecuted plans; per the rule, neither held it, and both
re-read `context/` when they execute. **UC-14 is free.**

Worth knowing: both phases already said *"final number fixed at execution"* in
their own words, so the collision was softer than the risk register read it. What
was missing was a central statement and the removal of the bare integers that
read as claims. Phase 05 now takes its A8 requirement number at the moment that
text lands.

## Findings outside this scope (reported, not fixed)

- **The `<UrlParamInfo>` element name is a recorded decision, not a defect.**
  `output/v6.1-sgai-spec.md:148–160` documents the schema-vs-prose split inside
  DASH 6th and states: *"This specification follows the §I.3.1 prose name
  `<UrlParamInfo>`. Implementers using a strict schema validator should expect
  the alternate names in DASH-6th-conformant tooling."* Retrieval against the
  ISO text surfaces the other side of that same split — *"the scheme uses a
  single element, **RequestParam** of type ExtendedUrlInfoType"*, with Table I.3
  listing `ExtUrlQueryInfo` / `ExtHttpHeaderInfo` / `RequestParam`. **Nothing
  here needs fixing**; changing the name would revert a decision taken with more
  information than a retrieval window gives.
- **What does not resolve, and needs the PDF: which clause holds which name.**
  Our note places `<UrlParamInfo>` in §I.3.1 prose and `<RequestParam>` in the
  §5.3 semantic tables; the retrieved text puts `RequestParam` in the I.3 prose
  and in Table I.3. Separately,
  `context/05-dash-linear-interfaces.md` cites **§I.4** for the descriptor at
  lines 115, 167, 185 and 251, while the retrieved text puts the descriptor's
  semantics at **I.3.2 / Table I.3** and uses I.4 for the state variables.
  Clause numbers differ between sources for the same material — the two
  retrievals in this round disagreed with each other on 5.16.2 vs 5.16.6.1 — so
  **this is not correctable without reading the PDF**, and it is recorded as a
  question rather than a defect.
- **`context-analysis/dash-gap-analysis.md` is stale on the UC range.** Lines 29
  and 284 both say `UC-01..UC-10`; the set has been `UC-01..UC-12` since UC-11 /
  UC-12 landed. It is a regenerable artefact, so the fix is a rebuild, not an
  edit — but it will silently under-cover two use cases until someone rebuilds it.
- **`.project/PROJECT.md` describes a layout that no longer matches the repo.**
  Its table (line 114) points at `analysis/dash-gap-analysis.md` and (line 116)
  describes `output/` filenames as `YYYY-MM-DD-sgai-spec.md`; the current layout
  is `context-analysis/` and `vN-sgai-spec.md` per `CLAUDE.md`. Navigational
  drift, not content.

---

## Appendix — Annex I state variables, as drafting input

Needed only when the new requirement is written: the names already taken, and
the sentinel convention each one follows. **Table I.5 — "DASH URL parameter
schema", clause I.4.2 — has 9 rows and two columns, `Suffix` and
`Description`.** The sentinel values are stated inside the descriptions; there is
no sentinel column.

| Suffix | Carries | Sentinel stated in its description |
|---|---|---|
| `audio` | `@codecs` + `@bandwidth` of the **currently playing** audio Representation | none |
| `video` | `@codecs` + `@bandwidth` of the **currently playing** video Representation; for simultaneous decoding (e.g. scalable video), base layer first, then dependent layers | none |
| `lang#[audio\|text]` | `@lang` of the currently playing Representation | `"und"` if not known |
| `encryption` | Protection scheme per ISO/IEC 23001-7 §10 (`nenc`, `cenc`, `cbcs`, `cas`) | none — `"nenc"` is the value for unencrypted content, not an unknown-marker |
| `cmcd#[key]` | Current value of a reserved CTA-5004 key | none |
| `execution-delta#[id]` | PRTA − PRT for the event with that `@id` (§5.16.6.1), fractional seconds | `"0"` when not known or not used |
| `expected-duration#[id]` | APDA of the Alternative MPD event with that `@id` (§5.16.6) | `"-1"` when not known or not used |
| `execution-count#[id]` | Times the event with that `@id` executed (counter `c` in the T table, §5.16.6.2.2) | `"-1"` when not known or not used |
| `previous-state` | Playback type before the current playhead position (`normal` / `ff` / `rw` / `listen`) | `"normal"`, which doubles as the unknown value |

Five of the nine declare their own unknown-marker in prose; the other four fall
back to the empty-string substitution of Tables I.1 / I.2.

`audio` and `video` are the pair that look like device capability and are not —
see the body of D-6.

Separately, Tables I.1 / I.2 / I.4 define substitution tokens that are **not**
state variables: `$$` (a literal `$`), `$querypart$` (the whole raw query
string), `$query:<param>$` (one parameter of the initial query string, `""` when
absent) and `$header:<header-name>$`, which **reads** the latest received value
of an HTTP *response* header named by `@headerParamSource` and uses it as a
substitution source. It is a value source, not an outgoing carrier.

**Confidence: the list is closed.** Three queries. The first was unseeded and
returned seven of the nine. The second was seeded with the nine names and is
therefore worthless as evidence of completeness on its own — it could only echo
what it was given. The third was unseeded again, asked for a verbatim
transcription, and explicitly invited a row the asker did not know about; it
returned these same nine, with the column headings and the clause number. A
tenth row would have surfaced there. Before any of this is quoted normatively in
the spec, still read Table I.5 in the ISO text directly.

## Open findings, recorded so they are not rediscovered

Three observations surfaced while reviewing `context/05-dash-linear-interfaces.md`
and were deliberately left alone. They are the same family — the document
describes what the APS does internally, which R18 declares this spec does not
define — and they are probably one short item some day, not three.

- **The `<Ad>` (Wrapper) row** says the wrapper chain is *"resolved
  recursively"*. That is APS behaviour, not a DASH-side target. It prescribes
  nothing, so it is weaker than the `<Error>` row was, but it is the same kind
  of statement.
- **The section heading** states that the VAST-to-ListMPD transformation *"is
  the central responsibility of the APS on linear SGAI integrations"*. True, and
  simultaneously the one thing the spec says about something it declares it does
  not define.
- **The document describes practice but never says "informative".** It opens as
  *"the **reference** for how SGAI is implemented today"* and presents the
  mapping *"that an APS performs in production"*, which is framing in substance;
  no sentence marks it non-normative. A reader auditing for normative force has
  to infer it.

## A method rule, proposed and NOT in force

Written for Nicolás to approve or correct; it has deliberately **not** been
applied anywhere, and it is recorded here only so the next person finds it
instead of rediscovering it.

> **When an idea is removed from a document, the sweep is by the idea and across
> every file — not by the phrase, in the file that was edited.** The same premise
> appears written differently elsewhere, and searching for the words just deleted
> only finds the ones whose location was already known.
>
> **And a negative is not asserted without a control.** Before saying "it appears
> nowhere", the same search must find a pattern known to be present. If it does
> not, the zero is not a result — it is a broken instrument.

**The three instances it was drawn from**, which is why it is stated as two rules
rather than one:

1. A publish to a NATS subject with no subscriber returns success, so the send
   tool's return value was mistaken for an acknowledgement. It looked like
   verification and could not fail.
2. A query seeded with the nine names it was asked to confirm returned those
   nine names. It could only echo what it was given.
3. A search for a deleted phrase, in the file it was deleted from, reported that
   the idea appeared nowhere. It appeared in five other places.

All three have the shape of a check that could not come back negative.

## A phase shape, proposed and NOT in force

Recorded next to the method rule above, for the same reason and with the same
status: it has not been applied, and adopting it is Nicolás's call.

> **When the person who decides is available, emitting a list of tasks and then
> executing it is a step that buys nothing.** Each item is decided and applied in
> the same pass, and the list is written at the end as the record of what
> happened. **When that person is not available, the list has to come first** —
> it is what lets the work proceed without them.

This phase is the evidence for both halves. It opened planning to emit a task per
proposed change and decide them one at a time; what actually happened is that
every item was put to Nicolás, decided and applied in the same sitting, and the
tasks were written afterwards (T-06..T-13 in `TASKS.md`). Nothing was lost by
inverting the order, because the control the list was there to provide — no edit
without its own decision — was satisfied by the decision itself being present.

The reason this is worth writing down rather than repeating by habit is that the
two halves fail differently. Emitting the list when the decider is present costs
a round trip and delays nothing else. Skipping the list when the decider is
absent means the work cannot proceed at all.

## Verification — `context/` untouched as of 2026-09-14, before any edit landed

**A dated record, not the current state.** It proves that while this document was
being written `context/` had not been touched. The edits of T-06..T-13 landed
afterwards, so five of the nine hashes below no longer match the working tree —
`02-actors.md`, `03-requirements.md`, `04-use-cases.md`,
`05-dash-linear-interfaces.md` and `99-glossary.md`. That is the decisions being
applied, not a discrepancy to investigate.

Baseline taken before any reading, checked after all of it, and the check itself
tested by breaking it on purpose.

```
$ find context -type f | sort | xargs sha256sum > /dev/shm/.../context.sha256
5acd57247afce136164ff3904bc49c0a3de8ffdb957c39e834a0dc152d9be668  context/01-intro.md
dba88293953fc64eafa6ba3384f9115b5763c5d1ccb1d85a8419fc3597346f25  context/02-actors.md
a4ffed4cc5fe07ec3e2a0044ac236c3c1671a2cf5b697fedb3fd9f59be5846e6  context/03-requirements.md
35bbce3b7a37f8ff9aa4f0b4cc74a9841f7902ab08ce6370f86fe590317b6e72  context/04-use-cases.md
a48e799d44a292beb1d718fd642ed8cd14903fb9a4484d0f1099def0716ebfd7  context/05-dash-linear-interfaces.md
86a90cfba28092cd2f7791dddb0f4bf3c947b004310a24492f36549a6b51b57a  context/06-naming-and-namespaces.md
3b33d50dc7bc9e0fe2043f9ed2cc420e79fd5123be72515d2749f4d582717b00  context/07-backward-compat-checklist.md
dd68d6b87ad04097d42e8a334bf52a3369f3e2f7c90c6c25f90ac1011d659908  context/08-dash-extension-rules.md
9379a48cb17deb02a38558f089f52ada0fc62c181f741af1c1e03ee2632c83a9  context/99-glossary.md
```

**Negative test** — the check is only worth something if it can go red:

```
$ echo "PROBE" >> context/01-intro.md && sha256sum -c .../context.sha256
context/01-intro.md: FAILED
... (8 OK)
sha256sum: WARNING: 1 computed checksum did NOT match
exit=1

$ git checkout -- context/01-intro.md && sha256sum -c .../context.sha256
... (9 OK)
exit=0
```

**Final state** — re-checked after all reading and after writing this file:

```
$ sha256sum -c .../context.sha256
context/01-intro.md: OK
context/02-actors.md: OK
context/03-requirements.md: OK
context/04-use-cases.md: OK
context/05-dash-linear-interfaces.md: OK
context/06-naming-and-namespaces.md: OK
context/07-backward-compat-checklist.md: OK
context/08-dash-extension-rules.md: OK
context/99-glossary.md: OK
exit=0
```
