from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='thunder_desert.apotre_du_dieu_celeste',
        display_name='Apôtre du dieu céleste',
        level_min=50,
        level_max=50,
        rarity='Élite',
        zone='Désert foudroyant',
        drops=['Lance céleste', "Ailes d'apôtre", 'Fragment divin'],
        abilities=['Attaque foudroyante:  2000', 'Fissure du vent:  Fend sol nuageux en 2'],
        variants={},
    )
)
