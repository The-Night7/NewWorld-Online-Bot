from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.elu_dechu_par_les_tenebres',
        display_name='Élu déchu par les ténèbres',
        level_min=60,
        level_max=60,
        rarity='Élite',
        zone=None,
        drops=None,
        abilities=['Lame sacrée purificatrice:  Dégâts lumière élevés', 'Note:  Invulnérable sauf zone rose', 'Drop (Phase 1):  Fragment de lumière, Armure déchue'],
        variants={},
    )
)
