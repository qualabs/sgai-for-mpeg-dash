# T-11 — El audit LLM contra lo que calculó el código

Compara `dist/dash-conformance-audit.md` (37 construcciones K-1..K-37, veredicto
LLM) con `conformance-tests.json` de esta carpeta (niveles 1, 2 y 3a sobre
`dist/sgai-spec.md`). Cada resultado se asigna a una construcción por lo que la
regla lee en su código (`bin/conformance/ext.py`, `dash/rules.py`,
`spec/checks.py`, `players.py`) y no por el nombre de la regla. Los bloques se
nombran `xml#N` como en el informe.

## Los números, verificados contra el json

Total: 2967 resultados. **PASS 1155, FAIL 8, NOT_VERIFIABLE 273,
NOT_APPLICABLE 1531**; la suma da 2967 y coincide con `counts` del json y con
el encabezado de `conformance-tests.md`. Hay 243 reglas: 196 de nivel 2 (R*) y
47 de niveles 1 y 3a.

Los 8 FAIL, todos de nivel 2:

| regla | sujeto | lugar | detalle |
|---|---|---|---|
| R12.1a | XSD de §5.10.1 | `RenderableAsset@layout` | falta `squeezeback-frame` |
| R12.1a | XSD de §5.10.1 | `OverlayPresentation@allowedLayouts` | falta `squeezeback-frame` |
| R12.1a | XSD de §5.10.1 | `PauseAdPresentation@allowedLayouts` | falta `squeezeback-frame` |
| R34.1a | XSD de §5.10.1 | `OverlayPresentation` | no puede llevar `@executeOnce` |
| R34.9a | XSD de §5.10.1 | `OverlayPresentation` | no puede llevar `@startWithOffset` |
| R13.6a | XSD de §5.10.1 | `RenderableAsset` | no puede llevar `Tracking` |
| R40.9a | xml#40 (G.3) | `EventStream[2]/Event[1]` | Event de `sgai-overlay` sin ventana |
| R40.9a | xml#40 (G.3) | `EventStream[3]/Event[1]` | Event de `sgai-pause-trigger` sin ventana |

Ningún resultado de nivel 1 (E-*, XSD-ID, DR-*, C07-*, K-*) ni de nivel 3a
(P-*) es FAIL.

## Construcción por construcción

Clases: **C** confirmada por código, **X** contradicha, **P** parcial, **S** sin
evidencia de código. "Ventanas" son los 17 MPD principales con
`OverlayPresentation` o `PauseAdPresentation`; "SPS" los 24 sub-MPD; "listas"
los 8 List MPD; "OverlayList" los 23 documentos `<svta:OverlayList>`.

