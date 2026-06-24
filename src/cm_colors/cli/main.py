import json as _json
import sys
import click
import tinycss2
from tinycss2.ast import QualifiedRule, Declaration, AtRule
from pathlib import Path
from rich.console import Console
from rich.table import Table
from cm_colors.core.colors import Color, ColorPair
from cm_colors.core.contrast import calculate_contrast_ratio, get_contrast_level, get_wcag_level

from cm_colors.cli.html_report import generate_report

console = Console()


def get_css_files(path):
    path = Path(path)
    if path.is_file():
        if path.suffix == ".css":
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


def collect_variables(rules):
    variables = {}
    for rule in rules:
        if isinstance(rule, QualifiedRule):
            selector = serialize_prelude(rule.prelude)
            if selector in (":root", "html"):
                declarations = tinycss2.parse_declaration_list(
                    rule.content, skip_whitespace=True, skip_comments=True
                )
                for decl in declarations:
                    if isinstance(decl, Declaration) and decl.name.startswith("--"):
                        variables[decl.name] = {
                            "decl": decl,
                            "value": tinycss2.serialize(decl.value).strip(),
                        }
    return variables


def resolve_variable(value_str, variables, visited=None):
    if visited is None:
        visited = set()

    if not value_str or "var(" not in value_str:
        return value_str

    import re

    var_pattern = re.compile(r"var\((--[\w-]+)(?:\s*,\s*(.*))?\)")
    match = var_pattern.search(value_str)

    if not match:
        return value_str

    var_name = match.group(1)
    fallback = match.group(2)

    if var_name in visited:
        return fallback

    visited.add(var_name)

    if var_name in variables:
        resolved = resolve_variable(variables[var_name]["value"], variables, visited)
        if resolved:
            return resolved

    if fallback:
        return resolve_variable(fallback, variables, visited)

    return None


