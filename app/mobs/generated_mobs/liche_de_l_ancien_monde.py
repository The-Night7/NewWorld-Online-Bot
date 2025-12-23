from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.liche_de_l_ancien_monde',
        display_name="Liche de l'ancien monde",
        level_min=60,
        level_max=60,
        rarity='Boss',
        zone='Event',
        drops=['Bâton de liche', 'Grimoire ancien', 'Phylactère'],
        abilities=['Invocation:  Armée de monstres (sauf boss/rares)'],
        level_stats={
    60: MobStats(hp=6000.0, mp=2500.0, STR=150.0, AGI=120.0, INT=320.0, DEX=160.0, VIT=180.0, base_attack=0.0),
},
        variants={},
    )
)
