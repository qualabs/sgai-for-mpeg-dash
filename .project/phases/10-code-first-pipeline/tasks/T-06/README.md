# T-06 — el lint dice por código si el documento armado está limpio (2026-11-23)

Registro de lo que se midió ese día; lo vigente está en `bin/lint-spec.py --help`.

- `bin/lint-spec.py dist/sgai-spec.md` → exit 1, 74 hallazgos: `L-COMMENT 72, L-GAPS 1, L-REF 1`; 305 encabezados numerados, 173 ids, 84 bloques xml. L-ID, L-NS y L-DRAFT: 0.
- **L-COMMENT 72**, no 38: 38 `<!-- refine: … -->` y 34 `<!-- delta: … -->` (las marcas del camino incremental), todas fuera de código. Contado aparte con `grep -o`: 38 refine, 34 delta, 91 `<!--` en total; los 19 restantes son comentarios XML dentro de bloques ```xml, que la regla no cuenta (son contenido del ejemplo).
- **L-GAPS**: línea 7462, `## Refinement gaps`.
- **L-REF**: línea 2156, `schemes are (DASH §5.16.3, §5.16.4)`. El segundo `§` va sin prefijo; por la convención que el propio documento declara (línea 18: *a bare `§n` … refers to this document*) es una referencia a este documento, y acá no hay §5.16.4. Lo que el autor quiso es `DASH §5.16.4`. No se suprime: es un hallazgo del documento. El mismo patrón en la línea 2181 (`(DASH\n§5.10.2.1, §3.1)`) no sale porque §3.1 existe acá; si el autor quiso `DASH §3.1`, el lint no lo puede ver.
- Prefijo en la línea anterior: con esa parte apagada, el lint marca 364, 1722, 2181 y 3717 (además de 2156), las cuatro que el pedido midió como falsos positivos del chequeo ingenuo.
- Cruce independiente de L-ID: `grep` de las definiciones `- **XXX-n**` da 173, 173 únicas; ids mencionados y no definidos (`comm`): 0.
- Profundidad: una referencia más honda que cualquier encabezado no resuelve (resolución exacta); aceptar el padre dejaría pasar un error de tipeo a cualquier profundidad.
- `bin/test_lint_spec.py`: 32 tests OK; campaña de mutación 26/26 atrapadas (en el informe de la task).
- `bin/assemble-spec.py --check dist/sgai-spec.md` → exit 0, sha256 197cbd88…a22.
