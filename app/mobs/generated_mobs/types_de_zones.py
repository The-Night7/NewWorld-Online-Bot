from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.types_de_zones',
        display_name='Types de zones:',
        level_min=None,
        level_max=None,
        rarity=None,
        zone=None,
        drops=None,
        abilities=None,
        variants={},
    )
)
