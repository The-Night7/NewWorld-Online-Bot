from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='corrupted_zone.chevalier_demoniaque',
        display_name='Chevalier démoniaque',
        level_min=25,
        level_max=25,
        rarity='Élite',
        zone='Zone corrompue',
        drops=None,
        abilities=['Lien maudit:  Immobilise + Empêche fuite/skills offensifs ou déplacement', 'Drop (Phase 1):  Armure démoniaque, Chaînes maudites', 'Goinfrerie:  Enferme victime dans ventre + Poison gastrique (dégâts durée)', 'Drop (Phase 2):  Épée démoniaque, Cœur corrompu'],
        variants={},
    )
)
