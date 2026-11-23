---
title: Tests de conformidad de la spec
description: "La conformidad de la spec la decide código: el XSD de las extensiones como artefacto del build y conforme con ISO/IEC 23009-1 6ta (E-1..E-4), 41 reglas de la norma y 196 de context/03 con su cita, 84 negativos, dash.js y Shaka reproduciendo los MPD, el tool de DASH-IF como segundo auditor, y la promoción atada a los tests; sobre la v12.6 publicada, 0 FAIL contra la norma y 8 contra context/03, y 0 contradicciones con el audit del LLM."
started: 2026-11-23
origin: "el líder del proyecto, 2026-11-23, hilo #sgai: «tal vez hay una parte del proceso que es justamente testear contra la norma», con la analogía de projects/tests-de-planos"
category: chore
---

# Tests de conformidad de la spec

El diseño, con lo medido antes de diseñar y las alternativas descartadas, está
en [`DESIGN.md`](DESIGN.md); las decisiones, en las ADR 0045 a 0058.

## Alcance

- **Nivel 1.** El XSD de las extensiones como artefacto del build
  (`output/v<N>-sgai-extension.xsd`, `dist/sgai-extension.xsd` al promover),
  extraído por código del bloque de §5.10.1, con su check de identidad. Su
  conformidad con DASH por E-1 a E-4 (compila con el XSD de ISO 6ta, no toca
  el namespace de DASH, cuelga sólo de los puntos de extensión, quitado lo
  nuestro queda DASH válido). Las reglas de la norma que el XSD no expresa
  como código con su cita: DR-1…DR-10, `context/07` y las oraciones del audit.
- **Nivel 2.** Los criterios de `context/03` sobre los documentos como código,
  con la población del índice "Interfaces" (75 elementos) y el hash del texto
  de cada criterio para detectar reglas viejas.
- **Nivel 3a.** dash.js v5.3.0 upstream sin modificar y Shaka v5.3.6, en
  Chromium headless, detrás de un adaptador por Player: el criterio de UC-07.
- El tool de DASH-IF (`v3.1.0`) como segundo auditor, sin su veredicto XSD de
  la 5ta; el borrador del issue a DASH-IF, sin publicar.
- Positivos (los 41 ejemplos de ISO) y negativos (uno por regla, commiteados),
  y la demo `--demo`.
- El pipeline: Step 6.1 (emitir el XSD) y Step 8.0 (los tests) en `build-all`,
  `build-incremental` y el camino minor; el audit del LLM pasa de veredictos a
  sospechas; el criterio de promoción suma los tests en `0` (`CLAUDE.md`,
  `check-promotable`).
- La primera corrida sobre `dist/sgai-spec.md` y su comparación con el audit
  publicado.

## Fuera de alcance

- SVTA 2053, multiview y el perfil multi-asset.
- La implementación de referencia sobre dash.js y sus tests de conducta: es
  `reference-player`, la fase siguiente, antes del v13.
- Conformidad de segmentos.
- Tocar `context/` o `dist/`, promover, o arreglar lo que los tests
  encuentren: un `FAIL` sobre la spec publicada es un hallazgo.
- Publicar el issue a DASH-IF sin el OK explícito del líder del proyecto.
- Push.

## Riesgos y mitigaciones

| Riesgo | Mitigación | Task |
|---|---|---|
| Una regla mal transcripta da `PASS` sobre lo que viola | Su negativo, y la cita verificada contra la copia primaria o `context/03` | T-04, T-05, T-06 |
| Una regla demasiado estricta da `FAIL` sobre lo válido | Los 41 ejemplos de ISO como referencia; en el nivel 2, cada `FAIL` sobre un ejemplo se investiga en los dos sentidos | T-06 |
| El XSD y el bloque de la spec divergen | Extraído por código, y el check de identidad | T-02 |
| El v13 cambia `context/03` | El hash del texto de cada criterio: el check sale `2` y lista qué revisar | T-05 |
| ISO cambia el zip | sha256 fijado: el check sale `2` | T-03 |
| Los Players cambian | Versiones fijadas | T-07 |
| El tool de DASH-IF da falsos positivos en la 6ta | Línea de base sobre los ejemplos de ISO; no bloquea lo que no se pueda separar | T-08 |
| Un Player headless varía entre corridas | No bloquea hasta corridas estables; tres corridas y su varianza | T-07 |

## Interesados

El líder del proyecto (aprueba, recibe la demo, el informe y el REPORT).
