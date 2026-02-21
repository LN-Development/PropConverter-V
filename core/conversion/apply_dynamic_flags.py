"""Apply dynamic prop flags to the collision composite and armature skeleton.

This module sets the correct BoundFlags and bone properties to make
a prop behave as a dynamic, physics-enabled object in GTA V.
"""

import bpy
from ... import constants


def _set_bound_flags(flags_obj, flags_dict):
    """Set specific flags on a BoundFlags property group."""
    for flag_name, flag_value in flags_dict.items():
        if hasattr(flags_obj, flag_name):
            setattr(flags_obj, flag_name, flag_value)


def _apply_flags_recursive(obj):
    """Recursively apply dynamic composite flags to all bound objects."""
    sollum_type = str(getattr(obj, "sollum_type", "")).lower()

    if "bound" in sollum_type:
        if hasattr(obj, "composite_flags1"):
            _set_bound_flags(obj.composite_flags1, constants.DYNAMIC_COMPOSITE_FLAGS1)
            print(f"[DYNAMIC] Set composite_flags1 on {obj.name}")

        if hasattr(obj, "composite_flags2"):
            _set_bound_flags(obj.composite_flags2, constants.DYNAMIC_COMPOSITE_FLAGS2)
            print(f"[DYNAMIC] Set composite_flags2 on {obj.name}")

    for child in obj.children:
        _apply_flags_recursive(child)


def _convert_empty_to_armature(context, empty_obj):
    """Replace an EMPTY drawable parent with an Armature, preserving all children and properties."""
    try:
        original_name = empty_obj.name
        sollum_type = getattr(empty_obj, "sollum_type", None)
        matrix = empty_obj.matrix_world.copy()
        
        # Copy drawable properties before deleting
        lod_dists = {}
        if hasattr(empty_obj, "drawable_properties"):
            dp = empty_obj.drawable_properties
            for attr in ["lod_dist_high", "lod_dist_med", "lod_dist_low", "lod_dist_vlow"]:
                if hasattr(dp, attr):
                    lod_dists[attr] = getattr(dp, attr)

        # Collect children and their world matrices BEFORE any changes
        children_data = []
        for child in list(empty_obj.children):
            children_data.append((child, child.matrix_world.copy()))

        # Unparent children first
        for child, _ in children_data:
            child.parent = None

        # Remove old EMPTY (frees the name)
        bpy.data.objects.remove(empty_obj, do_unlink=True)
        print(f"[DYNAMIC] Removed old EMPTY '{original_name}'")

        # Now create Armature with the original name (name is free now)
        arm_data = bpy.data.armatures.new(original_name)
        arm_obj = bpy.data.objects.new(original_name, arm_data)
        context.collection.objects.link(arm_obj)

        # Restore transforms and properties
        arm_obj.matrix_world = matrix
        if sollum_type:
            arm_obj.sollum_type = sollum_type
        if hasattr(arm_obj, "drawable_properties"):
            dp_dst = arm_obj.drawable_properties
            for attr, val in lod_dists.items():
                setattr(dp_dst, attr, val)

        # Reparent children to the new Armature
        for child, child_mat in children_data:
            child.parent = arm_obj
            child.matrix_world = child_mat

        print(f"[DYNAMIC] Created Armature '{arm_obj.name}' with {len(children_data)} children")
        return arm_obj

    except Exception as e:
        print(f"[DYNAMIC] ERROR creating armature: {e}")
        import traceback
        traceback.print_exc()
        return None


# Removed _weight_meshes_to_root as it creates redundant Armature modifiers
# when Copy Transforms constraints are used.


def _apply_bone_flags(context, armature_obj):
    """Set bone flags on the root bone of the drawable for physics movement."""
    armature_data = armature_obj.data

    # Enter edit mode to create/position the root bone
    bpy.ops.object.select_all(action='DESELECT')
    armature_obj.select_set(True)
    context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Find or create root bone
    root_bone = None
    for eb in armature_data.edit_bones:
        if eb.parent is None:
            root_bone = eb
            break

    if root_bone is None:
        root_bone = armature_data.edit_bones.new(armature_obj.name)
        print(f"[DYNAMIC] Created root bone '{root_bone.name}'")

    # Place at world origin with Sollumz bone size
    root_bone.head = (0.0, 0.0, 0.0)
    root_bone.tail = constants.DYNAMIC_BONE_TAIL_OFFSET
    print(f"[DYNAMIC] Positioned root bone '{root_bone.name}' at origin")

    bpy.ops.object.mode_set(mode='OBJECT')

    # Set bone_properties.flags on the root bone
    for bone in armature_data.bones:
        if bone.parent is None and hasattr(bone, "bone_properties"):
            bp = bone.bone_properties
            bp.flags.clear()
            for flag_name in constants.DYNAMIC_BONE_FLAGS:
                new_flag = bp.flags.add()
                new_flag.name = flag_name
            print(f"[DYNAMIC] Set bone flags: {', '.join(constants.DYNAMIC_BONE_FLAGS)}")
            break


