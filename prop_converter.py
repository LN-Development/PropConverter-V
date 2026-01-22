import bpy
from .resolve_sollumz_mod_name import resolve_sollumz_mod_name
from .core.mesh_prep import duplicate_and_prepare_mesh
from .core.conversion import (
    convert_collision,
    convert_drawable,
    convert_materials,
    create_ytyp,
    create_archetype
)
from .core.mesh_prep.paint_vertex_colors import paint_vertex_colors
from . import i18n
from . import logger


def convertToGtaV(context, operator=None) -> bool:
    """
    Convert the selected mesh to a default prop
    Duplicates the object and adds 'col' to the duplicate's name
    Stores both objects in temporary memory for further operations
    
    Args:
        context: Blender context
        operator: Optional operator instance for error reporting
    """

    # Pre-flight checks
    obj = context.active_object
    if obj is None:
        logger.log_error('messages.error.no_object_selected', operator=operator)
        return False

    if obj.type != "MESH":
        logger.log_error('messages.error.not_mesh', operator=operator, type=obj.type)
        return False

    if not obj.select_get():
        logger.log_error('messages.error.not_selected', operator=operator)
        return False

    mod_name = resolve_sollumz_mod_name()
    if mod_name is None:
        logger.log_error('messages.error.sollumz_not_found', operator=operator)
        return False

    # Set geometry origin to world origin and reset transforms
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)

    original_name, collision_obj = duplicate_and_prepare_mesh(context, obj)
    if not collision_obj:
        logger.log_error('messages.error.duplicate_failed', operator=operator)
        return False

    composite_obj = convert_collision(context, collision_obj, mod_name)
    if composite_obj is None:
        logger.log_error('messages.error.collision_failed', operator=operator)
        return False

    model_objs, drawable_parent = convert_drawable(context, obj, composite_obj)
    if not model_objs:
        logger.log_error('messages.error.drawable_failed', operator=operator)
        return False

    # Get original mesh object
    original_mesh_obj = getattr(context.scene, "prop_converter", None)
    if original_mesh_obj:
        original_mesh_obj = original_mesh_obj.original_mesh

    if not convert_materials(context, model_objs, mod_name):
        logger.log_error('messages.error.material_failed', operator=operator)
        return False

    # Apply auto-color painting AFTER conversion
    if original_mesh_obj:
        paint_col = getattr(getattr(context.scene, "prop_converter", None), "vertex_color", (1.0, 1.0, 1.0, 1.0))
        paint_vertex_colors(original_mesh_obj, None, color=tuple(paint_col))
    else:
        logger.log_warning('messages.warning.original_mesh_not_found', operator=operator)

    if not create_ytyp(context, original_name):
        logger.log_error('messages.error.ytyp_failed', operator=operator)
        return False

    if not create_archetype(context, obj, mod_name, original_name):
        logger.log_error('messages.error.archetype_failed', operator=operator)
        return False
    
    return True

