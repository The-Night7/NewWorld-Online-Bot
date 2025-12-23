from typing import Dict, Any, Literal, Optional, Tuple
from .models import RuntimeEntity

AttackType = Literal["phys", "magic", "ranged"]


def _attack_stat(attacker: RuntimeEntity, attack_type: AttackType) -> float:
    """Stat qui sert à calculer les dégâts (pas la précision)."""
    if attack_type == "phys":
        return float(attacker.STR)
    if attack_type == "magic":
        return float(attacker.INT)
    if attack_type == "ranged":
        return float(attacker.DEX)
    raise ValueError(f"Unknown attack_type: {attack_type}")


def resolve_attack(
    attacker: RuntimeEntity,
    defender: RuntimeEntity,
    roll_a: float,
    roll_b: float,
    attack_type: AttackType = "phys",
    perce_armure: bool = False,
) -> Dict[str, Any]:
    """
    Toucher:
      A = d20 + AGI(attacker)/10
      D = d20 + AGI(defender)/10
      hit si A > D

    Réduction VIT:
      vit_term = VIT/10
      si perce_armure: vit_term = VIT/100
    """

    hit_a = float(roll_a) + float(attacker.AGI) / 10.0
    hit_b = float(roll_b) + float(defender.AGI) / 10.0

    vit_div = 100.0 if perce_armure else 10.0
    vit_term = float(defender.VIT) / vit_div

    out: Dict[str, Any] = {
        "hit": False,
        "roll_a": float(roll_a),
        "roll_b": float(roll_b),
        "hit_a": hit_a,
        "hit_b": hit_b,
        "attack_type": attack_type,
        "perce_armure": bool(perce_armure),
        "vit_scale_div": vit_div,
        "raw": {},
        "effects": [],
    }

    atk = _attack_stat(attacker, attack_type)
    out["atk_stat"] = atk
    out["vit_term"] = vit_term

    attack_desc = {
        "phys": "frappe",
        "magic": "lance un sort sur",
        "ranged": "tire sur",
    }.get(attack_type, "attaque")

    if hit_a > hit_b:
        out["hit"] = True

        dmg = (hit_a - hit_b) + atk

        if attack_type == "magic":
            dmg *= (1.2 if roll_a > 15 else 0.9)
        elif attack_type == "ranged":
            dmg *= 0.95

        dmg -= vit_term
        dmg = max(0.0, float(dmg))

        defender.hp = max(0.0, float(defender.hp) - dmg)

        out["raw"]["damage"] = dmg
        out["effects"].append(f"{attacker.name} {attack_desc} {defender.name} et inflige {dmg:.2f} dégâts.")
        out["effects"].append(f"PV {defender.name}: {defender.hp:.2f}/{defender.hp_max:.2f}")
        return out

    defense_power = (hit_b - hit_a) + vit_term - atk
    out["raw"]["defense_value"] = float(defense_power)

    if defense_power > 0:
        if attack_type == "phys":
            contrecoup = defense_power * 1.0
            out["effects"].append(
                f"{defender.name} contre l'attaque. {attacker.name} prend {contrecoup:.2f} dégâts de contrecoup."
            )
        elif attack_type == "magic":
            contrecoup = defense_power * 0.7
            out["effects"].append(
                f"{defender.name} résiste au sort. {attacker.name} subit {contrecoup:.2f} dégâts de réflexion magique."
            )
        else:
            contrecoup = defense_power * 0.5
            out["effects"].append(
                f"{defender.name} esquive et riposte. {attacker.name} prend {contrecoup:.2f} dégâts."
            )

        attacker.hp = max(0.0, float(attacker.hp) - contrecoup)
        out["effects"].append(f"PV {attacker.name}: {attacker.hp:.2f}/{attacker.hp_max:.2f}")
    else:
        if attack_type == "phys":
            out["effects"].append(f"{defender.name} bloque l'attaque de {attacker.name}. Aucun dégât en retour.")
        elif attack_type == "magic":
            out["effects"].append(f"{defender.name} dissipe le sort de {attacker.name}. Aucun dégât en retour.")
        else:
            out["effects"].append(f"{defender.name} évite le tir de {attacker.name}. Aucun dégât en retour.")

    return out


