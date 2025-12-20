from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.amethyste_le_sabre_maudit_devoreur',
        display_name='Améthyste, le sabre maudit dévoreur',
        zone='Grotte cristalline (Quête unique)',
        tags=['Boss', 'Niveau 45'],
        drops=["Fragment d'Améthyste", 'Lame maudite', 'Âme du shogun'],
        notes=['Quête: "La lame maudite du shogun d\'edo"'],
        level_stats={
            45: MobStats(
                hp=1000.0,
                mp=500.0,
                STR=45.0,
                AGI=45.0,
                INT=45.0,
                DEX=45.0,
                VIT=45.0
            )
        }
    )
)
