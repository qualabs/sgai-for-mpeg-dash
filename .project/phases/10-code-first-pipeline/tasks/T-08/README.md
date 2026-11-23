# T-08 — la validación se apoya en una traza verificada por código (2026-11-23)

Registro de lo que se midió ese día; lo vigente está en `bin/check-trace.py --help`,
`bin/validation-summary.py --help` y `prompts/3-post-spec/validate-spec.prompt`.

- `bin/check-trace.py` (check, `sources`, `stale`, `batch`), `bin/validation-summary.py`;
  `bin/check-promotable.py` lee `spec-validation.summary.json` si está al lado del sidecar
  (sha256 distinto = "no se puede saber").
- `output-analysis/v12.6-trace.json`: derivada por `derive-v12.6-trace.py` (acá) del mapa de
  `v12.6-spec-validation.md`: 211 unidades, 387 referencias a sección, 381 citas, verbatim.
- `population-924afcb.tsv`: la población de `context/` en el commit contra el que se validó v12.6.

## Citas no literales de v12.6: 33

`check-trace.py output-analysis/v12.6-trace.json --population population-924afcb.tsv` → exit 1,
33 `T-QUOTE` y nada más. Con la población de hoy suma 39 `missing` y 38 `extra`: `context/03`
se renumeró después de v12.6 (no es "una UC de más").

| Causa | Citas |
|---|---|
| `/` en lugar del `\|` de una tabla | 25 |
| `…` adentro de la cita (texto omitido) | 7 |
| un `<!-- refine -->` corta la oración en la spec (R6.3, §4.6) | 1 |

Contra el 28/364 medido antes: no se reproduce. Acá hay 381 citas (388 si se parte en `…`);
normalizando las barras, como aquella medición, quedarían 8. El script de aquella medición no
quedó en la evidencia de T-06.

## Fuente del veredicto

| Población | code | vector-pending | llm |
|---|---|---|---|
| hoy (212) | 34 (14 con `residual`) | 59 (3 con `residual`) | 119 |
| traza v12.6 (211) | 31 | 47 | 133 |

Contra el mapa de v12.6: R12.1 y R34.1 dicen `met` y su regla de código da FAIL; R40.1 dice
`partial` y su regla da PASS.

## Contexto por llamada de caminante

Lotes de 8 unidades `llm` de la traza v12.6 armados con `batch`: mediana 49k caracteres, máximo
72k (~12k y ~18k tokens a 4 caracteres por token), más ~4k de instrucciones. Antes: 120–200k por
llamada. La spec entera son 414k caracteres (~103k tokens). Un refine como v12.5 → v12.6:
`stale` marca 7.12, L.7, L.8, R.2.4 (lo mismo que dice el sidecar de v12.6) y 4 unidades, un lote
de 42k caracteres.
