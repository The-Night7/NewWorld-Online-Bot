from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.reine_des_abeilles',
        display_name='Reine des abeilles',
        level_min=10,
        level_max=10,
        rarity='miniboss',
        zone=None,
        drops=None,
        abilities=['- Cri de la reine: Quand PV dans le rouge, invoque 1-5 abeilles selon roll (max 15)', '- Dard empoisonné: 30/tour', "- Drop: Miel royal, Ailes d'abeille magique", '- Zone: Forêt'],
        level_stats={
    10: MobStats(hp=70.0, mp=80.0, STR=60.0, AGI=30.0, INT=35.0, DEX=28.0, VIT=14.0, base_attack=0.0),
},
        variants={},
    )
)
