"""Mesh validation utilities.

This module provides validation logic for mesh objects before conversion,
following the Single Responsibility Principle.
"""

from typing import Tuple, Optional
import bpy
from .. import logger


class MeshValidator:
    """Validates mesh objects before conversion operations.
    
    This class centralizes all validation logic, making it easier to maintain
    and test. Each validation method returns a tuple of (is_valid, object).
    """
    
    @staticmethod
    def validate_for_conversion(
        context: bpy.types.Context,
        operator: Optional[bpy.types.Operator] = None
    ) -> Tuple[bool, Optional[bpy.types.Object]]:
        """Validate that the active object is ready for GTA V conversion.
        
        Performs the following checks:
        1. User is in Object Mode
        2. An object is selected
        3. The object is a mesh
        4. The mesh is selected
        
        Args:
            context: Blender context containing scene and object information
            operator: Optional operator instance for error reporting to info window
            
        Returns:
            Tuple of (is_valid, object) where:
            - is_valid: True if all validation passes, False otherwise
            - object: The validated mesh object, or None if validation fails
            
        Example:
            >>> validator = MeshValidator()
            >>> is_valid, obj = validator.validate_for_conversion(context, self)
            >>> if not is_valid:
            >>>     return {'CANCELLED'}
        """
        # Check object mode
        if context.mode != 'OBJECT':
            logger.log_error("messages.error.switch_to_object_mode", operator=operator)
            return False, None
        
        # Check active object exists
        obj = context.active_object
        if obj is None:
            logger.log_error('messages.error.no_object_selected', operator=operator)
            return False, None
        
        # Check it's a mesh
        if obj.type != "MESH":
            logger.log_error('messages.error.not_mesh', operator=operator, type=obj.type)
            return False, None
        
        # Check it's selected
        if not obj.select_get():
            logger.log_error('messages.error.not_selected', operator=operator)
            return False, None
        
        return True, obj
    
    @staticmethod
    def validate_mesh_has_geometry(
        obj: bpy.types.Object,
        operator: Optional[bpy.types.Operator] = None
    ) -> bool:
        """Validate that a mesh object has actual geometry data.
        
        Args:
            obj: The mesh object to validate
            operator: Optional operator for error reporting
            
        Returns:
            True if mesh has vertices, False otherwise
        """
        if obj.type != 'MESH':
            return False
        
        mesh = obj.data
        if len(mesh.vertices) == 0:
            logger.log_error('messages.error.empty_mesh', operator=operator)
            return False
        
        return True
    
    @staticmethod
    def validate_object_type(
        obj: Optional[bpy.types.Object],
        expected_type: str,
        operator: Optional[bpy.types.Operator] = None
    ) -> bool:
        """Validate that an object is of the expected type.
        
        Args:
            obj: Object to validate (can be None)
            expected_type: Expected Blender object type (e.g., 'MESH', 'EMPTY')
            operator: Optional operator for error reporting
            
        Returns:
            True if object exists and matches expected type, False otherwise
        """
        if obj is None:
            logger.log_error('messages.error.no_object_selected', operator=operator)
            return False
        
        if obj.type != expected_type:
            logger.log_error(
                'messages.error.wrong_type',
                operator=operator,
                expected=expected_type,
                actual=obj.type
            )
            return False
        
        return True
