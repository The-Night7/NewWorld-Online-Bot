from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.fils_du_kraken',
        display_name='Fils du Kraken',
        level_min=25,
        level_max=25,
        rarity='Event',
        zone='Event',
        drops=['Tentacule du Kraken', 'Encre abyssale'],
        abilities=['Frappe tentaculaire:  150'],
        variants={},
    )
)
