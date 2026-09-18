# Decisiones pendientes — v9 (2026-09-18)

Las 23 filas bloqueantes del candidato v9. Cada entrada se entiende sola: trae
el texto literal que está hoy en juego, qué choca, qué rompe, y una cláusula
normativa lista para pegar.

**20 necesitan tu decisión y 3 no.** Fuente: `bin/check-promotable.py` sobre
`output-analysis/` (v9), que rutea 19 a vos, 2 al pipeline (`R13.3`, `R29.5`) y
deja 2 sin rutear (`C27`, `C31`). De esas dos últimas, `C31` resultó ser tuya y
`C27` no. Las 3 que no son tuyas están al final, en su propia sección: van
porque el documento cubre todo lo que bloquea, no porque te pidan algo.

**Una aclaración que vale para todas.** El texto normativo propuesto está en
inglés porque es el idioma de la spec, y está escrito en forma positiva (MUST
y no MUST NOT) porque DP-2 prohíbe enumerar prohibiciones y hoy la spec cumple
esa regla exactamente: 83 `MUST` y cero `MUST NOT` en los capítulos normativos.
Una recomendación redactada como prohibición rompería una regla que hoy está
verde.

Las cuatro citas al estándar base que aparecen abajo (§5.16.5.2 sobre el tope
ausente, §5.10.2.1 sobre el agrupamiento de eventos, y §8.3.2 y §8.3.3 sobre el
perfil On-Demand) se verificaron literales contra la copia primaria de
ISO/IEC 23009-1:2026 que declara `context/00-normative-base.md`.

---

## Índice

**Contradicciones — hay que elegir un lado (5)**

1. `UC-05` — en D5 (el dispositivo más pobre) el caso de uso dice que no se muestra nada y la spec muestra un ad fullscreen — elegir cuál de los dos textos de `context/` se mueve.
2. `R1.3` — si estrechar el valor por defecto de un atributo del estándar base cuenta o no como "alterar su semántica" — definir el criterio; hoy la spec afirma las dos cosas en dos secciones distintas.
3. `C31` — tres anexos declaran un perfil DASH que el media que ellos mismos escriben no cumple — elegir entre cambiar el perfil declarado o cambiar el media, y escribir la regla que falta.
4. `R15.3` — `context/` da al Player permiso de saltear un candidato y la spec se lo convierte en obligación — decidir si es permiso o deber.
5. `DP-1.1#p2` — dos atributos heredados del estándar base están declarados obligatorios con un solo valor posible, que es la forma que un principio de diseño prohíbe — decidir si ese principio alcanza a atributos que la spec no inventó.

**Gap — falta una declaración (1)**

6. `R32.4` — si dos pedidos de resolución dentro de una misma pausa son una oportunidad o dos, está declarado fuera de alcance en `context/` y en ningún lado de la spec — decidir si la spec lo declara o no.

**Fuerza normativa perdida — la obligación existe pero no obliga (14)**

7. `R1.1` — la compatibilidad hacia atrás con un Player viejo está escrita como obligación sobre ese Player, y la spec argumenta que esa obligación no se puede hacer — elegir la forma que sí es exigible.
8. `R26.2` — la spec delega la composición de superficies a la implementación y `context/` obliga al Player a componer el doble box — decidir cuál de las dos cede.
9. `R27.2` — mismo caso en el L-shape, y además el criterio nombra una "región declarada" que ninguna construcción declara — decidir la composición y sacar la frase huérfana.
10. `R32.1` — que el documento de pausa declare qué hacer al agotar candidatos es un MUST en `context/`, opcional en la tabla de atributos, y el único test de conformidad acepta que se omita — alinear las tres.
11. `R30.1` — una oportunidad sin ads debe responderse con un documento vacío y `200`, y nada obliga al APS a hacerlo — aprobar el MUST.
12. `R24.1` — la URL de un creativo no audiovisual tiene que viajar por un carrier que no la ate al registro RFC 4337, y la obligación está sólo en capítulos no normativos — aprobar el MUST.
13. `R24#p1` — la prohibición general que da origen a R24.1 no aparece en ningún capítulo normativo — aprobar la forma positiva que la reemplaza.
14. `R24#p2` — la enumeración de carriers admisibles existe y está bien, pero nada obliga a usar el que la spec eligió — aprobar el MUST.
15. `R12.2` — que el Publisher use sólo tokens de layout de la lista cerrada no obliga a nadie, y el atributo ni siquiera está tipado como enumeración — aprobar el MUST y el cambio de tipo.
16. `R20.2` — que todas las ventanas de una familia vayan en un solo `<EventStream>` está dicho en indicativo, aunque el estándar base lo exige — aprobar el MUST.
17. `R13.1` — que los beacons viajen como callback events en el timeline del ad está dicho en indicativo — aprobar el MUST.
18. `R28.1` — que el ClickThrough y su click-tracking viajen en `<svta:Click>` está dicho en indicativo — aprobar el MUST.
19. `R28#p1` — la declaración de que ese carrier es *el* carrier normativo está dicha en indicativo — aprobar el MUST.
20. `R33.4` — que el Publisher pida la métrica `PlayList` está dicho en indicativo, y sin eso la métrica de pausa mide algo que nadie recolecta — aprobar el MUST.

**No son tuyas — están acá para que la lista esté completa (3)**

21. `R13.3` — que el Player corte los beacons cuando el ad se corta antes de tiempo está dicho en indicativo, y el caso gemelo dos secciones más arriba sí lleva su MUST — el arreglo está especificado y lo aplica el build.
22. `R29.5` — que el APS tolere la ausencia de cualquier parámetro de capacidad está dicho en indicativo — el arreglo está especificado y lo aplica el build.
23. `C27` — cinco listados de anexo escriben `RequestParam` en el namespace equivocado y en una posición que el schema no admite — es un error de autoría con un único arreglo correcto: lo cierra el build.

---

# Contradicciones

## UC-05 — En el dispositivo más pobre (D5), el caso de uso dice "no se ve nada" y la spec muestra un ad a pantalla completa

**Categoría:** contradicted

**Lo que dice hoy, textual:**

De `context/04-use-cases.md`, UC-05, fila D5:

> #### D5 — Single-decoder, no overlay (worst case)
>
> - **Player decision:** no overlay capability of any kind. Per R3, declines the pause-ad opportunity entirely.
> - **What the user sees:** nothing. The paused frame stays on screen until the user resumes; no ad is rendered.

De `context/03-requirements.md`, R21.1, que es posterior al caso de uso:

> **R21.1** (Player): The Player MAY present a pause-ad form fullscreen, occupying the entire screen surface, or as a partial overlay composited over the paused primary frame. When the pause-ad is fullscreen, the Player MAY release the resources held by the primary content and by any pre-existing overlay to present a fullscreen video, image, or web page.

De la spec candidata, Anexo E §E.5.5 (L5322-5330), que siguió a R21.1:

> because the ad occupies the whole screen, the paused primary frame need not stay visible, and the Player MAY release the primary content's decoder and buffers and give the decoder to the ad. D5's single decoder is enough. **PA-3 wins.**

**Qué choca:** el caso de uso razona que D5 no tiene capacidad de overlay, y de
ahí concluye que no puede mostrar ningún ad de pausa. R21.1 rompe ese
razonamiento: un ad de pausa a pantalla completa no es un overlay, porque
reemplaza la superficie entera en lugar de componerse encima de ella, y el
Player puede soltar el decoder del contenido primario para dárselo al ad. Con
esa liberación, el único decoder de D5 alcanza. El caso de uso es anterior a
R21.1 y nunca se actualizó, así que `context/` se contradice a sí mismo sobre
qué ve un espectador de D5 cuando pausa. La misma contradicción arrastra la
fila D5 de UC-08, que deriva de ésta.

**Por qué importa:** es el único lugar del proyecto donde un requisito y un caso
de uso dan respuestas opuestas sobre qué llega a la pantalla de una persona. Un
implementador que lea el caso de uso escribe un Player que en D5 declina toda
oportunidad de pausa; uno que lea R21.1 escribe uno que la aprovecha. Los dos
pueden reclamar conformidad, y la diferencia es el 100% del inventario de pausa
en la clase de dispositivo más numerosa del parque instalado. Además es la
contradicción que más se propaga: mientras siga en `context/`, cada build futuro
la va a reproducir, porque el generador tiene que elegir un lado y no hay nada
que le diga cuál.

**Recomendación:** mover la fila D5 de UC-05 (y su derivada en UC-08), no R21.1.
La spec ya tomó ese lado y lo fundamentó. Texto de reemplazo para la fila D5 de
UC-05 en `context/04-use-cases.md`:

