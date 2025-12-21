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
        level_stats={},
        variants={},
    )
)
