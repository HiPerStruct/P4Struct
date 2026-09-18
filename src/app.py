# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import sys

from PySide6 import QtWidgets
from PySide6 import QtCore


if __name__ == "__main__":

    mkl_lib_path = os.sep.join([os.path.dirname(os.path.dirname(__file__)),r'libs\mkl_rt.2.dll'])
    if os.path.exists(mkl_lib_path) is False:
        print("The file 'mkl_rt.2.dll' is missing!")
        sys.exit()
    else:
        mkl_lib_env_path = os.environ.get('PYPARDISO_MKL_RT')

        if mkl_lib_env_path is None:
            import winreg 
            ins_windows_registry = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(ins_windows_registry, 'PYPARDISO_MKL_RT', 0, winreg.REG_EXPAND_SZ, mkl_lib_path)
            winreg.CloseKey(ins_windows_registry)

            os.environ['PYPARDISO_MKL_RT'] = mkl_lib_path
        else:
            if os.path.exists(mkl_lib_env_path) is False:
                import winreg                         
                ins_windows_registry = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(ins_windows_registry, 'PYPARDISO_MKL_RT', 0, winreg.REG_EXPAND_SZ, mkl_lib_path)
                winreg.CloseKey(ins_windows_registry)

                os.environ['PYPARDISO_MKL_RT'] = mkl_lib_path
            elif os.path.samefile(mkl_lib_env_path,mkl_lib_path) is False:
                import winreg        
                ins_windows_registry = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(ins_windows_registry, 'PYPARDISO_MKL_RT', 0, winreg.REG_EXPAND_SZ, mkl_lib_path)
                winreg.CloseKey(ins_windows_registry)

                os.environ['PYPARDISO_MKL_RT'] = mkl_lib_path
            else:
                pass
    
    from ui import main_window

    QtCore.qInstallMessageHandler(main_window.qtMessageHandler)

    ins_app = QtWidgets.QApplication(sys.argv)
    if len(ins_app.arguments()) == 1:
        pass
    else:
        print("Command mode is currently not supportd!")
        sys.exit()

    ins_main_window = main_window.P4SMainWindow()
    ins_main_window.show()

    sys.exit(ins_app.exec())
