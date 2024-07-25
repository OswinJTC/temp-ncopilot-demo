import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException

# Assuming the project root is in the Python path, these imports should work
from data_interface.interfaces.vitalsigns import FindVitalsignsInterface
from auth0.models import TokenData

@pytest.fixture
def setup_data():
    query = {'patientName': '憨斑斑'}
    projection = {'TP': 1, '_id': 0}
    conditions = {
        'duration': 365,
        'sortby': {'field': 'createdDate', 'order': 'descending'},
        'limit': 3
    }
    token_data = TokenData(
        sub='auth0|668f3cd9d0c86eb15af9c76a',
        permissions=['ah:tai', 'juboAgent_submit:query'],
        roles=['guest', 'jubo-admin-T0'],
        app_metadata={'organization': '5c10bdf47b43650f407de7d6'}
    )
    return query, projection, conditions, token_data

@patch('data_interface.interfaces.vitalsigns.get_db_connector')
@patch('data_interface.interfaces.vitalsigns.get_mongo_collections')
@patch('data_interface.interfaces.vitalsigns.check_organization_permission')
@patch('data_interface.interfaces.vitalsigns.check_patient_id_permission')
def test_execute_success(mock_check_patient_id_permission, mock_check_organization_permission, mock_get_mongo_collections, mock_get_db_connector, setup_data):
    query, projection, conditions, token_data = setup_data

    # Setup mock database connector
    mock_db_connector = MagicMock()
    mock_get_db_connector.return_value = mock_db_connector

    # Setup mock PostgreSQL response
    mock_pg_patient_object = {'patient_id': '5f0c0c0c0c0c0c0c0c0c0c0c'}
    mock_db_connector.run_sql_execute.return_value = None
    mock_db_connector._cur.fetchone.return_value = mock_pg_patient_object

    # Setup mock MongoDB collections
    mock_vitalsigns_collection = MagicMock()
    mock_patient_info_collection = MagicMock()
    mock_get_mongo_collections.return_value = {
        'vitalsigns': mock_vitalsigns_collection,
        'patients': mock_patient_info_collection
    }

    # Setup mock MongoDB patient information response
    mock_patient_info_collection.find_one.return_value = {'organization': ObjectId('5c10bdf47b43650f407de7d6')}

    # Setup mock vitalsigns query response
    mock_vitalsigns_collection.find.return_value.sort.return_value.limit.return_value = [
        {'TP': 36.6, 'createdDate': datetime.now()},
        {'TP': 37.0, 'createdDate': datetime.now()},
        {'TP': 36.8, 'createdDate': datetime.now()}
    ]

    # Initialize the interface
    interface = FindVitalsignsInterface(query, projection, conditions, token_data)
    
    # Execute the interface
    results = interface.execute()

    # Validate the results
    assert len(results) == 4  # 3 vitalsigns documents + 1 link
    assert 'TP' in results[0]
    assert 'link' in results[3]
    assert results[3]['link'].startswith('https://smc.jubo.health/VitalSign/patient/5f0c0c0c0c0c0c0c0c')

    # Verify the organization check was called
    mock_check_organization_permission.assert_called_once_with(token_data, '5c10bdf47b43650f407de7d6')

    # Verify the patient ID check was not called
    mock_check_patient_id_permission.assert_not_called()  # Ensure it's not called since organization check passed

