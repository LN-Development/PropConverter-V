"""Constants and configuration values for PropConverter-V.

This module centralizes all magic strings, numbers, and configuration values
to improve maintainability and reduce errors from typos.
"""

# === Naming Conventions ===
COLLISION_SUFFIX = "col"
MODEL_CHILD_SUFFIX = ".model"
BVH_SUFFIX = ".bvh"
POLY_MESH_SUFFIX = ".poly_mesh"

# === Sollumz Integration ===
SOLLUMZ_MODULE_CANDIDATES = ("sollumz", "Sollumz")
SOLLUMZ_OPERATOR_NAMESPACE = "sollumz"
AUTOPROP_MODULE_IDENTIFIER = "autoprop"

# === Shader Configuration ===
DEFAULT_SHADER_NAME = "default.sps"

# === Color Attributes ===
VERTEX_COLOR_ATTRIBUTE_NAME = "Color 1"  # Sollumz expects this naming

# === Default Collision Flags ===
DEFAULT_COLLISION_FLAGS = {
    "not_climbable": True,
    "not_cover": True,
    "too_steep_for_player": True,
}

# All collision flag names for iteration
ALL_COLLISION_FLAGS = [
    "stairs",
    "not_climbable",
    "see_through",
    "shoot_through",
    "not_cover",
    "walkable_path",
    "no_cam_collision",
    "shoot_through_fx",
    "no_decal",
    "no_navmesh",
    "no_ragdoll",
    "vehicle_wheel",
    "no_ptfx",
    "too_steep_for_player",
    "no_network_spawn",
    "no_cam_collision_allow_clipping",
]

# === File Extensions ===
TEXTURE_EXTENSION = ".dds"

# === Transform Defaults ===
DEFAULT_LOCATION = (0.0, 0.0, 0.0)
DEFAULT_ROTATION = (0.0, 0.0, 0.0)
DEFAULT_SCALE = (1.0, 1.0, 1.0)

# === Dynamic Prop Configuration ===
# Composite Flags from GTA V roadcone reference (m23_2_prop_m32_roadcone_01a)
DYNAMIC_COMPOSITE_FLAGS1 = {
    "map_weapon": True,
    "map_dynamic": True,
    "map_animal": True,
    "map_cover": True,
    "map_vehicle": True,
}

DYNAMIC_COMPOSITE_FLAGS2 = {
    "vehicle_not_bvh": True,
    "vehicle_bvh": True,
    "ped": True,
    "ragdoll": True,
    "animal": True,
    "animal_ragdoll": True,
    "object": True,
    "plant": True,
    "projectile": True,
    "explosion": True,
    "forklift_forks": True,
    "test_weapon": True,
    "test_camera": True,
    "test_ai": True,
    "test_script": True,
    "test_vehicle_wheel": True,
    "glass": True,
}

# Bone flags that enable full physics movement (rotation + translation on all axes)
DYNAMIC_BONE_FLAGS = ["RotX", "RotY", "RotZ", "TransX", "TransY", "TransZ"]

# Sollumz standard bone size (tail offset from head)
DYNAMIC_BONE_TAIL_OFFSET = (0.0, 0.05, 0.0)

# Drawable properties for dynamic props (from roadcone reference)
DYNAMIC_UNKNOWN_1 = 51
DYNAMIC_UNKNOWN_5 = 216
