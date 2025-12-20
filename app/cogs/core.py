import discord
from discord import app_commands
from discord.ext import commands

from ..dice import d20, d100


class CoreCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Lance un dé (combat=d20, metier=d100)")
    @app_commands.describe(mode="combat (d20) ou metier (d100)", bonus="Bonus à ajouter au jet")
    async def roll(self, interaction: discord.Interaction, mode: str, bonus: int = 0):
        mode_l = (mode or "").lower().strip()
        if mode_l not in {"combat", "metier"}:
            await interaction.response.send_message("Mode invalide: utilise `combat` ou `metier`.", ephemeral=True)
            return

        base = d20() if mode_l == "combat" else d100()
        total = base + int(bonus)

        title = "🎲 Jet de combat (d20)" if mode_l == "combat" else "🎲 Jet métier/recherche (d100)"
        embed = discord.Embed(title=title, color=discord.Color.blurple())
        embed.add_field(name="Jet", value=str(base), inline=True)
        embed.add_field(name="Bonus", value=str(bonus), inline=True)
        embed.add_field(name="Total", value=str(total), inline=True)

        await interaction.response.send_message(embed=embed)
