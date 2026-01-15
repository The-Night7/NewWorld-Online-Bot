from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='thunder_desert.apotre_du_dieu_celeste',
        display_name='Apôtre du dieu céleste',
        level_min=50,
        level_max=50,
        rarity='elite',
        zone='Désert foudroyant',
        drops=['Lance céleste', "Ailes d'apôtre", 'Fragment divin'],
        abilities=['Attaque foudroyante:  2000', 'Fissure du vent:  Fend sol nuageux en 2'],
        level_stats={
    50: MobStats(hp=5000.0, mp=800.0, STR=180.0, AGI=130.0, INT=190.0, DEX=145.0, VIT=150.0, base_attack=0.0),
},
        variants={},
    )
)
