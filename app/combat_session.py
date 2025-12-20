from __future__ import annotations

from typing import Iterable, Optional

import logging

class CombatError(RuntimeError):
    pass


async def combat_is_active(db, channel_id: int) -> bool:
    logger = logging.getLogger('bofuri.combat')
    logger.info(f"Vérification du combat actif dans le salon {channel_id}")

    try:
        row = await db.execute_fetchone(
            "SELECT status FROM combats WHERE channel_id = ?",
            (int(channel_id),),
        )

        logger.info(f"Résultat de la requête: {row}")
        result = bool(row and row["status"] == "active")
        logger.info(f"Combat actif: {result}")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du combat actif: {str(e)}", exc_info=True)
        return False


async def combat_get_thread_id(db, channel_id: int) -> Optional[int]:
    row = await db.execute_fetchone(
        "SELECT thread_id FROM combats WHERE channel_id = ? AND status = 'active'",
        (int(channel_id),),
    )
    return int(row["thread_id"]) if row and row["thread_id"] else None


async def combat_create(db, channel_id: int, created_by: int) -> None:
    channel_id = int(channel_id)  # Conversion explicite en entier
    created_by = int(created_by)  # Conversion explicite en entier

    if await combat_is_active(db, channel_id):
        raise CombatError("Un combat est déjà actif dans ce salon.")

    await db.conn.execute(
        "INSERT INTO combats(channel_id, status, created_by) VALUES(?, 'active', ?)",
        (channel_id, created_by),
    )
    await db.conn.commit()


async def combat_set_thread(db, channel_id: int, thread_id: int) -> None:
    await db.conn.execute(
        "UPDATE combats SET thread_id = ? WHERE channel_id = ? AND status = 'active'",
        (int(thread_id), int(channel_id)),
    )
    await db.conn.commit()


async def combat_close(db, channel_id: int) -> None:
    await db.conn.execute(
        "UPDATE combats SET status = 'closed', closed_at = CURRENT_TIMESTAMP WHERE channel_id = ? AND status = 'active'",
        (int(channel_id),),
    )
    await db.conn.commit()


async def participants_add(db, channel_id: int, user_id: int, added_by: int) -> None:
    await db.conn.execute(
        """
        INSERT INTO combat_participants(channel_id, user_id, added_by)
        VALUES(?, ?, ?)
        ON CONFLICT(channel_id, user_id) DO NOTHING
        """,
        (int(channel_id), int(user_id), int(added_by)),
    )
    await db.conn.commit()


async def participants_list(db, channel_id: int) -> list[int]:
    rows = await db.execute_fetchall(
        "SELECT user_id FROM combat_participants WHERE channel_id = ?",
        (int(channel_id),),
    )
    return [int(r["user_id"]) for r in rows]


async def log_add(db, channel_id: int, kind: str, message: str) -> None:
    await db.conn.execute(
        "INSERT INTO combat_logs(channel_id, kind, message) VALUES(?, ?, ?)",
        (int(channel_id), str(kind), str(message)),
    )
    await db.conn.commit()
