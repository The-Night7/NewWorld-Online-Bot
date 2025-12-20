from dataclasses import dataclass


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
