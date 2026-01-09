import bpy
from bpy.props import PointerProperty


class PROPCONVERTER_Properties(bpy.types.PropertyGroup):

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

    enable_decimate: bpy.props.BoolProperty(
        name="Enable Decimate",
        description="Apply decimate modifier to collision mesh to reduce polygon count",
        default=False,
    )

    decimate_type: bpy.props.EnumProperty(
        name="Decimate Type",
        description="Type of decimation to apply",
        items=[
            ('COLLAPSE', "Collapse", "Collapse edges"),
            ('UNSUBDIV', "Un-subdivide", "Remove subdivision surfaces"),
            ('PLANAR', "Planar", "Remove planar faces"),
        ],
        default='UNSUBDIV',
    )

    decimate_ratio: bpy.props.FloatProperty(
        name="Decimate Ratio",
        description="Ratio of faces to keep (for Collapse mode)",
        min=0.0,
        max=1.0,
        default=0.5,
    )

    decimate_iterations: bpy.props.IntProperty(
        name="Decimate Iterations",
        description="Number of times to un-subdivide the collision mesh (for Un-subdivide mode)",
        min=0,
        max=10,
        default=1,
    )

    decimate_use_dissolve: bpy.props.BoolProperty(
        name="Use Dissolve",
        description="Dissolve edges when un-subdividing (for Un-subdivide mode)",
        default=False,
    )

    decimate_planar_angle: bpy.props.FloatProperty(
        name="Planar Angle",
        description="Angle threshold for planar decimation (for Planar mode)",
        min=0.0,
        max=180.0,
        default=80.0,
    )

    enable_remesh: bpy.props.BoolProperty(
        name="Enable Remesh",
        description="Apply remesh modifier to collision mesh",
        default=False,
    )

    remesh_mode: bpy.props.EnumProperty(
        name="Remesh Mode",
        description="Type of remesh to apply",
        items=[
            ('blocks', "Blocks", "Blocky remesh"),
            ('smooth', "Smooth", "Smooth remesh"),
            ('sharp', "Sharp", "Sharp remesh"),
            ('voxels', "Voxels", "Voxel-based remesh"),
        ],
        default='smooth',
    )

    remesh_use_smooth_shade: bpy.props.BoolProperty(
        name="Smooth Shading",
        description="Use smooth shading for remesh",
        default=True,
    )

    remesh_threshold: bpy.props.FloatProperty(
        name="Threshold",
        description="Threshold for blocks, smooth, and sharp remesh modes",
        min=0.0,
        max=1.0,
        default=0.1,
    )

    remesh_voxel_size: bpy.props.FloatProperty(
        name="Voxel Size",
        description="Size of voxels for voxel mode remesh (smaller = higher detail)",
        min=0.01,
        max=1.0,
        default=0.1,
    )

    remesh_adaptivity: bpy.props.FloatProperty(
        name="Adaptivity",
        description="Adaptivity for voxel remesh (higher = more reduction)",
        min=0.0,
        max=1.0,
        default=0.0,
    )

    auto_texture_from_mesh_name: bpy.props.BoolProperty(
        name="Auto Texture from Mesh Name",
        description="After conversion, set each material's textures to external files named from the original mesh (e.g., mesh0_diffuse.dds)",
        default=False,
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
