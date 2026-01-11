import bpy


def log_pre_conversion(obj: bpy.types.Object):
    """Log comprehensive mesh state before conversion."""
    print("\n" + "="*80)
    print("[PRE_CONVERT] COMPREHENSIVE MESH ANALYSIS - BEFORE SOLLUMZ CONVERSION")
    print("="*80)
    
    mesh = obj.data
    print(f"[PRE_CONVERT] Object: {obj.name}")
    print(f"[PRE_CONVERT] Mesh data: {mesh.name}")
    print(f"[PRE_CONVERT] Mesh users: {mesh.users}")
    print(f"[PRE_CONVERT] Object type: {obj.type}")
    print(f"[PRE_CONVERT] Sollum type: {getattr(obj, 'sollum_type', 'N/A')}")
    
    # Topology
    print(f"\n[PRE_CONVERT] Topology:")
    print(f"[PRE_CONVERT]   Vertices: {len(mesh.vertices)}")
    print(f"[PRE_CONVERT]   Edges: {len(mesh.edges)}")
    print(f"[PRE_CONVERT]   Loops: {len(mesh.loops)}")
    print(f"[PRE_CONVERT]   Polygons: {len(mesh.polygons)}")
    
    # Normals
    print(f"\n[PRE_CONVERT] Normals:")
    print(f"[PRE_CONVERT]   Has custom normals: {mesh.has_custom_normals if hasattr(mesh, 'has_custom_normals') else 'N/A'}")
    if hasattr(mesh, 'corner_normals') and len(mesh.corner_normals) > 0:
        print(f"[PRE_CONVERT]   Corner normals count: {len(mesh.corner_normals)}")
        # Sample first 3 normals
        for i in range(min(3, len(mesh.corner_normals))):
            n = mesh.corner_normals[i].vector
            print(f"[PRE_CONVERT]     Loop {i} normal: ({n.x:.6f}, {n.y:.6f}, {n.z:.6f})")
    
    # Polygon analysis
    print(f"\n[PRE_CONVERT] Polygon analysis (first 3):")
    for poly_idx in range(min(3, len(mesh.polygons))):
        poly = mesh.polygons[poly_idx]
        print(f"[PRE_CONVERT]   Poly {poly_idx}: loop_start={poly.loop_start}, loop_total={poly.loop_total}, smooth={poly.use_smooth}")
        print(f"[PRE_CONVERT]     Vertices: {list(poly.vertices)}")
        print(f"[PRE_CONVERT]     Normal: ({poly.normal.x:.6f}, {poly.normal.y:.6f}, {poly.normal.z:.6f})")
    
    # Loop analysis
    print(f"\n[PRE_CONVERT] Loop analysis (first 5):")
    for i in range(min(5, len(mesh.loops))):
        loop = mesh.loops[i]
        print(f"[PRE_CONVERT]   Loop {i}: vertex={loop.vertex_index}, edge={loop.edge_index}")
    
    # Color attributes
    print(f"\n[PRE_CONVERT] Color attributes: {list(mesh.color_attributes.keys())}")
    for attr in mesh.color_attributes:
        print(f"[PRE_CONVERT]   '{attr.name}': domain={attr.domain}, type={attr.data_type}, length={len(attr.data)}")
    
    # Object transform
    print(f"\n[PRE_CONVERT] Transform:")
    print(f"[PRE_CONVERT]   Location: {obj.location}")
    print(f"[PRE_CONVERT]   Rotation: {obj.rotation_euler}")
    print(f"[PRE_CONVERT]   Scale: {obj.scale}")
    print(f"[PRE_CONVERT]   Matrix world: {obj.matrix_world}")
    
    # Parent info
    print(f"\n[PRE_CONVERT] Hierarchy:")
    print(f"[PRE_CONVERT]   Parent: {obj.parent.name if obj.parent else 'None'}")
    print(f"[PRE_CONVERT]   Children count: {len(obj.children)}")
    
    print("="*80 + "\n")


