import tinycss2
import re
from cm_colors.core.cm_colors import CMColors

cmc = CMColors()

COLOR_PROPERTIES = {"color", "background-color"}

CSS_NAMED_COLORS = {
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgreen': '#006400',
    'darkgrey': '#a9a9a9',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkslategrey': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dimgrey': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'grey': '#808080',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgray': '#d3d3d3',
    'lightgreen': '#90ee90',
    'lightgrey': '#d3d3d3',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightslategrey': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370db',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#db7093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'rebeccapurple': '#663399',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'slategrey': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32'
}


def hex_match(value: str) -> str | None:
    """
    Extract and validate hex color string from a CSS value.
    Returns the hex color string if valid, otherwise returns None.
    """
    regex = r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b"
    match = re.search(regex, value)
    return match.group(0) if match else None


def named_match(value: str) -> str | None:
    """
    Extract and validate named color string from a CSS value.
    Returns the name color string if valid, otherwise returns None.
    """
    regex = r"\b[a-zA-Z]+\b"
    match = re.search(regex, value)
    if match and match.group(0).lower() not in ["rgb", "rgba"]:
        return match.group(0)
    return None


def rgb_match(value: str) -> str | None:
    """
    Extract and validate RGB color string from a CSS value.
    Returns the RGB color string if valid, otherwise returns None.
    """
    regex = r"rgba?\(\s*[^)]+\)"
    match = re.search(regex, value)
    if not match:
        return None

    rgb_str = match.group(0)
    components = re.findall(r"[\d.]+", rgb_str)

    if rgb_str.startswith("rgb(") and len(components) == 3:
        # Ensure RGB values are within range
        try:
            r, g, b = map(int, components)
            if all(0 <= x <= 255 for x in [r, g, b]):
                return f"rgb({r}, {g}, {b})"
        except ValueError:
            return None

    elif rgb_str.startswith("rgba(") and len(components) == 4:
        # Ensure RGBA values are within range
        try:
            r, g, b = map(int, components[:3])
            a = float(components[3])
            if all(0 <= x <= 255 for x in [r, g, b]) and 0 <= a <= 1:
                return f"rgba({r}, {g}, {b}, {a})"
        except ValueError:
            return None

    return None


def parse_color_value(value: str) -> str | None:
    """
    Extract and validate a color string from a CSS value.
    Returns the color string if valid (HEX, named, or RGB), otherwise returns None.
    """
    return hex_match(value) or named_match(value) or rgb_match(value)


def parse_rule_colors(rule) -> dict | None:
    """
    Parse a CSS rule and extract color declarations.
    Returns a dictionary with 'selector', 'text', 'background', and 'line' keys.
    """
    if rule.type != "qualified-rule":
        return None

    selector = tinycss2.serialize(rule.prelude).strip()
    declarations = tinycss2.parse_declaration_list(rule.content)

    color = None
    background = None

    for declaration in declarations:
        if declaration.type != "declaration":
            continue

        property_name = declaration.lower_name
        property_value = tinycss2.serialize(declaration.value).strip()
        extracted_color = parse_color_value(property_value)

        if property_name == "color":
            color = extracted_color
        elif property_name == "background-color":
            background = extracted_color

    if color or background:
        return {
            "selector": selector,
            "text": color,
            "background": background,
            "line": rule.source_line,
        }

    return None


def extract_colors(filename: str) -> list[dict]:
    """
    Parse a CSS file and extract selectors with color/background-color info.
    Returns a list of dictionaries with 'selector', 'text', 'background', and 'line' keys.
    """
    with open(filename, "r", encoding="utf-8") as file:
        css_content = file.read()

    parsed_stylesheet = tinycss2.parse_stylesheet(
        css_content, skip_comments=True, skip_whitespace=True
    )
    extracted_colors = []

    for rule in parsed_stylesheet:
        color_info = parse_rule_colors(rule)
        if color_info:
            extracted_colors.append(color_info)

    return extracted_colors

# code below this comment may require cleaning, improvement, and optimization. For now, it works and achieves the goal [kylowren85]

def process_colors(input_file: str) -> list[dict]:
    processed_colors = []
    for color_pair in extract_colors(input_file):
        processed_dict = {
            "selector": color_pair["selector"],
            "text": color_pair["text"],
            "background": color_pair["background"],
            "line": color_pair["line"],
            "was_accessible": "Insufficient Data"
        }
        if color_pair["text"] != None and color_pair["background"] != None:
            if not color_pair["text"].startswith("#") and not color_pair["text"].startswith("rgb"):
                color_pair["text"] = CSS_NAMED_COLORS[color_pair["text"]]
            if not color_pair["background"].startswith("#") and not color_pair["background"].startswith("rgb"):
                color_pair["background"] = CSS_NAMED_COLORS[color_pair["background"]]
            processed_text_color, was_accessible = cmc.tune_colors(text_rgb=color_pair["text"], bg_rgb=color_pair["background"])
            processed_dict = {
                "selector": color_pair["selector"],
                "text": processed_text_color,
                "background": color_pair["background"],
                "line": color_pair["line"],
                "was_accessible": was_accessible,
            }
        processed_colors.append(processed_dict)
    return processed_colors
    

def construct_css_block(css_block: dict) -> str:
    if css_block["selector"] != None and css_block["text"] != None and css_block["background"] != None:
        return f"{css_block['selector']} {{\n    color: {css_block['text']};\n    background-color: {css_block['background']};\n    /* Was the color pair Accessible? {css_block['was_accessible']} */\n}}\n"
    elif css_block["selector"] != None and css_block["text"] != None:
        return f"{css_block['selector']} {{\n    color: {css_block['text']};\n    /* Was the color pair Accessible? {css_block['was_accessible']} */\n}}\n"
    elif css_block["selector"] != None and css_block["background"] != None:
        return f"{css_block['selector']} {{\n    background-color: {css_block['background']};\n    /* Was the color pair Accessible? {css_block['was_accessible']} */\n}}\n"

def write_css(processed_colors: list[dict], output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as file:
        for css_block in processed_colors:
            file.write(construct_css_block(css_block))
            file.write("\n")

if __name__ == "__main__":
    write_css(process_colors("test.css"), "output.css")