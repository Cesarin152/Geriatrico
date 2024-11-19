import requests
from typing import Dict, Any

class RelayController:
    def __init__(self, server_url: str) -> None:
        self.server_url: str = server_url

    def send_command(self, device_id: str, relay: str, state: bool) -> None:
        """Envía un comando para encender o apagar un relé específico en un dispositivo."""
        if not device_id or not relay:
            print("Error: Ingresa el ID del dispositivo y el nombre del relé")
            return

        command_data: Dict[str, Any] = {
            "device": device_id,
            "command": "setRelay",
            "params": {
                "relay": relay,
                "state": state
            }
        }

        try:
            response: requests.Response = requests.post(self.server_url, json=command_data)
            if response.status_code == 200:
                print(f"Comando enviado: {'Encendido' if state else 'Apagado'}")
            else:
                print("Error al enviar el comando")
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
