import pytest
from my_project.utils.azure_client import test_azure_credentials
import os
from unittest.mock import patch
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

def test_missing_credentials():
    with patch.dict(os.environ, clear=True):
        success, message = test_azure_credentials()
        assert not success
        assert "Missing Azure credentials" in message

def test_missing_endpoint():
    with patch.dict(os.environ, {
        'AZURE_DOCUMENT_INTELLIGENCE_KEY': 'test-key'
    }, clear=True):  # clear=True to ensure no other env vars interfere
        success, message = test_azure_credentials()
        assert not success
        assert "Missing Azure endpoint" in message

def test_missing_key():
    with patch.dict(os.environ, {
        'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT': 'https://test.endpoint'
    }, clear=True):  # clear=True to ensure no other env vars interfere
        success, message = test_azure_credentials()
        assert not success
        assert "Missing Azure key" in message

def test_invalid_credentials():
    with patch.dict(os.environ, {
        'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT': 'https://invalid.endpoint',
        'AZURE_DOCUMENT_INTELLIGENCE_KEY': 'invalid_key'
    }):
        success, message = test_azure_credentials()
        assert not success
        assert any(text in message.lower() for text in ['invalid', 'error', 'failed'])

@patch('azure.ai.formrecognizer.DocumentAnalysisClient.begin_analyze_document')
def test_successful_connection(mock_analyze):
    with patch.dict(os.environ, {
        'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT': 'https://test.endpoint',
        'AZURE_DOCUMENT_INTELLIGENCE_KEY': 'test_key'
    }):
        success, message = test_azure_credentials()
        assert success
        assert "Successfully connected" in message
        mock_analyze.assert_called_once_with("prebuilt-read", b"test")

@patch('azure.ai.formrecognizer.DocumentAnalysisClient.begin_analyze_document')
def test_invalid_request_error(mock_analyze):
    mock_analyze.side_effect = HttpResponseError(message="InvalidRequest: some error")
    with patch.dict(os.environ, {
        'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT': 'https://test.endpoint',
        'AZURE_DOCUMENT_INTELLIGENCE_KEY': 'test_key'
    }):
        success, message = test_azure_credentials()
        assert success  # Should still succeed as InvalidRequest means valid credentials
        assert "Successfully connected" in message

@patch('azure.ai.formrecognizer.DocumentAnalysisClient.begin_analyze_document')
def test_resource_not_found_error(mock_analyze):
    mock_analyze.side_effect = ResourceNotFoundError("Resource not found")
    with patch.dict(os.environ, {
        'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT': 'https://test.endpoint',
        'AZURE_DOCUMENT_INTELLIGENCE_KEY': 'test_key'
    }):
        success, message = test_azure_credentials()
        assert not success
        assert "Invalid endpoint URL" in message

@pytest.mark.integration
def test_valid_credentials():
    """
    This test requires valid credentials in environment variables.
    Skip if running unit tests only.
    """
    if not os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'):
        pytest.skip("Skipping integration test: No Azure credentials")
        
    success, message = test_azure_credentials()
    assert success
    assert "Successfully connected" in message 