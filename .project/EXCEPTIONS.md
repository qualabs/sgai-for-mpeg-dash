# Accepted findings

Findings of `scripts/validar-proyecto.py` that were looked at once and judged
legitimate, each with the reason it is. The reason is the point of the file: an
accepted finding is not a rule switched off, it is a judgement somebody made and
wrote down, and it lives here — in the project it is about — so that it travels
with this repo and whoever audits the project reads it. The validator prints
every one of them with its reason on every run.

One `##` section per finding: the three fields the report prints, and the reason
in prose under them. An entry that stops matching anything is reported RED, so a
fixed finding does not leave its excuse behind.

## 0001-defer-to-iab-ctv-for-spatial-caps.md — no-frontmatter

- file: `0001-defer-to-iab-ctv-for-spatial-caps.md`
- rule: `no-frontmatter`
- detail: `the file opens with no --- block`

Written before the frontmatter schema existed in this skill, and it is an
accepted ADR, so its prose is not rewritten. It opens with a `# ADR 0001 -- `
heading and carries no relation to any other ADR, so there is nothing for the
pair rules to check and nothing another file can contradict. Backfilling a
frontmatter block would be an edit to an accepted ADR that buys no assertion.

## 0002-custom-layout-viewport-pixel-model.md — superseded-without-successor

- file: `0002-custom-layout-viewport-pixel-model.md`
- rule: `superseded-without-successor`
- detail: `status is superseded and superseded_by is null`

La ADR 0002 nunca se adoptó: la fase 03 se abandonó y la reemplazó el requisito R39 (LOG del 2026-09-25), no otra ADR, así que no hay sucesor que nombrar. Aceptado en la pasada de structure 3.

## phases/06-multiview/TASKS.md — decision-deferred-to-a-person

- file: `phases/06-multiview/TASKS.md`
- rule: `decision-deferred-to-a-person`
- detail: `T-08 defers a decision to somebody who is not running it ('validate the `code` set with Nicolás'): R3 extension coherent with D1–D5 and R22 / R26 / R27 decoder reasoning; verify the advanced-extension framing is explicit and self-contained; validate the `multiview-*` set with Nicolás against the reference image | pend`

Las dos revisiones de Nicolás (validar el set contra la imagen de referencia, y revisar la ADR 0003 propuesta) son parte del producto de esta fase, no una decisión que la frena. Aceptado en la pasada de structure 3, por el coordinador, salvo que Nicolás diga otra cosa.

## phases/06-multiview/TASKS.md — decision-deferred-to-a-person

- file: `phases/06-multiview/TASKS.md`
- rule: `decision-deferred-to-a-person`
- detail: `(before the first task) defers a decision to somebody who is not running it ('so Nicolás can review'): T-02** — ADR 0003 is drafted in `.project/decisions/` in `status: proposed` so Nicolás can review the decision as recorded.`

Las dos revisiones de Nicolás (validar el set contra la imagen de referencia, y revisar la ADR 0003 propuesta) son parte del producto de esta fase, no una decisión que la frena. Aceptado en la pasada de structure 3, por el coordinador, salvo que Nicolás diga otra cosa.
