from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key="forest.coxiplooosion",
        display_name="Coxiplooosion",
        zone="Forêt",
        tags=["forest", "tier1"],
        drops=["Charbon", "Bouchon enflammé"],
        notes=["Explosion (à la mort): 50-80 dégâts"],
        level_stats={
            10: MobStats(hp=20, mp=15, STR=15, AGI=12, INT=8, DEX=10, VIT=4, base_attack=30),
            15: MobStats(hp=35, mp=25, STR=25, AGI=18, INT=12, DEX=15, VIT=6, base_attack=50),
        },
    )
)