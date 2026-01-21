import bpy
from ..prop_converter import convertToGtaV
from .. import i18n


class PROPCONVERTER_OT_convert_to_gtav(bpy.types.Operator):
    """Convert selected object to GTA V"""
    bl_idname = "propconverter.convert_to_gtav"
    bl_label = "Convert to GTA V"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        # Check if in Object Mode
        if context.mode != 'OBJECT':
            self.report({"ERROR"}, i18n.t("messages.error.switch_to_object_mode"))
            return {"FINISHED"}
        
        if context.active_object is None:
            self.report({"ERROR"}, i18n.t("messages.error.select_object"))
            return {"FINISHED"}
        
        obj = context.active_object
        
        if obj.type != "MESH":
            self.report({"ERROR"}, i18n.t("messages.error.not_a_mesh"))
            return {"FINISHED"}
        
        if not obj.select_get():
            self.report({"ERROR"}, i18n.t("messages.error.select_mesh"))
            return {"FINISHED"}
        
        if convertToGtaV(context):
            self.report({"INFO"}, i18n.t("messages.info.conversion_success"))
        else:
            self.report({"ERROR"}, i18n.t("messages.error.conversion_failed"))
        
        return {"FINISHED"}

