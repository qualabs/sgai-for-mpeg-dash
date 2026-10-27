---
title: Alinear context/ con SVTA2053 v3
description: "Llevó a context/ las decisiones de Nicolás sobre SVTA2053 v3 (failover de opción R5.9, ejecuciones y ONCE de las ventanas con @executeOnce, entrada tardía con @startWithOffset, retomar después del lineal, DP-4 y sus notas, tres precisiones), con las ADR 0022-0028; el rebuild pidió mayor y quedó para el build v13."
started: 2026-10-27
origin: "Nicolás, 2026-10-27, sobre output-analysis/2026-10-27-david-v3-vs-context.md (22 filas); la fila 18 entró el mismo día"
category: feature
---

# Alinear `context/` con SVTA2053 v3

El diseño, con las alternativas y las citas de la base, está en
[`DESIGN.md`](DESIGN.md); las decisiones, en las ADR 0022 a 0028.

## Alcance

- `context/03-requirements.md`: DP-4; R1.4; R4.11; R5.7 y R5.9; R13.7;
  R14.1; las notas de R29.2, R29.7, R33, R44.3 y R47.2; R34 entera (título,
  gist, R34.1, R34.3, R34.4 y R34.5 a R34.9); R36.4; R40.1 y R40.4; R42.1.
- `context/04-use-cases.md`: UC-09 (una opción que no carga), UC-14
  (retomar), UC-21 y UC-22 nuevos, la tabla de Coverage y el párrafo que
  repite R1.4.
- `context/06-naming-and-namespaces.md`: los carriers `@executeOnce` y
  `@startWithOffset`, con su default.
- `context/99-glossary.md`: *Execution (of an opportunity window)*, y lo que
  el chequeo de vocabulario pida.
- Las ADR 0022 a 0028.
- Los tres chequeos de `context/` en verde, `context/` commiteado, y la spec
  reconstruida por el camino incremental.

## Fuera de alcance

PRE, POST y `?adclass=` (confirmado afuera: es cómo el Publisher arma las URLs
de sus eventos). `multiView`, que va al ítem `multiview`. Varios assets por
opción con geometría libre, que va a `multi-asset-options-profile`. El
`RECOMMENDED` de David para mandar capacidades, y el `SHOULD` del APS para el
caso sin capacidades. `@clip` en las ventanas. El registro "Deliberately open"
no gana filas. Sin push.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Rebobinar duplica impresiones (R34.6) | Es la semántica de la base; el Publisher que no lo quiere declara ONCE (R34.5). UC-21 lo muestra (T-03). |
| Retomar después del lineal y entrar a la ventana se confunden | R40.4 dice *"it is not a new entry"* y UC-22 lo ejercita (T-04). |
| DP-4 vuelve opcionales los beacons | Su última frase deja afuera ejecutar una instrucción del documento (T-05). |
| Arrancar con offset pierde los beacons de lo no presentado | Es lo que hace la base; default sin offset, y R34.8 lo dice (T-03). |
| El delta excede el camino incremental | `check-incremental.py` dice `MAJOR RECOMMENDED`; no se fuerza, y el mayor se lanza sólo con el OK del coordinador (T-08). |
| Un descarte (R35) no sobrevive a un rebobinado; R5.9 hace esperar el primer pedido | Residuales, aceptados. |
