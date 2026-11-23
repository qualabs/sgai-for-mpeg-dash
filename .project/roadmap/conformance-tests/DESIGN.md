---
description: "Testing completo de la spec en tres niveles, con veredictos de código y no de un LLM: (1) el XSD de las extensiones como artefacto del build y su conformidad con ISO/IEC 23009-1 6ta; (2) las reglas de context/03 sobre los documentos como código con su cita; (3) la conducta de los Players, legacy aquí y el que implementa la extensión (referencia sobre dash.js) en reference-player. Las dos fases van antes del v13."
status: designing
category: chore
origin: "el líder del proyecto, 2026-11-23, hilo #sgai: «tal vez hay una parte del proceso que es justamente testear contra la norma», con la analogía de projects/tests-de-planos"
---

# Tests de conformidad de la spec

## Para qué

Hoy la conformidad de la spec con DASH la decide un LLM: el Step 8 de
`build-all` (`prompts/3-post-spec/audit-dash-conformance.prompt`) arma un
inventario de construcciones y les pone un veredicto leyendo la copia primaria.
Su veredicto se puede discutir pero no se puede volver a correr: dos corridas
sobre el mismo candidato pueden dar resultados distintos, y un error suyo no lo
detecta nadie salvo otra lectura.

El criterio rector, del líder del proyecto: *"hacer una demo con tests REALES
que un código falle y no sea un LLM diciendo algo está bien o mal es muy
distinto. Los tests dan confianza PQ es deterministico, un LLM JUZGANDO NO"*.

Por eso la evidencia pasa a ser tests que se corren y que pueden fallar, como en
`projects/tests-de-planos`: una regla por requerimiento, con su id, la
cláusula o el criterio, la oración citada, y un resultado por instancia,
`PASS` / `FAIL` / `NOT_VERIFIABLE` (con el motivo) / `NOT_APPLICABLE`, y dónde
falla (bloque de la spec, línea y XPath). **El veredicto lo da siempre código
determinístico**: XSD, reglas como código, el tool de DASH-IF, Players. Un LLM
puede ayudar a escribir un test; nunca decide si algo pasa. Lo que sólo se
puede juzgar con un LLM sale `NOT_VERIFIABLE` y no se cuenta como pasado.

