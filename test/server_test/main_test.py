import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Mock the logger setup and other external dependencies before importing the service module
with patch('linkinpark.lib.common.logger.setupCloudLogging'), \
     patch('linkinpark.lib.common.logger.Client'), \
     patch('linkinpark.lib.common.logger.getLogger'), \
     patch('linkinpark.lib.common.secret_accessor.SecretAccessor'), \
     patch('server.postgres_database.startup_postgres_event'), \
     patch('data_interface.db.mongo_database.startup_mongo_event'):
    from server.main import app, InputData, TokenData, process_input_text, convert_to_nl

client = TestClient(app)

@pytest.fixture
def token_data():
    return TokenData(sub="1234567890", name="Test User", email="test@example.com")

@pytest.fixture
def input_data():
    return InputData(input_text="Test input")

mock_response1 = [{"some_key": 1.0}, {"link": "http://example.com"}]
mock_response2 = "Formatted response"

@patch('llm_agent.llm.process_input_text')
@patch('llm_agent.llm.convert_to_nl')
@patch('auth0.auth.get_token_data')
@patch('auth0.utils.verify_jwt')
@patch('auth0.utils.get_public_key')
def test_agent_main_success(mock_get_unverified_header, mock_get_public_key, mock_verify_jwt, mock_get_token_data, mock_convert_to_nl, mock_process_input_text, token_data, input_data):
    mock_process_input_text.return_value = mock_response1
    mock_convert_to_nl.return_value = mock_response2
    mock_get_token_data.return_value = token_data

    mock_get_unverified_header.return_value = {"alg": "HS256"}
    mock_get_public_key.return_value = "mock_key"
    mock_verify_jwt.return_value = {"sub": "1234567890", "name": "Test User", "email": "test@example.com"}

    response = client.post(
        "/main-processing",
        json=input_data.dict(),
        headers={"Authorization": "Bearer mock_token"}
    )

    print("Response Status Code:", response.status_code)
    print("Response Content:", response.content)

    assert response.status_code == 200
    assert response.json() == mock_response2

@patch('llm_agent.llm.process_input_text')
@patch('llm_agent.llm.convert_to_nl')
@patch('auth0.auth.get_token_data')
@patch('auth0.utils.verify_jwt')
@patch('auth0.utils.get_public_key')
def test_agent_main_failure(mock_get_unverified_header, mock_get_public_key, mock_verify_jwt, mock_get_token_data, mock_convert_to_nl, mock_process_input_text, token_data, input_data):
    mock_process_input_text.side_effect = HTTPException(status_code=500, detail="Mocked Exception")
    mock_get_token_data.return_value = token_data

    mock_get_unverified_header.return_value = {"alg": "HS256"}
    mock_get_public_key.return_value = "mock_key"
    mock_verify_jwt.return_value = {"sub": "1234567890", "name": "Test User", "email": "test@example.com"}

    response = client.post(
        "/main-processing",
        json=input_data.dict(),
        headers={"Authorization": "Bearer mock_token"}
    )

    print("Response Status Code:", response.status_code)
    print("Response Content:", response.content)

    assert response.status_code == 500
    assert response.json()["detail"] == "Mocked Exception"
