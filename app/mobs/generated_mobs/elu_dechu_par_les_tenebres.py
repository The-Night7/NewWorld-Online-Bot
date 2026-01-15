from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.elu_dechu_par_les_tenebres',
        display_name='Élu déchu par les ténèbres',
        level_min=60,
        level_max=60,
        rarity='elite',
        zone=None,
        drops=None,
        abilities=['Phase 1: ', 'Lame sacrée purificatrice:  Dégâts lumière élevés', 'Note:  Invulnérable sauf zone rose', 'Drop (Phase 1):  Fragment de lumière, Armure déchue', 'Phase 2 (à 50% HP): '],
        level_stats={
    60: MobStats(hp=6000.0, mp=1500.0, STR=4000.0, AGI=160.0, INT=250.0, DEX=180.0, VIT=220.0, base_attack=0.0),
},
        variants={},
    )
)
