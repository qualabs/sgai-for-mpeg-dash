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

## Decisiones de norma (tomadas por el líder del proyecto, 2026-11-26/27)

Cada una con el texto de hoy, la evidencia y lo que el líder decidió.
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
  fijado a un commit (T-09); R12.5-1 y R27.1 pierden el `[inferred]` (T-02);
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
- La línea de tiempo del slot de un aviso de pausa sin media: N-12.

### N-12. La línea de tiempo del slot de pausa, `repeat` y su ejemplo

- **Hoy:** la spec §3.1 (src:366) *"For a pause slot it is the timeline of the
  pause ad itself, which advances while the pause ad plays … In every case it
  advances at the playback speed of the primary content (§4.5.12)."* Una imagen
  o un HTML no tienen línea de tiempo propia, y en pausa el principal está
  quieto: la regla no dice sobre qué se miden sus beacons ni su
  `dismissAfter`, y "a la velocidad del principal" no tiene sentido con el
  principal en pausa. R32.1 (03:1158) `repeat` *"the sequence is presented
  again from the start"* no dice si los beacons vuelven a dispararse.
- **Decidido (el líder, 2026-11-26):**
  1. Spec §3.1, la parte de pausa, pasa a: *"For a pause slot it is the
     timeline of the pause ad itself, which advances while the pause ad is on
     screen even though the primary content's presentation time is frozen
     (§4.5.10). A pause ad with no media timeline of its own (an image, an
     HTML document) gets one from the Player: it starts at zero when the ad is
     first rendered and advances at the rate of the wall clock while the ad
     stays on screen. For a linear or an overlay slot it advances at the
     playback speed of the primary content (§4.5.12); a pause slot advances at
     normal speed, since the primary content is paused."* En `context/03`: una
     frase de cierre en la introducción de R16 y un criterio nuevo del Player:
     para un aviso de pausa sin línea de tiempo de media, su línea de tiempo
     del slot empieza en cero al primer render y avanza al ritmo del reloj de
     pared mientras está en pantalla; sus beacons y su `dismissAfter` se miden
     sobre ella.
  2. R32.1 `repeat` suma *"each pass is a new presentation of each candidate,
     and its beacons fire again"*; en la spec, PLY-65 igual.
  3. Un ejemplo trabajado en el anexo de pausa: un solo candidato imagen con
     `@duration` (30 s) y `onExhausted="repeat"`, que cubre toda la pausa, con
     los beacons por pasada y la pasada cortada al reanudar (R13.3). Encaja en
     el Annex E: E.7 hoy muestra `request-again` y termina diciendo qué haría
     `repeat` (src:3976); el ejemplo es una variante de E.7.
- **El número del criterio nuevo es R16.3, no R16.2.** R16.2 está retirado
  (03:2922, `| R16.2 | R13.3 |`), y `check-context-interfaces.py` rechaza un
  identificador retirado citado fuera de su tabla.
