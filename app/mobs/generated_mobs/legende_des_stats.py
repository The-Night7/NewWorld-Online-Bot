from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='misc.legende_des_stats',
        display_name='Légende des stats:',
        level_min=None,
        level_max=None,
        rarity=None,
        zone=None,
        drops=None,
        abilities=['STR (Strength):  Force physique - Augmente dégâts physiques', "AGI (Agility):  Agilité - Vitesse d'action et esquive", 'INT (Intelligence):  Intelligence - Puissance magique', 'DEX (Dexterity):  Dextérité - Précision et critique', 'VIT (Vitality):  Vitalité - Résistance et défense'],
        level_stats={},
        variants={},
    )
)
