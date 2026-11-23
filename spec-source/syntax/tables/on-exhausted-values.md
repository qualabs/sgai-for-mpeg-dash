| Enum value | Description |
|---|---|
| `repeat` | The Player presents the sequence again from its first candidate, for as long as the pause lasts. <!-- refine: v12.2-spec-validation.md#T1 --> |
| `request-again` | The Player requests a new resolution document for the same pause. A document carrying no candidates ends the pause's ads (PLY-66). |
| `stop` | The Player presents no further ad; the paused primary frame is shown. The default: it is what the viewer would see if the mechanism did not exist, and every Player can do it. |
