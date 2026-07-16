"""
日志查看器对话框
Ctrl+L 快捷键弹出
"""

import logging
from collections import deque

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
from PyQt5.QtCore import QTimer

from i18n import T


MAX_LOG_LINES = 2000
_log_buffer = deque(maxlen=MAX_LOG_LINES)


class LogHandler(logging.Handler):
    """将日志同时写入文件和内存缓冲区"""

    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath
        self.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"
        ))

    def emit(self, record):
        msg = self.format(record)
        _log_buffer.append(msg)
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except OSError:
            pass


def init_logging(log_path: str):
    """初始化全局日志系统"""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    handler = LogHandler(log_path)
    root.addHandler(handler)
    # 同时拦截 stdout/stderr
    import sys
    sys.stdout = _StreamRedirect(logging.getLogger("stdout"), logging.INFO)
    sys.stderr = _StreamRedirect(logging.getLogger("stderr"), logging.ERROR)


def get_log_text() -> str:
    return "\n".join(_log_buffer)


class _StreamRedirect:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self._buf = ""

    def write(self, s):
        if s.strip():
            self.logger.log(self.level, s.rstrip("\n"))

    def flush(self):
        pass


class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T('log_title'))
        self.setMinimumSize(700, 450)
        self.resize(750, 500)
        self._init_ui()
        self._refresh()

    def _init_ui(self):
        lay = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        lay.addWidget(self.text_edit)

        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(self.accept)
        lay.addWidget(btns)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _refresh(self):
        self.text_edit.setPlainText(get_log_text())
        sb = self.text_edit.verticalScrollBar()
        sb.setValue(sb.maximum())

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)