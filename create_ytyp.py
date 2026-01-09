def create_ytyp(context, original_name: str):
    try:
        print(f"Creating YTYP with name: {original_name}")
        ytyp_item = context.scene.ytyps.add()
        ytyp_item.name = original_name
        context.scene.ytyp_index = len(context.scene.ytyps) - 1
        print(f"Successfully created YTYP: {ytyp_item.name} at index {context.scene.ytyp_index}")
        return True
    except Exception as e:
        print(f"WARNING: Failed to create YTYP - {e}")
        import traceback
        traceback.print_exc()
        return False
