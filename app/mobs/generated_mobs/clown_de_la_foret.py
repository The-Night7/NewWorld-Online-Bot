from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='forest.clown_de_la_foret',
        display_name='Clown de la forêt',
        level_min=10,
        level_max=15,
        rarity=None,
        zone='Forêt',
        drops=['Costumes clown', 'Roue de folie'],
        abilities=None,
        variants={
    10: MobStats(hp=40.0, mp=25.0, STR=20.0, AGI=18.0, INT=12.0, DEX=22.0, VIT=8.0),
    15: MobStats(hp=65.0, mp=40.0, STR=30.0, AGI=25.0, INT=18.0, DEX=30.0, VIT=12.0),
},
    )
)
