from __future__ import annotations

import discord
import logging
from discord import app_commands
from discord.ext import commands

from app.mobs import registry
from app.mobs.factory import spawn_entity
from app.combat_mobs import (
    next_unique_mob_name,
    insert_mob,
    list_mobs,
    fetch_mob_entity,
    save_mob_hp,
    cleanup_dead_mobs,
)
from app.dice import d20
from app.rules import resolve_attack, AttackType
from app.cogs.combat import fetch_player_entity, save_player_hp
from app.combat_session import combat_is_active

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bofuri.mobs')

class MobsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="mobs", description="Liste les mobs du bestiaire (keys)")
    async def mobs(self, interaction: discord.Interaction):
        logger.info(f"Commande /mobs appelée par {interaction.user}")
        mobs = registry.all()
        if not mobs:
            await interaction.response.send_message("Aucun mob enregistré.", ephemeral=True)
            return

        lines = [f"- `{m.key}` → **{m.display_name}** ({', '.join(m.tags) or 'no-tags'})" for m in mobs[:40]]
        msg = "## Bestiaire (extraits)\n" + "\n".join(lines)
        if len(mobs) > 40:
            msg += f"\n… +{len(mobs) - 40} autres"

        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="mob_spawn", description="Spawn un mob dans ce salon (nom unique auto)")
    @app_commands.describe(key="Ex: forest.lapin_vegetal", level="Niveau voulu (interpolé si besoin)")
    async def mob_spawn(self, interaction: discord.Interaction, key: str, level: int):
        try:
            # Répondre immédiatement pour éviter le timeout
            await interaction.response.defer(ephemeral=False)
            if not await combat_is_active(self.bot.db, interaction.channel_id):
                await interaction.followup.send("Aucun combat actif dans ce salon. Utilise /combat_start.", ephemeral=True)
                return

            defn = registry.get(key)
            if not defn:
                await interaction.followup.send("Key inconnue. Utilise /mobs.", ephemeral=True)
                return

            channel_id = interaction.channel_id
            mob_name = await next_unique_mob_name(self.bot.db.conn, channel_id, defn.display_name)

            ent = spawn_entity(defn, level=level, instance_name=mob_name)
            await insert_mob(self.bot.db.conn, channel_id, mob_name, defn.key, level, ent, created_by=interaction.user.id)

            await interaction.followup.send(
                f"Mob spawné: **{mob_name}** (`{defn.key}` lvl {level}) — PV {ent.hp:.0f}/{ent.hp_max:.0f}"
            )
        except Exception as e:
            logger = logging.getLogger('bofuri')
            logger.error(f"Erreur dans /mob_spawn: {str(e)}", exc_info=True)
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Une erreur est survenue: {str(e)}", ephemeral=True)
            else:
                await interaction.followup.send(f"Une erreur est survenue: {str(e)}", ephemeral=True)

    @app_commands.command(name="mob_list", description="Liste les mobs présents dans ce salon")
    async def mob_list(self, interaction: discord.Interaction):
        try:
            # Répondre immédiatement pour éviter le timeout
            await interaction.response.defer(ephemeral=False)
            if not await combat_is_active(self.bot.db, interaction.channel_id):
                await interaction.followup.send("Aucun combat actif dans ce salon. Utilise /combat_start.", ephemeral=True)
                return

            rows = await list_mobs(self.bot.db.conn, interaction.channel_id)
            if not rows:
                await interaction.followup.send("Aucun mob dans ce salon.", ephemeral=True)
                return

            lines = [
                f"- **{r['mob_name']}** — `{r['mob_key']}` lvl {r['level']} — PV {float(r['hp']):.2f}/{float(r['hp_max']):.2f}"
                for r in rows
            ]
            await interaction.followup.send("## Mobs du salon\n" + "\n".join(lines))
        except Exception as e:
            logger = logging.getLogger('bofuri')
            logger.error(f"Erreur dans /mob_list: {str(e)}", exc_info=True)
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Une erreur est survenue: {str(e)}", ephemeral=True)
            else:
                await interaction.followup.send(f"Une erreur est survenue: {str(e)}", ephemeral=True)

    @app_commands.command(name="atk_mob", description="Attaque un mob (par nom unique)")
    @app_commands.describe(
        mob_name='Nom exact, ex: "Lapin végétal#1"',
        attack_type="phys, magic, ranged",
        perce_armure="Ignore partiellement la VIT (VIT/100)",
    )
    async def atk_mob(
        self,
        interaction: discord.Interaction,
        mob_name: str,
        attack_type: AttackType = "phys",
        perce_armure: bool = False,
    ):
        if not await combat_is_active(self.bot.db, interaction.channel_id):
            await interaction.response.send_message("Aucun combat actif dans ce salon. Utilise /combat_start.", ephemeral=True)
            return

        try:
            attacker = await fetch_player_entity(self.bot, interaction.user)
            defender = await fetch_mob_entity(self.bot.db.conn, interaction.channel_id, mob_name)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        ra = d20()
        rb = d20()
        result = resolve_attack(attacker, defender, ra, rb, attack_type=attack_type, perce_armure=perce_armure)

        # persist
        await save_player_hp(self.bot, interaction.user.id, attacker.hp)
        await save_mob_hp(self.bot.db.conn, interaction.channel_id, mob_name, defender.hp)
        deleted = await cleanup_dead_mobs(self.bot.db.conn, interaction.channel_id)

        color = discord.Color.red() if result["hit"] else discord.Color.dark_gray()
        embed = discord.Embed(title="⚔️ Attaque sur mob", color=color)
        embed.add_field(name="Cible", value=mob_name, inline=True)
        embed.add_field(name="Type", value=str(attack_type), inline=True)
        embed.add_field(name="Perce-armure", value="Oui" if perce_armure else "Non", inline=True)

        embed.add_field(name="Toucher A vs D", value=f'{result["hit_a"]:.2f} vs {result["hit_b"]:.2f}', inline=False)
        embed.add_field(name="Log", value="\n".join(result["effects"]) if result["effects"] else "—", inline=False)

        if deleted:
            embed.add_field(name="Info", value=f"{deleted} mob(s) mort(s) retiré(s) du salon.", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="atk_player", description="Attaque un joueur (commande conservée)")
    async def atk_player(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        attack_type: AttackType = "phys",
        perce_armure: bool = False,
    ):
        if not await combat_is_active(self.bot.db, interaction.channel_id):
            await interaction.response.send_message("Aucun combat actif dans ce salon. Utilise /combat_start.", ephemeral=True)
            return

        # reprend ton /atk actuel, juste renommé pour éviter ambiguïtés
        try:
            attacker = await fetch_player_entity(self.bot, interaction.user)
            defender = await fetch_player_entity(self.bot, target)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        ra = d20()
        rb = d20()
        result = resolve_attack(attacker, defender, ra, rb, attack_type=attack_type, perce_armure=perce_armure)

        await save_player_hp(self.bot, interaction.user.id, attacker.hp)
        await save_player_hp(self.bot, target.id, defender.hp)

        color = discord.Color.red() if result["hit"] else discord.Color.dark_gray()
        embed = discord.Embed(title="⚔️ Attaque sur joueur", color=color)
        embed.add_field(name="Cible", value=target.mention, inline=True)
        embed.add_field(name="Type", value=str(attack_type), inline=True)
        embed.add_field(name="Perce-armure", value="Oui" if perce_armure else "Non", inline=True)
        embed.add_field(name="Toucher A vs D", value=f'{result["hit_a"]:.2f} vs {result["hit_b"]:.2f}', inline=False)
        embed.add_field(name="Log", value="\n".join(result["effects"]) if result["effects"] else "—", inline=False)

        await interaction.response.send_message(embed=embed)