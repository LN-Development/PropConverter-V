import bpy
from typing import Optional, Tuple
from .collect_models import collect_model_meshes
from .debug_utils import log_pre_conversion, log_post_conversion, log_mesh_internals


def convert_drawable(context, obj: bpy.types.Object, composite_obj: Optional[bpy.types.Object]) -> Tuple[list, Optional[bpy.types.Object]]:
    """Convert to drawable and parent collision structure."""
    try:
        # Select object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Convert to drawable
        bpy.ops.sollumz.converttodrawable()
        
        # Update scene
        context.view_layer.update()
        context.evaluated_depsgraph_get()

        # Get parent and collect models
        drawable_parent = obj.parent
        if drawable_parent:
            model_objs = collect_model_meshes(drawable_parent)
            if not model_objs:
                print("[WARNING] Could not find .model child, using original object")
                model_objs = [obj]
        else:
            print("[WARNING] No drawable parent found, using original object")
            model_objs = [obj]

        # Parent collision composite if present
        if composite_obj:
            if drawable_parent:
                composite_obj.parent = drawable_parent
                composite_obj.location = (0, 0, 0)
            else:
                print("[WARNING] Mesh has no drawable parent, parenting composite to mesh instead")
                composite_obj.parent = obj
                composite_obj.location = (0, 0, 0)

        return model_objs, drawable_parent
    except Exception as e:
        print(f"[ERROR] Failed to convert to drawable - {e}")
        return None, None
