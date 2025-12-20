from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='crystal_cave.chenille_ortifleur_1',
        display_name='Chenille ortifleur',
        level_min=40,
        level_max=45,
        rarity=None,
        zone='Grotte cristalline',
        drops=['Cocon cristallisé', 'Essence florale'],
        abilities=None,
        variants={
    40: MobStats(hp=3000.0, mp=150.0, STR=125.0, AGI=50.0, INT=45.0, DEX=70.0, VIT=140.0),
    45: MobStats(hp=3500.0, mp=180.0, STR=150.0, AGI=60.0, INT=55.0, DEX=85.0, VIT=160.0),
},
    )
)
