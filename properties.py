import bpy
from bpy.props import PointerProperty


class PROPCONVERTER_Properties(bpy.types.PropertyGroup):
    """Custom properties for Auto Prop addon"""

    original_mesh: PointerProperty(
        name="Original Mesh",
        description="Reference to the original mesh object",
        type=bpy.types.Object
    )

    collision_mesh: PointerProperty(
        name="Collision Mesh",
        description="Reference to the collision mesh object (with 'col' suffix)",
        type=bpy.types.Object
    )

    vertex_color: bpy.props.FloatVectorProperty(
        name="Vertex Color",
        description="Color used to paint vertices on the original mesh",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )


classes = [
    PROPCONVERTER_Properties,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.prop_converter = bpy.props.PointerProperty(type=PROPCONVERTER_Properties)

def unregister():
    if hasattr(bpy.types.Scene, "prop_converter"):
        del bpy.types.Scene.prop_converter
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
