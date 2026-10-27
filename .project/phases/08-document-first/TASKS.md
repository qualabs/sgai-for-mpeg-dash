# Tasks — document-first

| id   | brief                                                                                     | status  | who   | plan | evidence |
| ---- | ----------------------------------------------------------------------------------------- | ------- | ----- | ---- | -------- |
| T-01 | El mapa de obligaciones queda congelado y legible por script, criterios y prosa            | done    | agent | —    | `tasks/T-01/obligation-map.tsv`, `tasks/T-01/build-map.py` |
| T-02 | 03 está reescrito según el mapa, con la regla, el índice de interfaces y los retirados     | done    | agent | —    | `tasks/T-02/notes.md` |
| T-03 | Un check en `bin/` hace cumplir la parte estructural de la regla, como Step 0.7            | planned | agent | —    | —        |
| T-04 | Las pruebas del check: cada una de sus cinco condiciones, rota a propósito, sale en rojo   | planned | agent | —    | —        |
| T-05 | La versión nueva conserva cada obligación de la vieja, y `context/` cierra                 | planned | agent | —    | —        |

---

## T-01 — El mapa de obligaciones queda congelado y legible por script
- **Objective:** existe un mapa, en `tasks/T-01/`, que dice para cada unidad
  de `context/03-requirements.md` (los 199 criterios y las 32 unidades de
  prosa que lista `check-promotable.py --population`) qué acción tiene y dónde
  queda su contenido, sobre un commit nombrado. T-02 lo aplica, T-03 toma de
  ahí el commit de referencia y T-05 lo usa para emparejar cada obligación
  vieja con su lugar nuevo.
- **What it must cover:** empezar por `DESIGN.md`, Anexo A (A.2, A.3, A.4 y
  A.5). Primero, `git diff 44cfff4..HEAD -- context/03-requirements.md`: si no
  es vacío, el mapa se rehace sobre el commit nuevo y se avisa al coordinador
  antes de seguir. Los criterios salen de A.2 y A.3; las unidades de prosa no
  están mapeadas una por una en el diseño, y esta tarea lo hace: cada modal de
  la prosa queda en la prosa o sube a un criterio (A.5 y R33, D-3). Formato
  tabular (`id`, `kind`, `acción`, `destino`), un destino por id o la lista
  cuando son dos (R4.3, R34.5). El script que lo arma aborta si falta o sobra
  un id frente a la población. No toca `context/`.
- **Definition of done:** el mapa y su script están en `tasks/T-01/`, el
  script corre limpio (`missing [] extra []`, 199 criterios y 32 prosa, con
  los conteos de A.1) y sale en rojo con un id borrado a propósito; el commit
  de referencia está escrito en el mapa.
- **nivel de verificación:** alto. Es la referencia contra la que T-05 valida:
  un destino mal puesto hace que T-05 busque la obligación en el lugar
  equivocado y la dé por perdida, o peor, por encontrada.

## T-02 — 03 está reescrito según el mapa
- **Objective:** en `context/03-requirements.md` cada elemento de las tres
  interfaces tiene su significado escrito una vez, en un criterio del lado del
  documento y con la fuerza de la obligación que absorbió; un criterio del
  Player queda sólo donde dice algo que esa semántica no alcanza; y nada de lo
  que 04 y 99 citan apunta a un id que ya no existe.
- **What it must cover:** leer primero `PHASE.md`, el mapa de T-01 y las ADR
  0029 a 0043. 03 según el mapa, requerimiento por requerimiento, con los
  criterios del documento primero dentro de cada uno (ADR 0032). La regla de
  escritura con el texto de la ADR 0034, la sección "Interfaces" (una tabla
  por interfaz, elemento → id, sin semántica, con los 76 elementos de A.7 y una
  fila para cada uno) y la tabla "Retired identifiers" (los 37 ids, con su
  destino). Las decisiones de contenido: ADR 0040 (R29.1 en dos tablas con los
  tres nombres), 0041 (MUST en R13.1), 0042 (double-box en R12.5 y R26.1) y
  0043 (ClickThrough en R28). Las garantías de la ADR 0031 (R28.2, R42.3,
  R47.2) y R20.5/R20.6 sin cambios. Las notas de privacidad según D-3 (la de
  R29.2 a R29.1; la de R47.2 se queda). Las 12 referencias internas de 03,
  las 24 de 04 y las 2 de 99, al id destino; en 04 y 99 no cambia ninguna otra
  palabra. La línea del `CLAUDE.md` del proyecto (ADR 0034). Una ambigüedad de
  fondo nueva va a `tasks/T-02/questions.md` y no se resuelve. Restricciones:
  no tocar 02, 05, 06, 07, 08 ni las ADRs; no renumerar ni mover
  requerimientos. Depende de T-01.
- **Definition of done:** 03 tiene la regla, el índice y la tabla de
  retirados; ningún id retirado aparece fuera de esa tabla en `context/`
  (`grep` por cada uno, con un control positivo); `check-context-coherence`
  sale `0` o su único rojo es el de los ids retirados que T-03 resuelve; un
  commit con `context/` y el `CLAUDE.md`, sin push.
- **nivel de verificación:** alto. Es la entrada normativa del build v13, y
  una obligación perdida no se ve hasta la spec. La verificación de fondo es
  T-05, que la hace otro agente.

