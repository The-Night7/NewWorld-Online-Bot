from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='event.phenix_de_glace',
        display_name='Phénix de glace',
        level_min=25,
        level_max=25,
        rarity='Élite',
        zone='Event',
        drops=None,
        abilities=['- Pluie de plumes: 50/plume', '- Javelot de glace: 150', '- Gel instantané: Glacifie attaques liquides (réduction dégâts, sauf après attaque vent)', '- Laserglace: 200', '- Drop (Phase 1): Plume de glace, Cristal gelé'],
        level_stats={},
        variants={},
    )
)
