import bpy
from ...sollumz_integration import SollumzIntegration
from ... import constants


def convert_materials(context, model_objs, mod_name: str, original_name: str = None) -> bool:
    """Convert materials on model objects to the selected shader.
    
    Args:
        context: Blender context
        model_objs: List of model objects to convert materials for
        mod_name: Sollumz module name
        original_name: Original mesh name (before conversion) for texture naming
    """
    try:
        sollumz = SollumzIntegration.get_instance()
        shadermats = sollumz.get_shader_materials()
        
        if not shadermats:
            print("[ERROR] Could not load Sollumz shader materials")
            return False
        
        wm = context.window_manager
        selected_idx = getattr(wm, "sz_shader_material_index", -1)
        
        if not (0 <= selected_idx < len(shadermats)):
            selected_idx = next(
                (i for i, shader in enumerate(shadermats) 
                 if shader.value == constants.DEFAULT_SHADER_NAME), 
                None
            )
            if selected_idx is None:
                print(f"[ERROR] Could not find {constants.DEFAULT_SHADER_NAME} shader")
                return False
            wm.sz_shader_material_index = selected_idx

        if model_objs:
            bpy.ops.object.select_all(action='DESELECT')
            for m in model_objs:
                m.select_set(True)
            context.view_layer.objects.active = model_objs[0]

        bpy.ops.sollumz.convertallmaterialstoselected()
        
        # Set texture parameters after conversion (only if auto texture is enabled)
        from .set_textures import set_textures_from_original_name
        scene_props = getattr(context.scene, "prop_converter", None)
        
        # Check if auto texture feature is enabled
        if scene_props and getattr(scene_props, "auto_texture_from_mesh_name", False):
            # Use the passed original_name if provided, otherwise fall back to stored mesh name
            texture_name = original_name
            if not texture_name:
                original_mesh = scene_props.original_mesh if scene_props else None
                if original_mesh:
                    texture_name = original_mesh.name
            
            if texture_name:
                ok_textures = set_textures_from_original_name(context, model_objs, texture_name)
                if not ok_textures:
                    print("[WARNING] Failed to set texture parameters; continuing")
            else:
                print("[WARNING] Original mesh name not found, skipping texture parameter setup")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to convert materials - {e}")
        return False
