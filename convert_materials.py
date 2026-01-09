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
                print("ERROR: Could not find default.sps shader")
                return False
            wm.sz_shader_material_index = selected_idx
            print(f"Selected shader index invalid; falling back to default.sps at {selected_idx}")
        else:
            print(f"Using user-selected shader index: {selected_idx} ({shadermats[selected_idx].value})")

        if model_objs:
            bpy.ops.object.select_all(action='DESELECT')
            for m in model_objs:
                m.select_set(True)
            context.view_layer.objects.active = model_objs[0]

        bpy.ops.sollumz.convertallmaterialstoselected()
        print("Successfully converted all materials to selected shader")
        return True
    except Exception as e:
        print(f"ERROR: Failed to convert materials - {e}")
        import traceback
        traceback.print_exc()
        return False
