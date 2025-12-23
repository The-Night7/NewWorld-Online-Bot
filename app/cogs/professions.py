
import discord
from discord import app_commands
from discord.ext import commands
import random
import math
from ..character import get_character, add_item_to_inventory
from ..dice import d100

class ProfessionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_quality(self, roll: int) -> str:
        if roll >= 100: return "✨ Qualité supérieure"
        if roll > 95: return "💎 Haute qualité"
        if roll > 85: return "🌟 Bonne qualité"
        if roll >= 25: return "📦 Qualité standard"
        return "❌ Échec"

    @app_commands.command(name="craft", description="Réaliser un craft (Forge, Alchimie, Renforcement, Enchantement)")
    @app_commands.describe(
        metier="Le métier utilisé",
        item_name="Nom de l'objet que vous tentez de fabriquer"
    )
    @app_commands.choices(metier=[
        app_commands.Choice(name="Forge (DEX)", value="forge"),
        app_commands.Choice(name="Alchimie (DEX)", value="alchimie"),
        app_commands.Choice(name="Renforcement (DEX)", value="renforcement"),
        app_commands.Choice(name="Enchantement (INT)", value="enchantement"),
    ])
    async def craft(self, interaction: discord.Interaction, metier: str, item_name: str):
        await interaction.response.defer()
        char = await get_character(self.bot.db, interaction.user.id)
        if not char:
            return await interaction.followup.send("Vous n'avez pas de personnage. Utilisez /profile d'abord.")

        # Calcul du bonus selon la stat
        stat_val = char.INT if metier == "enchantement" else char.DEX
        base_roll = d100()
        bonus = math.floor(stat_val / 10)
        total = base_roll + bonus
        
        quality = self.get_quality(total)
        color = discord.Color.gold() if total >= 25 else discord.Color.red()

        embed = discord.Embed(title=f"🛠️ Artisanat : {metier.capitalize()}", color=color)
        embed.add_field(name="Objet", value=item_name, inline=False)
        embed.add_field(name="Jet de dé", value=f"{base_roll} (+{bonus} bonus)", inline=True)
        embed.add_field(name="Total", value=str(total), inline=True)
        embed.add_field(name="Résultat", value=f"**{quality}**", inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="recolte", description="Récolter des ressources selon le lieu")
    @app_commands.choices(lieu=[
        app_commands.Choice(name="Lac de Crystal (Coquillages)", value="lac_coquillages"),
        app_commands.Choice(name="Lac de Crystal (Pêche)", value="lac_peche"),
        app_commands.Choice(name="Lac de Crystal (Sirène - Rare)", value="lac_sirene"),
        app_commands.Choice(name="Forêt (Plantes)", value="foret_plantes"),
        app_commands.Choice(name="Grotte (Minage)", value="grotte_minage"),
    ])
    async def recolte(self, interaction: discord.Interaction, lieu: str):
        await interaction.response.defer()
        char = await get_character(self.bot.db, interaction.user.id)
        if not char:
            return await interaction.followup.send("Personnage introuvable.")

        embed = discord.Embed(title="🌿 Récolte de ressources", color=discord.Color.green())
        result_text = ""

        if lieu == "lac_coquillages":
            # Étape A
            if d100() >= 80:
                # Étape B
                roll_b = d100()
                if roll_b <= 20:
                    qty = random.randint(1, 20)
                    result_text = f"🐚 Trouvé **{qty}x Coquillage rare** !"
                else:
                    qty = random.randint(80, 100)
                    result_text = f"🐚 Trouvé **{qty}x Coquillage commun** !"
            else:
                result_text = "Désolé, vous n'avez rien trouvé dans le sable."

        elif lieu == "lac_peche":
            if d100() <= 30:
                result_text = "🐟 Glouglou ! Vous avez pêché **1x Poisson-chat** !"
            else:
                result_text = "Le poisson a mangé l'appât et s'est enfui..."

        elif lieu == "lac_sirene":
            # Règle A : Seuil DEX
            success_threshold = 98 if char.DEX >= 30 else 100
            roll = d100()
            if roll >= success_threshold:
                result_text = "🧜‍♀️ Incroyable ! Vous avez trouvé le **Pendentif de la sirène amoureuse** !"
            else:
                result_text = "Rien d'inhabituel à la surface de l'eau."

        elif lieu == "foret_plantes":
            roll = d100()
            if roll <= 50: result_text = "🌿 Récolté : **Plante médicinale de soin**"
            elif roll <= 80: result_text = "🧪 Récolté : **Plante anti-poison**"
            elif roll <= 97: result_text = "⚡ Récolté : **Plante anti-paralysie**"
            else: result_text = "✨ Récolté : **Plante de la vie** (Anti-malédiction)"

        elif lieu == "grotte_minage":
            roll = d100()
            if roll <= 30: result_text = "🪨 Miné : **Minerai de roche**"
            elif roll <= 50: result_text = "🟠 Miné : **Minerai de cuivre**"
            elif roll <= 80: result_text = "💎 Miné : **Pierre de mana**"
            elif roll <= 97: result_text = "🔮 Miné : **Cristal aléatoire**"
            else: result_text = "🌌 Miné : **Cristal épique** !"

        embed.description = result_text
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfessionsCog(bot))
