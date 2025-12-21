from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='honey_tree_dungeon.sanglier_enrage',
        display_name='Sanglier enragé',
        level_min=20,
        level_max=20,
        rarity='Élite',
        zone="Donjon de l'Arbre Honey",
        drops=['Défense de sanglier', 'Fourrure épaisse'],
        abilities=['Charge enragée:  110'],
        level_stats={},
        variants={},
    )
)
