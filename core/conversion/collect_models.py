import bpy
from typing import List, Optional


def collect_model_meshes(parent: bpy.types.Object) -> Optional[List[bpy.types.Object]]:
    """Collect all .model child meshes from drawable parent."""
    models = []
    for child in parent.children:
        if child.sollum_type == "Drawable Model":
            models.append(child)
    return models if models else None
