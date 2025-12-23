from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


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
        level_stats={
    25: MobStats(hp=2000.0, mp=250.0, STR=150.0, AGI=50.0, INT=60.0, DEX=55.0, VIT=75.0, base_attack=0.0),
},
        variants={},
    )
)
