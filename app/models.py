from dataclasses import dataclass
from typing import Optional


@dataclass
class RuntimeEntity:
    # Identité
    name: str

    # Ressources
    hp: float
    hp_max: float
    mp: float
    mp_max: float

    # Stats
    STR: float
    AGI: float
    INT: float
    DEX: float
    VIT: float
    
    # Attribut pour la gestion de la provocation/aggro
    provoked_by: Optional['RuntimeEntity'] = None
    
    # Attribut pour identifier si l'entité est un mob ou un joueur
    is_mob: bool = False