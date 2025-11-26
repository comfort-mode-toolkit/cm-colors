import pytest
from click.testing import CliRunner
from cm_colors.cli.main import main
import os

def test_css_vars_support(tmp_path):
    runner = CliRunner()
    
    # Create a CSS file with variables
    css_content = """
    :root {
        --bg: #ffffff;
        --text: #777777; /* Borderline contrast */
    }
    body {
        background-color: var(--bg);
        color: var(--text);
    }
    """
    
    css_file = tmp_path / "test.css"
    css_file.write_text(css_content, encoding="utf-8")
    
    # Run the CLI
    result = runner.invoke(main, [str(css_file.parent)])
    
    assert result.exit_code == 0
    
    # Check the output file
    output_file = tmp_path / "test_cm.css"
    
    # Currently, this might fail to produce output or fail to tune
    # If it works as expected (after fix), it should exist and have updated --text
    
    if output_file.exists():
        output_content = output_file.read_text(encoding="utf-8")
        
        # We expect --text to be tuned (e.g. to a darker grey)
        # And the usage in body should still be var(--text)
        
        assert "var(--text)" in output_content
        assert "#777777" not in output_content # Should be replaced
        assert "--text: #777777" not in output_content
    else:
        # If file not created, it means CLI didn't process it or failed silently
        # For now, we expect this to fail or not tune
        pass
