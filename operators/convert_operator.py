import bpy
from ..prop_converter import convertToGtaV
from .. import i18n
from .. import logger


class PROPCONVERTER_OT_convert_to_gtav(bpy.types.Operator):
    """Convert selected object to GTA V"""
    bl_idname = "propconverter.convert_to_gtav"
    bl_label = "Convert to GTA V"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        # Check if in Object Mode
        if context.mode != 'OBJECT':
            logger.log_error("messages.error.switch_to_object_mode", operator=self)
            return {"FINISHED"}
        
        if context.active_object is None:
            logger.log_error("messages.error.select_object", operator=self)
            return {"FINISHED"}
        
        obj = context.active_object
        
        if obj.type != "MESH":
            logger.log_error("messages.error.not_a_mesh", operator=self)
            return {"FINISHED"}
        
        if not obj.select_get():
            logger.log_error("messages.error.select_mesh", operator=self)
            return {"FINISHED"}
        
        if convertToGtaV(context, operator=self):
            logger.log_info("messages.info.conversion_success", operator=self)
        else:
            logger.log_error("messages.error.conversion_failed", operator=self)
        
        return {"FINISHED"}

