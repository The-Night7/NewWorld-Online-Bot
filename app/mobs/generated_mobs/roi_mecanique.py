from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='mechanical_zone.roi_mecanique',
        display_name='Roi mécanique',
        level_min=30,
        level_max=30,
        rarity='elite',
        zone='Zone mécanique',
        drops=None,
        abilities=['Phase 1: ', 'Drop (Phase 1):  Pièces mécaniques, Circuit magique', 'Phase 2 (à 50% HP): ', 'Obtention skill:  "Dieu mécanique" (pour vainqueur)', 'Drop (Phase 2):  Cœur mécanique, Blueprint légendaire, Core du roi'],
        level_stats={
    30: MobStats(hp=3500.0, mp=500.0, STR=100.0, AGI=70.0, INT=140.0, DEX=90.0, VIT=120.0, base_attack=0.0),
},
        variants={},
    )
)
