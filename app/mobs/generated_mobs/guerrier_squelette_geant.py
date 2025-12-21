from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.guerrier_squelette_geant',
        display_name='Guerrier squelette géant',
        level_min=60,
        level_max=60,
        rarity='Élite',
        zone='Event',
        drops=['Épée géante maudite', 'Armure de squelette', 'Crâne colossal'],
        abilities=["Coup d'épée:  3000"],
        level_stats={},
        variants={},
    )
)
