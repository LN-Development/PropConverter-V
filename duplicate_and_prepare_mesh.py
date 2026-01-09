import bpy
from .rename_uv_maps import rename_uv_maps_sequential
from .clear_uv_maps import clear_uv_maps
from .paint_vertex_colors import paint_vertex_colors


def duplicate_and_prepare_mesh(context, obj: bpy.types.Object):
    """Duplicate mesh, store refs, normalize UVs, clear on collision, paint vertex colors."""
    sanitized_name = obj.name.lower().replace(" ", "")
    if sanitized_name != obj.name:
        print(f"Renaming mesh from '{obj.name}' to '{sanitized_name}'")
        obj.name = sanitized_name
    original_name = obj.name

    context.scene.prop_converter.original_mesh = obj
    print(f"Saved original mesh to temporary memory: {obj.name}")

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj

    new_obj = obj.copy()
    new_obj.data = obj.data.copy()
    new_obj.animation_data_clear()
    context.collection.objects.link(new_obj)

    print(f"Duplicated object created: {new_obj.name}")

    rename_uv_maps_sequential(obj.data)
    clear_uv_maps(new_obj.data)

    new_obj.name = f"{original_name}col"
    context.scene.prop_converter.collision_mesh = new_obj
    print(f"Saved collision mesh to temporary memory: {new_obj.name}")

    paint_col = getattr(getattr(context.scene, "prop_converter", None), "vertex_color", (1.0, 1.0, 1.0, 1.0))
    print(f"Painting vertex colors on original (Color 1) and clearing on collision with color: {paint_col}")
    paint_vertex_colors(obj, new_obj, color=tuple(paint_col))

    return original_name, new_obj