- **Una secuencia de candidatos: elegí una línea de tiempo continua por
  slot, hecha de un tramo por aviso.** Empieza en cero cuando el primer
  aviso del slot empieza a renderizarse y sigue a través de la secuencia y de
  las pasadas de `repeat`. Cada aviso ocupa un tramo de ella, que avanza con su
  media o, sin media, con el reloj de pared. Los beacons de un aviso se miden
  desde el inicio de su tramo (R13.1 ya los fecha *"relative to the
  presentation of the candidate that hosts them"*), así que empiezan en cero
  en cada aviso y en cada pasada. El `dismissAfter` se mide sobre la línea
  continua, porque es del slot: la spec lo mide *"from the moment the slot
  begins rendering"* (PLY-74, src:1349) y una línea por aviso lo reiniciaría
  en cada aviso. Esto precisa "sus beacons y su `dismissAfter` se miden sobre
  ella" del texto del líder: los beacons sobre el tramo del aviso, el
  `dismissAfter` sobre el slot. Una pausa no tiene tope (R31.2), así que el
  tope no entra.
- **Dónde cae:** `spec-source/sgai-spec.src.md` no se toca en esta fase (D-5).
  El criterio de R16 y la frase de R32.1 van a `context/03`; el ejemplo, a
  UC-05 en `context/04` como variante `repeat` con una imagen, que es de donde
  el v13 escribe el Annex E. El texto exacto de §3.1 y de PLY-65 queda en
  `roadmap/major-build-v13` como texto decidido para el build.
- **Tests:**
  - un aviso de pausa imagen con un beacon a 2 s lo dispara 2 s después del
    render, con el principal a 2x;
  - `repeat` sostenido dos pasadas o más dispara los beacons una vez por
    pasada, y la última pasada se corta al reanudar según R13.3;
  - una secuencia de dos imágenes: el beacon del segundo aviso se mide desde
    su render, y el `dismissAfter` desde el del primero.
- **La referencia:** `sgai-nonlinear.js:717` avanza el reloj de pared por
  `playbackRate` del principal; T-03 verifica que en un slot de pausa no lo
  haga (el test de 2x lo decide) y que `repeat` (`:1086`) abra una presentación
  nueva por pasada.

### N-4. R4.5: media del aviso más larga que lo declarado

- **Hoy:** 03:648 *"When the actual rendered length of an accepted candidate
  exceeds its declared duration, the Player MUST enforce the cap against
  actual length"*. Ningún documento conforme la activa, y
  `behaviour/index.yaml:56` la deja sin test.
- **Decidido (el líder, 2026-11-27): se queda, como regla defensiva.** La
  media viene de terceros con defectos (segmentos declarados de 2 s que miden
  2,1 o 2,3 s), y quien diseña el Player tiene que saber qué se espera. Dejarlo
  sin decir es un hueco. Imagen y HTML no aplican: duran exacto su
  `@duration`.
- **Lo que dicen la base y dash.js** (6ta verificada contra la copia
  primaria):
  - §5.3.5.1 *"A Representation starts at the start of the Period PeriodStart
    and continues to the end of the Period"*; §7.2.1 nombra los segmentos
    *"longer … than indicated by the Period duration"* y ajusta el playout al
    borde. El sobrante se recorta en el fin del Period.
  - Con `SegmentTemplate@duration` la duración es *"constant approximate"*
    (§5.3.9.2.1) y la deriva admitida es `@tolerance` (default 50%) de
    `@duration` (§7.2.1). Segmentos de 2,2 s declarados de 2 s son conformes
    hasta que la deriva pasa 1 s (unos 5 segmentos); con `SegmentTimeline`
    *"@d … shall represent the accurate presentation duration"* (§5.3.9.6) y no
    lo son.
  - La alternativa lineal termina en lo declarado: Table 57 `APD` es la
    duración *"defined by the MPD"*, y §5.16.2.2 paso 5 presenta *"for
    duration min(APDE, APDA)"*; el caso "más larga" no existe en el modelo.
  - dash.js 5.3.0 ya corta en el fin del Period: `appendWindowEnd = sInfo.start
    + sInfo.duration` (`dash.all.debug.js:37369`, más 10 ms, `:37235`;
    `useAppendWindow: true`, `:23305`).
  - La referencia ya corta en lo declarado: lineal por `Part.duration`
    (`sgai-linear.js:525`, `:698`), no lineal por la línea de tiempo del slot
    (`sgai-nonlinear.js:760`).
- **El texto actual pide lo contrario de la base**: "enforce the cap against
  actual length" contradice Table 57, no es observable y le correría al
  siguiente candidato y a los beacons. El texto nuevo corta en lo declarado.
- **Texto para `context/03`:**

  > **R4.5** (Player): When the media of an accepted candidate runs longer
  > than its declared duration (R19.3) — a third-party encode whose segments
  > are longer than its MPD states — the Player MUST end the candidate at its
  > declared duration and MUST NOT present the media past it, as the base
  > specification ends a Representation at the end of its Period (§5.3.5.1).
  > The next candidate, or the primary content, starts at that point; the cap
  > (R4.2, R4.6) and the beacon schedule (R13.1) are computed on declared
  > durations and are not moved by the excess. A form with no media timeline
  > (image, HTML) cannot run longer and is outside this criterion.

- **UC-23 para `context/04`** (más su fila en la tabla de cobertura):

  > ### UC-23 — A third-party ad whose media runs longer than declared
  >
  > **Scenario:** A VOD programme carries an inherited linear insertion at
  > 10:00 (`InsertPresentation`, UC-02), maximum duration 30 s (R4), resolved
  > to a List MPD of two 15 s ads, A and B. A's third-party encode declares
  > 2 s segments that are 2.2 s long, so its media runs about 1.5 s past its
  > declared 15 s.
  >
  > **Publisher intent:** a 30 s break of two 15 s ads, whatever the ad media
  > does.
  >
  > **Expected behavior:** on every device class (D1–D5):
  > - **0–15 s of the break.** A is presented; its beacons fire on its
  >   declared schedule. At 15 s A ends (R4.5); its surplus media is not shown.
  > - **15–30 s.** B starts at 15 s, from its beginning, and plays whole; the
  >   cap is not reached early.
  > - **The programme returns at 10:00** (`RT = PRTA`, Table 57).
  > - **The same candidate as the video option of an overlay** (D1, D2; D3–D5
  >   select an image option or skip, as in UC-03): removed at its declared
  >   duration.
  > - **Legacy Player** — executes the break with its base semantics (§5.16)
  >   and ends A at its declared duration, as its Period ends.
  >
  > **What this demonstrates:** a declared duration is a promise the Player
  > keeps for the ad, so a defective encode costs its own surplus and nothing
  > of the ads after it.

  La línea legacy queda: un legacy de la 6ta (D-1) sí ejecuta el corte, y
  corta en lo declarado igual, porque su dash.js recorta en el Period. T-01 la
  escribe así: *"**Legacy Player** — executes the break with its base
  semantics (§5.16) and ends A at its declared duration, as its Period
  ends."*
- **Tests:**
  - `R4.5-1` (lineal): inserción a los 2 s con `@maxDuration` 10 000 (el tope
    no acota), List MPD de ad1 (5 s declarados) y ad2 (4 s). ad1 trae
    segmentos **reales de 2,2 s declarados de 2 s**. Esperado en D1:
    0–2000 principal, 2000–7000 ad1, 7000–11000 ad2, 11000– principal desde
    2000; `imp` de ad2 a los 7000. Un Player que espera el fin real de la
    media muestra ad1 hasta ~8500 y falla con la tolerancia de 250.
  - `R4.5-2` (no lineal): ventana overlay, un candidato de video con el mismo
    ad1, removido a los 5 s declarados, `complete` ahí.
  - Se sale de `behaviour/index.yaml` la entrada de R4.5.
  - **Visto fallar:** con la referencia mutada para terminar en el `ended`
    del video y `useAppendWindow: false`. Sin esa mutación el test no puede
    fallar en un Player sobre dash.js, porque dash.js ya recorta: el test
    juzga al Player que no lo tiene, y eso se dice en su cabecera.
- **Lo que hay que construir:** hoy el harness corta la media exactamente en
  lo que declara el MPD (`bin/conformance/players.py:316`, `-seg_duration`) y
  exige una duración entera que divida los 32 s de contenido (`:212`). El
  fixture de 2,2 s pide un override de la duración real por fixture, y una
  marca en el vector de "media defectuosa a propósito, documento conforme",
  porque `expect_red` exige que fallen reglas de documento y acá no falla
  ninguna (el nivel 1 no mira la media). Va en T-06. Un `Period@duration`
  que no es múltiplo del segmento (PT5S con segmentos de 2 s) no sirve: es
  conforme (A.3.3), no es el defecto que se pidió, y dash.js lo resuelve solo.
- **El v13:** PLY-26, PLY-37 y R-PLY-13 de la spec dicen el texto viejo; los
  reescribe el build desde `context/`.

### N-5. La 6ta: "QE is reset" al terminar re-ejecuta una inserción

- **Hoy:** 6ta §5.16.2.2.5 paso 1a: *"QE is reset, as described in clause
  5.16.2.2.3 above"*; con RT = PRTA (Table 57) el evento sigue activo y vuelve
  a la cola. A.14.5 (informativo) no resetea. Nada en 03.
- **Problema:** leída literal, una inserción con `@executeOnce="false"` se
  re-ejecuta para siempre. Sin FAIL (la referencia toma A.14.5); el mutante
  literal lo caza E2.
- **Decidido (el líder, 2026-11-27): lectura en 03, sin issue al WG.**
  Texto exacto para `context/03` (R1.7 está libre: R1 llega a R1.6 y la tabla
  de retirados no tiene ningún R1):

  > **R1.7** (Player): An insertion does not trigger itself again: resuming
  > inside the same event's active interval is not entering it (MPEG-DASH 6th
  > edition §5.16.2.2.1).
  >
  > Note: this looks obvious, and it is the intent of MPEG-DASH 6th edition.
  > It is stated because the letter of that edition says otherwise: when an
  > insertion ends, §5.16.2.2.5 step 1a resets the event queue, and the reset
  > re-adds every event still active at the return point, so read literally
  > an insertion with @executeOnce="false" would run again in a loop. Its
  > informative Annex A.14.5 does not do this.

