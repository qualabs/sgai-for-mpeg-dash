# Bitácora — SGAI for Non-Linear Ads in DASH

Registro cronológico del proyecto. Una entry por sesión o acción
material. Las entries son inmutables (append-only) — si algo cambia
después, se anota en una entry posterior con la corrección.

Cada entry tiene formato:

```
## YYYY-MM-DD — Titulo corto

Contexto / por qué se hizo.

- Acción concreta 1 (links / refs).
- Acción concreta 2.

Decisiones derivadas:
- Decisión 1 (link a ADR si aplica).

Hilos abiertos / próximos pasos:
- ...
```

---

## 2026-05-11 — Re-organización de `.project/phases/`: una sola fase de setup

Reshape de la governance del proyecto. La estructura previa tenía
dos folders activos (`01-foundation` `in-progress` + `02-design`
`pending`) que proyectaban demasiado lejos cuando el setup todavía
no estaba estabilizado. Se colapsó en una sola fase `01-setup`,
cerrada in-place, que captura el bootstrap del proyecto. Las tareas
de validación con WG y las decisiones de diseño que vivían en las
fases viejas se re-planifican en próximas fases abiertas
explícitamente cuando el trabajo lo amerite.

- Borrados: `.project/phases/01-foundation/` y
  `.project/phases/02-design/` (PHASE.md + TASKS.md de cada uno).
  Contenido revisado antes del delete: las tasks viejas eran trabajo
  a futuro (validaciones con WG semanal, design work no iniciado),
  no contenido que el setup pierda. El modelo de 4 fases sigue
  documentado en `PROJECT.md` como long-range plan.
- Creado: `.project/phases/01-setup/` con `PHASE.md` (status
  `closed`, started + closed = 2026-05-11; el close report está
  embebido en PHASE.md) y `TASKS.md` (T-01 repo + workflow done,
  T-02 specs iniciales done).
- Actualizado: sección "Phases" de `PROJECT.md` para reflejar la
  estructura nueva (current state = `01-setup` closed; long-range
  plan = foundation → design → prototype → closeout descrito sin
  folders).

Decisiones derivadas:
- Solo se abre un phase folder cuando esa fase está activamente
  scopeada. Las fases futuras quedan descritas en `PROJECT.md` pero
  sin folder hasta el momento de abrirlas.

Hilos abiertos / próximos pasos:
- Próxima fase sugerida: `02-spec-iteration` (validación de la
  foundation set con WG interno y Comcast). No se abre acá — Nicolas
  decide cuándo.

## 2026-05-11 — docs/ renumerados como capítulos + intro + context.md migrado a PROJECT.md

Refactor de la organización del folder `docs/` para que sea
auto-navegable como un cuerpo numerado de capítulos. Razón: con el
crecimiento de la foundation set (actors, requirements, use-cases,
gap-analysis), el orden de lectura ya no era obvio desde los nombres
de archivo. Y `context.md` se había convertido en un híbrido entre
contexto del proyecto (que pertenece a `PROJECT.md`) y contenido
técnico (que pertenece a los docs numerados); había que partirlo.

**Renames aplicados (sin git mv — `projects/` está gitignored en el
parent repo cto-assistant, no hay tracking):**

- `docs/actors.md` → `docs/02-actors.md`.
- `docs/requirements.md` → `docs/03-requirements.md`.
- `docs/use-cases.md` → `docs/04-use-cases.md`.
- `docs/gap-analysis.md` → `docs/05-dash-gap-analysis.md` (nombre
  nuevo, no solo prefijo — explicita el scope del análisis).

**Nuevo:**

- `docs/01-intro.md` — objetivo del cuerpo de docs (SGAI para linear
  y non-linear ads en MPEG-DASH 6th edition) e índice de capítulos
  (02–05) con 1-2 líneas cada uno.

**Eliminado:**

- `docs/context.md` — el contenido relevante de diseño se migró a
  `PROJECT.md` (objetivo, motivación, output esperado, stakeholders,
  standards relevantes). El glosario (~50 entradas) quedó marcado
  como TODO en `PROJECT.md` para decisión de destino —
  candidato natural es `docs/glossary.md` (T-07 en
  `phases/01-foundation/TASKS.md`).

**PROJECT.md gana:**

- Sección "Objetivo y motivación" — antes solo aparecía en
  frontmatter `description`.
- Sección "Output esperado" — explicita el doble entregable (spec +
  prototipo).
- Sección "Stakeholders" — antes solo aparecían en el `description`
  de frontmatter; ahora con detalle a nivel organizaciones y roles
  públicos (Qualabs WG, Comcast, SVTA Ads WG, DASH-IF, MPEG-DASH WG,
  contribuidores externos identificados).
- Sección "Standards relevantes" — MPEG-DASH 6th ed, IAB CTV Ad
  Standard, SCTE-35.

**Cross-refs actualizadas:**

- `docs/02-actors.md`, `docs/03-requirements.md`, `docs/04-use-cases.md`,
  `docs/05-dash-gap-analysis.md` — links internos al nuevo naming.
- `.project/PROJECT.md` — tabla "Cómo está organizado el proyecto",
  expected outputs de Phase 1, regla de update de contexto.
- `.project/phases/01-foundation/PHASE.md` — scope, outputs, risk
  description.
- `.project/phases/02-design/PHASE.md` — referencia a use-cases y
  gap-analysis.
- `.project/phases/01-foundation/TASKS.md` — T-01 redirigido a las
  secciones de contexto de PROJECT.md (en vez de docs/context.md);
  T-02..T-04 renombrados.
- `.project/decisions/adr-004-device-aware-ad-selection.md` —
  referencias a `context.md` reemplazadas por las equivalentes en
  `docs/03-requirements.md` / `docs/04-use-cases.md`. Marcado con
  TODO HTML que UC-08 y UC-09 mencionados en ese ADR ya no existen
  en la lista actual de use cases (UC-01..UC-07 post 2026-05-07) —
  pendiente confirmar a qué UCs actuales mapean.
- `.project/decisions/adr-005-max-slot-duration-enforcement.md` —
  todas las refs a docs renombrados actualizadas.
- `.project/decisions/gap-analysis-validation-2026-05-06.md` —
  refs a los docs renombrados en source-under-review, method y
  observations.

**LOG.md:** entries históricas inmutables, no modificadas. Las refs
a los nombres viejos en entries pre-2026-05-11 son parte del
registro cronológico.

**Smoke verification:**

- `ls docs/` → exactamente `01-intro.md`, `02-actors.md`,
  `03-requirements.md`, `04-use-cases.md`, `05-dash-gap-analysis.md`.
- Grep estricto por `context.md`, `actors.md`, `requirements.md`,
  `use-cases.md`, `gap-analysis.md` (con regex que excluye prefijo
  numérico) sobre todo el proyecto excepto LOG.md → única match es
  el TODO comment en PROJECT.md que referencia explícitamente el
  archivo viejo eliminado.

**Hilos abiertos derivados:**

