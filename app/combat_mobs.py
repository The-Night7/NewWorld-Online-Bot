from __future__ import annotations

import re
from typing import Optional, Tuple

from .models import RuntimeEntity


_SUFFIX_RE = re.compile(r"^(?P<base>.+?)#(?P<num>\d+)$")


async def next_unique_mob_name(conn, channel_id: int, base_display_name: str) -> str:
    """
    Retourne base_display_name#N avec N = 1 + max(N existant) dans ce salon.
    """
    # On récupère tous les noms commençant par "Base#"
    like = f"{base_display_name}#%"
    rows = await conn.execute_fetchall(
        "SELECT mob_name FROM combat_mobs WHERE channel_id = ? AND mob_name LIKE ?",
        (int(channel_id), like),
    )

    max_n = 0
    for r in rows:
        name = r["mob_name"]
        m = _SUFFIX_RE.match(name)
        if m and m.group("base") == base_display_name:
            max_n = max(max_n, int(m.group("num")))

    return f"{base_display_name}#{max_n + 1}"


async def insert_mob(conn, channel_id: int, mob_name: str, mob_key: str, level: int, ent: RuntimeEntity, created_by: int):
    await conn.execute(
        """
        INSERT INTO combat_mobs(
          channel_id, mob_name, mob_key, level,
          hp, hp_max, mp, mp_max, str, agi, int_, dex, vit,
          created_by
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(channel_id), mob_name, mob_key, int(level),
            float(ent.hp), float(ent.hp_max), float(ent.mp), float(ent.mp_max),
            float(ent.STR), float(ent.AGI), float(ent.INT), float(ent.DEX), float(ent.VIT),
            int(created_by),
        ),
    )
    await conn.commit()


async def fetch_mob_entity(conn, channel_id: int, mob_name: str) -> RuntimeEntity:
    row = await conn.execute_fetchone(
        "SELECT * FROM combat_mobs WHERE channel_id = ? AND mob_name = ?",
        (int(channel_id), str(mob_name)),
    )
    if not row:
        raise ValueError("Mob introuvable dans ce salon. Utilise /mob_list pour voir les noms.")

    return RuntimeEntity(
        name=row["mob_name"],
        hp=float(row["hp"]),
        hp_max=float(row["hp_max"]),
        mp=float(row["mp"]),
        mp_max=float(row["mp_max"]),
        STR=float(row["str"]),
        AGI=float(row["agi"]),
        INT=float(row["int_"]),
        DEX=float(row["dex"]),
        VIT=float(row["vit"]),
    )


async def save_mob_hp(conn, channel_id: int, mob_name: str, hp: float) -> None:
    await conn.execute(
        "UPDATE combat_mobs SET hp = ? WHERE channel_id = ? AND mob_name = ?",
        (float(hp), int(channel_id), str(mob_name)),
    )
    await conn.commit()


async def list_mobs(conn, channel_id: int):
    return await conn.execute_fetchall(
        "SELECT mob_name, mob_key, level, hp, hp_max FROM combat_mobs WHERE channel_id = ? ORDER BY mob_name",
        (int(channel_id),),
    )


async def cleanup_dead_mobs(conn, channel_id: int) -> int:
    cur = await conn.execute(
        "DELETE FROM combat_mobs WHERE channel_id = ? AND hp <= 0",
        (int(channel_id),),
    )
    await conn.commit()
    return cur.rowcount or 0
