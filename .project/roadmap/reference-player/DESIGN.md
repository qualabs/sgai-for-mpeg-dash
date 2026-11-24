# reference-player — diseño

Un Player que implementa la extensión, sobre dash.js, y la batería que dice si
hace lo que `context/03` le pide: los tests de conducta de los criterios del
Player y los 22 vectores de UC que dejó `code-first-pipeline`, que hoy salen
todos `NOT_VERIFIABLE — no executor`. Es también el segundo entregable de
`PROJECT.md`, el prototipo con lineal y no lineal en la misma sesión. Va antes
del v13 (D-8 de `conformance-tests`).

## Lo medido (2026-11-23)

- **Criterios del Player.** `context/03` tiene 165 criterios; 60 tienen al
  Player entre sus titulares (57 sólo el Player, 2 `Publisher + Player`, 1
  `Player + APS`). Leído con `bin/conformance/spec/criteria.py`.
- **La población del nivel 3b son 76 criterios**, los que el catálogo del
  nivel 2 (`bin/conformance/spec/catalog.py`) manda a nivel 3: los 59 del
  Player que salen `Player behaviour: level 3` (R29.3 es del Player pero es una
  propiedad del pedido y ya tiene regla) y 17 de `spec document`, APS o
  Publisher cuya consecuencia ata al Player: R4.8, R6.5, R7.1, R12.5, R13.1,
  R13.6, R19.3, R20.4, R26.1, R27.1, R28.1, R32.1, R34.1, R34.6, R34.9, R36.1,
  R40.9. R1.1 es nivel 3a y queda afuera.
- **Testeables por conducta: 61 de los 76.** La clasificación es mía, criterio
  por criterio, sobre el texto:
  - 61 observables desde afuera: pedidos con sus parámetros y su momento,
    beacons, el reloj y el estado del Player, la geometría de lo que se dibuja.
  - 7 observables pero sin carrier en la spec hasta el v13: R41.4, R41.5,
    R41.6, R41.7 (audio del aviso), R42.3, R47.2 (beacons de ocurrencia) y
    R48.3 (disclosure). Son las filas 4, 8, 10 y 11 de `## Not placed` en
    `output-analysis/v12.7-context-delta.md`.
  - 8 que una prueba de caja negra no decide: R1.6 (cómo se detecta la
    degradación es del Player, y no se induce de forma repetible), R3.2 (es la
    suma de los demás), R11.2 (una propiedad de la arquitectura), R21.1 y
    R37.1 (permisos, nada que pueda fallar), R29.10 (la capacidad real del
    dispositivo), R33.2 (reportar métricas es opcional y no hay canal) y R44.3
    (SDK opcional, y además sin carrier).
- **13 de los 61 necesitan el lineal de la 6ta**: R4.2, R4.8, R6.5, R7.1,
  R13.1, R17.5, R20.1, R20.3, R40.3, R40.4, R40.5, R40.6, R40.9.
- **dash.js 5.3.0 no trae el lineal de la 6ta.** En el paquete fijado en
  `bin/players/`, cero archivos con `InsertPresentation`,
  `ReplacePresentation`, `ListMPD`, `ImportedMPD` o `alternativeMPD`; el mismo
  grep encuentra `urn:mpeg:dash:event:callback` en 24, así que el instrumento
  encuentra. Shaka 5.3.6 sí tiene `InsertPresentation` (13) y `alternativeMPD`
  (18), y tampoco `ListMPD`. El paquete npm de dash.js trae sólo `dist/`, no
  las fuentes.
- **La API pública de dash.js alcanza para engancharse** (`index.d.ts`):
  `on(schemeIdUri)` con `EVENT_MODE_ON_RECEIVE` / `ON_START`,
  `addRequestInterceptor` / `addResponseInterceptor`, `extend()`.
- **Los vectores de UC son 22, con 110 resultados** (105 por clase D1–D5, 5
  legacy), y suman **5,35 h de reproducción en serie**; el más largo, 1005 s
  (`observe_until` de cada vector por sus resultados).
- **Ningún vector de UC prueba un criterio de borde.** R4.9 (el redondeo de la
  duración contra el cap) no aparece ni en `context/04` ni en los vectores; el
  mismo conteo encuentra R4.2 dos veces en `04`.

## Decisiones

### D-1. La referencia es el dash.js fijado sin tocar más un módulo nuestro, no un fork

D-8 de `conformance-tests` dice "otra compilación del mismo dash.js fijado más
lo nuestro". Hay dos formas de hacerlo:

| | cómo | por qué sí | por qué no |
|---|---|---|---|
| **(a) módulo** | `sgai-dashjs`, cargado junto al `dist/` fijado, sólo por la API pública: suscribe nuestros esquemas y los de la 6ta, arma el pedido de resolución, dibuja en una capa DOM sobre el `<video>`, y el lineal corre en un segundo `MediaPlayer` sobre un segundo `<video>` | la base de la referencia y el Player legacy son el mismo archivo, así que una diferencia de conducta no es una diferencia de build; nada que rebasar cuando dash.js se mueva; el módulo se puede llevar a otro Player | el squeezeback escala el `<video>` por CSS, fuera del render de dash.js; el empalme entre dos `<video>` tiene un hueco de milisegundos |
| (b) fork | el código de dash.js en `v5.3.0` con parches | todo es alcanzable | hay que mantenerlo; el Player legacy y la referencia dejan de compartir binario |

