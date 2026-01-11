import bpy
from typing import Optional, Tuple
from .collect_models import collect_model_meshes
from .debug_utils import log_pre_conversion, log_post_conversion, log_mesh_internals


def convert_drawable(context, obj: bpy.types.Object, composite_obj: Optional[bpy.types.Object]) -> Tuple[list, Optional[bpy.types.Object]]:
    """Convert to drawable and parent collision structure."""
    try:
        print("\n" + "="*80)
        print("[STAGE] convert_drawable: ENTRY")
        print(f"[DEBUG] Input object: {obj.name}")
        print(f"[DEBUG]   Mesh loops before conversion: {len(obj.data.loops)}")
        print(f"[DEBUG]   Mesh vertices before conversion: {len(obj.data.vertices)}")
        print(f"[DEBUG]   Mesh polygons before conversion: {len(obj.data.polygons)}")
        print(f"[DEBUG]   Color attributes before conversion: {list(obj.data.color_attributes.keys())}")
        print(f"[DEBUG]   Has custom normals: {obj.data.has_custom_normals if hasattr(obj.data, 'has_custom_normals') else 'N/A'}")
        
        print("[SOLLUMZ] Selecting object for converttodrawable...")
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Log pre-conversion state
        log_pre_conversion(obj)
        
        print("[SOLLUMZ] Executing sollumz.converttodrawable()...")
        bpy.ops.sollumz.converttodrawable()
        print(f"[SOLLUMZ] Successfully converted '{obj.name}' to drawable")
        
        print("[UPDATE] Forcing complete scene update to finalize mesh data...")
        context.view_layer.update()
        context.evaluated_depsgraph_get()
        print("[UPDATE] Scene update complete")
        
        # Log post-conversion state
        log_post_conversion(obj)
        log_mesh_internals(context, obj)
        
        print(f"[DEBUG]   Mesh loops after conversion: {len(obj.data.loops) if obj.type == 'MESH' else 'N/A'}")
        print(f"[DEBUG]   Mesh vertices after conversion: {len(obj.data.vertices)}")
        print(f"[DEBUG]   Mesh polygons after conversion: {len(obj.data.polygons)}")
        print(f"[DEBUG]   Color attributes after conversion: {list(obj.data.color_attributes.keys())}")
        print(f"[DEBUG]   Has custom normals after: {obj.data.has_custom_normals if hasattr(obj.data, 'has_custom_normals') else 'N/A'}")

        drawable_parent = obj.parent
        if drawable_parent:
            print(f"[PARENT] Found drawable parent: {drawable_parent.name}")
            model_objs = collect_model_meshes(drawable_parent)
            if model_objs:
                print(f"[MODELS] Found {len(model_objs)} drawable models: {[m.name for m in model_objs]}")
                for m in model_objs:
                    print(f"[DEBUG]   Model: {m.name}")
                    print(f"[DEBUG]     - Loops: {len(m.data.loops)}")
                    print(f"[DEBUG]     - Vertices: {len(m.data.vertices)}")
                    print(f"[DEBUG]     - Polygons: {len(m.data.polygons)}")
                    print(f"[DEBUG]     - Color attributes: {list(m.data.color_attributes.keys())}")
            else:
                print("[WARNING] Could not find .model child, using original object")
                model_objs = [obj]
        else:
            print("[WARNING] No drawable parent found, using original object")
            model_objs = [obj]

        if composite_obj:
            if drawable_parent:
                print(f"[PARENT] Parenting collision composite {composite_obj.name} to drawable {drawable_parent.name}")
                composite_obj.parent = drawable_parent
                composite_obj.location = (0, 0, 0)
                print(f"[PARENT] Successfully parented collision structure")
            else:
                print("[WARNING] Mesh has no drawable parent, parenting composite to mesh instead")
                composite_obj.parent = obj
                composite_obj.location = (0, 0, 0)

        print("[STAGE] convert_drawable: EXIT")
        print(f"[DEBUG] Returning {len(model_objs)} model objects")
        print("="*80 + "\n")
        return model_objs, drawable_parent
    except Exception as e:
        print(f"[ERROR] Failed to convert to drawable - {e}")
        import traceback
        traceback.print_exc()
        print("[STAGE] convert_drawable: ERROR EXIT")
        print("="*80 + "\n")
        return None, None