- [ ] Decidir destino del glosario migrado (TODO en `PROJECT.md` al
  final). ¿Mover a `docs/glossary.md` ahora anticipando T-07, o
  esperar a que T-07 se ejecute formalmente?
- [ ] Revisar referencias a UC-08 y UC-09 en
  `adr-004-device-aware-ad-selection.md` — esos UCs no existen en
  la lista actual.

---

## 2026-05-07 — R1 strengthened (graceful degradation as MUST) + UC-07 added (legacy Player encounters new constructs)

Trabajo a partir de un comentario de Nicolas sobre la nota de UC-01:
"Per R1, a Player that does not understand the slot mechanism must
skip the slot entirely and continue playing the primary content
uninterrupted (graceful degradation)". Su pedido: convertir esto en
un requirement explícito (lo que sea que se proponga debe ser
retrocompatible si el dispositivo / Player no entiende los nuevos
constructs).

Estado previo: R1 ya cubría graceful degradation, pero como cláusula
parentética con "should" (RFC 2119: deseable, no obligatorio). Era
débil para algo que es contractual.

**Decisión (Opción A de las 3 evaluadas):** fortalecer R1 in place,
sin splittear en R8. Cero rework de las ~7 referencias existentes a
"Per R1" / "R1 graceful degradation" en use-cases.md y
gap-analysis.md. Las otras dos opciones (split R1+R8, dejar como
está) tenían contras: split → mucho rework editorial; dejar → no
transmite la fuerza que Nicolas quería.

**Acciones aplicadas:**

- `docs/requirements.md` R1 reescrito:
  - Title: "R1. MPEG-DASH 6th edition compliance and graceful
    degradation" (antes solo "compliance").
  - "should" → "MUST". Backward compatibility ahora es **mandatory**,
    no recomendación.
  - Texto expandido: "A Player that does not implement the new
    mechanisms... MUST skip them and continue playing the primary
    content uninterrupted. Any new construct introduced by the
    proposal MUST be expressed using MPEG-DASH 6th edition extension
    points whose 'ignore-if-unknown' semantics already enable this
    behavior on conforming legacy Players. The expected behavior of
    a legacy Player encountering the new constructs is captured as
    UC-07 in `use-cases.md`."

- `docs/use-cases.md` UC-07 nuevo (sección Scenarios):
  - Scenario: legacy Player que predates la propuesta encuentra un
    manifest con los nuevos constructs.
  - Expected behavior: uniforme cross-device-class (depende de Player
    version, no de hardware). Player ignora el construct silenciosamente,
    primary content continúa, no error al user.
  - Notes: scenario es la cornerstone del extensibility contract —
    cualquier construct nuevo debe ser expresable via extension points
    que produzcan este outcome. Broadcaster trata UC-07 fall-throughs
    como expected losses, no errors.

- `docs/use-cases.md` Coverage table: agregada fila UC-07 con
  comportamiento uniforme "primary continues (legacy)" en D1..D5.

- `docs/use-cases.md` notas redundantes removidas: las "Notes / open
  questions" sections de UC-01 y UC-02 contenían solo el bullet
  "Per R1, a Player that does not understand... graceful
  degradation". Esas notas ahora son redundantes (R1 fortalecido +
  UC-07 dedicada). Sections enteras eliminadas en UC-01 y UC-02.

- `docs/use-cases.md` Frame: "R1–R6" → "R1–R7".

- `docs/context.md`: actualizada la lista de docs:
  - "R1–R6" → "R1–R7"
  - "6 escenarios (UC-01..UC-06)" → "7 escenarios (UC-01..UC-07)"

**Decisiones derivadas:**

- Estilo "positive only" mantenido: UC-07 dice "MUST skip and
  continue", no "MUST NOT error".
- ADRs no se tocaron — esta no fue una decisión normativa nueva,
  fue refuerzo de R1 que ya existía.

**Hilos abiertos derivados:**

- En fase 02-design: el design tiene que listar explícitamente cuáles
  extension points de MPEG-DASH 6th edition se usan para cada
  construct nuevo, y demostrar que cada uno tiene "ignore-if-unknown"
  semantics. Sin eso, R1 (UC-07) no se cumple.

## 2026-05-07 — Use cases wording sweep — pasada 2 (UC-04 D2/D3/D4 + UC-06 D1/D3)

Cleanup follow-up al barrido del wording de UCs. Las primeras 6
ediciones cubrieron UC-01/02/03 + UC-04 D1; quedaba la cola de UC-04
y UC-06.

**Acciones aplicadas:**

- UC-04 D2: "validates candidates against slot rules" → "selects the
  highest-ranked candidate whose form-and-layout combinations
  conform to the allowed layouts and are renderable on this device,
  using ADS ranking hints".
- UC-04 D3 y D4: "validates candidates." → "selects the highest-
  ranked candidate." (vía replace_all dado que el wording era idéntico
  en ambos lugares y en UC-06 D3).
- UC-06 D1: "Reads the pause-triggered slot rules, validates
  candidates, selects one." → "Reads the pause-triggered slot rules
  and selects the highest-ranked renderable candidate using ADS
  ranking hints."
- UC-06 D3: idem replace_all anterior.

**Verificación:** grep `validates? (candidate|each|that)` sobre
`docs/use-cases.md` → 0 matches. El barrido del wording está
completo.

