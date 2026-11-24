# Tasks — reference-player

| id   | brief                                                                                         | status  | who   | plan | evidence |
| ---- | --------------------------------------------------------------------------------------------- | ------- | ----- | ---- | -------- |
| T-01 | Se sabe si el lineal (insert y replace) sale con el módulo sobre el dash.js fijado             | done | agent | —    | `reference-player/spike/`, `tasks/T-01/`        |
| T-02 | Un test de conducta tiene esquema, población y hash, y un check que lo juzga                   | done | agent | —    | `bin/check-behaviour.py`, `bin/test_check_behaviour.py`, `spec-source/behaviour/`, `tasks/T-02/`        |
| T-03 | El harness corre un vector con el adaptador `sgai` y compara lo observado con lo esperado      | done | agent | —    | `reference-player/src/`, `bin/players/adapters/sgai.js`, `bin/players/behaviour.mjs`, `bin/conformance/behaviour*.py`, `tasks/T-03/`        |
| T-04 | Los 61 criterios observables tienen su test, escrito del texto y visto fallar                  | done | agent | —    | `spec-source/behaviour/`, `tasks/T-04/`        |
| T-05 | La referencia ejecuta el lineal de la 6ta que piden los criterios y los vectores               | in-progress | agent | —    | —        |
| T-06 | La referencia resuelve y elige: pedido, validación, opciones, perfil de clase, fallback, cap   | in-progress | agent | —    | —        |
| T-07 | La referencia presenta el no lineal: overlay, squeezeback con sus tokens, pausa, convivencia   | in-progress | agent | —    | —        |
| T-08 | La referencia dispara el tracking: callbacks, beacons de opción, click                         | pending | agent | —    | —        |
| T-09 | La batería corrió entera, con su tiempo medido y cada FAIL clasificado                         | pending | agent | —    | —        |
| T-10 | La suite de `bin/` cubre lo nuevo y prueba que nada corre la batería por defecto               | in-progress | agent | —    | —        |
| T-11 | Hay una demo: página local y grabación de una sesión con lineal, overlay y pausa               | pending | agent | —    | —        |
| T-12 | Cierre: REPORT.md (Mode D), LOG y validador                                                   | pending | agent | —    | —        |

Lo común a todas: las decisiones están en `PHASE.md` y en las ADR 0075 a 0087.
El código de la referencia va en `reference-player/`; el del ejecutor y los
checks, en `bin/`, con exits `0/1/2/64` y un `--help` que dice qué cubre su
verde y qué no. `context/` y `dist/` no se tocan, y de `spec-source/` sólo
`behaviour/` y `scenarios/schema.json` (si una task necesita más, se frena y se
avisa). dash.js se usa como está fijado en `bin/players/package.json`. Nada se
pushea. Los temporales van a `$XDG_RUNTIME_DIR/cto/`; los servers y browsers se
bajan por el PID que se guardó. La copia primaria de la norma está fuera del
repo y no entra a él: se citan oraciones, nunca páginas.

---

## T-01 — Se sabe si el lineal sale con el módulo

- **Objective:** hay una respuesta medida a si un módulo que usa sólo la API
  pública de dash.js 5.3.0 puede ejecutar un `InsertPresentation` (el principal
  se detiene y vuelve al mismo punto) y un `ReplacePresentation` (el reloj del
  principal sigue y se vuelve a PRT + duración). Decide si ADR 0075 se sostiene.
- **What it must cover:** un spike en `reference-player/spike/` con dos
  `MediaPlayer` sobre dos `<video>`, contenido de `ffmpeg` corto, y la
  semántica de §5.16 citada contra la copia primaria. Entradas: `bin/players/`
  (harness, `run.mjs`, adaptador de dash.js), `bin/conformance/players.py` (el
  server de medios), `spec-source/examples/` (los MPD con eventos
  alternativeMPD). Sin dependencias.
- **Definition of done:** para insert y replace, la posición del principal
  antes y después medida contra la esperada, con la salida en
  `tasks/T-01/`; y la conclusión: alcanza, o qué no alcanza y por qué. Si no
  alcanza, se avisa al líder antes de seguir (cambia el plan).
- **nivel de verificación:** mínimo. Su salida es una decisión que lee una
  persona; el código del spike no se adopta tal cual.

## T-02 — Esquema, población y hash de los tests de conducta

- **Objective:** un test de conducta es un archivo que un check puede juzgar:
  forma, criterio, hash, y la población completa cubierta.
