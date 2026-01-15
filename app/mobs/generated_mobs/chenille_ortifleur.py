from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='hydra_dungeon.chenille_ortifleur',
        display_name='Chenille ortifleur',
        level_min=1,
        level_max=12,
        rarity='elite',
        zone="Donjon de l'Hydre",
        drops=["Pétale d'ortifleur", 'Poudre apaisante'],
        abilities=None,
        level_stats={
    1: MobStats(hp=12.0, mp=5.0, STR=5.0, AGI=3.0, INT=2.0, DEX=4.0, VIT=4.0, base_attack=0.0),
    10: MobStats(hp=45.0, mp=20.0, STR=30.0, AGI=8.0, INT=6.0, DEX=10.0, VIT=12.0, base_attack=0.0),
    12: MobStats(hp=80.0, mp=30.0, STR=40.0, AGI=10.0, INT=8.0, DEX=14.0, VIT=18.0, base_attack=0.0),
},
        variants={},
    )
)
