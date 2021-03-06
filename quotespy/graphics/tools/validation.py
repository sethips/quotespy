from re import findall
from typing import Dict, List, Optional, Tuple, Union
from PIL import ImageFont
from .errors import (
    FontNotFound,
    InvalidColorFormat,
    InvalidFieldLength,
    InvalidFormatOption,
    MissingDictKeys,
    MissingGraphicInfoField,
    MissingGraphicSettings,
    MissingQuotes,
    MissingTitles,
    MissingTitlesOrQuotes,
)
from .type_interfaces import DefaultFormats, GraphicInfo, GraphicSettings


def __validate_dict_keys(
    dict_data: Union[GraphicInfo, GraphicSettings],
    typed_dict: Union[GraphicInfo, GraphicSettings],
    dict_name: str,
) -> None:
    """Validate that a custom `graphic_settings` or `graphic_info` dictionary has all the required fields.

    Parameters
    ----------
    dict_data : Union[GraphicInfo, GraphicSettings]
        Dictionary of graphic settings or information to be validated.
    typed_dict : Union[GraphicInfo, GraphicSettings]
        TypedDict that sets the required fields.
    dict_name : str
        Name of the dictionary under validation.

    Raises
    ------
    MissingDictKeys
        Raised when the custom dictionary is missing one or more fields.
    """
    # Get the keys from the type interface
    if dict_name == "graphic_settings":
        keys = typed_dict.__annotations__.keys()
    elif dict_name == "tweet_info":
        keys = typed_dict.__annotations__.keys()

    # Get the keys given by the user
    provided_keys = dict_data.keys()
    # Get a list of the keys not provided by the user
    missing_keys = [key for key in keys if key not in provided_keys]

    # If there are any missing keys, raise an error
    if missing_keys != list():
        error_msg = f"The `{dict_name}` dictionary must include the keys:\n\t{keys}.\n\tYou are missing {missing_keys}"
        raise MissingDictKeys(error_msg)


def __validate_text_loaded(titles: List[str], quotes: List[str]) -> None:
    """Validate that titles and quotes have been loaded from the given .txt file and that there's an equal amount of both.

    Parameters
    ----------
    titles : List[str]
        List of titles loaded.
    quotes : List[str]
        List of quotes/lyrics loaded.

    Raises
    ------
    MissingTitles
        Raised when no title has been loaded from the .txt file.
    MissingQuotes
        Raised when no quote/lyrics has been loaded from the .txt file.
    MissingTitlesOrQuotes
        Raised when titles and quotes/lyrics have been loaded in an uneven amount.
    """
    if titles == list():
        error_msg = "Make sure your titles are wrapped in brackets."
        raise MissingTitles(error_msg)
    elif quotes == list():
        error_msg = (
            "Make sure your quotes are written in the line right after the title."
        )
        raise MissingQuotes(error_msg)
    elif len(titles) != len(quotes):
        error_msg = (
            "Make sure your .txt file has an equal amount of titles and quotes/lyrics."
        )
        raise MissingTitlesOrQuotes(error_msg)


def __validate_font_family(value: str, error_msg: str) -> str:
    """Validate that the user has specified a font available in their machine.

    Parameters
    ----------
    value : str
        Name of the font.family loaded
    error_msg : str
        Error message for an invalid font name.

    Returns
    -------
    str
        The validated font name (including the .ttf file extension).

    Raises
    ------
    FontNotFound
        Raised when the font is not found on the user's machine.
    """
    # If the user has only passed the font name, add the file extension
    font_data = value.split(".")
    if len(font_data) == 1:
        value += ".ttf"

    # If the font can be loaded, it is valid; otherwise raise an exception
    try:
        dummy_font = ImageFont.truetype(value, 1, encoding="utf-8")
        return value
    except OSError:
        raise FontNotFound(error_msg)


def __validate_integer_fields(value: int, error_msg: str) -> int:
    """Validate integer values from a dictionary.

    Parameters
    ----------
    value : int
        Value to be validated.
    error_msg : str
        Error message for an invalid value.

    Returns
    -------
    int
        Validated value.

    Raises
    ------
    TypeError
        Raised when the value is not valid (namely, when it is data that cannot be cast to int).
    """
    try:
        int_field = int(value)
        return int_field
    except ValueError:
        raise TypeError(error_msg)


