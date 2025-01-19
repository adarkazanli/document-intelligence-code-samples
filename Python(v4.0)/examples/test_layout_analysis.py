#!/usr/bin/env python3
"""
Example script demonstrating the LayoutAnalyzer functionality.
"""

import os
import sys
from pathlib import Path
from my_project.models.layout_analyzer import LayoutAnalyzer
from my_project.utils.azure_client import test_azure_credentials

def main():
    # First verify Azure credentials
    print("Verifying Azure credentials...")
    success, message = test_azure_credentials()
    if not success:
        print(f"Error: {message}")
        sys.exit(1)
    print("✓ Azure credentials verified")

    # Initialize the analyzer
    try:
        analyzer = LayoutAnalyzer()
        print("✓ Layout analyzer initialized")
    except ValueError as e:
        print(f"Error initializing analyzer: {e}")
        sys.exit(1)

    # Get sample document path
    script_dir = Path(__file__).parent
    sample_dir = script_dir / "sample_documents"
    sample_dir.mkdir(exist_ok=True)

    # Check if sample document exists
    sample_path = sample_dir / "sample.pdf"
    if not sample_path.exists():
        print(f"\nError: Sample document not found at {sample_path}")
        print("Please place a PDF document named 'sample.pdf' in the examples/sample_documents directory")
        sys.exit(1)

    # Set up output paths
    json_path = sample_dir / "sample_analysis.json"

    # Analyze the document
    print(f"\nAnalyzing document: {sample_path}")
    print(f"Results will be saved to: {json_path}")
    print("-" * 50)
    
    try:
        analyzer.analyze_and_save_json(str(sample_path), str(json_path))
        print("-" * 50)
        print("✓ Analysis complete")
        print(f"✓ Results saved to {json_path}")
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 