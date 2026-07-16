"""
主窗口 UI
包含文件选择、参数设置、解析按钮、导航网格、按钮组、跨批次导航逻辑
"""

import os
import sys
import glob as glob_module
import logging

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QSpinBox, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QStatusBar, QHeaderView, QAbstractItemView, QAction, QSizePolicy,
    QTextEdit, QPlainTextEdit, QSplitter, QCheckBox,
)
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QBrush, QColor, QFont

from igv_core import (
    load_bam_batch, goto_loci, make_bam_batches, sample_name, set_genome,
    check_igv_port, run_tcp_commands, igv_cmd, set_port,
)
from tsv_csv_parser import parse_positions, make_position_batches
from settings_manager import AppSettings
from help_dialog import HelpDialog
from settings_dialog import SettingsDialog
from cmd_reference_dialog import CmdReferenceDialog
from log_dialog import LogViewerDialog
from version import VERSION
from i18n import T, LANG, toggle_lang

logger = logging.getLogger(__name__)

IS_FROZEN = getattr(sys, "frozen", False)

HEADER_BG = QColor("#e8e8e8")
CURRENT_BG = QColor("#b3d9ff")
NORMAL_BG = QColor("#ffffff")

SETTINGS_BTN_STYLE = """
    QPushButton {
        background-color: #e67e22;
        color: white;
        font-weight: bold;
        font-size: 13px;
        border-radius: 4px;
        padding: 6px 14px;
        border: 2px solid #d35400;
        min-width: 90px;
    }
    QPushButton:hover {
        background-color: #d35400;
    }
    QPushButton:pressed {
        background-color: #ba4a00;
    }
"""

HELP_BTN_STYLE = """
    QPushButton {
        background-color: #27ae60;
        color: white;
        font-weight: bold;
        font-size: 13px;
        border-radius: 4px;
        padding: 6px 14px;
        border: 2px solid #1e8449;
        min-width: 90px;
    }
    QPushButton:hover {
        background-color: #1e8449;
    }
    QPushButton:pressed {
        background-color: #186a3b;
    }
"""

TITLE_BTN_STYLE = """
    QPushButton {
        background-color: #27ae60;
        color: white;
        font-weight: bold;
        font-size: 11px;
        border-radius: 3px;
        padding: 3px 8px;
        border: 1px solid #1e8449;
    }
    QPushButton:hover {
        background-color: #1e8449;
    }
    QPushButton:pressed {
        background-color: #186a3b;
    }
    QPushButton:checked {
        background-color: #1e8449;
        border-color: #145a32;
    }
"""

RELEVANT_BTN_STYLE = """
    QPushButton {
        background-color: #27ae60;
        color: white;
        font-weight: bold;
        font-size: 13px;
        border-radius: 4px;
        padding: 6px 12px;
        border: 2px solid #1e8449;
    }
    QPushButton:hover {
        background-color: #1e8449;
    }
    QPushButton:pressed {
        background-color: #186a3b;
    }
    QPushButton:disabled {
        background-color: #95a5a6;
        color: #cccccc;
        border-color: #7f8c8d;
    }
"""

PARSE_BTN_STYLE = """
    QPushButton {
        background-color: #27ae60;
        color: white;
        font-weight: bold;
        font-size: 14px;
        border-radius: 4px;
        padding: 2px 20px;
        border: 2px solid #1e8449;
    }
    QPushButton:hover {
        background-color: #1e8449;
    }
    QPushButton:pressed {
        background-color: #186a3b;
    }
    QPushButton:disabled {
        background-color: #cccccc;
        color: #888888;
        border-color: #aaaaaa;
    }
"""


