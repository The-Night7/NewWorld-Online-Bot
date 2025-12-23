from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.gardien_du_3eme_palier_terongor',
        display_name='Gardien du 3ème palier: Terongor',
        level_min=25,
        level_max=25,
        rarity='Élite',
        zone='Passage Palier 3',
        drops=['Clé du 3ème palier', 'Fragment de gardien', 'Armure de Terongor'],
        abilities=None,
        level_stats={
    25: MobStats(hp=3000.0, mp=400.0, STR=300.0, AGI=60.0, INT=80.0, DEX=70.0, VIT=110.0, base_attack=0.0),
},
        variants={},
    )
)
