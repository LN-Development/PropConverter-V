import bpy
from typing import Optional


def _rename_uv_maps_sequential(mesh: bpy.types.Mesh) -> None:
    """Rename existing UV maps to 'UVMap 0', 'UVMap 1', ... preserving order."""
    if not mesh or not getattr(mesh, "uv_layers", None):
        return

    for idx, uv in enumerate(mesh.uv_layers):
        target_name = f"UVMap {idx}"
        if uv.name != target_name:
            uv.name = target_name


def _clear_uv_maps(mesh: bpy.types.Mesh) -> None:
    """Remove all UV maps from the mesh."""
    if not mesh or not getattr(mesh, "uv_layers", None):
        return

    while len(mesh.uv_layers) > 0:
        mesh.uv_layers.remove(mesh.uv_layers[0])


def paint_vertex_colors(original_obj: bpy.types.Object, collision_obj: bpy.types.Object, color=(1.0, 1.0, 1.0, 1.0)) -> bool:
    """Fill vertex colors on the original mesh (Color 1) and remove all vertex colors from the collision mesh."""
    try:
        if original_obj and original_obj.type == "MESH":
            mesh = original_obj.data
            loops = len(mesh.loops)
            if loops > 0:
                attr_name = "Color 1"  # Sollumz expects this naming (get_color_attr_name(0))
                if hasattr(mesh, "attributes"):
                    # Find attribute by name
                    target_attr = None
                    for a in mesh.attributes:
                        if a.name == attr_name:
                            target_attr = a
                            break
                    # Create or normalize the attribute
                    if target_attr is None or target_attr.domain != 'CORNER' or target_attr.data_type not in {'BYTE_COLOR', 'FLOAT_COLOR'}:
                        if target_attr is not None:
                            mesh.attributes.remove(target_attr)
                        target_attr = mesh.attributes.new(name=attr_name, type="BYTE_COLOR", domain="CORNER")

                    # Fill with uniform color (SRGB for BYTE_COLOR)
                    rgba = list(color[:4]) + ([1.0] if len(color) < 4 else [])
                    values = rgba * loops
                    try:
                        target_attr.data.foreach_set("color_srgb", values)
                    except Exception:
                        target_attr.data.foreach_set("color", values)
                else:
                    # Fallback to color_attributes container
                    ca = mesh.color_attributes.get(attr_name)
                    if ca is None:
                        ca = mesh.color_attributes.new(name=attr_name, type="BYTE_COLOR", domain="CORNER")
                    for elem in ca.data:
                        elem.color = color

        if collision_obj and collision_obj.type == "MESH":
            cmesh = collision_obj.data
            # Remove all color attributes
            if hasattr(cmesh, "attributes"):
                to_remove = [a for a in cmesh.attributes if a.data_type in {'BYTE_COLOR', 'FLOAT_COLOR'}]
                for a in to_remove:
                    cmesh.attributes.remove(a)
            elif hasattr(cmesh, "color_attributes"):
                while len(cmesh.color_attributes) > 0:
                    cmesh.color_attributes.remove(cmesh.color_attributes[0])

        return True
    except Exception as exc:
        print(f"ERROR: Failed painting vertex colors - {exc}")
        import traceback
        traceback.print_exc()
        return False


