from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='twilight_forest.ours_en_colere_1',
        display_name='Ours en colère',
        level_min=40,
        level_max=45,
        rarity='normal',
        zone='Forêt du crépuscule',
        drops=['Griffe titanesque', "Cœur d'ours"],
        abilities=None,
        level_stats={
    40: MobStats(hp=3000.0, mp=150.0, STR=300.0, AGI=60.0, INT=30.0, DEX=70.0, VIT=130.0, base_attack=0.0),
    45: MobStats(hp=3500.0, mp=180.0, STR=350.0, AGI=70.0, INT=35.0, DEX=80.0, VIT=150.0, base_attack=0.0),
},
        variants={},
    )
)
