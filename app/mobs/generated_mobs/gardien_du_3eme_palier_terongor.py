from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.gardien_du_3eme_palier_terongor',
        display_name='Gardien du 3ème palier: Terongor',
        level_min=None,
        level_max=None,
        rarity='Élite',
        zone='Passage Palier 3',
        drops=['Clé du 3ème palier', 'Fragment de gardien', 'Armure de Terongor'],
        abilities=None,
        variants={},
    )
)
