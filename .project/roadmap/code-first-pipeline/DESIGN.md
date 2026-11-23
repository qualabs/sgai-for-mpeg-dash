---
description: "El pipeline de la spec pasa a código primero: los artefactos (XSD, tablas, ejemplos, vectores de las UC) son la fuente y se verifican por código; la prosa se escribe al final contra ellos, se edita por parches de sección, y lo que hoy juzga un LLM sin necesidad lo decide un script. Objetivo medible: bajar drásticamente los tokens por build y por vuelta de refine."
status: designing
category: feature
depends_on: [conformance-tests]
origin: "el líder del proyecto, 2026-11-23, hilo #sgai, al cerrar conformance-tests: «los tests dan confianza PQ es deterministico, un LLM JUZGANDO NO», «tal vez deberíamos hacer más 'código' … y por último se escribe la norma en sí misma», «no quiero dejar cosas 'para después' … antes de la v13», y que el camino baje drásticamente los tokens"
---

# Código primero: el pipeline de la spec

## Para qué

Hoy la spec se produce como texto y se juzga como texto: un LLM escribe 7.483
líneas, otros LLM las releen enteras para validarlas, revisarlas, auditarlas y
compararlas, y un refine vuelve a escribir sobre el documento entero. Tres
consecuencias, todas medidas abajo: lo que un script podría decidir lo decide
un LLM (y a veces mal: la comparación de v12.6 restó objetos distintos), los
cambios que nadie declaró pasan (v9.1), y el costo está dominado por releer
contexto, no por escribir.

La fase da vuelta el orden. **Los artefactos son la fuente**: el XSD y la
fuente de las tablas de §5, los ejemplos XML como fixtures que pasan los
niveles 1 y 2 de `conformance-tests`, y las UC de `context/04` como vectores
ejecutables. **La prosa se escribe al final, contra ellos**, y el documento
publicado lo arma un script. Lo que sigue en manos de un LLM es lo que es prosa
por naturaleza, y se lo lee por sección, no entero.

Todo entra antes del v13, por el tercer principio: el v13 es el primer build
que corre entero sobre el pipeline nuevo.

## Lo medido

Cada número se midió hoy con un script sobre los archivos; el comando queda en
`$XDG_RUNTIME_DIR` y se rehace en T-01. Lo que el análisis previo dijo y no se
reprodujo, se dice.

| # | Afirmación del análisis | Medido | Cómo |
|---|---|---|---|
| 1 | `compare-spec-versions` restó 17 requisitos contra 207 criterios | **Confirmado.** `output-analysis/v12.6-comparison.md` fila "met: 17 → 207, +190 ✅"; su propia nota dice que las columnas no cuentan los mismos objetos, y el veredicto `BETTER THAN PUBLISHED` igual suma ese Δ | lectura del archivo |
| 2 | v9.1 cambió 8 secciones sin anotar | **Confirmado: 8 sustantivas** (7 anexos H–N perdieron `*Informative.*`; A.5 cambió `<up:RequestParam>` por `<RequestParam>`) más una línea en blanco en O.8. En v12.4→v12.5 (incremental) 13 secciones cambiadas sin anotación | diff por sección, `<!-- refine` buscado en cada una |
| 3 | `dist/` con 38 `<!-- refine -->`, "Refinement gaps", y sin `sgai-extension.xsd` ni `conformance-tests.*` | **Confirmado.** 38, la sección en L7462, los tres archivos faltan. Corrida sobre `dist/` tal como está, `check-dash-conformance` da **FAIL 9**: los 8 del REPORT de la fase 09 (que la corrió con el XSD emitido aparte) más `XSD-ID: dist/sgai-extension.xsd does not exist` | `grep -c`, `ls dist/`, corrida del check |
| 3b | Lint editorial | En `dist/`: §n sin prefijo que no resuelven **0** (mis 4 candidatos eran "DASH" en la línea anterior), 173 ids PUB/PLY/APS/DOC/ADS definidos, 0 duplicados, 0 colgados, 84 bloques XML sin prefijo sin declarar, 0 TODO/TBD, **20 comentarios en línea** con texto | script sobre `dist/sgai-spec.md` |
| 4 | Citas del mapa de cobertura: 27/382 no literales, 30/326 con la línea mal | **Mitad.** No literales: **28 de 364** segmentos (coincide). Línea mal: **1 de 280**, no 30 — el análisis no se reproduce. El instrumento se probó en los dos sentidos: con las L corridas 8 líneas da 279/280 mal, y con `MUST`→`SHALL` en la spec da 176 no literales | script con mutaciones |
| 5 | Los ejemplos XML son ~50% del documento | **Los anexos son el 49% de las líneas; los bloques de código, el 31,5%** (2.353 de 7.459). Dentro de los anexos A–Q, el 61% es código. Con las tablas de §5 (165 líneas) lo generable por código es ~34% del documento | conteo por capítulo |
| 7 | Un arreglo toca 3–11 de 28 capítulos; 528 refs cruzadas | **Capítulos: 3 a 18** en siete refines (v9.1 tocó 18), y los tocados son el **11% a 82%** de los bytes (típico ~42%, porque §4 y §5 caen en casi todos). **Secciones: 4 a 42**, el **2,7% a 21%** de los bytes (típico ~9%). Refs `§n`: 524 | diff por capítulo y por sección |

