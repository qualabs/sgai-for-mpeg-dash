# T-12 — los orquestadores corren sobre la fuente (2026-11-23)

Registro del día; lo vigente está en los prompts y en el `--help` de cada script.

## Qué cambió

- `prompts/2-build/apply-context-delta.prompt` reescrito, con `MODE=incremental|major`: precondición `assemble-spec --check` del candidato base; la limpieza única (§1); primero los artefactos (XSD, `syntax.yaml`, fixtures, vectores) por ops `file` en bucle con `check-dash-conformance --source` y `check-scenarios` contra la corrida de la base; después la prosa por parches de sección; armar con `--version`, `lint-spec`, `gen-syntax-tables --check`. La tabla `## Sections changed` sale de los registros de parche, del diff de los manifiestos y de `{{version}}`, nunca de comparar los documentos (eso lo hace `scope`). Clases de *Not placed*: `needs-structure` (sólo incremental), `ambiguous-source`, `conformance-fail`, `tool-limit`.
- `prompts/2-build/build-spec.prompt` retirado (`git rm`); sus reglas de escritura pasaron a `apply-context-delta`.
- `prompts/build-all.prompt`: Step 6 = `apply-context-delta` en modo mayor sobre el último candidato (sin tope; `scope --max-fraction inf`); Step 6.1 con `cmp` contra `spec-source/syntax/sgai-extension.xsd`; post-spec 8.0 → 7 → 7.5 → 8; 7.5 sólo nombres, sin autofix; audit una vez por mayor o incremental; vuelta 9: refine (parche) → armar → lint → conformance `--source` → validación acotada por `check-trace stale` → nombres → audit copiado → `check-promotable` → `compare-candidates`; rollback por `apply-spec-patch.py --reverse`; resumen final sin pasos retirados. Invariante declarado: `spec-source/` es siempre la fuente del candidato más nuevo de `output/`.
- `prompts/build-incremental.prompt` alineado: precondición de identidad, *restore* (reverse de los parches de mayor a menor, borrar lo creado, regenerar tablas, `assemble --check` de la base) en REJECT/MAJOR/UNCERTAIN; `MAJOR RECOMMENDED` sólo en `scope` (= correr el mismo delta sin tope); la degradación pasa a `DEGRADED` (un mayor ya no regenera nada que recupere lo perdido).
- `prompts/3-post-spec/audit-dash-conformance.prompt`: alcance = secciones y archivos de `v<N>-context-delta.md`, por sección; falla en un refine; arrastra las sospechas de la base fuera del alcance.
- `bin/apply-spec-patch.py --reverse RECORD` (aditivo): el registro guarda el orden de secciones, el texto previo de cada sección cambiada y el contenido previo y sha256 posterior de cada archivo. Rechaza si la fuente se movió después del parche o si lo reconstruido no tiene el sha256 previo.
- `bin/assemble-spec.py`: `{{version}}` en la prosa, de `--version`, del nombre del archivo, o (sólo `--check`) leído del documento — así `--check dist/sgai-spec.md` sigue valiendo después de una promoción.
- `bin/check-incremental.py`: `scope` acepta filas por clave, exige declarar toda sección de los registros `v<N>-delta-patch-<k>.json`, no cuenta `cleanup`/`version` para el tope, y ya no marca cambiada la sección anterior a la última cuando la última se borra; `anchor` lee el `Context head` del propio mayor (`v<N>-context-delta.md`).
- `bin/strip-legacy-annotations.py` (nuevo): escribe el parche único que saca los `<!-- refine/delta -->` (prosa y `syntax.yaml`), la sección *Refinement gaps* y la iteración tipeada del status (→ `{{version}}`). Usa `gen-syntax-tables` como oráculo para los overrides que quedaban iguales al texto derivado. Idempotente: sobre una fuente limpia sale 0 y no escribe.

## Por qué el rollback es `--reverse` y no git

El pipeline no commitea (los commits son del operador), así que no hay commit de la fuente anterior al que volver, y un `stash` barre lo demás del árbol. El registro ya tiene el estado previo y los dos sha256: el deshacer se verifica en los dos extremos, y una tercera vez, independiente, con `assemble-spec --check` contra el candidato anterior.

## Evidencia

- `dry-run.sh` (salida en `dry-run.out.txt`): incremental v12.6 → v12.7 con la limpieza, parches escritos a mano en `patches/`; minor v12.7 → v12.8 y su rollback; corre en una copia scratch.
- `mutation-campaign.py`: 33 mutaciones, una por regla, cada una contra sólo sus tests: 33 en rojo.
- `carry-trace.py`, `sections-changed.py`: sólo para la corrida en seco (hacen de validación y de agente).
