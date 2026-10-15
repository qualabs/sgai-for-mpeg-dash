---
description: "Reescribir context/03-requirements.md para que la semántica de cada interfaz se escriba una sola vez, del lado del documento, y cerrar con una v13 mayor."
status: designing
origin: "Nicolás, 2026-09-28, abierta como fase 06 en diseño (de output-analysis/v12.6-requirements-redundancy-review.md); phase 06, returned to the roadmap 2026-10-15"
---

# Fase 06: el documento primero

Diseño de la fase. Lo revisa Nicolás antes de que se escriban `PHASE.md`,
`TASKS.md` y las ADRs, y antes de tocar `context/`.

## Para qué es esta fase

Hoy `context/03-requirements.md` escribe muchos hechos dos veces: una vez
como lo que declara el Publisher o lleva el APS, y otra vez como lo que el
Player hace cuando lo encuentra. La fase reescribe 03 para que la semántica
de cada interfaz esté escrita una sola vez, del lado del documento, y el
comportamiento de un actor aparezca sólo donde no se deduce de esa
semántica. La fase termina con una v13 mayor, construida una sola vez sobre
el `context/` reescrito.

## Por qué: así está escrita la base

El análisis de `output-analysis/v12.6-requirements-redundancy-review.md`
leyó la copia primaria de ISO/IEC 23009-1:2026. Lo que importa para esta
fase:

- **La base dice de sí misma que especifica documentos.** *"This document
  primarily specifies formats for the Media Presentation Description and
  Segments"* (§1). *"However, this document does not provide a normative
  specification for such a client"* (§4.1). El modelo de cliente es
  *"the informative client model"* (§4.2), y los perfiles *"merely specify
  restrictions on MPD and Segments rather than DASH Client behaviour"*
  (§8.1).
- **Casi todas sus obligaciones tienen por sujeto el documento.** De 1069
  modales (`shall` y `should`), 1029 tienen por sujeto un construct del
  documento, 35 al cliente y 5 al autor. Una muestra al azar de 25 del
  primer grupo dio 25 restricciones sobre el documento.
- **La semántica se escribe como efecto del documento, sin actor.** La
  tabla de `@maxDuration` dice *"it shall be terminated at the end of this
  duration"* y *"If the value of @maxDuration is zero, the event is not
  executed"* (Table 63). No dice que el autor lo declara ni que el cliente
  lo termina.
- **Donde hace falta comportamiento, es una garantía para el autor.** *"The
  MPD author may assume that the steps described in this subclause are
  taken, while the client implementer may provide any functionally
  equivalent implementation"* (§5.16.2.2.1). En todo §5.16.2.2 hay un solo
  modal, y es sobre el documento.
- **La base no escribe el mismo hecho dos veces.** Lo que se repite es una
  capa de derivación (la tabla de semántica, la variable de la Table 57 y
  el modelo que opera sobre ella), y la tabla remite al modelo en lugar de
  repetirlo: *"For details see the definition of APDmax in Table 57"*.

La conclusión es que el documento funciona como la interfaz, y que lo que
hace cada actor queda obvio a partir de él. 03 está escrito al revés: de sus
191 criterios, 89 son del Player.

## Por qué antes del build

Correr la v12.7 ahora gastaría un build completo en una estructura que ya se
sabe que va a cambiar, y el build siguiente tendría que volver a validarla
entera. Además, el camino incremental no protege una reescritura: la
comparación de degradación de `check-incremental` saltea las unidades que el
delta tocó, así que no miraría justo los 77 criterios que cambian. Hacer la
reestructura primero y validarla a nivel de `context/`, comparando la
versión vieja con la nueva, deja una sola corrida al final sobre una
entrada estable.

## Decisiones

### D-1. La v12.7 no se corre; la fase termina en una v13 mayor

Los cambios de `context/` hechos desde la v12.6 (R41, R42, R44, R47, R48,
F-2, F-3, D-1 y R29) y la reestructura entran juntos en una sola corrida
mayor al final de la fase. Mezclar el delta de fondo con la reestructura
hace que la comparación de la v13 contra lo publicado no pueda separar un
cambio del otro. Se acepta por dos razones. La protección de la
reestructura no depende del build: se hace antes, sobre `context/`, con el
mapa de obligaciones (D-9). Y el delta de fondo ya está registrado decisión
por decisión en el `LOG.md`.

### D-2. El documento se define como tres interfaces

- **I-MPD, lo que el Publisher escribe en el MPD:** las ventanas no
  lineales, su familia, su rango, su tope, sus layouts y región admitidos,
  su relación con los eventos lineales, su offset de resolución anticipada,
  su declaración de una vez por sesión y el permiso de audio; y los
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
escrita una vez. El inventario (Anexo A, sección 5) cuenta hoy 74
elementos. De esos, 27 están definidos más de una vez, 6 no tienen
definición en ningún criterio y 10 están definidos una sola vez pero como
obligación del Player.

| Interfaz | Elementos | Una vez | Más de una | Ninguna | Una vez, sólo del lado del Player |
|---|---:|---:|---:|---:|---:|
| I-MPD | 26 | 14 | 9 | 3 | 5 |
| I-REQ | 16 | 10 | 5 | 1 | 3 |
| I-RES | 32 | 17 | 13 | 2 | 2 |
| Total | 74 | 41 | 27 | 6 | 10 |

La lista de elementos es del inventario, porque `context/` no enumera los
elementos de ninguna interfaz. Enumerarlos es parte de lo que la fase
produce (D-5).

Los casos de uso de 04 son la guía de cómo cada actor usa las interfaces.
No definen semántica.

### D-3. La semántica de un elemento se escribe una vez, en un criterio del lado del documento

Cada elemento de una interfaz tiene su significado en un único criterio, con
el rol de quien lo escribe (Publisher, APS o spec document). El significado
incluye el efecto, escrito como lo escribe la base: "an option that declares
its audio is heard in place of the primary content's", y no "when the option
declares its audio, the Player MUST render it". Otros criterios y los casos
de uso lo citan por su id y no lo repiten.

La semántica que hoy vive sólo en la prosa sube a un criterio. Son nueve
requerimientos: R3, R12, R26, R27, R28, R29, R31, R32 y R40 (Anexo A,
sección 2). Esto agrega dos criterios, R12.5 (qué composición denota cada
token de layout) y R40.9 (a qué se ancla una ventana y qué significa cada
relación). Hay que subirla porque `check-promotable` sólo recorre criterios
y modales de la prosa, y una semántica que está en una tabla de la prosa no
entra en la validación.

### D-4. El comportamiento de un actor se escribe sólo cuando no se deduce

Un criterio sobre lo que hace un actor se queda cuando dice algo que la
semántica del documento no alcanza. Las clases que el recorrido encontró:

- un orden, o qué se prueba primero;
- un fallback: qué pasa cuando algo no se puede;
- qué hacer ante un documento que falla, falta o no es conforme;
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

### D-6. La estructura de los archivos de `context/` no cambia en esta fase

El orden 00 a 08 y 99 sigue como está. Revisado contra la convención:

- 02, 03 y 04 ya siguen el orden actores, requerimientos y casos de uso.
- 06 es el cómo, y no se toca salvo sus citas a ids.
- 05 describe la interfaz lineal de base con el mapeo VAST, y se superpone
  con I-RES en lo lineal. Queda como pregunta abierta (P-6), no como
  cambio de esta fase.

### D-7. Dos excepciones de fondo: R28.2 y R20.5/R20.6

- **R28.2 queda.** R28.1 recibe la semántica: el click-tracking se dispara
  cuando el espectador activa el ClickThrough. R28.2 queda como garantía
  explícita, porque R28 existe para que *"every Player conformant to this
  specification reads them the same way"*. Esa frase es una promesa sobre
  los Players y no sobre el documento. Si se deduce, deja de ser una
  promesa.
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
>    specification document), including its effect. Every other criterion,
>    and every use case, cites it by identifier and does not restate it.
> 2. A criterion on what an actor does is written only when it does not
>    follow from the meaning of what the document carries: an order, a
>    fallback, what to do when something fails, is missing or does not
>    conform, a device limit, a computation, when something happens, a
>    chain between actors, or a guarantee of interoperability that has to
>    be stated to hold.
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
  compara los ids contra el commit de la v12.6.

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

Hay 9 menciones en las ADRs 0011, 0014 y 0018 a ids que se retiran (R5.7,
R27.2, R36.2 y R36.3). Las ADRs aceptadas son registro. La tabla de
retirados resuelve esas citas sin editarlas, así que no llevan nota.

