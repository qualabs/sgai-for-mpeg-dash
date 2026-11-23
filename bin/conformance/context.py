"""What a rule's check receives."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Ctx:
    spec_path: Path
    spec_text: str
    blocks: list
    requests: list
    isodir: Path
    iso: object              # lxml XMLSchema of DASH-MPD.xsd alone
    combined: object = None  # DASH-MPD.xsd + extension XSD, or None if it does not compile
    ext_text: str = ""
    context_dir: Path | None = None
    extra: dict = field(default_factory=dict)

    def by_kind(self, *kinds):
        return [b for b in self.blocks if b.kind in kinds]
