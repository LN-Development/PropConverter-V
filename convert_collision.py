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
            bpy.ops.object.select_all(action='DESELECT')
            bvh_obj.select_set(True)
            context.view_layer.objects.active = bvh_obj
            try:
                bpy.ops.sollumz.load_flag_preset()
                print("Applied flag preset to BVH via operator.")
            except Exception as op_err:
                print(f"WARNING: Could not apply flag preset via operator: {op_err}")

        poly_mesh = next((o for o in bpy.data.objects if o.name.endswith(".poly_mesh") and o.parent and o.parent.name == (bvh_obj.name if bvh_obj else "")), None)
        if poly_mesh and mod_name:
            print(f"Found poly_mesh: {poly_mesh.name}")
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
        print("Successfully converted collision mesh to Bound Composite")
        return composite_obj
    except Exception as e:
        print(f"ERROR: Failed to convert collision mesh to composite - {e}")
        import traceback
        traceback.print_exc()
        return None
