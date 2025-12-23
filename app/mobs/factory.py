from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from .mob_types import MobDefinition, MobStats
from ..models import RuntimeEntity


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _interpolate_stats(low_lvl: int, low: MobStats, high_lvl: int, high: MobStats, lvl: int) -> MobStats:
    if high_lvl == low_lvl:
        return low
    t = (lvl - low_lvl) / (high_lvl - low_lvl)
    return MobStats(
        hp=_lerp(low.hp, high.hp, t),
        mp=_lerp(low.mp, high.mp, t),
        STR=_lerp(low.STR, high.STR, t),
        AGI=_lerp(low.AGI, high.AGI, t),
        INT=_lerp(low.INT, high.INT, t),
        DEX=_lerp(low.DEX, high.DEX, t),
        VIT=_lerp(low.VIT, high.VIT, t),
        base_attack=_lerp(low.base_attack, high.base_attack, t),
    )


def stats_for_level(defn: MobDefinition, level: int) -> Tuple[int, MobStats]:
    """
    Finds the best matching stats for the given level.
    If the exact level isn't found, it picks the highest available level
    that doesn't exceed the requested level.
    """
    if level in defn.level_stats:
        return level, defn.level_stats[level]

    # Get all defined levels and sort them
    available_levels = sorted(defn.level_stats.keys())

    if not available_levels:
        raise ValueError(f"Mob definition '{defn.display_name}' has no level_stats defined.")

    # Find the closest level that is <= requested level
    best_level = available_levels[0]
    for l in available_levels:
        if l <= level:
            best_level = l
        else:
            break

    return best_level, defn.level_stats[best_level]


def spawn_entity(defn: MobDefinition, level: int, instance_name: str | None = None) -> RuntimeEntity:
    lvl, st = stats_for_level(defn, level)
    name = instance_name or f"{defn.display_name} (Lvl {lvl})"

    return RuntimeEntity(
        name=name,
        hp=float(st.hp),
        hp_max=float(st.hp),
        mp=float(st.mp),
        mp_max=float(st.mp),
        STR=float(st.STR),
        AGI=float(st.AGI),
        INT=float(st.INT),
        DEX=float(st.DEX),
        VIT=float(st.VIT),
    )