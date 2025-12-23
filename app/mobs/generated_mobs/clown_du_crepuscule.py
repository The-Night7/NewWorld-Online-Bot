from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='twilight_forest.clown_du_crepuscule',
        display_name='Clown du crépuscule',
        level_min=40,
        level_max=45,
        rarity=None,
        zone='Forêt du crépuscule',
        drops=['Cape du crépuscule', 'Carte joker'],
        abilities=None,
        level_stats={
    40: MobStats(hp=600.0, mp=200.0, STR=300.0, AGI=100.0, INT=80.0, DEX=110.0, VIT=90.0, base_attack=0.0),
    45: MobStats(hp=750.0, mp=250.0, STR=350.0, AGI=120.0, INT=95.0, DEX=130.0, VIT=105.0, base_attack=0.0),
},
        variants={},
    )
)
