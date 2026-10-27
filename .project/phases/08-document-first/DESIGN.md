# El documento primero

Diseño del ítem, hecho sobre `context/` en `44cfff4`, el último commit que
lo cambió.

## Para qué es

`context/03-requirements.md` escribe muchos hechos dos veces: una vez como lo
que declara el Publisher o lleva el APS, y otra vez como lo que el Player hace
cuando lo encuentra. Este trabajo reescribe 03 para que la semántica de cada
interfaz esté escrita una sola vez, del lado del documento, y el
comportamiento de un actor aparezca sólo donde no se deduce de esa semántica.
Termina con la reescritura validada sobre `context/`; la spec se reconstruye
después, en el build v13 (D-1).

## Por qué: así está escrita la base

Verificado contra la copia primaria que declara `context/00-normative-base.md`
(sha256 `a7274eb2…`), por búsqueda literal de cada cita:

- **La base dice de sí misma que especifica documentos.** *"This document
  primarily specifies formats for the Media Presentation Description and
  Segments"* (§1). *"However, this document does not provide a normative
  specification for such a client"* (§4.1). El modelo de cliente es
  *"the informative client model"* (§4.2), y los perfiles *"merely specify
  restrictions on MPD and Segments rather than DASH Client behaviour"*
  (§8.1).
- **Casi todas sus obligaciones tienen por sujeto el documento.** La base
  tiene 1069 modales `shall` y `should`. El análisis v12.6 los clasificó por
  sujeto: 1029 sobre un construct del documento, 35 sobre el cliente y 5
  sobre el autor, y una muestra al azar de 25 del primer grupo dio 25
  restricciones sobre el documento [inferred: el total se recontó, la
  clasificación por sujeto no se rehízo].
- **La semántica se escribe como efecto del documento, sin actor.** La
  tabla de `@maxDuration` dice *"it shall be terminated at the end of this
  duration"* y *"If the value of @maxDuration is zero, the event is not
  executed"* (Table 63). No dice que el autor lo declara ni que el cliente
  lo termina. Lo mismo para la ejecución de un evento: *"An event is
  executed every time the playhead enters the active interval"* y *"The
  alternative MPD is resolved at each execution of the Event"*
  (§5.16.2.2.1 y §5.16.2.2.6).
