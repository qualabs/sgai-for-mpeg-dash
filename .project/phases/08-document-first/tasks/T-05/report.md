# T-05 — validación de la versión vieja contra la nueva

Hecha por un subagente que no participó de T-02. OLD = `2d0d54c`, NEW =
`aebfbd5`. El subagente no tenía permiso para escribir archivos de informe,
así que este archivo transcribe su informe; sus tres scripts están en esta
misma carpeta (`pairs.py`, `ids-only-diff.py`, `interfaces-vs-a7.py`).

## Veredicto

**Una obligación debilitada, y sólo una: R6.4 / R6#p2.** El mapa retiraba
R6.4 ("A Player MUST safely ignore unknown namespaces on tracking-related
extension elements") hacia R1.1 y R1.5, con el argumento de que ya la decían.
No la decían: R1.1 obliga a poner los constructs en lugares de donde se puedan
sacar, no dice qué hace un Player de esta spec, y la base sólo dice que el
cliente *"is expected to ignore"*. Sin R6.4, ningún MUST de 03 obligaba a un
Player de esta spec a ignorarlos.

**Corrección (después de T-05):** se restauró R6.4 con su texto original y su
id; se sacó su fila de la tabla de retirados (ahora tiene 36); la prosa de R6
remite a R6.4. Es la clase de D-4 "una garantía de interoperabilidad que tiene
que estar escrita para valer". El retiro de R6.4 nunca se publicó, así que el
id no se reusa: vuelve a ser el que fue.

## 1. Cada modal viejo contra su lugar nuevo

`pairs.py` lista las 231 unidades (199 criterios y 32 de prosa, con la misma
regla que `check-promotable`): `exit 0`, `SUMMARY identical=130 changed=101`.
Las 130 idénticas son `queda`. De las 101 que cambian se leyeron todos los
pares y todos los modales: todos están con la misma fuerza o más, salvo R6.4 /
R6#p2. Los cambios aceptados aparecen sólo en su lugar: R6.2 de SHOULD a MUST
en R13.1 y en la prosa de R6; las dos tablas y los tres nombres de R29.1; el
destino del ClickThrough en R28.1; los tokens de double-box en R12.5 y R26.1;
la frase de R1.4; R20.4 con rol spec document; "capability parameter" en
R29.7.

Prueba del instrumento: en una copia del 03 nuevo se borró "MUST NOT be
re-ordered…" de R7.1 y un MUST NOT de R22.1. R7.4 queda sin la obligación
(`MUST NOT=1` → ninguno), R22.1 pasa de IDENTICAL a CHANGED, y el resumen pasa
de 130/101 a 129/102.

Barrido de SHOULD y MAY en todo 03: SHOULD de 3 a 1 y MAY de 33 a 29, cada
uno explicado (R6.2; R5.5; el "MAY drop" de R7, que ahora es el MUST de R5.3;
R21.1, que ahora es el token de R12.5; la prosa de R26, que ahora es el token
de R26.1; la prosa de R29, que ahora es R29.2).

## 2. 04 y 99 cambian sólo ids

`ids-only-diff.py` reemplaza cada id retirado por el primer destino de la
tabla y colapsa los repetidos. En 04 el único residuo son las dos líneas de
UC-10 que pasaron a R5.6 (aceptado), `exit 1`; en 99 el diff es vacío,
`exit 0`, sin entradas de glosario nuevas. Prueba: una palabra cambiada en una
copia de 04 ("skips it" → "drops it") y otra en una de 99 dejan los dos diffs
no vacíos, `exit 1`.

## 3. Los dobles, uno por uno

Desaparecieron los 9 redundantes (R28.2, R42.3 y R47.2 quedan como garantías,
ADR 0031), los 6 grupos del mismo actor, el doble de R29.8, los de R31.1, R4.6
y R35.8, los cuatro pares de R34 y 11 de los 14 parciales. Siguen:

- Parcial 9: la prosa de R40 describe las tres relaciones y el anclaje con
  palabras cercanas a R40.9. No tiene modales, y la ADR 0035 dice que ningún
  check lo puede ver.
- Parcial 10: R40.6 todavía repite R40.2, porque el mapa la deja (`queda`).
- Parcial 1: R4.1 y R4.2 dicen los dos "no pasa del tope"; R4.2 conserva la
  política, como estaba previsto.
- Además, R47.2 repite en parte los dos casos de R47.1, y la prosa de R27
  repite la composición de R27.1.

## 4. Interfaces contra A.7

`interfaces-vs-a7.py`: 76 elementos, 75 filas. `EventStream@value` no tiene
fila, y el índice dice por qué (lo fija 06, 06:44). 73 filas apuntan al
criterio que nombra A.7; dos apuntan a R34.4 en lugar de R34.3 y R30.2 (notes
de T-02, punto 3). Se leyó el texto de los 75 pares, porque el
emparejamiento es posicional. Los 6 elementos sin definición la tienen:
R40.9 (dos), R29.1 (transporte), R28.1 (destino), R32.1 (los tres
significados), y 06 para `@value`. Prueba: borrar la fila de
`sgai-custom-region` en una copia da `exit 2`, "index rows 74".

## 5. Los tres chequeos

Sobre `context/` real, los tres en `exit 0` (coherence "OK: 296
identificadores…", vocabulary `HALLAZGOS=0`, interfaces "OK: 75 index
rows…"). En rojo a propósito, cada uno sobre su copia: coherence con un
`R99.9` sin definir en 04 (`exit 1`); vocabulary con "A restart MUST be
expected." en R1.4 (`modal-malformado`, `exit 1`); interfaces con `(R7.3)` en
04 (`FINDING: retired R7.3 cited at 04-use-cases.md:148`, `exit 1`).

Después de restaurar R6.4, los tres en `exit 0` otra vez; interfaces dice "36
retired ids".

## 6. Población

Vieja 199 / 32 / 22, nueva (en `aebfbd5`) 164 / 25 / 22: se fueron los 37
de la tabla de retirados y del mapa, y se sumaron R12.5 y R40.9; en la prosa
se fueron las 7 que el mapa mueve. Con R6.4 restaurada: **165 / 25 / 22**.

## Otros hallazgos (ninguno es una obligación perdida)

1. R29.2 termina "…and not otherwise" para los parámetros del slot. Es
   coherente con R38.2 ("When the slot declares none, nothing is sent").
2. R4.6: "ends at the scheduled end" pasó a "MUST end no later than the
   scheduled end", bajo la semántica de `@clip` de la base. No se verificó
   contra la copia primaria.
3. La columna de destinos del mapa no nombra R40.9 para R40.3–R40.5 ni R13.1
   para R35.6; las notas sí, y el validador los buscó ahí.
4. `check-context-coherence.py --help` corría el chequeo: ahora imprime la
   ayuda.
