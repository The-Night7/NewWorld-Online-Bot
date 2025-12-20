from app.mobs.registry import REGISTRY
from app.mobs.types import MobDefinition, MobStats


REGISTRY.register(
    MobDefinition(
        key='crystal_cave.araignee_des_grottes',
        display_name='Araignée des grottes',
        level_min=40,
        level_max=45,
        rarity=None,
        zone='Grotte cristalline',
        drops=['Toile cristalline', "Œufs d'araignée rare"],
        abilities=['Entoilement de poison:  Immobilise + Poison +5% + Statuts "immobile" & "empoisonné"', 'Entoilement de poison:  Immobilise + Poison +5% + Statuts "immobile" & "empoisonné"'],
        variants={
    40: MobStats(hp=3000.0, mp=220.0, STR=120.0, AGI=110.0, INT=70.0, DEX=130.0, VIT=115.0),
    45: MobStats(hp=3500.0, mp=270.0, STR=145.0, AGI=130.0, INT=85.0, DEX=155.0, VIT=135.0),
},
    )
)
