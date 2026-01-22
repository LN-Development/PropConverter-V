"""
Centralized logging utility for PropConverter-V
Provides error, warning, and info logging with:
- Popup notifications
- Console output
- Info window integration (when operator is available)
"""
import bpy
from datetime import datetime
from . import i18n


class ShowMessageBox(bpy.types.Operator):
    """Display a message box popup"""
    bl_idname = "propconverter.show_message_box"
    bl_label = "PropConverter-V"
    
    message: bpy.props.StringProperty(
        name="Message",
        description="Message to display",
        default=""
    )
    
    title: bpy.props.StringProperty(
        name="Title",
        description="Title of the message box",
        default="PropConverter-V"
    )
    
    icon: bpy.props.StringProperty(
        name="Icon",
        description="Icon to display",
        default="INFO"
    )
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        # Split message by newlines and display each line
        lines = self.message.split('\n')
        for line in lines:
            if line.strip():
                layout.label(text=line)


def _show_popup(title, message, icon='INFO'):
    """
    Show a popup message box
    
    Args:
        title: Title of the popup
        message: Message to display
        icon: Icon to display ('ERROR', 'WARNING', 'INFO')
    """
    try:
        bpy.ops.propconverter.show_message_box('INVOKE_DEFAULT', 
                                                message=message, 
                                                title=title, 
                                                icon=icon)
    except Exception as e:
        print(f"[LOGGER] Failed to show popup: {e}")


def _format_console_message(level, message):
    """
    Format a message for console output
    
    Args:
        level: Log level (ERROR, WARNING, INFO)
        message: Message to log
        
    Returns:
        Formatted string with timestamp and level
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] [{level}] PropConverter-V: {message}"


def log_error(message_key, operator=None, show_popup=False, **kwargs):
    """
    Log an error message
    
    Args:
        message_key: Translation key for the error message
        operator: Optional operator instance for info window reporting
        show_popup: Whether to show a popup notification (default: False)
        **kwargs: Format arguments for the message
    """
    # Get translated message
    message = i18n.t(message_key, **kwargs)
    
    # Console output
    console_msg = _format_console_message("ERROR", message)
    print(console_msg)
    
    # Popup notification
    if show_popup:
        _show_popup("Error", message, icon='ERROR')
    
    # Info window (if operator available)
    if operator is not None:
        try:
            operator.report({'ERROR'}, message)
        except Exception as e:
            print(f"[LOGGER] Failed to report to operator: {e}")


def log_warning(message_key, operator=None, show_popup=False, **kwargs):
    """
    Log a warning message
    
    Args:
        message_key: Translation key for the warning message
        operator: Optional operator instance for info window reporting
        show_popup: Whether to show a popup notification (default: False)
        **kwargs: Format arguments for the message
    """
    # Get translated message
    message = i18n.t(message_key, **kwargs)
    
    # Console output
    console_msg = _format_console_message("WARNING", message)
    print(console_msg)
    
    # Popup notification (optional for warnings)
    if show_popup:
        _show_popup("Warning", message, icon='WARNING')
    
    # Info window (if operator available)
    if operator is not None:
        try:
            operator.report({'WARNING'}, message)
        except Exception as e:
            print(f"[LOGGER] Failed to report to operator: {e}")


def log_info(message_key, operator=None, show_popup=False, **kwargs):
    """
    Log an info message
    
    Args:
        message_key: Translation key for the info message
        operator: Optional operator instance for info window reporting
        show_popup: Whether to show a popup notification (default: False)
        **kwargs: Format arguments for the message
    """
    # Get translated message
    message = i18n.t(message_key, **kwargs)
    
    # Console output
    console_msg = _format_console_message("INFO", message)
    print(console_msg)
    
    # Popup notification (optional for info)
    if show_popup:
        _show_popup("Information", message, icon='INFO')
    
    # Info window (if operator available)
    if operator is not None:
        try:
            operator.report({'INFO'}, message)
        except Exception as e:
            print(f"[LOGGER] Failed to report to operator: {e}")


# Classes to register
classes = [
    ShowMessageBox,
]


def register():
    """Register logger classes"""
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass  # Already registered


def unregister():
    """Unregister logger classes"""
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass  # Already unregistered
