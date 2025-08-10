import tinycss2
import re
from cm_colors.core.cm_colors import CMColors
from cm_colors.core.named_colors import CSS_NAMED_COLORS

cmc = CMColors()

COLOR_PROPERTIES = {"color", "background-color"}

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