- **"Deliberately open"** suma una fila: la contradicción entre el paso 1a de
  §5.16.2.2.5 y A.14.5, *Decided by MPEG*. "Recorded in" cita la ADR de esta
  decisión (la que escribe la generación del plan), como las otras filas citan
  la ADR 0021; ningún link al issue. El
  párrafo de abajo de la tabla dice *"The three rows above are the only
  questions this edition leaves open"*: pasa a cuatro.
- **Test** (E2 de los vectores de borde pasa a ser este test de conducta):
  inserción con intervalo activo 100–130 s, un aviso de 15 s,
  `@executeOnce="false"`. Se ejecuta una vez y el principal sigue desde los
  100 s; después de un seek a los 90 s se ejecuta otra vez al llegar a 100.
  Un Player en loop falla. Visto fallar con el mutante literal (el reset de QE
  al terminar), que hoy caza E2.
- **La referencia** ya toma la lectura de A.14.5 (cabecera de
  `sgai-linear.js:27`): no cambia.

### N-6. La 6ta: un evento justo en el fin del Period

- **Hoy:** §5.10.2.1 *"Events shall terminate at the end of a Period"*; A.13.7
  despacha *"at the presentation time of the corresponding media sample"*, y en
  el fin no hay sample. `context/05:346` pone el `complete` en 15000 de un
  Period de 15 s. Para lo no lineal ya está resuelto (src:2535).
