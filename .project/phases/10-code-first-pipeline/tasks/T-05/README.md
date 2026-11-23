# T-05: the use cases as executable vectors (part A)

ADR 0064. Part A: the format (`spec-source/scenarios/schema.json`), the
check (`bin/check-scenarios.py`, tests `bin/test_check_scenarios.py`), two
vectors (`UC-01.yaml` on Annex A, `UC-03.yaml` on Annex C) and the brief for
part B (`spec-source/scenarios/README.md`).

## State

`check-scenarios.py` exits 1: the 20 UCs without a vector (UC-02, UC-04 to
UC-22), and nothing else. UC-01 and UC-03 have no finding; every class of
both is `NOT_VERIFIABLE — no executor`. With context/04 cut down to UC-01 and
UC-03 the check exits 0 (test `test_two_vectors_alone_exit_0`).

## Choices part B inherits

- **Times on the session clock**, not the presentation timeline the task
  named: a linear insertion and a pause both stop the main presentation's
  timeline while the screen changes, so it cannot order what is observed.
  Each `primary` element carries `from`, its main presentation time, so that
  timeline is still recoverable.
- **The classes a UC states** are its `#### Dk` headings plus the non-"—"
  cells of its Coverage row: 12 UCs have no `#### Dk` headings at all
  (UC-07, UC-11, UC-12, UC-14 to UC-22). That gives UC-19 only D1 and UC-20
  D1, D3, D4, D5. `legacy` is required on UC-14, UC-17, UC-22 (a
  `**Legacy Player**` entry).
- **R3.1 and R12.2 are read from context/03** at run time, not copied into
  the check: a capability or layout that context/03 stops admitting fails the
  vector.
- **Fixture green** means no FAIL in the levels 1 and 2 run whose subject is
  that file. The 6 FAILs of the source run today are on the subject
  `specification` (the v13 carriers), not on a fixture.

## Disagreements recorded, not resolved

- UC-01: context/04 D1 "the extra decoder … not exercised" against A.6 "the
  second decoder may pre-buffer ad 102". Not observable in the outcome.
- UC-03: context/04's double box has a still-image background element and
  needs an image surface for it (D2 has none); C.1 offers "the double box
  without background" and C.6 renders it on D2. The outcomes follow the annex.

## Findings out of scope

- `bin/spec-section.py` cannot split `context/04-use-cases.md` (exit 2:
  "section keys repeated: D1, D2, D3, D4, D5"), so `--file
  context/04-use-cases.md` does not work. `check-scenarios.py section UC-NN`
  prints one UC and its hash instead.

## Parte B (2026-11-23): los 22 vectores

Cuatro lotes en paralelo (UC-02,04–07 · UC-08–12 · UC-13–17 · UC-18–22). `bin/check-scenarios.py` → `22 vectors of 22 use cases; 0 findings`, exit 0; cada clase `NOT_VERIFIABLE — no executor`. Cada lote verificó a mano al menos un tiempo o un id por UC contra su anexo y rompió una copia para ver al checker fallar.

**Desacuerdos registrados en los vectores, no resueltos** (entradas para el v13): UC-01 (pre-buffer del 2.º decodificador), UC-02 (vuelta "near the slot" vs RT=630 s de B.5), UC-03 y UC-10 (el fondo de la double box: atributo del slot en context/04, opción en el anexo), UC-05 (sin cap vs `durationCap=60000`; D5 vs `request-again`), UC-06 (política de overflow), UC-07 (break por replacement en live), UC-14 y UC-22 (la forma en pantalla se suspende y retoma según context/04 / R40.4; termina según el anexo y PLY-49), UC-21 (ejecución tardía desde A, MUST en R34.6, MAY en §5.1.3).

**Carriers que faltan** (la lista del v13, más R13.6 en UC-09 y R34.1/R34.9 en la ventana overlay en UC-21): R41 en UC-18, R48 en UC-20, R13.7 en UC-06/21/22, R42 en UC-03.

**Lo que el formato no expresa todavía** (entrada para `reference-player`, que lo ejecuta): capacidades distintas por clase o por variante; una variante que cambie el MPD de entrada, `play_from` u `observe_until`; una resolución que falla (timeout, 503, 404 de un recurso); el clic (URL de tracking sin `@id`, destino); la acción "skip"; una oportunidad con dos `Event@id` iguales en distintos EventStreams (H.2-1, K.2-1, D.2-1, G.2-1, Q.2-1); más de un pedido en un `.http`; tiempos de beacons cruzados con `presentationTime` (hoy sólo id y URL). UC-07 tiene D1–D5 escritos como un Player legacy en ese hardware, igual que `legacy`, porque la cobertura de context/04 los pide.

**Fuera de alcance:** `bin/spec-section.py` no lee `context/04` (claves D1–D5 repetidas); el anexo L referencia `…/cr/0917/lt.mpd`, que no existe; el timing del anexo N es ambiguo ("opens one minute into the slate"); `sgai-ad-audio` y `sgai-ad-audio-allowed` están en context/03 R29.1 y no en la spec.