def convertToGtaV(context) -> bool:
    """
    Convert the selected mesh to a default prop
    Duplicates the object and adds 'col' to the duplicate's name
    Stores both objects in temporary memory for further operations
    """
    # Check if in Object Mode
    if context.mode != 'OBJECT':
        print(f"ERROR: Must be in Object Mode (current mode: {context.mode})")
        return False
    
    # Get active object
    obj = context.active_object
    
    # Check if there's an active object
    if obj is None:
        print("ERROR: No active object")
        return False
    
    # Check if it's a mesh
    if obj.type != "MESH":
        print(f"ERROR: Object is not a mesh")
        return False
    
    # Check if selected is active (
    if not obj.select_get():
        print(f"ERROR: Object outline is not selected")
        return False
    
    # Sanitize mesh name: convert to lowercase and remove spaces BEFORE any operations
    sanitized_name = obj.name.lower().replace(" ", "")
    if sanitized_name != obj.name:
        print(f"Renaming mesh from '{obj.name}' to '{sanitized_name}'")
        obj.name = sanitized_name
    
    original_name = obj.name
    print(f"Original object name: {original_name}")
    
    try:
        
        # Save reference to original mesh in temporary memory
        context.scene.prop_converter.original_mesh = obj
        print(f"Saved original mesh to temporary memory: {obj.name}")
        
        # Deselect all first
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select only the target object
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        print(f"Object selected: {obj.select_get()}")
        print(f"Active object: {context.view_layer.objects.active.name}")
        
        # Duplicate the object using copy
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.animation_data_clear()

        # Link to scene collection
        context.collection.objects.link(new_obj)

        print(f"Duplicated object created: {new_obj.name}")

        # Normalize UV maps on the original; clear them on the collision duplicate
        _rename_uv_maps_sequential(obj.data)
        _clear_uv_maps(new_obj.data)
        
        # Add 'col' to the end of the name
        new_name = f"{original_name}col"
        new_obj.name = new_name
        
        # Save reference to collision mesh in temporary memory
        context.scene.prop_converter.collision_mesh = new_obj
        print(f"Saved collision mesh to temporary memory: {new_obj.name}")

        # Paint vertex colors on original and clear collision vertex colors using selected color
        paint_col = getattr(getattr(context.scene, "prop_converter", None), "vertex_color", (1.0, 1.0, 1.0, 1.0))
        print(f"Painting vertex colors on original (Color 1) and clearing on collision with color: {paint_col}")
        paint_vertex_colors(obj, new_obj, color=tuple(paint_col))

        # Resolve Sollumz module for collision material imports
        import importlib, sys
        mod_name = None
        for name in ("sollumz", "Sollumz"):
            try:
                importlib.import_module(name)
                mod_name = name
                break
            except ImportError:
                continue

        if mod_name is None:
            for key in sys.modules.keys():
                if key.lower().endswith("sollumz"):
                    mod_name = key
                    break

        # Convert collision mesh to Bound Composite using Sollumz operator
        try:
            bpy.ops.object.select_all(action='DESELECT')
            new_obj.select_set(True)
            context.view_layer.objects.active = new_obj
            pre_object_names = {o.name for o in bpy.data.objects}
            bpy.ops.sollumz.converttocomposite()
            # Identify created BVH from newly added objects
            created_objs = [o for o in bpy.data.objects if o.name not in pre_object_names]
            bvh_obj = next((o for o in created_objs if o.name.lower().endswith(".bvh")), None)
            if bvh_obj is None:
                # Fallback search in case naming/creation differs
                bvh_obj = next((o for o in bpy.data.objects if o.name.lower().endswith(".bvh")), None)
            if bvh_obj:
                bpy.ops.object.select_all(action='DESELECT')
                bvh_obj.select_set(True)
                context.view_layer.objects.active = bvh_obj
                try:
                    bpy.ops.sollumz.load_flag_preset()
                    print("Applied flag preset to BVH via operator.")
                except Exception as op_err:
                    print(f"WARNING: Could not apply flag preset via operator: {op_err}")
            
            # Find the .poly_mesh child and convert its materials to collision material
            poly_mesh = next((o for o in bpy.data.objects if o.name.endswith(".poly_mesh") and o.parent and o.parent.name == (bvh_obj.name if bvh_obj else "")), None)
            if poly_mesh and mod_name:
                print(f"Found poly_mesh: {poly_mesh.name}")
                bpy.ops.object.select_all(action='DESELECT')
                poly_mesh.select_set(True)
                context.view_layer.objects.active = poly_mesh
                
                # Convert all materials to collision materials (preserving count)
                try:
                    collision_mat_index = getattr(context.window_manager, "sz_collision_material_index", 0)
                    print(f"Converting materials to collision material index: {collision_mat_index}")
                    
                    # Import collision material creation function
                    collision_materials = importlib.import_module(f"{mod_name}.ybn.collision_materials")
                    create_collision_material = collision_materials.create_collision_material_from_index
                    
                    # Convert each existing material to a collision material
                    mesh = poly_mesh.data
                    num_materials = len(mesh.materials)
                    
                    if num_materials > 0:
                        # Replace each material with a collision material (preserving slot count)
                        for i in range(num_materials):
                            collision_mat = create_collision_material(collision_mat_index)
                            mesh.materials[i] = collision_mat
                            print(f"Converted material slot {i} to collision material")
                    else:
                        # If no materials, create one
                        collision_mat = create_collision_material(collision_mat_index)
                        mesh.materials.append(collision_mat)
                        print(f"Created collision material for empty mesh")
                    
                    print(f"Successfully converted all materials to collision material on {poly_mesh.name}")
                except Exception as mat_err:
                    print(f"WARNING: Could not apply collision material to poly_mesh: {mat_err}")
                    import traceback
                    traceback.print_exc()
            else:
                print("WARNING: Could not find .poly_mesh child for collision material conversion")
            
            # Store composite reference to parent it after drawable conversion
            composite_obj = None
            if bvh_obj:
                composite_obj = bvh_obj.parent
            
            print("Successfully converted collision mesh to Bound Composite")
        except Exception as e:
            print(f"ERROR: Failed to convert collision mesh to composite - {e}")
            import traceback
            traceback.print_exc()
        
        # Select the original object to convert to drawable
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        print(f"Converting original mesh '{obj.name}' to drawable...")
        
        # Call Sollumz convert to drawable operation
        try:
            bpy.ops.sollumz.converttodrawable()
            print(f"Successfully converted '{obj.name}' to drawable")
            
            # Find the drawable parent and all drawable model mesh children
            drawable_parent = obj.parent
            model_objs = []

            # Helper to collect model meshes under a parent
            def _collect_model_meshes(parent):
                found = []
                if not parent:
                    return found
                for child in parent.children:
                    if child.type == 'MESH' and (child.name.endswith('.model') or getattr(child, 'sollum_type', None) is not None and 'MODEL' in str(child.sollum_type)):
                        found.append(child)
                    # Some setups nest models deeper
                    found.extend(_collect_model_meshes(child))
                return found

            if drawable_parent:
                model_objs = _collect_model_meshes(drawable_parent)
                if model_objs:
                    print(f"Found drawable models: {[m.name for m in model_objs]}")
                else:
                    print(f"WARNING: Could not find .model child, using original object")
                    model_objs = [obj]
            else:
                print(f"WARNING: No drawable parent found, using original object")
                model_objs = [obj]
            
            # Parent collision structure to the Drawable 
            if composite_obj:
                if drawable_parent:
                    print(f"Parenting collision composite {composite_obj.name} to drawable {drawable_parent.name}")
                    composite_obj.parent = drawable_parent
                    composite_obj.location = (0, 0, 0)  # Reset location relative to parent
                    print(f"Successfully parented collision structure to drawable {drawable_parent.name}")
                else:
                    print("WARNING: Mesh has no drawable parent, parenting composite to mesh instead")
                    composite_obj.parent = obj
                    composite_obj.location = (0, 0, 0)
        except Exception as e:
            print(f"ERROR: Failed to convert to drawable - {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Convert all materials using the shader selected in Sollumz (falls back to default.sps if invalid)
        print(f"Converting all materials to selected shader (fallback: default.sps)...")
        try:
            import importlib, sys

            # Resolve Sollumz module name even if registered under different casing/path
            mod_name = None
            for name in ("sollumz", "Sollumz"):
                try:
                    importlib.import_module(name)
                    mod_name = name
                    break
                except ImportError:
                    continue

            if mod_name is None:
                # Try to discover from already loaded modules
                for key in sys.modules.keys():
                    if key.lower().endswith("sollumz"):
                        mod_name = key
                        break

            if mod_name is None:
                print("ERROR: Sollumz addon is not installed or not in sys.path")
                return False

            shadermats = importlib.import_module(f"{mod_name}.ydr.shader_materials").shadermats

            wm = context.window_manager
            selected_idx = getattr(wm, "sz_shader_material_index", -1)

            # Validate selected index; fallback to default.sps if invalid
            if not (0 <= selected_idx < len(shadermats)):
                selected_idx = next((i for i, shader in enumerate(shadermats) if shader.value == "default.sps"), None)
                if selected_idx is None:
                    print("ERROR: Could not find default.sps shader")
                    return False
                wm.sz_shader_material_index = selected_idx
                print(f"Selected shader index invalid; falling back to default.sps at {selected_idx}")
            else:
                print(f"Using user-selected shader index: {selected_idx} ({shadermats[selected_idx].value})")

            # Select the model objects for material conversion (process first model as active)
            if model_objs:
                bpy.ops.object.select_all(action='DESELECT')
                for m in model_objs:
                    m.select_set(True)
                context.view_layer.objects.active = model_objs[0]
            
            bpy.ops.sollumz.convertallmaterialstoselected()
            print("Successfully converted all materials to selected shader")
        except Exception as e:
            print(f"ERROR: Failed to convert materials - {e}")
            import traceback
            traceback.print_exc()
            return False
        
        
        print(f"SUCCESS: Duplicated '{original_name}' as '{new_obj.name}'")
        print(f"Both objects stored in temporary memory")
        
        # Create YTYP with the original mesh name
        try:
            print(f"Creating YTYP with name: {original_name}")
            ytyp_item = context.scene.ytyps.add()
            ytyp_item.name = original_name
            context.scene.ytyp_index = len(context.scene.ytyps) - 1
            print(f"Successfully created YTYP: {ytyp_item.name} at index {context.scene.ytyp_index}")
        except Exception as e:
            print(f"WARNING: Failed to create YTYP - {e}")
            import traceback
            traceback.print_exc()
        
        # Create archetype from the converted drawable 
        try:
            print(f"Creating archetype from drawable: {obj.name}")
            print(f"Object sollum_type: {obj.sollum_type}")
            
            # Import ArchetypeType and SollumType from Sollumz addon
            import importlib
            sollumz_props = importlib.import_module(f"{mod_name}.sollumz_properties")
            ArchetypeType = sollumz_props.ArchetypeType
            SollumType = sollumz_props.SollumType
            
        
           
            drawable_parent = obj.parent if obj.parent and obj.parent.sollum_type == SollumType.DRAWABLE else None
            
            if drawable_parent is None:
                print(f"WARNING: Could not find parent Drawable for {obj.name}")
                # If no parent, check if obj itself is the drawable
                if obj.sollum_type == SollumType.DRAWABLE:
                    drawable_parent = obj
                else:
                    print(f"ERROR: {obj.name} is not inside a Drawable structure")
                    raise Exception("Could not find Drawable object for archetype creation")
            
            print(f"Found drawable parent: {drawable_parent.name} (type: {drawable_parent.sollum_type})")
            
            # Set the archetype type to BASE (default for simple props)
            context.scene.create_archetype_type = ArchetypeType.BASE
            print(f"Set create_archetype_type to: {context.scene.create_archetype_type}")
            
            # Ensure ONLY the parent drawable is selected and active
            bpy.ops.object.select_all(action='DESELECT')
            drawable_parent.select_set(True)
            context.view_layer.objects.active = drawable_parent
            
            print(f"Drawable is selected: {drawable_parent.select_get()}")
            print(f"Active object: {context.view_layer.objects.active.name if context.view_layer.objects.active else 'None'}")
            print(f"Selected objects: {[o.name for o in context.selected_objects]}")
            print(f"YTYP index: {context.scene.ytyp_index}")
            
         
            context.view_layer.update()
            
            # Call the sollumz operator to create archetype from selected
            result = bpy.ops.sollumz.createarchetypefromselected()
            print(f"Operator result: {result}")
            
            # Get the newly created archetype and override texture_dictionary to original mesh name
            selected_ytyp = context.scene.ytyps[context.scene.ytyp_index]
            print(f"Number of archetypes in YTYP: {len(selected_ytyp.archetypes)}")
            
            if len(selected_ytyp.archetypes) > 0:
                archetype = selected_ytyp.archetypes[-1]  # Get the last added archetype
                archetype.texture_dictionary = original_name
                print(f"Successfully created archetype: {archetype.name} with texture_dictionary: {original_name}")
            else:
                print(f"WARNING: No archetypes found after calling createarchetypefromselected")
        except Exception as e:
            print(f"WARNING: Failed to create archetype - {e}")
            import traceback
            traceback.print_exc()
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to duplicate object - {e}")
        import traceback
        traceback.print_exc()
        return False

