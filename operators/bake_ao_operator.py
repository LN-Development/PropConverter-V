import bpy
from ..core.post_processing import bake_ambient_occlusion


class PROPCONVERTER_OT_bake_ambient_occlusion(bpy.types.Operator):
    """Bake ambient occlusion directly on the converted drawable"""
    bl_idname = "propconverter.bake_ambient_occlusion"
    bl_label = "Bake Ambient Occlusion"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """Check if operator can run."""
        return (context.active_object is not None and 
                context.active_object.type == 'MESH')
    
    def execute(self, context):
        """Execute ambient occlusion baking directly on the drawable."""
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}
        
        self.report({'INFO'}, f"Starting ambient occlusion bake on {obj.name}...")
        
        # Call the bake function directly
        success = bake_ambient_occlusion(context, obj)
        
        if success:
            self.report({'INFO'}, f"Ambient occlusion baked successfully")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to bake ambient occlusion")
            return {'CANCELLED'}