def log_post_conversion(obj: bpy.types.Object):
    """Log comprehensive mesh state after conversion."""
    print("\n" + "="*80)
    print("[POST_CONVERT] COMPREHENSIVE MESH ANALYSIS - AFTER SOLLUMZ CONVERSION")
    print("="*80)
    
    # After conversion, the original object becomes the parent, child is .model
    print(f"[POST_CONVERT] Original object: {obj.name}")
    print(f"[POST_CONVERT] Original object type: {obj.type}")
    print(f"[POST_CONVERT] Original Sollum type: {getattr(obj, 'sollum_type', 'N/A')}")
    
    if obj.type == 'MESH':
        mesh = obj.data
        print(f"[POST_CONVERT] Original still has mesh: {mesh.name}")
        print(f"[POST_CONVERT]   Vertices: {len(mesh.vertices)}")
        print(f"[POST_CONVERT]   Loops: {len(mesh.loops)}")
        print(f"[POST_CONVERT]   Polygons: {len(mesh.polygons)}")
    else:
        print(f"[POST_CONVERT] Original is now: {obj.type}")
    
    print(f"\n[POST_CONVERT] Parent check:")
    print(f"[POST_CONVERT]   Has parent: {obj.parent is not None}")
    print(f"[POST_CONVERT]   Children count: {len(obj.children)}")
    
    # Analyze all children
    print(f"\n[POST_CONVERT] Analyzing children:")
    for child in obj.children:
        print(f"[POST_CONVERT]   Child: {child.name}")
        print(f"[POST_CONVERT]     Type: {child.type}")
        print(f"[POST_CONVERT]     Sollum type: {getattr(child, 'sollum_type', 'N/A')}")
        
        if child.type == 'MESH':
            child_mesh = child.data
            print(f"[POST_CONVERT]     Mesh data: {child_mesh.name}")
            print(f"[POST_CONVERT]     Mesh users: {child_mesh.users}")
            print(f"[POST_CONVERT]     Vertices: {len(child_mesh.vertices)}")
            print(f"[POST_CONVERT]     Loops: {len(child_mesh.loops)}")
            print(f"[POST_CONVERT]     Polygons: {len(child_mesh.polygons)}")
            print(f"[POST_CONVERT]     Color attributes: {list(child_mesh.color_attributes.keys())}")
            print(f"[POST_CONVERT]     Has custom normals: {child_mesh.has_custom_normals if hasattr(child_mesh, 'has_custom_normals') else 'N/A'}")
            
            # Check if mesh data is shared with parent
            if obj.type == 'MESH' and child_mesh.name == obj.data.name:
                print(f"[POST_CONVERT]     WARNING: Child shares mesh data with parent!")
            
            # Sample normals
            if hasattr(child_mesh, 'corner_normals') and len(child_mesh.corner_normals) > 0:
                print(f"[POST_CONVERT]     Corner normals (first 3):")
                for i in range(min(3, len(child_mesh.corner_normals))):
                    n = child_mesh.corner_normals[i].vector
                    print(f"[POST_CONVERT]       Loop {i}: ({n.x:.6f}, {n.y:.6f}, {n.z:.6f})")
            
            # Sample polygon smoothing
            print(f"[POST_CONVERT]     Polygon smoothing (first 3):")
            for poly_idx in range(min(3, len(child_mesh.polygons))):
                poly = child_mesh.polygons[poly_idx]
                print(f"[POST_CONVERT]       Poly {poly_idx}: smooth={poly.use_smooth}, normal=({poly.normal.x:.6f}, {poly.normal.y:.6f}, {poly.normal.z:.6f})")
    
    print("="*80 + "\n")


