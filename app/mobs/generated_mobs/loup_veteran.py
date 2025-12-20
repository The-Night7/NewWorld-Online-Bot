from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='rocky_crystal.loup_veteran',
        display_name='Loup vétéran',
        level_min=30,
        level_max=35,
        rarity=None,
        zone='Zone rocheuse & Grotte cristal',
        drops=['Peau légendaire', 'Griffes de cristal'],
        abilities=None,
        variants={
    30: MobStats(hp=350.0, mp=120.0, STR=90.0, AGI=85.0, INT=35.0, DEX=75.0, VIT=60.0),
    35: MobStats(hp=450.0, mp=150.0, STR=110.0, AGI=100.0, INT=40.0, DEX=90.0, VIT=75.0),
},
    )
)
