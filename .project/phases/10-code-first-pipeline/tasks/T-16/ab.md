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

## El incremental

(pendiente)
