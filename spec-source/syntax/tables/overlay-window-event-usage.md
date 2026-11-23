| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `EventStream@schemeIdUri` | M | `xs:anyURI` | — | `urn:svta:dash:sgai-overlay:2026`. |
| `EventStream@value` | — | `xs:string` | — | Not present (PUB-8). A Player ignores one if present (PLY-87). |
| `EventStream@timescale` | OD | `xs:unsignedInt` | `1` (base) | Units of `Event@presentationTime`, `Event@duration`, `@durationCap` and `@earliestResolutionTimeOffset`. |
| `Event@presentationTime` | OD | `xs:unsignedLong` | `0` (base) | The start of the window's span, relative to the start of the Period as the base defines. |
| `Event@duration` | M | `xs:unsignedLong` | — | The length of the span. A window without it is not a window this specification defines, and the Player treats it as PLY-29 treats a window without a cap. |
| `Event@id` | M | `xs:unsignedLong` | — | Unique in the `EventStream`, as the base requires of event identifiers. |
| `Event@status` | OD | `EventStatusType` | `repeat` (base) | As the base (DASH §5.10.2.4). |
