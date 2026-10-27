# T-04 — evidencia

> Registro de la fase 08, cerrada el 2026-10-27: dice lo que pasó, no lo que hay que hacer.

## Suite completa

```
$ python3 -W error::ResourceWarning bin/test_check_context_interfaces.py -v
test_green_on_the_real_context (__main__.CoherenceRetired.test_green_on_the_real_context) ... ok
test_retired_id_defined_again_is_defined_twice (__main__.CoherenceRetired.test_retired_id_defined_again_is_defined_twice) ... ok
test_retired_row_counts_as_defined (__main__.CoherenceRetired.test_retired_row_counts_as_defined) ... ok
test_a_player_criterion_is_the_writer_of_the_request (__main__.Interfaces.test_a_player_criterion_is_the_writer_of_the_request) ... ok
test_element_in_two_interfaces (__main__.Interfaces.test_element_in_two_interfaces) ... ok
test_element_twice_in_one_interface (__main__.Interfaces.test_element_twice_in_one_interface) ... ok
test_green_on_the_real_context (__main__.Interfaces.test_green_on_the_real_context) ... ok
test_help_states_the_exits (__main__.Interfaces.test_help_states_the_exits) ... ok
test_interface_with_no_rows_cannot_tell (__main__.Interfaces.test_interface_with_no_rows_cannot_tell) ... ok
test_no_interfaces_section_cannot_tell (__main__.Interfaces.test_no_interfaces_section_cannot_tell) ... ok
test_no_retired_section_cannot_tell (__main__.Interfaces.test_no_retired_section_cannot_tell) ... ok
test_retired_id_cited_in_03_outside_its_row (__main__.Interfaces.test_retired_id_cited_in_03_outside_its_row) ... ok
test_retired_id_cited_in_a_use_case (__main__.Interfaces.test_retired_id_cited_in_a_use_case) ... ok
test_retired_id_defined_again (__main__.Interfaces.test_retired_id_defined_again) ... ok
test_row_to_a_criterion_its_writer_does_not_hold (__main__.Interfaces.test_row_to_a_criterion_its_writer_does_not_hold) ... ok
test_row_to_missing_criterion (__main__.Interfaces.test_row_to_missing_criterion) ... ok
test_row_with_two_ids (__main__.Interfaces.test_row_with_two_ids) ... ok
test_vanished_id_not_in_the_retired_table (__main__.Interfaces.test_vanished_id_not_in_the_retired_table) ... ok
test_wrong_command_line (__main__.Interfaces.test_wrong_command_line) ... ok
Ran 19 tests in 1.233s
OK
```

## Campaña de mutación

Una rotura deliberada por regla en el código de los checks, cada una contra
el único test que la cubre; el archivo se restaura después de cada una
(`diff -q` contra la copia: idénticos al final).

```
M1 no existence check -> Interfaces.test_row_to_missing_criterion: FAILED (failures=1)
M2a no duplicate check -> Interfaces.test_element_twice_in_one_interface: FAILED (failures=1)
M2b no duplicate check -> Interfaces.test_element_in_two_interfaces: FAILED (failures=1)
M3 no writer check -> Interfaces.test_row_to_a_criterion_its_writer_does_not_hold: FAILED (failures=1)
M3b writer of I-REQ dropped -> Interfaces.test_a_player_criterion_is_the_writer_of_the_request: FAILED (failures=1)
M3c one-id rule -> Interfaces.test_row_with_two_ids: FAILED (failures=1)
M4a no retired-cite check -> Interfaces.test_retired_id_cited_in_a_use_case: FAILED (failures=1)
M4b skip all of 03 -> Interfaces.test_retired_id_cited_in_03_outside_its_row: FAILED (failures=1)
M4c reuse -> Interfaces.test_retired_id_defined_again: FAILED (failures=1)
M5 no vanished check -> Interfaces.test_vanished_id_not_in_the_retired_table: FAILED (failures=1)
M6a exit2 interfaces -> Interfaces.test_no_interfaces_section_cannot_tell: FAILED (failures=1)
M6b exit2 retired -> Interfaces.test_no_retired_section_cannot_tell: FAILED (failures=1)
M6c exit2 empty -> Interfaces.test_interface_with_no_rows_cannot_tell: FAILED (failures=1)
M7 exit64 -> Interfaces.test_wrong_command_line: FAILED (failures=1)
C1 retired not defined -> CoherenceRetired.test_green_on_the_real_context: FAILED (failures=1)
C2 twice -> CoherenceRetired.test_retired_id_defined_again_is_defined_twice: FAILED (failures=1)
```

Ninguna rotura quedó verde. `check-context-coherence.py` ganó `--context DIR`
para poder correr sobre una copia.