**El costo, medido.** El único transcript de una corrida de pipeline que
sobrevive es el incremental del 2026-10-27 (sesión `5ad312df`, el que terminó
en `MAJOR RECOMMENDED`); los anteriores se borraron con la limpieza de 30 días
de Claude Code. Contado por llamada a la API (cada llamada aparece una vez por
bloque de contenido en el transcript; sumar líneas da 90M, el doble):

| Paso | Tokens de entrada procesados | de ellos, lectura de cache | Salida | Llamadas | Contexto máx. |
|---|---|---|---|---|---|
| orquestador | 2,73M | 2,61M | 13,6k | 26 | 127k |
| `extract-conformance-assertions` | 4,11M | 3,90M | 0,6k | 29 | 212k |
| `analyze-dash-gap` | 5,91M | 5,69M | 26,5k | 36 | 225k |
| `build-uc-coverage-matrix` | 1,41M | 1,27M | 0,7k | 13 | 136k |
| `analyze-iab-ad-templates` | 1,05M | 0,96M | 0,2k | 13 | 96k |
| `build-error-semantics` | 1,39M | 1,26M | 10,2k | 14 | 127k |
| `apply-context-delta` | **25,24M** | 24,85M | 47,6k | 88 | **400k** |
| **Total** | **41,8M** | 40,5M | 99k | 219 | |

Tres lecturas:

- **El costo es contexto × llamadas, no escritura.** `apply-context-delta`
  es el 60% con 88 llamadas a un promedio de 287k de contexto: la spec entera
  (~105k tokens) más `context/` más sus propias ediciones, releídos en cada
  llamada. La salida total es el 0,2% de la entrada.
- **El 13% se gasta en artefactos que nadie lee.**
  `conformance-assertions.md` y `uc-coverage-matrix.md` (5,5M juntos) no son
  entrada de ningún paso: `grep -rl` sobre `prompts/`, `bin/` y los `.md` vivos
  los encuentra sólo en su propio prompt, en `build-all` que los invoca y en
  `prompts/README.md`. `build-spec` declara como entradas sólo gap, error
  semantics e IAB.
- **Esa corrida no llegó a la mitad cara.** Cortó antes de validar, revisar,
  auditar, comparar y refinar.

Lo que no tiene transcript se **estima** (marcado así en todo el documento),
con la misma fórmula — contexto promedio × llamadas — y los tamaños de hoy:
spec ~105k tokens, `context/03`+`04` ~70k, el sidecar de validación ~32k,
`CLAUDE.md` del proyecto ~12k.

| Corrida | Hoy | Con este diseño |
|---|---|---|
| Incremental (lo que corrió el 10-27) | **41,8M medido** | **~12–16M estimado**: pre-spec sin los dos artefactos huérfanos (−5,5M), el delta leyendo sólo las secciones que toca (~70k de contexto en vez de ~290k) |
| Una vuelta de refine (refine + validate + review + audit + compare) | **~40–50M estimado** | **~6–10M estimado**: parche por sección, validación de los criterios cuyas secciones cambiaron, review y compare por código, audit fuera de la vuelta |
| Mayor completo (pre-spec + build + post-spec + hasta 5 vueltas) | **~100–300M estimado** | **~30–50M estimado**; el mayor deja de reescribir la prosa entera (D-8) |

