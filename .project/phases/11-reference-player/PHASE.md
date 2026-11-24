---
title: Player de referencia
description: "Un Player que implementa la extensión, el dash.js 5.3.0 fijado más un módulo nuestro, y la batería opt-in que lo prueba: los tests de conducta de los 61 criterios observables de context/03 y los 22 vectores de UC."
started: 2026-11-23
origin: "el líder del proyecto, 2026-11-23, hilo #sgai: el testing en tres niveles («Me gusta los 3!!!») y «Dash.js tiene que ser la referencia»; diseño aprobado el mismo día: «Ok, construyamos pero que por defecto no se use porque es muy caro en tiempo»"
category: feature
depends_on: [conformance-tests, code-first-pipeline]
---

# Player de referencia

El diseño, con lo medido y las alternativas descartadas, está en
[`DESIGN.md`](DESIGN.md); las decisiones, en las ADR 0075 a 0087 (D-1 a
D-13).

## Alcance

- **La referencia** (`reference-player/`): un módulo sobre el `dist/` de
  dash.js 5.3.0 fijado, sin modificarlo, que implementa la extensión y, de la
  6ta, el lineal que piden los criterios y los vectores (insert y replace, la
  cola por PRT, List MPD, callbacks).
- **Los tests de conducta**: `spec-source/behaviour/`, un vector por criterio
  con el esquema de los de UC extendido, y un `index.yaml` con los
  `NOT_VERIFIABLE`. La población (76) se lee del catálogo del nivel 2; cada
  test guarda el hash de su criterio.
- **El ejecutor**: un adaptador `sgai` en `bin/players/`, el APS y los beacons
  como rutas de Playwright, las clases D1–D5 como perfiles, y
  `check-dash-conformance.py --behaviour`, que corre los tests de criterio y
  los 22 vectores de UC.
- **Opt-in**: nada la corre por defecto, y un test lo verifica (ADR 0087).
- **La demo**: una página local y la grabación de una sesión con lineal,
  overlay y pausa.

## Fuera de alcance

- Modificar dash.js o mandarle un PR.
- La calidad del empalme lineal, el rendimiento, DRM, dispositivos reales,
  otro navegador que Chromium.
- Los 8 criterios que una prueba de caja negra no decide y los 7 sin carrier
  (son del v13).
- `context/`, `dist/`, y `spec-source/` fuera de `behaviour/` y del esquema de
  vectores. Un hueco de la spec es un hallazgo, no un cambio.
- VAST, SCTE-35, SDK de verificación, métricas.
- Push: nunca sin el líder del proyecto.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| La API pública de dash.js no alcanza para el lineal | T-01 lo prueba primero; si no alcanza, fork acotado a ese punto, y se avisa al líder porque cambia el plan |
| Los tiempos en Chromium headless varían | `tolerance` de los vectores; un test inestable se reporta como inestable, no como PASS |
| R16.1 pide "within one rendering frame" | `requestAnimationFrame`; si headless no da frames confiables, `NOT_VERIFIABLE` con motivo |
| La batería tarda horas | concurrencia y contenido corto; T-09 la mide; opt-in (ADR 0087) |
| La referencia pasa sus propios tests | los tests de cada familia se escriben antes y se ven fallar (ADR 0085) |
| Dibujar cada layout es la parte más grande | T-07 propia, con tests de geometría |

## Stakeholders

El líder del proyecto aprueba; la audiencia asumida de la demo es el WG de
DASH, a confirmar cuando exista.
