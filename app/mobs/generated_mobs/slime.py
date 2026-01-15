from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='hydra_dungeon.slime',
        display_name='Slime',
        level_min=5,
        level_max=12,
        rarity='elite',
        zone="Donjon de l'Hydre",
        drops=['Gelée premium', 'Essence de slime'],
        abilities=['Mucus gluant:  Immobilise + 20% dégâts subis (cumulable)', 'Mucus gluant:  Immobilise + 20% dégâts subis (cumulable)'],
        level_stats={
    5: MobStats(hp=100.0, mp=20.0, STR=15.0, AGI=4.0, INT=4.0, DEX=4.0, VIT=25.0, base_attack=0.0),
    10: MobStats(hp=100.0, mp=35.0, STR=30.0, AGI=8.0, INT=8.0, DEX=8.0, VIT=35.0, base_attack=0.0),
    12: MobStats(hp=150.0, mp=45.0, STR=40.0, AGI=10.0, INT=10.0, DEX=10.0, VIT=45.0, base_attack=0.0),
},
        variants={},
    )
)