UC-04 D5 y UC-06 D2 no requirieron edits — su wording ya era
descriptivo positivo ("reads slot rules. For each candidate, walks
the forms and finds none renderable" / "the device cannot composite
anything on top of video — but the primary is paused...").

## 2026-05-07 — Use cases wording cleanup + multi-form ADS response + duration as ADS hint

Refinement adicional sobre R7 después de un comentario de Nicolas
sobre el wording de varios UCs. El issue: frases tipo "Player
validates duration against slot cap and selects one candidate"
sonaban como si el Player eligiera ads de una lista filtrando por
duración. Eso es incorrecto:

- El ad ES lo que ES — la duración es intrínseca al ad, no un
  parámetro que el Player negocie.
- El Player NO filtra por duración. Selecciona entre candidatos por
  renderability + ADS ranking hints. La duración se enforces al
  playback (cut at cap si se excede).
- La duration del slot (cap) se manda al ADS como HINT para mejor
  decisioning, pero respetar el cap es responsabilidad del Player.
- Edge case: el ADS puede declarar duration=X pero el stream real
  ser duration=Y. El Player enforces contra la duración REAL del
  stream rendered.

Estilo: Nicolas pidió que el wording diga lo que SÍ es, no lo que
NO es ("selects by renderability" en vez de "selects NOT by
duration"). Y todo en inglés, sin mezcla de idiomas en docs.

**Acciones aplicadas:**

- `docs/use-cases.md` — barrido de los UCs, reemplazo de wording
  ambiguo por wording correcto en inglés:
  - UC-01 D1: "discards any candidate whose declared duration
    exceeds the slot cap" → eliminado. Nuevo: "Selects the highest-
    ranked renderable candidate using ADS ranking hints. R7 is
    enforced at playback".
  - UC-01 D3: "validates duration against slot cap and selects one
    candidate" → "selects the highest-ranked renderable candidate
    using ADS ranking hints. R7 is enforced at playback".
  - UC-02 D1: "Validates each candidate's duration against the slot
    cap and discards any that exceed it" → "Selects the highest-
    ranked renderable candidate using ADS ranking hints. R7 is
    enforced at playback".
  - UC-02 D3: idem.
  - UC-03 D1: "Validates that the sum of candidate durations does
    not exceed the break cap (see Notes for the open question
    about what to do when it does)" → "Plays each candidate in
    order... R7 is enforced at playback: when the cumulative
    sequence duration reaches the break cap, the Player stops".
    El "see Notes for the open question" sale (la open question ya
    está resuelta por R7 / ADR-005).
  - UC-04 D1: "Validates each candidate against the rules and
    discards violators" → "Selects the highest-ranked candidate
    whose form-and-layout combinations conform to the allowed
    layouts and concurrency cap and are renderable on this device".
    R7 explícito sobre cap del overlay.

- `docs/use-cases.md` — UC-01 y UC-02 ADS response actualizados:
  el ad ahora se describe como multi-form ("typically a video form,
  optionally with image or HTML fallback for devices that cannot
  render video"). Antes decían solo "video form with its own
  duration". UC-04 ya tenía multi-form.

- `docs/requirements.md` Design Characteristics > Device-aware ad
  selection: agregado un párrafo que captura los 4 puntos —
  duration intrínseca al ad, selección por renderability + ranking,
  cap como hint al ADS, enforcement contra rendered stream length
  real (no la declarada por el ADS).

- ADR-005 NO se modificó. La regla normativa que captura ya estaba
  alineada (ADS no enforces, Player sí). Las aclaraciones de wording
  viven mejor en requirements.md (donde es system-level) y en los
  UCs (donde se ve el comportamiento concreto).

**Decisiones derivadas:**

- Estilo: positive statements only en docs/. No se enuncia "X is not
  Y" cuando el positive "X is Z" es exhaustivo.
- Idioma: todos los docs/ en inglés. ADR-005 queda en español por
  consistencia con ADR-001..004 (existentes en español); LOG sigue
  en español por consistencia interna del archivo.

**Hilos abiertos derivados:**

- El spec downstream (fase 02-design) tiene que proveer el mecanismo
  por el cual el broadcaster manda duration al ADS como hint en el
  request. Anotado, no es foundation work.
- T-03 (validar use-cases con WG interno) y T-04 (validar
  requirements) tienen ahora más material consolidado para validar.

## 2026-05-07 — R7 added: max slot duration broadcaster-declared + Player-enforced (cuts at cap)

Refinement of the use cases en T-03 de fase 01-foundation arrancó con
una observación de Nicolas: hace falta enunciar explícitamente que el
content owner declara una duración máxima del slot, el ADS puede
devolver uno o más ads, y el Player corta cuando se excede el cap.
Aplica a linear y non-linear (overlay).

Después de discutir dónde ubicarla — "common constraints" en
`docs/use-cases.md` vs un requirement funcional en
`docs/requirements.md` — Nicolas eligió R7 (functional req).
Layering: requirements = system rules; use-cases = scenarios donde
los reqs juegan. R7 es instancia concreta de R2 (Broadcaster
declares, Player enforces, ADS doesn't).

**Acciones aplicadas:**

- `docs/requirements.md` — R7 nuevo bajo Functional Requirements,
  después de R6. El texto deja explícito: cap broadcaster-declared,
  Player MUST cut at cap (default), aplica a linear (UC-01, UC-02,
  UC-03) y non-linear (UC-04, UC-05, UC-06). Policies alternativas
  (skip break, trim-clean, fail-closed) no son default; pueden ser
  expresadas opt-in por el broadcaster.

- `docs/use-cases.md` — UC-03 "Notes / open questions" reescrita a
  "Notes": el bloque referencia R7 + ADR-005 como resolución
  normativa. La open question original ("fail-closed vs trim vs cut")
  queda cerrada con cut como default.

- `decisions/adr-005-max-slot-duration-enforcement.md` — ADR nuevo.
  Captura: la regla, dónde vive (R7 en requirements, no common
  constraints en use-cases) con justificación de layering, las
  alternativas consideradas y rechazadas (common constraints
  section, default skip-break, default trim-clean), y la trazabilidad
  cruzada a UC-03 + R2 + UC-01..06.

- Cross-link fixes en `docs/`: 3 links pre-move-a-docs apuntaban a
  paths root (`decisions/...`, `proposal-drafts/...`); ahora apuntan
  a `../decisions/...` y `../proposal-drafts/...`. Específicamente
  `docs/requirements.md` × 2 (líneas 5 y 103) y `docs/gap-analysis.md`
  × 1 (línea 19).

**Decisiones derivadas (resumen, ver ADR-005 para el detalle):**

- R7 es system-level → vive en requirements.md, no en common
  constraints de use-cases.md.
- Default overflow policy = cut at cap. Alternativas opt-in.
- UC-03 open question cerrada.
- Otros UCs heredan R7 sin cambios per-UC.

**Hilos abiertos derivados:**

- En fase `02-design`: definir el atributo/elemento con el que el
  broadcaster declara max-duration por slot, y opcionalmente la
  overflow policy si se permite no-default.
- T-04 (validar requirements con WG interno) ahora cubre R1..R7.
- T-03 (validar use-cases) tiene a UC-03 actualizado para validar.

## 2026-05-07 — Foundation knowledge artifacts moved to docs/ + Phase 1 tasks rethought + Phase 2 opened (pending)

Después del reshape de fases (entry siguiente) Nicolas pidió dos
ajustes adicionales:

1. **Re-pensar las tareas de fase 1**. Las tareas que tenía
   (T-01..T-05: sintaxis DynamicPresentation, workflow del player,
   split pause-ads timeline, IAB CTV alignment, rename Working Doc)
   son design-level, no foundation. Foundation = lo que va ANTES de
   la sintaxis (use cases, actors, requirements, NFRs).

2. **Carpeta `docs/`** que aloje las "fuentes de conocimiento" del
   proyecto (los markdowns que vamos generando como artefactos
   sustantivos). PROJECT.md y LOG.md se quedan en la raíz por ser
   project management; decisions/ y phases/ tienen sus propias
   carpetas; proposal-drafts/ se queda separado por ser drafts del
   spec, no fuentes.

   Notación importante (Nicolas): **stakeholders** es del proyecto
   (gestión PMP), no del deliverable. Su output va a una sección de
   PROJECT.md, no a `docs/`.

**Acciones aplicadas:**

- Carpeta nueva `docs/` con: `actors.md`, `context.md`,
  `use-cases.md`, `requirements.md`, `gap-analysis.md`. Los archivos
  cambiaron de `<root>/<file>.md` a `<root>/docs/<file>.md`. Los
  cross-links internos (entre los archivos movidos) siguen
  funcionando porque siguen siendo siblings.

- `PROJECT.md` updated: tabla "Cómo está organizado el proyecto" usa
  ahora `docs/<file>.md`; sección Phase 1 outputs idem; nota de
  workflow de tareas idem.

- `phases/01-foundation/PHASE.md` updated: scope, outputs y risks
  apuntan a `docs/<file>.md`.

- `phases/01-foundation/TASKS.md` reescrito completamente con tareas
  foundation-level:
  - T-01..T-04: Validar context, actors, use-cases y functional
    requirements con WG interno.
  - T-05: Generar `docs/nfrs.md` (Non-Functional Requirements).
  - T-06: Stakeholder map → output a PROJECT.md (PMP, NO docs/).
  - T-07: Glossary → `docs/glossary.md`.

- `phases/02-design/` abierta con `status: pending`. PHASE.md describe
  el scope (concrete designs from foundation, multi-track) y
  TASKS.md aloja el backlog parkeado de design-level (las viejas
  T-01..T-05) hasta que la fase pase a in-progress.

- LOG.md (este archivo) — entry nueva.

**Decisiones derivadas:**

- Abrir 02-design ahora con status `pending` fue preferido sobre
  parquear el backlog en otro lado (PROJECT.md "Hilos abiertos",
  comentario suelto). Razón: el backlog tiene casa natural en su fase
  destino, ya queda visible cuando se haga `list-projects` o se
  navegue al proyecto, y el switch a in-progress será trivial.
- Stakeholder map se etiquetó explícitamente como PMP-side (output a
  PROJECT.md), no deliverable-side (no va a `docs/`). Glossary sí va
  a `docs/` porque es deliverable knowledge.
- Cross-links entre los archivos movidos NO se tocaron — al estar
  todos en `docs/` ahora, las referencias bare `[actors.md](actors.md)`
  siguen resolviendo correctamente.
- Referencias en LOG.md a paths viejos NO se actualizaron — son
  histórico, append-only. La presencia de esta entry indica el
  cambio de path para futuros lectores.

**Hilos abiertos derivados:**

- Cuando arranque T-05 (NFRs), generar `docs/nfrs.md` con secciones
  latency, scale, security, observability, privacy.
- Cuando arranque T-06 (stakeholder map), agregar sección
  "Stakeholders" en PROJECT.md (no `docs/`).
- Cuando arranque T-07 (glossary), generar `docs/glossary.md` con
  términos clave (DynamicPresentation, OverlayPresentation,
  ListOverlay, Form, ad candidate, etc.).

## 2026-05-07 — Phase model reshape: 6 phases → 4 phases (foundation/design/prototype/closeout)

Nicolas pidió reestructurar las fases del proyecto. El modelo viejo
de 6 fases (WG-internal-alignment → External-alignment →
Internal-design → External-iteration → Prototype → Close-out) tenía
"external alignment" como fase propia, lo cual no encajaba bien
porque las charlas con externos (SVTA, Alex Giladi @ Netflix, Thasso
@ Castlabs, Thomas Stockhammer) no son una fase con scope/timeline,
son interacciones que se disparan según madurez del artefacto.

Modelo nuevo, 4 fases:

1. **Foundation** — produce el set de inputs (context, actors, use
   cases, functional + non-functional requirements) que habilita
   diseños downstream.
2. **Design** — uno o más diseños concretos basados en la foundation.
3. **Prototype** — implementar uno o más diseños end-to-end.
4. **Closeout** — final proposal packaging + recap + publication-ready
   artifacts.

External touchpoints quedan **transversales**: se loguean en `LOG.md`
cuando ocurren y pueden disparar iteraciones dentro de cualquier fase
activa. No son una fase en sí.

**Acciones aplicadas:**

- Carpeta `phases/01-wg-interno-alignment/` renombrada a
  `phases/01-foundation/`.
- `PHASE.md` reescrito en inglés, scope adaptado al nuevo objetivo
  (foundation set), out-of-scope apunta a 02-design / 03-prototype /
  04-closeout, sección "External touchpoints" como transversal.
- `TASKS.md` adaptado: T-01..T-05 (spec/foundation work) se quedan
  con el header actualizado + nueva tarea **T-06: Generar
  Non-Functional Requirements doc** (latency, scale, security,
  observability, privacy) — los NFRs no existían como artefacto.
- `PROJECT.md` sección "Fases del proyecto" → "Phases" (en inglés),
  reescrita al modelo de 4 fases. Las fases 02, 03, 04 se
  materializan como carpetas cuando arranquen.
- Snapshot histórico de "Hilos abiertos al cierre del 2026-05-06" se
  preservó tal cual — los hilos vivos canónicos pasan a vivir en el
  TASKS.md de la fase activa.
- Decisiones (ADRs) NO se tocaron. Las pre-schema sin `scope:` se
  siguen interpretando como `scope: project` por default.

**Decisiones derivadas:**

- Renombrar (preservar) la fase activa fue preferido sobre cerrar y
  abrir nueva fase, porque el contenido de la fase anterior
  (validación de foundation docs + foundational ADRs) coincide con
  el scope de la nueva fase 01-foundation.
- Nombres en inglés a nivel headers/slugs porque el proyecto va a ser
  visto por audiencia internacional (MPEG-DASH WG, SVTA, etc.).

**Hilos abiertos derivados:**

- T-06 (NFRs) en `phases/01-foundation/TASKS.md`.
- Cuando arranque 02-design, materializar `phases/02-design/PHASE.md`
  + `TASKS.md` y mover hilos de "Prototipo — user parameters
  dinámicos" / "brand safety guardrails" al PHASE.md de 03-prototype
  cuando se abra.

## 2026-05-06 — Gap analysis vs MPEG-DASH 6th edition (research + validación)

Nicolas pidió mapear los 6 use cases (post-reestructura) contra lo que
MPEG-DASH 6th edition puede hacer hoy, identificando qué cubre la
spec y qué falta. El pipeline tuvo dos etapas: research por un
subagente A y validación por un subagente B independiente.

**Subagente A (research) — 22 min, 4 queries a NotebookLM:**

Generó `gap-analysis.md` (547 líneas, 27 KB) con el análisis per-UC
y per-device, summary matrix y top gaps consolidados. Status por UC:

- UC-01 Slot at start of session: 5/5 fully covered.
- UC-02 Mid-content slot: 5/5 fully covered.
- UC-03 Multi-ad break: 5/5 fully covered (soft gap: trim policy
  hardwired al final del slot vía `@maxDuration`; broadcaster no
  puede declarar fail-closed o play-until-cap-and-cut).
- UC-04 Coexisting overlay: 0/5 covered. Spec no tiene construct
  para overlay ads sobre primary content corriendo.
- UC-05 Hybrid linear + overlay: 0/5 covered. §5.16.1 normative:
  *"the main Media Presentation shall not be displayed during the
  playback of the alternative Media Presentation"*. Spec
  explícitamente forbids concurrent ad presentations.
- UC-06 Pause-triggered ad: 0/5 covered. Eventos atados a
  `presentationTime` (§5.10.1); no hay state-triggered events.

Top 6 gaps consolidados (la superficie que el proposal debe cubrir
para R1):

1. No overlay/non-linear ad event.
2. No state-triggered (pause/action) ad opportunity.
3. No concurrent ad presentations.
4. No multi-form ad candidate model (single `@uri` → single MPD).
5. No broadcaster-declared layout-constraint vocabulary.
6. No spec status para "decline the slot" como Player outcome.

Side-finding: §I.4 / Annex I.4 (`ExtUrlQueryInfo` /
`UrlParamInfo` con `@includeInRequests="altmpd"`, vocabulary
`urn:mpeg:dash:state:<suffix>`) tiene mecanismos para Player → ADS
state hints, pero el vocabulary cubre solo media-stream descriptors
y event-execution telemetry. Ninguna key cubre device-rendering
capabilities (decoder count, overlay surfaces, HTML rendering). Vale
documentarlo porque es el primer "ya tenés esto" que un reviewer
levanta.

**Subagente B (validación) — 14 min, 3 queries adicionales:**

Generó `decisions/gap-analysis-validation-2026-05-06.md` con
cross-check independiente. Encontró:

- 2 issues materiales (M1, M2): citation errors en el bloque §I.4.
  M1 tenía la URN equivocada (`urn:mpeg:dash:urlparam:2025` en lugar
  de `urn:mpeg:dash:state:<suffix>`). M2 enumeraba el vocabulary
  incompleto (faltaba CMCD, execution-telemetry, previous-state).
- 2 issues minor (m1, m2): `@returnOffset` no listado en el primer;
  R2-violation framing en UC-04 D2 podría anclarse a UC-04 Notes.
- 7 observations: confirmaciones de que el §5.16 quote es verbatim,
  Annex L es interactive storyline branching (no SGAI), Top-6 gaps
  cada uno trazable a un UC concreto, etc.
- Confianza: medium-high. Ningún issue invalida el análisis.

**Correcciones aplicadas (M1 + M2):**

- Bloque §I.4 del primer reescrito con la URN correcta y el
  vocabulary completo (incluyendo CMCD y telemetry keys).
- Closing paragraph del archivo reescrito con la enumeración correcta
  + frase explícita "Reviewers who wonder 'what about §I.4 / CMCD?'
  should find the explicit explanation here".
- Issues minor (m1, m2) NO corregidos en este run — quedan como
  hilos abiertos para una pasada posterior.

**Lección registrada:**

El validation subagent es una pieza valiosa cuando el research toca
spec normativa que va a ser revisada por terceros (MPEG, SVTA). En
este run encontró 2 issues materiales en menos de 15 min y 3
queries — costo bajo, valor alto. Vale repetir el patrón cuando
generemos contenido que va a ir a stakeholders externos.

## 2026-05-06 — Use cases re-estructurados a scenario × device behavior

La estructura anterior tenía un UC por combinación específica
(escenario, device class). Eso fragmentaba el mismo escenario en
múltiples casos sueltos (p. ej. el escenario "coexisting overlay"
aparecía como UC-03, UC-06, UC-08, UC-09, UC-11) y obligaba al
lector a saltar entre casos para entender cómo el spec maneja la
heterogeneidad de devices para un único escenario. Eso no es lo
que el broadcaster necesita validar: el broadcaster no prueba un
device aislado, prueba **qué se espera que pase en cada device
class de su población de viewers para un escenario dado**.

Reescritura aplicada en `use-cases.md`. Estructura nueva:

- **Frame**: explicita que cada UC describe un escenario y enumera
  el expected behavior en cada device class D1–D5.
- **Coverage**: tabla scenario × device con un indicador del
  comportamiento dominante por celda; reemplaza la coverage matrix
  anterior que apuntaba a UC-IDs.
- **Por UC**: scenario, broadcaster intent, ADS response, y
  sub-secciones por device class (D1, D2, D3, D4, D5) con "Player
  decision" y "What the user sees". Notes / open questions al final.

Consolidación 12 → 6 escenarios:

| Nuevo | Título | UCs anteriores |
| --- | --- | --- |
| UC-01 | Slot at start of session | UC-01, UC-10 |
| UC-02 | Mid-content slot | UC-02, UC-05 |
| UC-03 | Multi-ad break | UC-12 |
| UC-04 | Coexisting overlay | UC-03, UC-06, UC-08, UC-09, UC-11 |
| UC-05 | Hybrid linear + concurrent overlay | UC-04 |
| UC-06 | Pause-triggered ad | UC-07 |

Reglas que se mantuvieron:

- Cero ocurrencias de los 12 strings de la mecánica del proposal
  (ListMPD, ListOverlay, OverlayPresentation, DynamicPresentation,
  InsertPresentation, ReplacePresentation, `<svta:`, `urn:svta:`,
  `layoutMode`, pre-roll, mid-roll, post-roll). Verificado con
  `grep`.
- R-anchors (R1, R2, R5, R6) inline donde aplican.
- Open questions preservadas; cuando una pregunta era específica
  a un device del UC original, ahora vive en el sub-section del
  device del UC nuevo o en las notes globales del UC.
- Para evitar duplicar texto, devices que actúan igual a otro se
  declaran explícito ("D2 — same as D1") en lugar de copiar.

Decisiones editoriales:

- **D5 multi-ad break y mid-content slot**: los UCs originales no
  cubrían explícitamente "multi-ad break en D5" ni "mid-content
  slot en D2/D3/D4/D5"; se infirieron por extensión natural del
  caso linear-only de UC-01/UC-10 (linear en single decoder es
  sequential, no concurrent). Es una extensión conservadora, no
  una invención.
- **Hybrid linear + overlay en D2/D3/D4**: el UC-04 original solo
  cubría D1. Se agregó análisis explícito de qué hace el Player
  en devices con menos capabilities. Para D3/D4 se introdujo una
  open question (¿se puede componer overlay sobre un linear ad
  con un solo decoder?) que la spec va a tener que cerrar; queda
  flagged como open en las Notes del UC.
- **Pause-triggered en D2**: el UC-07 original solo cubría D3. Se
  agregó análisis de D2 que explicita la ambigüedad
  device-específica entre "no overlay sobre running video" vs
  "no overlay sobre paused frame", marcada también como open
  question.

Verificación final:

- `wc -l use-cases.md` → 611 líneas, ~28 KB. Por debajo del techo
  de 30–40 KB que se anticipó al diseñar el rewrite, así que no
  hace falta splittear el frame inicial en este run.
- `grep` para los 12 strings prohibidos → todos en 0.

`actors.md` y `requirements.md` no requirieron cambios — los
cross-links apuntan a `use-cases.md` sin referenciar UC-IDs
específicos, y los UC-IDs nuevos cubren todo lo que los 12
anteriores cubrían. `PROJECT.md` necesitó update menor: la fila
de la tabla que describe `use-cases.md` mencionaba "UC-01..UC-12"
y matriz de cobertura device × ad opportunity; ahora dice
"UC-01..UC-06" y describe la estructura scenario × device behavior.

Lección capturada: cuando un documento enumera combinaciones
(N escenarios × M devices), la pregunta de diseño es si el lector
quiere navegar por escenario o por device. En este caso el lector
es el broadcaster validando compliance, y el broadcaster siempre
tiene un escenario en mente y quiere saber qué pasa en su fauna
de devices — así que la estructura natural es scenario-first con
sub-secciones por device, no una grilla de UC-IDs sueltos.

Hilos abiertos / próximos pasos:

- La open question de hybrid linear+overlay en D3/D4 (UC-05) y la
  de pause-ads en D2 (UC-06) son decisiones de spec pendientes
  — deberían terminar como ADRs o como design characteristics en
  `requirements.md` cuando se cierren.

---

## 2026-05-06 — Use cases reescritos para ser agnósticos a la solución técnica

Nicolas observó que los 12 use cases (UC-01..UC-12) escritos al
agregar la sección Use Cases estaban atados a la mecánica concreta
del proposal actual: nombres de eventos del MPD (`InsertPresentation`,
`ReplacePresentation`, `DynamicPresentation`), nombres de resolution
documents (`ListMPD`, `ListOverlay`), elementos XML específicos
(`<svta:Overlay>`), atributos puntuales (`layoutMode`), y tipos
pre-cargados (`pre-roll`, `mid-roll`). Esa redacción los volvía
inservibles como input para evaluar **diseños alternativos**: si
mañana cambia el nombre o la forma del mecanismo, hay que reescribir
todos los casos.

Reescritura aplicada en `use-cases.md`. Estructura nueva por UC:

- **Broadcaster intent**: reglas conceptuales del slot (qué tipos
  permite, qué layouts permite, qué duraciones, qué concurrencia).
  Sin nombres de schema.
- **ADS response**: qué tipo de candidates devuelve y con qué forms.
  Sin nombres de resolution documents.
- **Player decision and rendering**: qué hace el Player —
  validación contra reglas del broadcaster, walk de forms por
  capability, selección. Sin nombres de eventos del MPD.
- **What the user sees**: narrativa corta del experience.
- **Notes / open questions**: preguntas reformuladas en abstracto
  (ej. "how does the ADS express form-level priority?" en lugar de
  "shape of `priority_hint` in `<svta:Form>`").

Otros cambios:

- Sección de tipos: renombrada de "Ad opportunity types" (que tenía
  "Linear pre-roll", "Linear mid-roll splice", etc.) a "Scenario
  types" con narrativos: "Slot at start of session", "Mid-content
  slot", "Multi-ad break", "Coexisting overlay", "Pause-triggered
  ad", "Hybrid (linear + concurrent overlay)". El broadcaster
  declara qué tipos permite por slot, no pre-decide cuál se usará.
- Coverage matrix: columnas renombradas para coincidir con los
  nuevos nombres narrativos (Slot at start, Mid-content slot,
  Multi-ad break, Coexisting overlay, Pause-triggered, Hybrid).
- Frame inicial actualizado: explicita que los casos son agnósticos
  a los MPD constructs y que tienen que sobrevivir a un rediseño.
- Device classes D1-D5 preservadas tal cual (son del device, no del
  spec).
- 12 UCs preservados, misma numeración, misma cobertura device ×
  scenario.

Verificación: `grep` sobre `use-cases.md` para los 12 strings
prohibidos (ListMPD, ListOverlay, OverlayPresentation,
DynamicPresentation, InsertPresentation, ReplacePresentation,
`<svta:`, `urn:svta:`, layoutMode, pre-roll, mid-roll, post-roll) —
todos en 0 ocurrencias.

`actors.md` y `requirements.md` no requirieron cambios — los
cross-links son por número de UC (UC-01..UC-12), que se preservó.
`PROJECT.md` tampoco — la descripción de `use-cases.md` sigue
siendo correcta.

Lección: **cuando un input para diseño tiene la solución embebida,
no se puede evaluar diseños alternativos sin reescribir el input.**
Para que los use cases sirvan como criterio estable contra el cual
medir distintas propuestas, tienen que describir el escenario y la
intención, no la mecánica. El "qué pasa", no el "cómo se logra".

## 2026-05-06 — Kickoff del proyecto

Nicolas pidió crear el proyecto y describirlo en un PROJECT.md, en el
contexto del WG Comcast. Objetivo: SGAI para non-linear ads en
MPEG-DASH, con doble entregable (spec + prototipo) y colaboración con
SVTA Ads WG y contribuidores de MPEG-DASH (Alex Giladi de Netflix,
Thasso de Castlabs).

- Creada la carpeta `projects/sgai-non-linear-ads/` con `PROJECT.md`
  inicial y subcarpetas vacías (`references/`, `prototype/`,
  `meeting-notes/`, `external-collab/`, `decisions/`, `drafts/`).
- Identificado el working doc compartido:
  https://docs.google.com/document/d/1CWm1BP65h45iJ5RwCAQkUAZ6lz7f-w3qJRGMdH8DDdQ/edit
  (Proposal v2 al momento del kickoff, modificado el 2026-04-29).

Hilos abiertos:
- Sintaxis DynamicPresentation, workflow del Player, alineación con
  Alex Giladi y Thasso, etc. (ver `PROJECT.md` → Hilos abiertos).

## 2026-05-06 — Recap del WG Comcast 2026-04-29 enviado a `#wg-comcast`

Nicolas pidió un recap de la sesión anterior del WG para que los
asistentes de la próxima reunión llegaran con contexto compartido.

- Draft armado en español, después traducido a inglés a pedido de
  Nicolas, después re-redactado en texto plano (sin markdown crudo)
  para Slack.
- Mensaje enviado al canal `#wg-comcast`:
  https://qualabsuy.slack.com/archives/C06AR5G596H/p1778077426144939
- Disclaimer al final: "This recap was generated with AI and may
  contain errors."

Errores factuales detectados después en el thread (Emil Santurio +
Nicolas) y corregidos:
- David Hassoun es Chief Solution Architect at **Qualabs**, no
  Comcast. Participa en foros como representante de Qualabs.
- La sigla correcta es **SVTA** (Streaming Video Technology Alliance),
  no SBTA.

Acciones correctivas:
- Follow-up en el mismo thread con la corrección:
  https://qualabsuy.slack.com/archives/C06AR5G596H/p1778078422559609
- Profile de David Hassoun actualizado (4 menciones SBTA → SVTA + nota
  explicativa).
- Minuta del WG Comcast 2026-04-29 corregida in-place en Drive
  (mismo fileId, formato nativo verificado): SBTA → SVTA en 6
  ocurrencias, rol de David corregido en 2 lugares (header de
  participantes + recap).
- PROJECT.md de este proyecto actualizado con los datos correctos.

Aprendizaje guardado: cuando el contenido fuente tiene roles
ambiguos, validar contra el profile correspondiente antes de publicar.

## 2026-05-06 — Sección "Actors and Responsibilities" agregada al working doc

Nicolas pidió agregar una sección de actores y responsabilidades al
working doc. Discutimos la estructura, iteramos sobre el primer draft
(Nicolas señaló que el ADS no es responsable de respetar las
constraints del MPD — esa validación es del Player, que faltaba como
actor explícito).

- Iteración 1 (rechazada por Nicolas): solo dos actores Broadcaster +
  ADS. ADS responsable de respetar constraints. Nicolas corrigió.
- Iteración 2 (aprobada): tres actores. Broadcaster declara, ADS
  provee candidatos sin validar, Player valida y compone. El Player
  es la "goma de pegar" — autoridad efectiva sobre lo que aparece en
  pantalla.
- Draft final en inglés aprobado por Nicolas.

Inserción en el doc:
- Primer intento: pipeline HTML → upload (`gws drive files update
  --upload-content-type text/html`). Insertó la sección OK pero
  **rompió todos los comentarios** del doc — Drive reemplaza el
  contenido completo, los anchors de los comments se rompen y los
  comments quedan huérfanos / borrados.
- Nicolas restauró la versión anterior desde el historial de
  versiones.
- Segundo intento (correcto): Google Docs API `documents.batchUpdate`
  con operaciones quirúrgicas (`insertText`, `updateParagraphStyle`,
  `createParagraphBullets`). Solo modifica el delta, no toca el resto.
  Comentarios preservados (verificado: count idéntico antes/después,
  IDs idénticos).
- Faltó la tabla del Boundary Summary y unos sub-bullets nested. Una
  pasada adicional con `insertTable` y `updateParagraphStyle` lo
  cerró.

Decisiones formales registradas:
- ADR-001: Three-actor model (Broadcaster / ADS / Player).
- ADR-002: Rename OverlayPresentation → DynamicPresentation
  (decisión que ya venía del WG 2026-04-29; formalizada acá).

Aprendizaje guardado como regla durable (CLAUDE.md Rule 7.0.1):
**editar Google Docs existentes con comentarios o suggestions usar
siempre `documents.batchUpdate`, NUNCA `gws drive files update
--upload`** (es destructivo). Para Shared Drives agregar
`supportsAllDrives: true` en cada llamada.

## 2026-05-06 — Sección "Requirements" agregada al working doc

Después de Actors, Nicolas pidió agregar una sección de requerimientos
que gobiernan el diseño. Listó 5 requerimientos iniciales y pidió
estructura.

Estructura propuesta y aprobada:
- Functional Requirements: R1 (DASH 6th compliance), R2 (honour
  actor responsibilities).
- Governance Requirements: R3 (justify additions/omissions), R4
  (minimise net new constructs), R5 (do not recreate layout system —
  defer to HTML5/CSS, requirement de Thomas Stockhammer chair de
  MPEG-DASH).
- Out of Scope: layout engine propio, lógica interna del ADS,
  position semantics dentro de un layout.

Inserción al doc:
- Vía `documents.batchUpdate` quirúrgico (mismo método que para
  Actors). 23 requests en una sola llamada (insertText +
  updateParagraphStyle + createParagraphBullets + updateTextStyle
  para bolds en R1-R5).
- Comentarios preservados (verificado: 9 threads / 20 entries antes y
  después, IDs idénticos).
- Tiempo total: ~3 min.

Decisiones formales registradas:
- ADR-003: R5 — defer layout to HTML5/CSS via IAB CTV Ad Standard,
  do not recreate a layout system.

## 2026-05-06 — Comentarios del doc revisados, primer reply

Nicolas pidió listar los 9 threads abiertos del doc y sugerir
respuestas en base a las secciones nuevas (Actors + Requirements).

- Listados los 9 threads: 1 de Nicolas, 5 de David Hassoun, 3 de
  Olivier Cortambert.
- Para cada uno, sugerencia de respuesta anclada al texto recién
  agregado o a las decisiones tomadas (rename DynamicPresentation,
  R5 layout, three-actor model).
- 1 thread sigue requiriendo decisión del WG: el de Olivier sobre
  separar pause-ads del flujo OverlayPresentation
  (action-triggered vs timeline-triggered). Pendiente.

Reply enviado al thread:
- Comment de David Hassoun sobre `content="insert|replace"` ("? or in
  mpd list?"). Respuesta de Nicolas (posteada via
  `gws drive replies create`):
  *"On this — I don't think the URL itself should encode a fixed API.
  If a given ADS exposes an API that takes parameters via URL, that's
  fine on its side, but the MPD should carry the information the
  Player needs to know what to do, independent of whatever URL-level
  API the ADS happens to use. The normative contract is between the
  MPD event constraints and the Player; ADS-side URL semantics
  shouldn't leak into the spec."*
- Reply ID: `AAAB53AOAMA`.

Los otros 8 threads tienen sugerencias de respuesta listas en el
último mensaje de Telegram, pero quedan pendientes de envío hasta que
Nicolas decida cuáles postear.

## 2026-05-06 — Bitácora creada

Nicolas pidió guardar logs / bitácora de todo lo que hacemos en el
proyecto.

- Creado este archivo `LOG.md`.
- Backfill de las 4 entries del día.
- PROJECT.md actualizado para apuntar a `LOG.md` y para reflejar la
  estructura actual del working doc (Introduction, Actors,
  Requirements, Design Characteristics, ...).
- Status del proyecto: `starting` → `ongoing`.
- Decisiones formales archivadas en `decisions/` (ADR-001, ADR-002,
  ADR-003).

## 2026-05-06 — Split de context.md en 4 archivos

Después de agregar los 12 use cases (UC-01..UC-12), context.md
pasó de 19 KB a 40 KB y la lectura empezó a ser pesada para
alguien nuevo entrando al repo. Nicolas validó que la propuesta
inicial de partir el contexto era correcta — la simplificación
inicial (un solo archivo) sirvió como punto de partida pero ya no
escala.

Split aplicado:
- context.md (más liviano): Overview, Stakeholders, Glossary.
- actors.md (nuevo): three-actor model autocontenido.
- requirements.md (nuevo): R1-R6, Out of Scope, Design Characteristics.
- use-cases.md (nuevo): device classes D1-D5, matrix de cobertura,
  UC-01..UC-12.

Cross-links agregados entre los 4 archivos para mantener
navegabilidad. PROJECT.md actualizado con la nueva tabla de
navegación. Cada archivo es leíble en aislación.

Lección registrada: cuando un archivo de contexto cruza ~5000
palabras o ~25 KB, el costo de "todo en un solo archivo" supera al
beneficio. Próxima vez, partir antes de llegar a ese punto.

## 2026-05-06 — Refactor de R6: separar requirement (qué) de design (cómo)

Nicolas observó que la primera versión de R6 mezclaba *requirement*
con *design solution*. El requerimiento puro era "soportar
dispositivos con distintas capacidades, enumerarlas"; el resto (ADS
device-agnostic, multi-form candidates, Player elige según caps,
worst-case skip) ya es decisión de diseño.

Se aplicó el refactor:

- **R6 reformulado** (puro) en `context.md` y a aplicar al working doc:
  *"Support a diverse range of device capabilities (...). The
  supported device classes and the expected behaviour for each
  combination of device class and ad opportunity are enumerated in
  the Use Cases section. *How* the spec achieves this — the design
  choice that the ADS stays device-agnostic and the Player selects
  from multi-form candidates — is described in Design Characteristics
  → Device-aware ad selection, not here."*
- **Sección nueva en Design Characteristics** ("Device-aware ad
  selection") con la mecánica que sacamos de R6. Vive ahora en
  `context.md` y se va a insertar al working doc en la próxima
  iteración.
- **ADR-004** creado (`decisions/adr-004-device-aware-ad-selection.md`)
  con contexto, decisión, alternativas consideradas (3
  rechazadas: device-class header, capability bitmap, negociación
  bidireccional), y consecuencias. Hilos abiertos derivados sobre el
  schema concreto del response del ADS.

Lección a llevarme (ya generalizable a futuros requirements del
proyecto): **un requirement responde "qué"; un design characteristic
responde "cómo"**. Cuando se cuelan los dos en un requirement, las
alternativas de diseño quedan invisibles y los reviewers no saben
qué están aprobando. Si en el futuro escribo un requirement y noto
que incluye una mecánica concreta, separar antes de publicar.

## 2026-05-06 — Use cases iniciales (UC-01 a UC-12)

Nicolas pidió generar casos de uso reales que el spec debe cumplir,
cubriendo combinaciones de device classes (D1-D5) con tipos de ad
opportunity (linear pre-roll, mid-roll, ad pod, non-linear overlay,
pause-ad, linear+non-linear concurrente).

Se generaron 12 casos de uso en `context.md` (sección "Use Cases").
Resumen:

| Device | Pre-roll | Mid-roll | Ad pod | Overlay | Pause-ad | Concurrent |
|---|---|---|---|---|---|---|
| D1 | UC-01 | UC-02 | UC-12 | UC-03 | — | UC-04 |
| D2 | — | UC-05 | — | UC-11 | — | — |
| D3 | — | — | — | UC-06 | UC-07 | — |
| D4 | — | — | — | UC-08 | — | — |
| D5 | UC-10 | — | — | UC-09 | — | — |

Selección intencional: happy paths concentrados en D1 (top-tier);
graceful degradation distribuida en D2 (side-by-side fallback), D4
(image fallback), D5 (skip total); pause-ad tratada explícitamente en
D3 (UC-07) por ser caso action-triggered diferente.

Casos con preguntas abiertas para aterrizar en spec design (siete
ítems registrados en cada caso, resumen aparte): shape de priority
hints (UC-03), cross-slot rules (UC-04), pre-fetch vs lazy fetch para
pause-ads (UC-07), explicitar "no overlay shown" como outcome
legítimo (UC-08), si emitir request al ADS aunque no se renderice
nada (UC-09), promoción de layout en el Player (UC-11), política de
ad pods que exceden duración total declarada (UC-12).

Los casos están en `context.md` para ser consumidos por el diseño
del spec en iteraciones siguientes (proposal-drafts/).

## 2026-05-06 — R6 inicial: Device-agnostic ADS responses with multi-form candidates (luego refactoreado)

Nicolas marcó como muy importante incorporar un requerimiento adicional
que refuerza la separación de actores ya definida en el three-actor
model.

**Texto del requerimiento (resumen):** el ADS no conoce las
capacidades del dispositivo target. Los ad candidates que devuelve el
ADS pueden contener una o más formas renderizables (video, image,
HTML), opcionalmente con prioridades. El Player elige la mejor forma
que puede renderizar según sus capacidades. Worst case: si el
candidate solo tiene formas que el Player no puede renderizar, esa
oportunidad de ad se skippea (el Player decline el candidate y o bien
hace fallback al siguiente candidate o continúa con el primary
content uninterrupted).

**Por qué importa:** mantiene la separación entre ADS (provee) y
Player (decide qué renderizar) sin asumir que el ADS tenga conocimiento
de cada device target. Es viable para escenarios reales donde el ADS
sirve a millones de devices con caps heterogéneas (CTV, mobile, web,
embedded) sin tener que mantener una matriz device → caps.

**Acciones:**
- R6 agregado a `context.md` (sección Functional Requirements,
  ubicado después de R2 porque refuerza la separación de actores).
- R6 a agregar al working doc compartido en Drive vía
  `documents.batchUpdate` quirúrgico (preserva comentarios). Tarea
  en cola.

**Hilos abiertos derivados:**
- Definir cómo expresar las "formas renderizables" en el schema de la
  respuesta del ADS (`<svta:Ad><svta:Form type="video" priority="1"/>...`
  vs cada Form como sub-elemento separado). Tarea para una iteración
  de spec.
- Validar que los "priority hints" sean suficientes o si hace falta
  algún metadato adicional (ej. `device-class` hints, `min-resolution`,
  etc.).

## 2026-05-06 — Reestructura del proyecto: contexto inmutable + drafts iterativos + fases

Nicolas pidió que el repo del proyecto contenga todo el contexto
necesario **independientemente del Doc en Drive** (porque el Doc
puede cambiar, mientras que el contexto trabajado tiene que
sobrevivir). También pidió reflejar las **6 fases del proyecto** y
preparar la estructura para iteraciones largas de research / spec
generation.

Reestructura aplicada:

- Carpetas vacías eliminadas: `meeting-notes/`, `external-collab/`,
  `references/`, `prototype/`, `drafts/`. Se re-crean cuando aparezca
  el primer archivo de cada una.
- Carpeta nueva `proposal-drafts/`: iteraciones del spec, una por
  archivo, con fecha y versión (`YYYY-MM-DD-vN.md`). La idea es
  iterar sobre drafts independientes en el repo, sin tocar el Doc
  compartido, y mergear al Doc cuando una versión esté aprobada.
- Archivo nuevo `context.md` (uno solo, no partido en 5 — Nicolas lo
  pidió simplificado): contexto inmutable / source of truth con
  overview, glosario, actores, requirements, stakeholders.
- Snapshot inicial del Doc en `proposal-drafts/2026-05-06-v0.md` —
  baseline congelada para iterar.
- `PROJECT.md` reescrito como hub liviano: navegación + descripción
  de las 6 fases (con status independiente) + cadencia + cómo enviar
  tareas + hilos abiertos. El contenido sustantivo se movió a
  `context.md`.

Fases definidas:
1. WG interno alignment — `in-progress` (la fase actual).
2. External alignment — `starting`.
3. Internal design — `pending`.
4. External design iteration — `pending`.
5. Prototype implementation — `pending`.
6. Close-out — `pending`.

Workflow de iteración registrado en PROJECT.md:
- Decisiones nuevas → ADR.
- Cambios del proposal → nueva iteración en `proposal-drafts/` (los
  drafts anteriores quedan inmutables).
- Cambios del contexto base → update de `context.md`.
- Siempre → entry en `LOG.md`.
- Mergeo al Doc compartido solo cuando Nicolas dice explícitamente
  "esta versión va".