- **Problema:** el `complete` de todo aviso convertido de VAST cae en ese
  borde; un Player puede no dispararlo nunca. Sin FAIL (la referencia usa
  `≤`).
- **Decidido (el líder, 2026-11-27): A, con una nota, sin WG.** Texto exacto
  para `context/03` (R1.8 queda libre después de R1.7):

  > **R1.8** (Player): An event at the end of its Period still fires: an
  > on-start event whose presentation time equals the end of its Period is
  > dispatched when the presentation reaches that end.
  >
  > Note: this looks obvious. It is stated because MPEG-DASH 6th edition
  > dispatches an on-start event at the presentation time of its media sample
  > (Annex A.13.7), and at the very end of a Period there is no sample: the
  > last frame starts slightly before it. Read literally, a Player could never
  > fire such an event, and that is where the `complete` beacon of every ad
  > converted from VAST falls.

- `context/05` queda como está: el beacon sigue en el fin del Period.
- **Test:** un aviso de 15 s con `complete` a los 15 s lo dispara; un Player
  que espera un sample a los 15 s falla (visto fallar con la referencia
  mutada para exigir el instante estrictamente antes del fin, en
  `fireCallbacks`, `sgai-linear.js:729`).
- **La referencia** ya lo hace: no cambia.

### N-7. La 6ta: `@clip` corta la latencia de ejecución

- **Hoy:** Table 57 *"APDadj = max(APDmax -PRTA + PRT, 0)"*; §5.16.2.2.1 paso 4
  *"Typically, the event is executed at its scheduled time, i.e. PRTA = PRT"*;
  §5.16.2.2.6 nombra los atrasos: join, seek, un alternativo previo. R4.6
  (03:606) *"a late start shortens it"*.
