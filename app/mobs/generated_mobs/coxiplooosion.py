from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='forest.coxiplooosion',
        display_name='Coxiplooosion',
        level_min=10,
        level_max=15,
        rarity=None,
        zone='Forêt',
        drops=['Charbon', 'Bouchon enflammé'],
        abilities=['Explosion (à la mort):  50', 'Explosion (à la mort):  80'],
        variants={
    10: MobStats(hp=20.0, mp=15.0, STR=15.0, AGI=12.0, INT=8.0, DEX=10.0, VIT=4.0),
    15: MobStats(hp=35.0, mp=25.0, STR=25.0, AGI=18.0, INT=12.0, DEX=15.0, VIT=6.0),
},
    )
)
