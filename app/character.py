# app/character.py (VERSION SANS skill_points)

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
import logging

logger = logging.getLogger('bofuri.character')


@dataclass
class Character:
    user_id: int
    name: str
    level: int
    xp: int
    xp_next: int
    hp: float
    hp_max: float
    mp: float
    mp_max: float
    STR: float
    AGI: float
    INT: float
    DEX: float
    VIT: float
    gold: int
    skills: List[str] = field(default_factory=list)

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
            STR=float(row["STR"]),
            AGI=float(row["AGI"]),
            INT=float(row["INT"]),
            DEX=float(row["DEX"]),
            VIT=float(row["VIT"]),
            gold=row["gold"],
            skills=skills,
        )

    async def save_to_db(self, db) -> None:
        """Save the character to the database."""
        await db.execute(
            """
            INSERT OR REPLACE INTO characters
            (user_id, name, level, xp, xp_next, hp, hp_max, mp, mp_max, STR, AGI, INT, DEX, VIT, gold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        STR=10.0,
        AGI=10.0,
        INT=10.0,
        DEX=10.0,
        VIT=10.0,
        gold=0,
    )
    await character.save_to_db(db)
    return character


async def get_character(db, user_id: int) -> Optional[Character]:
    """Retrieve a character from the database."""
    return await Character.from_db(db, user_id)


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

    await character.save_to_db(db)
    return character, leveled_up, levels_gained


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
    return True