# Import registry and trigger mob discovery
from .registry import REGISTRY, discover_and_register
from .mob_types import MobDefinition, MobStats

# Discover and register all mobs
registry.discover_and_register("app.mobs.generated_mobs")