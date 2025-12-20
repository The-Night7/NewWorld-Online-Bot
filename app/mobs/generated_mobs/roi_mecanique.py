from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='mechanical_zone.roi_mecanique',
        display_name='Roi mécanique',
        level_min=30,
        level_max=30,
        rarity='Élite',
        zone='Zone mécanique',
        drops=None,
        abilities=['Drop (Phase 1):  Pièces mécaniques, Circuit magique', 'Obtention skill:  "Dieu mécanique" (pour vainqueur)', 'Drop (Phase 2):  Cœur mécanique, Blueprint légendaire, Core du roi'],
        variants={},
    )
)
