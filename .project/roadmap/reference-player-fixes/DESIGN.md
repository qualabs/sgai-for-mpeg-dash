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

### N-1. R12.5: ¿60% / 25% es área o lado?

- **Hoy:** 03:842 *"the upper-left 60% of the frame"*; :844 *"the centre-left
  25% of the frame"*; :846 *"the centre 60% of the frame"*.
- **Problema:** no dice área ni lado, ni dónde va el double box. Sin FAIL: la
  referencia (`sgai-compositor.js:39`, *"read as AREA … sqrt(0.60) = 77.46%"*)
  y R12.5-1/R27.1 leen área, marcado `[inferred]`.
- **Opciones:**
  - A. "Área, con el aspecto conservado" en la cabecera de la tabla. Nada
    cambia salvo quitar el `[inferred]`.
  - B. Lado (60%×60%). Cambian la referencia, R12.5-1, R27.1, R26.x, y falta
    fijar la ubicación horizontal del double box.
  - C. Rectángulos explícitos por token (x, y, ancho, alto en %) con los
    valores de la lectura por área. Fija también la ubicación.
- **Recomendación: C.** Cierra las dos dudas y no cambia tests ni referencia.

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
- **Opciones:**
  - A. En pausa gana "sólo cuando dispara". La referencia no cambia; UC-08
    acepta un arranque tardío acotado.
  - B. Gana "desde el inicio": se borra la última frase o se limita al overlay.
    Cambian la referencia (`preResolvePause`) y UC-08, y un video de pausa
    puede arrancar sin espera.
  - C. El offset sólo pone el piso del pedido, para las dos familias, y
    "fresco en la pausa" es lo que el Publisher consigue con `@validFor` 0
    (R36.4). La referencia resuelve antes de la pausa.
  - En las tres: un criterio de qué se ve mientras tanto (el cuadro pausado)
    y una cota a la retención.
- **Recomendación: C.** Una sola regla de offset para las dos familias, y la
  frescura queda donde ya la modela R36.4.

### N-3. R13.3: beacon en el borde del trim, y seek dentro del overlay

- **Hoy:** 03:2343 *"A beacon whose time falls after the presentation of its
  ad has ended … MUST NOT be fired."* La spec PLY-80 (src:1385): *"stop firing
  the remaining beacons at the trim boundary"*. src:2522: *"An `@id` is scoped
  to one `<svta:Ad>` and one presentation of it"*.
- **Problema:** "after" excluye el borde y "at the boundary" se puede leer
  como que lo incluye; R13.3-4 espera que dispare y dice que es lectura del
  test. "One presentation" no define qué hace un seek de adentro a adentro
  de la ventana; la referencia no re-dispara y ningún test lo cubre.
- **Opciones:**
  - A. En 03: el beacon en el instante del fin dispara; un seek dentro del
    rango no es una ejecución nueva y el alcance de `@id` sigue. La referencia
    no cambia; dos tests nuevos.
  - B. Lo opuesto: borde excluido, seek interno = ejecución nueva. Cambian la
    referencia y R13.3-4.
  - C. Sólo el borde; el seek queda como nota.
- **Recomendación: A.** Es lo que la referencia hace y lo que pide el
  `complete` en la duración (src:2534).

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

### D-6. La batería entera, una vez, al cierre

Opt-in como siempre (ADR 0087), con la máquina sin carga ajena y
concurrencia igual a los núcleos (2). Mientras tanto cada task corre sólo los
jobs que toca, con un resumen por FAIL y el detalle en archivo. Sin capturas.

## Lo que no se hace

- Correr el v13, ni un incremental: es `major-build-v13`, que pasa a depender
  de esta fase.
- Los tests de las mitades sin carrier (Y-1 a Y-3): después del v13.
- Publicar issues en GitHub, pushear.
- Lo que el formato no puede expresar (color de región, audio): es otra fase.
