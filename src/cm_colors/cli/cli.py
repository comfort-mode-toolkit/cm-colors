import typer # typer is the python package that faciliates cli creation. Refer `https://typer.tiangolo.com/`
from typing_extensions import Annotated
import cm_colors.cli.css_parser as cm_parser

# main app instance, will be used in setup.py to act as console script entry point.
# console script entry point is what helps in achieving `cm-colors` command with just `pip install cm-colors`.
app = typer.Typer()

# Register "process" command into the app instance which executes process_and_output function, with the defined arguments and options.
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


# A usless, pass, callback funtion to prevent typer from assuming the only command, process, to get executed without explicitly mentioning process command
# For eg. without this callback, `cm-colors ./input.css` would automatically run process command as its the only command, typer feature it is.
# We want `cm-colors ./input.css` to fail, mentioning absence of command name.
# hence, this callback function makes, `cm-colors process ./input.css` the correct usage despite `process` being the only command defined.
# Multiple commands when defined, will render this explicit callback function of no use in this context, may or may not be removed depending on needs.
# For now, with just one command defined, and as per desire, callback exists.
# According to typer, by default, callback function is called when it doesnt know what to do, that is, in our case, no command name is given, so it fails stating user to enter a command.

# TL;DR ---> https://typer.tiangolo.com/tutorial/commands/one-or-multiple/#using-the-callback-to-document

@app.callback()
def callback():
    pass