def process_nodes_recursive(
    node_list,
    default_bg,
    stats,
    file_path,
    variables=None,
    mode=1,
    premium=False,
):
    if variables is None:
        variables = {}

    for node in node_list:
        if isinstance(node, QualifiedRule):
            declarations = tinycss2.parse_declaration_list(
                node.content, skip_whitespace=False, skip_comments=False
            )
            valid_decls = [d for d in declarations if isinstance(d, Declaration)]

            modified = False
            color_decl = None
            bg_decl = None

            for decl in valid_decls:
                if decl.name == "color":
                    color_decl = decl
                elif decl.name == "background-color":
                    bg_decl = decl

            if color_decl:
                raw_text_color = extract_color_from_decl(color_decl)
                raw_bg_color = (
                    extract_color_from_decl(bg_decl) if bg_decl else default_bg
                )

                text_color_str = (
                    resolve_variable(raw_text_color, variables) or raw_text_color
                )
                bg_color_str = resolve_variable(raw_bg_color, variables) or raw_bg_color

                selector = serialize_prelude(node.prelude)

                try:
                    pair = ColorPair(text_color_str, bg_color_str)
                    if not pair.is_valid:
                        stats["failed"] += 1
                        stats["failed_details"].append(
                            {
                                "file": file_path.name,
                                "selector": selector,
                                "text": text_color_str,
                                "bg": bg_color_str,
                                "reason": f"Invalid colors: {', '.join(pair.errors)}",
                            }
                        )
                    else:
                        target_ratio = 7.0 if premium else 4.5
                        contrast = calculate_contrast_ratio(pair.text.rgb, pair.bg.rgb)

                        if contrast >= target_ratio:
                            stats["accessible"] += 1
                        else:
                            original_level = get_wcag_level(
                                pair.text.rgb, pair.bg.rgb, large=False
                            )
                            tuned_rgb, is_accessible = pair.make_readable(
                                mode=mode, very_readable=premium
                            )

                            if is_accessible:
                                stats["tuned"] += 1

                                if "var(" in raw_text_color:
                                    import re

                                    var_match = re.search(
                                        r"var\((--[\w-]+)\)", raw_text_color
                                    )
                                    if var_match:
                                        var_name = var_match.group(1)
                                        if var_name in variables:
                                            var_def = variables[var_name]
                                            update_decl_value(
                                                var_def["decl"], tuned_rgb
                                            )
                                            var_def["value"] = tuned_rgb
                                else:
                                    update_decl_value(color_decl, tuned_rgb)
                                    modified = True

                                new_pair = ColorPair(tuned_rgb, bg_color_str)
                                new_level = get_wcag_level(
                                    new_pair.text.rgb,
                                    new_pair.bg.rgb,
                                    large=False,
                                )

                                stats["fixed_details"].append(
                                    {
                                        "file": file_path.name,
                                        "selector": selector,
                                        "bg": bg_color_str,
                                        "original_text": text_color_str,
                                        "tuned_text": tuned_rgb,
                                        "original_level": original_level,
                                        "new_level": new_level,
                                    }
                                )
                            else:
                                stats["failed"] += 1
                                stats["failed_details"].append(
                                    {
                                        "file": file_path.name,
                                        "selector": selector,
                                        "text": text_color_str,
                                        "bg": bg_color_str,
                                        "contrast": contrast,
                                        "reason": "Could not tune without too many changes",
                                    }
                                )
                except Exception as e:
                    stats["failed"] += 1
                    stats["failed_details"].append(
                        {
                            "file": file_path.name,
                            "selector": selector,
                            "text": text_color_str,
                            "bg": bg_color_str,
                            "reason": str(e),
                        }
                    )

            if modified:
                new_content_str = tinycss2.serialize(declarations)
                node.content = tinycss2.parse_component_value_list(new_content_str)

        elif isinstance(node, AtRule):
            if node.lower_at_keyword in ("media", "supports") and node.content:
                nested_rules = tinycss2.parse_rule_list(
                    node.content, skip_whitespace=False, skip_comments=False
                )
                process_nodes_recursive(
                    nested_rules,
                    default_bg,
                    stats,
                    file_path,
                    variables,
                    mode=mode,
                    premium=premium,
                )

                nested_css = tinycss2.serialize(nested_rules)
                new_content = tinycss2.parse_component_value_list(nested_css)
                node.content = new_content


def _check_pair(fg_str, bg_str, large):
    fg_color = Color(fg_str)
    bg_color = Color(bg_str)
    if not fg_color.is_valid or not bg_color.is_valid:
        errors = []
        if not fg_color.is_valid:
            errors.append(f"fg: {fg_color.error}")
        if not bg_color.is_valid:
            errors.append(f"bg: {bg_color.error}")
        return {"fg": fg_str, "bg": bg_str, "error": "; ".join(errors), "pass": False}
    ratio = calculate_contrast_ratio(fg_color.rgb, bg_color.rgb)
    level = get_contrast_level(ratio, large)
    return {
        "fg": fg_color.to_hex(),
        "bg": bg_color.to_hex(),
        "ratio": round(ratio, 2),
        "level": level,
        "pass": level != "FAIL",
        "large": large,
    }


@click.group()
def cli():
    """CM-Colors: Color accessibility toolkit."""
    pass


def _fix_pair_result(fg_str, bg_str, large, mode, very_readable):
    fg_color = Color(fg_str)
    bg_color = Color(bg_str)
    if not fg_color.is_valid or not bg_color.is_valid:
        errors = []
        if not fg_color.is_valid:
            errors.append(f"fg: {fg_color.error}")
        if not bg_color.is_valid:
            errors.append(f"bg: {bg_color.error}")
        return {"fg": fg_str, "bg": bg_str, "error": "; ".join(errors), "success": False}
    pair = ColorPair(fg_str, bg_str, large_text=large)
    fixed, success = pair.make_readable(mode=mode, very_readable=very_readable)
    ratio = calculate_contrast_ratio(Color(fixed).rgb, bg_color.rgb)
    level = get_contrast_level(ratio, large)
    return {
        "fg": fg_color.to_hex(),
        "bg": bg_color.to_hex(),
        "fixed": fixed,
        "ratio": round(ratio, 2),
        "level": level,
        "success": success,
    }


