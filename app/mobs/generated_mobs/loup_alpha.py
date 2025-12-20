from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='forest_plains.loup_alpha',
        display_name='Loup Alpha',
        level_min=10,
        level_max=15,
        rarity='Boss',
        zone='Forêt & Plaine',
        drops=["Griffe d'Alpha", "Perle d'âme de loup"],
        abilities=['Hurlement du chef de meute:  Invoque 3-5 louveteaux (Lvl 10-15 selon nombre ennemis)', 'Hurlement du chef de meute:  Invoque 3-5 louveteaux (Lvl 10-15 selon nombre ennemis)'],
        variants={
    10: MobStats(hp=150.0, mp=60.0, STR=30.0, AGI=28.0, INT=15.0, DEX=25.0, VIT=20.0),
    15: MobStats(hp=250.0, mp=90.0, STR=45.0, AGI=38.0, INT=20.0, DEX=35.0, VIT=30.0),
},
    )
)
