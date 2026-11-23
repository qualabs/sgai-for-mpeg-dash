| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@returnOffset` | O | `xs:unsignedLong` | — | As the base: the offset from `Event@presentationTime` at which the main presentation resumes. |
| `@clip` | OD | `xs:boolean` | `true` | As the base: `true` terminates the alternative presentation *"at the latest at time PRT + APDmax"*, `false` at PRTA + APDmax (Table 62). |
| `@startWithOffset` | OD | `xs:boolean` | `false` | As the base. |
