| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@src` | M | `xs:anyURI` | — | The creative: an SPS sub-MPD for the video form, the image, or the HTML document. |
| `@mimeType` | M | `xs:string` | — | The media type of `@src`. Determines the form (table below). |
| `@duration` | CM | `xs:duration` | — | How long the option is shown, on the slot timeline (PLY-70). Present if and only if the form is image or HTML. A video option's duration is the `Period@duration` of its sub-MPD, which this attribute does not restate (DOC-6). |
| `@layout` | M | `LayoutTokenType` | — | One token of §3.4.2 (§5.3.3). |
| `@rect` | CM | `PercentRectType` | — | The overlay's rectangle. Present if and only if `@layout="custom"` (§5.3.5). |
| `@background` | CM | `xs:anyURI` | — | The advertiser's background image. Present if and only if `@layout="squeezeback-double-box-background"` (§5.3.6). |
