from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='hydra_dungeon.hydre_au_poison',
        display_name='Hydre au poison',
        level_min=15,
        level_max=15,
        rarity='elite',
        zone="Donjon de l'Hydre",
        drops=["Écailles de l'hydre", 'Venin purifié', "Cœur d'hydre"],
        abilities=['Crachat de poison:  50/tour + dégats de base'],
        level_stats={
    15: MobStats(hp=1500.0, mp=200.0, STR=50.0, AGI=20.0, INT=45.0, DEX=30.0, VIT=80.0, base_attack=0.0),
},
        variants={},
    )
)
