| Enum value | Description |
|---|---|
| *(absent)* | **Default.** The window is presented only over the content of the presentation whose MPD declares it. It does not replace an inherited linear event, and it is not composited over an alternative presentation (PLY-49). Two ads on screen at once never come from an overlap nobody declared. |
| `supersede` | The window stands in for the inherited linear events whose `Event@presentationTime` falls within its span. A Player of this specification presents the window and does not execute those events, and executes them after all when the window presents no ad (PLY-48). A legacy Player ignores the window and plays the linear events, so the linear break is the legacy fallback of the non-linear offering (Annex Q, Annex G). |
| `on-top` | The window is presented also while an alternative presentation that starts within its span is active, composited over it: a hybrid break (PLY-50, Annex D). |
