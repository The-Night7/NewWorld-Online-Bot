from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='hydra_dungeon.hydre_au_poison',
        display_name='Hydre au poison',
        level_min=15,
        level_max=15,
        rarity='Élite',
        zone="Donjon de l'Hydre",
        drops=["Écailles de l'hydre", 'Venin purifié', "Cœur d'hydre"],
        abilities=['Crachat de poison:  50/tour + dégats de base'],
        variants={},
    )
)
