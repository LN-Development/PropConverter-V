import bpy
from ... import constants


def bake_ambient_occlusion(context, obj: bpy.types.Object) -> bool:
    """
    Bake ambient occlusion to a color attribute named "AO".
    
    Args:
        context: Blender context
        obj: The mesh object to bake AO for
    
    Returns:
        True if successful, False otherwise
    """
    
    print("=" * 80)
    print("[AO_BAKE] Starting ambient occlusion bake process...")
    print("=" * 80)
    
    # Validate input
    if not obj or obj.type != 'MESH':
        print("[ERROR] Object is not a valid mesh")
        return False
    
    mesh = obj.data
    
    if not mesh.polygons:
        print("[ERROR] Mesh has no geometry")
        return False
    
    try:
        print("[AO_BAKE] Step 1/5: Enforcing smooth shading...")
        
        # CRITICAL: Ensure ALL polygons have smooth shading enabled
        # This replicates Sollumz mesh_builder.py line 85:
        # mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
        smooth_values = [True] * len(mesh.polygons)
        mesh.polygons.foreach_set("use_smooth", smooth_values)
        
        # Update mesh to apply shading changes
        mesh.update()
        context.view_layer.update()
        
        print(f"[AO_BAKE] ✓ Set smooth shading on {len(mesh.polygons)} polygons")
        
        # Ensure we're in object mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Make sure the object is selected and active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        print("[AO_BAKE] Step 2/5: Creating AO color attribute...")
        
        # Isolate the target object for rendering to prevent overlapping shadows (e.g. from collision meshes)
        original_render_visibility = {}
        for scene_obj in context.scene.objects:
            if scene_obj.type == 'MESH':
                original_render_visibility[scene_obj.name] = scene_obj.hide_render
                if scene_obj.name != obj.name:
                    scene_obj.hide_render = True
        
        # Remove existing AO attribute if it exists
        if hasattr(mesh, 'color_attributes') and "AO" in mesh.color_attributes:
            ao_attr = mesh.color_attributes.get("AO")
            if ao_attr:
                mesh.color_attributes.remove(ao_attr)
                print("[AO_BAKE] Removed existing AO attribute")
        
        # Create new AO color attribute (CORNER domain, BYTE_COLOR type)
        ao_attr = mesh.color_attributes.new(
            name="AO",
            type='BYTE_COLOR',
            domain='CORNER'
        )
        
        # Initialize to white (1.0, 1.0, 1.0, 1.0)
        for i in range(len(ao_attr.data)):
            ao_attr.data[i].color = (1.0, 1.0, 1.0, 1.0)
        
        print(f"[AO_BAKE] Created AO attribute with {len(ao_attr.data)} elements")
        
        # Set as active color attribute for baking
        mesh.color_attributes.active_color = ao_attr
        
        # Store original render engine
        original_engine = context.scene.render.engine
        print(f"[AO_BAKE] Step 3/5: Configuring Cycles render engine...")
        print(f"[AO_BAKE]   Original engine: {original_engine}")
        
        # Switch to Cycles (required for AO baking)
        if original_engine != 'CYCLES':
            context.scene.render.engine = 'CYCLES'
        
        # Configure bake settings
        context.scene.cycles.samples = 32  # Lower samples for faster bake
        context.scene.render.bake.use_pass_direct = False
        context.scene.render.bake.use_pass_indirect = False
        context.scene.render.bake.use_pass_color = False
        
        print("[AO_BAKE] Step 4/5: Performing AO bake...")
        
        # Perform the bake
        result = bpy.ops.object.bake(
            type='AO',
            target='VERTEX_COLORS',
            use_clear=False,
            margin=0
        )
        
        print("[AO_BAKE] Step 5/5: Restoring render engine...")
        if original_engine != 'CYCLES':
            print(f"[AO_BAKE] Restoring {original_engine} render engine...")
            context.scene.render.engine = original_engine
        
        if result == {'FINISHED'}:
            print("[SUCCESS] Ambient occlusion baked successfully!")
            
            print("[AO_BAKE] Step 6/6: Merging AO into 'Color 1' Red channel...")
            
            # Create or get standard vertex color 'Color 1'
            color_1_attr = None
            if constants.VERTEX_COLOR_ATTRIBUTE_NAME in mesh.color_attributes:
                color_1_attr = mesh.color_attributes.get(constants.VERTEX_COLOR_ATTRIBUTE_NAME)
                # Ensure it's the correct format
                if color_1_attr.domain != 'CORNER' or color_1_attr.data_type != 'BYTE_COLOR':
                    mesh.color_attributes.remove(color_1_attr)
                    color_1_attr = None
                    
            if not color_1_attr:
                color_1_attr = mesh.color_attributes.new(
                    name=constants.VERTEX_COLOR_ATTRIBUTE_NAME,
                    type='BYTE_COLOR',
                    domain='CORNER'
                )
                # Initialize Color 1 to white if newly created
                for i in range(len(color_1_attr.data)):
                    color_1_attr.data[i].color = (1.0, 1.0, 1.0, 1.0)
            
            # Merge AO (grayscale R channel) into Color 1 R channel
            for i in range(len(ao_attr.data)):
                ao_val = ao_attr.data[i].color[0]  # Get R channel of AO bake
                current_color = color_1_attr.data[i].color
                # Preserve G, B, A; overwrite R
                color_1_attr.data[i].color = (ao_val, current_color[1], current_color[2], current_color[3])
                
            print(f"[SUCCESS] Merged AO into {len(color_1_attr.data)} vertices.")
            
            # Remove the temporary AO layer
            mesh.color_attributes.remove(ao_attr)
            print("[AO_BAKE] Removed temporary AO attribute")
            
            return True
        else:
            print(f"[ERROR] Bake operation returned: {result}")
            return False
        
    except Exception as e:
        print(f"[ERROR] Failed to bake ambient occlusion: {e}")
        import traceback
        traceback.print_exc()
        
        # Restore original render engine on error
        try:
            if 'original_engine' in locals() and context.scene.render.engine != original_engine:
                context.scene.render.engine = original_engine
        except:
            pass
        
        return False
    finally:
        # Restore original render visibility
        try:
            if 'original_render_visibility' in locals():
                for scene_obj in context.scene.objects:
                    if scene_obj.name in original_render_visibility:
                        scene_obj.hide_render = original_render_visibility[scene_obj.name]
        except Exception as vis_err:
            print(f"[ERROR] Failed to restore original render visibility: {vis_err}")
            
        print("=" * 80)
