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
    skill_points: int
    gold: int
    skills: List[str] = field(default_factory=list)

    @classmethod
    async def from_db(cls, db, user_id: int) -> Optional[Character]:
        """Charge un personnage depuis la base de données"""
        row = await db.execute_fetchone(
            "SELECT * FROM characters WHERE user_id = ?",
            (user_id,)
        )
    
        if not row:
            return None
        
        # Charger les compétences
        skills_rows = await db.execute_fetchall(
            "SELECT skill_id FROM character_skills WHERE user_id = ?",
            (user_id,)
        )
        skills = [r['skill_id'] for r in skills_rows]
        
        return cls(
            user_id=row['user_id'],
            name=row['name'],
            level=row['level'],
            xp=row['xp'],
            xp_next=row['xp_next'],
            hp=float(row['hp']),
            hp_max=float(row['hp_max']),
            mp=float(row['mp']),
            mp_max=float(row['mp_max']),
            STR=float(row['STR']),
            AGI=float(row['AGI']),
            INT=float(row['INT']),
            DEX=float(row['DEX']),
            VIT=float(row['VIT']),
            skill_points=row['skill_points'],
            gold=row['gold'],
            skills=skills
        )

    async def save_to_db(self, db) -> None:
        """Sauvegarde le personnage dans la base de données"""
        await db.execute(
            """
            INSERT OR REPLACE INTO characters 
            (user_id, name, level, xp, xp_next, hp, hp_max, mp, mp_max, STR, AGI, INT, DEX, VIT, skill_points, gold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.user_id, self.name, self.level, self.xp, self.xp_next,
                self.hp, self.hp_max, self.mp, self.mp_max,
                self.STR, self.AGI, self.INT, self.DEX, self.VIT,
                self.skill_points, self.gold
            )
        )
        await db.commit()


@dataclass
class InventoryItem:
    id: int
    character_id: int
    item_id: str
    quantity: int
    equipped: bool
    properties: Dict[str, Any]
    
    @classmethod
    def from_db_row(cls, row) -> InventoryItem:
        """Crée un objet d'inventaire à partir d'une ligne de la base de données"""
        return cls(
            id=row['id'],
            character_id=row['character_id'],
            item_id=row['item_id'],
            quantity=row['quantity'],
            equipped=bool(row['equipped']),
            properties=json.loads(row['properties']) if row['properties'] else {}
        )


async def create_character(db, user_id: int, name: str) -> Character:
    """Crée un nouveau personnage avec des statistiques par défaut"""
    # Statistiques de base pour un personnage de niveau 1
    character = Character(
        user_id=user_id,
        name=name,
        level=1,
        xp=0,
        xp_next=100,  # XP nécessaire pour le niveau 2
        hp=100.0,
        hp_max=100.0,
        mp=50.0,
        mp_max=50.0,
        STR=10.0,
        AGI=10.0,
        INT=10.0,
        DEX=10.0,
        VIT=10.0,
        skill_points=0,
        gold=0
    )
    
    await character.save_to_db(db)
    return character


async def get_character(db, user_id: int) -> Optional[Character]:
    """Récupère un personnage depuis la base de données"""
    return await Character.from_db(db, user_id)


async def get_or_create_character(db, user_id: int, name: str) -> Character:
    """Récupère un personnage ou en crée un nouveau s'il n'existe pas"""
    character = await get_character(db, user_id)
    if character is None:
        character = await create_character(db, user_id, name)
    return character


async def add_xp(db, user_id: int, xp_amount: int) -> Tuple[Character, bool, int]:
    """
    Ajoute de l'XP à un personnage et gère la montée de niveau
    
    Retourne:
    - Le personnage mis à jour
    - Un booléen indiquant si le personnage a gagné un niveau
    - Le nombre de niveaux gagnés
    """
    character = await get_character(db, user_id)
    if character is None:
        raise ValueError(f"Aucun personnage trouvé pour l'utilisateur {user_id}")
    
    old_level = character.level
    character.xp += xp_amount
    
    levels_gained = 0
    leveled_up = False
    
    # Vérifier si le personnage a gagné un niveau
    while character.xp >= character.xp_next:
        character.xp -= character.xp_next
        character.level += 1
        levels_gained += 1
        leveled_up = True
        
        # Augmenter les points de compétence
        character.skill_points += 3
        
        # Calculer l'XP nécessaire pour le prochain niveau (formule personnalisable)
        character.xp_next = int(character.xp_next * 1.5)
        
        # Augmenter les statistiques de base avec le niveau
        character.hp_max += 10
        character.mp_max += 5
        character.hp = character.hp_max
        character.mp = character.mp_max
    
    await character.save_to_db(db)
    return character, leveled_up, levels_gained


async def add_item_to_inventory(db, user_id: int, item_id: str, quantity: int = 1, properties: Dict[str, Any] = None) -> None:
    """Ajoute un objet à l'inventaire d'un personnage"""
    if properties is None:
        properties = {}
    
        # Vérifier si l'objet existe déjà dans l'inventaire
        existing_item = await db.execute_fetchone(
            "SELECT id, quantity FROM inventories WHERE character_id = ? AND item_id = ?",
            (user_id, item_id)
        )
    
        if existing_item:
            # Mettre à jour la quantité
            await db.execute(
                "UPDATE inventories SET quantity = quantity + ? WHERE id = ?",
                (quantity, existing_item['id'])
            )
        else:
            # Ajouter un nouvel objet
            await db.execute(
                """
                INSERT INTO inventories (character_id, item_id, quantity, equipped, properties)
                VALUES (?, ?, ?, 0, ?)
                """,
                (user_id, item_id, quantity, json.dumps(properties))
            )
    
    await db.commit()


async def get_inventory(db, user_id: int) -> List[InventoryItem]:
    """Récupère l'inventaire complet d'un personnage"""
    async with db.execute(
        "SELECT * FROM inventories WHERE character_id = ?",
        (user_id,)
    ) as cursor:
        rows = await cursor.fetchall()
    
    return [InventoryItem.from_db_row(row) for row in rows]


async def remove_item_from_inventory(db, user_id: int, item_id: str, quantity: int = 1) -> bool:
    """
    Retire un objet de l'inventaire d'un personnage
    
    Retourne True si l'opération a réussi, False sinon
    """
    async with db.execute(
        "SELECT id, quantity FROM inventories WHERE character_id = ? AND item_id = ?",
        (user_id, item_id)
    ) as cursor:
        existing_item = await cursor.fetchone()
    
    if not existing_item:
        return False
    
    if existing_item['quantity'] <= quantity:
        # Supprimer l'objet
        await db.execute(
            "DELETE FROM inventories WHERE id = ?",
            (existing_item['id'],)
        )
    else:
        # Réduire la quantité
        await db.execute(
            "UPDATE inventories SET quantity = quantity - ? WHERE id = ?",
            (quantity, existing_item['id'])
        )
    
    await db.commit()
    return True


async def equip_item(db, user_id: int, item_id: str) -> bool:
    """
    Équipe un objet pour un personnage
    
    Retourne True si l'opération a réussi, False sinon
    """
    async with db.execute(
        "SELECT id FROM inventories WHERE character_id = ? AND item_id = ? AND quantity > 0",
        (user_id, item_id)
    ) as cursor:
        item = await cursor.fetchone()
    
    if not item:
        return False
    
    await db.execute(
        "UPDATE inventories SET equipped = 1 WHERE id = ?",
        (item['id'],)
    )
    await db.commit()
    return True


async def unequip_item(db, user_id: int, item_id: str) -> bool:
    """
    Déséquipe un objet pour un personnage
    
    Retourne True si l'opération a réussi, False sinon
    """
    async with db.execute(
        "SELECT id FROM inventories WHERE character_id = ? AND item_id = ? AND equipped = 1",
        (user_id, item_id)
    ) as cursor:
        item = await cursor.fetchone()
    
    if not item:
        return False
    
    await db.execute(
        "UPDATE inventories SET equipped = 0 WHERE id = ?",
        (item['id'],)
    )
    await db.commit()
    return True