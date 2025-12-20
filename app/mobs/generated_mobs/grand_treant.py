from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.grand_treant',
        display_name='Grand tréant',
        level_min=25,
        level_max=60,
        rarity=None,
        zone='Forêt Palier 6',
        drops=['Bois légendaire', "Cœur d'arbre ancien", 'Sève éternelle'],
        abilities=None,
        variants={
    25: MobStats(hp=500.0, mp=100.0, STR=90.0, AGI=25.0, INT=50.0, DEX=35.0, VIT=100.0),
    60: MobStats(hp=2000.0, mp=400.0, STR=220.0, AGI=50.0, INT=140.0, DEX=80.0, VIT=280.0),
},
    )
)
