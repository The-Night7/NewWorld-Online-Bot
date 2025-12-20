from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key="forest.loup_alpha",
        display_name="Loup Alpha",
        zone="Forêt & Plaine",
        tags=["forest", "plain", "boss", "tier1"],
        drops=["Griffe d'Alpha", "Perle d'âme de loup"],
        notes=["Hurlement du chef de meute: Invoque 3-5 louveteaux (Lvl 10-15 selon nombre ennemis)"],
        level_stats={
            10: MobStats(hp=150, mp=60, STR=30, AGI=28, INT=15, DEX=25, VIT=20, base_attack=50),
            15: MobStats(hp=250, mp=90, STR=45, AGI=38, INT=20, DEX=35, VIT=30, base_attack=70),
        },
    )
)