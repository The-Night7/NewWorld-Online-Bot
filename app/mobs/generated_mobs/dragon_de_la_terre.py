from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.dragon_de_la_terre',
        display_name='Dragon de la terre',
        level_min=60,
        level_max=60,
        rarity='Élite',
        zone=None,
        drops=None,
        abilities=['- Barrière magique: Protège vs magie (sauf pendant souffle)', '- Souffle de pierre: 2000', '- Écaille solide: -99% dégâts extérieur, x3 dégâts intérieur', '- Drop: Écaille de dragon, Cœur de terre, Griffe titanesque', '- Zone: Event'],
        level_stats={},
        variants={},
    )
)
