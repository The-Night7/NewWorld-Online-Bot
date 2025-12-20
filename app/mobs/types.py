from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class MobStats:
    hp: float
    mp: float
    STR: float
    AGI: float
    INT: float
    DEX: float
    VIT: float

    base_attack: float = 0.0  # optionnel (si tu veux t'en servir plus tard)


@dataclass(frozen=True)
class MobDefinition:
    """
    Définition "bestiaire".

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

    # Champs pour la compatibilité avec les fichiers générés
    level_min: Optional[int] = None
    level_max: Optional[int] = None
    rarity: Optional[str] = None
    abilities: List[str] = field(default_factory=list)
    variants: Dict[str, Any] = field(default_factory=dict)

    def available_levels(self) -> List[int]:
        if self.level_min is not None and self.level_max is not None:
            return list(range(self.level_min, self.level_max + 1))
        return sorted(self.level_stats.keys())