def __validate_size(
    value: List[int], error_msg_length: str, error_msg_type: str
) -> List[int]:
    """Validate the list that represents the size of the graphic (width and height).

    Parameters
    ----------
    value : List[int]
        List of integers (width and height).
    error_msg_length : str
        Error message to display for a list that has too many or too few values.
    error_msg_type : str
        Error message to be displayed if one of the two values is not a valid integer.

    Returns
    -------
    List[int]
        Validated list.

    Raises
    ------
    InvalidFieldLength
        Raised when the list has more or less than two values.    
    """
    # Fist verify that the list has appropriate length
    if len(value) != 2:
        raise InvalidFieldLength(error_msg_length)

    # Now validate that both values are valid integers
    width = __validate_integer_fields(value[0], error_msg_type)
    height = __validate_integer_fields(value[1], error_msg_type)
    return [width, height]


def __validate_color_scheme(
    value: List[str], error_msg_size: str, error_msg_color_format: str
) -> List[str]:
    """Validate the list that represents the graphic's color scheme (background and text colors in Hexadecimal format).

    Parameters
    ----------
    value : List[str]
        List of the color scheme.
    error_msg_size : str
        Error message to display for a list that has too many or too few values.
    error_msg_color_format : str
        Error message to display if either of the colors is invalid.

    Returns
    -------
    List[str]
        Validated color scheme.

    Raises
    ------
    InvalidFieldLength
        Raised if the list does not have the required length (two).
    InvalidColorFormat
        Raised if either the background or text color are not valid Hexadecimal values.
    """
    # Fist validate the list has the required length
    if len(value) != 2:
        raise InvalidFieldLength(error_msg_size)

    # Use regex to verify the colors are written as valid Hexadecimal values
    hex_color_pattern = r"^#(?:[0-9a-fA-F]{3}){1,2}$"
    background_color = findall(hex_color_pattern, value[0])
    text_color = findall(hex_color_pattern, value[1])
    # If the regex didn't match either the background or the text color, raise an exception
    if (background_color == list()) or (text_color == list()):
        raise InvalidColorFormat(error_msg_color_format)
    # Otherwise, the color scheme is valid
    else:
        return [background_color[0], text_color[0]]


def __validate_float_fields(value: float, error_msg: str) -> float:
    """Validate float values from a dictionary.

    Parameters
    ----------
    value : float
        Value to be validated.
    error_msg : str
        Error message for an invalid value.

    Returns
    -------
    float
        Validated value.

    Raises
    ------
    TypeError
        Raised when the value is not valid (namely, when it is data that cannot be cast to float).
    """
    try:
        float_field = float(value)
        return float_field
    except ValueError:
        raise TypeError(error_msg)


def validate_settings_existence(g_settings: GraphicSettings, def_settings: str) -> None:
    """Validate that there is either custom or default graphic settings to be used (i.e., either the user passed a dictionary of custom settings or an empty dictionary along with the specification of a default settings format).

    Parameters
    ----------
    g_settings : GraphicSettings
        Custom graphic settings.
    def_settings : str
        Default settings option chosen.

    Raises
    ------
    MissingGraphicSettings
        Raised when the user passed an empty dictionary and chose custom settings for the default settings format.
    """
    # Check if an empty dictionary was passed as the custom graphic settings
    custom_settings_empty = g_settings == dict()
    # Check if no default settings format was chosen (i.e., the user wants custom settings)
    custom_format_chosen = def_settings == DefaultFormats.CUSTOM.value

    # If True, then the custom settings are empty and the user chose a custom\
    # settings format, i.e., there are no graphic settings to use
    # Otherwise, there is either custom settings or a default format to use
    settings_not_received = custom_settings_empty and custom_format_chosen
    if settings_not_received == True:
        raise MissingGraphicSettings(
            'You did not pass custom settings (`graphic_settings`) nor a default settings format (`default_settings_format`).\n\tYou can either specify your own settings in a dictionary or, if you don\'t want that, pass an empty dictionary and specify a default format: "lyrics" or "quote".\n\tYou can call the `settings_help` method for indications on the fields needed for custom settings.'
        )


