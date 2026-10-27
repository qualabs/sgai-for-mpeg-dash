---
title: El documento primero
description: "Reescribió context/03-requirements.md con el documento primero: regla de escritura, índice de las tres interfaces (75 elementos), 83 criterios reescritos, fusionados o retirados (165 quedan, 36 ids retirados con su tabla), D-13..D-16 y R1.4; check-context-interfaces como Step 0.7; la validación independiente no encontró otra pérdida que R6.4, que se restauró."
started: 2026-10-27
origin: "Nicolás, 2026-09-28, abierta como fase 06 en diseño (de output-analysis/v12.6-requirements-redundancy-review.md); phase 06, returned to the roadmap 2026-10-15"
priority: medium
category: chore
---

# El documento primero

El diseño, con el mapa de obligaciones (Anexo A) y las alternativas
descartadas, está en [`DESIGN.md`](DESIGN.md); las decisiones, en las ADR
0029 a 0043.

## Alcance

- `context/03-requirements.md` reescrito según el mapa: 83 criterios cambian
  (46 se reescriben, 31 se fusionan, 6 se retiran), 2 nuevos (R12.5, R40.9),
  164 después. Lleva al principio la regla de escritura ("How requirements are
  written") y la sección "Interfaces" (un índice por interfaz, elemento →
  criterio que lo define), y al final la tabla "Retired identifiers".
- Las decisiones de contenido D-13 a D-16: los nombres `sgai-allowed-layouts`,
  `sgai-custom-region` y `sgai-ad-audio-allowed` en R29.1; el carrier de los
  beacons con tiempo como MUST; los dos tokens de double-box dicen si hay
  fondo; la URL de destino del ClickThrough con el modelo de R48.3.
- `context/04-use-cases.md` y `context/99-glossary.md`: sólo las citas a ids
  que se van (24 y 2).
- `bin/check-context-interfaces.py`, como Step 0.7 de `build-all`, con sus
  pruebas; lo que haga falta en `bin/check-context-coherence.py` para que los
  ids de la tabla de retirados no cuenten como referencias rotas.
- El `CLAUDE.md` del proyecto: la línea que apunta a la regla y el check en la
  descripción de `bin/`.
- La validación de la versión vieja contra la nueva, por un agente que no
  reescribió, con los tres chequeos de `context/` en `0`.

## Fuera de alcance

El build v13 y la promoción (son de `roadmap/major-build-v13`). Renumerar
archivos de `context/` o mover requerimientos entre secciones de 03. Cambiar
02, 05, 06, 07 u 08. Editar ADRs aceptadas (D-11). Renombrar parámetros o
atributos que ya tienen nombre. Decisiones de fondo fuera de D-13 a D-16: una
ambigüedad nueva se anota como pregunta. Sin push.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Una obligación se pierde al fusionar o retirar un criterio | T-05 recorre cada modal de cada unidad vieja contra su lugar nuevo del mapa, con la misma fuerza, y prueba el instrumento borrando una obligación a propósito. |
| 03 cambia entre el diseño y el arranque (por ejemplo, multiview escribe en 03) | T-01 confirma `git diff 44cfff4..HEAD -- context/03-requirements.md` vacío; si no lo está, rehace el mapa sobre el commit nuevo antes de T-02. |
| `check-context-coherence` toma los ids de la tabla de retirados como referencias a nada y sale en rojo | T-03 le enseña la tabla: un id retirado está definido como retirado, y citarlo fuera de la tabla lo detecta el check nuevo. |
| `check-context-vocabulary` pide entradas de glosario para términos que trae la reescritura, y 99 deja de cambiar sólo ids | T-05 acepta en 99, además de los ids, sólo las entradas que el chequeo pide para términos nuevos de T-02, listadas una por una. |
| El que reescribe resuelve una ambigüedad de fondo | T-02 la anota en `tasks/T-02/questions.md` y no la resuelve; T-05 lo controla al comparar obligaciones. |
| El diff contra la versión vieja se vuelve ilegible | 03 conserva sus requerimientos, su orden y sus ids (D-5, D-10). |
| La comparación del v13 no separa la reestructura del resto del delta | Residual, aceptado (D-1): la protección es T-05, a nivel de `context/`. |

## Orden respecto de otros ítems

Va antes de que multiview escriba su requerimiento en 03, y antes de
`major-build-v13`, que ya depende de este ítem.

## Stakeholders

Nicolás aprueba el plan y lee la validación. El working group lee `context/`
reescrito; la tabla "Retired identifiers" es lo que mantiene válidas sus
citas a ids viejos.
