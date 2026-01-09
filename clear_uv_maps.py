import bpy


def clear_uv_maps(mesh: bpy.types.Mesh) -> None:
    """Remove all UV maps from the mesh."""
    if not mesh or not getattr(mesh, "uv_layers", None):
        return

    while len(mesh.uv_layers) > 0:
        mesh.uv_layers.remove(mesh.uv_layers[0])