El testing es completo en tres niveles, y los tres los pidió el líder del
proyecto (*"Me gusta los 3!!! … está muy bien hacer mucho testing en esto así
la norma no tiene problemas"*):

1. **Sintaxis y conformidad con DASH**: el XSD de nuestras extensiones, que el
   build produce, y los documentos de la spec, contra el XSD de la 6ta y las
   reglas de la norma que el XSD no expresa.
2. **Las reglas propias de la spec**: los criterios de `context/03` sobre los
   documentos, como código con la cita del criterio.
3. **La conducta de un Player**: uno que no implementa la extensión (que la
   ignore y siga reproduciendo) y uno que la implementa (que haga lo que la
   spec dice).

Y tiene que ser demostrable: un comando que corre todo y sale con un exit
code, y casos negativos, documentos rotos a propósito que el test hace fallar
con la cita y el lugar, además de los positivos.

El alcance de la norma lo fijó el líder del proyecto el 2026-11-23: **sólo la
norma DASH nativa**, la edición que declara `context/00-normative-base.md`
(ISO/IEC 23009-1:2026, 6ta edición). SVTA 2053 queda afuera; son trabajos en
paralelo que no se tocan.

## Lo que se verificó antes de diseñar

Las ideas de partida venían "a verificar y no a asumir". Esto se midió el
2026-11-23, con los archivos en una carpeta temporal fuera del repo.

**1. El XSD oficial de la 6ta edición existe y es público.** La copia primaria
lo dice: *"The schema of the MPD for this document is provided at:
https://standards.iso.org/iso-iec/23009/-1/ed-6/en (DASH-MPD.xsd)"* (Annex B).
Búsqueda: `pdftotext -layout` de la copia primaria y `grep -n -i 'xsd\|schema
file\|standards.iso.org'`. La página responde 200 y lista un solo archivo,
`DASHSchema-6th-Ed.zip` (sha256 `43b62f3d…1feb1d28`), con `DASH-MPD.xsd`,
`DASH-MPD-UP.xsd`, `DASH-MPD-PATCH.xsd` y 41 MPD de ejemplo (G1 a G30, H1 a H3,
K6.4). Ese XSD declara `InsertPresentation`, `ReplacePresentation` e
`ImportedMPD`, y abre `xs:any namespace="##other" processContents="lax"` en
`EventType`, `PeriodType` y el resto de los puntos de extensión.

- La URL genérica `standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-DASH_schema_files/DASH-MPD.xsd`
  **no** es la 6ta: `grep -c InsertPresentation` da `0`.
- La rama `6th-Ed` de `github.com/MPEGGroup/DASHSchema` difiere del zip de ISO
  en 4 líneas (por ejemplo `popularityRate` sin `use="required"`). La
  referencia es el zip de ISO, que es lo que la norma nombra.

**2. El conformance tool de DASH-IF existe pero valida contra la 5ta.**
`github.com/Dash-Industry-Forum/DASH-IF-Conformance`, última release `v3.1.0`
(2026-09-10). Su módulo XSD (`app/Modules/Common/MPD/XSDValidation.php`)
valida contra `xsd/DASH5th.xsd`, `xsd/DASH2nd.xsd` y `xsd/DASH4th-amd1.xsd`, y
`resources/xsd/` no tiene otro. Búsqueda: `gh api
repos/Dash-Industry-Forum/DASH-IF-Conformance/git/trees/v3.1.0?recursive=1`
filtrado por `xsd$`. Medido con ese `DASH5th.xsd`:

| Qué se validó | XSD ISO 6ta | XSD del tool (5ta) |
|---|---|---|
| Los 41 ejemplos de ISO de la 6ta | 41 válidos | 33 válidos, 8 rechazados |
| Los 52 MPD de `dist/sgai-spec.md` | 52 válidos | 35 válidos, 17 rechazados |

Los 17 rechazos son todos por construcciones de la 6ta: `InsertPresentation`
(7), `ImportedMPD` (7), `ReplacePresentation` (2), `MPD@type="list"` (1). El
módulo XSD del tool da por inválido lo que la norma da por válido, y lo hace
también con los ejemplos de la propia ISO.

El proyecto `qualabs-video-replacement` ya tiene el tool construido y fijado
(`tools/dash-conformance/`, `v3.0.0`), con un README que muestra que el tool y
el XSD **no se contienen**: el XSD pasó `frameRate` en `AdaptationSet` y en
`Representation` a la vez, y el tool lo rechazó por una regla de coexistencia;
sacar `@codecs` deja el documento válido para el XSD.

**3. Los Players.**

- **dash.js v5.3.0** (2026-11-04): su tabla de features dice "Server Guided Ad
  Insertion — Not supported" (`docs/site/pages/features/index_features.md`).
  No implementa ni el lineal de la 6ta (`InsertPresentation` /
  `ReplacePresentation`) ni, por supuesto, nuestra extensión.
- **Shaka v5.3.6** (2026-11-20): `lib/ads/dash_interstitial_parser.js`
  reconoce `urn:mpeg:dash:event:alternativeMPD:insert:2025` y `…:replace:2025`
  y lee `InsertPresentation`/`ReplacePresentation` (cita
  *"ISO/IEC 23009-1:2026"*). Implementa el lineal de la 6ta; nuestra extensión
  no lineal, no.

Búsqueda: `gh api search/code` sobre cada repo con `alternativeMPD`,
`InsertPresentation` e `ImportedMPD`. En dash.js la búsqueda de código no
encontró nada; para no leer un cero como resultado se corrió la misma búsqueda
con `callback:2015`, que dash.js implementa, y dio 2. Lo que respalda "no lo
soporta" es la tabla de features, no el cero. Ningún Player implementa hoy la
extensión.

**4. Los 84 bloques XML de `dist/sgai-spec.md`.** 52 son MPD completos, 23
`svta:OverlayList`, 1 es el XSD de la extensión (el de §5.10.1, auditado como
K-31), 2 son VAST (IAB), y 6 son fragmentos (`Period`, `OverlayPresentation`,
`RenderableAsset`, `Tracking`, `ClickThrough`, `Metrics` sin namespace).
Con el XSD de ISO más el de la spec cargados juntos: los 52 MPD, los 23
`OverlayList`, `OverlayPresentation` y `ClickThrough` validan; `Period`,
`RenderableAsset` y `Tracking` no son elementos globales y no se pueden validar
como raíz.

**El instrumento encuentra.** Errores inyectados a propósito, uno por clase:

| Inyección | Sólo XSD ISO | ISO + XSD de la spec |
|---|---|---|
| Elemento desconocido del namespace DASH dentro de `Event` | FAIL | FAIL |
| `Event@id="one"` | FAIL | FAIL |
| `OverlayList@family` con un token inventado | (no aplica) | FAIL |
| `bogusAttr` en `svta:ClickThrough` dentro de un MPD | **PASS** | FAIL |

La última fila es la razón del XSD propio: el `##other lax` de DASH acepta
cualquier cosa de un namespace que no conoce, así que el XSD de ISO solo no ve
ningún error de nuestras extensiones.

**El XSD de las extensiones hoy no existe como archivo.** Vive sólo como el
bloque de §5.10.1 dentro de `dist/sgai-spec.md`; para medir lo de arriba hubo
que sacarlo del markdown a mano.

**5. `context/03` como fuente del nivel 2.** 165 criterios. Por quién los
tiene: `spec document` 61, `Player` 57, `APS` 19, `Publisher` 13, y 15 con
dos o más actores (3 de ellos incluyen al Player). Su índice "Interfaces"
lista 75 elementos: 27 del MPD (I-MPD), 16 del pedido (I-REQ) y 32 del
documento de resolución (I-RES), cada uno con el criterio que lo define.
Medido con `grep` sobre los marcadores `- **R<n>.<n>** (<actor>)` y sobre las
filas de las tres tablas.

## Decisiones

### D-1 — Qué se testea: lo que el build produce, no un documento aparte

El sujeto de los niveles 1 y 2 son dos productos del build: **el XSD de las
extensiones** (D-3) y **los documentos que la spec da como ejemplo**, sacados
de su markdown (los 84 bloques ```` ```xml ````, y las URL de pedido de
ejemplo para I-REQ). No se mantienen documentos de prueba escritos a mano en
paralelo: serían una segunda copia de lo que la spec dice, que se desincroniza
en el primer build.

Lo que la spec define y no tiene ejemplo es un hallazgo de cobertura, no un
test que falta escribir: el informe lista cada construcción con las instancias
que la cubren, y las que no tienen ninguna salen como `NOT_VERIFIABLE — sin
instancia en la spec`. La corrección es que el build agregue el ejemplo, y eso
va por el camino normal (`context/` o el prompt del build). La lista de
construcciones sale de código y no del inventario que arma el LLM del audit:
los elementos y atributos que declara el XSD de las extensiones, los
`schemeIdUri` que aparecen en los bloques, y los 75 elementos del índice
"Interfaces" de `context/03`. El inventario del audit (K-1…K-37) sirve sólo
para comparar en T-11.

Fragmentos: si su raíz es un elemento global de alguno de los dos XSD, se
valida; si no, `NOT_VERIFIABLE — fragmento sin raíz validable`. No se arma un
documento envolvente a mano: sería validar algo que la spec no dice. VAST es
IAB y queda `NOT_APPLICABLE`.

### D-2 — El XSD de la norma: el zip de ISO de la 6ta, fijado por contenido

Se usa `DASHSchema-6th-Ed.zip` de `standards.iso.org/iso-iec/23009/-1/ed-6/en/`,
identificado por su sha256 como la copia primaria (`context/00-normative-base.md`),
y no la URL genérica ni la rama de GitHub (las dos difieren, ver arriba). El
check sale `2` si el hash no coincide, como `check-normative-base.py`.

No se commitea: el LICENSE del zip remite a las ISO/IEC Directives y no dice
que se pueda redistribuir. Se baja a un cache fuera del repo, igual que la
copia primaria. Las dos dependencias de red del XSD (`xlink.xsd`, y `xml.xsd`
que éste importa) se resuelven contra copias locales, también fijadas por hash.

### D-3 — El XSD de las extensiones es un artefacto del build

Las extensiones nacen en el proceso que genera la spec, así que su XSD es
producto de ese proceso con el mismo rango que la spec: un archivo por
candidato, `output/v<N>-sgai-extension.xsd`, y al promover,
`dist/sgai-extension.xsd`. Es lo que un implementador baja para validar, y es
lo que los tests prueban contra DASH (D-4).

**Una sola fuente: el bloque de §5.10.1 de la spec.** El archivo no lo escribe
el LLM por separado: lo extrae un script, `bin/emit-extension-xsd.py`, del
candidato recién generado. La spec es lo que lee el WG y el XSD es parte de su
texto normativo; si el LLM escribiera las dos cosas habría dos copias que
coinciden sólo cuando el LLM no se equivoca. Extraído por código, el archivo es
idéntico al bloque por construcción.

El script sale `2` si el candidato no tiene un bloque `xs:schema` con
`targetNamespace="urn:svta:dash:sgai:2026"` o tiene más de uno, y `1` si el
bloque no compila junto con el XSD de ISO (E-1 de D-4). Corre como **Step
6.1**, inmediatamente después de cada paso que escribe un candidato: el build
de `build-all` (Step 6), `apply-context-delta` en el incremental y
`refine-spec` en el minor. Un candidato sin su XSD no sigue al Step 7.

**El check de identidad cubre donde sí pueden separarse**: después del build.
`check-dash-conformance` compara byte a byte el archivo con el bloque de la
spec que lo acompaña, en `output/` y en `dist/`, y da `FAIL` si difieren. Eso
agarra una promoción que copió uno y no el otro, o una edición a mano de
cualquiera de los dos. La promoción copia los dos juntos y reescribe
`dist/inputs.sha256` como hoy.

`CLAUDE.md` dice hoy que `output/` tiene "the candidate spec, and only that";
pasa a decir el candidato y su XSD, y `dist/` suma `sgai-extension.xsd` a sus
nombres sin versión.

### D-4 — Nivel 1: cómo se prueba con código que las extensiones son conformes con DASH

"Conformes con DASH" quiere decir lo que §5.2.1 pide: que lo nuestro cuelgue
sólo de los puntos de extensión que DASH abre, y que al sacarlo quede un
documento DASH válido. Ningún check solo prueba eso; lo prueban cuatro juntos,
todos de código:

- **E-1 — El XSD compila junto con el de ISO 6ta.** El nuestro importa
  `DASH-MPD.xsd` y usa tipos suyos (por ejemplo `svta:Tracking` es de tipo
  `dash:EventStreamType`). Compilar los dos juntos prueba que cada referencia a
  DASH resuelve y que no hay conflictos de partícula con los comodines
  `##other`. No prueba la colocación: un XSD que compila puede declarar
  elementos que después nadie puede poner en un lugar válido.
- **E-2 — El XSD no toca el namespace de DASH.** Chequeo estático sobre el
  archivo: `targetNamespace` distinto de `urn:mpeg:dash:schema:mpd:2011`, ni
  `xs:redefine`, ni `xs:override`, ni `xs:include` de DASH, ni declaraciones en
  su namespace. Con eso el XSD sólo puede agregar, nunca cambiar lo que DASH
  define.
- **E-3 — Cuelga sólo de los puntos de extensión.** Cada documento de ejemplo
  valida contra los dos XSD juntos. El XSD de ISO rechaza contenido ajeno en
  cualquier tipo sin comodín, y los comodines no son iguales en todos: por
  ejemplo `EventStreamType` admite elementos ajenos y no atributos, e
  `ImportedMpdType` atributos y no elementos (DR-2). Un elemento nuestro en un
  lugar que DASH no abre es un `FAIL` con su XPath. Cubre lo que los ejemplos
  ejercitan, y lo que no ejercitan sale como hallazgo de cobertura (D-1).
- **E-4 — Sacado lo nuestro, queda DASH válido.** La oración de §5.2.1 hecha
  test: *"the MPD shall be authored such that, after XML attributes or
  elements in the other namespaces than the DASH namespace are removed, the
  result is a valid XML document formatted according to that schema and that
  conforms to this document"*. A cada MPD se le sacan todos los elementos y
  atributos de otros namespaces, y lo que queda se valida contra el XSD de ISO
  solo y pasa por las reglas de D-5. Es también el invariante de
  `context/07` §4 y §5 (quitado C, el documento sigue parseando) en su parte
  que es propiedad del documento; la parte de que la reproducción siga es del
  nivel 3 (D-7).

Negativos para cada uno, en D-10: un tipo de DASH referenciado con un nombre
que no existe (E-1), una declaración en el namespace de DASH (E-2), un
atributo nuestro sobre un `EventStream`, cuyo tipo no admite atributos ajenos
(E-3), y un `AdaptationSet` puesto adentro de un elemento nuestro en un
`Period` que sin él queda sin ninguno (E-4).

### D-5 — Nivel 1: las reglas de la norma que el XSD no expresa, como código con su cita

Un catálogo de reglas en Python, una por oración de la norma, con el molde de
`tests-de-planos`: `id`, cláusula, la oración citada verbatim (verificada contra
la copia primaria; nunca páginas), a qué se aplica, y una función que devuelve
el resultado por instancia con su ubicación.

La fuente es lo que el proyecto ya curó contra la copia primaria, no una
lectura nueva de la norma. Primero `context/08-dash-extension-rules.md`, regla
por regla:

| Regla | Qué chequea el código | Lo que queda `NOT_VERIFIABLE`, y por qué |
|---|---|---|
| DR-1 | Un MPD que declara el perfil SPS (los sub-MPD de los ejemplos) tiene un solo `Period`, es `static`, y todo `@mimeType` es `video/mp4`, `audio/mp4` o `application/mp4` | Que el documento detrás de cada `ImportedMPD` sea ése: en los ejemplos la URL es de `example.com` y no resuelve |
| DR-2 | Es E-3 y E-4 de D-4 | — |
| DR-3 | Encuentra todo elemento del namespace de DASH anidado dentro de uno nuestro, con su XPath | Si un Player legacy "se espera" que lo procese: es intención del autor, no propiedad del documento. Sin ocurrencias, `PASS` |
| DR-4 | Todo URI de `@profiles` es uno que la 6ta define | Si una construcción nueva necesitaba un Interoperability Point: es una decisión de diseño |
| DR-5 | En una List MPD, los `AdaptationSet`/`Representation` en línea tienen `@mimeType` de RFC 4337, y los `@profiles` de cada `AdaptationSet` son subconjunto de los del `MPD` (Table 16) | — |
| DR-6 | Ningún `AdaptationSet`/`Representation` en todo el camino de la List MPD lleva un `@mimeType` no MP4 | Que los cuatro carriers sean los únicos: es una conclusión sobre la norma, no algo que un documento muestre |
| DR-7 | Todo `Period` con duración distinta de cero tiene al menos un `AdaptationSet` (Table 4) | — |
| DR-8 | Nada | Toda la regla: dice qué puede prometer el texto de la spec sobre un Player, no cómo es un documento |
| DR-9 | Un `EssentialProperty` con un esquema nuestro sobre un `AdaptationSet` o `Representation` del contenido principal es `FAIL` (lo descartaría un Player legacy); cada uso de los dos descriptores se lista con su padre | Que cada construcción diga cuál usa y por qué: es texto de la spec |
| DR-10 | El documento de resolución no lineal no es un `MPD`, ni declara `@type="list"` ni `@profiles` | — |

Después `context/07-backward-compat-checklist.md`: §1 (colocación) y §2
(punto de extensión) son E-3 y E-4; §4 (hermano requerido) es E-4; §5 (UC-07)
es E-4 más el nivel 3 (D-7); §6 (política de namespace) se chequea contra
`context/06-naming-and-namespaces.md`: todo elemento, atributo y esquema ajeno a
DASH está en un namespace o URN que 06 declara. §3 y §7 piden prosa en la spec
y quedan `NOT_VERIFIABLE`.

Por último, las oraciones citadas en las filas del audit publicado
(`dist/dash-conformance-audit.md`) que son propiedades de un documento: por
ejemplo K-4, *"A Period shall contain at most one EventStream element with the
same @schemeIdUri and @value"*; K-14, `@clip` sólo con `@maxDuration` (Table
62); K-15, la forma de la List MPD (§8.14). Se toman como fuente de oraciones,
no de veredictos.

Una regla cuya oración no se encuentra en la copia primaria no entra al
catálogo: va al informe de la task como `[fetch-failed]`, con lo que se buscó.
Un LLM puede proponer la lista de oraciones o el borrador de una regla; lo que
entra es código revisado, y lo que decide es su ejecución.

### D-6 — Nivel 2: los criterios de `context/03` sobre los documentos, como código

Un segundo catálogo, con el mismo molde que D-5, cuya cita es el criterio de
`context/03` y no una cláusula de la norma. Se escribe contra el `context/03`
de hoy, y se ajusta cuando llegue el v13.

**La población la da el índice "Interfaces", leído por código.** Cada uno de
los 75 elementos (I-MPD 27, I-REQ 16, I-RES 32) tiene una regla o un
`NOT_VERIFIABLE` con su motivo, y el parser es el de
`bin/check-context-interfaces.py`, importado y no reescrito, así los dos no
pueden leer el índice distinto. Además del índice entran los criterios sobre
los documentos que no definen un elemento sino una propiedad del conjunto
(cardinalidades, combinaciones prohibidas, orden), que son de `spec document`,
`Publisher` o `APS`: hasta 108 de los 165, el número exacto lo da la
clasificación de T-05.

**Sobre qué instancias corre**: los MPD de la spec para I-MPD, los documentos
de resolución (List MPD, `OverlayList`) para I-RES, y las URL de pedido de
ejemplo para I-REQ (parámetros reservados `sgai-*` y sus valores).

**Lo que no es de un documento** son los 57 criterios del Player y la parte del
Player de los mixtos: en este catálogo salen `NOT_VERIFIABLE — conducta del
Player, nivel 3`, y son la fuente de los tests de conducta (D-8). También sale
`NOT_VERIFIABLE` un criterio sobre un documento cuyo cumplimiento depende de
algo que el documento no lleva (el estado del Player, el reloj, el ADS).

**Una regla vieja no pasa callada.** Cada regla guarda el id del criterio y el
hash de su texto en `context/03`. Si el criterio se retiró (está en la tabla
"Retired identifiers") o su texto cambió, el check sale `2` y nombra las
reglas que hay que revisar. Es lo que hace que ajustar el catálogo al v13 sea
una lista y no una relectura.

### D-7 — Nivel 3a: el Player que no implementa la extensión

Cada MPD de la spec, con sus URLs de medios reescritas a un contenido de prueba
local, se carga en **dash.js v5.3.0 sin modificar** y en **Shaka v5.3.6** en
Chromium headless (Playwright). Lo que se mide es lo que pide `context/07` §5
(UC-07): el contenido principal arranca, avanza un tramo definido, y no hay
error fatal; los eventos de nuestros esquemas se ignoran. En Shaka, además,
que un `InsertPresentation` de la 6ta se reconozca: es el único de los dos que
implementa el lineal de la base.

- Contenido de prueba: generado con `ffmpeg` (está en la máquina; no hay MP4Box
  ni Shaka Packager) en perfil `isoff-live`, servido por un server local que la
  task levanta y baja por PID. Sin CDN externo: un test que depende de un
  tercero falla por el tercero.
- Versiones fijadas, como el tool de DASH-IF en `qualabs-video-replacement`: un
  Player que se mueve da veredictos que no se comparan entre corridas.
- Los MPD de anuncio (List MPD, sub-MPD SPS) se cargan sólo en el papel que
  tienen: un Player legacy no los pide nunca, así que no se le dan como
  manifiesto principal.
- **El harness se escribe con un adaptador por Player** (cargar, esperar un
  estado, leer eventos, pedidos de red y lo que está en pantalla), para que el
  Player de referencia de D-8 entre como un adaptador más y no como un harness
  nuevo.

### D-8 — Nivel 3b: el Player que implementa la extensión, sobre dash.js, en una fase propia antes del v13

Probar que un Player que soporta la extensión hace lo que la spec dice
necesita un Player que la soporte, y no existe ninguno. Hace falta una
**implementación de referencia**, y se hace **sobre dash.js** (decisión del
líder del proyecto: *"Dash.js tiene que ser la referencia"*). El Player legacy
de D-7 sigue siendo dash.js upstream sin modificar; la referencia es otra
compilación, del mismo dash.js fijado más lo nuestro.

**Los tests de conducta salen de los criterios del Player**, uno o más por
criterio, con el mismo molde: el criterio citado, lo que se carga (un MPD de la
spec y un APS de prueba que sirve sus documentos de resolución), lo que se
observa (pedidos de red con sus parámetros, beacons y su momento, eventos del
Player, la geometría de lo que se dibuja), y lo esperado. Lo que un test de
caja negra no puede observar sale `NOT_VERIFIABLE` con su motivo.

**Va en una fase propia, `reference-player`, entre ésta y el v13.** El orden
es `conformance-tests` → `reference-player` → `major-build-v13` (el líder del
proyecto: *"todos estos cambios tenemos que hacerlos ANTES de v13"*), y está
escrito en los `depends_on` de los dos ítems. Es una fase aparte y no tasks de
ésta porque es otro tipo de trabajo: esta fase escribe checks sobre
documentos, y la referencia es construir un Player, el prototipo que
`PROJECT.md` ya nombra como segundo entregable del proyecto, con decisiones de
diseño propias (dónde vive el código, cómo se engancha en dash.js) que no
están tomadas.

Su tamaño, ~10 tasks: su diseño, el APS de prueba, la clasificación de los ~60
criterios del Player en observables o no, la implementación por familias (el
lineal de la 6ta, que dash.js no trae; overlay y los 12 tokens de layout;
pausa; tracking y beacons; fallback y errores; el pedido con sus parámetros),
los tests de conducta, la demo y el cierre. No hay estimación en días que se
pueda respaldar: lo que se sabe es que su parte más grande es dibujar cada
layout.

**Cómo se absorbe el v13.** La referencia y sus tests se construyen contra el
`context/03` de hoy, y el v13 los va a mover: el incremental dejó sin ubicar
los carriers de beacons (R42, y R1.6, R5.9 y R47 que cuelgan de él), de audio
(R41) y otros (`roadmap/major-build-v13`). Eso no se resuelve esperando sino
con el mismo mecanismo que el nivel 2: cada test de conducta guarda el id y el
hash del texto de su criterio, y cuando el v13 cambia o retira un criterio, el
check sale `2` y lista qué tests de conducta, qué reglas del nivel 2 y, por
ellos, qué partes de la referencia hay que revisar. El v13 llega con los tres
niveles andando: lo que cambia aparece como una lista, y adaptar la referencia
a los carriers nuevos es trabajo del v13, que tiene esa lista para medirlo.

### D-9 — Dónde encaja en el pipeline, y el audit deja de ser juez

Dos steps nuevos:

- **Step 6.1 — Emitir el XSD de las extensiones** (D-3), después de cada paso
  que escribe un candidato.
- **Step 8.0 — Conformance tests**, antes del audit:
  `bin/check-dash-conformance.py output/v<N>-sgai-spec.md`, que lee el
  candidato y su XSD, corre los niveles 1 y 2, y escribe
  `output-analysis/v<N>-conformance-tests.md` (y el `.json` al lado). Salidas
  como el resto de `bin/`: `0` nada falla, `1` algo falla, `2` no se puede
  decir (falta el XSD de ISO, el hash no coincide, falta el XSD del
  candidato, una regla del nivel 2 quedó vieja), `64` línea de comandos mal.
  El nivel 3 entra con `--players`, con el mismo contrato, porque necesita
  node, Chromium y un server y tarda minutos; lo demás tarda segundos.

Los dos van en `build-all`, en `build-incremental` y en el camino minor, donde
ya se re-corren los tres análisis.

**El audit del LLM queda como complemento y nunca como evidencia de
conformidad.** Sigue corriendo después de los tests, y su papel cambia: deja
de poner veredictos `Conforming` / `Non-conforming` y pasa a señalar
sospechas, lugares donde cree que la norma se viola o es ambigua y que ningún
test cubre. Una sospecha no bloquea nada por sí misma; se vuelve un bloqueo
sólo cuando alguien la convierte en una regla y esa regla falla. El informe
del audit lo dice en su primera línea, y `check-promotable` deja de leer sus
filas como veredictos (D-13). Sacarlo del todo perdería al único lector que
busca lo que nadie pensó en testear; dejarlo como juez contradice el criterio
rector.

**El tool de DASH-IF entra como segundo auditor, sin su veredicto XSD.** Corre
sus módulos de schematron (Global Module) e IOP; el resultado de su módulo XSD
se descarta porque es el de la 5ta (medido arriba). Antes de usarlo sobre la
spec se corre sobre los 41 ejemplos de ISO de la 6ta: lo que el tool marque ahí
es su línea de base de falsos positivos, y se resta. Se reusa el build de
`qualabs-video-replacement/tools/dash-conformance/` subido a `v3.1.0`, y no se
construye otro.

### D-10 — Positivos y negativos: referencias que no salen de nosotros

Dos referencias, las dos independientes de lo que se verifica:

- **Positivos.** Para el nivel 1, los 41 ejemplos de ISO de la 6ta tienen que
  dar `PASS` o `NOT_APPLICABLE` en el XSD, en E-4 y en cada regla de D-5: una
  regla que falla sobre un ejemplo de la propia norma está mal escrita. Para
  el nivel 2 no hay una referencia externa equivalente: los positivos son los
  ejemplos de la spec, y una regla que falla sobre ellos es un hallazgo que se
  investiga en los dos sentidos (la regla o el ejemplo).
- **Negativos: un documento roto a propósito por regla y por cada E de D-4**,
  derivado de un ejemplo de la spec o de su XSD (que son nuestros y se pueden
  commitear; los de ISO no, D-2) con un solo cambio, y con el resultado
  esperado escrito al lado: la regla, la cláusula o el criterio, y el XPath
  donde tiene que fallar. El test pasa sólo si el `FAIL` sale de esa regla y en
  ese lugar; un negativo que queda verde, o que falla por otra regla, es un
  hallazgo. Las cuatro inyecciones medidas arriba son los primeros cuatro.

Los negativos son a la vez la campaña de mutación de las reglas y la mitad de
la demo (D-12).

### D-11 — Dónde vive el código

En `bin/`, como el resto de los checks del build: `emit-extension-xsd.py` y
`check-dash-conformance.py` como entradas, los dos catálogos en un módulo al
lado (`bin/conformance/`, con `dash/` para el nivel 1 y `spec/` para el nivel
2), y sus tests como `bin/test_*.py`, igual que
`test_check_context_interfaces.py`. El harness de Players en `bin/players/`
con su `package.json`, que fija las versiones. `CLAUDE.md` y
`prompts/README.md` se actualizan con los dos steps, los dos scripts y el
artefacto nuevo.

### D-12 — La demo: un comando, y el informe que muestra la cita y el lugar

`bin/check-dash-conformance.py` sin más argumentos que el candidato corre todo
lo de código de los niveles 1 y 2 (E-1 a E-4, el XSD, las dos familias de
reglas, el tool de DASH-IF; el nivel 3 con `--players`) y sale con su exit
code. Con `--demo` corre además los positivos y los negativos de D-10 y los
muestra lado a lado: cada negativo con lo que se rompió, la regla que lo
agarró, la oración citada y el XPath. Es lo que el líder del proyecto le puede
mostrar a alguien: el mismo comando, el mismo resultado cada vez, y un
documento roto que el código rechaza diciendo por qué.

### D-13 — La promoción exige los tests en verde, y el audit deja de bloquear

El criterio de promoción (el líder del proyecto, 2026-09-27) era
`check-promotable` en `0` y la comparación `BETTER THAN PUBLISHED`. Se suma
una tercera condición: **`check-dash-conformance` sale `0`** sobre el
candidato. Un `FAIL` de código bloquea por la ruta del pipeline; un
`NOT_VERIFIABLE` no bloquea y se lista con su número; **las filas del audit
del LLM dejan de bloquear**, y una sospecha suya bloquea sólo cuando es una
regla que falla (D-9). **Los Players informan y no bloquean** hasta tener
corridas estables. Decisión del líder del proyecto, 2026-11-23; T-09 la
escribe en `CLAUDE.md` y en `check-promotable`.

### D-14 — El issue a DASH-IF, con la medición del tool corriendo y con OK explícito

Que el tool de DASH-IF valida contra la 5ta se le avisa a DASH-IF, con un
issue en `Dash-Industry-Forum/DASH-IF-Conformance`. La evidencia es la de
T-08, con el tool corriendo sobre los 41 ejemplos de ISO, y no sólo su XSD.
Es hacia afuera: T-08 deja el borrador del issue en su evidencia y **no se
publica sin el OK explícito del líder del proyecto**, que decide en ese
momento quién lo manda.

## Lo que la fase no hace

- **SVTA 2053**, en ninguna versión. Decisión del líder del proyecto,
  2026-11-23.
- **Multiview** y **el perfil multi-asset** (`multi-asset-options-profile`,
  en espera del feedback de DASH-IF/MPEG). Si se agregan después, los tests
  los cubren por construcción: corren sobre lo que la spec publique.
- **La implementación de referencia sobre dash.js** y sus tests de conducta:
  son `reference-player`, la fase que sigue a ésta y va antes del v13 (D-8).
- **Publicar el issue a DASH-IF** sin el OK explícito del líder del proyecto
  (D-14).
- **Conformidad de segmentos.** Los ejemplos de la spec no traen medios; el
  contenido de D-7 es nuestro y su conformidad no dice nada de la spec.
- **Tocar `context/` o `dist/`**, ni promover nada. Correr los tests sobre
  `dist/` es medir, no publicar; el primer `dist/sgai-extension.xsd` llega con
  la próxima promoción.
- **Arreglar lo que los tests encuentren.** Un `FAIL` sobre la spec publicada
  es un hallazgo que se reporta y va por el camino normal (minor o v13).

## Tasks propuestas

Todas `who: agent`. El número de fase lo toma al arrancar (hoy sería 09).

| id | qué | nivel |
|---|---|---|
| T-01 | Extractor de bloques e inventario: los 84 bloques de un `vN-sgai-spec.md` y las URL de pedido de ejemplo, clasificados (MPD, List MPD, sub-MPD, OverlayList, fragmento, XSD, VAST, pedido), con su línea en el markdown | alto |
| T-02 | El XSD como artefacto (D-3): `bin/emit-extension-xsd.py`, sus salidas `1` y `2`, y el check de identidad archivo-bloque | alto |
| T-03 | Nivel 1, conformidad de las extensiones (D-4): E-1 a E-4, con el zip de ISO fijado por hash y cacheado fuera del repo | alto |
| T-04 | Nivel 1, reglas de la norma (D-5): DR-1…DR-10, `context/07` y las oraciones del audit, cada una re-citada contra la copia primaria; lo no verificable, `NOT_VERIFIABLE` con su motivo | alto |
| T-05 | Nivel 2, reglas de la spec (D-6): clasificación de los 165 criterios, una regla por elemento del índice y por criterio sobre documentos, y el chequeo de reglas viejas | alto |
| T-06 | Positivos y negativos (D-10): los 41 ejemplos de ISO en verde, un negativo commiteado por regla y por cada E con su resultado esperado, y la suite que los corre | alto |
| T-07 | Nivel 3a (D-7): contenido de prueba con ffmpeg, server local, dash.js upstream y Shaka fijados detrás de un adaptador por Player, el criterio de UC-07 como test | alto |
| T-08 | El tool de DASH-IF como segundo auditor: subir el build a `v3.1.0`, línea de base sobre los ejemplos de ISO, correr sobre la spec, descartar el XSD de la 5ta; el borrador del issue a DASH-IF (D-14), sin publicar | bajo |
| T-09 | Pipeline (D-9): Steps 6.1 y 8.0 en `build-all`, `build-incremental` y el camino minor; la promoción copia el XSD; `audit-dash-conformance.prompt` pasa de veredictos a sospechas; `check-promotable` y el criterio de promoción de `CLAUDE.md` según D-13; `CLAUDE.md` y `prompts/README.md` | alto |
| T-10 | La demo (D-12): `--demo` con positivos y negativos lado a lado, y el informe con la cita y el XPath de cada `FAIL`; corrida dos veces, mismo resultado byte a byte | bajo |
| T-11 | Primera corrida sobre `dist/sgai-spec.md`: el XSD emitido de su §5.10.1, el informe de los tres niveles, y la comparación construcción por construcción contra el veredicto del audit publicado | alto |
| T-12 | Cierre: REPORT.md, LOG y validador | mínimo |

T-11 es la medición de lo que la fase cambió: cada construcción que el audit
publicado dio por `Conforming` queda con evidencia de código (`PASS`), en
contra (`FAIL`, y entonces el LLM se había equivocado), o sin evidencia
(`NOT_VERIFIABLE`), y el número de cada una es el resultado.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Una regla mal transcripta da `PASS` sobre lo que viola | Su negativo (D-10) y la cita verificada contra la copia primaria o contra `context/03` (T-04, T-05) |
| Una regla demasiado estricta da `FAIL` sobre lo válido | Los 41 ejemplos de ISO como referencia en el nivel 1 (D-10); en el nivel 2, cada `FAIL` sobre un ejemplo se investiga en los dos sentidos |
| El XSD de las extensiones y el bloque de la spec divergen | Extraído por código del bloque (D-3), y el check de identidad en `output/` y `dist/` |
| El v13 cambia `context/03` y las reglas del nivel 2 quedan viejas | El hash del texto de cada criterio: el check sale `2` y lista las reglas a revisar (D-6) |
| ISO mueve o cambia el zip | El hash fijado: el check sale `2` y dice por qué (D-2) |
| Los Players cambian y el resultado se mueve | Versiones fijadas en `package.json` (D-7) |
| El tool de DASH-IF da falsos positivos en la 6ta además del XSD | La línea de base sobre los ejemplos de ISO (D-9); lo que no se pueda separar, se reporta y no bloquea |
| Un Player headless da resultados que varían entre corridas | No bloquea hasta tener corridas estables (D-13); T-07 lo corre tres veces y reporta la varianza |
