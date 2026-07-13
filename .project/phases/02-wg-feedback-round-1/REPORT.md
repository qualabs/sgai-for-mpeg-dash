# Phase 02 — Working-group feedback round 1 — Closure report

**Phase:** `02-wg-feedback-round-1`
**Status:** closed (2026-07-13)
**Reviewer processed:** David Hassoun (WG contributor)

## 1. Resumen

La fase procesó la primera ronda de feedback del working group sobre la spec
de SGAI, centrada en la review de David Hassoun. El trabajo arrancó con el
cross-reference de sus 3 archivos editados (round 1, sesión del 2026-05-20)
contra el estado vigente de `context/`, clasificando cada uno de sus 10 items
como ya-resuelto, cambio-necesario u abierto-a-discusión. Ese reporte
(`hassoun-feedback-crossref.md`) fue el producto de trabajo de la fase y la
fuente de verdad de las tareas T-01..T-08.

Sobre esa base se resolvieron las tres decisiones abiertas, se aplicaron las
tres ediciones de documentación a `context/`, y se cerró el follow-up. Una
segunda ronda de feedback de David (thread de Slack en `#wg-comcast`,
2026-05-29) cerró los tres puntos previamente abiertos más un cuarto (U1),
consolidando el modelo del L-box, el fallback dependiente de contenido para
UC-07, y el pause-ad como overlay parcial. Al cierre, los 10 items de David
quedan resueltos e incorporados a `context/`.

## 2. Decisiones tomadas

- **Layout no se declara por clase de dispositivo** (T-04). El Publisher no
  emite layouts por clase de dispositivo. El mismo resultado se logra con un
  fallback ordenado posicional del lado del Player (R5/R5.1/R5.2/R5.5/R5.6/R5.7)
  y, para regiones vacías, con un background provisto por el anunciante. Preserva
  "la capacidad del dispositivo es autoridad exclusiva del Player" (R5/R5.4) y
  DP-1. Ilustrado por UC-09.
- **Modelo del L-box** (T-04 / T-05, ronda 2). El L-box (L-shape / squeezeback)
  tiene un unico creativo publicitario (imagen, video o web) colocado siempre
  full-frame en el fondo, con el contenido primario reducido compuesto encima.
  Es su propio layout, modelado por la nueva R27; el side-by-side / double-box
  queda en R26.
- **Fallback dependiente de contenido para players legacy** (T-02 / UC-07). Para
  contenido live, skip-and-continue; para no-live / VOD, el Publisher puede
  autorear un corte lineal estandar como fallback para monetizar la oportunidad.
- **Pause-ad como overlay parcial** (T-06 / R21). R21 se relajo de "el pause-ad
  DEBE ser fullscreen" a "el pause-ad PUEDE ser fullscreen O un overlay parcial".
- **UC-02 vs UC-06 se mantienen separados** (T-03 / U1). Se resuelve el conflicto
  de round 1 a favor de la decision v1: se mantienen discretos.

Estas decisiones se registraron en `TASKS.md` y en `.project/LOG.md`. No se
crearon ADRs formales nuevos en esta fase. El ADR global `0001` (deferir spatial
caps a IAB CTV) es contexto relacionado pero precede la apertura de la fase.

## 3. Tareas

Todas las tareas de la fase quedaron `done`:

- **T-01** — Cross-reference de la feedback de David contra la spec vigente.
- **T-02** — UC-07: fallback dependiente de contenido para players legacy.
- **T-03** — UC-02 vs UC-06: se mantienen separados (David: "sounds good").
- **T-04** — Layout device-agnostic + interseccion Player-side (UC-09).
- **T-05** — Background/L-box documentado (R26 side-by-side, R27 L-shape).
- **T-06** — Pause-ad como overlay parcial (R21 relajado).
- **T-07** — Reescritura del wording "CONFUSING" en UC-04 D2.
- **T-08** — Split ADS+APS: incorporado y commiteado en la spec. La confirmacion
  explicita con David queda como follow-up externo no bloqueante.

Ninguna tarea fue abandonada.

## 4. Hilos abiertos

- **Confirmacion con David del split ADS+APS** — follow-up externo no bloqueante.
  El split esta en la spec commiteada; falta el visto bueno explicito de David de
  que el split matchea su intencion del rename ADS->APS. A levantar en el proximo
  intercambio en `#wg-comcast`.
- **Feedback de otros reviewers** — Alex Giladi, Thasso, SVTA Ads WG. Fuera de
  scope de esta fase; disparan una fase de round 2 cuando llegue ese trabajo.
- **PR #6** — el conflicto de spatial caps (issue #4 / ADR 0001) siguio su curso
  fuera de esta fase; la fase no lo gestiono.

## 5. Riesgos materializados

Ninguno material. El feedback de David llego fuera del canal esperado (no pudo
editar el Doc compartido, devolvio archivos con comentarios inline por Slack),
lo que agrego un paso de cross-reference manual, pero no bloqueo ni desvio la
fase. Las decisiones de diseno que David empujaba en direccion opuesta a la
decision v1 (UC-02 vs UC-06) se cerraron por acuerdo sin friccion.

## 6. Recomendaciones para la proxima fase

- La progresion de largo plazo del proyecto sigue siendo foundation -> design ->
  prototype -> closeout. El PROJECT.md sugiere `02-spec-iteration` para la
  iteracion de foundation; dado que la fase de feedback ya esta numerada 02, la
  proxima fase de iteracion/feedback deberia abrirse como `03-...`.
- Si el proximo trabajo es otra ronda de feedback del WG (mas reviewers o un
  segundo pase), abrir `03-wg-feedback-round-2`. Si en cambio el foco pasa a
  cerrar los ADRs fundacionales y agregar el doc de requisitos no funcionales,
  abrir `03-spec-iteration`.
- Levantar el follow-up de confirmacion con David como primer touchpoint externo
  de la proxima fase, para cerrar el ultimo hilo de round 1.
- No abrir la proxima fase hasta que Nicolas lo decida explicitamente.
