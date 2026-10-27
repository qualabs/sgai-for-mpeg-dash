---
description: context/ cierra tres huecos de error-semantics (E1, E5, E11) con decisiones de Nicolás
touches: 07-svta2053-v3-alignment
category: fix
impact: low
---

## Qué se vio

El build de la fase 07 anotó tres `UNDEFINED` en `context-analysis/error-semantics.md`
(REPORT de la fase, §4):

- **E1**: `context/` no fija reintentos, backoff ni plazo del pedido de resolución.
- **E5**: no dice qué hace el Player con una resolución que llega cuando la ventana ya terminó.
- **E11**: no dice si un candidato que empezó a renderizar y se abortó cuenta como "renderizado".

## Decisiones (Nicolás, 2026-10-27)

- E1: "esto no queda definido, es un tema de implementación; acá principalmente solo
  definimos la interfaz".
- E5: "nada... no se muestra".
- E11: "el tracking envía hasta donde el usuario vio, fin; cómo se cuentan las
  visualizaciones es tema de quien interpreta los datos; el spec solo va hasta cómo se
  envían las métricas".

## Cambio en `context/03-requirements.md`

- **OOS-13** (nuevo): la política de reintentos del pedido de resolución es de
  implementación; lo que sigue a un intento fallido es de R20.1. OOS-11 no se reusa.
- **R34.10** (nuevo): una resolución que llega después de terminada la ventana no se
  presenta; el Player la descarta.
- **R13.8** (nuevo): la spec define qué beacons se disparan y cuándo, y no cómo se
  interpretan; si un aviso abortado cuenta como visto es de quien lee los beacons.

`context-analysis/` y `output/` no se tocan: los regenera el próximo build (v13).

## Verificación

- `bin/check-context-coherence.py`: exit 0 antes y después (291 → 294 identificadores).
- `bin/check-context-vocabulary.py`: exit 0 antes y después, `HALLAZGOS=0` en los dos.
