"""
持久化配置管理
基于 QSettings，用户设置后下次打开自动恢复
"""

import sys

from PyQt5.QtCore import QSettings


class AppSettings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = QSettings("IGV", "BatchNavigator")
        return cls._instance

    @property
    def python_exe_path(self) -> str:
        return self._settings.value("python_exe_path", sys.executable)

    @python_exe_path.setter
    def python_exe_path(self, val: str):
        self._settings.setValue("python_exe_path", val)

    # ── 旧列名（保留兼容，已不再使用）──
    @property
    def chrom_col(self) -> str:
        return self._settings.value("chrom_col", "CHROM")

    @chrom_col.setter
    def chrom_col(self, val: str):
        self._settings.setValue("chrom_col", val)

    @property
    def pos_col(self) -> str:
        return self._settings.value("pos_col", "POS")

    @pos_col.setter
    def pos_col(self, val: str):
        self._settings.setValue("pos_col", val)

    # ── 新列名 ──
    @property
    def locus_col(self) -> str:
        return self._settings.value("locus_col", "CHROM:POS")

    @locus_col.setter
    def locus_col(self, val: str):
        self._settings.setValue("locus_col", val)

    @property
    def sample_col(self) -> str:
        return self._settings.value("sample_col", "sample")

    @sample_col.setter
    def sample_col(self, val: str):
        self._settings.setValue("sample_col", val)

    @property
    def position_batch_size(self) -> int:
        val = self._settings.value("position_batch_size", 5)
        try:
            return int(val)
        except (TypeError, ValueError):
            return 5

    @position_batch_size.setter
    def position_batch_size(self, val: int):
        self._settings.setValue("position_batch_size", val)

    @property
    def bam_batch_size(self) -> int:
        val = self._settings.value("bam_batch_size", 2)
        try:
            return int(val)
        except (TypeError, ValueError):
            return 2

    @bam_batch_size.setter
    def bam_batch_size(self, val: int):
        self._settings.setValue("bam_batch_size", val)

    @property
    def genome_items(self) -> str:
        """分号分隔的基因组/文件列表"""
        return self._settings.value("genome_items", "hg38")

    @genome_items.setter
    def genome_items(self, val: str):
        self._settings.setValue("genome_items", val)

    @property
    def tcp_commands(self) -> str:
        return self._settings.value("tcp_commands", "sort base")

    @tcp_commands.setter
    def tcp_commands(self, val: str):
        self._settings.setValue("tcp_commands", val)

    @property
    def igv_port(self) -> int:
        port = self._settings.value("igv_port", 60151)
        return int(port)

    @igv_port.setter
    def igv_port(self, val: int):
        self._settings.setValue("igv_port", int(val))