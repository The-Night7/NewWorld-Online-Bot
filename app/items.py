from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger('bofuri.items')

@dataclass
class ItemDefinition:
    item_id: str
    name: str
    description: str
    type: str  # weapon, armor, consumable, material, etc.
    rarity: str  # common, uncommon, rare, epic, legendary
    value: int  # valeur en or
    properties: Dict[str, Any]  # propriétés spécifiques (dégâts, défense, etc.)
    
    @classmethod
    async def from_db(cls, db, item_id: str) -> Optional[ItemDefinition]:
        # Charge une définition d'objet depuis la base de données
        async with db.conn.execute(
            "SELECT * FROM items WHERE item_id = ?",
            (item_id,)
        ) as cursor:
            row = await cursor.fetchone()
            
        if not row:
            return None
            
        return cls(
            item_id=row['item_id'],
            name=row['name'],
            description=row['description'] or "",
            type=row['type'],
            rarity=row['rarity'],
            value=row['value'],
            properties=json.loads(row['properties']) if row['properties'] else {}
        )
    
    async def save_to_db(self, db):
        # Convertir les propriétés en JSON
        properties_json = json.dumps(self.properties)
        
        # Insérer ou mettre à jour l'objet dans la base de données
        await db.conn.execute(
            """
            INSERT INTO items (item_id, name, description, type, rarity, value, properties)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(item_id) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                type = excluded.type,
                rarity = excluded.rarity,
                value = excluded.value,
                properties = excluded.properties
            """,
            (self.item_id, self.name, self.description, self.type, self.rarity, self.value, properties_json)
        )
        await db.conn.commit()


# Registre des objets (similaire au registre des mobs)
class ItemRegistry:
    def __init__(self):
        self._items: Dict[str, ItemDefinition] = {}
    
    def register(self, item: ItemDefinition) -> None:
        """Enregistre une définition d'objet"""
        if item.item_id in self._items:
            raise ValueError(f"Objet déjà enregistré: {item.item_id}")
        self._items[item.item_id] = item
    
    def get(self, item_id: str) -> Optional[ItemDefinition]:
        """Récupère une définition d'objet par son ID"""
        return self._items.get(item_id)
    
    def all(self) -> List[ItemDefinition]:
        """Récupère toutes les définitions d'objets"""
        return list(self._items.values())
    
    def by_type(self, type_name: str) -> List[ItemDefinition]:
        """Récupère toutes les définitions d'objets d'un type spécifique"""
        return [item for item in self._items.values() if item.type == type_name]
    
    def by_rarity(self, rarity: str) -> List[ItemDefinition]:
        """Récupère toutes les définitions d'objets d'une rareté spécifique"""
        return [item for item in self._items.values() if item.rarity == rarity]


# Créer une instance globale du registre
ITEM_REGISTRY = ItemRegistry()


# Fonction pour initialiser quelques objets de base
async def initialize_basic_items(db) -> None:
    """Initialise quelques objets de base dans la base de données"""
    basic_items = [
        ItemDefinition(
            item_id="weapon.sword.basic",
            name="Épée basique",
            description="Une épée simple mais efficace.",
            type="weapon",
            rarity="common",
            value=50,
            properties={
                "damage": 5,
                "weapon_type": "sword",
                "two_handed": False
            }
        ),
        ItemDefinition(
            item_id="weapon.bow.basic",
            name="Arc court",
            description="Un arc léger pour les débutants.",
            type="weapon",
            rarity="common",
            value=45,
            properties={
                "damage": 4,
                "weapon_type": "bow",
                "two_handed": True,
                "range": 20
            }
        ),
        ItemDefinition(
            item_id="armor.leather.basic",
            name="Armure en cuir",
            description="Une armure légère offrant une protection de base.",
            type="armor",
            rarity="common",
            value=40,
            properties={
                "defense": 3,
                "armor_type": "light",
                "weight": 5
            }
        ),
        ItemDefinition(
            item_id="consumable.potion.health",
            name="Potion de soin",
            description="Restaure 50 points de vie.",
            type="consumable",
            rarity="common",
            value=20,
            properties={
                "effect": "heal",
                "amount": 50,
                "duration": 0
            }
        ),
        ItemDefinition(
            item_id="consumable.potion.mana",
            name="Potion de mana",
            description="Restaure 30 points de mana.",
            type="consumable",
            rarity="common",
            value=25,
            properties={
                "effect": "restore_mana",
                "amount": 30,
                "duration": 0
            }
        ),
        ItemDefinition(
            item_id="material.herb.common",
            name="Herbe commune",
            description="Une herbe que l'on trouve facilement dans la forêt.",
            type="material",
            rarity="common",
            value=5,
            properties={
                "crafting_category": "alchemy",
                "crafting_value": 1
            }
        )
    ]
    
    # Enregistrer les objets dans le registre et la base de données
    for item in basic_items:
        ITEM_REGISTRY.register(item)
        await item.save_to_db(db)
    
    logger.info(f"Initialisé {len(basic_items)} objets de base")