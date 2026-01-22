import bpy
from .. import i18n
from .. import logger
from ..resolve_sollumz_mod_name import get_sollumz_preferences


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
        col = row.column(align=True, heading=i18n.t("operators.export.format_heading"))
        sub = col.row(align=True)
        sub.prop(self, "export_format_native", text=i18n.t("operators.export.format_native"), toggle=True)
        sub = col.row(align=True)
        sub.prop(self, "export_format_xml", text=i18n.t("operators.export.format_xml"), toggle=True)

        # Version column
        col = row.column(align=True, heading=i18n.t("operators.export.version_heading"))
        sub = col.row(align=True)
        sub.prop(self, "target_version_gen8", text=i18n.t("operators.export.version_gen8"), toggle=True)
        sub = col.row(align=True)
        sub.prop(self, "target_version_gen9", text=i18n.t("operators.export.version_gen9"), toggle=True)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if not self.directory:
            logger.log_error("messages.error.no_directory", operator=self)
            return {"CANCELLED"}

        # Check if there's a YTYP to export
        if len(context.scene.ytyps) == 0:
            logger.log_error("messages.error.no_ytyp", operator=self)
            return {"CANCELLED"}

        # Check if there's a selected YTYP
        if context.scene.ytyp_index < 0 or context.scene.ytyp_index >= len(context.scene.ytyps):
            logger.log_error("messages.error.no_ytyp_selected", operator=self)
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
            logger.log_error("messages.error.no_format", operator=self)
            return {"CANCELLED"}
        if not versions_selected:
            logger.log_error("messages.error.no_version", operator=self)
            return {"CANCELLED"}

        # Get Sollumz preferences and temporarily set export options
        try:
            # Find Sollumz addon preferences using our helper function
            sollumz_prefs = get_sollumz_preferences(context)
            
            if sollumz_prefs is None:
                logger.log_error("messages.error.sollumz_addon_not_found", operator=self)
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
                    logger.log_warning("messages.warning.ytyp_export_warning", operator=self)
                
                # Export Drawable (YDR)
                result = bpy.ops.sollumz.export_assets(directory=self.directory, direct_export=True)
                if result != {"FINISHED"}:
                    logger.log_warning("messages.warning.drawable_export_warning", operator=self)
                    
            finally:
                # Restore original settings
                export_settings.target_formats = original_formats
                export_settings.target_versions = original_versions
                
        except Exception as e:
            logger.log_error("messages.error.export_failed", operator=self, error=str(e))
            return {"CANCELLED"}

        logger.log_info("messages.info.export_success", operator=self, directory=self.directory)
        return {"FINISHED"}
