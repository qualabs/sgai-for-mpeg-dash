---
description: "Implementación de referencia de la extensión SGAI sobre dash.js, con tests de conducta derivados de los criterios del Player de context/03: el nivel 3 del testing de la spec."
status: idea
category: feature
depends_on: [conformance-tests, code-first-pipeline]
origin: "el líder del proyecto, 2026-11-23, hilo #sgai: el testing en tres niveles («Me gusta los 3!!!») y «Dash.js tiene que ser la referencia»"
---

Lo que ya se sabe, del diseño de `conformance-tests` (D-8): la referencia es
otra compilación del mismo dash.js fijado que hace de Player legacy, más lo
nuestro; los tests de conducta salen de los ~60 criterios del Player de
`context/03`, cada uno con lo que se carga, lo que se observa y lo esperado;
se enchufan como un adaptador más al harness de Players de esa fase. dash.js
no implementa ni el lineal de la 6ta, así que la referencia también lo trae.
Va antes del v13 (orden `conformance-tests` → `code-first-pipeline` →
`reference-player` → `major-build-v13`; los tests de conducta son los
vectores de las UC que deja `code-first-pipeline`, D-5): se construye contra el `context/03` de hoy, y cada test
de conducta guarda el hash del texto de su criterio, así lo que el v13 mueva
(los carriers de beacons y audio, entre otros) aparece como la lista de tests
y partes de la referencia a revisar.

## Requisito agregado (2026-11-23, pedido de Nicolás)

La batería de vectores corre en tiempo real y puede tardar horas. El diseño de esta fase mide cuánto tarda la batería entera (22 UC × clases de dispositivo) y fija un tope, evaluando: arrancar en `play_from`, paralelismo, fixtures sintéticos cortos y tiempo virtual o velocidad de reproducción mayor (verificar que funcione con un player real). Los vectores no tienen que correr en cada build: pueden correr antes de promover.
