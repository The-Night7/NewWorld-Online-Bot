# app/character.py (VERSION AVEC stat_points)

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
import logging

logger = logging.getLogger('bofuri.character')


@dataclass
class Character:
    def __init__(self, user_id, name, level, xp, xp_next, hp, hp_max, mp, mp_max,
                 str_, agi, int_, dex, vit, gold=0, stat_points=0, skills=None):
        self.user_id = user_id
        self.name = name
        self.level = level
        self.xp = xp
        self.xp_next = xp_next
        self.hp = hp
        self.hp_max = hp_max
        self.mp = mp
        self.mp_max = mp_max
        self.STR = str_  # Uniformisation des noms d'attributs
        self.AGI = agi
        self.INT = int_
        self.DEX = dex
        self.VIT = vit
        self.gold = gold
        self.stat_points = stat_points
        self.skills = skills or []

    @classmethod
    async def from_db(cls, db, user_id: int) -> Optional["Character"]:
        """Load a character from the database."""
        row = await db.execute_fetchone(
            "SELECT * FROM characters WHERE user_id = ?",
            (int(user_id),)
        )
        if not row:
            return None
        
        # Load skills
        skills_rows = await db.execute_fetchall(
            "SELECT skill_id FROM character_skills WHERE user_id = ?",
            (int(user_id),)
        )
        skills = [r["skill_id"] for r in skills_rows]

        return cls(
            user_id=row["user_id"],
            name=row["name"],
            level=row["level"],
            xp=row["xp"],
            xp_next=row["xp_next"],
            hp=float(row["hp"]),
            hp_max=float(row["hp_max"]),
            mp=float(row["mp"]),
            mp_max=float(row["mp_max"]),
            str_=float(row["STR"]),
            agi=float(row["AGI"]),
            int_=float(row["INT"]),
            dex=float(row["DEX"]),
            vit=float(row["VIT"]),
            gold=row["gold"],
            stat_points=row.get("stat_points", 0),
            skills=skills,
        )

    async def save_to_db(self, db) -> None:
        """Save the character to the database."""
        await db.execute(
            """
            INSERT OR REPLACE INTO characters
            (user_id, name, level, xp, xp_next, hp, hp_max, mp, mp_max, STR, AGI, INT, DEX, VIT, gold, stat_points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(self.user_id),
                str(self.name),
                int(self.level),
                int(self.xp),
                int(self.xp_next),
                float(self.hp),
                float(self.hp_max),
                float(self.mp),
                float(self.mp_max),
                float(self.STR),
                float(self.AGI),
                float(self.INT),
                float(self.DEX),
                float(self.VIT),
                int(self.gold),
                int(self.stat_points),
            )
        )
        await db.commit()


async def create_character(db, user_id: int, name: str) -> Character:
    """Create a new character with default stats."""
    character = Character(
        user_id=int(user_id),
        name=str(name),
        level=1,
        xp=0,
        xp_next=1100,
        hp=100.0,
        hp_max=100.0,
        mp=50.0,
        mp_max=50.0,
        str_=10.0,
        agi=10.0,
        int_=10.0,
        dex=10.0,
        vit=10.0,
        gold=0,
        stat_points=0,
            )
    await character.save_to_db(db)
    return character


async def get_character(db, user_id: int) -> Optional[Character]:
    """Retrieve a character from the database."""
    return await Character.from_db(db, user_id)


async def get_or_create_character(db, user_id: int, name: str) -> Character:
    """Récupère un personnage ou en crée un nouveau s'il n'existe pas."""
    character = await get_character(db, user_id)
    if character is None:
        character = await create_character(db, user_id, name)
    return character


async def add_xp(db, user_id: int, xp_amount: int) -> Tuple[Character, bool, int]:
    """
    Add XP to a character and handle level-ups.
    Returns:
    - The updated character
    - A boolean indicating if the character leveled up
    - The number of levels gained
    """
    character = await get_character(db, user_id)
    if character is None:
        raise ValueError(f"No character found for user {user_id}")

    character.xp += int(xp_amount)
    levels_gained = 0
    leveled_up = False

    # Check if the character leveled up
    while character.xp >= character.xp_next:
        character.xp -= character.xp_next
        character.level += 1
        levels_gained += 1
        leveled_up = True

        # Calculate XP needed for the next level: 100 * L^2 + 1000 * L
        L = character.level
        character.xp_next = (100 * (L ** 2)) + (1000 * L)

        # Increase base stats with level
        character.hp_max += 10.0

        # Add stat points when leveling up
        character.stat_points += 5
    await character.save_to_db(db)
    return character, leveled_up, levels_gained


@dataclass
class InventoryItem:
    id: int
    character_id: int
    item_id: str
    quantity: int
    equipped: bool
    properties: Dict[str, Any]

    @classmethod
    def from_db_row(cls, row) -> "InventoryItem":
        return cls(
            id=row["id"],
            character_id=row["character_id"],
            item_id=row["item_id"],
            quantity=row["quantity"],
            equipped=bool(row["equipped"]),
            properties=json.loads(row["properties"]) if row["properties"] else {},
        )


async def get_inventory(db, user_id: int) -> List[InventoryItem]:
    rows = await db.execute_fetchall(
        "SELECT * FROM inventories WHERE character_id = ? ORDER BY id",
        (int(user_id),)
    )
    return [InventoryItem.from_db_row(r) for r in rows]


async def add_item_to_inventory(db, user_id: int, item_id: str, quantity: int = 1, properties: Dict[str, Any] | None = None) -> None:
    if properties is None:
        properties = {}

    existing_item = await db.execute_fetchone(
        "SELECT id, quantity FROM inventories WHERE character_id = ? AND item_id = ?",
        (int(user_id), str(item_id))
    )

    if existing_item:
        await db.execute(
                "UPDATE inventories SET quantity = quantity + ? WHERE id = ?",
                (int(quantity), int(existing_item["id"]))
        )
    else:
        await db.execute(
            """
            INSERT INTO inventories (character_id, item_id, quantity, equipped, properties)
            VALUES (?, ?, ?, 0, ?)
            """,
            (int(user_id), str(item_id), int(quantity), json.dumps(properties))
    )
    await db.commit()


async def remove_item_from_inventory(db, user_id: int, item_id: str, quantity: int = 1) -> bool:
    row = await db.execute_fetchone(
        "SELECT id, quantity FROM inventories WHERE character_id = ? AND item_id = ?",
        (int(user_id), str(item_id))
    )
    if not row:
        return False

    current_qty = int(row["quantity"])
    inv_id = int(row["id"])

    if current_qty <= int(quantity):
        await db.execute("DELETE FROM inventories WHERE id = ?", (inv_id,))
    else:
        await db.execute(
            "UPDATE inventories SET quantity = quantity - ? WHERE id = ?",
            (int(quantity), inv_id)
        )

    await db.commit()
    return True


async def equip_item(db, user_id: int, item_id: str) -> bool:
    row = await db.execute_fetchone(
        "SELECT id FROM inventories WHERE character_id = ? AND item_id = ? AND quantity > 0",
        (int(user_id), str(item_id))
    )
    if not row:
        return False

    await db.execute(
        "UPDATE inventories SET equipped = 1 WHERE id = ?",
        (int(row["id"]),)
    )
    await db.commit()
    return True


async def unequip_item(db, user_id: int, item_id: str) -> bool:
    row = await db.execute_fetchone(
        "SELECT id FROM inventories WHERE character_id = ? AND item_id = ? AND equipped = 1",
        (int(user_id), str(item_id))
    )
    if not row:
        return False

    await db.execute(
        "UPDATE inventories SET equipped = 0 WHERE id = ?",
        (int(row["id"]),)
    )
    await db.commit()
    return True