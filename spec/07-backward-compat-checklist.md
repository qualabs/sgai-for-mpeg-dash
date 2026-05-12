# Backward-compat checklist

R1 demands that legacy Players (those that predate this proposal)
ignore any new construct cleanly, without crashing or producing
visible artefacts. This document is the **checklist the norm MUST
follow** for every new construct it introduces, so the
ignore-if-unknown guarantee is auditable per construct rather than
left to a generic claim.

The checklist is spec-side: it does not enumerate the constructs
themselves (those live in the norm output). It defines the
verification procedure the norm's chapter 4 (Conformance) and
chapter 10 (Test cases) MUST apply.

## Per-construct checklist

For each new construct C the norm introduces, the norm MUST
explicitly answer the following questions in the construct's
specification chapter. Unanswered items SHOULD block publication.

### 1. Placement in DASH XML hierarchy

Where does C live in the document tree?

- Inside `MPD` / `Period` / `AdaptationSet` / `Representation` /
  `EventStream` / `SegmentTemplate` / ... ?
- As an attribute or as a child element?
- Required or optional in its parent?

The placement determines which DASH extension rule governs
ignore-if-unknown.

### 2. Extension point and ignore-if-unknown rule

Cite the DASH 6th edition (or successor) section that documents
the ignore-if-unknown rule for C's placement.

- For new XML elements under known parents: typically the
  open-content model rule.
- For new attributes on known elements: typically the
  ignore-unknown-attribute rule.
- For new namespaces: standard XML namespace rules apply, but
  the construct MUST be in an extension namespace per
  [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md).
- For new event schemes: the `Event` `schemeIdUri`
  ignore-if-unknown rule (the Player skips events whose scheme
  it does not implement).

### 3. Legacy Player behaviour walk-through

Step through what a legacy Player does when it encounters C:

1. Where does the parser first see C?
2. Does the parser skip C silently, or does it raise an error?
3. After skipping, does the remaining structure still parse?
4. Does playback continue with primary content uninterrupted?

This walk-through MUST be present in the construct's chapter as
an explicit prose paragraph, not implicit.

### 4. Required-sibling check

If C is mandatory for a Player that implements this proposal,
verify that:

- No legacy-required sibling element becomes inconsistent when C
  is present.
- No legacy-required attribute on the parent of C has its
  semantics changed by the presence of C.
- Removing C from the document MUST still leave a document that
  parses and plays.

### 5. Equivalent of UC-07 (legacy compatibility test)

Each new construct MUST have a corresponding test case under
chapter 10 modelled on UC-07
([`04-use-cases.md`](./04-use-cases.md)):

- A representative MPD/ListMPD containing C.
- A legacy Player implementation harness.
- The expected behaviour: silent skip + uninterrupted primary
  content + no tracking beacon for C.
- Pass criteria: observable playback continues; no errors logged
  at FATAL level.

### 6. Namespace policy

Verify that C is in one of the namespaces declared by the current
namespace policy in
[`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md).
Constructs introduced by this norm live under the SVTA Ads WG
namespace; vendor-private extensions live under the Qualabs vendor
namespace. The exact URI patterns, the year-pinning rule, and the
tracking-callback-scheme inheritance from MPEG-DASH 6th edition
are normative in `06-naming-and-namespaces.md` — this checklist
delegates to that document and does not restate the patterns,
so the two files cannot drift.

If C is in a different namespace, document why and obtain explicit
review.

### 7. Documentation cross-reference

The construct's chapter MUST link to this checklist and confirm
each item is satisfied. Reviewers SHOULD reject construct chapters
that omit the checklist confirmation.

## Aggregated audit table

The norm SHOULD ship with an audit table summarising the checklist
status for every new construct it introduces:

| Construct | Placement | Extension rule | Walk-through | Sibling check | UC-07 test | Namespace | Status |
|-----------|-----------|----------------|--------------|---------------|------------|-----------|--------|
| (per construct) | ... | ... | ... | ... | ... | ... | OK / FAIL |

A `FAIL` in any column blocks publication.

## Anti-patterns to reject

Common ways the ignore-if-unknown contract can be silently broken
— reviewers MUST flag these:

- Placing a new mandatory element in a position whose legacy
  schema declares it as a required field with no extension hook.
- Reusing an existing element name from the baseline with new
  semantics (covered separately in
  [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md)).
- Introducing a construct whose semantics implicitly depend on a
  sibling that legacy Players cannot interpret, without a
  fallback that legacy Players can execute.
- Using a scheme URI without a year suffix (covered in
  [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md)).

## References

- [`03-requirements.md`](./03-requirements.md) — R1 (the
  obligation this checklist verifies).
- [`04-use-cases.md`](./04-use-cases.md) — UC-07 (the legacy
  Player scenario the checklist's step 5 models on).
- [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md)
  — namespace and URI versioning policy.
- [`../analysis/error-semantics.md`](../analysis/error-semantics.md)
  — E9 (unknown scheme URI handling, complementary at runtime).
