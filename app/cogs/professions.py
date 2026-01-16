import discord
from discord import app_commands
from discord.ext import commands
import random
import math
import logging
from typing import Dict, List, Optional, Tuple, Any
from ..character import get_character, add_item_to_inventory
from ..dice import d100
import json
import os

logger = logging.getLogger('bofuri.professions')

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

# Tables de butin pour chaque type de récolte
LOOT_TABLES = {
    "harvesting": {
        "foret": [
            {"range": (1, 50), "item_id": "plante_medicinale", "name": "Plante médicinale de soin", "emoji": "🌿"},
            {"range": (51, 80), "item_id": "plante_antipoison", "name": "Plante anti-poison", "emoji": "🌿"},
            {"range": (81, 97), "item_id": "plante_antiparalysie", "name": "Plante anti-paralysie", "emoji": "🌿"},
            {"range": (98, 100), "item_id": "plante_vie", "name": "Plante de la vie", "emoji": "🌿"}
        ],
        "plaines": [
            {"range": (1, 40), "item_id": "herbe_commune", "name": "Herbe commune", "emoji": "🌾"},
            {"range": (41, 70), "item_id": "fleur_sauvage", "name": "Fleur sauvage", "emoji": "🌼"},
            {"range": (71, 90), "item_id": "champignon", "name": "Champignon", "emoji": "🍄"},
            {"range": (91, 100), "item_id": "baies_rouges", "name": "Baies rouges", "emoji": "🍒"}
        ],
        "hante": [
            {"range": (1, 40), "item_id": "herbe_spectrale", "name": "Herbe spectrale", "emoji": "👻"},
            {"range": (41, 70), "item_id": "champignon_toxique", "name": "Champignon toxique", "emoji": "☠️"},
            {"range": (71, 90), "item_id": "fleur_nocturne", "name": "Fleur nocturne", "emoji": "🌙"},
            {"range": (91, 99), "item_id": "racine_maudite", "name": "Racine maudite", "emoji": "🌑"},
            {"range": (100, 100), "item_id": "coeur_fantome", "name": "Cœur de fantôme", "emoji": "💔"}
        ]
    },
    "mining": {
        "grotte": [
            {"range": (1, 30), "item_id": "minerai_roche", "name": "Minerai de roche", "emoji": "🪨"},
            {"range": (31, 50), "item_id": "minerai_cuivre", "name": "Minerai de cuivre", "emoji": "🧱"},
            {"range": (51, 80), "item_id": "pierre_mana", "name": "Pierre de mana", "emoji": "💎"},
            {"range": (81, 95), "item_id": "minerai_fer", "name": "Minerai de fer", "emoji": "⚙️"},
            {"range": (96, 100), "item_id": "minerai_or", "name": "Minerai d'or", "emoji": "✨"}
        ]
    },
    "fishing": {
        "lac": [
            {"range": (1, 30), "item_id": "poisson_commun", "name": "Poisson commun", "emoji": "🐟"},
            {"range": (31, 50), "item_id": "vieille_botte", "name": "Vieille botte", "emoji": "👢"},
            {"range": (51, 80), "item_id": "saumon_dore", "name": "Saumon doré", "emoji": "🐠"},
            {"range": (81, 95), "item_id": "coffre_tresor", "name": "Coffre au trésor", "emoji": "🧰"},
            {"range": (96, 99), "item_id": "poisson_rare", "name": "Poisson rare", "emoji": "🐡"},
            {"range": (100, 100), "item_id": "monstre_marin", "name": "Monstre marin", "emoji": "🐙", "special": "combat"}
        ]
    }
}

class ProfessionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.resources_data = self._load_resources()

    def _load_resources(self) -> Dict:
        """Charge les données des ressources depuis le fichier JSON"""
        path = os.path.join("app", "professions_items.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_quality(self, roll: int) -> str:
        """Détermine la qualité d'un craft en fonction du jet de dé"""
        if roll >= 100: return "✨ Qualité supérieure"
        if roll > 95: return "💎 Haute qualité"
        if roll > 85: return "🌟 Bonne qualité"
        if roll >= 25: return "📦 Qualité standard"
        return "❌ Échec"

    def get_loot_from_table(self, category: str, subcategory: str, roll: int) -> Optional[Dict[str, Any]]:
        """Récupère un item de butin depuis les tables prédéfinies en fonction du jet de dé"""
        if category not in LOOT_TABLES or subcategory not in LOOT_TABLES[category]:
            return None
            
        table = LOOT_TABLES[category][subcategory]
        for item in table:
            min_val, max_val = item["range"]
            if min_val <= roll <= max_val:
                return item
                
        return None

    @app_commands.command(name="recolte", description="Récolter des ressources selon le lieu (Quantité basée sur la DEX)")
    async def recolte(self, interaction: discord.Interaction):
        """Détecte le lieu et lance la récolte appropriée"""
        await interaction.response.defer()
        
        channel_id = interaction.channel_id
        zone_key = ZONE_PROFESSIONS.get(channel_id)
        
        if not zone_key or "." not in zone_key:
            return await interaction.followup.send("Il n'y a rien à récolter ici.", ephemeral=True)

        category, subcategory = zone_key.split(".", 1)
        
        char = await get_character(self.bot.db, interaction.user.id)
        if not char:
            return await interaction.followup.send("Personnage introuvable. Utilisez /profile.")

        # Logique spécifique pour le Lac de Crystal (Coquillages, Pêche, Pendentif)
        if channel_id == 1398617871588003870:  # Lac de Crystal
            return await self.handle_crystal_lake(interaction, char)

        # Calcul du jet (DEX pour tout, ou INT pour les zones hantées)
        stat_val = char.INT if subcategory == "hante" else char.DEX
        bonus = math.floor(stat_val / 10)
        base_roll = d100()
        total = base_roll + bonus

        # Calcul de la quantité selon la DEX (1 + bonus)
        # Pour la pêche, on garde 1 par défaut (sauf cas spéciaux)
        quantity = 1
        if category != "fishing":  # Pas de bonus de quantité pour la pêche standard
            quantity = 1 + bonus

        # Récupération de l'item depuis la table de butin
        loot_item = self.get_loot_from_table(category, subcategory, base_roll)
        
        if not loot_item:
            # Fallback sur les anciennes tables si la nouvelle table n'est pas disponible
            available_items = self.resources_data.get(category, {}).get(subcategory, [])
            if not available_items:
                return await interaction.followup.send("❌ Vous ne trouvez rien d'intéressant cette fois-ci...", ephemeral=True)
                
            # Sélection de l'item basé sur les chances dans le JSON
            item_pool = sorted(available_items, key=lambda x: x.get('chance', 0))
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
                selected_item = item_pool[-1] if item_pool else None
                
            if not selected_item or 'id' not in selected_item or 'name' not in selected_item:
                return await interaction.followup.send("❌ Vous ne trouvez rien d'intéressant cette fois-ci...", ephemeral=True)
                
            # Ajout à l'inventaire (avec quantité basée sur DEX)
            await add_item_to_inventory(self.bot.db, char.user_id, selected_item['id'], quantity)
            
            action_name = "Pêche" if category == "fishing" else "Minage" if category == "mining" else "Récolte"
            
            # Message avec info sur la quantité
            qty_text = f"**{quantity}x {selected_item['name']}**"
            if quantity > 1:
                qty_text += f" *(Base: 1 + Bonus {stat_name}: {bonus})*"
                
            return await interaction.followup.send(f"✨ **{action_name}** : Vous avez obtenu {qty_text} !")
        
        # Traitement des cas spéciaux
        if loot_item.get("special") == "combat":
            # Déclencher un combat contre un monstre marin
            await interaction.followup.send(
                f"{loot_item['emoji']} **{base_roll}/100** ! Oh non ! Vous avez pêché un **{loot_item['name']}** !\n"
                "Préparez-vous au combat !"
            )
            # Ici on pourrait déclencher un combat automatiquement
            return
            
        # Ajout de l'item à l'inventaire (avec quantité basée sur DEX)
        await add_item_to_inventory(self.bot.db, char.user_id, loot_item["item_id"], quantity)
        
        # Création de l'embed de réponse
        color = discord.Color.green()
        if base_roll > 80:
            color = discord.Color.blue()
        if base_roll > 95:
            color = discord.Color.gold()
            
        embed = discord.Embed(title=f"{loot_item['emoji']} Récolte réussie !", color=color)
        embed.add_field(name="Jet de dé", value=f"🎲 **{base_roll}**/100 (+{bonus} bonus)", inline=True)
        embed.add_field(name="Total", value=str(total), inline=True)
        
        # Affichage détaillé du butin avec quantité
        qty_text = f"**{quantity}x {loot_item['name']}**"
        stat_name = "INT" if subcategory == "hante" else "DEX"
        
        # Explication du calcul de quantité si > 1
        if quantity > 1:
            qty_text += f"\n*(Base: 1 + Bonus {stat_name}: {bonus})*"
            
        embed.add_field(name="Butin", value=qty_text, inline=False)
        
        profession_name = "Pêche" if category == "fishing" else "Minage" if category == "mining" else "Herboristerie"
        embed.set_footer(text=f"{profession_name} | {stat_name}: {stat_val}")
        
        await interaction.followup.send(embed=embed)

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
                # Pour les coquillages rares, on applique le bonus de DEX
                base_qty = random.randint(1, 5)
                bonus = math.floor(char.DEX / 10)
                qty = base_qty + bonus
                item_id, item_name = "coquillage_rare", "Coquillage Rare"
                
                # Message avec explication du bonus
                qty_text = f"**{qty}x {item_name}**"
                if bonus > 0:
                    qty_text += f" *(Base: {base_qty} + Bonus DEX: {bonus})*"
                
                await add_item_to_inventory(self.bot.db, char.user_id, item_id, qty)
                return await interaction.followup.send(f"🐚 **Ramassage** : Vous avez ramassé {qty_text} !")
            else: # Commun (21-100)
                # Pour les coquillages communs, on garde la logique existante
                base_qty = random.randint(80, 100)
                qty = min(200, base_qty + (char.DEX // 5))  # Bonus plus important pour les communs
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

    @app_commands.command(name="peche", description="Pêcher dans un point d'eau")
    async def peche(self, interaction: discord.Interaction):
        """Commande dédiée à la pêche"""
        await interaction.response.defer()
        
        channel_id = interaction.channel_id
        zone_key = ZONE_PROFESSIONS.get(channel_id)
        
        if not zone_key or not zone_key.startswith("fishing"):
            return await interaction.followup.send("Il n'y a pas d'eau où pêcher ici.", ephemeral=True)
        
        char = await get_character(self.bot.db, interaction.user.id)
        if not char:
            return await interaction.followup.send("Personnage introuvable. Utilisez /profile.")
        
        # Cas spécial du Lac de Crystal
        if channel_id == 1398617871588003870:  # Lac de Crystal
            roll_activity = d100()
            
            # Tentative de Drop très rare (Pendentif de la sirène)
            success_threshold = 98 if char.DEX >= 30 else 100
            if roll_activity >= success_threshold:
                await add_item_to_inventory(self.bot.db, char.user_id, "pendentif_sirene", 1)
                return await interaction.followup.send("💖 **INCROYABLE !** Vous avez pêché le **Pendentif de la sirène amoureuse** !")
            
            # Pêche normale
            if roll_activity <= 30:
                await add_item_to_inventory(self.bot.db, char.user_id, "poisson_chat", 1)
                return await interaction.followup.send("🐟 **Pêche** : Un **Poisson-chat** a mordu à l'hameçon !")
            else:
                return await interaction.followup.send("🎣 Rien ne mord... Le lac est calme.")
        
        # Pêche standard dans les autres zones
        _, subcategory = zone_key.split(".", 1)
        
        # Bonus de DEX
        bonus = math.floor(char.DEX / 10)
        base_roll = d100()
        total = base_roll + bonus
        
        loot_item = self.get_loot_from_table("fishing", subcategory, base_roll)
        
        if not loot_item:
            return await interaction.followup.send("🎣 Vous n'avez rien attrapé cette fois-ci...", ephemeral=True)
        
        # Cas spécial du monstre marin
        if loot_item.get("special") == "combat":
            await interaction.followup.send(
                f"{loot_item['emoji']} **{base_roll}/100** ! Oh non ! Vous avez pêché un **{loot_item['name']}** !\n"
                "Préparez-vous au combat !"
            )
            # Ici on pourrait déclencher un combat automatiquement
            return
        
        # Pour la pêche, on garde généralement 1 par défaut
        # Sauf pour les coffres au trésor où on peut appliquer un bonus
        quantity = 1
        if loot_item["item_id"] == "coffre_tresor":
            quantity = 1 + bonus
        
        # Ajout de l'item à l'inventaire
        await add_item_to_inventory(self.bot.db, char.user_id, loot_item["item_id"], quantity)
        
        # Création de l'embed de réponse
        color = discord.Color.green()
        if base_roll > 80:
            color = discord.Color.blue()
        if base_roll > 95:
            color = discord.Color.gold()
            
        embed = discord.Embed(title=f"{loot_item['emoji']} Pêche réussie !", color=color)
        embed.add_field(name="Jet de dé", value=f"🎲 **{base_roll}**/100 (+{bonus} bonus)", inline=True)
        embed.add_field(name="Total", value=str(total), inline=True)
        
        # Affichage du butin avec quantité
        qty_text = f"**{quantity}x {loot_item['name']}**"
        if quantity > 1:
            qty_text += f" *(Base: 1 + Bonus DEX: {bonus})*"
            
        embed.add_field(name="Butin", value=qty_text, inline=False)
        embed.set_footer(text=f"Pêche | DEX: {char.DEX}")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfessionsCog(bot))
    logger.info("ProfessionsCog chargé")