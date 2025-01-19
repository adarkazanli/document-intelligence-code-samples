import pytest
from my_project.models.layout_analyzer import LayoutAnalyzer
from unittest.mock import patch, Mock
import os

def test_init_with_env_vars():
    with patch.dict(os.environ, {
        'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT': 'https://test.endpoint',
        'AZURE_DOCUMENT_INTELLIGENCE_KEY': 'test_key'
    }):
        analyzer = LayoutAnalyzer()
        assert analyzer.endpoint == 'https://test.endpoint'
        assert analyzer.key == 'test_key'

def test_init_with_params():
    analyzer = LayoutAnalyzer('https://custom.endpoint', 'custom_key')
    assert analyzer.endpoint == 'https://custom.endpoint'
    assert analyzer.key == 'custom_key'

def test_init_missing_credentials():
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError, match="Missing Azure credentials"):
            LayoutAnalyzer()

def test_format_polygon():
    polygon = [1, 2, 3, 4, 5, 6]
    expected = "[1, 2], [3, 4], [5, 6]"
    assert LayoutAnalyzer._format_polygon(polygon) == expected

def test_format_polygon_empty():
    assert LayoutAnalyzer._format_polygon(None) == "N/A"
    assert LayoutAnalyzer._format_polygon([]) == "N/A"

@pytest.mark.integration
def test_analyze_document():
    """Integration test requiring valid credentials and a test document."""
    if not os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'):
        pytest.skip("Skipping integration test: No Azure credentials")
    
    analyzer = LayoutAnalyzer()
    # You would need to provide a path to a test document
    with pytest.raises(FileNotFoundError):
        analyzer.analyze_document("nonexistent_file.pdf")

def test_analyze_and_save_results(tmp_path):
    """Test saving analysis results to a file."""
    analyzer = LayoutAnalyzer('https://test.endpoint', 'test_key')
    
    # Create a temporary PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.5")  # Minimal PDF content
    
    # Set up output path
    output_path = tmp_path / "analysis.txt"
    
    with patch('azure.ai.formrecognizer.DocumentAnalysisClient.begin_analyze_document'):
        analyzer.analyze_and_save_results(str(pdf_path), str(output_path))
        
    assert output_path.exists()
    content = output_path.read_text()
    assert "Analyzing layout from page" in content 