from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='twilight_forest.ourson_min_min',
        display_name='Ourson Min Min',
        level_min=40,
        level_max=45,
        rarity=None,
        zone='Forêt du crépuscule',
        drops=['Patte mignonne', 'Ruban Min Min'],
        abilities=None,
        level_stats={
    40: MobStats(hp=3000.0, mp=180.0, STR=130.0, AGI=80.0, INT=40.0, DEX=85.0, VIT=125.0, base_attack=0.0),
    45: MobStats(hp=3500.0, mp=220.0, STR=155.0, AGI=95.0, INT=50.0, DEX=100.0, VIT=145.0, base_attack=0.0),
},
        variants={},
    )
)
