from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key="forest.chenille_ortifleur",
        display_name="Chenille ortifleur",
        zone="Donjon de l'Hydre",
        tags=["forest", "elite"],
        drops=["Pétale d'ortifleur", "Poudre apaisante"],
        level_stats={
            1: MobStats(hp=12, mp=5, STR=4, AGI=3, INT=2, DEX=4, VIT=4, base_attack=5),
            10: MobStats(hp=80, mp=30, STR=22, AGI=10, INT=8, DEX=14, VIT=18, base_attack=40),
        },
    )
)