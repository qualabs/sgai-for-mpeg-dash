# Estado del build al pausarlo — 2026-09-18

Nicolás pidió parar el pipeline de SGAI y dejar el estado escrito para
retomar después. Esto es ese estado. No es un informe de resultados: es lo
que alguien necesita para continuar sin reconstruir nada.

## Por qué está parado

No falló: **se agotó la ventana de 5 horas de tokens**, tres veces
(2026-09-17 ~17:00, ~00:45 y 2026-09-18 ~10:16). Cada corrida retoma donde
la anterior quedó, porque los pasos saltean lo que ya está fresco.

La última se cortó con `You've hit your session limit · resets 2pm`.

## Qué hay en disco

| Artefacto | Estado |
|---|---|
| `output/v9.1-sgai-spec.md` | candidato más nuevo, **sin sus tres sidecars** |
| `output/v9-sgai-spec.md` | candidato con los tres sidecars completos |
| `output/v8.1`, `output/v8` | iteraciones anteriores, con sidecars |
| `dist/` | lo publicado: v7.2, promovido **sin criterio** (ver `dist/PROVENANCE.md`) |

## Cómo retomar

```bash
cd projects/sgai-for-mpeg-dash
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 claude -p "$(cat prompts/build-all.prompt)"
```

La variable **no es opcional**: sin ella el harness mata la corrida a los
600 s esperando subagentes, y este pipeline los despacha por contrato.

Va a saltear lo que está fresco y seguir por los sidecars de `v9.1`.

## El resultado que importa, y hay que verificarlo antes de festejar

**El mecanismo de obligaciones funcionó solo.** El documento generado no
tenía obligaciones normativas —2 en 7657 líneas, y las tres del publicado
son el propio párrafo que declara el vocabulario—; el paso de validación lo
detectó con el veredicto `force-lost` (158 filas), el loop de refinamiento
lo corrigió, y el candidato siguiente tenía 90.

| | líneas | MUST | MUST NOT |
|---|---|---|---|
| `dist` (v7.2) | 4802 | 3 | 1 |
| v8 | 7657 | 2 | 1 |
| **v8.1** (tras refinar) | 7816 | **90** | 6 |
| v9 | 8680 | 84 | 1 |
| v9.1 | 8792 | 88 | 1 |

**Lo que NO está verificado**: que esas obligaciones estén en los lugares
correctos y no repartidas a ojo, y que el resto del documento no se haya
degradado al reescribirlo. Que el número suba es condición necesaria, no
suficiente. Ésa es la primera lectura que hay que hacer al retomar.

## El gate, corrido contra v9

`bin/check-promotable.py` sale **2 — no se puede saber**, por dos hallazgos
del audit sin rutear (`C27`, `C31`): no se sabe quién los destraba, y el
gate prefiere decirlo antes que llamar limpio o bloqueado a algo que no
midió.

De lo que sí clasificó: **19 necesitan a Nicolás**, entre ellas `R1.3` y
`R6.2` (el spec se contradice) y varias `force-lost` que la vuelta de
refinamiento todavía no tocó.

## Decisiones abiertas que el build no puede resolver

- **M5** — el espacio de valores de `@value` en nuestros esquemas. Sin
  declarar. Nicolás lo entendió y decidió que el CÓMO lo resuelve el agente
  al construir; falta escribir las convenciones de acarreo en
  `context/06-naming-and-namespaces.md` para que la elección se haga
  comparando y no por descarte.
- **G-6/M3** — la clave de request-type. Se cayó: el APS ya distingue por su
  propio endpoint. No hace falta declararlo abierto.
- **Los 17 criterios sin modal** en `context/` — el paso de validación los
  lista con `source-has-no-modal` (24 filas en el sidecar de v8.1). Son 17
  lecturas de Nicolás: ¿obliga o describe?
- **R4.10** — provisorio, con el issue #9 abierto en GitHub.
- **PR #5 de Emil**, abierto desde 2026-05-20, toca `context/` y quedó muy
  atrás tras los pushes de estos dos días.

## Lo que cambió en el pipeline mientras tanto

Todo commiteado y pusheado: el mapa de cobertura pasó a indexar por criterio
(108 filas, no 33), tiene veredictos que distinguen *falta* de *dice lo
contrario*, exige la cita del pasaje, y `check-promotable.py` decide con
tres salidas donde la tercera —no se puede saber— gana sobre las otras dos.
