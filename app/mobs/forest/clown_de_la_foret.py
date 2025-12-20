from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key="forest.clown_de_la_foret",
        display_name="Clown de la forêt",
        zone="Forêt",
        tags=["forest", "tier1"],
        drops=["Costumes clown", "Roue de folie"],
        level_stats={
            10: MobStats(hp=40, mp=25, STR=20, AGI=18, INT=12, DEX=22, VIT=8, base_attack=30),
            15: MobStats(hp=65, mp=40, STR=30, AGI=25, INT=18, DEX=30, VIT=12, base_attack=50),
        },
    )
)