from __future__ import annotations

from typing import Iterable, Optional


class CombatError(RuntimeError):
    pass


async def combat_is_active(conn, channel_id: int) -> bool:
    row = await conn.execute_fetchone(
        "SELECT status FROM combats WHERE channel_id = ?",
        (int(channel_id),),
    )
    return bool(row and row["status"] == "active")


async def combat_get_thread_id(conn, channel_id: int) -> Optional[int]:
    row = await conn.execute_fetchone(
        "SELECT thread_id FROM combats WHERE channel_id = ? AND status = 'active'",
        (int(channel_id),),
    )
    return int(row["thread_id"]) if row and row["thread_id"] else None


async def combat_create(conn, channel_id: int, created_by: int) -> None:
    if await combat_is_active(conn, channel_id):
        raise CombatError("Un combat est déjà actif dans ce salon.")

    await conn.execute(
        "INSERT INTO combats(channel_id, status, created_by) VALUES(?, 'active', ?)",
        (int(channel_id), int(created_by)),
    )
    await conn.commit()


async def combat_set_thread(conn, channel_id: int, thread_id: int) -> None:
    await conn.execute(
        "UPDATE combats SET thread_id = ? WHERE channel_id = ? AND status = 'active'",
        (int(thread_id), int(channel_id)),
    )
    await conn.commit()


async def combat_close(conn, channel_id: int) -> None:
    await conn.execute(
        "UPDATE combats SET status = 'closed', closed_at = CURRENT_TIMESTAMP WHERE channel_id = ? AND status = 'active'",
        (int(channel_id),),
    )
    await conn.commit()


async def participants_add(conn, channel_id: int, user_id: int, added_by: int) -> None:
    await conn.execute(
        """
        INSERT INTO combat_participants(channel_id, user_id, added_by)
        VALUES(?, ?, ?)
        ON CONFLICT(channel_id, user_id) DO NOTHING
        """,
        (int(channel_id), int(user_id), int(added_by)),
    )
    await conn.commit()


async def participants_list(conn, channel_id: int) -> list[int]:
    rows = await conn.execute_fetchall(
        "SELECT user_id FROM combat_participants WHERE channel_id = ?",
        (int(channel_id),),
    )
    return [int(r["user_id"]) for r in rows]


async def log_add(conn, channel_id: int, kind: str, message: str) -> None:
    await conn.execute(
        "INSERT INTO combat_logs(channel_id, kind, message) VALUES(?, ?, ?)",
        (int(channel_id), str(kind), str(message)),
    )
    await conn.commit()
