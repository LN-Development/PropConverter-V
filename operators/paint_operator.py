import bpy
from ..core.mesh_prep.paint_vertex_colors import paint_vertex_colors


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

        ok = paint_vertex_colors(original, collision, color=color)
        if ok:
            self.report({"INFO"}, "Painted original and cleared collision vertex colors")
            return {"FINISHED"}

        self.report({"ERROR"}, "Failed to paint vertex colors")
        return {"CANCELLED"}
