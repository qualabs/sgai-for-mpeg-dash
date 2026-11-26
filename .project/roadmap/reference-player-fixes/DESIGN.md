# reference-player-fixes — diseño

Lo que la fase 11 aprendió, arreglado antes del v13: que el v13 salga con la
norma ya decidida, y que la batería de conducta se pueda usar como juicio
(hoy 62 FAIL, ninguno de la referencia, que son ruido). Pedido del líder del
proyecto, 2026-11-26.

## Lo medido (2026-11-26)

- **La batería** (`phases/11-reference-player/tasks/T-09/final/battery-final.md`):
  1249 PASS, 62 FAIL, 70 NOT_VERIFIABLE sobre 329 jobs. Los 62: 18 del Player
  legacy, 16 de vectores mal escritos o del formato, 23 con causa en la norma
  (UC-07 10, UC-14 13), 5 inestables por carga.
- **La v12.6 está 126 commits de `context/` atrás.** `bin/check-incremental.py
  anchor v12.6` da `924afcb` (2026-09-27); `git rev-list --count
  924afcb..HEAD -- context/` da 126. Los commits que agregan `squeezeback-frame`
  (`fcd75e9`), `@executeOnce`/`@startWithOffset` en overlay y R34.9
  (`6c91952`), y el "retomar" de R40.4 (`7ba2297`) no son ancestros del anchor
  (`git merge-base --is-ancestor`). Por eso cinco de los hallazgos del REPORT
  §4 no son decisiones abiertas: `context/` ya los decidió y el v13 los
  absorbe (abajo, "Ya decidido").
- **`context/05` no puede llevar una regla**: su línea 8 dice *"constrains no
  implementation and defines no semantics"*. Toda lectura que el Player tome
  va en `context/03`, bajo R1.5 (03:301: donde la base no responde, la nuestra
  se declara como extensión). Lo que se deja abierto va al registro
  "Deliberately open" (03:2866).
- **Hay un registro grabado de la batería** para re-comparar sin browser
  (`--replay`), pero el de run2 se borró (142 MB). Re-comparar un vector
  corregido exige correr su job.

## Ya decidido en `context/`, lo absorbe el v13

No se tocan en esta fase. Los tests de sus mitades sin carrier se escriben
después del v13, cuando el carrier exista en `spec-source/`.

| | Hallazgo | Lo que ya dice `context/` |
|---|---|---|
| Y-1 | Falta `squeezeback-frame` (3 FAIL de R12.1a en `--source`) | R12.2 lo lista (03:803), R12.5 lo compone (03:846), R27.1 (03:1727) |
| Y-2 | Tracking por opción (R13.6a) | R13.6 (03:2324) y el carrier en `context/06:352`: el `Tracking` del candidato, puesto en la opción |
| Y-3 | `@executeOnce`/`@startWithOffset` en overlay (R34.1a, R34.9a) | `context/06:175` y `:183`, los atributos de la 6ta (ADR 0024, 0028). La v12.6 todavía dice lo contrario (`sgai-spec.src.md:5131`, R-PUB-5) y el v13 lo retira |
| Y-4 | R40.4/R40.9 retoman, PLY-49 termina | ADR 0025: retomar. R40.9 (03:2170), R40.4 (03:2209), UC-22 (04:2040) |
| Y-5 | §5.1.3 MAY vs R34.9 MUST | ADR 0028: MUST desde el primer candidato (03:1272) |

## Decisiones de norma (las toma el líder del proyecto)

Cada una con el texto de hoy, la evidencia, las opciones y la recomendación.
Las citas de la 6ta están verificadas contra la copia primaria; las de
nuestro texto, contra su línea.

**Criterio de toda la fase (el líder, 2026-11-26, al decidir N-3):** donde
DASH tiene un mecanismo nativo, el requisito es **usarlo**, no re-describir
cómo se comporta. Re-describir cuándo se despacha un beacon es el camino a
reinventar el callback. Lo que nuestro texto agrega es sólo lo que la base no
define.

### N-1. R12.5: ¿60% / 25% es área o lado?

- **Hoy:** 03:842 *"the upper-left 60% of the frame"*; :844 *"the centre-left
  25% of the frame"*; :846 *"the centre 60% of the frame"*.
- **Problema:** no dice área ni lado, ni dónde va el double box. Sin FAIL: la
  referencia (`sgai-compositor.js:39`, *"read as AREA … sqrt(0.60) = 77.46%"*)
  y R12.5-1/R27.1 leen área, marcado `[inferred]`.