### D-12. Un agente reescribe y otro valida, contra el mapa de obligaciones

La ejecución se reparte en cuatro tareas:

1. **El mapa.** El Anexo A, sección 1, es el mapa de obligaciones: cada id
   viejo, su acción y su lugar nuevo. Se congela como evidencia de la fase
   antes de reescribir.
2. **La reescritura**, por una sesión o un agente: 03 según el mapa, la
   sección "Interfaces", la regla, la tabla de retirados, y las 20
   menciones de 04 y 99 a ids que se van. Además, las 10 referencias
   internas de 03 a esos ids.
3. **El check** de D-9, con su prueba de que falla.
4. **La validación**, por otro agente que no reescribió, con la versión
   vieja (el commit anterior a la reescritura) y la nueva:
   - **Que cada obligación siga estando.** Por cada modal de cada unidad
     vieja (criterio o prosa), el lugar nuevo del mapa tiene que tener esa
     obligación, con la misma fuerza. Un script lista los pares y el
     validador los lee; el script no juzga significado. La prueba del
     instrumento: se borra a propósito una obligación del texto nuevo, y el
     validador la tiene que encontrar.
   - **Que no queden dobles:** los 9 redundantes, los 14 parciales y los 6
     grupos del mismo actor del análisis, uno por uno.
   - **Que las tres interfaces estén completas:** los 74 elementos del
     inventario tienen una fila en el índice, y los 6 sin definición la
     tienen.
   - **Que `context/` siga cerrando:** `check-context-coherence`,
     `check-context-vocabulary` y el check nuevo, todos en `0`.

**Qué se hace con los checks que no protegen una reescritura:**

- `check-incremental degradation` no aplica: la v13 es mayor. Su función
  (que no se pierda lo que había) la cumple la validación de la tarea 4.
- La población de `check-promotable` baja de 191 a 157 criterios y cambia
  en las unidades de prosa, porque la semántica que estaba en la prosa sube
  a criterios. Eso es correcto, siempre que cada unidad que sale figure en
  el mapa con su destino. Se deja escrito en la evidencia: población vieja,
  población nueva y la diferencia explicada por el mapa.

Recién con la tarea 4 en verde se corre la v13, una sola vez, y se promueve
con el criterio de siempre.

## Impacto fuera de 03

- **04:** 19 menciones a ids que se van (R5.7, R5.2, R26.2, R7.3, R38.5,
  R41.1 y R5.5), que se reescriben al id nuevo. Los casos de uso no cambian
  de contenido.
- **99:** 1 mención (R29.9), que se reescribe.
- **06:** 0 menciones a ids que se van. Las citas a R13.6, R13.7, R35.2 y
  R41.2 siguen valiendo.
- **02, 05, 07 y 08:** 0 menciones.
- **ADRs:** 9 menciones, que no se editan (D-11).

## Qué no se hace en esta fase

- **Decisiones de fondo nuevas.** Donde la reescritura encuentra una
  ambigüedad, la anota como pregunta y no la resuelve.
- **Renumerar archivos de `context/`**, o mover requerimientos entre
  secciones de 03.
- **Cambiar 05, 06, 07 u 08**, salvo citas a ids.
- **Editar ADRs.**
- **Correr un build** antes de que la validación esté en verde.
- **Renombrar parámetros o atributos.** Si algo necesita nombre, es una
  pregunta (P-1).

## Preguntas abiertas, cada una con recomendación

### P-1. Tres parámetros reservados no tienen nombre y la lista de R29.1 los excluye

R29.1 dice "the four below and the audio parameter of R29.9, and no others".
Pero los layouts permitidos (R38), la región custom (R39) y el permiso de
audio (R41.5) también son parámetros reservados, R38.3 lo dice, y no
tienen nombre en `context/`. La contradicción la introdujo el cambio de R29
de hoy.

**Recomendación:** R29.1 con dos tablas, la de capacidad y la de lo que el
slot declara. Los nombres de las dos primeras se toman de la spec publicada
(`sgai-allowed-layouts` y `sgai-custom-region`), y para el permiso de audio
se usa `sgai-ad-audio-allowed`. Es una decisión de nombres, y es de
Nicolás.

### P-2. El carrier de los beacons con tiempo es SHOULD en R6.2 y MUST en R13.1

La fusión en R13.1 obliga a elegir uno. **Recomendación:** MUST, que es lo
que ya dicen R13.1 y R13.4 (*"mandatory"*). R6.3 sigue siendo la salida para
lo que el callback no puede expresar.

### P-3. Qué significan los dos tokens de double-box respecto del fondo

R26 dice que el fondo es opcional, y hay dos tokens:
`squeezeback-double-box` y `squeezeback-double-box-background`. No está
dicho si el primero puede llevar fondo, ni si el segundo puede no llevarlo.
**Recomendación:** el token dice la composición. `-background` lleva fondo,
y el otro no lo lleva.

### P-4. Qué hace el Player con la URL de destino del ClickThrough

Ningún criterio lo dice: sólo que dispara el click-tracking.
**Recomendación:** el mismo modelo de R48.3. El Player hace disponible el
destino por los medios de su dispositivo, y cómo es suyo.

### P-5. ¿R42.3 y R47.2 son garantías como R28.2?

El inventario los fusiona en R42.1 y R47.1. Tienen la misma forma que
R28.2, y la misma razón: son carriers nuevos que un Player legacy ignora.
**Recomendación:** conservarlos como garantías, igual que R28.2, por
coherencia. Cuesta dos criterios.

### P-6. 05 se superpone con I-RES en lo lineal

05 mapea VAST al List MPD, que es I-RES para el caso lineal.
**Recomendación:** no tocarlo en esta fase. Ver en la fase siguiente si
pasa a ser el anexo ilustrativo de R11.5.

### P-7. La derivación del intervalo de pausa de R33 está sólo en la prosa

No es de ninguna de las tres interfaces, pero tiene el mismo patrón que D-3.
**Recomendación:** incluirla en la reestructura. Sube a R33.2 y no cambia
de contenido.

## Anexo A. Inventario criterio por criterio

El inventario lo produjo un agente sobre `context/03-requirements.md` en el
commit `b9c6276`. Lo verifiqué: la tabla tiene 191 filas, con los mismos ids
y en el mismo orden que el archivo, y las acciones suman 114 que quedan, 41
que se reescriben, 30 que se fusionan y 6 que se retiran. Con los dos
criterios nuevos, 03 pasa a tener 157. Los números difieren de los del
análisis v12.6 (11 borrados y 36 reescritos) porque acá cada criterio
absorbido cuenta como fusionado, y porque el recorrido se rehizo sobre el
archivo actual.


Alcance: `context/03-requirements.md` en `b9c6276`, leído entero. Trabajo de sólo lectura: no se editó ni se commiteó nada del repo. Base del análisis: `output-analysis/v12.6-requirements-redundancy-review.md`, aplicado sobre el archivo actual (R29 ya enumera parámetros, R29.1 tiene cuatro filas, R29.9 es el audio y R3 tiene la tabla de clases).

**Cómo leer la columna "acción".** *Queda*: el texto no cambia de fondo. *Se reescribe*: el id se conserva y su texto cambia, porque absorbe a otro o porque pasa a escribir la semántica del lado del documento. *Se fusiona en X*: su contenido tiene que aparecer en X, y el id queda retirado. *Se retira*: no hay nada que mover, porque otro criterio ya lo dice entero, y el id queda retirado. En los dos últimos casos el id no se reasigna.

**Resultado en una línea.** De 191 criterios, 114 quedan, 41 se reescriben, 30 se fusionan y 6 se retiran; se agregan 2 criterios nuevos (R12.5 y R40.9), así que 03 pasaría a tener 157. Hay 29 menciones fuera de 03 que apuntan a un id que se va: 19 en 04, 1 en 99 y 9 en ADRs aceptadas.

### A.1. Tabla de criterios

Conteo de criterios:

```
$ grep -cE '^\s*- \*\*R[0-9]+\.[0-9]+\*\* \(' context/03-requirements.md
191
```

La tabla tiene 191 filas, en el orden del archivo. Las citas son el conteo de `grep -oP '\bR<n>\.<m>(?![0-9])'` en `04-use-cases.md`, `06-naming-and-namespaces.md`, `99-glossary.md`, `02-actors.md`, `05-dash-linear-interfaces.md`, `07-backward-compat-checklist.md`, `08-dash-extension-rules.md` y la concatenación de `.project/decisions/*.md`, en ese orden.

