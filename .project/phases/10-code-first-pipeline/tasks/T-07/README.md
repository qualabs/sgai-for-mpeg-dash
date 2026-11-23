# T-07 — toda edición de la prosa es un parche (2026-11-23)

Registro del día; lo vigente está en `bin/apply-spec-patch.py --help`.

- `bin/spec_sections.py` (la división en secciones, compartida), `bin/spec-section.py list|get|find`, `bin/apply-spec-patch.py`.
- Sobre la fuente de v12.6: 309 secciones, claves únicas, la división es sin pérdida (`join(split(t)) == t`).
- Ops: `find/replace` en una sección (find exactamente una vez), `replace_section`, `insert_after`, `delete_section`, y `file` para un artefacto de `spec-source/`. Se rechaza: find ausente o repetido, tocar una línea de directiva, un reemplazo que agrega o cambia un encabezado, `replace_section` con otra clave o sin la directiva que tenía, insertar una clave existente, borrar una sección con directivas, op sin `reason`, `file` sobre `syntax/tables/` (generado), sobre la prosa o fuera de `spec-source/`, un op que no cambia nada, y el alcance (cambió algo no declarado, o se declaró algo que no cambió). `--max-fraction` da MAJOR.
- `bin/test_apply_spec_patch.py`: 27 tests OK.
- Mutaciones, una por regla, corriendo sólo su test: las 10 dan rojo.

```
once | test_find_twice | FAILED (failures=1)
directive | test_find_on_directive | FAILED (failures=1)
heading | test_replace_adds_heading | FAILED (failures=1)
rs-key | test_replace_section_other_key | FAILED (errors=1)
rs-dir | test_replace_section_drops_directive | FAILED (failures=1)
ins-exists | test_insert_existing_key | FAILED (errors=1)
del-dir | test_delete_section_with_directive | FAILED (failures=1)
reason | test_no_reason | FAILED (failures=1)
fraction | test_max_fraction | FAILED (failures=1)
scope | test_undeclared_change_is_caught | FAILED (failures=1)
```

- `prompts/4-auto-refine/refine-spec.prompt` reescrito: precondición `assemble-spec --check` del candidato; lee por sección; devuelve `v<N.M+1>-patch.json`, lo aplica y arma; sin anotaciones; los gaps a `v<N.M+1>-refine-gaps.md`. La recolección de issues de los sidecars queda como estaba (T-08 y T-09 la ajustan a sus formatos nuevos).
- Hallazgo para el v13: la línea `**Status:** candidate specification, build iteration 12.4.` de la spec publicada (v12.6) no avanzó en dos refines; el armado puede generarla.
