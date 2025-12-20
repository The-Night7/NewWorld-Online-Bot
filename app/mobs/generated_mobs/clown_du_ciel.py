from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='cloud_plains.clown_du_ciel',
        display_name='Clown du ciel',
        level_min=50,
        level_max=55,
        rarity=None,
        zone='Plaines nuageuses',
        drops=['Chapeau volant', 'Carte du ciel'],
        abilities=None,
        variants={
    50: MobStats(hp=1000.0, mp=350.0, STR=150.0, AGI=140.0, INT=120.0, DEX=145.0, VIT=115.0),
    55: MobStats(hp=1200.0, mp=420.0, STR=175.0, AGI=165.0, INT=140.0, DEX=170.0, VIT=135.0),
},
    )
)
