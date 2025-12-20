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


async def combat_get_thread_ids(db, channel_id: int) -> list[int]:
    """Retourne la liste des thread_id de tous les combats actifs dans un salon."""
    rows = await db.execute_fetchall(
        "SELECT thread_id FROM combats WHERE channel_id = ? AND status = 'active' AND thread_id IS NOT NULL",
        (int(channel_id),),
    )
    return [int(row["thread_id"]) for row in rows if row["thread_id"]]


async def combat_get_thread_id(db, channel_id: int) -> Optional[int]:
    """Fonction maintenue pour compatibilité, retourne le premier thread_id trouvé."""
    thread_ids = await combat_get_thread_ids(db, channel_id)
    return thread_ids[0] if thread_ids else None


async def combat_create(db, channel_id: int, created_by: int) -> int:
    channel_id = int(channel_id)  # Conversion explicite en entier
    created_by = int(created_by)  # Conversion explicite en entier

    # Insérer un nouveau combat sans vérification (plusieurs combats autorisés par salon)
    cursor = await db.conn.execute(
        "INSERT INTO combats(channel_id, status, created_by) VALUES(?, 'active', ?)",
        (channel_id, created_by),
    )
    combat_id = cursor.lastrowid
    await db.conn.commit()

    return combat_id

async def combat_set_thread(db, channel_id: int, thread_id: int, combat_id: Optional[int] = None) -> None:
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
    if combat_id is not None:
        # Si un combat_id est fourni, mettre à jour ce combat spécifique
        await db.conn.execute(
            "UPDATE combats SET thread_id = ? WHERE id = ? AND status = 'active'",
            (thread_id, int(combat_id)),
        )
    else:
        # Sinon, utiliser l'ancienne méthode (pour compatibilité)
        # Récupérer d'abord le premier combat actif sans thread_id
        row = await db.execute_fetchone(
            "SELECT id FROM combats WHERE channel_id = ? AND status = 'active' AND thread_id IS NULL",
            (int(channel_id),),
        )

        if row and row["id"]:
            # Mettre à jour ce combat spécifique
            await db.conn.execute(
                "UPDATE combats SET thread_id = ? WHERE id = ?",
                (thread_id, row["id"]),
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
    # Récupérer d'abord le combat_id associé au thread_id
    row = await db.execute_fetchone(
        "SELECT id, channel_id FROM combats WHERE thread_id = ? AND status = 'active'",
        (int(thread_id),),
    )

    if not row:
        raise CombatError("Aucun combat actif trouvé pour ce fil.")

    combat_id = row['id']
    channel_id = row['channel_id']

    # Vérifier si la table a la colonne combat_id
    has_combat_id_column = False
    try:
        table_info = await db.execute_fetchall("PRAGMA table_info(combat_participants)")
        for column in table_info:
            if column["name"] == "combat_id":
                has_combat_id_column = True
                break

        if has_combat_id_column:
            await db.conn.execute(
                """
                INSERT INTO combat_participants(channel_id, user_id, added_by, combat_id)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(combat_id, user_id) DO NOTHING
                """,
                (int(channel_id), int(user_id), int(added_by), combat_id),
            )
        else:
            # Utiliser l'ancienne structure sans combat_id
            await db.conn.execute(
                """
                INSERT INTO combat_participants(channel_id, user_id, added_by)
                VALUES(?, ?, ?)
                ON CONFLICT(channel_id, user_id) DO NOTHING
                """,
                (int(channel_id), int(user_id), int(added_by)),
        )

        await db.conn.commit()
    except Exception as e:
        logger = logging.getLogger('bofuri.combat')
        logger.error(f"Erreur lors de l'ajout du participant: {str(e)}", exc_info=True)
        # Essayer avec l'ancienne structure
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
    # Récupérer d'abord le combat_id associé au thread_id
    row = await db.execute_fetchone(
        "SELECT id, channel_id FROM combats WHERE thread_id = ? AND status = 'active'",
        (int(thread_id),),
    )

    if not row:
        raise CombatError("Aucun combat actif trouvé pour ce fil.")

    combat_id = row['id']
    channel_id = row['channel_id']

    # Vérifier si la table a la colonne combat_id
    has_combat_id_column = False
    try:
        table_info = await db.execute_fetchall("PRAGMA table_info(combat_participants)")
        for column in table_info:
            if column["name"] == "combat_id":
                has_combat_id_column = True
                break

        if has_combat_id_column:
            rows = await db.execute_fetchall(
                "SELECT user_id FROM combat_participants WHERE combat_id = ?",
                (combat_id,),
            )
        else:
            # Utiliser l'ancienne structure sans combat_id
            rows = await db.execute_fetchall(
                "SELECT user_id FROM combat_participants WHERE channel_id = ?",
                (channel_id,),
            )

        return [int(r["user_id"]) for r in rows]
    except Exception as e:
        logger = logging.getLogger('bofuri.combat')
        logger.error(f"Erreur lors de la récupération des participants: {str(e)}", exc_info=True)
        # Essayer avec l'ancienne structure
        rows = await db.execute_fetchall(
            "SELECT user_id FROM combat_participants WHERE channel_id = ?",
            (channel_id,),
        )
        return [int(r["user_id"]) for r in rows]


async def log_add(db, thread_id: int, kind: str, message: str) -> None:
    # Récupérer d'abord le combat_id associé au thread_id
    row = await db.execute_fetchone(
        "SELECT id, channel_id FROM combats WHERE thread_id = ? AND status = 'active'",
        (int(thread_id),),
    )

    if not row:
        raise CombatError("Aucun combat actif trouvé pour ce fil.")

    combat_id = row['id']
    channel_id = row['channel_id']

    # Vérifier si la table a la colonne combat_id
    has_combat_id_column = False
    try:
        table_info = await db.execute_fetchall("PRAGMA table_info(combat_logs)")
        for column in table_info:
            if column["name"] == "combat_id":
                has_combat_id_column = True
                break

        if has_combat_id_column:
            await db.conn.execute(
                "INSERT INTO combat_logs(channel_id, kind, message, combat_id) VALUES(?, ?, ?, ?)",
                (int(channel_id), str(kind), str(message), combat_id),
            )
        else:
            # Utiliser l'ancienne structure sans combat_id
            await db.conn.execute(
                "INSERT INTO combat_logs(channel_id, kind, message) VALUES(?, ?, ?)",
                (int(channel_id), str(kind), str(message)),
            )

        await db.conn.commit()
    except Exception as e:
        logger = logging.getLogger('bofuri.combat')
        logger.error(f"Erreur lors de l'ajout du log: {str(e)}", exc_info=True)
        # Essayer avec l'ancienne structure
        await db.conn.execute(
            "INSERT INTO combat_logs(channel_id, kind, message) VALUES(?, ?, ?)",
            (int(channel_id), str(kind), str(message)),
        )
        await db.conn.commit()
