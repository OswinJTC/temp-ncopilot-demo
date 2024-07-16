import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
import json
from pydantic import BaseModel
from typing import List, Dict

# Assuming these are defined in the same module or imported appropriately
class HeHeDbOutput(BaseModel):
    DbOutput: List[Dict[str, float]]

class RequestBody(BaseModel):
    input_text: str
    dboutput: HeHeDbOutput
    link: str

# Mock the logger setup before importing the service module
with patch('linkinpark.lib.common.logger.setupCloudLogging'), \
     patch('linkinpark.lib.common.logger.Client'), \
     patch('linkinpark.lib.common.logger.getLogger'):
    from llm_agent.llm import process_input_text, convert_to_nl, TokenData


@pytest.fixture
def token_data():
    return TokenData(sub="1234567890", name="Test User", email="test@example.com")


@pytest.fixture
def request_body():
    db_output = HeHeDbOutput(DbOutput=[{"key1": 1.0}, {"key2": 2.0}])
    return RequestBody(input_text="Test input", dboutput=db_output, link="http://example.com")

# Mock data for the tests
mock_classify_query = "mock_query_type"
mock_base_prompt = "mock_base_prompt"
mock_tools_from_db = ['{"tool_name": "example_tool", "tool_config": {}}']


@patch('llm_agent.llm.classify_query')
@patch('llm_agent.llm.get_base_prompt')
@patch('llm_agent.llm.get_tools')
@patch('llm_agent.llm.Service')
def test_process_input_text_success(mock_service, mock_get_tools, mock_get_base_prompt, mock_classify_query, token_data):
    mock_classify_query.return_value = mock_classify_query
    mock_get_base_prompt.return_value = mock_base_prompt
    mock_get_tools.return_value = mock_tools_from_db
    mock_service_instance = MagicMock()
    mock_service.return_value = mock_service_instance
    mock_service_instance.generate.return_value = "mock_response"

    response = process_input_text("Test input", token_data)
    assert response == "mock_response"


@patch('llm_agent.llm.classify_query')
@patch('llm_agent.llm.get_base_prompt')
@patch('llm_agent.llm.get_tools')
@patch('llm_agent.llm.Service')
def test_process_input_text_failure(mock_service, mock_get_tools, mock_get_base_prompt, mock_classify_query, token_data):
    mock_classify_query.return_value = mock_classify_query
    mock_get_base_prompt.return_value = None
    mock_get_tools.return_value = mock_tools_from_db

    with pytest.raises(HTTPException) as exc_info:
        process_input_text("Test input", token_data)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Failed to retrieve prompt or tools from the database"


@patch('llm_agent.llm.Service2')
def test_convert_to_nl_success(mock_service2, request_body):
    mock_service2_instance = MagicMock()
    mock_service2.return_value = mock_service2_instance
    mock_service2_instance.generate.return_value = "mock_response"

    response = convert_to_nl(request_body)
    assert response == "mock_response"


@patch('llm_agent.llm.Service2')
def test_convert_to_nl_failure(mock_service2, request_body):
    mock_service2_instance = MagicMock()
    mock_service2.return_value = mock_service2_instance
    mock_service2_instance.generate.side_effect = Exception("Mocked Exception")

    with pytest.raises(HTTPException) as exc_info:
        convert_to_nl(request_body)
    assert exc_info.value.status_code == 500
    assert "Mocked Exception" in exc_info.value.detail
