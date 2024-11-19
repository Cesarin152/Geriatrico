from pathlib import Path
from typing import Dict, Union

# Estado de la cámara con información de alerta
camera: Dict[str, Union[str, bool]] = {'info': "", 'level': "", 'alert': False}

# Configuración de rutas
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR: Path = PROJECT_ROOT / 'assets'
AUDIO_DIR: Path = ASSETS_DIR / 'audio'
MODEL_DIR: Path = ASSETS_DIR / 'model'

# Rutas específicas convertidas a cadena
audio_path: str = str(AUDIO_DIR / 'WarningBeep.mp3')
model_path: str = str(MODEL_DIR / 'yolo11l.pt')
