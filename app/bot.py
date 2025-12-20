import discord
from discord.ext import commands

from app.config import load_config  # Changed from "from config import load_config"
from app.db import Database  # Changed from "from db import Database"
from app.cogs.core import CoreCog  # Changed from "from cogs.core import CoreCog"
from app.cogs.combat import CombatCog  # Changed from "from cogs.combat import CombatCog"
from app.cogs.mobs import MobsCog  # Changed from "from cogs.mobs import MobsCog"
from app.cogs.combat_session import CombatSessionCog  # Changed from "from cogs.combat_session import CombatSessionCog"
from app.mobs.registry import discover_and_register  # Changed from "from mobs.registry import discover_and_register"

class BofuriBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.config = load_config()
        self.db = Database(self.config.DB_PATH)

    async def setup_hook(self) -> None:
        await self.db.connect()

        discover_and_register("app.mobs")

        await self.add_cog(CoreCog(self))
        await self.add_cog(CombatCog(self))
        await self.add_cog(MobsCog(self))
        await self.add_cog(CombatSessionCog(self))

        # Sync global ou guild (guild = plus rapide en dev)
        if self.config.GUILD_ID:
            guild = discord.Object(id=self.config.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def close(self) -> None:
        await self.db.close()
        await super().close()


def create_bot() -> BofuriBot:
    return BofuriBot()
