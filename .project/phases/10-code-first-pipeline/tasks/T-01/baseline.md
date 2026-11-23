# T-01 — la línea de base del pipeline viejo (2026-11-23)

Medido con `bin/measure-run.py`: una vez por llamada a la API; un subagente
que no nombra un prompt se carga al paso de su padre. "Entrada" = fresca +
escritura de cache + lectura de cache. Las tablas completas están al lado.

## Incremental (sesión `5ad312df`, 2026-10-27)

El incremental sobre v12.6 que terminó en `MAJOR RECOMMENDED`: pre-spec y
`apply-context-delta`, sin validación ni refine.

| Paso | Entrada | Salida | Llamadas |
|---|---|---|---|
| orquestador | 2,73M | 13,6k | 26 |
| `extract-conformance-assertions` | 4,11M | 0,6k | 29 |
| `analyze-dash-gap` | 5,91M | 26,5k | 36 |
| `build-uc-coverage-matrix` | 1,41M | 0,7k | 13 |
| `analyze-iab-ad-templates` | 1,05M | 0,2k | 13 |
| `build-error-semantics` | 1,39M | 10,2k | 14 |
| `apply-context-delta` | 25,24M | 47,6k | 88 |
| **Total** | **41,83M** | **99k** | **219** |

## Una vuelta de refine sobre v12.6 (pagada, P-1)

Corrida en `.worktrees/baseline-refine` (commit `eb16e7f`), con el Step 9 de
`build-all` limitado a una iteración. Sesión `4074f7ec`:

| Paso | Entrada | Salida | Llamadas |
|---|---|---|---|
| orquestador | 1,26M | 4,7k | 15 |
| `refine-spec` | 2,04M | 13,0k | 21 |
| `validate-spec` (con sus 18 caminantes) | **49,11M** sin terminar | 0,30M | 456 |
| **Total** | **52,42M** | 0,32M | 492 |

**Se cortó** en la validación por el límite de 5 horas de la cuenta, antes
de escribir su sidecar. Un segundo intento desde la validación (sesión
`28fed40a`) se paró a los 35 s por decisión del coordinador: la vuelta
aprobada era de ~40–50M y ya iba por encima. Gastó 0,75M. **Total gastado en la
línea de base: 53,2M.** Lo perdido: los 49,1M de la validación, que no dejó
sidecar, y los 0,75M del segundo intento. No se midieron review, audit ni
compare.

## Lo que queda como línea de base

- **Incremental: 41,8M medidos.**
- **Una vuelta de refine con el pipeline viejo cuesta más de 51,1M**:
  refine 2,0M más la validación sola, 49,1M sin terminar. Es una cota
  inferior; faltan review, audit, compare y el resto de la validación.
- **Lo que cambió del diagnóstico:** el refine en sí es barato (2,0M, 21
  llamadas). Lo caro es la validación: reparte la población en 18 caminantes
  y cada uno relee la spec (~120–200k de contexto por llamada). El diseño
  estimaba la vuelta en ~40–50M con el costo repartido; medido, la vuelta
  pasa de 51M y la validación sola es el 96% de lo gastado. T-08 es la task
  que más pesa en la meta.
