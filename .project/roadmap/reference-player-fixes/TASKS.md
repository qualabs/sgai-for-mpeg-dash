# Tasks — reference-player-fixes

| id   | brief                                                                                     | status  | who   | plan | evidence |
| ---- | ----------------------------------------------------------------------------------------- | ------- | ----- | ---- | -------- |
| T-01 | `context/` dice lo que el líder decidió en N-1 a N-12, con las citas y hashes al día       | pending | agent | —    | —        |
| T-02 | Cada decisión tiene el test o vector que la cubre, visto fallar                           | pending | agent | —    | —        |
| T-03 | La referencia toma la lectura decidida en cada punto                                       | pending | agent | —    | —        |
| T-04 | La clase legacy es el dash.js fijado con el lineal de la 6ta                               | pending | agent | —    | —        |
| T-05 | Los vectores mal escritos dicen lo que dicta el texto                                     | pending | agent | —    | —        |
| T-06 | El formato dice capacidades por clase y la presentación alternativa                         | pending | agent | —    | —        |
| T-07 | Los 3 jobs inestables dan el mismo veredicto cargados que solos                           | pending | agent | —    | —        |
| T-08 | La batería entera corrió una vez, con el antes y el después                               | pending | agent | —    | —        |
| T-09 | El proyecto lee la guía IAB de la v2.0 final, fijada a un commit                          | pending | agent | —    | —        |
| T-10 | Cierre: REPORT.md (Mode D), LOG y validador                                               | pending | agent | —    | —        |

Lo común a todas: las decisiones están en `PHASE.md`, en `DESIGN.md` (N-1 a
N-11 con la opción que eligió el líder, D-1 a D-7) y en sus ADR. La batería es
opt-in (ADR 0087) y se verifica 100% por código: sin capturas; el runner
devuelve un resumen y el detalle va a archivo. Cada subagente toma una familia,
no una task entera, y lee de este archivo sólo el bloque de su task.
`spec-source/sgai-spec.src.md`, `output/` y `dist/` no se tocan. Un commit por
cambio, nada se pushea. Temporales en `$XDG_RUNTIME_DIR/cto/`, los grandes en
`~/.cache/cto-tmp/`; lo que se levanta se baja por su PID. La copia primaria de
la 6ta no entra al repo: se citan oraciones.

---

## T-01 — `context/` dice lo decidido

- **Objective:** cada decisión N-1 a N-12 que cambia `context/` está escrita
  ahí, y nada de lo que lee `context/` quedó desfasado.
