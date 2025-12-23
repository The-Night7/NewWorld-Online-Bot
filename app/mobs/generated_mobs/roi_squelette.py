from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.roi_squelette',
        display_name='Roi squelette',
        level_min=25,
        level_max=25,
        rarity='Élite',
        zone='Donjon Secret (après 4 morts)',
        drops=['Couronne du roi squelette', 'Sceptre maudit', 'Âme royale'],
        abilities=['Hurlement des morts:  Malédiction -20% gain de stats si touché', 'Condition apparition:  Être mort 4 fois'],
        level_stats={
    25: MobStats(hp=2500.0, mp=350.0, STR=200.0, AGI=55.0, INT=100.0, DEX=60.0, VIT=80.0, base_attack=0.0),
},
        variants={},
    )
)
