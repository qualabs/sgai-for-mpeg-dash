---
closed: 2026-10-27
---

# REPORT — 08-document-first

## 1. Resumen

`context/03-requirements.md` quedó escrito con el documento primero. Al
principio lleva la regla de escritura y el índice de las tres interfaces
(I-MPD 27, I-REQ 16, I-RES 32). Cada elemento tiene su significado escrito
una vez, del lado de quien lo escribe, con la fuerza que tenía. De los 199
criterios, 83 cambiaron según el mapa: 46 se reescribieron, 31 se fusionaron
y 6 se retiraron. R6.4 volvió después de la validación, así que quedan 165
criterios, contando R12.5 y R40.9, que son nuevos. Hay 36 ids retirados, con
su tabla. Entraron las decisiones de contenido D-13 a D-16 y la frase de R1.4.
`bin/check-context-interfaces.py` hace cumplir la parte estructural de la
regla como Step 0.7 de `build-all`. Una validación independiente comparó la
versión vieja con la nueva.

## 2. Decisiones

ADR 0029 a 0043, del evento de generación (las de D-1 a D-16), y la ADR 0044:
la regla nombra al Player como quien escribe el pedido, y generaliza la 0034.
Todas tienen `scope: project`, como las de la fase 07. Fuera de las ADR, en
`LOG.md`:

- R1.4: un candidato abortado después de empezar cuenta como renderizado.
- Las dos citas de UC-10 pasan a R5.6.

## 3. Tareas

| id | estado | resultado |
|---|---|---|
| T-01 | done | Mapa de 231 unidades sobre `44cfff4`, armado por script que falla con un id de menos o un destino inexistente o retirado. |
| T-02 | done | 03 reescrito, 04 y 99 sólo ids, línea en `CLAUDE.md`; apartamientos en `tasks/T-02/notes.md`. |
| T-03 | done | El check y el ajuste de `check-context-coherence` para los retirados. |
| T-04 | done | 19 tests; 16 mutaciones, ninguna verde. |
| T-05 | done | Validación por un agente que no reescribió; una sola pérdida, R6.4. |

## 4. Hilos abiertos

- El build v13 (`roadmap/major-build-v13`): `context/`, `prompts/` y `bin/`
  cambiaron, así que lo publicado en `dist/` está stale contra sus entradas.
- Multiview ya puede escribir su requerimiento en 03 con la regla y bajo el
  check (`depends_on: [document-first]`).
- Quedan tres dobles parciales que no tienen modales o que el mapa dejó a
  propósito: la prosa de R40 frente a R40.9, R40.6 frente a R40.2, y R4.1
  frente a R4.2. Hay además repeticiones menores en R47.2 y en la prosa de
  R27. Ningún check los ve (ADR 0035).
- 05 se superpone con I-RES en lo lineal (D-6): sigue sin decidir si pasa a
  ser el anexo de R11.5.

## 5. Riesgos que se dieron

- **Una obligación perdida al retirar un criterio.** Pasó con R6.4: el mapa
  suponía que R1.1 y R1.5 ya la decían. Lo encontró T-05, que era su
  mitigación, y se restauró.
- **`check-context-coherence` en rojo por la tabla de retirados.** Pasó como
  estaba previsto, y lo resolvió T-03.
- **Términos nuevos que piden glosario.** No pasó: vocabulary dio 0 hallazgos.

## 6. Recomendaciones

- Un mapa que retira un criterio "porque otro ya lo dice" es la premisa que
  falló. En la próxima reestructura conviene que el armado del mapa cite, por
  cada retiro, la frase del destino que lo dice, para que T-05 no sea el
  primero en leerla.
- El v13 tiene que correr con los cuatro gates. Su comparación con lo
  publicado no va a separar esta reestructura del resto del delta (D-1).

## 7. Correcciones post-ejecución

`grep -n "post-ejecuci" TASKS.md`:

- T-02 (línea 67): R6.4 restaurada después de T-05. Es la única. Dice que la
  verificación de T-02 por sí sola no alcanzaba, que es por lo que T-05
  existía separada.

## 8. Revisión de documentación

- **`description` de `PHASE.md`:** reescrita como lo que la fase terminó siendo.
- **`docs/arc42/`:** el proyecto no tiene uno.
- **El resto de `docs/`:** no existe.
- **`README.md`:** sin cambios. Describe el layout y el build, y no nombra los
  checks de `bin/` ni el formato de 03.
- **`CLAUDE.md` del proyecto:** actualizado en la fase. Tiene la línea que
  apunta a la regla (T-02) y `check-context-interfaces.py` en el párrafo de
  `bin/` (T-03).
- **`SETUP.md`, el runbook:** decía que después de `check-normative-base` corre
  sólo `check-context-coherence`. Ahora nombra los tres checks de `context/`.
- **`prompts/README.md`:** sin cambios. No enumera los gates del Step 0; los
  pasos están en `build-all.prompt`, que se actualizó con el 0.7, y en
  `build-incremental.prompt`, que ahora dice cuatro gates.
- **`.project/knowledge/`:** no existe.
- **`CLAUDE.md` y `knowledge/` de la raíz del repo:** sin cambios. La fase no
  cambió nada que valga para todo el repo.
- **`tasks/` de la fase:** `T-02/notes.md`, `T-04/evidence.md` y
  `T-05/report.md` quedan marcados como registro. `T-01/` es el mapa y su
  script: es evidencia, y el check nombra su commit como constante.
