---
closed: 2026-11-23
---

# REPORT — fase 09, tests de conformidad de la spec

## 1. Resumen

La conformidad de la spec la decide ahora código, no un LLM. Un comando,
`bin/check-dash-conformance.py`, corre tres niveles con salida por exit code
(0/1/2/64), y `--demo` muestra los positivos y los rotos a propósito.

- **Nivel 1 — contra ISO/IEC 23009-1:2026.** El XSD de las extensiones es un
  artefacto del build (`bin/emit-extension-xsd.py`, idéntico al bloque de
  §5.10.1 por construcción). E-1 a E-4 prueban su conformidad con el XSD
  oficial de la 6ta (bajado de `standards.iso.org`, fijado por sha256).
  41 reglas de la norma, 28 con código, cada oración encontrada en la copia
  primaria.
- **Nivel 2 — contra `context/03`.** 196 reglas sobre los 165 criterios,
  48 con código; los 75 elementos del índice "Interfaces" cubiertos (contado
  por código) y cada regla fijada al hash del texto de su criterio, así lo que
  el v13 mueva sale como lista (exit 2).
- **Nivel 3a — Players legacy.** dash.js 5.3.0 upstream y Shaka 5.3.6
  reproducen los 20 MPD principales de la spec, tres corridas sin un cambio;
  Shaka reconoce el `InsertPresentation` de la 6ta en los 7 que lo traen.
- **Segundo auditor.** El tool de DASH-IF `v3.1.0`, construido y fijado en
  `bin/dashif/`, corre con `--dashif`; informa y no cambia el exit. Sobre los
  52 MPD publicados: 0 hallazgos propios de la spec, 32 sólo con hallazgos que
  también da en los ejemplos de ISO, 17 rechazados por su XSD de la 5ta
  (descartado).
- **Pipeline.** Step 6.1 (emitir el XSD) y Step 8.0 (los tests) en `build-all`,
  el incremental y el minor. El audit del LLM entrega sospechas (`S-<n>`) y no
  bloquea. La promoción exige `check-dash-conformance` en 0 (`CLAUDE.md`,
  `check-promotable`).

