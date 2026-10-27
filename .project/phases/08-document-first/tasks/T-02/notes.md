# T-02 — notas de la reescritura

Commit base (antes de T-02): `2d0d54c` (`context/` idéntico a `44cfff4`).

## Lo que se hizo fuera de la letra del mapa, y por qué

1. **R20.4 se reescribió** aunque el mapa la daba como `queda`. El índice de
   interfaces tiene que apuntar a un criterio del lado del documento (ADR
   0035), y el elemento "familia del documento frente a la del slot" sólo
   estaba definido en R20.4, con rol Player. Su primera frase ya era la
   semántica ("is not a resolution of that slot"); pasó a rol `spec
   document`, con los mismos tres MUST con el documento como sujeto. El
   contenido no cambió.
2. **La regla de escritura dice "(the Publisher, the APS, or the
   specification document; for the request, the Player)"**. El texto de la
   ADR 0034 no nombra al Player, pero I-REQ lo escribe el Player (D-2), y
   R29.3, R29.4 y R29.10 son criterios del Player que definen cómo se
   escribe el pedido. Sin la cláusula, la regla contradice la definición de
   I-REQ. El check de T-03 toma como lado del documento, por interfaz, a
   quien la escribe: Publisher o spec document en I-MPD, Player o spec
   document en I-REQ, APS o spec document en I-RES.
3. **Dos elementos de I-MPD apuntan a otro criterio que el que dice A.7**:
   "cuándo se consume una ventana once-per-session" y "`@executeOnce` ante una
   ejecución sin aviso" apuntan a R34.4 (`spec document`, que define el
   consumo con el contador de la base), no a R34.3 ni a R30.2, que son del
   Player y quedan como comportamiento.
4. **`EventStream@value` no tiene fila**: A.7 ya dice que queda en 06 (es el
   HOW), y ningún criterio de 03 lo define. El índice lleva una línea que lo
   dice. Son 75 filas: 27 + 16 + 32.
5. **R29.7 dice "capability parameter"** en lugar de "reserved parameter".
   Con D-13 los reservados incluyen los del slot, y la ausencia de uno de esos
   significa que el slot no lo declaró (R29.2, R38.2), no "indeterminado".
6. **La prosa de R6 dejó el SHOULD del carrier** y remite a R13.1, que es MUST
   (D-14): era el mismo hecho con otra fuerza.
7. **R1.4** ganó la frase que decidió Nicolás el 2026-10-27 (cerrada por el
   coordinador): un candidato que empezó a renderizar y se abortó cuenta como
   renderizado, y R20.1 no aplica.
8. **Orden dentro de cada requerimiento** (ADR 0032): los criterios cuyo
   primer rol no es el Player van primero, en el orden que tenían. R29 no se
   reordenó porque sus criterios del Player son el lado del documento de
   I-REQ. Se movieron 21 requerimientos.

## Hallazgo fuera de alcance (no se tocó)

`context/04-use-cases.md` citaba R5.7 (saltear el candidato) en dos lugares
que hablan de pasar a la opción siguiente (UC-10, D3 y D4: "the Player skips
to the next option per R5.7"). La sustitución mecánica los deja en R5.3, que
sigue siendo el criterio equivocado: el que corresponde es R5.6. Corregirlo
cambia una cita, no sólo la reemplaza. El coordinador decidió corregirlo:
las dos citas pasaron a R5.6, y T-05 lo acepta como cambio.

## Comprobaciones

- Ningún id retirado aparece en `context/` fuera de la tabla: 0 (control
  positivo: R5.6 en 04 = 6).
- La tabla "Retired identifiers" tiene 37 filas.
- `check-promotable.py --population`: 164 criterios, 25 prosa, 22 casos de
  uso (antes 199, 32, 22).
- `check-context-vocabulary`: exit 0.
- `check-context-coherence`: exit 1, con los 37 ids de la tabla de retirados
  como únicos errores. Lo resuelve T-03.