- **What it must cover:** la opción elegida de cada N (en `DESIGN.md`), en
  `context/03` (lecturas del Player bajo R1.5, filas de "Deliberately open",
  R4.5 reescrito como regla defensiva, N-4) o `context/04` (UC-07 si N-11
  sale B; UC-23 nuevo con su fila de cobertura, N-4). N-5: R1.7 con su nota,
  la fila nueva de "Deliberately open" (*Decided by MPEG*, "Recorded in" la
  ADR de N-5, sin link al issue) y "three rows" pasa a "four". N-6: R1.8 con
  su nota; `context/05` no cambia. N-7: R4.12 a continuación de R4.6, con su
  "Implementation note". N-8: la "Implementation note" de las
  transiciones bajo R1.7, después de su nota; sin número ni MUST. N-9: R1.9
  (SHOULD). En el mismo commit: las oraciones citadas por las reglas de
  `bin/conformance/spec/` y los `criterion_sha256` de los tests y vectores del
  criterio tocado. Las N que no cambian `context/` (N-10) no van acá.
  Restricciones: `context/` sigue autocontenido (CLAUDE.md); ninguna regla en
  `context/05`, que es informativo. N-1 son los rectángulos de `DESIGN.md`
  (N-1), cada valor con su referencia a `v2.0.md` y la nota de que los videos
  de ejemplo son ilustrativos y que el Frame de ejemplo mide ≈ 52% contra el
  60% del texto. N-2 es el texto exacto de `DESIGN.md` (R36.1 cambia la
  última frase; R36.8 nuevo, que entra también al catálogo del nivel 2 y a
  la población de conducta). N-3 es el texto exacto de `DESIGN.md` (R13.1,
  R13.3, la frase de R34.6, R13.9 nuevo) y las cinco re-descripciones
  decididas: R13.8 sin "and when"; R13.7 eliminado (a "Retired identifiers",
  y cada referencia de la lista de N-3 en `context/03`, `04` y `06`
  corregida); R34.6 acotado a "a seek back from beyond its end"; R6.5 sin la
  regla del Player y "same URL at the same time" como criterio del APS (el
  número siguiente libre); R40.9 y la introducción de R16 remiten a R13.3.
  Las ADR 0023 y 0025 llevan una nota fechada al pie, y
  `roadmap/major-build-v13` deja de esperar el carrier de R13.7. N-12: la
  frase de cierre de la introducción de R16, R16.3 nuevo (R16.2 está
  retirado), la frase de R32.1 `repeat`, la variante `repeat` con imagen de
  UC-05 en `context/04`, y el texto de §3.1 y PLY-65 anotado en
  `roadmap/major-build-v13` como texto decidido. Depende de T-09 para N-1; el resto,
  sin dependencias.
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
  (R36.1-1 a -3 reescritos contra el texto nuevo; un test de R36.8: la pausa
  resuelta después de la pausa deja el cuadro pausado en pantalla, sin nada
  en blanco, y sin resolución a tiempo la pausa sigue sin aviso; UC-08 acepta
  el pedido al inicio de la sesión y sus tiempos de restauración se corrigen
  contra el texto), N-3 (seek atrás dentro del overlay re-despacha
  sin pedido nuevo, seek adelante dentro del rango, el negativo del borde;
  R13.3-4 sin la nota de que su lectura es del test). R13.7: fuera de
  `catalog.py`, `pins.json`, el README de escenarios y los `missing_carrier`
  de UC-06, UC-21 y UC-22. R6.5: R6.5-3 (same URL, same time) deja de ser un
  test de conducta y pasa a ser una regla de documento del nivel 2 con su
  negativo; R6.5-1 y R6.5-2 revisados contra el texto nuevo. R34.6: un test
  de seek atrás desde más allá del fin (entrada) contra uno desde adentro
  (no lo es). N-12: imagen de pausa con beacon a 2 s y el principal a 2x;
  `repeat` en dos pasadas o más, la última cortada al reanudar; secuencia de
  dos imágenes (beacons desde el render de cada aviso, `dismissAfter` desde el
  del primero); el vector de UC-05 suma su variante. N-4: `R4.5-1` (lineal) y
  `R4.5-2` (overlay) con media real de 2,2 s declarada de 2 s, vistos fallar
  con la referencia mutada (fin en el `ended` del video, `useAppendWindow:
  false`); el vector de UC-23; R4.5 sale de `behaviour/index.yaml`. Depende
  de T-06 para el fixture. N-5 (`R1.7-1`: intervalo activo
  100–130 s, aviso de 15 s, `@executeOnce="false"`; una sola ejecución y el
  principal sigue desde 100 s; seek a 90 s y se ejecuta otra vez al llegar a
  100; visto fallar con el mutante del reset literal de QE; E2 pasa a este
  test), N-6 (`R1.8-1`: un aviso de 15 s con `complete` a
  los 15 s lo dispara; visto fallar con la referencia mutada para exigir el
  instante estrictamente antes del fin), N-7 (`R4.12-1`: un aviso de 8 s arrancado con la
  latencia del loop dispara `complete` a los 8 s; visto fallar con el mutante
  M1, que lo acorta por esa latencia), N-9
  (UC-14: los campos que dependen de la alineación con `strength: should`;
  con la referencia mutada para arrancar el slate en su borde dan
  `SHOULD_NOT_MET` y no FAIL; depende de T-06), según la opción elegida. Esquema en
  `spec-source/behaviour/README.md`. Depende de T-01.
- **Definition of done:** cada test nuevo o cambiado falla contra la
  referencia anterior o contra una mutación que viola la lectura, y pasa con
  la referencia de T-03; `check-behaviour.py` en 0. Salidas en `tasks/T-02/`.
- **nivel de verificación:** alto. Un test que no puede fallar aprueba
  cualquier Player.

## T-03 — La referencia sigue lo decidido

- **Objective:** la referencia implementa la lectura elegida en cada punto, y
  su cabecera dice cuál.
- **What it must cover:** N-2 (`preResolvePause` precarga la pausa desde el
  inicio de la ventana; la cabecera de `sgai-nonlinear.js:70` deja de
  atribuirle a H.3 la otra lectura), N-7 (PRTA =
  PRT en reproducción normal, sin la tolerancia ad hoc de
  `sgai-linear.js:789`; R1.8-1 sigue en PASS), N-9 (el slate
  en su borde menos la demora del principal), N-1 (B: geometría),
  N-3 (re-despacho en un seek interno, §5.10.2.4, sin re-resolver), N-10 (la marca neutra, `data-sgai-element="alternative"`), N-12
  (el slot de pausa no avanza con el `playbackRate` del principal,
  `sgai-nonlinear.js:717`; `repeat` abre una presentación nueva por pasada,
  `:1086`), según lo elegido. Entradas:
  `reference-player/src/`, sus vectores de borde E1–E18. Depende de T-02 (los
  tests se ven fallar antes, ADR 0085).
- **Definition of done:** los tests de T-02 pasan; E1–E18 pasan; los jobs de
  los criterios que tocó cada cambio dan el mismo veredicto que antes o mejor.
- **nivel de verificación:** alto. Es el juez de la batería.

## T-04 — Legacy es un Player de la 6ta

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
  da FAIL en los 6; la muestra de regresión del modo `sgai` igual que en T-08.
  ADR de D-1.
- **nivel de verificación:** alto. Cambia qué mide toda una clase.

## T-05 — Vectores mal escritos

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

