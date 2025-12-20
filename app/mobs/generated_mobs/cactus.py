from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='crystal_cave.cactus',
        display_name='Cactus',
        level_min=40,
        level_max=45,
        rarity=None,
        zone='Grotte cristalline',
        drops=['Noyau de cactus', 'Sève toxique'],
        abilities=['Passif:  Zone poison (dégâts environnementaux/tour)', 'Passif:  Zone poison (dégâts environnementaux/tour)'],
        variants={
    40: MobStats(hp=3000.0, mp=200.0, STR=115.0, AGI=40.0, INT=60.0, DEX=65.0, VIT=150.0),
    45: MobStats(hp=3500.0, mp=240.0, STR=140.0, AGI=50.0, INT=75.0, DEX=80.0, VIT=170.0),
},
    )
)
