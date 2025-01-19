"""
My Project initialization
"""
import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env file
load_dotenv()

# Access environment variables
AZURE_ENDPOINT = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
AZURE_KEY = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Import utility functions
from .utils.azure_client import test_azure_credentials

# Test credentials on import if in debug mode
if DEBUG:
    success, message = test_azure_credentials()
    print(f"Azure Credentials Test: {message}")

from my_project import test_azure_credentials

success, message = test_azure_credentials()
if success:
    print("Azure credentials are valid!")
    # Proceed with document analysis
else:
    print(f"Error: {message}")
    # Handle the error appropriately 