## T-06 — Formato por clase y presentación alternativa

- **Objective:** el formato puede decir lo que un UC pide por clase, y una
  presentación alternativa que no es candidato (N-10).
- **What it must cover:** N-4: un override de la duración real de los
  segmentos por fixture en la generación de media
  (`bin/conformance/players.py`, hoy `-seg_duration` igual a lo declarado y
  duración entera divisora de 32 s), y una marca en el vector de "media
  defectuosa a propósito, documento conforme", distinta de `expect_red`. N-9: la
  marca `strength: should` por campo del vector, y el veredicto
  `SHOULD_NOT_MET` del comparador, contado aparte, con su negativo (el mismo
  desvío sin la marca da FAIL). D-2: `sends_capabilities` por clase (UC-13 D3/D4) y
  la capacidad de sesión del perfil de clase (UC-19 D1), en
  `spec-source/scenarios/schema.json`, `check-scenarios.py`,
  `bin/conformance/behaviour*.py`. N-10: `element: alternative` en esquema,
  adaptador, comparador; UC-14 y R40.6 reescritos. Compatibilidad con los
  vectores que no lo usan. Sin dependencias (N-10 no cambia `context/`).
- **Definition of done:** un fixture con segmentos reales de 2,2 s
  declarados de 2 s, medido (`ffprobe` de cada segmento); los 3 jobs de D-2 y los 11 de N-10 sin esos FAIL; los
  tests de `bin/` del formato con su negativo; la suite de `bin/` en 0.
- **nivel de verificación:** alto. Es el instrumento con que se juzga todo.

## T-07 — Sin inestables

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

## T-08 — La batería entera

- **Objective:** hay una medición de la batería entera sobre el código final,
  comparable con la de la fase 11.
- **What it must cover:** D-7: máquina sin carga ajena, concurrencia 2,
  `uptime` al inicio y al final; cada FAIL clasificado (referencia, test,
  norma, inestable) y lo inestable re-corrido solo dos veces. Depende de T-01
  a T-07 y de T-09.
- **Definition of done:** `tasks/T-08/battery.md` con los totales antes y
  después y cada FAIL clasificado; cero FAIL de la referencia.
- **nivel de verificación:** alto. Es la medición que dice si la batería ya
  sirve de juicio.

## T-09 — La guía IAB v2.0 final

- **Objective:** todo lo que el proyecto toma de la guía IAB sale de la
  versión final, en un commit fijo, y se puede citar por línea.
- **What it must cover:** D-6. El prompt del paso 5
  (`prompts/1-pre-spec/analyze-iab-ad-templates.prompt`) lee `v2.0.md` del repo
  `InteractiveAdvertisingBureau/Ad-Format-Guidelines-for-Digital-Video-CTV` en
  un commit fijado (no la rama), con su skip por hash de entrada
  (`bin/step-inputs.py`) y `build-all.prompt` §Step 5 sin el "NEVER skips";
  `context-analysis/iab-ad-templates.md` regenerado. En `context/`: las citas
  de 03:789, 03:817, 03:1656, 03:1722 y `99-glossary.md:46` (buscar todas con
  `grep -rn -i "iab\|docs.google" context/`) pasan a v2.0 con fecha, commit y
  línea. Las ADR 0001, 0002 y 0004: una nota fechada al pie, sin tocar la
  prosa; si una decisión dejó de valer con la v2.0, ADR nueva que la
  supersede. `PROJECT.md` donde nombra el estándar. La guía de signaling de
  IAB y los códigos `pos` de AdCOM 1.0: buscar el término literal en todo
  `context/`, `spec-source/`, `context-analysis/` y `prompts/`, y escribir lo
  que se buscó y qué se encontró; si nuestro texto los toca, migrarlos igual.
  Sin dependencias; T-01 la necesita para N-1.
- **Definition of done:** el commit de IAB fijado en el prompt y en las
  citas; `step-inputs.py` dice que el paso 5 no tiene que correr dos veces
  seguidas con la misma entrada y sí al cambiar el commit (visto); los gates
  de `context/` en 0; `grep -rn "Dec 2025\|docs.google.com/document/d/17JX"`
  sobre `context/` y `prompts/` vacío, probado antes contra un archivo que lo
  tiene; la búsqueda de signaling y `pos` en `tasks/T-09/`.
- **nivel de verificación:** alto. Es fuente de requisitos: una cita que no
  dice lo que la v2.0 dice se construye entera en el v13.

## T-10 — Cierre

- **Objective:** la fase cerrada con su REPORT, y `major-build-v13` sabe lo que
  recibe.
- **What it must cover:** corre cuando las demás están `done` o `abandoned`.
  Mode D de `create-project`; la lista para el v13 (Y-1 a Y-5 y los tests que
  esperan su carrier).
- **Definition of done:** `REPORT.md` con `closed:`, entrada en `LOG.md`,
  validador sin rojos nuevos.
- **nivel de verificación:** mínimo. Lo lee el líder.
