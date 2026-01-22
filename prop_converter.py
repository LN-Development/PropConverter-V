import bpy
from .services.conversion_service import ConversionService


def convertToGtaV(context, operator=None) -> bool:
    """Convert the selected mesh to a default prop.
    
    This function is a thin wrapper around ConversionService for backward
    compatibility. New code should use ConversionService directly.
    
    Args:
        context: Blender context
        operator: Optional operator instance for error reporting
        
    Returns:
        True if conversion succeeded, False otherwise
        
    Example:
        >>> if convertToGtaV(context, self):
        >>>     print("Conversion successful!")
    """
    service = ConversionService()
    return service.convert_to_gtav(context, operator)


