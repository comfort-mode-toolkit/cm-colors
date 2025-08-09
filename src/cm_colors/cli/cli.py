import typer
from typing_extensions import Annotated
import cm_colors.cli.css_parser as cm_parser

app = typer.Typer()

@app.command("process")
def process_and_output(
    input_filepath: Annotated[str, typer.Argument(help="Specify the name of the input css file.")],
    output_filepath: Annotated[str, typer.Option("--output", "-o", help="Specifiy the name of the the output css file. Defaults to 'processed.css'")] = "processed.css"
):
    """
    Process a CSS file by tuning the colors based on Comfort Mode Standard and output the processed CSS.
    """
    processed_colors = cm_parser.process_colors(input_filepath)
    cm_parser.write_css(processed_colors, output_filepath)