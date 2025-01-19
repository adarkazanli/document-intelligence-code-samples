import pytest
from pathlib import Path
from examples.visualize_analysis import LayoutVisualizer
import fitz

def test_parse_polygon():
    """Test polygon string parsing."""
    polygon_str = "[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]"
    expected = [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]
    result = LayoutVisualizer._parse_polygon(polygon_str)
    assert result == expected

def test_visualizer_missing_files():
    """Test error handling for missing files."""
    with pytest.raises(FileNotFoundError):
        LayoutVisualizer("nonexistent.pdf", "analysis.txt", "output.pdf")

def test_visualization(tmp_path):
    """Test the visualization process."""
    # Create a simple PDF
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.new_document()
    page = doc.new_page()
    doc.save(pdf_path)
    doc.close()

    # Create a simple analysis file
    analysis_path = tmp_path / "analysis.txt"
    analysis_content = """
    Analyzing layout from page #1
    Word 'Test' has confidence 0.99 within bounding polygon '[72.0, 72.0], [144.0, 72.0], [144.0, 96.0], [72.0, 96.0]'
    """
    analysis_path.write_text(analysis_content)

    # Set up output path
    output_path = tmp_path / "annotated.pdf"

    # Run visualization
    visualizer = LayoutVisualizer(str(pdf_path), str(analysis_path), str(output_path))
    visualizer.process_analysis()

    # Check that output file exists and is larger than input
    assert output_path.exists()
    assert output_path.stat().st_size > pdf_path.stat().st_size 