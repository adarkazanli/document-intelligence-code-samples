from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
import os

def test_azure_credentials():
    """
    Test Azure Document Intelligence credentials from environment variables.
    
    Returns:
        tuple: (bool, str) - (success status, message)
    """
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    # Check if either credential is missing
    if not endpoint and not key:
        return False, "Missing Azure credentials in environment variables"
    if not endpoint:
        return False, "Missing Azure endpoint in environment variables"
    if not key:
        return False, "Missing Azure key in environment variables"
    
    try:
        # Initialize the client
        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
        
        # Test the credentials by beginning a simple read operation
        # This is a lightweight operation that won't complete but will validate credentials
        document_analysis_client.begin_analyze_document(
            "prebuilt-read", 
            b"test"  # Minimal document content for testing
        )
        
        return True, "Successfully connected to Azure Document Intelligence service"
        
    except ResourceNotFoundError:
        return False, "Invalid endpoint URL"
    except HttpResponseError as e:
        if "InvalidRequest" in str(e):
            # This is expected as we sent invalid document content
            # But it means our credentials were accepted
            return True, "Successfully connected to Azure Document Intelligence service"
        return False, f"Invalid credentials or service error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}" 