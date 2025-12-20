from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.gardienne_du_5eme_palier_kyubi_masque_au_chakra_bleu',
        display_name='Gardienne du 5ème palier: Kyubi masqué au chakra bleu',
        level_min=50,
        level_max=50,
        rarity='Élite',
        zone='Passage Palier 5',
        drops=['Clé du 5ème palier', 'Masque de Kyubi', 'Queue de chakra'],
        abilities=['Flammes des 9 queues:  400/boule + Chance moyenne brûlure'],
        variants={},
    )
)
