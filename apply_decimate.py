import bpy


def apply_decimate(context, obj: bpy.types.Object, decimate_type: str, ratio: float = 0.5, iterations: int = 1, use_dissolve: bool = False, planar_angle: float = 80.0) -> bool:
    """Apply decimate modifier to collision mesh with selected technique."""
    try:
        if not obj or obj.type != 'MESH':
            print("ERROR: Invalid object for decimate")
            return False
        
        print(f"Applying decimate modifier ({decimate_type}) to {obj.name}")
        
        # Add decimate modifier
        decimate_mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
        decimate_mod.decimate_type = decimate_type
        
        # Set parameters based on type
        if decimate_type == 'COLLAPSE':
            decimate_mod.ratio = ratio
            print(f"Collapse mode - ratio: {ratio}")
        elif decimate_type == 'UNSUBDIV':
            decimate_mod.iterations = iterations
            decimate_mod.use_dissolve = use_dissolve
            print(f"Un-subdivide mode - iterations: {iterations}, dissolve: {use_dissolve}")
        elif decimate_type == 'PLANAR':
            decimate_mod.angle_limit = planar_angle
            print(f"Planar mode - angle: {planar_angle}")
        
        # Apply the modifier
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Apply modifier using Blender operator
        bpy.ops.object.modifier_apply(modifier=decimate_mod.name)
        
        print(f"Successfully applied decimate modifier to {obj.name}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to apply decimate modifier - {e}")
        import traceback
        traceback.print_exc()
        return False