def scan_igv_genomes() -> list:
    """扫描 IGV 已下载的基因组（C:\\Users\\<用户名>\\igv\\genomes\\*.genome）"""
    genomes_dir = os.path.join(os.path.expanduser("~"), "igv", "genomes")
    if not os.path.isdir(genomes_dir):
        return ["hg38", "hg19"]
    genomes = []
    for f in glob_module.glob(os.path.join(genomes_dir, "*.genome")):
        name = os.path.splitext(os.path.basename(f))[0]
        genomes.append(name)
    if not genomes:
        return ["hg38", "hg19"]
    genomes.sort()
    return genomes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = AppSettings()
        self.pos_batches = []
        self.bam_batches = []
        self.current_pos_idx = 0
        self.current_bam_idx = 0
        self._prev_bam_idx = -1
        self._last_loaded_bams = None  # frozenset of sample_name, 追踪 IGV 当前加载的轨道
        self._cell_click_in_progress = False
        self.relevant_grids = []  # [(bam_idx, pos_idx), ...] 行优先排序
        self._has_k_relation = False
        self.grid_pair_info = {}  # {(bam_idx, pos_idx): [(pair_num, locus_text, bam_name), ...]}
        self.all_pairs = []  # [(locus_idx, bam_idx, locus_text, bam_name, pair_num), ...]
        self._is_collapsed = False
        self._is_minimal = False
        self._lang = LANG  # 'zh' or 'en'
        self._is_on_top = False
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        self.setWindowTitle(T('window_title', version=VERSION))
        self.setMinimumSize(900, 650)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(3)

        self.menuBar().hide()

        root.addWidget(self._build_file_group())

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self._build_nav_group())
        self.splitter.setStretchFactor(0, 3)
        root.addWidget(self.splitter)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(
            "QStatusBar { padding: 0px; min-height: 18px; max-height: 20px; }"
            "QStatusBar QLabel { padding: 0px; margin: 0px; }"
        )
        self.setStatusBar(self.status_bar)

        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self._open_log_viewer)

        # ── 六个导航按钮的快捷键 ──
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Comma), self).activated.connect(self._prev_relevant)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Period), self).activated.connect(self._next_relevant)
        QShortcut(QKeySequence("Ctrl+4"), self).activated.connect(self._prev_pos)
        QShortcut(QKeySequence("Ctrl+6"), self).activated.connect(self._next_pos)
        QShortcut(QKeySequence("Ctrl+8"), self).activated.connect(self._prev_bam)
        QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(self._next_bam)

    def _build_file_group(self) -> QGroupBox:
        g = QGroupBox()
        g.setStyleSheet("QGroupBox { padding-top: 1px; }")
        lay = QVBoxLayout(g)
        lay.setContentsMargins(6, 4, 6, 2)
        lay.setSpacing(8)

        # ── 自定义标题行（含帮助/设置按钮）──
        title_row = QHBoxLayout()
        self.file_group_title_label = QLabel("<b>" + T('file_group_title') + "</b>")
        title_row.addWidget(self.file_group_title_label)
        title_row.addStretch()

        self.lang_btn = QPushButton(T('btn_lang'))
        self.lang_btn.setStyleSheet(TITLE_BTN_STYLE)
        self.lang_btn.clicked.connect(self._toggle_language)
        title_row.addWidget(self.lang_btn)

        self.top_btn = QPushButton(T('btn_pin'))
        self.top_btn.setCheckable(True)
        self.top_btn.setStyleSheet(TITLE_BTN_STYLE)
        self.top_btn.clicked.connect(self._toggle_always_on_top)
        title_row.addWidget(self.top_btn)

        self.collapse_btn = QPushButton(T('btn_collapse'))
        self.collapse_btn.setStyleSheet(TITLE_BTN_STYLE)
        self.collapse_btn.clicked.connect(self._toggle_collapse)
        title_row.addWidget(self.collapse_btn)

        self.minimal_btn = QPushButton(T('btn_minimal'))
        self.minimal_btn.setStyleSheet(TITLE_BTN_STYLE)
        self.minimal_btn.clicked.connect(self._toggle_minimal)
        title_row.addWidget(self.minimal_btn)

        self.help_btn = QPushButton(T('btn_help'))
        self.help_btn.setStyleSheet(TITLE_BTN_STYLE)
        self.help_btn.clicked.connect(self._open_help)
        title_row.addWidget(self.help_btn)

        if not IS_FROZEN:
            settings_btn = QPushButton(T('btn_settings'))
            settings_btn.setStyleSheet(SETTINGS_BTN_STYLE)
            settings_btn.clicked.connect(self._open_settings)
            title_row.addWidget(settings_btn)

        lay.addLayout(title_row)

        # ── 可折叠内容容器 ──
        self.file_content_widget = QWidget()
        file_content_lay = QVBoxLayout(self.file_content_widget)
        file_content_lay.setContentsMargins(0, 0, 0, 0)
        file_content_lay.setSpacing(8)

        # ── 表格文件行（可被手动模式隐藏）──
        self.table_file_widget = QWidget()
        r1 = QHBoxLayout(self.table_file_widget)
        r1.setContentsMargins(0, 0, 0, 0)
        self.table_file_label = QLabel(T('label_table_file'))
        r1.addWidget(self.table_file_label)
        self.table_file_edit = QLineEdit()
        self.table_file_edit.setReadOnly(True)
        r1.addWidget(self.table_file_edit)
        self.btn_table = QPushButton(T('btn_browse'))
        self.btn_table.clicked.connect(self._browse_table_file)
        r1.addWidget(self.btn_table)
        file_content_lay.addWidget(self.table_file_widget)

        # ── 列名行（可被手动模式隐藏）──
        self.column_widget = QWidget()
        r2 = QHBoxLayout(self.column_widget)
        r2.setContentsMargins(0, 0, 0, 0)
        self.locus_col_label = QLabel(T('label_locus_col'))
        r2.addWidget(self.locus_col_label)
        self.locus_col_edit = QLineEdit()
        self.locus_col_edit.setPlaceholderText("CHROM:POS")
        self.locus_col_edit.setMaximumWidth(120)
        r2.addWidget(self.locus_col_edit)
        self.sample_col_label = QLabel(T('label_sample_col'))
        r2.addWidget(self.sample_col_label)
        self.sample_col_edit = QLineEdit()
        self.sample_col_edit.setPlaceholderText("sample")
        self.sample_col_edit.setMaximumWidth(100)
        r2.addWidget(self.sample_col_edit)
        r2.addStretch()
        file_content_lay.addWidget(self.column_widget)

        # ── 手动输入位置信息 ──
        r_manual_check = QHBoxLayout()
        self.manual_checkbox = QCheckBox(T('manual_checkbox'))
        self.manual_checkbox.toggled.connect(self._on_manual_mode_toggled)
        r_manual_check.addWidget(self.manual_checkbox)
        r_manual_check.addStretch()
        file_content_lay.addLayout(r_manual_check)

        self.manual_pos_edit = QPlainTextEdit()
        self.manual_pos_edit.setPlaceholderText(
            T('manual_placeholder')
        )
        self.manual_pos_edit.setMinimumHeight(100)
        self.manual_pos_edit.setVisible(False)
        file_content_lay.addWidget(self.manual_pos_edit)

        # ── 基因组 / 附加文件（勾选列表）──
        r_genome_label = QHBoxLayout()
        self.genome_label = QLabel(T('label_genome'))
        r_genome_label.addWidget(self.genome_label)
        r_genome_label.addStretch()
        file_content_lay.addLayout(r_genome_label)

        self.genome_list = QListWidget()
        self.genome_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.genome_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.genome_list.setMinimumHeight(70)
        self.genome_list.setMaximumHeight(120)
        file_content_lay.addWidget(self.genome_list)

        r_genome_btn = QHBoxLayout()
        self.genome_browse_btn = QPushButton(T('btn_browse_local'))
        self.genome_browse_btn.clicked.connect(self._browse_genome_file)
        r_genome_btn.addWidget(self.genome_browse_btn)
        self.btn_remove_genome = QPushButton(T('btn_remove_selected'))
        self.btn_remove_genome.clicked.connect(self._remove_genome_items)
        r_genome_btn.addWidget(self.btn_remove_genome)
        r_genome_btn.addStretch()
        file_content_lay.addLayout(r_genome_btn)

        r3_label = QHBoxLayout()
        self.track_label = QLabel(T('label_track_files'))
        r3_label.addWidget(self.track_label)
        r3_label.addStretch()
        file_content_lay.addLayout(r3_label)

        self.bam_list = QListWidget()
        self.bam_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bam_list.setMinimumHeight(60)
        file_content_lay.addWidget(self.bam_list)

        r3b = QHBoxLayout()
        self.btn_add = QPushButton(T('btn_add_tracks'))
        self.btn_add.clicked.connect(self._add_bam_files)
        r3b.addWidget(self.btn_add)
        self.btn_auto_find = QPushButton(T('btn_auto_find'))
        self.btn_auto_find.clicked.connect(self._auto_find_bam_files)
        r3b.addWidget(self.btn_auto_find)
        self.btn_remove = QPushButton(T('btn_remove_selected'))
        self.btn_remove.clicked.connect(self._remove_bam_files)
        r3b.addWidget(self.btn_remove)
        self.btn_remove_all = QPushButton(T('btn_remove_all'))
        self.btn_remove_all.clicked.connect(self._remove_all_bam_files)
        r3b.addWidget(self.btn_remove_all)
        r3b.addStretch()
        file_content_lay.addLayout(r3b)

        r4 = QHBoxLayout()
        self.pos_batch_label = QLabel(T('label_pos_batch'))
        r4.addWidget(self.pos_batch_label)
        self.pos_batch_spin = QSpinBox()
        self.pos_batch_spin.setRange(0, 1000)
        self.pos_batch_spin.setValue(5)
        r4.addWidget(self.pos_batch_spin)
        self.bam_batch_label = QLabel(T('label_bam_batch'))
        r4.addWidget(self.bam_batch_label)
        self.bam_batch_spin = QSpinBox()
        self.bam_batch_spin.setRange(0, 1000)
        self.bam_batch_spin.setValue(2)
        r4.addWidget(self.bam_batch_spin)
        self.filter_no_k_bams_check = QCheckBox(T('filter_no_k_bams'))
        self.filter_no_k_bams_check.setChecked(True)
        r4.addWidget(self.filter_no_k_bams_check)
        self.filter_k_tracks_check = QCheckBox(T('filter_k_tracks'))
        self.filter_k_tracks_check.setChecked(True)
        r4.addWidget(self.filter_k_tracks_check)
        r4.addStretch()
        file_content_lay.addLayout(r4)

        # ── 后处理 TCP 命令 ──
        r_post_label = QHBoxLayout()
        self.post_cmd_label = QLabel(T('label_post_cmds'))
        r_post_label.addWidget(self.post_cmd_label)
        r_post_label.addStretch()
        self.cmd_ref_btn = QPushButton(T('btn_cmd_ref'))
        self.cmd_ref_btn.setMinimumHeight(28)
        self.cmd_ref_btn.clicked.connect(self._open_cmd_reference)
        r_post_label.addWidget(self.cmd_ref_btn)
        file_content_lay.addLayout(r_post_label)

        self.post_cmds_edit = QPlainTextEdit()
        self.post_cmds_edit.setPlaceholderText(T('post_cmds_placeholder'))
        self.post_cmds_edit.setMaximumHeight(80)
        file_content_lay.addWidget(self.post_cmds_edit)

        # ── 端口设置 + 解析按钮 ──
        port_row = QHBoxLayout()
        self.port_label = QLabel(T('label_port'))
        port_row.addWidget(self.port_label)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(self.settings.igv_port)
        self.port_spin.setToolTip(T('port_tooltip'))
        self.port_spin.valueChanged.connect(lambda v: setattr(self.settings, 'igv_port', v))
        port_row.addWidget(self.port_spin)
        self.parse_btn = QPushButton(T('btn_parse'))
        self.parse_btn.setMinimumHeight(32)
        self.parse_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.parse_btn.setStyleSheet(PARSE_BTN_STYLE)
        self.parse_btn.clicked.connect(self._on_parse)
        port_row.addWidget(self.parse_btn)
        file_content_lay.addLayout(port_row)

        lay.addWidget(self.file_content_widget)

        return g

    def _build_nav_group(self) -> QGroupBox:
        self.nav_group_box = QGroupBox(T('nav_group_title'))
        g = self.nav_group_box
        g.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay = QVBoxLayout(g)
        lay.setContentsMargins(6, 6, 6, 0)

        self.grid_table = QTableWidget()
        self.grid_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.grid_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.grid_table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.grid_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.grid_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.grid_table.cellClicked.connect(self._on_cell_clicked)
        self.grid_table.currentCellChanged.connect(self._on_current_cell_changed)
        self.grid_table.installEventFilter(self)
        self.grid_table.verticalHeader().setDefaultAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )
        lay.addWidget(self.grid_table)

        self.cell_display_widget = QWidget()
        cd_layout = QHBoxLayout(self.cell_display_widget)
        cd_layout.setContentsMargins(0, 0, 0, 0)

        self.pos_display = QTextEdit()
        self.pos_display.setReadOnly(True)
        self.pos_display.setPlaceholderText(T('pos_placeholder'))
        self.pos_display.setMinimumHeight(80)
        self.pos_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        cd_layout.addWidget(self.pos_display)

        self.bam_display = QTextEdit()
        self.bam_display.setReadOnly(True)
        self.bam_display.setPlaceholderText(T('bam_placeholder'))
        self.bam_display.setMinimumHeight(80)
        self.bam_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        cd_layout.addWidget(self.bam_display)

        lay.addWidget(self.cell_display_widget)

        btn_layout = QHBoxLayout()

        self.btn_prev_relevant = QPushButton(T('btn_prev_relevant'))
        self.btn_prev_relevant.setStyleSheet(RELEVANT_BTN_STYLE)
        self.btn_prev_relevant.clicked.connect(self._prev_relevant)
        self.btn_prev_relevant.setEnabled(False)
        self.btn_next_relevant = QPushButton(T('btn_next_relevant'))
        self.btn_next_relevant.setStyleSheet(RELEVANT_BTN_STYLE)
        self.btn_next_relevant.clicked.connect(self._next_relevant)
        self.btn_next_relevant.setEnabled(False)

        self.btn_prev_pos = QPushButton(T('btn_prev_pos'))
        self.btn_prev_pos.clicked.connect(self._prev_pos)
        self.btn_next_pos = QPushButton(T('btn_next_pos'))
        self.btn_next_pos.clicked.connect(self._next_pos)

        self.btn_prev_bam = QPushButton(T('btn_prev_bam'))
        self.btn_prev_bam.clicked.connect(self._prev_bam)
        self.btn_next_bam = QPushButton(T('btn_next_bam'))
        self.btn_next_bam.clicked.connect(self._next_bam)

        btn_layout.addWidget(self.btn_prev_relevant)
        btn_layout.addWidget(self.btn_next_relevant)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_prev_pos)
        btn_layout.addWidget(self.btn_next_pos)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_prev_bam)
        btn_layout.addWidget(self.btn_next_bam)
        lay.addLayout(btn_layout)

        return g

    # ── 国际化 ──────────────────────────────────────

    def _toggle_language(self):
        self._lang = toggle_lang()
        self._retranslate_ui()

    def _retranslate_ui(self):
        """刷新所有 UI 文本"""
        self.setWindowTitle(T('window_title', version=VERSION))
        
        # Title row
        self.lang_btn.setText(T('btn_lang'))
        self.top_btn.setText(T('btn_pin'))
        self._update_collapse_btn_text()
        self._update_minimal_btn_text()
        self.help_btn.setText(T('btn_help'))
        if hasattr(self, 'settings_btn'):
            self.settings_btn.setText(T('btn_settings'))
        
        # File group labels
        self.file_group_title_label.setText("<b>" + T('file_group_title') + "</b>")
        self.table_file_label.setText(T('label_table_file'))
        self.btn_table.setText(T('btn_browse'))
        self.locus_col_label.setText(T('label_locus_col'))
        self.sample_col_label.setText(T('label_sample_col'))
        self.manual_checkbox.setText(T('manual_checkbox'))
        self.manual_pos_edit.setPlaceholderText(T('manual_placeholder'))
        self.genome_label.setText(T('label_genome'))
        self.genome_browse_btn.setText(T('btn_browse_local'))
        self.btn_remove_genome.setText(T('btn_remove_selected'))
        self.track_label.setText(T('label_track_files'))
        self.btn_add.setText(T('btn_add_tracks'))
        self.btn_auto_find.setText(T('btn_auto_find'))
        self.btn_remove.setText(T('btn_remove_selected'))
        self.btn_remove_all.setText(T('btn_remove_all'))
        self.pos_batch_label.setText(T('label_pos_batch'))
        self.bam_batch_label.setText(T('label_bam_batch'))
        self.filter_no_k_bams_check.setText(T('filter_no_k_bams'))
        self.filter_k_tracks_check.setText(T('filter_k_tracks'))
        self.post_cmd_label.setText(T('label_post_cmds'))
        self.cmd_ref_btn.setText(T('btn_cmd_ref'))
        self.post_cmds_edit.setPlaceholderText(T('post_cmds_placeholder'))
        self.port_label.setText(T('label_port'))
        self.port_spin.setToolTip(T('port_tooltip'))
        self._update_parse_btn_text()
        
        # Nav group
        self.nav_group_box.setTitle(T('nav_group_title'))
        self.pos_display.setPlaceholderText(T('pos_placeholder'))
        self.bam_display.setPlaceholderText(T('bam_placeholder'))
        self.btn_prev_relevant.setText(T('btn_prev_relevant'))
        self.btn_next_relevant.setText(T('btn_next_relevant'))
        self.btn_prev_pos.setText(T('btn_prev_pos'))
        self.btn_next_pos.setText(T('btn_next_pos'))
        self.btn_prev_bam.setText(T('btn_prev_bam'))
        self.btn_next_bam.setText(T('btn_next_bam'))
        
        # Refresh grid and status
        if hasattr(self, 'bam_batches') and self.bam_batches:
            self._build_grid()
        self._update_status()

    def _update_parse_btn_text(self):
        if not self.parse_btn.isEnabled() or self.parse_btn.text() in (T('btn_parsing'), '解析中...'):
            self.parse_btn.setText(T('btn_parsing'))
        else:
            self.parse_btn.setText(T('btn_parse'))

    def _update_collapse_btn_text(self):
        if self._is_collapsed:
            self.collapse_btn.setText(T('btn_expand'))
        else:
            self.collapse_btn.setText(T('btn_collapse'))

    def _update_minimal_btn_text(self):
        if self._is_minimal:
            self.minimal_btn.setText(T('btn_minimal_on'))
        else:
            self.minimal_btn.setText(T('btn_minimal'))

    # ── 文件操作 ──────────────────────────────────────

    def _browse_table_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, T('dlg_select_table'), "",
            T('filter_table')
        )
        if path:
            self.table_file_edit.setText(path)
            self.settings.locus_col = self._get_locus_col()
            self.settings.sample_col = self._get_sample_col()

    def _browse_genome_file(self):
        """浏览本地基因组/文件，添加到列表"""
        path, _ = QFileDialog.getOpenFileName(
            self, T('dlg_select_local'), "",
            T('filter_local')
        )
        if not path:
            return
        self._add_genome_item(path)

    def _add_genome_item(self, text: str, checked: bool = True):
        """向列表添加一项（去重），带勾选框"""
        for i in range(self.genome_list.count()):
            if self.genome_list.item(i).text() == text:
                return
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.genome_list.insertItem(0, item)

    def _remove_genome_items(self):
        """移除列表中选中的项"""
        for item in self.genome_list.selectedItems():
            row = self.genome_list.row(item)
            self.genome_list.takeItem(row)

    def _on_manual_mode_toggled(self, checked: bool):
        """手动输入模式切换：隐藏表格/列名行，显示手动输入框"""
        self.table_file_widget.setVisible(not checked)
        self.column_widget.setVisible(not checked)
        self.manual_pos_edit.setVisible(checked)

    def _toggle_collapse(self):
        """折叠/展开：隐藏文件组内容，窗口收缩/恢复"""
        if self._is_minimal:
            return  # 极简模式下折叠/展开无意义
        self._is_collapsed = not self._is_collapsed
        if self._is_collapsed:
            # 先存当前尺寸，再隐藏内容并收缩窗口
            self._saved_size = self.size()
            self.collapse_btn.setText(T('btn_expand'))
            self.file_content_widget.setVisible(False)
            self.setMinimumSize(0, 0)
            self.resize(self.width(), 420)
        else:
            self.file_content_widget.setVisible(True)
            self.collapse_btn.setText(T('btn_collapse'))
            self.setMinimumSize(900, 650)
            if hasattr(self, '_saved_size') and self._saved_size:
                self.resize(self._saved_size)

    def _toggle_minimal(self):
        """极简模式：仅保留标题栏、位置批次详情和对应批次按钮"""
        self._is_minimal = not self._is_minimal
        if self._is_minimal:
            self._saved_size_minimal = self.size()
            self.minimal_btn.setText(T('btn_minimal_on'))
            # 隐藏所有不需要的区域
            self.file_content_widget.setVisible(False)
            self.grid_table.setVisible(False)
            self.bam_display.setVisible(False)
            self.btn_prev_pos.setVisible(False)
            self.btn_next_pos.setVisible(False)
            self.btn_prev_bam.setVisible(False)
            self.btn_next_bam.setVisible(False)
            self.setMinimumSize(0, 0)
            self.resize(self.width(), 280)
        else:
            self.minimal_btn.setText(T('btn_minimal'))
            # 恢复所有区域（文件内容区根据折叠状态决定）
            self.file_content_widget.setVisible(not self._is_collapsed)
            self.grid_table.setVisible(True)
            self.bam_display.setVisible(True)
            self.btn_prev_pos.setVisible(True)
            self.btn_next_pos.setVisible(True)
            self.btn_prev_bam.setVisible(True)
            self.btn_next_bam.setVisible(True)
            self.setMinimumSize(900, 650)
            if hasattr(self, '_saved_size_minimal') and self._saved_size_minimal:
                self.resize(self._saved_size_minimal)

    def _toggle_always_on_top(self):
        """切换窗口置顶状态"""
        self._is_on_top = not self._is_on_top
        if self._is_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.top_btn.setChecked(True)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.top_btn.setChecked(False)
        self.show()  # setWindowFlags 后需重新 show

    def _parse_manual_positions(self, text: str):
        """解析手动输入的位置信息，返回 (loci, samples)。
        - 如果首行含 tab 或逗号分隔的两列，则第一列为 locus，第二列为 sample
        - 否则只有 locus 列，samples 为 None
        """
        lines = [
            l.strip() for l in text.splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        if not lines:
            return [], None

        # 检测是否有样本列：首行含 tab/逗号且可拆分为两列（第一列含 ':'）
        has_sample = False
        first = lines[0]
        if '\t' in first or ',' in first:
            delim = '\t' if '\t' in first else ','
            parts = first.split(delim, 1)
            if len(parts) == 2 and ':' in parts[0]:
                has_sample = True

        loci = []
        samples = [] if has_sample else None

        for line in lines:
            if has_sample:
                delim = None
                if '\t' in line:
                    delim = '\t'
                elif ',' in line:
                    delim = ','
                if delim:
                    parts = line.split(delim, 1)
                    if len(parts) == 2 and ':' in parts[0]:
                        loci.append(parts[0].strip())
                        samples.append(parts[1].strip())
                        continue
                if ':' in line:
                    loci.append(line)
                    samples.append("")
            else:
                if ':' in line:
                    loci.append(line)

        return loci, samples

    def _add_bam_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, T('dlg_select_tracks'), "",
            T('filter_bam')
        )
        for p in paths:
            self._add_bam_item(p)

    def _add_bam_item(self, p: str):
        existing = [
            self.bam_list.item(i).data(Qt.UserRole)
            for i in range(self.bam_list.count())
        ]
        if p in existing:
            return
        idx = self.bam_list.count() + 1
        item_text = f"[{idx}] {sample_name(p)}  ({p})"
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, p)
        self.bam_list.addItem(item)

    def _remove_bam_files(self):
        for item in self.bam_list.selectedItems():
            self.bam_list.takeItem(self.bam_list.row(item))
        self._refresh_bam_indices()

    def _remove_all_bam_files(self):
        self.bam_list.clear()

    def _refresh_bam_indices(self):
        for i in range(self.bam_list.count()):
            item = self.bam_list.item(i)
            p = item.data(Qt.UserRole)
            item.setText(f"[{i + 1}] {sample_name(p)}  ({p})")

    def _auto_find_bam_files(self):
        table_path = self.table_file_edit.text().strip()
        if not table_path:
            QMessageBox.warning(self, T('msg_title_notice'), T('msg_need_table_first'))
            return

        # 在路径中向上查找 final_out 目录
        current = os.path.dirname(os.path.abspath(table_path))
        base_dir = None
        while True:
            if os.path.basename(current).lower() == "final_out":
                base_dir = os.path.dirname(current)
                break
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent

        if not base_dir:
            QMessageBox.warning(
                self, T('msg_title_not_found'),
                T('msg_final_out_not_found')
            )
            return

        bam_out_dir = os.path.join(base_dir, "bam_out")
        if not os.path.isdir(bam_out_dir):
            QMessageBox.warning(
                self, T('msg_title_not_found'),
                T('msg_bam_out_not_found', path=bam_out_dir)
            )
            return

        bam_files = glob_module.glob(os.path.join(bam_out_dir, "*.bam"))
        if not bam_files:
            QMessageBox.warning(
                self, T('msg_title_not_found'),
                T('msg_no_bam_in_bam_out', path=bam_out_dir)
            )
            return

        # 清空现有列表并填充
        self.bam_list.clear()
        bam_files.sort()
        for p in bam_files:
            self._add_bam_item(p)

        self.status_bar.showMessage(
            T('status_auto_loaded', n=len(bam_files)), 5000
        )

    # ── 解析逻辑 ──────────────────────────────────────

    def _get_locus_col(self):
        t = self.locus_col_edit.text().strip()
        return t if t else self.locus_col_edit.placeholderText().strip()

    def _get_sample_col(self):
        t = self.sample_col_edit.text().strip()
        return t if t else self.sample_col_edit.placeholderText().strip()

    def _on_parse(self):
        # 防止重复点击
        if not self.parse_btn.isEnabled():
            return
        self.parse_btn.setEnabled(False)
        self.parse_btn.setText(T('btn_parsing'))

        port = self.port_spin.value()
        set_port(port)

        if not check_igv_port():
            self._enable_parse_btn()
            QMessageBox.warning(
                self, T('msg_title_igv_not_conn'),
                T('msg_port_unreachable', port=port)
            )
            return

        bam_paths = [
            self.bam_list.item(i).data(Qt.UserRole)
            for i in range(self.bam_list.count())
        ]
        if not bam_paths:
            self._enable_parse_btn()
            QMessageBox.warning(self, T('msg_title_error'), T('msg_need_at_least_one_bam'))
            return

        pos_batch_size = self.pos_batch_spin.value()
        bam_batch_size = self.bam_batch_spin.value()

        # ── 分支：手动输入 vs 表格文件 ──
        if self.manual_checkbox.isChecked():
            manual_text = self.manual_pos_edit.toPlainText().strip()
            if not manual_text:
                self._enable_parse_btn()
                QMessageBox.warning(self, T('msg_title_error'), T('msg_manual_empty'))
                return
            loci, samples = self._parse_manual_positions(manual_text)
            if not loci:
                self._enable_parse_btn()
                QMessageBox.warning(
                    self, T('msg_title_parse_fail'),
                    T('msg_manual_no_loci')
                )
                return
        else:
            table_path = self.table_file_edit.text().strip()
            if not table_path or not os.path.exists(table_path):
                self._enable_parse_btn()
                QMessageBox.warning(self, T('msg_title_error'), T('msg_invalid_table'))
                return
            locus_col = self._get_locus_col()
            sample_col = self._get_sample_col()
            try:
                loci, samples, _ = parse_positions(table_path, locus_col, sample_col)
            except ValueError as e:
                self._enable_parse_btn()
                QMessageBox.warning(self, T('msg_title_parse_fail'), str(e))
                return
            if not loci:
                self._enable_parse_btn()
                QMessageBox.warning(
                    self, T('msg_title_parse_fail'),
                    T('msg_no_loci_from_col', col=locus_col)
                )
                return

        self.pos_batches = make_position_batches(loci, pos_batch_size)
        self.bam_batches = make_bam_batches(bam_paths, bam_batch_size)
        self.current_pos_idx = 0
        self.current_bam_idx = 0
        self._prev_bam_idx = -1
        self._last_loaded_bams = None

        # ── K 关系计算 ──
        self._compute_k_relations(loci, samples, bam_paths, pos_batch_size,
                                  bam_batch_size)

        # ── 过滤无样本对应的轨道 ──
        if self._has_k_relation and self.filter_no_k_bams_check.isChecked():
            k_bam_indices = sorted(set(
                bam_j for (_, bam_j, _, _, _) in self.all_pairs))
            bam_paths = [bam_paths[i] for i in k_bam_indices]
            self.bam_batches = make_bam_batches(bam_paths, bam_batch_size)
            # 用过滤后的 bam_paths 重新计算 K 关系，修正 batch 索引
            self._compute_k_relations(loci, samples, bam_paths, pos_batch_size,
                                      bam_batch_size)

        self._persist_params()
        self._build_grid()
        self._navigate_to_current()

        # 解析成功后 5 秒恢复按钮
        QTimer.singleShot(5000, self._enable_parse_btn)

    def _enable_parse_btn(self):
        self.parse_btn.setEnabled(True)
        self.parse_btn.setText(T('btn_parse'))

    # ── K 关系计算 ───────────────────────────────────

    def _compute_k_relations(self, loci, samples, bam_paths,
                             pos_batch_size, bam_batch_size):
        """计算哪些网格单元格存在 K 关系（位置-样本-BAM 匹配）。
        将结果存入 self.relevant_grids（行优先排序）、self._has_k_relation、
        self.all_pairs（全局配对列表，带编号）和 self.grid_pair_info（每个网格的配对详情）。
        """
        self.relevant_grids = []
        self._has_k_relation = False
        self.all_pairs = []
        self.grid_pair_info = {}

        if not samples:
            return

        # 构建: 原始 locus 索引 → 匹配的 BAM 索引
        locus_to_bam = {}
        for i, sample in enumerate(samples):
            if not sample:
                continue
            sample_lower = sample.lower()
            for j, bam_path in enumerate(bam_paths):
                bam_name = sample_name(bam_path).lower()
                # 样本名是 BAM 文件名的前缀
                if bam_name.startswith(sample_lower):
                    locus_to_bam[i] = j
                    break

        if not locus_to_bam:
            return

        pos_batches = make_position_batches(loci, pos_batch_size)
        bam_batches = make_bam_batches(bam_paths, bam_batch_size)

        n_pos = len(pos_batches)
        n_bam = len(bam_batches)

        # ── 构建全局配对列表（带 1-based 编号）──
        pair_num = 0
        for locus_i, bam_j in sorted(locus_to_bam.items()):
            pair_num += 1
            self.all_pairs.append(
                (locus_i, bam_j, loci[locus_i],
                 sample_name(bam_paths[bam_j]), pair_num)
            )

        for bb_idx in range(n_bam):
            bb_start = bb_idx * bam_batch_size if bam_batch_size > 0 else 0
            bb_end = bb_start + len(bam_batches[bb_idx])
            for pb_idx in range(n_pos):
                pb_start = pb_idx * pos_batch_size if pos_batch_size > 0 else 0
                relevant = False
                cell_pairs = []
                for locus_i, bam_j, locus_text, bam_name, pn in self.all_pairs:
                    if pb_start <= locus_i < pb_start + len(pos_batches[pb_idx]):
                        if bb_start <= bam_j < bb_end:
                            relevant = True
                            cell_pairs.append((pn, locus_text, bam_name))
                if relevant:
                    self.relevant_grids.append((bb_idx, pb_idx))
                    self._has_k_relation = True
                    self.grid_pair_info[(bb_idx, pb_idx)] = cell_pairs

    def _persist_params(self):
        s = self.settings
        s.locus_col = self._get_locus_col()
        s.sample_col = self._get_sample_col()
        s.position_batch_size = self.pos_batch_spin.value()
        s.bam_batch_size = self.bam_batch_spin.value()
        items = []
        for i in range(self.genome_list.count()):
            it = self.genome_list.item(i)
            if it.checkState() == Qt.Checked:
                items.append(it.text().strip())
        s.genome_items = ";".join(items) if items else "hg38"
        s.tcp_commands = self.post_cmds_edit.toPlainText().strip()

    # ── 导航网格 ──────────────────────────────────────

    def _build_grid(self):
        n_pos = len(self.pos_batches)
        n_bam = len(self.bam_batches)
        self.grid_table.setRowCount(n_bam)
        self.grid_table.setColumnCount(n_pos)

        pos_headers = [T('grid_pos_header', i=i + 1) for i in range(n_pos)]
        self.grid_table.setHorizontalHeaderLabels(pos_headers)
        bam_headers = [T('grid_bam_header', i=i + 1) for i in range(n_bam)]
        self.grid_table.setVerticalHeaderLabels(bam_headers)

        # 构建有关网格的快速查找集合
        relevant_set = set(self.relevant_grids)

        for row in range(n_bam):
            for col in range(n_pos):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, (row, col))
                if self._has_k_relation and (row, col) in relevant_set:
                    item.setText("●")
                    item.setForeground(QBrush(QColor("#27ae60")))
                    font = item.font()
                    font.setPointSize(font.pointSize() + 2)
                    font.setBold(True)
                    item.setFont(font)
                self.grid_table.setItem(row, col, item)

        self.grid_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.grid_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        # 控制有关批次按钮的启用状态
        self.btn_prev_relevant.setEnabled(self._has_k_relation)
        self.btn_next_relevant.setEnabled(self._has_k_relation)

    def _pos_html(self, col: int, bam_row: int) -> str:
        """返回位置批次显示的 HTML，有 K 关系的位置用绿色标识并带配对编号"""
        import html as _html
        header = T('pos_html_header', col=col + 1, total=len(self.pos_batches))
        lines = [header]

        pair_info = self.grid_pair_info.get((bam_row, col), [])
        # 构建: locus_text → [(pair_num, bam_name), ...]
        locus_pairs = {}
        for pn, locus_text, bam_name in pair_info:
            locus_pairs.setdefault(locus_text, []).append((pn, bam_name))

        for loc in self.pos_batches[col]:
            if loc in locus_pairs:
                pair_strs = [
                    f"({pn}) {_html.escape(bn)}"
                    for pn, bn in locus_pairs[loc]
                ]
                pair_label = ", ".join(pair_strs)
                lines.append(
                    f'  <span style="color:#27ae60;font-weight:bold;">'
                    f'\u2022 {_html.escape(loc)} \u2190 {pair_label}</span>'
                )
            else:
                lines.append(f"  \u2022 {_html.escape(loc)}")

        return "<br>".join(lines)

    def _bam_html(self, bam_row: int, pos_col: int) -> str:
        """返回轨道批次显示的 HTML，有 K 关系的轨道用绿色标识并带配对编号。
        如果勾选了"不展示无位置对应的轨道"，则仅显示有 K 关系的轨道。"""
        import html as _html
        header = T('bam_html_header', row=bam_row + 1, total=len(self.bam_batches))
        lines = [header]

        pair_info = self.grid_pair_info.get((bam_row, pos_col), [])
        # 构建: bam_name → [(pair_num, locus_text), ...]
        bam_pairs = {}
        for pn, locus_text, bam_name in pair_info:
            bam_pairs.setdefault(bam_name, []).append((pn, locus_text))

        filter_k = (self.filter_k_tracks_check.isChecked() and bool(pair_info))

        for bam_path in self.bam_batches[bam_row]:
            bn = sample_name(bam_path)
            if bn in bam_pairs:
                pair_strs = [
                    f"({pn}) {_html.escape(lt)}"
                    for pn, lt in bam_pairs[bn]
                ]
                pair_label = ", ".join(pair_strs)
                lines.append(
                    f'  <span style="color:#27ae60;font-weight:bold;">'
                    f'\u2022 {_html.escape(bn)} \u2190 {pair_label}</span>'
                )
            elif not filter_k:
                lines.append(f"  \u2022 {_html.escape(bn)}")

        return "<br>".join(lines)

    def _highlight_cell(self, row: int, col: int):
        for r in range(self.grid_table.rowCount()):
            for c in range(self.grid_table.columnCount()):
                item = self.grid_table.item(r, c)
                if item:
                    item.setBackground(QBrush(NORMAL_BG))

        item = self.grid_table.item(row, col)
        if item:
            item.setBackground(QBrush(CURRENT_BG))
            self.grid_table.scrollToItem(item)

    def _on_cell_clicked(self, row: int, col: int):
        if self._cell_click_in_progress:
            return
        self.current_bam_idx = row
        self.current_pos_idx = col
        self._navigate_to_current()

    def _on_current_cell_changed(self, row: int, col: int, prev_row: int,
                                 prev_col: int):
        if row < 0 or col < 0:
            return
        self._update_cell_display(row, col)

    def eventFilter(self, obj, event):
        if obj is self.grid_table and event.type() == QEvent.KeyPress:
            key = event.key()
            row = self.grid_table.currentRow()
            col = self.grid_table.currentColumn()
            n_rows = self.grid_table.rowCount()
            n_cols = self.grid_table.columnCount()

            if key in (Qt.Key_Return, Qt.Key_Enter):
                if row >= 0 and col >= 0:
                    self._on_cell_clicked(row, col)
                return True

            if key == Qt.Key_Right:
                if col == n_cols - 1 and row < n_rows - 1:
                    self.grid_table.setCurrentCell(row + 1, 0)
                    return True

            if key == Qt.Key_Left:
                if col == 0 and row > 0:
                    self.grid_table.setCurrentCell(row - 1, n_cols - 1)
                    return True

        return super().eventFilter(obj, event)

    def _update_cell_display(self, row: int, col: int):
        if not self.bam_batches or not self.pos_batches:
            return
        if row >= len(self.bam_batches) or col >= len(self.pos_batches):
            return
        self.pos_display.setHtml(self._pos_html(col, row))
        self.bam_display.setHtml(self._bam_html(row, col))

    # ── 导航逻辑 ──────────────────────────────────────

    def _navigate_to_current(self):
        if not self.bam_batches or not self.pos_batches:
            return

        self._cell_click_in_progress = True
        try:
            # 读取所有勾选的项目（checkbox checked）
            # 基因组引用识别规则：
            #   - 非文件路径（如 "hg38"） → 内置基因组 ID → 参考基因组
            #   - .fa / .fasta / .genome 文件 → 参考基因组文件
            #   - 其他文件 → 附加资源（如 .gtf / .bed / .vcf）
            checked_items = []
            for i in range(self.genome_list.count()):
                it = self.genome_list.item(i)
                if it.checkState() == Qt.Checked:
                    checked_items.append(it.text().strip())
            if not checked_items:
                checked_items = ["hg38"]

            genome = None
            extra_files = []
            for it in checked_items:
                if os.path.isfile(it):
                    ext = os.path.splitext(it)[1].lower()
                    if ext in ('.fa', '.fasta', '.genome') and genome is None:
                        genome = it
                    else:
                        extra_files.append(it)
                else:
                    if genome is None:
                        genome = it
            if genome is None:
                genome = "hg38"

            set_genome(genome)
            bam_changed = self.current_bam_idx != self._prev_bam_idx
            # 如果在同 BAM 行内从无关网格切换到有关网格且勾选了过滤，
            # 需强制重载以应用 K 关系过滤
            if not bam_changed and self._has_k_relation \
                    and self.filter_k_tracks_check.isChecked():
                target_pair = self.grid_pair_info.get(
                    (self.current_bam_idx, self.current_pos_idx), [])
                if target_pair:
                    # 计算待加载的过滤后轨道集合，与 IGV 当前集合比较
                    k_bam_names = set(
                        bam_name for (pn, lt, bam_name) in target_pair)
                    pending_bams = frozenset(
                        sample_name(b) for b in self.bam_batches[self.current_bam_idx]
                        if sample_name(b) in k_bam_names)
                    if pending_bams != self._last_loaded_bams:
                        bam_changed = True
            if bam_changed:
                bams_to_load = self.bam_batches[self.current_bam_idx]
                # 如果勾选了"不展示无位置对应的轨道"且当前是有关网格，
                # 则仅加载有 K 关系的轨道
                if self._has_k_relation and self.filter_k_tracks_check.isChecked():
                    pair_info = self.grid_pair_info.get(
                        (self.current_bam_idx, self.current_pos_idx), [])
                    if pair_info:
                        k_bam_names = set(
                            bam_name for (pn, lt, bam_name) in pair_info)
                        bams_to_load = [b for b in bams_to_load
                                        if sample_name(b) in k_bam_names]
                # 1) 通过 session XML 加载基因组 + BAM 轨道
                ok = load_bam_batch(bams_to_load)
                if not ok:
                    self._show_igv_error()
                    return
                self._prev_bam_idx = self.current_bam_idx
                self._last_loaded_bams = frozenset(
                    sample_name(b) for b in bams_to_load)
                # 2) 附加文件通过独立 HTTP load 命令逐个加载
                for extra_path in extra_files:
                    if not igv_cmd("load", {"file": extra_path}):
                        logger.warning("附加文件加载失败: %s", extra_path)
            goto_loci(self.pos_batches[self.current_pos_idx])
            # 延迟执行后处理命令：IGV 收到 HTTP 命令后需要时间加载和渲染
            delay = 2500 if bam_changed else 800
            cmds = self.post_cmds_edit.toPlainText().strip().splitlines()
            cmds = [c.strip() for c in cmds if c.strip()]
            QTimer.singleShot(delay, lambda: run_tcp_commands(cmds))
            self._highlight_cell(self.current_bam_idx, self.current_pos_idx)
            self._update_cell_display(self.current_bam_idx,
                                      self.current_pos_idx)
            self._update_status()
        finally:
            QTimer.singleShot(200,
                              lambda: setattr(self, '_cell_click_in_progress',
                                              False))

    def _update_status(self):
        self.status_bar.showMessage(
            T('status_format',
              bam=self.current_bam_idx + 1,
              bam_total=len(self.bam_batches),
              pos=self.current_pos_idx + 1,
              pos_total=len(self.pos_batches))
        )

    def _show_igv_error(self):
        port = self.port_spin.value() if hasattr(self, 'port_spin') else 60151
        QMessageBox.warning(
            self, T('msg_title_igv_conn_fail'),
            T('msg_igv_conn_fail', port=port)
        )

    # ── 按钮导航 ──────────────────────────────────────

    def _next_pos(self):
        if not self.pos_batches:
            return
        n_pos = len(self.pos_batches)
        n_bam = len(self.bam_batches)
        if self.current_pos_idx + 1 < n_pos:
            self.current_pos_idx += 1
        elif self.current_bam_idx + 1 < n_bam:
            self.current_bam_idx += 1
            self.current_pos_idx = 0
        else:
            self.current_bam_idx = 0
            self.current_pos_idx = 0
        self._navigate_to_current()

    def _prev_pos(self):
        if not self.pos_batches:
            return
        n_pos = len(self.pos_batches)
        n_bam = len(self.bam_batches)
        if self.current_pos_idx - 1 >= 0:
            self.current_pos_idx -= 1
        elif self.current_bam_idx - 1 >= 0:
            self.current_bam_idx -= 1
            self.current_pos_idx = n_pos - 1
        else:
            self.current_bam_idx = n_bam - 1
            self.current_pos_idx = n_pos - 1
        self._navigate_to_current()

    def _next_bam(self):
        if not self.bam_batches:
            return
        n_bam = len(self.bam_batches)
        self.current_bam_idx = (self.current_bam_idx + 1) % n_bam
        self._navigate_to_current()

    def _prev_bam(self):
        if not self.bam_batches:
            return
        n_bam = len(self.bam_batches)
        self.current_bam_idx = (self.current_bam_idx - 1) % n_bam
        self._navigate_to_current()

    def _next_relevant(self):
        """跳转到下一个有关网格（跳过无关网格），行优先顺序"""
        if not self.relevant_grids:
            return
        current = (self.current_bam_idx, self.current_pos_idx)
        for grid in self.relevant_grids:  # 已按 (bam, pos) 排序
            if grid > current:
                self.current_bam_idx, self.current_pos_idx = grid
                self._navigate_to_current()
                return
        # 回绕到第一个
        self.current_bam_idx, self.current_pos_idx = self.relevant_grids[0]
        self._navigate_to_current()

    def _prev_relevant(self):
        """跳转到上一个有关网格（跳过无关网格），行优先顺序"""
        if not self.relevant_grids:
            return
        current = (self.current_bam_idx, self.current_pos_idx)
        for grid in reversed(self.relevant_grids):
            if grid < current:
                self.current_bam_idx, self.current_pos_idx = grid
                self._navigate_to_current()
                return
        # 回绕到最后一个
        self.current_bam_idx, self.current_pos_idx = self.relevant_grids[-1]
        self._navigate_to_current()

    # ── 设置对话框 ────────────────────────────────────

    def _open_help(self):
        dlg = HelpDialog(self, lang=self._lang)
        dlg.exec_()

    def _open_cmd_reference(self):
        dlg = CmdReferenceDialog(self, lang=self._lang)
        dlg.exec_()

    def _open_settings(self):
        try:
            dlg = SettingsDialog(self)
            dlg.exec_()
        except Exception as e:
            QMessageBox.warning(self, T('msg_title_settings_err'),
                                T('msg_settings_error', error=e))

    def _open_log_viewer(self):
        dlg = LogViewerDialog(self)
        dlg.exec_()

    # ── 启动时恢复参数 ────────────────────────────────

    def _load_settings(self):
        s = self.settings
        set_port(s.igv_port)
        self.locus_col_edit.setText(s.locus_col)
        self.sample_col_edit.setText(s.sample_col)
        self.pos_batch_spin.setValue(s.position_batch_size)
        self.bam_batch_spin.setValue(s.bam_batch_size)

        # 填充基因组/附加文件列表（持久化项目优先，内置基因组在后，去重，带勾选框）
        # 规则：仅上次勾选过的项目默认勾选，内置基因组默认不勾选
        saved_items_str = s.genome_items
        saved_items = [x.strip() for x in saved_items_str.split(";") if x.strip()] if saved_items_str else ["hg38"]
        builtin = scan_igv_genomes()
        self.genome_list.clear()
        seen = set()
        saved_set = set(saved_items)
        for item_text in saved_items + builtin:
            if item_text and item_text not in seen:
                it = QListWidgetItem(item_text)
                it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
                it.setCheckState(Qt.Checked if item_text in saved_set else Qt.Unchecked)
                self.genome_list.addItem(it)
                seen.add(item_text)

        # 恢复后处理命令，默认 "sort base"
        saved_cmds = s.tcp_commands
        if saved_cmds:
            self.post_cmds_edit.setPlainText(saved_cmds)
        else:
            self.post_cmds_edit.setPlainText("sort base")