```
#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** no compositing capability of any kind, so no
  partial pause-ad form is renderable. A `pause-fullscreen` form is
  renderable notwithstanding: it replaces the whole visual surface
  instead of being composited over the paused frame, so per R21.1 the
  Player MAY release the resources held by the primary content and
  give the single decoder to the ad. The Player selects the first
  candidate carrying a `pause-fullscreen` option whose creative it can
  render, and declines the opportunity only when no candidate carries
  one.
- **What the user sees:** the paused frame gives way to a fullscreen ad
  for its declared duration. On resume the Player re-acquires the
  decoder and the primary content comes back from the paused position,
  which the viewer perceives as a short start-up. Where no candidate
  offers a fullscreen form, nothing is rendered and the paused frame
  stays on screen.
```

La alternativa defendible sería la inversa —borrar de R21.1 la liberación de
recursos y dejar que D5 decline— pero cuesta el único inventario de pausa que
D5 puede monetizar, y a cambio no compra nada: el costo que el Anexo E ya
documenta (un start-up corto al retomar) es visible, acotado y ocurre mientras
el espectador ya estaba pausado.

---

## R1.3 — Si estrechar el valor por defecto de un atributo del estándar base cuenta como "alterar su semántica"

**Categoría:** contradicted

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R1.3** (Publisher / spec document): The specification MUST NOT alter or override the semantics of any pre-existing MPEG-DASH 6th edition construct.

De la spec candidata, §4.5.4 (L845-856):

> A slot declaration carrying **no** cap is not a slot this specification defines: the Player MUST present no ads from it and MUST continue with the primary content. Reading the absence as the base specification's unbounded default would make cap enforcement inert for exactly the slots whose declaration is defective.
>
> **That last position is provisional and open with the working group.** It diverges from the base specification's unbounded default, and what is being weighed is which failure is worse: a Publisher who omits the attribute sells nothing from that slot and may take a while to notice, against an advertisement that runs for as long as it likes.

De la spec candidata, §4.8.5 (L1581-1582), sobre otra construcción:

> Reusing the element and redefining its child would alter the semantics of a pre-existing construct, which this specification does not do.

El estándar base, para el atributo en cuestión (`@maxDuration`, DASH §5.16.5.2):

> If absent, the value is assumed to be infinity, in which case the current presentation resumes only when the alternative presentation terminates.

**Qué choca:** el estándar base dice que si el tope de duración no está, vale
infinito. R4.10 de `context/` obliga al Player a no presentar ningún ad desde un
slot sin tope. Las dos cosas no pueden ser ciertas a la vez sobre el mismo
atributo ausente: o la ausencia significa infinito, o significa slot inválido.
La spec adoptó lo segundo por mandato de R4.10, y al hacerlo estrechó el
significado de un atributo preexistente — que es exactamente lo que R1.3
prohíbe. Y después, en otra sección, la spec se declara a sí misma respetuosa
de R1.3. Las dos afirmaciones están en capítulos normativos y se leen como
opuestas.

**Por qué importa:** un implementador que se encuentre un `<Event>` de slot sin
`@maxDuration` no tiene manera de saber qué hacer. Si sigue el estándar base,
deja correr el ad sin límite; si sigue esta spec, no presenta nada. Los dos
comportamientos son máximamente distintos —un ad infinito contra cero ads— y
ambos son citables desde un documento normativo. Peor: el propio texto de la
spec anticipa la objeción y la marca como provisional, con lo cual un lector
prudente no implementa ninguno de los dos y trata el caso como indefinido, que
es lo que R3.2 declara no conforme.

**Recomendación:** no es un problema del build: es que `context/` pide dos cosas
incompatibles y hay que decidir cuál cede. Recomiendo agregarle a R1.3 el
criterio que hoy le falta, dejando que un estrechamiento estilo perfil sea
admisible y quede auditado. Texto para `context/03-requirements.md`, como
criterio nuevo bajo R1:

```
- **R1.5** (spec document): Narrowing the admissible values of a
  pre-existing MPEG-DASH construct, including narrowing the meaning
  this specification assigns to that construct's absence, is a
  profile-style restriction and does not alter the construct's
  semantics for the purposes of R1.3, provided that (a) the narrowing
  only removes documents the base standard admits and adds none it
  forbids, and (b) the specification states the narrowing, the base
  standard's own default, and the reason, at the place where the
  narrowing takes effect.
```

y, con ese criterio, el pasaje §4.5.4 de la spec queda conforme reemplazando la
nota provisional por la declaración que R1.5 exige:

```
A slot declaration carrying no cap is not a slot this specification
defines: the Player MUST present no ads from it and MUST continue with
the primary content. The base standard reads an absent `@maxDuration`
as infinity (DASH §5.16.5.2); this specification narrows that reading
on the slots it defines, because taking the absence as unbounded makes
cap enforcement inert on exactly the declarations that are defective.
The narrowing admits no document the base standard forbids.
```

El camino contrario —dejar R1.3 como está y cambiar R4.10 para que la ausencia
del tope se lea como infinito— también cierra la contradicción, y lo descarto
porque el modo de falla que habilita (un ad que corre indefinidamente sobre el
contenido de un Publisher que se olvidó un atributo) es el que rompe el
invariante duro de DP-3, que dice que nada de esta spec puede romper la
reproducción del contenido primario.

---

## C31 — Tres anexos declaran un perfil DASH que su propio media no cumple

**Categoría:** non-conforming (contra el estándar base)

**Lo que dice hoy, textual:**

De la spec candidata, §K.2, §L.2 y §M.2 — el MPD principal declara:

> `profiles="urn:mpeg:dash:profile:isoff-on-demand:2011"`

y el Adaptation Set primario de ese mismo documento es:

> ```xml
> <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
>                codecs="avc1.4d401f" segmentAlignment="true"
>                startWithSAP="1" par="16:9">
>   <SegmentTemplate timescale="90000" duration="360000" startNumber="1"
>                    initialization="$RepresentationID$/init.mp4"
>                    media="$RepresentationID$/seg-$Number$.m4s"/>
>   <Representation id="v-720" bandwidth="2500000" width="1280" height="720" sar="1:1"/>
> </AdaptationSet>
> ```

Del estándar base, §8.3.3, sobre ese perfil:

> Each Representation shall have one Segment that complies with the Self-Initializing Media Segment as defined in subclause 6.3.5.2.

y §8.3.2:

> if either the AdaptationSet.SegmentList or the AdaptationSet.SegmentTemplate element is present in an AdaptationSet element then this AdaptationSet element may be ignored

**Qué choca:** el perfil On-Demand exige que cada Representation sea un único
segmento autoinicializado. El media escrito en esos tres anexos es lo opuesto:
un segmento de inicialización aparte más segmentos numerados por
`SegmentTemplate`. El estándar base da tres motivos independientes para
descartar ese Adaptation Set bajo ese perfil, y al aplicar el procedimiento de
construcción del MPD específico de perfil el Period queda sin ninguna
Representation, con lo cual el documento falla la prueba de Media Presentation.
El mismo defecto está en el MPD de ejemplo de §5.8.1. Por contraste, los tres
anexos que declaran el perfil Live (§H.2, §I.2, §J.2) sí lo cumplen.

**Por qué importa:** son los listados completos que un implementador copia y
pega para arrancar. Un anexo que no valida contra el perfil que él mismo declara
enseña a construir mal, y el error no se ve hasta que alguien corre una
herramienta de conformidad DASH sobre el resultado. Y hay una causa de fondo más
cara que los tres anexos: nada en `context/` ni en la spec dice qué perfil
declara el MPD principal de un Publisher, ni que esa declaración restringe el
media que se puede escribir debajo. Los tres URIs distintos que aparecen en los
anexos son consecuencia de ese silencio, así que arreglar los listados sin
escribir la regla deja el mismo error listo para volver.

**Recomendación:** cambiar la declaración, no el media, y escribir la regla que
falta. Cambiar el perfil es una línea por anexo y el media ya escrito satisface
el perfil Live; reescribir el media a la forma On-Demand toca tres listados
completos y no compra nada, porque esta spec no depende de ninguno de los dos
perfiles.

1. En §K.2, §L.2, §M.2 y en el MPD de ejemplo de §5.8.1, reemplazar
   `urn:mpeg:dash:profile:isoff-on-demand:2011` por
   `urn:mpeg:dash:profile:isoff-live:2011`.
2. Agregar en §5.1 la regla que falta:

```
**The main MPD's profile.** This specification constrains no profile on
the Publisher's main MPD. A Publisher declares in `MPD@profiles`
whatever profile the media it authors satisfies, and the media it
authors MUST satisfy every profile it declares. The constructs this
specification adds are removal-safe under any profile of the base
standard (§4.7), so a Publisher's profile choice and its use of this
specification are independent.
```

Con esa regla, los anexos pasan a ser auditables contra algo, que es lo que hoy
no son.

---

## R15.3 — `context/` le da al Player permiso de saltear un candidato y la spec se lo convierte en obligación

**Categoría:** contradicted

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R15.3** (Player): The Player MAY skip a candidate whose creative carrier mimeType is not in the admissible set; such a candidate signals a non-conformant ADS, APS, or Publisher.

