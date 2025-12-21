from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='forest_plains.louveteau_des_forets',
        display_name='Louveteau des forêts',
        level_min=3,
        level_max=10,
        rarity=None,
        zone='Forêt & Plaine',
        drops=['Peau de loup', 'Dent de loup'],
        abilities=['Hurlement de la meute:  Roll 20, obtenir 15+ invoque 1-5 louveteaux', 'Hurlement de la meute:  Roll 20, obtenir 15+ invoque 1-5 louveteaux'],
        level_stats={
    3: MobStats(hp=25.0, mp=15.0, STR=8.0, AGI=12.0, INT=5.0, DEX=10.0, VIT=5.0, base_attack=0.0),
    10: MobStats(hp=60.0, mp=40.0, STR=18.0, AGI=22.0, INT=10.0, DEX=20.0, VIT=12.0, base_attack=0.0),
},
        variants={},
    )
)
