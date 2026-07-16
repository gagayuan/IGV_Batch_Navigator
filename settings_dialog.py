"""
设置对话框
仅包含 Python 路径配置（持久化参数）
"""

import sys

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QFileDialog, QDialogButtonBox,
)
from PyQt5.QtCore import Qt

from settings_manager import AppSettings
from i18n import T


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = AppSettings()
        self.setWindowTitle(T('settings_title'))
        self.setMinimumWidth(480)
        self._init_ui()
        self._load()

    def _init_ui(self):
        lay = QVBoxLayout(self)

        g = QGroupBox(T('settings_group'))
        gl = QVBoxLayout(g)

        desc = QLabel(T('settings_desc'))
        desc.setWordWrap(True)
        gl.addWidget(desc)

        r1 = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(sys.executable)
        r1.addWidget(self.path_edit)
        btn = QPushButton(T('btn_browse'))
        btn.clicked.connect(self._browse)
        r1.addWidget(btn)
        gl.addLayout(r1)

        lay.addWidget(g)
        lay.addStretch()

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, T('dlg_select_python'),
            "",
            T('filter_python')
        )
        if path:
            self.path_edit.setText(path)

    def _save_and_accept(self):
        p = self.path_edit.text().strip()
        if p:
            self.settings.python_exe_path = p
        self.accept()

    def _load(self):
        self.path_edit.setText(self.settings.python_exe_path)