def _add_copy_transforms_constraints(context, armature_obj):
    """Add Copy Transforms constraint to all children to sync with the root bone."""
    root_bone_name = None
    for bone in armature_obj.data.bones:
        if bone.parent is None:
            root_bone_name = bone.name
            break
            
    if not root_bone_name:
        print("[DYNAMIC] Could not find root bone for Copy Transforms")
        return

    for child in armature_obj.children:
        # ONLY apply Copy Transforms to VISUAL meshes (those with shaders)
        sollum_type = str(getattr(child, "sollum_type", "")).lower()
        if "bound" in sollum_type:
            continue
            
        # 1. Clean up existing Copy Transforms constraints to avoid duplicates
        for cons in list(child.constraints):
            if cons.type == 'COPY_TRANSFORMS' and cons.subtarget == root_bone_name:
                child.constraints.remove(cons)
        
        # 2. Add new constraint
        cons = child.constraints.new(type='COPY_TRANSFORMS')
        cons.target = armature_obj
        cons.subtarget = root_bone_name
        cons.target_space = 'POSE'
        cons.owner_space = 'LOCAL'
        
        print(f"[DYNAMIC] Added Copy Transforms to Visual Mesh '{child.name}'")


def _parent_bounds_to_bone(context, armature_obj):
    """Set collision bounds to follow the root bone via Bone Parenting."""
    root_bone_name = None
    for bone in armature_obj.data.bones:
        if bone.parent is None:
            root_bone_name = bone.name
            break
            
    if not root_bone_name:
        return

    for child in armature_obj.children:
        sollum_type = str(getattr(child, "sollum_type", "")).lower()
        if "bound" in sollum_type:
            # 1. Store world matrix to preserve position
            world_mat = child.matrix_world.copy()
            
            # 2. Set Bone Parenting
            child.parent = armature_obj
            child.parent_type = 'BONE'
            child.parent_bone = root_bone_name
            
            # 3. Restore world matrix relative to the bone
            child.matrix_world = world_mat
            print(f"[DYNAMIC] Bone-Parented Bound '{child.name}' to '{root_bone_name}'")


def _align_door_hinge(context, armature_obj, hinge_side):
    """Shift door components based on dominant axis so the selected edge is at 0."""
    if hinge_side == 'NONE':
        return

    import mathutils
    from mathutils import Vector
    min_x, max_x = None, None
    min_y, max_y = None, None
    min_z, max_z = None, None

    # 1. Calculate bounding box of visual meshes relative to armature
    for child in armature_obj.children:
        if child.type == 'MESH':
            sollum_type = str(getattr(child, "sollum_type", "")).lower()
            if "bound" not in sollum_type:
                for v in child.data.vertices:
                    local_v = child.matrix_basis @ v.co
                    if min_x is None or local_v.x < min_x: min_x = local_v.x
                    if max_x is None or local_v.x > max_x: max_x = local_v.x
                    if min_y is None or local_v.y < min_y: min_y = local_v.y
                    if max_y is None or local_v.y > max_y: max_y = local_v.y
                    if min_z is None or local_v.z < min_z: min_z = local_v.z
                    if max_z is None or local_v.z > max_z: max_z = local_v.z

    if min_x is None or min_y is None or min_z is None:
        print("[DOOR] Could not calculate bounds for alignment")
        return

    # 2. Determine Axis and Offset(s)
    offsets = {} # {axis_name: offset_value}
    
    # v_factors (Z axis presets)
    v_presets = {'BOTTOM': 0.0, 'MID': 0.5, 'TOP': 1.0}
    # h_factors (Width axis presets)
    h_presets = {'LEFT': 0.0, 'RIGHT': 1.0}

    # Determine factors from properties
    props = getattr(context.scene, "prop_converter", None)
    use_custom = props.use_custom_hinge_offset if props else False
    custom_factor = (props.door_hinge_custom_offset / 100.0) if props else 0.0

    print(f"[DOOR] Alignment Debug:")
    print(f"  - Selected Preset: {hinge_side}")
    print(f"  - Bounds (X): {min_x:.3f} to {max_x:.3f} (W: {max_x-min_x:.3f})")
    print(f"  - Bounds (Y): {min_y:.3f} to {max_y:.3f} (D: {max_y-min_y:.3f})")
    print(f"  - Bounds (Z): {min_z:.3f} to {max_z:.3f} (H: {max_z-min_z:.3f})")

    offsets = {}
    factor = 0.0
    axis = None

    if hinge_side in v_presets:
        # Vertical axis
        axis = 'Z'
        # If custom is on, use slider, otherwise use preset
        factor = custom_factor if use_custom else v_presets[hinge_side]
        offsets[axis] = -(min_z + (max_z - min_z) * factor)
        print(f"  - Mode: Vertical (Axis: {axis}, Factor: {factor*100:.1f}%)")
    elif hinge_side in h_presets:
        # Width axis (dominant horizontal)
        width_x = max_x - min_x
        width_y = max_y - min_y
        is_x_dominant = width_x >= width_y
        
        axis = 'X' if is_x_dominant else 'Y'
        factor = custom_factor if use_custom else h_presets[hinge_side]
        
        min_c = min_x if axis == 'X' else min_y
        max_c = max_x if axis == 'X' else max_y
        
        offsets[axis] = -(min_c + (max_c - min_c) * factor)
        print(f"  - Mode: Width (Axis: {axis} [dominant], Factor: {factor*100:.1f}%)")
    else:
        # Default to origin if anything else (shouldn't happen with current UI)
        offsets['X'] = -(min_x + max_x) / 2
        offsets['Y'] = -(min_y + max_y) / 2
        offsets['Z'] = -(min_z + max_z) / 2
        print(f"  - Mode: Default/Origin (Full Center)")

    if use_custom:
        print(f"  - Note: Using Custom Offset Slider ({custom_factor*100:.1f}%)")

    # 4. Apply offsets
    for child in armature_obj.children:
        sollum_type = str(getattr(child, "sollum_type", "")).lower()
        
        if "bound" in sollum_type:
            # Shift object location
            for axis, val in offsets.items():
                if abs(val) < 0.0001: continue
                if axis == 'X': child.location.x += val
                elif axis == 'Y': child.location.y += val
                elif axis == 'Z': child.location.z += val
            print(f"[DOOR] Shifted Bound '{child.name}' location")
        else:
            # Shift vertex data for visual meshes
            if child.type == 'MESH':
                for v in child.data.vertices:
                    for axis, val in offsets.items():
                        if abs(val) < 0.0001: continue
                        if axis == 'X': v.co.x += val
                        elif axis == 'Y': v.co.y += val
                        elif axis == 'Z': v.co.z += val
                child.data.update()
                print(f"[DOOR] Shifted vertex data of '{child.name}'")

    affected_axes = ", ".join(offsets.keys())
    print(f"[DOOR] Aligned {hinge_side} hinge on {affected_axes} axis")


