---
description: "El build mayor v13: reconstruir la spec desde context/ con todo lo acumulado desde v12.6 (fase 07, document-first y multiview), y decidir los carriers que el incremental no pudo ubicar."
status: idea
category: chore
depends_on: [document-first, multiview]
origin: "Nicolás, 2026-10-27, al cerrar la fase 07 sin rebuild"
---

El incremental sobre v12.6 (anchor `924afcb`) terminó en `RESULT: MAJOR
RECOMMENDED`: 82 secciones cambiadas, 36.9% de la base (tope 30%), y 19
cambios de clase `needs-structure`. La lista de lo que necesita el mayor es la
tabla `## Not placed` de `output-analysis/v12.7-context-delta.md`: sobre todo
los carriers de R41 (audio), R42 (beacons de ocurrencia, del que cuelgan R1.6,
R5.9 y R47), R44, R48, R23.2 y los beacons de slot de R13.7.

Nicolás: se hace al final, juntando la fase 07 con document-first y multiview, en vez de un mayor por cada
una. El perfil multi-asset no entra: quedó en el backlog (2026-10-27).

Se invoca como dice el `CLAUDE.md` del proyecto (`build-all.prompt`, con
`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`, en background).
