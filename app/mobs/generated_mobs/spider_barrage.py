from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.spider_barrage',
        display_name='Spider barrage',
        level_min=50,
        level_max=50,
        rarity='event',
        zone='Event',
        drops=['Toile de barrage', 'Venin concentré'],
        abilities=None,
        level_stats={
    50: MobStats(hp=1200.0, mp=300.0, STR=700.0, AGI=160.0, INT=100.0, DEX=170.0, VIT=120.0, base_attack=0.0),
},
        variants={},
    )
)
