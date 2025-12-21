import discord
import logging
from discord.ext import commands
from discord import app_commands

from app.config import load_config
from app.db import Database
from app.cogs.core import CoreCog
from app.cogs.combat import CombatCog
from app.cogs.mobs import MobsCog
from app.cogs.combat_session import CombatSessionCog
from app.mobs.registry import discover_and_register
from app.items import initialize_basic_items

# Ajoutez ces imports en haut du fichier
import traceback
import sys

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bofuri.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('bofuri')

class BofuriBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Enable message content intent for command prefix
        super().__init__(command_prefix="!", intents=intents)
        self.config = load_config()
        self.db = Database(self.config.DB_PATH)

        # Ajouter un gestionnaire d'erreurs pour les commandes slash
        self.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        error_msg = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        logger.error(f"Erreur lors de l'exécution de la commande {interaction.command.name}: {error_msg}")

        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"Une erreur est survenue lors de l'exécution de la commande. L'erreur a été enregistrée.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Une erreur est survenue lors de l'exécution de la commande. L'erreur a été enregistrée.", ephemeral=True)
        except:
            logger.error("Impossible d'envoyer un message d'erreur à l'utilisateur")

    async def setup_hook(self) -> None:
        logger.info("Configuration du bot en cours...")
        await self.db.connect()

        logger.info("Initialisation des objets de base...")
        await initialize_basic_items(self.db)

        logger.info("Découverte et enregistrement des mobs...")
        discover_and_register("app.mobs")

        logger.info("Ajout des cogs...")
        await self.add_cog(CoreCog(self))
        await self.add_cog(CombatCog(self))
        await self.add_cog(MobsCog(self))
        await self.add_cog(CombatSessionCog(self))

        # Charger le nouveau Cog pour les personnages
        from app.cogs.character import CharacterCog
        await self.add_cog(CharacterCog(self))

        from app.cogs.debug import DebugCog
        await self.add_cog(DebugCog(self))

        # Sync global ou guild (guild = plus rapide en dev)
        if self.config.GUILD_ID:
            logger.info(f"Synchronisation des commandes pour la guild {self.config.GUILD_ID}...")
            guild = discord.Object(id=self.config.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            logger.info("Synchronisation globale des commandes...")
            await self.tree.sync()

        logger.info("Bot configuré avec succès!")

    async def close(self) -> None:
        logger.info("Fermeture du bot...")
        await self.db.close()
        await super().close()


def create_bot() -> BofuriBot:
    return BofuriBot()
