import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from typing import Dict, List, Optional
from pathlib import Path
import json

class LayoutAnalyzer:
    """Class for analyzing document layouts using Azure Document Intelligence."""

    def __init__(self, endpoint: Optional[str] = None, key: Optional[str] = None):
        """Initialize the LayoutAnalyzer with Azure credentials."""
        self.endpoint = endpoint or os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        self.key = key or os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        
        if not self.endpoint or not self.key:
            raise ValueError("Missing Azure credentials. Set environment variables or provide credentials.")
        
        self.client = DocumentAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )

    def _format_polygon(self, polygon) -> List[List[float]]:
        """Format polygon coordinates into a list of points."""
        if not polygon:
            return []
        return [[polygon[i], polygon[i + 1]] for i in range(0, len(polygon), 2)]

    def analyze_document(self, document_path: str) -> Dict:
        """
        Analyze the layout of a document and return JSON-formatted results.
        
        Args:
            document_path: Path to the document file
            
        Returns:
            Dict containing the analysis results
        """
        document_path = Path(document_path)
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        with open(document_path, "rb") as document:
            poller = self.client.begin_analyze_document("prebuilt-layout", document)
            result = poller.result()

        # Convert analysis to JSON-friendly format
        analysis = {
            "pages": [],
            "tables": [],
            "has_handwritten_content": bool(result.styles and any(style.is_handwritten for style in result.styles))
        }

        # Process pages
        for page in result.pages:
            page_data = {
                "page_number": page.page_number,
                "width": page.width,
                "height": page.height,
                "unit": page.unit,
                "lines": [],
                "words": [],
                "selection_marks": []
            }

            # Process lines
            for line in page.lines or []:
                page_data["lines"].append({
                    "content": line.content,
                    "polygon": self._format_polygon(line.polygon),
                    "spans": [{"offset": span.offset, "length": span.length} for span in line.spans]
                })

            # Process words
            for word in page.words or []:
                page_data["words"].append({
                    "content": word.content,
                    "confidence": word.confidence,
                    "polygon": self._format_polygon(word.polygon),
                    "span": {"offset": word.span.offset, "length": word.span.length}
                })

            # Process selection marks
            for mark in page.selection_marks or []:
                page_data["selection_marks"].append({
                    "state": mark.state,
                    "confidence": mark.confidence,
                    "polygon": self._format_polygon(mark.polygon)
                })

            analysis["pages"].append(page_data)

        # Process tables
        for table in result.tables or []:
            table_data = {
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": [],
                "bounding_regions": [{
                    "page_number": region.page_number,
                    "polygon": self._format_polygon(region.polygon)
                } for region in table.bounding_regions or []]
            }

            for cell in table.cells:
                table_data["cells"].append({
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "content": cell.content,
                    "bounding_regions": [{
                        "page_number": region.page_number,
                        "polygon": self._format_polygon(region.polygon)
                    } for region in cell.bounding_regions or []]
                })

            analysis["tables"].append(table_data)

        return analysis

    def analyze_and_save_json(self, document_path: str, output_path: str) -> None:
        """
        Analyze document layout and save results as JSON.
        
        Args:
            document_path: Path to the document file
            output_path: Path where to save the JSON results
        """
        analysis = self.analyze_document(document_path)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False) 