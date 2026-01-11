# Mesh preparation utilities
from .duplicate_and_prepare import duplicate_and_prepare_mesh
from .rename_uv_maps import rename_uv_maps_sequential
from .clear_uv_maps import clear_uv_maps
from .apply_decimate import apply_decimate
from .apply_remesh import apply_remesh

__all__ = [
    'duplicate_and_prepare_mesh',
    'rename_uv_maps_sequential',
    'clear_uv_maps',
    'apply_decimate',
    'apply_remesh',
]
