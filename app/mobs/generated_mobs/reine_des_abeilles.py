from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.reine_des_abeilles',
        display_name='Reine des abeilles',
        level_min=10,
        level_max=10,
        rarity='Boss',
        zone=None,
        drops=None,
        abilities=['- Cri de la reine: Quand PV dans le rouge, invoque 1-5 abeilles selon roll (max 15)', '- Dard empoisonné: 30/tour', "- Drop: Miel royal, Ailes d'abeille magique", '- Zone: Forêt'],
        level_stats={},
        variants={},
    )
)
