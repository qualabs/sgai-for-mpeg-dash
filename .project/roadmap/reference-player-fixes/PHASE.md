---
title: Fixes de lo aprendido en la referencia
description: "Antes del v13: las 11 decisiones de norma que dejó la fase 11 escritas en context/ con su test, y la batería de conducta sin ruido (legacy como Player de la 6ta, vectores corregidos, formato por clase, sin inestables), para que sirva de juicio."
started: 2026-11-26
origin: "el líder del proyecto, 2026-11-26, vía el coordinador: fase de fixes con lo aprendido en la 11, antes del v13; la parte de norma la decide él"
category: fix
impact: medium
depends_on: [reference-player]
---

# Fixes de lo aprendido en la referencia

El diseño, con la evidencia de cada punto, está en [`DESIGN.md`](DESIGN.md):
las decisiones de norma N-1 a N-11, lo ya decidido Y-1 a Y-5 y las de
ejecución D-1 a D-6.

## Alcance

- **Norma** (`context/03`, `context/04`): lo que el líder elija en N-1 a N-11,
  un commit por decisión, cada uno con el test o vector que lo cubre. Los
  `[DISCUSSION]` para el WG, como borradores.
- **La referencia** (`reference-player/src/`): sigue cada lectura decidida.
- **El instrumento**: la clase legacy como Player de la 6ta (D-1), el formato
  con capacidades por clase (D-2) y el elemento `alternative` si N-10 sale A,
  los vectores mal escritos (D-3), los 3 jobs inestables (D-4).
- **Al cierre**: la batería entera una vez (D-6), con el antes y el después.

## Fuera de alcance

- `spec-source/sgai-spec.src.md`, `output/` y `dist/`: el v13
  (`major-build-v13`) absorbe `context/`.
- Y-1 a Y-5: ya decididos en `context/`; sus tests van después del v13.
- Publicar issues, pushear.
- Lo que el formato no expresa (color de región, audio).

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Un cambio de `context/` deja viejas las citas del nivel 2 y los hashes de los tests | D-5: en el mismo pase; `check-behaviour`, `check-scenarios` y `--source spec-source` en 0 antes de cada commit (T-01) |
| Un vector se "corrige" para que pase la referencia | D-3: cada valor contra la línea de `context/04` o del anexo; el vector viejo se ve fallar y el nuevo pasar (T-06) |
| El modo legacy arrastra conducta `svta` del lineal | T-05: un vector legacy con overlay ve fallar una mutación que carga la familia no lineal |
| La máquina cargada inventa FAIL al cierre | D-6: batería sin carga ajena, `uptime` registrado; lo inestable se re-corre solo dos veces |
| La batería tarda 4–5 h | una sola vez, al cierre; durante la fase sólo los jobs tocados |
| El límite de 5 h de la cuenta corta un subagente | una familia por subagente; se retoma desde el árbol |

## Stakeholders

El líder del proyecto decide N-1 a N-11 y publica los `[DISCUSSION]`.
