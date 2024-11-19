from PyQt5.QtWidgets import QVBoxLayout, QLabel

from MyApplication.yolo_thread import CameraThread
from typing import Optional
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
import cv2

class CameraController:
    def __init__(self, parent: 'App') -> None:  # Se puede especificar que `parent` es una instancia de `App`
        self.parent: 'App' = parent
        self.camera_thread_1: Optional[CameraThread] = None
        self.camera_thread_2: Optional[CameraThread] = None
        self.image_label_1: QLabel = QLabel()
        self.image_label_2: QLabel = QLabel()
        self.image_label_1.setScaledContents(True)
        self.image_label_2.setScaledContents(True)

    def setup_camera_views(self) -> None:
        """Configura los layouts de las vistas de cámara en la interfaz."""
        self.container_layout_1: QVBoxLayout = QVBoxLayout(self.parent.cam_view_1)
        self.container_layout_1.addWidget(self.image_label_1)
        self.container_layout_2: QVBoxLayout = QVBoxLayout(self.parent.cam_view_2)
        self.container_layout_2.addWidget(self.image_label_2)

    def start_camera(self, index_1: int, index_2: int) -> None:
        """Inicia los hilos de cámara para los índices especificados."""
        if self.camera_thread_1:
            self.camera_thread_1.stop()
        if self.camera_thread_2:
            self.camera_thread_2.stop()

        # Inicializar los hilos de cámara
        self.camera_thread_1: CameraThread = CameraThread(index_1)
        self.camera_thread_2: CameraThread = CameraThread(index_2)

        # Conectar las señales frame_ready y fall_detected después de la creación
        self.camera_thread_1.frame_ready.connect(self.update_image_1)
        self.camera_thread_1.fall_detected.connect(lambda: self.parent.display_alert("FALL", "CRITICAL", True))

        self.camera_thread_2.frame_ready.connect(self.update_image_2)
        self.camera_thread_2.fall_detected.connect(lambda: self.parent.display_alert("FALL", "CRITICAL", True))

        # Iniciar los hilos de cámara
        self.camera_thread_1.start()
        self.camera_thread_2.start()

    def update_image_1(self, frame: np.ndarray) -> None:
        """Actualiza la imagen en `image_label_1` con el frame procesado."""
        image: QImage = self.convert_frame_to_qimage(frame)
        self.image_label_1.setPixmap(QPixmap.fromImage(image))

    def update_image_2(self, frame: np.ndarray) -> None:
        """Actualiza la imagen en `image_label_2` con el frame procesado."""
        image: QImage = self.convert_frame_to_qimage(frame)
        self.image_label_2.setPixmap(QPixmap.fromImage(image))

    def convert_frame_to_qimage(self, frame: np.ndarray) -> QImage:
        """Convierte un frame de OpenCV a un objeto QImage para su visualización."""
        frame_rgb: np.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line: int = ch * w
        return QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
