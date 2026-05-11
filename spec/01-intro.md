# SGAI for Linear and Non-Linear Ads in MPEG-DASH 6th Edition

This document set specifies SGAI (Server-Guided Ad Insertion) for
**both linear and non-linear ads** in MPEG-DASH, extending the SGAI
primitives introduced in **MPEG-DASH 6th edition** for linear ads
(`InsertPresentation`, `ReplacePresentation`, `ListMPD`) and adding the
constructs required to cover non-linear ads — overlays, side-by-side,
pause ads, L-shapes, banners, fullscreen interactive layers — under
the same architecture.

The documents in this folder are the canonical, self-contained
statement of the proposal: the actor model, the requirements that
govern any candidate design, the use cases that any candidate design
must satisfy (linear and non-linear), and the gap analysis that
compares the status quo of MPEG-DASH 6th edition against those use
cases. This folder is consumed both by the working doc shared with
industry (Comcast, SVTA Ads WG, MPEG-DASH contributors) and by the
internal Qualabs WG that iterates the spec and the prototype.

The project-level context (goals, stakeholders, standards, phases,
open threads) lives in [`../.project/PROJECT.md`](../.project/PROJECT.md).
This folder stays focused on the technical content.

## Document index

- **[02-actors.md](./02-actors.md)** — Three-actor model
  (Broadcaster / ADS / Player). Bounded responsibilities and the
  Player as the enforcer of the Broadcaster's policy.
- **[03-requirements.md](./03-requirements.md)** — Functional and
  governance requirements R1–R10, out-of-scope items, and design
  characteristics that satisfy the Rs.
- **[04-use-cases.md](./04-use-cases.md)** — Device classes D1–D5
  and the seven scenarios UC-01..UC-07 (pre-roll, mid-roll,
  coexisting overlay, hybrid linear + overlay, pause-triggered ad,
  multi-ad break, legacy Player encountering new constructs). Each
  scenario is described once with per-device-class expected
  behavior.
- **[05-dash-linear-interfaces.md](./05-dash-linear-interfaces.md)** —
  Reference for how SGAI is implemented today for linear ads in
  MPEG-DASH 6th edition (FDIS ISO/IEC 23009-1:2025). Inventories the
  three-actor interfaces, walks the end-to-end message flow with
  concrete MPD and ListMPD examples, and lays out the VAST → ListMPD
  adapter mapping.
- **[06-naming-and-namespaces.md](./06-naming-and-namespaces.md)** —
  Naming conventions for new constructs (URN patterns, namespaces,
  versioning) and pointer to the canonical layout vocabulary.
- **[07-error-semantics.md](./07-error-semantics.md)** — Error
  conditions matrix and Player obligations, derived from R1..R7.
- **[08-backward-compat-checklist.md](./08-backward-compat-checklist.md)** —
  Verification checklist that the norm MUST apply to each new
  construct it introduces, so legacy Player compatibility (R1 /
  UC-07) is auditable per construct.
- **[99-glossary.md](./99-glossary.md)** — Technical terminology used
  across the document set.

The gap analysis that maps each UC against MPEG-DASH 6th edition
constructs lives outside this folder, at
[`../analysis/dash-gap-analysis.md`](../analysis/dash-gap-analysis.md).
It is a generated artefact derived from this spec, not part of the
canonical reading set.
