from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.roi_de_la_nature_cerf_de_vie',
        display_name='Roi de la nature: Cerf de vie',
        level_min=20,
        level_max=20,
        rarity='boss',
        zone=None,
        drops=None,
        abilities=['- Coup étourdissant: Étourdit cible 5 tours', '- Bouclier magique: Immunité effets secondaires (poison, etc.)', "- Régénération: Récupère tous PV tant qu'il a des pommes sur bois", '- Drop: Bois de cerf sacré, Pomme de vie, Couronne de nature', "- Zone: Donjon de l'Arbre Honey"],
        level_stats={
    20: MobStats(hp=1500.0, mp=300.0, STR=100.0, AGI=45.0, INT=80.0, DEX=50.0, VIT=85.0, base_attack=0.0),
},
        variants={},
    )
)
