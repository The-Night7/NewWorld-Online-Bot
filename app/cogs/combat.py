import discord
from discord import app_commands
from discord.ext import commands
import traceback
import sys

from ..models import RuntimeEntity
from ..dice import d20
from ..rules import resolve_attack, AttackType


async def fetch_player_entity(db, user_id: int) -> RuntimeEntity:
    """
    Récupère ou crée une entité de joueur pour le combat
    """
    # Essayer d'abord de récupérer depuis la nouvelle table characters
    async with db.execute(
        "SELECT * FROM characters WHERE user_id = ?",
        (user_id,)
    ) as cursor:
        row = await cursor.fetchone()

    if row:
        # Utiliser les données de la table characters
        return RuntimeEntity(
            name=row['name'],
            hp=float(row['hp']),
            hp_max=float(row['hp_max']),
            mp=float(row['mp']),
            mp_max=float(row['mp_max']),
            STR=float(row['STR']),
            AGI=float(row['AGI']),
            INT=float(row['INT']),
            DEX=float(row['DEX']),
            VIT=float(row['VIT']),
        )

    # Fallback: essayer l'ancienne table players
    async with db.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (user_id,)
    ) as cursor:
        row = await cursor.fetchone()

    if row:
        return RuntimeEntity(
            name=row['name'],
            hp=float(row['hp']),
            hp_max=float(row['hp_max']),
            mp=float(row['mp']),
            mp_max=float(row['mp_max']),
            STR=float(row['str']),
            AGI=float(row['agi']),
            INT=float(row['int_']),
            DEX=float(row['dex']),
            VIT=float(row['vit']),
        )

    # Si aucune donnée n'est trouvée, créer un personnage par défaut
    from ..character import create_character
    character = await create_character(db, user_id, f"Joueur_{user_id}")

    return RuntimeEntity(
        name=character.name,
        hp=character.hp,
        hp_max=character.hp_max,
        mp=character.mp,
        mp_max=character.mp_max,
        STR=character.STR,
        AGI=character.AGI,
        INT=character.INT,
        DEX=character.DEX,
        VIT=character.VIT,
    )


async def save_player_hp(db, user_id: int, hp: float) -> None:
    """
    Sauvegarde les HP d'un joueur après un combat
    """
    # Mettre à jour la table characters
    await db.execute(
        "UPDATE characters SET hp = ? WHERE user_id = ?",
        (hp, user_id)
    )
    await db.commit()

    # Pour la compatibilité, mettre également à jour l'ancienne table players
    await db.execute(
        "UPDATE players SET hp = ? WHERE user_id = ?",
        (hp, user_id)
    )
    await db.commit()


class CombatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="pc_create", description="Crée ta fiche joueur minimale (stats à la main)")
    @app_commands.describe(
        name="Nom RP affiché",
        hp_max="PV max",
        mp_max="PM max",
        str_val="Force",
        agi_val="Agilité",
        int_val="Intelligence",
        dex_val="Dextérité",
        vit_val="Vitalité",
    )
    async def pc_create(
        self,
        interaction: discord.Interaction,
        name: str,
        hp_max: float,
        mp_max: float,
        str_val: float,
        agi_val: float,
        int_val: float,
        dex_val: float,
        vit_val: float,
    ):
        try:
            await self.bot.db.conn.execute(
                """
                INSERT INTO players(user_id, name, hp, hp_max, mp, mp_max, str, agi, int_, dex, vit)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                  name=excluded.name,
                  hp=excluded.hp,
                  hp_max=excluded.hp_max,
                  mp=excluded.mp,
                  mp_max=excluded.mp_max,
                  str=excluded.str,
                  agi=excluded.agi,
                  int_=excluded.int_,
                  dex=excluded.dex,
                  vit=excluded.vit
                """,
                (
                    interaction.user.id,
                    name,
                    float(hp_max),
                    float(hp_max),
                    float(mp_max),
                    float(mp_max),
                    float(str_val),
                    float(agi_val),
                    float(int_val),
                    float(dex_val),
                    float(vit_val),
                ),
            )
            await self.bot.db.conn.commit()

            await interaction.response.send_message(f"Fiche enregistrée pour **{name}**.", ephemeral=True)
        except Exception as e:
            # Log l'erreur
            print(f"Erreur dans pc_create: {e}", file=sys.stderr)
            traceback.print_exc()

            # Si nous n'avons pas encore répondu, envoyez un message d'erreur
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Une erreur est survenue: {str(e)}", ephemeral=True)
            else:
                # Si nous avons déjà commencé à répondre, utilisez followup
                await interaction.followup.send(f"Une erreur est survenue: {str(e)}", ephemeral=True)

    @app_commands.command(name="atk", description="Attaque un joueur (d20 opposé + AGI/10, dégâts via STR/INT/DEX)")
    @app_commands.describe(
        target="Cible",
        attack_type="phys, magic ou ranged",
        perce_armure="Si vrai: vit_term = VIT/100 au lieu de VIT/10",
    )
    async def atk(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        attack_type: AttackType = "phys",
        perce_armure: bool = False,
    ):
        try:
            try:
                attacker = await fetch_player_entity(self.bot, interaction.user)
                defender = await fetch_player_entity(self.bot, target)
            except ValueError as e:
                await interaction.response.send_message(str(e), ephemeral=True)
                return

            ra = d20()
            rb = d20()
            result = resolve_attack(attacker, defender, ra, rb, attack_type=attack_type, perce_armure=perce_armure)

            # Persist HP
            await save_player_hp(self.bot, interaction.user.id, attacker.hp)
            await save_player_hp(self.bot, target.id, defender.hp)

            color = discord.Color.red() if result["hit"] else discord.Color.dark_gray()
            embed = discord.Embed(title="⚔️ Résolution d'attaque", color=color)
            embed.add_field(name="Type", value=str(attack_type), inline=True)
            embed.add_field(name="Perce-armure", value="Oui" if perce_armure else "Non", inline=True)
            embed.add_field(name="Réduction VIT", value=f'{result["vit_term"]:.2f}', inline=True)

            embed.add_field(name="Jet attaquant (d20)", value=str(ra), inline=True)
            embed.add_field(name="Jet défenseur (d20)", value=str(rb), inline=True)
            embed.add_field(name="Toucher A vs D", value=f'{result["hit_a"]:.2f} vs {result["hit_b"]:.2f}', inline=True)

            embed.add_field(name="Puissance (stat dégâts)", value=f'{result["atk_stat"]:.2f}', inline=True)
            if result["hit"]:
                embed.add_field(name="Dégâts", value=f'{result["raw"]["damage"]:.2f}', inline=True)
            else:
                embed.add_field(name="Défense (valeur)", value=f'{result["raw"].get("defense_value", 0.0):.2f}', inline=True)

            embed.add_field(
                name="Log",
                value="\n".join(result["effects"]) if result["effects"] else "—",
                inline=False,
            )

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            # Log l'erreur
            print(f"Erreur dans atk: {e}", file=sys.stderr)
            traceback.print_exc()

            # Si nous n'avons pas encore répondu, envoyez un message d'erreur
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Une erreur est survenue: {str(e)}", ephemeral=True)
            else:
                # Si nous avons déjà commencé à répondre, utilisez followup
                await interaction.followup.send(f"Une erreur est survenue: {str(e)}", ephemeral=True)

    # Ajout d'un gestionnaire d'erreurs général pour les commandes d'application
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandInvokeError):
            error = error.original  # Obtenez l'erreur d'origine

        print(f"Erreur de commande: {error}", file=sys.stderr)
        traceback.print_exc()

        # Si nous n'avons pas encore répondu, envoyez un message d'erreur
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Une erreur est survenue: {str(error)}", ephemeral=True)
        else:
            # Si nous avons déjà commencé à répondre, utilisez followup
            await interaction.followup.send(f"Une erreur est survenue: {str(error)}", ephemeral=True)
