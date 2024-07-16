import pytest
from unittest.mock import patch, MagicMock
from auth0.models import TokenData
from fastapi import HTTPException
import json

# Mock the logger setup and secret accessor before importing the service module
with patch('linkinpark.lib.common.logger.setupCloudLogging'), \
     patch('linkinpark.lib.common.logger.Client'), \
     patch('linkinpark.lib.common.logger.getLogger'), \
     patch('linkinpark.lib.common.secret_accessor.SecretAccessor') as mock_secret_accessor, \
     patch('requests.post') as mock_requests_post, \
     patch('requests.get') as mock_requests_get, \
     patch('langchain_core.output_parsers.StrOutputParser'), \
     patch('langchain_community.llms.HuggingFaceEndpoint', autospec=True) as mock_huggingface:
    
    from llm_agent.service import Service, classify_query  # Adjust the import to match the correct path
    from data_interface.routers.interface_primary import execute_query
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    # Configure the mock HuggingFaceEndpoint
    mock_huggingface.return_value = MagicMock()

    # Configure the mock SecretAccessor
    mock_secret_accessor.return_value.access_secret.side_effect = lambda key: "test_value"

    # Configure the mock requests.post to return a response with a 'token'
    mock_post_response = MagicMock()
    mock_post_response.json.return_value = {'token': 'test_token'}
    mock_requests_post.return_value = mock_post_response

    # Configure the mock requests.get to return a successful response
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {'key': 'value'}  # Ensure this returns a serializable object
    mock_requests_get.return_value = mock_get_response

@pytest.fixture
def llm_config():
    return {
        'service_name': 'test_service',
        'endpoint_url': 'http://test-endpoint',
        'repo_id': 'test-repo',
        # Add other LLM configuration details here
    }

@pytest.fixture
def service(llm_config):
    with patch('requests.post') as mock_requests_post, patch('requests.get') as mock_requests_get:
        # Ensure the patched requests.post is used here too
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {'token': 'test_token'}
        mock_requests_post.return_value = mock_post_response

        # Ensure the patched requests.get is used here too
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {'key': 'value'}  # Ensure this returns a serializable object
        mock_requests_get.return_value = mock_get_response

        return Service(llm_config)

@pytest.fixture
def token_data():
    return TokenData(
        sub='auth0|668f3cd9d0c86eb15af9c76a',
        permissions=['ah:tai', 'juboAgent_submit:query'],
        roles=['guest', 'jubo-admin-T0'],
        app_metadata={'organization': '5c10bdf47b43650f407de7d6'}
    )

def test_classify_query():
    assert classify_query("查詢血壓") == "vitalsigns"
    assert classify_query("安排會議") == "patients_info"
    assert classify_query("其他查詢") == "default"

def test_build_prompt(service):
    tools = "tool_list"
    user_input = "請查詢血壓"
    base_prompt = "這是一個基礎提示"
    expected_prompt = "你是一個人工智慧助理。請依照使用者提出的需求輸出對應的結果。\n這是一個基礎提示"

    formatted_prompt = service.build_prompt(tools, user_input, base_prompt)
    assert expected_prompt in formatted_prompt

def test_parse_response(service):
    valid_response = '{"result": "success"}'
    invalid_response = 'invalid json {result: success}'
    
    assert service.parse_response(valid_response) == {"result": "success"}
    assert service.parse_response(invalid_response) == {}

@patch('data_interface.routers.interface_primary.execute_query')
@patch('langchain_core.output_parsers.StrOutputParser.invoke')
def test_generate(mock_invoke, mock_execute_query, service, token_data):
    tools = "tool_list"
    user_input = "請查詢血壓"
    base_prompt = "這是一個基礎提示"

    # Mock the LLM response
    mock_invoke.return_value = '{"interface_type": "vitalsigns", "patientName": "憨斑斑", "retrieve": ["TP", "HR"], "conditions": {"duration": 365, "sortby": {"field": "createdDate", "order": "descending"}, "limit": 3}}'
    mock_execute_query.return_value = [{"TP": 36.6, "HR": 80}, {"TP": 37.0, "HR": 82}]

    results = service.generate(tools, user_input, base_prompt, token_data)
    
    assert len(results) == 2
    assert results[0]["TP"] == 36.6
    assert results[0]["HR"] == 80

    mock_invoke.assert_called_once()
    mock_execute_query.assert_called_once()

@patch('data_interface.routers.interface_primary.execute_query')
@patch('langchain_core.output_parsers.StrOutputParser.invoke')
def test_generate_http_exception(mock_invoke, mock_execute_query, service, token_data):
    tools = "tool_list"
    user_input = "請查詢血壓"
    base_prompt = "這是一個基礎提示"

    # Mock the LLM response
    mock_invoke.return_value = '{"interface_type": "vitalsigns", "patientName": "憨斑斑", "retrieve": ["TP", "HR"], "conditions": {"duration": 365, "sortby": {"field": "createdDate", "order": "descending"}, "limit": 3}}'
    mock_execute_query.side_effect = HTTPException(status_code=404, detail="Not found")

    with pytest.raises(HTTPException) as excinfo:
        service.generate(tools, user_input, base_prompt, token_data)
    
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Not found"

    mock_invoke.assert_called_once()
    mock_execute_query.assert_called_once()

@patch('data_interface.routers.interface_primary.execute_query')
@patch('langchain_core.output_parsers.StrOutputParser.invoke')
def test_generate_general_exception(mock_invoke, mock_execute_query, service, token_data):
    tools = "tool_list"
    user_input = "請查詢血壓"
    base_prompt = "這是一個基礟提示"

    # Mock the LLM response
    mock_invoke.return_value = '{"interface_type": "vitalsigns", "patientName": "憨斑斑", "retrieve": ["TP", "HR"], "conditions": {"duration": 365, "sortby": {"field": "createdDate", "order": "descending"}, "limit": 3}}'
    mock_execute_query.side_effect = Exception("General error")

    with pytest.raises(HTTPException) as excinfo:
        service.generate(tools, user_input, base_prompt, token_data)
    
    assert excinfo.value.status_code == 500
    assert "General error" in excinfo.value.detail

    mock_invoke.assert_called_once()
    mock_execute_query.assert_called_once()
