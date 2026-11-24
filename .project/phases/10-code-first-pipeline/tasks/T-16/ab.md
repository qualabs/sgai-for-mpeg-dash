# T-16 — medición A/B (2026-11-23)

Medido con `bin/measure-run.py` (una vez por llamada; los subagentes cargados al paso de su padre) y, para las llamadas de un turno de la validación, con sus propios transcripts (sesiones en directorios temporales posteriores al arranque de la corrida). "Entrada" = fresca + escritura + lectura de cache.

## Una vuelta de refine

| | Pipeline viejo (T-01) | Pipeline nuevo, 1.ª corrida | 2.ª corrida | **3.ª corrida (final)** |
|---|---|---|---|---|
| Cómo validaba | 18 subagentes caminantes | igual (el prompt nuevo, caminantes subagentes) | caminantes de un turno, orquestador y búsqueda abierta agentes | `bin/validate.py`: todo código, el modelo sólo en llamadas de un turno |
| orquestador | 1,26M | 0,88M | 1,66M | 3,56M |
| refine | 2,04M | 3,25M | 2,13M | 2,57M |
| revisión de nombres | — (no llegó) | — | — | 1,44M |
| validación | **49,11M sin terminar** | 21,12M sin terminar | 16,35M (agentes) + ~1,4M (caminantes) sin terminar | **2,41M**, dos corridas completas (89 llamadas de un turno) |
| audit, compare | no llegó | no llegó | no llegó | arrastrado / código (0) |
| **Total** | **> 51,1M (cota inferior)** | cortada en 24,7M | cortada en 20,1M | **9,99M, la vuelta entera** |

- **−80,5% como mínimo** contra la cota inferior del viejo (que no terminó la validación ni corrió review, audit ni compare). La meta era −70%.
- La validación pasó de >49,1M a 2,41M (−95%). Lo que queda caro son los tres agentes LLM de la vuelta: el orquestador de `build-all` (3,56M), el refine (2,57M) y la revisión de nombres (1,44M), cada uno con ~64k de contexto fijo por llamada (`fixed-cost-per-call.md`).
- **Comparable, no idéntico:** las dos vueltas caminan toda la población. La nueva caminó 192 unidades porque la traza de v12.7 viene de v12.6 sin el hash de texto de cada unidad (la transición por la renumeración de `context/03`); con hashes, `validate.py --plan-only` da 56 unidades en 8 lotes. La validación corrió dos veces porque 6 unidades salieron `not-verifiable` ("asks for sections") y el Step 9.5 re-corre ante exit 2; arreglado después (`walk-batches` da una tercera llamada a la unidad que sólo pide secciones), y el parseo de las listas de secciones de la búsqueda abierta que provocó 44 reintentos (`validate.py section_keys`).
- **El veredicto de la vuelta (WORSE) no es del pipeline:** la base v12.7 es v12.6 limpia, que nunca absorbió los cambios de `context/` posteriores; el refine no puede arreglar los 6 FAIL de carriers. Los artefactos de v12.8 se borraron como manda 9.7.
- Una vuelta de mantenimiento con la traza ya con hashes caminaría ~56 unidades: estimado ~0,6M de validación, ~8M la vuelta, dominada por los tres agentes.

## El incremental: el mismo delta del 2026-10-27

En `.worktrees/ab-inc`: el código del pipeline nuevo, `context/` en `61f7a8b` (la cabeza de aquella corrida), base v12.6, anchor `924afcb` (el mismo `git diff --stat`: 7 archivos, +1046 −281). Dos desvíos obligados por correr un `context/` anterior a chequeos atados al de hoy: se saltó el gate 0.7 (el índice "Interfaces" no existía) y el nivel 2 de conformidad y los escenarios reportan pins viejos (exit 2) que el bucle de artefactos tomó como conocidos. Las dos corridas terminan igual: **MAJOR RECOMMENDED**.

| Paso | Viejo (2026-10-27) | Nuevo |
|---|---|---|
| orquestador | 2,73M | 2,90M |
| `analyze-dash-gap` | 5,91M | 2,12M |
| `build-error-semantics` | 1,39M | 1,73M |
| `analyze-iab-ad-templates` | 1,05M | 1,30M |
| `extract-conformance-assertions` | 4,11M | retirado |
| `build-uc-coverage-matrix` | 1,41M | retirado |
| `apply-context-delta` | 25,24M | 4,14M |
| **Total** | **41,83M** | **12,18M (−71%)** |

- **Lo comparable uno a uno** es el pre-spec: 13,87M → 5,15M (−63%), por los dos pasos retirados y el gap más barato.
- **El apply no es comparable uno a uno.** El viejo editó 82 secciones antes de que el chequeo de alcance dijera MAJOR; el nuevo dejó de editar al primer cambio que necesita estructura (`REFUSED: MAJOR`, su §9) y restauró la fuente. El resultado es el mismo y el trabajo que el viejo descartaba ya no se paga, pero el número no mide un incremental que llega al final.
- **Hallazgo:** el apply clasificó 68 cambios como `needs-structure`; según su propio informe, unos 16 lo son (los cinco constructs sin carrier y lo que cuelga de ellos) y el resto tenía lugar. Que un solo cambio estructural haga abandonar el incremental entero es la lectura literal de §9; queda como entrada para el v13, que es un mayor y lo aplica todo sin tope.
- La limpieza única de las marcas viejas toca el 29,7% de las líneas: el chequeo de alcance no la cuenta, pero queda al borde del tope de 0,30.
- **No se midió:** un incremental que llegue a validar y refinar. Con lo medido en la vuelta de refine (validación ~1–2M por código), un incremental completo quedaría en el orden de 12M + ~10M de la vuelta.

## Resultado

| Corrida | Viejo | Nuevo | Δ |
|---|---|---|---|
| Vuelta de refine | > 51,1M (cota inferior) | 9,99M | ≤ −80% |
| Incremental hasta el chequeo de alcance | 41,8M | 12,2M | −71% |

La meta (≥ −70% en los dos) se cumplió. Lo que queda caro son los agentes LLM que siguen siendo agentes (orquestadores, apply, refine, revisión de nombres): cada llamada paga ~64k de contexto fijo (`fixed-cost-per-call.md`). Pasarlos a llamadas de un turno es el próximo escalón, y no entra en esta fase.
