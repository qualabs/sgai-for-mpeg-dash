| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | M | `xs:anyURI` | — | The APS endpoint. Resolves to an `<svta:OverlayList family="overlay">`. The Publisher MAY encode slot constraints as query parameters of this URL, by bilateral arrangement with the APS. |
| `@durationCap` | M | `xs:unsignedLong` | — | The cap, in units of `EventStream@timescale`: the cumulative duration of what the window presents. Zero means the window does not fire. |
| `@earliestResolutionTimeOffset` | OD | `xs:unsignedLong` | 60 s in units of `EventStream@timescale` | How far before `Event@presentationTime` the Player may resolve the window. Name, units and default are the base's (Table 63). Zero means only at the start of the window. |
| `@allowedLayouts` | OD | `LayoutTokenListType` | the family default (§3.4.3) | The layouts the window admits, drawn from the tokens an overlay window may list (§3.4.3). |
| `@customRegion` | OD | `PercentRectType` | the whole viewport | The region inside which a `custom` option's rectangle lies (§5.3.5). Present only when `@allowedLayouts` lists `custom`. |
| `@linearRelation` | OD | `LinearRelationType` (§5.1.6) <!-- refine: v12-detail-review.md#flag-1 --> | the default relation | How the window relates to the inherited linear events it overlaps. |
