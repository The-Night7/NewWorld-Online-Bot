from __future__ import annotations

import importlib
import pkgutil
from typing import Dict, Iterable, List, Optional

from .types import MobDefinition


class MobRegistry:
    def __init__(self):
        self._defs: Dict[str, MobDefinition] = {}

    def register(self, mob: MobDefinition) -> None:
        if mob.key in self._defs:
            raise ValueError(f"Mob déjà enregistré: {mob.key}")
        self._defs[mob.key] = mob

    def get(self, key: str) -> Optional[MobDefinition]:
        return self._defs.get(key)

    def all(self) -> List[MobDefinition]:
        return sorted(self._defs.values(), key=lambda m: m.key)


REGISTRY = MobRegistry()


def discover_and_register(package: str = "app.mobs") -> None:
    """
    Importe tous les sous-modules de `app.mobs` (et sous-dossiers)
    pour déclencher l’enregistrement (via REGISTRY.register).

    À appeler 1 fois au démarrage du bot.
    """
    root = importlib.import_module(package)

    # charge tous les modules du package (récursif)
    for modinfo in pkgutil.walk_packages(root.__path__, prefix=f"{package}."):
        importlib.import_module(modinfo.name)