def _pairs_from_file(path):
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or (line.startswith("#") and len(line) > 1 and not line[1].isalnum()):
                continue
            parts = line.split()
            if len(parts) >= 2:
                pairs.append((parts[0], parts[1]))
            else:
                console.print(f"[yellow]Skipped malformed line:[/yellow] {line}")
    return pairs


def _run_css_fix(path, default_bg, mode, very_readable):
    """Inner CSS-file fix logic, returns stats dict."""
    stats = {
        "accessible": 0,
        "tuned": 0,
        "failed": 0,
        "failed_details": [],
        "fixed_details": [],
    }

    files = list(get_css_files(path))
    if not files:
        click.echo("No CSS files found.")
        return

    click.echo(f"Processing {len(files)} files...")

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                css_content = f.read()

            rules = tinycss2.parse_stylesheet(
                css_content, skip_whitespace=False, skip_comments=False
            )

            variables = {}
            rule_declarations_map = {}

            for rule in rules:
                if isinstance(rule, QualifiedRule):
                    selector = serialize_prelude(rule.prelude)
                    if selector in (":root", "html"):
                        decls = tinycss2.parse_declaration_list(
                            rule.content,
                            skip_whitespace=False,
                            skip_comments=False,
                        )
                        rule_declarations_map[id(rule)] = decls

                        for decl in decls:
                            if isinstance(decl, Declaration) and decl.name.startswith(
                                "--"
                            ):
                                variables[decl.name] = {
                                    "decl": decl,
                                    "value": tinycss2.serialize(decl.value).strip(),
                                    "rule": rule,
                                }

            process_nodes_recursive(
                rules,
                default_bg,
                stats,
                file_path,
                variables,
                mode=mode,
                premium=very_readable,
            )

            for rule in rules:
                if id(rule) in rule_declarations_map:
                    decls = rule_declarations_map[id(rule)]
                    new_content_str = tinycss2.serialize(decls)
                    rule.content = tinycss2.parse_component_value_list(new_content_str)

            output_filename = file_path.stem + "_cm" + file_path.suffix
            output_path = file_path.parent / output_filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(tinycss2.serialize(rules))

        except Exception as e:
            click.echo(f"Error processing {file_path}: {e}", err=True)
            import traceback

            traceback.print_exc()

    click.echo("")

    if stats["accessible"] > 0:
        click.secho(f"✓ {stats['accessible']} color pairs already readable", fg="cyan")

    if stats["tuned"] > 0:
        click.secho(
            f"✓ {stats['tuned']} color pairs adjusted for better readability",
            fg="green",
        )

    if stats["failed"] > 0:
        click.secho(f"✗ {stats['failed']} color pairs need your attention", fg="red")

    click.echo("")

    if stats["failed"] > 0:
        click.echo(f"Could not tune {stats['failed']} color pairs:")
        for fail in stats["failed_details"]:
            reason = fail.get("reason", "")
            click.echo(f"  {fail['file']} -> {fail['selector']}")

            if reason:
                if "Could not tune without too many changes" in reason:
                    reason = "Couldn't find a similar color that's easy to read"
                elif "Invalid colors" in reason:
                    reason = "These colors don't look right, check if it's a valid color please?"

                click.echo(f"    Reason: {reason}")
        click.echo("")

    if stats["tuned"] > 0:
        report_path = generate_report(stats["fixed_details"])
        click.echo(f"Report generated: {report_path}")
        click.echo("Have a chocolate 🍫")
    elif stats["failed"] == 0 and stats["tuned"] == 0:
        click.echo("No changes needed. ✨")
    else:
        click.echo("Some colors could not be automatically tuned.")