@patch('data_interface.interfaces.vitalsigns.get_db_connector')
@patch('data_interface.interfaces.vitalsigns.get_mongo_collections')
@patch('data_interface.interfaces.vitalsigns.check_organization_permission', side_effect=HTTPException(status_code=403, detail="走開: 機構錯誤"))
@patch('data_interface.interfaces.vitalsigns.check_patient_id_permission')
def test_execute_organization_check_fails_but_patient_check_passes(mock_check_patient_id_permission, mock_check_organization_permission, mock_get_mongo_collections, mock_get_db_connector, setup_data):
    query, projection, conditions, token_data = setup_data

    # Setup mock database connector
    mock_db_connector = MagicMock()
    mock_get_db_connector.return_value = mock_db_connector

    # Setup mock PostgreSQL response
    mock_pg_patient_object = {'patient_id': '5f0c0c0c0c0c0c0c0c0c0c0c'}
    mock_db_connector.run_sql_execute.return_value = None
    mock_db_connector._cur.fetchone.return_value = mock_pg_patient_object

    # Setup mock MongoDB collections
    mock_vitalsigns_collection = MagicMock()
    mock_patient_info_collection = MagicMock()
    mock_get_mongo_collections.return_value = {
        'vitalsigns': mock_vitalsigns_collection,
        'patients': mock_patient_info_collection
    }

    # Setup mock MongoDB patient information response
    mock_patient_info_collection.find_one.return_value = {'organization': ObjectId('5c10bdf47b43650f407de7d6')}

    # Setup mock vitalsigns query response
    mock_vitalsigns_collection.find.return_value.sort.return_value.limit.return_value = [
        {'TP': 36.6, 'createdDate': datetime.now()},
        {'TP': 37.0, 'createdDate': datetime.now()},
        {'TP': 36.8, 'createdDate': datetime.now()}
    ]

    # Initialize the interface
    interface = FindVitalsignsInterface(query, projection, conditions, token_data)
    
    # Simulate patient ID permission check passing
    mock_check_patient_id_permission.return_value = True

    # Execute the interface
    results = interface.execute()

    # Validate the results
    assert len(results) == 4  # 3 vitalsigns documents + 1 link
    assert 'TP' in results[0]
    assert 'link' in results[3]
    assert results[3]['link'].startswith('https://smc.jubo.health/VitalSign/patient/5f0c0c0c0c0c0c0c0c')

    # Verify the organization check was called
    mock_check_organization_permission.assert_called_once_with(token_data, '5c10bdf47b43650f407de7d6')

    # Verify the patient ID check was called
    mock_check_patient_id_permission.assert_called_once_with(token_data, '5f0c0c0c0c0c0c0c0c0c0c0c')

@patch('data_interface.interfaces.vitalsigns.get_db_connector')
@patch('data_interface.interfaces.vitalsigns.get_mongo_collections')
@patch('data_interface.interfaces.vitalsigns.check_organization_permission', side_effect=HTTPException(status_code=403, detail="走開: 機構錯誤"))
@patch('data_interface.interfaces.vitalsigns.check_patient_id_permission', side_effect=HTTPException(status_code=403, detail="走開: 並非家屬"))
def test_execute_no_permission(mock_check_patient_id_permission, mock_check_organization_permission, mock_get_mongo_collections, mock_get_db_connector, setup_data):
    query, projection, conditions, token_data = setup_data

    # Setup mock database connector
    mock_db_connector = MagicMock()
    mock_get_db_connector.return_value = mock_db_connector

    # Setup mock PostgreSQL response
    mock_pg_patient_object = {'patient_id': '5f0c0c0c0c0c0c0c0c0c0c0c'}
    mock_db_connector.run_sql_execute.return_value = None
    mock_db_connector._cur.fetchone.return_value = mock_pg_patient_object

    # Setup mock MongoDB collections
    mock_vitalsigns_collection = MagicMock()
    mock_patient_info_collection = MagicMock()
    mock_get_mongo_collections.return_value = {
        'vitalsigns': mock_vitalsigns_collection,
        'patients': mock_patient_info_collection
    }

    # Setup mock MongoDB patient information response
    mock_patient_info_collection.find_one.return_value = {'organization': ObjectId('5c10bdf47b43650f407de7d6')}

    # Initialize the interface
    interface = FindVitalsignsInterface(query, projection, conditions, token_data)
    
    # Execute the interface and assert the HTTPException
    with pytest.raises(HTTPException) as excinfo:
        interface.execute()

    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "根本沒存取權拍謝"

    # Verify the organization check was called
    mock_check_organization_permission.assert_called_once_with(token_data, '5c10bdf47b43650f407de7d6')

    # Verify the patient ID check was called
    mock_check_patient_id_permission.assert_called_once_with(token_data, '5f0c0c0c0c0c0c0c0c0c0c0c')