**Se elige (a).** Una referencia de conducta mide qué hace el Player y cuándo,
no la calidad del empalme. (b) entra sólo para lo que la API pública no
alcance, y lo dice T-01, que prueba primero el caso más difícil: un insert y un
replace lineales que vuelven al punto correcto del principal. Queda descartado
en esta fase un PR a dash.js upstream.

Lo acordó el líder del proyecto al aprobar el diseño: cambia la frase de D-8
de `conformance-tests` y deja para otro momento un PR a dash.js.

### D-2. El código vive en este repo, en `reference-player/`

Las alternativas: una carpeta al lado de `bin/`, o un repo propio. **Se elige
este repo**: los tests, sus fixtures y el hash de los criterios viven acá, y en
dos repos cada cambio de `context/03` cruzaría los dos. Se separa el día que
haya que publicarlo como paquete. El `CLAUDE.md` del proyecto suma la carpeta
a su layout.

Lo acordó el líder del proyecto al aprobar el diseño; `PROJECT.md` dejaba
abierto si el prototipo vive "in this folder or in an external repo".

### D-3. Un test de conducta es un vector, con el mismo esquema que los de UC

Cada test es `spec-source/behaviour/R<n>.<m>[-<k>].yaml`, válido contra
`spec-source/scenarios/schema.json` extendido con campos opcionales:

- **qué criterio prueba**: `criterion` y `criterion_sha256`, en el lugar de
  `uc` / `uc_sha256`;
- **lo cargado**: lo que el esquema ya tiene (`fixtures`, capacidades del
  dispositivo), más `aps` (cómo responde el APS de prueba a cada pedido:
  documento, demora, status, nada) y `actions` (lo que hace quien mira y
  cuándo: pausa, reanuda, salta, cambia la velocidad, descarta, hace click);
- **lo observado y lo esperado**: lo que el esquema ya tiene (`requests`,
  `presentation`, `beacons`, con `tolerance`), más `geometry` para los layouts.

Así hay un solo ejecutor, un esquema y un check para los dos tipos. Se
descartan dos cosas: un catálogo en Python como el del nivel 2, porque ataría
los tests a nuestro harness cuando son datos que cualquier Player podría
correr, y dejar sólo los vectores de UC, porque recorren 22 escenarios y no los
61 criterios (R4.9 no está en ninguno).

### D-4. La población se lee del catálogo, y el hash es el del nivel 2

Los 76 criterios salen del catálogo del nivel 2 leído por código, no de una
lista escrita. Cada uno tiene al menos un test, o una entrada en
`spec-source/behaviour/index.yaml` con `NOT_VERIFIABLE` y su motivo (los 7 sin
carrier y los 8 de arriba). El check sale `1` si falta alguno o si un test
nombra un criterio de afuera.

El texto que se hashea es el que define `criteria.py` (`pin_entry`), importado y
no reescrito, así el nivel 2 y el 3b no pueden leer un criterio distinto. Un
criterio que cambió o se retiró da `2` con la lista de tests a revisar, que es
lo que el v13 recibe.

### D-5. El APS de prueba y los beacons son rutas de Playwright, no un server

`run.mjs` ya intercepta cada pedido. El APS es un `page.route` sobre la URL de
resolución: responde lo que dice el campo `aps` del test y anota el pedido con
sus parámetros y su tiempo de sesión. Los beacons, rutas que responden `204` y
anotan URL y tiempo. Los medios siguen en el server local de
`bin/conformance/players.py`, con el contenido de `ffmpeg`. No hay ningún
proceso nuevo que levantar ni bajar.

### D-6. Las clases D1–D5 se emulan en un Chromium, con un perfil de dispositivo

El navegador es uno. La clase es configuración del módulo: decodificadores de
video simultáneos, formas que renderiza (video, imagen, HTML), layouts y audio
del aviso, lo que R3.1 da por clase. La referencia elige lo que elegiría un
dispositivo de esa clase, y nada mide decodificadores reales.

### D-7. Se enchufa como un adaptador más, con `--behaviour`

`bin/players/adapters/sgai.js` es el adaptador de dash.js más el módulo. Además
de lo que los adaptadores exponen hoy, entrega lo observado: pedidos de
resolución, beacons, segmentos de presentación con tiempos de sesión y la
geometría de la capa del aviso en cada cambio. El JS mide y Python compara
contra lo esperado, como hoy en `players.py`.

Se corre con `check-dash-conformance.py --behaviour` (los tests de criterio y
los vectores de UC), con exits 0/1/2/64 como el resto de `bin/`, y sólo así
(D-13). Las 5,35 h en serie se bajan con la concurrencia que `run.mjs` ya
tiene y con contenido corto donde el vector lo permita; T-09 mide cuánto tarda
la batería.

