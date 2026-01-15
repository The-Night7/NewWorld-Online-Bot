from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='honey_tree_dungeon.sanglier_enrage',
        display_name='Sanglier enragé',
        level_min=20,
        level_max=20,
        rarity='elite',
        zone="Donjon de l'Arbre Honey",
        drops=['Défense de sanglier', 'Fourrure épaisse'],
        abilities=['Charge enragée:  110'],
        level_stats={
    20: MobStats(hp=200.0, mp=30.0, STR=70.0, AGI=25.0, INT=12.0, DEX=20.0, VIT=40.0, base_attack=0.0),
},
        variants={},
    )
)
