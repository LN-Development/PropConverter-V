import bpy
import importlib


def convert_collision(context, collision_obj: bpy.types.Object, mod_name: str):
    """Convert collision mesh to composite and apply collision materials."""
    try:
       
        bpy.ops.object.select_all(action='DESELECT')
        collision_obj.select_set(True)
        context.view_layer.objects.active = collision_obj
        pre_object_names = {o.name for o in bpy.data.objects}
        
      
        bpy.ops.sollumz.converttocomposite()
  

        created_objs = [o for o in bpy.data.objects if o.name not in pre_object_names]
   
        bvh_obj = next((o for o in created_objs if o.name.lower().endswith(".bvh")), None)
        if bvh_obj is None:
            bvh_obj = next((o for o in bpy.data.objects if o.name.lower().endswith(".bvh")), None)
        if bvh_obj:
   
            if bvh_obj.type == 'MESH':
                print(f"[DEBUG] BVH loops: {len(bvh_obj.data.loops)}, vertices: {len(bvh_obj.data.vertices)}")
            else:
                print(f"[DEBUG] BVH is {bvh_obj.type} (not a mesh - likely parent/empty)")
            bpy.ops.object.select_all(action='DESELECT')
            bvh_obj.select_set(True)
            context.view_layer.objects.active = bvh_obj
            print("[SOLLUMZ] Applying flag preset to BVH...")
            try:
                bpy.ops.sollumz.load_flag_preset()
                print("[SOLLUMZ] Flag preset applied successfully.")
            except Exception as op_err:
                print(f"[WARNING] Could not apply flag preset via operator: {op_err}")

        poly_mesh = next((o for o in bpy.data.objects if o.name.endswith(".poly_mesh") and o.parent and o.parent.name == (bvh_obj.name if bvh_obj else "")), None)
        if poly_mesh and mod_name:
            print(f"[POLY_MESH] Found poly_mesh: {poly_mesh.name}")
            print(f"[DEBUG]   Poly_mesh loops: {len(poly_mesh.data.loops)}")
            print(f"[DEBUG]   Poly_mesh vertices: {len(poly_mesh.data.vertices)}")
            print(f"[DEBUG]   Poly_mesh polygons: {len(poly_mesh.data.polygons)}")
            bpy.ops.object.select_all(action='DESELECT')
            poly_mesh.select_set(True)
            context.view_layer.objects.active = poly_mesh
            try:
                collision_mat_index = getattr(context.window_manager, "sz_collision_material_index", 0)
                print(f"Converting materials to collision material index: {collision_mat_index}")
                collision_materials = importlib.import_module(f"{mod_name}.ybn.collision_materials")
                create_collision_material = collision_materials.create_collision_material_from_index
                mesh = poly_mesh.data
                num_materials = len(mesh.materials)
                if num_materials > 0:
                    for i in range(num_materials):
                        collision_mat = create_collision_material(collision_mat_index)
                        mesh.materials[i] = collision_mat
                        print(f"Converted material slot {i} to collision material")
                else:
                    collision_mat = create_collision_material(collision_mat_index)
                    mesh.materials.append(collision_mat)
                    print("Created collision material for empty mesh")
                
                # Apply collision flags from PropConverter-V properties
                props = getattr(context.scene, "prop_converter", None)
                if props and hasattr(props, "collision_flags"):
                    collision_flags = props.collision_flags
                    # Apply flags to all collision materials on this mesh
                    for mat in mesh.materials:
                        if mat and hasattr(mat, "collision_flags"):
                            mat.collision_flags.stairs = collision_flags.stairs
                            mat.collision_flags.not_climbable = collision_flags.not_climbable
                            mat.collision_flags.see_through = collision_flags.see_through
                            mat.collision_flags.shoot_through = collision_flags.shoot_through
                            mat.collision_flags.not_cover = collision_flags.not_cover
                            mat.collision_flags.walkable_path = collision_flags.walkable_path
                            mat.collision_flags.no_cam_collision = collision_flags.no_cam_collision
                            mat.collision_flags.shoot_through_fx = collision_flags.shoot_through_fx
                            mat.collision_flags.no_decal = collision_flags.no_decal
                            mat.collision_flags.no_navmesh = collision_flags.no_navmesh
                            mat.collision_flags.no_ragdoll = collision_flags.no_ragdoll
                            mat.collision_flags.vehicle_wheel = collision_flags.vehicle_wheel
                            mat.collision_flags.no_ptfx = collision_flags.no_ptfx
                            mat.collision_flags.too_steep_for_player = collision_flags.too_steep_for_player
                            mat.collision_flags.no_network_spawn = collision_flags.no_network_spawn
                            mat.collision_flags.no_cam_collision_allow_clipping = collision_flags.no_cam_collision_allow_clipping
                            print(f"Applied collision flags to material: {mat.name}")
                
                print(f"Successfully converted all materials to collision material on {poly_mesh.name}")
            except Exception as mat_err:
                print(f"WARNING: Could not apply collision material to poly_mesh: {mat_err}")
                import traceback
                traceback.print_exc()
        else:
            print("WARNING: Could not find .poly_mesh child for collision material conversion")

        composite_obj = None
        if bvh_obj:
            composite_obj = bvh_obj.parent
        
        print("[COMPOSITE] Successfully converted collision mesh to Bound Composite")
        if composite_obj:
            print(f"[DEBUG] Composite object: {composite_obj.name}")
            print(f"[DEBUG] Composite object type: {composite_obj.type}")
            if composite_obj.type == 'MESH':
                print(f"[DEBUG]   Loops: {len(composite_obj.data.loops) if composite_obj.data else 'N/A'}")
            else:
                print(f"[DEBUG] Composite is {composite_obj.type} (not mesh)")
            print(f"[DEBUG]   Children: {[c.name for c in composite_obj.children]}")
        print("[STAGE] convert_collision: EXIT")
        print("="*80 + "\n")
        return composite_obj
    except Exception as e:
        print(f"[ERROR] Failed to convert collision mesh to composite - {e}")
        import traceback
        traceback.print_exc()
        print("[STAGE] convert_collision: ERROR EXIT")
        print("="*80 + "\n")
        return None
