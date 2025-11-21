import pytest
from click.testing import CliRunner
from cm_colors.cli.main import main
import os

@pytest.fixture
def runner():
    return CliRunner()

def test_process_accessible_pair(runner):
    """Test that accessible pairs are left alone."""
    with runner.isolated_filesystem():
        css = "body { color: black; background-color: white; }"
        with open("test.css", "w") as f:
            f.write(css)
        
        result = runner.invoke(main, ["test.css"])
        assert result.exit_code == 0
        assert "1 already accessible" in result.output
        assert "tuned" not in result.output
        
        # Check output file content (should be same logic, maybe reformatted)
        # But wait, if no changes, does it write the file? 
        # The code writes the file regardless of changes currently.
        assert os.path.exists("test_cm.css")
        with open("test_cm.css", "r") as f:
            content = f.read()
            assert "color: black" in content or "color:  black" in content

def test_process_fixable_pair(runner):
    """Test that fixable pairs are tuned."""
    with runner.isolated_filesystem():
        # #777 on white is ~4.47, just below 4.5. Should be tuned to something darker.
        css = ".fixable { color: #777; background-color: white; }"
        with open("test.css", "w") as f:
            f.write(css)
        
        result = runner.invoke(main, ["test.css"])
        assert result.exit_code == 0
        assert "1 tuned" in result.output
        
        with open("test_cm.css", "r") as f:
            content = f.read()
            # Should not be #777 anymore
            assert "#777" not in content
            # Should be an rgb string
            assert "rgb(" in content

def test_process_unfixable_pair(runner):
    """Test that unfixable pairs are reported."""
    with runner.isolated_filesystem():
        # #ccc on white is ~1.6, very low.
        css = ".bad { color: #ccc; background-color: white; }"
        with open("test.css", "w") as f:
            f.write(css)
        
        result = runner.invoke(main, ["test.css"])
        assert result.exit_code == 0
        assert "Could not tune 1 pairs" in result.output
        assert ".bad" in result.output
        assert "#ccc on white" in result.output
        assert "1 failed tuning" in result.output

def test_process_nested_rules(runner):
    """Test processing of nested rules (media queries)."""
    with runner.isolated_filesystem():
        css = "@media (min-width: 600px) { .nested { color: #777; background-color: white; } }"
        with open("test.css", "w") as f:
            f.write(css)
        
        result = runner.invoke(main, ["test.css"])
        assert result.exit_code == 0
        assert "1 tuned" in result.output
        
        with open("test_cm.css", "r") as f:
            content = f.read()
            assert "@media" in content
            assert "rgb(" in content

def test_process_implicit_background(runner):
    """Test using default background when not specified."""
    with runner.isolated_filesystem():
        css = ".implicit { color: #777; }"
        with open("test.css", "w") as f:
            f.write(css)
        
        # Default bg is white, so #777 should be fixed
        result = runner.invoke(main, ["test.css"])
        assert result.exit_code == 0
        assert "1 tuned" in result.output
