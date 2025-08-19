
# Proyecto Geriátrico - Sistema de Monitoreo y Control

## Descripción General

Este proyecto es un prototipo desarrollado. Su objetivo principal es monitorear y gestionar entornos geriátricos, enfocándose en la detección de caídas, supervisión ambiental y control de dispositivos conectados.

El sistema utiliza tecnologías como **inteligencia artificial (YOLO)**, un **servidor Flask** para comunicación centralizada, y una **interfaz gráfica moderna basada en PyQt5**.

---

## Características Principales

- **Monitoreo en Tiempo Real:** Supervisión de cámaras y sensores ambientales.
- **Detección de Caídas:** Implementada con YOLO para análisis de imágenes en tiempo real.
- **Control de Dispositivos:** Uso de relés para controlar luces, ventiladores y otros equipos.
- **Interfaz Gráfica:** Proporciona una vista consolidada de cámaras, métricas y alertas.
- **Servidor Centralizado:** Flask para gestionar la comunicación entre cámaras, sensores y relés.
- **Simulaciones:** Scripts para probar el sistema sin hardware físico.

---
## Flujo General del Sistema

### 1. Inicio del Sistema
- `main.py` configura la interfaz gráfica y el servidor Flask.
- Se inicializan las cámaras, sensores y relés.

### 2. Procesamiento en Tiempo Real
- Las cámaras capturan imágenes, que se procesan con YOLO en `yolo_thread.py`.
- Los sensores recopilan métricas y envían datos al servidor Flask.

### 3. Detección de Caídas
- El modelo YOLO identifica posturas peligrosas y envía alertas al sistema.
- Las alertas se muestran en la GUI y se registran en el servidor.

### 4. Control de Dispositivos
- Los comandos enviados desde la GUI activan o desactivan los relés.
- Los cambios se ejecutan mediante solicitudes procesadas en el servidor.

### 5. Registro y Análisis
- Todos los eventos y datos se almacenan para análisis y ajustes posteriores.

---

## Casos de Uso

### Instalación en una Sala Geriátrica
1. **Preparativos:**
   - Colocar cámaras en esquinas estratégicas para máxima cobertura.
   - Instalar sensores para monitoreo ambiental.
   - Conectar relés a dispositivos como luces o ventiladores.

2. **Configuración:**
   - Ejecutar `main.py` para inicializar el sistema.
   - Configurar parámetros desde la GUI.

3. **Uso Diario:**
   - Monitorear cámaras y métricas ambientales en tiempo real.
   - Detectar caídas y recibir alertas inmediatas.
   - Ajustar condiciones ambientales desde la GUI.

---

## Explicación del Modelo YOLO

### ¿Qué es YOLO?
YOLO (You Only Look Once) es un modelo de inteligencia artificial que detecta objetos en imágenes y videos en tiempo real. Es conocido por su rapidez y precisión.

### Uso en el Proyecto
- **Objetivo:** Detectar caídas analizando posiciones corporales.
- **Implementación:**
  - El modelo preentrenado (`yolo11s.pt`) fue ajustado para identificar posturas horizontales.
  - Procesa imágenes en tiempo real para calcular ángulos y velocidades.
- **Resultados Esperados:**
  - Detección precisa de caídas y emisión de alertas.

---

## Pruebas y Simulaciones

1. **Pruebas de Sensores:**
   - Usa `simulacion_sensor.py` para generar datos simulados.
   - **Ejemplo:**
     ```python
     from tests.simulacion_sensor import simulate_device
     simulate_device("sensor_01")
     ```

2. **Pruebas de Relés:**
   - Ejecuta `simulacion_rele.py` para simular el encendido de dispositivos.
   - **Ejemplo:**
     ```python
     from tests.simulacion_rele import esp32_relay
     esp32_relay(device_id="ESP32_02")
     ```

3. **Pruebas de YOLO:**
   - Usa videos en `assets/video` para pruebas de detección.
   - **Comando:**
     ```bash
     python src/MyApplication/yolo_test.py
     ```

---

## Errores Comunes y Soluciones

1. **El sistema no detecta cámaras conectadas.**
   - **Causa:** Configuración incorrecta.
   - **Solución:** Ajusta los índices de las cámaras en la GUI.

2. **El servidor Flask no inicia.**
   - **Causa:** Puerto en uso.
   - **Solución:** Cambia el puerto en `server.py`.

3. **YOLO no detecta caídas correctamente.**
   - **Causa:** Cámaras mal posicionadas.
   - **Solución:** Ajusta las cámaras para cubrir mejor el área.

4. **Las métricas de sensores no se actualizan.**
   - **Causa:** Problemas de conexión con ESP32.
   - **Solución:** Verifica la red Wi-Fi.

---

## Instalación y Uso

### Requisitos
- Python 3.8 o superior.
- CUDA (opcional, para optimizar YOLO).

### Instalación
1. Clona este repositorio:
   ```bash
   git clone <URL-del-repositorio>
   cd Geriatrico_proyecto
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Ejecución
1. Inicia el programa principal:
   ```bash
   python src/main.py
   ```
2. Usa la GUI para supervisar cámaras, sensores y relés.

---

## Estilo de Código y Contribuciones

### Estilo de Código
- Sigue las reglas de **PEP 8**.
- Usa nombres descriptivos para funciones y variables.
- Comenta bloques complejos para explicar su propósito.

### Contribuciones
1. Realiza un fork del repositorio.
2. Crea una nueva rama para tus cambios.
3. Envía un pull request explicando tus aportes.

---

## Resultados Esperados

1. **Interfaz:**
   - Visualización en tiempo real de cámaras.
   - Alertas claras ante eventos críticos.
   - Métricas actualizadas de sensores.

2. **Detección de Caídas:**
   - Alertas sonoras y visuales al detectar posturas peligrosas.

3. **Control Ambiental:**
   - Ajuste de dispositivos según condiciones detectadas.

---

## Licencia

Este proyecto está bajo la Licencia GNU General Public License (GPL) v3.0 . Consulta `LICENSE` para más detalles.
