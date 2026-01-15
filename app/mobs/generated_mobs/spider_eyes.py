from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='forest.spider_eyes',
        display_name='Spider-eyes',
        level_min=1,
        level_max=10,
        rarity='normal',
        zone='Forêt',
        drops=["Œuf d'araignée", 'Poussière toxique'],
        abilities=['Toile gluante:  Immobilise 2 tours', 'Toile gluante:  Immobilise 2 tours'],
        level_stats={
    1: MobStats(hp=15.0, mp=8.0, STR=5.0, AGI=6.0, INT=4.0, DEX=9.0, VIT=3.0, base_attack=0.0),
    10: MobStats(hp=50.0, mp=25.0, STR=30.0, AGI=15.0, INT=12.0, DEX=22.0, VIT=10.0, base_attack=0.0),
},
        variants={},
    )
)
