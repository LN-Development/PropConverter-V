import bpy
import importlib


def create_archetype(context, obj, mod_name: str, original_name: str):
    try:
        print(f"Creating archetype from drawable: {obj.name}")
        sollumz_props = importlib.import_module(f"{mod_name}.sollumz_properties")
        ArchetypeType = sollumz_props.ArchetypeType
        SollumType = sollumz_props.SollumType

        drawable_parent = obj.parent if obj.parent and obj.parent.sollum_type == SollumType.DRAWABLE else None
        if drawable_parent is None:
            print(f"WARNING: Could not find parent Drawable for {obj.name}")
            if obj.sollum_type == SollumType.DRAWABLE:
                drawable_parent = obj
            else:
                print(f"ERROR: {obj.name} is not inside a Drawable structure")
                raise Exception("Could not find Drawable object for archetype creation")

        print(f"Found drawable parent: {drawable_parent.name} (type: {drawable_parent.sollum_type})")
        context.scene.create_archetype_type = ArchetypeType.BASE
        bpy.ops.object.select_all(action='DESELECT')
        drawable_parent.select_set(True)
        context.view_layer.objects.active = drawable_parent
        print(f"Drawable is selected: {drawable_parent.select_get()}")
        print(f"Active object: {context.view_layer.objects.active.name if context.view_layer.objects.active else 'None'}")
        print(f"Selected objects: {[o.name for o in context.selected_objects]}")
        print(f"YTYP index: {context.scene.ytyp_index}")

        context.view_layer.update()
        result = bpy.ops.sollumz.createarchetypefromselected()
        print(f"Operator result: {result}")

        selected_ytyp = context.scene.ytyps[context.scene.ytyp_index]
        print(f"Number of archetypes in YTYP: {len(selected_ytyp.archetypes)}")
        if len(selected_ytyp.archetypes) > 0:
            archetype = selected_ytyp.archetypes[-1]
            archetype.texture_dictionary = original_name
            print(f"Successfully created archetype: {archetype.name} with texture_dictionary: {original_name}")
        else:
            print("WARNING: No archetypes found after calling createarchetypefromselected")
        return True
    except Exception as e:
        print(f"WARNING: Failed to create archetype - {e}")
        import traceback
        traceback.print_exc()
        return False
