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


def _weight_meshes_to_root(context, armature_obj):
    """Assign all vertices of child meshes to the root bone."""
    root_bone_name = None
    for bone in armature_obj.data.bones:
        if bone.parent is None:
            root_bone_name = bone.name
            break
    
    if not root_bone_name:
        print("[DYNAMIC] Could not find root bone for weighting")
        return

    for child in armature_obj.children:
        if child.type == 'MESH':
            # 1. Ensure Armature modifier exists and points to our armature
            mod = next((m for m in child.modifiers if m.type == 'ARMATURE'), None)
            if not mod:
                mod = child.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = armature_obj
            
            # 2. Add vertex group and weight everything to 1.0
            vg = child.vertex_groups.get(root_bone_name)
            if not vg:
                vg = child.vertex_groups.new(name=root_bone_name)
            
            # Fast assignment of all vertices
            # Using list comprehension for indices is safe and efficient for typical prop sizes
            indices = [v.index for v in child.data.vertices]
            if indices:
                vg.add(indices, 1.0, 'REPLACE')
            
            # 3. Ensure mesh has vertex groups for all bones if it's a Skinned Model
            # (For dynamic props with 1 bone, just the root is enough)
            print(f"[DYNAMIC] Weighted {len(indices)} verts of '{child.name}' to root bone '{root_bone_name}'")


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


def apply_dynamic_flags(context, composite_obj, drawable_parent):
    """Apply all dynamic prop flags to the collision composite and armature.
    
    Args:
        context: Blender context
        composite_obj: The BoundComposite object
        drawable_parent: The Drawable parent (Armature or EMPTY)
    """
    print("[DYNAMIC] ===== Applying dynamic prop flags =====")
    print(f"[DYNAMIC] Composite: {composite_obj.name if composite_obj else 'None'}")
    print(f"[DYNAMIC] Drawable: {drawable_parent.name if drawable_parent else 'None'} (type: {drawable_parent.type if drawable_parent else 'N/A'})")

    # 1. Set composite flags on all bound objects
    if composite_obj:
        _apply_flags_recursive(composite_obj)

    # 2. Setup Armature
    if drawable_parent:
        armature_obj = drawable_parent
        if drawable_parent.type != 'ARMATURE':
            armature_obj = _convert_empty_to_armature(context, drawable_parent)
        
        if armature_obj:
            # A. Bone flags and position
            _apply_bone_flags(context, armature_obj)
            
            # B. Mesh weighting (CRITICAL for dynamic props)
            _weight_meshes_to_root(context, armature_obj)
            
            # C. Set Drawable flags if possible (experimental)
            if hasattr(armature_obj, "drawable_properties"):
                dp = armature_obj.drawable_properties
                # These attributes are sometimes found in reports, though Sollumz might not name them 'unknown_1'
                for attr, val in [("unknown_1", constants.DYNAMIC_UNKNOWN_1), 
                                  ("unknown_5", constants.DYNAMIC_UNKNOWN_5)]:
                    if hasattr(dp, attr):
                        setattr(dp, attr, val)
                        print(f"[DYNAMIC] Set {attr} to {val}")

    print("[DYNAMIC] ===== Dynamic prop flags complete =====")
