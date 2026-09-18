# Auditoría a ciegas de `context/`

Este documento es el resultado de una lectura de `context/` hecha sin abrir
`output/`, `output-analysis/`, `dist/`, `context-analysis/`, `.github-ai/` ni
`bin/`. La pregunta que contesta es si los defectos que hacen que una
especificación generada salga mal eran detectables mirando únicamente la capa
de requerimientos.

Fuentes leídas: los diez archivos de `context/`, el `CLAUDE.md` y el
`README.md` del proyecto, y los trece ADR de `.project/decisions/`. No se
abrió ningún artefacto generado, ni el código de los chequeos de `bin/`. La
descripción de `bin/check-context-coherence.py` que se usa en el cierre sale
del `CLAUDE.md`, no del script.

Las citas van en inglés porque el material está en inglés. El análisis va en
castellano.

---

## Índice de hallazgos

**Bloqueantes**

1. Contradicción — `02-actors.md`, `99-glossary.md`, `05-dash-linear-interfaces.md`, R2, R6.2, R13 vs R11 — el texto normativo ata el sistema a VAST, y a una versión de VAST, cuando R11 prohíbe exactamente eso.
2. Contradicción — R1 / R1.1 vs DR-8 — se le pone un MUST a un Player que por definición no implementa esta especificación.
3. Contradicción — `02-actors.md` (Video Player, "Select the ad to render") vs R7.4 — al Player se le permite y se le prohíbe deduplicar y reordenar.
4. Contradicción — R4.1 + R4.10 vs R4 (prosa) + R31 — se exige declarar un cap en todo slot, y el slot de pausa no tiene nada que ese cap pueda acotar.
5. Contradicción — `02-actors.md` (Publisher) + UC-03 vs R22.1 + R14.3 + DP-1.1 — un tope de overlays concurrentes declarado por el Publisher contra una regla que fija ese número en uno.
6. Contradicción — UC-03, UC-04, UC-09, UC-13 vs R12.2 — los casos de uso declaran layouts (`banner`, `sidebar`) que la enumeración cerrada no admite.
7. Contradicción — UC-09 / UC-13 (opción 4) vs R12 + R20.4 — un `full-screen takeover`, que R12 clasifica como `linear`, aparece como opción dentro de un slot no-lineal.
8. Gap — R20 vs R12 + `06-naming-and-namespaces.md` — la palabra "family" gobierna todo el mecanismo de fallback y su enumeración deja afuera a `squeezeback`.
9. Gap — R12 + `06-naming-and-namespaces.md` — cuatro de los placements admitidos no tienen token, y el único ejemplo del repo inventa dos.
10. Gap — UC-04 y UC-14 vs R14 / R17 / R20 / R22 — ambos dependen de composición concurrente lineal + no-lineal, y ningún requerimiento la define.

**Riesgos**

11. Contradicción — UC-05 ("Publisher intent") vs R31 — el caso de uso acota la duración de un pause-ad que R31 declara inacotable.
12. Contradicción — `01-intro.md` vs R12 + OOS-5 — la introducción promete formas que la enumeración cerrada excluye.
13. Contradicción — `06-naming-and-namespaces.md` vs DR-10 — un perfil que identifica el documento de resolución no-lineal, y una regla que dice que ese documento no declara perfil.
14. Contradicción — `06-naming-and-namespaces.md` vs R12 — se prohíben los nombres de layout privados de la spec y R12 acuña dos.
15. Contradicción — `05-dash-linear-interfaces.md` (pasos 7 y ListMPD) vs R4.6 — el cap aplicado como suma acumulada también en replacement.
16. Contradicción — DP-2 vs las 38 apariciones de `MUST NOT` en `03-requirements.md`.
17. Obligación sin fuerza — `02-actors.md` completo: cero modales RFC 2119 en el documento que se declara normativo, y R2 lo invoca con un "must" minúscula.
18. Ambigüedad de alcance — R4.5 ("actual rendered length") vs R19.3 y R4.11 — no se sabe si se recorta contra la línea de tiempo de presentación o contra el reloj de pared.
19. Contradicción — UC-08 ("Ad response") vs R31.1 — un atajo que evita la request de resolución que R31.1 declara obligatoria.
20. Gap — UC-04, UC-05 ("Notes / open questions") vs la tabla "Deliberately open" vacía de `03-requirements.md`.
21. Gap — R29 vs `05-dash-linear-interfaces.md` (§I.4 `UrlParamInfo`) — dos mecanismos que escriben query params en la misma request, sin regla de convivencia.
22. Definición que no define — "resolution document": 115 apariciones, ninguna entrada de glosario.
23. Definición que no define — "Overlay" en el glosario es a la vez el paraguas y un hermano de `squeezeback`, y la tabla de terminología de UC contradice la definición de "Non-linear ad".
24. Definición que no define — "legacy Player": 42 apariciones y ninguna definición; dos lecturas incompatibles.

**Menores**

25. Obligación sin fuerza — UC-07 impone un SHOULD al Publisher que ningún requerimiento carga.
26. Obligación sin fuerza — `07-backward-compat-checklist.md` mezcla tres fuerzas distintas para la misma idea.
27. Ambigüedad — R32.1 exige declarar y a la vez define el default para la ausencia.
28. Obligación sin fuerza — R2.2 y R5.4 usan una negación malformada de RFC 2119 ("Neither MUST be expected / required").
29. Menores editoriales — encabezado de `04-use-cases.md` desactualizado, frase truncada en R29.1, entrada "Brand safety" del glosario.

---

## Bloqueantes

### 1. El texto normativo ata el sistema a VAST, y a una versión de VAST

**Dónde está**: `02-actors.md` (APS, "Convert VAST → MPD-native / SGAI"),
`99-glossary.md` (entrada **ListMPD**), `05-dash-linear-interfaces.md`
(component inventory, interface contracts, diagrama de flujo),
`03-requirements.md` R2 (prosa), R6.2, R13 (prosa) — contra R11, R11.1 y R11.3.

**El texto literal.** R11 dice qué está prohibido:

> **R11.1** (spec document): The normative chapters of the spec MUST NOT cite a
> specific VAST version as required.
>
> **R11.3** (spec document): Any reference to VAST in the spec MUST be in an
> annex or in a non-normative note explicitly flagged as illustrative.

Y el resto del conjunto hace exactamente eso. R2, en su prosa:

> the Publisher declares constraints, the ADS decides which ads to serve
> (output as VAST), the APS converts that VAST into the resolution document
> the Player reads

R6.2, que es un criterio de conformidad:

> The APS produces these entries by translating the tracking events the ADS
> declared in its VAST.

El glosario, en la definición de ListMPD:

> The APS derives the `ListMPD` from the VAST the ADS produced.

`02-actors.md`, en el encabezado de una responsabilidad del APS:

> **Convert VAST → MPD-native / SGAI.** On each resolution request, the APS
> obtains the ad decision from the ADS as VAST and transforms it into the
> resolution document

Y `05-dash-linear-interfaces.md` llega a fijar la versión, en la tabla de
inventario de componentes y en la de contratos de interfaz:

> | ADS | VAST 4.x (the ad decision) in response to the APS's request |
>
> | APS | ADS | HTTP/HTTPS | VAST 4.x (XML) request / response |

**Cuál es el problema.** El mismo conjunto de documentos dice dos cosas que no
pueden ser ciertas a la vez: que la especificación no depende de VAST, y que el
ADS emite VAST 4.x y el APS lo convierte. La reparación se hizo sólo en algunos
lugares: R2.2 y R11.2 ya dicen "decision document (typically VAST)", y
`02-actors.md` abre su sección del ADS con "the ADS is not bound to VAST and MAY
emit another format". Pero el encabezado de la responsabilidad del APS, el
glosario, R6.2, R13 y todo `05-dash-linear-interfaces.md` quedaron sin tocar. No
hay ninguna marca que diga que ese material es ilustrativo: el índice de
`01-intro.md` presenta `05-dash-linear-interfaces.md` como "Reference for how
SGAI is implemented today", que es lo contrario de un anexo no-normativo.

**Qué pasaría aguas abajo.** Un generador que lea `context/` como una sola
fuente va a escribir el capítulo del APS con VAST como entrada obligatoria, y
va a copiar "VAST 4.x" a una tabla de interfaces del cuerpo normativo. El
resultado viola R11.1 y R11.3 en su propio documento, y cualquier auditoría
contra R11 lo va a marcar. Peor: el capítulo de tracking (R6/R13) queda
escrito como una traducción de `<TrackingEvents>` de VAST, lo que convierte el
formato de decisión del ADS en parte del contrato, que es precisamente lo que
R18 declara fuera de alcance.

**Severidad**: `bloqueante`.

---

### 2. Se le pone un MUST a un Player que no implementa esta especificación

