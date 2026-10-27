---
description: "Varios assets por opción con geometría libre (viewport, zDepth, volumen por asset), como un perfil nuevo, uno que extiende, u opcional."
status: designing
category: feature
origin: "Nicolás, 2026-10-27, al decidir sobre output-analysis/2026-10-27-david-v3-vs-context.md (fila 22)"
---

# Varios assets por opción, como modo opcional

Lo que trae SVTA2053 v3 (David Hassoun): una opción con varios assets
adicionales, cada uno con `viewport`, `zDepth` y `volume` (borrador
`sandbox/sgai/2026-10-02-svta-doc-update/borrador.md`, §4.4.7 `LayoutControl`,
§4.4.8 `AssetLayout`, §5.3.1-5.3.3, Tables 20 y 22). El caso que lo motiva es
la L de dos barras: el primario en `"0 40 40 0"`, una barra vertical y una
horizontal, y como las dos son video, *"two video bars need three"*
decodificadores (§5.3.2). La demo `hls-non-linear-ads-demo` lo implementa
(`lib/capabilities.js` `needsOf`: 1 decodificador para el primario más uno por
elemento que no es `image/*`; `lib/renderer.js` `stackingOf`; ADR 0026, 0047,
0089 de ese repo).

Nicolás: *"una fase únicamente con esto, de forma que sea un perfil nuevo, un
perfil que extiende, u opcional"*.

**Base.** `context/` en `76c4845`. Las cláusulas de la base se verificaron
contra la copia primaria (sha256 `a7274eb2…`, la que declara
`context/00-normative-base.md`) con `pdftotext` y búsqueda literal; se cita
cláusula y frase. Lo que no se pudo verificar ahí va `[inferred]`.

**Lo que este diseño no hace:** no toca `context/` (Nicolás aprueba antes), no
decide carriers (es del build, con `context/06`), no decide multiview (ítem
`multiview`), no trae mezcla de audio ni el foco de audio del espectador.

## El antecedente, y lo que se aprende de la fase 03

**Descartado el 2026-09-28** (fila 22 de `output-analysis/2026-10-27-david-v3-vs-context.md`,
"Point 14 of 2026-09-28") por cuatro choques: R22 (una forma no lineal a la
vez), R27.1 (una L lleva *"exactly one ad creative"*), R10.2 (no hay estándar de
layout propio), R41.7 (una sola fuente de audio).