La meta de la fase: **≥70% menos tokens de entrada procesados** por
incremental y por vuelta de refine, medido como en T-16. El análisis previo
hablaba de ~600k por vuelta; ésa es la lectura única de la spec 3–4 veces, no
lo que se paga, que es esa lectura multiplicada por cada llamada.

## Decisiones

### D-1. La fuente de la spec es `spec-source/`, y el documento lo arma un script

Un directorio nuevo, versionado, entre `context-analysis/` y `output/`:

```
spec-source/
├── sgai-spec.src.md        la prosa, con directivas de inclusión
├── syntax/
│   ├── sgai-extension.xsd  el XSD de las extensiones (hoy §5.10.1)
│   └── syntax.yaml         lo que el XSD no dice: descripción de cada fila,
│                           default semántico, uso de los atributos base
├── examples/<anexo>/*.mpd|*.xml   los ejemplos, con su metadata (D-4)
└── scenarios/UC-NN.yaml    los vectores de las UC (D-5)
```

`bin/assemble-spec.py` reemplaza cada directiva (`{{example:a/main.mpd}}`,
`{{syntax-table:overlay-window}}`, `{{xsd}}`, `{{device-table:UC-01}}`) por su
contenido y escribe `output/v<N>-sgai-spec.md`; junto, el manifiesto de hashes
de la fuente que lo produjo. `output/` sigue siendo lo que un build produjo y
nunca se edita a mano; lo que cambió es que el build ahora escribe en
`spec-source/` y arma. La flecha queda `context/` → `context-analysis/` →
`spec-source/` → `output/` → `output-analysis/`.

El arranque no inventa nada: `spec-source/` sale de extraer `v12.6` (los
bloques con `bin/conformance/extract.py`, que ya los clasifica), y **armar esa
fuente tiene que reproducir `dist/sgai-spec.md` byte a byte**. Ése es el test
que dice que la fuente es la spec y no otra cosa.

### D-2. Una sola fuente de prosa, no una por capítulo

El pedido era reevaluar partir la spec con el principio nuevo. Partir sirve si
lo que cuesta es leer; y lo que cuesta leer baja por sección, no por capítulo.
Medido en siete refines: los capítulos tocados son en general el ~42% de los
bytes (§4 y §5 caen en casi todos los arreglos y suman 2.409 líneas), y hasta
el 82%; las secciones tocadas, ~9% y hasta 21%. Un archivo por capítulo deja
al agente leyendo casi la mitad del documento; un lector por sección
(`bin/spec-section.py get 5.1.3`) le da el 9% sin partir nada.

Las otras dos razones para partir tampoco se sostienen: las 524 refs `§n`
resuelven dentro de un documento y el lint las verifica en el armado (D-6), y
un mayor que quiere generar capítulos en paralelo los escribe en scratch y el
script los concatena. Queda un archivo de prosa, `sgai-spec.src.md`, y la
partición útil es la que ya existe: la prosa por un lado, los artefactos por
otro.

### D-3. El XSD es la fuente de la sintaxis, y las tablas de §5 se generan

Las tablas de §5 repiten, fila por fila, tipo, obligatoriedad y default que el
XSD ya dice. `bin/gen-syntax-tables.py` las genera del XSD más `syntax.yaml`,
que trae sólo lo que el XSD no puede decir: la descripción, el default cuando
es semántico ("the family default (§3.4.3)"), y las filas de **atributos base**
(`EventStream@timescale`, `Event@duration`…) que cada esquema usa. El código
verifica lo que se puede cruzar: `OD` ⇒ `use="optional"`, un default del XSD
igual al de la tabla, y las filas base contra el XSD de la 6ta
(`AlternativeMPDEventType` y sus vecinos) en tipo y default. El bloque de
§5.10.1 es `{{xsd}}`, así el XSD y la spec no pueden divergir (hoy lo garantiza
`emit-extension-xsd.py` en la dirección inversa).

Al pasar de v12.6 a tablas generadas, las filas donde la tabla actual y el XSD
no coinciden salen como lista: son hallazgos para el v13, no se corrigen acá.

### D-4. Los ejemplos son fixtures con metadata, y cada uno dice qué es

