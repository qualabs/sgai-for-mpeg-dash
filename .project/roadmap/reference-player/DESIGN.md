---
description: "Implementación de referencia de la extensión SGAI sobre dash.js, con tests de conducta derivados de los criterios del Player de context/03: el nivel 3 del testing de la spec."
status: idea
category: feature
depends_on: [conformance-tests, major-build-v13]
origin: "el líder del proyecto, 2026-11-23, hilo #sgai: el testing en tres niveles («Me gusta los 3!!!») y «Dash.js tiene que ser la referencia»"
---

Lo que ya se sabe, del diseño de `conformance-tests` (D-8): la referencia es
otra compilación del mismo dash.js fijado que hace de Player legacy, más lo
nuestro; los tests de conducta salen de los ~60 criterios del Player de
`context/03`, cada uno con lo que se carga, lo que se observa y lo esperado;
se enchufan como un adaptador más al harness de Players de esa fase. dash.js
no implementa ni el lineal de la 6ta, así que la referencia también lo trae.
Va después del v13 porque el v13 mueve los carriers de beacons y audio.
