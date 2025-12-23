from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='ghost_zone.spectre',
        display_name='Spectre',
        level_min=12,
        level_max=20,
        rarity=None,
        zone='Zone Fantôme',
        drops=['Essence spectrale', 'Voile maudit'],
        abilities=['Toucher maudit:  Malédiction -10% stats (cumulable)', 'Toucher maudit:  Malédiction -10% stats (cumulable)'],
        level_stats={
    12: MobStats(hp=60.0, mp=40.0, STR=30.0, AGI=20.0, INT=30.0, DEX=22.0, VIT=12.0, base_attack=0.0),
    20: MobStats(hp=120.0, mp=80.0, STR=70.0, AGI=35.0, INT=55.0, DEX=40.0, VIT=22.0, base_attack=0.0),
},
        variants={},
    )
)
