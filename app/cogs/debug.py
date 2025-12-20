from discord import app_commands
from discord.ext import commands

class DebugCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="debug_combat", description="Affiche les informations de débogage sur les combats")
    async def debug_combat(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Vérifier la structure de la table
        structure = await self.bot.db.execute_fetchall(
            "PRAGMA table_info(combats)"
        )
        structure_info = "\n".join([f"- {col['name']} ({col['type']})" for col in structure])
        
        # Vérifier les données dans la table
        combats = await self.bot.db.execute_fetchall(
            "SELECT * FROM combats WHERE channel_id = ?",
            (interaction.channel_id,)
        )
        
        combats_info = "Aucun combat trouvé pour ce salon."
        if combats:
            combats_info = "\n".join([
                f"ID: {c['id']}, Channel: {c['channel_id']}, Status: {c['status']}, "
                f"Created by: {c['created_by']}, Thread: {c['thread_id'] or 'None'}"
                for c in combats
            ])
        
        # Vérifier spécifiquement si un combat actif existe
        active = await self.bot.db.execute_fetchone(
            "SELECT * FROM combats WHERE channel_id = ? AND status = 'active'",
            (interaction.channel_id,)
        )
        active_info = "Aucun combat actif trouvé selon la requête directe."
        if active:
            active_info = f"Combat actif trouvé: ID {active['id']}, Status {active['status']}"
        
        await interaction.followup.send(
            f"## Structure de la table combats\n{structure_info}\n\n"
            f"## Combats dans ce salon\n{combats_info}\n\n"
            f"## Vérification directe\n{active_info}"
        )