- **Problema:** un Player ve el PRT un tick tarde, corta el aviso por esa
  diferencia y el `complete` no sale (mutante M1 de T-08: *"complete expected
  at 8000 | observed at never"*). La referencia lo tapa con una tolerancia
  (`sgai-linear.js:789`).
- **Decidido (el líder, 2026-11-27): A, con una "Implementation note"** (esa
  etiqueta, literal). Criterio nuevo **R4.12**, escrito a continuación de
  R4.6. El número: R4 usa R4.1–R4.11 y retira R4.3; la regla 3 de "How
  requirements are written" deja los ids estables, y no hay sub-numeración
  `R4.6-x` en el archivo, así que es el siguiente libre. Texto exacto:

  > **R4.12** (Player): In normal playback an event counts as executed at its
  > scheduled time (PRTA = PRT, MPEG-DASH 6th edition §5.16.2.2.1 step 4). The
  > delay that @clip subtracts is only the one the base names: a join, a seek,
  > or a previous alternative still playing.
  >
  > Implementation note: a real Player always executes an event slightly
  > after its scheduled time, by the latency of the loop that detects it (a
  > few to a few hundred milliseconds). That latency is an implementation
  > tolerance, not a late start: it MUST NOT shorten the ad. Otherwise an 8 s
  > ad started 1 ms late is cut at 7.999 s and its complete beacon never
  > fires.

- **Test:** un aviso de 8 s arrancado con la latencia del loop dispara su
  `complete` a los 8 s; un Player que lo acorta por esa latencia falla (el
  mutante M1 de la fase 11, que hoy caza E12).
- **La referencia** saca su tolerancia ad hoc (`sgai-linear.js:789`, el
  `Math.max(EPS, alt.lag)`) y aplica la regla: en reproducción normal PRTA =
  PRT, y `@clip` descuenta sólo join, seek o alternativo previo. Ese mismo
  parche cubre hoy el evento en el fin del Period: al sacarlo, R1.8 (N-6) se
  tiene que seguir cumpliendo, y su test lo verifica.
- Sin WG.

### N-8. La 6ta: el blanco al volver a RT

- **Hoy:** §5.16.2.2.6 *"the playhead moves to the resumption time"*;
  "seamlessly" sólo para la ejecución fallida. Nada en 03. El reloj del
  formato congela hasta 1000 ms por transición (`scenarios/README.md:58`).
- **Problema:** la referencia mide 376–1025 ms sin nada en pantalla; bajo
  1000 ms queda como nota, nunca FAIL.
- **Decidido (el líder, 2026-11-27): sólo una "Implementation note"**, sin
  número, sin MUST, sin fila en "Deliberately open", sin nombrar el harness ni
  los 1000 ms. Texto exacto:

  > Implementation note: every transition, into an ad and back to the primary
  > content, is expected to be imperceptible: no black frames, no frozen
  > frame, no visible gap. A Player achieves it by preparing the next
  > presentation ahead of time (for example, preloading its first segments
  > before the transition). MPEG-DASH 6th edition does not quantify this, and
  > neither does this specification.

- **Dónde va: bajo R1.7** (N-5), después de su nota. Es el único criterio cuyo
  sujeto es la vuelta de un aviso lineal al principal. Busqué "return",
  "resum", "back to the primary" y "transition" en todo `context/03`; no hay
  un criterio general de transiciones. Los otros candidatos son más angostos:
  R4.6 trata el fin de un reemplazo bajo el tope, R16.1 la salida de la pausa
  (ya pide *"within one rendering frame"*) y R35.5 el descarte.
- El instrumento conserva su regla de 1000 ms tal como está (sólo
  instrumento). Ni test nuevo ni cambio en la referencia.

### N-9. Alternativa en vivo acoplada a la latencia (UC-14, 6 FAIL)

- **Hoy:** §5.16.2.2.6 *"When alternative media presentation is a live
  presentation, it always starts at the live edge"*; PHPLE es *"wall-clock
  time NOW"*. Ningún MPD del Annex N declara `@suggestedPresentationDelay`.
  N.4 (src:4807): *"Its overlay window opens one minute into the slate"*.
- **Problema:** nada ata la demora del principal con el arranque del
  alternativo. En UC-14 D1 el slate entra con su tiempo en 66 198, no 60 000;
  la ventana queda 13,8 s de 20 y el `complete` no sale.
- **Decidido (el líder, 2026-11-27): A, como SHOULD.** Criterio nuevo
  **R1.9**: va en R1 con las otras lecturas de la 6ta (R1.7, R1.8), y es el
  siguiente libre. Texto exacto:

  > **R1.9** (Player): When the alternative is a live presentation, the
  > Player SHOULD start it at its live edge minus the same delay at which it
  > was playing the primary content, so the viewer sees the alternative with
  > the same latency as the main presentation. MPEG-DASH 6th edition says a
  > live alternative "always starts at the live edge" (§5.16.2.2.6), with the
  > live edge defined as wall-clock time NOW; no Player plays exactly at NOW,
  > so each one picks a delay, and this criterion says which. Where that is
  > not possible, the Player starts it as close to that point as it can.

- **Los vectores, con un SHOULD: elegí que afirmen el caso alineado y que un
  desvío ahí no sea FAIL.** Los campos de UC-14 que dependen de la alineación
  (los tiempos del overlay sobre el slate y su `complete`, los 6 FAIL de hoy)
  llevan una marca nueva del formato, `strength: should`. El comparador
  informa un desvío en esos campos como `SHOULD_NOT_MET`, contado aparte del
  PASS y del FAIL, con lo esperado y lo observado. Todo lo demás de UC-14
  (que el slate se presenta, que el overlay se presenta sobre él, los pedidos)
  sigue siendo MUST y da FAIL.
  - Descartadas: convertir los 6 en notas sin esperado (se pierde la medición
    de quién alinea) y que el vector afirme sólo para un Player alineado (un
    Player que no alinea quedaría sin juzgar en lo demás).
  - Cuesta un cambio de formato (esquema, `check-scenarios`, comparador), que
    va en T-06 con su negativo: un desvío en un campo `should` no da FAIL, el
    mismo desvío en un campo sin la marca sí.
- **Test de R1.9:** UC-14 alineado da PASS; con la referencia mutada para
  arrancar el slate en su borde (sin la demora), los campos `should` dan
  `SHOULD_NOT_MET` y no FAIL.
- **La referencia** arranca el slate en su borde menos la demora del
  principal (T-03).

### N-10. Un reemplazo que no es publicidad (UC-14 7 FAIL, R40.6 4 FAIL)

- **Hoy:** 03:2099 *"Whether an alternative presentation is an ad is therefore
  not observable by a Player (ADR 0012), and no rule here depends on it."*;
  04:1649 *"This specification does not specify blackouts."* UC-14.yaml:25
  *"The format has no element for the slate"*.
- **Problema:** la spec ya tiene posición; el formato no. El slate y la
  alternativa de R40.6 se escriben `shows: []`, la referencia los marca
  `ad` y el comparador los lee como aviso lineal.
- **Decidido (el líder, 2026-11-27): A, sólo el formato y la observación; la
  spec no cambia.** La razón, en sus términos: la spec es agnóstica de qué es
  el contenido. Una alternativa es contenido (video, imagen o HTML), y que sea
  un aviso, un slate de blackout o un gráfico de estadísticas durante un
  partido no le importa al Player. Es lo que ya dice 03:2099.
- **Qué cambia:**
  - El formato (T-06): todo lo que ejecuta un evento lineal heredado se
    registra como `element: alternative`, con su documento. `selection` lo
    registra sin llamarlo aviso. Los vectores que no lo usan no cambian.
  - La referencia (T-03) marca esas superficies neutras
    (`data-sgai-element="alternative"`), no `ad`.
  - Los vectores (T-02): UC-14 y R40.6 reescritos, sin el `shows: []` ni la
    nota de que el formato no tiene el elemento.
- **Fuera de alcance:** renombrar "ad" en la spec o en `context/`.

### N-11. UC-07 / Annex G.9 sin documento de resolución (10 FAIL)

- **Hoy:** 04:821 *"Expected behavior (uniform across device classes
  D1..D5)"*; G.9 (src:4192) dice que un Player de esta spec resuelve el overlay
  desde 840 s, pero el Annex G no trae esos documentos. UC-07.yaml: D1–D5 con
  resultados legacy y las ventanas contestadas 404.
