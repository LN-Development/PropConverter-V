"""
UI module - Define panels and UI elements for the addon
"""

import bpy


class PROPCONVERTER_PT_main_panel(bpy.types.Panel):

    bl_label = "PropConverter-V"
    bl_idname = "PROPCONVERTER_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PropConverter-V"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1
    
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        layout.operator("propconverter.convert_to_gtav", text="Convert to GTA V")

        # Vertex color selector (runs automatically during convert)
        props = getattr(context.scene, "prop_converter", None)
        if props:
            layout.prop(props, "vertex_color", text="Vertex Color")

        # Mirror Sollumz shader picker using its collection/list so users see the full shader list
        if hasattr(wm, "sz_shader_materials") and hasattr(wm, "sz_shader_material_index"):
            layout.label(text="Shader Material")
            layout.template_list(
                "SOLLUMZ_UL_SHADER_MATERIALS_LIST",
                "propconverter_shader_list",
                wm,
                "sz_shader_materials",
                wm,
                "sz_shader_material_index",
            )
        else:
            layout.label(text="Install & enable Sollumz to pick shaders", icon="INFO")

        # Collision material selector for the collision mesh
        if hasattr(wm, "sz_collision_materials") and hasattr(wm, "sz_collision_material_index"):
            layout.separator()
            layout.label(text="Collision Material")
            layout.template_list(
                "SOLLUMZ_UL_COLLISION_MATERIALS_LIST",
                "propconverter_collision_list",
                wm,
                "sz_collision_materials",
                wm,
                "sz_collision_material_index",
            )
        
        # YTYP
        layout.separator()
        layout.label(text="YTYP")
        
        # YTYP List (simple display)
        box = layout.box()
        if len(context.scene.ytyps) > 0:
            for i, ytyp in enumerate(context.scene.ytyps):
                box.label(text=ytyp.name)
        else:
            box.label(text="No YTYPs", icon="INFO")
        
        # Archetypes List (only show if a YTYP is selected)
        if context.scene.ytyp_index >= 0 and context.scene.ytyp_index < len(context.scene.ytyps):
            selected_ytyp = context.scene.ytyps[context.scene.ytyp_index]
            
            layout.separator()
            layout.label(text="Archetype")
            
            # List archetype names
            box = layout.box()
            for arch in selected_ytyp.archetypes:
                box.label(text=arch.name)
        
      
        layout.separator()
        layout.separator()
        layout.operator("propconverter.export_prop", text="Export YTYP and YDR", icon="EXPORT")



classes = [
    PROPCONVERTER_PT_main_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