De la spec candidata, §4.5.2 (L766-771):

> Before anything is rendered, the Player MUST validate each candidate against the declarations of the window that served it: that window's `@allowedLayouts`, its `@maxDuration`, and the admissible creative carriers of §3.3. A candidate that satisfies them is eligible; one that satisfies none is skipped and the Player moves to the next candidate in document order.

**Qué choca:** el requisito dice que el Player *puede* saltear un candidato cuyo
tipo de creativo esté fuera del conjunto admisible; la spec dice que lo *tiene
que* validar y que uno que no pasa se saltea, sin dejar discrecionalidad. Es un
endurecimiento, no un ablandamiento, así que operativamente no se pierde nada:
todo Player que cumpla la spec cumple de más respecto del requisito. Lo que sí
pasa es lo inverso: un Player que ejercite el permiso de R15.3 y decida
renderizar ese candidato es conforme a `context/` y no conforme a §4.5.2.

**Por qué importa:** un implementador que lea el requisito puede razonablemente
decidir "lo intento igual, capaz mi decoder lo aguanta" y quedar fuera de
conformidad sin haber violado nada que él pueda ver. Y la razón por la que
sospecho que el MAY fue deliberado está en el propio criterio: dice que un
candidato así *señala* un actor upstream no conforme, o sea que describe un
síntoma de error ajeno, y ante un error ajeno la tolerancia suele ser
intencional. Hay que decidir si esa tolerancia es una funcionalidad o un
descuido de redacción.

**Recomendación:** quedarse con el MUST de la spec y endurecer R15.3 en
`context/`. El valor de esta spec es la interoperabilidad, y un permiso que
permite a dos Players conformes hacer cosas opuestas frente al mismo documento
es exactamente lo que resta interoperabilidad; además el conjunto admisible
(video, imagen, HTML) es tan ancho que un creativo afuera de él no es un caso
límite sino un documento roto. Texto de reemplazo en
`context/03-requirements.md`:

```
- **R15.3** (Player): The Player MUST skip a candidate whose creative
  carrier media type is outside the admissible set and move to the next
  candidate in document order. Such a candidate signals a
  non-conformant ADS, APS or Publisher, and rendering it would make two
  conformant Players behave differently on the same document.
```

La alternativa es restaurar el MAY en §4.5.2 sólo para la validación de
carrier, dejando la de layouts y la del tope como MUST. La descarto porque
parte la misma oración en dos regímenes normativos y obliga al implementador a
recordar cuál de los tres chequeos es opcional, sin que ese recuerdo compre
ningún comportamiento deseable.

---

## DP-1.1#p2 — Dos atributos heredados del estándar base están declarados obligatorios con un solo valor posible

**Categoría:** contradicted

**Lo que dice hoy, textual:**

De `context/03-requirements.md`, principio de diseño:

> **DP-1.1. No "future flexibility" placeholders.** A construct MUST NOT be introduced "just in case a future edition relaxes it". Constructs whose only admissible value matches the construct's default OR is fixed by another rule MUST NOT exist in the spec.

De la spec candidata, §5.5.1 (L2689), tabla de atributos del `<EventStream>` de tracking:

> | `@value` | yes | `xs:string` | — | `1`, the value the base specification fixes for this scheme (DASH §5.10.4.5) |

De la spec candidata, §5.2.2 (L2214), tabla de atributos del documento de resolución:

> | `@type` | yes | enum (`static` \| `dynamic` \| `list`) | `static` | `static` on this document, for the reason above. |

**Qué choca:** los dos atributos están marcados obligatorios y sólo admiten un
valor. El de `@value` está fijado por otra regla (la tabla de parámetros que el
estándar base define para el esquema de callback), y el de `@type` es igual al
default declarado del propio atributo. Las dos son literalmente las dos formas
que DP-1.1 enumera como prohibidas. Y la spec aplica el principio correctamente
en otro lado: en §5.1.3 argumenta que no declara un atributo de concurrencia
máxima porque su único valor admisible sería `1`.

**Por qué importa:** el choque es entre un principio de diseño y el schema del
estándar base. Si se eliminan los dos atributos porque el principio lo pide, un
documento de esta spec puede salir sin campos que un validador o un parser de
DASH espera encontrar, y el costo no es estético sino que el documento se
rechaza. Si se dejan como están, el principio queda escrito y desobedecido, que
es peor que no tenerlo, porque el próximo autor no sabe si puede invocarlo.

**Recomendación:** dejar los dos atributos y acotar el alcance de DP-1.1 a las
construcciones que esta spec introduce. Ni `EventStream@value` ni `MPD@type` son
construcciones de esta spec: son atributos preexistentes cuya presencia el
estándar base espera, y DP-1.1 fue escrito contra la tentación de inventar
campos nuevos "por si acaso", no contra la de poblar campos ajenos. Texto de
reemplazo en `context/03-requirements.md`:

```
- **DP-1.1. No "future flexibility" placeholders.** A construct MUST
  NOT be introduced "just in case a future edition relaxes it".
  Constructs *this specification introduces* whose only admissible
  value matches the construct's default OR is fixed by another rule
  MUST NOT exist in the spec. The principle does not reach a
  pre-existing attribute of the base standard: where the base standard
  or one of its schemes fixes the value, this specification states the
  value and the rule that fixes it, and the attribute stays.
```

y una línea de fundamento en cada tabla de la spec, del tipo *"Fixed by the base
standard's parameter table for this scheme; declared here so the document is
complete against the base schema, which DP-1.1 does not reach (it governs
constructs this specification introduces)."*

La alternativa es sacar los dos atributos y dejar que valgan los defaults. La
descarto por asimetría de costo: dejarlos cuesta dos líneas de fundamento, y
sacarlos arriesga un documento que un validador base rechaza, que es un error
que se descubre tarde y en casa del implementador.

---

# Gap

## R32.4 — Si dos pedidos de resolución dentro de una misma pausa son una oportunidad o dos

**Categoría:** gap

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R32.4** (spec document): Whether a second resolution request within one pause is the same opportunity or a new one is **out of scope**. The two readings are identical at the Player: it requests, it renders what arrives, and it stops on resume, in both. What differs is accounting between the APS and the ADS, which this specification does not observe (R18), so it is in no position to fix which reading is correct. What the specification does measure is **how much of the paused interval carried an ad** (R33), and that figure is the same however the requests are counted.

De la spec candidata: no hay pasaje. §1.3 enumera siete exclusiones y ésta no
está entre ellas, y ninguna otra sección toca el tema.

**Qué falta y dónde se nota el agujero:** el requisito le pide a la spec que
declare un silencio, y la spec no lo declara. El agujero se nota en §1.3, que es
donde un lector busca las exclusiones y donde están las otras siete, cada una
con su razón. Como el comportamiento del Player es idéntico bajo las dos
lecturas, nada más en el documento delata que la pregunta se hizo y se decidió
no contestarla.

**Por qué importa:** el Player no se rompe, pero la contabilidad sí. Un APS que
cuente dos pedidos dentro de una pausa como dos oportunidades y un ADS que los
cuente como una van a diferir permanentemente en el conteo de oportunidades, y
la diferencia no se manifiesta como un error sino como dos números que no cierran
al final del mes, sin que ninguna de las dos partes esté violando nada. Y un
lector de la spec que se tope con la pregunta no puede distinguir un silencio
elegido de un olvido: si cree que es un olvido, va a inventar la regla, y ahí
aparece una tercera lectura.

**Recomendación:** que lo declare la spec, no sólo `context/`. La razón es
exactamente esa indistinguibilidad: la lista de exclusiones existe para que un
lector sepa qué no va a encontrar, y una exclusión que vive únicamente en el
repositorio de requisitos no llega a ese lector. Bullet para agregar a §1.3 de
la spec:

```
- **Whether a second resolution request inside one pause is the same
  opportunity or a new one.** The Player behaves identically under both
  readings: it requests, it renders what arrives, and it returns to the
  primary content on resume. What differs is accounting between the APS
  and the ADS, an exchange this specification does not observe, so it
  is in no position to fix which reading is correct. What it does
  measure is how much of the paused interval carried an ad (§5.9), and
  that figure is the same however the requests are counted.
```

`context/03-requirements.md` puede quedar como está: R32.4 pasa a estar
satisfecho por ese bullet. Si preferís lo contrario —moverlo a la sección Out of
Scope de `context/` y no decir nada en la spec— el criterio se cierra igual y el
costo es que el implementador se queda sin la respuesta.

---

# Fuerza normativa perdida

**Una sola causa explica once de estas catorce.** Los capítulos de conformidad
del Publisher (§4.2), del ADS (§4.3) y del APS (§4.4) están escritos enteros en
indicativo, bajo un encabezado del tipo *"A conformant Publisher:"* y *"A
conformant APS returns, for each request it answers, a document that satisfies
all of the following."*. Entre los tres suman cero `MUST`, contra 83 en el resto
del documento, todos sobre el Player. Si ese encabezado confiere fuerza
normativa a cada bullet —que es la convención ISO— las once obligaciones están
bien y no hay nada que hacer salvo decirlo; si no la confiere, el único actor
obligado por esta spec es el Player.

