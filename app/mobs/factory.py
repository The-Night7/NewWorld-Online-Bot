from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from .types import MobDefinition, MobStats
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
    levels = defn.available_levels()
    if not levels:
        raise ValueError(f"{defn.key}: aucun level_stats")

    lvl = int(level)

    # exact
    if lvl in defn.level_stats:
        return lvl, defn.level_stats[lvl]

    # clamp
    if lvl <= levels[0]:
        l0 = levels[0]
        return l0, defn.level_stats[l0]
    if lvl >= levels[-1]:
        l1 = levels[-1]
        # Correction ici: on utilise directement l1 qui est garanti d'être dans level_stats
        return l1, defn.level_stats[l1]

    # find bounding levels
    lo = max(x for x in levels if x < lvl)
    hi = min(x for x in levels if x > lvl)
    return lvl, _interpolate_stats(lo, defn.level_stats[lo], hi, defn.level_stats[hi], lvl)


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