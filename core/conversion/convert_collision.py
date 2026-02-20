import bpy
import importlib
from ... import constants


def convert_collision(context, collision_obj: bpy.types.Object, mod_name: str, is_dynamic: bool = False, is_door: bool = False):
    """Convert collision mesh to composite (Dynamic/Static) or standalone Box (Door)."""
    try:
        from ...sollumz_integration import SollumzIntegration
        sollumz = SollumzIntegration.get_instance()
        SollumType = sollumz.get_sollumz_properties().SollumType

        # Store bounds for Box creation (used by both Dynamic and Door)
        bb_min, bb_max = None, None
        if is_dynamic or is_door:
            mesh_data = collision_obj.data
            import mathutils
            
            # For Doors, calculate bounds based on occupied surface area (ignoring handles)
            if is_door:
                # Calculate face areas and centers
                face_data = []
                total_area = 0.0
                for face in mesh_data.polygons:
                    area = face.area
                    if area > 0.00001:
                        face_data.append((face.center, area))
                        total_area += area
                
                if total_area > 0:
                    def get_area_percentile(axis_idx, p):
                        # Sort faces by coordinate on the specific axis
                        sorted_faces = sorted(face_data, key=lambda f: f[0][axis_idx])
                        target = total_area * p
                        acc = 0.0
                        for center, area in sorted_faces:
                            acc += area
                            if acc >= target:
                                return center[axis_idx]
                        return sorted_faces[-1][0][axis_idx]

                    # 1st and 99th area percentile to capture the main door body
                    bb_min = mathutils.Vector((get_area_percentile(0, 0.01), 
                                             get_area_percentile(1, 0.01), 
                                             get_area_percentile(2, 0.01)))
                    bb_max = mathutils.Vector((get_area_percentile(0, 0.99), 
                                             get_area_percentile(1, 0.99), 
                                             get_area_percentile(2, 0.99)))
                    print(f"[DOOR] Calculated area-weighted bounds (1%-99% area) to ignore small details")
                else:
                    # Fallback to standard min/max
                    bb_min = mathutils.Vector((min(v.co.x for v in mesh_data.vertices), 
                                             min(v.co.y for v in mesh_data.vertices), 
                                             min(v.co.z for v in mesh_data.vertices)))
                    bb_max = mathutils.Vector((max(v.co.x for v in mesh_data.vertices), 
                                             max(v.co.y for v in mesh_data.vertices), 
                                             max(v.co.z for v in mesh_data.vertices)))
            else:
                # Standard Min/Max for dynamic props (usually simpler shapes)
                bb_min = mathutils.Vector((min(v.co.x for v in mesh_data.vertices), 
                                         min(v.co.y for v in mesh_data.vertices), 
                                         min(v.co.z for v in mesh_data.vertices)))
                bb_max = mathutils.Vector((max(v.co.x for v in mesh_data.vertices), 
                                         max(v.co.y for v in mesh_data.vertices), 
                                         max(v.co.z for v in mesh_data.vertices)))

        if is_door:
            print("[DOOR] Creating Bound Composite with Box child")
            old_bound_type = context.scene.create_bound_type
            
            # 1. Create Bound Composite
            context.scene.create_bound_type = SollumType.BOUND_COMPOSITE
            pre_comp_objs = {o.name for o in bpy.data.objects}
            bpy.ops.sollumz.createbound()
            composite_obj = next((o for o in bpy.data.objects if o.name not in pre_comp_objs), None)
            
            if composite_obj:
                composite_obj.name = "Bound Composite"
                
                # 2. Create Bound Box as child
                context.scene.create_bound_type = SollumType.BOUND_BOX
                pre_box_objs = {o.name for o in bpy.data.objects}
                bpy.ops.sollumz.createbound()
                box_obj = next((o for o in bpy.data.objects if o.name not in pre_box_objs), None)
                
                if box_obj:
                    box_obj.name = "Bound Box"
                    box_obj.parent = composite_obj
                    if hasattr(box_obj, "sz_bound_shape"):
                        box_obj.sz_bound_shape.box_extents = bb_max - bb_min
                    box_obj.location = (bb_max + bb_min) / 2
                    
                    # Apply material and flags to the Box
                    if len(collision_obj.data.materials) > 0:
                        box_obj.data.materials.append(collision_obj.data.materials[0])
                    
                    # Map collision flags
                    props = getattr(context.scene, "prop_converter", None)
                    if props and hasattr(props, "collision_flags"):
                        collision_flags = props.collision_flags
                        for mat in box_obj.data.materials:
                            if mat and hasattr(mat, "collision_flags"):
                                for attr in ["stairs", "not_climbable", "see_through", "shoot_through", 
                                           "not_cover", "walkable_path", "no_cam_collision", "shoot_through_fx", 
                                           "no_decal", "no_navmesh", "no_ragdoll", "vehicle_wheel", "no_ptfx", 
                                           "too_steep_for_player", "no_network_spawn", "no_cam_collision_allow_clipping"]:
                                    if hasattr(collision_flags, attr):
                                        setattr(mat.collision_flags, attr, getattr(collision_flags, attr))
            
            context.scene.create_bound_type = old_bound_type
            
            # 3. Clean up the temporary collision mesh created in Stage 3
            if collision_obj:
                print(f"[DOOR] Removing temporary collision mesh: {collision_obj.name}")
                bpy.data.objects.remove(collision_obj, do_unlink=True)
                
            return composite_obj

        # --- NORMAL CONVERSION FLOW (Creates Bound Geometry/BVH) ---
        bpy.ops.object.select_all(action='DESELECT')
        collision_obj.select_set(True)
        context.view_layer.objects.active = collision_obj
        
        pre_object_names = {o.name for o in bpy.data.objects}
        bpy.ops.sollumz.converttocomposite()
        created_objs = [o for o in bpy.data.objects if o.name not in pre_object_names]
        
        bvh_obj = next((o for o in created_objs if o.name.lower().endswith(constants.BVH_SUFFIX)), None)
        if bvh_obj is None:
            # Fallback to searching all objects if not in created_objs
            bvh_obj = next((o for o in bpy.data.objects if o.name.lower().endswith(constants.BVH_SUFFIX) and o.name not in pre_object_names), None)
        
        composite_obj = bvh_obj.parent if bvh_obj else None
        
        # Apply flag presets and materials to the generated geometry
        if bvh_obj:
            bpy.ops.object.select_all(action='DESELECT')
            bvh_obj.select_set(True)
            context.view_layer.objects.active = bvh_obj
            try:
                bpy.ops.sollumz.load_flag_preset()
            except Exception:
                pass

        poly_mesh = next((o for o in bpy.data.objects if o.name.endswith(constants.POLY_MESH_SUFFIX) and o.parent and o.parent.name == (bvh_obj.name if bvh_obj else "")), None)
        if poly_mesh and mod_name:
            bpy.ops.object.select_all(action='DESELECT')
            poly_mesh.select_set(True)
            context.view_layer.objects.active = poly_mesh
            try:
                collision_mat_index = getattr(context.window_manager, "sz_collision_material_index", 0)
                collision_materials = importlib.import_module(f"{mod_name}.ybn.collision_materials")
                create_collision_material = collision_materials.create_collision_material_from_index
                mesh = poly_mesh.data
                num_materials = len(mesh.materials)
                if num_materials > 0:
                    for i in range(num_materials):
                        collision_mat = create_collision_material(collision_mat_index)
                        mesh.materials[i] = collision_mat
                else:
                    collision_mat = create_collision_material(collision_mat_index)
                    mesh.materials.append(collision_mat)
                
                # Apply collision flags from PropConverter-V properties
                props = getattr(context.scene, "prop_converter", None)
                if props and hasattr(props, "collision_flags"):
                    collision_flags = props.collision_flags
                    for mat in mesh.materials:
                        if mat and hasattr(mat, "collision_flags"):
                            for attr in ["stairs", "not_climbable", "see_through", "shoot_through", 
                                       "not_cover", "walkable_path", "no_cam_collision", "shoot_through_fx", 
                                       "no_decal", "no_navmesh", "no_ragdoll", "vehicle_wheel", "no_ptfx", 
                                       "too_steep_for_player", "no_network_spawn", "no_cam_collision_allow_clipping"]:
                                if hasattr(collision_flags, attr):
                                    setattr(mat.collision_flags, attr, getattr(collision_flags, attr))
            except Exception as mat_err:
                print(f"WARNING: Could not apply collision material to poly_mesh: {mat_err}")

        # --- DYNAMIC PROP ADDITIONS (Add Bound Box as sibling to Geometry) ---
        if is_dynamic and composite_obj and bb_min and bb_max:
            print("[DYNAMIC] Adding Bound Box child to existing composite")
            bpy.ops.object.select_all(action='DESELECT')
            composite_obj.select_set(True)
            context.view_layer.objects.active = composite_obj
            
            old_bound_type = context.scene.create_bound_type
            context.scene.create_bound_type = SollumType.BOUND_BOX
            pre_box_objs = {o.name for o in bpy.data.objects}
            bpy.ops.sollumz.createbound()
            box_obj = next((o for o in bpy.data.objects if o.name not in pre_box_objs), None)
            context.scene.create_bound_type = old_bound_type
            
            if box_obj:
                box_obj.name = f"{composite_obj.name.replace('.ybn', '')}.box"
                
                # 5% Height Calculation
                total_height = bb_max.z - bb_min.z
                new_box_height = total_height * 0.05
                # Ensure minimum height for collision
                new_box_height = max(0.01, new_box_height)
                
                if hasattr(box_obj, "sz_bound_shape"):
                    # Extents: X, Y remain same, Z is 5%
                    box_obj.sz_bound_shape.box_extents = (bb_max.x - bb_min.x, bb_max.y - bb_min.y, new_box_height)
                
                # Location: Centered horizontally, at the base vertically + half of new height
                box_obj.location = (
                    (bb_max.x + bb_min.x) / 2.0,
                    (bb_max.y + bb_min.y) / 2.0,
                    bb_min.z + (new_box_height / 2.0)
                )
                
                # Copy first material to the box
                if poly_mesh and len(poly_mesh.data.materials) > 0:
                    box_obj.data.materials.append(poly_mesh.data.materials[0])
                elif collision_obj and len(collision_obj.data.materials) > 0:
                    box_obj.data.materials.append(collision_obj.data.materials[0])

        return composite_obj
    except Exception as e:
        print(f"[ERROR] Failed to convert collision mesh to composite - {e}")
        import traceback
        traceback.print_exc()
        return None
