import bpy
import importlib


def convert_materials(context, model_objs, mod_name: str) -> bool:
    """Convert materials on model objects to the selected shader."""
    try:
        shadermats = importlib.import_module(f"{mod_name}.ydr.shader_materials").shadermats
        wm = context.window_manager
        selected_idx = getattr(wm, "sz_shader_material_index", -1)
        
        if not (0 <= selected_idx < len(shadermats)):
            selected_idx = next((i for i, shader in enumerate(shadermats) if shader.value == "default.sps"), None)
            if selected_idx is None:
                print("[ERROR] Could not find default.sps shader")
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
            original_mesh = scene_props.original_mesh if scene_props else None
            if original_mesh:
                original_name = original_mesh.name
                ok_textures = set_textures_from_original_name(context, model_objs, original_name)
                if not ok_textures:
                    print("[WARNING] Failed to set texture parameters; continuing")
            else:
                print("[WARNING] Original mesh not found, skipping texture parameter setup")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to convert materials - {e}")
        return False