**La fase 03 (custom layout) se abandonó** (LOG 2026-09-25, "R39 reemplaza a la
fase 03"): proponía N elementos, orden Z y píxeles contra un viewport de
referencia, y nunca se ejecutó. Nicolás la reemplazó por la versión más chica
que servía: R39, un solo overlay, opcional para todos, rectángulo en porcentaje,
región opcional del Publisher. Tres cosas de esa fase no se repiten acá:

1. **Era un sistema de layout general**, sin tope ni familia. Acá hay tope de
   elementos, tope de decodificadores, y sólo slots overlay (D4, D2).
2. **Resolvía R10 reinterpretándolo** (*"R10 does NOT govern the advanced,
   on-top extensions"*, su PHASE.md). R39 hizo lo contrario: se declara *"the one
   declared exception … to R10.2 / R10.3"* y R10.3 lo nombra. Acá se hace como R39.
3. **Traía sus decisiones cerradas** (*"not open for re-litigation"*) sin
   exploración. Este diseño compara y deja las preguntas abiertas con su
   recomendación.

## D1. La forma: modo opcional dentro del mismo documento, el patrón de R39

| Forma | A favor | En contra |
|---|---|---|
| **A. Perfil nuevo** (documento o clase de conformidad aparte) | El texto base no se toca; ciclo de vida propio. | Duplica la maquinaria que ya existe (opciones R5, capacidades R29, admisión R38) o la referencia entera. "Perfil" en DASH es otra cosa: *"A profile imposes a set of specific restrictions"*, y *"profiles merely specify restrictions on MPD and Segments rather than DASH Client behaviour"* (§8.1, NOTE 1); lo nuevo acá es casi todo conducta del Player. §8.1 además recomienda que lo definido afuera *"be not referred to as profiles, but as Interoperability Points"*. |
| **B. Perfil que extiende el base** (superconjunto: base + esto) | Una afirmación de conformidad clara. | Para admitir esto tendría que **aflojar** obligaciones del base, y una implementación que cumple el perfil extendido dejaría de cumplir el base. En DASH un perfil sólo restringe: *"All profiles are a subset of the full profile"* (§8.1). Si se arregla diciendo "salvo bajo el perfil X" en cada requerimiento, es la forma C con otro nombre. |
| **C. Modo opcional en el mismo documento** (como `custom`, R39) | **Ya existe y está aprobado**: R39 es *"an optional mode: an implementation that does not support it is conformant"*, con su token en R12.2, su parámetro `sgai-custom-layout` en R29.1, admisión por lista en R38.1, y *"A Player that does not support `custom` treats every `custom` option as not renderable"* (R39.5). La degradación es la de R5.6, sin mecanismo nuevo. | El texto base se toca en las listas cerradas (R12.1, R12.2, R29.1, R38.1) y en la lista de excepciones de R10.3, igual que con R39. La conducta del base no cambia, el texto sí, en esos puntos. |

**Recomendación: C.** Es la única de las tres que cumple *"el perfil base no
cambie"* en lo que importa, la conducta: una implementación sin el modo sigue
siendo conforme, y un slot que no lista el token se comporta exactamente como
hoy. Y es la única que no inventa mecanismo: capacidad, admisión y degradación
son las de R39. **El documento no lo llama "perfil"**, por §8.1; lo llama
"optional mode", como R39.

**Cómo se declara el soporte.** Un parámetro reservado más en R29.1
(`sgai-multi-asset-layout`, `1`/`0`, nombre propuesto), opcional como todos
(R29.2); ausente es indeterminado (R29.7). Las clases D1-D5 de R3 no cambian:
se definen con los tres primeros ejes (R29.6), y el soporte de un modo no es un
eje del dispositivo sino del Player, igual que `sgai-custom-layout`.

## D2. Qué es: un layout nuevo, `multi-asset`, y una opción sigue siendo una forma

Un token nuevo en R12.2, `multi-asset` (nombre propuesto), sólo para slots
overlay (la familia de R39; R38.1 ya pone overlay y squeezeback en el mismo
slot). **Una opción `multi-asset` es una sola forma no lineal y un solo aviso**:
sus elementos son las piezas de ese aviso, se presentan juntos, se trackean por
opción (R13.6), se descartan juntos (R35) y llevan un identificador de creativo
(R23.2). Por eso R22 y R27.1 no cambian (D7).

No se reusan los tokens de squeezeback con varios elementos: eso sí obligaría a
aflojar R27.1. Una L de dos barras es, en esta spec, una opción `multi-asset`, no
una `squeezeback-l-shape-*`.

## D3. Geometría: rectángulo en porcentaje, orden de apilado, y el primario es un elemento

- **Cada elemento de aviso** tiene su forma (video, imagen o HTML, R15), un
  rectángulo en porcentaje del viewport de video **en las unidades de R39.2**
  (x, y, ancho, alto, origen arriba a la izquierda) y una posición de apilado.
- **El primario** es un elemento con rectángulo y posición propios, opcionales:
  sin declararlos ocupa todo el viewport, debajo de todo. Hace falta para la L
  de dos barras, y para el fondo a cuadro entero con el primario encima (borrador
  §5.3.1, *"in squeezebackFrame the asset is at zDepth 0 and the primary content
  at 1"*).
- **Las posiciones de apilado son distintas** dentro de la opción; los elementos
  se pueden superponer y gana el de posición más alta. David pone *"SHOULD be
  unique"* (§4.4.8); acá es obligación porque dos iguales dejan el orden sin
  definir.
- **El primario no se deforma**: el Player lo escala dentro de su rectángulo
  manteniendo la relación de aspecto. Es lo que la demo tuvo que decidir (ADR
  0047: *"Una caja que no lo hiciera deformaría la imagen"*).

Porcentaje y no píxeles por la misma razón que R39 (LOG 2026-09-25). Inserts
(borrador §4.2.3) o x/y/ancho/alto es carrier: lo decide el build, y `06` tiene
que nombrar el `LayoutControl` de SVTA como alternativa, para que entre a la
comparación (CLAUDE.md, "The two layers").

No entran: modo de llenado de los elementos de aviso (recorte, encaje), redondeo
a píxeles, tiempos distintos por elemento. Son del Player o del creativo.

## D4. El tope: se mide por lo que la opción le pide al dispositivo

**Cómo se mide.** Como R26.3 y R27.3 y como `needsOf` de la demo: un
decodificador para el primario, más uno por elemento de aviso que es video; una
superficie de imagen sobre video si algún elemento es imagen; una de HTML si
alguno es HTML. El Player compara eso contra lo que declara (R29.10) en R5.6.

**Dos topes:**

- **A lo sumo tres decodificadores de video por opción, el primario incluido.**
  R29.1 da a `sgai-video-decoders` los valores `1`, `2`, `3`, con *"`3` means
  three or more"*: una opción que pidiera cuatro no se podría chequear contra
  ese parámetro sin cambiarlo, y cambiarlo cambia el base. Tres alcanzan para la
  L de dos barras en video.
- **A lo sumo tres elementos de aviso por opción.** Es el máximo de la Table 20
  de David (multiView, tres vistas además del primario); la L de dos barras usa
  dos. Sin tope, el modo es el sistema de layout general de la fase 03.

## D5. Audio: R41 entero, un elemento audible

R41 no cambia. Con la ventana habilitada (R41.2), la opción puede declarar **un**
elemento de aviso cuyo audio se escucha, en lugar del primario (R41.4); sin
declarar, ninguno. R41.7 sigue: una fuente a la vez, al volumen del espectador.

El `volume` 0-100 por elemento de David no se trae: es mezcla, y R41 la excluye
(*"This specification defines no mixing, ducking or gain level"*). La demo llegó
a lo mismo cuando el espectador elige: *"El elemento con foco suena a 100 y todo
el resto de la composición va a 0"* (ADR 0026 de la demo).

## D6. Un Player sin el modo, y el APS

- Player sin soporte: toda opción `multi-asset` es no renderizable y pasa a la
  siguiente (R5.6), como R39.5.
- Un recurso de un elemento que falla en su primer pedido tira la opción: ya lo
  dice R5.9 (*"each resource an option references"*), sin cambios.
- Nota informativa para el APS: una opción `multi-asset` seguida de una en un
  layout de R12 conserva la oportunidad en todo Player sin el modo (R5.8, DP-3).
  No es obligación: qué formatos van lo decide el anunciante (R5.8).

## D7. Cómo quedan R22, R27.1, R10 y R41.7

| Req | En el modo | Cambio de texto en el base |
|---|---|---|
| **R22** | Se cumple: una opción es una forma (D2). Lo que deja de valer es la frase de R22.1 *"so the device never needs more than main content plus one ad form's video decoder"*: una forma `multi-asset` puede pedir dos. | Una oración en el párrafo de razón de R22: la necesidad de una opción `multi-asset` la cuenta R49.4 contra la capacidad declarada. R22.1 no cambia. |
| **R27.1** | No aplica: gobierna los tokens `squeezeback-*`, y la L de dos barras va como `multi-asset` (D2). | Ninguno. |
| **R10** | Excepción declarada, como R39: el modo define posiciones. | R10.3, última oración: las excepciones son `custom` (R39) y `multi-asset` (R49). Y R12.1/R12.2 suman el token como el segundo sin contraparte IAB. |
| **R41.7** | Se cumple: un elemento audible (D5). | Ninguno. |

Los otros toques de texto, todos en listas cerradas y con el mismo molde que
R39: R12.1, R12.2 (token), R29.1 (parámetro; *"the four below"* pasa a cinco),
R38.1 (*"does not admit `custom` or `multi-asset`, which a slot admits only by
listing it"*).

## Redacción propuesta

Números provisorios: se asignan al ejecutar (PROJECT.md, "Requirement and
use-case numbering"); hoy el siguiente libre es R49 (R43, R45, R46 están
reservados por `sgai-for-hls`, LOG 2026-09-28) y UC-23.

> - **R49. The `multi-asset` layout (optional).**
>   *Gist: An optional layout, `multi-asset`, lets one option place up to three ad elements and the primary content, each in its own rectangle and stacking position; one such option is one non-linear form.*
>
>   `multi-asset` is an **optional mode**: an implementation that does not
>   support it is conformant to this specification. With `custom` (R39), it
>   is a declared exception to the IAB mapping of R12 and to R10.2 / R10.3,
>   and it applies to the overlay family only. The case is **UC-23**.
>
>   **Conformance criteria** (runtime):
>   - **R49.1** (spec document): Supporting `multi-asset` is OPTIONAL for
>     every actor. The layout carries no IAB ad type and applies only to
>     non-linear overlay slots. A slot admits it only by listing it in its
>     allowed layouts (R38.1).
>   - **R49.2** (APS): An option with layout `multi-asset` MUST carry one to
>     three ad elements. Each ad element carries a form (R15), a rectangle in
>     percent of the video viewport in the units of R39.2, and a stacking
>     position. The option MAY carry a rectangle and a stacking position for
>     the primary content; when it carries none, the primary content occupies
>     the whole viewport beneath every ad element. The stacking positions of an
>     option MUST be distinct.
>   - **R49.3** (Player): The Player MUST render every element of the option
>     in its rectangle, drawing an element over every element with a lower
>     stacking position, and MUST scale the primary content into its rectangle
>     preserving its aspect ratio.
>   - **R49.4** (Player): An option with layout `multi-asset` needs one
>     concurrent video decoder for the primary content and one for each ad
>     element that is a video, the image-over-video capability when an ad
>     element is an image, and the HTML-over-video capability when one is
>     HTML. The option is satisfiable only when the capability the Player
>     declares (R29.10) covers all of them (R5.6). An option MUST need at most
>     three concurrent video decoders, the primary content included.
>   - **R49.5** (spec document): An option with layout `multi-asset` is one
>     non-linear ad form (R22) and one ad: its elements are presented
>     together for as long as the option is presented, and the beacons
>     (R13.6), dismissal (R35) and creative identifier (R23.2) are those of
>     the option.
>   - **R49.6** (APS): When the window allows the ad's audio (R41.2), the
>     option MAY declare one of its ad elements as the one whose audio is
>     heard; R41 then applies to that element.
>   - **R49.7** (Player): A Player that does not support `multi-asset` MUST
>     treat every `multi-asset` option as not renderable (R5.6).
>
>   *Informative note:* an APS that follows a `multi-asset` option with an
>   option in a layout of R12 keeps the opportunity on every Player that does
>   not support this mode (R5.8, DP-3).

R29.1, fila nueva:

> | `sgai-multi-asset-layout` | `1`, `0` | Whether the Player supports the optional `multi-asset` layout (R49). |

R22, al final del párrafo de razón:

> An option of the optional `multi-asset` layout is one form; what it needs
> from the device is counted by R49.4 against the declared capability, and it
> may be more than one video decoder for the ad.

**UC-23** (sección propia, marcada optional mode): la L de dos barras en video
como primera opción, la L con backplate en video como segunda, el backplate en
imagen como tercera. Con `sgai-video-decoders=3` se ve la primera; con `2`, la
segunda; con `1` e imagen sobre video, la tercera; un Player sin el modo
arranca por la segunda. **Glosario** (*proposed*): multi-asset layout, ad
element, stacking position.

## Multiview sobre este mismo mecanismo (observación)

El molde de D1 (token opcional, parámetro de capacidad, degradación por R5.6,
excepción declarada en R10.3 y R12.1) le sirve igual a multiview. Y en geometría
una composición multiview es una opción de este modo con N videos: David la
define así (*"carried like any other concurrent presentation"*, §4.3.1, Table 2;
Table 22 es informativa). Lo que separa a multiview no es la geometría: es
contenido que no es aviso (R12 es de tipos de aviso), las vistas en vivo, y el
audio que elige el espectador (contra R41.7). Si multiview se montara acá, sus
presets `multiview-*` pasarían a ser layouts sugeridos, y la tensión con R10 que
ese ítem evitó con presets fijos ya estaría pagada por este modo. Se decide en
`multiview`.

## Lo que no entra

- Mezcla de audio o volumen por elemento, y el foco de audio que elige el
  espectador (D5).
- Pausa y lineal: sólo slots overlay.
- Región del Publisher para este modo (pregunta 2).
- Más de tres decodificadores o de tres elementos de aviso (D4).
- Modo de llenado, redondeo y tiempos por elemento (D3).
- Beacons o identificadores por elemento (D2).
- Multiview y contenido que no es aviso.
- El carrier: inserts o rectángulo, nombres, dónde viaja. Es del build.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| El WG (R10 lo pidió el chair de DASH) lo lee como un sistema de layout por la puerta de atrás. | Topes de D4, sólo overlay, excepción declarada y nombrada en R10.3 (no reinterpretación, lección de la fase 03), y ningún vocabulario de posiciones: sólo rectángulos. |
| Un APS manda sólo opciones `multi-asset` y la oportunidad se pierde en casi todos los dispositivos. | Nota informativa de R49 y DP-3; el UC-23 muestra la escalera. |
| Se solapa con `custom`: un elemento sin primario declarado es casi R39 sin región. | Aceptado: `custom` es el modo barato y tiene región; ver pregunta 6. |
| El build v13 lo absorbe junto con todo lo demás (ítem `major-build-v13`) y no se puede aislar su efecto. | Una task de la fase mide la cobertura de R49 en el sidecar de validación de v13. |
| El carrier cae por defecto en un atributo propio sin pesar el `LayoutControl` de SVTA. | Una task agrega la alternativa a `context/06` antes del build. |

## Preguntas abiertas, con recomendación

1. **Topes: tres elementos de aviso y tres decodificadores.** Recomiendo los dos
   (D4). Subir el de decodificadores obliga a cambiar el dominio de R29.1.
2. **¿Región del Publisher (R39.2) también para este modo?** Recomiendo que no
   en esta versión: con el primario movible y fondos a cuadro entero, una región
   que encierre los elementos de aviso casi nunca se cumple. El control del
   Publisher es admitir o no el token en el slot.
3. **¿El APS puede mover el primario, y siempre sin deformarlo?** Recomiendo que
   sí a las dos (D3): sin primario movible no hay L de dos barras.
4. **¿Elementos HTML?** Recomiendo que sí: R15 admite las tres formas y R49.4 ya
   los cuenta contra `sgai-html-over-video`.
5. **¿Sólo overlay, o también pausa?** Recomiendo sólo overlay; David tampoco
   cubre pausa (*"This specification does not handle pause ads"*, §4.3.1).
6. **¿`custom` queda aparte, o pasa a ser el caso de un elemento?** Recomiendo
   aparte: cambiar R39 rompe a los Players que ya declaran `sgai-custom-layout`.
7. **Nombres `multi-asset` y `sgai-multi-asset-layout`.** Recomiendo esos. No
   usar "profile" (§8.1).
