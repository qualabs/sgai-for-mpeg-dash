# Scenario vectors

One file per use case of `context/04-use-cases.md`: `UC-NN.yaml`, valid
against `schema.json` (ADR 0064). A vector states what a Player of each
device class is observed to do on that use case's documents: what it
requests, what it selects, what is on screen and when, which beacons fire.
The executor will be the reference Player of the next phase, on the Player
harness of `bin/players/`; until it exists every outcome is
`NOT_VERIFIABLE — no executor`.

`UC-01.yaml` (linear, Annex A) and `UC-03.yaml` (non-linear, with a variant,
missing carriers and a disagreement, Annex C) are the worked examples. Copy
the shape of the closer one.

```bash
python3 bin/check-scenarios.py                    # the whole check (exit 0/1/2/64, --json)
python3 bin/check-scenarios.py section UC-NN      # the UC's text, with its uc_sha256 on line 1
```

## Where each value comes from

| Field | Read from |
|---|---|
| `uc`, `uc_sha256` | `check-scenarios.py section UC-NN`, line 1. Never by hand |
| expected behaviour (`selection`, what `presentation` shows, `summary`) | `context/04`, the UC's `#### Dk` sub-sections, or its Coverage-table row and prose when it has none |
| documents, ids, URLs, times | the annex that walks the UC: its fixtures in `../examples/<annex>/` and its walk-through / timing sections (`bin/spec-section.py get C.6 C.7`) |
| `player_capabilities` | R3.1 of `context/03` for the first three axes (the check enforces the row); `sgai-custom-layout` and `sgai-ad-audio` as the UC needs (`0` when it says nothing) |
| `sends_capabilities` | what the annex's request fixture sends; `[]` when it declares nothing |

The annexes match the use cases by title: A UC-01, B UC-02, C UC-03, D UC-04,
E UC-05, F UC-06, G UC-07, H UC-08, I UC-09, J UC-10, K UC-11, L UC-12, M UC-13,
N UC-14, O UC-15, P UC-16, Q UC-17. UC-18 to UC-22 have no annex: write their
documents as new fixtures in `fixtures/UC-NN/`, each with its `class` in the
vector (the classes of `../examples/index.yaml`), and the check runs levels 1
and 2 on them as on the examples. Do not add them to `../examples/`.

Which classes need an outcome is decided by the check, from `context/04`:
the UC's `#### D1`..`#### D5` headings plus every non-"—" cell of its
Coverage row; `legacy` when the section has a `**Legacy Player**` entry. An
outcome for a class the UC does not state is a finding.

## The fields

- **Times** are integers in `1/timescale` s on the **session clock**:
  wall-clock time since playback was started, pauses included. Not the main
  presentation's timeline, which stands still during a linear insertion and
  a pause; each `primary` element carries `from`, the main presentation time
  it shows at the segment's start, so that timeline can be read back. Where
  the source gives a window instead of an instant (a request "from 270 s",
  a fetch "before it plays"), write `{from, to}`. `tolerance` is how far an
  executor may observe an exact time from the written one.
- **`play_from`, `observe_until`**: where playback starts in the main
  presentation, and when observation ends. End a little after the last
  thing the UC is about, not at the end of the content.
- **`fixtures`**: every document the Player is given or fetches, as paths
  under `spec-source/`; `url` is where the harness serves it, copied from
  the document that points to it. Media (segments, images, HTML) are not
  fixtures and their requests are not recorded; the chosen option says which
  was used. `entry` is the main MPD.
- **`requests`**: the document requests, in order: `url` as the pointing
  document writes it, `query` the parameters the Player adds,
  `answered_by` the fixture served, `matches` the `.http` fixture this
  request equals when the annex has one.
- **`selection`**: per opportunity (the main MPD's `Event@id`), `presented`
  (each candidate and option the Player presents, in order, with its
  layout), `declined` (it had the document and presented nothing), or
  `ignored` (a legacy Player that does not recognise the event).
  Candidates and options by `id` when the document has one, else by
  `index`, 1-based document order. `option: null` for a linear candidate.
- **`presentation`**: segments that tile `[0, observe_until]` in order, no
  gap, no overlap; each says the `layout` (an R12.2 token, `none` for the
  primary alone) and what `shows`. `region` and `note` are free text for a
  person; the executor compares `layout` and the elements.
- **`beacons`**: every beacon fired, with its time, its fixture and `@id`,
  `candidate` when the `@id` is scoped by the candidate, and its `url`
  (checked against the event's text).
- **`actions`** and **`variants`**: viewer actions (`pause`, `resume`,
  `seek` with `to`, `dismiss`, `activate`, `rate` with `rate`). The main run
  is `outcomes` with `actions`. A second run the UC or its annex states
  (a dismissal, a seek) is a variant with its own actions and outcomes for
  the classes where it applies.

## What the UC needs and the spec cannot carry: `missing_carrier`

When the UC requires something for which the specification defines no
syntax yet (the v13 list: audio R41, beacons of occurrence R42, slot beacons
R13.7, R23.2, R44, R47, R48), add an entry with the requirement, what is
missing, and the classes (and the `variant`, if it is one). **Do not invent
syntax** and do not write an outcome for it: no beacon without an `@id` in a
fixture, no attribute the fixtures do not have. Record what is observable
without it (UC-03 records `audio: primary` and the beacons that stop on a
dismissal, and marks the dismissal beacon as missing).

## When the annex and context/04 disagree: `disagreements`

Record it: what `context/04` says (quoted, with the sub-section), what the
annex says (quoted, with its section), and which one the outcomes follow.
**Do not resolve it**, in the vector or anywhere else: the disagreement is
the finding, and resolving it is a `context/` or spec change for the project
lead. Follow the annex in the outcomes when it is the one with concrete
documents, and say so. A difference that is not observable in the outcome
(UC-01's pre-buffer) is recorded the same way.

## Checking it

`check-scenarios.py` exits 1 while UCs lack vectors; the findings that name
your UC must be none. Run `python3 bin/test_check_scenarios.py` if you touch
the check. `--help` lists every check and what a green does not say.
