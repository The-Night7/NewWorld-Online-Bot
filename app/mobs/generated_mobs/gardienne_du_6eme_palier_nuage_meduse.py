from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.gardienne_du_6eme_palier_nuage_meduse',
        display_name='Gardienne du 6ème palier: Nuage-médusé',
        level_min=55,
        level_max=55,
        rarity='Élite',
        zone='Passage Palier 6',
        drops=['Clé du 6ème palier', 'Tentacule nuageux', 'Perle céleste'],
        abilities=['Coup de tentacule:  1000 x6'],
        level_stats={},
        variants={},
    )
)
