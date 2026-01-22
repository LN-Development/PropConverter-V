"""Integration layer for Sollumz addon.

This module provides a clean abstraction for interacting with the Sollumz addon,
following the Dependency Inversion Principle. It isolates all Sollumz-specific
code and provides a stable API for the rest of the addon.
"""

from typing import Optional, Any
import bpy
import importlib
import sys
from . import constants


class SollumzIntegration:
    """Service class for interacting with the Sollumz addon.
    
    This class provides a singleton interface to the Sollumz addon, handling:
    - Module name resolution
    - Availability checking
    - Preferences access
    - Material system access
    
    The singleton pattern ensures consistent state across the addon.
    """
    
    _instance: Optional['SollumzIntegration'] = None
    _module_name: Optional[str] = None
    
    @classmethod
    def get_instance(cls) -> 'SollumzIntegration':
        """Get the singleton instance of SollumzIntegration.
        
        Returns:
            The singleton SollumzIntegration instance
            
        Example:
            >>> sollumz = SollumzIntegration.get_instance()
            >>> if sollumz.is_available():
            >>>     mod_name = sollumz.get_module_name()
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance and cached module name.
        
        This is primarily useful for testing or when Sollumz is
        enabled/disabled at runtime.
        """
        cls._instance = None
        cls._module_name = None
    
    def is_available(self) -> bool:
        """Check if Sollumz is installed and its operators are available.
        
        This is the primary way to check if Sollumz functionality can be used.
        It verifies that the Sollumz operator namespace is registered in Blender.
        
        Returns:
            True if Sollumz operators are available, False otherwise
            
        Example:
            >>> sollumz = SollumzIntegration.get_instance()
            >>> if not sollumz.is_available():
            >>>     print("Sollumz addon is not installed")
        """
        return hasattr(bpy.ops, constants.SOLLUMZ_OPERATOR_NAMESPACE)
    
    def get_module_name(self) -> Optional[str]:
        """Get the Sollumz Python module name.
        
        This method finds the correct module name for importing Sollumz
        submodules. It caches the result for performance.
        
        The search strategy is:
        1. Try common module names first
        2. Search sys.modules for any module ending with "sollumz"
        3. Exclude our own addon's modules (containing "autoprop")
        
        Returns:
            The Sollumz module name (e.g., "sollumz" or "Sollumz"),
            or None if Sollumz is not available
            
        Example:
            >>> sollumz = SollumzIntegration.get_instance()
            >>> mod_name = sollumz.get_module_name()
            >>> if mod_name:
            >>>     materials_module = importlib.import_module(f"{mod_name}.ydr.shader_materials")
        """
        # Return cached value if available
        if self._module_name:
            return self._module_name
        
        # Verify Sollumz is available first
        if not self.is_available():
            return None
        
        # Try common module names first
        for name in constants.SOLLUMZ_MODULE_CANDIDATES:
            try:
                importlib.import_module(name)
                self._module_name = name
                return name
            except ImportError:
                continue
        
        # Search sys.modules for any module ending with "sollumz"
        # but exclude our own addon's internal modules
        for key in sys.modules.keys():
            if (key.lower().endswith("sollumz") and 
                constants.AUTOPROP_MODULE_IDENTIFIER not in key.lower()):
                self._module_name = key
                return key
        
        return None
    
    def get_preferences(self, context: bpy.types.Context) -> Optional[Any]:
        """Get Sollumz addon preferences from Blender.
        
        This method finds the Sollumz addon preferences, which contain
        export settings and other configuration options.
        
        Args:
            context: Blender context
            
        Returns:
            Sollumz addon preferences object, or None if not found
            
        Example:
            >>> sollumz = SollumzIntegration.get_instance()
            >>> prefs = sollumz.get_preferences(context)
            >>> if prefs:
            >>>     export_settings = prefs.export_settings
        """
        if not self.is_available():
            return None
        
        # Search through enabled addons
        for addon in context.preferences.addons:
            addon_module = addon.module.lower()
            # Match 'sollumz' but exclude our own addon (autoprop*)
            if ('sollumz' in addon_module and 
                constants.AUTOPROP_MODULE_IDENTIFIER not in addon_module):
                return addon.preferences
        
        return None
    
    def get_shader_materials(self) -> Optional[Any]:
        """Get Sollumz shader materials list.
        
        Returns:
            Sollumz shadermats object containing all available shaders,
            or None if Sollumz is not available
            
        Example:
            >>> sollumz = SollumzIntegration.get_instance()
            >>> shadermats = sollumz.get_shader_materials()
            >>> if shadermats:
            >>>     default_shader = next(s for s in shadermats if s.value == "default.sps")
        """
        mod_name = self.get_module_name()
        if not mod_name:
            return None
        
        try:
            shader_materials_module = importlib.import_module(
                f"{mod_name}.ydr.shader_materials"
            )
            return shader_materials_module.shadermats
        except (ImportError, AttributeError) as e:
            print(f"[SollumzIntegration] Failed to load shader materials: {e}")
            return None
    
    def get_collision_materials(self) -> Optional[Any]:
        """Get Sollumz collision materials module.
        
        Returns:
            Sollumz collision_materials module, or None if not available
            
        Example:
            >>> sollumz = SollumzIntegration.get_instance()
            >>> collision_mats = sollumz.get_collision_materials()
            >>> if collision_mats:
            >>>     material = collision_mats.create_collision_material_from_index(0)
        """
        mod_name = self.get_module_name()
        if not mod_name:
            return None
        
        try:
            return importlib.import_module(f"{mod_name}.ybn.collision_materials")
        except ImportError as e:
            print(f"[SollumzIntegration] Failed to load collision materials: {e}")
            return None
    
    def get_sollumz_properties(self) -> Optional[Any]:
        """Get Sollumz properties module (for ArchetypeType, SollumType, etc.).
        
        Returns:
            Sollumz sollumz_properties module, or None if not available
            
        Example:
            >>> sollumz = SollumzIntegration.get_instance()
            >>> props = sollumz.get_sollumz_properties()
            >>> if props:
            >>>     ArchetypeType = props.ArchetypeType
            >>>     SollumType = props.SollumType
        """
        mod_name = self.get_module_name()
        if not mod_name:
            return None
        
        try:
            return importlib.import_module(f"{mod_name}.sollumz_properties")
        except ImportError as e:
            print(f"[SollumzIntegration] Failed to load sollumz properties: {e}")
            return None


# Legacy function for backward compatibility
# TODO: Remove this after all code is migrated to use SollumzIntegration class
def resolve_sollumz_mod_name() -> Optional[str]:
    """Legacy function - use SollumzIntegration.get_instance().get_module_name() instead.
    
    DEPRECATED: This function is kept for backward compatibility.
    New code should use the SollumzIntegration class directly.
    """
    return SollumzIntegration.get_instance().get_module_name()


# Legacy function for backward compatibility
def get_sollumz_preferences(context: bpy.types.Context) -> Optional[Any]:
    """Legacy function - use SollumzIntegration.get_instance().get_preferences() instead.
    
    DEPRECATED: This function is kept for backward compatibility.
    New code should use the SollumzIntegration class directly.
    """
    return SollumzIntegration.get_instance().get_preferences(context)
