---
description: "Pasar a llamadas de un turno validadas por código los agentes que quedan en el pipeline (orquestador de build-all, refine, revisión de nombres; el apply donde se pueda), que pagan ~64k de contexto fijo por llamada."
status: idea
category: chore
origin: "fase 10 (code-first-pipeline), al cerrar: lo medido en tasks/T-16/ab.md y fixed-cost-per-call.md"
---

En la vuelta de refine medida (9,99M), los agentes son ~7,6M: orquestador
3,56M, refine 2,57M, nombres 1,44M; la validación por código, 2,41M.
