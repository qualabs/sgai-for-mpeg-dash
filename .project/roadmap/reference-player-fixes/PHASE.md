---
title: Fixes de lo aprendido en la referencia
description: "Antes del v13: las 12 decisiones de norma que dejó la fase 11 escritas en context/ con su test, y la batería de conducta sin ruido (legacy como Player de la 6ta, la guía IAB v2.0 final, vectores corregidos, formato por clase, sin inestables), para que sirva de juicio."
started: 2026-11-26
origin: "el líder del proyecto, 2026-11-26, vía el coordinador: fase de fixes con lo aprendido en la 11, antes del v13; la parte de norma la decide él"
category: fix
impact: medium
depends_on: [reference-player]
---

# Fixes de lo aprendido en la referencia

El diseño, con la evidencia de cada punto, está en [`DESIGN.md`](DESIGN.md):
las decisiones de norma N-1 a N-12, lo ya decidido Y-1 a Y-5 y las de
ejecución D-1 a D-7.

## Alcance

- **Norma** (`context/03`, `context/04`, `context/06`): lo que el líder
  decidió en N-1 a N-12, con el texto exacto de `DESIGN.md`, un commit por
  decisión, cada uno con el test o vector que lo cubre. La fase no abre nada
  con el WG.
- **La referencia** (`reference-player/src/`): sigue cada lectura decidida.
- **El instrumento**: la clase legacy como Player de la 6ta (D-1), el formato
  con capacidades por clase (D-2) y el elemento `alternative` (N-10),
  los vectores mal escritos (D-3), los 3 jobs inestables (D-4).
- **La guía IAB v2.0 final** (D-6): el paso 5, las citas de `context/`, el
  mirror y una nota en las ADR 0001, 0002 y 0004.
- **Al cierre**: la batería entera una vez (D-7), con el antes y el después.

## Fuera de alcance

- `spec-source/sgai-spec.src.md`, `output/` y `dist/`: el v13
  (`major-build-v13`) absorbe `context/`.
- Y-1 a Y-5: ya decididos en `context/`; sus tests van después del v13.
- Abrir issues con el WG, pushear.
- Lo que el formato no expresa (color de región, audio).

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Un cambio de `context/` deja viejas las citas del nivel 2 y los hashes de los tests | D-5: en el mismo pase; `check-behaviour`, `check-scenarios` y `--source spec-source` en 0 antes de cada commit (T-01) |
| Un vector se "corrige" para que pase la referencia | D-3: cada valor contra la línea de `context/04` o del anexo; el vector viejo se ve fallar y el nuevo pasar (T-05) |
| El modo legacy arrastra conducta `svta` del lineal | T-04: un vector legacy con overlay ve fallar una mutación que carga la familia no lineal |
| La máquina cargada inventa FAIL al cierre | D-7: batería sin carga ajena, `uptime` registrado; lo inestable se re-corre solo dos veces |
| La batería tarda 4–5 h | una sola vez, al cierre; durante la fase sólo los jobs tocados |
| El límite de 5 h de la cuenta corta un subagente | una familia por subagente; se retoma desde el árbol |

## Stakeholders

El líder del proyecto decidió N-1 a N-12 (2026-11-26/27) y aprueba el plan; da
la ventana sin carga de T-08.
