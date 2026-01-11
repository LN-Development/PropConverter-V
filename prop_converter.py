import bpy
from .resolve_sollumz_mod_name import resolve_sollumz_mod_name
from .core.mesh_prep import duplicate_and_prepare_mesh
from .core.conversion import (
    convert_collision,
    convert_drawable,
    convert_materials,
    create_ytyp,
    create_archetype
)
from .core.mesh_prep.paint_vertex_colors import paint_vertex_colors


def convertToGtaV(context) -> bool:
    """
    Convert the selected mesh to a default prop
    Duplicates the object and adds 'col' to the duplicate's name
    Stores both objects in temporary memory for further operations
    """
    print("\n\n" + "="*80)
    print("[MAIN] PropConverter - Convert to GTA V: STARTING")
    print("="*80 + "\n")
    
    # Pre-flight checks
    print("[CHECK] Performing pre-flight checks...")
    if context.mode != 'OBJECT':
        print(f"[ERROR] Must be in Object Mode (current mode: {context.mode})")
        return False
    print("[CHECK]   ✓ Mode is OBJECT")

    obj = context.active_object
    if obj is None:
        print("[ERROR] No active object selected")
        return False
    print(f"[CHECK]   ✓ Active object: {obj.name}")
    
    if obj.type != "MESH":
        print(f"[ERROR] Object is not a mesh (type: {obj.type})")
        return False
    print("[CHECK]   ✓ Object is a MESH")
    
    if not obj.select_get():
        print("[ERROR] Object outline is not selected")
        return False
    print("[CHECK]   ✓ Object is selected")

    mod_name = resolve_sollumz_mod_name()
    if mod_name is None:
        print("[ERROR] Sollumz addon is not installed or not in sys.path")
        return False
    print(f"[CHECK]   ✓ Sollumz module found: {mod_name}")
    print("[CHECK] All pre-flight checks passed!\n")

    # Set geometry origin to world origin and reset transforms
    print("[PREPARE] Setting geometry origin to world origin...")
    print(f"[DEBUG] Original location: {obj.location}")
    print(f"[DEBUG] Original rotation: {obj.rotation_euler}")
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    print(f"[PREPARE] Origin set to world origin (0, 0, 0)")
    print(f"[PREPARE] Rotation reset to (0, 0, 0)\n")

    original_name, collision_obj = duplicate_and_prepare_mesh(context, obj)
    if not collision_obj:
        print("[ERROR] Failed to duplicate and prepare mesh")
        return False
    print(f"[STAGE 1] ✓ Mesh duplication and preparation complete\n")

    composite_obj = convert_collision(context, collision_obj, mod_name)
    if composite_obj is None:
        print("[ERROR] Collision conversion failed")
        return False
    print(f"[STAGE 2] ✓ Collision conversion complete\n")

    model_objs, drawable_parent = convert_drawable(context, obj, composite_obj)
    if not model_objs:
        print("[ERROR] Drawable conversion failed")
        return False
    print(f"[STAGE 3] ✓ Drawable conversion complete - {len(model_objs)} model objects found\n")
    
    # DEBUG: Log original mesh and model objects state
    original_mesh_obj = getattr(context.scene, "prop_converter", None)
    if original_mesh_obj:
        original_mesh_obj = original_mesh_obj.original_mesh
    print(f"[DEBUG] Original mesh object: {original_mesh_obj.name if original_mesh_obj else 'None'}")
    print(f"[DEBUG] Model objects count: {len(model_objs)}")
    print(f"[DEBUG] Model objects: {[m.name for m in model_objs]}")
    print(f"[DEBUG] Original mesh color attributes before material conversion: {list(original_mesh_obj.data.color_attributes.keys()) if original_mesh_obj else 'N/A'}\n")

    if not convert_materials(context, model_objs, mod_name):
        print("[ERROR] Material conversion failed")
        return False
    print(f"[STAGE 4] ✓ Material conversion complete\n")
    
    # Apply auto-color painting AFTER conversion
    print("[STAGE 5] Painting vertex colors...")
    if original_mesh_obj:
        paint_col = getattr(getattr(context.scene, "prop_converter", None), "vertex_color", (1.0, 1.0, 1.0, 1.0))
        print(f"[PAINT] Painting vertex colors on original mesh AFTER conversion with color: {paint_col}")
        paint_vertex_colors(original_mesh_obj, None, color=tuple(paint_col))
    else:
        print("[WARNING] Original mesh object not found")
    
    print(f"[STAGE 5] ✓ Vertex color painting complete\n")
    
    # DEBUG: Final mesh state for comparison
    print("[DEBUG] FINAL MESH STATE AFTER ALL CONVERSIONS:")
    print("="*80)
    if original_mesh_obj:
        mesh = original_mesh_obj.data
        print(f"[FINAL] Object: {original_mesh_obj.name}")
        print(f"[FINAL] Vertices: {len(mesh.vertices)}")
        print(f"[FINAL] Edges: {len(mesh.edges)}")
        print(f"[FINAL] Loops: {len(mesh.loops)}")
        print(f"[FINAL] Polygons: {len(mesh.polygons)}")
        print(f"[FINAL] Color attributes: {list(mesh.color_attributes.keys())}")
        print(f"[FINAL] Has custom normals: {mesh.has_custom_normals if hasattr(mesh, 'has_custom_normals') else 'N/A'}")
        print(f"[FINAL] Use auto smooth: {mesh.use_auto_smooth if hasattr(mesh, 'use_auto_smooth') else 'N/A'}")
        
        # Count sharp edges
        sharp_edges = sum(1 for edge in mesh.edges if edge.use_edge_sharp)
        print(f"[FINAL] Sharp edges: {sharp_edges} / {len(mesh.edges)}")
        
        # Material info
        print(f"[FINAL] Material slots: {len(original_mesh_obj.material_slots)}")
        for i, slot in enumerate(original_mesh_obj.material_slots):
            print(f"[FINAL]   Slot {i}: {slot.material.name if slot.material else '<empty>'}")
        
        # Check if mesh is using smooth shading
        smooth_faces = sum(1 for poly in mesh.polygons if poly.use_smooth)
        print(f"[FINAL] Smooth faces: {smooth_faces} / {len(mesh.polygons)}")
    print("="*80 + "\n")

    print("[STAGE 6] Creating YTYP file...")
    if not create_ytyp(context, original_name):
        print("[ERROR] YTYP creation failed")
        return False
    print(f"[STAGE 6] ✓ YTYP creation complete\n")

    print("[STAGE 7] Creating archetype...")
    if not create_archetype(context, obj, mod_name, original_name):
        print("[ERROR] Archetype creation failed")
        return False
    print(f"[STAGE 7] ✓ Archetype creation complete\n")

    print("="*80)
    print("[SUCCESS] PropConverter - Convert to GTA V: COMPLETE")
    print(f"[RESULT] Successfully converted '{original_name}' to GTA V prop with collision and archetype")
    print("="*80 + "\n")
    return True

