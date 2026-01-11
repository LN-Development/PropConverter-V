# Operators module
from .convert_operator import PROPCONVERTER_OT_convert_to_gtav
from .paint_operator import PROPCONVERTER_OT_paint_vertex_colors
from .export_operator import PROPCONVERTER_OT_export_prop

classes = [
    PROPCONVERTER_OT_convert_to_gtav,
    PROPCONVERTER_OT_paint_vertex_colors,
    PROPCONVERTER_OT_export_prop,
]


def register():
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    import bpy
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
