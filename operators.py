import bpy
from . import prop_converter


class PROPCONVERTER_OT_convert_to_gtav(bpy.types.Operator):
    """Convert selected object to GTA V"""
    bl_idname = "propconverter.convert_to_gtav"
    bl_label = "Convert to GTA V"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
       
        print("=" * 50)
        print("Conversion Started")
        
        # Check if in Object Mode
        if context.mode != 'OBJECT':
            print(f"ERROR: Not in Object Mode (current mode: {context.mode})")
            self.report({"ERROR"}, "Please switch to Object Mode!")
            print("=" * 50)
            return {"FINISHED"}
        
        if context.active_object is None:
            print("ERROR: No object selected")
            self.report({"ERROR"}, "Please select an object!")
            print("=" * 50)
            return {"FINISHED"}
        
        obj = context.active_object
        print(f"Active object: {obj.name}")
        print(f"Object type: {obj.type}")
        print(f"Object selected (select_get): {obj.select_get()}")
        
        if obj.type != "MESH":
            print(f"ERROR: Selected object is not a mesh (type: {obj.type})")
            self.report({"ERROR"}, f"Selected object is not a mesh!")
            print("=" * 50)
            return {"FINISHED"}
        
        # Check if object is selected
        if not obj.select_get():
            print("ERROR: Object not selected")
            self.report({"ERROR"}, "Please select a mesh to continue!")
            print("=" * 50)
            return {"FINISHED"}
        
        print("SUCCESS: Object is valid, proceeding with conversion...")
        
        if prop_converter.convertToGtaV(context):
            print("Prop converted successfully!")
            self.report({"INFO"}, "Prop converted successfully!")
        else:
            print("ERROR: Conversion failed")
            self.report({"ERROR"}, "Failed to convert prop")
        
        print("=" * 50)
        return {"FINISHED"}


class PROPCONVERTER_OT_paint_vertex_colors(bpy.types.Operator):
    """Paint vertex colors on the original mesh and remove them from the collision mesh"""
    bl_idname = "propconverter.paint_vertex_colors"
    bl_label = "Paint Vertex Colors"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene_props = getattr(context.scene, "prop_converter", None)
        original = getattr(scene_props, "original_mesh", None) if scene_props else None
        collision = getattr(scene_props, "collision_mesh", None) if scene_props else None
        color = tuple(getattr(scene_props, "vertex_color", (1.0, 1.0, 1.0, 1.0))) if scene_props else (1.0, 1.0, 1.0, 1.0)

        if not original:
            self.report({"ERROR"}, "No original mesh stored. Convert first.")
            return {"CANCELLED"}

        ok = prop_converter.paint_vertex_colors(original, collision, color=color)
        if ok:
            self.report({"INFO"}, "Painted original and cleared collision vertex colors")
            return {"FINISHED"}

        self.report({"ERROR"}, "Failed to paint vertex colors")
        return {"CANCELLED"}


class PROPCONVERTER_OT_export_prop(bpy.types.Operator):
    """Export the created YTYP and YDR to selected directory"""
    bl_idname = "propconverter.export_prop"
    bl_label = "Export YTYP and YDR"
    bl_options = {"REGISTER"}

    directory: bpy.props.StringProperty(
        name="Output directory",
        description="Select export output directory",
        subtype="DIR_PATH",
        options={"HIDDEN"}
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if not self.directory:
            self.report({"ERROR"}, "No directory selected!")
            return {"CANCELLED"}

        # Check if there's a YTYP to export
        if len(context.scene.ytyps) == 0:
            self.report({"ERROR"}, "No YTYP found! Please convert a prop first.")
            return {"CANCELLED"}

        # Check if there's a selected YTYP
        if context.scene.ytyp_index < 0 or context.scene.ytyp_index >= len(context.scene.ytyps):
            self.report({"ERROR"}, "No YTYP selected!")
            return {"CANCELLED"}

        print("=" * 50)
        print(f"Exporting to directory: {self.directory}")

        # Export YTYP first
        try:
            print("Exporting YTYP...")
            result = bpy.ops.sollumz.export_ytyp_io(directory=self.directory)
            if result == {"FINISHED"}:
                print("YTYP exported successfully")
            else:
                self.report({"WARNING"}, "YTYP export returned non-finished status")
        except Exception as e:
            print(f"ERROR exporting YTYP: {e}")
            self.report({"ERROR"}, f"Failed to export YTYP: {e}")
            return {"CANCELLED"}

        # Export Drawable (YDR)
        try:
            print("Exporting Drawable...")
            # The export_assets operator exports all selected Sollumz objects
            result = bpy.ops.sollumz.export_assets(directory=self.directory, direct_export=True)
            if result == {"FINISHED"}:
                print("Drawable exported successfully")
            else:
                self.report({"WARNING"}, "Drawable export returned non-finished status")
        except Exception as e:
            print(f"ERROR exporting Drawable: {e}")
            self.report({"ERROR"}, f"Failed to export Drawable: {e}")
            return {"CANCELLED"}

        print("=" * 50)
        self.report({"INFO"}, f"Exported YTYP and Drawable to {self.directory}")
        return {"FINISHED"}


classes = [
    PROPCONVERTER_OT_convert_to_gtav,
    PROPCONVERTER_OT_paint_vertex_colors,
    PROPCONVERTER_OT_export_prop,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
