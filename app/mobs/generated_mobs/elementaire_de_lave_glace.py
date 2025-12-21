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
        abilities=['Drop (Phase 1):  Cristal de lave, Glace éternelle', 'Drop (Phase 2):  Noyau élémentaire, Essence duale'],
        level_stats={},
        variants={},
    )
)
