import bpy
import importlib


def convert_materials(context, model_objs, mod_name: str) -> bool:
    """Convert materials on model objects to the selected shader."""
    try:
        print("\n" + "="*80)
        print("[STAGE] convert_materials: ENTRY")
        print(f"[DEBUG] Input model objects count: {len(model_objs) if model_objs else 0}")
        
        shadermats = importlib.import_module(f"{mod_name}.ydr.shader_materials").shadermats
        wm = context.window_manager
        selected_idx = getattr(wm, "sz_shader_material_index", -1)
        
        print(f"[SHADER] Available shaders: {[s.value for s in shadermats[:5]]}...({len(shadermats)} total)")
        print(f"[SHADER] Selected shader index: {selected_idx}")
        
        if not (0 <= selected_idx < len(shadermats)):
            selected_idx = next((i for i, shader in enumerate(shadermats) if shader.value == "default.sps"), None)
            if selected_idx is None:
                print("[ERROR] Could not find default.sps shader")
                return False
            wm.sz_shader_material_index = selected_idx
            print(f"[SHADER] Selected shader index invalid; falling back to default.sps at {selected_idx}")
        else:
            print(f"[SHADER] Using user-selected shader: {shadermats[selected_idx].value}")

        if model_objs:
            print(f"[SOLLUMZ] Selecting {len(model_objs)} model objects for material conversion...")
            bpy.ops.object.select_all(action='DESELECT')
            for m in model_objs:
                m.select_set(True)
            context.view_layer.objects.active = model_objs[0]
            print(f"[DEBUG] Selected objects: {[m.name for m in model_objs]}")
            for m in model_objs:
                print(f"[DEBUG]   PRE-CONVERSION {m.name}:")
                print(f"[DEBUG]     - Loops: {len(m.data.loops)}, Vertices: {len(m.data.vertices)}, Polygons: {len(m.data.polygons)}")
                print(f"[DEBUG]     - Color attributes: {list(m.data.color_attributes.keys())}")
                print(f"[DEBUG]     - Material slots: {len(m.material_slots)}")
                print(f"[DEBUG]     - Has custom normals: {m.data.has_custom_normals if hasattr(m.data, 'has_custom_normals') else 'N/A'}")

        print(f"[SOLLUMZ] Calling sollumz.convertallmaterialstoselected()...")
        bpy.ops.sollumz.convertallmaterialstoselected()
        print(f"[SOLLUMZ] Material conversion completed")
        
        # Set texture parameters after conversion
        print(f"[TEXTURE] Setting texture parameters from original mesh name...")
        from .set_textures import set_textures_from_original_name
        scene_props = getattr(context.scene, "prop_converter", None)
        original_mesh = scene_props.original_mesh if scene_props else None
        if original_mesh:
            original_name = original_mesh.name
            ok_textures = set_textures_from_original_name(context, model_objs, original_name)
            if ok_textures:
                print(f"[TEXTURE] ✓ Successfully set texture parameters using base '{original_name}'")
            else:
                print("[WARNING] Failed to set texture parameters; continuing")
        else:
            print("[WARNING] Original mesh not found, skipping texture parameter setup")
        
        # DEBUG: Check after conversion
        if model_objs:
            for m in model_objs:
                print(f"[DEBUG]   POST-CONVERSION {m.name}:")
                print(f"[DEBUG]     - Loops: {len(m.data.loops)}, Vertices: {len(m.data.vertices)}, Polygons: {len(m.data.polygons)}")
                print(f"[DEBUG]     - Color attributes: {list(m.data.color_attributes.keys())}")
                print(f"[DEBUG]     - Material slots: {len(m.material_slots)}")
                print(f"[DEBUG]     - Has custom normals: {m.data.has_custom_normals if hasattr(m.data, 'has_custom_normals') else 'N/A'}")
        
        print("[SHADER] Successfully converted all materials to selected shader")
        print("[STAGE] convert_materials: EXIT")
        print("="*80 + "\n")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to convert materials - {e}")
        import traceback
        traceback.print_exc()
        print("[STAGE] convert_materials: ERROR EXIT")
        print("="*80 + "\n")
        return False
