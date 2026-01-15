from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.reine_des_abeilles_enragee',
        display_name='Reine des abeilles enragée',
        level_min=50,
        level_max=50,
        rarity='elite',
        zone='Event',
        drops=['Miel royal enragé', 'Dard légendaire', 'Couronne de la reine'],
        abilities=None,
        level_stats={
    50: MobStats(hp=5000.0, mp=800.0, STR=1000.0, AGI=150.0, INT=180.0, DEX=155.0, VIT=145.0, base_attack=0.0),
},
        variants={},
    )
)
