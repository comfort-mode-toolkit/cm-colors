import click
import tinycss2
from tinycss2.ast import QualifiedRule, Declaration, AtRule
from pathlib import Path
from cm_colors.core.colors import ColorPair
from cm_colors.core.cm_colors import CMColors # Still needed for some utils if any, but ColorPair is main.

from cm_colors.cli.html_report import generate_report

def get_css_files(path):
    path = Path(path)
    if path.is_file():
        if path.suffix == '.css':
            yield path
    elif path.is_dir():
        for p in path.rglob("*.css"):
            if not p.name.endswith("_cm.css"):
                yield p

def serialize_prelude(prelude):
    return tinycss2.serialize(prelude).strip()

def extract_color_from_decl(decl):
    return tinycss2.serialize(decl.value).strip()

def update_decl_value(decl, new_value_str):
    decl.value = tinycss2.parse_component_value_list(new_value_str)

def process_nodes_recursive(node_list, default_bg, stats, file_path):
    for node in node_list:
        if isinstance(node, QualifiedRule):
            # Process declarations
            declarations = tinycss2.parse_declaration_list(node.content, skip_whitespace=True, skip_comments=True)
            valid_decls = [d for d in declarations if isinstance(d, Declaration)]
            
            modified = False
            color_decl = None
            bg_decl = None
            
            for decl in valid_decls:
                if decl.name == 'color':
                    color_decl = decl
                elif decl.name == 'background-color':
                    bg_decl = decl
            
            if color_decl:
                text_color_str = extract_color_from_decl(color_decl)
                bg_color_str = extract_color_from_decl(bg_decl) if bg_decl else default_bg
                selector = serialize_prelude(node.prelude)
                
                try:
                    pair = ColorPair(text_color_str, bg_color_str)
                    if not pair.is_valid:
                         stats['failed'] += 1
                         stats['failed_details'].append({
                            'file': file_path.name,
                            'selector': selector,
                            'text': text_color_str,
                            'bg': bg_color_str,
                            'reason': f"Invalid colors: {', '.join(pair.errors)}"
                         })
                    else:
                        if pair.contrast_ratio >= 4.5:
                            stats['accessible'] += 1
                        else:
                            original_level = pair.wcag_level
                            tuned_rgb, is_accessible = pair.tune_colors()
                            
                            if is_accessible:
                                stats['tuned'] += 1
                                update_decl_value(color_decl, tuned_rgb)
                                modified = True
                                
                                # Calculate new level
                                new_pair = ColorPair(tuned_rgb, bg_color_str)
                                new_level = new_pair.wcag_level
                                
                                stats['fixed_details'].append({
                                    'file': file_path.name,
                                    'selector': selector,
                                    'bg': bg_color_str,
                                    'original_text': text_color_str,
                                    'tuned_text': tuned_rgb,
                                    'original_level': original_level,
                                    'new_level': new_level
                                })
                            else:
                                stats['failed'] += 1
                                stats['failed_details'].append({
                                    'file': file_path.name,
                                    'selector': selector,
                                    'text': text_color_str,
                                    'bg': bg_color_str,
                                    'contrast': pair.contrast_ratio,
                                    'reason': "Could not tune without too much changes"
                                })
                except Exception as e:
                    stats['failed'] += 1
                    stats['failed_details'].append({
                        'file': file_path.name,
                        'selector': selector,
                        'text': text_color_str,
                        'bg': bg_color_str,
                        'reason': str(e)
                    })
            
            if modified or True:
                # Reconstruct content tokens
                new_content = []
                new_content.append(tinycss2.ast.WhitespaceToken(None, None, "\n  "))
                for i, decl in enumerate(valid_decls):
                    new_content.append(tinycss2.ast.IdentToken(None, None, decl.name))
                    new_content.append(tinycss2.ast.LiteralToken(None, None, ":"))
                    new_content.append(tinycss2.ast.WhitespaceToken(None, None, " "))
                    new_content.extend(decl.value)
                    new_content.append(tinycss2.ast.LiteralToken(None, None, ";"))
                    if i < len(valid_decls) - 1:
                        new_content.append(tinycss2.ast.WhitespaceToken(None, None, "\n  "))
                    else:
                        new_content.append(tinycss2.ast.WhitespaceToken(None, None, "\n"))
                node.content = new_content

        elif isinstance(node, AtRule):
            if node.lower_at_keyword in ('media', 'supports') and node.content:
                nested_rules = tinycss2.parse_rule_list(node.content, skip_whitespace=False, skip_comments=False)
                process_nodes_recursive(nested_rules, default_bg, stats, file_path)
                
                nested_css = tinycss2.serialize(nested_rules)
                new_content = tinycss2.parse_component_value_list(nested_css)
                node.content = new_content

@click.command()
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('--default-bg', default='white', help='Default background color if not specified.')
def main(path, default_bg):
    """CM-Colors CLI: Automatically tune color contrast in CSS files."""
    stats = {'accessible': 0, 'tuned': 0, 'failed': 0, 'failed_details': [], 'fixed_details': []}
    
    files = list(get_css_files(path))
    if not files:
        click.echo("No CSS files found.")
        return

    click.echo(f"Processing {len(files)} files...")
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            rules = tinycss2.parse_stylesheet(css_content, skip_whitespace=False, skip_comments=False)
            process_nodes_recursive(rules, default_bg, stats, file_path)
            
            output_filename = file_path.stem + "_cm" + file_path.suffix
            output_path = file_path.parent / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(tinycss2.serialize(rules))
                
        except Exception as e:
            click.echo(f"Error processing {file_path}: {e}", err=True)

    # Report
    click.echo("")

    # Summary List (moved to top)
    if stats['accessible'] > 0:
        click.secho(f"{stats['accessible']} pairs already accessible ( Great job on these )", fg='cyan')
    
    if stats['tuned'] > 0:
        click.secho(f"{stats['tuned']} pairs tuned", fg='green')
        
    if stats['failed'] > 0:
        click.secho(f"{stats['failed']} failed tuning (Please pick better starter colors for these)", fg='red')

    click.echo("")
    
    if stats['failed'] > 0:
        click.echo(f"Could not tune {stats['failed']} pairs:")
        for fail in stats['failed_details']:
            reason = fail.get('reason', '')
            contrast_info = f"(Contrast: {fail['contrast']:.2f})" if 'contrast' in fail else ""
            
            click.echo(f"  {fail['file']} -> {fail['selector']}")
            
            # Colorize the failing pair details in red
            pair_details = f"{fail['text']} on {fail['bg']}"
            click.secho(f"    {pair_details}", fg='red', nl=False)
            click.echo(f" {contrast_info}")
            
            if reason:
                click.echo(f"    Reason: {reason}")
        click.echo("")
    
    if stats['tuned'] > 0:
        report_path = generate_report(stats['fixed_details'])
        click.echo(f"Report generated: {report_path}")
        click.echo("Have a chocolate 🍫")
    elif stats['failed'] == 0 and stats['tuned'] == 0:
        click.echo("No changes needed. ✨")
    else:
        click.echo("Some colors could not be automatically tuned.")

if __name__ == "__main__":
    main()