- **Decidido (el líder, 2026-11-26): rectángulos explícitos por token**, con
  los valores de la lectura por área, cada valor con su referencia y de dónde
  sale. Descartadas: "área" en la cabecera sin coordenadas (deja la
  ubicación inferida) y "lado" (cambia referencia y tests, y sigue sin fijar
  la ubicación del double box).
- **La fuente es la guía IAB final, no el borrador de diciembre de 2025.**
  *Ad Format Guidelines for Digital Video and CTV* es final desde 2026-07-22:
  `v2.0.md` del repo `InteractiveAdvertisingBureau/Ad-Format-Guidelines-for-Digital-Video-CTV`.
  Su línea 121: *"L-Shape - The content will take up 60% of the 1920 x 1080
  screen…"*, el Frame igual, *"Double Box Video - Each box … 25%"*; la 120, el
  underlay de 1920×1080 con su recorte; la 125, el placement. No dice área ni
  lado, ni coordenadas.
- **Los videos de ejemplo** de la landing (`iabtechlab.com/standards/ctv-ad-portfolio/`,
  1920×1080), medidos, dan la lectura por área. Son ilustrativos, no
  normativos, y la referencia lo dice así:
  - L-Shape ≈ 1473×828 en (0,0), ≈ 59% del área;
  - Double Box: cajas ≈ 960×535, centradas en vertical, mitad izquierda y
    mitad derecha, ≈ 24,8% cada una;
  - Frame ≈ 1390×781 centrado, ≈ 52%. El texto dice 60% y se sigue el texto;
    la diferencia se anota.
- **Los rectángulos** (x, y, ancho, alto en % del viewport):
  - `squeezeback-l-shape-upper-left`: 0, 0, 77,46, 77,46 (√0,60);
  - double box: 0, 25, 50, 50 y 50, 25, 50, 50 (√0,25 = 50%);
  - `squeezeback-frame`: 11,27, 11,27, 77,46, 77,46 (centrado, √0,60).
- **Qué cambia:** la tabla de R12.5 en `context/03` (T-01), citando `v2.0.md`
  fijado a un commit (T-10); R12.5-1 y R27.1 pierden el `[inferred]` (T-02);
  la referencia no cambia, salvo sumar el frame cuando exista su token (Y-1).

### N-2. R36.1: offset 0 en una ventana de pausa

- **Hoy:** 03:1424 *"measured from the start of the window … never from the
  pause"*; 03:1431 *"An offset of zero means the window is resolved only when
  it fires."* El Annex H.3 (src:4228) dice *"the Player may resolve it from
  the start of playback; this Player resolves at the pause instead"*.
- **Problema:** con offset 0 en pausa, la primera frase deja resolver al
  inicio de la ventana y la segunda sólo en la pausa. La referencia toma la
  segunda y se la atribuye a H.3, que dice la primera. Dos huecos más: nada
  dice qué ve el viewer hasta que llega el aviso de pausa (UC-08 lo espera en
  30 000 exacto y falló una vez en 30 449), ni cuánto puede retener el
  contenido un Player que sólo resuelve en el PRT (R40.9-3, R40.3-2).
- **Decidido (el líder, 2026-11-26): el offset sólo pone el piso del pedido,
  para las dos familias; la frescura la declara el APS (R36.4).** Descartadas:
  "sólo cuando dispara" para la pausa (dos reglas de offset, y un video de
  pausa nunca arranca en el instante de la pausa) y borrar la frase sin decir
  qué la reemplaza.
- **Texto exacto para `context/03`:**
  - R36.1: sale *"An offset of zero means the window is resolved only when it
    fires."* Entra: *"An offset of zero means the window may be resolved from
    its start, never before it. The offset bounds only how early a resolution
    may be requested; how fresh it must be when the opportunity fires is
    declared by the APS (R36.4): a resolution whose usable lifetime is zero is
    usable only if it arrives when the opportunity fires."*
  - R36.8 nuevo (Player): *"When a pause opportunity is resolved after the
    pause, the Player MUST keep the paused primary frame on screen until an ad
    begins rendering, and MUST NOT cover it with a blank or loading surface. If
    no usable resolution arrives within a time the Player chooses, the pause
    continues with no ad, as for an empty resolution (R30)."* Sin número de
    timeout, como R6. R36.8 está libre: "Retired identifiers" retira R36.2,
    R36.3 y R36.6, no R36.8.
  - R36.4, R36.5 y R36.7 no cambian.
