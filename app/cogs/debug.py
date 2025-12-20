from discord import app_commands
from discord.ext import commands
import discord
import logging

class DebugCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="debug_combats", description="Affiche les informations de débogage sur les combats")
    async def debug_combats(self, interaction: discord.Interaction):
        logger = logging.getLogger('bofuri.debug')

        try:
            await interaction.response.defer(ephemeral=True)

            # Récupérer tous les combats pour ce canal
        combats = await self.bot.db.execute_fetchall(
            "SELECT * FROM combats WHERE channel_id = ?",
            (interaction.channel_id,)
        )
        
            if not combats:
                await interaction.followup.send("Aucun combat trouvé pour ce salon.")
                return

            # Formater les résultats
            lines = []
            for c in combats:
                lines.append(f"ID: {c['id']}, Status: {c['status']}, Thread: {c['thread_id'] or 'None'}, "
                            f"Created by: {c['created_by']}, Created at: {c['created_at']}, "
                            f"Closed at: {c['closed_at'] or 'None'}")

            await interaction.followup.send("## Combats dans ce salon\n" + "\n".join(lines))

            # Vérifier s'il y a des combats actifs
        active = await self.bot.db.execute_fetchone(
                "SELECT COUNT(*) as count FROM combats WHERE channel_id = ? AND status = 'active'",
            (interaction.channel_id,)
        )

            await interaction.followup.send(f"Nombre de combats actifs: {active['count']}")

        except Exception as e:
            logger.error(f"Erreur dans /debug_combats: {str(e)}", exc_info=True)
            await interaction.followup.send(f"Une erreur est survenue: {str(e)}")

    @app_commands.command(name="fix_combats", description="Corrige les problèmes de combats dans ce salon")
    async def fix_combats(self, interaction: discord.Interaction):
        logger = logging.getLogger('bofuri.debug')

        try:
            await interaction.response.defer(ephemeral=True)

            # Fermer tous les combats actifs dans ce salon
            await self.bot.db.conn.execute(
                "UPDATE combats SET status = 'closed', closed_at = CURRENT_TIMESTAMP "
                "WHERE channel_id = ? AND status = 'active'",
                (interaction.channel_id,)
        )
            await self.bot.db.conn.commit()

            await interaction.followup.send("Tous les combats actifs ont été fermés dans ce salon.")

        except Exception as e:
            logger.error(f"Erreur dans /fix_combats: {str(e)}", exc_info=True)
            await interaction.followup.send(f"Une erreur est survenue: {str(e)}")
