---
closed: 2026-10-27
---
# Phase 07 — Alinear context/ con SVTA2053 v3 — Closure report

## 1. Summary

`context/` absorbió las decisiones de Nicolás sobre el análisis de SVTA2053 v3
(`output-analysis/2026-10-27-david-v3-vs-context.md`, commiteado en `58d8168`):
una opción cuyo recurso no carga se saltea y no su candidato (R5.9); cada
entrada del playhead a una ventana de overlay o squeezeback es una ejecución
que resuelve de nuevo (R34.6, R34.7, R36.4); ONCE alcanza a las tres familias
no lineales con `@executeOnce` y el contador de la base (R34.1–R34.5); una
ejecución tardía arranca desde el primer candidato salvo que la ventana declare
`@startWithOffset` (R34.8, R34.9); la ventana se suspende durante un lineal
heredado y se retoma en la misma ejecución (R40.4, R4.11); DP-4 hace opcional y
anotado lo que el Player origina sobre el dispositivo o el espectador, sin los
beacons; y tres precisiones (R29.7, R40.1, R14.1). UC-21 y UC-22 son nuevos.

La spec no se reconstruyó: el incremental pidió mayor y Nicolás lo dejó para el
build v13 (sección 4).

## 2. Decisions made

ADR 0022 a 0028, todas `accepted`, `scope: project`:

- 0022 — una opción cuyo recurso falla su primer pedido se saltea, no su candidato.
- 0023 — una ventana se ejecuta cada vez que el playhead entra, y cada ejecución resuelve.
- 0024 — once-per-session alcanza overlay y squeezeback, con el contador y el carrier de la base.
- 0025 — una ventana interrumpida por un lineal heredado se retoma, en la misma ejecución (la 0020 sigue en pie).
- 0026 — lo que puede identificar al dispositivo o al espectador es opcional y lleva nota.
- 0027 — cómo resuelve el APS una capacidad indeterminada sigue siendo suyo; devolver todas es una sugerencia.
- 0028 — una ejecución tardía arranca desde el primer candidato salvo `@startWithOffset`.

La 0028 no estaba en el diseño original: salió de la decisión de Nicolás de
replicar lo que la base define para entrar a mitad del intervalo. Se verificó
contra la copia primaria (§5.16.4, Table 62; §5.16.2.2.6) antes de escribirla.

## 3. Tasks

| id | estado | evidencia |
|---|---|---|
| T-01 | done | `58d8168` |
| T-02 | done | `f1c642a` |
| T-03 | done | `cd9c260` |
| T-04 | done | `e1666a0` |
| T-05 | done | `301b031` |
| T-06 | done | `d87fcef` |
| T-07 | done | los tres chequeos en `0` sobre `d87fcef`, y cada uno visto en `1` rompiéndolo a propósito |
| T-08 | abandoned | el incremental dio `MAJOR RECOMMENDED`; sin rebuild por decisión de Nicolás (`df7f13d`) |

## 4. Open threads

- **El build mayor v13**, ítem `roadmap/major-build-v13` (`idea`). Lo que
  necesita está en la tabla `## Not placed` de
  `output-analysis/v12.7-context-delta.md`: 19 cambios `needs-structure`, casi
  todos de commits anteriores a esta fase (`622b204`, `14fa827`: los carriers
  de R41, R42, R44, R47, R48 y R23.2). De esta fase sólo quedan afuera lo que
  cuelga de esos carriers: los beacons de slot de R13.7 (en R34.6, R40.4, UC-21
  y UC-22) y el beacon de error de R5.9 (carrier de R42).
- **`dist/` sigue desactualizado** respecto de sus entradas
  (`check-dist-freshness.py`: 7 diferencias antes del build) hasta el v13.
- **Huecos que vio el build en `context-analysis/error-semantics.md`**, para
  una fase futura: E1 (reintentos del pedido de resolución), E5 (una resolución
  que llega cuando la ventana ya terminó), E11 (si un candidato abortado cuenta
  como renderizado). Y `uc-coverage-matrix.md`: R24, R32, R33 y R47 sin caso de
  uso.

## 5. Risks that materialized

- **El delta excedió el camino incremental.** Mitigación prevista: no forzarlo
  y avisar; se cumplió, y Nicolás decidió posponer el mayor.
- Los demás riesgos de `PHASE.md` quedaron resueltos en el texto (UC-21, UC-22,
  la excepción de DP-4) y no se materializaron.

## 6. Recommendations for the next phase

- Hacer el v13 una sola vez, cuando entren document-first, el perfil
  multi-asset y multiview, como decidió Nicolás; antes, decidir en `context/06`
  los carriers que dejó abiertos `622b204`, porque son la mayoría de lo que el
  mayor tiene que resolver.
- **Hallazgo para el skill create-project:** `start.sh` calcula el número como
  el máximo de `phases/` más uno y no conoce los números liberados. Dio `06`,
  que había usado multiview antes de volver al roadmap; la regla del proyecto
  (2026-10-15) es no reusarlos, y se renombró a mano a `07` (`3a971c5`).

## 7. Post-execution corrections

`grep -n "post-ejecuci" TASKS.md`: una línea, en T-08 — el incremental pidió
mayor y la tarea se cerró sin rebuild. No es una corrección de algo mal hecho
sino el registro de por qué no se hizo; ninguna tarea de texto necesitó
corregirse después de cerrada.

## 8. Documentation review

- **`description` de `PHASE.md`**: reescrita como lo que la fase fue.
- **`docs/arc42/`**: el proyecto no tiene `docs/`; nada que revisar.
- **`README.md` del proyecto**: no cambió; describe el proyecto, cómo leerlo y
  cómo construir, y la fase no tocó nada de eso.
- **`CLAUDE.md` del proyecto**: no cambió; la fase no agregó carpetas, prompts
  ni chequeos.
- **`.project/knowledge/`**: no existe.
- **`CLAUDE.md` y `knowledge/` de la raíz**: no aplican; la fase no cambió nada
  que valga para todo el repo. El hallazgo de `start.sh` es del skill y va en
  la sección 6.
- **Runbook**: el proyecto no tiene uno aparte del `CLAUDE.md`.
- **`context/`** es la entrada de la fase, no documentación suya: sus cambios
  están en las tareas.
