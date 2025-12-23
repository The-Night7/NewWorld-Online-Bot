from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='forest.lapin_vegetal',
        display_name='Lapin végétal',
        level_min=1,
        level_max=5,
        rarity=None,
        zone='Forêt',
        drops=['Plante médicinale', 'Bois renforcé'],
        abilities=None,
        level_stats={
    1: MobStats(hp=10.0, mp=5.0, STR=5.0, AGI=8.0, INT=2.0, DEX=5.0, VIT=2.0, base_attack=0.0),
    5: MobStats(hp=30.0, mp=15.0, STR=15.0, AGI=15.0, INT=5.0, DEX=10.0, VIT=6.0, base_attack=0.0),
},
        variants={},
    )
)
