from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='honey_tree_dungeon.ours_en_colere',
        display_name='Ours en colère',
        level_min=20,
        level_max=20,
        rarity='Élite',
        zone="Donjon de l'Arbre Honey",
        drops=["Patte d'ours", 'Miel sauvage'],
        abilities=None,
        variants={},
    )
)
