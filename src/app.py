# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later


import sys

from PySide6 import QtWidgets


if __name__ == "__main__":

    ins_app = QtWidgets.QApplication(sys.argv)
    
    from ui import P4SMainWindow
    ins_main_window = P4SMainWindow()
    ins_main_window.show()

    sys.exit(ins_app.exec())


