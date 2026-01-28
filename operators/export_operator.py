import bpy
from .. import i18n
from .. import logger
from ..sollumz_integration import SollumzIntegration

# Get the root addon package name (handles both normal addons and Blender 5.0 extensions)
ADDON_PACKAGE = __package__.split('.')[0] if '.' in __package__ else __package__
if __package__.startswith('bl_ext.'):
    # For Blender 5.0 extensions: bl_ext.user_default.propconverterv.operators -> bl_ext.user_default.propconverterv
    parts = __package__.split('.')
    ADDON_PACKAGE = '.'.join(parts[:3]) if len(parts) > 3 else __package__


class PROPCONVERTER_OT_export_prop(bpy.types.Operator):
    """Export the created YTYP and YDR to selected directory"""
    bl_idname = "propconverter.export_prop"
    bl_label = "Export YTYP and YDR"

    directory: bpy.props.StringProperty(
        name="Output directory",
        description="Select export output directory",
        subtype="DIR_PATH",
        options={"HIDDEN"}
    )
    
    @staticmethod
    def _save_to_preferences(prop_name):
        """Callback factory to save property changes to addon preferences"""
        def update_func(self, context):
            try:
                prefs = context.preferences.addons[ADDON_PACKAGE].preferences
                setattr(prefs, prop_name, getattr(self, prop_name))
                # Save preferences to disk
                bpy.ops.wm.save_userpref()
            except:
                pass  # Ignore errors during preference save
        return update_func
    
    # Mesh Domain options (exclusive selection)
    export_mesh_domain: bpy.props.EnumProperty(
        name="Mesh Domain",
        description="Select which mesh domain to export",
        items=[
            ('FACE_CORNER', "Face Corner", "Export Face Corner domain attributes (UVs, vertex colors)"),
            ('VERTEX', "Vertex", "Export Vertex domain attributes"),
        ],
        default='FACE_CORNER',
        update=lambda self, context: PROPCONVERTER_OT_export_prop._save_to_preferences('export_mesh_domain')(self, context),
    )

    # Format options
    export_format_native: bpy.props.BoolProperty(
        name="Native",
        description="Export in native binary format",
        default=True,
        update=lambda self, context: PROPCONVERTER_OT_export_prop._save_to_preferences('export_format_native')(self, context),
    )
    export_format_xml: bpy.props.BoolProperty(
        name="CodeWalker XML",
        description="Export as CodeWalker XML",
        default=True,
        update=lambda self, context: PROPCONVERTER_OT_export_prop._save_to_preferences('export_format_xml')(self, context),
    )

    # Version options
    target_version_gen8: bpy.props.BoolProperty(
        name="Gen 8",
        description="GTAV Legacy",
        default=True,
        update=lambda self, context: PROPCONVERTER_OT_export_prop._save_to_preferences('target_version_gen8')(self, context),
    )
    target_version_gen9: bpy.props.BoolProperty(
        name="Gen 9",
        description="GTAV Enhanced",
        default=True,
        update=lambda self, context: PROPCONVERTER_OT_export_prop._save_to_preferences('target_version_gen9')(self, context),
    )

    def draw(self, context):
        layout = self.layout
        
        # First row: Format and Version columns side by side
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
        
        # Second row: Mesh Domains below
        layout.separator()
        
        # Mesh Domains as radio buttons (exclusive selection)
        layout.label(text=i18n.t("operators.export.mesh_domains_heading"))
        layout.prop(self, "export_mesh_domain", expand=True)

    def invoke(self, context, event):
        # Load settings from addon preferences
        prefs = context.preferences.addons[ADDON_PACKAGE].preferences
        
        self.export_mesh_domain = prefs.export_mesh_domain
        self.export_format_native = prefs.export_format_native
        self.export_format_xml = prefs.export_format_xml
        self.target_version_gen8 = prefs.target_version_gen8
        self.target_version_gen9 = prefs.target_version_gen9
        
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

        # Collect format/version selections from operator properties
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
            # Find Sollumz addon preferences using the integration service
            sollumz = SollumzIntegration.get_instance()
            sollumz_prefs = sollumz.get_preferences(context)
            
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
