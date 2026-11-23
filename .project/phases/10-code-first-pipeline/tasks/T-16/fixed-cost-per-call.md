# El costo fijo de cada llamada de un agente (2026-11-23)

Medido con una llamada de un solo turno ("Say OK.", `claude -p --output-format json`), contando entrada = fresca + escritura + lectura de cache, el mismo modelo y la misma cuenta. Es el piso que paga **cada llamada** de un agente o subagente antes de leer nada, y se vuelve a pagar (como lectura de cache) en cada turno.

| | Dónde corre | Tools | Settings | Entrada de la llamada |
|---|---|---|---|---|
| A | el proyecto (carga los dos `CLAUDE.md`: el del repo raíz y el del proyecto) | default | default | **66.707** |
| B | el proyecto | ninguna (`--tools ""`) | default | 42.356 |
| C | un directorio vacío (sin `CLAUDE.md`) | default | default | 27.347 |
| D | un directorio vacío | ninguna | ninguna (`--setting-sources ""`), system prompt propio | **568** |

- Los dos `CLAUDE.md` (43 KB + 54 KB) pesan ~39k tokens por llamada (A − C).
- Las definiciones de tools, ~24k (A − B).
- Un subagente del pipeline arranca en ~64k (medido en el transcript de un caminante de la validación: 55k de escritura + 8,6k de lectura en su primera llamada), y su lote era ~6k.

**Por qué vale para todo el repo padre:** cualquier subagente o `claude -p` lanzado dentro de `cto-assistant` paga este piso en cada turno. Un trabajo que se puede hacer en una llamada sin tools (juzgar un texto dado, clasificar, extraer) cuesta ~100 veces menos como llamada de un turno desde un directorio vacío que como subagente.
