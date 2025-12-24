from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional, List

from ..character import (
    Character, get_or_create_character, add_xp,
    add_item_to_inventory, get_inventory, remove_item_from_inventory,
    equip_item, unequip_item
)
from ..items import ITEM_REGISTRY, ItemDefinition

logger = logging.getLogger('bofuri.character')

class CharacterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="profile", description="Affiche votre profil de personnage")
    async def profile(self, interaction: discord.Interaction):
        """Affiche le profil du personnage de l'utilisateur"""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        character = await get_or_create_character(self.bot.db, user_id, interaction.user.display_name)
        
        embed = discord.Embed(
            title=f"Profil de {character.name}",
            color=discord.Color.blue()
        )
        
        # Informations de base
        embed.add_field(name="Niveau", value=str(character.level), inline=True)
        embed.add_field(name="XP", value=f"{character.xp}/{character.xp_next}", inline=True)
        embed.add_field(name="Or", value=str(character.gold), inline=True)
        
        # Statistiques
        embed.add_field(name="HP", value=f"{int(character.hp)}/{int(character.hp_max)}", inline=True)
        embed.add_field(name="MP", value=f"{int(character.mp)}/{int(character.mp_max)}", inline=True)
        embed.add_field(name="Points de compétence", value=str(character.skill_points), inline=True)
        
        # Attributs
        stats = (
            f"**FOR**: {int(character.STR)}\n"
            f"**AGI**: {int(character.AGI)}\n"
            f"**INT**: {int(character.INT)}\n"
            f"**DEX**: {int(character.DEX)}\n"
            f"**VIT**: {int(character.VIT)}"
        )
        embed.add_field(name="Attributs", value=stats, inline=False)
        
        # Avatar de l'utilisateur
        if interaction.user.avatar:
            embed.set_thumbnail(url=interaction.user.avatar.url)
    
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="skills", description="Liste vos compétences apprises")
    async def list_skills(self, interaction: discord.Interaction):
        await interaction.response.defer()
        character = await get_or_create_character(self.bot.db, interaction.user.id, interaction.user.display_name)
        
        if not character.skills:
            await interaction.followup.send("Vous n'avez encore aucune compétence.")
            return

        embed = discord.Embed(title=f"Compétences de {character.name}", color=discord.Color.purple())
        skills_list = "\n".join([f"• {s.replace('_', ' ').capitalize()}" for s in character.skills])
        embed.description = skills_list
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="learn_perce_armure", description="Apprendre 'Coup Perçant' (Coûte 5 points)")
    async def learn_piercing(self, interaction: discord.Interaction):
        await interaction.response.defer()
        db = self.bot.db
        char = await get_or_create_character(db, interaction.user.id, interaction.user.display_name)
        
        if "perce_defense" in char.skills:
            return await interaction.followup.send("Vous possédez déjà cette compétence.")
        
        if char.skill_points < 5:
            return await interaction.followup.send(f"Points insuffisants ({char.skill_points}/5).")

        char.skill_points -= 5
        await db.execute("INSERT INTO character_skills (user_id, skill_id) VALUES (?, ?)", (char.user_id, "perce_defense"))
        await char.save_to_db(db)
        await interaction.followup.send("✨ Vous avez appris le passif **Coup Perçant** !")

    @app_commands.command(name="inventory", description="Affiche votre inventaire")
    async def inventory(self, interaction: discord.Interaction):
        """Affiche l'inventaire du personnage"""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        character = await get_or_create_character(self.bot.db, user_id, interaction.user.display_name)
        inventory_items = await get_inventory(self.bot.db, user_id)
        
        if not inventory_items:
            await interaction.followup.send("Votre inventaire est vide.")
            return
        
        embed = discord.Embed(
            title=f"Inventaire de {character.name}",
            description=f"Or: {character.gold}",
            color=discord.Color.gold()
        )
        
        # Grouper les objets par type
        items_by_type = {}
        for inv_item in inventory_items:
            item_def = ITEM_REGISTRY.get(inv_item.item_id)
            if not item_def:
                continue
                
            item_type = item_def.type
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            
            equipped_str = " (Équipé)" if inv_item.equipped else ""
            items_by_type[item_type].append(
                f"{item_def.name} x{inv_item.quantity}{equipped_str}"
            )
        
        # Ajouter chaque type d'objet comme un champ séparé
        for item_type, items in items_by_type.items():
            embed.add_field(
                name=item_type.capitalize(),
                value="\n".join(items) or "Aucun",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="add_xp", description="Ajoute de l'XP à un utilisateur (Admin seulement)")
    @app_commands.describe(
        user="L'utilisateur à qui ajouter de l'XP",
        amount="La quantité d'XP à ajouter"
    )
    @app_commands.default_permissions(administrator=True)
    async def add_xp_command(self, interaction: discord.Interaction, user: discord.User, amount: int):
        """Ajoute de l'XP à un utilisateur (Admin seulement)"""
        await interaction.response.defer()
        
        if amount <= 0:
            await interaction.followup.send("La quantité d'XP doit être positive.")
            return
        
        try:
            character, leveled_up, levels_gained = await add_xp(self.bot.db, user.id, amount)
            
            message = f"Ajouté {amount} XP à {user.mention}."
            if leveled_up:
                message += f"\n{user.mention} a gagné {levels_gained} niveau(x) ! Niveau actuel: {character.level}"
            
            await interaction.followup.send(message)
        except ValueError as e:
            await interaction.followup.send(f"Erreur: {str(e)}")
    
    @app_commands.command(name="give_item", description="Donne un objet à un utilisateur (Admin seulement)")
    @app_commands.describe(
        user="L'utilisateur à qui donner l'objet",
        item_id="L'ID de l'objet à donner",
        quantity="La quantité à donner (défaut: 1)"
    )
    @app_commands.default_permissions(administrator=True)
    async def give_item_command(
        self, interaction: discord.Interaction, 
        user: discord.User, item_id: str, quantity: int = 1
    ):
        """Donne un objet à un utilisateur (Admin seulement)"""
        await interaction.response.defer()
        
        if quantity <= 0:
            await interaction.followup.send("La quantité doit être positive.")
            return
        
        item_def = ITEM_REGISTRY.get(item_id)
        if not item_def:
            await interaction.followup.send(f"Objet non trouvé: {item_id}")
            return
        
        # S'assurer que le personnage existe
        await get_or_create_character(self.bot.db, user.id, user.display_name)
        
        # Ajouter l'objet à l'inventaire
        await add_item_to_inventory(self.bot.db, user.id, item_id, quantity)
        
        await interaction.followup.send(
            f"Ajouté {quantity}x {item_def.name} à l'inventaire de {user.mention}."
        )
    
    @app_commands.command(name="use_item", description="Utilise un objet de votre inventaire")
    @app_commands.describe(
        item_id="L'ID de l'objet à utiliser",
        quantity="La quantité à utiliser (défaut: 1)"
    )
    async def use_item_command(
        self, interaction: discord.Interaction,
        item_id: str, quantity: int = 1
    ):
        """Utilise un objet de l'inventaire"""
        await interaction.response.defer()
        
        if quantity <= 0:
            await interaction.followup.send("La quantité doit être positive.")
            return
        
        user_id = interaction.user.id
        character = await get_or_create_character(self.bot.db, user_id, interaction.user.display_name)
        
        item_def = ITEM_REGISTRY.get(item_id)
        if not item_def:
            await interaction.followup.send(f"Objet non trouvé: {item_id}")
            return
        
        # Vérifier si l'objet est utilisable (consommable)
        if item_def.type != "consumable":
            await interaction.followup.send(f"{item_def.name} n'est pas un objet consommable.")
            return
        
        # Retirer l'objet de l'inventaire
        success = await remove_item_from_inventory(self.bot.db, user_id, item_id, quantity)
        if not success:
            await interaction.followup.send(f"Vous n'avez pas {quantity}x {item_def.name} dans votre inventaire.")
            return
        
        # Appliquer les effets de l'objet
        effect = item_def.properties.get("effect", "")
        amount = item_def.properties.get("amount", 0)
        
        message = f"Vous avez utilisé {quantity}x {item_def.name}."
        
        if effect == "heal":
            old_hp = character.hp
            character.hp = min(character.hp + amount * quantity, character.hp_max)
            healed = character.hp - old_hp
            message += f" Vous avez récupéré {int(healed)} points de vie."
            await character.save_to_db(self.bot.db)
        
        elif effect == "restore_mana":
            old_mp = character.mp
            character.mp = min(character.mp + amount * quantity, character.mp_max)
            restored = character.mp - old_mp
            message += f" Vous avez récupéré {int(restored)} points de mana."
            await character.save_to_db(self.bot.db)
        
        await interaction.followup.send(message)
    
    @app_commands.command(name="equip", description="Équipe un objet de votre inventaire")
    @app_commands.describe(item_id="L'ID de l'objet à équiper")
    async def equip_command(self, interaction: discord.Interaction, item_id: str):
        """Équipe un objet de l'inventaire"""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        character = await get_or_create_character(self.bot.db, user_id, interaction.user.display_name)
        
        item_def = ITEM_REGISTRY.get(item_id)
        if not item_def:
            await interaction.followup.send(f"Objet non trouvé: {item_id}")
            return
        
        # Vérifier si l'objet est équipable
        if item_def.type not in ["weapon", "armor", "accessory"]:
            await interaction.followup.send(f"{item_def.name} n'est pas équipable.")
            return
        
        # Équiper l'objet
        success = await equip_item(self.bot.db, user_id, item_id)
        if not success:
            await interaction.followup.send(f"Vous n'avez pas {item_def.name} dans votre inventaire.")
            return
        
        await interaction.followup.send(f"Vous avez équipé {item_def.name}.")
    
    @app_commands.command(name="unequip", description="Déséquipe un objet")
    @app_commands.describe(item_id="L'ID de l'objet à déséquiper")
    async def unequip_command(self, interaction: discord.Interaction, item_id: str):
        """Déséquipe un objet"""
        await interaction.response.defer()
        
        user_id = interaction.user.id
        
        item_def = ITEM_REGISTRY.get(item_id)
        if not item_def:
            await interaction.followup.send(f"Objet non trouvé: {item_id}")
            return
        
        # Déséquiper l'objet
        success = await unequip_item(self.bot.db, user_id, item_id)
        if not success:
            await interaction.followup.send(f"Vous n'avez pas {item_def.name} équipé.")
            return
        
        await interaction.followup.send(f"Vous avez déséquipé {item_def.name}.")


async def setup(bot):
    await bot.add_cog(CharacterCog(bot))
    logger.info("CharacterCog chargé")