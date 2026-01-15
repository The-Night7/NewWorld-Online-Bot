from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.amethyste_le_sabre_maudit_devoreur',
        display_name='Améthyste, le sabre maudit dévoreur',
        level_min=45,
        level_max=45,
        rarity='boss',
        zone='Grotte cristalline (Quête unique)',
        drops=["Fragment d'Améthyste", 'Lame maudite', 'Âme du shogun'],
        abilities=['Quête:  "La lame maudite du shogun d\'edo"'],
        level_stats={
    45: MobStats(hp=4500.0, mp=600.0, STR=500.0, AGI=140.0, INT=110.0, DEX=150.0, VIT=130.0, base_attack=0.0),
},
        variants={},
    )
)