**Medición sobre la spec publicada (`dist/sgai-spec.md`, v12.6):** exit 1,
PASS 1155, FAIL 8, NOT_VERIFIABLE 273, NOT_APPLICABLE 1531. Nivel 1 sin
fallas: las extensiones publicadas son conformes con la 6ta en todo lo que el
código decide. Los 8 FAIL son de nivel 2: el XSD publicado no tiene carriers
que `context/` pide desde las fases 07 y 08 (`squeezeback-frame` ×3,
`@executeOnce` y `@startWithOffset` en la ventana overlay, `Tracking` por
opción) y el ejemplo G.3 (xml#40) deja Events de esquemas SGAI sin ventana.
Contra el audit del LLM (37 construcciones): 17 confirmadas por código, 10
parciales, 10 sin evidencia de código, 0 contradichas
(`tasks/T-11/comparison.md`).

## 2. Decisiones

ADR 0045 a 0058, una por decisión del diseño (D-1 a D-14), todas
`scope: phase-09`: lo que se testea (0045), el XSD de ISO fijado (0046), el
XSD de las extensiones como artefacto (0047), E-1 a E-4 (0048), las reglas de
la norma como código (0049), las de `context/03` por el índice (0050), los
Players legacy (0051), la referencia sobre dash.js en `reference-player`
antes del v13 (0052), el pipeline y el audit como complemento (0053),
positivos y negativos (0054), el código en `bin/` (0055), la demo (0056), la
promoción con los tests en verde (0057) y el issue a DASH-IF con OK explícito
(0058). En la ejecución, **ADR 0059**: E-4 es la validación XSD del MPD sin lo
ajeno, sin re-correr las reglas (medido: la re-corrida nunca encontró nada).

Decisiones del líder del proyecto registradas en el LOG del 2026-11-23: alcance
sólo DASH nativa (SVTA 2053 afuera), `multi-asset-options-profile` en espera
del feedback de DASH-IF/MPEG, los tres niveles, la referencia sobre dash.js, y
el orden `conformance-tests` → `reference-player` → `major-build-v13`.

## 3. Tasks

Las 12 `done`. T-01 a T-03, T-09 y T-10 las hizo el coordinador; T-04, T-05,
T-07, T-08 y la comparación de T-11 se delegaron a subagentes y se verificaron
al integrarlas (suites corridas, negativos, mutaciones, lectura de los
hallazgos contra `context/` y `dist/`). Evidencia por task en `tasks/T-NN/` y
en la columna de `TASKS.md`. Suites: `test_conformance_core` (9),
`test_conformance_dash` (6), `test_conformance_spec` (59),
`test_conformance_players` (6), `test_check_promotable_conformance` (5), todas
verdes; 84 negativos commiteados, todos atrapados por su regla.

## 4. Hilos abiertos

- **Los 8 FAIL sobre la spec publicada** son trabajo del v13: los carriers que
  faltan y el ejemplo G.3. Para G.3 hay que decidir cómo se presenta una
  ilustración "MPD visto por un Player legacy" para que no se lea como un MPD de
  Publisher (nada en el documento las distingue hoy).
- **Siete elementos de `context/03` sin carrier** en el XSD publicado (audio
  R41, beacons de slot R13.7 y de ocurrencia R42, R23.2, R44, R47, R48): salen
  `NOT_VERIFIABLE`; es la lista "Not placed" que el v13 ya tenía.
- **Cobertura sin ejemplo:** `RequestParam`, Advanced Linear, `sgai-ad-audio`,
  `sgai-ad-audio-allowed` y los MPD SPS de DR-1 (ningún ejemplo de ISO es SPS,
  así que DR-1a..i no tienen positivo externo); DR-5a/b nunca aplican.
- **Reglas fáciles que faltan** (de la comparación): tipo y default de
  `@earliestResolutionTimeOffset` y `@executeOnce` contra
  `AlternativeMPDEventType`; unicidad de `Event@id` dentro de `svta:Tracking`.
- **El issue a DASH-IF** está en borrador (`tasks/T-08/issue-draft.md`): no se
  publica sin el OK explícito del líder del proyecto (ADR 0058).
- **`reference-player`**, la fase siguiente: el harness de T-07 ya tiene el
  adaptador por Player para enchufarla.

## 5. Riesgos que se materializaron

- **El tool de DASH-IF da falsos positivos en la 6ta además del XSD:** sí. Su
  schematron no conoce `advanced-linear:2025`, `list:2024` ni `sps:2024`, falla
  al correr en G10, H1 y H2 y el CLI se cae en G11, G12 y G13-2. Mitigado como
  estaba previsto: línea de base sobre los 41 ejemplos de ISO, restada; no
  bloquea. Dos coincidencias de la resta son débiles (PROFILE y MPD-DUR sobre
  los SPS) y están escritas en `tasks/T-08/spec-run.md`.
- **Players headless variables:** no se materializó en resultados (ningún
  cambio entre tres corridas); la variación del tiempo de arranque (97 ms a 3,7
  s) se atribuye a carga de CPU y no se re-midió con la máquina libre.

## 6. Recomendaciones para la fase siguiente

- `reference-player` puede arrancar: su fuente de tests es el nivel 2 (las 56
  reglas `NOT_VERIFIABLE — conducta del Player`), y su harness es el de T-07.
- El v13 tiene que salir con los 8 FAIL resueltos para poder promoverse: con
  ADR 0057, un FAIL de código bloquea la promoción.
- Que el nivel 3a llegue al break: hoy cada Player avanza unos 8 s y no
  alcanza ninguna ventana; mover el arranque cerca de la primera ventana daría
  evidencia sobre K-12, K-33, K-34, K-36 y K-37, que hoy no tienen ninguna.

## 7. Correcciones post-ejecución

`grep -n "post-ejecuci" TASKS.md`: dos líneas.

- **T-03:** E-4 re-corría las reglas sobre el MPD sin lo ajeno y nunca agregó
  nada; se sacó (ADR 0059).
- **T-04:** el ejecutor dejó DR-3, DR-4 y DR-9 enteras como `NOT_VERIFIABLE`
  cuando el diseño tenía una mitad de código para cada una; se agregaron DR-3a,
  DR-4a y DR-9a con sus negativos.

Como medición: la de T-04 es de traspaso. El subagente no podía leer el
`DESIGN.md` y la ADR 0049 remite a su tabla en lugar de copiarla, así que
construyó la división desde `context/08`. Una ADR que delega su contenido a
un documento que el ejecutor tiene prohibido leer no alcanza como brief; el
despacho tiene que llevar la tabla. La de T-03 es del diseño: E-4 se
especificó sin medir si la re-corrida podía encontrar algo.

## 8. Revisión de documentación

- **`description` de `PHASE.md`:** reescrita como lo que la fase resultó ser.
- **`docs/arc42/`:** el proyecto no lo tiene; nada que corregir.
- **Resto de `docs/`:** no existe.
- **`README.md`:** `dist/` y `output/` con el XSD y los informes de los tests;
  `output-analysis/` con el Step 8.0 y el audit como complemento; la promoción
  apunta al criterio de `CLAUDE.md` (antes decía "no definido"); sección nueva
  "How to test conformance".
- **`CLAUDE.md` del proyecto:** layout, los scripts de `bin/` con qué cubre y
  qué no su verde, el criterio de promoción con su tercera condición, los
  re-runs del camino minor; `--dashif`; los ejemplos que escribían en `/dev/shm`
  pasan a `$XDG_RUNTIME_DIR/cto/`.
- **`SETUP.md` (runbook):** sección "Conformance tests": `uv`/lxml, el cache
  del XSD de ISO, `npm ci` de los Players, `bin/dashif/build.sh`.
- **`prompts/`:** `build-all`, `build-incremental`, `audit-dash-conformance`,
  `validate-spec`, `review-spec-details`, `refine-spec`,
  `compare-spec-versions` y `prompts/README.md`.
- **`.project/knowledge/`:** no existe; nada de esta fase lo necesita (lo
  transversal quedó en ADRs).
- **`CLAUDE.md` y `knowledge/` de la raíz de cto-assistant:** nada; la fase no
  cambió nada que aplique fuera del proyecto.
- **Registro:** las carpetas `tasks/T-NN/` de esta fase son evidencia de lo que
  se midió el 2026-11-23, no instrucciones vigentes; lo vigente está en `bin/`,
  `CLAUDE.md` y `SETUP.md`.
