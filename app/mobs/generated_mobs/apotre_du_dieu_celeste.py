from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='thunder_desert.apotre_du_dieu_celeste',
        display_name='Apôtre du dieu céleste',
        zone='Désert foudroyant',
        tags=['Élite', 'Niveau 50'],
        drops=['Lance céleste', "Ailes d'apôtre", 'Fragment divin'],
        notes=['Attaque foudroyante: 2000', 'Fissure du vent: Fend sol nuageux en 2'],
        level_stats={
            50: MobStats(
                hp=1500.0,
                mp=800.0,
                STR=50.0,
                AGI=50.0,
                INT=50.0,
                DEX=50.0,
                VIT=50.0
            )
        }
    )
)
