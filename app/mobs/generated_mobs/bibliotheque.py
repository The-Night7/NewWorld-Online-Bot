from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.bibliotheque',
        display_name='Bibliothèque',
        level_min=60,
        level_max=60,
        rarity='Élite',
        zone='Event',
        drops=['Livre ancien', 'Parchemin de connaissance', 'Clé de bibliothèque'],
        abilities=['Vole-skill:  Vole temporairement compétences adversaire'],
        variants={},
    )
)
