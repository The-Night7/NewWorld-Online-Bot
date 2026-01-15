from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.gardienne_du_5eme_palier_kyubi_masque_au_chakra_bleu',
        display_name='Gardienne du 5ème palier: Kyubi masqué au chakra bleu',
        level_min=50,
        level_max=50,
        rarity='elite',
        zone='Passage Palier 5',
        drops=['Clé du 5ème palier', 'Masque de Kyubi', 'Queue de chakra'],
        abilities=['Flammes des 9 queues:  400/boule + Chance moyenne brûlure'],
        level_stats={
    50: MobStats(hp=5000.0, mp=900.0, STR=1000.0, AGI=140.0, INT=200.0, DEX=150.0, VIT=155.0, base_attack=0.0),
},
        variants={},
    )
)