### D-8. Un FAIL de conducta informa y no bloquea la promoción

ADR 0057: los Players informan y no bloquean. La referencia es nuestra, pero
un FAIL puede ser un bug de la referencia o un hueco de la spec, y no se sabe
cuál hasta mirarlo. **Se elige**: informa, y el informe de T-09 clasifica cada
FAIL (referencia o spec). La alternativa, bloquear, ataba la promoción a la
calidad de un prototipo y a una batería de horas; con D-13 la promoción ni
siquiera la corre. Lo acordó el líder del proyecto al aprobar el diseño.

### D-9. Del lineal de la 6ta, lo que piden los criterios y los vectores

La referencia implementa eventos `urn:mpeg:dash:event:alternativeMPD:insert:2025`
y `…:replace:2025` (§5.16), la cola de ejecución por PRT con `@executeOnce`,
`@maxDuration`, `@clip`, `@earliestResolutionTimeOffset` y `@startWithOffset`
(§5.16.2.2, §5.16.4), la List MPD (§8.14) con sus `ImportedMPD`, y los
callbacks `urn:mpeg:dash:event:callback:2015` de los MPD de aviso. Cada cosa se
cita contra la copia primaria cuando se implementa. No entra lo que ningún
criterio ni vector usa: SCTE-35, encadenamiento de MPD, Periods remotos por
xlink.

### D-10. Los 7 criterios sin carrier esperan al v13

Salen `NOT_VERIFIABLE — sin carrier`, con su hash. El v13 decide los carriers
y los vuelve tests. Inventar carriers provisorios en la referencia sería
decidir el HOW del v13 desde un Player, al revés del orden acordado.

### D-11. El Player no se prueba con tests que lo copian

Los tests de una familia se escriben del texto del criterio **antes** que el
código de esa familia, y cada uno se ve fallar contra la referencia sin esa
familia. Un test que nunca falló no se sabe si mide algo.

### D-12. La demo es una página local y un video de una sesión

Una página servida en local que reproduce, con la referencia, una sesión con
lineal, overlay y pausa (sale de un vector de UC), y la grabación de esa sesión
con Playwright. Publicarla afuera (por ejemplo en un bucket público) no entra:
sería mandarla a terceros, y lo decide el líder cuando la vea.

La audiencia es el WG de DASH, y la sesión, la que mejor muestre lineal,
overlay y pausa juntos. El líder no lo contestó al aprobar; se le pregunta
cuando la demo exista.

### D-13. La batería de conducta es opt-in: nada la corre por defecto

El líder del proyecto, al aprobar: *"Ok, construyamos pero que por defecto no
se use porque es muy caro en tiempo"*. La batería corre sólo con `--behaviour`
explícito. No la invocan `build-all`, el incremental, `promote.py`, la suite
`bin/test_*.py`, ni `check-dash-conformance.py` sin flag. Un test de `bin/` lo
verifica: arma cada camino por defecto y falla si alguno llama al ejecutor de
la batería. Los tests de las piezas de la batería (el check, la comparación)
corren sobre datos, sin Chromium. Por eso D-8 no tiene nada que gatear: la
promoción no la ve.

## Lo que no se hace

- No se modifica dash.js ni se manda un PR upstream.
- No se mide la calidad del empalme lineal ni el rendimiento. No hay DRM.
- No hay dispositivos reales, otro navegador que Chromium, ni Shaka como base.
- No se prueban los 8 criterios no observables ni los 7 sin carrier.
- No se toca `context/`, ni `spec-source/` fuera de `behaviour/` y de la
  extensión del esquema. Un hueco de la spec que aparezca es un hallazgo (un
  ítem o un issue), no un cambio de esta fase.
- No corre por defecto en ningún camino (D-13).
- No hay VAST, SDK de verificación, métricas ni SCTE-35.
- No se adapta a los carriers del v13: eso es trabajo del v13, con la lista
  que dan los `2`.

## Riesgos

| riesgo | mitigación |
|---|---|
| La API pública no alcanza para el lineal (el reloj del principal en un replace, la vuelta al punto) | T-01 lo prueba primero; si no alcanza, D-1 (b) acotado a ese punto, y se avisa |
| Los tiempos en Chromium headless varían entre corridas | la `tolerance` de los vectores; un test inestable se corre tres veces y se reporta como inestable, no como PASS |
| R16.1 pide "within one rendering frame" | se mide con `requestAnimationFrame`; si headless no da frames confiables, `NOT_VERIFIABLE` con el motivo |
| La batería es larga (5,35 h en serie) | concurrencia y contenido corto; T-09 mide el tiempo |
| La referencia pasa sus propios tests porque los escribió el mismo agente | D-11 |
| La parte más grande es dibujar cada layout (D-8 de `conformance-tests`) | T-07 lleva su propia task y los tests de geometría (D-3) |
