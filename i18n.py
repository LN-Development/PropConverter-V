"""
Internationalization (i18n) module for PropConverter-V
Provides translation support for multiple languages
"""
import os
import json
import bpy

# Global translation cache
_translations = {}
_current_language = "en_US"  # Default to English
_fallback_language = "en_US"

def get_addon_directory():
    """Get the addon directory path"""
    # Return the directory containing this i18n.py file
    # This works both for regular addons and Blender extensions
    return os.path.dirname(os.path.abspath(__file__))

def load_language(language_code):
    """
    Load translation file for the specified language
    
    Args:
        language_code: Language code (e.g., 'en_US', 'pt_BR')
    
    Returns:
        dict: Translation dictionary or None if file not found
    """
    addon_dir = get_addon_directory()
    locale_file = os.path.join(addon_dir, "locales", f"{language_code}.json")
    
    if not os.path.exists(locale_file):
        print(f"[i18n] Translation file not found: {locale_file}")
        return None
    
    try:
        with open(locale_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[i18n] Error loading translation file {locale_file}: {e}")
        return None

def initialize():
    """Initialize the translation system"""
    global _translations, _current_language
    
    # Load default language (English)
    _translations[_current_language] = load_language(_current_language)
    
    # Load fallback language (English)
    if _fallback_language != _current_language:
        _translations[_fallback_language] = load_language(_fallback_language)
    
    print(f"[i18n] Initialized with language: {_current_language}")

def set_language(language_code):
    """
    Set the current language
    
    Args:
        language_code: Language code (e.g., 'en_US', 'pt_BR')
    """
    global _current_language, _translations
    
    # Load language if not already loaded
    if language_code not in _translations:
        _translations[language_code] = load_language(language_code)
    
    if _translations.get(language_code):
        _current_language = language_code
        print(f"[i18n] Language changed to: {language_code}")
        
        # Update Blender UI
        try:
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    area.tag_redraw()
        except:
            pass  # Ignore if context is not available
    else:
        print(f"[i18n] Failed to set language: {language_code}")

def get_current_language():
    """Get the current language code"""
    return _current_language

def t(key, **kwargs):
    """
    Translate a key to the current language
    
    Args:
        key: Translation key in dot notation (e.g., 'ui.convert_button')
        **kwargs: Optional format arguments for string interpolation
    
    Returns:
        str: Translated string or the key itself if translation not found
    """
    global _translations, _current_language, _fallback_language
    
    # Get translation from current language
    translation = _get_nested_value(_translations.get(_current_language, {}), key)
    
    # Fallback to English if not found
    if translation is None and _fallback_language != _current_language:
        translation = _get_nested_value(_translations.get(_fallback_language, {}), key)
    
    # If still not found, return the key itself
    if translation is None:
        print(f"[i18n] Translation not found for key: {key}")
        return key
    
    # Apply string formatting if kwargs provided
    if kwargs:
        try:
            return translation.format(**kwargs)
        except KeyError as e:
            print(f"[i18n] Missing format argument for key '{key}': {e}")
            return translation
    
    return translation

def _get_nested_value(data, key):
    """
    Get a nested value from a dictionary using dot notation
    
    Args:
        data: Dictionary to search
        key: Key in dot notation (e.g., 'ui.convert_button')
    
    Returns:
        Value if found, None otherwise
    """
    if not data:
        return None
    
    keys = key.split('.')
    value = data
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None
    
    return value

def get_available_languages():
    """
    Get list of available languages
    
    Returns:
        list: List of tuples (language_code, language_name, description)
    """
    addon_dir = get_addon_directory()
    locales_dir = os.path.join(addon_dir, "locales")
    
    if not os.path.exists(locales_dir):
        return []
    
    languages = []
    for filename in os.listdir(locales_dir):
        if filename.endswith('.json'):
            lang_code = filename[:-5]  # Remove .json extension
            lang_data = load_language(lang_code)
            if lang_data:
                lang_name = lang_data.get('language_name', lang_code)
                languages.append((lang_code, lang_name, lang_name))
    
    return languages

