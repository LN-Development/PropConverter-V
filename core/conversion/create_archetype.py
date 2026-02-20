import bpy
from ...sollumz_integration import SollumzIntegration


def create_archetype(context, obj, mod_name: str, original_name: str, is_dynamic: bool = False, is_door: bool = False):
    """Create a new archetype in the selected YTYP for the converted drawable."""
    try:
        print(f"Creating archetype from drawable: {obj.name}")
        sollumz = SollumzIntegration.get_instance()
        sollumz_props = sollumz.get_sollumz_properties()
        
        if not sollumz_props:
            print("[ERROR] Could not load Sollumz properties")
            return False
        
        SollumType = sollumz_props.SollumType

        # Find the Drawable parent
        drawable_parent = obj if obj.sollum_type == SollumType.DRAWABLE else obj.parent
        if not drawable_parent or drawable_parent.sollum_type != SollumType.DRAWABLE:
            print(f"ERROR: {obj.name} is not inside a Drawable structure")
            return False

        print(f"Found drawable parent: {drawable_parent.name} (type: {drawable_parent.sollum_type})")
        
        # Ensure it is selected and active for Sollumz operator
        bpy.ops.object.select_all(action='DESELECT')
        drawable_parent.select_set(True)
        context.view_layer.objects.active = drawable_parent
        
        # Create archetype from selected
        bpy.ops.sollumz.createarchetypefromselected()
        
        # Access the newly created archetype in the current YTYP
        ytyp_index = context.scene.ytyp_index
        if ytyp_index < 0 or ytyp_index >= len(context.scene.ytyps):
            print("[ERROR] No valid YTYP selected after creation")
            return False
            
        ytyp = context.scene.ytyps[ytyp_index]
        if not ytyp.archetypes:
            print("[ERROR] No archetypes found in YTYP after creation")
            return False
            
        archetype = ytyp.archetypes[-1]
        
        # Set texture dictionary to match the prop name
        archetype.texture_dictionary = original_name
        
        # Physics Dictionary & Flags
        # Doors and Dynamic props both need physics_dictionary set to asset name
        if is_dynamic or is_door:
            archetype.physics_dictionary = original_name
            
            # Clear ALL flags first to ensure a clean state
            for i in range(32):
                flag_attr = f"flag{i}"
                if hasattr(archetype.flags, flag_attr):
                    setattr(archetype.flags, flag_attr, False)

            if is_door:
                # User specifically requested flags 67239936 for doors
                # 67239936 = 2^17 (Bit 17) + 2^26 (Bit 26)
                archetype.flags.flag17 = True
                archetype.flags.flag26 = True
                print(f"[DOOR] Cleared all flags and set Flags 17/26 (Value: 67239936)")
            elif is_dynamic:
                # Standard Dynamic bit is 18
                archetype.flags.flag18 = True
                print(f"[DYNAMIC] Cleared all flags and set Flag 18")
            
        print(f"Successfully created archetype: {archetype.name} with texture_dictionary: {original_name}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create archetype - {e}")
        import traceback
        traceback.print_exc()
        return False
