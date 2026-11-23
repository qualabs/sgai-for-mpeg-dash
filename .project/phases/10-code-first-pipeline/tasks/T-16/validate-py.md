# La validación entera como código: `bin/validate.py` (2026-11-23)

El paso 7 (`prompts/3-post-spec/validate-spec.prompt`) deja de ser un agente.
Es un comando: `python3 bin/validate.py v<N> --prev v<P> --mode <mode>`. El
modelo queda solamente en llamadas de un turno sin tools: los caminantes
(`bin/walk-batches.py`, sin cambios de comportamiento) y la búsqueda abierta.
El prompt conserva §A como la definición que el script implementa. El texto
que reciben las llamadas (§A.1–§A.5, las "Walker rules" y las "Open-search
rules") lo lee el script del prompt, y sale con 2 si faltan los anclajes.

## Qué pasó a código (0 tokens)

Población y fuentes; qué se camina según el modo; lotes; `defs.txt`; el
ruteo que decide una regla (`contradicted` y `force-lost` van a 5.a; una
fila o un hallazgo arrastrado conserva su fila de v<P>; tope de 5 con
overflow); la traza y `check-trace`; el sidecar; el resumen. Medido con
`--plan-only` sobre los datos reales v12.7→v12.8: **1,0 s de CPU y ninguna
llamada al modelo**.

## Cambios respecto del §B anterior (decididos en ejecución)

- **Una unidad cuyo texto de `context/` cambió se camina.** La traza guarda
  `unit_sha256` por unidad. Una entrada sin hash se camina, porque nada
  muestra que su texto sea el mismo. El §B anterior la habría arrastrado: la
  traza de v12.7 se había juzgado con la población de v12.6 (39 unidades
  nuevas). Es lo que hizo que el orquestador caminara 172 unidades.
- **El detail review es opcional.** En `build-all` el Paso 7.5 corre después
  del 7. Si el archivo existe, sus flags se rutean; si no, el sidecar lo
  dice.
- **La cadena de resolución de §A.5 corre sobre lo que la llamada recibe**
  (unidades de `context/` y secciones). No lee ADRs ni la norma base, así que
  el sidecar sale `[GROUNDED_BY=spec-only]`.

## Estimación v12.7→v12.8 (el caso medido: 172 unidades, 30 lotes, 8 secciones cambiadas)

| Parte | Antes (medido) | Ahora |
|---|---|---|
| Orquestador | 8,1M (60 llamadas × ~135k) | **0** |
| Caminantes | ~1,4M (`walk-batches`, 30 lotes) | ~1,4M (el mismo script) |
| Búsqueda abierta | 8,2M (subagentes de hasta 380k) | **~15–31k**: 1 llamada de 38.828 caracteres (`--plan-only`, ≈15,5k tokens), o 2 si hay reintento. Medido en el smoke real: 24.722 tokens en 2 llamadas |
| **Total** | **~16M** | **~1,43M (−91%)** |

- Con la regla del hash, los datos de hoy caminan **192 unidades en 27
  lotes** (la traza de v12.7 no tiene hashes): ≈1,4M × 192/172 ≈ 1,56M. En
  régimen, con hashes en la traza, el mismo refine camina **56 unidades en 8
  lotes** (39 nuevas + 14 stale + 3 no-`met`; recuento independiente más
  abajo), ≈0,45M.
- Mayor/incremental (`--plan-only`): **5 llamadas de 95–126k caracteres**
  (≈38–51k tokens cada una a 2,5 caracteres por token), ≈236k en total,
  contra 8,2M.
- Caracteres por token, **medido** en el smoke: 24.722 tokens por 2 × ~31k
  caracteres ≈ 2,5. La primera versión suponía 4, y con eso el presupuesto
  de un fragmento (120k + 40k caracteres) daba ~64k tokens. Se bajó a
  90k + 25k caracteres (≈53k con las reglas).

## Verificación

- `bin/test_validate.py`: 33 tests sobre un proyecto fixture y un modelo
  stub. Cubren: refine camina solo lo stale/nuevo/no-met/con fuente o texto
  cambiado y arrastra el resto; un caminante `not-verifiable` se renderiza y
  `check-promotable` sale 2; una cita no literal de la búsqueda abierta se
  reintenta y después se descarta; `check-promotable` y `compare-candidates`
  leen el sidecar; también todo-o-nada, el tope de 5.a, los flags, el
  solapamiento, el dedupe, skip-if y los 64.
- Campaña de mutación: 44 reglas, 44 detectadas (salida en el informe del
  worker).
- Fuente independiente: el recuento de la regla B.2 sobre los datos reales,
  hecho con un script aparte (`Counter`): 39 nuevas + 14 stale + 2
  no-`met` + 1 stale y no-`met` = **56**, igual al plan. La parte sin hash da
  192 = 212 − 20 `code` sin residual.
- Datos reales con caminantes stub: el sidecar de v12.8 lo leen
  `check-promotable` (exit 1, `UNCERTAIN=0`) y `validation-summary` (exit 0).
- Un smoke real: búsqueda abierta de verdad con caminantes stub, 2 llamadas
  (hubo un reintento), exit 0. Devolvió un hallazgo nuevo (G-3, sobre PLY-31
  y R4.11) con citas literales verificadas, y descartó A-6 y A-9 (los dos
  re-juzgados). Los errores de la primera ronda no quedaron guardados: el
  registro de respuestas se agregó después de esa corrida.
