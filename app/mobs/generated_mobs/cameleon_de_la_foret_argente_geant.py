from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


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
        level_stats={
    60: MobStats(hp=6000.0, mp=900.0, STR=1000.0, AGI=180.0, INT=160.0, DEX=220.0, VIT=190.0, base_attack=0.0),
},
        variants={},
    )
)