- **Qué arrastra:**
  - T-01: el texto de arriba; R36.8 entra al catálogo del nivel 2 y a la
    población de conducta (un criterio más).
  - T-02: los tests de R36.1 (R36.1-1 a -3) reescritos contra el texto nuevo;
    un test nuevo de R36.8 (pausa resuelta después de la pausa: el cuadro
    pausado sigue en pantalla, nada en blanco, y sin resolución a tiempo la
    pausa sigue sin aviso). UC-08 acepta el pedido al inicio de la sesión, y
    sus tiempos de restauración se corrigen contra el texto.
  - T-03: `preResolvePause` precarga la pausa desde el inicio de la ventana;
    la cabecera de `sgai-nonlinear.js` (línea 70, que hoy atribuye la otra
    lectura a H.3) dice la nueva.
  - El v13: Annex H.3 muestra la precarga.
- **Lo que esta decisión no cubre:** la cota a cuánto puede retener el
  contenido un Player que sólo resuelve en el PRT de un corte lineal (R40.9-3,
  R40.3-2). Queda abierto.

### N-3. R13: el despacho de los beacons es el de DASH

- **Hoy:** R13.1 (03:2307) *"Each beacon MUST fire when the presentation of
  its ad reaches its time"*; R13.3 (03:2343) *"A beacon whose time falls after
  the presentation of its ad has ended … MUST NOT be fired."*; la spec PLY-80
  (src:1385) *"stop firing the remaining beacons at the trim boundary"*.
- **Problema:** las dos frases re-describen el despacho, y por eso quedaron
  huecos que DASH ya contesta: el beacon justo en el borde, y el seek dentro
  de un overlay. La 6ta, §5.10.2.4: *"A previously processed event will be
  dispatched as if it was encountered for the first time in case it is
  encountered due to a time-shift (seek) operation"* (verificado contra la
  copia primaria). La referencia hoy no re-despacha en un seek interno.
- **Decidido (el líder, 2026-11-26): A, usando lo nativo.** Texto exacto para
  `context/03`:
  - R13.1: sale *"Each beacon MUST fire when the presentation of its ad
    reaches its time"*. Entra: *"The Player dispatches them as the base
    specification dispatches callback events (DASH §5.10, §5.10.4.5), seeks
    included."*
  - R13.3 queda en lo que DASH no define: *"A trim, a dismissal or a resume
    ends the ad's presentation timeline at that instant; its events are
    dispatched under R13.1 up to and including that instant."* El `complete`
    en el borde sale de ahí.
  - R34.6 suma sólo: *"A seek whose origin and destination both lie inside
    the window's range is not an entry: the execution continues with the ad
    being presented, and no new resolution is requested."* Nada sobre
    beacons: eso es R13.1.
  - R13.9 nuevo (spec document): *"The specification MUST include an
    informative annex on reading the beacons received: worked examples of what
    the Player dispatches on a seek back, a seek forward, a trimmed ad and a
    re-execution, for whoever computes what was viewed. The annex adds no
    rule."* R13.9 está libre (la tabla de retirados sólo tiene R13.2).
- **Qué arrastra:**
  - T-01: el texto; R13.9 al catálogo del nivel 2 (spec document: lo juzga el
    v13, que escribe el anexo).
  - T-02: un test de seek atrás dentro del overlay (los callbacks ya
    despachados se despachan de nuevo, sin pedido nuevo); uno de seek
    adelante dentro del rango; el negativo del borde (el evento en el instante
    del corte se despacha, uno después no); R13.3-4 deja de decir que su
    lectura es del test.
  - T-03: la referencia re-despacha en un seek interno (§5.10.2.4) sin
    re-resolver.
  - El v13: el anexo de R13.9 y PLY-80 alineado.
