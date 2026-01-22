import bpy
from ... import constants


def paint_vertex_colors(original_obj: bpy.types.Object, collision_obj: bpy.types.Object, color=(1.0, 1.0, 1.0, 1.0)) -> bool:
    """Fill vertex colors on the original mesh (Color 1) and remove all vertex colors from the collision mesh.
    Uses Face Corner domain and Byte Color type as required."""
    try:
        if original_obj and original_obj.type == "MESH":
            mesh = original_obj.data
            loops = len(mesh.loops)
            if loops > 0:
                attr_name = constants.VERTEX_COLOR_ATTRIBUTE_NAME
                
                # Create or get color attribute with Face Corner and Byte Color
                if attr_name in mesh.color_attributes:
                    target_attr = mesh.color_attributes[attr_name]
                    # Ensure it's Face Corner and Byte Color
                    if target_attr.domain != 'CORNER' or target_attr.data_type != 'BYTE_COLOR':
                        mesh.color_attributes.remove(target_attr)
                        target_attr = mesh.color_attributes.new(
                            name=attr_name, 
                            type='BYTE_COLOR',
                            domain='CORNER'
                        )
                else:
                    target_attr = mesh.color_attributes.new(
                        name=attr_name, 
                        type='BYTE_COLOR',
                        domain='CORNER'
                    )
                
                # Fill with vertex color
                for loop_index in range(loops):
                    target_attr.data[loop_index].color = color

        if collision_obj and collision_obj.type == "MESH":
            cmesh = collision_obj.data
            # Remove all color attributes from collision mesh
            while len(cmesh.color_attributes) > 0:
                cmesh.color_attributes.remove(cmesh.color_attributes[0])

        return True
    except Exception as exc:
        print(f"[ERROR] Failed painting vertex colors - {exc}")
        return False