| K | LLM | Lo que decide el código | Clase | Lo que no decide |
|---|---|---|---|---|
| K-1 | Conf | E-4 PASS 52 (todos los MPD siguen válidos contra el XSD de ISO tras quitar lo ajeno); E-2 PASS (namespace propio, sin redefine/override/include); C07-6b PASS 48 | C | E-4 valida contra el esquema y no el resto de "conforms to this document"; el audit tampoco afirma más |
| K-2 | Conf | E-3 PASS en los 14 MPD con el esquema overlay; K-4a PASS; P-LEGACY (dash.js y Shaka) PASS en esos 14, sin error y sin pedir URIs nuestras | P | Que la norma admita un esquema de aplicación es lectura. Los Players corren ~8 s: no llegan a la ventana, solo prueban que el MPD con el stream carga y reproduce |
| K-3 | Conf | Igual que K-2 sobre los 5 MPD con `sgai-pause-trigger`; R31.1 PASS 4 (la ventana declara `@duration`) | P | Que `@duration` como intervalo sea semántica del dueño del esquema (Table 44) es lectura |
| K-4 | Conf | K-4a PASS 33 (un EventStream por esquema y `@value` por Period); K-4b PASS 33 (`Event@id` único); R20.2a/R20.2b PASS 16 (un stream por familia, sin `@value`); E-3 PASS (tipos de `EventType`; un atributo ajeno en `EventStream` fallaría porque `EventStreamType` no abre `anyAttribute`) | C | — |
| K-5 | Conf | E-3 PASS 13 MPD con `OverlayPresentation` (hijo de `Event` por el `xs:any ##other`); E-4 PASS 13 | C | — |
| K-6 | Conf | E-3 PASS 4, E-4 PASS 4 con `PauseAdPresentation` | C | — |
| K-7 | Conf | E-1/E-3: `@durationCap` declarado en el XSD de extensión y válido en las 17 ventanas; R4.1 PASS 15 (presente en cada ventana) | C | Que no "acote nada" en pausa es semántica, fuera del juicio de conformidad |
| K-8 | Conf | R36.1a PASS 1: el XSD declara el atributo en las dos ventanas | S | Ninguna regla compara tipo y default con `AlternativeMPDEventType`. Lectura directa (no es regla): las dos declaraciones son `xs:unsignedLong` sin default de XSD, idénticas a la de ISO; el default de 60 s vive en la prosa de Table 63 |
| K-9 | Conf | R34.1a: el XSD de pausa lo declara (su FAIL es por la ventana overlay, otra propiedad) | S | Mismo hueco que K-8. Lectura directa: `xs:boolean default="false"`, igual que ISO |
| K-10 | Conf | E-1 (tipos lista válidos), E-3 PASS en las 17 ventanas; R12.2 PASS 15 (tokens válidos); R39.2a/b PASS 1 (xml#78) | C | El FAIL de R12.1a es otra propiedad (ver abajo) |
| K-11 | Conf | R40.7 PASS 9 (nada nuestro dentro de un evento lineal heredado); R40.1 PASS 4 (pausa solo `on-top`); P-INSERT-shaka PASS en xml#23, #39, #55, #80 (Shaka reconoce el `InsertPresentation` junto a una ventana; #39 y #80 declaran `supersede`) | P | Que la desviación de `supersede` respecto de §5.16.2.2.1 sea aceptable y esté declarada es lectura de prosa |
| K-12 | Conf | nada | S | El modo de despacho es texto de la definición del esquema; ningún Player llega a despachar una ventana |
| K-13 | Conf | K-13a PASS 7 (ningún MPD `dynamic` con insert); K-13b PASS 7 (sin `Event@status`); E-3 PASS 7 (tipos de `AlternativeMPDEventType`); P-INSERT-shaka PASS 7 | C | — |
| K-14 | Conf | K-14 PASS 1 (xml#15, el único `@clip`, con `@maxDuration`); E-3 PASS en los 2 MPD replace | C | Una sola instancia |
| K-15 | Conf | DR-10a, DR-10b, K-15a, K-15b PASS 8 (§8.14 reglas 1, 2, 3, 5); E-3 PASS 8 (orden `ImportedMPD` / `ServiceDescription` del `PeriodType`) | P | DR-10d NOT_VERIFIABLE 8 (restricciones de MPD estático, sin lista cerrada); el resto de §8.14 no está en el catálogo y no pude ver qué dice sin la copia primaria; lo que sobrevive al merge no lo decide nadie |
| K-16 | Conf | E-3 y E-4 PASS en los 5 List MPD con `ClickThrough`/`AdSystem`/`AdTitle`; R28.1a PASS 3 | C | Que el merge los conserve (paso 3 b ix) es procesamiento, no propiedad del documento |
| K-17 | **Marg** | E-3, E-4, DR-7 y DR-10a PASS en xml#3 (válido; Table 4 lo admite por `PT0S`) | P | El punto Marginal (§8.1, una Representation por Period) es K-17 NOT_VERIFIABLE 52: condición sobre la Media Presentation, no sobre el MPD |
| K-18 | Conf | DR-1a..DR-1i PASS 24 cada una (los 24 SPS cumplen §8.15.2 y §8.15.3); E-3 PASS 24 | C | DR-1 NOT_VERIFIABLE 8: el MPD referido no está en el List MPD que lo nombra |
| K-19 | Conf | DR-4a PASS 24 (los dos perfiles existen en la 6.ª edición); DR-1* PASS | P | La consecuencia del merge de `@profiles` y que §8.4.2 permita ignorar `EventStream` es lectura |
| K-20 | Conf | K-20 PASS 12 (`callback` con `@value="1"`); K-4b PASS 12 en esos SPS | C | La sustitución del stream en el merge no se ejecuta |
| K-21 | Conf | E-1 (reuso de `dash:EventStreamType` compila); E-3 PASS 17 OverlayList con `Tracking`; R13.1a PASS 17 (esquema `callback`) | P | K-4b solo lee `dash:EventStream`, así que la unicidad de `Event@id` dentro de `<svta:Tracking>`, que la spec hace suya, no la chequea nadie. DR-3a NOT_VERIFIABLE 45 (Events DASH dentro de `Tracking`); E-3 NOT_VERIFIABLE en el fragmento xml#6 |
| K-22 | Conf | E-3 PASS 23 OverlayList; E-4 PASS 20 MPD principales (el `@uri` de la ventana desaparece con el elemento ajeno); P-LEGACY PASS 40 sin pedidos a URIs nuestras | C | — |
| K-23 | Conf | R24.1 PASS 24 (ningún image/HTML como `@mimeType` de AdaptationSet o Representation en SPS); DR-1a PASS 24 (tipos de RFC 4337); R15.2a PASS 20; E-3 PASS 23; DR-5b NOT_APPLICABLE 52 (ningún List MPD tiene AdaptationSet propio) | C | E-3 NOT_VERIFIABLE en el fragmento xml#5 |
| K-24 | Conf | DR-1a..DR-1i PASS en los 24 SPS; R15.2a admite `application/dash+xml` | P | El código no une un `@src` con el documento al que apunta; "es un MPD §8.15 común" vale para los ejemplos, no para la referencia |
| K-25 | Conf | E-3 PASS 23; R35.1 y R35.2 PASS 23, R36.4 PASS 23, R32.1a PASS 3; R35.8 PASS 17 (ningún `@dismissAfter` en un slot lineal, así que no pisa `@skipAfter`) | C | — |
| K-26 | Conf | R29.1a PASS 12, R29.1b..h, R29.3 PASS 11 sobre los pedidos; R29.1j NOT_APPLICABLE en los 52 MPD: la búsqueda no encontró ningún elemento de Annex I | C | La evidencia de "no usa Annex I" es un NOT_APPLICABLE por búsqueda completa, no un PASS |
| K-27 | Conf | nada | S | Ningún ejemplo lleva `RequestParam` (R29.1j sin instancias; en la spec aparece solo en prosa) |
| K-28 | Conf | DR-4a PASS 20; P-LEGACY PASS 40 | P | Ninguna regla chequea las restricciones de `isoff-live` (§8.4) ni la consecuencia que la spec declara |
| K-29 | **Marg** | nada | S | Ningún ejemplo declara Advanced Linear; la pregunta es qué esquemas admite el perfil |
| K-30 | Conf | R33.4 PASS 4; E-3 PASS en los 5 MPD con `Metrics` (orden después de `Period`); DR-1g PASS 24 (sin `MPD.Metrics` en SPS) | C | E-3 NOT_VERIFIABLE en el fragmento xml#8 |
| K-31 | Conf | E-1, E-2, XSD-ID PASS (compila con el XSD de ISO, que en libxml2 incluye la verificación de determinismo; archivo idéntico al bloque); E-3 PASS 77 (incluye los `Event` DASH dentro de `Tracking`) | C | — |
| K-32 | Conf | R39.2b, R39.4b PASS 1 (cuatro porcentajes dentro del viewport; regla de context/03) | S | Que SRD (H.1) no se active es lectura; nadie busca un descriptor SRD |
| K-33 | Conf | nada | S | Comportamiento del Player ante una falla; ningún nivel lo ejercita |
| K-34 | **Marg** | nada | S | Regla del Player |
| K-35 | **Marg** | C07-6a PASS 17, C07-6b PASS 48 (sintaxis `urn:svta:dash:<x>:<año>`) | P | Confirma la sintaxis URN, que el audit ya concedía; que el NID no esté registrado no lo decide código |
| K-36 | Conf | nada | S | Regla del Player |
| K-37 | **Marg** | nada | S | Regla del Player; los Players no llegan a ninguna pausa publicitaria |

## Cuentas

| clase | total | de los 32 Conforming | de los 5 Marginal |
|---|---|---|---|
| confirmada por código | 17 | 17 | 0 |
| contradicha por código | 0 | 0 | 0 |
| parcial | 10 | 8 (K-2, K-3, K-11, K-15, K-19, K-21, K-24, K-28) | 2 (K-17, K-35) |
| sin evidencia de código | 10 | 7 (K-8, K-9, K-12, K-27, K-32, K-33, K-36) | 3 (K-29, K-34, K-37) |

Ningún Conforming tiene un FAIL de código sobre la propiedad que el audit juzgó.

**No hay contradicciones.** Los 8 FAIL tocan construcciones del inventario
(K-9, K-10, K-21, K-1), pero miden otra propiedad: si la spec tiene los
carriers que pide `context/03`, no si lo que tiene es conforme con DASH. El
audit no juzgó eso y el código tampoco lo contradice:

- **R12.1a** (K-10): el audit dice que las listas de tokens son tipos válidos de
  la extensión, y E-1/E-3 lo confirman. El FAIL es que a la enumeración le
  falta `squeezeback-frame`, un token de R12.2.
- **R34.1a** (K-9): el audit juzgó `@executeOnce` en la ventana de pausa, y el
  XSD lo tiene. El FAIL es que la ventana overlay no lo tiene, y R34.1 lo pide
  en las dos.
- **R13.6a** (K-21): el audit juzgó el reuso de `EventStreamType` en el
  candidato. El FAIL es que la opción no puede llevar `Tracking`, como pide
  R13.6.
- **R40.9a sobre xml#40** (K-1): xml#40 es el bloque G.3, "el mismo documento
  después de quitar el namespace de extensión", que la spec muestra justamente
  para ilustrar K-1. Que sus Events SGAI queden sin ventana es el resultado
  correcto de esa remoción. La regla está bien para un MPD que escribe un
  Publisher, pero el catálogo no distingue esa ilustración de un MPD de autor.
  A mi juicio el defecto está en el alcance de la regla y no en la spec.
  E-3, E-4 y P-LEGACY dan PASS sobre el mismo bloque.

## Lo que el código encontró y el audit no juzgó

- **Los carriers que pide `context/03` y el XSD publicado no tiene** (R12.1a ×3,
  R34.1a, R34.9a, R13.6a). El audit tiene alcance DASH ("Design quality is out
  of scope") y por eso no podía verlos. Son huecos de cobertura de la v12.6
  frente a requisitos posteriores de `context/`, no problemas de conformidad.
- **R40.9a en G.3**, ver arriba.
- **Los Players.** dash.js 5.3.0 y Shaka 5.3.6 reproducen los 20 MPD
  principales sin error y sin pedir URIs nuestras (P-LEGACY, 40 PASS). Shaka
  reconoce el `InsertPresentation` de la 6.ª edición en los 7 MPD que lo tienen
  (P-INSERT-shaka, 7 PASS). El audit afirma la compatibilidad hacia atrás por
  lectura (§5.2.1, `xs:any`); esto la mide en dos Players reales. Tiene dos
  límites: cada corrida avanza unos 8 s de media, así que ningún break ni
  ventana posterior se alcanza, y los eventos de anuncio solo aparecen en
  xml#10, cuyo cue está en 0 s.
- **DR-3a NOT_VERIFIABLE 45**: los `Event` DASH dentro de `<svta:Tracking>`
  (17 OverlayList) se van con su padre si se quita lo ajeno. El audit no lo
  menciona. No afecta a un Player legacy, que nunca pide un OverlayList.

## Los Marginal del audit

Ninguno de los 5 se resuelve por código, ni a favor ni en contra:

- **K-17**: el código confirma los hechos que el audit usa para descartar
  Non-conforming (xml#3 es válido y Table 4 lo admite). La condición de §8.1
  queda NOT_VERIFIABLE por diseño: es sobre la Media Presentation, y una regla
  que contaba Representations falló el ejemplo K.6.4 de ISO (T-04).
- **K-35**: el código confirma la sintaxis. El registro del NID no es una
  propiedad del documento.
- **K-29, K-34, K-37**: no hay regla. K-29 no tiene ningún ejemplo en Advanced
  Linear. K-34 y K-37 son comportamiento del Player en un break, que el nivel
  3a no alcanza.
