from __future__ import annotations

import discord
import logging
import asyncio
from discord import app_commands
from discord.ext import commands
from typing import Dict, Optional

from ..combat_session_manager import CombatSession, get_or_create_session
from ..combat_session import combat_is_active, log_add
from ..combat_mobs import save_mob_hp, cleanup_dead_mobs
from ..cogs.combat import save_player_hp

logger = logging.getLogger('bofuri.combat_turn')

class CombatTurnCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_sessions: Dict[int, CombatSession] = {}  # thread_id -> CombatSession
    
    async def _get_or_create_session(self, thread_id: int) -> CombatSession:
        """Récupère ou crée une session de combat pour un thread donné"""
        if thread_id not in self.active_sessions:
            session = await get_or_create_session(self.bot.db, thread_id)
            self.active_sessions[thread_id] = session
        return self.active_sessions[thread_id]
    
    def _require_thread(self, interaction: discord.Interaction) -> Optional[discord.Thread]:
        """Vérifie que l'interaction a lieu dans un thread et le retourne"""
        if not isinstance(interaction.channel, discord.Thread):
            return None
        return interaction.channel
    
    @app_commands.command(name="next_turn", description="Passe au tour suivant dans le combat")
    async def next_turn(self, interaction: discord.Interaction):
        """Passe au tour suivant dans le combat et exécute automatiquement le tour des mobs"""
        # Vérifier que la commande est utilisée dans un thread
        thread = self._require_thread(interaction)
        if not thread:
            await interaction.response.send_message("Utilisez cette commande dans un fil de combat.", ephemeral=True)
            return
        
        # Vérifier que le combat est actif
        thread_id = thread.id
        if not await combat_is_active(self.bot.db, thread_id):
            await interaction.response.send_message("Aucun combat actif dans ce fil.", ephemeral=True)
            return
        
        # Réponse différée pour éviter le timeout
        await interaction.response.defer()
        
        # Récupérer la session de combat
        session = await self._get_or_create_session(thread_id)
        
        # Nettoyer les mobs morts avant de commencer
        await cleanup_dead_mobs(self.bot.db, thread_id)
        
        # Passer au tour suivant
        found_next_actor = session.advance_turn()
        if not found_next_actor:
            await interaction.followup.send("⚠️ Impossible de trouver un participant en vie pour le prochain tour.")
            return
            
        current_actor = session.current_actor
        
        if not current_actor:
            await interaction.followup.send("Aucun participant dans ce combat.")
            return
        
        # Boucle pour gérer les tours des mobs automatiquement
        while current_actor.is_mob and current_actor.hp > 0:
            # Ajouter un message pour indiquer que c'est au tour du mob
            await thread.send(f"🎲 C'est au tour de **{current_actor.name}**...")
            
            # Petite pause pour créer un effet de tour par tour
            await asyncio.sleep(1)
            
            # Exécuter le tour du mob
            await session.execute_mob_turn(current_actor, thread)
            
            # Sauvegarder les changements si le mob a été modifié
            mob_name = session.get_mob_name_for_entity(current_actor)
            if mob_name:
                await save_mob_hp(self.bot.db, thread_id, mob_name, current_actor.hp)
            
            # Nettoyer les mobs morts
            await cleanup_dead_mobs(self.bot.db, thread_id)
            
            # Vérifier si le combat est terminé (tous les joueurs sont KO)
            alive_players = [p for p in session.participants if not p.is_mob and p.hp > 0]
            if not alive_players:
                await thread.send("💀 Tous les joueurs sont KO ! Le combat est terminé.")
                await log_add(self.bot.db, thread_id, "system", "Combat terminé : tous les joueurs sont KO.")
                try:
                    await thread.edit(archived=True, locked=True)
                except Exception as e:
                    logger.error(f"Erreur lors de l'archivage du thread: {e}")
                return
            
            # Passer au tour suivant
            found_next_actor = session.advance_turn()
            if not found_next_actor:
                await thread.send("⚠️ Plus aucun participant en vie pour continuer le combat.")
                return
                
            current_actor = session.current_actor
            
            # Pause entre les tours de mobs pour éviter le spam
            await asyncio.sleep(1)
        
        # Une fois que c'est à un joueur de jouer, on notifie
        # Vérifier que le joueur est en vie (par sécurité)
        if not current_actor or current_actor.hp <= 0:
            await interaction.followup.send("⚠️ Le joueur suivant n'est plus en vie. Utilisez `/next_turn` à nouveau.")
            return
            
        user_id = session.get_user_id_for_entity(current_actor)
        if user_id:
            user_mention = f"<@{user_id}>"
            await interaction.followup.send(f"👉 C'est au tour de {user_mention} ({current_actor.name}) !")
        else:
            await interaction.followup.send(f"👉 C'est au tour de **{current_actor.name}** !")
    
    @app_commands.command(name="provoke", description="Provoque un mob pour qu'il vous attaque en priorité")
    @app_commands.describe(mob_name="Nom exact du mob à provoquer")
    async def provoke(self, interaction: discord.Interaction, mob_name: str):
        """Provoque un mob pour qu'il attaque l'utilisateur en priorité"""
        # Vérifier que la commande est utilisée dans un thread
        thread = self._require_thread(interaction)
        if not thread:
            await interaction.response.send_message("Utilisez cette commande dans un fil de combat.", ephemeral=True)
            return
        
        # Vérifier que le combat est actif
        thread_id = thread.id
        if not await combat_is_active(self.bot.db, thread_id):
            await interaction.response.send_message("Aucun combat actif dans ce fil.", ephemeral=True)
            return
        
        # Récupérer la session de combat
        session = await self._get_or_create_session(thread_id)
        
        # Vérifier que le mob existe
        mob_entity = session.mob_name_to_entity.get(mob_name)
        if not mob_entity:
            await interaction.response.send_message(f"Mob introuvable: **{mob_name}**. Utilisez `/mob_list`.", ephemeral=True)
            return
            
        # Vérifier que le mob est en vie
        if mob_entity.hp <= 0:
            await interaction.response.send_message(f"**{mob_name}** est déjà mort et ne peut pas être provoqué.", ephemeral=True)
            return
        
        # Récupérer l'entité du joueur
        player_entity = session.user_id_to_entity.get(interaction.user.id)
        if not player_entity:
            await interaction.response.send_message("Vous n'êtes pas un participant de ce combat.", ephemeral=True)
            return
            
        # Vérifier que le joueur est en vie
        if player_entity.hp <= 0:
            await interaction.response.send_message("Vous ne pouvez pas provoquer un mob lorsque vous êtes KO.", ephemeral=True)
            return
        
        # Provoquer le mob
        mob_entity.provoked_by = player_entity
        
        await interaction.response.send_message(f"🔥 **{player_entity.name}** provoque **{mob_name}** qui va maintenant le cibler en priorité !")

    @app_commands.command(name="show_turn", description="Affiche de qui c'est le tour actuellement")
    async def show_turn(self, interaction: discord.Interaction):
        """Affiche de qui c'est le tour actuellement"""
        # Vérifier que la commande est utilisée dans un thread
        thread = self._require_thread(interaction)
        if not thread:
            await interaction.response.send_message("Utilisez cette commande dans un fil de combat.", ephemeral=True)
            return
        
        # Vérifier que le combat est actif
        thread_id = thread.id
        if not await combat_is_active(self.bot.db, thread_id):
            await interaction.response.send_message("Aucun combat actif dans ce fil.", ephemeral=True)
            return
        
        # Récupérer la session de combat
        session = await self._get_or_create_session(thread_id)
        
        # Récupérer l'acteur actuel
        current_actor = session.current_actor
        if not current_actor:
            await interaction.response.send_message("Aucun participant dans ce combat.")
            return
            
        # Vérifier que l'acteur actuel est en vie
        if current_actor.hp <= 0:
            await interaction.response.send_message("⚠️ Le tour actuel est attribué à un participant KO. Utilisez `/next_turn` pour passer au suivant.")
            return
        
        # Afficher de qui c'est le tour
        if current_actor.is_mob:
            await interaction.response.send_message(f"🎲 C'est au tour de **{current_actor.name}** (mob).")
        else:
            user_id = session.get_user_id_for_entity(current_actor)
            if user_id:
                user_mention = f"<@{user_id}>"
                await interaction.response.send_message(f"👉 C'est au tour de {user_mention} ({current_actor.name}).")
            else:
                await interaction.response.send_message(f"👉 C'est au tour de **{current_actor.name}**.")

async def setup(bot):
    await bot.add_cog(CombatTurnCog(bot))
    logger.info("CombatTurnCog chargé")