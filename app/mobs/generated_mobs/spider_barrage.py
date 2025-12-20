from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.spider_barrage',
        display_name='Spider barrage',
        level_min=50,
        level_max=50,
        rarity='Event',
        zone='Event',
        drops=['Toile de barrage', 'Venin concentré'],
        abilities=None,
        variants={},
    )
)
