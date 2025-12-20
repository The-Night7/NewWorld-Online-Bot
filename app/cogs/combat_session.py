from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from app.combat_session import (
    CombatError,
    combat_create,
    combat_close,
    combat_get_thread_id,
    combat_is_active,
    combat_set_thread,
    participants_add,
    participants_list,
    log_add,
)


class CombatSessionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_active_thread(self, channel: discord.abc.GuildChannel) -> discord.Thread | None:
        tid = await combat_get_thread_id(self.bot.db.conn, channel.id)
        if not tid:
            return None
        thr = channel.guild.get_thread(tid)
        if thr:
            return thr
        try:
            return await channel.guild.fetch_channel(tid)  # type: ignore
        except Exception:
            return None

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
            await combat_create(self.bot.db.conn, channel.id, created_by=interaction.user.id)
        except CombatError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        # participants = auteur + mentions
        await participants_add(self.bot.db.conn, channel.id, interaction.user.id, added_by=interaction.user.id)
        for uid in ids:
            await participants_add(self.bot.db.conn, channel.id, uid, added_by=interaction.user.id)

        await log_add(self.bot.db.conn, channel.id, "system", f"Combat démarré par {interaction.user} (participants: {len(ids)+1}).")

        # Crée un fil privé
        try:
            thread = await channel.create_thread(
                name=f"Combat — {channel.name}",
                type=discord.ChannelType.private_thread,
                invitable=False,  # seuls les invités (par le bot) y entrent
                reason="Combat RP",
            )
        except Exception as e:
            # On garde le combat actif en DB, mais on signale l’échec thread
            await interaction.response.send_message(
                f"Combat créé, mais impossible de créer le fil privé (permissions/config). Erreur: {e}",
                ephemeral=True,
            )
            return

        await combat_set_thread(self.bot.db.conn, channel.id, thread.id)

        # Invite les participants
        uids = await participants_list(self.bot.db.conn, channel.id)
        invited = 0
        for uid in uids:
            member = interaction.guild.get_member(uid)
            if member:
                try:
                    await thread.add_user(member)
                    invited += 1
                except Exception:
                    pass

        await thread.send(f"Combat démarré. Participants invités: {invited}/{len(uids)}.")

        await interaction.response.send_message(f"Combat démarré. Fil privé: {thread.mention}")

    @app_commands.command(name="combat_add", description="Ajoute un membre au combat actif et l'invite au fil")
    async def combat_add(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.guild or not interaction.channel:
            await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)
            return

        if not await combat_is_active(self.bot.db.conn, interaction.channel_id):
            await interaction.response.send_message("Aucun combat actif dans ce salon.", ephemeral=True)
            return

        await participants_add(self.bot.db.conn, interaction.channel_id, member.id, added_by=interaction.user.id)
        await log_add(self.bot.db.conn, interaction.channel_id, "system", f"{member} ajouté au combat par {interaction.user}.")

        thread = await self._get_active_thread(interaction.channel)  # type: ignore
        if thread:
            try:
                await thread.add_user(member)
            except Exception:
                pass
            await interaction.response.send_message(f"{member.mention} ajouté. Fil: {thread.mention}")
        else:
            await interaction.response.send_message(f"{member.mention} ajouté, mais fil introuvable/non défini.", ephemeral=True)

    @app_commands.command(name="combat_end", description="Termine le combat actif dans ce salon")
    async def combat_end(self, interaction: discord.Interaction):
        if not interaction.guild or not interaction.channel:
            await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)
            return

        if not await combat_is_active(self.bot.db.conn, interaction.channel_id):
            await interaction.response.send_message("Aucun combat actif dans ce salon.", ephemeral=True)
            return

        thread = await self._get_active_thread(interaction.channel)  # type: ignore
        await combat_close(self.bot.db.conn, interaction.channel_id)
        await log_add(self.bot.db.conn, interaction.channel_id, "system", f"Combat terminé par {interaction.user}.")

        if thread:
            try:
                await thread.send("Combat terminé. Thread va être archivé.")
                await thread.edit(archived=True, locked=True)
            except Exception:
                pass

        await interaction.response.send_message("Combat terminé.")
