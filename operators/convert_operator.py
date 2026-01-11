import bpy
from ..prop_converter import convertToGtaV


class PROPCONVERTER_OT_convert_to_gtav(bpy.types.Operator):
    """Convert selected object to GTA V"""
    bl_idname = "propconverter.convert_to_gtav"
    bl_label = "Convert to GTA V"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        # Check if in Object Mode
        if context.mode != 'OBJECT':
            self.report({"ERROR"}, "Please switch to Object Mode!")
            return {"FINISHED"}
        
        if context.active_object is None:
            self.report({"ERROR"}, "Please select an object!")
            return {"FINISHED"}
        
        obj = context.active_object
        
        if obj.type != "MESH":
            self.report({"ERROR"}, f"Selected object is not a mesh!")
            return {"FINISHED"}
        
        if not obj.select_get():
            self.report({"ERROR"}, "Please select a mesh to continue!")
            return {"FINISHED"}
        
        if convertToGtaV(context):
            self.report({"INFO"}, "Prop converted successfully!")
        else:
            self.report({"ERROR"}, "Failed to convert prop")
        
        return {"FINISHED"}
