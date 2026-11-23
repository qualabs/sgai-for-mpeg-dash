| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@family` | M | `FamilyType` <!-- refine: v12-detail-review.md#flag-1 --> | — | The family of the window this document resolves. |
| `@dismissAfter` | OD | `DismissAfterType` | `never` | The dismissal declaration of the overlay or pause slot (§5.2.4). The APS always writes it (APS-19); a document without it leaves the slot non-dismissible. |
| `@validFor` | OD | `xs:duration` | the remainder of the window's span | How long the document stays usable after the Player receives it (§5.2.5). |
| `@onExhausted` | CM | `OnExhaustedType` (§5.2.6) <!-- refine: v12-detail-review.md#flag-1 --> | `stop` | The exhaustion behaviour. Written on every document with `@family="pause"` (APS-22); absent on `@family="overlay"`. |