| # | id | rol actual | interfaz | acción | lugar nuevo | citas: 04 / 06 / 99 / 02 / 05 / 07 / 08 / ADR |
|---:|---|---|---|---|---|---|
| 1 | R1.1 | spec document | gobierno | queda | R1.1, sin cambios. | 0 / 2 / 0 / 0 / 0 / 1 / 0 / 0 |
| 2 | R1.2 | Publisher / spec document | gobierno | queda | R1.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 1 / 2 / 0 |
| 3 | R1.3 | Publisher / spec document | gobierno | queda | R1.3, sin cambios. | 0 / 1 / 0 / 0 / 0 / 0 / 0 / 1 |
| 4 | R1.4 | Player | comportamiento | queda | R1.4, sin cambios: abortar ante una falla en tiempo de ejecución no se deduce del documento. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 5 | R1.5 | spec document | gobierno | queda | R1.5, sin cambios. | 0 / 2 / 0 / 0 / 1 / 0 / 0 / 8 |
| 6 | R1.6 | Player | comportamiento | queda | R1.6, sin cambios. | 3 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 7 | R2.1 | Publisher | I-MPD | queda | R2.1, sin cambios: fija que las restricciones del slot viven en el MPD. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 8 | R2.2 | ADS + APS | gobierno | queda | R2.2, sin cambios (reparto de roles entre ADS y APS). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 9 | R2.3 | Player | comportamiento | queda | R2.3, sin cambios: el Player es quien hace cumplir las restricciones; R5.6 es su instancia. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 10 | R2.4 | spec document | gobierno | queda | R2.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 11 | R11.1 | spec document | gobierno | queda | R11.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 12 | R11.2 | Player | comportamiento | queda | R11.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 13 | R11.3 | spec document | gobierno | queda | R11.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 14 | R11.4 | spec document | gobierno | queda | R11.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 15 | R11.5 | spec document | gobierno | queda | R11.5, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 16 | R18.1 | spec document | gobierno | queda | R18.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 17 | R18.2 | Publisher / APS / ADS | gobierno | queda | R18.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 18 | R29.1 | spec document | I-REQ | se reescribe | R29.1: una sola tabla con todos los parámetros del pedido y su significado: los cuatro de capacidad, `sgai-ad-audio` (de R29.9) y los tres que reenvían declaraciones del slot (layouts permitidos, región custom, permiso de audio, hoy en R38.3); viajan como query parameters y no por el template de URL del MPD (hoy sólo en la prosa). | 3 / 0 / 1 / 0 / 0 / 0 / 0 / 1 |
| 19 | R29.2 | Player | I-REQ | se reescribe | R29.2: todo parámetro reservado es opcional, salvo los que el slot declara, que R38.2, R39.3 y R41.5 obligan a enviar (absorbe R29.8). | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 20 | R29.3 | Player | I-REQ | queda | R29.3, sin cambios (omitir, no mandar vacío). | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 21 | R29.4 | Player | I-REQ | queda | R29.4, sin cambios (prefijo de vendor). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 22 | R29.5 | APS | comportamiento | queda | R29.5, sin cambios (el APS tolera la ausencia). | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 23 | R29.6 | spec document | gobierno | se fusiona en R3.1 | R3.1 dice que las clases son las combinaciones de los tres primeros ejes de R29.1 que da la tabla de R3, y que una combinación sin nombre se declara igual. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 24 | R29.7 | spec document | I-REQ | queda | R29.7, sin cambios (ausencia = indeterminado). | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 25 | R29.8 | spec document | I-REQ | se fusiona en R29.2 | R29.2 nombra las tres excepciones a la opcionalidad. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 26 | R29.9 | spec document | I-REQ | se fusiona en R29.1 | R29.1 lleva `sgai-ad-audio` como quinta fila de la tabla de capacidad. | 0 / 0 / 1 / 0 / 0 / 0 / 0 / 0 |
| 27 | R29.10 | Player | I-REQ | queda | R29.10, sin cambios: dice qué significa el valor declarado (la capacidad real en esa sesión). | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 28 | R4.1 | Publisher | I-MPD | se reescribe | R4.1: todo slot overlay y pausa declara un máximo, y el máximo es la cota que la presentación del slot no pasa, con lo que acota cada familia en R4.2, R4.6 y R31.2 (absorbe R4.3); en un evento lineal heredado es `@maxDuration`, opcional (R4.8). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 8 |
| 29 | R4.2 | Player | comportamiento | se reescribe | R4.2: donde el tope acota duración acumulada (overlay, secuencia no lineal, inserción lineal), el Player corta en el tope aunque caiga a mitad de aviso, y una duración declarada no es razón para descartar un candidato (absorbe R7.3 y R14.2). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 30 | R4.3 | Player | I-MPD | se fusiona en R4.1 y R4.6 | R4.1 recibe "no se pasa de la cota"; R4.6 recibe el caso `@clip="false"`. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 31 | R4.4 | ADS | gobierno | queda | R4.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 32 | R4.5 | Player | comportamiento | queda | R4.5, sin cambios (medir contra la duración real); absorbe R7.5, que la repetía. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 33 | R4.6 | Player | I-MPD | se reescribe | R4.6 pasa a ser semántica del documento: en un reemplazo lineal el tope acota el fin programado según `@clip` de la base (default `true`), y con `@clip="false"` termina en PRTA + APDmax, que es la base moviendo la cota; la inserción no tiene `@clip`. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 34 | R4.7 | Publisher + Player | I-MPD | queda | R4.7, sin cambios (ya está escrita como efecto del documento). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 35 | R4.8 | spec document | I-MPD | queda | R4.8, sin cambios. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 4 |
| 36 | R4.9 | Player | comportamiento | queda | R4.9, sin cambios (conversión de timescale con redondeo hacia arriba). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 37 | R4.10 | Player | comportamiento | queda | R4.10, sin cambios (slot defectuoso). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 8 |
| 38 | R4.11 | Player | I-MPD | se reescribe | R4.11 como semántica del tope: se mide sobre la línea de tiempo de presentación, y un intervalo en que esa línea no avanza no cuenta (absorbe la parte de tope de R19.3). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 39 | R31.1 | Player | I-MPD | se reescribe | R31.1 como semántica de la ventana de pausa: una pausa del espectador que empieza dentro de la ventana dispara el pedido de resolución, y una que empieza fuera de toda ventana no dispara ninguno. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 40 | R31.2 | Publisher + Player | I-MPD | queda | R31.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 41 | R12.1 | spec document | gobierno | queda | R12.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 42 | R12.2 | Publisher | I-MPD | queda | R12.2, sin cambios (vocabulario cerrado de `@allowedLayouts`). | 1 / 2 / 0 / 0 / 0 / 0 / 0 / 1 |
| 43 | R12.3 | APS | I-RES | queda | R12.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 44 | R12.4 | spec document | I-MPD | queda | R12.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 45 | R15.1 | spec document | gobierno | queda | R15.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 46 | R15.2 | APS + Publisher | I-RES | queda | R15.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 47 | R15.3 | Player | comportamiento | queda | R15.3, sin cambios (tolerancia ante un documento no conforme). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 48 | R5.1 | APS | I-RES | se reescribe | R5.1: opciones como lista ordenada donde el orden de documento es la preferencia, lo que significa que se presenta la primera que el Player puede satisfacer (absorbe R5.2 y R5.5). | 3 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 49 | R5.2 | Player | comportamiento | se fusiona en R5.1 | R5.1 dice que el orden es la preferencia y qué implica; los chequeos quedan en R5.6. | 3 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 50 | R5.3 | Player | comportamiento | se reescribe | R5.3: un candidato sin opción que pase R5.6 se saltea y se sigue con el siguiente en orden; agotados, R20.1 o el contenido principal (absorbe R5.7 y R7.2). | 3 / 0 / 0 / 0 / 0 / 0 / 0 / 5 |
| 51 | R5.4 | ADS + APS | gobierno | queda | R5.4, sin cambios. | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 52 | R5.5 | APS | I-RES | se retira | Nada que mover: R5.1 ya lo dice entero. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 53 | R5.6 | Player | comportamiento | se reescribe | R5.6: los chequeos (a) capacidad del dispositivo y (b) layouts que el slot admite, y que reenviar el set no quita el chequeo (absorbe R38.5); deja de repetir el recorrido en orden, que es R5.1. | 5 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 54 | R5.7 | Player | comportamiento | se fusiona en R5.3 | R5.3 lleva el salto al siguiente candidato preservando el orden. | 6 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 55 | R5.8 | spec document | I-RES | queda | R5.8, sin cambios (qué representan las opciones). | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 56 | R7.1 | Player | I-RES | se reescribe | R7.1 como semántica del documento: el orden de los candidatos es el orden de presentación, lineales y no lineales, cada uno empieza cuando termina el anterior, y un candidato salteado bajo R5.3 no es un reordenamiento (absorbe R7.4 y R14.1). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 57 | R7.2 | Player | comportamiento | se fusiona en R5.3 | R5.3 cubre el descarte; "no es un reordenamiento" va a R7.1. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 58 | R7.3 | Player | comportamiento | se fusiona en R4.2 | R4.2 lleva "se reproduce y se corta en el tope, la duración declarada no es razón para descartar". | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 59 | R7.4 | Player | I-RES | se fusiona en R7.1 | R7.1 dice el orden en positivo. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 60 | R7.5 | Player | comportamiento | se retira | Nada que mover: repite R4.5. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 61 | R30.1 | APS | I-RES | queda | R30.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 62 | R30.2 | Player | comportamiento | queda | R30.2, sin cambios (el contador `E.c`). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 63 | R3.1 | spec document | gobierno | se reescribe | R3.1: las clases de dispositivo son las filas de la tabla de R3, combinaciones de los tres primeros ejes de R29.1 (absorbe R29.6), y la spec da el comportamiento esperado por clase y oportunidad. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 64 | R3.2 | Player | comportamiento | queda | R3.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 65 | R3.3 | Player | comportamiento | se retira | Nada que mover: es el chequeo (a) de R5.6. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 66 | R16.1 | Player | comportamiento | se reescribe | R16.1: al pasar de pausa a play el Player quita el aviso de pausa en un frame y vuelve al contenido principal aunque haya un aviso a mitad de presentación (absorbe R32.3). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 67 | R16.2 | Player | comportamiento | se fusiona en R13.3 | R13.3 dice que un beacon cuyo tiempo cae después de que terminó la presentación del aviso no se dispara, termine como termine. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 68 | R32.1 | APS | I-RES | se reescribe | R32.1: el documento de una pausa declara `repeat`, `request-again` o `stop`, con el significado de cada uno (hoy sólo en la prosa), y uno que no declara nada significa `stop`. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 69 | R32.2 | Player | comportamiento | queda | R32.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 70 | R32.3 | Player | comportamiento | se fusiona en R16.1 | R16.1 lleva "vuelve al contenido principal aunque haya un aviso a mitad". | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 71 | R32.4 | spec document | gobierno | queda | R32.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 72 | R34.1 | Publisher | I-MPD | se reescribe | R34.1: la declaración once-per-session significa como máximo un aviso de pausa por ventana en la sesión, y una pausa posterior dentro de la ventana deja el contenido sin interrumpir (absorbe R34.2). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 73 | R34.2 | Player | I-MPD | se fusiona en R34.1 | R34.1 lleva la semántica. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 74 | R34.3 | Player | comportamiento | queda | R34.3, sin cambios (cuándo se consume la ventana). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 75 | R34.4 | spec document | gobierno | queda | R34.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 76 | R35.1 | APS | I-RES | queda | R35.1, sin cambios (ya es semántica del documento con su default). | 0 / 2 / 0 / 0 / 0 / 0 / 0 / 11 |
| 77 | R35.2 | APS | I-RES | se reescribe | R35.2: la demora es el tiempo desde que el slot empieza a presentarse antes del cual no se puede cerrar, y desde el cual se puede cerrar mientras el slot esté en pantalla; cero es inmediato (absorbe R35.3). | 0 / 1 / 0 / 0 / 0 / 0 / 0 / 0 |
| 78 | R35.3 | Player | comportamiento | se fusiona en R35.2 | R35.2 lleva el antes y el después de la demora. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 79 | R35.4 | Player | comportamiento | queda | R35.4, sin cambios; recibe de R35.6 la frase "un cierre es un resultado de la presentación, no una falla". | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 80 | R35.5 | Player | comportamiento | queda | R35.5, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 81 | R35.6 | Player | comportamiento | se fusiona en R13.3 | R13.3 cubre los beacons después del cierre; la frase sobre falla va a R35.4. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 82 | R35.7 | spec document | gobierno | queda | R35.7, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 83 | R35.8 | Player | I-MPD | se reescribe | R35.8 como semántica del documento: en un slot lineal rige `@skipAfter` de la base con su default, el default de R35.1 no aplica, y la spec no agrega precedencia entre los dos `@skipAfter`. | 0 / 1 / 0 / 0 / 0 / 0 / 0 / 7 |
| 84 | R36.1 | Publisher | I-MPD | se reescribe | R36.1: el offset es lo más temprano que un Player puede resolver, medido desde el inicio de la ventana en overlay y en pausa, nunca desde la pausa; default 60 s; cero es resolver al disparo (absorbe R36.2 y R36.3). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 4 |
| 85 | R36.2 | Player | I-MPD | se fusiona en R36.1 | R36.1 lleva la cota y el ancla. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 86 | R36.3 | Player | I-MPD | se fusiona en R36.1 | R36.1 lleva el ancla "inicio de la ventana, nunca la pausa". | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 87 | R36.4 | APS | I-RES | se reescribe | R36.4: la validez declarada es hasta cuándo se pueden presentar los candidatos de esa resolución; sin declaración, mientras dure la ventana. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 88 | R36.5 | Player | comportamiento | se reescribe | R36.5: al disparar la oportunidad el Player verifica la validez y, vencida, pide una nueva; una re-resolución sin candidato usable es una resolución vacía (R30) (absorbe R36.6). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 89 | R36.6 | Player | comportamiento | se fusiona en R36.5 | R36.5 lleva que el vacío al re-resolver cuenta como R30; "no volver a la vencida" ya lo dice R36.4. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 90 | R36.7 | spec document | comportamiento | queda | R36.7, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 91 | R37.1 | Player | comportamiento | queda | R37.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 92 | R37.2 | Player | comportamiento | queda | R37.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 93 | R37.3 | spec document | gobierno | queda | R37.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 94 | R38.1 | Publisher | I-MPD | se reescribe | R38.1: `@allowedLayouts`, cuando está, es el conjunto de layouts que el slot admite; cuando no está, el de su familia (hoy sólo se escribe el caso ausente). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 95 | R38.2 | Player | comportamiento | queda | R38.2, sin cambios (cadena Publisher, Player, APS). | 3 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 96 | R38.3 | spec document | I-REQ | se fusiona en R29.1 | R29.1 lleva el parámetro de layouts permitidos en su tabla. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 97 | R38.4 | APS | comportamiento | queda | R38.4, sin cambios (el APS obedece lo recibido). | 1 / 0 / 0 / 1 / 0 / 0 / 0 / 0 |
| 98 | R38.5 | Player | comportamiento | se fusiona en R5.6 | R5.6 (b) lleva el chequeo y la frase "reenviar el set no quita el chequeo". | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 99 | R38.6 | spec document | gobierno | queda | R38.6, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 100 | R39.1 | spec document | gobierno | queda | R39.1, sin cambios. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 101 | R39.2 | Publisher | I-MPD | queda | R39.2, sin cambios (semántica de la región). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 102 | R39.3 | Player | comportamiento | queda | R39.3, sin cambios de fondo; su remisión a R38.3 pasa a R29.1. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 103 | R39.4 | APS | I-RES | queda | R39.4, sin cambios (semántica del rectángulo). | 0 / 0 / 0 / 1 / 0 / 0 / 0 / 0 |
| 104 | R39.5 | Player | comportamiento | se reescribe | R39.5: sólo lo que no se deduce de R39.4: una opción `custom` fuera de la región no es renderizable y se pasa a la siguiente, y un Player sin `custom` trata toda opción `custom` como no renderizable. | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 105 | R19.1 | Player | comportamiento | queda | R19.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 106 | R19.2 | Player | comportamiento | se retira | Nada que mover: es R19.1 en negativo. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 107 | R19.3 | Player | I-RES | se reescribe | R19.3: la duración declarada de toda forma, imagen y HTML incluidas, es un valor de la línea de tiempo de presentación, y su largo en reloj es duración / velocidad (absorbe R19.4; la parte del tope va a R4.11 y la de beacons ya está en R13.1). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 108 | R19.4 | Player | I-RES | se fusiona en R19.3 | R19.3 lleva "toda forma, imagen y HTML incluidas". | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 109 | R21.1 | Player | comportamiento | se reescribe | R21.1: sólo el MAY de liberar recursos cuando el layout es `pause-fullscreen`; la superficie la fija el token (R12.5) y la forma única activa ya es R22.1 y R17.1. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 110 | R25.1 | Player | comportamiento | queda | R25.1, sin cambios. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 111 | R26.1 | APS + Publisher | I-RES | se reescribe | R26.1: el fondo es un atributo de composición del layout, opcional, siempre imagen fija, creativo del anunciante, llena las bandas que dejan las dos cajas, y sin fondo las bandas son negras (hoy la imagen y el negro están en la prosa) (absorbe R26.2). | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 112 | R26.2 | Player | comportamiento | se fusiona en R26.1 | R26.1 lleva la composición y el negro por defecto; la geometría de las dos cajas la da el token (R12.5). | 3 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 113 | R26.3 | Player | comportamiento | queda | R26.3, sin cambios (capacidad del dispositivo). | 11 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 114 | R27.1 | APS + Publisher | I-RES | se reescribe | R27.1: la opción lleva un solo creativo, que cubre todo el cuadro por debajo, y el contenido principal achicado va encima en la región que denota el token; vale para los dos L-shape y para `squeezeback-frame` (esto último hoy sólo en la prosa); no hay un tercer elemento (absorbe R27.2). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 115 | R27.2 | Player | comportamiento | se fusiona en R27.1 | R27.1 lleva la composición. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 3 |
| 116 | R27.3 | Player | comportamiento | queda | R27.3, sin cambios (capacidad del dispositivo). | 6 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 117 | R41.1 | Player | I-RES | se fusiona en R41.3 | R41.3 lleva el default sin audio del aviso y qué se oye mientras tanto. | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 118 | R41.2 | Publisher | I-MPD | queda | R41.2, sin cambios (permiso en la ventana, ausente = no permitido). | 1 / 1 / 0 / 0 / 0 / 0 / 0 / 0 |
| 119 | R41.3 | APS | I-RES | se reescribe | R41.3: una opción que declara su audio se presenta con el audio del aviso en lugar del del contenido (overlay y squeezeback) mientras dure; una que no lo declara se presenta sin audio del aviso y con el del contenido sobre el que se compone; en pausa, sin audio del aviso salvo declaración (absorbe R41.1). | 1 / 1 / 0 / 0 / 0 / 0 / 0 / 0 |
| 120 | R41.4 | Player | comportamiento | se reescribe | R41.4: sólo restaurar el audio del contenido cuando la opción termina, termine como termine. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 121 | R41.5 | Player + APS | comportamiento | queda | R41.5, sin cambios (cadena Player, APS). | 1 / 0 / 0 / 1 / 0 / 0 / 0 / 0 |
| 122 | R41.6 | Player | comportamiento | queda | R41.6, sin cambios (capacidad del dispositivo). | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 123 | R41.7 | Player | comportamiento | queda | R41.7, sin cambios. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 124 | R14.1 | Player | I-RES | se fusiona en R7.1 | R7.1 lleva el orden para no lineales y "cada uno empieza cuando termina el anterior". | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 125 | R14.2 | Player | comportamiento | se fusiona en R4.2 | R4.2 nombra la secuencia no lineal entre los casos de duración acumulada. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 126 | R14.3 | spec document | gobierno | queda | R14.3, sin cambios de fondo; su remisión a R14.1 pasa a R7.1. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 127 | R17.1 | Player | comportamiento | queda | R17.1, sin cambios. | 4 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 128 | R17.2 | Player | comportamiento | se reescribe | R17.2: sólo restaurar el overlay al reanudar si su ventana sigue activa; quitar el aviso de pausa es R16.1. | 4 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 129 | R17.3 | Player | comportamiento | se retira | Nada que mover: es R17.2 en negativo, y fuera de su rango el overlay no se presenta (R40.9). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 130 | R17.4 | spec document | gobierno | queda | R17.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 131 | R17.5 | Player | comportamiento | queda | R17.5, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 132 | R20.1 | Player | comportamiento | queda | R20.1, sin cambios. | 6 / 0 / 0 / 0 / 2 / 0 / 0 / 8 |
| 133 | R20.2 | Publisher | I-MPD | queda | R20.2, sin cambios. | 0 / 2 / 0 / 0 / 0 / 0 / 0 / 0 |
| 134 | R20.3 | Player | comportamiento | queda | R20.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 3 |
| 135 | R20.4 | Player | comportamiento | queda | R20.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 136 | R20.5 | Player | comportamiento | queda | R20.5, sin cambios: EXCEPCIÓN deliberada (R20.6), ver punto 4. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 137 | R20.6 | spec document | gobierno | queda | R20.6, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 138 | R22.1 | Player | comportamiento | queda | R22.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 139 | R40.1 | Publisher | I-MPD | queda | R40.1, sin cambios (opcional, una relación como máximo, pausa sólo on top). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 140 | R40.2 | Publisher | I-MPD | queda | R40.2, sin cambios. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 141 | R40.3 | Player | comportamiento | se reescribe | R40.3: sólo lo que no se deduce de R40.9: la ejecución del evento lineal con las reglas de la base para una ejecución tardía, y que cuándo resolver es del Player dentro de R36. | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 142 | R40.4 | Player | comportamiento | se reescribe | R40.4: sólo que una forma en pantalla cuando empieza una presentación alternativa termina ahí y la ventana no presenta nada más. | 5 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 143 | R40.5 | Player | comportamiento | se reescribe | R40.5: sólo lo que agrega a R40.9: dentro de la capacidad del dispositivo y de R22, el tope corre sobre la línea de tiempo de la alternativa (R4.11) y la forma termina cuando termina la alternativa. | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 144 | R40.6 | Player | comportamiento | queda | R40.6, sin cambios (recursión sobre las alternativas que dispara). | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 145 | R40.7 | spec document | gobierno | queda | R40.7, sin cambios. | 0 / 1 / 0 / 0 / 0 / 0 / 0 / 0 |
| 146 | R40.8 | spec document | gobierno | queda | R40.8, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 147 | R6.1 | spec document | gobierno | queda | R6.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 148 | R6.2 | APS | I-RES | se fusiona en R13.1 | R13.1 es la única definición del carrier de beacons con tiempo (hoy R6.2 dice SHOULD y R13.1 dice MUST). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 149 | R6.3 | spec document | gobierno | queda | R6.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 150 | R6.4 | Player | comportamiento | se retira | Nada que mover: es la regla de la base para namespaces desconocidos (§5.2.1), que R1.1 y R1.5 ya adoptan. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 151 | R6.5 | Player + APS | I-RES | se reescribe | R6.5 como semántica del documento: el alcance de `@id` de un beacon es su candidato en un documento no lineal y el de la base en un ListMPD; "disparar los dos" queda como consecuencia. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 152 | R6.6 | Player | I-RES | se fusiona en R13.1 | R13.1 lleva el ancla temporal: el tiempo del beacon es relativo a la presentación propia del candidato que lo aloja. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 153 | R6.7 | spec document | gobierno | queda | R6.7, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 154 | R13.1 | APS | I-RES | se reescribe | R13.1: carrier (callback de la base), tiempos relativos a la presentación propia del candidato que los aloja, y significado: cada beacon se dispara cuando la presentación del aviso llega a su tiempo (absorbe R6.2, R6.6 y R13.2). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 155 | R13.2 | Player | comportamiento | se fusiona en R13.1 | R13.1 lleva la semántica del disparo. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 156 | R13.3 | Player | comportamiento | se reescribe | R13.3: un beacon cuyo tiempo cae después de que terminó la presentación del aviso, por recorte (R4), cierre (R35) o reanudación (R16), no se dispara (absorbe R16.2 y R35.6). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 157 | R13.4 | spec document | gobierno | queda | R13.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 158 | R13.5 | APS + ADS | gobierno | queda | R13.5, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 159 | R13.6 | APS + Player | I-RES | se reescribe | R13.6 como semántica del documento: un beacon adjunto a una opción informa esa opción y se dispara sólo si esa opción se presenta; uno adjunto al candidato, cualquiera que se presente. | 1 / 2 / 0 / 0 / 0 / 0 / 0 / 0 |
| 160 | R13.7 | APS + Player | I-RES | se reescribe | R13.7 como semántica del documento: el beacon de inicio del slot corresponde al primer aviso que empieza, también si se entra tarde; el de fin, al fin del slot termine como termine; un slot sin avisos no tiene ni uno ni otro. | 1 / 2 / 0 / 0 / 0 / 0 / 0 / 0 |
| 161 | R23.1 | spec document | gobierno | queda | R23.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 162 | R23.2 | spec document | I-RES | queda | R23.2, sin cambios. | 1 / 3 / 0 / 0 / 2 / 0 / 0 / 0 |
| 163 | R24.1 | APS / spec document | I-RES | queda | R24.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 1 / 0 |
| 164 | R33.1 | spec document | gobierno | queda | R33.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 165 | R33.2 | Player | comportamiento | queda | R33.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 166 | R33.3 | spec document | gobierno | queda | R33.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 167 | R33.4 | Publisher | I-MPD | queda | R33.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 168 | R28.1 | APS | I-RES | se reescribe | R28.1: además de dónde va, qué significa: las URLs de click-tracking se disparan cuando el espectador activa el ClickThrough (hoy no lo dice ningún criterio del lado del documento). Ver punto 4. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 169 | R28.2 | Player | comportamiento | se reescribe | R28.2 se queda como la garantía explícita: todo Player conforme lee el carrier de R28.1 con esa semántica. Ver punto 4. | 2 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 170 | R28.3 | APS + ADS | gobierno | queda | R28.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 171 | R42.1 | spec document | I-RES | se reescribe | R42.1: carrier, conjunto cerrado y significado: cada beacon se dispara una vez por ocurrencia en el aviso que lo lleva, nunca desde la línea de tiempo (absorbe R42.3). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 172 | R42.2 | APS | I-RES | queda | R42.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 173 | R42.3 | Player | comportamiento | se fusiona en R42.1 | R42.1 lleva la semántica. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 174 | R42.4 | spec document | gobierno | queda | R42.4, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 175 | R44.1 | spec document | I-RES | queda | R44.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 176 | R44.2 | APS | I-RES | queda | R44.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 177 | R44.3 | Player | comportamiento | queda | R44.3, sin cambios (datos opacos). | 1 / 0 / 0 / 0 / 2 / 0 / 0 / 0 |
| 178 | R47.1 | APS | I-RES | se reescribe | R47.1: cada beacon marcado con su resultado se dispara una vez por impresión cuando se determina ese resultado, e "indeterminado" es el resultado de un Player que no lo determina (absorbe R47.2). | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 179 | R47.2 | Player | comportamiento | se fusiona en R47.1 | R47.1 lleva la semántica. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 180 | R47.3 | spec document | gobierno | queda | R47.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 181 | R48.1 | spec document | I-RES | queda | R48.1, sin cambios. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 182 | R48.2 | APS | I-RES | queda | R48.2, sin cambios. | 1 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 183 | R48.3 | Player | comportamiento | queda | R48.3, sin cambios (datos opacos, presentación según el dispositivo). | 2 / 0 / 0 / 0 / 1 / 0 / 0 / 0 |
| 184 | R8.1 | spec document | gobierno | queda | R8.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 185 | R8.2 | spec document | gobierno | queda | R8.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 186 | R9.1 | spec document | gobierno | queda | R9.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 187 | R9.2 | spec document | gobierno | queda | R9.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 188 | R9.3 | spec document | gobierno | queda | R9.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 2 |
| 189 | R10.1 | spec document | gobierno | queda | R10.1, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 4 |
| 190 | R10.2 | spec document | gobierno | queda | R10.2, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 1 |
| 191 | R10.3 | spec document | gobierno | queda | R10.3, sin cambios. | 0 / 0 / 0 / 0 / 0 / 0 / 0 / 4 |