def calculate_xp_gain(
    player_level: int,
    mob_level: int,
    mob_type: str,
    mob_name: str,
    is_boss: bool = False,
    is_event: bool = False,
) -> Tuple[float, str]:
    """
    Calcule le gain d'XP selon le tableau Bofuri RP.
    """
    # Pourcentages de base selon le type
    base_xp_percentages = {
        "commun": 0.015,  # Milieu de 1-2%
        "rare": 0.035,    # Milieu de 3-4%
        "elite": 0.05,    # Fixe à 5%
        "boss": 0.15,     # Base pour boss
    }

    mob_category = "boss" if is_boss else mob_type.lower()
    base_percentage = base_xp_percentages.get(mob_category, 0.015)

    # Cas particuliers des Boss de Donjon (Palier 1 & 2)
    if is_boss:
        low_name = mob_name.lower()
        if "hydre au poison" in low_name: base_percentage = 0.125
        elif "poisson tentaculaire" in low_name: base_percentage = 0.10
        elif "cerf de vie" in low_name: base_percentage = 0.175
        elif mob_level >= 60: base_percentage = 0.50 # High level boss
    
    # Calcul de la différence de niveau
    level_diff = player_level - mob_level
    final_percentage = base_percentage
    explanation = f"Base {base_percentage:.1%}"

    # Règle: Niveau joueur > niveau mob (Malus)
    if level_diff > 0:
        if level_diff > 10 and not is_boss:
            return 0.0, "Niveau trop élevé (>10 lvl d'écart)"
        
        if level_diff >= 10: 
            final_percentage /= 4.0
            explanation += " (÷4 car >10 lvl d'écart)"
        elif level_diff >= 5:
            final_percentage /= 2.0
            explanation += " (÷2 car >5 lvl d'écart)"
    
    # Règle: Niveau joueur < niveau mob (Bonus jusqu'à +5)
    elif level_diff < 0:
        diff_abs = abs(level_diff)
        bonus = min(diff_abs, 5) * 0.006 # +0.6% par niveau, max +3%
        final_percentage += bonus
        explanation += f" (+{bonus:.1%} bonus niveau)"

    return final_percentage, explanation


def calculate_xp_amount(
    player_level: int,
    mob_level: int,
    mob_type: str,
    mob_name: str,
    is_boss: bool = False,
    is_event: bool = False,
    xp_next_level: Optional[int] = None
) -> Tuple[int, str]:
    """
    Calcule le montant d'XP gagné en fonction du niveau du joueur, du niveau du mob et de son type.

    Args:
        player_level: Niveau du joueur
        mob_level: Niveau du mob
        mob_type: Type du mob ('commun', 'rare', 'elite')
        mob_name: Nom du mob (pour identifier certains boss spéciaux)
        is_boss: Indique si le mob est un boss
        is_event: Indique si le mob est un mob d'événement
        xp_next_level: XP nécessaire pour le prochain niveau (si None, calcule une valeur approximative)

    Returns:
        Tuple contenant le montant d'XP gagné et une description du calcul
    """
    # Calculer le pourcentage d'XP
    xp_percentage, explanation = calculate_xp_gain(
        player_level, mob_level, mob_type, mob_name, is_boss, is_event
    )

    # Si aucune XP n'est gagnée, retourner 0
    if xp_percentage <= 0:
        return 0, explanation

    # Si l'XP pour le prochain niveau n'est pas fournie, estimer une valeur
    if xp_next_level is None:
        # Formule approximative: 100 * (1.5 ^ (niveau - 1))
        xp_next_level = int(100 * (1.5 ** (player_level - 1)))

    # Calculer le montant d'XP
    xp_amount = int(xp_next_level * xp_percentage)

    # Assurer un minimum d'XP pour les mobs communs (au moins 1)
    if xp_amount < 1 and xp_percentage > 0:
        xp_amount = 1

    return xp_amount, explanation
