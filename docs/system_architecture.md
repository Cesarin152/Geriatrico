
# Arquitectura del Sistema

El sistema está compuesto por los siguientes módulos:

1. **Cámaras y YOLO:**
   - Procesan video en tiempo real para detectar caídas.
   - Usan el modelo YOLO para análisis avanzado.

2. **Servidor Flask:**
   - Gestiona la comunicación entre sensores, relés y la interfaz gráfica.

3. **Interfaz Gráfica (PyQt5):**
   - Muestra la visualización de cámaras y métricas ambientales.

4. **Sensores y Relés:**
   - Sensores capturan datos ambientales (temperatura, humedad, etc.).
   - Relés controlan dispositivos conectados, como luces o ventiladores.

5. **Base de Datos (Opcional):**
   - Los datos y alertas pueden almacenarse localmente para análisis futuro.

