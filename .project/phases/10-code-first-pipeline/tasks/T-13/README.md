# T-13 — la promoción es un script (2026-11-23)

Registro del día; lo vigente está en `bin/promote.py --help`.

- Siete compuertas, todas corren y cada falla se nombra: archivos del juego completo, `assemble-spec --check`, `lint-spec`, `check-trace`, `check-promotable` (sobre copias sin versión de los sidecars), `compare-candidates` (sólo `BETTER THAN PUBLISHED` pasa), `check-dash-conformance` con el XSD del candidato. Copia nueve archivos (spec, XSD, validación, detail review, `conformance-tests.md`/`.json`, audit, comparación, traza), escribe `PROVENANCE.md` con la tabla de compuertas e `inputs.sha256` con `spec-source/` incluido. `check-dist-freshness.py` ahora incluye `spec-source/` y acepta `--dist DIR`.
- **Sobre v12.6 se niega** (`--dry-run`, exit 2) y nombra cada condición: faltan el XSD, los `conformance-tests.*` y la traza; lint con 74 hallazgos; check-promotable `UNCERTAIN=2`; compare sin `conformance-tests.json` del candidato; conformance sin XSD.
- **Un candidato de prueba en verde** (compuertas reemplazadas por stubs, raíz y dist en scratch): `PROMOTED`, el dist de scratch con los nueve archivos más `PROVENANCE.md` e `inputs.sha256`, y `check-dist-freshness.py --dist <scratch>` → `0 OK … 143 archivos, sin diferencias`.
- `bin/test_promote.py`, 6 tests OK: todo en verde copia el juego completo; `--dry-run` no copia; cada una de las seis compuertas de script fallando bloquea sin copiar (1); `NO BETTER` y `WORSE` bloquean; una que no puede decir da 2 sin copiar; un archivo faltante bloquea y se nombra.
- Mutaciones (una por regla, sólo su test): veredicto de compare, compuerta de archivos, rama de falla, rama de "no se puede decir" → las cuatro rojas.
- La compuerta `trace` depende de `bin/check-trace.py` (T-08).
