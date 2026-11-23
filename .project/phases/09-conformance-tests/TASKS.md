# Tasks — conformance-tests

| id   | brief                                                                                   | status  | who   | plan | evidence |
| ---- | --------------------------------------------------------------------------------------- | ------- | ----- | ---- | -------- |
| T-01 | Los bloques de un candidato quedan extraídos y clasificados, con su línea               | done | agent | —    | `bin/conformance/extract.py`; `bin/test_conformance_core.py` (Extract)        |
| T-02 | El XSD de las extensiones sale como archivo del build, idéntico al bloque de §5.10.1    | done | agent | —    | `bin/emit-extension-xsd.py`; `bin/test_conformance_core.py` (Emitter)        |
| T-03 | Nivel 1: E-1 a E-4 dicen por código si las extensiones son conformes con DASH          | in-progress | agent | —    | —        |
| T-04 | Nivel 1: las reglas de la norma que el XSD no expresa corren como código con su cita    | in-progress | agent | —    | —        |
| T-05 | Nivel 2: los criterios de context/03 sobre documentos corren como código                | in-progress | agent | —    | —        |
| T-06 | Cada regla tiene su positivo y su negativo, y la suite los corre                        | pending | agent | —    | —        |
| T-07 | Nivel 3a: dash.js upstream y Shaka reproducen los MPD de la spec ignorando lo nuestro   | in-progress | agent | —    | —        |
| T-08 | El tool de DASH-IF corre como segundo auditor, con su línea de base y el borrador del issue | in-progress | agent | —    | —        |
| T-09 | El pipeline corre los tests, el audit deja de ser juez y la promoción los exige         | in-progress | agent | —    | `bin/check-promotable.py`, `bin/test_check_promotable_conformance.py`        |
| T-10 | La demo muestra positivos y negativos con la cita y el lugar, igual en cada corrida     | pending | agent | —    | —        |
| T-11 | La spec publicada tiene su informe de tres niveles y la comparación con el audit        | pending | agent | —    | —        |
| T-12 | Cierre: REPORT.md (Mode D), LOG y validador                                             | pending | agent | —    | —        |

Lo común a todas: el diseño está en `PHASE.md` y en las ADR 0045 a 0058; el
código va en `bin/` (ADR de D-11); `context/` y `dist/` no se tocan; nada se
publica ni se pushea; los temporales van a `$XDG_RUNTIME_DIR/cto/`; la copia
primaria de la norma está fuera del repo (`NORMATIVE_PDF_PATH` en `.env.agent`)
y no entra a él ni por cita de páginas: se citan oraciones.

---

