| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | M | `xs:anyURI` | — | The APS endpoint. Resolves to an `<svta:OverlayList family="pause">`. |
| `@durationCap` | M | `xs:unsignedLong` | — | The cap, in units of `EventStream@timescale`. Required on every pause window (PUB-2); it bounds nothing on a pause window, whose slot the viewer bounds (PLY-32). <!-- refine: v12.2-spec-validation.md#T1 --> |
| `@earliestResolutionTimeOffset` | OD | `xs:unsignedLong` | 60 s in units of `EventStream@timescale` | How far before the start of the window the Player may resolve it. Computed against `Event@presentationTime`, never against the pause. |
| `@allowedLayouts` | OD | `LayoutTokenListType` | the family default (§3.4.3) | The layouts the window admits: `pause-fullscreen`, `pause-partial`, or both (§3.4.3). |
| `@executeOnce` | OD | `xs:boolean` | `false` | When `true`, the window yields at most one pause ad for the whole session (PLY-63, PLY-64). The name is the base's, and so is the counter rule: the window is consumed when a pause ad successfully starts rendering. |
| `@linearRelation` | OD | `OnTopOnlyType` (§5.1.6) <!-- refine: v12-detail-review.md#flag-1 --> | the default relation | Takes only the value `on-top` on a pause window (§5.1.6). |
