---
closed: 2026-11-26
---

# REPORT — fase 11, Player de referencia

## 1. Resumen

Existe un Player que implementa la extensión: el `dist/` de dash.js 5.3.0
fijado, sin modificar, más un módulo nuestro (`reference-player/src/`) que usa
sólo la API pública de dash.js. El spike de T-01 midió que eso alcanza, sin
fork. La referencia implementa:

- el lineal de la 6ta, que dash.js no trae: insert y replace, la cola por PRT,
  la List MPD, los callbacks y el MPD alternativo dinámico desde su live edge;
- el no lineal: resolución, selección por perfil de clase, cap, fallback,
  overlay, squeezeback, pausa y la convivencia entre familias;
- el tracking y el click.

La batería que la juzga es 100% código y corre sólo con `--behaviour` (ADR
0087, con un test que lo verifica). La forman un vector por criterio en
`spec-source/behaviour/`, con la población de 76 leída del catálogo del nivel
2 (59 con test, 17 `NOT_VERIFIABLE` con motivo), más los 22 vectores de UC.

**Medido sobre la batería entera** (`tasks/T-09/battery/battery.md`, más la
remedición final en `tasks/T-09/final/battery-final.md`):

| | T-09 (HEAD `fff79a8`) | final |
|---|---|---|
| jobs | 323 | 329 |
| PASS | 1155 | 1249 |
| FAIL | 132 | 62 |
| NOT_VERIFIABLE | 70 | 70 |
| FAIL de la referencia | 37 | **0** |

- **Tiempo:** 4 h 37 min con concurrencia 2, contra 8 h 53 min en serie
  (1,93×), en una máquina de 2 núcleos. UC-05 y UC-11 son la mitad del tiempo.
- **Los 62 FAIL que quedan:**
  - 34 son de los vectores o del instrumento, como la clase legacy, que espera
    que dash.js 5.3.0 haga el lineal de la 6ta.
  - 23 tienen su causa en la norma: 13 de UC-14 y 10 de UC-07. En UC-07 el
    vector escribe lo que le falta al Annex G.
  - 5 FAIL de 3 jobs son inestables por la carga: dan PASS al correrlos solos
    dos veces.

La demo (`reference-player/demo/demo.py`) reproduce una sesión con lineal,
overlay y pausa, la verifica por código y la graba para una persona.

## 2. Decisiones

ADR 0075 a 0087 (`scope: phase-11`), una por decisión del diseño (D-1 a D-13).
El líder del proyecto aprobó D-1, D-2, D-8 y D-12 como estaban recomendadas, y
sumó D-13 al aprobar: *"Ok, construyamos pero que por defecto no se use porque
es muy caro en tiempo"*.

Decisiones de ejecución que conviene conocer, porque cambian cómo se lee la
batería:

- **El reloj de sesión es de presentación**
  (`spec-source/scenarios/README.md`):
  - arranca en el primer frame del principal;
  - avanza con el tiempo del media que está en pantalla, y con el reloj de
    pared durante una pausa;
  - no avanza en una transición sin nada en pantalla, hasta 1000 ms.

  El reloj de pared medía la máquina: el principal corría a 0,3–0,99× del
  tiempo real. Verificado con la CPU frenada 4×: el reloj de pared da FAIL y el
  de presentación da PASS. Un retraso real de 1 s sigue dando FAIL.
- **Una oportunidad se identifica por documento, esquema, valor e id**
  (§5.10.2.4). Cada presentación lleva un número propio. Un beacon se mide desde
  el inicio observado de su aviso.
- **Método, por pedido del líder del proyecto desde T-07:**
  - 100% verificación por código, sin capturas;
  - el runner devuelve sólo un resumen y el detalle va a un archivo;
  - un subagente toma una familia de criterios por vez;
  - cada FAIL se clasifica primero como de la referencia, del test o de la
    norma.

## 3. Tasks

Las 12 `done`; ninguna se abandonó. Lo que no estaba en el plan:

- **T-04:** sumó R15.3 y R4.5 al índice de `NOT_VERIFIABLE`, con el motivo de
  cada uno.
