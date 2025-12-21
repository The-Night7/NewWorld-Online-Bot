# Générateur de modules "mobs" à partir de compendium.json
#
# Objectif:
# - créer 1 fichier .py par mob qui fait REGISTRY.register(MobDefinition(...))
# - conserver la "bonne typographie" côté affichage (accents, apostrophes, etc.) via display_name
# - utiliser des noms de fichiers sûrs (ascii, snake_case) et des keys stables (namespace.slug)
#
# Hypothèses (à adapter si besoin):
# - app.mobs.mob_types expose MobDefinition, MobStats
# - MobDefinition accepte au minimum: key, display_name, level_min, level_max, rarity, zone, drops, abilities, level_stats
# - level_stats est un dict[int, MobStats] avec les statistiques par niveau
#
# Si vos champs MobDefinition diffèrent, modifiez la fonction render_module().

from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Tuple


# --------- Slug / normalisation ---------

def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )


def snake_slug(s: str) -> str:
    """
    Transforme en slug ascii snake_case:
    - retire accents
    - remplace espaces/&/' etc.
    - supprime caractères non alphanum + underscore
    """
    s = s.strip()
    s = s.replace("&", " and ")
    s = s.replace("'", "'")
    s = strip_accents(s).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        return "mob"
    if s[0].isdigit():
        s = f"mob_{s}"
    return s


# --------- Mapping zone -> namespace de key ---------
#
# Ajustez pour coller à votre convention existante (ex: "forest.*").
#
ZONE_NAMESPACE = {
    "Forêt": "forest",
    "Forêt & Plaine": "forest_plains",
    "Forêt Palier 2": "forest_tier2",
    "Forêt du crépuscule": "twilight_forest",
    "Forêt du crépuscule & Montagne du soleil couchant": "twilight_sunset",
    "Donjon de l'Hydre": "hydra_dungeon",
    "Donjon de la Pêche": "fishing_dungeon",
    "Donjon de l'Arbre Honey": "honey_tree_dungeon",
    "Grotte cristalline": "crystal_cave",
    "Zone Fantôme": "ghost_zone",
    "Zone mécanique": "mechanical_zone",
    "Zone rocheuse & Grotte cristal": "rocky_crystal",
    "Zone corrompue": "corrupted_zone",
    "Plaines nuageuses": "cloud_plains",
    "Désert foudroyant": "thunder_desert",
    "Event": "event",
    "Event Secret": "event_secret",
    "Divers": "misc",
}


def compute_key(monster_id: str, zone: str | None) -> str:
    # monster_id vient des clés JSON (souvent avec accents). On le normalise pour la key.
    slug = snake_slug(monster_id)
    ns = ZONE_NAMESPACE.get(zone or "", None)
    if ns is None:
        # fallback: si zone manquante, on garde "misc"
        ns = "misc"
    return f"{ns}.{slug}"


# --------- Rendu module Python ---------

def py_str(s: str | None) -> str:
    if s is None:
        return "None"
    # JSON peut contenir des guillemets, on utilise repr() pour un littéral Python sûr.
    return repr(s)


def render_list_str(items: Any) -> str:
    if not items:
        return "None"
    if not isinstance(items, list):
        return "None"
    return "[" + ", ".join(py_str(x) for x in items) + "]"


def render_level_stats(variants: Dict[str, Any]) -> Tuple[str, int | None, int | None]:
    """
    Produit:
    - un littéral Python pour level_stats (dict[int, MobStats])
    - level_min, level_max déduits des keys si possible
    """
    if not variants:
        return "{}", None, None

    # keys JSON = "1", "10", etc.
    lvls = sorted(int(k) for k in variants.keys())
    level_min, level_max = lvls[0], lvls[-1]

    # On ne garde ici que les stats compatibles MobStats; le reste peut aller dans extra si votre MobDefinition le supporte.
    # D'après votre types.py: hp, mp, STR, AGI, INT, DEX, VIT
    lines = []
    lines.append("{")
    for k in lvls:
        v = variants[str(k)]
        hp = v.get("hp_max")
        mp = v.get("mp_max")
        STR = v.get("STR")
        AGI = v.get("AGI")
        INT = v.get("INT")
        DEX = v.get("DEX")
        VIT = v.get("VIT")
        lines.append(
            f"    {k}: MobStats(hp={float(hp)}, mp={float(mp)}, STR={float(STR)}, AGI={float(AGI)}, INT={float(INT)}, DEX={float(DEX)}, VIT={float(VIT)}, base_attack=0.0),"
        )
    lines.append("}")
    return "\n".join(lines), level_min, level_max


def render_module(monster_id: str, data: Dict[str, Any]) -> str:
    name = data.get("name") or monster_id
    zone = data.get("zone")
    rarity = data.get("rarity")
    abilities = data.get("abilities")
    drops = data.get("drops")

    variants = data.get("variants") or {}
    level_stats_py, level_min, level_max = render_level_stats(variants)

    # fallback si "level_range" est un format texte (ex "1-10" / "10")
    # On s'en sert si variants est vide.
    if (level_min is None or level_max is None) and isinstance(data.get("level_range"), str):
        lr = data["level_range"].strip()
        if re.fullmatch(r"\d+", lr):
            level_min = level_max = int(lr)
        else:
            m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", lr)
            if m:
                level_min, level_max = int(m.group(1)), int(m.group(2))

    key = compute_key(monster_id, zone)

    # Nom de fichier sûr
    module_slug = snake_slug(monster_id)

    # Utiliser level_stats au lieu de variants et le nouveau chemin d'import
    return f'''from app.mobs.registry import REGISTRY
from app.mobs.mob_types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key={py_str(key)},
        display_name={py_str(name)},
        level_min={level_min if level_min is not None else "None"},
        level_max={level_max if level_max is not None else "None"},
        rarity={py_str(rarity)},
        zone={py_str(zone)},
        drops={render_list_str(drops)},
        abilities={render_list_str(abilities)},
        level_stats={level_stats_py},
        variants={{}},
    )
)
'''


# --------- Main ---------

def main() -> None:
    here = Path(__file__).resolve().parent
    comp_path = here / "compendium.json"

    out_dir = here / "generated_mobs"
    out_dir.mkdir(parents=True, exist_ok=True)

    with comp_path.open("r", encoding="utf-8") as f:
        comp = json.load(f)

    monsters = comp.get("monsters", {})
    if not isinstance(monsters, dict):
        raise ValueError("compendium.json: 'monsters' doit être un objet")

    created = 0
    for monster_id, data in monsters.items():
        if not isinstance(data, dict):
            continue

        module_slug = snake_slug(monster_id)
        py = render_module(monster_id, data)
        target = out_dir / f"{module_slug}.py"
        target.write_text(py, encoding="utf-8")
        created += 1

    # init.py pour importer / discovery (selon votre système)
    (out_dir / "__init__.py").write_text(
        "# generated package\n", encoding="utf-8"
    )

    print(f"OK: {created} mobs générés dans: {out_dir}")


if __name__ == "__main__":
    main()