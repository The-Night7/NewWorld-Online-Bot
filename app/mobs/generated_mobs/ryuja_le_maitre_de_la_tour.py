from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.ryuja_le_maitre_de_la_tour',
        display_name='Ryuja le maître de la tour',
        level_min=50,
        level_max=50,
        rarity='Élite',
        zone=None,
        drops=None,
        abilities=['- Aura surpuissante: Repousse attaques distance (0 dégâts, fonctionne vs "Hydre")', '- Perce-armure: Ignore défense', '- Drop: Katana de Ryuja, Parchemin du maître, Médaillon de la tour', '- Zone: Temple de Ryuja'],
        level_stats={},
        variants={},
    )
)
