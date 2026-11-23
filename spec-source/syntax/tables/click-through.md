| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | M | `xs:anyURI` | — | The destination opened, or handed off to the device, when the viewer activates the ClickThrough. |
| `@trackingUris` | O | `URIListType` <!-- refine: v12-detail-review.md#flag-1 --> | — | The click-tracking URLs. On activation the Player issues an HTTP GET to each once and ignores the response, as for a callback. Absent when the advertiser declared none. |