- **Las otras re-descripciones del despacho**, encontradas buscando `fire`,
  `firing` y `dispatch` en todo `context/03`. **Decididas (el líder,
  2026-11-26):**
  1. R13.8 (03:2339) *"The specification defines which beacons the Player
     fires and when"*: sale "and when"; el cuándo es de DASH.
  2. R13.7 (03:2330), los beacons de slot: **se eliminan** (less is more).
     El anexo de R13.9 muestra cómo reconstruir el inicio y el fin de la
     ventana con los beacons de los avisos, incluido el corte por el tope (un
     aviso cortado antes de su `complete`). R13.7 va a "Retired identifiers".
  3. R34.6 (03:1260): la entrada *"a seek back to a point before its end"* se
     acota a "a seek back from beyond its end", y deja de chocar con la frase
     del seek interno.
  4. R6.5 (03:2261): sale la regla del Player (*"are one beacon and fire
     once"*): DASH ya deduplica por `@id` (§5.10.2.4). "The same URL at the same
     presentation time" pasa a ser una regla del servidor: el APS no emite
     duplicados.
  5. R40.9 (03:2175) *"or fire the slot-start beacon again"* y la
     introducción de R16 (03:1119) *"ceases firing further tracking beacons"*:
     la repetición se reemplaza por una referencia a R13.3. R16.1 ya la tiene
     (03:1134).
  - No son re-descripciones, porque DASH no tiene nativo: R13.6 (alcance por
    opción), R42.1 (beacons de ocurrencia, *"never from the timeline"*), R47.1
    (viewability), R34.3 (ventana consumida: no se presenta, no hay beacons).
- **Lo que referencia a R13.7** (`grep -rn "R13\.7\|slot-start\|slot-end"` en
  `context/`, `spec-source/`, `bin/conformance/`, `reference-player/src/`,
  `.project/`, `output-analysis/`; la spec v12.6 no lo tiene: sin carrier):
  - `context/03`: :123 (fila del índice de Interfaces), :1267 (R34.6, *"its
    own beacons (R13, R13.7, R42)"*), :2175 (R40.9), :2330 (el criterio).
  - `context/04`: UC-06 :783–788 ("Slot beacons"), UC-21 :1973–2008, UC-22
    :2021–2042.
  - `context/06`: :326 (la lista de requisitos con carrier nuevo) y :354
    (el carrier de los beacons de slot).
  - Vectores: `UC-06.yaml:97`, `UC-21.yaml:11` y `:205`, `UC-22.yaml:11` y
    `:123` (entradas `missing_carrier`).
  - Nivel 2: `bin/conformance/spec/catalog.py:235` (regla NOT_VERIFIABLE sin
    carrier) y `pins.json:122`.
  - `spec-source/scenarios/README.md:152` (la lista de criterios sin carrier).
  - Registros, que no se reescriben: ADR 0023 y 0025 (una nota fechada al
    pie), `output-analysis/v12.7-context-delta.md`. `roadmap/major-build-v13`
    deja de esperar el carrier de R13.7 (su línea 14).
  - La referencia no lo implementa: nada que sacar.
- **Pendiente del OK del líder, no planificado:** la línea de tiempo del slot
  de un aviso de pausa sin media (una imagen, HTML).

### N-4. R4.5: ningún documento conforme la ejercita

- **Hoy:** 03:648 *"When the actual rendered length of an accepted candidate
  exceeds its declared duration, the Player MUST enforce the cap against
  actual length"*. La spec pide un test (R-PLY-13, src:5180).
- **Problema:** `behaviour/index.yaml:56` la deja sin test: el video no pasa de
  `Period@duration`, la List MPD toma el menor, imagen y HTML duran exacto.
- **Opciones:**
  - A. Retirarla, absorbida por R4.2 + R4.11 (el tope en la línea de tiempo
    del slot). Se borra la entrada del índice.
  - B. Reformularla como robustez ante media defectuosa, con un fixture no
    conforme. No verificado que el formato lo admita.
  - C. Dejarla, y que R-PLY-13 diga NOT_VERIFIABLE con el mismo motivo.
- **Recomendación: A.** Una obligación que nada conforme puede activar no
  compra nada.

### N-5. La 6ta: "QE is reset" al terminar re-ejecuta una inserción

- **Hoy:** 6ta §5.16.2.2.5 paso 1a: *"QE is reset, as described in clause
  5.16.2.2.3 above"*; con RT = PRTA (Table 57) el evento sigue activo y vuelve
  a la cola. A.14.5 (informativo) no resetea. Nada en 03.
- **Problema:** leída literal, una inserción con `@executeOnce="false"` se
  re-ejecuta para siempre. Sin FAIL (la referencia toma A.14.5); el mutante
  literal lo caza E2.
- **Opciones:**
  - A. Lectura en 03 (R1.5): al terminar, el evento no vuelve a la cola; se
    re-ejecuta sólo si el playhead *entra* de nuevo. Se apoya en §5.16.2.2.1:
    *"An event is executed every time the playhead enters the active
    interval"*. E2 pasa a test de conducta.
  - B. Sólo `[DISCUSSION]` al WG y una fila en "Deliberately open": un Player
    en loop sería conforme.
  - C. A + B.
- **Recomendación: C.** La lectura tiene ancla en la 6ta; la contradicción
  interna es de ISO y sólo el WG la corrige.

### N-6. La 6ta: un evento justo en el fin del Period

- **Hoy:** §5.10.2.1 *"Events shall terminate at the end of a Period"*; A.13.7
  despacha *"at the presentation time of the corresponding media sample"*, y en
  el fin no hay sample. `context/05:346` pone el `complete` en 15000 de un
  Period de 15 s. Para lo no lineal ya está resuelto (src:2535).
- **Problema:** el `complete` de todo aviso convertido de VAST cae en ese
  borde; un Player puede no dispararlo nunca. Sin FAIL (la referencia usa
  `≤`).
- **Opciones:**
  - A. Lectura en 03 (R1.5): un evento on-start en el fin de su Period se
    despacha cuando la presentación llega a ese fin. Un test nuevo.
  - B. Al APS: el callback de fin va estrictamente adentro del Period (un
    frame antes). Cambian `context/05:346` y la tabla VAST→ListMPD.
  - C. A + `[DISCUSSION]`.
- **Recomendación: C.** Coherente con el no lineal y no obliga a los APS.

### N-7. La 6ta: `@clip` corta la latencia de ejecución

- **Hoy:** Table 57 *"APDadj = max(APDmax -PRTA + PRT, 0)"*; §5.16.2.2.1 paso 4
  *"Typically, the event is executed at its scheduled time, i.e. PRTA = PRT"*;
  §5.16.2.2.6 nombra los atrasos: join, seek, un alternativo previo. R4.6
  (03:606) *"a late start shortens it"*.
- **Problema:** un Player ve el PRT un tick tarde, corta el aviso por esa
  diferencia y el `complete` no sale (mutante M1 de T-08: *"complete expected
  at 8000 | observed at never"*). La referencia lo tapa con una tolerancia
  (`sgai-linear.js:789`).
- **Opciones:**
  - A. Lectura en R4.6: por reproducción normal PRTA = PRT; el atraso que
    `@clip` descuenta es el de join, seek o alternativo previo. La referencia
    saca el parche.
  - B. Tolerancia explícita: un corte no mayor que la latencia de ejecución
    cuenta como fin. Un número sin base en la 6ta.
  - C. A + `[DISCUSSION]`.
- **Recomendación: A.** Ya está en el texto normativo; no hace falta el WG.

### N-8. La 6ta: el blanco al volver a RT

- **Hoy:** §5.16.2.2.6 *"the playhead moves to the resumption time"*;
  "seamlessly" sólo para la ejecución fallida. Nada en 03. El reloj del
  formato congela hasta 1000 ms por transición (`scenarios/README.md:58`).
- **Problema:** la referencia mide 376–1025 ms sin nada en pantalla; bajo
  1000 ms queda como nota, nunca FAIL.
- **Opciones:**
  - A. Criterio con número ("primer frame a ≤ X ms"). Testeable, pero sin base
    para X, y la referencia hoy lo rompe (1025 ms).
  - B. Calidad de implementación: fila en "Deliberately open" y
    `[DISCUSSION]`; los 1000 ms quedan como regla del instrumento.
  - C. SHOULD sin número. No testeable.
- **Recomendación: B.** No hay fuente para un número.

### N-9. Alternativa en vivo acoplada a la latencia (UC-14, 6 FAIL)

- **Hoy:** §5.16.2.2.6 *"When alternative media presentation is a live
  presentation, it always starts at the live edge"*; PHPLE es *"wall-clock
  time NOW"*. Ningún MPD del Annex N declara `@suggestedPresentationDelay`.
  N.4 (src:4807): *"Its overlay window opens one minute into the slate"*.
- **Problema:** nada ata la demora del principal con el arranque del
  alternativo. En UC-14 D1 el slate entra con su tiempo en 66 198, no 60 000;
  la ventana queda 13,8 s de 20 y el `complete` no sale.
- **Opciones:**
  - A. Lectura en 03: el borde del alternativo se toma con la misma demora
    con que se reproduce el principal (el NOW literal es inalcanzable, así que
    todo Player elige alguna). La referencia arranca el slate en su borde
    menos esa demora.
  - B. Del Publisher: el mismo `MPD@suggestedPresentationDelay` en los dos
    MPD; N.4/N.7 dejan de suponer latencia igual y el vector se ensancha.
    Ningún Player cambia.
  - C. A o B, más `[DISCUSSION]` sobre qué demora quiere decir "live edge".
- **Recomendación: A + `[DISCUSSION]`.** El resultado de UC-14 sólo vale con
  latencia igual, y hoy nada la garantiza.

### N-10. Un reemplazo que no es publicidad (UC-14 7 FAIL, R40.6 4 FAIL)

- **Hoy:** 03:2099 *"Whether an alternative presentation is an ad is therefore
  not observable by a Player (ADR 0012), and no rule here depends on it."*;
  04:1649 *"This specification does not specify blackouts."* UC-14.yaml:25
  *"The format has no element for the slate"*.
- **Problema:** la spec ya tiene posición; el formato no. El slate y la
  alternativa de R40.6 se escriben `shows: []`, la referencia los marca
  `ad` y el comparador los lee como aviso lineal.
- **Opciones:**
  - A. Sólo el formato y la observación: `element: alternative` para todo lo
    que ejecuta un evento lineal heredado, `selection` lo registra sin
    llamarlo aviso, la referencia lo marca neutro. Se reescriben UC-14 y R40.6.
  - B. Un carrier del Publisher que diga "no es publicidad". Contradice R40 y
    ADR 0012; es un constructo nuevo.
  - C. `[DISCUSSION]` para que MPEG le dé valores a `EventStream@value`.
- **Recomendación: A.** La spec ya dice lo correcto; los 11 FAIL son del
  instrumento.

### N-11. UC-07 / Annex G.9 sin documento de resolución (10 FAIL)

- **Hoy:** 04:821 *"Expected behavior (uniform across device classes
  D1..D5)"*; G.9 (src:4192) dice que un Player de esta spec resuelve el overlay
  desde 840 s, pero el Annex G no trae esos documentos. UC-07.yaml: D1–D5 con
  resultados legacy y las ventanas contestadas 404.
- **Problema:** la referencia pide las ventanas y el vector espera que no
  pida nada. No es de la 6ta: es nuestro anexo.
- **Opciones:**
  - A. Completar el Annex G: documentos de overlay y pausa, resultado de G.9
    por clase. Duplica lo que UC-17 / Annex Q ya cubre.
  - B. UC-07 queda sólo para legacy: en 04 D1–D5 pasan a "—", `check-scenarios`
    exige sólo `legacy`, G.9 remite a UC-17.
- **Recomendación: B.** El sujeto de UC-07 es el Player legacy, y el caso
  Player de esta spec ya está en UC-17.

## Decisiones de ejecución

### D-1. La clase legacy es el dash.js fijado más el lineal de la 6ta

El glosario (99:202) define el Player legacy como *"a Player conforming to
MPEG-DASH 6th edition that does not implement this specification"*: hace el
lineal de la 6ta e ignora `svta`. El instrumento de hoy es dash.js 5.3.0 solo,
que no trae `alternativeMPD`, y por eso los 18 FAIL `legacy` de UC-07, 11, 14,
17 y 22 miden al instrumento. La referencia ya separa las familias
(`sgai-reference.js`, `FAMILY_FILES`): el modo `legacy` carga el esqueleto y
`sgai-linear.js` con la extensión ignorada. Sigue siendo el mismo dash.js que
la base de la referencia (ADR 0075). El nivel 3a (`--players`, dash.js y
Shaka solos) no cambia: mide otra cosa.

| Alternativa | Por qué no |
|---|---|
| Shaka 5.3.6 como legacy | No verifiqué que traiga el lineal de la 6ta; suma un segundo Player a la batería |
| `NOT_APPLICABLE` para lo lineal de legacy | Esconde cobertura en lugar de medirla |
| Reescribir los vectores legacy sin corte | Contradice el glosario: un legacy de la 6ta sí hace el corte |

### D-2. El formato de vectores dice capacidades por clase

`sends_capabilities` pasa a poder ser por clase (Annex M.3 lo pide así;
UC-13 D3/D4), y la capacidad de sesión (UC-19 D1: 1 decoder con contenido
protegido) sale del perfil de la clase y no del vector. 3 FAIL.

### D-3. Los vectores mal escritos se corrigen contra el texto

UC-08 `mid` del overlay restaurado en 75 000 (no 85 000); UC-11 lista los
beacons de ClickThrough; las oportunidades de UC-07, 08, 11 y 17 nombran su
esquema (los 29 NOT_VERIFIABLE por oportunidad ambigua). Cada corrección
contra la línea de `context/04` o del anexo que la dicta, nunca contra lo que
la referencia hace.

### D-4. Lo inestable se arregla en la causa, no en la tolerancia

R40.3-2 D1 (aviso 445 ms tarde), R28.1-1 D1 [no-activation] (264 ms) y UC-12
D1 (`complete` 7 213 ms tarde) dan PASS solos. Se reproducen con
`--cpu-throttle` (o carga propia, bajada por su PID), se busca dónde entra
tiempo de pared en lo que el reloj de presentación debería no contar (una
espera de red, un timer, un stall), y se arregla ahí. Ensanchar la tolerancia
se descarta: un atraso real de 1 s tiene que seguir dando FAIL.

### D-5. Cómo cae una decisión de norma

Un commit por decisión en `context/`, con el porqué en el mensaje. En el mismo
pase: las citas de las reglas del nivel 2 (`bin/conformance/spec/`) que
transcriben la oración cambiada, los hashes de los tests y vectores de ese
criterio, y el test que lo cubre, visto fallar (ADR 0085). Los gates de
`context/` (Steps 0–0.7) en verde. `spec-source/` (la prosa) y `dist/` no se
tocan: el v13 los absorbe. Los `[DISCUSSION]` al WG salen como borradores; los
publica el líder del proyecto.

### D-6. La guía IAB se lee de la v2.0 final, fijada a un commit

Hoy el proyecto la lee de tres formas, todas del borrador: el paso 5 de
`build-all` regenera `context-analysis/iab-ad-templates.md` desde un Google
Doc vivo (`prompts/1-pre-spec/analyze-iab-ad-templates.prompt:5`) y por eso
"NEVER skips"; `context/03` la cita como *"public comment, Dec 2025"* con
páginas (R27 en 03:1656 *"pp.12-13"*, 03:1722 *"p.12"*) y el Doc en 03:789 y
`99-glossary.md:46`; y las ADR 0001, 0002 y 0004 la citan desde el Doc.

Pasa a leerse del `v2.0.md` del repo de IAB **fijado a un commit**, no a la
rama: una fuente fija es la que deja que el paso 5 se salte por el hash de su
entrada (`bin/step-inputs.py`, ADR 0072) en lugar de correr siempre, y la que
hace que una cita por línea siga siendo verdad. Las citas de `context/` pasan a
v2.0 con fecha, commit y línea; el mirror se regenera; las ADR se anotan con
una nota fechada, porque son inmutables y lo que cambió es la fuente, no la
decisión (si una decisión dejó de valer por lo que dice la v2.0, es una ADR
nueva que la supersede). La guía de signaling de IAB y los códigos `pos` de
AdCOM 1.0 entran sólo si nuestro texto los toca: hoy el único rastro es
`iab-ad-templates.md:62`, que remite los *Placement Types* a `plcmt` de
OpenRTB/AdCOM y no genera filas. La task lo confirma buscando en todo el
alcance y lo deja escrito.

| Alternativa | Por qué no |
|---|---|
| Seguir la rama viva del repo | Una cita por línea deja de valer con el próximo commit de IAB, y el paso 5 no se puede saltar |
| Copiar `v2.0.md` al repo | Es un documento de terceros; alcanza con el commit y la URL |

### D-7. La batería entera, una vez, al cierre

Opt-in como siempre (ADR 0087), con la máquina sin carga ajena y
concurrencia igual a los núcleos (2). Mientras tanto cada task corre sólo los
jobs que toca, con un resumen por FAIL y el detalle en archivo. Sin capturas.

## Lo que no se hace

- Correr el v13, ni un incremental: es `major-build-v13`, que pasa a depender
  de esta fase.
- Los tests de las mitades sin carrier (Y-1 a Y-3): después del v13.
- Publicar issues en GitHub, pushear.
- Lo que el formato no puede expresar (color de región, audio): es otra fase.
