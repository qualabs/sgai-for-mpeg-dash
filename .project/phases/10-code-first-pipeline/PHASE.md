---
title: Pipeline código primero
description: "La spec sale de spec-source/ (XSD + syntax.yaml, 93 ejemplos con clase, 22 UC como vectores) armada por script y byte a byte igual a dist; la prosa se edita por parches; comparación, lint, traza, validación y promoción son código, con el modelo sólo en llamadas de un turno validadas. Medido: vuelta de refine 9,99M contra >51,1M, incremental 12,2M contra 41,8M; el fijo de ~64k por llamada de agente es lo que queda."
started: 2026-11-23
origin: "el líder del proyecto, 2026-11-23, hilo #sgai, al cerrar conformance-tests: «los tests dan confianza PQ es deterministico, un LLM JUZGANDO NO», «tal vez deberíamos hacer más 'código' … y por último se escribe la norma en sí misma», «no quiero dejar cosas 'para después' … antes de la v13», y que el camino baje drásticamente los tokens; diseño acordado el mismo día («Ok a todo»), con la línea de base pagada (P-1)"
category: feature
depends_on: [conformance-tests]
---

# Pipeline código primero

El diseño, con lo medido y las alternativas descartadas, está en
[`DESIGN.md`](DESIGN.md); las decisiones, en las ADR 0060 a 0074 (D-1 a
D-15).

## Alcance

- **La fuente.** `spec-source/` entre `context-analysis/` y `output/`: la
  prosa (`sgai-spec.src.md`) con directivas, el XSD y `syntax.yaml`, los
  ejemplos como fixtures con clase declarada, los vectores de las UC.
  `bin/assemble-spec.py` arma `output/v<N>-sgai-spec.md`; la fuente extraída
  de v12.6 reproduce `dist/sgai-spec.md` byte a byte.
- **Lo generado.** Las tablas de §5 y el bloque de §5.10.1 salen del XSD y
  `syntax.yaml`; las tablas de clases de los anexos, de los vectores.
- **Lo que juzga código.** Niveles 1 y 2 por fixture (con las reglas fáciles
  que dejó la fase 09 y las `DASH §n` contra la copia primaria), lint e
  higiene, alcance de los parches, traza y citas, comparación, promoción.
- **Lo que sigue en un LLM, acotado.** La prosa por sección y por parche; la
  validación por criterio sobre sus secciones, y la búsqueda abierta una vez
  por mayor o incremental; los nombres sobre la lista que arma el código; el
  audit fuera de la vuelta de refine.
- **El costo medido.** Un medidor por paso; la línea de base (el incremental
  del 2026-10-27 y una vuelta de refine vieja pagada); la medición A/B al
  final.

## Fuera de alcance

- `dist/` y `context/` no se tocan sin OK del líder del proyecto. `dist/`
  queda como está hasta la promoción del v13.
- Los 9 FAIL de `dist/` y los 7 elementos sin carrier: son del v13.
- Ejecutar los vectores (es `reference-player`), los Stages 5 y 6, SVTA 2053,
  `multi-asset-options-profile`.
- Push: nunca sin el líder del proyecto.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| La extracción de v12.6 no reproduce el documento byte a byte | Es la definición de hecho de T-02; nada se construye sobre una fuente que no es la spec |
| Juzgar por criterio con contexto chico pierde lo que cruza secciones | Búsqueda abierta sobre la spec entera una vez por mayor e incremental (T-08) |
| Los parches acumulan incoherencia | La misma lectura completa, más el reemplazo de sección entera que admite el parche (T-07) |
| Un vector codifica mal lo esperado y nadie lo ejecuta hasta la fase siguiente | Hash de la UC en cada vector; `NOT_VERIFIABLE — sin ejecutor` hasta `reference-player` (T-05) |
| El transcript se borra o se cuenta dos veces | El medidor cuenta por llamada (su negativo) y los números se guardan como evidencia al terminar cada corrida (T-01) |
| Faltan carriers para 7 elementos | Aceptado: salen como lista; el v13 los agrega sobre la fuente |
| La línea de base vieja escribe en `output/` y corre la numeración | Corre en un worktree; nada de su salida vuelve a la rama principal salvo los números (T-01) |

## Stakeholders

El líder del proyecto aprueba; el coordinador recibe los hitos: T-02 (armado
byte a byte), T-01 (línea de base), T-16 (A/B) y el cierre.

## Arquitectura

El proyecto no tiene `docs/arc42/`. La arquitectura del pipeline vive en el
`CLAUDE.md` del proyecto, que T-15 pone al día.
