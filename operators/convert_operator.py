import bpy
from ..prop_converter import convertToGtaV


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
        
        if convertToGtaV(context):
            print("Prop converted successfully!")
            self.report({"INFO"}, "Prop converted successfully!")
        else:
            print("ERROR: Conversion failed")
            self.report({"ERROR"}, "Failed to convert prop")
        
        print("=" * 50)
        return {"FINISHED"}
