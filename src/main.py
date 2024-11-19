import sys
import threading
from PyQt5.QtWidgets import QApplication
from MyApplication import App, ESP32Handler
from MyApplication import aux_value

def start_flask_server() -> None:
    """Inicia el servidor Flask en un hilo."""
    esp32_handler: ESP32Handler = ESP32Handler()
    esp32_handler.run()

if __name__ == "__main__":
    # aux_value.aux()
    # Inicia el servidor Flask en un hilo separado
    flask_thread: threading.Thread = threading.Thread(target=start_flask_server)
    flask_thread.daemon = True  # Finaliza el hilo cuando se cierra la aplicación principal
    flask_thread.start()
    
    # Inicia la aplicación PyQt
    app: QApplication = QApplication(sys.argv)
    main_window: App = App()

    main_window.show()
    sys.exit(app.exec_())
