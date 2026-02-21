import bpy
from bpy.props import PointerProperty
from . import i18n
from . import constants


def update_language(self, context):
    """Update language when user changes preference"""
    i18n.set_language(self.language)
    # Save user preferences to persist the language selection
    try:
        bpy.ops.wm.save_userpref()
    except:
        pass  # Ignore if saving fails


def update_default_flags(self, context):
    """Apply default collision flags when use_default_flags is enabled.
    
    This function uses constants to eliminate magic values and uses
    iteration to reduce code duplication (DRY principle).
    """
    if self.use_default_flags:
        # Set default flags from constants
        for flag_name, flag_value in constants.DEFAULT_COLLISION_FLAGS.items():
            setattr(self.collision_flags, flag_name, flag_value)
        
        # Clear all non-default flags
        for flag_name in constants.ALL_COLLISION_FLAGS:
            if flag_name not in constants.DEFAULT_COLLISION_FLAGS:
                setattr(self.collision_flags, flag_name, False)


def update_hinge_preset(self, context):
    """Synchronize the custom offset slider with the selected preset."""
    factors = {
        'LEFT': 0.0,
        'RIGHT': 100.0,
        'BOTTOM': 0.0,
        'TOP': 100.0,
        'MID': 50.0
    }
    if self.door_hinge_side in factors:
        self.door_hinge_custom_offset = factors[self.door_hinge_side]
    
    # Disable custom alignment if Middle is selected (as requested)
    if self.door_hinge_side == 'MID':
        self.use_custom_hinge_offset = False


def update_prop_type(self, context):
    """Ensure mutual exclusivity between Dynamic and Door prop types."""
    if self.is_dynamic_prop:
        self["is_door_prop"] = False
    elif self.is_door_prop:
        self["is_dynamic_prop"] = False


def update_door_type(self, context):
    """Automatically set special_attribute based on selected door_type."""
    mapping = {
        'GARAGE': 5,
        'NORMAL': 7,
        'SLIDING': 8,
        'BARRIER': 9,
        'SLIDING_VERTICAL': 10,
        'RAIL_CROSSING': 12
    }
    if self.door_type in mapping:
        self.special_attribute = mapping[self.door_type]


class CollisionFlagsProperties(bpy.types.PropertyGroup):
    """Collision material flags that will be applied during conversion"""
    stairs: bpy.props.BoolProperty(name="STAIRS", default=False)
    not_climbable: bpy.props.BoolProperty(name="NOT CLIMBABLE", default=False)
    see_through: bpy.props.BoolProperty(name="SEE THROUGH", default=False)
    shoot_through: bpy.props.BoolProperty(name="SHOOT THROUGH", default=False)
    not_cover: bpy.props.BoolProperty(name="NOT COVER", default=False)
    walkable_path: bpy.props.BoolProperty(name="WALKABLE PATH", default=False)
    no_cam_collision: bpy.props.BoolProperty(name="NO CAM COLLISION", default=False)
    shoot_through_fx: bpy.props.BoolProperty(name="SHOOT THROUGH FX", default=False)
    no_decal: bpy.props.BoolProperty(name="NO DECAL", default=False)
    no_navmesh: bpy.props.BoolProperty(name="NO NAVMESH", default=False)
    no_ragdoll: bpy.props.BoolProperty(name="NO RAGDOLL", default=False)
    vehicle_wheel: bpy.props.BoolProperty(name="VEHICLE WHEEL", default=False)
    no_ptfx: bpy.props.BoolProperty(name="NO PTFX", default=False)
    too_steep_for_player: bpy.props.BoolProperty(name="TOO STEEP FOR PLAYER", default=False)
    no_network_spawn: bpy.props.BoolProperty(name="NO NETWORK SPAWN", default=False)
    no_cam_collision_allow_clipping: bpy.props.BoolProperty(name="NO CAM COLLISION ALLOW CLIPPING", default=False)