La decisión de fondo es una y vale para las once: **(a)** declarar en §4.1 que
una cláusula de conformidad obliga en indicativo, que no cambia ni una palabra
más, o **(b)** reescribir §4.2-§4.4 como obligaciones modales, que es la
edición grande y la que hace que cada bullet se pueda citar solo.

Recomiendo **(b)**. La razón es que el documento se va a citar por fragmento:
una disputa de conformidad no se argumenta contra un capítulo, se argumenta
contra una oración, y una oración en indicativo no gana esa discusión aunque el
encabezado la respalde. El costo de (b) es una pasada de edición; el costo de
(a) es que cada cita de una obligación del Publisher o del APS arrastre consigo
el encabezado y la convención que lo interpreta.

Las entradas de abajo dan, cada una, la cláusula concreta que esa pasada
escribe. Sirven igual si elegís (a): en ese caso son mejoras opcionales y no
hace falta aplicarlas.

Las tres primeras (`R1.1`, `R26.2`, `R27.2`) **no** son de esta causa: cada una
tiene un choque propio y necesita una decisión propia.

---

## R1.1 — La compatibilidad hacia atrás está escrita como una obligación sobre un Player que nunca oyó hablar de esta spec

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R1.1** (Player): Given an `MPD` containing an SGAI construct introduced by this proposal that the Player does not implement, a conforming legacy Player MUST ignore the unknown construct and continue playing the primary content uninterrupted.

De la spec candidata, §4.1 (L548-554):

> **This is not a weakening.** An obligation on a Player that has never heard of this specification is not available to be made, here or in any other extension of the base standard, so scoping it to conformant Players is the strongest form the obligation has. What replaces the missing half is auditable and is §4.7: every construct introduced here is removal-safe, so a Player that predates this specification keeps playing the primary content.

De la spec candidata, §7.9 (L3558-3560), único lugar donde aparece el comportamiento:

> Such a Player therefore skips the overlay window, the pause window and every element they carry, never reaches the APS, and plays the primary content uninterrupted.

**Qué obligación se perdió y qué quedó en su lugar:** se perdió el MUST sobre el
Player legacy. Quedó una afirmación en indicativo dentro de un capítulo
explicativo, y un argumento en §4.1 de por qué la obligación original no se
puede hacer. El argumento es correcto y está fundado en el propio estándar base,
que dice explícitamente que no especifica normativamente el comportamiento de un
cliente DASH. Una spec de extensión no puede obligar a un software que no la
implementa. El mismo problema alcanza a R6.4 y al segundo párrafo de R6, que
piden que un Player ignore namespaces desconocidos.

**Por qué importa:** la compatibilidad hacia atrás es el invariante central de
todo el trabajo —es R1, el primer requisito— y hoy no hay ninguna oración
exigible que la sostenga. Si mañana alguien pregunta "¿dónde dice esta spec que
no rompe a los Players existentes?", la respuesta es un párrafo de un capítulo
no normativo. Un implementador no hace nada mal con el texto como está; el
problema es que nadie puede demostrar que la garantía existe, que es justamente
lo que un organismo de estandarización va a pedir.

**Recomendación:** dar vuelta el sujeto de la obligación. La garantía no puede
recaer sobre el Player viejo, pero sí sobre el documento y sobre quien lo
escribe, y así se vuelve verificable sin correr nada. Texto para reemplazar
R1.1 en `context/03-requirements.md`:

```
- **R1.1** (Publisher / spec document): Every construct this
  specification introduces MUST be expressed through an extension point
  of MPEG-DASH 6th edition whose ignore-if-unknown semantics leave a
  Player that does not implement this specification playing the primary
  content uninterrupted, and the specification MUST audit each
  introduced construct against that property, construct by construct.
```

y la obligación correspondiente en §4.2 de la spec:

```
A conformant Publisher MUST author every construct of this
specification at an extension point of the base standard whose
ignore-if-unknown semantics are stated in §4.7, so that removing every
element and attribute outside the base schema leaves a valid and
conformant Media Presentation.
```

Aplicar lo mismo a R6.4 y al párrafo de R6 que hoy obliga al Player a ignorar
namespaces desconocidos: pasan a ser obligaciones de autoría sobre el APS y el
Publisher.

El camino alternativo —acotar R1.1 a *"a Player conformant to this
specification"*— también produce una obligación alcanzable, y lo descarto
porque es circular: dice que un Player que implementa la spec ignora
correctamente las construcciones de la spec, que es lo único que no hace falta
garantizar.

---

## R26.2 — La spec delega la composición de superficies a la implementación, y `context/` obliga al Player a componer el doble box

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R26.2** (Player): The Player MUST composite the primary content and the ad as the two boxes of a side-by-side / double-box layout. When the advertiser supplies a background element, the Player MUST place it in the uncovered bands. When the advertiser supplies no background element, the uncovered region renders as black.

De la spec candidata, §5.3.7.2 (L2536-2539):

> In a double-box layout the shrunk primary content and the ad are composed as two on-screen boxes that leave bands uncovered. A **background element** MAY fill those bands; where none is present they render as black.

De la spec candidata, §1.3 (L152-160):

> The composition of two visual surfaces is likewise left to the implementation. The base specification takes the same position for its own supplementary-video service:
>
> > "Potential manipulation of the stream and the composition of the main video and the supplementary video are out of the scope of the DASH client." (DASH §5.8.5.16)
>
> This specification states which surfaces are simultaneously active, in what order and for how long, and leaves how they are drawn to the device.

**Qué obligación se perdió y qué quedó en su lugar:** se perdieron tres MUST
sobre el Player. Quedó una descripción en indicativo de cómo se ve el layout, y
un `MAY` para el elemento de fondo donde el requisito ponía un `MUST`. Pero acá
la fuerza no se perdió por descuido de redacción: se perdió porque §1.3 delega
explícitamente la composición a la implementación, siguiendo al estándar base.
La spec no podía escribir los tres MUST sin contradecir su propia declaración de
alcance.

**Por qué importa:** con el texto como está, un Player puede renderizar el ad y
el contenido primario en cualquier arreglo que se le ocurra y seguir siendo
conforme, incluso uno donde el ad quede tapado. Eso vacía el layout: si `layout`
es un token que el Publisher admite y el APS emite, pero nada obliga a que lo
que aparece en pantalla se parezca al layout, el token no transporta ninguna
garantía comercial. Un anunciante que compra un doble box no tiene ninguna
cláusula que invocar si le entregan otra cosa.

**Recomendación:** separar dos cosas que hoy están mezcladas bajo la palabra
"composición", y obligar sólo una. Qué superficies están simultáneamente en
pantalla y cuál va encima de cuál es una garantía comercial y es de esta spec;
dónde están los píxeles es del dispositivo y del layout de IAB, y ahí la
delegación de §1.3 es correcta. Cláusula para agregar a §4.5 de la spec:

```
Where the Player presents a presentation option whose `@layout` names a
double-box layout, it MUST place the primary content and the ad
creative on screen simultaneously, each in its own region and neither
occluding the other, for the duration of the presentation. Where the
candidate carries a `<svta:BackgroundElement>`, the Player MUST render
it behind both, filling the frame area they leave uncovered; where it
carries none, that area MUST be rendered opaque black. The size,
position and proportions of each region follow the IAB layout the token
names and are not fixed here (§1.3).
```

y ajustar la última oración de §1.3 para que la delegación diga qué delega:

```
This specification states which surfaces are simultaneously active, in
what order, in what stacking relationship and for how long, and leaves
their size, position and proportions to the device and to the IAB
layout the token names.
```

El camino contrario —quedarse con la delegación y bajar R26.2 en `context/` a
una descripción sin MUST— es coherente y lo descarto porque deja el token de
layout sin ninguna garantía detrás, que es lo único que ese token existe para
dar.

---

## R27.2 — Mismo caso en el L-shape, y además el criterio nombra una "región declarada" que nada declara

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R27.2** (Player): The Player MUST composite the two elements of an L-shape — the full-frame ad creative in the background and the shrunk primary content on top of it — with the ad creative covering the whole frame and the shrunk primary content occupying its declared region.

De la spec candidata, §5.3.7.1 (L2518-2521):

> An L-shape presentation option carries exactly **one** ad creative — a single URL carrying an image, a video or an HTML creative — and that creative is placed full-frame in the background. The shrunk primary content is composited **on top of** it, in one region of the screen; the "L" is the band of the background creative that stays visible around the shrunk primary content, commonly the side and the bottom.

De la spec candidata, §5.3.7 (L2508-2512):

> **This specification declares no positioning vocabulary**: no coordinates, no dimensions, no anchors, no z-order attribute. What it fixes is which elements a layout puts on screen and what each of them costs; where they sit inside the frame is the IAB layout's and the renderer's.

