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

    # Format options
    export_format_native: bpy.props.BoolProperty(
        name="Native",
        description="Export in native binary format",
        default=True,
    )
    export_format_xml: bpy.props.BoolProperty(
        name="CodeWalker XML",
        description="Export as CodeWalker XML",
        default=True,
    )

    # Version options
    target_version_gen8: bpy.props.BoolProperty(
        name="Gen 8",
        description="GTAV Legacy",
        default=True,
    )
    target_version_gen9: bpy.props.BoolProperty(
        name="Gen 9",
        description="GTAV Enhanced",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=False)
        
        # Format column
        col = row.column(align=True, heading="Format")
        sub = col.row(align=True)
        sub.prop(self, "export_format_native", text="Native", toggle=True)
        sub = col.row(align=True)
        sub.prop(self, "export_format_xml", text="CodeWalker XML", toggle=True)

        # Version column
        col = row.column(align=True, heading="Version")
        sub = col.row(align=True)
        sub.prop(self, "target_version_gen8", text="Gen 8", toggle=True)
        sub = col.row(align=True)
        sub.prop(self, "target_version_gen9", text="Gen 9", toggle=True)

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

        # Collect format/version selections
        formats_selected = set()
        if self.export_format_native:
            formats_selected.add('NATIVE')
        if self.export_format_xml:
            formats_selected.add('CWXML')

        versions_selected = set()
        if self.target_version_gen8:
            versions_selected.add('GEN8')
        if self.target_version_gen9:
            versions_selected.add('GEN9')

        if not formats_selected:
            self.report({"ERROR"}, "Please select at least one export format!")
            return {"CANCELLED"}
        if not versions_selected:
            self.report({"ERROR"}, "Please select at least one target version!")
            return {"CANCELLED"}

        # Get Sollumz preferences and temporarily set export options
        try:
            # Find Sollumz addon preferences
            sollumz_prefs = None
            for addon in context.preferences.addons:
                if 'sollumz' in addon.module.lower():
                    sollumz_prefs = addon.preferences
                    break
            
            if sollumz_prefs is None:
                self.report({"ERROR"}, "Sollumz addon not found. Please ensure it's installed and enabled.")
                return {"CANCELLED"}
            
            # Store original settings to restore later
            export_settings = sollumz_prefs.export_settings
            original_formats = set(export_settings.target_formats)
            original_versions = set(export_settings.target_versions)
            
            # Apply our custom settings temporarily
            export_settings.target_formats = formats_selected
            export_settings.target_versions = versions_selected
            
            print(f"Set export settings - Formats: {export_settings.target_formats}, Versions: {export_settings.target_versions}")
            
            try:
                # Export YTYP first
                print("Exporting YTYP...")
                result = bpy.ops.sollumz.export_ytyp_io(directory=self.directory)
                if result == {"FINISHED"}:
                    print("YTYP exported successfully")
                else:
                    self.report({"WARNING"}, "YTYP export returned non-finished status")
                
                # Export Drawable (YDR)
                print("Exporting Drawable...")
                result = bpy.ops.sollumz.export_assets(directory=self.directory, direct_export=True)
                if result == {"FINISHED"}:
                    print("Drawable exported successfully")
                else:
                    self.report({"WARNING"}, "Drawable export returned non-finished status")
                    
            finally:
                # Restore original settings
                export_settings.target_formats = original_formats
                export_settings.target_versions = original_versions
                print("Restored original export settings")
                
        except Exception as e:
            print(f"ERROR during export: {e}")
            import traceback
            traceback.print_exc()
            self.report({"ERROR"}, f"Export failed: {str(e)}")
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
