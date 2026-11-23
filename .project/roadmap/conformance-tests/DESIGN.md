---
description: "Tests reales de conformidad contra ISO/IEC 23009-1 (6ta edición): los XML de la spec validados con el XSD oficial y el nuestro, las reglas de la norma que el XSD no expresa como código con su cita, y los MPD de ejemplo reproducidos en dash.js y Shaka."
status: designing
category: chore
origin: "el líder del proyecto, 2026-11-23, hilo #sgai: «tal vez hay una parte del proceso que es justamente testear contra la norma», con la analogía de projects/tests-de-planos"
---

# Tests de conformidad contra la norma DASH

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

Por eso la fase pone la evidencia de conformidad en tests que se corren y que
pueden fallar, como en `projects/tests-de-planos`: una regla por requerimiento
de la norma, con su id, la cláusula, la oración citada, y un resultado por
instancia, `PASS` / `FAIL` / `NOT_VERIFIABLE` (con el motivo) /
`NOT_APPLICABLE`, y dónde falla (bloque de la spec, línea y XPath). **El
veredicto lo da siempre código determinístico**: el XSD, las reglas como
código, el tool de DASH-IF, los Players. Un LLM puede ayudar a escribir un
test; nunca decide si algo pasa. Lo que sólo se puede juzgar con un LLM sale
`NOT_VERIFIABLE` y no se cuenta como pasado.

Y tiene que ser demostrable: un comando que corre todo y sale con un exit
code, y casos negativos, documentos rotos a propósito que el test hace fallar
con la cita y el lugar, además de los positivos.

El alcance lo fijó el líder del proyecto el 2026-11-23: **sólo la norma DASH
nativa**, la edición que declara `context/00-normative-base.md`
(ISO/IEC 23009-1:2026, 6ta edición). SVTA 2053 queda afuera; son trabajos en
paralelo que no se tocan.

## Lo que se verificó antes de diseñar

Las tres ideas de partida venían "a verificar y no a asumir". Esto se midió el
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

**3. dash.js y Shaka sirven, en papeles distintos.**

- **dash.js v5.3.0** (2026-11-04): su tabla de features dice "Server Guided Ad
  Insertion — Not supported" (`docs/site/pages/features/index_features.md`).
  Para nuestra spec es el Player legacy.
- **Shaka v5.3.6** (2026-11-20): `lib/ads/dash_interstitial_parser.js`
  reconoce `urn:mpeg:dash:event:alternativeMPD:insert:2025` y `…:replace:2025`
  y lee `InsertPresentation`/`ReplacePresentation` (cita
  *"ISO/IEC 23009-1:2026"*). Para el lineal de la 6ta es un Player que lo
  entiende; para nuestra extensión no lineal, otro legacy.

Búsqueda: `gh api search/code` sobre cada repo con `alternativeMPD`,
`InsertPresentation` e `ImportedMPD`. En dash.js la búsqueda de código no
encontró nada; para no leer un cero como resultado se corrió la misma búsqueda
con `callback:2015`, que dash.js implementa, y dio 2. Lo que respalda "no lo
soporta" es la tabla de features, no el cero.

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

## Decisiones

### D-1 — Qué se testea: lo que la spec publica, no un MPD aparte

