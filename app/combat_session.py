from __future__ import annotations

from typing import Iterable, Optional

import logging

class CombatError(RuntimeError):
    pass


async def combat_is_active(db, thread_id: int) -> bool:
    logger = logging.getLogger('bofuri.combat')
    logger.info(f"Vérification du combat actif dans le fil {thread_id}")

    try:
        row = await db.execute_fetchone(
            "SELECT status FROM combats WHERE thread_id = ?",
            (int(thread_id),),
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

    # La vérification du combat actif sera faite après avoir créé le thread
    # car nous avons besoin du thread_id pour vérifier
    await db.conn.execute(
        "INSERT INTO combats(channel_id, status, created_by) VALUES(?, 'active', ?)",
        (channel_id, created_by),
    )
    await db.conn.commit()


async def combat_set_thread(db, channel_id: int, thread_id: int) -> None:
    # Mise à jour pour inclure le thread_id et vérifier si un combat est déjà actif dans ce fil
    thread_id = int(thread_id)

    # Vérifier si un combat est déjà actif dans ce fil
    row = await db.execute_fetchone(
    "SELECT id FROM combats WHERE thread_id = ? AND status = 'active'",
    (thread_id,),
    )

    if row and row["id"]:
        # Un combat est déjà actif dans ce fil
        raise CombatError("Un combat est déjà actif dans ce fil.")

    # Mettre à jour le combat avec le thread_id
    await db.conn.execute(
    "UPDATE combats SET thread_id = ? WHERE channel_id = ? AND status = 'active'",
    (thread_id, int(channel_id)),
    )
    await db.conn.commit()


async def combat_close(db, thread_id: int) -> None:
    logger = logging.getLogger('bofuri.combat')
    logger.info(f"Tentative de fermeture du combat dans le fil {thread_id}")

    try:
        # Vérifier d'abord si un combat actif existe
        row = await db.execute_fetchone(
            "SELECT id, channel_id FROM combats WHERE thread_id = ? AND status = 'active'",
            (int(thread_id),),
        )

        logger.info(f"Résultat de la requête pour trouver le combat actif: {row}")

        if not row:
            # Aucun combat actif à fermer
            logger.warning(f"Aucun combat actif trouvé dans le fil {thread_id}")
            return

        combat_id = row['id']
        channel_id = row['channel_id']
        logger.info(f"Fermeture du combat ID {combat_id} dans le fil {thread_id} (salon {channel_id})")

        # Vérifier s'il existe déjà un combat fermé pour ce thread
        existing_closed = await db.execute_fetchone(
            "SELECT id FROM combats WHERE thread_id = ? AND status = 'closed'",
            (int(thread_id),),
    )

        if existing_closed:
            logger.warning(f"Un combat fermé existe déjà pour le fil {thread_id}. Suppression de cet enregistrement.")
            # Supprimer l'ancien combat fermé pour éviter le conflit
            await db.conn.execute(
                "DELETE FROM combats WHERE thread_id = ? AND status = 'closed'",
                (int(thread_id),),
            )

        # Mettre à jour le statut du combat existant
        await db.conn.execute(
            "UPDATE combats SET status = 'closed', closed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (combat_id,),
        )
        await db.conn.commit()
        logger.info(f"Combat ID {combat_id} fermé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la fermeture du combat: {str(e)}", exc_info=True)
        raise


async def participants_add(db, thread_id: int, user_id: int, added_by: int) -> None:
    # Récupérer d'abord le channel_id associé au thread_id
    row = await db.execute_fetchone(
        "SELECT channel_id FROM combats WHERE thread_id = ? AND status = 'active'",
        (int(thread_id),),
    )

    if not row:
        raise CombatError("Aucun combat actif trouvé pour ce fil.")

    channel_id = row['channel_id']
    await db.conn.execute(
        """
        INSERT INTO combat_participants(channel_id, user_id, added_by)
        VALUES(?, ?, ?)
        ON CONFLICT(channel_id, user_id) DO NOTHING
        """,
        (int(channel_id), int(user_id), int(added_by)),
    )
    await db.conn.commit()


async def participants_list(db, thread_id: int) -> list[int]:
    # Récupérer d'abord le channel_id associé au thread_id
    row = await db.execute_fetchone(
        "SELECT channel_id FROM combats WHERE thread_id = ? AND status = 'active'",
        (int(thread_id),),
    )

    if not row:
        raise CombatError("Aucun combat actif trouvé pour ce fil.")

    channel_id = row['channel_id']

    rows = await db.execute_fetchall(
        "SELECT user_id FROM combat_participants WHERE channel_id = ?",
        (int(channel_id),),
    )
    return [int(r["user_id"]) for r in rows]


async def log_add(db, thread_id: int, kind: str, message: str) -> None:
    # Récupérer d'abord le channel_id associé au thread_id
    row = await db.execute_fetchone(
        "SELECT channel_id FROM combats WHERE thread_id = ? AND status = 'active'",
        (int(thread_id),),
    )

    if not row:
        raise CombatError("Aucun combat actif trouvé pour ce fil.")

    channel_id = row['channel_id']

    await db.conn.execute(
        "INSERT INTO combat_logs(channel_id, kind, message) VALUES(?, ?, ?)",
        (int(channel_id), str(kind), str(message)),
    )
    await db.conn.commit()