**Dónde está**: `03-requirements.md` R1 y R1.1, contra
`08-dash-extension-rules.md` DR-8.

**El texto literal.** R1:

> Backward compatibility is mandatory: a Player that does not implement the new
> mechanisms introduced by this proposal MUST skip them and continue playing
> the primary content uninterrupted.
>
> **R1.1** (Player): Given an `MPD` containing an SGAI construct introduced by
> this proposal that the Player does not implement, a conforming legacy Player
> MUST ignore the unknown construct and continue playing the primary content
> uninterrupted.

DR-8, que es la regla que cierra esa posibilidad:

> **DASH specifies no Player behaviour anywhere** — so no construct defined
> here, in any namespace and under any profile, can compel a Player that does
> not implement this specification.
>
> **Consequence for authoring:** a requirement in this specification **may**
> oblige a Player conformant **to this specification**. It **may not** promise
> what *"every Player"* will do

**Cuál es el problema.** R1.1 dirige un MUST al Player legacy, que es por
definición el que no implementa esta especificación. DR-8 dice que esa
obligación no está disponible. No es una interpretación mía: DR-8 documenta que
esto ya pasó una vez y se arregló, y nombra el caso —

> R28 is the worked case: its ClickThrough carrier promised that *"every
> conformant Player"* would read it, which under this rule is unpromiseable,
> and the guarantee is now scoped to Players conformant to this specification
> across the nine sites that stated it.

El arreglo de ADR 0009 se aplicó a R28 y no a R1, que es donde la promesa
imposible es la premisa de todo el requerimiento de compatibilidad.

**Qué pasaría aguas abajo.** El capítulo de conformidad de la spec generada va
a contener una obligación de Player dirigida a implementaciones fuera de su
alcance. Un revisor de MPEG o del WG lo va a rechazar con la misma cita de §8.1
NOTE 1 que DR-8 ya trae, y el arreglo no es cosmético: R1 hay que reescribirlo
como una obligación sobre el **documento** (que los constructos se expresen en
puntos de extensión cuya semántica de descarte ya existe) en vez de sobre el
Player. Eso cambia también R1.1 de criterio de runtime a criterio de documento,
y con él la tabla de conformidad.

**Severidad**: `bloqueante`.

---

### 3. Al Player se le permite y se le prohíbe deduplicar y reordenar

**Dónde está**: `02-actors.md`, sección "Video Player", quinto bullet, contra
`03-requirements.md` R7.4.

**El texto literal.** `02-actors.md`:

> Select the ad to render from the candidates that passed validation. The
> Player may apply additional client-side criteria (ranking, ordering,
> deduplication, simultaneity caps), but it must operate within the validated
> subset.

R7.4:

> **R7.4** (Player): The Player MUST NOT re-order, deduplicate, or otherwise
> rearrange the remaining candidates after applying R7.2 / R7.3.

**Cuál es el problema.** Las dos frases nombran las mismas tres operaciones —
ordenar, deduplicar, rankear — y una las permite mientras la otra las prohíbe
con un MUST NOT. Además, `02-actors.md` se declara a sí mismo como "the
canonical statement of that model" y R2 remite a él, así que no hay una
jerarquía escrita que permita decidir cuál manda.

**Qué pasaría aguas abajo.** El capítulo de selección de la spec va a salir con
una de las dos reglas, elegida por el orden en que el generador leyó los
archivos, y la otra va a sobrevivir en el capítulo de actores. Dos
implementadores que lean capítulos distintos van a producir dos órdenes de
reproducción distintas para el mismo pod, que es justamente el resultado que R7
existe para evitar. Y no hay test que lo agarre: los dos comportamientos pasan
el criterio del capítulo que cada uno leyó.

**Severidad**: `bloqueante`.

---

### 4. Un cap obligatorio en un slot que no tiene nada que acotar

**Dónde está**: `03-requirements.md` R4.1 y R4.10, contra la prosa de R4 y
contra R31 / R31.2.

**El texto literal.** R4.1 no admite excepción:

> **R4.1** (Publisher): The Publisher MUST declare a maximum duration on every
> ad slot (linear or non-linear) defined in the `MPD`.

R4.10 hace que la omisión sea fatal:

> **R4.10** (Player): A slot declaration carrying no maximum duration is not a
> slot this specification defines (R4.1, R4.8). The Player MUST NOT present ads
> from such a slot and MUST continue with the primary content.

Y la prosa de R4, junto con R31, dice que el slot de pausa no tiene duración
declarable:

> A **pause** slot has no declared duration for a cap to bound: the viewer
> decides how long it lasts, and R31 states what follows from that.
>
> **R31.2** (Publisher + Player): The Publisher-declared slot cap (R4) MUST NOT
> be interpreted as bounding the duration of a pause slot. R4's cap bounds an
> end on a replacement slot and a cumulative duration elsewhere; on a pause
> slot it bounds neither, because there is no authored duration for it to bound.

**Cuál es el problema.** Un pause-ad es una familia no-lineal (R12 lo enumera
como tal), así que R4.1 lo alcanza. El Publisher queda obligado a declarar un
valor que R31.2 declara sin significado. Si lo omite, R4.10 obliga al Player a
no presentar el aviso: la ventana de pausa deja de funcionar. Si lo declara, el
atributo es exactamente lo que DP-1.1 prohíbe —

> Constructs whose only admissible value matches the construct's default OR is
> fixed by another rule MUST NOT exist in the spec.

Los tres textos son irreconciliables tal como están: no hay lectura en la que
R4.1, R4.10, R31.2 y DP-1.1 sean todos verdaderos para un slot de pausa.

**Qué pasaría aguas abajo.** El capítulo de sintaxis tiene que decidir si el
atributo de duración máxima es obligatorio en la declaración de ventana de
pausa. Cualquiera de las dos decisiones deja una regla del propio documento sin
cumplir, y la que el generador tome por defecto (obligatorio, porque R4.1 es el
texto más explícito) produce ventanas de pausa que un validador marca como
conformes llevando un número que nadie usa — el escenario de "silent drift" que
DP-1.2 nombra. La otra decisión produce ventanas que R4.10 obliga a ignorar en
runtime.

**Severidad**: `bloqueante`.

---

### 5. Un tope de overlays concurrentes contra una regla que fija ese número en uno

**Dónde está**: `02-actors.md` (Publisher, sub-bullet de constraints) y
`04-use-cases.md` UC-03 ("Publisher intent" y decisión de D1), contra
`03-requirements.md` R22.1, R14.3 y DP-1.1.

**El texto literal.** `02-actors.md` lo lista entre lo que el Publisher declara:

> other slot-level constraints such as maximum overlay duration, **maximum
> number of concurrent overlays**, or mutually exclusive layouts.

UC-03 lo declara en la intención del Publisher y lo usa en la decisión del
Player:

> - Maximum number of concurrent overlays for this slot is bounded.
>
> **Player decision:** reads Publisher slot rules (allowed layouts, duration
> cap, concurrency cap). Selects a candidate whose presentation options conform
> to the allowed layouts and concurrency cap

R22.1 fija el número:

> **R22.1** (Player): At any instant `t`, the Player MUST keep at most ONE
> non-linear ad form active on the screen. The Player MUST NOT present two or
> more non-linear ad forms simultaneously.

Y R14.3 prohíbe introducir el constructo:

> **R14.3** (spec document): The specification MUST NOT introduce a construct
> that implies or requires the parallel (simultaneous) rendering of two or more
> non-linear ad forms.

**Cuál es el problema.** Un atributo "máximo de overlays concurrentes" sólo
tiene sentido si el máximo puede ser mayor que uno. R22.1 lo fija en uno para
toda esta edición, así que el único valor admisible está fijado por otra regla:
DP-1.1 lo prohíbe explícitamente. Y declararlo implica que la concurrencia es
expresable, que es lo que R14.3 prohíbe declarar. El modelo de actores y el caso
de uso central de los no-lineales piden los dos una capacidad que tres reglas
distintas cierran.

