# T-10 — la comparación es código (2026-11-23)

Registro del día; lo vigente está en `bin/compare-candidates.py --help`.

- Lee los sidecars con los mismos parsers de `check-promotable.py`; compara la cobertura **unidad por unidad** sobre las unidades de los dos lados; exit 2 si comparten menos del 90% de la población menor.
- **El caso que el LLM sumó:** v12.6 contra los sidecars de `dist/` del commit `225dacf` (v7.2) → `exit 2: populations not comparable: 0 shared units of 30 published and 211 candidate (per-requirement against per-criterion)`.
- v12.6 contra el `dist/` de hoy (que es v12.6), con el `conformance-tests.json` de v12.6 generado por código → `NO BETTER THAN PUBLISHED (0 worse, 0 better, 211 shared units)`; el informe en `v12.6-vs-dist.md`. Las categorías de conformidad que `dist/` no tiene salen n/a y fuera de la regla.
- `bin/test_compare_candidates.py`: 9 tests OK (igual, met→contradicted WORSE, met→partial no es WORSE, partial→met BETTER, FAIL arriba/abajo, dist sin tests fuera de la regla, v7.2 → 2, candidato sin tests → 2, CLI 64).
- Mutaciones, una por regla, sólo su test: solapamiento, worse, better, FAIL, dist n/a, tests requeridos del candidato → las 6 rojas. La de `better` **sobrevivió primero**: el test buscaba "BETTER THAN PUBLISHED", que está contenido en "NO BETTER THAN PUBLISHED"; los tests ahora comparan el comienzo del veredicto, y la mutación da rojo.
- Retirado `prompts/4-auto-refine/compare-spec-versions.prompt`; `build-all` (9.6, 9.7 y la configuración del Step 9) y `build-incremental` (Stage 5) llaman al script.
