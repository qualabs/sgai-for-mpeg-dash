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
