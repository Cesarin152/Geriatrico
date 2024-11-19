from PyQt5.QtCore import QThread, pyqtSignal
import requests
import time
import psutil
from typing import Dict, Any, Optional

class StatusThread(QThread):
    update_ui_signal: pyqtSignal = pyqtSignal(dict, float, float)  # Señal para actualizar la UI con datos de dispositivos, CPU y RAM

    def __init__(self) -> None:
        super().__init__()
        self._is_running: bool = True

    def run(self) -> None:
        """Ejecuta el hilo que obtiene el estado de los dispositivos y el uso de CPU y RAM en intervalos regulares."""
        while self._is_running:
            start_time: float = time.time()
            try:
                # Obtener el estado de los dispositivos desde el servidor Flask
                response: requests.Response = requests.get("http://192.168.0.163:5000/devices")
                
                if response.status_code == 200:
                    devices: Dict[str, Any] = response.json()  # Espera un diccionario JSON de la respuesta
                    print("Dispositivos encontrados: ", devices)
                else:
                    print(f"Error al obtener el estado de los dispositivos: {response.status_code}")
                    devices: Dict[str, Any] = {}
            except requests.exceptions.RequestException as e:
                print(f"Error de conexión: {e}")
                devices = {}

            # Obtener el uso de CPU y RAM sin bloquear
            cpu_percent: float = psutil.cpu_percent(interval=None)
            mem: psutil._pslinux.svmem = psutil.virtual_memory()
            ram_percent: float = mem.used / mem.total  # Porcentaje de uso de RAM

            # Emitir la señal con los datos
            self.update_ui_signal.emit(devices, cpu_percent, ram_percent)

            # Mantener un intervalo de actualización
            elapsed_time: float = time.time() - start_time
            time.sleep(max(0, 1 - elapsed_time))  # Actualiza cada 1 segundo aproximadamente

    def stop(self) -> None:
        """Detiene el hilo al cambiar el estado de ejecución."""
        self._is_running = False