**Qué pasaría aguas abajo.** El generador tiene que producir el elemento de
declaración de slot. Si sigue a `02-actors.md` y a UC-03, emite un atributo de
concurrencia que viola DP-1.1, R14.3 y R22.1 en el mismo documento. Si sigue a
R22, la descripción del Publisher en el capítulo de actores queda prometiendo
un control que la sintaxis no ofrece, y UC-03 —que es el caso de uso central de
los no-lineales— describe una decisión del Player ("conform to ... concurrency
cap") contra un dato que no existe.

**Severidad**: `bloqueante`.

---

### 6. Los casos de uso declaran layouts que la enumeración cerrada no admite

**Dónde está**: `04-use-cases.md` UC-03 ("Publisher intent"), UC-04 ("Publisher
intent"), UC-09 y UC-13 ("Publisher intent" y opción 3), contra
`03-requirements.md` R12 y R12.2.

**El texto literal.** UC-03:

> Allowed layouts for this slot are restricted to a subset declared by the
> Publisher (e.g. banner, corner, L-shape, side-by-side, sidebar).

UC-04:

> Non-linear forms allowed concurrently with the linear ad, with a restricted
> layout set (e.g. banner only — no L-shape on top of a linear ad).

UC-09 y UC-13:

> One **device-agnostic** allowed-layout set for the slot, including
> side-by-side, L-shape / squeezeback, banner overlay, and full-screen takeover.

R12.2 lo prohíbe:

> **R12.2** (Publisher): Publishers declaring allowed layouts MUST use names
> drawn from the enumerated set, each of which maps 1:1 to an IAB-defined ad
> type or visual placement. Publisher-private layout names, and IAB values
> outside the enumerated set, MUST NOT appear in the allowed-layouts
> declaration on the slot.

La enumeración de R12 contiene `linear`, `overlay` (con corner/bug y
lower-third), `squeezeback` (con L-shape y side-by-side/double-box) y `pause`
(con `pause-fullscreen` y `pause-partial`). No contiene `banner` ni `sidebar`.

**Cuál es el problema.** Cuatro casos de uso declaran conjuntos de layouts
permitidos que un Publisher conforme no podría escribir. Y no es un descuido
sin historia: ADR 0004, en sus consecuencias, dice que esto ya se limpió —

> stale illustrative names outside the CTV catalogue (skyscraper, sidebar) were
> dropped from the ad-overlay context. Future ad-format edits MUST keep those
> pointers coherent with R12.

`sidebar` sigue en UC-03 y `banner` aparece en cuatro lugares. La limpieza que
el ADR declara hecha no se completó.

**Qué pasaría aguas abajo.** El capítulo de ejemplos de la spec generada va a
llevar declaraciones de slot con tokens que su propio capítulo de sintaxis
rechaza, porque los ejemplos se derivan de los casos de uso y la enumeración se
deriva de R12. Es el tipo de defecto que un implementador encuentra copiando el
ejemplo: escribe `allowedLayouts="banner"` y el validador lo rechaza.

**Severidad**: `bloqueante`.

---

### 7. Un `full-screen takeover` como opción dentro de un slot no-lineal

**Dónde está**: `04-use-cases.md` UC-09 y UC-13 (opción 4, y el resultado de D2
y D5), contra `03-requirements.md` R12 (entrada **Linear**) y R20.4.

**El texto literal.** UC-09 declara el slot como no-lineal y pone el takeover
entre sus opciones:

> **Publisher intent:**
> - Non-linear forms allowed.
> - One **device-agnostic** allowed-layout set for the slot, including
>   side-by-side, L-shape / squeezeback, banner overlay, and full-screen
>   takeover.
>
> 4. **Full-screen takeover video** — a linear-style video ad that replaces the
>    primary content for the slot, played sequentially (primary stops, ad
>    plays, primary resumes).

R12 lo clasifica en la familia lineal:

> A full-screen takeover is the `linear` full-viewport rendering offered as a
> fallback presentation option for a candidate whose richer non-linear options
> are not renderable on the device (see UC-09 …); it is a placement of the
> `linear` type, not a separate ad type.

Y R20.4 dice qué hacer con un documento de resolución cuya familia no coincide
con el slot:

> **R20.4** (Player): A resolution document whose family does not match the
> slot that requested it is not a resolution of that slot. The Player MUST
> treat it as a failure to resolve and continue down the chain of R20.1.

**Cuál es el problema.** El takeover es de la familia lineal según R12, y
aparece como opción de un candidato servido para un slot no-lineal. Hay tres
preguntas que ningún requerimiento contesta. Primero, si el conjunto de layouts
permitidos de un slot no-lineal puede contener un placement de la familia
lineal, cosa que R12.2 no habilita ni prohíbe. Segundo, si R20.4 alcanza al caso
— un documento cuyo único candidato renderizable es de otra familia es,
leyéndolo literalmente, una falla de resolución, y entonces D2 y D5 no deberían
ver el takeover sino caer a la ventana siguiente. Tercero, qué acota el cap
mientras el takeover está en pantalla: R4.2 (duración acumulada, familias
no-lineales) o R4.6 (semántica de clip, replacement lineal).

Vale la pena notar que ADR 0002 trata al takeover como uno de los layouts
no-lineales — "The core SGAI spec offers a fixed set of layouts for non-linear
ads: overlay, side-by-side / double-box (R26), L-shape / squeezeback (R27), and
full-screen takeover" —, lo que confirma que las dos lecturas conviven en el
proyecto.

**Qué pasaría aguas abajo.** El resultado de dos de las cinco clases de
dispositivo en dos casos de uso (D2 y D5 en UC-09 y UC-13) depende de esta
pregunta. Una spec generada que aplique R20.4 literalmente describe un
comportamiento observable distinto del que los casos de uso declaran, y la tabla
de coverage de `04-use-cases.md` queda contradiciendo el capítulo de
comportamiento del Player.

**Severidad**: `bloqueante`.

---

### 8. "Family" gobierna el fallback y su enumeración deja afuera a squeezeback

**Dónde está**: `03-requirements.md` R20 (prosa), contra R12 y contra
`06-naming-and-namespaces.md` ("A family name and a layout token are different
things").

**El texto literal.** R20 enumera las familias entre paréntesis, de pasada:

> How the Player handles **multiple overlapping opportunity windows of the same
> family in the primary `MPD`** (the families are linear, overlays, and pause
> ads — each family is a category of ad).

R12 enumera cuatro tipos de aviso, no tres:

> - **Linear** (IAB *Linear Ad*, `linear`) …
> - **Overlay** (IAB *Overlay*, `overlay`) …
> - **Squeezeback** (IAB *Squeezeback*, `squeezeback`) …
> - **Pause-ad** (IAB *Pause Ad*, `pause`) …

Y `06-naming-and-namespaces.md` define familia de una manera que excluye a la
lineal:

> A **family** is a kind of non-linear ad opportunity; a **layout token** is
> one spatial arrangement inside a rendering frame

**Cuál es el problema.** "Family" es el término del que dependen R20 (qué
ventanas compiten y cuál es fallback de cuál), R20.4 (cuándo un documento de
resolución es de la familia equivocada), R17 (prioridad entre familias) y R31.
Nunca se define en el glosario, y los dos lugares donde el conjunto se enumera
dan conjuntos distintos: R20 dice tres e incluye la lineal, `06` dice que una
familia es una clase de oportunidad **no-lineal**, y R12 enumera cuatro tipos
sin decir cuántas familias forman. Un `squeezeback` no tiene familia asignada en
ningún lado: no se sabe si una ventana de L-shape y una de corner-overlay son
"la misma familia" a los efectos de R20.

**Qué pasaría aguas abajo.** El capítulo que especifique la cadena de fallback
tiene que decir cuándo dos ventanas son de la misma familia, y no tiene la
información. Si el generador asume que overlay y squeezeback son la misma
familia, dos ventanas superpuestas de esos tipos forman una cadena de fallback y
la segunda nunca se sirve mientras la primera resuelva. Si asume que son
distintas, las dos pueden estar activas a la vez, y eso choca de frente con
R22.1. Las dos lecturas producen comportamientos observables opuestos, y el
texto admite las dos.

**Severidad**: `bloqueante`.

---

### 9. Cuatro placements admitidos no tienen token, y el único ejemplo del repo inventa dos

**Dónde está**: `03-requirements.md` R12 y R12.1, contra
`06-naming-and-namespaces.md` ("Preferred encoding patterns").

**El texto literal.** R12.1 exige que los valores aceptados sean exactamente los
enumerados:

> **R12.1** (spec document): The accepted ad-type and visual-placement values
> are exactly those enumerated in this requirement, each mapped to its IAB
> definition. The spec MUST NOT accept a value outside the enumeration

Pero la enumeración da forma de token sólo para los cuatro tipos (`linear`,
`overlay`, `squeezeback`, `pause`) y para los dos placements de pausa
(`pause-fullscreen`, `pause-partial`). Para los otros cuatro placements da
nombres en prosa:

> Its named visual placements are corner / bug (IAB *Corner Overlay*) and
> lower-third (IAB *Lower-Third Overlay*)
>
> Supported placements are L-shape / squeezeback (IAB *L-Shape*; see R27) and
> side-by-side / double-box (IAB *Double Box Video* and *Double Box Video +
> Background*; see R26).

Y el único ejemplo escrito del repo, en `06-naming-and-namespaces.md`, inventa
dos tokens que no están en ningún lado:

> ```xml
> <svta:OverlayPresentation allowedLayouts="overlay-corner overlay-lower-third"/>
> ```

**Cuál es el problema.** R12.1 dice que los valores aceptados son "exactamente
los enumerados", y para cuatro de los diez placements no hay valor enumerado:
hay una descripción con barra ("corner / bug", "side-by-side / double-box"), que
no es un token XML. El ejemplo de `06` resuelve el hueco inventando
`overlay-corner` y `overlay-lower-third`, que es exactamente lo que ese mismo
archivo prohíbe dos secciones más arriba ("no publisher-private or spec-private
layout names are admissible").

**Qué pasaría aguas abajo.** El capítulo de sintaxis tiene que emitir la lista
de valores del atributo de layouts permitidos. Como cuatro valores no existen, el
generador los va a acuñar — probablemente copiando el estilo del ejemplo de `06`
—, y el resultado es un vocabulario inventado por la herramienta, no decidido
por nadie, que además no puede mapearse 1:1 a un nombre IAB porque el nombre IAB
("Corner Overlay") no es el token. Cualquier corrección posterior rompe todos los
MPD de ejemplo y todas las implementaciones de prueba.

**Severidad**: `bloqueante`.

---

### 10. Dos casos de uso dependen de composición concurrente lineal + no-lineal que ningún requerimiento define

**Dónde está**: `04-use-cases.md` UC-04 ("Hybrid linear + concurrent overlay") y
UC-14 ("A non-linear ad over a replacement that is not advertising"), contra
`03-requirements.md` R14, R17, R20 y R22.

**El texto literal.** UC-04 declara la intención del Publisher:

> - Linear forms allowed for the take-over portion.
> - Non-linear forms allowed concurrently with the linear ad, with a restricted
>   layout set …
> - Maximum break duration is bounded.
>
> **Ad response:** … The two responses are independent: the ADS does not
> cross-reference one against the other.

UC-14 hace lo mismo con un slate de blackout debajo:

> - A `ReplacePresentation` window over the blacked-out span, resolving to the
>   Publisher's own slate rather than to an ad decision.
> - An overlay opportunity window covering the same span

Del lado de los requerimientos, R22 acota sólo las formas no-lineales entre sí:

> **R22.1** (Player): At any instant `t`, the Player MUST keep at most ONE
> non-linear ad form active on the screen.

R20 arbitra sólo ventanas de la misma familia, R17 define prioridad entre
familias únicamente para la pausa (sobre overlay en R17.1, sobre lineal en
R17.5), y R14 secuencia candidatos dentro de un slot.

**Cuál es el problema.** UC-04 y UC-14 necesitan que una ventana lineal y una
no-lineal estén activas **a la vez**, resolviéndose de forma independiente, y
ninguna regla lo autoriza ni lo describe. Faltan cuatro cosas concretas: cómo
declara el Publisher un slot con dos porciones (o dos ventanas solapadas de
familias distintas y qué las vincula); qué acota el "maximum break duration"
cuando las dos porciones corren en paralelo, dado que R4.2 habla de duración
acumulada de los candidatos aceptados y acá la suma de las dos porciones no es
la duración del break; si el overlay sobre un aviso lineal cuenta contra el cap
del lineal o contra uno propio; y qué pasa si la porción no-lineal sobrevive al
final de la porción lineal. ADR 0013 confirma que el hueco existe y que sólo se
tapó para el caso de la pausa: "R17 … says nothing about a **linear** ad, because
R22 and the concurrency rules bound the non-linear families only".

**Qué pasaría aguas abajo.** Dos de los catorce casos de uso —uno de ellos el
caso híbrido que se usa para justificar la aritmética de decodificadores de
ADR 0012— no son derivables de los requerimientos. El generador va a inventar el
constructo de slot híbrido, o va a escribir el capítulo del caso de uso sin
poder citar un requerimiento, y en cualquiera de los dos casos la trazabilidad
requerimiento → caso de uso queda rota justo donde más se la va a mirar.

**Severidad**: `bloqueante`.

---

## Riesgos

### 11. UC-05 acota la duración de un pause-ad que R31 declara inacotable

**Dónde está**: `04-use-cases.md` UC-05, "Publisher intent", último bullet,
contra `03-requirements.md` R31 y R16.

**El texto literal.** UC-05:

> - Maximum display duration before automatic dismissal is bounded.

R31:

> How long the resulting slot lasts is determined entirely by the viewer and is
> unbounded and unknowable when the document is authored.
>
> Every other slot family this specification defines has a duration the
> Publisher can declare. A pause slot does not.

R16 fija el único evento que lo termina:

> A pause-ad form … is admissible only while the primary content is paused. When
> the viewer resumes primary playback, the Player dismisses any active pause-ad
> form immediately

**Cuál es el problema.** UC-05 describe un "automatic dismissal" al llegar a una
duración máxima declarada. R31 dice que no hay duración declarable y R16 dice
que lo que descarta el aviso es el resume del espectador, no un temporizador.
R32 confirma la otra lectura: cuando los candidatos se agotan y la pausa sigue,
lo que pasa es `repeat` / `request-again` / `stop`, no un auto-dismissal.

**Qué pasaría aguas abajo.** El capítulo del ciclo de vida del pause-ad puede
salir con un temporizador de descarte que ningún requerimiento manda y que
contradice a R32: agotados los candidatos, la spec diría a la vez "aplicá el
comportamiento declarado por el APS" y "descartá al llegar al máximo".

**Severidad**: `riesgo`.

---

### 12. La introducción promete formas que la enumeración cerrada excluye

**Dónde está**: `01-intro.md`, primer párrafo, contra `03-requirements.md` R12 y
OOS-5.

**El texto literal.** `01-intro.md`:

> adding the constructs required to cover non-linear ads — overlays,
> side-by-side, pause ads, L-shapes, banners, fullscreen interactive layers —
> under the same architecture.

R12 cierra el conjunto en cuatro tipos y OOS-5 excluye lo interactivo:

> **OOS-5. Interactive ad frameworks.** An ad built on an interactive framework
> such as SIMID is delivered by that framework, not by this specification: SIMID
> is not among the ad types R12 enumerates, and this edition defines no
> non-linear form that carries a SIMID payload.

**Cuál es el problema.** El primer párrafo del documento que define el alcance
nombra dos formas —`banners` y `fullscreen interactive layers`— que el
requerimiento de alcance excluye. `banners` puede leerse como el tipo base
`overlay`, pero "fullscreen interactive layers" no tiene lectura compatible con
OOS-5.

**Qué pasaría aguas abajo.** El resumen ejecutivo de la spec generada va a
prometer capas interactivas a pantalla completa, y el capítulo de alcance las va
a excluir. Es el primer párrafo que lee cualquiera del WG.

**Severidad**: `riesgo`.

---

### 13. Un perfil que identifica el documento no-lineal, y una regla que dice que no lo hay

**Dónde está**: `06-naming-and-namespaces.md` ("A family name and a layout token
are different things"), contra `08-dash-extension-rules.md` DR-10.

**El texto literal.** `06`:

> Names of documents, elements and profile URIs that serve **the whole
> non-linear family** — the resolution document, its root element, the profile
> URI that identifies it — take the **family** reading.

DR-10:

> **The non-linear resolution document therefore declares no profile**, and the
> cost of that is stated rather than hidden … Minting a profile URI for it is a
> decision this specification has not taken

**Cuál es el problema.** `06` da por sentado que existe un profile URI que
identifica al documento de resolución no-lineal, y le fija una regla de
nomenclatura. DR-10 dice que ese URI no existe y que acuñarlo es una decisión no
tomada. Un generador que lea `06` va a acuñarlo para poder aplicar la regla.

**Qué pasaría aguas abajo.** La spec puede salir declarando un
`urn:svta:dash:...` en `MPD@profiles` del documento de resolución no-lineal, que
es precisamente la decisión que DR-10 dice que nadie tomó, con las obligaciones
que arrastra (definir las restricciones, publicar el URI, conseguir que los
implementadores lo declaren).

**Severidad**: `riesgo`.

---

### 14. Se prohíben los nombres de layout privados de la spec, y R12 acuña dos

**Dónde está**: `06-naming-and-namespaces.md` ("Layout vocabulary"), contra
`03-requirements.md` R12 (entrada **Pause-ad**).

**El texto literal.** `06`:

> The accepted layout names for overlay templates are defined and maintained by
> the IAB, not by this spec. The spec MUST reference those IAB-defined values
> without inventing new layout names at chapter level. … the layout vocabulary
> MUST map 1:1 to IAB-defined ad-type values; no publisher-private or
> spec-private layout names are admissible.

R12:

> Its two visual placements are **fullscreen** (`pause-fullscreen`), occupying
> the entire screen surface, and **partial overlay** (`pause-partial`)

**Cuál es el problema.** A diferencia de los placements de `overlay` y
`squeezeback`, que R12 mapea a un nombre IAB explícito (*Corner Overlay*,
*L-Shape*, *Double Box Video*), los dos de pausa no citan ningún nombre IAB:
son tokens acuñados por esta especificación. `06` los prohíbe.

**Qué pasaría aguas abajo.** Un capítulo de sintaxis que aplique la regla de `06`
tiene que sacar `pause-fullscreen` y `pause-partial` del vocabulario, y sin ellos
R21 se cae: R21 dice explícitamente que la separación de los dos placements es
lo que le permite al Publisher admitir uno y excluir el otro en
`@allowedLayouts`.

**Severidad**: `riesgo`.

---

### 15. El cap aplicado como suma acumulada también en replacement

**Dónde está**: `05-dash-linear-interfaces.md` (paso 7 del flujo, y la
explicación del ListMPD), contra `03-requirements.md` R4.6 y R4.2.

**El texto literal.** `05`:

> 7. Player **enforces** the cumulative duration cap (R4): if the sum of the
>    candidates it chose exceeds `@maxDuration`, the Player terminates the last
>    ad at the cap (the spec mandates trim, §5.16.5).
>
> - The Player enforces R4 against the **sum** of the periods' durations versus
>   `@maxDuration` on the parent SGAI event: 15 + 30 = 45 s in this example.

R4 dice que eso vale para una de las dos operaciones lineales y no para la otra:

> - **Replacement** (`ReplacePresentation`) — the cap bounds **until when**.
>   `@clip`, whose default is `"true"`, makes the alternative presentation
>   *"terminate at the latest at time PRT + APDmax"*, the end the Publisher
>   scheduled, whatever time the event actually fired. Starting late therefore
>   shortens the ad instead of moving the end.
> - **Insertion** (`InsertPresentation`) — the cap bounds **how long**.

**Cuál es el problema.** El documento de referencia de la interfaz lineal
describe el cap de forma uniforme, como una suma de duraciones contra
`@maxDuration`, y el ejemplo que da es un `ReplacePresentation` con
`clip="true"`. En replacement el cap acota el **fin programado**, no la suma: un
evento que dispara tarde tiene que recortar el aviso aunque la suma de las
duraciones no llegue al cap. `05` describe el comportamiento equivocado para la
mitad de los slots lineales.

**Qué pasaría aguas abajo.** El capítulo de ejecución puede salir con una sola
aritmética de cap, la de la suma, que es la que `05` describe y la que el
ejemplo ilustra. El resultado es un Player que en un replacement que arranca
tarde termina más tarde que el fin programado, y lo que se corre es el retorno
al contenido principal, que es exactamente lo que `@clip` existe para evitar.

**Severidad**: `riesgo`.

---

### 16. DP-2 dice que la spec no enumera prohibiciones, y hay 38

**Dónde está**: `03-requirements.md`, "Design principles", DP-2, contra el resto
del propio archivo.

**El texto literal.** DP-2:

> **DP-2. Obligations are positive.** When the spec states what an actor MUST
> do, it states the positive obligation — the action, the construct, the value.
> The spec does NOT enumerate prohibitions. … (For example: instead of saying
> "the Player MUST NOT fire tracking beacons after the slot end," say "the
> Player MUST fire tracking beacons within the slot window.")

La medición: `grep -c 'MUST NOT' context/03-requirements.md` devuelve **38**.

**Cuál es el problema.** El principio dice que la especificación no enumera
prohibiciones y el archivo que lo contiene tiene treinta y ocho. Algunas son
inevitables y correctas (R1.3 "MUST NOT alter or override the semantics of any
pre-existing construct" es una obligación sobre el documento, no sobre un
actor), pero muchas son exactamente el patrón que el ejemplo de DP-2 dice cómo
dar vuelta (R5.6 "an option that fails either MUST NOT be rendered", R19.2 "The
Player MUST NOT force an ad to 1x").

**Qué pasaría aguas abajo.** Un principio de diseño que el propio conjunto de
requerimientos no cumple no le sirve al generador para decidir nada: cuando
tenga que elegir entre escribir una obligación positiva o una prohibición, el
ejemplo mayoritario le va a decir una cosa y el principio la contraria. El
riesgo real no es estilístico sino de cobertura: DP-2 justifica no enumerar
prohibiciones porque "the space of what is forbidden is unbounded", y una spec
con 38 MUST NOT parciales invita a leer lo no prohibido como permitido.

**Severidad**: `riesgo`.

---

### 17. El documento canónico del modelo de actores no tiene un solo modal

**Dónde está**: `02-actors.md` completo, contra `03-requirements.md` R2.

**El texto literal.** `02-actors.md` se declara normativo y canónico:

> Each actor has a clearly bounded set of responsibilities, and the separation
> is normative … This document is the canonical statement of that model and is
> mirrored verbatim in the working doc.

La medición: `02-actors.md` contiene **0** apariciones de `MUST`, **0** de
`SHOULD` y **1** de `MAY`. Todas sus responsabilidades están escritas como
bullets descriptivos: "Signal ad opportunities in the primary timeline by
emitting events in the main MPD", "Receive the ad request and decide **how
many** ads to return".

Y R2, que es el requerimiento que lo invoca, también usa minúscula:

> The design must enforce the separation defined in the Actors and
> Responsibilities section

**Cuál es el problema.** El proyecto declara usar RFC 2119 —cada ADR abre con
"This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY)"— y el documento
que fija quién puede hacer qué no tiene ningún modal. Un implementador no puede
saber si "the Publisher decides whether the slot is a linear replacement, a
linear insertion, or a non-linear opportunity" es una obligación o una
descripción de cómo suele pasar. Los criterios R2.1–R2.4 rescatan cuatro de esas
frases y las convierten en MUST; el resto del documento queda sin fuerza, y ahí
viven el reparto de autoridad sobre el tracking, la regla de que el ADS no valida
contra las constraints, y el bullet de selección del hallazgo 3.

**Qué pasaría aguas abajo.** El capítulo de actores de la spec generada va a
mezclar prosa descriptiva con obligaciones, sin que se pueda distinguir cuál es
cuál, y el capítulo de conformidad sólo va a poder testear lo que R2.1–R2.4
rescataron. Todo lo demás del modelo de actores queda fuera de la superficie
auditable.

**Severidad**: `riesgo`.

---

### 18. No se sabe contra qué reloj se recorta un aviso

**Dónde está**: `03-requirements.md` R4.5, contra R19.3 y R4.11.

**El texto literal.** R4.5:

> **R4.5** (Player): When the actual rendered length of an accepted candidate
> exceeds its declared duration, the Player MUST enforce the cap against actual
> length, not declared length ("trim during play").

R19.3 y R4.11 dicen sobre qué línea de tiempo corre la aritmética:

> **R19.3** … cap enforcement (R4) and beacon scheduling (R13) operate on the
> presentation-timeline `duration`, while wall-clock on-screen behaviour
> follows the derived value.
>
> **R4.11** (Player): Cap arithmetic runs on the presentation timeline.

**Cuál es el problema.** "Actual rendered length" es exactamente la magnitud que
R19 dice que difiere entre las dos líneas de tiempo: a 2x, un aviso de 10 s de
presentación tiene una longitud renderizada de 5 s de reloj de pared. R4.5 no
dice cuál de las dos mide, y es el único criterio de R4 que habla de longitud
"actual" en vez de declarada.

**Qué pasaría aguas abajo.** Un implementador que lea R4.5 sin leer R19.3 mide
en reloj de pared y recorta los avisos a la mitad cuando el espectador mira a
2x, o al doble cuando mira a 0.5x. Los dos comportamientos pasan el criterio tal
como está escrito. Es el tipo de defecto que no aparece en ningún test hasta que
alguien prueba trick-play, y UC-02 tiene una variante de trick-play que lo
ejercita sin resolver la ambigüedad.

**Severidad**: `riesgo`.

---

### 19. Un atajo que evita la request de resolución que R31.1 declara obligatoria

**Dónde está**: `04-use-cases.md` UC-08, "Ad response", contra
`03-requirements.md` R31.1.

**El texto literal.** UC-08:

> On pause-ad trigger, the Player resolves the APS again for the pause-ad slot
> (which consults the ADS) per the UC-05 flow, **unless the Publisher's MPD
> signals that the overlay candidate doubles as the pause-ad candidate**.

R31.1:

> **R31.1** (Player): The Player MUST request a resolution document when a
> viewer pause begins inside a pause opportunity window, and MUST NOT request
> one for a pause that begins outside every such window.

**Cuál es el problema.** El caso de uso introduce una excepción a un MUST sin
excepciones, y la excepción depende de una señal en el MPD —"the overlay
candidate doubles as the pause-ad candidate"— que ningún requerimiento define,
ningún constructo carga y ninguna regla de naming nombra. Es una capacidad
mencionada de pasada en una sola cláusula subordinada.

**Qué pasaría aguas abajo.** O el generador inventa el constructo de reuso de
candidato (que además cruza la frontera de familias del hallazgo 8: un candidato
de overlay sirviendo un slot de pausa es justo lo que R20.4 llama familia
equivocada), o escribe UC-08 omitiendo la cláusula, y entonces el caso de uso de
la spec no coincide con el de `context/`.

**Severidad**: `riesgo`.

---

### 20. Hay preguntas abiertas en los casos de uso y el registro de preguntas abiertas está vacío

**Dónde está**: `04-use-cases.md` UC-04 y UC-05 ("Notes / open questions"), y
`03-requirements.md` R4.10, contra la sección "Deliberately open" de
`03-requirements.md`.

**El texto literal.** La sección que existe para registrar esto:

> | Unit | Why it is open | Recorded in |
> |------|----------------|-------------|
>
> The table is empty, and that is a statement: **no silence in this
> specification has been declared deliberate yet.**

UC-04:

> - Whether the Publisher can express constraints linking the two portions of
>   the break … or whether such cross-portion linkage is out of scope. Either
>   answer is compatible with the four-actor model; **the spec must pick one**.

UC-05:

> - Whether the Player is allowed to pre-fetch pause-triggered candidates
>   speculatively when the manifest loads, or must defer the APS resolution
>   call to the moment of pause, is an open design decision …
> - Whether single-decoder devices (D3, D4) can re-task the decoder to play a
>   video form on top of a paused primary frame … is an open device capability
>   question.

Y R4.10, que es un criterio con un MUST NOT, se declara provisional:

> **This position is provisional.** It diverges from the base specification …
> and it is open with the working group rather than settled here. … A reader
> finding this criterion should not take it as closed.

**Cuál es el problema.** El mecanismo que la especificación se dio para
distinguir "nadie lo pensó" de "se decidió no contestarlo" está vacío y afirma
explícitamente que no hay silencios deliberados, mientras cuatro preguntas
abiertas viven dispersas en casos de uso y en un criterio de conformidad. La
propia sección explica por qué eso importa: "the absence of an entry says nothing
was chosen, and those are the two states a reader must be able to tell apart".

**Qué pasaría aguas abajo.** Cada una de esas preguntas llega al generador como
texto en prosa dentro del documento que tiene que convertir en spec. La de UC-05
sobre el re-tasking del decodificador es peor que abierta: choca con R3.2, que
exige que todo Player de toda clase soportada produzca un comportamiento
definido para todo tipo de oportunidad. Una spec que deje eso abierto es
no-conforme con su propio R3.2.

**Severidad**: `riesgo`.

---

### 21. Dos mecanismos escriben query params en la misma request y no se habla el uno del otro

**Dónde está**: `03-requirements.md` R29, contra `05-dash-linear-interfaces.md`
(paso 4a y el ejemplo de `UrlParamInfo`).

**El texto literal.** R29 define un conjunto reservado y se aparta explícitamente
del mecanismo del caso base:

> These parameters are carried as query parameters on the resolution request.
> They are defined here and are NOT expressed through the MPD-declared
> URL-parameter template mechanism of MPEG-DASH 6th edition, whose contents are
> declared by the content author.

`05` describe la request de resolución como si el mecanismo del caso base fuera
el único:

> (4a) `GET <event @uri>` augmented with the query parameters declared by the
> `UrlParamInfo` descriptor on the MPD (§I.4)
>
> | Player | APS | HTTP/HTTPS | request: query params (§I.4); response: `ListMPD` (XML) |

**Cuál es el problema.** Las dos cosas van a la misma URL y nadie dice cómo
conviven. Faltan tres reglas: qué pasa si el `queryTemplate` del Publisher usa un
nombre que coincide con un nombre reservado de R29; en qué orden se concatenan;
y si `@includeInRequests="altmpd"` —que es lo que scopea el descriptor a la
request de resolución— tiene algo que ver con los parámetros de R29, que el
Player manda sin que nadie los declare ("no declaration by the Publisher, the
APS or the ADS is required before a Player sends them").

**Qué pasaría aguas abajo.** El capítulo que especifique la request de
resolución va a describir un solo mecanismo, y el otro va a aparecer en los
ejemplos. La colisión de nombres queda sin resolver, que es justo el escenario
que R29.4 anticipa para los parámetros de terceros ("A parameter that is not one
of the reserved names MUST carry a vendor-specific prefix") y no para los del
propio Publisher.

**Severidad**: `riesgo`.

---

### 22. "Resolution document" aparece 115 veces y no está definido

**Dónde está**: `99-glossary.md` (ausencia), contra todo el conjunto.

**El texto literal.** El término no tiene entrada propia. Lo más parecido a una
definición vive dentro de la entrada del APS, y define por enumeración de casos
de uso:

> converts whatever the ADS emits … into the MPD-native / SGAI resolution
> document** the Player understands (`ListMPD` or single-period alternative MPD
> for linear, the overlay resolution document for non-linear)

**Cuál es el problema.** Es el objeto central de la especificación —la única
cosa que el APS produce y el Player consume, y contra la cual se chequea la
conformidad en R5.1, R12.3, R13.1, R15.2, R28.1 y R30.1— y se define diciendo
para qué se usa en cada familia, no qué es. Lo que queda sin fijar es
sustantivo: si "resolution document" es un tipo de documento con una raíz común
y una familia declarada, o un nombre paraguas para tres documentos distintos sin
nada en común. R20.4 depende de la primera lectura, porque exige que el Player
compare la familia del documento con la del slot, y eso requiere que el documento
declare su familia. La única otra pista es el circunloquio de
`06-naming-and-namespaces.md` sobre "the resolution document, its root element,
the profile URI that identifies it", que DR-10 contradice (hallazgo 13).

**Qué pasaría aguas abajo.** El capítulo de anatomía del documento de resolución
tiene que empezar diciendo qué es, y no lo tiene. El generador va a elegir una de
las dos lecturas, y si elige la del paraguas, R20.4 queda sin forma de
implementarse.

**Severidad**: `riesgo`.

---

### 23. "Overlay" es a la vez el paraguas y uno de sus miembros

**Dónde está**: `99-glossary.md`, entradas **Overlay** y **Non-linear ad**, y
`04-use-cases.md`, tabla "Terminology".

**El texto literal.** El glosario define Overlay como paraguas:

> **Overlay**: umbrella term for any non-linear ad surface (a surface
> composited on top of the primary content, or a squeezeback that shrinks the
> primary content to share the frame).

y en la misma entrada lo lista como hermano de squeezeback:

> The subset this edition supports is enumerated in R12 …: overlay (corner /
> bug, lower-third), squeezeback (L-shape, side-by-side / double-box), and
> pause-ad.

Y la tabla de terminología de `04-use-cases.md` define no-lineal de una forma
que excluye al squeezeback:

> | Non-linear ad | An ad whose form is composited on top of the primary content during a slot |

mientras el glosario lo define de otra:

> **Non-linear ad**: ad that *coexists* with the primary content; it does not
> interrupt playback. Rendered as an overlay or as a side-by-side composition.

**Cuál es el problema.** `06-naming-and-namespaces.md` identifica el problema y
da la regla — "A **family** is a kind of non-linear ad opportunity; a **layout
token** is one spatial arrangement … `overlay` is a member of both vocabularies"
— pero la regla no se aplicó al glosario, que es donde el lector va a buscar. Dos
lectores del glosario entienden cosas distintas por "overlay": uno lee "cualquier
superficie no-lineal" y el otro lee "corner/bug o lower-third". Y la tabla de
terminología de los casos de uso define no-lineal como "composited on top", que
deja al squeezeback y al side-by-side afuera de la definición aunque R12 los
enumere adentro.

**Qué pasaría aguas abajo.** Cada aparición de "overlay" en la spec generada
hereda la ambigüedad, incluida la de R20 ("the families are linear, overlays,
and pause ads") que es donde ya produjo el hallazgo 8. Y una definición de
no-lineal como "compuesto encima" hace que el capítulo de squeezeback contradiga
el capítulo de definiciones.

**Severidad**: `riesgo`.

---

### 24. "Legacy Player" aparece 42 veces y no está definido

**Dónde está**: `99-glossary.md` (ausencia), contra R1, R1.1, UC-07,
`07-backward-compat-checklist.md` y `05-dash-linear-interfaces.md`.

**El texto literal.** R1 lo define de una manera:

> a Player that does not implement the new mechanisms introduced by this
> proposal MUST skip them

UC-07 de otra:

> A Player implementation that **predates this proposal** receives a manifest
> that uses the new SGAI mechanisms

**Cuál es el problema.** Las dos lecturas difieren en un punto caro: si "legacy"
significa "no implementa SGAI no-lineal pero sí la 6ª edición", o "es anterior a
todo esto y puede no implementar la 6ª edición". La diferencia decide qué
constructos cuentan como seguros. El ejemplo de `05-dash-linear-interfaces.md`
cae del lado caro: declara
`profiles="urn:mpeg:dash:profile:advanced-linear:2025"` y cuelga un
`<EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">` al nivel del MPD.
Bajo la segunda lectura, un Player que no conoce §I.4 aplica la regla que DR-9
cita —*"the DASH Client is expected to ignore the parent element that contains
the descriptor"*— y el padre es el MPD entero. Bajo la primera lectura no pasa
nada, porque §I.4 es de la 6ª edición y el Player la implementa.

**Qué pasaría aguas abajo.** El capítulo de compatibilidad y el checklist por
constructo de `07` prueban contra un "legacy Player" cuya capacidad nadie fijó.
El resultado es una batería de tests cuyo criterio de aprobación depende de qué
Player eligió el que la corre, que es la definición de un test que no puede
fallar de forma informativa.

**Severidad**: `riesgo`.

---

## Menores

### 25. UC-07 le impone un SHOULD al Publisher que ningún requerimiento carga

**Dónde está**: `04-use-cases.md` UC-07, y `07-backward-compat-checklist.md`
paso 5.

**El texto literal.**

> The Publisher SHOULD treat the opportunity as a loss on legacy Players
>
> **Non-live / VOD content** → the Publisher MAY (and SHOULD, where monetising
> the opportunity matters) author a **standard linear break** alongside the
> SGAI construct

**Cuál es el problema.** Es una obligación RFC 2119 sobre el Publisher —
authorear un break lineal estándar como fallback para VOD — que vive sólo en un
caso de uso. Ningún requerimiento la carga: R1 y sus cuatro criterios no la
mencionan. Un caso de uso describe comportamiento esperado; no es el lugar donde
un implementador busca sus obligaciones.

**Qué pasaría aguas abajo.** O la obligación se pierde al generar (el capítulo
de requerimientos no la tiene), o aparece en el capítulo de casos de uso con
fuerza normativa y sin requerimiento que la respalde, rompiendo la trazabilidad.

**Severidad**: `menor`.

---

### 26. El checklist mezcla tres fuerzas para la misma idea

**Dónde está**: `07-backward-compat-checklist.md`.

**El texto literal.** Tres formas de decir lo mismo:

> Unanswered items SHOULD block publication.
>
> A `FAIL` in any column blocks publication.
>
> The classification MUST be stated explicitly in the construct's chapter —
> leaving it implicit is a checklist failure.

**Cuál es el problema.** El documento se declara "the checklist the spec MUST
follow", y después dice que un ítem sin contestar *debería* bloquear, que un FAIL
bloquea (en indicativo, sin modal), y que una omisión "is a checklist failure"
(descriptivo). Un lector no sabe si el checklist es una puerta o una
recomendación.

**Qué pasaría aguas abajo.** El capítulo de conformidad puede salir con un
checklist cuya condición de bloqueo es opcional, que es equivalente a no tenerla.

**Severidad**: `menor`.

---

### 27. R32.1 exige declarar y a la vez define el default de la ausencia

**Dónde está**: `03-requirements.md` R32.1.

**El texto literal.**

> **R32.1** (APS): A resolution document for a pause slot MUST declare which of
> the three behaviours applies. Absent the declaration, the Player MUST apply
> `stop`.

**Cuál es el problema.** Si declararlo es obligatorio, la ausencia es
no-conformidad y el default es inalcanzable en un documento conforme; si hay
default, la declaración es opcional y el MUST sobra. La prosa de R32 empuja hacia
la segunda lectura ("`stop` is the default"), el criterio hacia la primera.

**Qué pasaría aguas abajo.** El capítulo de sintaxis tiene que decidir si el
atributo es `mandatory` u `optional with default`, y las dos decisiones
contradicen la mitad de R32.

**Severidad**: `menor`.

---

### 28. Una negación malformada de RFC 2119

**Dónde está**: `03-requirements.md` R2.2 y R5.4.

**El texto literal.**

> Neither MUST be expected to enforce Publisher-declared constraints (e.g. slot
> duration cap).
>
> **R5.4** (ADS + APS): Neither the ADS nor the APS MUST be required to maintain
> a device-class matrix or a per-Player capability view to produce candidates.

**Cuál es el problema.** "Neither MUST be expected" y "MUST be required" no son
construcciones de RFC 2119. Lo que quieren decir —"no están obligados a"— se
escribe sin MUST, o como una obligación sobre el documento ("The specification
MUST NOT require the ADS or the APS to …"). Tal como están, se pueden leer como
prohibiciones sobre quien espera o requiere, que no es un actor.

**Qué pasaría aguas abajo.** Un extractor de obligaciones que busque MUST las va
a levantar como obligaciones de ADS y APS, que es lo contrario de lo que dicen.
Si la validación de la spec se hace contando obligaciones cubiertas, estas dos
entran con el signo cambiado.

**Severidad**: `menor`.

---

### 29. Editoriales

**Dónde está**: `04-use-cases.md` (encabezado), `03-requirements.md` R29.1,
`99-glossary.md` (entrada "Brand safety").

**El texto literal.** El encabezado de los casos de uso apunta a un rango de
requerimientos que ya no existe:

> see … [`03-requirements.md`](03-requirements.md) for R1–R10 that ground these
> scenarios.

R29.1 tiene una frase truncada:

> deriving the second from the first is the APS's.

Y la entrada "Brand safety" del glosario describe el prototipo en vez del
término:

> **Brand safety**: the requirement that the actual creative shown to a viewer
> satisfies the Publisher's policy on prohibited content. In the
> AI-generated-ads pipeline that the prototype experiments with, brand safety
> becomes an explicit pipeline stage …

**Cuál es el problema.** El rango R1–R10 quedó viejo (hay 34 requerimientos), la
frase de R29.1 no termina, y la segunda mitad de la entrada del glosario habla de
un prototipo que no es parte de la especificación. La primera oración de "Brand
safety" sí define; la segunda es contexto de proyecto en un documento que
`CLAUDE.md` exige autocontenido.

**Qué pasaría aguas abajo.** Ruido menor en el documento generado. Ninguno de
los tres cambia una decisión de implementación.

**Severidad**: `menor`.

---

## Blancos honestos

Estas cosas se buscaron y no se encontraron, y vale decirlo:

- **No hay referencias colgadas entre requerimientos.** Se extrajeron los 34
  identificadores `RNN` definidos y las 557 apariciones de referencias `RNN` /
  `RNN.M` que hay en los diez archivos de `context/` — 157 identificadores
  distintos: todas resuelven. Lo mismo vale
  para las diez reglas `DR-N`, los catorce `UC-NN`, los cinco `DP-N` y los siete
  `OOS-N`. La numeración es consistente y la política de identificadores
  estables se está respetando.
- **No hay ninguna referencia desde `context/` hacia `context-analysis/`,
  `output/` o `output-analysis/`.** La regla de autocontención del `CLAUDE.md`
  se cumple. Las únicas referencias hacia afuera son a `.project/decisions/`,
  que la propia regla autoriza.
- **La aritmética de decodificadores y superficies es consistente.** R26.3,
  R27.3 y las cinco clases de dispositivo de `04-use-cases.md` dan el mismo
  resultado en los catorce casos donde se cruzan (UC-03, UC-04, UC-09, UC-10,
  UC-13, UC-14). Se verificó caso por caso; no se encontró ninguna celda donde
  la clase de dispositivo declarada no soporte lo que el caso de uso dice que
  renderiza. Esta parte está bien.
- **El tratamiento de la resolución vacía es coherente de punta a punta.** R30,
  R20.1, R32.2, UC-12 y la tabla de contratos de interfaz de `05` dicen todos lo
  mismo, con la misma cita del caso base. Es la parte del conjunto donde más se
  nota el trabajo de los ADR 0005 / 0010 / 0011.

---

## Cierre: ¿qué de esto lo puede encontrar un script?

**Conteo.** 29 hallazgos: **10 bloqueantes**, **14 riesgos**, **5 menores**. Por
tipo: 14 contradicciones, 6 obligaciones sin fuerza o mal formadas, 6 gaps, 2
ambigüedades de alcance, 3 definiciones que no definen (los totales se solapan
porque varios hallazgos son de dos tipos a la vez).

La pregunta de fondo era si conviene meter un paso de verificación de `context/`
**antes** de generar la spec. La respuesta es que sí, y que se puede hacer mucho
más de lo que parece, pero no todo. El reparto es este.

### Detectable por script, con alto rendimiento

Estas clases se detectan leyendo sólo `context/`, sin juicio y sin modelo:

- **Términos usados y no definidos** (hallazgos 22, 24, y la mitad del 8).
  Extraer los sustantivos técnicos que aparecen más de N veces y cruzarlos
  contra los encabezados del glosario. "resolution document" con 115 apariciones
  y "legacy Player" con 42, ninguno en el glosario, salen de un `grep` y una
  diferencia de conjuntos. El chequeo es barato y el falso positivo es fácil de
  silenciar con una lista de excepciones.
- **Vocabulario cerrado usado fuera de la enumeración** (hallazgo 6, y el 12
  parcialmente). R12 declara un conjunto cerrado; un script puede extraer los
  tokens de layout que aparecen en cualquier contexto de "allowed layouts" o
  "layout set" y verificar que cada uno esté en la enumeración. `banner` y
  `sidebar` caen en la primera corrida. Este chequeo es de alto valor porque el
  conjunto cerrado ya existe y es explícito: no hay que inferir nada.
- **Enumeración incompleta de tokens** (hallazgo 9). Si R12 declara diez
  placements y sólo seis tienen una forma `` `token` `` en backticks, la
  diferencia es contable.
- **Marcas RFC 2119 malformadas** (hallazgo 28). "Neither … MUST", "MUST be
  required", "MUST be expected" son patrones fijos; un `grep -E` los encuentra.
- **Fuerza normativa faltante por archivo** (hallazgo 17). Un archivo que se
  declara normativo y contiene cero MUST/SHOULD/MAY es una anomalía medible.
  `02-actors.md` con 0 modales y la frase "the separation is normative" es
  exactamente eso.
- **Conteo de prohibiciones contra DP-2** (hallazgo 16). DP-2 dice que la spec
  no enumera prohibiciones; contar `MUST NOT` es una línea. No decide si cada
  una está mal, pero un contador que diga "38" contra un principio que dice
  "ninguna" obliga a mirar.
- **Preguntas abiertas fuera del registro** (hallazgo 20). Buscar "open
  question", "the spec must pick one", "provisional", "TBD", "is an open" en
  `context/` y cruzarlo contra las filas de la tabla "Deliberately open". Una
  tabla vacía con cuatro marcadores sueltos es un fallo mecánico. Este es
  probablemente el chequeo de mejor relación costo/beneficio de toda la lista,
  porque el registro ya existe y sólo hay que hacerlo obligatorio.
- **Rangos de referencia desactualizados** (hallazgo 29). "R1–R10" cuando hay
  R34 es comparable contra el conjunto de identificadores definidos.
- **Términos prohibidos en material normativo** (hallazgo 1, parcialmente).
  R11.3 dice que toda referencia a VAST tiene que estar en un anexo o en una
  nota marcada como ilustrativa. Un script puede levantar las 90 apariciones de
  "VAST" en `context/` y verificar que cada una esté dentro de un bloque marcado.
  Hoy ninguna lo está. Este chequeo es especialmente bueno porque **el
  requerimiento mismo escribe la regla del chequeo**: R11.3 es una condición
  verificable tal como está redactada.

Nota importante sobre este grupo: el `CLAUDE.md` describe
`bin/check-context-coherence.py` como el paso 0.5 que "confirms that `context/`
holds together — identifiers defined, no duplicates, links resolving". No leí
ese script, así que no sé qué cubre exactamente. Pero lo que describe es el eje
**estructural** (identificadores, duplicados, links), y los hallazgos de esta
auditoría que caen ahí son cero: las referencias resuelven todas. Lo que falta es
un eje distinto —**vocabulario y fuerza normativa**— sobre los mismos archivos.
Es el mismo tipo de herramienta, con otras reglas.

### Detectable por script sólo si alguien escribe primero el modelo

Estas se pueden automatizar, pero antes hay que declarar en `context/` algo que
hoy está implícito:

- **Familias** (hallazgo 8). Si `context/` declarara, en un solo lugar, la tabla
  de familias y a qué familia pertenece cada tipo de R12, un script podría
  verificar que toda mención de "family" sea consistente y que ningún tipo quede
  sin familia. Sin esa tabla no hay nada contra qué comparar. **Esto es una
  recomendación concreta: la tabla de familias falta y es barata de escribir.**
- **Qué acota el cap en cada familia** (hallazgos 4, 15, 7). R4 ya explica la
  asimetría en prosa. Puesta como tabla (familia → qué acota el cap → criterio
  que aplica), un script verifica que cada familia tenga una fila y que ningún
  documento describa el cap de una forma distinta a la de su fila. El caso de la
  pausa —que hoy es la única familia sin fila posible— saltaría solo.
- **Matriz caso de uso × requerimiento** (hallazgos 5, 10, 19). Si cada bullet
  de "Publisher intent" y cada capacidad que un caso de uso ejercita tuviera que
  citar el requerimiento que la manda, un script podría marcar los bullets sin
  cita. "Maximum number of concurrent overlays for this slot is bounded" sin R
  que lo respalde, y la composición concurrente lineal + no-lineal de UC-04 sin
  requerimiento, aparecen de inmediato. Esto es una convención de autoría, no una
  heurística: el chequeo es un `grep` de "¿este bullet cita una R?".

### No detectable por script: necesita juicio

Estas requieren entender qué dicen dos frases y darse cuenta de que no pueden
ser ciertas a la vez:

- **El MAY de `02-actors.md` contra el MUST NOT de R7.4** (hallazgo 3). Las dos
  frases están bien formadas, usan modales correctos, citan las mismas tres
  operaciones y viven en archivos distintos. Ningún patrón sintáctico las une:
  hay que leer que "deduplication" en una lista de cosas permitidas y
  "deduplicate" en una prohibición son la misma cosa. Un LLM revisor lo ve; un
  `grep` no.
- **La promesa imposible de R1.1 contra DR-8** (hallazgo 2). Requiere entender
  que "legacy Player" y "Player que no implementa esta especificación" son el
  mismo sujeto, y que DR-8 le prohíbe a la spec obligarlo. Es un razonamiento de
  dos pasos sobre el significado, no sobre la forma.
- **El timebase ambiguo de R4.5** (hallazgo 18). "Actual rendered length" es una
  frase impecable. Lo que la hace ambigua es que R19 introduce dos líneas de
  tiempo y R4.5 no dice cuál. Detectarlo requiere saber que existe la distinción
  y notar que este criterio no la resuelve.
- **La definición de "Overlay" que es paraguas y miembro a la vez** (hallazgo
  23). Un script puede ver que "overlay" aparece en dos vocabularios; no puede
  ver que eso hace que dos lectores entiendan cosas distintas.
- **El perfil de `06` contra DR-10, y los tokens de pausa contra la regla de
  `06`** (hallazgos 13, 14). Las dos son contradicciones semánticas entre
  documentos, sin ningún token compartido que las delate.

### Recomendación

**Sí conviene el paso de verificación, y conviene que tenga dos mitades.**

La primera es un script, hermano del `check-context-coherence.py` que ya existe,
con las reglas del primer grupo. Lo que lo hace valioso no es que encuentre
mucho —encuentra unos diez de los veintinueve— sino que encuentra las clases que
**vuelven**: vocabulario que se sale de una enumeración cerrada, términos nuevos
sin definir, preguntas abiertas que no llegaron al registro. Son las que
reaparecen en cada edición de `context/`, y son las que un humano deja pasar
porque leer las 5.257 líneas de `context/` buscando un `sidebar` no es
trabajo de humano. El
hallazgo 6 es la prueba: ADR 0004 declara esa limpieza hecha, y `sidebar` sigue
ahí. Un chequeo lo habría visto el mismo día.

La segunda mitad es una revisión con juicio, y no se puede evitar: los cinco
hallazgos bloqueantes más caros —el MAY contra el MUST NOT, la promesa imposible
de R1.1, el cap de pausa, el tope de concurrencia y la concurrencia lineal +
no-lineal— son todos contradicciones semánticas entre documentos distintos, y
ninguno tiene una firma sintáctica. Lo que sí se puede hacer es **abaratarla**:
casi todos se vuelven mecánicos si `context/` declara tres cosas que hoy no
declara — la tabla de familias, la tabla de qué acota el cap por familia, y la
obligación de que cada bullet de "Publisher intent" cite su requerimiento. Con
esas tres, seis de los diez bloqueantes pasan del grupo de juicio al grupo de
script.

Y hay una asimetría que decide la prioridad: un defecto de `context/` no se
queda en `context/`. Se multiplica en cada capítulo de la spec que lo hereda, y
cuando se corrige hay que regenerar. El paso de verificación no se paga en los
defectos que encuentra sino en las generaciones que evita.