- **Donde hace falta comportamiento, es una garantía para el autor.** *"the
  MPD author may assume that the steps described in this subclause are
  taken, while the client implementer may provide any functionally
  equivalent implementation"* (§5.16.2.2.1). En todo §5.16.2.2 hay un solo
  modal, y es sobre el documento (*"@startWithOffset attribute shall not be
  present"*).
- **La base no escribe el mismo hecho dos veces.** Lo que se repite es una
  capa de derivación (la tabla de semántica, la variable de la Table 57 y
  el modelo que opera sobre ella), y la tabla remite al modelo en lugar de
  repetirlo: *"For details see the definition of APDmax in Table 57"*
  (Table 63).

El documento funciona como la interfaz, y lo que hace cada actor queda obvio
a partir de él. 03 está escrito al revés: de sus 199 criterios, 95 tienen
por rol sólo al Player (Anexo A.1).

## Por qué antes del v13

El build es uno solo, el v13 (D-1). Si corriera sobre la estructura de hoy,
el build siguiente tendría que volver a validarla entera. Y ningún build
protege una reescritura: la comparación de degradación de
`check-incremental` saltea las unidades que el delta tocó, así que no
miraría justo los 83 criterios que cambian, y el camino incremental sobre
v12.6 ya terminó en `MAJOR RECOMMENDED` (`output-analysis/v12.7-context-delta.md`).
La protección es a nivel de `context/`, comparando la versión vieja con la
nueva (D-12), y el v13 corre después sobre una entrada estable.

## Decisiones

### D-1. Este ítem no construye la spec: el v13 es un ítem aparte, al final

La reescritura termina en `context/`, validada. El build lo hace
`roadmap/major-build-v13`: una sola corrida mayor que junta lo acumulado
desde v12.6 (la fase 07, el fix de error-semantics y los carriers que el
incremental no pudo ubicar), este ítem y multiview. El perfil multi-asset no
entra: quedó en backlog.

La comparación del v13 contra lo publicado no va a poder separar la
reestructura del resto del delta. Se acepta por dos razones: la protección de
la reestructura no depende del build (D-12), y el resto del delta está
registrado decisión por decisión en `LOG.md` y en las ADRs.

**Orden en `context/`:** este ítem va antes de que multiview escriba su
requerimiento en 03 (su `T-01-PLAN.md`). Así multiview lo escribe una sola
vez con la regla (D-8) y bajo el check (D-9), en lugar de que la reescritura
lo alcance después. Si 03 cambia entre este diseño y el arranque, el mapa
(Anexo A) se rehace sobre el commit nuevo antes de reescribir (D-12, tarea 1).

### D-2. El documento se define como tres interfaces

- **I-MPD, lo que el Publisher escribe en el MPD:** las ventanas no
  lineales, su familia, su rango, su tope, sus layouts y región admitidos,
  su relación con los eventos lineales, su offset de resolución anticipada,
  su ejecución en cada entrada del playhead y el offset de una ejecución
  tardía, su declaración de una vez por sesión y el permiso de audio; y los
  eventos lineales heredados de la base, con su semántica de base.
- **I-REQ, el pedido del Player al APS:** la URL que declara la ventana y
  los parámetros reservados, los de capacidad de R29 y los que el slot
  declara y el Player reenvía (R38, R39 y R41).
- **I-RES, lo que devuelve el APS:** el documento de resolución, con sus
  candidatos, las opciones ordenadas de cada uno, su tracking (con tiempo,
  por opción, del slot, por ocurrencia y de viewability), el ClickThrough,
  los identificadores del creativo, la verificación, la divulgación, su
  validez y su comportamiento al agotarse.

Cada interfaz tiene que quedar completa: cada elemento, con su semántica
escrita una vez. El inventario (Anexo A.7) cuenta 76 elementos. De esos, 30
están definidos más de una vez, 6 no tienen definición en ningún criterio y
9 están definidos una sola vez pero como obligación del Player.

| Interfaz | Elementos | Una vez | Más de una | Ninguna | Una vez, sólo del lado del Player |
|---|---:|---:|---:|---:|---:|
| I-MPD | 28 | 13 | 12 | 3 | 4 |
| I-REQ | 16 | 10 | 5 | 1 | 3 |
| I-RES | 32 | 17 | 13 | 2 | 2 |
| Total | 76 | 40 | 30 | 6 | 9 |

La lista de elementos es del inventario, porque `context/` no enumera los
elementos de ninguna interfaz. Enumerarlos es parte de lo que este trabajo
produce (D-5).

Los casos de uso de 04 son la guía de cómo cada actor usa las interfaces.
No definen semántica.

### D-3. La semántica de un elemento se escribe una vez, en un criterio del lado del documento

Cada elemento de una interfaz tiene su significado en un único criterio, con
el rol de quien lo escribe (Publisher, APS o spec document). El significado
incluye el efecto, escrito como lo escribe la base: "the audio of an option
that declares it MUST replace the primary content's audio while the option
is presented", y no "when the option declares its audio, the Player
MUST render it". Otros criterios y los casos de uso lo citan por su id y no
lo repiten.

**La semántica conserva la fuerza de la obligación que absorbe.** Un MUST del
Player pasa a un MUST con el elemento como sujeto, como hace la base con
*"it shall be terminated at the end of this duration"* (Table 63). Sin eso,
la validación de D-12 (cada obligación, con la misma fuerza) no puede pasar.

**Una nota de privacidad de DP-4 sigue a la definición.** DP-4 pide la nota
donde se define la información que describe, así que se mueve con ella: la de
R29.2 pasa a R29.1, donde quedan definidos los parámetros. La de R47.2 se
queda en R47.2, que sigue como garantía (D-7).

La semántica que hoy vive sólo en la prosa sube a un criterio. Son nueve
requerimientos: R3, R12, R26, R27, R28, R29, R31, R32 y R40 (Anexo A.5).
Esto agrega dos criterios, R12.5 (qué composición denota cada token de
layout) y R40.9 (a qué se ancla una ventana y qué significa cada relación).
Hay que subirla porque `check-promotable` sólo recorre criterios y modales
de la prosa, y una semántica que está en una tabla de la prosa no entra en
la validación.

**R33 sigue el mismo patrón aunque no es de ninguna interfaz.** R33.2 obliga
a derivar el intervalo de pausa "as described above", y esa derivación (del
fin de un período detenido por `UserRequest` al `start` del siguiente
`Resume`) está sólo en la prosa de R33. Sube a R33.2 sin cambiar de
contenido, por la misma razón: fuera de un criterio, la validación no la
ve.

### D-4. El comportamiento de un actor se escribe sólo cuando no se deduce

Un criterio sobre lo que hace un actor se queda cuando dice algo que la
semántica del documento no alcanza. Las clases que el recorrido encontró:

- un orden, o qué se prueba primero;
- un fallback: qué pasa cuando algo no se puede, por ejemplo una opción
  cuyo recurso no carga (R5.9);
- qué hacer ante un documento que falla, falta, no es conforme o llega
  tarde (R34.10);
- un límite del dispositivo;
- un cómputo, por ejemplo la conversión de timescale de R4.9;
- cuándo ocurre algo, por ejemplo cuándo se consume una ventana de una vez
  por sesión (R34.3);
- una cadena entre actores: el Publisher declara, el Player reenvía y el
  APS obedece (R38);
- una garantía de interoperabilidad que tiene que estar escrita para valer
  (D-7).

Todo criterio del Player cuyo contenido sea "cuando el documento dice X,
el Player hace lo que X significa" se va, y su contenido pasa al criterio
del documento que define X.

### D-5. La estructura de 03: los requerimientos siguen siendo la unidad, con un índice de interfaces al principio

03 conserva sus requerimientos y sus ids. Hay tres cambios:

- **Una sección "Interfaces" al principio**, con una tabla por interfaz.
  Cada fila es un elemento y el id del criterio que lo define. La tabla es
  un índice, no una segunda definición: no lleva semántica, sólo punteros.
- **Dentro de cada requerimiento, los criterios del documento van
  primero**, y los de comportamiento después.
- **La regla de escritura** en una sección propia (D-8).

| Alternativa | Por qué no |
|---|---|
| Reorganizar 03 en tres secciones, una por interfaz | Parte cada requerimiento entre secciones (R40 tiene criterios de I-MPD y de comportamiento), rompe la unidad que `check-promotable` recorre y cambia la posición de casi todo, lo que vuelve ilegible el diff contra la versión vieja. |
| Un archivo de `context/` por interfaz | Lo mismo, más la renumeración de archivos y de cada referencia cruzada. |
| Dejar la estructura y sólo borrar duplicados | Resuelve los dobles, pero ninguna interfaz queda enumerada, y "completa" no se puede verificar. |

### D-6. La estructura de los archivos de `context/` no cambia

El orden 00 a 08 y 99 sigue como está. Revisado contra la convención:

- 02, 03 y 04 ya siguen el orden actores, requerimientos y casos de uso.
- 06 es el cómo, y no se toca: no cita ningún id que se va.
- 05 describe la interfaz lineal de base con el mapeo VAST, y se superpone
  con I-RES en lo lineal. No se toca en este trabajo. Si pasa a ser el
  anexo ilustrativo de R11.5 se decide aparte.

### D-7. Las garantías de interoperabilidad quedan escritas: R28.2, R42.3 y R47.2; R20.5 y R20.6 sin cambios

- **R28.2 queda.** R28.1 recibe la semántica: el click-tracking se dispara
  cuando el espectador activa el ClickThrough. R28.2 queda como garantía
  explícita, porque R28 existe para que *"every Player conformant to this
  specification reads them the same way"*. Esa frase es una promesa sobre
  los Players y no sobre el documento. Si se deduce, deja de ser una
  promesa. Lo que sale de R28.2 es la semántica repetida: queda como
  remisión a R28.1.
- **R42.3 y R47.2 quedan igual que R28.2.** Tienen la misma forma y la misma
  razón: son carriers nuevos que un Player legacy ignora, y la semántica sola
  no obliga a ningún Player a leerlos. R42.1 y R47.1 reciben la semántica;
  R42.3 y R47.2 quedan como la garantía, con remisión. Cuesta dos criterios,
  y la nota de privacidad de R47.2 se queda donde está.
- **R20.5 y R20.6 quedan sin cambios.** R20.5 se deduce del documento,
  pero R20.6 exige a propósito que sea una obligación normativa del Player,
  porque *"a rule that selects which presentation option reaches the
  screen cannot depend on a reader treating an illustration as a
  requirement"*. Cambiarlo es una decisión de contenido, no de redacción.

### D-8. La regla de escritura vive en `context/`, el CLAUDE.md apunta a ella

La regla completa va en una sección "How requirements are written" al
principio de 03. Las razones: `context/` tiene que entenderse solo, y lo leen
tanto los prompts del build como el working group. El `CLAUDE.md` del
proyecto lleva una línea que apunta ahí, sin copiarla.

Texto propuesto, en inglés como el resto de `context/`:

> **How requirements are written.** This specification defines three
> interfaces: what the Publisher writes in the MPD, the request the Player
> sends the APS, and the resolution document the APS returns. The
> "Interfaces" section lists every element of each, and the criterion that
> defines it.
>
> 1. The meaning of an element is written once, in a criterion held by the
>    party that writes the element (the Publisher, the APS, or the
>    specification document), including its effect, with the strength of
>    the obligation it states. Every other criterion, and every use case,
>    cites it by identifier and does not restate it.
> 2. A criterion on what an actor does is written only when it does not
>    follow from the meaning of what the document carries: an order, a
>    fallback, what to do when something fails, is missing, does not
>    conform or arrives late, a device limit, a computation, when something
>    happens, a chain between actors, or a guarantee of interoperability
>    that has to be stated to hold.
> 3. Identifiers are stable. A criterion that is merged into another, or
>    withdrawn, keeps its identifier out of use, and the "Retired
>    identifiers" table says where its content went.

Línea para el `CLAUDE.md` del proyecto, en la sección de tono: *"Requirements
follow the writing rule at the top of `context/03-requirements.md` ("How
requirements are written"); it is not restated here."*

### D-9. Un check en `bin/` hace cumplir la parte estructural de la regla

`bin/check-context-interfaces.py`, como paso 0.7 de `build-all`, con las
mismas salidas que los otros checks (`0`, `1`, `2` y `64`).

**Qué detecta de verdad:**

- que cada fila del índice apunte a un criterio que existe;
- que ningún elemento aparezca en dos filas, ni en dos interfaces;
- que el criterio al que apunta cada fila tenga un rol del lado del
  documento (Publisher, APS o spec document), y no Player;
- que ningún id de la tabla "Retired identifiers" aparezca citado en
  `context/`, salvo en esa tabla;
- que ningún id que falte en 03 deje de figurar en la tabla de retirados:
  compara los ids contra el commit sobre el que se congeló el mapa
  (Anexo A), que el check nombra como constante. No contra el de la v12.6:
  los ids nacidos después (R5.9, R13.8, R34.5 a R34.10) ya los citan 04 y
  las ADRs 0022 a 0028, y tres de ellos se retiran.

**Qué no detecta, y no puede:** que dos criterios digan lo mismo con otras
palabras, que un criterio del Player sea deducible, que la prosa repita
semántica, o que un elemento que nadie puso en el índice exista en el
documento. Todo eso es de significado y no tiene firma sintáctica. Un aviso
heurístico ("un criterio del Player nombra un elemento del índice, así que
revisalo") se evaluó y se descarta: marcaría casi todos los criterios de
comportamiento legítimos, y una lista que nadie lee es la forma en que un
check muere. El check tiene que poder fallar: se prueba rompiendo a
propósito cada una de las cinco condiciones.

### D-10. Los ids son estables, y los retirados tienen su tabla

Un criterio fusionado conserva el id del que lo absorbe. El absorbido y el
retirado no se reusan nunca. Al final de 03 va una tabla "Retired
identifiers", con una fila por id y a dónde pasó su contenido. Es un
registro de identificadores y no una huella de iteración: el working group,
las ADRs y los issues citan ids viejos, y sin la tabla esas citas apuntan a
nada.

### D-11. Las ADRs no se tocan

Hay 19 menciones a ids que se retiran en 7 ADRs (0011, 0014, 0018, 0022,
0023, 0024 y 0028), todas `accepted`. Las ADRs aceptadas son
registro. La tabla de retirados resuelve esas citas sin editarlas, así que no
llevan nota.

### D-12. Un agente reescribe y otro valida, contra el mapa de obligaciones

La ejecución se reparte en cuatro tareas:

1. **El mapa.** El Anexo A es el mapa de obligaciones: cada id, su acción y
   su lugar nuevo. Antes de reescribir se confirma que 03 no cambió desde
   `44cfff4` (si cambió, el mapa se rehace sobre el commit nuevo), y se
   congela como evidencia de la fase.
2. **La reescritura**, por una sesión o un agente: 03 según el mapa, la
   sección "Interfaces", la regla, la tabla de retirados, las 26 menciones
   de 04 y 99 a ids que se van y las 12 referencias internas de 03 a esos
   ids.
3. **El check** de D-9, con su prueba de que falla.
4. **La validación**, por otro agente que no reescribió, con la versión
   vieja (el commit anterior a la reescritura) y la nueva:
   - **Que cada obligación siga estando.** Por cada modal de cada unidad
     vieja (criterio o prosa), el lugar nuevo del mapa tiene que tener esa
     obligación, con la misma fuerza. Un script lista los pares y el
     validador los lee; el script no juzga significado. La prueba del
     instrumento: se borra a propósito una obligación del texto nuevo, y el
     validador la tiene que encontrar. Tres cambios de fuerza o de
     contenido son decisiones de este diseño y no pérdidas, y el validador
     los da por buenos sólo en su lugar: el carrier de los beacons con
     tiempo pasa de SHOULD a MUST (D-14), R29.1 nombra tres parámetros
     (D-13) y R28.1 dice qué pasa con la URL de destino (D-16).
   - **Que 04 y 99 sólo cambien ids.** El diff de cada uno, con los ids
     viejos reemplazados por su destino en la tabla de retirados, es vacío.
     La prueba: se cambia a propósito una palabra de un caso de uso y el
     diff deja de ser vacío.
   - **Que no queden dobles:** los 9 redundantes, los 14 parciales y los 6
     grupos del mismo actor del análisis v12.6, y los tres pares de R34 que
     entraron con la fase 07 (R34.2 y R34.5 con R34.1, R34.7 con R34.6, R34.8
     con R34.9), uno por uno.
   - **Que las tres interfaces estén completas:** los 76 elementos del
     inventario tienen una fila en el índice, y los 6 sin definición la
     tienen.
   - **Que `context/` siga cerrando:** `check-context-coherence`,
     `check-context-vocabulary` y el check nuevo, todos en `0`.

**Qué se hace con los checks que no protegen una reescritura:**

- `check-incremental degradation` no aplica: el v13 es mayor. Su función
  (que no se pierda lo que había) la cumple la validación de la tarea 4.
- La población de `check-promotable` baja de 199 a 164 criterios y cambia
  en las 32 unidades de prosa, porque la semántica que estaba en la prosa
  sube a criterios. Eso es correcto, siempre que cada unidad que sale figure
  en el mapa con su destino. Se deja escrito en la evidencia: población
  vieja, población nueva y la diferencia explicada por el mapa.

Con la tarea 4 en verde el trabajo termina. El build y la promoción son de
`major-build-v13`, con el criterio de siempre.

### D-13. Los tres parámetros que reenvían lo que el slot declara tienen nombre, y R29.1 los enumera

R29.1 dice "the four below and the audio parameter of R29.9, and no others",
pero los layouts permitidos (R38), la región custom (R39) y el permiso de
audio (R41.5) también son parámetros reservados, R38.3 lo dice, y no tienen
nombre en `context/`. La contradicción entró con la enumeración de R29
(`94ef488`).

R29.1 pasa a tener dos tablas: la de capacidad (los cuatro de hoy y
`sgai-ad-audio`) y la de lo que el slot declara y el Player reenvía. Los
nombres de las dos primeras filas de la segunda son los de la spec
publicada, `sgai-allowed-layouts` y `sgai-custom-region`, y el permiso de
audio es `sgai-ad-audio-allowed`. La lista cerrada de R29.1 cuenta las dos
tablas.

| Alternativa | Por qué no |
|---|---|
| Una sola tabla con los ocho | Mezcla lo que el Player dice de sí con lo que reenvía del MPD, y R29.2 trata distinto a cada grupo (opcional frente a obligatorio). |
| Nombres nuevos para los tres | Los dos primeros ya están publicados en `dist/` y en ejemplos de pedido; cambiarlos sólo agrega una diferencia con lo publicado. |

### D-14. El carrier de los beacons con tiempo es MUST

R6.2 lo dice como SHOULD y R13.1 como MUST, y la fusión en R13.1 obliga a
elegir uno. Es MUST, que es lo que ya dicen R13.1 y R13.4 (*"mandatory"*).
R6.3 sigue siendo la salida para lo que el callback no puede expresar. Es el
único cambio de fuerza de la reestructura, y D-12 lo registra como tal.

### D-15. Los dos tokens de double-box dicen si hay fondo

R26 dice que el fondo es opcional, y hay dos tokens,
`squeezeback-double-box` y `squeezeback-double-box-background`, sin que esté
dicho si el primero puede llevar fondo ni si el segundo puede no llevarlo. El
token dice la composición: `-background` lleva fondo y el otro no lo lleva.
Va en R12.5 (qué denota cada token) y en R26.1. Es lo que UC-10 ya ilustra
(*"the first token is the case with no background, the second the case with
an advertiser background"*), así que 04 no cambia.

### D-16. La URL de destino del ClickThrough sigue el modelo de R48.3

Ningún criterio dice qué hace el Player con la URL de destino del
ClickThrough: sólo que dispara el click-tracking. Sigue el modelo de R48.3:
el Player hace disponible el destino al espectador por los medios de su
dispositivo, y cómo es suyo. Va en R28.

## Impacto fuera de 03

- **04:** 24 menciones a ids que se van (R5.7, R5.2, R26.2, R7.3, R38.5,
  R41.1, R34.5, R34.8, R5.5 y R34.7), que se reescriben al id nuevo. Los
  casos de uso no cambian de contenido.
- **99:** 2 menciones (R29.9 y R34.8), que se reescriben.
- **06:** 0 menciones a ids que se van. Sus citas (entre ellas R13.6, R13.7,
  R34.9, R35.2 y R41.2) apuntan a ids que se conservan.
- **02, 05, 07 y 08:** 0 menciones.
- **ADRs:** 19 menciones, que no se editan (D-11).

## Qué no se hace

- **Decisiones de fondo fuera de D-13 a D-16.** Donde la reescritura
  encuentra otra ambigüedad, la anota como pregunta y no la resuelve.
- **Renumerar archivos de `context/`**, o mover requerimientos entre
  secciones de 03.
- **Cambiar 05, 06, 07 u 08**, salvo citas a ids.
- **Editar ADRs.**
- **Correr un build.** Es de `major-build-v13`.
- **Renombrar parámetros o atributos.** Los tres de D-13 se nombran porque
  no tenían nombre; ninguno existente cambia.

## Anexo A. El mapa de obligaciones

Sobre `context/03-requirements.md` en `44cfff4`. La clasificación queda,
reescribe, fusiona o retira es juicio aplicado a la regla, no una medición;
lo que sí se mide son los conteos, y cada uno lleva su comando.

**Cómo leer la columna "acción".** *Queda*: el texto no cambia de fondo. *Se
reescribe*: el id se conserva y su texto cambia, porque absorbe a otro o
porque pasa a escribir la semántica del lado del documento. *Se fusiona en
X*: su contenido tiene que aparecer en X, y el id queda retirado. *Se
retira*: no hay nada que mover, porque otro criterio ya lo dice entero, y el
id queda retirado. En los dos últimos casos el id no se reasigna.

### A.1. Cifras y método

| Cifra | Valor |
|---|---:|
| Criterios hoy | 199 |
| Criterios cuyo rol es sólo el Player | 95 |
| Quedan | 116 |
| Se reescriben | 46 |
| Se fusionan | 31 |
| Se retiran | 6 |
| Cambian (reescriben, fusionan o retiran) | 83 |
| Nuevos (R12.5, R40.9) | 2 |
| Criterios después de la reestructura | 164 |
| Menciones fuera de 03 a ids que se van (04 / 99 / ADRs) | 24 / 2 / 19 |
| Referencias internas de 03 a ids que se van | 12 |

```
$ grep -cE '^\s*- \*\*R[0-9]+\.[0-9]+\*\* \(' context/03-requirements.md
199
$ grep -oP '^\s*- \*\*R[0-9]+\.[0-9]+\*\* \(\K[^)]+' context/03-requirements.md | grep -cx 'Player'
95
$ python3 bin/check-promotable.py --population | cut -f2 | sort | uniq -c
    199 criterion
     32 prose
     22 use-case
```

"Del Player" es el rol exactamente `Player`: los criterios compartidos
(`Player + APS`, `APS + Player`, `Publisher + Player`) no cuentan, y con
ellos serían 101.

Las acciones salen de un script que arma la tabla A.2 desde los ids
extraídos del archivo y aborta si falta o sobra una decisión:

```
missing [] extra []
199 {'se reescribe': 46, 'se fusiona': 31, 'se retira': 6, 'queda': 116}
gone 37 03-internal 12 04 24 99 2 ADR 19
after 164
```

Con R33.1 borrado a propósito de la lista de A.3, el mismo script da
`missing ['R33.1']`.

Las citas se cuentan por id y archivo con
`grep -oP "\b${id//./\\.}(?![0-9])" <archivo> | wc -l`, y para las ADRs
sobre la concatenación de `.project/decisions/*.md`. Las internas de 03
son las menciones menos la de la propia definición. Controles del
instrumento, para ver que sabe encontrar y que no cuenta de más:

```
R5.6 en 04: 5                       (control positivo)
R99.9 (inexistente) en 04: 0
ADRs, \bR4\.1 sin lookahead: 18     (cuenta R4.1, R4.10 y R4.11 juntos)
ADRs, R4.1 / R4.10 / R4.11 con (?![0-9]): 8 / 8 / 2
```

El grep cuenta ids sueltos, no rangos. Los rangos de todo `context/` y de
las ADRs:

```
$ grep -noP '\bR[0-9]+\.[0-9]+\s*(–|-|to|through)\s*R?[0-9]+\.[0-9]+' context/*.md .project/decisions/*.md
context/03-requirements.md:2126:R40.3–R40.5
.project/decisions/0004-enumerate-edition-scoped-iab-ad-type-subset.md:64:R12.1 to R12.3
```

Los dos abarcan sólo ids que se conservan.

### A.2. Los 83 criterios que cambian

En el orden del archivo.

| # | id | rol actual | interfaz | acción | lugar nuevo |
|---:|---|---|---|---|---|
| 1 | R29.1 | spec document | I-REQ | se reescribe | R29.1: los parámetros del pedido y su significado, en dos tablas (D-13): la de capacidad, con los cuatro de hoy y `sgai-ad-audio` (de R29.9), y la de lo que el slot declara y el Player reenvía, con `sgai-allowed-layouts`, `sgai-custom-region` y `sgai-ad-audio-allowed` (hoy sin nombre, en R38.3); viajan como query parameters y no por el template de URL del MPD (hoy sólo en la prosa). La nota de privacidad de R29.2 pasa a R29.1, que es donde queda la definición de los parámetros (DP-4). |
| 2 | R29.2 | Player | I-REQ | se reescribe | R29.2: todo parámetro reservado es opcional, salvo los que el slot declara, que R38.2, R39.3 y R41.5 obligan a enviar (absorbe R29.8). |
| 3 | R29.6 | spec document | gobierno | se fusiona en R3.1 | R3.1 dice que las clases son las combinaciones de los tres primeros ejes de R29.1 que da la tabla de R3, y que una combinación sin nombre se declara igual. |
| 4 | R29.8 | spec document | I-REQ | se fusiona en R29.2 | R29.2 nombra las tres excepciones a la opcionalidad. |
| 5 | R29.9 | spec document | I-REQ | se fusiona en R29.1 | R29.1 lleva `sgai-ad-audio` como quinta fila de la tabla de capacidad. |
| 6 | R4.1 | Publisher | I-MPD | se reescribe | R4.1: todo slot overlay y pausa declara un máximo, y el máximo es la cota que la presentación del slot no pasa, con lo que acota cada familia en R4.2, R4.6 y R31.2 (absorbe R4.3); en un evento lineal heredado es `@maxDuration`, opcional (R4.8). |
| 7 | R4.2 | Player | comportamiento | se reescribe | R4.2: donde el tope acota duración acumulada (overlay, secuencia no lineal, inserción lineal), el Player corta en el tope aunque caiga a mitad de aviso, y una duración declarada no es razón para descartar un candidato (absorbe R7.3 y R14.2). |
| 8 | R4.3 | Player | I-MPD | se fusiona en R4.1 y R4.6 | R4.1 recibe "no se pasa de la cota"; R4.6 recibe el caso `@clip="false"`. |
| 9 | R4.6 | Player | I-MPD | se reescribe | R4.6 pasa a ser semántica del documento: en un reemplazo lineal el tope acota el fin programado según `@clip` de la base (default `true`), y con `@clip="false"` termina en PRTA + APDmax, que es la base moviendo la cota; la inserción no tiene `@clip`. |
| 10 | R4.11 | Player | I-MPD | se reescribe | R4.11 como semántica del tope: se mide sobre la línea de tiempo de presentación, y no cuenta un intervalo en que esa línea no avanza ni uno en que la forma está suspendida, por una pausa del espectador (R17.1) o por un evento lineal heredado en ejecución (R40.4) (absorbe la parte de tope de R19.3). |
| 11 | R31.1 | Player | I-MPD | se reescribe | R31.1 como semántica de la ventana de pausa: una pausa del espectador que empieza dentro de la ventana dispara el pedido de resolución, y una que empieza fuera de toda ventana no dispara ninguno. |
| 12 | R5.1 | APS | I-RES | se reescribe | R5.1: opciones como lista ordenada donde el orden de documento es la preferencia, lo que significa que se presenta la primera que el Player puede satisfacer (absorbe R5.2 y R5.5). |
| 13 | R5.2 | Player | comportamiento | se fusiona en R5.1 | R5.1 dice que el orden es la preferencia y qué implica; los chequeos quedan en R5.6. |
| 14 | R5.3 | Player | comportamiento | se reescribe | R5.3: un candidato sin opción que pase R5.6 y R5.9 se saltea y se sigue con el siguiente en orden; agotados, R20.1 o el contenido principal (absorbe R5.7 y R7.2). |
| 15 | R5.5 | APS | I-RES | se retira | Nada que mover: R5.1 ya lo dice entero. |
| 16 | R5.6 | Player | comportamiento | se reescribe | R5.6: los chequeos (a) capacidad del dispositivo y (b) layouts que el slot admite, y que reenviar el set no quita el chequeo (absorbe R38.5); deja de repetir el recorrido en orden, que es R5.1. |
| 17 | R5.7 | Player | comportamiento | se fusiona en R5.3 | R5.3 lleva el salto al siguiente candidato, preservando el orden, cuando ninguna opción pasa R5.6 y R5.9. |
| 18 | R7.1 | Player | I-RES | se reescribe | R7.1 como semántica del documento: el orden de los candidatos es el orden de presentación, lineales y no lineales, cada uno empieza cuando termina el anterior, y un candidato salteado bajo R5.3 no es un reordenamiento ni ocupa tiempo (absorbe R7.4 y R14.1). |
| 19 | R7.2 | Player | comportamiento | se fusiona en R5.3 | R5.3 cubre el descarte; "no es un reordenamiento" va a R7.1. |
| 20 | R7.3 | Player | comportamiento | se fusiona en R4.2 | R4.2 lleva "se reproduce y se corta en el tope, la duración declarada no es razón para descartar". |
| 21 | R7.4 | Player | I-RES | se fusiona en R7.1 | R7.1 dice el orden en positivo. |
| 22 | R7.5 | Player | comportamiento | se retira | Nada que mover: repite R4.5. |
| 23 | R3.1 | spec document | gobierno | se reescribe | R3.1: las clases de dispositivo son las filas de la tabla de R3, combinaciones de los tres primeros ejes de R29.1 (absorbe R29.6), y la spec da el comportamiento esperado por clase y oportunidad. |
| 24 | R3.3 | Player | comportamiento | se retira | Nada que mover: es el chequeo (a) de R5.6. |
| 25 | R16.1 | Player | comportamiento | se reescribe | R16.1: al pasar de pausa a play el Player quita el aviso de pausa en un frame y vuelve al contenido principal aunque haya un aviso a mitad de presentación (absorbe R32.3). |
| 26 | R16.2 | Player | comportamiento | se fusiona en R13.3 | R13.3 dice que un beacon cuyo tiempo cae después de que terminó la presentación del aviso no se dispara, termine como termine. |
| 27 | R32.1 | APS | I-RES | se reescribe | R32.1: el documento de una pausa declara `repeat`, `request-again` o `stop`, con el significado de cada uno (hoy sólo en la prosa), y uno que no declara nada significa `stop`. |
| 28 | R32.3 | Player | comportamiento | se fusiona en R16.1 | R16.1 lleva "vuelve al contenido principal aunque haya un aviso a mitad". |
| 29 | R34.1 | Publisher | I-MPD | se reescribe | R34.1: la declaración once-per-session vale en overlay, squeezeback y pausa, y significa: en overlay y squeezeback, consumida la ventana, toda entrada posterior del playhead deja el contenido sin interrumpir y no dispara ninguno de sus beacons; en pausa, como máximo un aviso de pausa por ventana en la sesión, y una pausa posterior dentro de la ventana deja el contenido sin interrumpir (absorbe R34.2 y R34.5). |
| 30 | R34.2 | Player | I-MPD | se fusiona en R34.1 | R34.1 lleva la semántica para la pausa. |
| 31 | R34.5 | Player | I-MPD | se fusiona en R34.1 y R34.3 | R34.1 lleva la semántica para overlay y squeezeback; R34.3 recibe que cruzar la ventana sin que empiece un aviso (un seek que la saltea, una resolución vacía) la deja disponible. |
| 32 | R34.6 | Player | I-MPD | se reescribe | R34.6 como semántica del documento (rol spec document): una ventana overlay o squeezeback se ejecuta cada vez que el playhead entra en su rango (la reproducción la alcanza, un join o un seek cae adentro, un seek vuelve antes de su fin), y cada ejecución se resuelve de nuevo (R36), con su tope (R4) y sus beacons (R13, R13.7, R42) (absorbe R34.7). |
| 33 | R34.7 | Player | I-MPD | se fusiona en R34.6 | R34.6 lleva que cada ejecución resuelve de nuevo; que una resolución anterior se presenta sólo si sigue vigente ya lo dicen R36.4 y R36.5. |
| 34 | R34.8 | Player | I-MPD | se fusiona en R34.9 | R34.9 lleva el default, el significado del offset y que la ejecución termina a más tardar con la ventana; que no se dispara el beacon de una parte no presentada se deduce de R13.1. |
| 35 | R34.9 | Publisher | I-MPD | se reescribe | R34.9: la declaración de que una ejecución tardía empieza con offset significa que empieza en el punto de la secuencia (R14) que está tan lejos de su inicio como la ejecución lo está del inicio de la ventana, y los candidatos que terminan antes no se presentan; sin la declaración, toda ejecución empieza en el primer candidato; en los dos casos termina a más tardar con la ventana (absorbe R34.8). |
| 36 | R35.2 | APS | I-RES | se reescribe | R35.2: la demora es el tiempo desde que el slot empieza a presentarse antes del cual no se puede cerrar, y desde el cual se puede cerrar mientras el slot esté en pantalla; cero es inmediato (absorbe R35.3). |
| 37 | R35.3 | Player | comportamiento | se fusiona en R35.2 | R35.2 lleva el antes y el después de la demora. |
| 38 | R35.6 | Player | comportamiento | se fusiona en R13.3 | R13.3 cubre los beacons después del cierre; la frase sobre falla va a R35.4. |
| 39 | R35.8 | Player | I-MPD | se reescribe | R35.8 como semántica del documento: en un slot lineal rige `@skipAfter` de la base con su default, el default de R35.1 no aplica, y la spec no agrega precedencia entre los dos `@skipAfter`. |
| 40 | R36.1 | Publisher | I-MPD | se reescribe | R36.1: el offset es lo más temprano que un Player puede resolver, medido desde el inicio de la ventana en overlay y en pausa, nunca desde la pausa; default 60 s; cero es resolver al disparo (absorbe R36.2 y R36.3). |
| 41 | R36.2 | Player | I-MPD | se fusiona en R36.1 | R36.1 lleva la cota y el ancla. |
| 42 | R36.3 | Player | I-MPD | se fusiona en R36.1 | R36.1 lleva el ancla "inicio de la ventana, nunca la pausa". |
| 43 | R36.4 | APS | I-RES | se reescribe | R36.4: la validez declarada es hasta cuándo se pueden presentar los candidatos de esa resolución; sin declaración, durante la ejecución para la que se obtuvo (R34.6). |
| 44 | R36.5 | Player | comportamiento | se reescribe | R36.5: al disparar la oportunidad el Player verifica la validez y, vencida, pide una nueva; una re-resolución sin candidato usable es una resolución vacía (R30) (absorbe R36.6). |
| 45 | R36.6 | Player | comportamiento | se fusiona en R36.5 | R36.5 lleva que el vacío al re-resolver cuenta como R30; "no volver a la vencida" ya lo dice R36.4. |
| 46 | R38.1 | Publisher | I-MPD | se reescribe | R38.1: `@allowedLayouts`, cuando está, es el conjunto de layouts que el slot admite; cuando no está, el de su familia (hoy sólo se escribe el caso ausente). |
| 47 | R38.3 | spec document | I-REQ | se fusiona en R29.1 | R29.1 lleva el parámetro de layouts permitidos en su tabla. |
| 48 | R38.5 | Player | comportamiento | se fusiona en R5.6 | R5.6 (b) lleva el chequeo y la frase "reenviar el set no quita el chequeo". |
| 49 | R39.5 | Player | comportamiento | se reescribe | R39.5: sólo lo que no se deduce de R39.4: una opción `custom` fuera de la región no es renderizable y se pasa a la siguiente, y un Player sin `custom` trata toda opción `custom` como no renderizable. |
| 50 | R19.2 | Player | comportamiento | se retira | Nada que mover: es R19.1 en negativo. |
| 51 | R19.3 | Player | I-RES | se reescribe | R19.3: la duración declarada de toda forma, imagen y HTML incluidas, es un valor de la línea de tiempo de presentación, y su largo en reloj es duración / velocidad (absorbe R19.4; la parte del tope va a R4.11 y la de beacons ya está en R13.1). |
| 52 | R19.4 | Player | I-RES | se fusiona en R19.3 | R19.3 lleva "toda forma, imagen y HTML incluidas". |
| 53 | R21.1 | Player | comportamiento | se reescribe | R21.1: sólo el MAY de liberar recursos cuando el layout es `pause-fullscreen`; la superficie la fija el token (R12.5) y la forma única activa ya es R22.1 y R17.1. |
| 54 | R26.1 | APS + Publisher | I-RES | se reescribe | R26.1: el fondo es un atributo de composición del layout, presente con `squeezeback-double-box-background` y ausente con `squeezeback-double-box` (D-15), siempre imagen fija, creativo del anunciante, llena las bandas que dejan las dos cajas, y sin fondo las bandas son negras (hoy la imagen y el negro están en la prosa) (absorbe R26.2). |
| 55 | R26.2 | Player | comportamiento | se fusiona en R26.1 | R26.1 lleva la composición y el negro por defecto; la geometría de las dos cajas la da el token (R12.5). |
| 56 | R27.1 | APS + Publisher | I-RES | se reescribe | R27.1: la opción lleva un solo creativo, que cubre todo el cuadro por debajo, y el contenido principal achicado va encima en la región que denota el token; vale para los dos L-shape y para `squeezeback-frame` (esto último hoy sólo en la prosa); no hay un tercer elemento (absorbe R27.2). |
| 57 | R27.2 | Player | comportamiento | se fusiona en R27.1 | R27.1 lleva la composición. |
| 58 | R41.1 | Player | I-RES | se fusiona en R41.3 | R41.3 lleva el default sin audio del aviso y qué se oye mientras tanto. |
| 59 | R41.3 | APS | I-RES | se reescribe | R41.3: una opción que declara su audio se presenta con el audio del aviso en lugar del del contenido (overlay y squeezeback) mientras dure; una que no lo declara se presenta sin audio del aviso y con el del contenido sobre el que se compone; en pausa, sin audio del aviso salvo declaración (absorbe R41.1). |
| 60 | R41.4 | Player | comportamiento | se reescribe | R41.4: sólo restaurar el audio del contenido cuando la opción termina, termine como termine. |
| 61 | R14.1 | Player | I-RES | se fusiona en R7.1 | R7.1 lleva el orden para no lineales, "cada uno empieza cuando termina el anterior" y que un candidato salteado no ocupa tiempo. |
| 62 | R14.2 | Player | comportamiento | se fusiona en R4.2 | R4.2 nombra la secuencia no lineal entre los casos de duración acumulada. |
| 63 | R17.2 | Player | comportamiento | se reescribe | R17.2: sólo restaurar el overlay al reanudar si su ventana sigue activa; quitar el aviso de pausa es R16.1. |
| 64 | R17.3 | Player | comportamiento | se retira | Nada que mover: es R17.2 en negativo, y fuera de su rango el overlay no se presenta (R40.9). |
| 65 | R40.3 | Player | comportamiento | se reescribe | R40.3: sólo lo que no se deduce de R40.9: la ejecución del evento lineal con las reglas de la base para una ejecución tardía, y que cuándo resolver es del Player dentro de R36. |
| 66 | R40.4 | Player | comportamiento | se reescribe | R40.4: sólo lo que no se deduce de R40.9 y R34.6: la forma suspendida se retoma desde donde quedó y después sigue la secuencia, hasta el fin de la ventana o el tope; si la presentación vuelve fuera del rango, la ejecución terminó. |
| 67 | R40.5 | Player | comportamiento | se reescribe | R40.5: sólo lo que agrega a R40.9: dentro de la capacidad del dispositivo y de R22, el tope corre sobre la línea de tiempo de la alternativa (R4.11) y la forma termina cuando termina la alternativa. |
| 68 | R6.2 | APS | I-RES | se fusiona en R13.1 | R13.1 es la única definición del carrier de beacons con tiempo (hoy R6.2 dice SHOULD y R13.1 dice MUST). |
| 69 | R6.4 | Player | comportamiento | se retira | Nada que mover: es la regla de la base para namespaces desconocidos (§5.2.1), que R1.1 y R1.5 ya adoptan. |
| 70 | R6.5 | Player + APS | I-RES | se reescribe | R6.5 como semántica del documento: el alcance de `@id` de un beacon es su candidato en un documento no lineal y el de la base en un ListMPD; "disparar los dos" queda como consecuencia. |
| 71 | R6.6 | Player | I-RES | se fusiona en R13.1 | R13.1 lleva el ancla temporal: el tiempo del beacon es relativo a la presentación propia del candidato que lo aloja. |
| 72 | R13.1 | APS | I-RES | se reescribe | R13.1: carrier (callback de la base), MUST (D-14), tiempos relativos a la presentación propia del candidato que los aloja, y significado: cada beacon se dispara cuando la presentación del aviso llega a su tiempo (absorbe R6.2, R6.6 y R13.2). |
| 73 | R13.2 | Player | comportamiento | se fusiona en R13.1 | R13.1 lleva la semántica del disparo. |
| 74 | R13.3 | Player | comportamiento | se reescribe | R13.3: un beacon cuyo tiempo cae después de que terminó la presentación del aviso, por recorte (R4), cierre (R35) o reanudación (R16), no se dispara (absorbe R16.2 y R35.6). |
| 75 | R13.6 | APS + Player | I-RES | se reescribe | R13.6 como semántica del documento: un beacon adjunto a una opción informa esa opción y se dispara sólo si esa opción se presenta; uno adjunto al candidato, cualquiera que se presente. |
| 76 | R13.7 | APS + Player | I-RES | se reescribe | R13.7 como semántica del documento: el beacon de inicio del slot corresponde al primer aviso que empieza en cada ejecución (R34.6), también en una ejecución tardía; el de fin, al fin de la ejecución termine como termine; una ejecución sin avisos no tiene ni uno ni otro. |
| 77 | R33.2 | Player | comportamiento | se reescribe | R33.2 recibe la derivación del intervalo de pausa que hoy está sólo en la prosa de R33 (del fin de un período detenido por `UserRequest` al `start` del siguiente `Resume`), sin cambiar de contenido (D-3). |
| 78 | R28.1 | APS | I-RES | se reescribe | R28.1: además de dónde va, qué significa: las URLs de click-tracking se disparan cuando el espectador activa el ClickThrough (hoy no lo dice ningún criterio del lado del documento), y el destino se hace disponible al espectador con el modelo de R48.3 (D-16). Ver D-7. |
| 79 | R28.2 | Player | comportamiento | se reescribe | R28.2 se queda como la garantía explícita: todo Player conforme lee el carrier de R28.1 con esa semántica. Ver D-7. |
| 80 | R42.1 | spec document | I-RES | se reescribe | R42.1: carrier, conjunto cerrado (incluida la falla de R5.9) y significado: cada beacon se dispara una vez por ocurrencia en el aviso que lo lleva, nunca desde la línea de tiempo. R42.3 queda como garantía (D-7). |
| 81 | R42.3 | Player | comportamiento | se reescribe | R42.3 se queda como la garantía explícita: todo Player conforme dispara los beacons de R42.1 con esa semántica; la semántica repetida queda como remisión a R42.1. Ver D-7. |
| 82 | R47.1 | APS | I-RES | se reescribe | R47.1: cada beacon marcado con su resultado se dispara una vez por impresión cuando se determina ese resultado, e "indeterminado" es el resultado de un Player que no lo determina. R47.2 queda como garantía, con su nota de privacidad (D-7). |
| 83 | R47.2 | Player | comportamiento | se reescribe | R47.2 se queda como la garantía explícita: todo Player que determina la viewability dispara el beacon de R47.1 con esa semántica, y conserva su nota de privacidad; la semántica repetida queda como remisión a R47.1. Ver D-7. |

### A.3. Los 116 que quedan

R1.1, R1.2, R1.3, R1.4, R1.5, R1.6, R2.1, R2.2, R2.3, R2.4, R11.1, R11.2, R11.3, R11.4, R11.5, R18.1, R18.2, R29.3, R29.4, R29.5, R29.7, R29.10, R4.4, R4.5, R4.7, R4.8, R4.9, R4.10, R31.2, R12.1, R12.2, R12.3, R12.4, R15.1, R15.2, R15.3, R5.4, R5.8, R5.9, R30.1, R30.2, R3.2, R32.2, R32.4, R34.3, R34.4, R34.10, R35.1, R35.4, R35.5, R35.7, R36.7, R37.1, R37.2, R37.3, R38.2, R38.4, R38.6, R39.1, R39.2, R39.3, R39.4, R19.1, R25.1, R26.3, R27.3, R41.2, R41.5, R41.6, R41.7, R14.3, R17.1, R17.4, R17.5, R20.1, R20.2, R20.3, R20.4, R20.5, R20.6, R22.1, R40.1, R40.2, R40.6, R40.7, R40.8, R6.1, R6.3, R6.7, R13.4, R13.5, R13.8, R23.1, R23.2, R24.1, R33.1, R33.3, R33.4, R28.3, R42.2, R42.4, R44.1, R44.2, R44.3, R47.3, R48.1, R48.2, R48.3, R8.1, R8.2, R9.1, R9.2, R9.3, R10.1, R10.2, R10.3.

Cinco de ellos cambian sólo una remisión o reciben una frase, sin cambio de
fondo: R14.3 (su remisión a R14.1 pasa a R7.1), R39.3 (la de R38.3 pasa a
R29.1), R34.4 (la de R34.2 pasa a R34.1), R34.3 (recibe de R34.5 que cruzar
la ventana sin que empiece un aviso la deja disponible) y R35.4 (recibe de
R35.6 "un cierre es un resultado de la presentación, no una falla").

Las 12 referencias internas de 03 a ids que se van, que la reescritura
cambia junto con la reestructura: R29.9 (1, en R29.1), R5.7 (2), R7.2 (2),
R7.3 (1), R7.4 (1), R34.2 (1, en R34.4), R38.3 (1, en R39.3), R14.1 (1, en
R14.3), R14.2 (1) y R13.2 (1, en R34.8).

### A.4. Criterios nuevos

- **R12.5** (spec document, I-MPD e I-RES). Qué composición denota cada token de layout: para los squeezeback, la región que ocupa el contenido principal según la tabla de R12; para los dos double-box, si llevan fondo (D-15); para `pause-fullscreen` y `pause-partial`, la superficie; para los overlay, que el creativo se compone sobre un contenido que no se transforma. Hoy la tabla está en la prosa de R12 y el efecto se repite en R21.1, R26.2 y R27.2. Es el siguiente sub-id libre de R12.
- **R40.9** (spec document, I-MPD). La semántica de la ventana no lineal: a qué está anclada (una ventana overlay o squeezeback a su rango de tiempo de medio, una de pausa a la pausa del espectador dentro de su rango) y qué significa cada una de las tres relaciones con el evento lineal: la por defecto (la ventana se suspende mientras se ejecuta un evento lineal heredado que pisa, y se retoma en la misma ejecución si la presentación vuelve dentro de su rango; ADR 0025), supersede con su fallback, y on top. Hoy vive sólo en la prosa de R40 y, repartida, en R40.3, R40.4 y R40.5 como obligaciones del Player. Es el siguiente sub-id libre de R40.

### A.5. Semántica que hoy vive sólo en la prosa

| Requerimiento | Qué está sólo en la prosa (o en una tabla de la prosa) | Criterio que la sube |
|---|---|---|
| R26 | Que el fondo es siempre una imagen fija, del anunciante, y que sin fondo las bandas son negras (R26.2 lo dice del lado del Player) | R26.1, reescrito |
| R27 | La composición (creativo a cuadro completo debajo, contenido achicado encima en la región del token) y que R27 vale también para `squeezeback-frame` | R27.1, reescrito |
| R28 | Qué significa el click-tracking: se dispara cuando el espectador activa el ClickThrough. R28.1 sólo dice dónde va | R28.1, reescrito (R28.2 queda como garantía, D-7) |
| R40 | El anclaje de una ventana no lineal y el significado de default, supersede y on top | R40.9, nuevo |
| R12 | La tabla token a región de los squeezeback y la superficie de cada token de pausa | R12.5, nuevo |
| R32 | Qué hace cada uno de `repeat`, `request-again` y `stop` | R32.1, reescrito |
| R29 | Que los parámetros viajan como query parameters y no por el template de URL del MPD (R38.3 lo dice sólo como ejemplo) | R29.1, reescrito |
| R3 | La tabla de clases de dispositivo, que la prosa llama "the only definition of the classes" y ningún criterio carga (R29.6 remite a ella) | R3.1, reescrito |
| R31 | Qué es una ventana de pausa (dispara el pedido si la pausa empieza dentro). Hoy está en la prosa y en R31.1 como obligación del Player | R31.1, reescrito |

Fuera de las tres interfaces, R33 tiene el mismo patrón y sube a R33.2 (D-3).

### A.6. Los 37 ids que se van, y quién los cita

06, 02, 05, 07 y 08 no citan ninguno. Las ADRs que citan alguno: 0011
(R5.7), 0014 (R27.2), 0018 (R36.2, R36.3), 0022 (R5.7), 0023 (R34.7), 0024
(R34.5) y 0028 (R34.8, R14.1, R13.2), todas `accepted`.

| id | acción | 03 | 04 | 99 | ADR |
|---|---|---:|---:|---:|---:|
| R29.6 | se fusiona en R3.1 | 0 | 0 | 0 | 0 |
| R29.8 | se fusiona en R29.2 | 0 | 0 | 0 | 0 |
| R29.9 | se fusiona en R29.1 | 1 | 0 | 1 | 0 |
| R4.3 | se fusiona en R4.1 y R4.6 | 0 | 0 | 0 | 0 |
| R5.2 | se fusiona en R5.1 | 0 | 3 | 0 | 0 |
| R5.5 | se retira | 0 | 1 | 0 | 0 |
| R5.7 | se fusiona en R5.3 | 2 | 6 | 0 | 4 |
| R7.2 | se fusiona en R5.3 | 2 | 0 | 0 | 0 |
| R7.3 | se fusiona en R4.2 | 1 | 2 | 0 | 0 |
| R7.4 | se fusiona en R7.1 | 1 | 0 | 0 | 0 |
| R7.5 | se retira | 0 | 0 | 0 | 0 |
| R3.3 | se retira | 0 | 0 | 0 | 0 |
| R16.2 | se fusiona en R13.3 | 0 | 0 | 0 | 0 |
| R32.3 | se fusiona en R16.1 | 0 | 0 | 0 | 0 |
| R34.2 | se fusiona en R34.1 | 1 | 0 | 0 | 0 |
| R34.5 | se fusiona en R34.1 y R34.3 | 0 | 2 | 0 | 1 |
| R34.7 | se fusiona en R34.6 | 0 | 1 | 0 | 2 |
| R34.8 | se fusiona en R34.9 | 0 | 2 | 1 | 2 |
| R35.3 | se fusiona en R35.2 | 0 | 0 | 0 | 0 |
| R35.6 | se fusiona en R13.3 | 0 | 0 | 0 | 0 |
| R36.2 | se fusiona en R36.1 | 0 | 0 | 0 | 2 |
| R36.3 | se fusiona en R36.1 | 0 | 0 | 0 | 2 |
| R36.6 | se fusiona en R36.5 | 0 | 0 | 0 | 0 |
| R38.3 | se fusiona en R29.1 | 1 | 0 | 0 | 0 |
| R38.5 | se fusiona en R5.6 | 0 | 2 | 0 | 0 |
| R19.2 | se retira | 0 | 0 | 0 | 0 |
| R19.4 | se fusiona en R19.3 | 0 | 0 | 0 | 0 |
| R26.2 | se fusiona en R26.1 | 0 | 3 | 0 | 0 |
| R27.2 | se fusiona en R27.1 | 0 | 0 | 0 | 3 |
| R41.1 | se fusiona en R41.3 | 0 | 2 | 0 | 0 |
| R14.1 | se fusiona en R7.1 | 1 | 0 | 0 | 2 |
| R14.2 | se fusiona en R4.2 | 1 | 0 | 0 | 0 |
| R17.3 | se retira | 0 | 0 | 0 | 0 |
| R6.2 | se fusiona en R13.1 | 0 | 0 | 0 | 0 |
| R6.4 | se retira | 0 | 0 | 0 | 0 |
| R6.6 | se fusiona en R13.1 | 0 | 0 | 0 | 0 |
| R13.2 | se fusiona en R13.1 | 1 | 0 | 0 | 1 |
| **Total** | | **12** | **24** | **2** | **19** |

### A.7. Las tres interfaces

Criterio de conteo: "una" es una sola definición en un criterio; "más de una" es la misma semántica escrita en dos o más criterios; "ninguna" es que ningún criterio la escribe (está sólo en la prosa, en otro archivo o en ninguna parte). La columna "lado" dice si la definición está escrita del lado del documento o como obligación del Player: los elementos definidos una sola vez pero del lado del Player son los que la reestructura tiene que dar vuelta aunque no estén duplicados.

| Interfaz | Elementos | Definidos una vez | Más de una | Ninguna | De los "una vez", sólo del lado del Player |
|---|---:|---:|---:|---:|---:|
| I-MPD | 28 | 13 | 12 | 3 | 4 |
| I-REQ | 16 | 10 | 5 | 1 | 3 |
| I-RES | 32 | 17 | 13 | 2 | 2 |
| **Total** | **76** | **40** | **30** | **6** | **9** |

#### I-MPD (28 elementos: 13 una vez, 12 más de una, 3 ninguna; de los definidos una vez, 4 lo están sólo del lado del Player)

| # | Elemento | Dónde está hoy la semántica | Veces | Lado | Dónde queda |
|---:|---|---|---|---|---|
| 1 | Familia de la ventana (scheme overlay o pause-trigger) | ninguno en 03; los schemes los nombra 06 | ninguna | - | R40.9 (nuevo) dice qué es una ventana de cada familia |
| 2 | Rango temporal de una ventana overlay o squeezeback | sólo la prosa de R40 ("What a non-linear ad is anchored to") | ninguna | - | R40.9 (nuevo) |
| 3 | Rango de una ventana de pausa | R31.1 | una | Player | R31.1 reescrito del lado del documento |
| 4 | Máximo de un slot overlay o pausa | R4.1; R4.2, R4.3, R7.3 y R14.2 lo repiten como cota | más de una | doc + Player | R4.1 (qué es) y R4.2 (política de corte) |
| 5 | `@maxDuration` de un evento lineal heredado | R4.1 y R4.8 | más de una | doc | R4.8 (R4.1 remite) |
| 6 | `@maxDuration` igual a cero | R4.7 | una | doc | R4.7 |
| 7 | `@clip` del reemplazo lineal | R4.3 y R4.6 | más de una | Player | R4.6 reescrito del lado del documento |
| 8 | Sobre qué línea de tiempo se mide el tope | R4.11 y R19.3 | más de una | Player | R4.11 reescrito |
| 9 | El tope no acota un slot de pausa | R31.2 | una | doc | R31.2 |
| 10 | `@allowedLayouts` presente: qué admite | sólo como chequeo: R5.6 (b) y R38.5 | más de una | Player | R38.1 reescrito (presente y ausente) |
| 11 | `@allowedLayouts` ausente: default de la familia | R38.1 | una | doc | R38.1 |
| 12 | Vocabulario de tokens | R12.2 (R12.1 lo gobierna) | una | doc | R12.2 |
| 13 | Qué composición denota cada token (región del contenido, superficie de pausa) | tabla en la prosa de R12, R21.1, R26.2, R27.2 (y el límite IAB en R12.4) | más de una | Player | R12.5 (nuevo) |
| 14 | Región custom | R39.2 | una | doc | R39.2 |
| 15 | Once-per-session (overlay, squeezeback y pausa) | R34.1, R34.2 y R34.5 | más de una | doc + Player | R34.1 |
| 16 | Cuándo se consume la ventana once-per-session | R34.3 y la última frase de R34.5 | más de una | Player | R34.3 (se queda como comportamiento) |
| 17 | `@earliestResolutionTimeOffset` (offset, ancla, default) | R36.1, R36.2 y R36.3 | más de una | doc + Player | R36.1 |
| 18 | Permiso de audio del aviso en la ventana | R41.2 | una | doc | R41.2 |
| 19 | Relación con el evento lineal (default, con su suspensión y reanudación; supersede; on top): qué significa | prosa de R40; R40.4, R40.3 y R40.5, uno por relación | una | Player | R40.9 (nuevo); R40.3 a R40.5 quedan con lo que no se deduce |
| 20 | Relación: opcional, una sola, pausa sólo on top | R40.1 | una | doc | R40.1 |
| 21 | Ventanas declaradas en el MPD de una alternativa | R40.2 y R40.6 | más de una | doc + Player | R40.2 (lugar) y R40.6 (recursión) |
| 22 | Un solo `EventStream` por familia y Period | R20.2 | una | doc | R20.2 |
| 23 | Pedido de la métrica `PlayList` (`Metrics`) | R33.4 | una | doc | R33.4 |
| 24 | `@skipAfter` de un evento lineal heredado | R35.8 | una | Player | R35.8 reescrito del lado del documento |
| 25 | `@executeOnce` ante una resolución vacía | R30.2 | una | Player | R30.2 (comportamiento del contador de la base) |
| 26 | `@value` en un `EventStream` SGAI | ninguno en 03; lo fija 06 | ninguna | - | queda en 06 (es HOW) |
| 27 | Ejecuciones de una ventana overlay o squeezeback (cada entrada del playhead es una ejecución que se resuelve de nuevo) | R34.6 y R34.7 | más de una | Player | R34.6 reescrito del lado del documento |
| 28 | Ejecución tardía: default desde el primer candidato y declaración de offset | R34.8 y R34.9 | más de una | Publisher + Player | R34.9 reescrito |

#### I-REQ (16 elementos: 10 una vez, 5 más de una, 1 ninguna; de los definidos una vez, 3 lo están sólo del lado del Player)

| # | Elemento | Dónde está hoy la semántica | Veces | Lado | Dónde queda |
|---:|---|---|---|---|---|
| 1 | URL del evento (`@uri`) a la que se pide | R18.1 | una | gobierno | R18.1 |
| 2 | Transporte: query parameters, no el template de URL del MPD | sólo la prosa de R29; R38.3 dice "for example, a query parameter" | ninguna | - | R29.1 reescrito |
| 3 | `sgai-video-decoders` | R29.1 | una | doc | R29.1 |
| 4 | `sgai-image-over-video` | R29.1 | una | doc | R29.1 |
| 5 | `sgai-html-over-video` | R29.1 | una | doc | R29.1 |
| 6 | `sgai-custom-layout` | R29.1 | una | doc | R29.1 |
| 7 | `sgai-ad-audio` | R29.9, fuera de la tabla de R29.1 | una | doc | R29.1 (quinta fila) |
| 8 | Layouts permitidos reenviados | R38.2, R38.3 y R29.8; sin nombre de parámetro y fuera de la lista cerrada de R29.1 | más de una | Player + doc | `sgai-allowed-layouts`, fila de R29.1 (D-13); R38.2 queda como obligación de reenviar |
| 9 | Región custom reenviada | R39.3 y R29.8; sin nombre de parámetro | más de una | Player + doc | `sgai-custom-region`, fila de R29.1 (D-13); R39.3 queda |
| 10 | Permiso de audio reenviado | R41.5 y R29.8; sin nombre de parámetro | más de una | Player + doc | `sgai-ad-audio-allowed`, fila de R29.1 (D-13); R41.5 queda |
| 11 | Opcionalidad de los parámetros | R29.2 y R29.8 | más de una | Player + doc | R29.2 |
| 12 | Ausencia significa indeterminado | R29.7 | una | doc | R29.7 |
| 13 | Omitir en lugar de mandar vacío | R29.3 | una | Player | R29.3 |
| 14 | Parámetros no reservados llevan prefijo de vendor | R29.4 | una | Player | R29.4 |
| 15 | El valor es la capacidad real en la sesión | R29.10 | una | Player | R29.10 |
| 16 | Clase de dispositivo (derivada, no viaja) | R29.6 y la tabla de la prosa de R3 | más de una | doc | R3.1 reescrito |

#### I-RES (32 elementos: 17 una vez, 13 más de una, 2 ninguna; de los definidos una vez, 2 lo están sólo del lado del Player)

| # | Elemento | Dónde está hoy la semántica | Veces | Lado | Dónde queda |
|---:|---|---|---|---|---|
| 1 | Familia del documento frente a la del slot | R20.4 | una | Player | R20.4 |
| 2 | Documento sin candidatos | R30.1 | una | doc | R30.1 |
| 3 | Orden de los candidatos | R7.1, R7.4 y R14.1 | más de una | Player | R7.1 reescrito del lado del documento |
| 4 | Opciones de un candidato y su orden de preferencia | R5.1 y R5.5; R5.2 y R5.6 lo repiten | más de una | doc + Player | R5.1 |
| 5 | Qué representan las opciones (formatos que el anunciante permite) | R5.8 | una | doc | R5.8 |
| 6 | `@layout` de la opción y metadatos de tipo de aviso: vocabulario | R12.3 (la semántica del token es la de la fila I-MPD de tokens) | una | doc | R12.3 y R12.5 |
| 7 | Forma y mimeType del creativo | R15.2 | una | doc | R15.2 |
| 8 | URL de un asset no AV | R24.1 | una | doc | R24.1 |
| 9 | Duración declarada de una forma | R19.3 y R19.4 (timebase en R4.9) | más de una | Player | R19.3 reescrito |
| 10 | Rectángulo de una opción `custom` | R39.4; R39.5 repite que debe caer dentro | más de una | doc + Player | R39.4 |
| 11 | Fondo del double-box | R26.1 y R26.2; "sólo imagen" y "negro por defecto" en la prosa | más de una | doc + Player | R26.1 reescrito |
| 12 | Creativo del L-shape y del frame | R27.1 y R27.2; que vale para `squeezeback-frame` sólo en la prosa | más de una | doc + Player | R27.1 reescrito |
| 13 | Audio declarado en la opción | R41.1 (default), R41.3 (declaración), R41.4 (efecto) | más de una | doc + Player | R41.3 reescrito; R41.4 sólo la restauración |
| 14 | Carrier de los beacons con tiempo | R6.2 (SHOULD), R13.1 (MUST) y R13.4 (mandatory) | más de una | doc + gobierno | R13.1, MUST (D-14); R13.4 queda como gobierno |
| 15 | Ancla temporal y disparo de los beacons con tiempo | R6.6, R13.1 y R13.2 | más de una | doc + Player | R13.1 |
| 16 | Alcance de `@id` de un beacon | R6.5 | una | Player + doc | R6.5 reescrito del lado del documento |
| 17 | Beacons adjuntos a una opción o al candidato | R13.6 | una | Player + doc | R13.6 reescrito del lado del documento |
| 18 | Beacons de inicio y fin de slot, por ejecución | R13.7 | una | Player + doc | R13.7 reescrito del lado del documento |
| 19 | Beacons por ocurrencia (incluida la falla de R5.9) | R42.1 y R42.3; R5.9 repite el caso de la falla | más de una | doc + Player | R42.1 (R42.3 queda como garantía, D-7) |
| 20 | Beacons de viewability | R47.1 y R47.2 | más de una | doc + Player | R47.1 (R47.2 queda como garantía, D-7) |
| 21 | Carrier del ClickThrough y su click-tracking | R28.1 | una | doc | R28.1 |
| 22 | Click-tracking disparado al activar | R28.2 | una | Player | R28.1 (semántica) y R28.2 (garantía) |
| 23 | Qué significa activar el ClickThrough respecto de su URL de destino | ninguno | ninguna | - | R28.1, con el modelo de R48.3 (D-16) |
| 24 | Cerrable o no | R35.1 | una | doc | R35.1 |
| 25 | Demora antes de poder cerrar | R35.2 y R35.3 | más de una | doc + Player | R35.2 |
| 26 | Comportamiento al agotar la pausa: declaración y default | R32.1 | una | doc + Player | R32.1 |
| 27 | Qué significa `repeat`, `request-again` y `stop` | sólo la lista de la prosa de R32 | ninguna | - | R32.1 reescrito |
| 28 | Validez de la resolución (por defecto, la ejecución para la que se obtuvo) | R36.4, R36.5, R36.6 y R34.7 | más de una | doc + Player | R36.4 |
| 29 | Metadatos de aplicación (`AdSystem`, `AdTitle`) | R23.1 | una | doc | R23.1 |
| 30 | Identificadores del creativo | R23.2 | una | doc | R23.2 |
| 31 | Recursos de verificación | R44.1 | una | doc | R44.1 |
| 32 | Divulgación regulatoria | R48.1 | una | doc | R48.1 |

Conteo de las tres tablas, por script sobre sus filas:

```
I-MPD 28 {'una': 13, 'más de una': 12, 'ninguna': 3} una-Player 4
I-REQ 16 {'una': 10, 'más de una': 5, 'ninguna': 1} una-Player 3
I-RES 32 {'una': 17, 'más de una': 13, 'ninguna': 2} una-Player 2
```

### A.8. Lo que no se pudo determinar

- La lista de elementos de A.7 es del inventario: salió de 03 y de 06,
  porque ninguna parte de `context/` enumera los elementos de cada interfaz.
  Los números valen para esa lista. Otra partición (por ejemplo, separar el
  offset en valor, ancla y default) cambia los conteos, aunque no cuáles
  elementos están duplicados o faltan.
- Que las 45 menciones de 04, 99 y las ADRs sigan teniendo sentido con el id
  destino no se verificó una por una. Se ve al reescribirlas, y la
  validación de 04 y 99 (D-12) lo controla para esos dos archivos.
