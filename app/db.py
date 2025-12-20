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

-- Suppression de l'ancienne table combats pour recréer avec la nouvelle contrainte
DROP TABLE IF EXISTS combats;

-- Création de la table combats avec la nouvelle contrainte
CREATE TABLE IF NOT EXISTS combats (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id  INTEGER NOT NULL,
  thread_id   INTEGER,
  status      TEXT NOT NULL,
  created_by  INTEGER NOT NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  closed_at   TIMESTAMP,
  UNIQUE(thread_id, status)
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

CREATE TABLE IF NOT EXISTS combat_mobs (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id  INTEGER NOT NULL,
  mob_name    TEXT NOT NULL,
  mob_key     TEXT NOT NULL,
  level       INTEGER NOT NULL,
  hp          REAL NOT NULL,
  hp_max      REAL NOT NULL,
  mp          REAL NOT NULL,
  mp_max      REAL NOT NULL,
  str         REAL NOT NULL,
  agi         REAL NOT NULL,
  int_        REAL NOT NULL,
  dex         REAL NOT NULL,
  vit         REAL NOT NULL,
  created_by  INTEGER NOT NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(channel_id, mob_name)
);
"""

class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row

        # Exécuter le script de schéma
        try:
            await self._conn.executescript(SCHEMA_SQL)
            await self._conn.commit()
            logger.info("Base de données initialisée avec succès")

            # Vérifier que les tables ont été créées
            tables = ["players", "combats", "combat_participants", "combat_logs", "combat_mobs"]
            for table in tables:
                async with self._conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'") as cursor:
                    if not await cursor.fetchone():
                        logger.error(f"La table {table} n'a pas été créée correctement")
                    else:
                        logger.info(f"Table {table} créée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}", exc_info=True)
            raise

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if not self._conn:
            raise RuntimeError("DB non connectée")
        return self._conn

    async def execute_fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Exécute une requête SQL et retourne la première ligne du résultat."""
        if not self._conn:
            raise RuntimeError("DB non connectée")
        async with self._conn.execute(query, params) as cursor:
            return await cursor.fetchone()

    async def execute_fetchall(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Exécute une requête SQL et retourne toutes les lignes du résultat."""
        if not self._conn:
            raise RuntimeError("DB non connectée")
        async with self._conn.execute(query, params) as cursor:
            return await cursor.fetchall()

    async def check_tables(self) -> bool:
        """Vérifie que toutes les tables nécessaires existent dans la base de données."""
        tables = ["players", "combats", "combat_participants", "combat_logs", "combat_mobs"]
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