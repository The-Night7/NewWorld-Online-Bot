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
        level_stats={
    60: MobStats(hp=6000.0, mp=600.0, STR=230.0, AGI=90.0, INT=120.0, DEX=110.0, VIT=240.0, base_attack=0.0),
},
        variants={},
    )
)
