from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.louveteau_enrage',
        display_name='Louveteau enragé',
        level_min=20,
        level_max=25,
        rarity='normal',
        zone='Palier 2',
        drops=["Peau d'alpha junior", 'Dent acérée'],
        abilities=['Hurlement de la meute:  Invoque 1+ loups selon roll 20', 'Hurlement de la meute:  Invoque 1+ loups selon roll 20'],
        level_stats={
    20: MobStats(hp=150.0, mp=60.0, STR=70.0, AGI=45.0, INT=20.0, DEX=40.0, VIT=30.0, base_attack=0.0),
    25: MobStats(hp=200.0, mp=80.0, STR=100.0, AGI=60.0, INT=25.0, DEX=55.0, VIT=40.0, base_attack=0.0),
},
        variants={},
    )
)
