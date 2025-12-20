from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


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
        variants={},
    )
)
