from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.elementaire_de_lave_glace',
        display_name='Élémentaire de lave/glace',
        level_min=60,
        level_max=60,
        rarity='Élite',
        zone='Event',
        drops=None,
        abilities=['Phase 1: ', 'Drop (Phase 1):  Cristal de lave, Glace éternelle', 'Phase 2: ', 'Drop (Phase 2):  Noyau élémentaire, Essence duale'],
        level_stats={
    60: MobStats(hp=1000.0, mp=1200.0, STR=250.0, AGI=110.0, INT=300.0, DEX=140.0, VIT=220.0, base_attack=0.0),
},
        variants={},
    )
)
