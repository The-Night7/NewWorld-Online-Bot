from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.gardien_du_4eme_palier_garde_lave_oursobot',
        display_name='Gardien du 4ème palier: Garde-Lave Oursobot',
        level_min=40,
        level_max=40,
        rarity='Élite',
        zone=None,
        drops=None,
        abilities=['- Environnement hostile: 5% HP/tour à tous (sauf lui)', '- Canon multiple: 200/tir', '- Déferlement de lave: 500 (zone)', "- Drop: Clé du 4ème palier, Cœur de lave, Armure d'Oursobot", '- Zone: Passage Palier 4'],
        level_stats={
    40: MobStats(hp=4000.0, mp=600.0, STR=400.0, AGI=50.0, INT=100.0, DEX=70.0, VIT=150.0, base_attack=0.0),
},
        variants={},
    )
)