El sujeto de los tests son los documentos que la spec da como ejemplo, sacados
de su markdown (los 84 bloques ```` ```xml ````), y las construcciones que
define. No se mantienen MPD de prueba escritos a mano en paralelo: serían una
segunda copia de lo que la spec dice, que se desincroniza en el primer build.

Lo que la spec define y no tiene ejemplo es un hallazgo de cobertura, no un
test que falta escribir: el informe lista cada construcción que la spec define
con las instancias que la cubren, y las que no tienen ninguna
salen como `NOT_VERIFIABLE — sin instancia en la spec`. La corrección es que el
build agregue el ejemplo, y eso va por el camino normal (`context/` o el prompt
del build), no por la fase. La lista de construcciones también sale de código
y no del inventario que arma el LLM del audit: los elementos y atributos que
declara el XSD de §5.10.1 y los `schemeIdUri` que aparecen en los bloques. El
inventario del audit (K-1…K-37) sirve sólo para comparar en T-09.

Fragmentos: si su raíz es un elemento global de alguno de los dos XSD, se
valida; si no, `NOT_VERIFIABLE — fragmento sin raíz validable`. No se arma un
documento envolvente a mano: sería validar algo que la spec no dice. VAST es
IAB y queda `NOT_APPLICABLE`.

### D-2 — El XSD de la norma: el zip de ISO de la 6ta, fijado por contenido

Se usa `DASHSchema-6th-Ed.zip` de `standards.iso.org/iso-iec/23009/-1/ed-6/en/`,
identificado por su sha256 como la copia primaria (`context/00-normative-base.md`),
y no la URL genérica ni la rama de GitHub (las dos difieren, ver arriba). El
check falla si el hash no coincide, como `check-normative-base.py`.

No se commitea: el LICENSE del zip remite a las ISO/IEC Directives y no dice
que se pueda redistribuir. Se baja a un cache fuera del repo, igual que la
copia primaria. Las dos dependencias de red del XSD (`xlink.xsd`, y `xml.xsd`
que éste importa) se resuelven contra copias locales, también fijadas por hash.

### D-3 — El XSD de la extensión: el que la spec publica

El XSD de `urn:svta:dash:sgai:2026` es el bloque de §5.10.1 de la spec, sacado
del mismo markdown. No se escribe uno aparte en el repo: el de la spec es
contenido normativo nuestro, y uno mantenido al lado sería otra copia. Si el
bloque falta o no compila, el check sale `2` (no se puede decir), no `0`.

Las dos se cargan juntas, así el `lax` de DASH valida nuestros elementos cuando
están declarados (medido arriba: sin él, un atributo inventado pasa).

### D-4 — Las reglas que el XSD no expresa, como código con su cita

Un catálogo de reglas en Python, una por oración de la norma, con el molde de
`tests-de-planos`: `id`, cláusula, la oración citada verbatim (verificada contra
la copia primaria; nunca páginas), a qué se aplica, y una función que devuelve
el resultado por instancia con su ubicación.

La lista inicial sale de lo que el proyecto ya curó contra la copia primaria, no
de una lectura nueva de la norma:

- `context/08-dash-extension-rules.md` (DR-1…DR-9): por ejemplo DR-1 (lo que
  llega por `ImportedMPD` cumple el perfil SPS, §8.15) y DR-7 (un `Period` de
  duración no nula tiene al menos un `AdaptationSet`, Table 4).
- Las oraciones citadas en las filas `Conforming` del audit publicado
  (`dist/dash-conformance-audit.md`): por ejemplo K-4, *"A Period shall contain
  at most one EventStream element with the same @schemeIdUri and @value"*;
  K-14, `@clip` sólo con `@maxDuration` (Table 62); K-15, la forma de la List
  MPD (§8.14).
- `context/07-backward-compat-checklist.md` §1, §2, §4 y §6: colocación,
  punto de extensión, hermano requerido y política de namespace.

Cada regla nace con su caso negativo (D-7). Una regla cuya oración no se
encuentra en la copia primaria no entra al catálogo: va al informe de la task
como `[fetch-failed]`, con lo que se buscó. Un LLM puede proponer la lista de
oraciones o el borrador de una regla; lo que entra es código revisado, y lo
que decide es su ejecución.

**Lo que no es código sale `NOT_VERIFIABLE`, con su motivo, en el mismo
informe**: las obligaciones de comportamiento del Player que ningún Player de
D-5 ejercita (K-33, K-34, K-36, K-37) y las lecturas ambiguas de la norma (los
`Marginal`: K-17, K-29, K-35). No se cuentan como pasadas ni se delegan a un
veredicto del audit: el informe dice cuántas construcciones tienen evidencia
de código y cuántas no.

### D-5 — Los Players: dash.js como legacy, Shaka como lector de la 6ta

Cada MPD de la spec, con sus URLs de medios reescritas a un contenido de prueba
local, se carga en dash.js v5.3.0 y en Shaka v5.3.6 en Chromium headless
(Playwright). Lo que se mide es lo que pide `context/07` §5 (UC-07, el test de
compatibilidad legacy): el contenido principal arranca, avanza un tramo
definido, y no hay error fatal; los eventos de nuestros esquemas se ignoran.
En Shaka, además, que un `InsertPresentation` de la 6ta se reconozca (el lineal
de la base).

- Contenido de prueba: generado con `ffmpeg` (está en la máquina; no hay MP4Box
  ni Shaka Packager) en perfil `isoff-live`, servido por un server local que la
  task levanta y baja por PID. Sin CDN externo: un test que depende de un
  tercero falla por el tercero.
- Versiones fijadas, como el tool de DASH-IF en `qualabs-video-replacement`: un
  Player que se mueve da veredictos que no se comparan entre corridas.
- Los MPD de anuncio (List MPD, sub-MPD SPS) se cargan sólo en el papel que
  tienen: un Player legacy no los pide nunca, así que no se le dan como
  manifiesto principal.

### D-6 — Dónde encaja en el pipeline: un Step 8.0 antes del audit, y el audit deja de ser juez

Un step nuevo antes del audit, **Step 8.0 — DASH conformance tests**:
`bin/check-dash-conformance.py output/v<N>-sgai-spec.md`, que escribe
`output-analysis/v<N>-dash-conformance-tests.md` (y el `.json` al lado).
Salidas como el resto de `bin/`: `0` nada falla, `1` algo falla, `2` no se
puede decir (falta el XSD, el hash no coincide, el bloque de §5.10.1 no
compila), `64` línea de comandos mal. Los Players entran con `--players`,
con el mismo contrato, porque necesitan node, Chromium y un server y tardan
minutos; el XSD y las reglas tardan segundos.

**El audit del LLM queda como complemento y nunca como evidencia de
conformidad.** Sigue corriendo después de los tests, y su papel cambia: deja
de poner veredictos `Conforming` / `Non-conforming` y pasa a señalar
sospechas, lugares donde cree que la norma se viola o es ambigua y que ningún
test cubre. Una sospecha no bloquea nada por sí misma; se vuelve un bloqueo
sólo cuando alguien la convierte en una regla de D-4 y esa regla falla. El
informe del audit lo dice en su primera línea, y `check-promotable` deja de
leer sus filas como veredictos (ver P-1). Sacarlo del todo perdería al único
lector que busca lo que nadie pensó en testear; dejarlo como juez contradice
el criterio rector.

**El tool de DASH-IF entra como segundo auditor, sin su veredicto XSD.** Corre
sus módulos de schematron (Global Module) e IOP; el resultado de su módulo XSD
se descarta porque es el de la 5ta (medido arriba). Antes de usarlo sobre la
spec se corre sobre los 41 ejemplos de ISO de la 6ta: lo que el tool marque ahí
es su línea de base de falsos positivos, y se resta. Se reusa el build de
`qualabs-video-replacement/tools/dash-conformance/` subido a `v3.1.0`, y no se
construye otro.

Mismo step en `build-incremental.prompt` y en el camino minor (después del
refine), donde ya se re-corren los tres análisis.

### D-7 — Positivos y negativos: referencias que no salen de nosotros

Dos referencias, las dos independientes de lo que se verifica:

- **Positivos: los 41 ejemplos de ISO de la 6ta** tienen que dar `PASS` o
  `NOT_APPLICABLE` en el XSD y en cada regla del catálogo. Una regla que falla
  sobre un ejemplo de la propia norma está mal escrita.
- **Negativos: un documento roto a propósito por regla**, derivado de un
  ejemplo de la spec (que es nuestro y se puede commitear; los de ISO no, D-2)
  con un solo cambio, y con el resultado esperado escrito al lado: la regla,
  la cláusula y el XPath donde tiene que fallar. El test pasa sólo si el
  `FAIL` sale de esa regla y en ese lugar; un negativo que queda verde, o que
  falla por otra regla, es un hallazgo. Las cuatro inyecciones medidas arriba
  son los primeros cuatro.

Los negativos son a la vez la campaña de mutación de las reglas y la mitad de
la demo (D-9).

### D-8 — Dónde vive el código

En `bin/`, como el resto de los checks del build: `check-dash-conformance.py`
como entrada, el catálogo en un módulo al lado (`bin/dash_conformance/`), y sus
tests como `bin/test_*.py`, igual que `test_check_context_interfaces.py`. El
harness de Players en `bin/players/` con su `package.json`, que fija las dos
versiones. `CLAUDE.md` y `prompts/README.md` se actualizan con el step y los
dos checks.

### D-9 — La demo: un comando, y el informe que muestra la cita y el lugar

`bin/check-dash-conformance.py` sin más argumentos que el candidato corre todo
lo de código (XSD, reglas, el tool de DASH-IF; los Players con
`--players`) y sale con su exit code. Con `--demo` corre además los positivos
y los negativos de D-7 y los muestra lado a lado: cada negativo con lo que se
rompió, la regla que lo agarró, la oración citada de la norma y el XPath. Es
lo que el líder del proyecto le puede mostrar a alguien: el mismo comando, el
mismo resultado cada vez, y un documento roto que el código rechaza diciendo
por qué.

## Lo que la fase no hace

- **SVTA 2053**, en ninguna versión. Decisión del líder del proyecto,
  2026-11-23.
- **Multiview** y **el perfil multi-asset** (`multi-asset-options-profile`,
  en espera del feedback de DASH-IF/MPEG). Si se agregan después, los tests
  los cubren por construcción: corren sobre lo que la spec publique.
- **Conformidad de segmentos.** Los ejemplos de la spec no traen medios; el
  contenido de D-5 es nuestro y su conformidad no dice nada de la spec.
- **Las obligaciones de comportamiento del Player que ningún Player de D-5
  ejercita**: salen `NOT_VERIFIABLE` (D-4), no se escriben Players de prueba
  propios para ejercitarlas.
- **Las reglas propias de la spec más allá de su XSD** (obligaciones del
  Publisher, del APS o del ADS sobre los documentos), salvo las de
  `context/07` que la fase ya toma. Ver P-3.
- **Tocar `context/` o `dist/`**, ni promover nada. Correr los tests sobre
  `dist/` es medir, no publicar.
- **Arreglar lo que los tests encuentren.** Un `FAIL` sobre la spec publicada
  es un hallazgo que se reporta y va por el camino normal (minor o v13).

## Tasks propuestas

Todas `who: agent`. El número de fase lo toma al arrancar (hoy sería 09).

| id | qué | nivel |
|---|---|---|
| T-01 | Extractor de bloques e inventario: los 84 bloques de un `vN-sgai-spec.md`, clasificados (MPD, List MPD, sub-MPD, OverlayList, fragmento, XSD, VAST), con su línea en el markdown | alto |
| T-02 | Validación XSD: el zip de ISO fijado por hash y cacheado fuera del repo, el XSD de §5.10.1 de la spec, los dos juntos; las dos referencias de D-7 | alto |
| T-03 | Catálogo de reglas (D-4): cada oración re-citada contra la copia primaria, una regla por oración; lo no verificable por código, listado como `NOT_VERIFIABLE` con su motivo | alto |
| T-04 | Positivos y negativos (D-7): los 41 ejemplos de ISO en verde, un negativo commiteado por regla con su resultado esperado (regla, cláusula, XPath), y la suite que los corre | alto |
| T-05 | Harness de Players (D-5): contenido de prueba con ffmpeg, server local, dash.js y Shaka fijados, el criterio de UC-07 como test | alto |
| T-06 | El tool de DASH-IF como segundo auditor: subir el build a `v3.1.0`, línea de base sobre los ejemplos de ISO, correr sobre la spec, descartar el XSD de la 5ta | bajo |
| T-07 | Pipeline: Step 8.0 en `build-all`, `build-incremental` y el camino minor; `audit-dash-conformance.prompt` pasa de veredictos a sospechas (D-6); `check-promotable` según P-1; `CLAUDE.md` y `prompts/README.md` | alto |
| T-08 | La demo (D-9): `--demo` con positivos y negativos lado a lado, y el informe con la cita y el XPath de cada `FAIL`; corrida dos veces, mismo resultado byte a byte | bajo |
| T-09 | Primera corrida sobre `dist/sgai-spec.md`: el informe, y la comparación construcción por construcción contra el veredicto del audit publicado (dónde coinciden, dónde no y por qué) | alto |
| T-10 | Cierre: REPORT.md, LOG y validador | mínimo |

T-09 es la medición de lo que la fase cambió: cada construcción que el audit
publicado dio por `Conforming` queda con evidencia de código (`PASS`), en
contra (`FAIL`, y entonces el LLM se había equivocado), o sin evidencia
(`NOT_VERIFIABLE`), y el número de cada una es el resultado.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Una regla mal transcripta da `PASS` sobre lo que viola | Su mutación (D-7) y la cita verificada contra la copia primaria (T-03) |
| Una regla demasiado estricta da `FAIL` sobre lo válido | Los 41 ejemplos de ISO como referencia (D-7) |
| ISO mueve o cambia el zip | El hash fijado: el check sale `2` y dice por qué (D-2) |
| Los Players cambian y el resultado se mueve | Versiones fijadas en `package.json` (D-5) |
| El tool de DASH-IF da falsos positivos en la 6ta además del XSD | La línea de base sobre los ejemplos de ISO (D-6); lo que no se pueda separar, se reporta y no bloquea |
| v13 cambia la spec en el medio y los tests se escriben contra v12.6 | Los tests son reglas sobre lo que la spec publique, no sobre v12.6; T-09 corre sobre lo que esté en `dist/` |
| Un Player headless da resultados que varían entre corridas | No bloquea hasta tener corridas estables (P-1); T-05 lo corre tres veces y reporta la varianza |

## Preguntas abiertas

**P-1 — ¿Los tests bloquean la promoción?** El criterio de promoción (el líder
del proyecto, 2026-09-27) es `check-promotable` en `0` y la comparación
`BETTER THAN PUBLISHED`. Recomendación: **sumar que `check-dash-conformance`
salga `0`, y que las filas del audit del LLM dejen de bloquear**: un `FAIL` de
código bloquea por la ruta del pipeline; un `NOT_VERIFIABLE` no bloquea y se
lista con su número; una sospecha del audit no bloquea hasta que es una regla
que falla (D-6). Los Players informan y no bloquean hasta tener corridas
estables.

**P-2 — ¿El v13 espera a esta fase?** Recomendación: **sí**, agregar
`conformance-tests` a `depends_on` de `major-build-v13`. La fase no depende de
document-first ni de multiview y puede correr ya, así el v13 es el primer build
mayor que sale con tests.

**P-3 — Las reglas propias de la spec sobre documentos (más allá del XSD).**
Recomendación: **fuera de esta fase**, como ítem nuevo (`spec-document-rule-tests`,
`idea`), porque su fuente es `context/03`, que document-first acaba de
reescribir y el v13 va a mover. Esta fase toma de nuestra spec sólo su XSD y lo
de `context/07`.

**P-4 — Avisarle a DASH-IF que el tool valida contra la 5ta.** Es hacia afuera:
un issue en `Dash-Industry-Forum/DASH-IF-Conformance` con la medición de los 8
ejemplos de ISO rechazados. Recomendación: **sí, después de T-06**, que lo mide
con el tool corriendo y no sólo con su XSD; lo manda quien el líder del
proyecto diga.