**Qué obligación se perdió y qué quedó en su lugar:** el MUST de composición del
L-shape, por la misma razón que R26.2. Y hay un segundo problema propio de este
criterio: R27.2 exige que el contenido primario reducido ocupe *"its declared
region"*, y ninguna construcción de esta spec declara región alguna, porque
R10.2 prohíbe expresamente introducir un vocabulario de posicionamiento y §5.3.7
lo confirma. La frase apunta a algo que por diseño no existe.

**Por qué importa:** el L-shape es el layout donde el orden de apilado es todo el
producto. Si el creativo de fondo va encima del contenido reducido en lugar de
abajo, el espectador no ve programa, y esta spec no tendría cómo llamarlo
incumplimiento. Y la frase *"declared region"* es peor que inútil: un
implementador que la lea va a buscar el atributo que declara la región, no lo va
a encontrar, y va a concluir que le falta una parte de la especificación.

**Recomendación:** la misma cláusula de apilado que R26.2, en su versión
L-shape, y sacar de R27.2 la frase huérfana. Cláusula para §4.5 de la spec:

```
Where the Player presents a presentation option whose `@layout` names
an L-shape or squeezeback layout, it MUST render the ad creative
full-frame as the background and the shrunk primary content above it,
in one region, for the duration of the presentation, leaving a band of
the ad creative visible around that region. The size, position and
proportions of that region follow the IAB layout the token names and
are not fixed here (§1.3).
```

y el reemplazo de R27.2 en `context/03-requirements.md`:

```
- **R27.2** (Player): The Player MUST composite the two elements of an
  L-shape — the full-frame ad creative as the background and the shrunk
  primary content above it — so that the ad creative covers the whole
  frame and a band of it stays visible around the shrunk primary
  content. Where that region sits and how large it is follows the IAB
  layout the token names; this specification declares no positioning
  vocabulary (R10.2).
```

---

## R32.1 — Que el documento de pausa declare qué hacer al agotar candidatos es obligatorio, opcional y testeado como opcional, las tres cosas a la vez

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R32.1** (APS): A resolution document for a pause slot MUST declare which of the three behaviours applies. Absent the declaration, the Player MUST apply `stop`.

De la spec candidata, §4.4 (L711-712), lado APS, en indicativo:

> **Every pause resolution document declares an exhaustion behaviour**, in `@onCandidatesExhausted`.

De la spec candidata, §5.2.2 (L2224), tabla de atributos:

> | `@onCandidatesExhausted` | no | enum (`repeat` \| `request-again` \| `stop`) | `stop` | What the Player does when the candidates run out while the viewer is still paused (§4.5.11). |

De la spec candidata, Anexo O, test T-16 (L8476):

> `<svta:OverlayList>` carries `@onCandidatesExhausted` with one of `repeat`, `request-again` or `stop`, or omits it and is read as `stop`.

De la spec candidata, §4.5.11 (L1028), lado Player, que sí conserva su MUST:

> Where the document declares nothing, the Player MUST apply `stop`

**Qué obligación se perdió y qué quedó en su lugar:** la mitad del APS. La mitad
del Player está bien y es un MUST. La del APS quedó en indicativo, y además hay
dos lugares que empujan activamente en la dirección contraria: la tabla marca el
atributo como no requerido con default `stop`, y el único test de conformidad
del documento acepta explícitamente que se omita. O sea que el chequeo
ejecutable pasa justo sobre el comportamiento que el requisito prohíbe.

**Por qué importa:** es el caso más caro de esta lista porque no falla, engaña.
Un APS que nunca declare el atributo pasa el test de conformidad de la propia
spec y queda certificado. Y el comportamiento por defecto que hereda —`stop`— es
el que menos inventario vende: el espectador sigue pausado y no ve nada más. Un
Publisher que quería `repeat` y contrató un APS certificado se entera por el
reporte de ingresos.

**Recomendación:** alinear los tres lugares en la dirección del requisito. El
default `stop` se queda, pero como tolerancia del Player frente a un documento
no conforme, no como una opción legítima del APS.

1. §4.4 de la spec, reemplazar el bullet:

```
Every pause resolution document MUST carry
`@onCandidatesExhausted` with one of `repeat`, `request-again` or
`stop`. The declaration is the APS's rather than the Publisher's, for
the reason below.
```

2. §5.2.2, tabla de atributos: `@onCandidatesExhausted` pasa a `Required: yes`,
   y la columna Default deja de decir `stop` y pasa a decir `—`.

3. Anexo O, T-16, criterio de aprobación:

```
`<svta:OverlayList>` carries `@onCandidatesExhausted` with one of
`repeat`, `request-again` or `stop`. A document that omits it fails.
```

4. §4.5.11 se queda tal cual: el `MUST apply stop` del Player sigue siendo la
   respuesta correcta frente a un documento que omite el atributo, y ahora dice
   qué hacer con un documento no conforme en lugar de describir un caso normal.

Vale la pena mirar el punto 2 con cuidado: un atributo requerido sin default es
lo que hace que el test pueda fallar. Con `Required: no` y default `stop`,
ningún instrumento puede distinguir un APS que eligió `stop` de uno que no
declaró nada.

---

## R30.1 — Una oportunidad sin ads se responde con un documento vacío y `200`, y nada obliga al APS a hacerlo

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R30.1** (APS): An opportunity that resolved with no ads MUST be expressed as a resolution document carrying no candidates, and MUST NOT be expressed as an error response or as a response without a body.

De la spec candidata, §4.4 (L667-672), en indicativo:

> **An unfilled opportunity is a document carrying no candidates** — well-formed, complete, served `200` with a body. The distinction is between *a document that says nothing was sold* and *no document at all*: expressing the first as an error collapses two conditions onto one code and leaves an auditor unable to tell an unfilled opportunity from a broken one.

De la spec candidata, §5.2.3 (L2257-2261), también en indicativo:

> An opportunity that resolved and produced **no ads** is expressed as a resolution document carrying no candidates, served with HTTP `200` and a parseable body — not a `204`, not a `404`, not an error status.

**Qué obligación se perdió y qué quedó en su lugar:** el MUST sobre el APS. La
sustancia está completa y en los dos lugares correctos, los dos en capítulos
normativos, pero ninguna oración obliga a nadie. El capítulo 7 tampoco lo
retoma: lo único que hay ahí es la lista de fallas del lado del Player.

**Por qué importa:** es la distinción entre "no se vendió" y "el sistema está
roto", y hoy nada impide que un APS las colapse en un `204`. Cuando eso pasa, el
Player que recibe el `204` no puede saber si tiene que reintentar o seguir, y el
operador que mira la telemetría no puede saber si tiene un problema de demanda o
una caída. Es el tipo de ambigüedad que se descubre durante un incidente, que es
el peor momento.

**Recomendación:** reemplazar el bullet de §4.4 por la obligación:

```
An APS MUST express an opportunity that resolved with no ads as a
resolution document carrying no candidates, well-formed and complete,
served with HTTP `200` and a parseable body. The distinction is between
a document that says nothing was sold and no document at all:
expressing the first as an error status collapses two conditions onto
one code and leaves an auditor unable to tell an unfilled opportunity
from a broken one.
```

y en §5.2.3, cambiar *"is expressed as"* por *"MUST be expressed as"*.

---

## R24.1 — La URL de un creativo no audiovisual tiene que evitar el registro RFC 4337, y la obligación vive sólo en capítulos no normativos

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R24.1** (APS / spec document): When a non-AV ad form (`mediaType ∈ {html, image, ...}`) is carried in the resolution document, the asset URL MUST NOT be expressed as `@mimeType` on an AdaptationSet or Representation reached through any path bound by RFC 4337 (DR-1, DR-5). It MUST be carried via one of the §5.2.1 / §5.10 / §5.8.4.x carriers enumerated by DR-6, per R1.2.

De la spec candidata, §4.4 (L690-692), en indicativo:

> A still image or an HTML document travels as an attribute value on `<svta:RenderableAsset>`, which is foreign-namespace open content and inherits no media-type constraint to escape.

De la spec candidata, §5.3.2 (L2350-2354):

> The media axis is closed to non-MP4 media types along the whole resolution path

**Qué obligación se perdió y qué quedó en su lugar:** el MUST NOT del APS. La
prohibición explícita aparece únicamente en §8.2 y en el Anexo O, los dos no
normativos. Lo que quedó en los capítulos normativos es la descripción del
carrier correcto, en indicativo.

**Por qué importa:** el estándar base ata el `@mimeType` de una Representation
alcanzada por `<ImportedMPD>` al registro de RFC 4337, que enumera tipos de
media audiovisuales. Un APS que ponga ahí la URL de un HTML o de una imagen
produce un documento que un validador DASH rechaza, o peor, que un Player
distinto interpreta de manera distinta según cuánto verifique. Es el error más
natural de cometer, porque poner el creativo donde ya está el resto del media es
lo que parece obvio. Con el texto actual nada normativo lo desalienta.

