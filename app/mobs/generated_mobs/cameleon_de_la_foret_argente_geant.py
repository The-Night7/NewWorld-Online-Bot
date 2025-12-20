from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.cameleon_de_la_foret_argente_geant',
        display_name='Caméléon de la forêt argenté géant',
        level_min=60,
        level_max=60,
        rarity='Élite',
        zone=None,
        drops=None,
        abilities=["- Camouflage de l'ombre: Invisibilité", '- Langue somnifère: Endort cible', '- Drop: Peau de caméléon, Langue magique, Œil argenté', '- Zone: Event'],
        variants={},
    )
)
