from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.poisson_tentaculaire',
        display_name='Poisson tentaculaire',
        level_min=10,
        level_max=10,
        rarity='Élite',
        zone=None,
        drops=None,
        abilities=["- Brume d'encre: Réduit précision (12+ pour toucher au lieu de 10+)", "- Rayon d'eau: 60 dégâts", '- Drop: Tentacule géant, Encre magique, Perle des profondeurs', '- Zone: Donjon de la Pêche'],
        level_stats={},
        variants={},
    )
)
