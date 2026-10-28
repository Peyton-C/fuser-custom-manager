import logging
import sys
import threading
from pathlib import Path

from PySide6.QtCore import Qt

# Log to ~/.fuser_manager/fuser_manager.log (and stderr) so download/install
# failures that only flash in the status bar leave a trace.
_LOG_FILE = Path.home() / ".fuser_manager" / "fuser_manager.log"
_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-7s [%(threadName)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(_LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
)
# Third-party HTTP chatter drowns out our own messages at DEBUG.
for _noisy in ("urllib3", "PIL", "filelock"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)
logging.getLogger(__name__).info("Starting Fuser Custom Song Manager (log: %s)", _LOG_FILE)

sys.excepthook = lambda *exc_info: logging.getLogger("uncaught").critical(
    "Uncaught exception", exc_info=exc_info)
threading.excepthook = lambda args: logging.getLogger("uncaught").critical(
    "Uncaught exception in thread %s", args.thread and args.thread.name,
    exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
from PySide6.QtGui import QFontDatabase, QFont, QPixmapCache
from PySide6.QtWidgets import QApplication

import assets_rc  # noqa: F401 — registers Qt resources (font + icons)

QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

app = QApplication(sys.argv)
# Fusion bypasses the Windows native widget renderer so QSS border-radius,
# custom backgrounds, and other properties are fully honoured.
app.setStyle("Fusion")

# Sora must be registered before any widget (including QSS) is created
QFontDatabase.addApplicationFont(":/fonts/Sora-VariableFont_wght.ttf")
app.setFont(QFont("Sora", 10))

# Pre-size the album-art gradient pixmap cache
QPixmapCache.setCacheLimit(20_000)  # KB

from gui.styles import APP_STYLE  # noqa: E402 — must come after QApplication
app.setStyleSheet(APP_STYLE)

from gui.widgets.rounded_button_filter import RoundedButtonFilter  # noqa: E402
_btn_filter = RoundedButtonFilter(app)
app.installEventFilter(_btn_filter)

from gui.main_window import FuserApp  # noqa: E402
window = FuserApp()
window.show()
sys.exit(app.exec())
