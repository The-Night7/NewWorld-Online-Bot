from typing import Dict, Any, Literal
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
