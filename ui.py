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
            
            # Decimate settings
            layout.separator()
            layout.label(text="Collision Mesh Settings")
            box = layout.box()
            box.prop(props, "enable_decimate", text="Enable Decimate")
            if props.enable_decimate:
                box.prop(props, "decimate_type", text="Type")
                
                if props.decimate_type == 'COLLAPSE':
                    box.prop(props, "decimate_ratio", text="Ratio")
                elif props.decimate_type == 'UNSUBDIV':
                    box.prop(props, "decimate_iterations", text="Iterations")
                    box.prop(props, "decimate_use_dissolve", text="Use Dissolve")
                elif props.decimate_type == 'PLANAR':
                    box.prop(props, "decimate_planar_angle", text="Angle")
            
            # Remesh settings
            layout.separator()
            box = layout.box()
            box.prop(props, "enable_remesh", text="Enable Remesh")
            if props.enable_remesh:
                box.prop(props, "remesh_mode", text="Mode")
                box.prop(props, "remesh_use_smooth_shade", text="Smooth Shading")
                
                if props.remesh_mode in ['blocks', 'smooth', 'sharp']:
                    box.prop(props, "remesh_threshold", text="Threshold")
                
                if props.remesh_mode == 'voxels':
                    box.prop(props, "remesh_voxel_size", text="Voxel Size")
                    box.prop(props, "remesh_adaptivity", text="Adaptivity")

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
        
        # YTYP List 
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
