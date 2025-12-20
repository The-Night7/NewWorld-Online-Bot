import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    DISCORD_TOKEN: str
    GUILD_ID: int
    DB_PATH: str


def load_config() -> Config:
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise RuntimeError("DISCORD_TOKEN manquant (voir .env.example)")

    guild_id = int(os.getenv("GUILD_ID", "0"))
    db_path = os.getenv("DB_PATH", "./bofuri.sqlite3")

    return Config(DISCORD_TOKEN=token, GUILD_ID=guild_id, DB_PATH=db_path)
