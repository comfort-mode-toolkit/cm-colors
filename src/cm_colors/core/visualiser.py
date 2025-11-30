from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.style import Style
from rich import box
import html
import os


def to_console(fg, bg, tuned_fg, original_level=None, new_level=None):
    """
    Prints a side-by-side comparison of the original and tuned colors to the console.
    """
    console = Console()

    # Helper to ensure color strings are safe for rich
    def safe_color(c):
        return str(c).replace(' ', '') if 'rgb' in str(c) else str(c)

    s_fg = safe_color(fg)
    s_bg = safe_color(bg)
    s_tuned_fg = safe_color(tuned_fg)

    def get_badge(level):
        if level == 'FAIL':
            return Text(' Not Readable ', style='white on red')
        elif level == 'AA' or level == 'AA Large':
            return Text(' Readable ', style='white on green')
        elif level == 'AAA' or level == 'AAA Large':
            return Text(' Very Readable ', style='white on green')
        return Text(f' {level} ', style='black on white')

    # Create main layout table
    main_table = Table(
        show_header=False, box=None, padding=0, collapse_padding=True
    )
    main_table.add_column('Original', ratio=1)
    main_table.add_column('Arrow', width=4, justify='center')
    main_table.add_column('Tuned', ratio=1)

    # Original Block with label above
    orig_badge = get_badge(original_level)
    original_text = Text('Sample Text', style=Style(color=s_fg, bgcolor=s_bg))

    original_content = Table.grid(padding=0, expand=True)
    original_content.add_column(justify='center')
    original_content.add_row(original_text)
    original_content.add_row(Text('\n'))
    original_content.add_row(Text(str(fg), style='dim'))
    original_content.add_row(Text('\n'))
    original_content.add_row(orig_badge)

    original_panel = Panel(
        original_content,
        style=Style(bgcolor=s_bg),
        padding=(1, 2),
        border_style='dim',
    )

    # Tuned Block with label above
    new_badge = get_badge(new_level)
    tuned_text = Text(
        'Sample Text', style=Style(color=s_tuned_fg, bgcolor=s_bg)
    )

    tuned_content = Table.grid(padding=0, expand=True)
    tuned_content.add_column(justify='center')
    tuned_content.add_row(tuned_text)
    tuned_content.add_row(Text('\n'))
    tuned_content.add_row(Text(str(tuned_fg), style='dim'))
    tuned_content.add_row(Text('\n'))
    tuned_content.add_row(new_badge)

    tuned_panel = Panel(
        tuned_content,
        style=Style(bgcolor=s_bg),
        padding=(1, 2),
        border_style='dim',
    )

    # Create label row
    label_table = Table(
        show_header=False, box=None, padding=0, collapse_padding=True
    )
    label_table.add_column('Original Label', ratio=1, justify='right')
    label_table.add_column('Arrow Space', width=4)
    label_table.add_column('Tuned Label', ratio=1, justify='right')
    label_table.add_row(
        Text('Before', style='bold'), '', Text('After', style='bold')
    )

    # Print label row then panels
    console.print(label_table)
    main_table.add_row(original_panel, '→', tuned_panel)
    console.print(main_table)


def _get_level_badge(level):
    if level == 'FAIL':
        return 'Not Readable', 'badge-fail'
    elif level == 'AA' or level == 'AA Large':
        return 'Readable', 'badge-pass'
    elif level == 'AAA' or level == 'AAA Large':
        return 'Very Readable', 'badge-pass'
    return level, 'badge-pass'


