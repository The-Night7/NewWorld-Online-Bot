import discord
from discord import app_commands
from discord.ext import commands
import random
import math
from ..character import get_character, add_item_to_inventory
from ..dice import d100
import json
import os

# Mapping des salons vers les types de ressources
ZONE_PROFESSIONS = {
    1398615884196610088: "harvesting.foret",    # forêt luxuriante
    1398617728474153061: "harvesting.foret",    # forêt sombre
    1398617842064035840: "mining.grotte",       # grotte rocheuse
    1398617763093807184: "harvesting.plaines",  # grandes plaines
    1398617871588003870: "fishing.lac",         # lac de crystal
    1398626100615188530: "harvesting.hante",    # forêt hantée
    1398626193254645820: "harvesting.hante",    # village hanté
    1398626132403687504: "harvesting.hante",    # manoir hanté
    1398632574276075580: "mining.grotte",       # sous-sol
    1398191886589624421: "fishing.lac",         # donjon aquatique
    1398626819296596070: "harvesting.hante",    # domaine du trépassé
    1398193027893432361: "mining.grotte",       # donjon palier grotte
}

class ProfessionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.resources_data = self._load_resources()

    def _load_resources(self):
        path = os.path.join("app", "professions_items.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_quality(self, roll: int) -> str:
        if roll >= 100: return "✨ Qualité supérieure"
        if roll > 95: return "💎 Haute qualité"
        if roll > 85: return "🌟 Bonne qualité"
        if roll >= 25: return "📦 Qualité standard"
        return "❌ Échec"

    @app_commands.command(name="recolte", description="Récolter des ressources automatiquement selon le lieu")
    async def recolte(self, interaction: discord.Interaction):
        """Détecte le lieu et lance la récolte appropriée"""
        await interaction.response.defer()
        
        channel_id = interaction.channel_id
        if channel_id not in ZONE_PROFESSIONS:
            return await interaction.followup.send("Il n'y a rien à récolter ici.", ephemeral=True)

        zone_key = ZONE_PROFESSIONS[channel_id]
        category, subcat = zone_key.split(".")
        
        char = await get_character(self.bot.db, interaction.user.id)
        if not char:
            return await interaction.followup.send("Personnage introuvable. Utilisez /profile.")

        # Logique spécifique pour le Lac de Crystal (Coquillages, Pêche, Pendentif)
        if channel_id == 1398617871588003870:  # Lac de Crystal
            return await self.handle_crystal_lake(interaction, char)

        # Logique générique pour les autres zones (Herboristerie, Minage, etc.)
        available_items = self.resources_data.get(category, {}).get(subcat, [])
        if not available_items:
            return await interaction.followup.send("Erreur: Table de loot vide pour cette zone.")

        char = await get_character(self.bot.db, interaction.user.id)
        if not char:
            return await interaction.followup.send("Personnage introuvable. Utilisez /profile.")

        # Calcul du jet (DEX pour tout, ou INT pour les zones hantées)
        stat_val = char.INT if subcat == "hante" else char.DEX
        bonus = math.floor(stat_val / 10)
        roll = d100()
        total = roll + bonus

        embed = discord.Embed(color=discord.Color.green())
        
        if roll <= 10: # Échec critique sur le dé pur
            await interaction.followup.send("❌ Vous n'avez rien trouvé d'intéressant.")
        else:
            # Sélection de l'item basé sur les chances dans le JSON
            item_pool = sorted(available_items, key=lambda x: x.get('chance', 0))
            
            if not item_pool:
                return await interaction.followup.send("❌ Aucun objet n'est disponible dans cette zone actuellement.")

            rand_chance = random.randint(1, 100)
            current_sum = 0
            selected_item = None
            
            for item in item_pool:
                current_sum += item.get('chance', 0)
                if rand_chance <= current_sum:
                    selected_item = item
                    break
                
            # Fallback if sum logic fails or rand_chance is high
            if not selected_item:
                selected_item = item_pool[-1]
            
            # Safety check for required keys
            if 'id' not in selected_item or 'name' not in selected_item:
                return await interaction.followup.send("❌ Erreur : L'objet trouvé est corrompu.")

            # Ajout à l'inventaire
            from ..character import add_item_to_inventory
            await add_item_to_inventory(self.bot.db, char.user_id, selected_item['id'], 1)
            
            action_name = "Pêche" if category == "fishing" else "Minage" if category == "mining" else "Récolte"
            await interaction.followup.send(f"✨ **{action_name}** : Vous avez obtenu **{selected_item['name']}** !")

    async def handle_crystal_lake(self, interaction: discord.Interaction, char):
        """Gestion spécifique du Lac de Crystal : Coquillages, Pêche et Pendentif"""
        roll_activity = d100()
        
        # 1. Tentative de Drop très rare (Pendentif de la sirène)
        # Règle A : DEX >= 30 (98-100), sinon uniquement 100
        success_threshold = 98 if char.DEX >= 30 else 100
        if roll_activity >= success_threshold:
            await add_item_to_inventory(self.bot.db, char.user_id, "pendentif_sirene", 1)
            return await interaction.followup.send("💖 **INCROYABLE !** Vous avez trouvé le **Pendentif de la sirène amoureuse** !")

        # 2. Choix aléatoire entre Ramassage (Coquillages) et Pêche (Poisson-chat)
        if random.random() < 0.5:
            # --- RAMASSAGE AQUATIQUE ---
            step_a = d100()
            if step_a < 80:
                return await interaction.followup.send("🐚 Vous fouillez le sable... mais ne trouvez aucun coquillage.")
            
            step_b = d100()
            if step_b <= 20: # Rare (1-20)
                qty = random.randint(1, 20)
                item_id, item_name = "coquillage_rare", "Coquillage Rare"
            else: # Commun (21-100)
                qty = min(200, random.randint(80, 100))
                item_id, item_name = "coquillage_commun", "Coquillage"
            
            await add_item_to_inventory(self.bot.db, char.user_id, item_id, qty)
            return await interaction.followup.send(f"🐚 **Ramassage** : Vous avez ramassé **{qty}x {item_name}** !")
        
        else:
            # --- PÊCHE ---
            if roll_activity <= 30:
                await add_item_to_inventory(self.bot.db, char.user_id, "poisson_chat", 1)
                return await interaction.followup.send("🐟 **Pêche** : Un **Poisson-chat** a mordu à l'hameçon !")
            else:
                return await interaction.followup.send("🎣 Rien ne mord... Le lac est calme.")

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

async def setup(bot):
    await bot.add_cog(ProfessionsCog(bot))
