from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='twilight_sunset.meduse_volante',
        display_name='Méduse volante',
        level_min=45,
        level_max=50,
        rarity=None,
        zone='Forêt du crépuscule & Montagne du soleil couchant',
        drops=['Membrane ailée', 'Essence aérienne'],
        abilities=None,
        level_stats={
    45: MobStats(hp=3000.0, mp=300.0, STR=110.0, AGI=120.0, INT=140.0, DEX=125.0, VIT=110.0, base_attack=0.0),
    50: MobStats(hp=3500.0, mp=400.0, STR=135.0, AGI=145.0, INT=170.0, DEX=150.0, VIT=130.0, base_attack=0.0),
},
        variants={},
    )
)
