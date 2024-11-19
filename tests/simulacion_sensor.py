import requests
import time
import random
from threading import Thread
from typing import Dict, Any

url_data = "http://181.197.42.195:5000/data"

def simulate_device(device_id: str) -> None:
    while True:
        # Datos de varios sensores simulados
        data: Dict[str, Any] = {
            "device": device_id,
            "type": "sensor",
            "sensors": [
                {"sensor": "temperatura", "value": round(random.uniform(20.0, 30.0), 2)},
                {"sensor": "humedad", "value": round(random.uniform(40.0, 60.0), 2)},
                {"sensor": "calidad_aire", "value": round(random.uniform(1000, 1100), 2)},
                {"sensor": "lux", "value": round(random.uniform(1000, 1100), 2)}
            ]
        }
        
        # Enviar datos al servidor
        try:
            response = requests.post(url_data, json=data)
            print(f"ESP32-{device_id} Data Response:", response.json())
        except Exception as e:
            print(f"Error sending data for {device_id}: {e}")
        
        # Esperar unos segundos antes del próximo envío
        time.sleep(2)

if __name__ == "__main__":
    # Simular el dispositivo
    device_thread = Thread(target=simulate_device, args=("ESP32_01",))
    device_thread.start()
    device_thread.join()
