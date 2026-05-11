---
name: SGAI for MPEG-DASH
slug: sgai-for-mpeg-dash
description: >
  Diseñar una norma completa de Server-Guided Ad Insertion (SGAI) para
  MPEG-DASH que cubra **linear y non-linear ads**, extendiendo
  MPEG-DASH 6th edition. Linear SGAI ya existe en 6th edition
  (InsertPresentation / ReplacePresentation / ListMPD) y se absorbe
  como baseline; el delta principal de diseño es la extensión
  non-linear (overlays, pause ads, L-shapes, banners, side-by-side,
  fullscreen interactive layers) que convive con el flujo linear bajo
  la misma arquitectura. Output dual: spec (working doc compartido
  con industria) + prototipo funcional. Colaboración con SVTA Ads WG
  y contribuidores de MPEG-DASH (Alex Giladi de Netflix, Thasso de
  Castlabs, Thomas Stockhammer chair de MPEG-DASH).
status: ongoing
type: research
owner: nicolas-levy
started: 2026-05-06
last_update: 2026-05-11
tags: [dash, sgai, non-linear-ads, mpeg, comcast, svta, overlays, dynamic-presentation, prototype, spec, server-guided-ads]
related_processes: [preparacion-working-group]
related_wgs: [comcast-sgai, svta-ads]
---

# SGAI for MPEG-DASH

Hub del proyecto. El contenido sustantivo vive en archivos
referenciados desde acá — este `PROJECT.md` es solo navegación + fases.

## Objetivo y motivación

Diseñar una **norma completa de Server-Guided Ad Insertion (SGAI)
para MPEG-DASH** que cubra **linear y non-linear ads** como una sola
extensión coherente de **MPEG-DASH 6th edition**.

- **Linear** ya existe en 6th edition (`InsertPresentation` /
  `ReplacePresentation` resolviendo un `ListMPD` devuelto por un Ad
  Decision Server externo). La norma absorbe ese mecanismo como
  **baseline**, lo clarifica, y puede sumar extensiones menores donde
  el gap analysis lo justifique.
- **Non-linear** es el **delta principal de diseño**: cubrir
  superficies non-linear (overlays, side-by-side, pause ads,
  L-shapes, banners, corner bugs, fullscreen interactive layers)
  reutilizando el mismo patrón — *MPD event → resolution document →
  Player composes the result* — sin fragmentar la arquitectura.

El output final es una sola spec SGAI que un implementador puede
seguir para cubrir ambos casos.

## Output esperado

Doble entregable:

1. **Spec técnica completa** de SGAI para MPEG-DASH (linear +
   non-linear), escrita colaborativamente en un Google Doc compartido
   con la industria. Destino: aterrizar en el **MPEG-DASH WG** como
   starting point de una extensión formal del standard.
2. **Prototipo funcional** que demuestra la propuesta end-to-end sobre
   un DASH player real, con coexistencia de linear y non-linear ad
   slots en la misma sesión de playback.

## Stakeholders

A nivel organizaciones y roles públicos (sin info personal interna —
ver `knowledge/output-policy.md`):

- **Qualabs Working Group** (interno) — WG semanal que avanza spec y
  prototipo. Roles públicos relevantes: Chief Solution Architect
  (lead técnico + representación en SVTA Ads WG), CTO Nicolás Levy
  (customer relationship + posicionamiento estratégico en MPEG /
  SVTA). El modelo de actores técnicos formal vive en
  `spec/02-actors.md`.
- **Comcast** — sponsor y customer principal del WG que produjo el
  SGAI linear de DASH 6th edition. Funda y prioriza la extensión
  non-linear.
- **SVTA Advertisement WG** — venue de socialización fuera de
  Comcast. Cadence y slot por arreglar.
- **DASH Industry Forum (DASH-IF)** — interop y guidelines sobre la
  spec base.
- **MPEG-DASH WG** (MPEG Systems WG que hosts DASH) — standards body
  formal. Chair: **Thomas Stockhammer**.
- **Contribuidores externos identificados**: Alex Giladi (Netflix,
  reviewer probable a v0.x estable), Thasso (Castlabs, validación
  prototype-side), Olivier Cortambert (comments detallados sobre la
  separación timeline-triggered overlays vs action-triggered pause
  ads).

## Standards relevantes

- **MPEG-DASH 6th edition** (ISO/IEC 23009-1) — base sobre la que
  extiende esta propuesta. `InsertPresentation`,
  `ReplacePresentation`, `ListMPD`.
- **IAB CTV Ad Standard** — formatos flexible-ratio (8:1, 6:1, 1:4,
  etc.) que esta propuesta referencia en vez de redefinir su propio
  layout system. R5 alinea explícitamente con él.
- **SCTE-35** (ANSI/SCTE digital program insertion cueing) — markers
  consumidos por el prototype vía Morpheus, convertidos a DASH
  dynamic events.

## Cómo está organizado el proyecto