#### Criterios nuevos

- **R12.5** (spec document, I-MPD e I-RES). Qué composición denota cada token de layout: para los squeezeback, la región que ocupa el contenido principal según la tabla de R12; para `pause-fullscreen` y `pause-partial`, la superficie; para los overlay, que el creativo se compone sobre un contenido que no se transforma. Hoy la tabla está en la prosa de R12 y el efecto se repite en R21.1, R26.2 y R27.2. Es el siguiente sub-id libre de R12.
- **R40.9** (spec document, I-MPD). La semántica de la ventana no lineal: a qué está anclada (una ventana overlay o squeezeback a su rango de tiempo de medio, una de pausa a la pausa del espectador dentro de su rango) y qué significa cada una de las tres relaciones con el evento lineal (default, supersede con su fallback, on top). Hoy vive sólo en la prosa de R40 y, repartida, en R40.3, R40.4 y R40.5 como obligaciones del Player. Es el siguiente sub-id libre de R40.

#### Referencias internas de 03 que cambian

Diez menciones dentro de 03 apuntan a ids que se van y hay que reescribirlas junto con la reestructura: R29.9 (1, en R29.1), R5.7 (1), R7.2 (2), R7.3 (1), R7.4 (1), R38.3 (1, en R39.3), R14.1 (1, en R14.3) y R14.2 (1). El comando está en el punto 6.