**Recomendación:** escribir la obligación en forma positiva, que es lo que DP-2
pide y además es más útil, porque le dice al implementador dónde va en lugar de
dónde no. Reemplazo del bullet de §4.4 de la spec:

```
A conformant APS MUST carry the asset URL of a still image or an HTML
creative as an attribute value on `<svta:RenderableAsset>`, which is
foreign-namespace open content and inherits no media-type constraint.
That element is the only carrier this specification defines for such a
URL. A video creative is reached through `<ImportedMPD>`, where the
base standard binds every Representation's `@mimeType` to the RFC 4337
registry (DASH §7.3.1) and therefore to audiovisual media.
```

Nota aparte, no es una decisión tuya: tres referencias cruzadas que sostienen
esta obligación en §5.2.1 y §5.3.2 apuntan a §4.7.2 y §4.7.3, que en v9 son otra
cosa y no mencionan tipo de media. Está anotado como arreglo del pipeline y se
corrige solo.

---

## R24#p1 — La prohibición general que da origen a R24.1 no aparece en ningún capítulo normativo

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`, prosa de R24:

> When a non-AV ad form (`mediaType ∈ {html, image, ...}`) is carried in the resolution document, the asset URL MUST NOT be expressed as `@mimeType` on an AdaptationSet or Representation reached through any path bound by RFC 4337. It MUST be carried via one of the DASH-conformant carriers enumerated by DR-6.

De la spec candidata, §4.4 (L690-692): el mismo pasaje que sostiene R24.1 — el
carrier positivo está, la prohibición no está en ninguna parte de los capítulos
4 a 7.

**Qué obligación se perdió y qué quedó en su lugar:** la prohibición general. Es
la misma oración de `context/` que produce R24.1; la diferencia es que R24.1 es
el criterio de conformidad y este párrafo es el enunciado del requisito. Quedó
sólo el lado positivo.

**Por qué importa:** el enunciado general es lo que cubre los casos que el
criterio puntual no enumera. R24.1 nombra `AdaptationSet` y `Representation`;
el párrafo dice *"any path bound by RFC 4337"*, que alcanza a cualquier camino
futuro con la misma atadura. Sin él, un APS que encuentre un tercer lugar donde
poner la URL puede argumentar que el criterio no lo menciona.

**Recomendación:** una oración de alcance en §4.4, inmediatamente después de la
obligación de R24.1, escrita en positivo:

```
This holds on every path: wherever the base standard binds a media type
to the RFC 4337 registry, the construct on that path carries
audiovisual media, and a non-audiovisual creative's asset URL travels
on the foreign-namespace carrier of §5.3.2 instead.
```

Si elegiste la opción (a) del encabezado de esta sección —declarar que el
indicativo obliga— esta entrada se cierra sola y no hay nada que escribir.

---

## R24#p2 — La enumeración de carriers admisibles está bien hecha, pero nada obliga a usar el que la spec eligió

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`, prosa de R24, segunda mitad:

> It MUST be carried via one of the DASH-conformant carriers enumerated by DR-6.

De la spec candidata, §5.3.2 (L2358-2363), la comparación de los cuatro carriers:

> | Carrier | Clause | Verdict |
> |---|---|---|
> | **(a)** Foreign-namespace open content: the URL as an attribute on an element of this specification | DASH §5.2.1 | **Selected.** The option is one named element whose attributes bind form, layout and creative together, and whose position among its siblings is the preference order. |
> | (b) An application-level `<Event>` whose text content carries the payload | DASH §5.10 | Rejected. […] |
> | (c1) A `SupplementalProperty` whose `@value` carries the URL | DASH §5.8.4.9 | Rejected […] |
> | (c2) An `EssentialProperty` whose `@value` carries the URL | DASH §5.8.4.8 | Rejected […] |

**Qué obligación se perdió y qué quedó en su lugar:** el MUST de usar uno de los
carriers enumerados. La enumeración está completa, cada alternativa tiene su
veredicto y su razón, y la elegida está marcada — que es exactamente el trabajo
de diseño que el requisito pedía. Lo que falta es la oración que obliga a
usarla: la tabla explica una decisión y no manda nada.

**Por qué importa:** una tabla de alternativas con una marcada es un documento
de diseño, no una especificación. Un implementador que lea esa tabla puede
concluir razonablemente que las cuatro son admisibles y que (a) es la
recomendación de los autores, y elegir (c1) porque le resulta más cómoda con su
toolchain. El resultado es un documento de resolución que otro Player no lee, y
ninguna de las dos partes está violando nada citable.

**Recomendación:** cerrar la tabla con la obligación, inmediatamente debajo:

```
Of the four carriers above, this specification defines exactly one: a
conformant APS MUST carry a non-audiovisual creative's asset URL as an
attribute on the `<svta:RenderableAsset>` element of §5.3.1. The other
three are recorded here with the reason each was rejected, so that a
future edition reopening the question starts from the comparison rather
than from scratch.
```

---

## R12.2 — Que el Publisher use sólo tokens de layout de la lista cerrada no obliga a nadie, y el atributo ni siquiera está tipado como enumeración

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R12.2** (Publisher): Publishers declaring allowed layouts MUST use names drawn from the enumerated set, each of which maps 1:1 to an IAB-defined ad type or visual placement. Publisher-private layout names, and IAB values outside the enumerated set, MUST NOT appear in the allowed-layouts declaration on the slot.

De la spec candidata, §3.2 (L402-403), en indicativo:

> A Publisher declaring the layouts a window admits draws every token from this table. An APS emitting a presentation option draws its `@layout` from this table. A Player matches a candidate's `@layout` against the window's admitted tokens by exact string comparison.

De la spec candidata, §5.1.3 (L1866), tabla de atributos de la ventana:

> | `@allowedLayouts` | yes | whitespace-separated token list | — | The layout tokens this slot admits, each drawn from §3.2. |

**Qué obligación se perdió y qué quedó en su lugar:** las dos mitades — el MUST
de usar la lista y el MUST NOT de nombres privados. Quedó una oración en
indicativo. Y hay un agravante que no es de redacción: el atributo está tipado
como lista de tokens libres, así que tampoco hay validación de schema que
atrape un valor inventado. El atributo del lado del APS (`@layout`) sí está
cerrado. O sea que el Publisher puede escribir cualquier cosa y el APS no.

**Por qué importa:** si un Publisher escribe un token propio en
`@allowedLayouts`, ningún candidato del mundo lo va a matchear, porque el
matcheo es comparación exacta de strings contra el `@layout` del APS, que sí
está restringido a la enumeración. El resultado es una ventana que nunca
resuelve en nada: no falla, no da error, simplemente no vende. Y es
silencioso en los dos extremos, porque el documento pasa validación y el Player
hace exactamente lo que le pidieron.

**Recomendación:** dos arreglos, y el segundo es el que importa porque no
depende de que nadie se acuerde.

1. Tipar el atributo como enumeración en §5.1.3, en lugar de lista de tokens
   libres, de modo que un valor fuera de la lista falle validación de schema:

```
| `@allowedLayouts` | yes | whitespace-separated list of `LayoutTokenType` | — | The layout tokens this slot admits. `LayoutTokenType` is the enumeration of §3.2, the same type `@layout` carries on a presentation option. |
```

2. Y la obligación en §4.2:

```
A conformant Publisher MUST draw every token it writes into
`@allowedLayouts` from the table of §3.2, each of which maps one-to-one
onto an IAB-defined ad type or visual placement. A Player matches a
candidate's `@layout` against those tokens by exact string comparison,
so a token outside the table admits no candidate at all.
```

La última oración del punto 2 es deliberada: le dice al implementador cuál es la
consecuencia, que es lo que hace que la regla se recuerde.

---

## R20.2 — Que todas las ventanas de una familia vayan en un solo `<EventStream>` está dicho en indicativo, aunque el estándar base lo exige

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R20.2** (Publisher): All opportunity windows of one family that share a `Period` MUST be authored as `<Event>` entries inside a **single** `<EventStream>`. DASH admits at most one `EventStream` per `Period` for a given scheme — §5.10.2.1: *"all Events of one type shall be clustered in one Event Stream"* — so two sibling streams carrying the same SGAI scheme in one `Period` is not a conformant document.

De la spec candidata, §4.2 (L592-593), en indicativo:

> **Authors all windows of one family that share a `<Period>` as `<Event>` entries inside a single `<EventStream>`**, which the base specification fixes for every event type: *"all Events of one type shall be clustered in one Event Stream"* (DASH §5.10.2.1).

De la spec candidata, §5.1.6 (L2002-2003), también en indicativo:

> **One family, one stream.** All windows of one family in a `<Period>` are authored in a single `<EventStream>`, per the base specification's own rule.

