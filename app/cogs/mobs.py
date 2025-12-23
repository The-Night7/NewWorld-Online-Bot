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
from app.combat_session import combat_is_active
from app.character import get_character, add_xp, add_item_to_inventory
from app.items import ITEM_REGISTRY, ItemDefinition
import random

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bofuri.mobs')

async def fetch_player_entity(bot, user: discord.User | discord.Member) -> RuntimeEntity:
    """
    Récupère ou crée une entité de joueur pour le combat.
    On passe 'bot' pour accéder à bot.db.
    """
    db = bot.db
    user_id = user.id
    
    # Essayer d'abord de récupérer depuis la nouvelle table characters
    async with db.conn.execute(
        "SELECT * FROM characters WHERE user_id = ?",
        (user_id,)
    ) as cursor:
        row = await cursor.fetchone()

    if row:
        # Créer une entité RuntimeEntity avec les données de la table characters
        ent = RuntimeEntity()
        ent.user_id = row["user_id"]
        ent.name = row["name"]
        ent.level = row["level"]
        ent.xp = row["xp"]
        ent.xp_next = row["xp_next"]
        ent.hp = row["hp"]
        ent.hp_max = row["hp_max"]
        ent.mana = row["mana"]
        ent.mana_max = row["mana_max"]
        ent.physical_attack = row["physical_attack"]
        ent.magical_attack = row["magical_attack"]
        ent.armor = row["armor"]
        ent.resistance = row["resistance"]
        ent.crit_chance = row["crit_chance"]
        ent.dodge_chance = row["dodge_chance"]
        ent.skill_points = row["skill_points"]
        ent.gold = row["gold"]

        # Log des infos récupérées pour débogage
        logger.info(f"Entité de joueur récupérée depuis la table 'characters': {ent.name} (lvl {ent.level})")
        return ent
    
    # Fallback: essayer l'ancienne table players
    async with db.conn.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (user_id,)
    ) as cursor:
        row = await cursor.fetchone()

    if row:
        # Créer une entité RuntimeEntity avec les données de l'ancienne table players
        ent = RuntimeEntity()
        ent.user_id = row["user_id"]
        ent.name = row["name"]
        ent.level = row["level"]
        ent.xp = row["xp"]
        ent.xp_next = row["xp_next"]
        ent.hp = row["hp"]
        ent.hp_max = row["hp_max"]
        ent.mana = row["mana"]
        ent.mana_max = row["mana_max"]
        ent.physical_attack = row["physical_attack"]
        ent.magical_attack = row["magical_attack"]
        ent.armor = row["armor"]
        ent.resistance = row["resistance"]
        ent.crit_chance = row["crit_chance"]
        ent.dodge_chance = row["dodge_chance"]
        # Les anciennes tables n'ont pas skill_points et gold, on initialise à 0
        ent.skill_points = 0
        ent.gold = 0

        # Log des infos récupérées pour débogage
        logger.info(f"Entité de joueur récupérée depuis la table 'players' (ancienne table): {ent.name} (lvl {ent.level})")
        return ent

    # Si aucune donnée n'est trouvée, log une erreur et retourne None
    logger.error(f"Aucune donnée trouvée pour l'utilisateur {user_id} dans les tables 'characters' ou 'players'.")
    raise ValueError(f"Aucun joueur trouvé avec l'ID {user_id}")

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

        # reprendre ton /atk actuel, juste renommé pour éviter ambiguïtés
        try:
            attacker = await fetch_player_entity(self.bot, interaction.user)
            defender = await fetch_mob_entity(self.bot.db, interaction.channel_id, mob_name)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        ra = d20()
        rb = d20()
        result = resolve_attack(attacker, defender, ra, rb, attack_type=attack_type, perce_armure=perce_armure)

        # persist
        await save_player_hp(self.bot, interaction.user.id, attacker.hp)
        await save_mob_hp(self.bot.db, interaction.channel_id, mob_name, defender.hp)
        deleted = await cleanup_dead_mobs(self.bot.db, interaction.channel_id)

        color = discord.Color.red() if result["hit"] else discord.Color.dark_gray()
        embed = discord.Embed(title="⚔️ Attaque sur mob", color=color)
        embed.add_field(name="Cible", value=mob_name, inline=True)
        embed.add_field(name="Type", value=str(attack_type), inline=True)
        embed.add_field(name="Perce-armure", value="Oui" if perce_armure else "Non", inline=True)

        embed.add_field(name="Toucher A vs D", value=f'{result["hit_a"]:.2f} vs {result["hit_b"]:.2f}', inline=False)
        embed.add_field(name="Log", value="\n".join(result["effects"]) if result["effects"] else "—", inline=False)

        # Vérifier si le mob est mort (HP = 0) et attribuer de l'XP si c'est le cas
        if defender.hp <= 0:
            try:
                # 1. Calcul de l'XP (déjà présent mais on s'assure qu'il utilise le nouveau rules.py)
                # Récupérer les informations du mob depuis le registre
                mob_key = None
                mob_level = None
                rows = await list_mobs(self.bot.db, interaction.channel_id)
                for row in rows:
                    if row['mob_name'] == mob_name:
                        mob_key = row['mob_key']
                        mob_level = row['level']
                        break

                if mob_key:
                    mob_def = REGISTRY.get(mob_key)
                    if mob_def:
                        # Déterminer le type de mob (commun, rare, elite, boss)
                        mob_type = "commun"
                        is_boss = False
                        is_event = False

                        # Vérifier les tags pour déterminer le type
                        if mob_def.tags:
                            if "boss" in mob_def.tags:
                                mob_type = "boss"
                                is_boss = True
                            elif "elite" in mob_def.tags:
                                mob_type = "elite"
                            elif "rare" in mob_def.tags:
                                mob_type = "rare"

                            if "event" in mob_def.tags:
                                is_event = True

                        # Récupérer le personnage du joueur
                            try:
                                character = await get_character(self.bot.db, interaction.user.id)
                            except Exception as e:
                                logger.error(f"Erreur lors de la récupération du personnage: {e}")
                                character = None

                            if character:
                                # Calculer l'XP gagnée
                                xp_amount, explanation = calculate_xp_amount(
                                    player_level=character.level,
                                    mob_level=mob_level,
                                    mob_type=mob_type,
                                    mob_name=mob_name,
                                    is_boss=is_boss,
                                    is_event=is_event,
                                    xp_next_level=character.xp_next
                                )

                            # Ajouter l'XP au personnage
                            if xp_amount > 0:
                                character, leveled_up, levels_gained = await add_xp(self.bot.db, character.user_id, xp_amount)

                                # Message d'XP
                                xp_message = f"Vous avez gagné {xp_amount} XP! ({explanation})"
                                if leveled_up:
                                    xp_message += f"\n**NIVEAU UP!** Vous êtes maintenant niveau {character.level}!"
                                    if levels_gained > 1:
                                        xp_message += f" (+{levels_gained} niveaux)"
                                    xp_message += f"\nPoints de compétence disponibles: {character.skill_points}"

                            # 2. Système de LOOT Automatisé
                            loot_received = []
                            if mob_def.drops:
                                for drop_name in mob_def.drops:
                                    # On simule une chance de drop (ex: 40% pour les items communs, 10% pour les boss)
                                    drop_chance = 0.15 if is_boss else 0.40
                                    if random.random() < drop_chance:
                                        # On cherche l'item dans le registre par son nom d'affichage
                                        item_to_give = None
                                        for item in ITEM_REGISTRY.all():
                                            if item.name.lower() == drop_name.lower():
                                                item_to_give = item
                                                break

                                        if item_to_give:
                                            await add_item_to_inventory(self.bot.db, character.user_id, item_to_give.item_id, 1)
                                            loot_received.append(f"**{item_to_give.name}**")
                                        else:
                                            # Si l'item n'existe pas encore dans ITEM_REGISTRY, on log l'erreur
                                            logger.warning(f"Loot défini mais inexistant dans le registre: {drop_name}")

                            # Bonus: Ajout d'un peu d'or
                            gold_gain = random.randint(mob_level, mob_level * 5)
                            character.gold += gold_gain
                            await character.save_to_db(self.bot.db)

                            # 3. Message de récompenses
                            reward_text = f"✨ **Récompenses de victoire !**\n"
                            reward_text += f"├ XP: +{xp_amount} ({explanation})\n"
                            reward_text += f"├ Or: +{gold_gain} pièces\n"

                            if loot_received:
                                reward_text += f"└ Butin: {', '.join(loot_received)}"
                            else:
                                reward_text += f"└ Butin: Aucun objet trouvé"

                            embed.add_field(name="Butin & Expérience", value=reward_text, inline=False)
            except Exception as e:
                logger.error(f"Erreur lors du traitement des récompenses: {str(e)}", exc_info=True)
                embed.add_field(name="Erreur", value="Une erreur est survenue lors du calcul des récompenses.", inline=False)

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