from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.guerrier_squelette_geant',
        display_name='Guerrier squelette géant',
        level_min=60,
        level_max=60,
        rarity='elite',
        zone='Event',
        drops=['Épée géante maudite', 'Armure de squelette', 'Crâne colossal'],
        abilities=["Coup d'épée:  3000"],
        level_stats={
    60: MobStats(hp=6000.0, mp=500.0, STR=250.0, AGI=130.0, INT=100.0, DEX=150.0, VIT=210.0, base_attack=0.0),
},
        variants={},
    )
)
