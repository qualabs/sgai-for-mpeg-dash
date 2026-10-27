# Tasks — svta2053-v3-alignment

| id   | brief                                                                                   | status  | who   | plan | evidence |
| ---- | --------------------------------------------------------------------------------------- | ------- | ----- | ---- | -------- |
| T-01 | El análisis de David contra `context/` queda commiteado como referencia                  | done    | agent | —    | `58d8168` |
| T-02 | Una opción cuyo recurso no carga se saltea, no el candidato (D1)                         | done    | agent | —    | `f1c642a` |
| T-03 | Ejecuciones de una ventana: volver, ONCE y entrar tarde (D2, D3)                         | done    | agent | —    | `cd9c260` |
| T-04 | La ventana se retoma después de un evento lineal heredado (D4)                           | done    | agent | —    | `e1666a0` |
| T-05 | Privacidad: DP-4 y sus notas (D5)                                                        | done    | agent | —    | commit "T-05" |
| T-06 | Tres precisiones: R29.7, el solapamiento y el candidato salteado (D6, D7, D8)            | planned | agent | —    | —        |
| T-07 | Los chequeos de `context/` en verde y `context/` commiteado                              | planned | agent | —    | —        |
| T-08 | La spec reconstruida con el delta (incremental, o mayor si el chequeo lo pide)           | planned | agent | —    | —        |

---

## T-01 — El análisis de David contra `context/` queda commiteado
- **Objective:** `output-analysis/2026-10-27-david-v3-vs-context.md`, la base
  del diseño, está en git y se puede citar por commit.
- **What it must cover:** sólo ese archivo, en un commit propio, antes de
  arrancar el plan (un commit fuera de `.project/` después lo vuelve stale).
- **Definition of done:** `git log -1 -- output-analysis/2026-10-27-david-v3-vs-context.md` muestra el commit.
- **nivel de verificación:** mínimo. Es un archivo que ya existe y no cambia.

## T-02 — Una opción cuyo recurso no carga se saltea, no el candidato
- **Objective:** un asset muerto en una opción lleva a la opción siguiente, y
  el candidato se pierde sólo cuando ninguna opción renderiza; en ese caso, y
  sólo en ése, se dispara el beacon de error.
- **What it must cover:** R5.9 nueva, R5.7, R1.4 y R42.1 en
  `context/03-requirements.md`, con los textos de D1 en `DESIGN.md`; una
  viñeta en UC-09 y el párrafo de Coverage que repite R1.4 en
  `context/04-use-cases.md`. ADR 0022. Sin timeout fijado y sin
  `preValidateAssets`.
- **Definition of done:** los textos están, R5.9 la cita R5.7 y R1.4, y la ADR
  0022 está `accepted`.
- **nivel de verificación:** alto. Es entrada normativa del build; un error no
  se ve hasta la spec. Se verifica con los chequeos de T-07 y leyendo cada
  criterio contra D1.

## T-03 — Ejecuciones de una ventana: volver, ONCE y entrar tarde
- **Objective:** cada entrada del playhead a una ventana de overlay o
  squeezeback es una ejecución nueva que resuelve de nuevo, ONCE la limita a
  una con el contador de la base, y una ejecución tardía arranca desde el
  primer candidato salvo que la ventana declare el offset de la base.
- **What it must cover:** R34 entera (D2 y D3), R36.4, R13.7; los párrafos de
  `@executeOnce` y `@startWithOffset` en `context/06-naming-and-namespaces.md`
  ("Naming consistency with baseline DASH"); *Execution* en el glosario; UC-21
  en `context/04-use-cases.md` y su fila de Coverage. ADR 0023, 0024 y 0028.
  Las citas de la base salen de la copia primaria, nunca de memoria.
- **Definition of done:** los textos están, UC-21 ejercita sin ONCE, con ONCE,
  un seek por encima y un seek a la mitad con y sin offset, y las tres ADR están
  `accepted`.
- **nivel de verificación:** alto. Cambia cuándo se presenta un aviso y cuántas
  veces se cuenta; se verifica con T-07 y contra D2 y D3.

## T-04 — La ventana se retoma después de un evento lineal heredado
- **Objective:** una ventana sin relación declarada se suspende mientras corre
  un lineal que se solapa con ella, y se retoma en la misma ejecución si el
  programa vuelve dentro de su rango.
- **What it must cover:** R40.4 y R4.11 (D4); la viñeta *Declaring nothing* de
  UC-14; UC-22 nuevo y su fila de Coverage. ADR 0025, que deja en pie la 0020.
- **Definition of done:** los textos están, UC-22 muestra suspender y retomar
  sin volver a resolver ni a disparar el slot-start, y la ADR 0025 está
  `accepted`.
- **nivel de verificación:** alto. Es la frontera con el lineal; se verifica con
  T-07 y contra D4.

## T-05 — Privacidad: DP-4 y sus notas
- **Objective:** lo que el Player origina sobre el dispositivo o el espectador
  es opcional y está anotado donde se define; los beacons quedan afuera.
- **What it must cover:** DP-4 en "Design principles"; notas en R29.2, R33,
  R44.3 y R47.2 (la tabla de D5). ADR 0026. Sin el `RECOMMENDED` de David.
- **Definition of done:** DP-4 y las cuatro notas están; la ADR 0026 está
  `accepted`.
- **nivel de verificación:** alto. DP-4 gobierna requerimientos futuros; se
  verifica con T-07 (vocabulario) y contra D5.

## T-06 — Tres precisiones
- **Objective:** R29.7 sigue dejando la decisión al APS con una nota que
  sugiere devolver todas las opciones; el solapamiento con el lineal es del
  Publisher; un candidato salteado no ocupa tiempo.
- **What it must cover:** R29.7 (D6, con *can* y no un modal), R40.1 (D7),
  R14.1 (D8). ADR 0027. D7 y D8 no llevan ADR.
- **Definition of done:** las tres frases están y la ADR 0027 está `accepted`.
- **nivel de verificación:** alto. Mismo motivo que T-02.

## T-07 — Los chequeos de `context/` en verde y `context/` commiteado
- **Objective:** `context/` cierra consigo mismo y con la base declarada, y el
  build incremental tiene un commit del que partir.
- **What it must cover:** `bin/check-normative-base.py`,
  `bin/check-context-coherence.py`, `bin/check-context-vocabulary.py`. Antes de
  dar por bueno el verde, romper a propósito una referencia y verla en rojo.
  Depende de T-02 a T-06.
- **Definition of done:** los tres salen `0`, con la salida pegada en el
  informe, y `context/` está commiteado sin push.
- **nivel de verificación:** alto. Es la verificación de las tareas de texto.

## T-08 — La spec reconstruida con el delta
- **Objective:** existe un candidato `v<N.M+1>` construido desde el `context/`
  de T-07, con sus análisis y la comparación contra lo publicado.
- **What it must cover:** `prompts/build-incremental.prompt` invocado como dice
  el `CLAUDE.md` del proyecto, con `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` y en
  background. Si `check-incremental.py` dice `MAJOR RECOMMENDED`, se avisa al
  coordinador antes de lanzar el mayor. La promoción a `dist/` sigue el
  criterio del `CLAUDE.md`. Depende de T-07.
- **Definition of done:** el candidato y sus sidecars están en `output/` y
  `output-analysis/`, con el veredicto de `check-promotable.py` y de la
  comparación en el informe.
- **nivel de verificación:** alto. Es lo que se publica; lo verifican
  `check-incremental.py` y `check-promotable.py`.
