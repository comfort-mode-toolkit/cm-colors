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
        assert "1 color pairs already readable" in result.output
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
        assert "1 color pairs adjusted for better readability" in result.output
        
        with open("test_cm.css", "r") as f:
            content = f.read()
            # Should not be #777 anymore
            assert "#777" not in content
            # Should be a hex string now (format consistency)
            assert "#" in content
            assert "rgb(" not in content

def test_process_unfixable_pair(runner):
    """Test that unfixable pairs are reported."""
    with runner.isolated_filesystem():
        # #ccc on white is fixable in default mode (recursive).
        # We need a pair that is truly unfixable or force strict mode.
        # Since CLI uses default mode (1), let's use a pair that fails even in recursive mode.
        # Or we can check that #ccc IS fixed now.
        
        # 1. Verify #ccc is fixed
        css_ccc = ".fixed { color: #ccc; background-color: white; }"
        with open("test_ccc.css", "w") as f:
            f.write(css_ccc)
        result_ccc = runner.invoke(main, ["test_ccc.css"])
        assert result_ccc.exit_code == 0
        assert "1 color pairs adjusted for better readability" in result_ccc.output
        
        # 2. Try a truly unfixable pair? 
        # In recursive mode, it tries very hard. 
        # Maybe we can't easily find one without strict mode.
        # But the test intent was "unfixable pairs are reported".
        # If we can't find one, we should skip this part or mock it.
        # Let's try to mock check_and_fix_contrast to return failure to test the reporting logic.
        pass # Logic moved to separate test or we accept it's hard to fail now.

def test_reporting_logic_with_mock(runner):
    """Test reporting logic by mocking a failure."""
    from unittest.mock import patch
    with runner.isolated_filesystem():
        css = ".bad { color: #ccc; background-color: white; }"
        with open("test.css", "w") as f:
            f.write(css)
            
        with patch('cm_colors.core.optimisation.check_and_fix_contrast') as mock_fix:
            # Simulate failure
            mock_fix.return_value = ("#ccc", False) 
            
            result = runner.invoke(main, ["test.css"])
            assert result.exit_code == 0
            assert "Could not tune 1 color pairs" in result.output
            assert ".bad" in result.output
            assert "1 color pairs need your attention" in result.output

def test_process_nested_rules(runner):
    """Test processing of nested rules (media queries)."""
    with runner.isolated_filesystem():
        css = "@media (min-width: 600px) { .nested { color: #777; background-color: white; } }"
        with open("test.css", "w") as f:
            f.write(css)
        
        result = runner.invoke(main, ["test.css"])
        assert result.exit_code == 0
        assert "1 color pairs adjusted for better readability" in result.output
        
        with open("test_cm.css", "r") as f:
            content = f.read()
            assert "@media" in content
            # Should be hex now
            assert "#" in content
            assert "rgb(" not in content

def test_process_implicit_background(runner):
    """Test using default background when not specified."""
    with runner.isolated_filesystem():
        css = ".implicit { color: #777; }"
        with open("test.css", "w") as f:
            f.write(css)
        
        # Default bg is white, so #777 should be fixed
        result = runner.invoke(main, ["test.css"])
        assert result.exit_code == 0
        assert "1 color pairs adjusted for better readability" in result.output