def log_mesh_internals(context, obj: bpy.types.Object):
    """Log deep mesh internals after conversion."""
    print("\n" + "="*80)
    print("[MESH_INTERNALS] DEEP MESH DATA ANALYSIS AFTER CONVERSION")
    print("="*80)
    
    models = [obj] if obj.type == 'MESH' else (obj.children if hasattr(obj, 'children') else [])
    
    for m_idx, model in enumerate(models):
        if model.type != 'MESH':
            continue
            
        mesh = model.data
        print(f"\n[MESH_INTERNALS] Model {m_idx}: {model.name}")
        print(f"[MESH_INTERNALS]   Mesh data name: {mesh.name}")
        print(f"[MESH_INTERNALS]   Mesh data pointer: {hash(mesh)}")
        print(f"[MESH_INTERNALS]   Mesh users: {mesh.users}")
        print(f"[MESH_INTERNALS]   Is library data: {mesh.library is not None}")
        print(f"[MESH_INTERNALS]   Is evaluated: {mesh.is_evaluated if hasattr(mesh, 'is_evaluated') else 'N/A'}")
        
        # Topology
        print(f"[MESH_INTERNALS]   Vertices: {len(mesh.vertices)}")
        print(f"[MESH_INTERNALS]   Edges: {len(mesh.edges)}")
        print(f"[MESH_INTERNALS]   Loops: {len(mesh.loops)}")
        print(f"[MESH_INTERNALS]   Polygons: {len(mesh.polygons)}")
        
        # Get evaluated mesh for comparison
        depsgraph = context.evaluated_depsgraph_get()
        eval_obj = model.evaluated_get(depsgraph)
        eval_mesh = eval_obj.data
        
        print(f"\n[MESH_INTERNALS] Evaluated mesh comparison:")
        print(f"[MESH_INTERNALS]   Eval mesh name: {eval_mesh.name}")
        print(f"[MESH_INTERNALS]   Eval mesh pointer: {hash(eval_mesh)}")
        print(f"[MESH_INTERNALS]   Same as base? {eval_mesh == mesh}")
        print(f"[MESH_INTERNALS]   Eval vertices: {len(eval_mesh.vertices)} (base: {len(mesh.vertices)})")
        print(f"[MESH_INTERNALS]   Eval loops: {len(eval_mesh.loops)} (base: {len(mesh.loops)})")
        print(f"[MESH_INTERNALS]   Eval polygons: {len(eval_mesh.polygons)} (base: {len(mesh.polygons)})")
        
        # Normals analysis
        print(f"\n[MESH_INTERNALS] Normals data:")
        print(f"[MESH_INTERNALS]   Has custom normals: {mesh.has_custom_normals if hasattr(mesh, 'has_custom_normals') else 'N/A'}")
        
        if hasattr(mesh, 'corner_normals'):
            print(f"[MESH_INTERNALS]   Corner normals count: {len(mesh.corner_normals)}")
            if len(mesh.corner_normals) > 0:
                # Calculate hash of normal data for change detection
                normal_hash = hash(tuple(round(n.vector.x, 6) + round(n.vector.y, 6) + round(n.vector.z, 6) for n in list(mesh.corner_normals)[:100]))
                print(f"[MESH_INTERNALS]   Normals hash (first 100): {normal_hash}")
                
                # Sample normals
                for i in [0, 1, 2, len(mesh.corner_normals)//2, -1]:
                    if 0 <= i < len(mesh.corner_normals) or i == -1:
                        n = mesh.corner_normals[i].vector
                        print(f"[MESH_INTERNALS]   Loop {i} normal: ({n.x:.6f}, {n.y:.6f}, {n.z:.6f})")
        
        # Transformation matrices
        print(f"\n[MESH_INTERNALS] Transformation:")
        print(f"[MESH_INTERNALS]   Object location: {model.location}")
        print(f"[MESH_INTERNALS]   Object rotation: {model.rotation_euler}")
        print(f"[MESH_INTERNALS]   Object scale: {model.scale}")
        print(f"[MESH_INTERNALS]   Matrix local: {model.matrix_local}")
        print(f"[MESH_INTERNALS]   Matrix world: {model.matrix_world}")
        print(f"[MESH_INTERNALS]   Matrix basis: {model.matrix_basis}")
        
        # Parent transformation
        if model.parent:
            print(f"[MESH_INTERNALS]   Parent: {model.parent.name}")
            print(f"[MESH_INTERNALS]   Parent matrix: {model.parent.matrix_world}")
        
        # Vertex data hashing
        if len(mesh.vertices) > 0:
            vert_hash = hash(tuple((round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in list(mesh.vertices)[:100]))
            print(f"[MESH_INTERNALS]   Vertex positions hash (first 100): {vert_hash}")
    
    print("="*80 + "\n")
