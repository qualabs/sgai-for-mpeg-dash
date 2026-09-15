# Proposed: UC-13 and the UC-09 scope line

**Status: PROPOSED — not applied.** `context/` is untouched by this
document; the verification is at the end. Four pieces, to be applied
together or not at all: they are one change, and applying a subset
leaves the spec asserting something it does not mean.

Origin: the use-case review of 2026-09-15. Findings 3 (R29 has no
scenario) and 5 (UC-09 asserts a division of labour that R5 and R29
made optional) are one piece of work, because the mitigation phase 05
wrote for T-05 requires that both cases be edited together so neither
reads as canonical.

---

## Piece 1 — UC-13, new, to be appended after UC-09

### UC-13 — One ad, Player-declared capabilities, resolved by the APS to a single option

**Scenario:** The same single non-linear ad candidate as UC-09 is
presented for an overlay slot, with the same four presentation options
available at the ADS and the same device-agnostic allowed-layout set
declared by the Publisher. What differs is where the capability check
is resolved: the Player attaches its declared capability parameters to
the resolution request (R29), and the APS resolves against them,
emitting a resolution document whose candidate carries **exactly one**
presentation option — the one the APS computed as renderable on that
device. The Player renders that option, or skips the candidate when its
own check fails (R5.3).

UC-09 shows the same ad with the Player disclosing nothing and the APS
emitting the full ordered list. The two cases exercise R5 differently
and neither is canonical; the D4 row below is this same APS behaving as
UC-09 describes, because that is what a Player that declares nothing
leaves it able to do.

**Publisher intent:**
- Non-linear forms allowed.
- The same single **device-agnostic** allowed-layout set as UC-09 —
  side-by-side, L-shape / squeezeback, banner overlay, and full-screen
  takeover. The Publisher declares no per-device-class variant.
- Maximum slot / overlay duration is bounded (R4).

**Ad response:**
- The ADS's decision carries the same four presentation options as
  UC-09, in the same order:
  1. **Side-by-side / double-box with a video ad + advertiser
     background** — two concurrent video decoders plus an image surface
     for the background element (R26, R26.3).
  2. **L-shape / squeezeback with an image full-frame ad creative** —
     one video decoder for the shrunk primary content plus one image
     surface for the full-frame creative (R27, R27.3).
  3. **Image banner overlay** — one video decoder plus an image overlay
     surface.
  4. **Full-screen takeover video** — one video decoder reused across
     ad and primary content; no overlay surface, no concurrent
     composition.
- The APS emits a resolution document per resolution request. Where the
  request carried capability parameters, the APS omits the options
  those parameters rule out and emits the first surviving option alone;
  where the request carried none, it emits all four. In both directions
  the options the APS does emit carry the order the ADS gave them,
  without reordering (R5.1).
- The parameters carry **capability axes** — how many video decoders
  the device can run concurrently, and what kinds of surface it can
  composite on top of video — and it is the APS that derives from them
  which presentation option can be served (R29.1).

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** declares its full capability set on the
  resolution request — two or more concurrent video decoders, image and
  HTML surfaces over video. The APS finds option 1 satisfiable on that
  declaration and emits it alone. The Player checks the option it
  received against its own capability and the Publisher's allowed
  layouts (R5.6), it passes, and the Player renders it.
- **What the user sees:** the primary content shrinks into one box, the
  ad video plays in the other, and the advertiser's background image
  fills the bands around them. The same rendered result as UC-09 on D1.

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** declares two concurrent video decoders and **no
  non-video compositing surface**. The APS rules out option 1 on its
  third element — the background is an image element D2 cannot
  composite (R26.3) — and options 2 and 3 for the same reason, both
  needing an image surface. Option 4 survives on a single decoder
  reused sequentially, and the APS emits it alone. The Player checks it
  and renders it.
- **What the user sees:** a full-screen video ad of bounded duration,
  after which the primary content resumes. The same rendered result as
  UC-09 on D2.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** declares one video decoder and an image surface,
  and **omits** the HTML-surface axis, whose value it cannot determine
  when it issues the request. It omits that parameter entirely rather
  than sending it empty or with a placeholder (R29.3). The APS treats
  the omitted axis as undetermined — neither present nor absent — and
  therefore emits no option that depends on it. Option 1 needs a second
  decoder and is ruled out; option 2 needs one decoder plus one image
  surface, depends on no undetermined axis, and survives. The APS emits
  it alone; the Player checks it and renders it.
- **What the user sees:** the primary content shrinks into one region
  and the image ad creative occupies the full frame behind it, the
  visible band of the creative forming the "L". The same rendered
  result as UC-09 on D3.

#### D4 — Single-decoder, image only

- **Player decision:** declares **nothing**. Sending a reserved
  parameter is optional, and a conformant Player may send none (R29.2).
  The APS receives no device information and must still produce
  candidates (R29.5), so it narrows nothing and emits all four options
  in the ADS's order — the resolution document UC-09 describes. The
  Player walks them in document order (R5.2 / R5.6): option 1 needs a
  second decoder and fails; option 2 needs one decoder plus one image
  surface, which D4 has. The Player renders option 2 and stops walking.
- **What the user sees:** the same as D3 — the primary content shrinks
  into one region with the image ad creative full-frame behind it. The
  same rendered result as UC-09 on D4.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** declares one video decoder and **no overlay
  surface of any kind**. The APS rules out options 1, 2 and 3, each of
  which needs a surface D5 lacks. Option 4 survives — one decoder
  reused sequentially, no overlay surface — and the APS emits it alone.
  The Player checks it and renders it.
