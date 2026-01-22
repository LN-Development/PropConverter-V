"""Main conversion service coordinating the prop conversion workflow.

This service orchestrates the entire GTA V prop conversion process,
delegating to specialized modules for each step while maintaining
clean separation of concerns.
"""

from typing import Optional, Tuple
import bpy
from ..sollumz_integration import SollumzIntegration
from ..validators.mesh_validator import MeshValidator
from ..core.mesh_prep import duplicate_and_prepare_mesh
from ..core.conversion import (
    convert_collision,
    convert_drawable,
    convert_materials,
    create_ytyp,
    create_archetype
)
from ..core.mesh_prep.paint_vertex_colors import paint_vertex_colors
from .. import logger
from .. import constants


class ConversionService:
    """Orchestrates the GTA V prop conversion workflow.
    
    This service class follows the Single Responsibility Principle by focusing
    solely on coordinating the conversion workflow. It delegates validation,
    transformation, and integration tasks to specialized components.
    
    Attributes:
        sollumz: Sollumz integration service instance
        validator: Mesh validator instance
    
    Example:
        >>> service = ConversionService()
        >>> if service.convert_to_gtav(context, operator):
        >>>     print("Conversion successful!")
    """
    
    def __init__(self):
        """Initialize the conversion service with required dependencies."""
        self.sollumz = SollumzIntegration.get_instance()
        self.validator = MeshValidator()
    
    def convert_to_gtav(
        self,
        context: bpy.types.Context,
        operator: Optional[bpy.types.Operator] = None
    ) -> bool:
        """Convert the selected mesh to a GTA V prop.
        
        This is the main entry point for the conversion workflow. It performs
        the conversion in stages:
        
        1. Validate mesh and environment
        2. Prepare mesh (reset transforms, duplicate for collision)
        3. Convert collision mesh to Sollumz composite
        4. Convert drawable to Sollumz drawable with models
        5. Convert materials to selected shader
        6. Apply vertex colors
        7. Create YTYP and archetype entries
        
        Args:
            context: Blender context containing scene and object information
            operator: Optional operator instance for progress reporting
            
        Returns:
            True if conversion succeeded, False otherwise
            
        Example:
            >>> service = ConversionService()
            >>> success = service.convert_to_gtav(context, self)
            >>> return {'FINISHED'} if success else {'CANCELLED'}
        """
        # Stage 1: Validate
        is_valid, obj = self.validator.validate_for_conversion(context, operator)
        if not is_valid:
            return False
        
        # Stage 2: Check Sollumz availability
        if not self.sollumz.is_available():
            logger.log_error('messages.error.sollumz_not_found', operator=operator)
            return False
        
        mod_name = self.sollumz.get_module_name()
        if not mod_name:
            logger.log_error('messages.error.sollumz_not_found', operator=operator)
            return False
        
        # Stage 3: Prepare mesh
        original_name, collision_obj = self._prepare_mesh(context, obj, operator)
        if not collision_obj:
            return False
        
        # Stage 4: Convert collision
        composite_obj = convert_collision(context, collision_obj, mod_name)
        if composite_obj is None:
            logger.log_error('messages.error.collision_failed', operator=operator)
            return False
        
        # Stage 5: Convert drawable
        model_objs, drawable_parent = convert_drawable(context, obj, composite_obj)
        if not model_objs:
            logger.log_error('messages.error.drawable_failed', operator=operator)
            return False
        
        # Stage 6: Convert materials
        if not convert_materials(context, model_objs, mod_name):
            logger.log_error('messages.error.material_failed', operator=operator)
            return False
        
        # Stage 7: Apply vertex colors
        self._apply_vertex_colors(context, operator)
        
        # Stage 8: Create YTYP and Archetype
        if not create_ytyp(context, original_name):
            logger.log_error('messages.error.ytyp_failed', operator=operator)
            return False
        
        if not create_archetype(context, obj, mod_name, original_name):
            logger.log_error('messages.error.archetype_failed', operator=operator)
            return False
        
        return True
    
    def _prepare_mesh(
        self,
        context: bpy.types.Context,
        obj: bpy.types.Object,
        operator: Optional[bpy.types.Operator]
    ) -> Tuple[str, Optional[bpy.types.Object]]:
        """Prepare mesh for conversion by resetting transforms and duplicating.
        
        This method:
        1. Resets object origin to geometry center
        2. Resets location and rotation to world origin
        3. Duplicates mesh for collision with naming convention
        
        Args:
            context: Blender context
            obj: The mesh object to prepare
            operator: Optional operator for error reporting
            
        Returns:
            Tuple of (original_name, collision_mesh) where collision_mesh
            is None if preparation failed
        """
        # Reset transform to world origin
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        obj.location = constants.DEFAULT_LOCATION
        obj.rotation_euler = constants.DEFAULT_ROTATION
        
        # Duplicate for collision
        original_name, collision_obj = duplicate_and_prepare_mesh(context, obj)
        if not collision_obj:
            logger.log_error('messages.error.duplicate_failed', operator=operator)
            return "", None
        
        return original_name, collision_obj
    
    def _apply_vertex_colors(
        self,
        context: bpy.types.Context,
        operator: Optional[bpy.types.Operator]
    ) -> None:
        """Apply vertex colors to the original mesh based on user settings.
        
        This method retrieves the original mesh reference from scene properties
        and applies the configured vertex color to all vertices.
        
        Args:
            context: Blender context
            operator: Optional operator for warning reporting
        """
        props = getattr(context.scene, "prop_converter", None)
        if not props:
            return
        
        original_mesh_obj = props.original_mesh
        if original_mesh_obj:
            paint_col = getattr(props, "vertex_color", (1.0, 1.0, 1.0, 1.0))
            paint_vertex_colors(original_mesh_obj, None, color=tuple(paint_col))
        else:
            logger.log_warning(
                'messages.warning.original_mesh_not_found',
                operator=operator
            )
