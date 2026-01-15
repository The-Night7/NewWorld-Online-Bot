from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.ryuja_le_maitre_de_la_tour',
        display_name='Ryuja le maître de la tour',
        level_min=50,
        level_max=50,
        rarity='elite',
        zone=None,
        drops=None,
        abilities=['- Aura surpuissante: Repousse attaques distance (0 dégâts, fonctionne vs "Hydre")', '- Perce-armure: Ignore défense', '- Drop: Katana de Ryuja, Parchemin du maître, Médaillon de la tour', '- Zone: Temple de Ryuja'],
        level_stats={
    50: MobStats(hp=5000.0, mp=700.0, STR=1000.0, AGI=120.0, INT=150.0, DEX=140.0, VIT=160.0, base_attack=0.0),
},
        variants={},
    )
)
