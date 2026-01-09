import bpy


def rename_uv_maps_sequential(mesh: bpy.types.Mesh) -> None:
    """Rename existing UV maps to 'UVMap 0', 'UVMap 1', ... preserving order."""
    if not mesh or not getattr(mesh, "uv_layers", None):
        return

    for idx, uv in enumerate(mesh.uv_layers):
        target_name = f"UVMap {idx}"
        if uv.name != target_name:
            uv.name = target_name
