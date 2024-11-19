from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from typing import Dict, Any
from MyApplication.CameraControllers import CameraController
from MyApplication.RelayController import RelayController
from MyApplication.ui_modern_dashboard import Ui_ModernDashboard
from MyApplication.status_thread import StatusThread
import pygame
from MyApplication.aux_value import audio_path
from MyApplication.SensorManager import SensorManager
from MyApplication.aux_value import camera

class App(QMainWindow, Ui_ModernDashboard):
    update_ui_signal: pyqtSignal = pyqtSignal(dict, float, float)

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)

        # Conectar la señal al método que actualizará la UI
        self.update_ui_signal.connect(self.update_ui)

        # Crear y configurar el hilo de estado
        self.status_thread: StatusThread = StatusThread()
        self.status_thread.update_ui_signal.connect(self.update_ui_signal)
        self.status_thread.start()

        # Inicializar controladores
        self.camera_controller: CameraController = CameraController(self)
        self.relay_controller: RelayController = RelayController("http://192.168.0.163:5000/command")

        # Configuración de cámaras
        self.camera_status()
        self.camera_controller.setup_camera_views()
        self.start_system.clicked.connect(lambda: self.camera_controller.start_camera(
            self.comboBox_camera1.currentIndex(), self.comboBox_2_camera_2.currentIndex()))
        
        # Configuración del botón para apagar la alerta
        self.system.clicked.connect(self.desactivar_alerta)

        # Conectar controles de relés
        self.bombilla_1.stateChanged.connect(lambda state: self.relay_controller.send_command("ESP32_02", "relay_01", state == Qt.Checked))
        self.bombilla_2.stateChanged.connect(lambda state: self.relay_controller.send_command("ESP32_02", "relay_02", state == Qt.Checked))
        self.bombilla_3.stateChanged.connect(lambda state: self.relay_controller.send_command("ESP32_02", "relay_03", state == Qt.Checked))
        self.bombilla_4.stateChanged.connect(lambda state: self.relay_controller.send_command("ESP32_02", "relay_04", state == Qt.Checked))
        self.purificador.stateChanged.connect(lambda state: self.relay_controller.send_command("ESP32_02", "relay_05", state == Qt.Checked))
        self.deshumificador.stateChanged.connect(lambda state: self.relay_controller.send_command("ESP32_02", "relay_06", state == Qt.Checked))
        self.abanico.stateChanged.connect(lambda state: self.relay_controller.send_command("ESP32_02", "relay_07", state == Qt.Checked))

    def desactivar_alerta(self) -> None:
        """Apaga la alerta de inmediato y actualiza el estado"""
        camera['alert'] = False  # Actualizar el estado del diccionario
        if pygame.mixer.music.get_busy():  # Solo detener si el sonido está activo
            pygame.mixer.music.stop()
        self.alert_list.setText("Alert Off")  # Actualizar la interfaz si es necesario

    def camera_status(self) -> None:
        """Actualiza el estado de las cámaras disponibles en la interfaz."""
        cameras = QCameraInfo.availableCameras()
        camera_available = [camera.description() for camera in cameras]
        
        if not cameras:
            self.alert_list.setText("No hay ninguna cámara disponible")
        else:
            self.comboBox_2_camera_2.addItems(camera_available)
            self.comboBox_camera1.addItems(camera_available)

    def update_ui(self, devices: Dict[str, Any], cpu_percent: float, ram_percent: float) -> None:
        """Actualiza la interfaz con los datos de dispositivos y uso de CPU/RAM."""
        self.sensor_manager = SensorManager(devices)
        try:
            # Actualizar el estado del ESP32_01
            online_esp32_01: bool = devices.get('ESP32_01', {}).get('status', {}).get('online', False)
            self.esp_01_status.setText("Online" if online_esp32_01 else "Offline")
            self.esp_01_status.setStyleSheet("color: green;" if online_esp32_01 else "color: red;")
            temp_esp_01 = self.sensor_manager.get_sensor_value('ESP32_01', "temperatura")
            humidity_esp_01 = self.sensor_manager.get_sensor_value('ESP32_01', "humedad")
            air_quality_esp_01 = self.sensor_manager.get_sensor_value('ESP32_01', "calidad_aire")

            self.environment_value.setText(f"Temp: {temp_esp_01} °C\nHumidity: {humidity_esp_01} %")
            self.air_quality_value.setText(str(air_quality_esp_01))

            # Actualizar el estado del ESP32_02
            online_esp32_02: bool = devices.get('ESP32_02', {}).get('status', {}).get('online', False)
            self.esp_02_status.setText("Online" if online_esp32_02 else "Offline")
            self.esp_02_status.setStyleSheet("color: green;" if online_esp32_02 else "color: red;")
        except Exception as e:
            print(f"Error al actualizar la UI: {e}")

        try:
            # Actualizar los datos de CPU y RAM en la interfaz gráfica
            self.cpu_usage.setText(f"{cpu_percent:.2f}%")
            self.ram_usage.setText(f"{ram_percent:.2f}%")
        except Exception as e:
            print(f"Error al actualizar los datos del computador: {e}")

        # Mostrar la alerta desde el estado del diccionario `camera`
        self.display_alert(camera['info'], camera['level'], camera['alert'])

    def display_alert(self, info: str = "", level: str = "", stop: bool = False) -> None:
        """Muestra y controla el sonido de la alerta en función del nivel y estado."""
        self.alert_list.setText(info)
        if level == "CRITICAL" and stop:
            if not pygame.mixer.music.get_busy():  # Solo reproduce si no está ya sonando
                pygame.mixer.music.play(loops=-1)
        elif level == "WARNING":
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
            pygame.mixer.music.stop()

        if stop is False and pygame.mixer.music.get_busy():  # Parar el sonido si `stop` es False
            pygame.mixer.music.stop()

    def closeEvent(self, event: QtCore.QEvent) -> None:
        """Limpia y detiene los hilos cuando se cierra la aplicación."""
        self.status_thread.stop()
        self.status_thread.wait()

        # Detener hilos de cámara si están corriendo
        if self.camera_controller.camera_thread_1:
            self.camera_controller.camera_thread_1.stop()
        if self.camera_controller.camera_thread_2:
            self.camera_controller.camera_thread_2.stop()

        event.accept()
