import yaml

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def process_config(config_path):
    """
    Process YAML configuration into brand palette format.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        List of color pair dictionaries ready for accessibility processing
        
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    root = config['root']
    mapping = config['mapping']['color']

    brand_palette = []

    for category, pairs in mapping.items():
        for idx, pair in enumerate(pairs):
            text_var = pair['text']
            bg_var = pair['bg']

            text_color = root.get(text_var)
            bg_color = root.get(bg_var)

            if isinstance(text_color, str) and text_color.startswith('#'):
                text_color = hex_to_rgb(text_color)
            if isinstance(bg_color, str) and bg_color.startswith('#'):
                bg_color = hex_to_rgb(bg_color)

            entry = {
                'text': {
                    'color': text_color,
                    'default': f'--text-{category}-{idx}',
                    'custom': text_var
                },
                'bg': {
                    'color': bg_color,
                    'default': f'--bg-{category}-{idx}',
                    'custom': bg_var
                },
                'type': category.replace('_text', '')  # 'normal' or 'large'
            }
            brand_palette.append(entry)
    return brand_palette

# Example usage:
# palette = process_palette('brand_config.yml')
# print(palette)