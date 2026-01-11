import bpy


def bake_ambient_occlusion(context, obj: bpy.types.Object) -> bool:
    """
    Bake ambient occlusion to vertex colors on the selected object.
    Uses Cycles render settings from the scene.
    
    Args:
        context: Blender context
        obj: The mesh object to bake AO on
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print("\n[AO_BAKE] Starting ambient occlusion bake...")
        
        # Validate and get mesh
        if not obj or obj.type != 'MESH':
            print("[ERROR] Invalid object - must be a mesh")
            return False
        
        mesh = obj.data
        if not hasattr(mesh, 'color_attributes'):
            print("[ERROR] Mesh doesn't support color_attributes")
            return False
        
        # Switch to object mode if needed
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Select the target object
        for o in context.scene.objects:
            o.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Create/replace AO color attribute
        ao_attr = mesh.color_attributes.get("AO")
        if ao_attr:
            mesh.color_attributes.remove(ao_attr)
        
        color_attr = mesh.color_attributes.new(
            name="AO",
            type='BYTE_COLOR',
            domain='CORNER'
        )
        
        # Initialize to white
        for i in range(len(color_attr.data)):
            color_attr.data[i].color = (1.0, 1.0, 1.0, 1.0)
        
        # Set as active for baking
        mesh.color_attributes.active_color = color_attr
        
        # Store original render engine
        original_engine = context.scene.render.engine
        
        # Switch to Cycles
        if context.scene.render.engine != 'CYCLES':
            context.scene.render.engine = 'CYCLES'
        
        # Bake AO
        result = bpy.ops.object.bake(
            type='AO',
            target='VERTEX_COLORS',
            use_clear=True,
            margin=0
        )
        
        # Restore render engine
        if context.scene.render.engine != original_engine:
            context.scene.render.engine = original_engine
        
        if 'FINISHED' not in result:
            print(f"[ERROR] Bake operation returned: {result}")
            return False
        
        print("[SUCCESS] Ambient occlusion baked successfully!")
        print("[AO_BAKE] Baking complete")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to bake ambient occlusion: {e}")
        import traceback
        traceback.print_exc()
        return False
