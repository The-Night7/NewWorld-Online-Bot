from __future__ import annotations

import discord
import logging
from discord import app_commands
from discord.ext import commands
import math

# Modifier cette ligne pour importer REGISTRY au lieu de registry
from app.mobs.registry import REGISTRY
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
from app.models import RuntimeEntity
from app.rules import resolve_attack, AttackType, calculate_xp_amount
from app.cogs.combat import fetch_player_entity, save_player_hp
from app.combat_session import combat_is_active, combat_close, participants_add, participants_list
from app.character import get_character, add_xp, add_item_to_inventory
from app.items import ITEM_REGISTRY, ItemDefinition
import random
import logging

logger = logging.getLogger('bofuri.mobs')

async def fetch_player_entity(bot, user: discord.User | discord.Member) -> RuntimeEntity:
    """
    Récupère ou crée une entité de joueur pour le combat.
    On passe 'bot' pour accéder à bot.db.
    """
    db = bot.db
    user_id = user.id

    # Correction: On utilise await directement au lieu de 'async with' sur l'appel de fonction
    cursor = await db.conn.execute(
        "SELECT * FROM characters WHERE user_id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()

    if row:
        return RuntimeEntity(
            name=row["name"],
            hp=float(row["hp"]),
            hp_max=float(row["hp_max"]),
            mp=float(row["mp"]),
            mp_max=float(row["mp"]),
            STR=float(row["STR"]),
            AGI=float(row["AGI"]),
            INT=float(row["INT"]),
            DEX=float(row["DEX"]),
            VIT=float(row["VIT"])
        )

    cursor = await db.conn.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()

    if row:
        return RuntimeEntity(
            name=row["name"],
            hp=float(row["hp"]),
            hp_max=float(row["hp_max"]),
            mp=float(row["mp"]),
            mp_max=float(row["mp"]),
            STR=float(row["str"]),
            AGI=float(row["agi"]),
            INT=float(row["int_"]),
            DEX=float(row["dex"]),
            VIT=float(row["vit"])
        )
    return None

async def save_player_hp(bot, user_id: int, hp: float) -> None:
    """
    Sauvegarde les HP d'un joueur après un combat.
    """
    db = bot.db
    # Mettre à jour la table characters
    await db.conn.execute(
        "UPDATE characters SET hp = ? WHERE user_id = ?",
        (float(hp), int(user_id))
    )
    await db.conn.commit()

    # Pour la compatibilité, mettre également à jour l'ancienne table players
    await db.conn.execute(
        "UPDATE players SET hp = ? WHERE user_id = ?",
        (float(hp), int(user_id))
    )
    await db.conn.commit()

class MobsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="mobs", description="Liste les mobs du bestiaire (keys)")
    async def mobs(self, interaction: discord.Interaction):
        logger.info(f"Commande /mobs appelée par {interaction.user}")
        # Utiliser REGISTRY.all() au lieu de registry.all()
        mobs = REGISTRY.all()
        if not mobs:
            await interaction.response.send_message("Aucun mob enregistré.", ephemeral=True)
            return

        # Répondre immédiatement pour éviter le timeout (correction de l'indentation)
        await interaction.response.defer(ephemeral=True)

        # Créer des pages de 20 mobs maximum pour éviter de dépasser la limite de caractères
        mobs_per_page = 20
        total_pages = math.ceil(len(mobs) / mobs_per_page)

        for page in range(total_pages):
            start_idx = page * mobs_per_page
            end_idx = min(start_idx + mobs_per_page, len(mobs))
            page_mobs = mobs[start_idx:end_idx]

            lines = [f"- `{m.key}` → **{m.display_name}** ({', '.join(m.tags) or 'no-tags'})" for m in page_mobs]

            page_title = f"## Bestiaire (page {page+1}/{total_pages})"
            msg = page_title + "\n" + "\n".join(lines)

            if page == 0:
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.followup.send(msg, ephemeral=True)

    @app_commands.command(name="mob_spawn", description="Spawn un mob dans ce salon (nom unique auto)")
    @app_commands.describe(key="Ex: forest.lapin_vegetal", level="Niveau voulu (interpolé si besoin)")
    async def mob_spawn(self, interaction: discord.Interaction, key: str, level: int):
        try:
            # Répondre immédiatement pour éviter le timeout
            await interaction.response.defer(ephemeral=False)
            if not await combat_is_active(self.bot.db, interaction.channel_id):
                await interaction.followup.send("Aucun combat actif dans ce salon. Utilise /combat_start.", ephemeral=True)
                return

            # Utiliser REGISTRY.get() au lieu de registry.get()
            defn = REGISTRY.get(key)
            if not defn:
                await interaction.followup.send("Key inconnue. Utilise /mobs.", ephemeral=True)
                return

            channel_id = interaction.channel_id
            mob_name = await next_unique_mob_name(self.bot.db, channel_id, defn.display_name)

            ent = spawn_entity(defn, level=level, instance_name=mob_name)
            await insert_mob(self.bot.db, channel_id, mob_name, defn.key, level, ent, created_by=interaction.user.id)

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

            rows = await list_mobs(self.bot.db, interaction.channel_id)
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
    )
    async def atk_mob(
        self,
        interaction: discord.Interaction,
        mob_name: str,
        attack_type: AttackType = "phys",
    ):
        try:
            # Utilisation de l'ID du salon/fil actuel
            target_id = interaction.channel_id

            if not await combat_is_active(self.bot.db, target_id):
                await interaction.response.send_message("Aucun combat actif ici. Utilise /combat_start.", ephemeral=True)
                return

            try:
                # Récupérer le personnage complet pour vérifier les skills
                char_data = await get_character(self.bot.db, interaction.user.id)
                if not char_data:
                    await interaction.response.send_message("Personnage introuvable.", ephemeral=True)
                    return

                attacker = await fetch_player_entity(self.bot, interaction.user)

                # --- Gestion du Passif Coup Perçant ---
                perce_armure = "perce_defense" in char_data.skills
                # --------------------------------------

                # --- Gestion du Mana ---
                mana_cost = 10 if attack_type == "magic" else 0

                if attacker.mp < mana_cost:
                    await interaction.response.send_message(
                        f"❌ Mana insuffisant ! (Requis: {mana_cost}, Actuel: {attacker.mp:.0f})",
                        ephemeral=True
                    )
                    return

                attacker.mp -= mana_cost
                # -----------------------

                defender = await fetch_mob_entity(self.bot.db, target_id, mob_name)
            except ValueError as e:
                await interaction.response.send_message(str(e), ephemeral=True)
                return

            ra, rb = d20(), d20()

            # Persistance du mana
            await self.bot.db.conn.execute(
                "UPDATE characters SET mp = ? WHERE user_id = ?",
                (float(attacker.mp), int(interaction.user.id))
            )

            result = resolve_attack(attacker, defender, ra, rb, attack_type=attack_type, perce_armure=perce_armure)

            # --- Riposte Automatique ---
            riposte_result = None
            if defender.hp > 0:
                ma, mb = d20(), d20()
                hp_ratio = defender.hp / defender.hp_max
                is_enraged = hp_ratio <= 0.5

                riposte_result = resolve_attack(defender, attacker, ma, mb, attack_type="phys")
                if is_enraged:
                    riposte_result["effects"].insert(0, f"💢 **{defender.name}** est enragé !")
            # ---------------------------

            # Sauvegarde
            await save_player_hp(self.bot, interaction.user.id, attacker.hp)
            await save_mob_hp(self.bot.db, target_id, mob_name, defender.hp)
            deleted = await cleanup_dead_mobs(self.bot.db, target_id)

            color = discord.Color.red() if result["hit"] else discord.Color.dark_gray()
            embed = discord.Embed(title="⚔️ Échange de Combat", color=color)
            embed.add_field(name=f"▶️ Ton action ({attack_type})", value="\n".join(result["effects"]), inline=False)

            if riposte_result:
                embed.add_field(name=f"🔄 Riposte de {defender.name}", value="\n".join(riposte_result["effects"]), inline=False)

            embed.set_footer(text=f"PV: {attacker.hp:.0f}/{attacker.hp_max:.0f} | MP: {attacker.mp:.0f}/{attacker.mp_max:.0f}")

            # Récompenses XP
            if defender.hp <= 0:
                xp_gain = 25
                await add_xp(self.bot.db, interaction.user.id, xp_gain)
                embed.add_field(name="Victoire", value=f"✨ Tu gagnes {xp_gain} XP !")

            await interaction.response.send_message(embed=embed)

            # Mort du joueur
            if attacker.hp <= 0:
                await combat_close(self.bot.db, target_id)
                if isinstance(interaction.channel, discord.Thread):
                    await interaction.channel.send("💀 Défait... Le combat s'arrête.")
                    await interaction.channel.edit(archived=True, locked=True)

        except Exception as e:
            logger.error(f"Erreur dans atk_mob: {e}", exc_info=True)
            if not interaction.response.is_done():
                await interaction.response.send_message("Une erreur est survenue lors du combat.", ephemeral=True)

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