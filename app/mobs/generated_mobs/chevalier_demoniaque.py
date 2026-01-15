from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='corrupted_zone.chevalier_demoniaque',
        display_name='Chevalier démoniaque',
        level_min=25,
        level_max=25,
        rarity='elite',
        zone='Zone corrompue',
        drops=None,
        abilities=['Phase 1: ', 'Lien maudit:  Immobilise + Empêche fuite/skills offensifs ou déplacement', 'Drop (Phase 1):  Armure démoniaque, Chaînes maudites', 'Phase 2 (à 50% HP): ', 'Goinfrerie:  Enferme victime dans ventre + Poison gastrique (dégâts durée)', 'Drop (Phase 2):  Épée démoniaque, Cœur corrompu'],
        level_stats={
    25: MobStats(hp=1500.0, mp=200.0, STR=200.0, AGI=50.0, INT=70.0, DEX=55.0, VIT=75.0, base_attack=0.0),
},
        variants={},
    )
)