- **What it must cover:** extender `spec-source/scenarios/schema.json` con
  `criterion`, `criterion_sha256`, `aps`, `actions` y `geometry` (ADR 0077),
  sin romper los 22 vectores de UC. La población, leída de
  `bin/conformance/spec/catalog.py` (ADR 0078): los criterios con parte de
  nivel 3 que no es sólo 3a (hoy 76). `spec-source/behaviour/index.yaml` con
  los `NOT_VERIFIABLE` y su motivo (los 7 sin carrier y los 8 no decidibles,
  `DESIGN.md` "Lo medido"). El hash, el de `criteria.py` importado. El check
  (extender `bin/check-scenarios.py` o uno nuevo que lo importe) sale `1` si
  un criterio de la población no tiene test ni entrada, o un test nombra uno
  de afuera; `2` si un hash no coincide o el criterio se retiró. Sin Chromium.
- **Definition of done:** el check corre sobre `spec-source/behaviour/` y sobre
  `scenarios/` y da lo esperado; visto fallar con un test sin criterio, un hash
  cambiado y un criterio sin cubrir.
- **nivel de verificación:** alto. Es el check que dice si la batería está
  completa, y corre sin que nadie lo mire.

## T-03 — El harness corre un vector con el adaptador `sgai`

- **Objective:** dado un vector (de UC o de criterio) y una clase, el harness
  lo carga en la referencia, lo observa y dice PASS, FAIL o `NOT_VERIFIABLE`
  por cada cosa esperada.
- **What it must cover:** `bin/players/adapters/sgai.js` (ADR 0081), el APS y
  los beacons como `page.route` (ADR 0079), las `actions` del viewer, el
  perfil de clase (ADR 0080), la observación (pedidos con parámetros y tiempo
  de sesión, beacons, presentación, geometría) y la comparación en Python con
  `tolerance`. `check-dash-conformance.py --behaviour` como única entrada
  (ADR 0087), con concurrencia. Entradas: `bin/players/run.mjs`,
  `bin/conformance/players.py`, `spec-source/scenarios/README.md`. Depende de
  T-01 y T-02.
- **Definition of done:** UC-01 corre de punta a punta en D1 y da un veredicto
  por cada campo esperado; un vector con un valor esperado cambiado a mano da
  FAIL nombrando el campo.
- **nivel de verificación:** alto. Decide PASS o FAIL sin mirada humana.

## T-04 — Los tests de los 61 criterios

- **Objective:** cada uno de los 61 criterios observables tiene al menos un
  test, escrito del texto del criterio, que falla contra la referencia sin la
  familia que lo implementa (ADR 0085).
- **What it must cover:** lo cargado (fixtures de `spec-source/examples/` o
  nuevos en `spec-source/behaviour/fixtures/`, `aps`, `actions`, clase), lo
  observado y lo esperado, cada uno citando su criterio. Los de borde que
  ningún UC toca (R4.9, R4.10, R30.2, R34.10, entre otros). Se escribe por
  familia, antes de T-05 a T-08 según corresponda. Depende de T-02 y T-03.
- **Definition of done:** el check de T-02 sale `0` con la población entera
  cubierta; cada test se vio fallar antes de su familia, con la salida en
  `tasks/T-04/`.
- **nivel de verificación:** alto. Es lo que dice si la referencia cumple.

## T-05 — El lineal de la 6ta

- **Objective:** la referencia ejecuta insert y replace, la cola por PRT con
  `@executeOnce`, `@maxDuration`, `@clip`, `@earliestResolutionTimeOffset` y
  `@startWithOffset`, la List MPD con sus `ImportedMPD`, y los callbacks de los
  MPD de aviso (ADR 0083).
- **What it must cover:** cada construcción citada contra la copia primaria al
  implementarla. Lo que no usan los criterios ni los vectores queda afuera
  (SCTE-35, encadenamiento, xlink). Depende de T-01 y de los tests lineales de
  T-04.
- **Definition of done:** los tests de los 13 criterios lineales y los vectores
  de UC lineales pasan, o el FAIL que queda está clasificado.
- **nivel de verificación:** alto. El tiempo de vuelta al principal es un
  número que nadie ve pasar.

## T-06 — Resolución y selección

- **Objective:** la referencia arma el pedido de resolución con sus
  parámetros, valida los candidatos, elige opción por capacidad y layout según
  el perfil de clase, sigue la cadena de fallback y aplica el cap.
