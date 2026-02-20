import bpy
from mathutils import Vector
from ..sollumz_integration import SollumzIntegration


class PROPCONVERTER_OT_gather_model_info(bpy.types.Operator):
    """Gather exhaustive hierarchical information about the active model and Sollumz metadata"""
    bl_idname = "propconverter.gather_model_info"
    bl_label = "Gather Model Info"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def format_flags(self, flags_obj):
        """Format a Sollumz flag struct into a comma-separated list of active flags."""
        if not flags_obj:
            return "None"
        active = []
        for attr in dir(flags_obj):
            if attr.startswith("_") or attr.startswith("bl_") or attr in ["rna_type", "name", "total"]:
                continue
            try:
                val = getattr(flags_obj, attr)
                if isinstance(val, bool) and val is True:
                    active.append(attr)
            except:
                continue
        return ", ".join(active) if active else "None"

    def get_hierarchy_bounds(self, obj):
        """Recursively calculate bounding box points of an object and all children in world space."""
        points = []
        if obj.type == 'MESH':
            mw = obj.matrix_world
            points.extend([mw @ Vector(v) for v in obj.bound_box])
        for child in obj.children:
            points.extend(self.get_hierarchy_bounds(child))
        return points

    def gather_drawable_info(self, obj, indent):
        """Gather properties specific to sollumz_drawable (Armature root)."""
        info = []
        # DrawableProperties are on obj.drawable_properties
        if hasattr(obj, "drawable_properties"):
            dp = obj.drawable_properties
            lods = []
            for attr, label in [("lod_dist_high", "High"), ("lod_dist_med", "Med"),
                                ("lod_dist_low", "Low"), ("lod_dist_vlow", "VLow")]:
                val = getattr(dp, attr, 9998)
                lods.append(f"{label}: {val:.1f}")
            info.append(f"{indent}[Drawable] LOD Dists: {', '.join(lods)}")
        return info

    def gather_drawable_model_info(self, obj, indent):
        """Gather properties specific to sollumz_drawable_model."""
        info = []
        # DrawableModelProperties on obj.drawable_model_properties or mesh
        dmp = None
        if hasattr(obj, "drawable_model_properties"):
            dmp = obj.drawable_model_properties
        elif obj.type == 'MESH' and hasattr(obj.data, "drawable_model_properties"):
            dmp = obj.data.drawable_model_properties

        if dmp:
            info.append(f"{indent}[DrawableModel] Render Mask: {dmp.render_mask} | LOD Level: {dmp.sollum_lod}")

        # Skinned model properties (on parent drawable)
        if hasattr(obj, "skinned_model_properties"):
            smp = obj.skinned_model_properties
            skinned_lods = []
            for level_name, level_prop in [("VHigh", "very_high"), ("High", "high"),
                                            ("Med", "medium"), ("Low", "low"), ("VLow", "very_low")]:
                lod = getattr(smp, level_prop, None)
                if lod:
                    skinned_lods.append(f"{level_name}(mask={lod.render_mask})")
            if skinned_lods:
                info.append(f"{indent}[SkinnedModel] {', '.join(skinned_lods)}")
        return info

    def gather_bound_composite_info(self, obj, indent):
        """Gather properties specific to sollumz_bound_composite."""
        info = []
        info.append(f"{indent}[BoundComposite]")
        for cp, label in [("composite_flags1", "Flags1"), ("composite_flags2", "Flags2")]:
            if hasattr(obj, cp):
                f_str = self.format_flags(getattr(obj, cp))
                info.append(f"{indent}  {label}: {f_str}")
        return info

    def gather_bound_shape_info(self, obj, indent, bound_type):
        """Gather properties specific to bound shapes (Box, Sphere, Capsule, Cylinder, Geometry, GeometryBVH)."""
        info = []
        info.append(f"{indent}[{bound_type}]")

        # Margin
        if hasattr(obj, "margin"):
            info.append(f"{indent}  Margin: {obj.margin}")

        # Composite Flags (also on child bounds)
        for cp, label in [("composite_flags1", "Flags1"), ("composite_flags2", "Flags2")]:
            if hasattr(obj, cp):
                f_str = self.format_flags(getattr(obj, cp))
                if f_str != "None":
                    info.append(f"{indent}  {label}: {f_str}")

        # BoundShapeProps (sz_bound_shape)
        if hasattr(obj, "sz_bound_shape"):
            bsp = obj.sz_bound_shape
            if "box" in bound_type.lower():
                try:
                    ext = bsp.box_extents
                    info.append(f"{indent}  Box Extents: ({ext[0]:.3f}, {ext[1]:.3f}, {ext[2]:.3f})")
                except:
                    pass
            if "sphere" in bound_type.lower():
                try:
                    info.append(f"{indent}  Sphere Radius: {bsp.sphere_radius:.3f}")
                except:
                    pass
            if "capsule" in bound_type.lower():
                try:
                    info.append(f"{indent}  Capsule Radius: {bsp.capsule_radius:.3f} | Length: {bsp.capsule_length:.3f}")
                except:
                    pass
            if "cylinder" in bound_type.lower() or "disc" in bound_type.lower():
                try:
                    info.append(f"{indent}  Cylinder Radius: {bsp.cylinder_radius:.3f} | Length: {bsp.cylinder_length:.3f}")
                except:
                    pass

        # Collision Material Properties
        if obj.type == 'MESH' and obj.material_slots:
            for i, slot in enumerate(obj.material_slots):
                mat = slot.material
                if mat and hasattr(mat, "collision_properties"):
                    cp = mat.collision_properties
                    info.append(f"{indent}  Col Mat [{i}] {mat.name}: ProcID={cp.procedural_id} | RoomID={cp.room_id} | PedDensity={cp.ped_density} | ColorIdx={cp.material_color_index}")
                if mat and hasattr(mat, "collision_flags"):
                    f_str = self.format_flags(mat.collision_flags)
                    if f_str != "None":
                        info.append(f"{indent}    Mat Flags: {f_str}")
        return info

    def gather_shader_info(self, mat, indent):
        """Gather detailed shader properties for a material."""
        info = []
        if hasattr(mat, "shader_properties"):
            sp = mat.shader_properties
            info.append(f"{indent}    Shader: {sp.filename} (Name: {sp.name}) | Bucket: {sp.renderbucket}")

            # Texture Parameters
            if hasattr(sp, "texture_parameters"):
                for tex in sp.texture_parameters:
                    tex_name = tex.texture_name if hasattr(tex, "texture_name") else "None"
                    info.append(f"{indent}      Tex: {tex.name} -> {tex_name}")
            # Float Parameters
            if hasattr(sp, "float_parameters"):
                for f in sp.float_parameters:
                    info.append(f"{indent}      Float: {f.name} = {f.value:.3f}")
            # Vector Parameters
            if hasattr(sp, "vector_parameters"):
                for v in sp.vector_parameters:
                    v_vals = ", ".join([f"{x:.3f}" for x in v.value])
                    info.append(f"{indent}      Vector: {v.name} = ({v_vals})")
        return info

    def gather_obj_info(self, obj, level=0):
        indent = "    " * level
        info = []

        # --- Header ---
        sollum_type = getattr(obj, "sollum_type", "None")
        info.append(f"{indent}=== {obj.name} ({obj.type} | {sollum_type}) ===")

        # --- Spatial Information (World Space) ---
        mw = obj.matrix_world
        loc, rot, scale = mw.decompose()
        rot_e = rot.to_euler()
        dims = obj.dimensions
        info.append(f"{indent}World Pos: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f}) | Rot: ({rot_e.x:.1f}, {rot_e.y:.1f}, {rot_e.z:.1f})")
        info.append(f"{indent}Scale: ({scale.x:.3f}, {scale.y:.3f}, {scale.z:.3f}) | Size: ({dims.x:.3f}, {dims.y:.3f}, {dims.z:.3f})")

        # Mesh Bounds
        if obj.type == 'MESH':
            bbox_world = [mw @ Vector(v) for v in obj.bound_box]
            b_min = Vector((min(v.x for v in bbox_world), min(v.y for v in bbox_world), min(v.z for v in bbox_world)))
            b_max = Vector((max(v.x for v in bbox_world), max(v.y for v in bbox_world), max(v.z for v in bbox_world)))
            info.append(f"{indent}World Bounds: Min({b_min.x:.3f}, {b_min.y:.3f}, {b_min.z:.3f}) Max({b_max.x:.3f}, {b_max.y:.3f}, {b_max.z:.3f})")

        # Hierarchy Bounds
        if obj.children:
            h_points = self.get_hierarchy_bounds(obj)
            if h_points:
                h_min = Vector((min(v.x for v in h_points), min(v.y for v in h_points), min(v.z for v in h_points)))
                h_max = Vector((max(v.x for v in h_points), max(v.y for v in h_points), max(v.z for v in h_points)))
                info.append(f"{indent}Hierarchy Bounds: Min({h_min.x:.3f}, {h_min.y:.3f}, {h_min.z:.3f}) Max({h_max.x:.3f}, {h_max.y:.3f}, {h_max.z:.3f})")

        # --- TYPE-SPECIFIC SOLLUMZ DATA ---
        st = str(sollum_type).lower()

        # *** Drawable (Armature root) ***
        if st == "sollumz_drawable":
            info.extend(self.gather_drawable_info(obj, indent))

        # *** Drawable Model ***
        if st == "sollumz_drawable_model":
            info.extend(self.gather_drawable_model_info(obj, indent))

        # *** Bound Composite ***
        if st == "sollumz_bound_composite":
            info.extend(self.gather_bound_composite_info(obj, indent))

        # *** Bound shapes (Box, Sphere, Capsule, Cylinder, Geometry, GeometryBVH, Disc, Plane) ***
        bound_types = {
            "sollumz_bound_box": "BoundBox",
            "sollumz_bound_sphere": "BoundSphere",
            "sollumz_bound_capsule": "BoundCapsule",
            "sollumz_bound_cylinder": "BoundCylinder",
            "sollumz_bound_disc": "BoundDisc",
            "sollumz_bound_geometry": "BoundGeometry",
            "sollumz_bound_geometrybvh": "BoundGeometryBVH",
            "sollumz_bound_poly_box": "BoundPolyBox",
            "sollumz_bound_poly_sphere": "BoundPolySphere",
            "sollumz_bound_poly_capsule": "BoundPolyCapsule",
            "sollumz_bound_poly_cylinder": "BoundPolyCylinder",
        }
        if st in bound_types:
            info.extend(self.gather_bound_shape_info(obj, indent, bound_types[st]))

        # --- Bone Info for Armatures ---
        if obj.type == 'ARMATURE' and obj.data and obj.data.bones:
            info.append(f"{indent}Bones ({len(obj.data.bones)}):")
            for bone in obj.data.bones:
                head = mw @ bone.head_local
                tail = mw @ bone.tail_local
                bone_line = f"{indent}  - {bone.name} | Head: ({head.x:.3f}, {head.y:.3f}, {head.z:.3f}) | Tail: ({tail.x:.3f}, {tail.y:.3f}, {tail.z:.3f})"
                # Bone Properties (tag, flags)
                if hasattr(bone, "bone_properties"):
                    bp = bone.bone_properties
                    bone_line += f" | Tag: {bp.tag}"
                    flag_names = [f.name for f in bp.flags]
                    if flag_names:
                        bone_line += f" | BoneFlags: {', '.join(flag_names)}"
                info.append(bone_line)

        # --- Mesh Data ---
        if obj.type == 'MESH':
            mesh = obj.data
            tri_count = sum(len(p.vertices) - 2 for p in mesh.polygons)
            info.append(f"{indent}Geometry: {len(mesh.vertices)} Verts | {len(mesh.polygons)} Faces | ~{tri_count} Tris")

            if obj.vertex_groups:
                info.append(f"{indent}V-Groups: {', '.join([vg.name for vg in obj.vertex_groups[:10]])}{'...' if len(obj.vertex_groups) > 10 else ''}")

            # Materials (with shader details for drawable models)
            if obj.material_slots:
                info.append(f"{indent}Materials ({len(obj.material_slots)}):")
                for i, slot in enumerate(obj.material_slots):
                    mat = slot.material
                    if not mat:
                        info.append(f"{indent}  [{i}] Empty Slot")
                        continue
                    info.append(f"{indent}  [{i}] {mat.name}")
                    info.extend(self.gather_shader_info(mat, indent))

        # --- Recurse children ---
        if obj.children:
            for child in obj.children:
                info.append("")
                info.extend(self.gather_obj_info(child, level + 1))

        return info

    def execute(self, context):
        obj = context.active_object
        props = context.scene.prop_converter

        report_lines = self.gather_obj_info(obj)

        # YTYP Archetype mapping
        ytyp_info = []
        try:
            for ytyp in context.scene.ytyps:
                for arch in ytyp.archetypes:
                    if arch.asset_name == obj.name or arch.name == obj.name:
                        ytyp_info.append(f"\n--- YTYP Archetype ---")
                        ytyp_info.append(f"Asset: {arch.asset_name} | Name: {arch.name} | Type: {arch.type}")
                        ytyp_info.append(f"Physics: {getattr(arch, 'physics_dictionary', 'N/A')} | Clip: {getattr(arch, 'clip_dictionary', 'N/A')}")
                        ytyp_info.append(f"Texture Dict: {getattr(arch, 'texture_dictionary', 'N/A')}")
                        if hasattr(arch, "position") and hasattr(arch, "rotation"):
                            p = arch.position
                            r = arch.rotation
                            ytyp_info.append(f"YTYP Pos: ({p.x:.3f}, {p.y:.3f}, {p.z:.3f}) | Rot: ({r.x:.1f}, {r.y:.1f}, {r.z:.1f}, {r.w:.1f})")
                        if hasattr(arch, "bb_min") and hasattr(arch, "bb_max"):
                            bmin = arch.bb_min
                            bmax = arch.bb_max
                            ytyp_info.append(f"Archetype Bounds: Min({bmin.x:.3f}, {bmin.y:.3f}, {bmin.z:.3f}) Max({bmax.x:.3f}, {bmax.y:.3f}, {bmax.z:.3f})")
        except:
            pass

        final_report = "\n".join(report_lines + ytyp_info)
        props.model_info = final_report

        print("\n" + "=" * 60)
        print("SOLLUMZ EXHAUSTIVE HIERARCHY REPORT")
        print("=" * 60)
        print(final_report)
        print("=" * 60 + "\n")

        self.report({'INFO'}, f"Full Sollumz report for {obj.name}")
        return {'FINISHED'}
