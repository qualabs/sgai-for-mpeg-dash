---
closed: 2026-11-23
---

# REPORT — fase 10, pipeline código primero

## 1. Resumen

La spec tiene ahora una fuente, `spec-source/`, y los artefactos de esa
fuente los juzga código. Los artefactos son el XSD y `syntax.yaml` (de donde
salen las 17 tablas de §5), los 93 ejemplos como fixtures con clase declarada
y las 22 UC como vectores. La prosa se edita sólo por parches que un script
aplica y verifica, y el documento lo arma `bin/assemble-spec.py`. Armar la
fuente extraída de v12.6 reproduce `dist/sgai-spec.md` byte a byte.

Lo que antes juzgaba un LLM sin necesidad pasó a código:

- la comparación con lo publicado (`compare-candidates.py`);
- el lint editorial;
- la traza de la validación y sus citas (`check-trace.py`);
- la promoción (`promote.py`);
- los pasos del pre-spec que nadie leía (retirados).

La validación entera es `bin/validate.py`, y el modelo sólo contesta
llamadas de un turno que el código valida.

**El costo, medido contra medido** (`tasks/T-16/ab.md`):

| Corrida | Viejo | Nuevo | Δ |
|---|---|---|---|
| Vuelta de refine | > 51,1M (cota inferior: no terminó) | 9,99M completa | ≤ −80% |
| Incremental, mismo delta del 2026-10-27, hasta el chequeo de alcance | 41,8M | 12,2M | −71% |

La meta era −70% en las dos. El hallazgo que más pesó se midió en esta fase.
Cada llamada de un agente o subagente dentro del repo paga ~64k tokens fijos
antes de leer nada (system prompt, tools y los dos `CLAUDE.md`). Una llamada
de un turno desde un directorio vacío paga 568
(`tasks/T-16/fixed-cost-per-call.md`). Vale para todo `cto-assistant`.

Suite: 23 archivos `bin/test_*.py`, todos verdes (420 tests en T-14, más los
de `validate.py`, `walk-batches.py` y el ruteo de flags). Cada script nuevo
tiene su campaña de mutación, una rotura por regla. `context/` y `dist/` no se
tocaron.

## 2. Decisiones

ADR 0060 a 0074, una por decisión del diseño (D-1 a D-15), todas
`scope: phase-10`:

- 0060: la fuente y el armado;
- 0061: una sola fuente de prosa, leída por sección;
- 0062: el XSD como fuente de las tablas;
- 0063: los fixtures con clase;
- 0064: las UC como vectores;
- 0065: el lint;
- 0066: el parche;
- 0067: el mayor edita la fuente;
- 0068: la validación por traza;
- 0069: la revisión queda en los nombres;
- 0070: la comparación es código;
- 0071: el audit sale de la vuelta;
- 0072: el pre-spec sin lo huérfano;
- 0073: la promoción es un script;
- 0074: el costo se mide.

Del líder del proyecto: el diseño y la vuelta de base pagada («Ok a todo»).
Del coordinador, con lo medido:

- no relanzar la vuelta vieja cuando pasó lo aprobado;
- los topes de 20M y 16M para la A/B;
- pasar los caminantes, y después la validación entera, a llamadas de un
  turno validadas por código.

## 3. Tasks

Las 17 `done`. Las hice yo, el coordinador de la fase:

- T-01, T-02, T-07, T-10, T-11, T-13 y T-14;
- la integración y verificación de cada una de las demás.

Se delegaron a subagentes, y verifiqué cada una al integrarla:

- T-03, T-04 (en dos tandas, por el límite de la cuenta), T-05 (formato más
  cuatro lotes de vectores), T-06, T-08, T-09 (dos tandas), T-12 y T-15;
- `bin/validate.py` (dentro de T-16).

Las verificaciones fueron suites corridas, `assemble --check`, las salidas de
los checks y las mutaciones. Las corridas pagas fueron sólo las de T-01 y
T-16.

## 4. Hilos abiertos

- **Para el v13:**
  - los 6 FAIL de carriers;
  - los 7 elementos sin carrier;
  - 8 desacuerdos tabla/XSD (`tasks/T-03/findings.md`);
  - 11 desacuerdos `context/04` contra los anexos y los límites del formato
    de vector (`tasks/T-05/README.md`);
  - `@executeOnce` sólo en la ventana de pausa (`context/06` lo pide en las
    tres);
  - la línea de status que no avanzaba (ahora `{{version}}`);
  - §5.16.4 sin prefijo `DASH`.
- **La regla "`Event@id` único en `svta:Tracking`" no existe.** La pedían la
  ADR 0063 y el REPORT de la fase 09, y R6.5 dice lo contrario. Hay que
  decidir cuál vale.
- **El apply incremental abandona al primer cambio `needs-structure`.**
  Marcó 68 y, según su informe, ~16 lo son. El v13 es mayor y lo aplica sin
  tope.
- **La primera vuelta sobre la fuente nueva camina toda la población.** La
  traza heredada de v12.6 no tiene `unit_sha256`. A partir de la primera
  validación de `validate.py`, un refine camina sólo lo que cambió
  (~56 unidades en el caso medido).
