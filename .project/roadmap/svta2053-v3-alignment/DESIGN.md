---
description: "Traer a context/ lo que Nicolás decidió del trabajo de David Hassoun en SVTA2053 v3: failover de opción por el primer pedido del asset, ONCE y repetición de las ventanas no lineales, retomar la ventana después del corte lineal, privacidad como regla general, y tres precisiones (R29.7, solapamiento, R14.1)."
status: designing
category: feature
origin: "Nicolás, 2026-10-27, sobre output-analysis/2026-10-27-david-v3-vs-context.md (22 filas); la fila 18 entró el mismo día"
---

# Alinear `context/` con SVTA2053 v3 (David, 2026-10-22/23)

Diseño de la fase. Lo aprueba Nicolás antes de tocar `context/`, y antes de
escribir `PHASE.md`, `TASKS.md` y las ADR.

**Base.** `output-analysis/2026-10-27-david-v3-vs-context.md` (filas 1 a 22) y
`context/` en `7e3b33c`. Los textos actuales se citan de
`context/03-requirements.md` salvo que se diga otro archivo. Las cláusulas de
la base se verificaron contra la copia primaria (sha256 `a7274eb2…`, la que
declara `context/00-normative-base.md`), con `pdftotext` y búsqueda literal;
se cita cláusula y frase, nada de la copia.

**Lo que esta fase no hace:** PRE, POST, `?adclass=`, `multiView` (va al ítem
`multiview`), varios assets por opción con geometría libre (va al ítem
`multi-asset-options-profile`), el `RECOMMENDED` de David para mandar
capacidades (D5), y el `SHOULD` del APS para el caso sin capacidades (D4).

---

## D1. Una opción cuyo asset no carga en el primer pedido se saltea; el candidato no (R5.9 nueva, R1.4, R5.7)

