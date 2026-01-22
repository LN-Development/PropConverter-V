import importlib
import sys
import bpy


def resolve_sollumz_mod_name():
    """
    Resolve the Sollumz addon module name by verifying it's actually installed.
    
    This function checks if Sollumz is installed by:
    1. Verifying that Sollumz operators are registered in Blender
    2. Finding the correct module name in sys.modules
    
    Returns:
        str: The Sollumz module name if found, None otherwise
    """
    # First, verify that Sollumz operators are actually available
    if not hasattr(bpy.ops, 'sollumz'):
        return None
    
    # Sollumz is installed, now find its module name
    mod_name = None
    
    # Try common module names first
    for name in ("sollumz", "Sollumz"):
        try:
            importlib.import_module(name)
            mod_name = name
            break
        except ImportError:
            continue

    # If not found, search sys.modules for any module ending with "sollumz"
    # but exclude our own addon's internal modules
    if mod_name is None:
        for key in sys.modules.keys():
            # Exclude our own addon's module name (autoPropSollumz)
            if key.lower().endswith("sollumz") and "autoprop" not in key.lower():
                mod_name = key
                break

    return mod_name


def get_sollumz_preferences(context):
    """
    Get the Sollumz addon preferences from Blender.
    
    This function searches through all enabled addons to find Sollumz,
    ensuring it doesn't match our own addon (autoPropSollumz).
    
    Args:
        context: Blender context
        
    Returns:
        Sollumz addon preferences object if found, None otherwise
    """
    # First verify Sollumz operators are available
    if not hasattr(bpy.ops, 'sollumz'):
        return None
    
    # Search through enabled addons
    for addon in context.preferences.addons:
        addon_module = addon.module.lower()
        # Match 'sollumz' but exclude our own addon (autoprop*)
        if 'sollumz' in addon_module and 'autoprop' not in addon_module:
            return addon.preferences
    
    return None