### A.2. Semántica que hoy vive sólo en la prosa

| Requerimiento | Qué está sólo en la prosa (o en una tabla de la prosa) | Criterio que la sube |
|---|---|---|
| R26 | Que el fondo es siempre una imagen fija, del anunciante, y que sin fondo las bandas son negras (R26.2 lo dice del lado del Player) | R26.1, reescrito |
| R27 | La composición (creativo a cuadro completo debajo, contenido achicado encima en la región del token) y que R27 vale también para `squeezeback-frame` | R27.1, reescrito |
| R28 | Qué significa el click-tracking: se dispara cuando el espectador activa el ClickThrough. R28.1 sólo dice dónde va | R28.1, reescrito (R28.2 queda como garantía, ver punto 4) |
| R40 | El anclaje de una ventana no lineal y el significado de default, supersede y on top | R40.9, nuevo |
| R12 | La tabla token a región de los squeezeback y la superficie de cada token de pausa | R12.5, nuevo |
| R32 | Qué hace cada uno de `repeat`, `request-again` y `stop` | R32.1, reescrito |
| R29 | Que los parámetros viajan como query parameters y no por el template de URL del MPD (R38.3 lo dice sólo como ejemplo) | R29.1, reescrito |
| R3 | La tabla de clases de dispositivo, que la prosa llama "the only definition of the classes" y ningún criterio carga (R29.6 remite a ella) | R3.1, reescrito |
| R31 | Qué es una ventana de pausa (dispara el pedido si la pausa empieza dentro). Hoy está en la prosa y en R31.1 como obligación del Player | R31.1, reescrito |

