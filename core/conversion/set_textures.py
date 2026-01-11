import bpy
import re


def set_textures_from_original_name(context, model_objs, original_name: str) -> bool:
    """
    Assign per-material external texture paths using the original mesh name with an index.
    """
    try:
        if not model_objs or not original_name:
            return False

        # Collect unique materials from all provided model objects
        unique_mats: list[bpy.types.Material] = []
        seen = set()
        for obj in model_objs:
            for slot in obj.material_slots:
                mat = slot.material
                if mat is None:
                    continue
                # Use id(mat) to ensure uniqueness by datablock pointer
                if id(mat) not in seen:
                    unique_mats.append(mat)
                    seen.add(id(mat))

        # Assign numbered texture paths per unique material
        for idx, mat in enumerate(unique_mats):
            # Ensure material has a node tree
            if not hasattr(mat, "node_tree") or mat.node_tree is None:
                continue

            base_name = f"{original_name}{idx}"

            for n in mat.node_tree.nodes:
                if isinstance(n, bpy.types.ShaderNodeTexImage):
                    raw_label = (getattr(n, "name", "") or "").lower()
                    # Sanitize: remove non-alphanumeric, collapse underscores, strip common suffixes like "sampler"
                    label = re.sub(r"[^a-z0-9]+", "_", raw_label).strip("_")
                    label = re.sub(r"_sampler$", "", label)
                    texture_relpath = f"//{base_name}_{label}.dds"
                    # Force external file reference
                    if n.image is None:
                        # Create a minimal image datablock so we can set a filepath
                        n.image = bpy.data.images.new(name=f"{base_name}_{label}", width=1, height=1)
                    n.image.source = "FILE"
                    n.image.filepath = texture_relpath
        return True
    except Exception as e:
        print(f"ERROR: set_textures_from_original_name failed: {e}")
        import traceback
        traceback.print_exc()
        return False
