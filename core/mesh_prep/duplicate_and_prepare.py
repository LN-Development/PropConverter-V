import bpy
from .rename_uv_maps import rename_uv_maps_sequential
from .clear_uv_maps import clear_uv_maps
from .paint_vertex_colors import paint_vertex_colors
from .apply_decimate import apply_decimate
from .apply_remesh import apply_remesh
from ... import constants


def duplicate_and_prepare_mesh(context, obj: bpy.types.Object):
    """Duplicate mesh, store refs, normalize UVs, clear on collision, paint vertex colors."""
    sanitized_name = obj.name.lower().replace(" ", "")
    if sanitized_name != obj.name:
        obj.name = sanitized_name
    original_name = obj.name

    # Check if object has any materials, if not create one
    if len(obj.material_slots) == 0 or not any(slot.material for slot in obj.material_slots):
        mat = bpy.data.materials.new(name=f"{original_name}_mat")
        mat.use_nodes = True
        
        # Clear default nodes
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        # Create basic shader setup
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (300, 0)
        
        bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_node.location = (0, 0)
        
        # Link BSDF to output
        mat.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
        
        # Assign material to object
        if len(obj.material_slots) == 0:
            obj.data.materials.append(mat)
        else:
            obj.material_slots[0].material = mat

    context.scene.prop_converter.original_mesh = obj

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj

    new_obj = obj.copy()
    new_obj.data = obj.data.copy()
    new_obj.animation_data_clear()
    context.collection.objects.link(new_obj)

    rename_uv_maps_sequential(obj.data)
    clear_uv_maps(new_obj.data)

    new_obj.name = f"{original_name}{constants.COLLISION_SUFFIX}"
    context.scene.prop_converter.collision_mesh = new_obj

    # Apply decimate modifier if enabled
    props = getattr(context.scene, "prop_converter", None)
    if props and props.enable_decimate:
        if not apply_decimate(context, new_obj, 
                             decimate_type=props.decimate_type,
                             ratio=props.decimate_ratio,
                             iterations=props.decimate_iterations,
                             use_dissolve=props.decimate_use_dissolve,
                             planar_angle=props.decimate_planar_angle):
            print("[WARNING] Failed to apply decimate modifier")

    # Apply remesh modifier if enabled
    if props and props.enable_remesh:
        if not apply_remesh(context, new_obj, props.remesh_mode, 
                           use_smooth_shade=props.remesh_use_smooth_shade,
                           threshold=props.remesh_threshold,
                           voxel_size=props.remesh_voxel_size,
                           adaptivity=props.remesh_adaptivity):
            print("[WARNING] Failed to apply remesh modifier")

    paint_col = getattr(getattr(context.scene, "prop_converter", None), "vertex_color", (1.0, 1.0, 1.0, 1.0))
    # Only paint colors on collision mesh during preparation
    # Original mesh colors will be painted AFTER material conversion to avoid interference
    paint_vertex_colors(None, new_obj, color=tuple(paint_col))

    return original_name, new_obj