- **T-07 y T-08:** se partieron en familias.
- **T-09 tuvo dos rondas acotadas de arreglos** antes de medir el final:
  - el ruteo de fixtures que comparten URL, que explicaba 55 FAIL;
  - en la referencia: UC-08, UC-14, UC-21, la vuelta al principal en vivo y el
    callback de fin a 2×;
  - el "now" de los vectores en vivo;
  - el seek del principal oculto.
- **Tests nuevos fuera del plan:**
  - de criterio: R13.3-4, R6.5-3, R34.6-2, R34.6-3 y R17.2-2;
  - vectores de borde de la 6ta: E1–E18, en `reference-player/test/edges/`.
- **Regla nueva S-DOC:** toda URL de documento a la que apunta un fixture está
  declarada.

## 4. Hilos abiertos

**Para el v13 (hallazgos de norma).** Cada uno con lo que le falta a la spec:

1. **R12.5:** "60% / 25%" no dice si es área o lado. Los tests y la referencia
   leen área.
2. **Faltan carriers:**
   - `squeezeback-frame` (R12.2, R12.5, R27.1);
   - el tracking por opción (R13.6);
   - `@executeOnce` y `@startWithOffset` en el overlay (R34.1, R34.3, R34.9).

   Son los 6 FAIL que `--source spec-source` ya marcaba sobre el esquema.
3. **Retomar o terminar:** R40.4 y R40.9 retoman la forma suspendida después
   de un corte lineal, y la spec (§4.5.8 PLY-49) la termina. Además, §5.1.3 de
   la v12.6 dice MAY presentar el resto, contra R34.9, que pide MUST desde el
   primer candidato.
4. **R36.1, offset 0 en una ventana de pausa:** "medido desde el inicio de la
   ventana" contradice "se resuelve sólo cuando dispara". El Annex H.3 sigue lo
   segundo, y la referencia también.
   - Con offset 0, un aviso de pausa en video no puede arrancar en el instante
     de la pausa, y nada dice qué ve el viewer mientras tanto.
   - Tampoco se dice cuánto puede retener el contenido un Player que sólo
     puede resolver en el PRT (R40.9-3, R40.3-2).
5. **La 6ta:**
   - §5.16.2.2.5 1a ("QE is reset") re-ejecuta una inserción para siempre; el
     pseudocódigo de A.14.5 no lo hace.
   - No hay regla para despachar un evento justo en el fin del Period.
   - `@clip` recorta la latencia de ejecución sin tolerancia, así que el
     callback de fin de un aviso lineal no se alcanza leído al pie de la letra.
   - Nada acota el blanco al volver a RT.
   - La referencia toma una lectura en cada caso, y su cabecera lo dice.
6. **Alternativa en vivo:** arranca en su live edge (§5.16.2.2.6), mientras el
   principal se ve con la demora del Player. Nada ata una cosa con la otra, así
   que una ventana en la línea de tiempo del slate se corre con la latencia
   (UC-14, 6 FAIL).
7. **No existe un reemplazo que no sea publicidad,** como el slate de blackout
   de UC-14 (7 FAIL). Ni la spec ni el formato de vectores pueden expresarlo.
8. **El Annex G no tiene documento de resolución para G.9:** no hay resultado
   escrito para un Player de esta spec en UC-07 D1–D5 (10 FAIL).
9. **R4.5:** ningún documento conforme la ejercita.
10. **R13.3:** no dice qué pasa con un beacon justo en el borde del trim, ni si
    un seek dentro de un overlay abre una presentación nueva para el alcance
    de `@id`.

**Defectos de vectores y formato** (FAIL del test, todos reproducibles):

- La clase `legacy` de los UC lineales espera que dash.js 5.3.0 traiga el
  corte, pero no tiene `alternativeMPD` (18 FAIL).
- UC-08: el `mid` está escrito en 85000, y es 75000.
- R40.6: escribe la alternativa como `shows: []`.
- UC-11: hay beacons de ClickThrough sin `@id`.
- UC-13 D3/D4: `sends_capabilities` va por vector, y el Annex M.3 lo pide por
  clase.
- UC-19 D1: el vector espera 1 decoder y el perfil D1 manda 2.

**Límites del instrumento:**

- **Lo que el esquema no puede expresar:**
  - el color de una región (las bandas negras de R26.1);
  - la posición dentro de un aviso;
  - el audio.

  Por el audio hay 24 `NOT_VERIFIABLE` en UC-03, 09, 18, 19, 21 y 22.
