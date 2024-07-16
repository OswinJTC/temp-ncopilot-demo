import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from auth0.models import TokenData

# Mock the logger setup before importing the service module
with patch('linkinpark.lib.common.logger.setupCloudLogging'), \
     patch('linkinpark.lib.common.logger.Client'), \
     patch('linkinpark.lib.common.logger.getLogger'):

    from data_interface.routers.interface_primary import parse_query, execute_query  # Adjust the import to match the correct path

@pytest.fixture
def query_data():
    return {
        "patientName": "憨斑斑",
        "retrieve": ["TP", "HR"],
        "conditions": {
            "duration": 365,
            "sortby": {"field": "createdDate", "order": "descending"},
            "limit": 3
        },
        "interface_type": "vitalsigns"
    }

@pytest.fixture
def token_data():
    return TokenData(
        sub='auth0|668f3cd9d0c86eb15af9c76a',
        permissions=['ah:tai', 'juboAgent_submit:query'],
        roles=['guest', 'jubo-admin-T0'],
        app_metadata={'organization': '5c10bdf47b43650f407de7d6'}
    )

def test_parse_query(query_data):
    query_dict, projection, conditions = parse_query(query_data)
    assert query_dict == {"patientName": "憨斑斑"}
    assert projection == {"TP": 1, "HR": 1, "_id": 0}
    assert conditions == {"duration": 365, "sortby": {"field": "createdDate", "order": "descending"}, "limit": 3}

@patch('data_interface.factory.DataInterfaceFactory.get_interface')
def test_execute_query_success(mock_get_interface, query_data, token_data):
    # Mock the interface and its execute method
    mock_interface = MagicMock()
    mock_interface.execute.return_value = [
        {"TP": 36.6, "HR": 80, "createdDate": "2023-07-01T12:00:00"},
        {"TP": 37.0, "HR": 82, "createdDate": "2023-07-02T12:00:00"}
    ]
    mock_get_interface.return_value = mock_interface

    result = execute_query(query_data, token_data)
    assert len(result) == 2
    assert result[0]["TP"] == 36.6
    assert result[0]["HR"] == 80

    mock_get_interface.assert_called_once_with(
        query_data["interface_type"],
        {"patientName": "憨斑斑"},
        {"TP": 1, "HR": 1, "_id": 0},
        {"duration": 365, "sortby": {"field": "createdDate", "order": "descending"}, "limit": 3},
        token_data
    )
    mock_interface.execute.assert_called_once()

@patch('data_interface.factory.DataInterfaceFactory.get_interface')
def test_execute_query_http_exception(mock_get_interface, query_data, token_data):
    mock_interface = MagicMock()
    mock_interface.execute.side_effect = HTTPException(status_code=404, detail="Not found")
    mock_get_interface.return_value = mock_interface

    with pytest.raises(HTTPException) as excinfo:
        execute_query(query_data, token_data)
    
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Not found"

@patch('data_interface.factory.DataInterfaceFactory.get_interface')
def test_execute_query_general_exception(mock_get_interface, query_data, token_data):
    mock_interface = MagicMock()
    mock_interface.execute.side_effect = Exception("General error")
    mock_get_interface.return_value = mock_interface

    with pytest.raises(HTTPException) as excinfo:
        execute_query(query_data, token_data)
    
    assert excinfo.value.status_code == 500
    assert "General error" in excinfo.value.detail
