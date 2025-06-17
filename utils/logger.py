import logging
from pathlib import Path

Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/detections.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("maintainability-detector")