Fuera de las tres interfaces encontré un caso más del mismo patrón: R33.2 obliga a derivar el intervalo de pausa "as described above", y esa derivación (del fin de un período detenido por `UserRequest` al `start` del siguiente `Resume`) está sólo en la prosa de R33. No es I-MPD, I-REQ ni I-RES, así que no lo incluí en la reestructura; lo dejo anotado.

### A.3. Totales

| Acción | Criterios |
|---|---:|
| Quedan | 114 |
| Se reescriben | 41 |
| Se fusionan | 30 |
| Se retiran | 6 |
| **Total** | **191** |
| Nuevos (R12.5, R40.9) | 2 |
| Criterios después de la reestructura | 157 |

Por interfaz, según la columna de la tabla: I-MPD 24, I-REQ 9, I-RES 36, comportamiento 74, gobierno 48.

La cuenta difiere del análisis v12.6, que daba 11 borrados y 36 reescritos. La diferencia es de método: acá cada criterio absorbido se cuenta como fusionado (su id se retira) y el que lo absorbe como reescrito, y además se incluyen los duplicados del mismo actor y los casos nuevos que salieron al rehacer el recorrido (R6.2 frente a R13.1, R6.4, R16.2 y R35.6 frente a R13.3, R17.3, R19.4, R29.6, R29.9, R38.3).

#### Menciones fuera de 03 que apuntan a un id que se va

29 menciones en total: 19 en 04, 0 en 06, 1 en 99, 9 en ADRs, y 0 en 02, 05, 07 y 08. Por id (sólo los que tienen alguna):

