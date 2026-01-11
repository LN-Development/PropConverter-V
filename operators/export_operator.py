import bpy


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
            
            try:
                # Export YTYP first
                result = bpy.ops.sollumz.export_ytyp_io(directory=self.directory)
                if result != {"FINISHED"}:
                    self.report({"WARNING"}, "YTYP export returned non-finished status")
                
                # Export Drawable (YDR)
                result = bpy.ops.sollumz.export_assets(directory=self.directory, direct_export=True)
                if result != {"FINISHED"}:
                    self.report({"WARNING"}, "Drawable export returned non-finished status")
                    
            finally:
                # Restore original settings
                export_settings.target_formats = original_formats
                export_settings.target_versions = original_versions
                
        except Exception as e:
            print(f"[ERROR] Export failed: {e}")
            self.report({"ERROR"}, f"Export failed: {str(e)}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Exported YTYP and Drawable to {self.directory}")
        return {"FINISHED"}
