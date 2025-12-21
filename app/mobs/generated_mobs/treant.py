from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='forest_tier2.treant',
        display_name='Tréant',
        level_min=20,
        level_max=25,
        rarity=None,
        zone='Forêt Palier 2',
        drops=['Écorce renforcée', 'Racine éternelle'],
        abilities=None,
        level_stats={
    20: MobStats(hp=200.0, mp=50.0, STR=50.0, AGI=15.0, INT=30.0, DEX=20.0, VIT=55.0, base_attack=0.0),
    25: MobStats(hp=280.0, mp=70.0, STR=70.0, AGI=18.0, INT=40.0, DEX=25.0, VIT=70.0, base_attack=0.0),
},
        variants={},
    )
)
