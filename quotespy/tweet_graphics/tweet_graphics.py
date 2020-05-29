from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap
from typing import Optional
from os import path
from .tools.type_interfaces import TweetInfo, GraphicSettings, DefaultFormats
from .tools.utils import parse_json_settings, process_pic, get_ready_tweets, calculate_content_dimensions
from .tools.validation import validate_settings_existence, validate_format_option, validate_g_settings, validate_tweet_info
from .tools.default_settings import blue_mode_settings, light_mode_settings, dark_mode_settings


def settings_help():
    print("""If you are interested in using custom graphic settings, please pass a dictionary with the following fields and data types to the `graphic_settings` argument:
    "font_family": string with the name of the font to use;
    "font_size_header": size of the font to be used for the header;
    "font_size_text": size of the font to be used for the tweet text;
    "size": two-item list with the width and height of the graphic;
    "color_scheme": two-item list with the background and text colors of the graphic;
    "wrap_limit": max number of characters to allow per line of text;
    "margin_bottom": space to leave in between text lines;
    Please note the colors must be passed as Hexadecimal values and the numerical values as integers.
    All numerical values are used as pixels.
    """)


def info_help():
    print("""The `graphic_info` dictionary must have two fields, both with string values:
    "tweet_name": name of the tweet graphic;
    "user_name": username of the tweet's creator;
    "user_tag": user tag/handle of the tweet's creator;
    "user_pic": profile picture of the tweet's creator (local files only);
    "tweet_text": text of the tweet;
    All fields should be passed with string values.
    """)


def __load_default_settings(default_settings_format) -> GraphicSettings:
    if default_settings_format == DefaultFormats.LIGHT.value:
        return light_mode_settings
    elif default_settings_format == DefaultFormats.BLUE.value:
        return blue_mode_settings
    elif default_settings_format == DefaultFormats.DARK.value:
        return dark_mode_settings


def __choose_graphic_settings(
    graphic_settings: GraphicSettings,
    default_settings_format: DefaultFormats = DefaultFormats.CUSTOM.value
) -> None:
    """Based on the custom graphic settings and (lack of) default settings passed,
    choose the settings to be used.
    """
    # Validate that either custom or default settings were passed
    validate_settings_existence(
        graphic_settings, default_settings_format)

    # Validate and sanitize the default settings format chosen
    if default_settings_format != "":
        default_settings_format = validate_format_option(
            default_settings_format)

    # If the custom settings are just an empty dict, use the default settings format specified
    if (graphic_settings == dict()):
        chosen_settings = __load_default_settings(default_settings_format)

    # Otherwise, use the custom settingss
    else:
        chosen_settings = graphic_settings

    # Validate the chosen settings, independent of it being custom or default settings
    validate_g_settings(chosen_settings)

    return chosen_settings


def __draw_header(username, user_tag, user_pic, graphic_size, img, d_interface, coords, margin, font, color):
    """Draw the graphic header (username, user tag and, if specified, profile picture).
    """
    x = int(coords[0])
    y = int(coords[1])

    # If a profile picture was not specified, draw the username and user tag
    if user_pic == "":
        # Draw the username
        user_name = wrap(username, 38)
        for line in user_name:
            d_interface.text((x, y), line, font=font, fill=color)
            y += font.size + margin
        # Draw the user handle
        d_interface.text((x, y), user_tag, font=font, fill=color)
        y += int(font.size + margin * 1.5)

    # Otherwise, draw the profile picture additionally
    else:
        # Process the profile picture and draw it
        user_pic_processed = process_pic(graphic_size, user_pic)
        img.paste(user_pic_processed, (x, y), mask=user_pic_processed)
        # Due to the presence of the profile picture, the horizontal\
        # coordinate for the rest of the header is updated
        x = int(coords[0] + user_pic_processed.size[0] + margin)
        # Draw the username
        user_name = wrap(username, 19)
        for line in user_name:
            d_interface.text((x, y), line, font=font, fill=color)
            y += font.size + margin
        # Draw the user tag
        d_interface.text((x, y), user_tag, font=font, fill=color)
        y += int(font.size + margin * 1.5)

    # Return the current vertical coordinate
    return y


def __get_initial_coordinates(img_size, dimensions):
    """Calculate the initial X and Y coordinates at which to start drawing.
    """
    # Get header and tweet text dimensions
    header_width, header_height = dimensions["header"]
    text_width, text_height = dimensions["text"]

    # Horizontal coordinate to draw at (centered)
    x = (img_size[0] - text_width) // 2
    # Initial vertical coordinate to draw at (centered)
    content_height = header_height + text_height
    y = (img_size[1] - content_height) // 2

    return (x, y)


def create_tweet(
    tweet_info,
    graphic_settings,
    default_settings_format: DefaultFormats = DefaultFormats.CUSTOM.value,
    save_dir: Optional[str] = ""
) -> None:
    t_info = validate_tweet_info(tweet_info)
    # Use the graphic settings passed (either custom or default)
    g_settings = __choose_graphic_settings(
        graphic_settings, default_settings_format)

    user_name = tweet_info["user_name"]
    user_tag = tweet_info["user_tag"]
    tweet_text = tweet_info["tweet_text"]
    user_pic = tweet_info["user_pic"]

    font_family = g_settings["font_family"]
    font_size_text = g_settings["font_size_text"]
    font_size_header = g_settings["font_size_header"]
    # Set up the fonts based on settings
    font_header = ImageFont.truetype(
        font_family, font_size_header, encoding="utf-8")
    font_text = ImageFont.truetype(
        font_family, font_size_text, encoding="utf-8")

    # Size of the graphic
    img_size = g_settings["size"]
    # Vertical margin in between lines
    margin_bottom = g_settings["margin_bottom"]
    background_color = g_settings["color_scheme"][0]
    text_color = g_settings["color_scheme"][1]
    chars_limit = g_settings["wrap_limit"]

    # Dict with size of header and size of text
    content_dims = calculate_content_dimensions(
        tweet_info, g_settings)
    # Calculate the inital drawing coordinates
    x, y = __get_initial_coordinates(img_size, content_dims)

    # Create what will be the final image
    img = Image.new("RGB", (img_size[0], img_size[1]), color=background_color)
    # Create the drawing interface
    draw = ImageDraw.Draw(img)

    # Draw the header text (and update the vertical coordinate to be where\
    # the header finishes)
    y = __draw_header(user_name, user_tag, user_pic, img_size, img,
                      draw, (x, y), margin_bottom, font_header, text_color)

    # Split the tweet text into lines
    text_wrapped = wrap(tweet_text, chars_limit)
    # Draw the tweet text
    for line in text_wrapped:
        draw.text((x, y), line, font=font_text, fill=text_color)
        y += font_text.size + margin_bottom

    save_name = f"{tweet_info['tweet_name']}.png"
    save_name = path.join(save_dir, save_name)
    img.save(save_name)


def gen_tweets(
    file_name: str,
    graphic_settings: GraphicSettings,
    default_settings_format: DefaultFormats = DefaultFormats.CUSTOM.value,
    save_dir: Optional[str] = ""
) -> None:
    """Load tweets from a JSON file and create a graphic for each one.

    If `default_settings_format` is passed, `graphic_settings` must be an empty dictionary.
    """
    # Load the tweets from a JSON file as a list of tweet_info dictionaries
    json_tweets = get_ready_tweets(file_name)

    # Use the graphic settings passed (either custom or default)
    g_settings = __choose_graphic_settings(
        graphic_settings, default_settings_format)

    # Create a graphic for each quote
    for tweet in json_tweets:
        create_tweet(tweet, g_settings, save_dir=save_dir)