- **29 `NOT_VERIFIABLE` por oportunidad ambigua:** vectores con `Event@id`
  repetido en varios esquemas que no nombran el esquema (UC-07, 08, 11 y 17).
  UC-04 ya lo nombra.
- **Un blanco de menos de 1000 ms al volver al principal** queda sólo como
  nota, nunca como FAIL.

## 5. Riesgos que se dieron

- **La máquina cargada** (2 núcleos, load de hasta 43 por trabajo ajeno)
  inventaba FAIL de tiempo. Lo mitigó el reloj de presentación. Queda como
  ruido: 3 jobs inestables.
- **La batería tarda horas,** como estaba previsto: 4 h 37 min. El opt-in (ADR
  0087) la saca de todo camino por defecto.
- **"La referencia pasa sus propios tests":** se cubrió viendo fallar cada
  test antes de su familia (D-11) y con campañas de mutación. Esas campañas
  encontraron agujeros del instrumento, no del Player:
  - beacons de más que nadie miraba;
  - pedidos a URLs no declaradas;
  - una imagen repetida que contaba como una sola.
- **No previsto: el límite de 5 h de la cuenta cortó subagentes dos veces**
  (2026-11-24 00:33 y 15:30). Se retomó desde el árbol, y el trabajo a medias
  entró en commits marcados WIP.
- **No previsto: el costo de contexto.** T-07 midió 154 llamadas y 44,8M
  tokens de entrada, sobre todo por capturas PNG y documentos de la fase
  releídos. Eso llevó al cambio de método del líder del proyecto.

## 6. Recomendaciones

- **El v13 recibe dos listas:** la de norma (sección 4) y la de
  `check-behaviour.py`, que va a salir con exit 2 en cada criterio que el v13
  mueva, con los tests a revisar.
- **Antes de usar la batería como juicio:**
  - arreglar los defectos de vectores de la sección 4;
  - decidir qué espera la clase `legacy` en un corte lineal. Hoy los vectores
    piden un Player legacy con el lineal de la 6ta, como Shaka 5.3.6.
- **Para correrla:** una máquina sin otra carga, concurrencia igual a los
  núcleos, y el cache de contenido de `~/.cache/cto-tmp/sgai-behaviour-content/`.

## 7. Correcciones post-ejecución

`grep -n "post-ejecuci" TASKS.md` no devuelve nada. Ninguna task necesitó
corrección después de declararse terminada. Las correcciones a trabajo propio
quedaron dentro de cada task, en su informe y en su evidencia.

## 8. Revisión de documentación

- **`description` de `PHASE.md`:** reescrita con lo que la fase resultó.
- **`docs/arc42/`:** el proyecto no tiene; la fase no lo crea, porque la
  arquitectura de la referencia está en la cabecera de cada módulo y en las
  ADR 0075 a 0087.
- **El resto de `docs/`:** no existe.
- **`README.md`:** suma una sección sobre el Player de referencia: la batería
  opt-in, los vectores de borde y la demo (`3c3a949`).
- **`CLAUDE.md` del proyecto:**
  - el layout suma `reference-player/` y `spec-source/behaviour/`;
  - la lista de `bin/` suma `check-behaviour.py` y `--behaviour` como opt-in;
  - "Outside the build" suma los vectores de borde y la demo (`3c3a949`).
- **`.project/knowledge/`:** no existe y no hizo falta crearla. Lo que dura
  más que la fase está en las ADR y en los README de `spec-source/`.
- **`CLAUDE.md` y `knowledge/` de la raíz del repo:** no cambian. La fase no
  tocó nada que valga para todo el repo.
- **Runbook (`SETUP.md`):** dice qué necesitan `--behaviour`, los vectores de
  borde y la demo (node, ffmpeg, el Chromium de Playwright) y cómo se vacía el
  cache de contenido.
- **Otros documentos vivos:**
  - `spec-source/scenarios/README.md` dice el reloj de presentación, el "now"
    en vivo y los campos nuevos;
  - `spec-source/behaviour/README.md`;
  - el `--help` de `check-scenarios.py`, que todavía decía "no executor".
- **Las tasks de la fase:** los README que quedaron viejos (T-03, T-04/a,
  T-04/b, T-04/c, T-07/f1) llevan una línea fechada que los marca como
  registro. Los demás ya se leen como informes en pasado.
