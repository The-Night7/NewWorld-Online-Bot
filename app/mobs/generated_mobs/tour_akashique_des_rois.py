from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.tour_akashique_des_rois',
        display_name='Tour akashique des rois',
        level_min=60,
        level_max=60,
        rarity='Élite',
        zone=None,
        drops=None,
        abilities=['- Barrière gravitationnelle: Repousse corps-à-corps (sauf attaques répétitives)', '- Copie-cast: Renvoie sorts', '- Drop: Fragment de tour, Archives royales, Clé akashique', '- Zone: Event'],
        level_stats={},
        variants={},
    )
)
