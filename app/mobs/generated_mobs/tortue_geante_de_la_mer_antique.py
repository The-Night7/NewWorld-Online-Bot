from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.tortue_geante_de_la_mer_antique',
        display_name='Tortue géante de la mer antique',
        level_min=60,
        level_max=60,
        rarity='elite',
        zone='Event',
        drops=['Carapace antique', 'Perle de mer', 'Écaille légendaire'],
        abilities=['Carapace:  Immunité dégâts sur carapace'],
        level_stats={
    60: MobStats(hp=6000.0, mp=800.0, STR=180.0, AGI=60.0, INT=140.0, DEX=100.0, VIT=300.0, base_attack=0.0),
},
        variants={},
    )
)
