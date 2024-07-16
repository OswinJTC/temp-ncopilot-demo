from typing import Dict, Optional
from data_interface.interfaces.patient_info import FindPatientInfoInterface
from data_interface.interfaces.vitalsigns import FindVitalsignsInterface
from data_interface.interfaces.base import BaseInterface
from auth0.models import TokenData

class DataInterfaceFactory:
    def get_interface(self, interface_type: str, query: Dict, projection: Dict = None, conditions: Optional[Dict] = None, token_data: TokenData = None) -> BaseInterface:
        if interface_type == "patient_info":
            return FindPatientInfoInterface(query, projection, token_data)
        elif interface_type == "vitalsigns":
            return FindVitalsignsInterface(query, projection, conditions, token_data)
        else:
            raise ValueError(f"Unknown interface type: {interface_type}")
