from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key="forest.lapin_vegetal",
        display_name="Lapin végétal",
        zone="Forêt",
        tags=["forest"],
        drops=["Herbes fraîches", "Bois sec", "Plante médicinale", "Bois renforcé"],
        level_stats={
            1: MobStats(hp=10, mp=5, STR=3, AGI=8, INT=2, DEX=5, VIT=2, base_attack=5),
            5: MobStats(hp=30, mp=15, STR=8, AGI=15, INT=5, DEX=10, VIT=6, base_attack=15),
        },
    )
)
