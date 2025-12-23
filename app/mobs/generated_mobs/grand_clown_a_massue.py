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
        level_stats={
    20: MobStats(hp=1000.0, mp=100.0, STR=100.0, AGI=35.0, INT=25.0, DEX=40.0, VIT=55.0, base_attack=0.0),
},
        variants={},
    )
)
