# Tasks — code-first-pipeline

| id   | brief                                                                                   | status  | who   | plan | evidence |
| ---- | --------------------------------------------------------------------------------------- | ------- | ----- | ---- | -------- |
| T-01 | El costo de una corrida se mide por paso, y la línea de base está medida                | in-progress | agent | —    | `bin/measure-run.py`, `bin/test_measure_run.py`        |
| T-02 | `spec-source/` existe y armarlo reproduce `dist/sgai-spec.md` byte a byte               | done | agent | —    | `spec-source/`, `bin/assemble-spec.py`, `bin/test_assemble_spec.py`, `tasks/T-02/`        |
| T-03 | Las tablas de §5 y el bloque de §5.10.1 salen del XSD y `syntax.yaml`                   | pending | agent | —    | —        |
| T-04 | Cada ejemplo es un fixture con su clase, y los niveles 1 y 2 lo juzgan antes de la prosa | pending | agent | —    | —        |
| T-05 | Cada UC × clase de `context/04` tiene su vector, con lo observable y el hash de la UC   | pending | agent | —    | —        |
| T-06 | El lint dice por código si el documento armado está limpio                               | pending | agent | —    | —        |
| T-07 | Toda edición de la prosa es un parche que aplica un script, y el refine devuelve uno    | pending | agent | —    | —        |
| T-08 | La validación se apoya en una traza verificada por código y el LLM juzga por criterio   | pending | agent | —    | —        |
| T-09 | La revisión de detalles queda en los nombres, sobre la lista que arma el código        | pending | agent | —    | —        |
| T-10 | La comparación es código y no compara poblaciones distintas                              | pending | agent | —    | —        |
| T-11 | El pre-spec no produce lo que nadie lee y saltea por hash                                | done | agent | —    | `bin/step-inputs.py`, `bin/test_step_inputs.py`, `tasks/T-11/`        |
| T-12 | Los orquestadores corren sobre la fuente: artefactos primero, prosa por parche           | pending | agent | —    | —        |
| T-13 | La promoción es un script que exige todo y copia el juego completo                       | pending | agent | —    | —        |
| T-14 | La suite de tests cubre todo lo nuevo de `bin/` y corre verde entera                     | pending | agent | —    | —        |
| T-15 | `CLAUDE.md`, `README.md`, `prompts/README.md` y `SETUP.md` dicen el pipeline nuevo       | pending | agent | —    | —        |
| T-16 | La medición A/B dice cuánto bajó el costo, medido contra medido                          | pending | agent | —    | —        |
| T-17 | Cierre: REPORT.md (Mode D), LOG y validador                                              | pending | agent | —    | —        |

Lo común a todas: las decisiones están en `PHASE.md` y en las ADR 0060 a 0074;
el código va en `bin/` con exits `0/1/2/64` como los checks existentes, y cada
check dice en su salida qué cubre su verde y qué no; `context/` y `dist/` no
se tocan (si una task lo necesita, se frena y se avisa); nada se pushea; los
temporales van a `$XDG_RUNTIME_DIR/cto/`; la copia primaria de la norma está
fuera del repo y no entra a él (se citan oraciones, nunca páginas ni texto con
los encabezados de la copia).

---

## T-01 — El costo de una corrida se mide por paso, y la línea de base está medida
- **Objective:** cualquier corrida del pipeline se puede medir después con un
  comando, por paso, y hay dos números de referencia medidos: el incremental
  del 2026-10-27 y una vuelta de refine con el pipeline de hoy.