## T-01 — Los bloques de un candidato quedan extraídos y clasificados
- **Objective:** dado un `v<N>-sgai-spec.md` (o `dist/sgai-spec.md`), hay un
  módulo que devuelve cada bloque ```` ```xml ```` y cada URL de pedido de
  ejemplo con su línea en el markdown y su clase (MPD, List MPD, sub-MPD SPS,
  OverlayList, fragmento con su raíz, XSD, VAST, pedido), y la lista de
  construcciones a cubrir sale de código (ADR de D-1).
- **What it must cover:** `bin/conformance/extract.py`. La clase sale del
  documento (raíz, namespace, `@type`, `@profiles`), no del texto alrededor.
  Sobre `dist/sgai-spec.md` hoy: 84 bloques, 52 MPD, 23 OverlayList, 1 XSD, 2
  VAST, 6 fragmentos. La lista de construcciones: elementos y atributos que
  declara el XSD del bloque de §5.10.1, `schemeIdUri` de los bloques, y los 75
  elementos del índice "Interfaces" de `context/03` (parser de
  `bin/check-context-interfaces.py`, importado). Sin dependencias.
- **Definition of done:** sobre `dist/sgai-spec.md` las cuentas coinciden con
  las de arriba, cada bloque trae su línea, y los tests de T-06 lo cubren.
- **nivel de verificación:** alto. Todo lo demás se apoya en este inventario;
  un bloque mal clasificado sale `NOT_APPLICABLE` en silencio.

## T-02 — El XSD de las extensiones sale como archivo del build
- **Objective:** `bin/emit-extension-xsd.py <candidato>` escribe
  `output/v<N>-sgai-extension.xsd` (o el destino que se le pase), idéntico
  byte a byte al bloque de §5.10.1; y el check de identidad archivo-bloque
  existe y puede fallar (ADR de D-3).
- **What it must cover:** salidas `0` escrito, `1` el bloque no compila junto
  con el XSD de ISO, `2` ningún bloque `xs:schema` con
  `targetNamespace="urn:svta:dash:sgai:2026"` o más de uno, `64` línea de
  comandos. El check de identidad vive en `check-dash-conformance` y compara
  el archivo con el bloque de la spec que lo acompaña. Usa T-01 y el cache del
  XSD de ISO de T-03 (si T-03 no está, la compilación sale `2`, no `0`).
  No escribe en `dist/` ni en `output/` reales en las pruebas: directorio
  temporal.
- **Definition of done:** sobre `dist/sgai-spec.md` emite un XSD que compila
  junto con el de ISO; las cuatro salidas se ven en tests; el check de
  identidad da `FAIL` con un byte cambiado.
- **nivel de verificación:** alto. Es un artefacto publicable que un
  implementador baja; uno distinto del bloque es invisible a simple vista.

## T-03 — Nivel 1: E-1 a E-4
- **Objective:** el código dice, sobre el XSD de las extensiones y cada MPD de
  la spec, si lo nuestro es conforme con DASH (ADR de D-2 y D-4).
- **What it must cover:** el zip `DASHSchema-6th-Ed.zip` de
  `standards.iso.org/iso-iec/23009/-1/ed-6/en/` fijado por sha256
  (`43b62f3d80a2cfca99d7530e8c092d032bf65736eb1ce176ae6bc8454feb1d28`), en un
  cache fuera del repo, con `xlink.xsd` y `xml.xsd` locales y fijados; hash
  que no coincide o cache ausente sin red → `2`. E-1 compilar juntos; E-2
  estático sobre el XSD (targetNamespace, `xs:redefine`/`xs:override`/
  `xs:include` de DASH, declaraciones en su namespace); E-3 validar cada
  documento contra los dos; E-4 quitar todo lo que no es de DASH y validar
  contra ISO solo. Resultado por instancia con XPath. Depende de T-01 y T-02.
- **Definition of done:** sobre los 41 ejemplos de ISO, E-3 y E-4 en `PASS`;
  sobre `dist/sgai-spec.md` cada E da un resultado por instancia; los cuatro
  negativos de E (T-06) dan `FAIL` en el lugar esperado.
- **nivel de verificación:** alto. Es la afirmación central de la fase, que lo
  nuestro es conforme con DASH, y corre sin nadie mirando.

## T-04 — Nivel 1: las reglas de la norma como código con su cita
- **Objective:** un catálogo (`bin/conformance/dash/`) con una regla por
  oración de la norma, cada una con id, cláusula, oración verbatim verificada
  contra la copia primaria y función que devuelve el resultado por instancia
  (ADR de D-5).
- **What it must cover:** DR-1…DR-10 de `context/08-dash-extension-rules.md`
  según la tabla de D-5 (incluido lo que queda `NOT_VERIFIABLE` y por qué),
  `context/07-backward-compat-checklist.md` §1, §2, §4, §6 (§3 y §7
  `NOT_VERIFIABLE`), y las oraciones de las filas de
  `dist/dash-conformance-audit.md` que son propiedad de un documento (K-4,
  K-14, K-15 y las que haya). Cada oración se busca en la extracción de la
  copia primaria (whitespace aplanado; antes de reportar un cero, la misma
  búsqueda sobre una frase que se sabe que está); la que no aparece no entra y
  va como `[fetch-failed]` en la evidencia. Ninguna línea de la extracción
  entra al repo salvo la oración citada. Depende de T-01 y T-03.
- **Definition of done:** cada regla del catálogo tiene la oración que la
  sostiene, encontrada en la copia primaria; las que no son código están
  listadas con su motivo; los 41 ejemplos de ISO dan `PASS` o
  `NOT_APPLICABLE` en todas.
- **nivel de verificación:** alto. Cada regla es un veredicto de conformidad
  que bloquea la promoción.

## T-05 — Nivel 2: los criterios de context/03 sobre documentos
- **Objective:** un catálogo (`bin/conformance/spec/`) con una regla o un
  `NOT_VERIFIABLE` motivado por cada elemento del índice "Interfaces" y por
  cada criterio sobre documentos, citando el criterio, y con el chequeo de
  reglas viejas (ADR de D-6).
- **What it must cover:** clasificar los 165 criterios de
  `context/03-requirements.md` (por quién los tiene; los 57 del Player y la
  parte del Player de los mixtos salen `NOT_VERIFIABLE — conducta del Player,
  nivel 3`). Instancias: MPD para I-MPD, List MPD y OverlayList para I-RES, URL
  de pedido para I-REQ. Cada regla guarda id y sha256 del texto del criterio;
  un criterio retirado (tabla "Retired identifiers") o con texto distinto →
  `2` con la lista. Un LLM puede proponer la clasificación; lo que entra es
  código, y la clasificación queda como tabla en la evidencia. Depende de T-01.
- **Definition of done:** los 75 elementos del índice tienen regla o
  `NOT_VERIFIABLE` motivado (la cobertura la cuenta el código, no la tabla);
  cambiar el texto de un criterio en una copia de `context/03` hace salir `2`
  con esa regla nombrada.
- **nivel de verificación:** alto. Mismo motivo que T-04, y además se
  mantiene contra un `context/03` que va a cambiar.

## T-06 — Positivos y negativos
- **Objective:** cada regla de T-03, T-04 y T-05 tiene un negativo commiteado
  que la hace fallar en el lugar esperado, y una suite los corre junto con los
  positivos (ADR de D-10).
- **What it must cover:** negativos en `bin/conformance/fixtures/negative/`,
  derivados de un ejemplo de la spec o de su XSD con un solo cambio, cada uno
  con su esperado al lado (regla, cita, XPath). Los cuatro de E y las cuatro
  inyecciones de `DESIGN.md` (sección "El instrumento encuentra") están entre
  ellos. Positivos: los 41 ejemplos de ISO (del cache, nunca commiteados) y
  los ejemplos de la spec. Suite en `bin/test_conformance*.py`, con
  `python3 -m unittest` o pytest como los tests que ya hay en `bin/`. Un
  negativo que queda verde o falla por otra regla es un hallazgo, no se
  silencia. Depende de T-03, T-04, T-05.
- **Definition of done:** la suite corre verde; romper la función de una regla
  (a mano, uno por regla, corriendo sólo sus tests) hace fallar su negativo.
- **nivel de verificación:** alto. Es la campaña de mutación de todo lo de
  arriba.

## T-07 — Nivel 3a: los Players legacy
- **Objective:** cada MPD principal de la spec, con medios reescritos a un
  contenido local, arranca y avanza en dash.js v5.3.0 upstream y en Shaka
  v5.3.6 sin error fatal, y el resultado sale por instancia (ADR de D-7).
- **What it must cover:** `bin/players/` con `package.json` que fija las dos
  versiones, Playwright con el Chromium ya instalado
  (`~/.cache/ms-playwright`), contenido de prueba generado con `ffmpeg` en
  `isoff-live` en un temporal (`~/.cache/cto-tmp/` si pasa ~100 MB), server
  local en un puerto libre que la task levanta y baja por su PID. Un
  adaptador por Player (cargar, esperar estado, leer eventos, red, pantalla).
  En Shaka, además, que un `InsertPresentation` se reconozca. Los MPD de
  anuncio no se cargan como principal. Tres corridas para medir la varianza.
  Entra en `check-dash-conformance --players`. Depende de T-01.
- **Definition of done:** informe por MPD y Player con `PASS`/`FAIL` y el
  motivo; un MPD roto a propósito (por ejemplo un `AdaptationSet` sin
  segmentos válidos) da `FAIL`; la varianza de las tres corridas reportada.
- **nivel de verificación:** alto. Es el test de compatibilidad legacy que
  R1.1 y UC-07 piden.

## T-08 — El tool de DASH-IF como segundo auditor
- **Objective:** el tool de DASH-IF `v3.1.0` corre sobre los MPD de la spec
  con su línea de base de falsos positivos restada, su veredicto XSD
  descartado, y el borrador del issue a DASH-IF queda escrito sin publicar
  (ADR de D-9 y D-14).
- **What it must cover:** el build de
  `../qualabs-video-replacement/tools/dash-conformance/` (README y `UPSTREAM`)
  se reusa como receta: el build para esta fase se hace con el pin a `v3.1.0`
  en un lugar propio, sin modificar el checkout de ese proyecto. Línea de base
  sobre los 41 ejemplos de ISO. El borrador del issue: la medición (cuáles de
  los 41 rechaza y por qué), en `tasks/T-08/`. Depende de T-01.
- **Definition of done:** el tool corre, la línea de base está medida, el
  informe separa lo que es del tool de lo que es de la spec, y el borrador
  existe. Si el build no es posible en esta máquina, la evidencia lo dice con
  la salida, y la fase sigue sin él.
- **nivel de verificación:** bajo. Es un segundo auditor que informa; lo que
  bloquea es el código propio.

## T-09 — El pipeline
- **Objective:** `build-all`, `build-incremental` y el camino minor corren el
  Step 6.1 y el Step 8.0; el audit del LLM señala sospechas y no veredictos; la
  promoción exige `check-dash-conformance` en `0` (ADR de D-9 y D-13).
- **What it must cover:** `prompts/build-all.prompt`,
  `prompts/build-incremental.prompt`, el camino minor descripto en
  `CLAUDE.md`, `prompts/3-post-spec/audit-dash-conformance.prompt`,
  `bin/check-promotable.py` (deja de leer las filas del audit como bloqueos y
  lee el informe de los tests), `CLAUDE.md` (layout de `output/` y `dist/`,
  los dos scripts, el criterio de promoción) y `prompts/README.md`. No se
  corre un build. `check-promotable` conserva sus salidas y su `--help`.
  Depende de T-02, T-03, T-04, T-05.
- **Definition of done:** los tests de `check-promotable` siguen verdes con el
  cambio y uno nuevo muestra que un `FAIL` del informe de tests bloquea y una
  fila `Non-conforming` del audit no; los prompts nombran los dos steps.
- **nivel de verificación:** alto. Cambia qué se publica y qué no.

## T-10 — La demo
- **Objective:** `bin/check-dash-conformance.py --demo` muestra positivos y
  negativos lado a lado, cada `FAIL` con lo que se rompió, la regla, la cita y
  el XPath, y da lo mismo en cada corrida (ADR de D-12).
- **What it must cover:** salida legible en una terminal; el informe markdown
  y el json. Dos corridas seguidas, diff vacío. Depende de T-06.
- **Definition of done:** la salida de dos corridas es idéntica byte a byte, y
  cada negativo aparece fallando donde su esperado dice.
- **nivel de verificación:** bajo. Es lo que una persona mira; la lógica de
  abajo ya la cubrió T-06.

## T-11 — La primera corrida sobre la spec publicada
- **Objective:** existe el informe de los tres niveles sobre
  `dist/sgai-spec.md` y la comparación construcción por construcción con
  `dist/dash-conformance-audit.md`: cuántas de las que el LLM dio por
  `Conforming` tienen `PASS`, `FAIL` o `NOT_VERIFIABLE`.
- **What it must cover:** el XSD emitido de su §5.10.1 y el informe van a
  `tasks/T-11/` (no a `dist/` ni a `output/`). Cada discrepancia con el audit,
  explicada: cuál de los dos se equivocó. Un `FAIL` sobre la spec publicada es
  un hallazgo que se reporta, no se arregla. Depende de T-01…T-09.
- **Definition of done:** el informe y la comparación están en `tasks/T-11/`
  con los números, y cada discrepancia tiene su explicación.
- **nivel de verificación:** alto. Es la medición de lo que la fase cambió.

## T-12 — Cierre: REPORT.md (Mode D), LOG y validador
- **Objective:** la fase queda cerrada con su `REPORT.md`.
- **What it must cover:** corre cuando todas las demás están `done` o
  `abandoned`. Mode D de create-project: REPORT con `closed:`, revisión de
  documentación, `description` reescrita, LOG, validador.
- **Definition of done:** `REPORT.md` escrito y el validador en verde.
- **nivel de verificación:** mínimo. Lo lee una persona.