Cada ejemplo de los anexos es un archivo en `spec-source/examples/` con su
clase declarada: `publisher-mpd`, `list-mpd`, `overlay-list`, `sps-mpd`,
`request`, `fragment`, y **`legacy-view`** (lo que ve un Player legacy, que no
es un MPD de Publisher). Los niveles 1 y 2 de `conformance-tests` corren sobre
el fixture según su clase, antes de que haya prosa. Así se cierra el hilo
abierto del G.3 (xml#40): la ilustración deja de leerse como MPD de Publisher
porque el archivo lo dice, y las reglas que no le aplican no corren.

Hoy la clase se deduce del documento (raíz, namespace, `@profiles`); la
deducción se mantiene como chequeo: si la clase declarada y la deducida no
coinciden, es un error.

Entran acá también las reglas fáciles que la fase 09 dejó (REPORT §4): unicidad
de `Event@id` dentro de `svta:Tracking`, tipo y default de
`@earliestResolutionTimeOffset` y `@executeOnce` contra
`AlternativeMPDEventType`; y las referencias `DASH §n` de la prosa contra el
índice de cláusulas de la copia primaria, armado al correr desde la copia local
(no se guarda nada de la copia en el repo).

### D-5. Las UC son vectores ejecutables; los ejecuta `reference-player`

Cada UC de `context/04` pasa a `spec-source/scenarios/UC-NN.yaml`: los
fixtures que la arman (MPD, documentos de resolución, capacidades declaradas
del Player) y, **por clase D1–D5, lo observable**: qué pide el Player y cuándo,
qué candidato y qué opción elige, con qué layout, qué segmentos de
presentación ocurren en qué tiempos, qué beacons disparan. Cada vector guarda
el hash del texto de su UC, como las reglas de la fase 09, así lo que el v13
mueva sale como lista.

En esta fase el código verifica el vector, no la conducta: que cada UC × clase
de `context/04` tenga el suyo, que sus fixtures pasen los niveles 1 y 2, que su
forma sea la del esquema. Lo ejecuta el harness de Players de la fase 09 con la
referencia de `reference-player`; hasta entonces salen `NOT_VERIFIABLE —
sin ejecutor`. Las tablas "Device classes" de los anexos se generan del
vector (`{{device-table:UC-01}}`); el recorrido en prosa (A.5) lo sigue
escribiendo el LLM.

### D-6. Lint e higiene, por código, sobre el documento armado

`bin/lint-spec.py`, exit 0/1/2/64 como los demás: `§n` sin prefijo resuelve a
un encabezado (con el prefijo `DASH` en la línea anterior contado), ids
definidos una vez y referidos sólo si existen, prefijos XML declarados, sin
`TODO`/`TBD`/`FIXME`, ningún `<!-- -->` en el documento armado, ninguna
sección "Refinement gaps". Hoy `dist/` falla por 38 comentarios de refine, 20
en línea y la sección de gaps; lo demás pasa, y las reglas quedan para que siga
así.

### D-7. Toda edición de la prosa es un parche, y lo aplica un script

El refine (y el incremental, y el mayor) no devuelve un documento: devuelve
`v<N>-patch.json`, una lista de `{sección, buscar, reemplazar, motivo}` donde
`buscar` aparece exactamente una vez en esa sección, o `{sección, reemplazar
entera}` cuando el cambio es de estructura. `bin/apply-spec-patch.py` lo aplica
a `sgai-spec.src.md` y se niega si `buscar` no está o está dos veces, o si la
sección es una directiva (un ejemplo o una tabla se arreglan en su fuente, no
en la prosa). El alcance se chequea con el `scope` de `check-incremental.py`:
lo que cambió es exactamente lo que el parche declara.

Así un cambio sin declarar no es posible por construcción (v9.1), las
anotaciones `<!-- refine -->` dejan de existir (el parche es la traza, en
`output-analysis/`), y "Refinement gaps" sale de la spec a un sidecar. El
agente lee las secciones que va a tocar con `spec-section.py`, no el archivo.

### D-8. Un mayor edita la fuente; ya no reescribe la prosa desde cero

Con la fuente persistente como el código, un build mayor deja de significar
"regenerar el documento": significa un delta sin tope de fracción, que puede
agregar o retirar construcciones y secciones. El orden es siempre el mismo:
primero los artefactos (XSD, `syntax.yaml`, fixtures, vectores) en un bucle
con el código hasta que los niveles 1 y 2 den verde; después la prosa, por
sección y por parche; después armar y chequear. `build-spec` desde cero queda
retirado. La salvaguarda contra la incoherencia que acumulan los parches es la
lectura completa de D-9, una vez por mayor.

### D-9. La validación se apoya en una traza, y el LLM juzga por criterio

El build escribe `output-analysis/v<N>-trace.json`: por cada unidad de la
población (`check-promotable.py --population`, 212 hoy: 165 criterios, 25 obligaciones de prosa, 22 UC), las secciones de la
spec que la cumplen. `bin/check-trace.py` verifica por código que toda unidad
tenga traza, que las secciones existan, y que cada cita sea **literal dentro de
su sección** (sin números de línea, que son frágiles y fueron la mitad de los
errores de cita que se buscaron).

Sobre esa traza, el veredicto por unidad sale de donde corresponde:

- **del código**, cuando una regla de nivel 1 o 2 la decide (81 reglas con
  código hoy);
- **del vector** (D-5), para la conducta del Player (59 reglas de nivel 2);
- **de un LLM**, para el resto, leyendo **sólo el criterio y sus secciones**:
  contexto chico, en paralelo, y en un refine sólo para las unidades cuyas
  secciones cambiaron.

La búsqueda abierta (gaps, edge cases, ambigüedades) es lo único que lee la
spec entera, y corre una vez por mayor o incremental; en una vuelta de refine
lee las secciones cambiadas. Cada análisis deja además un resumen máquina,
`v<N>-<análisis>.summary.json`, que es lo que leen los scripts.

### D-10. `review-spec-details` pasa a código salvo los nombres

De sus ocho categorías, seis son código: formato y delimitadores, referencias
cruzadas, anexo contra capítulo y regresión editorial (que con fixtures y
tablas generadas no pueden divergir), namespaces declarados, marcadores de
borrador. Las dos de nombres (un nombre de la base reusado con otra semántica,
o un sinónimo inventado para algo que la base ya nombra) quedan en el LLM,
pero sobre una lista que arma el código: los nombres de `spec-source/syntax`
que coinciden o se parecen a uno del XSD de la 6ta.

### D-11. La comparación es código, y no compara poblaciones distintas

`bin/compare-candidates.py` lee los `summary.json` del candidato y de `dist/`
y escribe `v<N>-comparison.md` con la tabla y el veredicto. Si las dos
poblaciones no son la misma (unidades distintas, como 17 requisitos contra 207
criterios), sale `2` y no da veredicto: eso es exactamente lo que el LLM hizo
mal en v12.6. `BETTER THAN PUBLISHED` queda definido como regla escrita en el
script: ninguna categoría bloqueante sube, y ninguna unidad `met` en `dist/`
baja (la junta de `check-incremental degradation`).

### D-12. El audit del LLM sale de la vuelta de refine

Desde la fase 09 el audit sólo entrega sospechas que no bloquean, y sobre
`dist/` 17 de 37 se confirmaron por código, 10 en parte, 10 sin evidencia y
ninguna contradicha. Corre una vez por mayor o incremental, sobre las
construcciones nuevas o cambiadas, y cada sospecha confirmada se vuelve una
regla de código. En la vuelta de refine no corre.

### D-13. El pre-spec pierde lo que nadie lee y deja de saltear por fecha

`extract-conformance-assertions` y `build-uc-coverage-matrix` se retiran (no
los consume ningún paso; la cobertura de UC la da D-5 y las aserciones, los
niveles 1 y 2). Los otros tres pasos del pre-spec saltean por el hash de sus
entradas, no por mtime: hoy un `touch` los vuelve a correr y una edición que
conserva la fecha no.

### D-14. La promoción es un script

`bin/promote.py v<N>` es el criterio de promoción ejecutable: el documento
armado coincide con su fuente, `lint-spec` 0, `check-trace` 0,
`check-promotable` 0, `compare-candidates` da `BETTER THAN PUBLISHED`, y
`check-dash-conformance` 0. Si todo da, copia a `dist/` **el juego completo**
(spec, XSD, `conformance-tests.md`/`.json`, los sidecars, la traza) y escribe
`PROVENANCE.md` e `inputs.sha256` con `spec-source/` incluido. El coordinador
lo corre y avisa, como hoy; la diferencia es que el juego incompleto de `dist/`
deja de ser posible. En esta fase no se promueve nada: v12.6 tiene 9 FAIL.

### D-15. El costo se mide con un instrumento, antes y después

`bin/measure-run.py <sesión>` suma el uso por paso (por el prompt que cada
subagente recibió), una vez por llamada a la API, y separa entrada fresca,
escritura y lectura de cache, y salida. El error que ya se cometió hoy al
contar (sumar líneas en vez de llamadas da el doble) es su test negativo. Se
corre al terminar cada corrida y el resultado se guarda como evidencia, porque
los transcripts se borran a los 30 días.

## Qué es prosa por naturaleza y queda en un LLM

- La prosa de los capítulos 1–4 y 6–8 y los recorridos de los anexos.
- En el nivel 2, **las reglas sobre el texto**: 32 marcadas "a property of the
  specification's prose" y ~20 de semántica caso a caso (qué significa un
  token, qué promete el texto sobre un Player), ~26% de las 196; más 7
  obligaciones entre partes fuera de los documentos.
