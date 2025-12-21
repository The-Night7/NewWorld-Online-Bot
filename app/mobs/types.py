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


@dataclass(frozen=False)  # Changed from frozen=True to allow post-init modification
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

    def __post_init__(self):
        # Copy variants to level_stats if variants is not empty and level_stats is empty
        if self.variants and not self.level_stats:
            # Create a new dict to avoid modifying the frozen dataclass
            new_level_stats = {}
            for level, stats in self.variants.items():
                if isinstance(level, (int, str)) and isinstance(stats, MobStats):
                    new_level_stats[int(level)] = stats
            
            # Use object.__setattr__ to modify the frozen dataclass
            object.__setattr__(self, 'level_stats', new_level_stats)

    def available_levels(self) -> List[int]:
        if self.level_min is not None and self.level_max is not None:
            return list(range(self.level_min, self.level_max + 1))
        return sorted(self.level_stats.keys())