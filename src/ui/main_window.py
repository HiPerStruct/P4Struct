# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

from config import common

class P4SMainWindow(QtWidgets.QMainWindow):
    
    def __init__(self) -> None:
        super().__init__(flags=QtCore.Qt.Window)
        self.setObjectName('main-window-widget')
        
        self.work_path = None
        self.ins_project_database = None
        
        self.__app_show_state = False
        
        self.__initizalizeDefaultFolders()
        self.__initizalizeWidgetStyle()
        self.__initizalizeMainMenubar()
        self.__initizalizeMainToolbar()
        self.__initizalizeVisualizationToolbar()
        self.__initizalizeManagerDockWidget()
        self.__initizalizeMessageDockWidget()
        self.__initizalizeVisualizationCentralStackedWidget()

    def __initizalizeDefaultFolders(self) -> None:
        
        DEFAULT_WORK_PATH = os.sep.join([os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"P4STemp"])
        DEFAULT_PLUGINS_PATH = os.sep.join([os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"P4SPlugins"])

        if os.path.isdir(DEFAULT_WORK_PATH):
            pass
        else:
            os.makedirs(DEFAULT_WORK_PATH)
        if os.path.isdir(DEFAULT_PLUGINS_PATH):
            pass
        else:
            os.makedirs(DEFAULT_PLUGINS_PATH)
    
        self.work_path = DEFAULT_WORK_PATH
    
    def __initizalizeWidgetStyle(self) -> None:
        DEFAULT_WORK_PATH = os.sep.join([os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"P4STemp"])
        self.setWindowTitle(f'{common.P4SString.VERSION_NUMBER} | Path - {DEFAULT_WORK_PATH}')
        self.setWindowIcon(QtGui.QIcon(r':image/images/AppIcon.png'))
        self.resize(int(self.screen().size().width()*0.5),int(self.screen().size().height()*0.5))
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        
        self.setStyleSheet("""
                    QWidget
                    { 
                        font: normal normal 12pt Microsoft Ya Hei;
                    }

                    QToolBar
                    {
                        border: 1px solid rgba(187, 182, 182, 255);
                    }

                    QToolTip
                    {
                        font: normal normal 12pt Microsoft Ya Hei;
                    }

                    QTabBar::tab:selected
                    {
                        font-size: 14pt;
                        color: rgba(255, 255, 255, 255);
                        background-color: rgba(130, 131, 133, 255);
                    }

                    QTreeWidget
                    {
                        font: normal 500 12pt Microsoft Ya Hei;
                        color: 'white';
                        background-color: rgba(94, 94, 97, 255);;
                    }


                    QMenuBar#main-menubar
                    {
                        font: normal 400 15pt Microsoft Ya Hei;
                        padding: 2px;
                        width: 100px;
                        background-color: rgba(192, 201, 211, 255);
                    }
                    QMenuBar#main-menubar::item
                    {
                        margin-top: 1px;
                        padding: 2px;
                        border-radius: 5px;
                    }
                    QMenuBar#main-menubar::item:selected
                    {
                        border-right: 2px solid;
                        border-bottom: 2px solid;
                        color: rgba(255, 255, 255, 255);
                        background-color: rgba(53, 52, 56, 255);
                    }

                    QLabel#model-label,#model-type-label,#model-dimension-label,#result-database-label,#contour-label,#graph-label
                    {
                        font-size: 13pt;
                        border-radius: 5px;
                        background-color: rgba(200, 200, 200, 255);
                    }

                    QDoubleSpinBox#spin-box-without-arrow::up-button
                    {
                        width:0px;
                    }
                    QDoubleSpinBox#spin-box-without-arrow::down-button
                    {
                        width:0px;
                    }
                    QDoubleSpinBox#rotation-angle-spin::up-button
                    {
                        width:0px;
                    }
                    QDoubleSpinBox#rotation-angle-spin::down-button
                    {
                        width:0px;
                    }

                    QSpinBox#spin-box-without-arrow::up-button
                    {
                        width:0px;
                    }
                    QSpinBox#spin-box-without-arrow::down-button
                    {
                        width:0px;
                    }

                    QTableWidget#attribute-parameters-table
                    {
                        background-color: rgba(200, 200, 200, 255);
                    }

                    QWidget#widget-with-border
                    {
                        border: 2px solid black;
                    }

                    QListWidget::item:hover{
                        background: rgba(204, 229, 255, 255)
                    }
                    QListWidget::item:selected{
                        color: rgba(0, 0, 0, 255);
                        background:rgba(192, 192, 192, 255);
                    }

                    QTableWidget#objective-table,#constrain-table
                    {
                        border: 1px solid black;
                    }
                    QTableWidget#objective-table::item:selected
                    {
                        background-color: black;
                    }
                    QTableWidget#constrain-table::item:selected
                    {
                        background-color: black;
                    }""")

    
    def __initizalizeMainMenubar(self) -> None:
        from .menubar import P4SMainMenubar
        P4SMainMenubar(self)
        del P4SMainMenubar
    
    def __initizalizeMainToolbar(self) -> None:
        from .toolbar import P4SMainToolbar
        P4SMainToolbar(self)
        del P4SMainToolbar
    
    def __initizalizeVisualizationToolbar(self) -> None:
        from .toolbar import P4SVisualizationToolbar
        P4SVisualizationToolbar(self)
        del P4SVisualizationToolbar
    
    def __initizalizeManagerDockWidget(self) -> None:
        ins_manager_dock_widget = QtWidgets.QDockWidget('Manager',parent=self,allowedAreas=QtCore.Qt.LeftDockWidgetArea,features=QtWidgets.QDockWidget.DockWidgetFloatable)
        ins_manager_dock_widget.setObjectName('manager-dock-widget')
        ins_manager_dock_widget.setMinimumWidth(480)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,ins_manager_dock_widget)
        
        ins_manager_tab_widget = QtWidgets.QTabWidget(ins_manager_dock_widget)
        ins_manager_dock_widget.setWidget(ins_manager_tab_widget)

        from .manager import P4SModelManager
        ins_model_manager = P4SModelManager(ins_manager_tab_widget)
        del P4SModelManager
        ins_manager_tab_widget.addTab(ins_model_manager,'Models')
        
        from .manager import P4SResultManager
        ins_result_manager = P4SResultManager(ins_manager_tab_widget)
        del P4SResultManager
        ins_manager_tab_widget.addTab(ins_result_manager,'Results')
        
        ins_manager_tab_widget.currentChanged.connect(self.__changeManagerVisualization)
    # region
    def __changeManagerVisualization(self,in_tab_index:int) -> None:
        ins_visualization_toolbar = self.findChild(QtCore.QObject,'visualization-toolbar')
        ins_visualization_toolbar.clearToolsState()
        
        self.centralWidget().setCurrentIndex(in_tab_index)
        self.centralWidget().currentWidget().activatePreviousSubWindow()
    # endregion
    
    def __initizalizeMessageDockWidget(self) -> None:
        ins_message_dock_widget = QtWidgets.QDockWidget('Message',parent=self,allowedAreas=QtCore.Qt.BottomDockWidgetArea,features=QtWidgets.QDockWidget.DockWidgetFloatable)
        ins_message_dock_widget.setObjectName('message-dock-widget')
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,ins_message_dock_widget)
        
        ins_text_browser = QtWidgets.QTextBrowser()
        ins_text_browser.setObjectName('message-text-browser')
        ins_text_browser.setReadOnly(True)
        ins_message_dock_widget.setWidget(ins_text_browser)
    
    def __initizalizeVisualizationCentralStackedWidget(self) -> None:
        ins_visualization_stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(ins_visualization_stacked_widget)
        
        ins_models_mdi_area = QtWidgets.QMdiArea(ins_visualization_stacked_widget)
        ins_visualization_stacked_widget.addWidget(ins_models_mdi_area)
        
        ins_results_mdi_area = QtWidgets.QMdiArea(ins_visualization_stacked_widget)
        ins_visualization_stacked_widget.addWidget(ins_results_mdi_area)
    
    def showEvent(self,event:object) -> None:
        if self.__app_show_state: 
            return None
        else:
            print("Start Tips:")
            print(f"-- Hello, Welcome to {common.P4SString.VERSION_NUMBER}!")

            for file_name in os.listdir(self.work_path):
                if file_name.endswith(".p4st_temp"):
                    os.remove(os.sep.join([self.work_path,file_name]))
                elif file_name.endswith(".p4st_temp-journal"):
                    os.remove(os.sep.join([self.work_path,file_name]))
                elif file_name.endswith(".p4st-journal"):
                    os.remove(os.sep.join([self.work_path,file_name]))
                elif file_name.endswith(".pro"):
                    os.remove(os.sep.join([self.work_path,file_name]))
                else:   continue

            self.__app_show_state = True
    def closeEvent(self,event:object) -> None:
        ins_main_menubar = self.menuBar()
        if ins_main_menubar.isEnabled():
            pass
        else:
            QtWidgets.QMessageBox.warning(self,'Exit P4Struct Waring','Please exit edit/show state of visualization first!')
            event.ignore()
            return None
        
        ins_main_toolbar = self.findChild(QtCore.QObject,'main-toolbar')
        if ins_main_toolbar.getRuningTaskNumber() != 0:
            QtWidgets.QMessageBox.warning(self,'Close P4Struct Waring','There are still tasks in running!')
            event.ignore()
            return None
        else:
            pass
        
        if self.ins_project_database is None:
            for file_name in os.listdir(self.work_path):
                if file_name.endswith(".p4st_temp"):
                    os.remove(os.sep.join([self.work_path,file_name]))
                elif file_name.endswith(".p4st_temp-journal"):
                    os.remove(os.sep.join([self.work_path,file_name]))
                elif file_name.endswith(".p4st-journal"):
                    os.remove(os.sep.join([self.work_path,file_name]))
                elif file_name.endswith(".pro"):
                    os.remove(os.sep.join([self.work_path,file_name]))
                else:   continue

            for ins_result_visual_window in self.centralWidget().widget(1).subWindowList():
                ins_result_visual_window.finalizeInteractor()

            print("\nEnd Tips:")
            print("-- You have exited successfully!")

            event.accept()
        else:
            response_to_exit = QtWidgets.QMessageBox.question(self,'Exit P4Struct Question','Unsaved data will be lost,exit?',defaultButton=QtWidgets.QMessageBox.StandardButton.No)
            
            if response_to_exit is QtWidgets.QMessageBox.StandardButton.Yes:
                self.ins_project_database.closeProjectDatabase()

                for ins_model_visual_window in self.centralWidget().widget(0).subWindowList():
                    ins_model_visual_window.finalizeInteractor()
                for file_name in os.listdir(self.work_path):
                    if file_name.endswith(".p4st_temp"):
                        os.remove(os.sep.join([self.work_path,file_name]))
                    elif file_name.endswith(".p4st_temp-journal"):
                        os.remove(os.sep.join([self.work_path,file_name]))
                    elif file_name.endswith(".p4st-journal"):
                        os.remove(os.sep.join([self.work_path,file_name]))
                    elif file_name.endswith(".pro"):
                        os.remove(os.sep.join([self.work_path,file_name]))
                    else:   continue

                for ins_result_visual_window in self.centralWidget().widget(1).subWindowList():
                    ins_result_visual_window.finalizeInteractor()

                print("\nEnd Tips:")
                print("-- You have exited successfully!")

                event.accept()
            else:
                event.ignore()
                return None
    
    def createProjectDatabase(self, in_full_project_name:str) -> None:
        from db.project import P4SProjectDatabase
        self.ins_project_database = P4SProjectDatabase(in_full_project_name,True)
        del P4SProjectDatabase
    def openProjectDatabase(self, in_full_project_name:str) -> None:
        from db.project import P4SProjectDatabase
        self.ins_project_database = P4SProjectDatabase(in_full_project_name,False)
        del P4SProjectDatabase
    def printMessage(self, in_text:str) -> None:
        ins_text_browser = self.findChild(QtWidgets.QTextBrowser,'message-text-browser')
        ins_text_browser.append(in_text)
    def clearMessage(self) -> None:
        ins_text_browser = self.findChild(QtWidgets.QTextBrowser,'message-text-browser')
        ins_text_browser.clear()