- Los tres análisis pre-spec que quedan (gap, error semantics, IAB).
- La búsqueda abierta de la validación (D-9), los dos chequeos de nombres
  (D-10) y las sospechas del audit (D-12).
- **Escribir** los fixtures y los vectores. Un LLM los escribe; el código los
  juzga.

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| Fuente partida por capítulo (D-2) | Medido: un capítulo tocado arrastra el ~42% de los bytes; la sección, el ~9%. Lo que abarata es leer por sección, y eso no necesita partir |
| Marcar en el documento las regiones generadas con comentarios y verificarlas, sin fuente aparte | El documento publicado tiene que salir sin comentarios (D-6), y el refine seguiría trabajando sobre el armado |
| YAML como fuente única de XSD y tablas (D-3) | Un tercer formato para lo que el XSD ya expresa y lo que se publica; el XSD compila contra el de ISO y ya es artefacto |
| Descripciones dentro del XSD (`xs:documentation`) | Hace del bloque de §5.10.1 un documento de prosa |
| Un modelo de decisión del Player en Python que ejecute los vectores ya en esta fase (D-5) | Una segunda implementación de la conducta a mantener al lado de la referencia sobre dash.js, que es la siguiente fase |
| Seguir regenerando la prosa entera en cada mayor (D-8) | Es el patrón "mucho texto" que la fase existe para sacar, y el 60% del costo medido |
| Partir esto en dos fases (herramientas, después fuente) | El parche, la traza y el lint operan sobre la fuente: hechos antes de ella habría que rehacerlos sobre otro archivo |

