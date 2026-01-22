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
