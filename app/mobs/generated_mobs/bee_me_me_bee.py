from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='forest.bee_me_me_bee',
        display_name='BEE ME ME BEE',
        level_min=1,
        level_max=10,
        rarity=None,
        zone='Forêt',
        drops=['Ailes de Bee', 'Pollen amélioré'],
        abilities=['Crachat de poison:  5/tour', 'Crachat de poison:  15/tour'],
        variants={
    1: MobStats(hp=15.0, mp=10.0, STR=4.0, AGI=10.0, INT=3.0, DEX=8.0, VIT=3.0),
    10: MobStats(hp=50.0, mp=30.0, STR=15.0, AGI=25.0, INT=8.0, DEX=20.0, VIT=10.0),
},
    )
)