- **What it must cover:** `bin/measure-run.py <sesión>` lee el transcript de
  Claude Code (ADR 0074) de la sesión y de sus subagentes (`<config>/projects/<slug>/
  <id>.jsonl` y `<id>/subagents/*.jsonl`), cuenta **una vez por llamada a la
  API** (el `message.id`; el transcript repite el uso por bloque de contenido)
  y da por paso (el prompt de `prompts/` que el subagente recibió) entrada
  fresca, escritura y lectura de cache, salida, llamadas y contexto máximo,
  en texto y `--json`. La línea de base del incremental es la sesión
  `5ad312df` (en `~/.claude/projects/-home-…-sgai-for-mpeg-dash/`): 41,8M de
  entrada, 99k de salida. La vuelta de refine (aprobada, P-1): en un worktree
  `.worktrees/baseline-refine` del commit de hoy, `refine-spec` sobre v12.6 y
  después validate, review, audit y compare como en el camino minor del
  `CLAUDE.md`, con `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`; su salida no
  vuelve a la rama principal, sólo los números. Los resultados se guardan en
  `tasks/T-01/` en el momento (los transcripts se borran a los 30 días).
- **Definition of done:** el medidor da sobre `5ad312df` los números de
  arriba; contar por línea en vez de por llamada (el negativo) da ~90M y su
  test lo atrapa; `tasks/T-01/baseline.md` con las dos líneas de base por
  paso.
- **nivel de verificación:** alto. Es el instrumento con el que se juzga la
  meta de la fase; un medidor que cuenta mal hace mentir a T-16.

## T-02 — `spec-source/` existe y armarlo reproduce `dist/sgai-spec.md` byte a byte
- **Objective:** la spec tiene una fuente separada en prosa y artefactos, y
  armarla da exactamente el documento publicado.