## Lo que la fase NO hace

- No toca `dist/` ni `context/`. `dist/` queda como está hasta que se promueva
  el v13; sus problemas de higiene se arreglan por construcción en esa
  promoción.
- No corrige los 9 FAIL ni los 7 elementos sin carrier: son del v13.
- No construye el Player de referencia ni ejecuta los vectores (es
  `reference-player`).
- No toca los pipelines de issues y PRs (Stages 5 y 6).
- SVTA 2053 y `multi-asset-options-profile` siguen fuera.

## Tasks propuestas

| id | Qué deja verdadero | Tamaño | Nivel |
|---|---|---|---|
| T-01 | `bin/measure-run.py` con su negativo; la corrida del 10-27 como línea de base en la evidencia; la vuelta de refine vieja medida si se aprueba (P-1) | S | alto |
| T-02 | `spec-source/` extraído de v12.6 y `bin/assemble-spec.py`; el armado reproduce `dist/sgai-spec.md` byte a byte; un fixture alterado hace fallar la identidad | M | alto |
| T-03 | XSD + `syntax.yaml` generan las tablas de §5; cruces con el XSD propio y con el de la 6ta; la lista de filas de v12.6 que no coinciden, como hallazgos | M | alto |
| T-04 | Fixtures con clase declarada (`legacy-view` incluida), niveles 1 y 2 por fixture, las reglas fáciles de la fase 09 y las `DASH §n` contra la copia primaria, con negativos | M | alto |
| T-05 | Vectores de las 22 UC × D1–D5 con su esquema, hash de la UC y chequeo de cobertura; tablas de clases generadas | L | alto |
| T-06 | `bin/lint-spec.py` con sus reglas y negativos; corrido sobre `dist/` da los hallazgos medidos | S | alto |
| T-07 | `bin/spec-section.py` y `bin/apply-spec-patch.py`; `refine-spec` devuelve parche; sin anotaciones en línea; gaps a sidecar | M | alto |
| T-08 | La traza, `bin/check-trace.py`, y `validate-spec` reescrito (veredicto por fuente, LLM por criterio, búsqueda abierta acotada) con `summary.json` | L | alto |
| T-09 | `review-spec-details` reducido a los nombres sobre la lista del código; el resto en `lint-spec` | S | alto |
| T-10 | `bin/compare-candidates.py` reemplaza el prompt; exit 2 ante poblaciones distintas (v12.6 contra v7.2 es su negativo) | S | alto |
| T-11 | Pre-spec sin los dos pasos huérfanos y con salto por hash | S | alto |
| T-12 | `build-all`, `build-incremental`, `apply-context-delta` reescritos sobre la fuente (artefactos primero, prosa por parche, audit fuera de la vuelta); `build-spec` retirado | L | alto |
| T-13 | `bin/promote.py` con todas las condiciones y el juego completo; probado contra un `dist/` en scratch | S | alto |
| T-14 | La suite de tests de todo lo nuevo de `bin/`, escrita y corrida entera | M | alto |
| T-15 | `CLAUDE.md`, `README.md`, `prompts/README.md`, `SETUP.md` dicen el pipeline nuevo | S | mínimo |
| T-16 | Medición A/B: el mismo delta de `context/` del 10-27 (anchor `924afcb` → `61f7a8b`) por el pipeline nuevo contra los 41,8M medidos; y la vuelta de refine contra la de T-01 si existe. Por paso y total; dice si llegó al −70% y, si no, qué paso domina | M | alto |
| T-17 | Cierre: REPORT, LOG y validador | S | — |

