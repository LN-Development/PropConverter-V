import bpy
from typing import List


def collect_model_meshes(parent: bpy.types.Object) -> List[bpy.types.Object]:
    found = []
    if not parent:
        return found
    for child in parent.children:
        if child.type == 'MESH' and (child.name.endswith('.model') or getattr(child, 'sollum_type', None) is not None and 'MODEL' in str(child.sollum_type)):
            found.append(child)
        found.extend(collect_model_meshes(child))
    return found