- **What it must cover:** R2.3, R4.x, R5.x, R7.1, R15.3, R20.x, R29.2, R29.4,
  R30.2, R32.x, R34.x, R36.x, R38.2, R39.x y los demás de esta familia en
  `index.yaml`. Depende de T-03 y de los tests de T-04.
- **Definition of done:** los tests de la familia pasan, o el FAIL que queda
  está clasificado.
- **nivel de verificación:** alto. Elegir mal una opción o cortar mal el cap
  no se ve en pantalla.

## T-07 — Presentación no lineal

- **Objective:** la referencia dibuja overlay y squeezeback con cada token de
  layout donde R12.5 dice, presenta la pausa, y hace convivir las familias
  (R16, R17, R19, R21, R22, R25, R26, R27, R35, R37, R40).
- **What it must cover:** la capa DOM sobre el `<video>`, el escalado del
  principal en squeezeback, el fondo y las bandas negras, la pausa en vivo
  congelada. Depende de T-05 (convivencia con el lineal) y de los tests de
  T-04.
- **Definition of done:** los tests de la familia pasan, incluidos los de
  geometría, o el FAIL que queda está clasificado; una captura por token en
  `tasks/T-07/`.
- **nivel de verificación:** alto. La parte visual se ve, pero los tiempos de
  suspensión y reanudación entre familias no, y son la parte riesgosa.

## T-08 — Tracking

- **Objective:** la referencia dispara los beacons de callback en su tiempo,
  los de opción sólo para la opción presentada, ninguno después del fin del
  aviso, y el click con su tracking (R6.4, R6.5, R13.1, R13.3, R13.6, R28.1,
  R28.2).
- **What it must cover:** el alcance de `@id` por candidato y en la List MPD.
  Depende de T-05, T-07 y de los tests de T-04.
- **Definition of done:** los tests de la familia pasan, o el FAIL que queda
  está clasificado.
- **nivel de verificación:** alto. Un beacon de más o de menos es plata mal
  contada y no se ve.

## T-09 — La batería entera

- **Objective:** la batería corrió completa (los tests de criterio y los 110
  resultados de UC), se sabe cuánto tarda con concurrencia, y cada FAIL dice si
  es de la referencia o de la spec (ADR 0082).
- **What it must cover:** el tiempo en serie estimado contra el medido con
  concurrencia; los inestables, corridos tres veces y reportados como tales.
  Un hueco de la spec es un hallazgo para el líder, no un cambio. Depende de
  T-05 a T-08.
- **Definition of done:** `tasks/T-09/battery.md` con la salida, el tiempo y
  la clasificación de cada FAIL.
- **nivel de verificación:** alto. Es la medición que el cierre reporta.

## T-10 — Tests de `bin/` y el opt-in

- **Objective:** lo nuevo de `bin/` tiene tests que corren sin Chromium, y un
  test prueba que ningún camino por defecto corre la batería (ADR 0087).
- **What it must cover:** el check de T-02, la comparación de T-03, con
  negativos. El test de opt-in arma cada camino por defecto
  (`check-dash-conformance.py` sin flag, `promote.py`, los orquestadores
  `build-all` e incremental leídos por lo que invocan, y la suite misma) y
  falla si alguno llama al ejecutor de la batería; se lo ve fallar agregando
  la llamada. Depende de T-02 y T-03.
- **Definition of done:** la suite `bin/test_*.py` entera verde, y el test de
  opt-in visto en rojo una vez.
- **nivel de verificación:** alto. Es el test que defiende la condición del
  líder.

## T-11 — Demo

- **Objective:** existe una página local que reproduce con la referencia una
  sesión con lineal, overlay y pausa, y su grabación (ADR 0086).
- **What it must cover:** la sesión sale de un vector de UC; la grabación con
  Playwright, en `tasks/T-11/`. No se publica afuera. Depende de T-05 a T-08.
- **Definition of done:** la grabación muestra las tres familias en una
  sesión.
- **nivel de verificación:** bajo. Es una interfaz que una persona mira.

## T-12 — Cierre: REPORT.md (Mode D), LOG y validador

- **Objective:** la fase está cerrada con su REPORT, y el líder sabe qué quedó
  y cuánto tarda la batería.
- **What it must cover:** corre cuando todas las demás están `done` o
  `abandoned`. Revisa `CLAUDE.md`, `README.md`, `SETUP.md` y los README de
  `bin/players/` y `spec-source/scenarios/` por lo que la fase cambió.
- **Definition of done:** `REPORT.md` con `closed:`, LOG, validador en verde.
- **nivel de verificación:** mínimo. Lo lee una persona.
