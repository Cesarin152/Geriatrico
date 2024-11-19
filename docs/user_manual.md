
# Manual del Usuario

Este manual tiene como objetivo guiar a los usuarios en la instalación, configuración y uso del **Sistema de Monitoreo y Control Geriátrico**.

## Instalación

### Requisitos Previos
- Python 3.8 o superior.
- CUDA (opcional, para optimizar YOLO).

### Pasos
1. Clona el repositorio:
   ```bash
   git clone <URL-del-repositorio>
   cd Geriatrico_proyecto
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Conecta las cámaras y sensores al sistema.
4. Ejecuta el programa principal:
   ```bash
   python src/main.py
   ```

## Uso del Sistema

### Interfaz Gráfica
- **Cámaras:** Supervisión en tiempo real de las cámaras conectadas.
- **Sensores:** Muestra datos de temperatura, humedad y calidad del aire.
- **Alertas:** Detecta caídas y las reporta visual y sonoramente.
- **Automatización del Hogar:** Controla dispositivos como luces y ventiladores desde la interfaz.

