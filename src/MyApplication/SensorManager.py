from typing import Dict, Any, Optional

class SensorManager:
    def __init__(self, device_states: Dict[str, Any]) -> None:
        self.device_states: Dict[str, Any] = device_states

    def get_sensor_value(self, device_id: str, sensor_type: str) -> Optional[float]:
        """Obtiene el valor de un sensor específico en un dispositivo."""
        device_data: Optional[Dict[str, Any]] = self.device_states.get(device_id)
        if device_data:
            sensor_data: Optional[Dict[str, Any]] = device_data["sensors"].get(sensor_type)
            if sensor_data:
                return sensor_data["value"]
        return None
