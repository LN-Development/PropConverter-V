import bpy


def paint_vertex_colors(original_obj: bpy.types.Object, collision_obj: bpy.types.Object, color=(1.0, 1.0, 1.0, 1.0)) -> bool:
    """Fill vertex colors on the original mesh (Color 1) and remove all vertex colors from the collision mesh."""
    try:
        if original_obj and original_obj.type == "MESH":
            mesh = original_obj.data
            loops = len(mesh.loops)
            if loops > 0:
                attr_name = "Color 1"  # Sollumz expects this naming
                if hasattr(mesh, "attributes"):
                    target_attr = None
                    for a in mesh.attributes:
                        if a.name == attr_name:
                            target_attr = a
                            break
                    if target_attr is None or target_attr.domain != 'CORNER' or target_attr.data_type not in {'BYTE_COLOR', 'FLOAT_COLOR'}:
                        if target_attr is not None:
                            mesh.attributes.remove(target_attr)
                        target_attr = mesh.attributes.new(name=attr_name, type="BYTE_COLOR", domain="CORNER")

                    rgba = list(color[:4]) + ([1.0] if len(color) < 4 else [])
                    values = rgba * loops
                    try:
                        target_attr.data.foreach_set("color_srgb", values)
                    except Exception:
                        target_attr.data.foreach_set("color", values)
                else:
                    ca = mesh.color_attributes.get(attr_name)
                    if ca is None:
                        ca = mesh.color_attributes.new(name=attr_name, type="BYTE_COLOR", domain="CORNER")
                    for elem in ca.data:
                        elem.color = color

        if collision_obj and collision_obj.type == "MESH":
            cmesh = collision_obj.data
            if hasattr(cmesh, "attributes"):
                to_remove = [a for a in cmesh.attributes if a.data_type in {'BYTE_COLOR', 'FLOAT_COLOR'}]
                for a in to_remove:
                    cmesh.attributes.remove(a)
            elif hasattr(cmesh, "color_attributes"):
                while len(cmesh.color_attributes) > 0:
                    cmesh.color_attributes.remove(cmesh.color_attributes[0])

        return True
    except Exception as exc:
        print(f"ERROR: Failed painting vertex colors - {exc}")
        import traceback
        traceback.print_exc()
        return False