| id | acción | 04 | 99 | ADR |
|---|---|---:|---:|---:|
| R5.7 | se fusiona en R5.3 | 6 | 0 | 2 (ADR 0011) |
| R5.2 | se fusiona en R5.1 | 3 | 0 | 0 |
| R26.2 | se fusiona en R26.1 | 3 | 0 | 0 |
| R7.3 | se fusiona en R4.2 | 2 | 0 | 0 |
| R38.5 | se fusiona en R5.6 | 2 | 0 | 0 |
| R41.1 | se fusiona en R41.3 | 2 | 0 | 0 |
| R5.5 | se retira | 1 | 0 | 0 |
| R29.9 | se fusiona en R29.1 | 0 | 1 | 0 |
| R27.2 | se fusiona en R27.1 | 0 | 0 | 3 (ADR 0014) |
| R36.2 | se fusiona en R36.1 | 0 | 0 | 2 (ADR 0018) |
| R36.3 | se fusiona en R36.1 | 0 | 0 | 2 (ADR 0018) |

Las cuatro ADRs citadas (0011, 0014, 0018) tienen `status: accepted`. Por `knowledge/documentation-policy.md` (regla B), una ADR aceptada es registro y no se reescribe: lo que corresponde es una nota fechada debajo que diga a qué id pasó cada mención. Las 20 menciones de 04 y 99 sí se reescriben.

La tabla completa de los 36 ids que se van, incluidos los que no tienen citas:

| id | acción | 04 | 06 | 99 | ADR | otras (02, 05, 07, 08) |
|---|---|---:|---:|---:|---:|---:|
| R29.6 | se fusiona en R3.1 | 0 | 0 | 0 | 0 | 0 |
| R29.8 | se fusiona en R29.2 | 0 | 0 | 0 | 0 | 0 |
| R29.9 | se fusiona en R29.1 | 0 | 0 | 1 | 0 | 0 |
| R4.3 | se fusiona en R4.1 y R4.6 | 0 | 0 | 0 | 0 | 0 |
| R5.2 | se fusiona en R5.1 | 3 | 0 | 0 | 0 | 0 |
| R5.5 | se retira | 1 | 0 | 0 | 0 | 0 |
| R5.7 | se fusiona en R5.3 | 6 | 0 | 0 | 2 | 0 |
| R7.2 | se fusiona en R5.3 | 0 | 0 | 0 | 0 | 0 |
| R7.3 | se fusiona en R4.2 | 2 | 0 | 0 | 0 | 0 |
| R7.4 | se fusiona en R7.1 | 0 | 0 | 0 | 0 | 0 |
| R7.5 | se retira | 0 | 0 | 0 | 0 | 0 |
| R3.3 | se retira | 0 | 0 | 0 | 0 | 0 |
| R16.2 | se fusiona en R13.3 | 0 | 0 | 0 | 0 | 0 |
| R32.3 | se fusiona en R16.1 | 0 | 0 | 0 | 0 | 0 |
| R34.2 | se fusiona en R34.1 | 0 | 0 | 0 | 0 | 0 |
| R35.3 | se fusiona en R35.2 | 0 | 0 | 0 | 0 | 0 |
| R35.6 | se fusiona en R13.3 | 0 | 0 | 0 | 0 | 0 |
| R36.2 | se fusiona en R36.1 | 0 | 0 | 0 | 2 | 0 |
| R36.3 | se fusiona en R36.1 | 0 | 0 | 0 | 2 | 0 |
| R36.6 | se fusiona en R36.5 | 0 | 0 | 0 | 0 | 0 |
| R38.3 | se fusiona en R29.1 | 0 | 0 | 0 | 0 | 0 |
| R38.5 | se fusiona en R5.6 | 2 | 0 | 0 | 0 | 0 |
| R19.2 | se retira | 0 | 0 | 0 | 0 | 0 |
| R19.4 | se fusiona en R19.3 | 0 | 0 | 0 | 0 | 0 |
| R26.2 | se fusiona en R26.1 | 3 | 0 | 0 | 0 | 0 |
| R27.2 | se fusiona en R27.1 | 0 | 0 | 0 | 3 | 0 |
| R41.1 | se fusiona en R41.3 | 2 | 0 | 0 | 0 | 0 |
| R14.1 | se fusiona en R7.1 | 0 | 0 | 0 | 0 | 0 |
| R14.2 | se fusiona en R4.2 | 0 | 0 | 0 | 0 | 0 |
| R17.3 | se retira | 0 | 0 | 0 | 0 | 0 |
| R6.2 | se fusiona en R13.1 | 0 | 0 | 0 | 0 | 0 |
| R6.4 | se retira | 0 | 0 | 0 | 0 | 0 |
| R6.6 | se fusiona en R13.1 | 0 | 0 | 0 | 0 | 0 |
| R13.2 | se fusiona en R13.1 | 0 | 0 | 0 | 0 | 0 |
| R42.3 | se fusiona en R42.1 | 0 | 0 | 0 | 0 | 0 |
| R47.2 | se fusiona en R47.1 | 0 | 0 | 0 | 0 | 0 |
| **Total** | | **19** | **0** | **1** | **9** | **0** |

### A.4. R28 y R20.5 / R20.6

**R28.** Acción: R28.1 se reescribe y R28.2 también se reescribe, y los dos ids se conservan. R28.1 pasa a decir, además de dónde va el ClickThrough, qué significa: las URLs de click-tracking se disparan cuando el espectador activa el ClickThrough. R28.2 no se fusiona ni se retira: queda como la garantía explícita, "todo Player conforme a esta especificación lee el carrier de R28.1 con esa semántica". La razón es que R28 existe para que *"every Player conformant to this specification reads them the same way"*, y esa frase es una promesa sobre los Players, no sobre el documento. Si la semántica sube a R28.1 y R28.2 desaparece, la garantía pasa a ser una deducción ("si el documento lo significa, un Player conforme lo hace"), que es justo lo que la advertencia del análisis v12.6 pide evitar. Lo que sí sale de R28.2 es la semántica repetida: queda como remisión a R28.1, no como segunda definición.

Una consecuencia para la reestructura: R42.3 y R47.2 tienen la misma forma que R28.2 ("A Player conformant to this specification MUST fire…"), y acá los fusiono en R42.1 y R47.1 porque sus requerimientos no declaran una garantía de lectura uniforme como la de R28. Si se quiere la misma garantía explícita para los beacons por ocurrencia y los de viewability, esos dos ids tendrían que quedarse como R28.2. No lo decidí: lo señalo porque es el mismo patrón.

**R20.5 y R20.6.** Acción: los dos quedan, sin cambios. Es una **excepción deliberada** a la regla de la reestructura. R20.5 se deduce del documento (una declaración pertenece a la ventana que la lleva, así que los candidatos que sirve cada ventana de un fallback se atan a las declaraciones de esa ventana), y por la regla general debería subir al lado del documento. Pero R20.6 exige a propósito que R20.5 sea una obligación normativa del Player, porque *"a rule that selects which presentation option reaches the screen cannot depend on a reader treating an illustration as a requirement"*. Cambiar R20.5 obligaría a revisar R20.6, y eso es una decisión de contenido, no de redacción.

### A.5. Las tres interfaces

Criterio de conteo: "una" es una sola definición en un criterio; "más de una" es la misma semántica escrita en dos o más criterios; "ninguna" es que ningún criterio la escribe (está sólo en la prosa, en otro archivo o en ninguna parte). La columna "lado" dice si la definición está escrita del lado del documento o como obligación del Player: los elementos definidos una sola vez pero del lado del Player son los que la reestructura tiene que dar vuelta aunque no estén duplicados.

| Interfaz | Elementos | Definidos una vez | Más de una | Ninguna | De los "una vez", sólo del lado del Player |
|---|---:|---:|---:|---:|---:|
| I-MPD | 26 | 14 | 9 | 3 | 5 |
| I-REQ | 16 | 10 | 5 | 1 | 3 |
| I-RES | 32 | 17 | 13 | 2 | 2 |
| **Total** | **74** | **41** | **27** | **6** | **10** |