| Archivo / carpeta | Qué tiene |
| --- | --- |
| `README.md` | Doc de entrada user-facing: qué hace el proyecto, layout, cómo regenerar artefactos. |
| `CLAUDE.md` | Convenciones para subagentes que tocan este proyecto. |
| `spec/01-intro.md` | Objetivo del cuerpo de docs e índice del set canónico. Punto de entrada técnico. |
| `spec/02-actors.md` | Three-actor model autocontenido: Broadcaster, ADS, Player. Boundary summary y responsabilidades por actor. |
| `spec/03-requirements.md` | Requirements R1–R7 (functional + governance), out of scope, y design characteristics que satisfacen los Rs. |
| `spec/04-use-cases.md` | Device classes D1–D5 y los 7 escenarios (UC-01..UC-07), cada uno con expected behavior por device class. Estructura scenario-first: el broadcaster valida un escenario contra toda su fauna de devices, no casos sueltos. |
| `spec/05-dash-linear-interfaces.md` | Reference de cómo se implementa SGAI hoy para linear ads en DASH 6th edition: inventario de las interfaces entre los tres actores, end-to-end message flow con MPDs y ListMPDs concretos, mapeo VAST → ListMPD. Foundation sobre la que extiende la propuesta non-linear. |
| `spec/99-glossary.md` | Glosario de la terminología técnica usada en el set de docs. Entries marcados *(proposed)* son constructs que esta propuesta pone sobre la mesa. |
| `analysis/dash-gap-analysis.md` | Artefacto generado: mapeo de cada UC contra MPEG-DASH 6th edition (ISO/IEC 23009-1) — qué construct existe hoy, cómo cubre el caso por device class, qué falta. Regenerable vía `prompts/analyze-dash-gap.prompt`. |
| `prompts/` | Build scripts en formato `.prompt` con header Inputs / Output / Skip if. Tres prompts: `analyze-dash-gap`, `build-norm`, `build-all` (orchestrator). |
| `output/` | Builds finales del norm document, con filename dated (`sgai-norm-YYYY-MM-DD.md`). No se sobreescriben — la historia de builds se preserva. |
| `proposal-drafts/` | Iteraciones históricas del spec en Google Doc form, una por archivo, con fecha y versión (`YYYY-MM-DD-vN.md`). Drafts internos que NO viven en el Doc compartido. Mantenidas como referencia histórica. |
| `.project/decisions/` | ADRs (Architecture Decision Records) numerados. Una decisión material por archivo. Inmutables — si una decisión se supersedea, se crea otro ADR que la marca como reemplazada. |
| `.project/LOG.md` | Bitácora cronológica del proyecto. Una entry por sesión de trabajo o acción material. Append-only. |
| `.project/phases/` | Phase folders con `PHASE.md` y `TASKS.md`. |

Carpetas que se crean cuando aparezca su primer archivo (no las creo
preemptivamente): `.project/meeting-notes/`, `references/`,
`external-collab/`, `prototype/`.

## Working doc compartido en Drive

- URL: https://docs.google.com/document/d/1CWm1BP65h45iJ5RwCAQkUAZ6lz7f-w3qJRGMdH8DDdQ/edit
- Title actual: *"Proposal for Non-Linear SGAI Ad Insertion"*.
- Audiencia: WG Qualabs, Comcast, SVTA Ads WG, contribuidores
  MPEG-DASH.
- Editar el Doc usando la regla 7.0.1 de `CLAUDE.md` (Docs API
  `documents.batchUpdate` quirúrgico, NUNCA `gws drive files update
  --upload`).
- El repo NO refleja automáticamente cambios del Doc. Cuando el Doc
  cambia (comments, edits de otros), el repo conserva su versión y
  reconciliamos manualmente. Si querés un snapshot fresco del Doc en
  el repo, generamos un nuevo archivo en `proposal-drafts/` con la
  fecha del snapshot.

## Phases

Phase folders live under `.project/phases/`. Only the phase that is
actively scoped has a folder — future phases are described here in
the long-range plan and get a folder when they open.

### Current state

- **`01-setup` — `closed`** (2026-05-11). Bootstrap of the project:
  repo layout, build pipeline (3 prompts), governance scaffolding
  under `.project/`, a first iteration of the spec set in `spec/`
  (6 files), first generated artefact
  (`analysis/dash-gap-analysis.md`), operational config (`SETUP.md`,
  `.env.agent.example`, `.gitignore`), and `git init` with an
  initial commit. See `phases/01-setup/` for PHASE.md and TASKS.md
  (the close report is embedded in PHASE.md).

### Long-range plan

The narrative of the project — once setup is done — remains a
foundation → design → prototype → closeout progression. Each phase
opens explicitly when its predecessor closes (or when Nicolas
decides to pivot).

**Foundation / spec iteration** — validate the foundation set
(actors, use cases, functional + non-functional requirements) with
the internal Qualabs WG (weekly) and Comcast (monthly). Capture
feedback as iterations on the existing `spec/` files. Close
foundational ADRs (actor model, rename, layout deferral, pause-ads
split, IAB CTV alignment) and add the non-functional requirements
doc. Suggested slug for the folder: `02-spec-iteration`.

**Design** — produce one or more concrete design candidates (MPD
event structure, schema, syntax, concrete examples). Iterate via
`proposal-drafts/<date>-v<n>.md`. Close design-level ADRs.
Decision matrix comparing candidates vs UCs and requirements.