**Qué obligación se perdió y qué quedó en su lugar:** el MUST del Publisher.
Quedaron dos descripciones en indicativo. La oración del estándar base que las
respalda es exacta y está bien citada, y ese es justamente el motivo por el que
esta pérdida cuesta poco de reparar: la obligación ya existe aguas arriba y esta
spec sólo tiene que repetirla como tal.

**Por qué importa:** un Publisher que agrupe mal produce un MPD que no es
conforme al estándar base, no sólo a esta spec. El Player que lo lea puede
quedarse con el primer `EventStream` y descartar el segundo en silencio, con lo
cual la mitad de las ventanas de esa familia desaparece sin ningún síntoma.

**Recomendación:** reemplazar el bullet de §4.2:

```
A conformant Publisher MUST author all windows of one family that share
a `<Period>` as `<Event>` entries inside a single `<EventStream>`. The
base standard fixes this for every event type — *"all Events of one
type shall be clustered in one Event Stream"* (DASH §5.10.2.1) — so a
`<Period>` carrying two sibling streams of the same SGAI scheme is not
a conformant document under the base standard either.
```

---

## R13.1 — Que los beacons viajen como callback events en el timeline del ad está dicho en indicativo

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R13.1** (APS): When the resolution document carries tracking instructions, the APS MUST express them using DASH callback events (or an equivalent baseline DASH construct), with timings relative to the ad's presentation timeline. Conformance is checked against the resolution document alone: it fixes the form the instructions take and the timebase they use, and it does not reveal how many beacons the ADS declared.

De la spec candidata, §4.4 (L698-701), en indicativo:

> **Beacons are callback events on the ad's presentation timeline** — `<Event>` entries inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015`, timed relative to the presentation of the ad that carries them. Every such `<Event>` carries an `@id`, which this specification narrows from optional to required on this carrier because de-duplication is keyed on it.

De la spec candidata, §5.5.3 (L2742-2746), también en indicativo:

> Every `<Event>@presentationTime` inside a resolution document is expressed **relative to the start of the ad's own presentation** — never to the primary timeline, never to wall-clock. The Player adds the ad's start position on the primary timeline to each relative value to obtain the firing point.

**Qué obligación se perdió y qué quedó en su lugar:** el MUST del APS sobre la
forma y sobre la base de tiempo. Las dos cosas están dichas de manera absoluta
—*"never to the primary timeline, never to wall-clock"*— pero en indicativo. En
todo el documento hay sólo dos obligaciones explícitas sobre el APS, y ninguna
es ésta.

**Por qué importa:** la base de tiempo es donde un malentendido se vuelve caro y
silencioso. Un APS que exprese los tiempos de beacon contra el timeline primario
en lugar de contra el del ad produce un documento que se parsea perfecto, y
cuyos beacons disparan en momentos arbitrarios. Las impresiones se cuentan mal,
los cuartiles se reportan mal, y nadie ve un error: ve números raros. Es el tipo
de defecto que se descubre auditando facturación.

**Recomendación:** reemplazar el bullet de §4.4:

```
A conformant APS MUST carry a candidate's tracking instructions as
`<Event>` entries inside an `<EventStream>` of scheme
`urn:mpeg:dash:event:callback:2015`, and MUST express every such
`<Event>@presentationTime` relative to the start of that candidate's
own presentation rather than to the primary timeline or to wall-clock.
Every such `<Event>` MUST carry an `@id`, which this specification
narrows from optional to required on this carrier because
de-duplication is keyed on it (§4.5.13).
```

y en §5.5.3, cambiar *"is expressed"* por *"MUST be expressed"* en la primera
oración.

---

## R28.1 — Que el ClickThrough y su click-tracking viajen en `<svta:Click>` está dicho en indicativo

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R28.1** (APS): When an ad candidate in the resolution document carries a ClickThrough, the ClickThrough URL and any click-tracking URL(s) accompanying it MUST be carried in the normative carrier this specification defines, and not elsewhere. […] Conformance is checked against the resolution document alone: a ClickThrough or a click-tracking URL carried outside the normative carrier is a violation the document shows.

De la spec candidata, §4.4 (L706-709), en indicativo:

> **The ClickThrough and its click-tracking travel in `<svta:Click>`.** Whether a ClickThrough has click-tracking at all is the advertiser's decision; a ClickThrough carried elsewhere is a violation the document itself shows.

El carrier en sí está completamente definido en §5.6.1, con `@clickThroughUrl`
requerido y `<svta:ClickTracking>` como hijo opcional de cardinalidad 0..n.

**Qué obligación se perdió y qué quedó en su lugar:** el MUST del APS. El lado
del Player sí conserva el suyo — §4.5.14 dice *"a Player conformant to this
specification MUST read the ClickThrough URL and, on viewer activation, open it
or hand it to the platform, and fire every `<svta:ClickTracking>` URL the
element carries"* — así que la asimetría es exacta: el Player está obligado a
leer de un lugar donde nada obliga al APS a escribir.

**Por qué importa:** es la asimetría la que hace daño. Un Player conforme lee
`<svta:Click>` y sólo `<svta:Click>`; un APS que ponga el ClickThrough en
cualquier otro lado produce un ad que se muestra bien y no es clickeable. Para
el espectador no pasa nada visible, para el anunciante se pierde el click, y
para el operador el síntoma es una tasa de clicks en cero que parece un problema
de creatividad.

**Recomendación:** reemplazar el bullet de §4.4:

```
Where a candidate carries a ClickThrough, a conformant APS MUST carry
its URL in `<svta:Click>@clickThroughUrl` and every click-tracking URL
accompanying it as an `<svta:ClickTracking>` child of that same
element. Whether a ClickThrough has click-tracking at all is the
advertiser's decision. A Player conformant to this specification reads
that element and no other (§4.5.14), so a ClickThrough carried
elsewhere is not reached.
```

---

