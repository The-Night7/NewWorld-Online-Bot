from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from app import db
from app.combat_session import (
    CombatError,
    combat_create,
    combat_close,
    combat_get_thread_id,
    combat_get_thread_ids,
    combat_is_active,
    combat_set_thread,
    participants_add,
    participants_list,
    log_add,
)

import logging

# Table des rencontres par salon
ZONE_MONSTERS = {
    1398615884196610088: ["forest.lapin_vegetal", "forest.bee_me_me_bee", "forest.spider_eyes", "hydra_dungeon.chenille_ortifleur", "misc.reine_des_abeilles"],  # Forêt luxuriante
    1398617728474153061: ["forest_plains.louveteau_des_forets", "forest.bee_me_me_bee", "forest.spider_eyes", "hydra_dungeon.chenille_ortifleur", "forest_plains.loup_alpha"],  # Forêt sombre
    1398617842064035840: ["misc.golem", "rocky_crystal.taupe_de_cristal", "rocky_crystal.loup_veteran"],  # Grotte rocheuse
    1398617763093807184: ["forest_plains.louveteau_des_forets", "hydra_dungeon.slime", "forest.coxiplooosion"],  # Grandes plaines
    1398617871588003870: ["misc.poisson_tentaculaire"],  # Lac de Crystal
    1398626100615188530: ["ghost_zone.spectre", "ghost_zone.zombie"],  # Forêt hantée
    1398626193254645820: ["ghost_zone.zombie", "ghost_zone.spectre"],  # Village hanté
    1398626132403687504: ["ghost_zone.spectre", "misc.zombie_du_manoir"],  # Manoir hanté
    1398632574276075580: ["ghost_zone.zombie", "misc.roi_squelette"],  # Sous-sol
    1398191886589624421: ["misc.poisson_tentaculaire", "hydra_dungeon.slime"],  # Donjon aquatique
    1398192851774345407: ["hydra_dungeon.hydre_au_poison"],  # Donjon de l'hydre (Boss)
    1398626819296596070: ["misc.spectre_de_la_mort", "misc.feu_follet"],  # Domaine du trépassé
    1398193027893432361: ["crystal_cave.araignee_des_grottes", "misc.amethyste_le_sabre_maudit_devoreur"],  # Donjon de palier grotte luxuriante
}

class CombatSessionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_active_thread(self, channel: discord.abc.GuildChannel) -> discord.Thread | None:
        tid = await combat_get_thread_id(self.bot.db, channel.id)
        if not tid:
            return None
        thr = channel.guild.get_thread(tid)
        if thr:
            return thr
        try:
            return await channel.guild.fetch_channel(tid)  # type: ignore
        except Exception:
            return None

    async def _get_active_threads(self, channel: discord.abc.GuildChannel) -> list[discord.Thread]:
        """Récupère tous les fils de combats actifs pour un salon."""
        thread_ids = await combat_get_thread_ids(self.bot.db, channel.id)
        threads = []

        for tid in thread_ids:
            thr = channel.guild.get_thread(tid)
            if thr:
                threads.append(thr)
            else:
                try:
                    thr = await channel.guild.fetch_channel(tid)
                    threads.append(thr)
                except Exception:
                    pass

        return threads
    @app_commands.command(name="combat_start", description="Démarre un combat dans ce salon et ouvre un fil privé")
    @app_commands.describe(members="Membres à inclure dans le combat (en plus de toi)")
    async def combat_start(self, interaction: discord.Interaction, members: str = ""):
        if not interaction.guild or not interaction.channel:
            await interaction.response.send_message("Commande utilisable uniquement sur un serveur.", ephemeral=True)
            return

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("Le combat doit être démarré dans un salon texte.", ephemeral=True)
            return

        # Parse mentions depuis le string (simple V1)
        # Ex: "<@123> <@456>"
        ids = []
        for tok in (members or "").split():
            tok = tok.strip()
            if tok.startswith("<@") and tok.endswith(">"):
                tok = tok.replace("<@", "").replace(">", "").replace("!", "")
                if tok.isdigit():
                    ids.append(int(tok))
        try:
            # Ajout de journalisation
            logger = logging.getLogger('bofuri.combat')
            logger.info(f"Tentative de création de combat dans le salon {channel.id} par {interaction.user.id}")

            # Création du combat dans la base de données (sans thread_id pour l'instant)
            combat_id = await combat_create(self.bot.db, int(channel.id), created_by=int(interaction.user.id))
            logger.info(f"Combat ID {combat_id} créé avec succès dans le salon {channel.id}")

            # Création du fil de discussion
            thread = await channel.create_thread(
                name=f"Combat - {interaction.user.display_name}",
                type=discord.ChannelType.private_thread,
                reason="Fil de combat créé par Bofuri"
            )

            # Ajout du créateur au fil
            await thread.add_user(interaction.user)

            # Enregistrement du thread dans la base de données
            try:
                await combat_set_thread(self.bot.db, channel.id, thread.id, combat_id=combat_id)
            except CombatError as e:
                # Si un combat est déjà actif dans ce fil, annuler la création
                await combat_close(self.bot.db, thread.id)
                await thread.delete()
                await interaction.response.send_message(str(e), ephemeral=True)
                return

            # Ajout des membres mentionnés au fil et au combat
            members_added = []
            for user_id in ids:
                try:
                    member = await interaction.guild.fetch_member(user_id)
                    if member:
                        await participants_add(self.bot.db, thread.id, member.id, added_by=interaction.user.id)
                        await thread.add_user(member)
                        members_added.append(member.mention)
                except Exception as e:
                    logger.error(f"Erreur lors de l'ajout du membre {user_id}: {str(e)}")

            # Message de bienvenue dans le fil
            welcome_message = f"Combat créé par {interaction.user.mention}."
            if members_added:
                welcome_message += f" Participants: {', '.join(members_added)}"
            await thread.send(welcome_message)

            # --- AUTO SPAWN LOGIC ---
            if channel.id in ZONE_MONSTERS:
                from app.mobs.registry import REGISTRY
                from app.mobs.factory import spawn_entity
                from app.combat_mobs import next_unique_mob_name, insert_mob
                import random

                mob_keys = ZONE_MONSTERS[channel.id]
                # Pour les zones normales, on spawn 1 ou 2 mobs aléatoires. 
                # Pour les donjons (ID spécifiques), on peut spawn le boss directement.
                mobs_to_spawn = []
                
                if len(mob_keys) == 1: # Boss unique ou zone à un seul mob
                    mobs_to_spawn = mob_keys
                else:
                    mobs_to_spawn = random.sample(mob_keys, k=random.randint(1, 2))

                for m_key in mobs_to_spawn:
                    defn = REGISTRY.get(m_key)
                    if defn:
                        # On prend le niveau min du mob ou 1 par défaut
                        level = defn.level_min or 1
                        m_name = await next_unique_mob_name(self.bot.db, thread.id, defn.display_name)
                        ent = spawn_entity(defn, level=level, instance_name=m_name)
                        await insert_mob(self.bot.db, thread.id, m_name, defn.key, level, ent, created_by=self.bot.user.id)
                        await thread.send(f"⚠️ Un sauvage **{m_name}** (Lvl {level}) apparaît !")
            # ------------------------

            # Ajout du log
            await log_add(self.bot.db, thread.id, "system", f"Combat créé par {interaction.user}.")

            # Réponse à l'interaction
            await interaction.response.send_message(f"Combat créé! Fil: {thread.mention}", ephemeral=False)
        except CombatError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.response.send_message("Je n'ai pas les permissions nécessaires pour créer un fil de discussion.", ephemeral=True)
            # Annuler le combat créé dans la base de données
            if 'combat_id' in locals():
                # Si le combat_id existe, utiliser cette méthode
                await db.conn.execute(
                    "UPDATE combats SET status = 'closed', closed_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (combat_id,),
                )
                await db.conn.commit()
            return
        except Exception as e:
            logger.error(f"Erreur lors de la création du combat: {str(e)}", exc_info=True)
            await interaction.response.send_message("Une erreur est survenue lors de la création du combat.", ephemeral=True)
            # Annuler le combat créé dans la base de données
            if 'combat_id' in locals():
                # Si le combat_id existe, utiliser cette méthode
                await db.conn.execute(
                    "UPDATE combats SET status = 'closed', closed_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (combat_id,),
                )
                await db.conn.commit()
            return

    @app_commands.command(name="combat_add", description="Ajoute un membre au combat actif et l'invite au fil")
    async def combat_add(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.guild or not interaction.channel:
            await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)
            return

        # Si l'interaction est dans un thread, utiliser directement ce thread_id
        if isinstance(interaction.channel, discord.Thread):
            thread_id = interaction.channel.id
            if not await combat_is_active(self.bot.db, thread_id):
                await interaction.response.send_message("Aucun combat actif dans ce fil.", ephemeral=True)
                return
            thread = interaction.channel
        else:
            # Sinon, chercher le thread associé au salon
            threads = await self._get_active_threads(interaction.channel)  # type: ignore
            if not threads:
                await interaction.response.send_message("Aucun fil de combat actif trouvé pour ce salon.", ephemeral=True)
                return
            elif len(threads) > 1:
                # S'il y a plusieurs fils actifs, demander à l'utilisateur de spécifier
                thread_options = "\n".join([f"{i+1}. {t.name} ({t.mention})" for i, t in enumerate(threads)])
                await interaction.response.send_message(
                    f"Plusieurs combats actifs trouvés. Veuillez utiliser la commande directement dans le fil concerné:\n{thread_options}",
                    ephemeral=True
                )
                return
            thread = threads[0]
            thread_id = thread.id

        await participants_add(self.bot.db, thread_id, member.id, added_by=interaction.user.id)
        await log_add(self.bot.db, thread_id, "system", f"{member} ajouté au combat par {interaction.user}.")

        try:
            await thread.add_user(member)
        except Exception:
            pass
        await interaction.response.send_message(f"{member.mention} ajouté. Fil: {thread.mention}")

    @app_commands.command(name="combat_end", description="Termine le combat actif dans ce fil")
    async def combat_end(self, interaction: discord.Interaction):
        if not interaction.guild or not interaction.channel:
            await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)
            return

        logger = logging.getLogger('bofuri.combat')
        try:
            # Si l'interaction est dans un thread, utiliser directement ce thread_id
            if isinstance(interaction.channel, discord.Thread):
                thread_id = interaction.channel.id
                thread = interaction.channel
                if not await combat_is_active(self.bot.db, thread_id):
                    await interaction.response.send_message("Aucun combat actif dans ce fil.", ephemeral=True)
                    return
            else:
                # Sinon, chercher le thread associé au salon
                threads = await self._get_active_threads(interaction.channel)  # type: ignore
                if not threads:
                    await interaction.response.send_message("Aucun fil de combat actif trouvé pour ce salon.", ephemeral=True)
                    return
                elif len(threads) > 1:
                    # S'il y a plusieurs fils actifs, demander à l'utilisateur de spécifier
                    thread_options = "\n".join([f"{i+1}. {t.name} ({t.mention})" for i, t in enumerate(threads)])
                    await interaction.response.send_message(
                        f"Plusieurs combats actifs trouvés. Veuillez utiliser la commande directement dans le fil concerné:\n{thread_options}",
                        ephemeral=True
                    )
                    return
                thread = threads[0]
                thread_id = thread.id

            logger.info(f"Fermeture du combat dans le fil {thread_id} par {interaction.user.id}")
            
            # On ajoute le log AVANT de fermer le combat en DB
            await log_add(self.bot.db, thread_id, "system", f"Combat terminé par {interaction.user}.")
            await combat_close(self.bot.db, thread_id)

            try:
                await thread.send("Combat terminé. Thread va être archivé.")
                await thread.edit(archived=True, locked=True)
            except Exception as e:
                logger.error(f"Erreur lors de l'archivage du thread: {str(e)}", exc_info=True)

            await interaction.response.send_message("Combat terminé.")
        except Exception as e:
            logger.error(f"Erreur dans /combat_end: {str(e)}", exc_info=True)
            if not interaction.response.is_done():
                await interaction.response.send_message("Une erreur est survenue lors de la fermeture du combat. Veuillez réessayer.", ephemeral=True)
            else:
                await interaction.followup.send("Une erreur est survenue lors de la fermeture du combat. Veuillez réessayer.", ephemeral=True)

    @app_commands.command(name="initiative", description="Affiche l'ordre de passage basé sur l'agilité")
    async def initiative(self, interaction: discord.Interaction):
        if not interaction.guild or not interaction.channel:
            return

        thread_id = interaction.channel.id
        if not await combat_is_active(self.bot.db, thread_id):
            await interaction.response.send_message("Aucun combat actif dans ce fil.", ephemeral=True)
            return

        await interaction.response.defer()
        
        # 1. Récupérer les joueurs participants
        user_ids = await participants_list(self.bot.db, thread_id)
        entities = []
        
        from app.cogs.combat import fetch_player_entity
        for uid in user_ids:
            try:
                ent = await fetch_player_entity(self.bot.db, uid)
                entities.append(ent)
            except Exception:
                continue

        # 2. Récupérer les mobs du salon
        from app.combat_mobs import list_mobs, fetch_mob_entity
        mob_rows = await list_mobs(self.bot.db, interaction.channel_id)
        for m in mob_rows:
            try:
                ent = await fetch_mob_entity(self.bot.db, interaction.channel_id, m['mob_name'])
                entities.append(ent)
            except Exception:
                continue

        # 3. Trier par AGI (décroissant)
        entities.sort(key=lambda x: x.AGI, reverse=True)

        embed = discord.Embed(title="⚔️ Ordre d'Initiative", color=discord.Color.gold())
        lines = []
        for i, ent in enumerate(entities):
            emoji = "👤" if hasattr(ent, 'user_id') or "Joueur" in ent.name else "👹"
            lines.append(f"{i+1}. {emoji} **{ent.name}** — AGI: `{ent.AGI:.0f}`")
        
        embed.description = "\n".join(lines) if lines else "Aucun combattant trouvé."
        await interaction.followup.send(embed=embed)
