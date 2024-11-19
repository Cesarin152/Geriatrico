import cv2
import cvzone
import numpy as np
import math
from numba import jit
from ultralytics import YOLO
from typing import Optional
from aux_value import model_path

# Carga el modelo YOLO una vez y en CUDA
global_model: YOLO = YOLO(model_path).to("cuda")

# Crear una matriz NumPy para almacenar las posiciones anteriores
MAX_TRACK_ID = 1000  # Define el número máximo de identificadores posibles
previous_positions = np.full((MAX_TRACK_ID, 2), -1, dtype=np.int32)  # Inicializa con -1 para identificar sin datos previos

@jit(nopython=True)
def calculate_angle(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calcula el ángulo de inclinación de la caja delimitadora."""
    dx = x2 - x1
    dy = y2 - y1
    angle = math.degrees(math.atan2(dy, dx))
    return abs(angle)  # Ángulo absoluto en grados

@jit(nopython=True)
def calculate_speed(prev_x: int, prev_y: int, x: int, y: int) -> float:
    """Calcula la velocidad de movimiento basada en la distancia entre posiciones."""
    distance = math.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
    return distance  # Suponiendo una unidad de tiempo constante entre cuadros

class TestCameraThread:
    """Clase de prueba para procesamiento de video sin interfaz gráfica de PyQt."""
    def __init__(self, video_path: Optional[str] = None) -> None:
        """
        Inicializa el hilo de prueba para video.
        :param video_path: Ruta del archivo de video para pruebas.
        """
        self.video_path = video_path
        self.running = True
        self.names = global_model.model.names  # Lista de nombres de clases en YOLO

    def display_frame(self, frame):
        """Muestra el frame procesado en una ventana de OpenCV."""
        cv2.imshow("Frame Procesado", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False  # Detiene la reproducción si se presiona 'q'
        return True

    def run(self) -> None:
        """Ejecuta el procesamiento de video para pruebas."""
        cap = cv2.VideoCapture(self.video_path)
        
        while cap.isOpened() and self.running:
            ret, frame = cap.read()
            if not ret:
                break  # Termina si se llega al final del video

            frame = cv2.resize(frame, (640, 480))
            results = global_model.track(frame, persist=True, classes=0)

            if results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.int().cpu().tolist()
                class_ids = results[0].boxes.cls.int().cpu().tolist()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                confidences = results[0].boxes.conf.cpu().tolist()

                for box, class_id, track_id, conf in zip(boxes, class_ids, track_ids, confidences):
                    x1, y1, x2, y2 = box
                    h = y2 - y1
                    w = x2 - x1

                    # Cálculo del ángulo de inclinación
                    angle = calculate_angle(x1, y1, x2, y2)
                    
                    # Cálculo de la velocidad de movimiento usando la matriz NumPy
                    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

                    # Verifica que el track_id esté en el rango de MAX_TRACK_ID
                    if 0 <= track_id < MAX_TRACK_ID:
                        prev_x, prev_y = previous_positions[track_id]
                        if prev_x != -1 and prev_y != -1:
                            # Calcular la velocidad si existen posiciones previas
                            speed = calculate_speed(prev_x, prev_y, center_x, center_y)
                        else:
                            # Sin datos previos, velocidad = 0
                            speed = 0.0

                        # Actualizar la posición para el próximo cálculo fuera de Numba
                        previous_positions[track_id] = (center_x, center_y)
                    else:
                        # Si el track_id está fuera de rango, se ignora
                        speed = 0.0

                    # Nuevo criterio de detección de caída
                    if angle >30 and speed >20 or h - w <= 0:  # Ajustar 45 y 5 según pruebas
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cvzone.putTextRect(frame, f'{track_id}', (x1, y2), 1, 1)
                        cvzone.putTextRect(frame, "Fall", (x1, y1), 1, 1)

                    else:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cvzone.putTextRect(frame, f'{track_id}', (x1, y2), 1, 1)
                        cvzone.putTextRect(frame, "Normal", (x1, y1), 1, 1)


            # Muestra el frame procesado
            if not self.display_frame(frame):
                break

        cap.release()
        cv2.destroyAllWindows()

# Prueba del procesamiento con un archivo de video
video_path = r"C:\Users\cesar\Documents\Python Scripts\Geriatrico_proyecto\assets\video\video2.mp4"
test_thread = TestCameraThread(video_path=video_path)
test_thread.run()  # Ejecuta la prueba directamente sin iniciar la UI de PyQt