**Prototype** — implement one or more designs end-to-end as a working
prototype. Tentative stack (to confirm at phase open): dash.js or
Shaka as base player, Morpheus for SCTE-35, Gemini for
overlay-template generation. Prototype code (in this folder or in an
external repo), run instructions, recorded demo.

**Closeout** — final proposal packaging, learnings recap, publication-
ready artifacts. Final doc in shareable format, learnings summary,
pull request or equivalent to the MPEG-DASH repo if applicable.

### External touchpoints — transversal

Engagements with **SVTA Ads WG**, **Alex Giladi (Netflix)**, **Thasso
(Castlabs)**, and **Thomas Stockhammer (MPEG-DASH chair)** are
transversal — they fire when the artifacts are mature enough to
share, not as a dedicated phase. Each touchpoint is logged in
`LOG.md` and feedback may inform iterations within the active phase.

## Cadencia y artefactos

- **WG interno Qualabs**: cadencia semanal. Las minutas las procesa
  el proceso `cto-minutes` y quedan indexadas con tags `Comcast` /
  `SGAI`. Para prep usar el proceso `preparacion-working-group`.
- **Sesiones con cliente Comcast**: monthly. Decisiones de spec que
  afecten al cliente se discuten ahí.
- **Posteo de recap a `#wg-comcast`**: después de cada sesión interna,
  recap aplicando `knowledge/output-policy.md` y disclaimer
  "generated by AI" si aplica.

## Cómo enviarme tareas (para Nicolas)

Cuando me mandes una tarea para este proyecto, podés referenciarla
con prefijo "tarea SGAI:". Asumo este proyecto como contexto y
trabajo dentro de su carpeta.

Patrones típicos:
- "tarea SGAI: armá el ADR del rename DynamicPresentation"
- "tarea SGAI: revisá la sección de schema del working doc y dame
  3 alternativas para el atributo content_type"
- "tarea SGAI: prep para el WG del jueves"
- "tarea SGAI: redactá el mensaje al SVTA Ads WG presentando la
  propuesta"
- "tarea SGAI: investigá X y proponé un draft, lo revisamos juntos"

Cuando reciba una tarea de research / spec generation:
- Si la decisión es nueva y material → ADR nuevo en `decisions/`.
- Si toca contenido del proposal → nueva iteración en
  `proposal-drafts/` (no edito las anteriores; quedan inmutables).
- Si cambia algo del contexto inmutable → update de `PROJECT.md`
  (secciones de objetivo, motivación, stakeholders, standards).
- Siempre → entry nueva en `LOG.md`.
- Solo mergeo al Doc compartido cuando vos digas explícitamente
  "esta versión va".

## Riesgos / blockers

- **Soporte de DASH 6th edition en players reales**: el prototipo
  necesita un player que entienda Insert/ReplacePresentation. Validar
  contra al menos 2 players (dash.js + Shaka o Castlabs) antes de
  cerrar el spec.
- **Coordinación con MPEG WG** (cadencia trimestral aprox.): si la
  propuesta no llega a un slot del WG, se pierde un trimestre.
  Mantener sincro con Alex Giladi y Thasso para no chocar con sus
  deliverables.
- **Tensión "build first" vs "spec first"**: la decisión del WG
  Comcast 2026-04-29 fue "build first, spec later". Mantener esa
  postura cuando aparezca presión para enmendar la spec antes de
  validar con prototipo.
- **Brand safety guardrails** (model serving + prompt engineering +
  content filtering): trabajo de IA significativo, no subestimar.

## Hilos abiertos (snapshot al cierre del 2026-05-06)

- [ ] **Spec — sintaxis DynamicPresentation**: atributo `content_type`
  vs sub-tipos `DynamicReplacePresentation` /
  `DynamicInsertPresentation`. Owner: Nico + David.
- [ ] **Spec — workflow del player**: cómo decide qué workflow usar
  antes de fetchear el MPD dinámico.
- [ ] **Spec — split pause-ads del flujo timeline**: separar pause-ads
  como tipo distinto (action-triggered) de OverlayPresentation
  (timeline-triggered). Surge del thread de Olivier.
- [ ] **Spec — alineación con IAB CTV Ad Standard**: la sección
  Positioning Templates debe referenciar la spec de IAB. Pendiente
  publicación oficial de IAB.
- [ ] **Prototipo — user parameters dinámicos** (cablear desde el
  cliente al manifest).
- [ ] **Prototipo — brand safety guardrails**.
- [ ] **External — SVTA Ads WG**: confirmar slot regular.
- [ ] **External — Alex Giladi**: oportunidad cuando el proposal
  alcance v0.3 o v0.4.
- [ ] **External — Thasso (Castlabs)**: contacto a identificar; pedirle
  intro a JP.
- [ ] **Working doc — rename del título** (todavía dice
  "OverlayPresentation"; pendiente cuando la decisión de rename
  esté completamente cerrada).

Para el detalle de cada hilo, ver el ADR correspondiente o la entry
relevante en `LOG.md`.
