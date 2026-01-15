from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.types_de_zones',
        display_name='Types de zones:',
        level_min=None,
        level_max=None,
        rarity='normal',
        zone=None,
        drops=None,
        abilities=None,
        level_stats={},
        variants={},
    )
)
