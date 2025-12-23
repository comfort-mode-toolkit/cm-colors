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


def test_cli_mode_option(runner):
    """Test that --mode option is accepted and affects processing."""
    with runner.isolated_filesystem():
        # #ccc on white is fixable in default mode (1) but might fail in strict mode (0)
        # Actually #ccc on white is 1.6:1. Strict mode (0) only allows small changes.
        # Let's use a color that is close to 4.5 but needs a small nudge, which strict mode can handle.
        # #767676 on white is 4.54 (accessible).
        # #777 on white is 4.47 (needs fix).

        css = ".strict-fail { color: #ccc; background-color: white; }"
        with open("test.css", "w") as f:
            f.write(css)

        # Mode 0 (Strict) should fail for #ccc (needs big change)
        result_strict = runner.invoke(main, ["test.css", "--mode", "0"])
        assert result_strict.exit_code == 0
        assert "Could not tune" in result_strict.output

        # Mode 1 (Default) should succeed
        result_default = runner.invoke(main, ["test.css", "--mode", "1"])
        assert result_default.exit_code == 0
        assert "1 color pairs adjusted" in result_default.output


def test_cli_premium_option(runner):
    """Test that --premium option is accepted and targets AAA."""
    with runner.isolated_filesystem():
        # #767676 on white is 4.54 (AA accessible).
        # With premium=False, it should be left alone.
        # With premium=True, it should be tuned to reach 7.0.

        css = ".aa-ok { color: #767676; background-color: white; }"
        with open("test.css", "w") as f:
            f.write(css)

        # Standard check
        result_std = runner.invoke(main, ["test.css"])
        assert result_std.exit_code == 0
        assert "1 color pairs already readable" in result_std.output

        # Premium check
        result_prem = runner.invoke(main, ["test.css", "--premium"])
        assert result_prem.exit_code == 0
        assert "1 color pairs adjusted" in result_prem.output
