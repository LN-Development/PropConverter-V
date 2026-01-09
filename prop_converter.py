import bpy
from .resolve_sollumz_mod_name import resolve_sollumz_mod_name
from .duplicate_and_prepare_mesh import duplicate_and_prepare_mesh
from .convert_collision import convert_collision
from .convert_drawable import convert_drawable
from .convert_materials import convert_materials
from .create_ytyp import create_ytyp
from .create_archetype import create_archetype
from .set_textures_from_original_name import set_textures_from_original_name


def convertToGtaV(context) -> bool:
    """
    Convert the selected mesh to a default prop
    Duplicates the object and adds 'col' to the duplicate's name
    Stores both objects in temporary memory for further operations
    """
    if context.mode != 'OBJECT':
        print(f"ERROR: Must be in Object Mode (current mode: {context.mode})")
        return False

    obj = context.active_object
    if obj is None:
        print("ERROR: No active object")
        return False
    if obj.type != "MESH":
        print("ERROR: Object is not a mesh")
        return False
    if not obj.select_get():
        print("ERROR: Object outline is not selected")
        return False

    mod_name = resolve_sollumz_mod_name()
    if mod_name is None:
        print("ERROR: Sollumz addon is not installed or not in sys.path")
        return False

    # Set geometry origin to world origin
    print(f"Setting geometry origin to world origin for {obj.name}")
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    print(f"Origin set to world origin (0, 0, 0)")

    original_name, collision_obj = duplicate_and_prepare_mesh(context, obj)
    if not collision_obj:
        print("ERROR: Failed to duplicate and prepare mesh")
        return False

    composite_obj = convert_collision(context, collision_obj, mod_name)
    if composite_obj is None:
        print("ERROR: Collision conversion failed")
        return False

    model_objs, drawable_parent = convert_drawable(context, obj, composite_obj)
    if not model_objs:
        print("ERROR: Drawable conversion failed")
        return False

    if not convert_materials(context, model_objs, mod_name):
        print("ERROR: Material conversion failed")
        return False

    # Optional: After materials are converted, set texture references based on original mesh name
    scene_props = getattr(context.scene, "prop_converter", None)
    if scene_props and getattr(scene_props, "auto_texture_from_mesh_name", False):
        ok_textures = set_textures_from_original_name(context, model_objs, original_name)
        if ok_textures:
            print(f"Successfully set per-material textures to external files using base '{original_name}'")
        else:
            print("WARNING: Failed to set textures from original name; continuing")

    if not create_ytyp(context, original_name):
        print("ERROR: YTYP creation failed")
        return False

    if not create_archetype(context, obj, mod_name, original_name):
        print("ERROR: Archetype creation failed")
        return False

    print(f"SUCCESS: Converted '{original_name}' to GTA V prop with collision and archetype")
    return True