def validate_format_option(format_option: str) -> str:
    """Validate that the user chose an existing default settings option.

    Parameters
    ----------
    format_option : str
        Default settings format chosen.

    Returns
    -------
    str
        Validated settings format name.

    Raises
    ------
    InvalidFormatOption
        Raised when the default settings format name does not exist.
    """
    valid_options = [option.value for option in DefaultFormats]
    format_option = format_option.lower()
    if format_option in valid_options:
        return format_option
    else:
        avail_options = [option for option in valid_options if option != ""]
        error_msg = f"You chose an invalid default graphic settings format.\n\tPlease choose one of this: {avail_options}"
        raise InvalidFormatOption(error_msg)


def validate_g_settings(g_settings: GraphicSettings) -> GraphicSettings:
    """Validate a complete `graphic_settings` dictionary.

    Parameters
    ----------
    g_settings : GraphicSettings
        Dictionary of graphic settings.

    Returns
    -------
    GraphicSettings
        Validated dictionary.
    """
    # Validate if the input dictionary has all the required fields
    __validate_dict_keys(g_settings, GraphicSettings, "graphic_settings")

    font_family_error_msg = f"The font {g_settings['font_family']} was not in found in your machine.\n\tPlease note you can provide an absolute path to your font if needed."
    font_family_validated = __validate_font_family(
        g_settings["font_family"], font_family_error_msg
    )

    font_size_error_msg = (
        "Please provide a number for the font size (preferably an integer)."
    )
    font_size_validated = __validate_integer_fields(
        g_settings["font_size"], font_size_error_msg
    )

    size_error_msg_type = "Please provide a list of numbers for the width and height of the graphic (preferably an integer)."
    size_error_msg_length = "Please provide two measures for the graphic size: a first one for the width and a second for the height."
    size_validated = __validate_size(
        g_settings["size"], size_error_msg_length, size_error_msg_type
    )

    color_scheme_error_msg_format = (
        "Please provide valid Hex color values for both the background and text colors."
    )
    color_scheme_error_msg_length = "Please provide two colors for the color scheme: a first one for the background and a second for the text."
    color_scheme_validated = __validate_color_scheme(
        g_settings["color_scheme"],
        color_scheme_error_msg_length,
        color_scheme_error_msg_format,
    )

    wrap_limit_error_msg = "Please provide a number for the maximum number of characters to include in each line of the graphic text (preferably an integer)."
    wrap_limit_validated = __validate_integer_fields(
        g_settings["wrap_limit"], wrap_limit_error_msg
    )

    margin_bottom_error_msg = (
        "Please provide a number (float or int) for the margin bottom."
    )
    margin_bottom_validated = __validate_float_fields(
        g_settings["margin_bottom"], margin_bottom_error_msg
    )

    validated_settings = {
        "font_family": font_family_validated,
        "font_size": font_size_validated,
        "size": size_validated,
        "color_scheme": color_scheme_validated,
        "wrap_limit": wrap_limit_validated,
        "margin_bottom": margin_bottom_validated,
    }

    return validated_settings


def __validate_graphic_info_field(
    g_info: GraphicInfo, field: str, error_msg: str
) -> None:
    """Validate one field of the graphic's information dictionary.

    Parameters
    ----------
    g_info : GraphicInfo
        Complete `graphic_info` dictionary.
    field : str
        Name of the field to validate.
    error_msg : str
        Error message to be displayed if the field's value is invalid or the field does not exist.

    Raises
    ------
    MissingGraphicInfoField
        Raised if the field's value is invalid or the field does not exist.
    """
    try:
        field = g_info[field]
    except KeyError:
        raise MissingGraphicInfoField(error_msg)

    if type(field) != str:
        raise MissingGraphicInfoField(error_msg)


def validate_graphic_info(g_info: GraphicInfo) -> None:
    """Validate the complete `graphic_info` dictionary.

    Parameters
    ----------
    g_info : GraphicInfo
        Dictionary of graphic info.
    """
    # Validate if the input dictionary has all the required fields
    __validate_dict_keys(g_info, GraphicInfo, "graphic_settings")

    title_error_msg = 'The graphic info dictionary must have a "title" field with the title of the graphic as a string.'
    __validate_graphic_info_field(g_info, "title", title_error_msg)
    text_error_msg = 'The graphic info dictionary must have a "text" field with the quote/lyrics you want to be drawn, as a string.'
    __validate_graphic_info_field(g_info, "text", text_error_msg)
