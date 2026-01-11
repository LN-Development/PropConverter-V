import bpy


def paint_vertex_colors(original_obj: bpy.types.Object, collision_obj: bpy.types.Object, color=(1.0, 1.0, 1.0, 1.0)) -> bool:
    """Fill vertex colors on the original mesh (Color 1) and remove all vertex colors from the collision mesh.
    Uses Face Corner domain and Byte Color type as required."""
    try:
        print("\n" + "="*80)
        print("[STAGE] paint_vertex_colors: ENTRY")
        
        if original_obj and original_obj.type == "MESH":
            mesh = original_obj.data
            loops = len(mesh.loops)
            print(f"[PAINT] Processing original: {original_obj.name}")
            print(f"[DEBUG]   Loops: {loops}, Vertices: {len(mesh.vertices)}, Polygons: {len(mesh.polygons)}")
            print(f"[DEBUG]   Current color attributes: {list(mesh.color_attributes.keys())}")
            print(f"[DEBUG]   Target color: {color}")
            if loops > 0:
                attr_name = "Color 1"  # Sollumz expects this naming
                
                # Create or get color attribute with Face Corner and Byte Color
                if attr_name in mesh.color_attributes:
                    target_attr = mesh.color_attributes[attr_name]
                    print(f"[ATTR] Using existing '{attr_name}' attribute")
                    print(f"[DEBUG]   Domain: {target_attr.domain}, Type: {target_attr.data_type}")
                    # Ensure it's Face Corner and Byte Color
                    if target_attr.domain != 'CORNER' or target_attr.data_type != 'BYTE_COLOR':
                        print(f"[ATTR] Recreating '{attr_name}' with correct format...")
                        mesh.color_attributes.remove(target_attr)
                        target_attr = mesh.color_attributes.new(
                            name=attr_name, 
                            type='BYTE_COLOR',  # Byte Color
                            domain='CORNER'     # Face Corner
                        )
                        print(f"[ATTR] Successfully recreated '{attr_name}' (CORNER/BYTE_COLOR)")
                else:
                    print(f"[ATTR] Creating new '{attr_name}' attribute...")
                    target_attr = mesh.color_attributes.new(
                        name=attr_name, 
                        type='BYTE_COLOR',  # Byte Color
                        domain='CORNER'     # Face Corner
                    )
                    print(f"[ATTR] Successfully created '{attr_name}' (CORNER/BYTE_COLOR)")
                
                # Fill with vertex color
                print(f"[FILL] Filling {loops} loop corners with color {color}...")
                for loop_index in range(loops):
                    target_attr.data[loop_index].color = color
                print(f"[FILL] Successfully filled all {loops} loop corners")

        if collision_obj and collision_obj.type == "MESH":
            cmesh = collision_obj.data
            print(f"[PAINT] Processing collision: {collision_obj.name}")
            print(f"[DEBUG]   Color attributes before removal: {list(cmesh.color_attributes.keys())}")
            # Remove all color attributes from collision mesh
            removed_count = len(cmesh.color_attributes)
            while len(cmesh.color_attributes) > 0:
                cmesh.color_attributes.remove(cmesh.color_attributes[0])
            print(f"[PAINT] Removed {removed_count} color attributes from collision mesh")
            print(f"[DEBUG]   Color attributes after removal: {list(cmesh.color_attributes.keys())}")

        print("[STAGE] paint_vertex_colors: EXIT")
        print("="*80 + "\n")
        return True
    except Exception as exc:
        print(f"[ERROR] Failed painting vertex colors - {exc}")
        import traceback
        traceback.print_exc()
        print("[STAGE] paint_vertex_colors: ERROR EXIT")
        print("="*80 + "\n")
        return False