## T-03 — Un check hace cumplir la parte estructural de la regla
- **Objective:** `bin/check-context-interfaces.py` sale en rojo cuando el
  índice de interfaces apunta a un criterio que no existe, repite un elemento,
  apunta a un criterio cuyo rol es el Player, cuando se cita un id retirado
  fuera de su tabla, o cuando falta en 03 un id del commit de referencia que la
  tabla de retirados no lista; y `build-all` lo corre antes de producir nada.
- **What it must cover:** ADR 0035 (qué detecta y qué no puede detectar). Las
  salidas de los otros checks de `bin/` (`0`, `1`, `2`, `64`, con `--help` que
  las dice) y la línea de lo que su verde cubre y no cubre, como
  `check-context-coherence.py`. El commit de referencia, como constante, el de
  T-01. Step 0.7 en `prompts/build-all.prompt`, después de 0.6, y su
  descripción en el párrafo de `bin/` del `CLAUDE.md` del proyecto. En
  `bin/check-context-coherence.py`, que un id de la tabla de retirados cuente
  como conocido. Sin aviso heurístico sobre criterios del Player (descartado
  en la ADR 0035). Depende de T-02 (el formato del índice y de la tabla).
- **Definition of done:** el check sale `0` sobre el 03 de T-02 y
  `check-context-coherence` también; Step 0.7 está en `build-all`; commit
  local.
- **nivel de verificación:** alto. Corre sin nadie mirando en cada build, y un
  check que no falla da un verde que no dice nada. Las pruebas son T-04.

## T-04 — Las pruebas del check
- **Objective:** cada una de las cinco condiciones del check, rota a propósito
  sobre una copia de 03, lo pone en rojo con su mensaje, y el 03 real lo deja
  en verde; lo mismo para el cambio en `check-context-coherence`.
- **What it must cover:** tests versionados junto a los checks (seguir cómo
  están probados los otros de `bin/`, si lo están; si no, un archivo de test
  propio en `bin/`). Una rotura por condición, corriendo sólo el test que la
  cubre: una fila que apunta a un id inexistente, un elemento en dos filas o
  dos interfaces, una fila que apunta a un criterio `(Player)`, un id retirado
  citado en 04, un id del commit de referencia que falta y no está en la tabla.
  Más el `2` (no hay índice o no hay tabla) y el `64`. Depende de T-03.
- **Definition of done:** los tests corren y pasan, cada rotura se vio en rojo
  con su salida pegada en la evidencia, y ninguna quedó verde.
- **nivel de verificación:** alto. Es la campaña de mutación del check: una
  rotura que queda verde es un hallazgo, no un pase.

## T-05 — La versión nueva conserva cada obligación de la vieja
- **Objective:** está mostrado, par por par, que cada obligación de la versión
  vieja de 03 está en su lugar nuevo con la misma fuerza (salvo los tres
  cambios que el diseño decidió), que 04 y 99 sólo cambiaron ids, que no quedan
  dobles, que las tres interfaces están completas y que `context/` cierra.
- **What it must cover:** lo hace un agente que no hizo T-02. Lee `PHASE.md`,
  el mapa de T-01 y las ADR 0029 a 0043, y compara el commit anterior a T-02
  con el de T-02/T-03. (1) Un script lista los pares (modal viejo de cada
  unidad, criterio o prosa → texto del lugar nuevo según el mapa); el
  validador los lee y juzga cada uno, el script no. Prueba del instrumento:
  se borra a propósito una obligación del texto nuevo en una copia y el
  validador la encuentra. Cambios aceptados sólo en su lugar: R6.2 de SHOULD a
  MUST en R13.1 (ADR 0041), los nombres de R29.1 (ADR 0040), la URL de destino
  en R28 (ADR 0043), los tokens de double-box en R12.5 y R26.1 (ADR
  0042), y la frase de R1.4 sobre el candidato abortado (LOG del
  2026-10-27), y las dos citas de UC-10 que pasan a R5.6 en lugar de R5.3
  (decisión del coordinador: R5.7 estaba mal citado ahí). Los apartamientos
  del mapa están en `tasks/T-02/notes.md`.
  (2) El diff de 04 y de 99 con los ids viejos reemplazados
  por su destino es vacío; se admite colapsar un id repetido que la
  sustitución deja ("R5.1 / R5.1") y, en 99, sólo las entradas que
  `check-context-vocabulary` pida para términos nuevos de T-02, listadas.
  Prueba: una palabra cambiada a propósito en un caso de uso lo deja no vacío.
  (3) Los dobles uno por uno: los 9 redundantes, los 14 parciales y los 6
  grupos de `output-analysis/v12.6-requirements-redundancy-review.md`, y los
  pares de R34 (R34.2 y R34.5 con R34.1, R34.7 con R34.6, R34.8 con R34.9).
  (4) Los 76 elementos de A.7 tienen fila en el índice, y los 6 sin definición
  la tienen. (5) `check-context-coherence`, `check-context-vocabulary` y
  `check-context-interfaces` en `0`, cada uno visto en rojo a propósito. (6) La
  población de `check-promotable.py --population`, vieja y nueva, con la
  diferencia explicada por el mapa. Depende de T-02, T-03 y T-04.
- **Definition of done:** un informe en `tasks/T-05/` con los seis puntos, la
  salida de cada comando pegada, cero obligaciones perdidas o cada pérdida
  devuelta y corregida en T-02 (con `post-ejecución`), y los tres chequeos en
  `0` sobre el commit final.
- **nivel de verificación:** alto. Es la única protección de la reescritura:
  ningún build la mira (D-12), y un "está todo" de un instrumento que no se vio
  fallar no vale.
