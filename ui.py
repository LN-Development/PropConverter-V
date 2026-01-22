import bpy
from . import i18n



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
        
        # Language selector at the top
        props = getattr(context.scene, "prop_converter", None)
        if props:
            layout.prop(props, "language", text=i18n.t("ui.language_setting"))
            layout.separator()
        
        layout.operator("propconverter.convert_to_gtav", text=i18n.t("ui.convert_button"))

        # Vertex color selector (runs automatically during convert)
        if props:
            layout.prop(props, "vertex_color", text=i18n.t("ui.vertex_color"))
            # Optional auto texture naming from mesh name
            layout.prop(props, "auto_texture_from_mesh_name", text=i18n.t("ui.auto_texture_from_mesh_name"))
        
        # Mirror Sollumz shader picker using its collection/list so users see the full shader list
        if hasattr(wm, "sz_shader_materials") and hasattr(wm, "sz_shader_material_index"):
            layout.separator()
            layout.label(text=i18n.t("ui.shader_material"))
            layout.template_list(
                "SOLLUMZ_UL_SHADER_MATERIALS_LIST",
                "propconverter_shader_list",
                wm,
                "sz_shader_materials",
                wm,
                "sz_shader_material_index",
            )
        else:
            layout.separator()
            layout.label(text=i18n.t("ui.install_sollumz"), icon="INFO")

        # Collision mesh settings
        if props:
            # Decimate settings
            layout.separator()
            layout.label(text=i18n.t("ui.collision_mesh_settings"))
            box = layout.box()
            box.prop(props, "enable_decimate", text=i18n.t("ui.enable_decimate"))
            if props.enable_decimate:
                box.prop(props, "decimate_type", text=i18n.t("ui.decimate_type"))
                
                if props.decimate_type == 'COLLAPSE':
                    box.prop(props, "decimate_ratio", text=i18n.t("ui.decimate_ratio"))
                elif props.decimate_type == 'UNSUBDIV':
                    box.prop(props, "decimate_iterations", text=i18n.t("ui.decimate_iterations"))
                    box.prop(props, "decimate_use_dissolve", text=i18n.t("ui.decimate_use_dissolve"))
                elif props.decimate_type == 'PLANAR':
                    box.prop(props, "decimate_planar_angle", text=i18n.t("ui.decimate_angle"))
            
            # Remesh settings
            layout.separator()
            box = layout.box()
            box.prop(props, "enable_remesh", text=i18n.t("ui.enable_remesh"))
            if props.enable_remesh:
                box.prop(props, "remesh_mode", text=i18n.t("ui.remesh_mode"))
                box.prop(props, "remesh_use_smooth_shade", text=i18n.t("ui.remesh_smooth_shading"))
                
                if props.remesh_mode in ['blocks', 'smooth', 'sharp']:
                    box.prop(props, "remesh_threshold", text=i18n.t("ui.remesh_threshold"))
                
                if props.remesh_mode == 'voxels':
                    box.prop(props, "remesh_voxel_size", text=i18n.t("ui.remesh_voxel_size"))
                    box.prop(props, "remesh_adaptivity", text=i18n.t("ui.remesh_adaptivity"))

        # Collision material selector for the collision mesh
        if hasattr(wm, "sz_collision_materials") and hasattr(wm, "sz_collision_material_index"):
            layout.separator()
            layout.label(text=i18n.t("ui.collision_material"))
            layout.template_list(
                "SOLLUMZ_UL_COLLISION_MATERIALS_LIST",
                "propconverter_collision_list",
                wm,
                "sz_collision_materials",
                wm,
                "sz_collision_material_index",
            )
        
        # Collision Flags section
        if props:
            layout.separator()
            # Checkbox to use default collision flags
            layout.prop(props, "use_default_flags", text=i18n.t("ui.use_default_flags"))
            
            # Only show customize option when default flags are NOT active
            if not props.use_default_flags:
                # Checkbox to toggle collision flags customization
                layout.prop(props, "customize_collision_flags", text=i18n.t("ui.customize_collision_flags"))
                
                # Only show flags if customize_collision_flags is enabled
                if props.customize_collision_flags:
                    box = layout.box()
                    # Make the text smaller for a more compact display
                    box.scale_y = 0.8
                    grid = box.grid_flow(columns=4, even_columns=True, even_rows=True)
                    
                    # Display all 16 collision flags in a 4-column grid
                    grid.prop(props.collision_flags, "stairs")
                    grid.prop(props.collision_flags, "not_climbable")
                    grid.prop(props.collision_flags, "see_through")
                    grid.prop(props.collision_flags, "shoot_through")
                    
                    grid.prop(props.collision_flags, "not_cover")
                    grid.prop(props.collision_flags, "walkable_path")
                    grid.prop(props.collision_flags, "no_cam_collision")
                    grid.prop(props.collision_flags, "shoot_through_fx")
                    
                    grid.prop(props.collision_flags, "no_decal")
                    grid.prop(props.collision_flags, "no_navmesh")
                    grid.prop(props.collision_flags, "no_ragdoll")
                    grid.prop(props.collision_flags, "vehicle_wheel")
                    
                    grid.prop(props.collision_flags, "no_ptfx")
                    grid.prop(props.collision_flags, "too_steep_for_player")
                    grid.prop(props.collision_flags, "no_network_spawn")
                    grid.prop(props.collision_flags, "no_cam_collision_allow_clipping")
        
        # YTYP
        layout.separator()
        layout.label(text=i18n.t("ui.ytyp_section"))
        
        # YTYP List 
        box = layout.box()
        if len(context.scene.ytyps) > 0:
            for i, ytyp in enumerate(context.scene.ytyps):
                box.label(text=ytyp.name)
        else:
            box.label(text=i18n.t("ui.no_ytyps"), icon="INFO")
        
        # Archetypes List (only show if a YTYP is selected)
        if context.scene.ytyp_index >= 0 and context.scene.ytyp_index < len(context.scene.ytyps):
            selected_ytyp = context.scene.ytyps[context.scene.ytyp_index]
            
            layout.separator()
            layout.label(text=i18n.t("ui.archetype_section"))
            
            # List archetype names
            box = layout.box()
            for arch in selected_ytyp.archetypes:
                box.label(text=arch.name)
        
      
        layout.separator()
        layout.separator()
        layout.operator("propconverter.export_prop", text=i18n.t("ui.export_button"), icon="EXPORT")





classes = [
    PROPCONVERTER_PT_main_panel,
]


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass  # Already registered


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
