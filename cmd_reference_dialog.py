"""
IGV 命令参考对话框
展示 igv_cmd.csv 的内容，按类别着色，支持文本选中和复制
"""

import csv
import html
import os
import sys

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from i18n import T

# 8 个类别的柔和背景色（CSS 格式）
CATEGORY_COLORS = [
    "#e8f5e9",  # 浅绿
    "#e3f2fd",  # 浅蓝
    "#fff3e0",  # 浅橙
    "#fce4ec",  # 浅粉
    "#e0f2f1",  # 浅青
    "#f3e5f5",  # 浅紫
    "#fff9c4",  # 浅黄
    "#ede7f6",  # 浅靛
]


def _csv_path(lang='zh') -> str:
    """返回 igv_cmd.csv 或 igv_cmd_en.csv 的路径"""
    filename = "igv_cmd_en.csv" if lang == 'en' else "igv_cmd.csv"
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


def _load_commands(lang='zh'):
    """解析 CSV，返回 [(command, category, description), ...]"""
    rows = []
    path = _csv_path(lang)
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # 跳过表头
        for row in reader:
            if len(row) >= 3:
                rows.append((row[0].strip(), row[1].strip(), row[2].strip()))
    return rows


def _build_html(lang='zh') -> str:
    """从 CSV 数据生成带样式 HTML 表格"""
    rows = _load_commands(lang)

    # 给每个唯一类别分配颜色
    cat_order = []
    cat_color_map = {}
    for _cmd, cat, _desc in rows:
        if cat not in cat_color_map:
            cat_color_map[cat] = CATEGORY_COLORS[
                len(cat_order) % len(CATEGORY_COLORS)
            ]
            cat_order.append(cat)

    parts = []
    parts.append("""
    <table style="width:100%; border-collapse:collapse; font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; font-size: 13px;">
    <thead>
      <tr style="background-color:#37474f; color:white; font-weight:bold;">
        <th style="padding:8px 10px; text-align:left; white-space:nowrap;">''' + T('cmdref_th_cmd') + '''</th>
        <th style="padding:8px 10px; text-align:left; white-space:nowrap;">''' + T('cmdref_th_cat') + '''</th>
        <th style="padding:8px 10px; text-align:left;">''' + T('cmdref_th_desc') + '''</th>
      </tr>
    </thead>
    <tbody>
    """)

    for cmd, cat, desc in rows:
        bg = cat_color_map.get(cat, "#ffffff")
        cmd_esc = html.escape(cmd)
        cat_esc = html.escape(cat)
        desc_esc = html.escape(desc)
        parts.append(
            f'<tr style="background-color:{bg};">'
            f'<td style="padding:6px 10px; font-family:Consolas,\'Courier New\',monospace; font-size:12px; white-space:nowrap;">{cmd_esc}</td>'
            f'<td style="padding:6px 10px; white-space:nowrap;">{cat_esc}</td>'
            f'<td style="padding:6px 10px;">{desc_esc}</td>'
            f'</tr>'
        )

    parts.append("</tbody></table>")
    return "\n".join(parts)


class CmdReferenceDialog(QDialog):
    def __init__(self, parent=None, lang='zh'):
        super().__init__(parent)
        self._lang = lang
        self.setWindowTitle(T('cmdref_title'))
        self.resize(980, 700)
        self.setMinimumSize(700, 400)

        layout = QVBoxLayout(self)

        self._title_label = QLabel(T('cmdref_desc'))
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; margin-bottom: 6px;"
        )
        layout.addWidget(self._title_label)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setHtml(_build_html(lang))
        layout.addWidget(self.text_edit)