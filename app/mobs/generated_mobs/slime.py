from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='hydra_dungeon.slime',
        display_name='Slime',
        level_min=5,
        level_max=10,
        rarity='Élite',
        zone="Donjon de l'Hydre",
        drops=['Gelée premium', 'Essence de slime'],
        abilities=['Mucus gluant:  Immobilise + 20% dégâts subis (cumulable)', 'Mucus gluant:  Immobilise + 20% dégâts subis (cumulable)'],
        variants={
    5: MobStats(hp=100.0, mp=20.0, STR=5.0, AGI=3.0, INT=4.0, DEX=2.0, VIT=25.0),
    10: MobStats(hp=150.0, mp=45.0, STR=18.0, AGI=6.0, INT=10.0, DEX=5.0, VIT=45.0),
},
    )
)
