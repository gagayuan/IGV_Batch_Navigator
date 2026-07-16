"""
IGV 批量导航器 {VERSION} - 入口
PyQt5 GUI 客户端，基于 run.py 的逻辑
"""

import sys
import traceback
import os
import logging

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

from log_dialog import init_logging
from main_window import MainWindow
from version import VERSION
from i18n import T

IS_FROZEN = getattr(sys, "frozen", False)


def _resource_path(relative: str) -> str:
    """PyInstaller 打包后获取数据文件路径"""
    if IS_FROZEN:
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)


def _show_crash_dialog(exc_info: str):
    """在 --windowed 模式下没有控制台，弹窗显示崩溃信息并写入日志"""
    logging.error(T('msg_unhandled_exception', exc_info=exc_info))
    log_path = os.path.join(os.path.dirname(sys.executable), "crash.log")
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(exc_info)
    except OSError:
        pass
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    QMessageBox.critical(
        None,
        T('msg_title_program_err'),
        T('msg_program_error', log_path=log_path, exc_info=exc_info[-600:]),
    )


def main():
    try:
        # 必须在 QApplication 之前设置，否则 Windows 任务栏图标不会生效
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("iict.igv.navigator")
        except Exception:
            pass

        log_dir = os.path.dirname(sys.executable) if IS_FROZEN else os.path.dirname(
            os.path.abspath(__file__)
        )
        log_path = os.path.join(log_dir, "igv_navigator.log")
        init_logging(log_path)

        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        icon_path = _resource_path("icon.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            app.setWindowIcon(app_icon)

        window = MainWindow()
        if os.path.exists(icon_path):
            window.setWindowIcon(app_icon)
        window.show()

        # PyInstaller --windowed 模式下，show() 后需再设一次 AppUserModelID
        # 才能让任务栏正确显示图标
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("iict.igv.navigator")
        except Exception:
            pass

        logging.info("IGV 批量导航器 %s 启动完成", VERSION)
        sys.exit(app.exec_())
    except Exception:
        _show_crash_dialog(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()