from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.amethyste_le_sabre_maudit_devoreur',
        display_name='Améthyste, le sabre maudit dévoreur',
        level_min=45,
        level_max=45,
        rarity='Boss',
        zone='Grotte cristalline (Quête unique)',
        drops=["Fragment d'Améthyste", 'Lame maudite', 'Âme du shogun'],
        abilities=['Quête:  "La lame maudite du shogun d\'edo"'],
        variants={},
    )
)
