from flask import Flask, request, jsonify
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional
import threading
import time

class ESP32Handler:
    def __init__(self) -> None:
        """
        Inicializa el manejador del ESP32, configurando logging, almacenamiento de datos y Flask.
        """
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger: logging.Logger = logging.getLogger(__name__)
        
        # Almacenamiento de datos
        self.device_states: Dict[str, Dict[str, Any]] = {}
        self.pending_commands: Dict[str, List[Dict[str, Any]]] = {}
        
        # Configurar Flask
        self.app: Flask = Flask(__name__)
        self.setup_routes()

    def setup_routes(self) -> None:
        """
        Configura las rutas de la aplicación Flask.
        """
        self.app.route('/data', methods=['POST'])(self.receive_data)
        self.app.route('/command', methods=['POST'])(self.send_command)
        self.app.route('/device/<device_id>', methods=['GET'])(self.get_device_state)
        self.app.route('/devices', methods=['GET'])(self.get_all_device_statuses)
        self.app.route('/get_commands', methods=['GET'])(self.get_commands)

    def init_device_state(self, device: str) -> None:
        """
        Inicializa el estado de un nuevo dispositivo si no existe.
        """
        if device not in self.device_states:
            self.device_states[device] = {
                'status': {'online': False, 'last_seen': None},
                'sensors': {},
                'relays': {}
            }
            self.pending_commands[device] = []

    def process_device_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa los datos recibidos del ESP32.
        """
        try:
            device: Optional[str] = data.get('device')
            device_type: Optional[str] = data.get('type')
            timestamp: str = datetime.now().isoformat()

            if not device or not device_type:
                raise ValueError("Faltan campos requeridos: 'device' o 'type'")

            self.init_device_state(device)

            # Actualizar estado de conexión
            self.update_device_status(device, online=True, last_seen=timestamp)

            # Procesar según tipo de dato
            if device_type == 'status':
                self._process_status_data(device, data)
            elif device_type == 'sensor':
                # Si es un conjunto de sensores, iteramos sobre cada sensor
                sensors = data.get('sensors')
                if isinstance(sensors, list):
                    for sensor_data in sensors:
                        self._process_sensor_data(device, sensor_data, timestamp)
                else:
                    raise ValueError("Se esperaba una lista de sensores en 'sensors'")
            elif device_type == 'relay':
                self._process_relay_data(device, data, timestamp)
            else:
                raise ValueError("Tipo de dato no reconocido")

            # Preparar respuesta con comandos pendientes
            return {
                'status': 'ok',
                'message': f'{device_type} updated',
                'commands': self.get_pending_commands(device)
            }

        except ValueError as ve:
            self.logger.error(f"Validation error: {str(ve)}")
            return {'status': 'error', 'message': str(ve)}
        except Exception as e:
            self.logger.error(f"Unexpected error processing data: {str(e)}")
            return {'status': 'error', 'message': 'Internal server error'}


    def update_device_status(self, device: str, online: bool, last_seen: str) -> None:
        """
        Actualiza el estado de conexión del dispositivo.
        """
        self.device_states[device]['status'].update({
            'online': online,
            'last_seen': last_seen
        })

    def _process_status_data(self, device: str, data: Dict[str, Any]) -> None:
        """
        Procesa datos de estado del dispositivo.
        """
        self.device_states[device]['status'].update({
            'wifi_strength': data.get('wifi_strength'),
            'ip': data.get('ip'),
            'uptime': data.get('uptime'),
            'error': data.get('error')
        })

    def _process_sensor_data(self, device: str, sensor_data: Dict[str, Any], timestamp: str) -> None:
        """
        Procesa datos de un sensor individual.
        """
        sensor: Optional[str] = sensor_data.get('sensor')
        value: Optional[Any] = sensor_data.get('value')
        if not sensor or value is None:
            raise ValueError("Faltan campos requeridos: 'sensor' o 'value'")
        
        self.device_states[device]['sensors'][sensor] = {
            'value': value,
            'timestamp': timestamp
        }


    def _process_relay_data(self, device: str, data: Dict[str, Any], timestamp: str) -> None:
        """
        Procesa datos de relés.
        """
        relay: Optional[str] = data.get('relay')
        state: Optional[Any] = data.get('state')
        if not relay or state is None:
            raise ValueError("Faltan campos requeridos: 'relay' o 'state'")
        
        self.device_states[device]['relays'][relay] = {
            'state': state,
            'timestamp': timestamp
        }

    def get_pending_commands(self, device: str) -> List[Dict[str, Any]]:
        """
        Obtiene y limpia la lista de comandos pendientes para un dispositivo.
        """
        commands: List[Dict[str, Any]] = self.pending_commands.get(device, [])
        self.pending_commands[device] = []
        return commands

    def receive_data(self):
        """
        Endpoint para recibir datos del ESP32.
        """
        try:
            data: Optional[Dict[str, Any]] = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No data received'}), 400

            self.logger.info(f"Received data: {data}")
            response_data = self.process_device_data(data)

            status_code: int = 200 if response_data.get('status') == 'ok' else 400
            return jsonify(response_data), status_code

        except Exception as e:
            self.logger.error(f"Error in receive_data: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    def get_commands(self):
        """
        Endpoint para que el ESP32 obtenga sus comandos pendientes.
        """
        try:
            device_id: Optional[str] = request.args.get('device')
            if not device_id or device_id not in self.pending_commands:
                return jsonify({'status': 'error', 'message': 'Device ID not found or invalid'}), 404

            # Obtener y limpiar la lista de comandos pendientes para el dispositivo
            commands = self.get_pending_commands(device_id)
            return jsonify({'status': 'ok', 'commands': commands}), 200

        except Exception as e:
            self.logger.error(f"Error in get_commands: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    def send_command(self):
        """
        Endpoint para enviar comandos al ESP32.
        """
        try:
            command_data: Optional[Dict[str, Any]] = request.get_json()
            device: Optional[str] = command_data.get('device') if command_data else None

            if not device:
                return jsonify({'status': 'error', 'message': 'Device ID required'}), 400

            self.init_device_state(device)

            # Agregar comando a la cola
            self.pending_commands[device].append({
                'command': command_data.get('command'),
                'params': command_data.get('params', {}),
                'timestamp': datetime.now().isoformat()
            })

            return jsonify({
                'status': 'ok',
                'message': 'Command queued successfully'
            }), 200

        except Exception as e:
            self.logger.error(f"Error in send_command: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    def get_device_state(self, device_id: str):
        """
        Endpoint para consultar el estado de un dispositivo.
        """
        try:
            if device_id in self.device_states:
                return jsonify(self.device_states[device_id]), 200
            else:
                return jsonify({'status': 'error', 'message': 'Device not found'}), 404
        except Exception as e:
            self.logger.error(f"Error in get_device_state: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    def get_all_device_statuses(self):
        """
        Endpoint para consultar el estado de todos los dispositivos.
        """
        try:
            return jsonify(self.device_states), 200
        except Exception as e:
            self.logger.error(f"Error in get_all_device_statuses: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    def monitor_devices(self, timeout: int = 5) -> None:
        """
        Monitorea los dispositivos y actualiza su estado a 'offline' si no han reportado en 'timeout' segundos.
        """
        while True:
            current_time: datetime = datetime.now()
            for device_id, device_info in list(self.device_states.items()):
                last_seen_str: Optional[str] = device_info['status'].get('last_seen')
                if last_seen_str:
                    last_seen = datetime.fromisoformat(last_seen_str)
                    elapsed_time = (current_time - last_seen).total_seconds()
                    if elapsed_time > timeout and device_info['status']['online']:
                        self.logger.info(f"Device {device_id} is offline (last seen {elapsed_time:.2f} seconds ago).")
                        device_info['status']['online'] = False
            time.sleep(1)  # Esperar 1 segundo antes de la siguiente comprobación

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = True) -> None:
        """
        Inicia el servidor Flask.
        """
        # Iniciar el hilo de monitoreo
        monitor_thread = threading.Thread(target=self.monitor_devices)
        monitor_thread.daemon = True  # El hilo se cerrará cuando se cierre el servidor
        monitor_thread.start()
        
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)

# Uso de la clase
if __name__ == '__main__':
    esp32_handler = ESP32Handler()
    esp32_handler.run()
