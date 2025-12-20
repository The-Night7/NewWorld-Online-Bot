from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key="forest.bee_me_me_bee",
        display_name="BEE ME ME BEE",
        zone="Forêt",
        tags=["forest"],
        drops=["Pollen", "Venin", "Ailes de Bee", "Pollen amélioré"],
        notes=["Crachat de poison: 5/tour (lvl1) -> 15/tour (lvl10)"],
        level_stats={
            1: MobStats(hp=15, mp=10, STR=4, AGI=10, INT=3, DEX=8, VIT=3, base_attack=5),
            10: MobStats(hp=50, mp=30, STR=15, AGI=25, INT=8, DEX=20, VIT=10, base_attack=30),
        },
    )
)
