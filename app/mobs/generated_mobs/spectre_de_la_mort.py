from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.spectre_de_la_mort',
        display_name='Spectre de la mort',
        level_min=55,
        level_max=60,
        rarity=None,
        zone='Forêt spectrale',
        drops=['Essence de mort', 'Couronne spectrale'],
        abilities=None,
        variants={
    55: MobStats(hp=1100.0, mp=500.0, STR=160.0, AGI=155.0, INT=200.0, DEX=170.0, VIT=130.0),
    60: MobStats(hp=1300.0, mp=600.0, STR=185.0, AGI=180.0, INT=230.0, DEX=195.0, VIT=150.0),
},
    )
)
