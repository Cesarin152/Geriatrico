import requests
import time
from typing import Dict, Any

url_get_commands: str = "http://127.0.0.1:5000/get_commands"  # Endpoint para obtener comandos
url_post_status: str = "http://127.0.0.1:5000/data"  # Endpoint para enviar datos del relé

def esp32_relay(device_id: str = "ESP32_02") -> None:
    relay_state: bool = False  # Estado inicial del relé (apagado)
    last_status_sent: float = 0  # Tiempo del último envío del estado

    while True:
        try:
            # Obtener comandos pendientes del servidor (GET)
            response = requests.get(url_get_commands, params={"device": device_id})
            if response.status_code == 200:
                commands: list[Dict[str, Any]] = response.json().get("commands", [])
                for command in commands:
                    # Procesar y ejecutar el comando del relé
                    if command.get("command") == "setRelay":
                        relay_state = command["params"].get("state", False)
                        print(f"{device_id} Ejecutando comando: {'Encender' if relay_state else 'Apagar'} el relé")
            else:
                print(f"{device_id} Error obteniendo comandos: {response.status_code}")
        
        except Exception as e:
            print(f"{device_id} Error en la conexión al obtener comandos: {e}")
        
        # Enviar el estado del relé (POST) cada 10 segundos
        current_time: float = time.time()
        if current_time - last_status_sent > 10:
            try:
                relay_data: Dict[str, Any] = {
                    "device": device_id,
                    "type": "relay_status",
                    "relay": "relay1",
                    "state": relay_state
                }
                status_response = requests.post(url_post_status, json=relay_data)
                print(f"{device_id} Data Response:", status_response.json())
                if status_response.status_code == 200:
                    print(f"{device_id} Estado del relé enviado: {'Encendido' if relay_state else 'Apagado'}")
                else:
                    print(f"{device_id} Error al enviar estado del relé: {status_response.status_code}")
            except Exception as e:
                print(f"{device_id} Error en la conexión al enviar estado del relé: {e}")

            last_status_sent = current_time  # Actualizar el tiempo del último envío

        # Espera antes de la próxima consulta de comandos
        time.sleep(3)  # Consulta comandos cada 3 segundos

# Ejecutar la simulación del ESP32 Relé
if __name__ == "__main__":
    esp32_relay()
