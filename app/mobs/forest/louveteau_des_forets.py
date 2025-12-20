from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key="forest.louveteau_des_forets",
        display_name="Louveteau des forêts",
        zone="Forêt & Plaine",
        tags=["forest", "plain", "tier1"],
        drops=["Peau de loup", "Dent de loup"],
        notes=["Hurlement de la meute: Roll 20, obtenir 15+ invoque 1-5 louveteaux"],
        level_stats={
            3: MobStats(hp=25, mp=15, STR=8, AGI=12, INT=5, DEX=10, VIT=5, base_attack=10),
            10: MobStats(hp=60, mp=40, STR=18, AGI=22, INT=10, DEX=20, VIT=12, base_attack=30),
        },
    )
)