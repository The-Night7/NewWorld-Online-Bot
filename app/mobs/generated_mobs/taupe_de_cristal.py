from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='rocky_crystal.taupe_de_cristal',
        display_name='Taupe de cristal',
        level_min=30,
        level_max=35,
        rarity=None,
        zone='Zone rocheuse & Grotte cristal',
        drops=['Cristal pur', 'Noyau de cristal'],
        abilities=None,
        level_stats={
    30: MobStats(hp=320.0, mp=100.0, STR=85.0, AGI=60.0, INT=45.0, DEX=80.0, VIT=70.0, base_attack=0.0),
    35: MobStats(hp=420.0, mp=130.0, STR=105.0, AGI=75.0, INT=55.0, DEX=95.0, VIT=85.0, base_attack=0.0),
},
        variants={},
    )
)
