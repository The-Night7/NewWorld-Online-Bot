from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.zombie_du_manoir',
        display_name='Zombie du manoir',
        level_min=55,
        level_max=60,
        rarity=None,
        zone="Manoir de l'ouest & Forêt spectrale",
        drops=['Os maudit', 'Relique du manoir'],
        abilities=None,
        level_stats={
    55: MobStats(hp=1400.0, mp=200.0, STR=180.0, AGI=80.0, INT=50.0, DEX=90.0, VIT=170.0, base_attack=0.0),
    60: MobStats(hp=1600.0, mp=250.0, STR=210.0, AGI=95.0, INT=60.0, DEX=105.0, VIT=195.0, base_attack=0.0),
},
        variants={},
    )
)
