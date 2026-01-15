from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='honey_tree_dungeon.ours_en_colere',
        display_name='Ours en colère',
        level_min=20,
        level_max=20,
        rarity='elite',
        zone="Donjon de l'Arbre Honey",
        drops=["Patte d'ours", 'Miel sauvage'],
        abilities=None,
        level_stats={
    20: MobStats(hp=250.0, mp=35.0, STR=90.0, AGI=22.0, INT=12.0, DEX=20.0, VIT=50.0, base_attack=0.0),
},
        variants={},
    )
)
