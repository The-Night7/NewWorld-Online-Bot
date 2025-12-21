from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.tortue_geante_de_la_mer_antique',
        display_name='Tortue géante de la mer antique',
        level_min=60,
        level_max=60,
        rarity='Élite',
        zone='Event',
        drops=['Carapace antique', 'Perle de mer', 'Écaille légendaire'],
        abilities=['Carapace:  Immunité dégâts sur carapace'],
        level_stats={},
        variants={},
    )
)
