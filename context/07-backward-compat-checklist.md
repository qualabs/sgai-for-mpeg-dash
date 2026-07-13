# Backward-compat checklist

R1 demands that legacy Players (those that predate this proposal)
ignore any new construct cleanly, without crashing or producing
visible artefacts. This document is the **checklist the spec MUST
follow** for every new construct it introduces, so the
ignore-if-unknown guarantee is auditable per construct rather than
left to a generic claim.

The checklist is context-side: it does not enumerate the constructs
themselves (those live in the spec output). It defines the
verification procedure the spec's chapter 4 (Conformance) and
chapter 10 (Test cases) MUST apply.

## Per-construct checklist

For each new construct C the spec introduces, the spec MUST
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
the ignore-if-unknown rule for C's placement. The construct's
chapter MUST name the applicable DR-N rule from
[`08-dash-extension-rules.md`](./08-dash-extension-rules.md).

- For new XML elements under known parents: §5.2.1 foreign-
  namespace open content (DR-2). Legacy clients discard the
  element together with its full subtree (DR-3) — verify the
  walk-through in step 3 against this discard semantic, not
  against a "descend and read known children" semantic.
- For new attributes on known elements: typically the
  ignore-unknown-attribute rule.
- For new namespaces: standard XML namespace rules apply, but
  the construct MUST be in an extension namespace per
  [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md).
- For new event schemes: the `Event` `schemeIdUri`
  ignore-if-unknown rule (the Player skips events whose scheme
  it does not implement).
- For constructs invoking Annex F (DR-4): the chapter MUST
  state which new Interoperability Point URI is being published
  in `MPD@profiles`, and justify why §5.2.1 / §5.10 / §5.8.4.x
  (DR-6 carriers) are not sufficient.

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
- The expected behaviour: silent skip of C + no tracking beacon for
  C. The legacy Player MUST ignore C in every case; this is the
  invariant the test verifies.
- What the viewer experiences around the skipped C is
  **content-dependent** and is the Publisher's authoring choice, not a
  property of C (see UC-07 in
  [`04-use-cases.md`](./04-use-cases.md)): for **live** content the
  primary content continues uninterrupted (the opportunity is an
  expected loss on legacy Players); for **non-live / VOD** content the
  Publisher MAY author a standard linear break — using only baseline
  constructs a legacy Player renders — alongside C, in which case the
  legacy Player skips C and plays the standard break. The standard
  break is itself a baseline construct, so it is out of scope of C's
  per-construct skip test; the test still asserts only that C is
  skipped silently.
- Pass criteria: C is skipped silently; no errors logged at FATAL
  level; observable playback continues (either the primary content for
  live, or the Publisher-authored standard break for VOD).

### 6. Namespace policy

Verify that C is in one of the namespaces declared by the current
namespace policy in
[`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md).
Constructs introduced by this spec live under the SVTA Ads WG
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

### 8. Carrier classification

For each new construct C, classify its carrier against DR-6 in
[`08-dash-extension-rules.md`](./08-dash-extension-rules.md):

- **(a) Foreign-namespace open content** (§5.2.1) — a new element
  in `urn:svta:dash:sgai:<year>` carrying the asset URL as an
  attribute.
- **(b) Event Stream payload** (§5.10) — an `<Event>` whose
  `text()` carries an inline payload.
- **(c) Vendor descriptor scheme** (§5.8.4.8 / §5.8.4.9) — a
  scheme URI with `@value` carrying the payload string.

Constructs not fitting (a) / (b) / (c) MUST justify why Annex F
(DR-4) is invoked and what new Interoperability Point URI is
published. The classification MUST be stated explicitly in the
construct's chapter — leaving it implicit is a checklist failure.

## Aggregated audit table

The spec SHOULD ship with an audit table summarising the checklist
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
- Placing a non-MP4 `@mimeType` on an AdaptationSet or
  Representation reached via `<ImportedMPD>` (violates DR-1) or
  inside a ListMPD-level Period (violates DR-5). Non-AV ad assets
  MUST be carried via one of the DR-6 carriers.
- Wrapping a non-MP4 payload in an `application/mp4` Representation
  solely to satisfy the RFC 4337 registry. The wrapper does not
  add DASH segment-delivery semantics for the underlying format
  (those are an Annex F exercise per DR-4) — the construction is
  a workaround that fails the spirit of R1.2 and DR-6.

## References

- [`03-requirements.md`](./03-requirements.md) — R1 (the
  obligation this checklist verifies).
- [`04-use-cases.md`](./04-use-cases.md) — UC-07 (the legacy
  Player scenario the checklist's step 5 models on).
- [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md)
  — namespace and URI versioning policy.
