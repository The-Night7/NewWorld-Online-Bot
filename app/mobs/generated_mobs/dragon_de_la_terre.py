from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.dragon_de_la_terre',
        display_name='Dragon de la terre',
        level_min=60,
        level_max=60,
        rarity='elite',
        zone=None,
        drops=None,
        abilities=['- Barrière magique: Protège vs magie (sauf pendant souffle)', '- Souffle de pierre: 2000', '- Écaille solide: -99% dégâts extérieur, x3 dégâts intérieur', '- Drop: Écaille de dragon, Cœur de terre, Griffe titanesque', '- Zone: Event'],
        level_stats={
    60: MobStats(hp=6000.0, mp=1000.0, STR=220.0, AGI=100.0, INT=180.0, DEX=130.0, VIT=250.0, base_attack=0.0),
},
        variants={},
    )
)
