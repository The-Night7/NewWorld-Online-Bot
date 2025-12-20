import aiosqlite
from typing import Optional, Any, Dict, List, Tuple


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
"""


class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA_SQL)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if not self._conn:
            raise RuntimeError("DB non connectée")
        return self._conn

    # Ajout de la méthode execute_fetchone
    async def execute_fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Exécute une requête SQL et retourne la première ligne du résultat."""
        if not self._conn:
            raise RuntimeError("DB non connectée")
        async with self._conn.execute(query, params) as cursor:
            return await cursor.fetchone()
