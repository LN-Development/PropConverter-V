import bpy


def apply_remesh(context, obj: bpy.types.Object, mode: str, use_smooth_shade: bool = True, threshold: float = 0.1, voxel_size: float = 0.1, adaptivity: float = 0.0) -> bool:
    """Apply remesh modifier to collision mesh."""
    try:
        if not obj or obj.type != 'MESH':
            print("ERROR: Invalid object for remesh")
            return False
        
        print(f"Applying remesh modifier to {obj.name} with mode: {mode}")
        
        # Add remesh modifier
        remesh_mod = obj.modifiers.new(name="Remesh", type='REMESH')
        remesh_mod.use_smooth_shade = use_smooth_shade
        
        # Set mode based on user selection
        if mode == 'blocks':
            remesh_mod.mode = 'BLOCKS'
            remesh_mod.threshold = threshold
            print(f"Blocks mode - threshold: {threshold}")
        elif mode == 'smooth':
            remesh_mod.mode = 'SMOOTH'
            remesh_mod.threshold = threshold
            print(f"Smooth mode - threshold: {threshold}")
        elif mode == 'sharp':
            remesh_mod.mode = 'SHARP'
            remesh_mod.threshold = threshold
            print(f"Sharp mode - threshold: {threshold}")
        elif mode == 'voxels':
            remesh_mod.mode = 'VOXELS'
            remesh_mod.voxel_size = voxel_size
            remesh_mod.adaptivity = adaptivity
            print(f"Voxels mode - voxel_size: {voxel_size}, adaptivity: {adaptivity}")
        
        # Apply the modifier
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Apply modifier using Blender operator
        bpy.ops.object.modifier_apply(modifier=remesh_mod.name)
        
        print(f"Successfully applied remesh modifier ({mode}) to {obj.name}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to apply remesh modifier - {e}")
        import traceback
        traceback.print_exc()
        return False
