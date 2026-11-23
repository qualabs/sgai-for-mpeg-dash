# T-02 — spec-source/ extraída de v12.6 y armada byte a byte (2026-11-23)

Registro de lo que se midió ese día; lo vigente está en `bin/assemble-spec.py`.

- `extract-source.py output/v12.6-sgai-spec.md spec-source` (este directorio): 94 bloques → 84 XML (83 a `spec-source/examples/<parte>/<sección>-<n>.<ext>`, el de §5.10.1 a `spec-source/syntax/sgai-extension.xsd`) y 10 pedidos `.http`. El diagrama ASCII de §6 queda en la prosa. `sgai-spec.src.md`: 5.430 líneas, 94 directivas.
- `bin/assemble-spec.py --check dist/sgai-spec.md` → `identical … sha256 197cbd888adccd34b13c7e085e36907d7f7d859d9906b90e65949ba559e88a22`, el sha256 de `dist/sgai-spec.md`.
- `spec-source/syntax/sgai-extension.xsd` es idéntico (`cmp`) al que `emit-extension-xsd.py` saca de v12.6.
- Negativos (`bin/test_assemble_spec.py`, 6 tests OK): un byte cambiado en `annex-c/C.2-1.mpd` → exit 1 nombrando el fixture; la prosa cambiada → exit 1 "(prose)"; un fixture borrado → exit 2; el XSD sin newline final → exit 2; línea de comandos mala → 64.
