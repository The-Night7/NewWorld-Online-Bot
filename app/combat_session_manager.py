from __future__ import annotations

import random
import logging
from typing import List, Optional, Dict, Tuple

import discord

from .models import RuntimeEntity
from .dice import d20
from .rules import resolve_attack, AttackType
from .combat_mobs import save_mob_hp, fetch_mob_entity, cleanup_dead_mobs
from .cogs.combat import save_player_hp, fetch_player_entity

logger = logging.getLogger('bofuri.combat_session')

class CombatError(Exception):
    """Exception spécifique aux erreurs de combat"""
    pass

class CombatSession:
    """
    Classe qui gère l'état d'un combat et la logique du tour des mobs
    """
    def __init__(self, db, thread_id: int):
        self.db = db
        self.thread_id = thread_id
        self.participants: List[RuntimeEntity] = []
        self.current_turn_index = 0
        self.user_id_to_entity: Dict[int, RuntimeEntity] = {}
        self.mob_name_to_entity: Dict[str, RuntimeEntity] = {}
        
        # Utiliser des noms (strings) comme clés au lieu des objets RuntimeEntity
        self._entity_id_counter = 0
        self.entity_name_to_id: Dict[str, int] = {}  # Nom d'entité -> ID unique
        self.id_to_user_id: Dict[int, int] = {}      # ID unique -> ID utilisateur
        self.id_to_mob_name: Dict[int, str] = {}     # ID unique -> Nom du mob
    
    def _get_entity_id(self, entity: RuntimeEntity) -> int:
        """Attribue un ID unique à une entité si elle n'en a pas déjà un"""
        # Utiliser le nom de l'entité comme clé (string hashable)
        name = entity.name
        if name not in self.entity_name_to_id:
            self._entity_id_counter += 1
            self.entity_name_to_id[name] = self._entity_id_counter
        return self.entity_name_to_id[name]
    
    @property
    def current_actor(self) -> Optional[RuntimeEntity]:
        """Retourne l'entité dont c'est le tour actuellement"""
        if not self.participants:
            return None
        return self.participants[self.current_turn_index]
    
    async def load_participants(self) -> None:
        """Charge tous les participants (joueurs et mobs) du combat"""
        from .combat_session import participants_list
        from .combat_mobs import list_mobs
        
        # Charger les joueurs
        user_ids = await participants_list(self.db, self.thread_id)
        for user_id in user_ids:
            try:
                entity = await fetch_player_entity(self.db, int(user_id))
                entity.is_mob = False
                self.participants.append(entity)
                self.user_id_to_entity[int(user_id)] = entity
                
                # Stocker l'ID utilisateur avec l'ID d'entité
                entity_id = self._get_entity_id(entity)
                self.id_to_user_id[entity_id] = int(user_id)
            except Exception as e:
                logger.error(f"Erreur lors du chargement du joueur {user_id}: {e}")
        
        # Charger les mobs
        mob_rows = await list_mobs(self.db, self.thread_id)
        for mob_row in mob_rows:
            try:
                mob_name = mob_row["mob_name"]
                entity = await fetch_mob_entity(self.db, self.thread_id, mob_name)
                entity.is_mob = True
                self.participants.append(entity)
                self.mob_name_to_entity[mob_name] = entity
                
                # Stocker le nom du mob avec l'ID d'entité
                entity_id = self._get_entity_id(entity)
                self.id_to_mob_name[entity_id] = mob_name
            except Exception as e:
                logger.error(f"Erreur lors du chargement du mob {mob_row['mob_name']}: {e}")
        
        # Trier les participants par AGI (décroissant)
        self.participants.sort(key=lambda x: x.AGI, reverse=True)
    
    def advance_turn(self) -> bool:
        """
        Passe au participant suivant qui est encore en vie.
        Retourne True si un participant vivant a été trouvé, False sinon.
        """
        if not self.participants:
            return False
        
        # On boucle pour trouver le prochain VIVANT
        # On ajoute une sécurité (max_loops) pour éviter une boucle infinie si tout le monde est mort
        max_loops = len(self.participants) + 1
        loops = 0
        
        while loops < max_loops:
            # Passage à l'index suivant
            self.current_turn_index = (self.current_turn_index + 1) % len(self.participants)
            candidate = self.participants[self.current_turn_index]
            
            # Si le candidat est en vie, c'est bon, on arrête de chercher
            if candidate.hp > 0:
                return True
                
            loops += 1
        
        # Si on arrive ici, c'est que tout le monde est mort ou bug
        return False
    
    def get_mob_target(self, mob_entity: RuntimeEntity) -> Optional[RuntimeEntity]:
        """
        Détermine la cible d'un mob selon la logique:
        1. Si provoqué et la cible est en vie -> Attaque la cible
        2. Sinon -> Attaque un joueur aléatoire en vie
        """
        # Filtrer les participants pour ne garder que les joueurs vivants
        alive_players = [p for p in self.participants if not p.is_mob and p.hp > 0]
        
        if not alive_players:
            return None  # Plus de joueurs en vie
        
        # 1. Vérification de la provocation
        if mob_entity.provoked_by and mob_entity.provoked_by in alive_players:
            return mob_entity.provoked_by
        else:
            # Réinitialiser la provocation si la cible n'est plus valide
            mob_entity.provoked_by = None
            
        # 2. Sélection aléatoire
        return random.choice(alive_players)
    
    async def execute_mob_turn(self, mob_entity: RuntimeEntity, channel: discord.TextChannel) -> None:
        """Exécute le tour d'un mob"""
        # Sécurité: vérifier que le mob est en vie
        if mob_entity.hp <= 0:
            logger.warning(f"Tentative d'exécuter le tour d'un mob mort: {mob_entity.name}")
            return
            
        target = self.get_mob_target(mob_entity)
        
        if not target:
            await channel.send(f"🤔 **{mob_entity.name}** ne trouve personne à attaquer...")
            return
        
        # Déterminer le type d'attaque (simple pour l'instant)
        attack_type: AttackType = "phys"
        if mob_entity.INT > mob_entity.STR:
            attack_type = "magic"
        elif mob_entity.DEX > mob_entity.STR:
            attack_type = "ranged"
        
        # Lancer les dés pour l'attaque
        roll_a = d20()
        roll_b = d20()
        
        # Résoudre l'attaque
        result = resolve_attack(mob_entity, target, roll_a, roll_b, attack_type=attack_type)
        
        # Sauvegarder les HP de la cible si c'est un joueur
        if not target.is_mob:
            # Utiliser l'ID d'entité pour récupérer l'ID utilisateur
            entity_id = self._get_entity_id(target)
            user_id = self.id_to_user_id.get(entity_id)
            if user_id:
                await save_player_hp(self.db, user_id, target.hp)
        
        # Créer un message pour l'attaque
        color = discord.Color.red() if result["hit"] else discord.Color.dark_gray()
        embed = discord.Embed(title=f"⚔️ {mob_entity.name} attaque {target.name}", color=color)
        
        embed.add_field(name="Type", value=str(attack_type), inline=True)
        embed.add_field(name="Jet attaquant (d20)", value=str(roll_a), inline=True)
        embed.add_field(name="Jet défenseur (d20)", value=str(roll_b), inline=True)
        
        if result["hit"]:
            embed.add_field(name="Dégâts", value=f'{result["raw"]["damage"]:.2f}', inline=True)
            embed.add_field(name="PV restants", value=f'{target.hp:.0f}/{target.hp_max:.0f}', inline=True)
        else:
            embed.add_field(name="Résultat", value="Attaque esquivée/bloquée", inline=True)
        
        embed.add_field(
            name="Log",
            value="\n".join(result["effects"]) if result["effects"] else "—",
            inline=False,
        )
        
        await channel.send(embed=embed)

    def get_user_id_for_entity(self, entity: RuntimeEntity) -> Optional[int]:
        """Récupère l'ID utilisateur associé à une entité"""
        entity_id = self._get_entity_id(entity)
        return self.id_to_user_id.get(entity_id)
    
    def get_mob_name_for_entity(self, entity: RuntimeEntity) -> Optional[str]:
        """Récupère le nom du mob associé à une entité"""
        entity_id = self._get_entity_id(entity)
        return self.id_to_mob_name.get(entity_id)

async def get_or_create_session(db, thread_id: int) -> CombatSession:
    """Récupère ou crée une session de combat pour un thread donné"""
    session = CombatSession(db, thread_id)
    await session.load_participants()
    return session