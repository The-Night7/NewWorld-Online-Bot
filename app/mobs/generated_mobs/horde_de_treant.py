from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


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
        level_stats={
    50: MobStats(hp=800.0, mp=150.0, STR=700.0, AGI=40.0, INT=80.0, DEX=60.0, VIT=140.0, base_attack=0.0),
},
        variants={},
    )
)
