from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='ghost_zone.zombie',
        display_name='Zombie',
        level_min=12,
        level_max=20,
        rarity=None,
        zone='Zone Fantôme',
        drops=['Crâne maudit', 'Essence nécrotique'],
        abilities=None,
        level_stats={
    12: MobStats(hp=80.0, mp=10.0, STR=22.0, AGI=8.0, INT=5.0, DEX=10.0, VIT=18.0, base_attack=0.0),
    20: MobStats(hp=150.0, mp=20.0, STR=45.0, AGI=12.0, INT=8.0, DEX=15.0, VIT=35.0, base_attack=0.0),
},
        variants={},
    )
)