#### I-MPD (26 elementos: 14 una vez, 9 más de una, 3 ninguna; de los definidos una vez, 5 lo están sólo del lado del Player)

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
| 15 | Once-per-session | R34.1 y R34.2 | más de una | doc + Player | R34.1 |
| 16 | Cuándo se consume la ventana once-per-session | R34.3 | una | Player | R34.3 (se queda como comportamiento) |
| 17 | `@earliestResolutionTimeOffset` (offset, ancla, default) | R36.1, R36.2 y R36.3 | más de una | doc + Player | R36.1 |
| 18 | Permiso de audio del aviso en la ventana | R41.2 | una | doc | R41.2 |
| 19 | Relación con el evento lineal (default, supersede, on top): qué significa | prosa de R40; R40.4, R40.3 y R40.5, uno por relación | una | Player | R40.9 (nuevo); R40.3 a R40.5 quedan con lo que no se deduce |
| 20 | Relación: opcional, una sola, pausa sólo on top | R40.1 | una | doc | R40.1 |
| 21 | Ventanas declaradas en el MPD de una alternativa | R40.2 y R40.6 | más de una | doc + Player | R40.2 (lugar) y R40.6 (recursión) |
| 22 | Un solo `EventStream` por familia y Period | R20.2 | una | doc | R20.2 |
| 23 | Pedido de la métrica `PlayList` (`Metrics`) | R33.4 | una | doc | R33.4 |
| 24 | `@skipAfter` de un evento lineal heredado | R35.8 | una | Player | R35.8 reescrito del lado del documento |
| 25 | `@executeOnce` ante una resolución vacía | R30.2 | una | Player | R30.2 (comportamiento del contador de la base) |
| 26 | `@value` en un `EventStream` SGAI | ninguno en 03; lo fija 06 | ninguna | - | queda en 06 (es HOW) |

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
| 8 | Layouts permitidos reenviados | R38.2, R38.3 y R29.8; sin nombre de parámetro y fuera de la lista cerrada de R29.1 | más de una | Player + doc | fila de R29.1; R38.2 queda como obligación de reenviar |
| 9 | Región custom reenviada | R39.3 y R29.8; sin nombre de parámetro | más de una | Player + doc | fila de R29.1; R39.3 queda |
| 10 | Permiso de audio reenviado | R41.5 y R29.8; sin nombre de parámetro | más de una | Player + doc | fila de R29.1; R41.5 queda |
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
| 14 | Carrier de los beacons con tiempo | R6.2 (SHOULD), R13.1 (MUST) y R13.4 (mandatory) | más de una | doc + gobierno | R13.1 (R13.4 queda como gobierno) |
| 15 | Ancla temporal y disparo de los beacons con tiempo | R6.6, R13.1 y R13.2 | más de una | doc + Player | R13.1 |
| 16 | Alcance de `@id` de un beacon | R6.5 | una | Player + doc | R6.5 reescrito del lado del documento |
| 17 | Beacons adjuntos a una opción o al candidato | R13.6 | una | Player + doc | R13.6 reescrito del lado del documento |
| 18 | Beacons de inicio y fin de slot | R13.7 | una | Player + doc | R13.7 reescrito del lado del documento |
| 19 | Beacons por ocurrencia | R42.1 y R42.3 | más de una | doc + Player | R42.1 |
| 20 | Beacons de viewability | R47.1 y R47.2 | más de una | doc + Player | R47.1 |
| 21 | Carrier del ClickThrough y su click-tracking | R28.1 | una | doc | R28.1 |
| 22 | Click-tracking disparado al activar | R28.2 | una | Player | R28.1 (semántica) y R28.2 (garantía) |
| 23 | Qué significa activar el ClickThrough respecto de su URL de destino | ninguno | ninguna | - | no lo decide este inventario: hoy ningún criterio dice qué hace el Player con la URL |
| 24 | Cerrable o no | R35.1 | una | doc | R35.1 |
| 25 | Demora antes de poder cerrar | R35.2 y R35.3 | más de una | doc + Player | R35.2 |
| 26 | Comportamiento al agotar la pausa: declaración y default | R32.1 | una | doc + Player | R32.1 |
| 27 | Qué significa `repeat`, `request-again` y `stop` | sólo la lista de la prosa de R32 | ninguna | - | R32.1 reescrito |
| 28 | Validez de la resolución | R36.4, R36.5 y R36.6 | más de una | doc + Player | R36.4 |
| 29 | Metadatos de aplicación (`AdSystem`, `AdTitle`) | R23.1 | una | doc | R23.1 |
| 30 | Identificadores del creativo | R23.2 | una | doc | R23.2 |
| 31 | Recursos de verificación | R44.1 | una | doc | R44.1 |
| 32 | Divulgación regulatoria | R48.1 | una | doc | R48.1 |

### A.6. Verificación

**Conteo de criterios y extracción de ids y roles.** La tabla del punto 1 se generó desde los ids extraídos del archivo, y el script que la arma aborta la lista si falta o sobra una decisión.

```
$ grep -cE '^\s*- \*\*R[0-9]+\.[0-9]+\*\* \(' context/03-requirements.md
191
$ grep -oP '^\s*- \*\*\KR[0-9]+\.[0-9]+(?=\*\* \()' context/03-requirements.md | wc -l
191
$ python3 gen.py   # arma la tabla desde ids.txt y decisions.py
missing [] extra []
191 {'queda': 114, 'se reescribe': 41, 'se fusiona': 30, 'se retira': 6}
{'gobierno': 48, 'comportamiento': 74, 'I-MPD': 24, 'I-REQ': 9, 'I-RES': 36}
gone 36 19 0 1 9 0
```

**Citas.** Comando por id y archivo: `grep -oP "\b${id//./\\.}(?![0-9])" context/<archivo>.md | wc -l`, y para las ADRs `cat .project/decisions/*.md | grep -oP … | wc -l`. Suma por columna sobre los 191 ids (04, 06, 99, 02, 05, 07, 08, ADR):

```
121 23 2 3 8 2 3 111
```

Controles del instrumento, para ver que sabe encontrar y que no cuenta de más:

```
R5.6 en 04: 5                       (el control positivo del análisis v12.6 daba 5)
ADRs, \bR4\.1 sin lookahead: 16     (cuenta R4.1 y R4.10 juntos)
ADRs, \bR4\.1(?![0-9]): 8
ADRs, \bR4\.10(?![0-9]): 8          (8 + 8 = 16: el lookahead separa bien)
R99.9 (inexistente) en 04: 0
```

**Rangos.** El grep cuenta ids sueltos, no rangos. Busqué rangos en todos los archivos citados:

```
$ grep -noP '\bR[0-9]+\.[0-9]+\s*(–|-|to|through)\s*R?[0-9]+\.[0-9]+' context/0[245678]*.md context/99*.md .project/decisions/*.md
.project/decisions/0004-enumerate-edition-scoped-iab-ad-type-subset.md:64:R12.1 to R12.3
```

Es el único, y abarca R12.2, que queda. Ningún id que se va está escondido dentro de un rango.

**Referencias internas en 03 a ids que se van** (menciones menos la de su propia definición):

```
R29.6:0 R29.8:0 R29.9:1 R4.3:0 R5.2:0 R5.5:0 R5.7:1 R7.2:2 R7.3:1 R7.4:1 R7.5:0 R3.3:0 R16.2:0 R32.3:0 R34.2:0 R35.3:0 R35.6:0 R36.2:0 R36.3:0 R36.6:0 R38.3:1 R38.5:0 R19.2:0 R19.4:0 R26.2:0 R27.2:0 R41.1:0 R14.1:1 R14.2:1 R17.3:0 R6.2:0 R6.4:0 R6.6:0 R13.2:0 R42.3:0 R47.2:0
```

**Estado de las ADRs citadas:**

```
R5.7  0011-empty-resolution-falls-through-to-the-next-window.md       status: accepted
R36.2 0018-early-resolution-adopts-the-base-offset-and-its-default.md status: accepted
R36.3 0018-early-resolution-adopts-the-base-offset-and-its-default.md status: accepted
R27.2 0014-the-layout-token-carries-the-squeezeback-geometry.md       status: accepted
```

**Conteo del punto 5.** Generado por script sobre las tres listas:

```
I-MPD 26 {'ninguna': 3, 'una': 14, 'más de una': 9} una-Player 5
I-REQ 16 {'una': 10, 'ninguna': 1, 'más de una': 5} una-Player 3
I-RES 32 {'una': 17, 'más de una': 13, 'ninguna': 2} una-Player 2
74 27 6
```

**Lo que no pude determinar.**

- La lista de elementos del punto 5 es mía: la saqué de 03 y de 06, porque ninguna parte de `context/` enumera los elementos de cada interfaz. Los números valen para esa lista. Otra partición (por ejemplo, separar el offset en valor, ancla y default) cambia los conteos, aunque no cuáles elementos están duplicados o faltan.
- La clasificación queda, reescribe, fusiona o retira es juicio aplicado a la regla, no una medición. Donde me aparté del análisis v12.6 lo dice la tabla.
- No verifiqué que las 29 menciones de 04, 99 y las ADRs sigan teniendo sentido con el id destino. Eso se ve al reescribirlas.


Los hallazgos del recorrido que no son redacción están en "Preguntas abiertas" (P-1 a P-4 y P-7).
