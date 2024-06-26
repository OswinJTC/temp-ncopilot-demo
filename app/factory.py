from typing import Dict, Optional
from app.interfaces.patient_info import FindPatientInfoInterface
from app.interfaces.vitalsigns import FindVitalsignsInterface
from app.interfaces.base import DataInterface

class DataInterfaceFactory:
    def get_interface(self, interface_type: str, query: Dict, projection: Dict = None, conditions: Optional[Dict] = None) -> DataInterface:
        if interface_type == "patient_info":
            return FindPatientInfoInterface(query, projection)
        elif interface_type == "vitalsigns":
            return FindVitalsignsInterface(query, projection, conditions)
        else:
            raise ValueError(f"Unknown interface type: {interface_type}")
        
