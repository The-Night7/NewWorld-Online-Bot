from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.symboles',
        display_name='Symboles:',
        level_min=None,
        level_max=None,
        rarity=None,
        zone=None,
        drops=None,
        abilities=None,
        variants={},
    )
)