- **What it must cover:** el layout de D-1 (ADR 0060, 0061). Extracción desde
  `output/v12.6-sgai-spec.md` (idéntico a `dist/sgai-spec.md`): cada bloque
  ```` ```xml ```` a `spec-source/examples/<anexo o capítulo>/<nombre>` (con
  `bin/conformance/extract.py`), el bloque de §5.10.1 a
  `spec-source/syntax/sgai-extension.xsd`, y la prosa con directivas
  `{{example:…}}` y `{{xsd}}` a `sgai-spec.src.md`. Las tablas de §5 quedan
  como prosa en esta task (las toma T-03). `bin/assemble-spec.py [--out]`
  arma y escribe junto un manifiesto de hashes de lo que usó; `--check
  <documento>` dice si un documento es el armado de la fuente.
- **Definition of done:** `assemble-spec.py` sobre la fuente da un archivo con
  el mismo sha256 que `dist/sgai-spec.md`; alterar un byte de un fixture hace
  que `--check dist/sgai-spec.md` salga 1 y nombre el fixture; una directiva a
  un archivo que no existe sale 2.
- **nivel de verificación:** alto. Todo lo demás se construye sobre esta
  fuente; si no es la spec, nada de lo que se mida después vale.

## T-03 — Las tablas de §5 y el bloque de §5.10.1 salen del XSD y `syntax.yaml`
- **Objective:** la sintaxis tiene una sola fuente y las tablas no pueden
  contradecir al XSD (ADR 0062).
- **What it must cover:** `spec-source/syntax/syntax.yaml` con lo que el XSD
  no dice (descripción, default semántico, filas de atributos base por
  esquema); `bin/gen-syntax-tables.py` y directivas `{{syntax-table:<id>}}`.
  Cruces por código: `OD` ⇒ `use="optional"`, `M` ⇒ requerido, default del
  XSD = default de la tabla, tipo de la tabla = tipo del XSD; las filas base
  contra el XSD de la 6ta (`AlternativeMPDEventType`, `EventType`,
  `EventStreamType`) en tipo y default. Las filas donde la tabla de v12.6 y el
  XSD no coinciden **no se arreglan**: se generan igual a v12.6 marcadas como
  hallazgo en `tasks/T-03/findings.md` para el v13 (o la tabla se mantiene
  literal con su hallazgo), así el armado sigue siendo byte a byte. Depende de
  T-02.
- **Definition of done:** el armado sigue dando el sha256 de `dist/`; cada
  cruce tiene un negativo que lo hace fallar; la lista de hallazgos existe
  aunque esté vacía.
- **nivel de verificación:** alto. Las tablas son lo que un implementador
  copia; una divergencia silenciosa con el XSD es invisible hasta que alguien
  implementa.

## T-04 — Cada ejemplo es un fixture con su clase, y los niveles 1 y 2 lo juzgan antes de la prosa
- **Objective:** los ejemplos se validan como archivos, por su clase
  declarada, sin depender del documento (ADR 0063).
- **What it must cover:** metadata por fixture (`spec-source/examples/
  index.yaml` o equivalente): clase entre `publisher-mpd`, `list-mpd`,
  `sps-mpd`, `overlay-list`, `request`, `fragment`, `legacy-view`, `vast`;
  la clase deducida por `extract.py` debe coincidir (si no, error). Un modo de
  `check-dash-conformance.py` sobre `spec-source/` que corre niveles 1 y 2 por
  fixture según su clase; `legacy-view` no corre las reglas de Publisher (el
  G.3, xml#40, se declara así). Reglas nuevas con su cita y su negativo:
  unicidad de `Event@id` dentro de `svta:Tracking`; tipo y default de
  `@earliestResolutionTimeOffset` y `@executeOnce` contra
  `AlternativeMPDEventType`; las `DASH §n` de la prosa contra el índice de
  cláusulas armado al correr desde la copia primaria (localizada como la
  localiza `check-normative-base.py`; no se guarda nada de ella). Depende de
  T-02.
- **Definition of done:** sobre la fuente de v12.6 el resultado coincide con
  la corrida sobre `dist/` salvo los FAIL del G.3, que pasan a
  `NOT_APPLICABLE` por la clase, y lo que agreguen las reglas nuevas (cada
  diferencia explicada en `tasks/T-04/`); cada regla nueva tiene su negativo
  atrapado.
- **nivel de verificación:** alto. Cambia qué regla corre sobre qué documento;
  un error acá esconde un FAIL.

## T-05 — Cada UC × clase de `context/04` tiene su vector, con lo observable y el hash de la UC
- **Objective:** las 22 UC son tests ejecutables en espera de su ejecutor
  (ADR 0064).
- **What it must cover:** un esquema de vector (`spec-source/scenarios/
  schema.json` o equivalente) con: fixtures de la UC (los de su anexo cuando
  existe; nuevos cuando no), capacidades del Player por clase (los ejes de
  R29.1), y por clase D1–D5 lo observable: pedidos (qué URL, cuándo),
  candidato y opción elegidos, layout, segmentos de presentación con tiempos,
  beacons; y el hash del texto de la UC. Un vector por UC
  (`UC-NN.yaml`), escrito por un LLM desde `context/04` y la fuente, y
  verificado por código (`bin/check-scenarios.py`): cobertura UC × clase
  contra los encabezados de `context/04`, forma contra el esquema, fixtures
  existentes y en verde en niveles 1 y 2, hash vigente (exit 2 si la UC
  cambió). Las tablas "Device classes" de los anexos se pueden generar del
  vector (`{{device-table:UC-NN}}`) sólo si eso mantiene el byte a byte; si
  no, quedan como prosa y se anota. Las UC que necesitan un carrier que no
  existe (los 7 de la lista del v13) salen con lo que falta marcado. Sin
  ejecutor: `NOT_VERIFIABLE — sin ejecutor`. Depende de T-02 y T-04.
- **Definition of done:** `check-scenarios.py` da 0 sobre los 22 vectores; una
  clase quitada, un fixture roto y un hash viejo dan cada uno su error.
- **nivel de verificación:** alto. Son los tests de la referencia de la fase
  siguiente; un esperado mal escrito vuelve verde una conducta incorrecta.

## T-06 — El lint dice por código si el documento armado está limpio
- **Objective:** la higiene editorial no depende de una lectura (ADR 0065).
- **What it must cover:** `bin/lint-spec.py <documento>`: `§n` sin prefijo
  resuelve a un encabezado (el prefijo `DASH`/`ISO`/… en la línea anterior
  cuenta); ids `PUB/PLY/APS/DOC/ADS-n` definidos una vez y referidos sólo si
  existen; prefijos XML declarados en cada bloque; sin `TODO`/`TBD`/`FIXME`/
  `XXX`; ningún `<!-- -->`; ninguna sección "Refinement gaps". Sobre
  `dist/` hoy da los hallazgos medidos (38 comentarios de refine, 20 en
  línea, la sección de gaps) y nada más.
- **Definition of done:** sobre `dist/` exit 1 con exactamente esos
  hallazgos; cada regla con un negativo; sobre un documento limpio, 0.
- **nivel de verificación:** alto. Es una condición de promoción.

## T-07 — Toda edición de la prosa es un parche que aplica un script, y el refine devuelve uno
- **Objective:** un cambio sin declarar es imposible y el refine lee sólo lo
  que toca (ADR 0066).
- **What it must cover:** `bin/spec-section.py get|list` (lee una sección de
  la fuente por número o encabezado). `bin/apply-spec-patch.py <fuente>
  <patch.json>`: operaciones `{section, find, replace, reason}` con `find`
  único en la sección, y `{section, replace_section, reason}`; se niega si
  `find` no está o está dos veces, o si toca una directiva; registra el
  parche aplicado. Alcance: lo cambiado = lo declarado (reusar la división
  en secciones de `check-incremental.py`). `prompts/4-auto-refine/
  refine-spec.prompt` reescrito: lee las secciones de cada issue, devuelve
  `output-analysis/v<N.M+1>-patch.json`, sin `<!-- refine -->`, y lo no
  resoluble va a `output-analysis/v<N.M+1>-refine-gaps.md`, no a la spec.
  Depende de T-02.
- **Definition of done:** un parche de prueba aplicado a la fuente de v12.6
  cambia exactamente sus secciones; `find` ausente, duplicado o sobre una
  directiva sale 1 con el motivo; el prompt nuevo no pide leer el archivo
  entero.
- **nivel de verificación:** alto. Es la puerta de toda edición futura de la
  spec.

## T-08 — La validación se apoya en una traza verificada por código y el LLM juzga por criterio
- **Objective:** la cobertura se verifica por código y el juicio de un LLM se
  acota a lo que sólo él puede juzgar, con contexto chico (ADR 0068).
- **What it must cover:** formato de `output-analysis/v<N>-trace.json`: por
  unidad de `check-promotable.py --population`, las secciones que la cumplen
  y sus citas (sin números de línea). `bin/check-trace.py`: toda unidad con
  traza, secciones existentes, cita literal dentro de su sección (normalizando
  sólo énfasis markdown y saltos de línea). La traza inicial de v12.6 se
  deriva del mapa de cobertura de `v12.6-spec-validation.md` (las L pasan a
  secciones); las 28 citas no literales quedan como hallazgo. Veredicto por
  fuente: regla de código (niveles 1 y 2), vector (conducta del Player), o
  LLM por criterio leyendo sólo el criterio y sus secciones.
  `validate-spec.prompt` reescrito así; la búsqueda abierta lee la spec
  entera sólo en mayor e incremental y las secciones cambiadas en refine.
  Cada análisis deja `v<N>-<análisis>.summary.json`; `check-promotable.py`
  lee los resúmenes. Depende de T-02, T-04, T-05.
- **Definition of done:** `check-trace.py` sobre la traza de v12.6 da 1 con
  exactamente las citas no literales; una cita alterada y una sección
  inexistente fallan; `check-promotable.py` da el mismo veredicto que hoy
  sobre v12.6 leyendo el resumen.
- **nivel de verificación:** alto. Es la mitad de la promoción.

## T-09 — La revisión de detalles queda en los nombres, sobre la lista que arma el código
- **Objective:** de las ocho categorías de `review-spec-details`, las seis
  mecánicas las cubre código y el LLM ve sólo los nombres (ADR 0069).
- **What it must cover:** `bin/name-candidates.py`: los nombres de
  `spec-source/syntax` iguales o parecidos a uno del XSD de la 6ta.
  `review-spec-details.prompt` reescrito: recibe esa lista y juzga las
  categorías 3 y 4; las otras seis las da `lint-spec.py` y la identidad del
  armado; sin autofix en la spec (si hace falta, devuelve un parche).
  Depende de T-03, T-06, T-07.
- **Definition of done:** la lista sobre la fuente de v12.6 existe y su
  conteo está en la evidencia; el prompt no pide leer la spec entera.
- **nivel de verificación:** alto. Saca juicio del LLM; lo que deje de mirar
  tiene que estar cubierto por código.

## T-10 — La comparación es código y no compara poblaciones distintas
- **Objective:** el veredicto contra lo publicado lo da una regla escrita
  (ADR 0070).
- **What it must cover:** `bin/compare-candidates.py <candidato>` contra
  `dist/`: tabla por categoría desde los `summary.json` (o, para `dist/`
  anterior a ellos, el parser de `check-promotable.py`), escribe
  `output-analysis/v<N>-comparison.md`. Exit 2 si las poblaciones difieren.
  `BETTER THAN PUBLISHED`: ninguna categoría bloqueante sube y ninguna unidad
  `met` en `dist/` baja (la junta de `check-incremental.py degradation`).
  Retira `compare-spec-versions.prompt`. Depende de T-08.
- **Definition of done:** v12.6 contra un `dist/` de prueba con la población
  de v7.2 sale 2 (el caso que el LLM sumó); contra sí misma, `NO BETTER`;
  con una unidad degradada, `WORSE`.
- **nivel de verificación:** alto. Es la otra mitad de la promoción.

## T-11 — El pre-spec no produce lo que nadie lee y saltea por hash
- **Objective:** el pre-spec cuesta sólo lo que alguien consume (ADR 0072).
- **What it must cover:** retirar `extract-conformance-assertions.prompt` y
  `build-uc-coverage-matrix.prompt` de `build-all` y de `prompts/` (la
  historia queda en git; los archivos de `context-analysis/` quedan como
  registro, sin regenerarse). Antes, el grep que prueba que ningún paso los
  lee, con su control positivo. Los otros tres saltean por el hash de sus
  entradas guardado junto a su salida.
- **Definition of done:** el grep (con control) en la evidencia; `build-all`
  sin los dos pasos; el salto por hash probado: `touch` no dispara, un cambio
  de byte sí.
- **nivel de verificación:** alto. Sacar un paso que alguien leía rompe en
  silencio.

## T-12 — Los orquestadores corren sobre la fuente: artefactos primero, prosa por parche
- **Objective:** `build-all`, `build-incremental` y el minor producen un
  candidato editando `spec-source/` y armándolo (ADR 0060, 0067, 0071).
- **What it must cover:** `apply-context-delta.prompt` reescrito: primero los
  artefactos (XSD, `syntax.yaml`, fixtures, vectores) en bucle con
  `check-dash-conformance` y `check-scenarios` hasta verde; después la prosa
  por parche, leyendo secciones; después armar, `lint-spec`, `check-trace`.
  Mayor = el mismo camino sin tope de fracción (ADR 0067); `build-spec.prompt`
  retirado. Audit una vez por mayor o incremental sobre lo nuevo o cambiado,
  fuera de la vuelta de refine. El minor del `CLAUDE.md` con los pasos
  nuevos. `check-incremental.py anchor` sigue funcionando con candidatos
  armados. Depende de T-03 a T-11.
- **Definition of done:** una corrida en seco (scratch, sin LLM: un parche de
  prueba) del minor y del incremental produce un candidato armado que pasa
  `lint`, `check-trace` y la identidad; los prompts no piden leer la spec
  entera fuera de la búsqueda abierta.
- **nivel de verificación:** alto. Es lo que corre sin nadie mirando.

## T-13 — La promoción es un script que exige todo y copia el juego completo
- **Objective:** promover sólo es posible con todo en verde y deja `dist/`
  completo (ADR 0073).
- **What it must cover:** `bin/promote.py v<N> [--dist <dir>]`: identidad del
  armado, `lint-spec` 0, `check-trace` 0, `check-promotable` 0,
  `compare-candidates` `BETTER`, `check-dash-conformance` 0; copia spec, XSD,
  `conformance-tests.md`/`.json`, sidecars y traza; escribe `PROVENANCE.md` e
  `inputs.sha256` con `spec-source/`; `check-dist-freshness.py` incluye
  `spec-source/`. Probado sólo contra un `--dist` en scratch.
- **Definition of done:** sobre v12.6 se niega y nombra cada condición que
  falla; sobre un candidato de prueba en verde, el `--dist` de scratch queda
  con el juego completo y `check-dist-freshness` en 0.
- **nivel de verificación:** alto. Publica.

## T-14 — La suite de tests cubre todo lo nuevo de `bin/` y corre verde entera
- **Objective:** lo construido en T-01 a T-13 tiene tests de regresión
  versionados.
- **What it must cover:** `bin/test_*.py` para medidor, armado, tablas,
  fixtures, vectores, lint, parche, traza, comparación, promoción; cada check
  con su positivo y su negativo. Corre la suite entera, incluidas las cinco
  de la fase 09.
- **Definition of done:** la suite entera verde; una mutación por regla de
  negocio de cada script nuevo atrapada por los tests de esa regla.
- **nivel de verificación:** alto. Es la red de lo que corre desatendido.

## T-15 — `CLAUDE.md`, `README.md`, `prompts/README.md` y `SETUP.md` dicen el pipeline nuevo
- **Objective:** quien llega al proyecto lee el pipeline como es.
- **What it must cover:** layout con `spec-source/`, la flecha nueva, los
  scripts nuevos de `bin/` con qué cubre su verde, las escalas de iteración
  (mayor sin prosa desde cero), el criterio de promoción como `promote.py`,
  los pasos retirados. Sin historia de cambios en los documentos vivos.
- **Definition of done:** cada script nuevo y cada paso retirado aparece donde
  corresponde; `grep` de los nombres retirados sólo encuentra registros.
- **nivel de verificación:** mínimo. Lo lee una persona antes de depender de
  ello.

## T-16 — La medición A/B dice cuánto bajó el costo, medido contra medido
- **Objective:** la meta de la fase tiene su número.
- **What it must cover:** con el pipeline nuevo, en un worktree: el mismo
  delta de `context/` que el incremental del 2026-10-27 (anchor `924afcb`,
  context head `61f7a8b`), y una vuelta de refine sobre las mismas entradas
  que la línea de base de T-01. `measure-run.py` sobre cada corrida. Tabla
  por paso y total, entrada procesada y salida; si llegó a −70% y, si no, qué
  paso domina. Lo que no sea comparable uno a uno se dice. Depende de T-01 y
  T-12.
- **Definition of done:** `tasks/T-16/ab.md` con las dos comparaciones y los
  comandos.
- **nivel de verificación:** alto. Es el número que se le da al líder del
  proyecto.

## T-17 — Cierre: REPORT.md (Mode D), LOG y validador
- **Objective:** la fase queda cerrada con su informe.
- **What it must cover:** corre cuando todas las demás están `done` o
  `abandoned`: REPORT.md con las ocho secciones, revisión de documentación,
  LOG, validador.
- **Definition of done:** REPORT.md con `closed:`; validador en verde.
- **nivel de verificación:** mínimo. Lo lee el líder del proyecto.
