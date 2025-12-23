from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.golem',
        display_name='Golem',
        level_min=5,
        level_max=25,
        rarity=None,
        zone='Divers',
        drops=['Noyau de golem', 'Minerai rare'],
        abilities=None,
        level_stats={
    5: MobStats(hp=120.0, mp=5.0, STR=30.0, AGI=5.0, INT=3.0, DEX=8.0, VIT=35.0, base_attack=0.0),
    25: MobStats(hp=400.0, mp=20.0, STR=100.0, AGI=12.0, INT=10.0, DEX=18.0, VIT=100.0, base_attack=0.0),
},
        variants={},
    )
)
