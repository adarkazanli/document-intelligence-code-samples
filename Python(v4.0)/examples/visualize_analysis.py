#!/usr/bin/env python3
"""
Script to visualize layout analysis results by drawing polygons on the PDF.
"""

import fitz  # PyMuPDF
import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict

class LayoutVisualizer:
    """Class for visualizing layout analysis results on PDF documents."""

    # Color scheme for different element types
    COLORS = {
        'word': (1, 0, 0),        # Red
        'line': (0, 0, 1),        # Blue
        'paragraph': (0, 0.7, 0), # Green
        'table': (0.7, 0, 0.7),   # Purple
        'cell': (1, 0.5, 0),      # Orange
        'selection_mark': (0, 0.7, 0.7)  # Teal
    }

    def __init__(self, pdf_path: str, analysis_path: str, output_path: str):
        """Initialize the visualizer with input and output paths."""
        self.pdf_path = Path(pdf_path)
        self.analysis_path = Path(analysis_path)
        self.output_path = Path(output_path)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        if not self.analysis_path.exists():
            raise FileNotFoundError(f"Analysis file not found: {self.analysis_path}")

    def _flatten_polygon(self, polygon: List[List[List[float]]]) -> List[Tuple[float, float]]:
        """Convert nested polygon format to flat list of points."""
        points = []
        try:
            # Extract points from the polygon data
            for segment in polygon:
                points.extend((point[0], point[1]) for point in segment)
            
            # Remove duplicates while preserving order
            seen = set()
            return [(float(x), float(y)) for x, y in points if (x, y) not in seen and not seen.add((x, y))]
        except Exception as e:
            print(f"Error flattening polygon: {e}")
            print(f"Polygon data: {polygon}")
            return []

    def _draw_polygon(self, page, polygon: List[List[List[float]]], element_type: str = 'word', content: str = ""):
        """Draw a polygon on the page with color based on element type."""
        try:
            # Use standard US Letter dimensions (8.5 x 11 inches)
            STANDARD_WIDTH = 8.5 * 72  # 612 points
            STANDARD_HEIGHT = 11.0 * 72  # 792 points
            
            print(f"\nDrawing {element_type} polygon for content: '{content}'")
            print(f"Using standard dimensions: {STANDARD_WIDTH} x {STANDARD_HEIGHT} points")

            # Flatten and scale the points
            points = self._flatten_polygon(polygon)
            if not points:
                return

            # Scale the points to page coordinates
            scaled_points = []
            for x, y in points:
                scaled_x = x * 72  # Convert inches directly to points
                scaled_y = y * 72  # Convert inches directly to points
                scaled_points.append((scaled_x, scaled_y))

            if len(scaled_points) < 2:
                return

            # Get color for element type
            color = self.COLORS.get(element_type, (0, 0, 0))  # Default to black if type unknown
            
            # Create a shape for drawing
            shape = page.new_shape()
            
            # Draw filled polygon with semi-transparency
            shape.draw_polyline(scaled_points + [scaled_points[0]])  # Close the polygon
            shape.finish(fill=color, fill_opacity=0.2, color=color, width=1.0)
            
            # Commit the shape to the page
            shape.commit()

        except Exception as e:
            print(f"Error drawing {element_type} polygon: {e}")
            raise

    def process_analysis(self):
        """Process the analysis file and create annotated PDF."""
        with open(self.analysis_path, 'r', encoding='utf-8') as f:
            analysis = json.load(f)

        pdf = fitz.open(self.pdf_path)
        
        try:
            if not analysis.get("pages"):
                return
                
            page_data = analysis["pages"][0]
            page = pdf[0]
            
            # Process elements in order (background to foreground)
            
            # Draw paragraphs first (background)
            for paragraph in page_data.get("paragraphs", []):
                polygon = paragraph.get("polygon")
                if polygon:
                    self._draw_polygon(page, polygon, 'paragraph', paragraph.get('content', ''))

            # Draw lines next
            for line in page_data.get("lines", []):
                polygon = line.get("polygon")
                if polygon:
                    self._draw_polygon(page, polygon, 'line', line.get('content', ''))

            # Draw words on top
            for word in page_data.get("words", []):
                polygon = word.get("polygon")
                if polygon:
                    self._draw_polygon(page, polygon, 'word', word.get('content', ''))

            # Draw tables
            for table in page_data.get("tables", []):
                # Draw table boundary
                for region in table.get("bounding_regions", []):
                    polygon = region.get("polygon")
                    if polygon:
                        self._draw_polygon(page, polygon, 'table')
                
                # Draw cells
                for cell in table.get("cells", []):
                    for region in cell.get("bounding_regions", []):
                        polygon = region.get("polygon")
                        if polygon:
                            self._draw_polygon(page, polygon, 'cell')

            # Draw selection marks last (on top)
            for mark in page_data.get("selection_marks", []):
                polygon = mark.get("polygon")
                if polygon:
                    self._draw_polygon(page, polygon, 'selection_mark')

        finally:
            pdf.save(self.output_path)
            pdf.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python visualize_analysis.py <sample_name>")
        print("Example: python visualize_analysis.py sample")
        sys.exit(1)

    sample_name = sys.argv[1]
    script_dir = Path(__file__).parent
    sample_dir = script_dir / "sample_documents"

    # Set up file paths
    pdf_path = sample_dir / f"{sample_name}.pdf"
    analysis_path = sample_dir / f"{sample_name}_analysis.json"
    output_path = sample_dir / f"{sample_name}_annotated.pdf"

    try:
        visualizer = LayoutVisualizer(
            str(pdf_path),
            str(analysis_path),
            str(output_path)
        )
        print(f"Processing {pdf_path}...")
        visualizer.process_analysis()
        print(f"✓ Annotated PDF saved to: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 