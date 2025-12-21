from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.dino_pic_de_glace',
        display_name='Dino-pic de glace',
        level_min=60,
        level_max=60,
        rarity='Élite',
        zone=None,
        drops=None,
        abilities=['- Roule mabroule: Oneshot si écrasé', '- Lance-pique: Dégâts zone', '- Drop: Pique de glace, Écaille de dino, Fossile gelé', '- Zone: Event'],
        level_stats={},
        variants={},
    )
)