## R28#p1 — La declaración de que `<svta:Click>` es *el* carrier normativo está dicha en indicativo

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`, prosa de R28:

> The resolution document MUST carry the ad's ClickThrough URL and its associated click-tracking URL(s) in a normative carrier that the specification defines explicitly, so that every Player conformant to this specification reads them the same way.

De la spec candidata, §5.6 (L2785-2787), en indicativo:

> The resolution document carries the ad's ClickThrough URL and its click-tracking URLs in a single carrier, so that a Player conformant to this specification reads them the same way.

**Qué obligación se perdió y qué quedó en su lugar:** la obligación de nivel
documento — la que dice que existe un carrier normativo y único, no cuál es.
Quedó la misma frase en indicativo. Es el enunciado general del que R28.1 es el
criterio.

**Por qué importa:** la diferencia entre este ítem y R28.1 es la diferencia entre
*"el carrier es `<svta:Click>`"* y *"hay un solo carrier y es normativo"*. Sin la
segunda, un implementador puede leer que `<svta:Click>` es el carrier que esta
spec define y suponer que otro carrier definido en otro lado también sirve —
típicamente el VAST original, del que el APS tradujo el documento. Ahí vuelve la
dependencia de VAST que toda la spec evita, por la puerta de atrás.

**Recomendación:** reemplazar la oración de apertura de §5.6:

```
The resolution document MUST carry the ad's ClickThrough URL and its
click-tracking URLs in `<svta:Click>`, and this specification defines
no other carrier for them, so that every Player conformant to this
specification reads them the same way. The guarantee is scoped to
conformant Players, for the reason §4.1 states.
```

---

## R33.4 — Que el Publisher pida la métrica `PlayList` está dicho en indicativo, y sin eso la métrica de pausa mide algo que nadie recolecta

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R33.4** (Publisher): Content carrying pause opportunity windows MUST request the `PlayList` metric through the base specification's `Metrics` element. Collection is triggered by the service provider and not by the Player — *"The trigger mechanism is based on the `Metrics` element in the MPD"* (§5.9.1) — so without this declaration R33.2 defines how to derive a quantity that nothing obliges anyone to collect.

De la spec candidata, §4.2 (L597-602), en indicativo:

> **Requests the play-list metric on content carrying pause windows**, through the `<Metrics>` element of the main MPD. Collection is triggered by the service provider rather than by the Player — *"The trigger mechanism is based on the Metrics element in the MPD"* (DASH §5.9.1) — so without the declaration §4.5.16 derives a quantity that nothing obliges anyone to collect.

**Qué obligación se perdió y qué quedó en su lugar:** el único MUST del
Publisher que esta spec necesitaba para que su métrica exista. Quedó la
descripción, que incluso reproduce la razón del criterio palabra por palabra. En
todo el documento hay un solo `Publisher MUST`, y es sobre el tope de duración.

**Por qué importa:** ésta es la que deja un capítulo entero girando en el vacío.
La spec define con cuidado cómo derivar la fracción del intervalo de pausa que
llevó publicidad a partir de las entradas del `PlayList`, pero en DASH esa
métrica sólo se recolecta si el MPD la pide: el disparador es el elemento
`<Metrics>`, no el Player. Un Publisher que no lo declare tiene un sistema
completo de medición de pausa que no produce ni un dato, y lo va a descubrir
cuando pida el primer reporte.

**Recomendación:** reemplazar el bullet de §4.2:

```
A conformant Publisher MUST request the `PlayList` metric through the
`<Metrics>` element of the main MPD on content carrying pause windows.
Collection is triggered by the service provider rather than by the
Player — *"The trigger mechanism is based on the Metrics element in the
MPD"* (DASH §5.9.1) — so without the declaration the pause-delivery
figure of §4.5.16 derives a quantity that nothing obliges anyone to
collect.
```

---

# No son tuyas

Las tres de abajo bloquean la promoción igual que las veinte de arriba, y
ninguna te pide una decisión: el arreglo de cada una ya está determinado y lo
aplica el build. Están acá para que la lista de lo que bloquea esté completa y
no haya que ir a buscar por qué faltan tres.

## R13.3 — Que el Player corte los beacons cuando el ad se corta antes de tiempo está dicho en indicativo

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R13.3** (Player): If R4 trims the ad before a scheduled beacon's time, the Player MUST stop firing remaining beacons at the trim boundary.

De la spec candidata, §4.5.13 (L1081-1083), en indicativo:

> **Where the ad stops early, the beacons stop with it.** Beacons scheduled past a trim boundary (§4.5.4), and past the dismissal of a pause ad on resume (§4.5.10), fall outside the ad's active window.

De la spec candidata, §4.5.10 (L993-997), el caso estructuralmente idéntico, que sí conserva su MUST:

> The Player MUST dismiss any rendered pause ad within one rendering frame of the pause-to-play transition, and MUST stop firing the beacons scheduled for it from that transition onward: a beacon scheduled at a relative time past the transition falls outside the pause ad's active window.

**Qué obligación se perdió y qué quedó en su lugar:** el MUST del Player de
dejar de disparar beacons en el borde del recorte. Quedó la descripción, que
dice lo mismo pero no obliga. Lo que hace este caso fácil es el contraste
interno: el caso de la pausa, dos secciones más arriba, es el mismo fenómeno —
el ad termina antes de lo que su cronograma de beacons suponía — y ahí la spec
sí escribió el MUST. Hay dos casos adyacentes con dos niveles de fuerza
distintos sin ninguna razón que los distinga.

**Por qué importa:** un Player que siga disparando beacons después de que el ad
fue recortado reporta impresiones y cuartiles de un ad que el espectador no
terminó de ver. No hay error visible: los beacons salen, el servidor los acepta,
y la métrica sobrecuenta. Es facturación inflada producida por un
comportamiento que ningún texto normativo prohíbe.

**Recomendación:** ya está escrita y decidida; la aplica el build. El reemplazo
de §4.5.13, con el caso de §4.5.10 como modelo:

```
**Where the ad stops early, the beacons stop with it.** The Player MUST
stop firing an ad's remaining beacons where that ad stops before its
schedule ends: a beacon scheduled past a trim boundary (§4.5.4), or
past the dismissal of a pause ad on resume (§4.5.10), falls outside the
ad's active window.
```

## R29.5 — Que el APS tolere la ausencia de cualquier parámetro de capacidad está dicho en indicativo

**Categoría:** force-lost

**Lo que dice hoy, textual:**

De `context/03-requirements.md`:

> **R29.5** (APS): The APS MUST tolerate the absence of any reserved parameter and MUST be able to produce ad candidates without receiving any of them. An APS that requires a parameter in order to answer would make R29.2 unattainable for the Player.

De la spec candidata, §4.4 (L719-724), en indicativo:

> **The answer depends on no reserved capability parameter.** The APS tolerates the absence of every reserved parameter of §5.8 and produces candidates without receiving any of them; requiring one would make the Player's freedom to omit it unattainable. An absent parameter means **undetermined**, and how an APS resolves an undetermined value is its own decision.

**Qué obligación se perdió y qué quedó en su lugar:** dos MUST del APS, los dos
en indicativo. Y este caso no se arregla con la decisión general sobre si un
encabezado de conformidad obliga: el encabezado de §4.4 está redactado alrededor
del **documento** que el APS devuelve (*"returns … a document that satisfies all
of the following"*), y tolerar la ausencia de una entrada no es una propiedad de
un documento. El encabezado no alcanza gramaticalmente a este bullet ni bajo la
lectura más generosa, así que el arreglo es local e independiente.

**Por qué importa:** el Player tiene libertad de no mandar los parámetros de
capacidad — es el camino que la spec habilita para un Player que no quiere
exponer qué dispositivo es. Si un APS puede exigirlos, esa libertad no existe en
la práctica: el Player que la ejerza recibe un error o un documento vacío, y
queda obligado a identificarse para poder monetizar. La garantía se cae entera
sin que ningún documento la viole.

**Recomendación:** ya está escrita y decidida; la aplica el build. El reemplazo
del bullet de §4.4, como dos obligaciones:

```
**The answer depends on no reserved capability parameter.** The APS
MUST tolerate the absence of every reserved parameter of §5.8 and MUST
be able to produce candidates without receiving any of them; requiring
one would make the Player's freedom to omit it unattainable. An absent
parameter means **undetermined**, and how an APS resolves an
undetermined value is its own decision.
```

## C27 — Cinco listados de anexo escriben `RequestParam` en el namespace equivocado y en una posición que el schema no admite

**Categoría:** non-conforming (contra el estándar base)

**Lo que dice hoy, textual:**

De la spec candidata, §A.2, §B.2, §F.2, §G.2 y §G.3 — cada uno enlaza
`xmlns:up="urn:mpeg:dash:urlparam:2025"` y escribe, como primer hijo de `<MPD>`
y antes de `<Period>`:

> `<up:RequestParam includeInRequests="…" queryTemplate="…"/>`

De la misma spec, §5.8.1, en el cuerpo, que lo hace bien — sin prefijo, adentro
del `<EventStream>` y después del `<Event>`:

> ```xml
>     <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
>                  timescale="1000">
>       <Event id="201" presentationTime="600000" duration="30000">
>         <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay"
>                                   maxDuration="30000"
>                                   allowedLayouts="overlay-corner"/>
>       </Event>
>       <RequestParam includeInRequests="urn:svta:dash:request:sgai-resolution:2026"
>                     queryTemplate="video_profile=$urn:mpeg:dash:state:video$&amp;session_id=$urn:mpeg:dash:state:cmcd#sid$"/>
>     </EventStream>
> ```

**Qué choca:** `RequestParam` es una partícula del tipo `MPDtype` del schema
principal de DASH, así que su nombre calificado pertenece al namespace DASH.
Puesto en `urn:mpeg:dash:urlparam:2025` no es el elemento que el mecanismo
define, y la parametrización extendida de la petición HTTP GET no queda
señalizada. Y por estar en un namespace ajeno, el único lugar del schema donde
podría encajar es el comodín final de `MPDtype`, que va **después** de `Period`,
`Metrics` y el resto: escrito antes de `<Period>`, falla validación incluso como
elemento de extensión. El cuerpo de la spec y los anexos se contradicen entre
sí.

**Por qué importa:** los anexos son los listados que un implementador copia. Con
el prefijo `up` puesto, la parametrización simplemente no ocurre: el Player no
reconoce el elemento y el APS recibe peticiones sin los parámetros que el
Publisher quería mandar. No hay error visible en ningún lado.

**De quién es y por qué:** del build, no tuya. Es un error de autoría con un
único arreglo correcto, y ese arreglo ya está escrito en el propio documento: el
cuerpo de la spec, en §5.8.1, hace exactamente lo que hay que hacer. No hay dos
caminos defendibles ni nada que elegir; hay cinco listados que tienen que
quedar iguales al ejemplo del cuerpo. Lo incluí acá porque el check no supo
rutearlo, no porque necesite tu decisión.

**Recomendación:** en los cinco listados, sacar el prefijo `up` y el binding
`xmlns:up`, y escribir el elemento sin prefijo en el namespace DASH por defecto
adentro del `<EventStream>` al que el template le da alcance, después del
`<Event>` — que es donde `EventStreamType` ubica la partícula y donde §5.8.1 ya
lo pone:

```xml
<EventStream schemeIdUri="urn:svta:dash:sgai:overlay:2026" timescale="1000">
  <Event presentationTime="…" duration="…" …/>
  <RequestParam includeInRequests="…" queryTemplate="…"/>
</EventStream>
```

El prefijo `up` no hace falta en ningún otro lugar del documento: ningún otro
elemento de esta spec viene de ese namespace, así que el binding se elimina
entero.

Si preferís la otra posición admisible —`<RequestParam>` a nivel `MPD`, sin
prefijo, donde `MPDtype` declara la partícula— también es conforme; la descarto
sólo por consistencia con el cuerpo y porque el template que llevan esos cinco
listados tiene alcance de slot, no de presentación.
