from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.feu_follet',
        display_name='Feu follet',
        level_min=55,
        level_max=60,
        rarity=None,
        zone='Cimetière',
        drops=['Lanterne du cimetière', 'Âme errante'],
        abilities=None,
        level_stats={
    55: MobStats(hp=800.0, mp=600.0, STR=1000.0, AGI=180.0, INT=220.0, DEX=185.0, VIT=100.0, base_attack=0.0),
    60: MobStats(hp=950.0, mp=700.0, STR=1200.0, AGI=205.0, INT=250.0, DEX=210.0, VIT=115.0, base_attack=0.0),
},
        variants={},
    )
)
