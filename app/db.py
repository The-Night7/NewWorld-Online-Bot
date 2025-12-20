import aiosqlite
import logging
from typing import Optional, Any, Dict, List, Tuple

logger = logging.getLogger('bofuri.db')

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS players (
  user_id     INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  hp          REAL NOT NULL,
  hp_max      REAL NOT NULL,
  mp          REAL NOT NULL,
  mp_max      REAL NOT NULL,
  str         REAL NOT NULL,
  agi         REAL NOT NULL,
  int_        REAL NOT NULL,
  dex         REAL NOT NULL,
  vit         REAL NOT NULL
);

-- Ajout des tables manquantes
CREATE TABLE IF NOT EXISTS combats (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id  INTEGER NOT NULL,
  thread_id   INTEGER,
  status      TEXT NOT NULL,
  created_by  INTEGER NOT NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  closed_at   TIMESTAMP,
  UNIQUE(channel_id, status)
);

CREATE TABLE IF NOT EXISTS combat_participants (
  channel_id  INTEGER NOT NULL,
  user_id     INTEGER NOT NULL,
  added_by    INTEGER NOT NULL,
  added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (channel_id, user_id)
);

CREATE TABLE IF NOT EXISTS combat_logs (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id  INTEGER NOT NULL,
  kind        TEXT NOT NULL,
  message     TEXT NOT NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mobs (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id  INTEGER NOT NULL,
  mob_name    TEXT NOT NULL,
  mob_key     TEXT NOT NULL,
  level       INTEGER NOT NULL,
  hp          REAL NOT NULL,
  hp_max      REAL NOT NULL,
  created_by  INTEGER NOT NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(channel_id, mob_name)
);
"""


# Étendre la classe Connection pour ajouter execute_fetchone
class ExtendedConnection(aiosqlite.Connection):
    async def execute_fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Exécute une requête SQL et retourne la première ligne du résultat."""
        async with self.execute(query, params) as cursor:
            return await cursor.fetchone()


class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn: Optional[ExtendedConnection] = None

    async def connect(self) -> None:
        # Utiliser factory=ExtendedConnection pour créer une instance de notre classe étendue
        self._conn = await aiosqlite.connect(self.path, factory=ExtendedConnection)
        self._conn.row_factory = aiosqlite.Row

        # Exécuter le script de schéma
        try:
            await self._conn.executescript(SCHEMA_SQL)
            await self._conn.commit()
            logger.info("Base de données initialisée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
            raise

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> ExtendedConnection:
        if not self._conn:
            raise RuntimeError("DB non connectée")
        return self._conn

    async def check_tables(self) -> bool:
        """Vérifie que toutes les tables nécessaires existent dans la base de données."""
        tables = ["players", "combats", "combat_participants", "combat_logs", "mobs"]
        missing_tables = []

        for table in tables:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            async with self._conn.execute(query, (table,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    missing_tables.append(table)

        if missing_tables:
            logger.error(f"Tables manquantes dans la base de données: {', '.join(missing_tables)}")
            return False

        logger.info("Toutes les tables nécessaires sont présentes dans la base de données")
        return True