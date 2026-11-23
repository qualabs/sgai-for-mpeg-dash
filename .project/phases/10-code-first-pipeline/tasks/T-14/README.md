# T-14 — la suite entera (2026-11-23)

Registro del día. Las 21 suites de `bin/test_*.py` (las cinco de la fase 09 y las dieciséis de esta), corridas una vez entera con las dependencias que piden (`uv run --with lxml==6.1.3 --with pyyaml==6.0.3 --with jsonschema==4.25.1`): **420 tests, todas OK** (`suite.txt`).

Las campañas de mutación, una por regla de negocio de cada script nuevo y corriendo sólo los tests de esa regla, están en la evidencia de cada task: T-01 (medidor), T-02 (armado), T-03 (18 reglas), T-04 (16), T-05 (34), T-06 (26), T-07 (10), T-08 (33), T-09 (23), T-10 (6), T-11 (2), T-12 (33), T-13 (4). Las que sobrevivieron en una primera ronda (T-05, T-06, T-08, T-09, T-10, T-12) encontraron un test flojo o código muerto, y se corrigieron antes de cerrar la task.