Orden: T-01 y T-02 primero (instrumento y fuente); T-03 a T-06 en paralelo
sobre la fuente; T-07 a T-11 después; T-12 cuando todo lo anterior existe; T-13
a T-16 al final.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| La extracción de v12.6 no reproduce el documento byte a byte (espacios, bordes de bloque) | Es la definición de hecho de T-02: no se avanza con una fuente que no es la spec |
| Juzgar por criterio con contexto chico pierde lo que cruza secciones | La búsqueda abierta de D-9 lee la spec entera una vez por mayor e incremental |
| Los parches acumulan incoherencia sin una reescritura completa | La misma lectura completa, más el reemplazo de sección entera que el parche admite |
| Un vector codifica mal lo esperado de `context/04` y nadie lo ejecuta hasta la fase siguiente | Hash de la UC en cada vector; `NOT_VERIFIABLE — sin ejecutor` hasta `reference-player`, que lo revisa al ejecutarlo |
| La medición no se puede hacer porque el transcript se borró, o se cuenta mal | T-01 guarda los números al terminar cada corrida; el doble conteo es el negativo del medidor |
| Faltan carriers para 7 elementos, así que hay fixtures y vectores incompletos | Aceptado: salen como lista; el v13 los agrega sobre la fuente |
| La fase misma gasta tokens | Casi todo es código; las corridas pagas son T-16 y, si se aprueba, la línea de base de T-01 |

## Roadmap

Esta fase va antes de `reference-player` (que ejecuta los vectores de D-5) y
del v13 (el primer build sobre el pipeline nuevo). `reference-player` y
`major-build-v13` pasan a depender de ella.

## Preguntas abiertas

**P-1. ¿Se paga una vuelta de refine con el pipeline viejo para tener la línea
de base medida?** Hoy la vuelta de refine sólo está estimada (~40–50M de
entrada procesada), porque su transcript se borró. Correrla sobre v12.6 en un
worktree del commit actual, sin tocar `output/`, la deja medida y hace que la
comparación de T-16 sea medida contra medida. Sin ella, T-16 compara el
incremental (que sí está medido) y el refine contra un estimado.
**Recomendación: sí**, una sola vuelta; es lo que convierte "bajó
drásticamente" en un número para el refine, que es lo que más se repite.
