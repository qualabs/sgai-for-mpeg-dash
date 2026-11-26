# Tasks — reference-player-fixes

| id   | brief                                                                                     | status  | who   | plan | evidence |
| ---- | ----------------------------------------------------------------------------------------- | ------- | ----- | ---- | -------- |
| T-01 | `context/` dice lo que el líder decidió en N-1 a N-11, con las citas y hashes al día       | pending | agent | —    | —        |
| T-02 | Cada decisión tiene el test o vector que la cubre, visto fallar                           | pending | agent | —    | —        |
| T-03 | La referencia toma la lectura decidida en cada punto                                       | pending | agent | —    | —        |
| T-04 | Los `[DISCUSSION]` para el WG están escritos, listos para publicar                         | pending | agent | —    | —        |
| T-05 | La clase legacy es el dash.js fijado con el lineal de la 6ta                               | pending | agent | —    | —        |
| T-06 | Los vectores mal escritos dicen lo que dicta el texto                                     | pending | agent | —    | —        |
| T-07 | El formato dice capacidades por clase y, si N-10 sale A, la presentación alternativa       | pending | agent | —    | —        |
| T-08 | Los 3 jobs inestables dan el mismo veredicto cargados que solos                           | pending | agent | —    | —        |
| T-09 | La batería entera corrió una vez, con el antes y el después                               | pending | agent | —    | —        |
| T-10 | Cierre: REPORT.md (Mode D), LOG y validador                                               | pending | agent | —    | —        |

Lo común a todas: las decisiones están en `PHASE.md`, en `DESIGN.md` (N-1 a
N-11 con la opción que eligió el líder, D-1 a D-6) y en sus ADR. La batería es
opt-in (ADR 0087) y se verifica 100% por código: sin capturas; el runner
devuelve un resumen y el detalle va a archivo. Cada subagente toma una familia,
no una task entera, y lee de este archivo sólo el bloque de su task.
`spec-source/sgai-spec.src.md`, `output/` y `dist/` no se tocan. Un commit por
cambio, nada se pushea. Temporales en `$XDG_RUNTIME_DIR/cto/`, los grandes en
`~/.cache/cto-tmp/`; lo que se levanta se baja por su PID. La copia primaria de
la 6ta no entra al repo: se citan oraciones.

---

## T-01 — `context/` dice lo decidido

- **Objective:** cada decisión N-1 a N-11 que cambia `context/` está escrita
  ahí, y nada de lo que lee `context/` quedó desfasado.
- **What it must cover:** la opción elegida de cada N (en `DESIGN.md`), en
  `context/03` (lecturas del Player bajo R1.5, filas de "Deliberately open",
  R4.5 a "Retired identifiers" si N-4 sale A) o `context/04` (UC-07 si N-11
  sale B). En el mismo commit: las oraciones citadas por las reglas de
  `bin/conformance/spec/` y los `criterion_sha256` de los tests y vectores del
  criterio tocado. Las N que no cambian `context/` (N-10 A) no van acá.
  Restricciones: `context/` sigue autocontenido (CLAUDE.md); ninguna regla en
  `context/05`, que es informativo. Sin dependencias.
- **Definition of done:** un commit por decisión con el porqué en el mensaje;
  después de cada uno, los gates `check-normative-base`,
  `check-context-coherence`, `check-context-vocabulary`,
  `check-context-interfaces`, `check-behaviour.py`, `check-scenarios.py` y
  `check-dash-conformance.py --source spec-source` dan lo mismo que antes
  salvo lo que la decisión explica (salida antes/después en `tasks/T-01/`).
- **nivel de verificación:** alto. Es la premisa del v13: un texto mal
  escrito acá se construye entero arriba.

## T-02 — Un test por decisión

- **Objective:** cada decisión que obliga a un Player tiene un test de
  conducta o un vector que la juzga, y se lo vio fallar.
- **What it must cover:** N-1 (rectángulos por token en R12.5-1/R27.1), N-2
  (pedido de la ventana de pausa, lo que se ve mientras tanto, la cota de
  retención), N-3 (beacon en el borde, seek interno), N-5 (E2 pasa a
  `spec-source/behaviour/`), N-6 (callback en el fin del Period), N-7, N-9
  (UC-14 con la demora del principal), según la opción elegida. Esquema en
  `spec-source/behaviour/README.md`. Depende de T-01.
- **Definition of done:** cada test nuevo o cambiado falla contra la
  referencia anterior o contra una mutación que viola la lectura, y pasa con
  la referencia de T-03; `check-behaviour.py` en 0. Salidas en `tasks/T-02/`.
- **nivel de verificación:** alto. Un test que no puede fallar aprueba
  cualquier Player.

## T-03 — La referencia sigue lo decidido

- **Objective:** la referencia implementa la lectura elegida en cada punto, y
  su cabecera dice cuál.
- **What it must cover:** N-2 (si sale B o C, `preResolvePause`), N-7 (A:
  PRTA = PRT por cruce, sin el parche de `sgai-linear.js:789`), N-9 (A: el
  slate en su borde menos la demora del principal), N-1 (B: geometría),
  N-3 (B), N-10 (A: la marca neutra), según lo elegido. Entradas:
  `reference-player/src/`, sus vectores de borde E1–E18. Depende de T-02 (los
  tests se ven fallar antes, ADR 0085).
- **Definition of done:** los tests de T-02 pasan; E1–E18 pasan; los jobs de
  los criterios que tocó cada cambio dan el mismo veredicto que antes o mejor.
- **nivel de verificación:** alto. Es el juez de la batería.

## T-04 — Borradores `[DISCUSSION]`

