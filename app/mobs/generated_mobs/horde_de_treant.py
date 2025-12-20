from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.horde_de_treant',
        display_name='Horde de tréant',
        level_min=50,
        level_max=50,
        rarity='Event',
        zone='Event',
        drops=['Bois ancien massif', 'Racine entrelacée'],
        abilities=None,
        variants={},
    )
)
