| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | M | `xs:anyURI` | — | The APS endpoint. Resolves to a List MPD or a single-period alternative MPD. |
| `@earliestResolutionTimeOffset` | OD | `xs:unsignedLong` | 60 s in units of `EventStream@timescale` | As the base: the MPD *"can be retrieved at any time between PRT – T and PRT"* (Table 63). |
| `@serviceDescriptionId` | O | `xs:unsignedInt` | — | As the base; a `PlaybackRestrictions@skipAfter` of the service description it references applies under §5.2.4. |
| `@maxDuration` | OD | `xs:unsignedLong` | infinity | The cap, in units of `EventStream@timescale`. Absent means infinity; zero means the event is not executed (Table 63). What it bounds is given in §4.5.4. |
| `@executeOnce` | OD | `xs:boolean` | `false` | As the base. |
| `@noJump` | OD | `xs:integer` | `0` | As the base. |
| `@skipAfter` | OD | `xs:duration` | `PT0S` | As the base, default included: absent, the slot is skippable everywhere (§5.2.4). |
