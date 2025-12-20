# Import registry and trigger mob discovery
from . import registry
from .registry import REGISTRY

# Discover and register all mobs
registry.discover_and_register("app.mobs.generated_mobs")