- **Objective:** cada punto de la 6ta que el líder mandó al WG (según N-5,
  N-6, N-8, N-9, N-10) tiene su issue escrito, listo para que él lo publique.
- **What it must cover:** la cláusula y la oración citadas, el problema, el
  vector de borde o el FAIL que lo muestra, y la lectura que toma nuestra
  spec; el marcador `<!-- sgai-issues: ours -->` al final (D15). En inglés.
  Sin datos de la copia primaria fuera de la oración citada. Depende de T-01.
- **Definition of done:** un archivo por issue en `tasks/T-04/`; ninguno
  publicado.
- **nivel de verificación:** mínimo. Lo lee el líder antes de que salga.

## T-05 — Legacy es un Player de la 6ta

- **Objective:** la clase `legacy` de la batería hace el lineal de la 6ta e
  ignora la extensión, como dice el glosario, y sus 18 FAIL dejan de medir al
  instrumento.
- **What it must cover:** D-1. El modo `legacy` del adaptador
  (`bin/players/adapters/sgai.js`) carga el esqueleto y `sgai-linear.js` con
  todo lo `svta` ignorado; si `sgai-linear.js` mezcla conducta `svta`, se
  separa con un interruptor, sin cambiar la conducta del modo `sgai`. Los
  jobs: UC-07 legacy ×2, UC-11, UC-14, UC-17, UC-22 `legacy`. El nivel 3a
  (`--players`) no cambia. Sin dependencias.
- **Definition of done:** los 6 jobs legacy en PASS; una mutación que carga la
  familia no lineal en legacy da FAIL en UC-11 legacy; una que quita el lineal
  da FAIL en los 6; la muestra de regresión del modo `sgai` igual que en T-09.
  ADR de D-1.
- **nivel de verificación:** alto. Cambia qué mide toda una clase.

## T-06 — Vectores mal escritos

- **Objective:** los vectores dicen lo que dicta el texto, y los 29
  NOT_VERIFIABLE por oportunidad ambigua se pueden juzgar.
- **What it must cover:** D-3. UC-08 D1–D4 (`mid` en 75 000), UC-11 D1–D5 (los
  beacons de ClickThrough), el `scheme` de las oportunidades de UC-07, 08, 11 y
  17. Cada valor citando la línea de `context/04` o del anexo que lo dicta.
  Sin dependencias.
- **Definition of done:** los jobs tocados sin esos FAIL ni esos
  NOT_VERIFIABLE, y cada vector viejo visto fallar o quedar NOT_VERIFIABLE por
  lo que se corrigió; `check-scenarios.py` en 0.
- **nivel de verificación:** alto. Un vector escrito sobre la conducta de la
  referencia la aprueba por definición.

## T-07 — Formato por clase y presentación alternativa

- **Objective:** el formato puede decir lo que un UC pide por clase, y, si
  N-10 sale A, una presentación alternativa que no es candidato.
- **What it must cover:** D-2: `sends_capabilities` por clase (UC-13 D3/D4) y
  la capacidad de sesión del perfil de clase (UC-19 D1), en
  `spec-source/scenarios/schema.json`, `check-scenarios.py`,
  `bin/conformance/behaviour*.py`. N-10 A: `element: alternative` en esquema,
  adaptador, comparador; UC-14 y R40.6 reescritos. Compatibilidad con los
  vectores que no lo usan. Depende de T-01 para N-10.
- **Definition of done:** los 3 jobs de D-2 y los 11 de N-10 sin esos FAIL; los
  tests de `bin/` del formato con su negativo; la suite de `bin/` en 0.
- **nivel de verificación:** alto. Es el instrumento con que se juzga todo.

## T-08 — Sin inestables

- **Objective:** R40.3-2 D1, R28.1-1 D1 [no-activation] y UC-12 D1 dan el mismo
  veredicto con la máquina cargada que solos.
- **What it must cover:** D-4. Reproducir el FAIL (`--cpu-throttle N`, o carga
  propia bajada por su PID), encontrar dónde entra tiempo de pared en el reloj
  de presentación o en la referencia, y arreglarlo ahí. No se ensancha la
  tolerancia. Sin dependencias.
- **Definition of done:** con la condición que reproducía el FAIL sobre HEAD,
  los 3 jobs en PASS 3 de 3; un atraso real de 1 s inyectado sigue dando FAIL;
  la muestra de regresión igual.
- **nivel de verificación:** alto. Un reloj que perdona demasiado esconde
  atrasos reales.

## T-09 — La batería entera

- **Objective:** hay una medición de la batería entera sobre el código final,
  comparable con la de la fase 11.
- **What it must cover:** D-6: máquina sin carga ajena, concurrencia 2,
  `uptime` al inicio y al final; cada FAIL clasificado (referencia, test,
  norma, inestable) y lo inestable re-corrido solo dos veces. Depende de T-01
  a T-08.
- **Definition of done:** `tasks/T-09/battery.md` con los totales antes y
  después y cada FAIL clasificado; cero FAIL de la referencia.
- **nivel de verificación:** alto. Es la medición que dice si la batería ya
  sirve de juicio.

## T-10 — Cierre

- **Objective:** la fase cerrada con su REPORT, y `major-build-v13` sabe lo que
  recibe.
- **What it must cover:** corre cuando las demás están `done` o `abandoned`.
  Mode D de `create-project`; la lista para el v13 (Y-1 a Y-5 y los tests que
  esperan su carrier).
- **Definition of done:** `REPORT.md` con `closed:`, entrada en `LOG.md`,
  validador sin rojos nuevos.
- **nivel de verificación:** mínimo. Lo lee el líder.
