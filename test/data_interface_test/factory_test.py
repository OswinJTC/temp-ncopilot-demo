import pytest
from unittest.mock import patch, MagicMock
from data_interface.interfaces.patient_info import FindPatientInfoInterface
from data_interface.interfaces.vitalsigns import FindVitalsignsInterface
from data_interface.interfaces.base import BaseInterface
from auth0.models import TokenData
from data_interface.factory import DataInterfaceFactory

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

def test_get_interface_patient_info(setup_data):
    query, projection, _, token_data = setup_data
    factory = DataInterfaceFactory()
    
    with patch.object(FindPatientInfoInterface, '__init__', return_value=None) as mock_init:
        interface = factory.get_interface("patient_info", query, projection, token_data=token_data)
        assert isinstance(interface, FindPatientInfoInterface)
        mock_init.assert_called_once_with(query, projection, token_data)

def test_get_interface_vitalsigns(setup_data):
    query, projection, conditions, token_data = setup_data
    factory = DataInterfaceFactory()
    
    with patch.object(FindVitalsignsInterface, '__init__', return_value=None) as mock_init:
        interface = factory.get_interface("vitalsigns", query, projection, conditions, token_data)
        assert isinstance(interface, FindVitalsignsInterface)
        mock_init.assert_called_once_with(query, projection, conditions, token_data)

def test_get_interface_unknown():
    factory = DataInterfaceFactory()
    with pytest.raises(ValueError) as excinfo:
        factory.get_interface("unknown_interface", {}, {})
    assert str(excinfo.value) == "Unknown interface type: unknown_interface"