- **What the user sees:** a full-screen video ad of bounded duration,
  after which the primary content resumes. The same rendered result as
  UC-09 on D5.

**What this demonstrates:** every device class lands on the rendered
result it lands on in UC-09 — D1 on the side-by-side, D2 and D5 on the
full-screen takeover, D3 and D4 on the L-shape — from the same ad, the
same four options and the same Publisher declaration. What moved is
where the capability check was resolved: in UC-09 the APS emits every
option and each Player selects among them; here each Player declares
and the APS selects. The viewer-visible outcome is identical, which is
what makes these two divisions of one responsibility rather than two
behaviours to choose between.

D4 is where that stops being incidental. A Player that declares nothing
leaves the APS unable to narrow, and an APS that cannot narrow emits
the full ordered list — so the document UC-09 describes is what this
same APS produces when it is told nothing. UC-09 is not a different
design reached by a different route; it is this one, addressed by a
silent Player.

**Notes:**
- **Declaring does not delegate the Player's check.** No presentation
  option reaches the screen without passing the Player's own capability
  check (R5), and that holds for an option the APS computed from the
  Player's own declaration. If the device's state changed between the
  request and the render, or the APS derived the wrong option, the
  Player skips the candidate and falls through (R5.3 / R5.7).
  Declaring narrows what arrives; it does not make what arrives
  authoritative.
- **A single option does not require a declaration.** R5 admits a
  candidate carrying exactly one option whether or not anything was
  declared: an APS that wants the choice to sit with it sends one, and
  the Player renders it or skips the candidate. What a declaration
  changes is the basis on which the APS chose that option, not what the
  Player does with it.
- **The capability axes are named here in prose.** Which parameters the
  reserved set contains, and how each is written, is fixed when the
  syntax is specified (R29.1). A use case that named them would fix
  them early and would age against a decision that has not been taken.

---

## Piece 2 — the UC-09 addition

**Insertion point:** `context/04-use-cases.md`, UC-09, at the end of
the `**Scenario:**` paragraph, immediately after the existing sentence
*"This use case is the worked example of that emergence."*

**Nothing already written in UC-09 is changed.** Its claims are scoped
to its own scenario and are true — line 984 already reads *"in this
scenario neither the ADS nor the APS holds a view of the device"*. What
is missing is not a correction but a statement that the other division
exists; without it a reader closes that this one is the only one. The
edit is purely additive.

> In this scenario the Player discloses nothing about its device on the
> resolution request, so no actor upstream of it holds a device view.
> R5 admits the other division of labour equally: UC-13 shows the same
> ad, with the same options, resolved by an APS that received the
> Player's declared capabilities (R29) and emitted a single option —
> and every device class lands on the same rendered result. Neither
> case is canonical; they exercise R5 differently.

## Piece 3 — the Coverage table row

`context/04-use-cases.md`, the **Coverage** table, immediately after
the existing `UC-09` row (same `Worked example` category):

```
| UC-13 One ad, Player-declared capabilities, APS resolves to one option | Worked example | side-by-side — option 1, emitted alone | full-screen takeover — option 4, emitted alone (non-video surfaces declared absent) | L-shape — option 2, emitted alone (HTML axis omitted, not relied on) | L-shape — option 2, after walking the full list it received (declared nothing) | full-screen takeover — option 4, emitted alone (no overlay surface) |
```

Without this row a coverage audit finds UC-13 orphaned from the
navigational table that claims to list every scenario.

## Piece 4 — record that UC-13 is taken

`.project/phases/05-wg-feedback-round-2/context-change-recommendations.md`,
§X-1, the *"Allocated so far"* paragraph. It currently records R29 and
R30 as allocated and R31 as free, and says nothing about UC numbers
while §X-1's own table still lists UC-13 as *"proposed by both phases;
highest landed is UC-12"*.

Proposed addition to that paragraph:

> **UC-13 is taken** by the Player-declared-capabilities case, which
> lands in `context/04-use-cases.md`. Phases `03-custom-layout` and
> `04-multiview` both named UC-13 in their unexecuted plans; per the
> rule, neither held it, and both re-read `context/` when they execute.
> **UC-14 is free.**

The rule itself stays where it is — `.project/PROJECT.md`, *"Requirement
and use-case numbering across phases"*, which is the one place it is
written. This is an allocation record, not a restatement of the rule.

---

## What this proposal deliberately does not do

- **It names no parameter.** The reserved set's contents and syntax are
  fixed when the syntax is specified (R29.1); inventing a name here
  would be the speculative construct DP-1.1 rejects.
- **It adds no attribute, label or mode selector.** Nothing in either
  case tells an implementer which division of labour to pick, because
  there is nothing to declare: the same R5 admits both, and the
  identical per-class outcomes are the demonstration.
- **It does not touch UC-04 or UC-08.** Both are waiting on David
  Hassoun and Zach Kava respectively; nothing here reaches them.
- **It does not extend UC-01 for R30.** In a single-window scenario an
  empty resolution and a failed one produce the same playback, so the
  distinction has no observable consequence there; it is observable
  only where a fallback window exists, which is UC-12.

## Verification — `context/` untouched while this was written

```
$ git status --porcelain
(no entry under context/)
```

Checked with a negative control: appending a probe line to
`context/01-intro.md` made the check report the file as modified, and
reverting it returned the check to clean.
