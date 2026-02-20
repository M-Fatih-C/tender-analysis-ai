"""
TenderAI Logging Yapılandırması / Logging Configuration.

Tüm projede tutarlı loglama sağlar.
Provides consistent logging throughout the project.

Log dosyası: logs/tenderai.log
Format: "2025-06-12 14:30:00 | INFO | module_name | message"
"""

import logging
import sys
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "tenderai.log"

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(debug: bool = False) -> None:
    """
    Proje genelinde loglama yapılandır / Configure project-wide logging.

    Args:
        debug: True ise DEBUG seviyesi, yoksa INFO / DEBUG if True, else INFO
    """
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    level = logging.DEBUG if debug else logging.INFO

    # Root logger
    root = logging.getLogger()
    root.setLevel(level)

    # Daha önce handler varsa temizle / Clear existing handlers
    root.handlers.clear()

    # File handler
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT))
    root.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT))
    root.addHandler(ch)

    # Gürültülü kütüphaneleri sustur / Silence noisy libraries
    for name in ("httpx", "httpcore", "openai", "urllib3", "watchdog"):
        logging.getLogger(name).setLevel(logging.WARNING)

    logging.info("TenderAI logging başlatıldı / initialized (level=%s)", logging.getLevelName(level))
