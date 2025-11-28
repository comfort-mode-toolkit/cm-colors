import os
import pytest
from click.testing import CliRunner
from cm_colors.cli.main import main

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_no_args_default_path(runner):
    """Test running CLI with no arguments uses current directory."""
    with runner.isolated_filesystem():
        # Create a dummy css file
        with open("test.css", "w") as f:
            f.write("body { color: black; background-color: white; }")
        
        result = runner.invoke(main)
        assert result.exit_code == 0
        assert "Processing 1 files..." in result.output

def test_cli_invalid_path(runner):
    """Test running CLI with a non-existent path."""
    result = runner.invoke(main, ["non_existent_path"])
    assert result.exit_code != 0
    assert "Path 'non_existent_path' does not exist" in result.output

def test_cli_valid_file_path(runner):
    """Test running CLI with a specific file path."""
    with runner.isolated_filesystem():
        with open("test.css", "w") as f:
            f.write("body { color: black; background-color: white; }")
        
        result = runner.invoke(main, ["test.css"])
        assert result.exit_code == 0
        assert "Processing 1 files..." in result.output

def test_cli_valid_directory_path(runner):
    """Test running CLI with a directory path."""
    with runner.isolated_filesystem():
        os.mkdir("styles")
        with open("styles/test.css", "w") as f:
            f.write("body { color: black; background-color: white; }")
        
        result = runner.invoke(main, ["styles"])
        assert result.exit_code == 0
        assert "Processing 1 files..." in result.output

def test_cli_default_bg_option(runner):
    """Test --default-bg option."""
    with runner.isolated_filesystem():
        with open("test.css", "w") as f:
            # Implicit background, should use default-bg
            f.write("body { color: #ccc; }") 
        
        # Run with default-bg black (so #ccc is accessible)
        result = runner.invoke(main, ["test.css", "--default-bg", "black"])
        assert result.exit_code == 0
        assert "1 color pairs already readable" in result.output
