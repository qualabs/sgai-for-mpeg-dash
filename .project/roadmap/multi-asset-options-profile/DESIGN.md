---
description: "Varios assets por opción con geometría libre (viewport, zDepth, volumen por asset), como un perfil nuevo, uno que extiende, u opcional."
status: idea
category: feature
origin: "Nicolás, 2026-10-27, al decidir sobre output-analysis/2026-10-27-david-v3-vs-context.md (fila 22)"
---

Lo que trae SVTA2053 v3 (David Hassoun): una opción con varios assets
adicionales, cada uno con `viewport`, `zDepth` y `volume` (la L de dos barras,
tres decodificadores; borrador §4.4.7-4.4.8 y §5.3.2).

Nicolás: *"una fase únicamente con esto, de forma que sea un perfil nuevo, un
perfil que extiende, u opcional"*.

**Antecedente.** Se descartó el 2026-09-28 (punto 14 del análisis de ese día,
LOG del 2026-09-28) porque choca con R22 (una sola forma no lineal a la vez),
R27.1 (una L lleva *"exactly one ad creative"*) y R10 (no rehacer un sistema de
layouts); R41.7 (una sola fuente de audio) también. Ahora se plantea como perfil
opcional, que es lo que permitiría tenerlo sin cambiar esos requerimientos para
el perfil base.
