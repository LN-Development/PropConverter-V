import bpy
from typing import Optional, Tuple
from .collect_model_meshes import collect_model_meshes


def convert_drawable(context, obj: bpy.types.Object, composite_obj: Optional[bpy.types.Object]) -> Tuple[list, Optional[bpy.types.Object]]:
    """Convert to drawable and parent collision structure."""
    try:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.sollumz.converttodrawable()
        print(f"Successfully converted '{obj.name}' to drawable")

        drawable_parent = obj.parent
        if drawable_parent:
            model_objs = collect_model_meshes(drawable_parent)
            if model_objs:
                print(f"Found drawable models: {[m.name for m in model_objs]}")
            else:
                print("WARNING: Could not find .model child, using original object")
                model_objs = [obj]
        else:
            print("WARNING: No drawable parent found, using original object")
            model_objs = [obj]

        if composite_obj:
            if drawable_parent:
                print(f"Parenting collision composite {composite_obj.name} to drawable {drawable_parent.name}")
                composite_obj.parent = drawable_parent
                composite_obj.location = (0, 0, 0)
                print(f"Successfully parented collision structure to drawable {drawable_parent.name}")
            else:
                print("WARNING: Mesh has no drawable parent, parenting composite to mesh instead")
                composite_obj.parent = obj
                composite_obj.location = (0, 0, 0)

        return model_objs, drawable_parent
    except Exception as e:
        print(f"ERROR: Failed to convert to drawable - {e}")
        import traceback
        traceback.print_exc()
        return None, None