@cli.command()
@click.argument("fg_or_path", default=".", metavar="FG_OR_PATH")
@click.argument("bg", required=False, default=None)
@click.option(
    "--pairs",
    multiple=True,
    help='Inline pair as "FG BG" string. Repeat for bulk.',
)
@click.option(
    "--file",
    "pairs_file",
    type=click.Path(exists=True),
    default=None,
    help="File with one 'FG BG' pair per line.",
)
@click.option("--large", is_flag=True, default=False, help="Large-text WCAG thresholds.")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="JSON output (pair/bulk mode).",
)
@click.option("--default-bg", default="white", help="Default background for CSS mode.")
@click.option(
    "--mode",
    default=1,
    type=int,
    help="Optimization mode: 0 (Strict), 1 (Default), 2 (Relaxed).",
)
@click.option("--very-readable", is_flag=True, default=False, help="Aim for AAA (same as very_readable=True in the Python API).")
def fix(fg_or_path, bg, pairs, pairs_file, large, as_json, default_bg, mode, very_readable):
    """Fix color contrast — for a pair, a bulk list, or CSS files.

    Fix a single pair:

      cm-colors fix '#777777' '#ffffff'

    Fix multiple pairs inline (no file needed):

      cm-colors fix --pairs '#777 #fff' --pairs '#888 #000' --json

    Fix CSS files in a directory:

      cm-colors fix ./styles/
    """
    from pathlib import Path as _Path

    # --- pair / bulk mode ---
    if pairs or pairs_file or bg is not None:
        pairs_input = []

        if pairs_file:
            with open(pairs_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or (line.startswith("#") and len(line) > 1 and not line[1].isalnum()):
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        pairs_input.append((parts[0], parts[1]))
                    else:
                        console.print(f"[yellow]Skipped malformed line:[/yellow] {line}")

        for p in pairs:
            parts = p.split()
            if len(parts) >= 2:
                pairs_input.append((parts[0], parts[1]))
            else:
                console.print(f"[yellow]Skipped malformed --pairs value:[/yellow] {p}")

        if bg is not None:
            pairs_input.insert(0, (fg_or_path, bg))

        if not pairs_input:
            click.echo("No valid pairs provided. See --help.", err=True)
            sys.exit(2)

        results = [_fix_pair_result(f, b, large, mode, very_readable) for f, b in pairs_input]
        any_fail = any(not r["success"] for r in results)

        if as_json:
            if len(results) == 1:
                click.echo(_json.dumps(results[0], indent=2))
            else:
                total = len(results)
                succeeded = sum(1 for r in results if r["success"])
                click.echo(_json.dumps({
                    "results": results,
                    "summary": {"total": total, "fixed": succeeded, "failed": total - succeeded},
                }, indent=2))
        else:
            table = Table(show_header=True, header_style="bold")
            table.add_column("FG", style="dim")
            table.add_column("BG", style="dim")
            table.add_column("Fixed")
            table.add_column("Ratio", justify="right")
            table.add_column("Level", justify="center")
            table.add_column("Status", justify="center")

            for r in results:
                if "error" in r:
                    table.add_row(r["fg"], r["bg"], "-", "-", "-", "[red]ERROR[/red]")
                else:
                    level_style = "green" if r["level"] == "AAA" else "yellow" if r["level"] == "AA" else "red"
                    status = "[green]FIXED[/green]" if r["success"] else "[red]FAIL[/red]"
                    table.add_row(
                        r["fg"], r["bg"], r["fixed"],
                        f"{r['ratio']:.2f}:1",
                        f"[{level_style}]{r['level']}[/{level_style}]",
                        status,
                    )

            console.print(table)

            if len(results) > 1:
                succeeded = sum(1 for r in results if r["success"])
                total = len(results)
                if any_fail:
                    console.print(f"[red]{total - succeeded} of {total} pairs could not be fixed.[/red]")
                else:
                    console.print(f"[green]All {total} pairs fixed.[/green]")

        sys.exit(1 if any_fail else 0)

    # --- CSS file mode ---
    path = fg_or_path
    if not _Path(path).exists():
        click.echo(f"Path '{path}' does not exist.", err=True)
        sys.exit(2)

    _run_css_fix(path, default_bg, mode, very_readable)


@cli.command()
@click.argument("fg", required=False)
@click.argument("bg", required=False)
@click.option("--pairs", multiple=True, help='Inline pair as "FG BG". Repeat for bulk.')
@click.option(
    "--file",
    "pairs_file",
    type=click.Path(exists=True),
    default=None,
    help="File with one 'FG BG' pair per line.",
)
@click.option("--large", is_flag=True, default=False, help="Large-text WCAG thresholds (AA>=3.0, AAA>=4.5).")
@click.option("--json", "as_json", is_flag=True, default=False, help="JSON output for agents and scripts.")
def contrast(fg, bg, pairs, pairs_file, large, as_json):
    """Check WCAG contrast ratio for a color pair or a bulk list.

    Single pair:

      cm-colors contrast '#777777' '#ffffff'

    Bulk inline (no file needed):

      cm-colors contrast --pairs '#777 #fff' --pairs '#888 #000' --json

    Bulk from file:

      cm-colors contrast --file pairs.txt --json

    Exit code 0 = all pass, 1 = any fail.
    """
    pairs_input = []

    if fg and bg:
        pairs_input.append((fg, bg))

    for p in pairs:
        parts = p.split()
        if len(parts) >= 2:
            pairs_input.append((parts[0], parts[1]))
        else:
            console.print(f"[yellow]Skipped malformed --pairs value:[/yellow] {p}")

    if pairs_file:
        pairs_input.extend(_pairs_from_file(pairs_file))

    if not pairs_input:
        click.echo("Provide FG and BG arguments, or use --pairs/--file. See --help.", err=True)
        sys.exit(2)

    results = [_check_pair(f, b, large) for f, b in pairs_input]
    any_fail = any(not r["pass"] for r in results)

    if as_json:
        if len(results) == 1:
            click.echo(_json.dumps(results[0], indent=2))
        else:
            total = len(results)
            passed = sum(1 for r in results if r["pass"])
            click.echo(
                _json.dumps(
                    {
                        "results": results,
                        "summary": {
                            "total": total,
                            "pass": passed,
                            "fail": total - passed,
                        },
                    },
                    indent=2,
                )
            )
    else:
        table = Table(show_header=True, header_style="bold")
        table.add_column("FG", style="dim")
        table.add_column("BG", style="dim")
        table.add_column("Ratio", justify="right")
        table.add_column("Level", justify="center")
        table.add_column("Status", justify="center")

        for r in results:
            if "error" in r:
                table.add_row(r["fg"], r["bg"], "-", "-", "[red]ERROR[/red]")
            else:
                level_style = (
                    "green" if r["level"] == "AAA" else
                    "yellow" if r["level"] == "AA" else
                    "red"
                )
                status = "[green]PASS[/green]" if r["pass"] else "[red]FAIL[/red]"
                table.add_row(
                    r["fg"],
                    r["bg"],
                    f"{r['ratio']:.2f}:1",
                    f"[{level_style}]{r['level']}[/{level_style}]",
                    status,
                )

        console.print(table)

        if len(results) > 1:
            passed = sum(1 for r in results if r["pass"])
            total = len(results)
            if any_fail:
                console.print(f"[red]{total - passed} of {total} pairs failed.[/red]")
            else:
                console.print(f"[green]All {total} pairs passed.[/green]")

    sys.exit(1 if any_fail else 0)


# ponytail: tests import `main` expecting the fix command; entry point uses `cli`
main = fix

if __name__ == "__main__":
    cli()