- **Problema:** la referencia pide las ventanas y el vector espera que no
  pida nada. No es de la 6ta: es nuestro anexo.
- **Decidido (el líder, 2026-11-27): UC-07 es sólo del Player legacy.** Su
  sujeto es el legacy, y el caso de un Player de esta spec con supersede ya
  está escrito en UC-17. Descartado completar el Annex G con los documentos de
  overlay y pausa: duplica UC-17 / Annex Q.
- **Qué cambia:**
  - `context/04` (T-01): en UC-07 las columnas D1–D5 de la fila de cobertura
    pasan a "—", y el *"Expected behavior (uniform across device classes
    D1..D5)"* (04:821) pasa a ser el del Player legacy; G.9 remite a UC-17.
  - El vector (T-02): `UC-07.yaml` sólo con `legacy`; salen sus D1–D5 y la
    variante `[pause-requests-nothing]` de D1–D5. `check-scenarios.py` exige
    las clases que la fila de cobertura declara, así que con "—" pide sólo
    `legacy`; si no lo lee así, se corrige ahí (T-06).
  - El v13: el Annex G.9 remite a UC-17 / Annex Q.
  - Los 10 FAIL desaparecen porque esos jobs dejan de existir, no porque
    pasen: el informe de T-08 lo cuenta así.

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
tocan: el v13 los absorbe. La fase no abre nada con el WG (el líder,
2026-11-27).

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
