from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.fantome_des_flammes_bleues',
        display_name='Fantôme des flammes bleues',
        level_min=55,
        level_max=60,
        rarity=None,
        zone="Manoir de l'ouest",
        drops=['Cœur de flamme', 'Lanterne maudite'],
        abilities=None,
        level_stats={
    55: MobStats(hp=1050.0, mp=550.0, STR=155.0, AGI=165.0, INT=210.0, DEX=175.0, VIT=125.0, base_attack=0.0),
    60: MobStats(hp=1250.0, mp=650.0, STR=180.0, AGI=190.0, INT=240.0, DEX=200.0, VIT=145.0, base_attack=0.0),
},
        variants={},
    )
)
