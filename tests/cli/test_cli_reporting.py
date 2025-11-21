import pytest
from click.testing import CliRunner
from cm_colors.cli.main import main
import os

@pytest.fixture
def runner():
    return CliRunner()

def test_console_report_stats(runner):
    """Test console output stats."""
    with runner.isolated_filesystem():
        css = """
        .good { color: black; background-color: white; }
        .bad { color: #ccc; background-color: white; }
        """
        with open("test.css", "w") as f:
            f.write(css)
        
        result = runner.invoke(main, ["test.css"])
        assert "1 already accessible" in result.output
        assert "Could not tune 1 pairs" in result.output
        assert "test.css -> .bad" in result.output
        assert "1 failed tuning" in result.output

def test_html_report_generation(runner):
    """Test that HTML report is generated when fixes occur."""
    with runner.isolated_filesystem():
        # Fixable pair
        css = ".fixable { color: #777; background-color: white; }"
        with open("test.css", "w") as f:
            f.write(css)
        
        result = runner.invoke(main, ["test.css"])
        assert "Report generated:" in result.output
        assert "cm_colors_report.html" in result.output
        
        assert os.path.exists("cm_colors_report.html")
        with open("cm_colors_report.html", "r") as f:
            content = f.read()
            assert "CM-Colors Report" in content
            assert ".fixable" in content
            assert "Before" in content
            assert "After" in content
            assert "Yeseva One" in content # Font check

def test_no_html_report_if_no_fixes(runner):
    """Test that HTML report is NOT generated if no fixes occur."""
    with runner.isolated_filesystem():
        # Only good and bad (unfixable) pairs
        css = """
        .good { color: black; background-color: white; }
        .bad { color: #ccc; background-color: white; }
        """
        with open("test.css", "w") as f:
            f.write(css)
        
        result = runner.invoke(main, ["test.css"])
        assert "Report generated" not in result.output
        assert not os.path.exists("cm_colors_report.html")