def to_html(
    fg,
    bg,
    tuned_fg,
    original_level,
    new_level,
    selector='Color Pair',
    file_path='Manual Check',
):
    """
    Returns an HTML string for a single pair card.
    """
    fg = html.escape(str(fg))
    bg = html.escape(str(bg))
    tuned_fg = html.escape(str(tuned_fg))

    orig_label, orig_class = _get_level_badge(original_level)
    new_label, new_class = _get_level_badge(new_level)

    bg_style = f'background-color: {bg};'
    orig_text_style = f'color: {fg};'
    tuned_text_style = f'color: {tuned_fg};'

    return f"""
    <div class="card">
        <div class="card-header">
            <div>
                <div class="selector">{html.escape(str(selector))}</div>
                <div class="file-info">{html.escape(str(file_path))}</div>
            </div>
        </div>
        
        <div class="comparison">
            <div class="color-box" style="{bg_style} {orig_text_style}">
                <span class="label">Before</span>
                <div class="sample-text">Sample Text</div>
                <div class="color-code">{fg}</div>
                <div class="badge {orig_class}">{orig_label}</div>
            </div>
            
            <div class="arrow">→</div>
            
            <div class="color-box" style="{bg_style} {tuned_text_style}">
                <span class="label">After</span>
                <div class="sample-text">Sample Text</div>
                <div class="color-code">{tuned_fg}</div>
                <div class="badge {new_class}">{new_label}</div>
            </div>
        </div>
    </div>
    """


def to_html_bulk(pairs, output_path='cm_colors_report.html'):
    """
    Generates a full HTML page for multiple pairs.
    pairs: list of dicts with keys: fg, bg, tuned_fg, original_level, new_level, selector, file
    """
    cards_html = ''
    if not pairs:
        cards_html = """
            <div class="card" style="text-align: center; padding: 50px;">
                <h3>No changes were needed!</h3>
                <p>All color pairs found were already accessible.</p>
            </div>
        """
    else:
        for pair in pairs:
            cards_html += to_html(
                pair['fg'],
                pair['bg'],
                pair['tuned_fg'],
                pair.get('original_level', 'FAIL'),
                pair.get('new_level', 'AA'),
                pair.get('selector', 'Color Pair'),
                pair.get('file', 'Manual Check'),
            )

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CM-Colors Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400;1,700&family=Yeseva+One&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #f9f9f9;
            --text-color: #333;
            --card-bg: #ffffff;
            --accent: #2c3e50;
        }}
        
        body {{
            font-family: 'Atkinson Hyperlegible', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }}
        
        h1, h2, h3 {{
            font-family: 'Yeseva One', serif;
            font-weight: 400;
            margin-top: 0;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 60px;
        }}
        
        h1 {{
            font-size: 3rem;
            color: var(--accent);
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            font-size: 1.2rem;
            opacity: 0.7;
        }}
        
        .container {{
            max_width: 900px;
            margin: 0 auto;
        }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 15px;
        }}
        
        .file-info {{
            font-size: 0.9rem;
            color: #666;
        }}
        
        .selector {{
            font-family: 'Atkinson Hyperlegible', monospace;
            font-weight: 700;
            font-size: 1.1rem;
            color: var(--accent);
        }}
        
        .comparison {{
            display: flex;
            gap: 20px;
            align-items: stretch;
        }}
        
        .color-box {{
            flex: 1;
            border-radius: 8px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            min-height: 120px;
            position: relative;
            border: 1px solid rgba(0,0,0,0.1);
        }}
        
        .label {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            opacity: 0.7;
            position: absolute;
            top: 10px;
            left: 10px;
        }}
        
        .sample-text {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .color-code {{
            font-family: monospace;
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .badge-fail {{
            background-color: #ffebee;
            color: #c62828;
        }}
        
        .badge-pass {{
            background-color: #e8f5e9;
            color: #2e7d32;
        }}
        
        .arrow {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: #ccc;
        }}
        
        footer {{
            text-align: center;
            margin-top: 60px;
            font-size: 0.9rem;
            color: #555555;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>CM-Colors Report</h1>
            <div class="subtitle">Readability Fixes</div>
        </header>
        
        <main>
            {cards_html}
        </main>
        
        <footer>
            Generated by CM-Colors
        </footer>
    </div>
</body>
</html>
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return os.path.abspath(output_path)