**Hoy.** R1.4: *"When resolving or rendering an accepted ad fails at runtime
(for example a decode error, a malformed candidate, or a mid-ad network loss),
the Player MUST abort that ad."* R5.6 recorre las opciones sólo contra
capacidad y layouts. Un asset muerto en la opción 1 tira el candidato entero
aunque la opción 2 se hubiera podido renderizar, lo que DP-3 no admite
(*"an opportunity is given up only after every way of filling it that the
manifest declares has been tried"*).

**Propuesta.**

> - **R5.9** (Player): The first request the Player makes for each resource
>   an option references decides whether that option is satisfiable. When
>   that request fails — a final HTTP status outside the 2xx range, a
>   network error, or no response within a time the Player chooses — the
>   option is not satisfiable, and the Player MUST move to the next option
>   in document order, as R5.6 requires for an option that fails a check.
>   Only the first request for each resource governs this; a failure after
>   the option has begun rendering is a runtime failure under R1.4. This
>   specification fixes no timeout value.

R5.7, primera frase: *"If no presentation option on a candidate satisfies
R5.6 **and R5.9**, the Player MUST skip that candidate…"*.

R1.4, primera frase: *"When rendering an accepted ad fails at runtime **after
it has begun** (for example a decode error, or a mid-ad network loss), or its
candidate is malformed, the Player MUST abort that ad. A resource of an option
that fails on its first request is not a runtime failure: R5.9 governs it."*

**Por qué así.** Es la fila 7 tal como la escribió David (*"Only the first
request for an asset governs this"*), y en nuestro modelo cae entera dentro de
R5.6: no satisfacible es no satisfacible, sea por capacidad o porque el
recurso no responde. No se fija timeout (la librería de David usa 10 s; es del
Player). No se trae `preValidateAssets` (fila 8): cómo se entera el Player es
el HOW. La cadena R5.7 → R5.3 → R20.1 ya lleva un candidato sin opciones
satisfacibles al siguiente candidato y, agotados, a la siguiente ventana.

## D2. ONCE alcanza a las ventanas de overlay y squeezeback (R34)

**Hoy.** R34 es sólo de pausa: *"R34.1 (Publisher): The Publisher MAY declare
a pause opportunity window as once-per-session."* Su texto ya cita la regla de
la base para lo que consume la ventana.

**La referencia de la base, verificada.** `@executeOnce`, en los atributos
comunes de `InsertPresentation` y `ReplacePresentation` (§5.16.5.2, Table 63):
*"specifies whether the event is executed only once during the media
presentation. If true, if some of the media during the active interval of this
event is played more than once, the event is executed only the first time this
media time is traversed."* Default `"false"`. El contador: *"E.c — Execution
counter (number of times alternative MPD playback successfully started)"*
(§5.16.2.2.2, Table 58), y *"The counter E.c has not been incremented due to
the failure, consequently if E.c = 0 the event can still be executed in the
future even if the value of @executeOnce is "true""* (§5.16.2.2.6, NOTE 3).

**Propuesta.** R34 pasa a cubrir las tres familias no lineales y se retitula:

> - **R34. A non-linear opportunity window may be declared once-per-session.**
>   *Gist: The Publisher may declare that an overlay, squeezeback or pause
>   window yields ads at most once in the session; without the declaration a
>   window yields ads each time it is executed (R34.6).*

Criterios (los de pausa quedan; cambian R34.1 y R34.4, se agrega R34.5):

> - **R34.1** (Publisher): The Publisher MAY declare an overlay, squeezeback
>   or pause opportunity window as once-per-session. The declaration is
>   optional; a window that does not carry it is executed each time the
>   playhead enters it (R34.6), and a pause window that does not carry it
>   yields a pause ad on every qualifying pause.
> - **R34.5** (Player): On an overlay or squeezeback window declared
>   once-per-session, once the window is consumed (R34.3) the Player MUST
>   leave the primary content uninterrupted on every later entry of the
>   playhead into the window's range, and MUST fire none of its beacons.
>   A playhead that crosses the window without an ad beginning to render —
>   a seek over it, an empty resolution (R30) — leaves it available.
> - **R34.4** (spec document): The capability is the base specification's
>   single-execution bound (`@executeOnce`, §5.16.5.2) applied to the windows
>   this specification defines, with the base's counter: a window is
>   consumed when an ad begins rendering, as `E.c` counts executions whose
>   playback *"successfully started"* (§5.16.2.2.2). On an overlay or
>   squeezeback window, which occupies the timeline, the base semantics
>   carry over unchanged; on a pause window, whose trigger is the viewer,
>   R34.2 and R34.3 state them in the trigger's terms.

R34.3 (consumo al empezar a renderizar) vale tal cual para las tres familias:
se le saca la palabra *pause* (*"when an ad **begins rendering**"*).

**Carrier, en `06-naming-and-namespaces.md`** (HOW, para que el build lo
pese): un párrafo en "Naming consistency with baseline DASH", *"Once-per-session
reuses the baseline construct, default included"*: `@executeOnce` (§5.16.5.2,
Table 63), con su nombre y su default `"false"`, en las ventanas de las tres
familias.

**Por qué así.** Nicolás pidió tomar como referencia `@executeOnce`, y la regla
de consumo de R34 ya era la del `E.c` de la base. Se diferencia de la ONCE de
David en un punto: él la da por gastada cuando la reproducción entró y salió de
la ventana; acá se gasta cuando un aviso empieza a renderizarse, como la base.
Una ventana que resolvió vacía queda disponible (R30.2 ya lo dice para lo
lineal).

## D3. Volver a una ventana ya presentada es una ejecución nueva (R34.6, R34.7, R36.4, R13.7)

**Hoy.** Nada lo dice: `seek` aparece una vez (OOS-7), `rewind` cero. R3.2 hace
no conforme el comportamiento indefinido.

**La base, verificada.** *"An event is executed every time the playhead enters
the active interval, including the case of join (tune-in) during the active
interval or time-shifted operation moving the playhead to a position prior to
EAP."* (§5.16.2.2.1). *"The alternative MPD is resolved at each execution of
the Event, and a previous failure to resolve the MPD of the same event does not
impact the current resolution."* (§5.16.2.2.6), con NOTE 5: *"Re-resolution is
initiated by the DASH client every time the event is executed, however this
does not necessarily mean that the resulting HTTP GET request will always be
sent over the network."* Lo que Nicolás decidió es lo que la base ya hace con
sus eventos; R1.5 lo adopta.

**Propuesta.**

> - **R34.6** (Player): On an overlay or squeezeback window not declared
>   once-per-session, every entry of the playhead into the window's range —
>   playback reaching it, a join or a seek landing inside it, a seek back to
>   a point before its end — is a new **execution** of the window, as the
>   base specification executes an event *"every time the playhead enters
>   the active interval"* (§5.16.2.2.1). The Player MUST present each
>   execution as it presents the first, with its own cap (R4) and its own
>   beacons (R13, R13.7, R42). An execution that begins after the window's
>   start presents the sequence from its first candidate and ends with the
>   window (R40).
> - **R34.7** (Player): Each execution resolves the opportunity as R36
>   defines, so its candidates may differ from those of an earlier
>   execution. A resolution obtained for an earlier execution is presented
>   again only if it is still usable (R36.5).

R36.4, segunda frase: *"A resolution document that does not declare it remains
usable **for the execution it was obtained for**."* (hoy: *"for as long as its
opportunity window lasts"*, que en un VOD rebobinado no dice si sigue o no).

R13.7: *"The Player MUST fire the slot-start beacon once **per execution of the
window (R34)**…"*.

**Glosario**: entrada **Execution (of an opportunity window)**: *"one
presentation of a window, begun each time the playhead enters its range (R34.6)
or, for a pause window, by a qualifying pause; the base specification's term for
an event (§5.16.2.2)."*

**Por qué así.** Es la fila 15, con el término de la base (*execution*), que
`context/` ya usa en R20.1 (*"failed execution"*). Lo de R36.4 sigue a la
base (se resuelve en cada ejecución) y deja al APS alargarlo declarando cuánto
dura su resolución; ver P2. Que una ejecución tardía arranque desde el primer
candidato es la ejecución demorada de la base (§5.16.2.2.6, *"join and seek
operation … may have caused it to start at a delay"*), y que termine con la
ventana ya lo dice R40 (*"its ad is shown while the presentation plays through
that range, and not outside it"*).

## D4. Retomar la ventana después del corte lineal heredado (R40.4, R4.11, UC-14)

**Hoy.** R40.4: *"A form on screen when an alternative presentation begins ends
there, and the window presents nothing further."* David (ADR 0114 de la demo):
mientras corre el lineal no se dibuja ni se cuenta nada; *"y si al volver el
programa la ventana nuestra sigue abierta, se retoma"*.

**Propuesta.** R40.4, desde *"A form on screen…"*:

> While an inherited linear event the window overlaps is being executed, the
> Player MUST present nothing of the window and fire none of its beacons; a
> form on screen when the alternative presentation begins is suspended. When
> the presentation that declares the window is output again and the playhead
> is still inside the window's range, the Player MUST resume the window: the
> suspended form from where it was suspended, then the rest of the sequence,
> until the window ends or its cap is reached. Resuming continues the same
> execution (R34.6): it is not a new entry, it does not resolve again, and it
> does not consume a once-per-session window a second time or fire the
> slot-start beacon again. When the presentation resumes at a point outside
> the window's range, the execution has ended.

R4.11: la frase *"The only suspension this specification defines happens while
the viewer is paused (R17.1), and a pause does not advance the presentation
timeline."* se reemplaza por *"The interval during which a form is suspended —
during a viewer pause (R17.1), or while an inherited linear event is executed
(R40.4) — MUST NOT accrue against the cap."* (en una inserción el timeline del
programa no avanza; en un reemplazo sí, así que hay que decirlo).

**Misma ejecución, no una nueva: por qué.**

1. **La base distingue entrar de volver.** Una ejecución nueva es *"every time
   the playhead enters the active interval"*. Al terminar una inserción el
   programa sigue en *"RT … defined as PRTA"* (§5.16.2.2.1, paso 5): el playhead
   no salió ni entró. En un reemplazo vuelve en RT; si RT cae dentro de la
   ventana es la misma reproducción del programa, no un salto del espectador.
2. **Es el patrón que ya tenemos.** R17.2: un overlay suspendido por un aviso de
   pausa *"MUST restore the overlay rendering if the overlay slot window is
   still active"*, y R17.3 cuando expiró. D4 es R17 con el lineal en lugar de la
   pausa.
3. **Con ONCE no se cuenta dos veces** una venta que se está completando, y con
   D3 queda claro qué es nuevo: lo que mueve el espectador (seek, rebobinar,
   join). Lo que mueve el Player por un corte, no.

**Lo que no cambia de la ADR 0020.** El default sigue presentando la ventana
sólo sobre el contenido de su presentación y nunca sobre el lineal: no vuelve el
caso de dos avisos a la vez. Supersede y on top no se tocan.

**UC-14**, viñeta *Declaring nothing*: *"…composites nothing from that window
over the slate; a form already on screen when the slate begins is suspended,
and resumes when the slate ends if the window is still open (R40.4)."*

## D5. Privacidad: lo que puede identificar al dispositivo o al espectador es opcional y lleva nota

**La regla general va en los principios de diseño**, porque gobierna cualquier
requerimiento futuro y no uno:

> - **DP-4. What can identify the viewer is optional to send, and says so.**
>   Information about the device or the viewer that the Player originates and
>   discloses to another actor — a capability, a measurement, a determination
>   it makes — MUST be optional for the Player to send, and the specification
>   MUST carry a privacy note where it defines that information, stating what
>   it discloses. Executing an instruction the resolution document carries,
>   such as firing a beacon whose URL the APS wrote complete (OOS-10), is not
>   information the Player originates.

La última frase es la recomendación de P1; si Nicolás decide lo contrario, sale
y R13, R42 y R47 entran en la lista de abajo.

**R29.2**, se agrega:

> *Privacy note:* the reserved parameters describe the device, and each one
> adds to the information that can single out a device or a viewer
> (fingerprinting). Whether a Player sends them is subject to the privacy and
> personal-data policies that apply to whoever deploys it; this specification
> requires none of them (DP-4).

**Revisión del resto.** Búsqueda: `/usr/bin/grep -niE "MUST (send|fire|report|hand)|MAY (send|attach|fire|report)|reports metrics|run(s|ning)? a verification"`
sobre `03-requirements.md`, más R13.2 y R42.3 leídos a mano.

| Requerimiento | Qué sale del Player | ¿Bajo DP-4? | Cambio |
|---|---|---|---|
| R29.1, R29.2, R29.9 | capacidades del dispositivo | sí; ya opcional | la nota de arriba |
| R29.8 → R38.2, R39.3, R41.5 | lo que el slot declaró en el MPD (layouts, región, permiso de audio) | no: repite el manifiesto, no dice nada del dispositivo | ninguno |
| R44.3 | recursos de verificación a un SDK de terceros, que mide el dispositivo y la pantalla | sí; ya opcional | nota de privacidad |
| R33.2 | métricas `PlayList` (pausas, seeks del espectador) | sí; ya opcional (*"A Player that reports metrics"*) | nota de privacidad |
| R47.2 | si el aviso fue visible (determinación del Player) | sí; determinarlo ya es opcional, el beacon de "indeterminado" no | nota de privacidad; ver P1 |
| R42.3 | beacons de acciones del espectador (pausa, mute, descarte) | depende de P1 | según P1 |
| R13.2, R13.7, R35.6 | beacons de entrega del aviso, URL escrita por el APS | no, con la recomendación de P1 | ninguno |
| R28 | click del espectador | no: lo inicia el espectador | ninguno |

## D6. R29.7 queda: el APS decide; "devolver todas" va como sugerencia

**Hoy.** R29.7: *"This specification does not define how an APS resolves an
undetermined value; that is the APS's decision, and two APSs that resolve it
differently are both conformant."* No cambia. Se agrega al final:

> *Informative note:* an APS that does not know a capability can return every
> option the advertiser allowed and leave the choice to the Player's check
> (R5.6), which keeps every device that could render one of them.

No se trae el `SHOULD` de David (ADR 0105 de la demo, v3 5.3.3). La nota usa
*can* para que `check-context-vocabulary.py` no la lea como obligación.

## D7. El solapamiento de una ventana no lineal con el lineal es del Publisher (R40.1)

**Hoy** está implícito: las tres relaciones de R40 presuponen solapamiento, pero
ninguna frase lo permite. Búsqueda: `grep -niE "may overlap|overlap in time"`
sobre `03`, `04` y `02`: sólo R20 (misma familia) y UC-08/UC-12.

**Propuesta**, al principio de R40.1: *"Whether a non-linear window overlaps
inherited linear events in time is the Publisher's decision."* No se trae la
prohibición de David (ADR 0113 de la demo), que viene de que hls.js no compone
sobre su propio intersticial; la ADR 0020 ya dice por qué DASH necesita el
solapamiento (UC-07, UC-04).

## D8. Un candidato salteado no ocupa tiempo (R14.1)

Al final de R14.1: *"A candidate the Player skips (R5.3, R5.7) occupies no time:
the next one starts where the skipped one would have started."* Fila 10; no se
trae el `preserve` de David (DP-1.1).

---

## Lo que toca en `context/`

| Archivo | Cambio |
|---|---|
| `03-requirements.md` | DP-4; R1.4; R4.11; R5.7, R5.9; R13.7; R14.1; R29.2 (nota), R29.7 (nota); R33 y R44.3 (nota); R34 (título, gist, R34.1, R34.3, R34.4, R34.5–R34.7); R36.4; R40.1, R40.4; la tabla de invariantes no cambia (R34 y R29 no están). R47 según P1. |
| `04-use-cases.md` | UC-09: una viñeta para una opción cuyo recurso no carga (R5.9). **UC-21** nuevo: un VOD rebobinado sobre un overlay, sin ONCE (se presenta de nuevo, puede traer otro aviso, beacons de nuevo), con ONCE (no), y un seek por encima (no la gasta). **UC-22** nuevo: un mid-roll lineal dentro de una ventana de overlay sin relación declarada, que se suspende y se retoma. UC-14 (D4). La tabla de Coverage (dos filas) y el párrafo que repite R1.4. |
| `06-naming-and-namespaces.md` | El párrafo de `@executeOnce` (D2). |
| `99-glossary.md` | *Execution (of an opportunity window)*; *Privacy note* si el chequeo de vocabulario lo pide. |
| Registro "Deliberately open" | Sin filas: todo lo de esta fase queda decidido, y el registro es sólo para lo que decide otro cuerpo (ADR 0021). |

## ADR que hacen falta

| # | Título | De |
|---|---|---|
| 0022 | An option whose resource fails its first request is skipped, not its candidate | D1 |
| 0023 | A non-linear window is executed each time the playhead enters it, and each execution resolves | D3 |
| 0024 | Once-per-session reaches overlay and squeezeback windows, with the base's counter and carrier | D2 |
| 0025 | A window interrupted by an inherited linear event resumes after it, in the same execution | D4 (cambia R40.4, aceptado; ADR 0020 sigue en pie) |
| 0026 | What can identify the device or the viewer is optional to send and carries a privacy note | D5 |
| 0027 | How an APS resolves an undetermined capability stays its own; returning every option is a suggestion | D6 (R29.7 no tenía ADR y el texto de David lo va a volver a plantear) |

D7 y D8 no llevan ADR: precisan lo que ya estaba. `?adclass=` (confirmado
afuera, 2026-10-27) tampoco: va una línea en el LOG. No se agrega la línea
informativa: en DASH la clase la da qué construct escribe el Publisher (evento
lineal o ventana), cada uno con su URL, y una nota sobre un mecanismo que un
lector de DASH no busca es ruido.

## Rebuild

**Incremental** (`prompts/build-incremental.prompt`), con `context/` commiteado
antes. Es un delta acotado de requerimientos que la spec ya tiene dónde poner:
opciones (R5), ventanas y su relación con lo lineal (R34, R40), parámetros
(R29). Lo que puede empujarlo a mayor es DP-4 si el build reparte notas por
muchas secciones, o el carrier de ONCE en la ventana de overlay; si pasa,
`check-incremental.py` lo dice (`MAJOR RECOMMENDED`) y no se fuerza.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| R34.6 duplica impresiones al rebobinar | Es la decisión de Nicolás y la semántica de la base; el Publisher que no lo quiere declara ONCE (R34.5). UC-21 lo muestra. |
| D4 y D3 se confunden (retomar vs entrar) | El criterio está escrito en R40.4 (*"it is not a new entry"*) y UC-22 lo ejercita. |
| Un descarte del espectador (R35) no sobrevive a un rebobinado | Consecuencia de D3: una ejecución nueva es una ventana nueva. Se acepta; queda explícito en UC-21. |
| R5.9 hace esperar al Player el primer pedido antes de mostrar | El timeout es del Player y R36 ya le deja resolver y precargar antes. Residual, aceptado. |
| DP-4 sin acotar vuelve opcionales los beacons | P1 lo decide antes de escribir. |

## Preguntas abiertas, con recomendación

- **P1. ¿Los beacons entran en DP-4?** Los de acciones del espectador (R42:
  pausa, mute, descarte) cuentan qué hizo una persona. **Recomiendo que no**:
  el Player no agrega datos (el APS escribe la URL completa, OOS-10), y hacerlos
  opcionales rompe la medición sobre la que se vende la oportunidad (DP-3). El
  consentimiento para trackear es de la ley de cada mercado y del que despliega
  el Player, no de esta spec. Con eso DP-4 lleva la frase de la excepción y
  R13/R42 no cambian; R47 lleva nota porque la determinación sí la origina el
  Player.
- **P2. R36.4 por defecto: ¿una resolución sin vigencia declarada vale para la
  ejecución o para toda la ventana?** **Recomiendo "para la ejecución"**: es lo
  que hace la base (*"resolved at each execution"*), es lo que da "anuncios
  distintos" al volver, y el APS que quiere reusarla declara su vigencia.
- **P3. Una ejecución tardía (join o seek a la mitad): ¿arranca desde el primer
  candidato?** **Recomiendo que sí**, como la ejecución demorada de la base, y
  que termine con la ventana (R40). La alternativa (arrancar en el segundo del
  seek, como hace David) necesita un mapeo de tiempo dentro de la secuencia que
  no tenemos.
- **P4. ¿Una opción que falla por R5.9 dispara el beacon de error (R42)?**
  **Recomiendo**: sólo cuando el candidato termina sin renderizar ninguna opción
  y alguna falló por R5.9; si otra opción se renderiza, nada (R13.6 ya prohíbe
  disparar los de una opción no renderizada). Agregaría a R42.1 *"none of its
  options could be loaded (R5.9)"* entre las ocurrencias. Si Nicolás no lo
  quiere, el ADS no se entera de un creativo muerto.
- **P5. ¿Se trae el `RECOMMENDED` de David para mandar capacidades donde la
  política lo permite?** **Recomiendo que no**: empuja a mandar, contra lo que
  pide DP-4, y R29.7 + R5 ya funcionan sin ellas.
