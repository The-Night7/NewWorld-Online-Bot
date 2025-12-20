from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='hydra_dungeon.chenille_ortifleur',
        display_name='Chenille ortifleur',
        level_min=1,
        level_max=10,
        rarity='Élite',
        zone="Donjon de l'Hydre",
        drops=["Pétale d'ortifleur", 'Poudre apaisante'],
        abilities=None,
        variants={
    1: MobStats(hp=12.0, mp=5.0, STR=4.0, AGI=3.0, INT=2.0, DEX=4.0, VIT=4.0),
    10: MobStats(hp=80.0, mp=30.0, STR=22.0, AGI=10.0, INT=8.0, DEX=14.0, VIT=18.0),
},
    )
)
