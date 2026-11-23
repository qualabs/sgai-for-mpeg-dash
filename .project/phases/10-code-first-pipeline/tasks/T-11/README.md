# T-11 — el pre-spec sin los pasos huérfanos y con salto por hash (2026-11-23)

Registro del día.

**Nadie lee los dos artefactos.** `grep -rl` de cada nombre sobre el repo,
sin `.git`, `.worktrees`, `output*` ni las carpetas de fases (`grep.txt`):
`conformance-assertions` y `uc-coverage-matrix` aparecen sólo en su propio
prompt, en `build-all.prompt` que los invocaba, en `prompts/README.md`, en
`dist/inputs.sha256` (que registra todos los insumos) y en la ADR 0072.
**Control positivo:** el mismo grep con `dash-gap-analysis`, que sí se
consume, lo encuentra en sus lectores `prompts/2-build/apply-context-delta.prompt`
y `prompts/2-build/build-spec.prompt`; la búsqueda encuentra a los
consumidores cuando existen.

**Retirados:** `prompts/1-pre-spec/extract-conformance-assertions.prompt` y
`build-uc-coverage-matrix.prompt` (siguen en git); los Steps 2 y 4 de
`build-all`. Los archivos de `context-analysis/` quedan como registro.

**Salto por hash:** `bin/step-inputs.py check|record` para
`analyze-dash-gap` y `build-error-semantics`; el IAB no está porque su fuente
es un documento vivo y corre siempre. `bin/test_step_inputs.py`, 7 tests:
sin manifiesto → 2; `touch` (mtime +1 h) → sigue fresco; un byte con el mismo
mtime → 1 nombrando el archivo; un archivo nuevo en `context/` → 1; cambiar el
prompt → 1; un archivo no declarado no cuenta; CLI mala → 64.
Mutaciones: comparar sólo el conjunto de nombres (no el contenido) → 2 tests
rojos; ignorar altas y bajas → 1 rojo.
