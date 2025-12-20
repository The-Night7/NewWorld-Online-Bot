from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.roi_de_la_nature_cerf_de_vie',
        display_name='Roi de la nature: Cerf de vie',
        level_min=None,
        level_max=None,
        rarity='Boss',
        zone=None,
        drops=None,
        abilities=['- Coup étourdissant: Étourdit cible 5 tours', '- Bouclier magique: Immunité effets secondaires (poison, etc.)', "- Régénération: Récupère tous PV tant qu'il a des pommes sur bois", '- Drop: Bois de cerf sacré, Pomme de vie, Couronne de nature', "- Zone: Donjon de l'Arbre Honey"],
        variants={},
    )
)
