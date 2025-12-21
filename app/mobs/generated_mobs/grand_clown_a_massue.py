from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event_secret.grand_clown_a_massue',
        display_name='Grand Clown à massue',
        level_min=20,
        level_max=20,
        rarity='Élite',
        zone='Event Secret',
        drops=['Massue légendaire', 'Masque du clown fou'],
        abilities=['Grand coup de massue:  200'],
        level_stats={},
        variants={},
    )
)
