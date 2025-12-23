from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.phenix_de_glace',
        display_name='Phénix de glace',
        level_min=25,
        level_max=25,
        rarity='Élite',
        zone=None,
        drops=None,
        abilities=['Phase 1: '],
        level_stats={
    25: MobStats(hp=2500.0, mp=400.0, STR=100.0, AGI=70.0, INT=120.0, DEX=65.0, VIT=90.0, base_attack=0.0),
},
        variants={},
    )
)
