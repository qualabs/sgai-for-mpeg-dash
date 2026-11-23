| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@schemeIdUri` | M | `xs:anyURI` | — | `urn:mpeg:dash:event:callback:2015`. |
| `@value` | M | `xs:string` | — | `1`, as Table 47 requires for the callback scheme. |
| `@timescale` | OD | `xs:unsignedInt` | `1` | As the base. |
| `@presentationTimeOffset` | OD | `xs:unsignedLong` | `0` | As the base, subtracted from each event's presentation time. |
