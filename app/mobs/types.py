from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class MobStats:
    hp: float
    mp: float
    STR: float
    AGI: float
    INT: float
    DEX: float
    VIT: float

    base_attack: float = 0.0  # optionnel (si tu veux t’en servir plus tard)


@dataclass(frozen=True)
class MobDefinition:
    """
    Définition “bestiaire”.

    level_stats: dict {level: MobStats}
      - tu peux mettre 1 seul niveau (ex: boss fixe)
      - ou 2+ niveaux (ex: niveau 1 et 5) pour interpolation.
    """

    key: str                 # identifiant unique (slug)
    display_name: str        # nom RP
    zone: str = "?"
    tags: List[str] = field(default_factory=list)  # ex: ["forest"], ["boss"], ["rare"]

    drops: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)  # ex: poison, toile...

    level_stats: Dict[int, MobStats] = field(default_factory=dict)

    def available_levels(self) -> List[int]:
        return sorted(self.level_stats.keys())