class PROPCONVERTER_Properties(bpy.types.PropertyGroup):

    language: bpy.props.EnumProperty(
        name="Language",
        description="Interface language",
        items=[
            ('en_US', "English (USA)", "English (United-Statesian)"),
            ('es_ES', "Español", "Spanish"),
            ('pt_BR', "Português (Brasil)", "Portuguese (Brazilian)"),
        ],
        update=update_language,
        default='en_US',
    )

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
        default=(1.0, 0.0, 1.0, 1.0),
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

    use_default_flags: bpy.props.BoolProperty(
        name="Use Default Flags",
        description="Apply default collision flags (NOT CLIMBABLE, NOT COVER, TOO STEEP FOR PLAYER)",
        default=False,
        update=update_default_flags,
    )

    customize_collision_flags: bpy.props.BoolProperty(
        name="Customize Flags",
        description="Show collision flags customization options",
        default=False,
    )

    collision_flags: PointerProperty(
        name="Collision Flags",
        description="Collision material flags to apply during conversion",
        type=CollisionFlagsProperties
    )

    model_info: bpy.props.StringProperty(
        name="Model Information",
        description="Gathered information about the model and Sollumz metadata",
        default="",
    )

    is_dynamic_prop: bpy.props.BoolProperty(
        name="Dynamic Prop",
        description="Convert as a dynamic prop with physics (pushable, reactable). Sets composite flags, bone flags, and physics dictionary",
        default=False,
        update=update_prop_type,
    )

    is_door_prop: bpy.props.BoolProperty(
        name="Door Prop",
        description="Convert as a door. Uses embedded Bound Box collision and specific bone flags",
        default=False,
        update=update_prop_type,
    )

    door_type: bpy.props.EnumProperty(
        name="Door Type",
        description="Type of door behavior in GTA V",
        items=[
            ('NORMAL', "Normal Door", "Common swinging door"),
            ('GARAGE', "Garage Door", "Standard rollup/garage door"),
            ('SLIDING', "Sliding Door", "Horizontal sliding door"),
            ('BARRIER', "Barrier Door", "Parking/toll barrier arm"),
            ('SLIDING_VERTICAL', "Sliding Vertical Door", "Door that slides upwards"),
            ('RAIL_CROSSING', "Rail Crossing Barrier Door", "Train crossing barrier"),
        ],
        default='NORMAL',
        update=update_door_type,
    )

    special_attribute: bpy.props.IntProperty(
        name="Special Attribute",
        description="Sollumz Special Attribute for the door",
        default=7, # Default for Normal Door
        min=0,
        max=255,
    )

    door_hinge_side: bpy.props.EnumProperty(
        name="Hinge Preset",
        description="Choose a starting side or center for alignment",
        items=[
            ('LEFT', "Left", "Horizontal 0%"),
            ('RIGHT', "Right", "Horizontal 100%"),
            ('BOTTOM', "Bottom", "Vertical 0%"),
            ('TOP', "Top", "Vertical 100%"),
            ('MID', "Middle", "Vertical 50%"),
        ],
        default='LEFT',
        update=update_hinge_preset
    )

    use_custom_hinge_offset: bpy.props.BoolProperty(
        name="Custom Alignment",
        description="Manually specify the offset percentage",
        default=False
    )

    door_hinge_custom_offset: bpy.props.FloatProperty(
        name="Offset %",
        description="Offset percentage from the minimum edge (0% = Min, 100% = Max)",
        default=0.0,
        min=0.0,
        max=100.0,
        precision=1,
        subtype='PERCENTAGE'
    )


class PROPCONVERTER_ExportPreferences(bpy.types.AddonPreferences):
    """Global addon preferences for export settings.
    
    These settings persist across all Blender sessions and .blend files,
    matching Sollumz's behavior exactly.
    """
    # Get the root addon package name (handles both normal addons and Blender 5.0 extensions)
    bl_idname = __package__.split('.operators')[0] if '.operators' in __package__ else __package__
    if __package__.startswith('bl_ext.'):
        # For Blender 5.0 extensions: bl_ext.user_default.propconverterv
        parts = __package__.split('.')
        bl_idname = '.'.join(parts[:3]) if len(parts) >= 3 else __package__
    
    # Mesh Domain Selection (exclusive - only one can be selected)
    export_mesh_domain: bpy.props.EnumProperty(
        name="Mesh Domain",
        description="Select which mesh domain to export",
        items=[
            ('FACE_CORNER', "Face Corner", "Export Face Corner domain attributes (UVs, vertex colors)"),
            ('VERTEX', "Vertex", "Export Vertex domain attributes"),
        ],
        default='FACE_CORNER',
    )
    
    # Export Format Options
    export_format_native: bpy.props.BoolProperty(
        name="Native",
        description="Export in native binary format",
        default=True,
    )
    
    export_format_xml: bpy.props.BoolProperty(
        name="CodeWalker XML",
        description="Export as CodeWalker XML",
        default=True,
    )
    
    # Target Version Options
    target_version_gen8: bpy.props.BoolProperty(
        name="Gen 8",
        description="GTAV Legacy",
        default=True,
    )
    
    target_version_gen9: bpy.props.BoolProperty(
        name="Gen 9",
        description="GTAV Enhanced",
        default=True,
    )



classes = [
    CollisionFlagsProperties,
    PROPCONVERTER_Properties,
    PROPCONVERTER_ExportPreferences,
]


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass  # Already registered
    bpy.types.Scene.prop_converter = bpy.props.PointerProperty(type=PROPCONVERTER_Properties)

def unregister():
    if hasattr(bpy.types.Scene, "prop_converter"):
        del bpy.types.Scene.prop_converter
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
