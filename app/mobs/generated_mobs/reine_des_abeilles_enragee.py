from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.reine_des_abeilles_enragee',
        display_name='Reine des abeilles enragée',
        level_min=50,
        level_max=50,
        rarity='Élite',
        zone='Event',
        drops=['Miel royal enragé', 'Dard légendaire', 'Couronne de la reine'],
        abilities=None,
        level_stats={},
        variants={},
    )
)