def apply_dynamic_flags(context, composite_obj, drawable_parent, is_dynamic=False, is_door=False):
    """Apply all dynamic or door prop flags to the collision and armature.
    
    Args:
        context: Blender context
        composite_obj: The BoundComposite or BoundBox object
        drawable_parent: The Drawable parent (Armature or EMPTY)
        is_dynamic: Whether it's a dynamic prop
        is_door: Whether it's a door prop
    """
    label = "DOOR" if is_door else "DYNAMIC"
        
    print(f"[{label}] ===== Applying {label.lower()} prop flags =====")
    print(f"[{label}] Collision: {composite_obj.name if composite_obj else 'None'}")
    print(f"[{label}] Drawable: {drawable_parent.name if drawable_parent else 'None'} (type: {drawable_parent.type if drawable_parent else 'N/A'})")

    # 1. Set composite flags on all bound objects (Dynamic only)
    if is_dynamic and composite_obj:
        _apply_flags_recursive(composite_obj)

    # 2. Setup Armature (Required for all)
    if drawable_parent:
        armature_obj = drawable_parent
        if drawable_parent.type != 'ARMATURE':
            armature_obj = _convert_empty_to_armature(context, drawable_parent)
        
        if armature_obj:
            # A. Bone flags and position (CRITICAL for all)
            _apply_bone_flags(context, armature_obj)
            
            # B. Sync bones and children (Copy Transforms for Visuals, Bone Parent for Bounds)
            _add_copy_transforms_constraints(context, armature_obj)
            _parent_bounds_to_bone(context, armature_obj)
            
            # C. Hinge Alignment (Move mesh, keep bone at origin)
            if is_door:
                props = getattr(context.scene, "prop_converter", None)
                if props:
                    _align_door_hinge(context, armature_obj, props.door_hinge_side)

            # D. Set Drawable flags
            if is_dynamic and hasattr(armature_obj, "drawable_properties"):
                dp = armature_obj.drawable_properties
                for attr, val in [("unknown_1", constants.DYNAMIC_UNKNOWN_1), 
                                  ("unknown_5", constants.DYNAMIC_UNKNOWN_5)]:
                    if hasattr(dp, attr):
                        setattr(dp, attr, val)
                        print(f"[{label}] Set {attr} to {val}")

    print(f"[{label}] ===== {label.lower()} prop flags complete =====")
    return armature_obj
