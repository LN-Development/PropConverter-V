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
from ..core.conversion.apply_dynamic_flags import apply_dynamic_flags
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
        props = getattr(context.scene, "prop_converter", None)
        is_dynamic = props.is_dynamic_prop if props else False
        is_door = props.is_door_prop if props else False
        
        # Stages sync: if door, we skip composite requirement
        collision_parent = convert_collision(context, collision_obj, mod_name, is_dynamic=is_dynamic, is_door=is_door)
        if collision_parent is None:
            logger.log_error('messages.error.collision_failed', operator=operator)
            return False
        
        # Stage 5: Convert drawable
        # For Doors, the collision_parent is the Box itself, but it should be a sibling to the model, 
        # both under the Armature. convert_drawable handles this by parenting to the armature.
        model_objs, drawable_parent = convert_drawable(context, obj, collision_parent)
        if not model_objs:
            logger.log_error('messages.error.drawable_failed', operator=operator)
            return False
        
        if is_dynamic or is_door:
            from ..core.conversion.apply_dynamic_flags import apply_dynamic_flags
            drawable_parent = apply_dynamic_flags(
                context, collision_parent, drawable_parent, 
                is_dynamic=is_dynamic, is_door=is_door
            )
        
        # Stage 6: Convert materials
        if not convert_materials(context, model_objs, mod_name, original_name):
            logger.log_error('messages.error.material_failed', operator=operator)
            return False
        
        # Stage 7: Apply vertex colors
        self._apply_vertex_colors(context, operator)
        
        # Stage 8: Create YTYP and Archetype
        if not create_ytyp(context, original_name):
            logger.log_error('messages.error.ytyp_failed', operator=operator)
            return False
        
        if not create_archetype(
            context, drawable_parent, mod_name, original_name, 
            is_dynamic=is_dynamic, is_door=is_door
        ):
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
        
        # For dynamic props, reset rotation and move to world origin with origin point at (0,0,0)
        props = getattr(context.scene, "prop_converter", None)
        if props and props.is_dynamic_prop and obj.type == 'MESH':
            from mathutils import Vector
            
            # 1. Clear parent to ensure absolute world space logic
            if obj.parent:
                world_matrix = obj.matrix_world.copy()
                obj.parent = None
                obj.matrix_world = world_matrix

            # 2. Reset rotation and location to identity
            obj.location = (0.0, 0.0, 0.0)
            obj.rotation_euler = (0.0, 0.0, 0.0)
            obj.scale = (1.0, 1.0, 1.0)
            context.view_layer.update()
            
            # 3. Center origin on geometry bounds center
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            
            # 4. Move mesh so the bottom sits at Z=0 and center is at XY=0
            obj.location = (0.0, 0.0, 0.0)
            context.view_layer.update()
            bbox_world = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
            min_z = min(v.z for v in bbox_world)
            obj.location.z -= min_z
            
            # 5. Bring origin to world (0,0,0) while mesh stays grounded
            # This satisfies "set the origin to world origin"
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
            
            print(f"[DYNAMIC] Rotation reset to 0. Mesh grounded at (0,0,0). Origin moved to world (0,0,0).")
        else:
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
