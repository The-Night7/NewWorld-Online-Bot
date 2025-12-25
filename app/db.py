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

CREATE TABLE IF NOT EXISTS items (
  item_id     TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT NOT NULL,
  type        TEXT NOT NULL,
  rarity      TEXT NOT NULL,
  value       INTEGER NOT NULL,
  properties  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS characters (
  user_id      INTEGER PRIMARY KEY,
  name         TEXT NOT NULL,
  level        INTEGER DEFAULT 1,
  xp           INTEGER DEFAULT 0,
  xp_next      INTEGER DEFAULT 100,
  hp           REAL NOT NULL,
  hp_max       REAL NOT NULL,
  mp           REAL NOT NULL,
  mp_max       REAL NOT NULL,
  STR          REAL NOT NULL,
  AGI          REAL NOT NULL,
  INT          REAL NOT NULL,
  DEX          REAL NOT NULL,
  VIT          REAL NOT NULL,
  gold         INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS inventories (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  character_id INTEGER NOT NULL,
  item_id      TEXT NOT NULL,
  quantity     INTEGER DEFAULT 1,
  equipped     INTEGER DEFAULT 0,
  properties   TEXT,
  FOREIGN KEY(character_id) REFERENCES characters(user_id)
);

CREATE TABLE IF NOT EXISTS character_skills (
  user_id INTEGER NOT NULL,
  skill_id TEXT NOT NULL,
  acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, skill_id),
  FOREIGN KEY(user_id) REFERENCES characters(user_id)
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

    async def execute(self, query: str, params: Tuple = ()) -> aiosqlite.Cursor:
        """Helper to execute a query directly via the Database object."""
        if not self._conn:
            raise RuntimeError("DB non connectée")
        return await self._conn.execute(query, params)

    async def commit(self) -> None:
        """Helper to commit changes."""
        if self._conn:
            await self._conn.commit()

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