- **Siguen siendo agentes** el orquestador de `build-all`, el apply, el
  refine y la revisión de nombres. Son el grueso de lo que queda: 3,6M, 2,6M
  y 1,4M en la vuelta medida. Queda sembrado como `roadmap/single-turn-agents`.
- **`dist/`** sigue en v12.6 con sus 74 hallazgos de lint y el juego
  incompleto. Se corrige al promover el v13 con `promote.py`.
- **El issue a DASH-IF** sigue en borrador, de la fase 09.

## 5. Riesgos que se materializaron

- **La medición casi no se pudo hacer.** El límite de 5 h de la cuenta cortó
  la vuelta de base dos veces y una de las A/B. La vuelta vieja quedó como
  cota inferior (> 51,1M), sin terminar. Se gastaron 53,2M en la base, 49,8M
  de ellos perdidos.
- **El supuesto del diseño sobre el costo era falso.** Suponía que el
  contexto de un caminante era su lote: era 64k de fijo más el lote. La
  primera A/B se cortó en 24,7M. Se resolvió dentro de la fase (caminantes y
  validación por script) y se re-midió.
- **Población cambiada.** La renumeración de `context/03` (fase 08) dejó la
  traza y los sidecars de v12.6 sobre otra población. Eso hizo caminar 172 y
  192 unidades, y dejó a `compare-candidates` sin poder comparar contra
  `dist/`. Se arregló la comparación para que tolere la renumeración sin
  aceptar clases de unidad distintas.

## 6. Recomendaciones para la fase siguiente

- **`reference-player`** ejecuta los 22 vectores con el harness de la
  fase 09. Antes conviene extender el formato con lo que hoy no expresa:
  - capacidades por clase y por variante;
  - resoluciones que fallan;
  - el clic;
  - `Event@id` repetidos entre EventStreams.
- **El v13** corre ya sobre este pipeline:
  - el mayor sin tope;
  - la limpieza única de las marcas;
  - `measure-run` al terminar, que será la primera medición de un build
    completo;
  - promoción con `promote.py`.
- Pasar los agentes que quedan a llamadas de un turno, donde la tarea lo
  permita (el refine y la revisión de nombres, sí; el apply de un mayor,
  probablemente no).

## 7. Correcciones post-ejecución

`grep -n "post-ejecuci" TASKS.md`: seis líneas.

- **T-01:** la vuelta vieja se cortó por el límite y no se relanzó. El
  medidor pasó a cargar los subagentes anidados al paso de su padre.
- **T-04:** no se escribió la regla de `Event@id`, porque contradice R6.5.
- **T-06:** la definición de hecho contaba mal lo medido en el diseño (faltaban
  34 comentarios `delta` y una referencia rota).
- **T-08:** 33 citas no literales y no 28 (la medición del diseño normalizaba
  `/` como `|`). La población de v12.6 no es la de hoy.
- **T-12:** `promote.py` y `validate-spec` corrían la conformidad sobre el
  documento y no sobre la fuente.
- **T-16:** la validación pasó a código después de la primera medición.

Como medición: tres de las seis (T-04, T-06, T-08) son números o reglas que
el diseño tomó de una medición propia sin probar su instrumento contra el
caso real. La lección es la misma que en la fase 09: el instrumento se prueba
antes de citar su número. T-12 y T-16 son del diseño. La conformidad sobre el
documento y el costo fijo de un subagente no se habían medido antes de
decidir.

## 8. Revisión de documentación

- **`description` de `PHASE.md`:** reescrita como lo que la fase resultó ser.
- **`docs/arc42/`:** el proyecto no lo tiene; el pipeline está descrito en
  `CLAUDE.md`.
- **Resto de `docs/`:** no existe.
- **`README.md`:** `spec-source/`, `bin/`, el armado, `--source`, la
  promoción por `promote.py` y la medición de una corrida (T-15).
- **`CLAUDE.md` del proyecto:**
  - layout y flecha con `spec-source/`;
  - cada script nuevo con lo que cubre su verde (incluidos `validate.py` y
    `walk-batches.py`);
  - escalas de iteración;
  - promoción;
  - medición.
- **`SETUP.md` (runbook):** "Dependencies" (lxml, PyYAML, jsonschema, `uv`)
  y el comando de la suite entera.
- **`prompts/README.md`:** árbol sin los prompts retirados, diagrama, tabla y
  Step 9.
- **`.project/knowledge/`:** no existe. Lo transversal quedó en ADRs y, el
  costo fijo por llamada, en `tasks/T-16/`.
- **`CLAUDE.md` y `knowledge/` de la raíz de `cto-assistant`:** no los
  toqué. El costo fijo por llamada vale para todo el repo y se le pasa al
  coordinador como hallazgo: decidir si va a la raíz es suyo, y es una regla
  (A5).
- **Registro:** las carpetas `tasks/T-NN/` son evidencia de lo medido el
  2026-11-23, no instrucciones vigentes; lo vigente está en `bin/`, `prompts/`,
  `CLAUDE.md` y `SETUP.md`.
