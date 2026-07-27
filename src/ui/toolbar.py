# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import sqlite3
import multiprocessing
import shutil
import glob

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
import h5py
import numpy
import psutil
import datetime

from config import common
from analysis.finite_element_analysis import intoFEAProcess
from analysis.optimizatoin_analysis import intoOPTProcess


class P4SMainToolbar(QtCore.QObject):

    def __init__(self, in_parent:object) -> None:
        super().__init__(parent=in_parent,objectName='main-toolbar')
        
        self.__initializeWindowTools(in_parent)
        self.__initializeModelManagerTools(in_parent)
        self.__initializeResultManagerTools(in_parent)
        self.__initializeFunctionTools(in_parent)
        
        self.__ins_task_manager = _CreateFiniteElementAnalysisTaskManager(in_parent)
        self.__ins_optimization_task_manager = _CreateOptimizationTaskManager(in_parent)

    def __initializeWindowTools(self, in_parent:object) -> None:
        ins_window_tools = QtWidgets.QToolBar(in_parent,allowedAreas=QtCore.Qt.TopToolBarArea,iconSize=QtCore.QSize(28,28),floatable=False,toolButtonStyle=QtCore.Qt.ToolButtonIconOnly)
        ins_window_tools.setObjectName('window-toolbar')
        ins_window_tools.setFixedWidth(90)
        in_parent.addToolBar(ins_window_tools)
        
        ins_show_viewports_tool = ins_window_tools.addAction(QtGui.QIcon(':/image/images/ToolShowViewports.png'),'')
        ins_show_viewports_tool.setToolTip('show viewports')
        ins_show_viewports_tool.triggered.connect(self.__slotShowViewports)
        
        ins_tile_viewports_tool = ins_window_tools.addAction(QtGui.QIcon(':/image/images/ToolTileViewports.png'),'')
        ins_tile_viewports_tool.setToolTip('tile viewports')
        ins_tile_viewports_tool.triggered.connect(self.__slotTileViewports)
    # region
    def __slotShowViewports(self) -> None:
        ins_main_window = self.parent()
        ins_model_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,"model-manager-toolbar")
        
        QtWidgets.QMessageBox.warning(ins_model_toolbar,'Tool Waring',"Coming soon!")
    def __slotTileViewports(self) -> None:
        ins_main_window = self.parent()
        ins_model_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,"model-manager-toolbar")
        
        QtWidgets.QMessageBox.warning(ins_model_toolbar,'Tool Waring',"Coming soon!")
    # endregion
    
    def __initializeModelManagerTools(self, in_parent:object) -> None:
        ins_model_toolbar = QtWidgets.QToolBar(in_parent,allowedAreas=QtCore.Qt.TopToolBarArea,iconSize=QtCore.QSize(28,28),floatable=False)
        ins_model_toolbar.setObjectName('model-manager-toolbar')
        ins_model_toolbar.setFixedWidth(155)
        in_parent.addToolBar(ins_model_toolbar)
        
        ins_create_model_tool = ins_model_toolbar.addAction(QtGui.QIcon(':/image/images/ManagerCreateModel.png'),'')
        ins_create_model_tool.setToolTip('create model')
        ins_create_model_tool.triggered.connect(self.__slotCreateModel)
        
        ins_import_model_tool = ins_model_toolbar.addAction(QtGui.QIcon(':/image/images/ManagerImportModel.png'),'')
        ins_import_model_tool.setToolTip('import model')
        ins_import_model_tool.triggered.connect(self.__slotImportModel)

        ins_rename_model_tool = ins_model_toolbar.addAction(QtGui.QIcon(':/image/images/ManagerRenameModel.png'),'')
        ins_rename_model_tool.setToolTip('rename model')
        ins_rename_model_tool.triggered.connect(self.__slotRenameModel)
        
        ins_remove_model_tool = ins_model_toolbar.addAction(QtGui.QIcon(':/image/images/ManagerRemoveModel.png'),'')
        ins_remove_model_tool.setToolTip('remove model')
        ins_remove_model_tool.triggered.connect(self.__slotRemoveModel)
    # region
    def __slotCreateModel(self) -> None:
        ins_main_window = self.parent()
        ins_model_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,"model-manager-toolbar")
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(0)
        
        if ins_main_window.ins_project_database is None:
            QtWidgets.QMessageBox.warning(ins_model_toolbar,'Create Model Waring','None project exist!')
            return None
        else:   pass

        ins_create_model_dialog = _CreateModelDialog(ins_model_toolbar)
        ins_create_model_dialog.show()
        if ins_create_model_dialog.exec() == QtWidgets.QDialog.Accepted:
            model_name = ins_create_model_dialog.getModelName()
            model_dimension = ins_create_model_dialog.getModelDimension()
            
            ins_main_window.ins_project_database.createModel(model_name,model_dimension)
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            from .visualization import P4SModelVisualWindow
            P4SModelVisualWindow(ins_models_mdi_area,model_name)
            del P4SModelVisualWindow
            
            ins_model_manager = ins_manager_tab_widget.currentWidget()
            ins_model_manager.createModelManager(model_name, model_dimension)

            ins_main_window.printMessage(f'Model "{model_name}" successfully created!')
        else:
            pass
        ins_create_model_dialog.deleteLater()
    def __slotImportModel(self) -> None:
        ins_main_window = self.parent()
        ins_model_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,"model-manager-toolbar")
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(0)
        
        if ins_main_window.ins_project_database is None:
            QtWidgets.QMessageBox.warning(ins_model_toolbar,'Import Model Waring','None project exist!')
            return None
        else:   pass
                
        project_full_name,_ = QtWidgets.QFileDialog.getOpenFileName(ins_model_toolbar,'Select Project File',ins_main_window.work_path,'P4Struct File(*.p4st)')
        if project_full_name == '':
            return None
        elif os.path.samefile(ins_main_window.ins_project_database.getFullProjectName(),project_full_name):
            QtWidgets.QMessageBox.warning(ins_model_toolbar,'Import Model Waring','The project has been opened!')
            return None
        else:
            pass
        
        project_indlude_models_by_dimension_dict = {'2D':[],'3D':[]}
        try:
            ins_project_database = sqlite3.connect(project_full_name,isolation_level=None)
            ins_cursor = ins_project_database.cursor()
            
            ins_cursor.execute('SELECT name,dimension FROM models')
            models_info_list = ins_cursor.fetchall()
            if models_info_list is None:
                pass
            else:
                for model_name,model_dimension in models_info_list:
                    project_indlude_models_by_dimension_dict[model_dimension].append(model_name)
        except:
            ins_cursor.close()
            ins_project_database.close()
            
            QtWidgets.QMessageBox.critical(ins_model_toolbar,'Imoprt Model Error','Project file read error!')
            return None
        else:
            ins_cursor.close()
            ins_project_database.close()
            
            ins_import_model_dialog = _ImportModelDialog(ins_model_toolbar,project_indlude_models_by_dimension_dict)
            ins_import_model_dialog.show()
            if ins_import_model_dialog.exec() == QtWidgets.QDialog.Accepted:
                model_name = ins_import_model_dialog.getModelName()
                
                exist_models_name_list =ins_main_window.ins_project_database.getModels()
                if model_name in exist_models_name_list:
                    QtWidgets.QMessageBox.warning(ins_model_toolbar, 'Import Model Waring','The model already exist!')
                    ins_import_model_dialog.deleteLater()
                    return None
                else:
                    pass
                
                ins_main_window.ins_project_database.importModelDataToProject(project_full_name,model_name)
                
                ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
                ins_manager_tab_widget.setCurrentIndex(0)
                ins_model_manager = ins_manager_tab_widget.currentWidget()
                
                ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        
                from .visualization import P4SModelVisualWindow
                P4SModelVisualWindow(ins_models_mdi_area,model_name)
                model_dimension = ins_main_window.ins_project_database.getModelDimension(model_name)
                ins_model_manager.ImportModelFromProject(model_name,model_dimension)
                del P4SModelVisualWindow
        
                ins_main_window.printMessage(f'The model "{model_name}" successfully imported!')
            else:
                pass
            ins_import_model_dialog.deleteLater()
    def __slotRenameModel(self) -> None:
        ins_main_window = self.parent()
        ins_model_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,"model-manager-toolbar")
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(0)
        
        if ins_main_window.ins_project_database is None:
            QtWidgets.QMessageBox.warning(ins_model_toolbar,'Rename Model Waring','None project exist!')
            return None
        else:
            pass
        
        ins_model_manager = ins_manager_tab_widget.currentWidget()
        models_name_list = ins_model_manager.getModelsNameList()
        if models_name_list == []:
            QtWidgets.QMessageBox.warning(ins_model_toolbar,'Rename Model Waring','None model exist!')
            return None
        else:
            pass
        
        ins_rename_model_dialog = _RenameModelDialog(ins_model_toolbar,models_name_list)
        ins_rename_model_dialog.show()
        if ins_rename_model_dialog.exec() == QtWidgets.QDialog.Accepted:
            current_model_name = ins_model_manager.getCurrentModleName()
            new_model_name = ins_rename_model_dialog.getModelName()
            
            ins_model_manager.renameCurrentModel(new_model_name)
            
            ins_main_window.ins_project_database.renameModel(current_model_name,new_model_name)
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_model_name)
            ins_model_visual_window.renameModel(new_model_name)

            ins_main_window.printMessage(f'Rename the model "{current_model_name}" to "{new_model_name}".')
        else:
            pass
        ins_rename_model_dialog.deleteLater()
    def __slotRemoveModel(self) -> None:
        ins_main_window = self.parent()
        ins_model_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,"model-manager-toolbar")
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(0)
        
        if ins_main_window.ins_project_database is None:
            QtWidgets.QMessageBox.warning(ins_model_toolbar,'Remove Model Waring','None project exist!')
            return None
        else:   pass
        
        ins_model_manager = ins_manager_tab_widget.currentWidget()
        current_model_name = ins_model_manager.getCurrentModleName()
        if current_model_name == '':
            QtWidgets.QMessageBox.warning(ins_model_toolbar,'Remove Model Waring','None model exist!')
            return None
        else:
            pass
        
        ins_response_button = QtWidgets.QMessageBox.question(ins_model_toolbar,'Remove Model',f'Model "{current_model_name}" will be removed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_main_window.ins_project_database.removeModel(current_model_name)
        
        ins_model_manager.removeCurrentModel()

        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_model_name)
        ins_model_visual_window.finalizeInteractor()
        ins_model_visual_window.close(in_enable_hide=False)
        ins_models_mdi_area.removeSubWindow(ins_model_visual_window)
        ins_model_visual_window.setParent(None)
        ins_model_visual_window.deleteLater()
        
        ins_main_window.printMessage(f'Model "{current_model_name}" successfully removed.')
    # endregion
    
    def __initializeResultManagerTools(self, in_parent:object) -> None:
        ins_result_tools = QtWidgets.QToolBar(in_parent,allowedAreas=QtCore.Qt.TopToolBarArea,iconSize=QtCore.QSize(28,28),floatable=False)
        ins_result_tools.setObjectName('result-manager-toolbar')
        ins_result_tools.setFixedWidth(120)
        in_parent.addToolBar(ins_result_tools)
        
        ins_open_database_tool = ins_result_tools.addAction(QtGui.QIcon(':/image/images/ManagerOpenDatabase.png'),'')
        ins_open_database_tool.setToolTip('open result database')
        ins_open_database_tool.triggered.connect(self.__slotOpenResultDatabase)
        
        ins_close_database_tool = ins_result_tools.addAction(QtGui.QIcon(':/image/images/ManagerCloseDatabase.png'),'')
        ins_close_database_tool.setToolTip('close result database')
        ins_close_database_tool.triggered.connect(self.__slotCloseResultDatabase)
        
        ins_change_result_mode_tool = ins_result_tools.addAction(QtGui.QIcon(':/image/images/ManagerChangeResultMode.png'),'')
        ins_change_result_mode_tool.setToolTip('result mode')
        ins_change_result_mode_tool.triggered.connect(self.__slotChangeResultMode)
    # region
    def __slotOpenResultDatabase(self) -> None:
        ins_main_window = self.parent()
        
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_visualization_toolbar.clearToolsState()
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(1)
        
        ins_result_manager = ins_manager_tab_widget.currentWidget()
        exist_result_database_full_name_list = ins_result_manager.getExistResultDatabaseFullName()
        
        ins_result_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,"result-manager-toolbar")
        result_full_name,_ = QtWidgets.QFileDialog.getOpenFileName(ins_result_toolbar,'Select Result File',ins_main_window.work_path,'P4Struct Result File(*.res)')
        if result_full_name == '':
            return None
        elif not os.path.exists(result_full_name):
            QtWidgets.QMessageBox.critical(ins_result_toolbar,'Open Result Error',"The result file does't exist!")
            return None
        elif result_full_name in exist_result_database_full_name_list:
            QtWidgets.QMessageBox.critical(ins_result_toolbar,'Open Result Error',"The result file already opened!")
            return None 
        else:
            pass
        
        ins_result_manager.createResultManager(result_full_name)
    def __slotCloseResultDatabase(self) -> None:
        ins_main_window = self.parent()
        
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_visualization_toolbar.clearToolsState()
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(1)
        
        ins_result_manager = ins_manager_tab_widget.currentWidget()
        exist_result_database_full_name_list = ins_result_manager.getExistResultDatabaseFullName()
        if exist_result_database_full_name_list == []:
            ins_result_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,"result-manager-toolbar")
            QtWidgets.QMessageBox.warning(ins_result_toolbar,'Close Result Database Waring','None database opened!')
            return None
        else:
            ins_result_manager.closeCurrentResultManager()
    def __slotChangeResultMode(self) -> None:
        ins_main_window = self.parent()
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(1)
        
        ins_result_manager = ins_manager_tab_widget.currentWidget()
        exist_result_database_full_name_list = ins_result_manager.getExistResultDatabaseFullName()
        if exist_result_database_full_name_list == []:
            ins_result_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,"result-manager-toolbar")
            QtWidgets.QMessageBox.warning(ins_result_toolbar,'Change Result Mode Waring','None database opened!')
            return None
        else:
            ins_result_manager.changeResultMode()
    # endregion

    def __initializeFunctionTools(self, in_parent:object) -> None:
        ins_function_tools = QtWidgets.QToolBar(in_parent,allowedAreas=QtCore.Qt.TopToolBarArea,iconSize=QtCore.QSize(28,28),floatable=False)
        ins_function_tools.setObjectName('function-toolbar')
        ins_function_tools.setFixedWidth(120)
        in_parent.addToolBar(ins_function_tools)
        
        ins_task_tool = ins_function_tools.addAction(QtGui.QIcon(':/image/images/ToolFunctionTask.png'),'')
        ins_task_tool.setToolTip('task')
        ins_task_tool.triggered.connect(self.__slotSwitchTaskManagerVisibility)
        
        ins_optimization_tool = ins_function_tools.addAction(QtGui.QIcon(':/image/images/ToolFunctionOptimization.png'),'')
        ins_optimization_tool.setToolTip('optimization')
        ins_optimization_tool.triggered.connect(self.__slotSwitchOptimizationManagerVisibility)
        
        ins_clear_message_tool = ins_function_tools.addAction(QtGui.QIcon(':/image/images/ToolFunctionClearMessage.png'),'')
        ins_clear_message_tool.setToolTip('clear message')
        ins_clear_message_tool.triggered.connect(self.__slotClearMessage)
    # region
    def __slotSwitchTaskManagerVisibility(self) -> None:
        if self.__ins_task_manager.isVisible():
            self.__ins_task_manager.close()
        else:
            self.__ins_task_manager.show()
    def __slotSwitchOptimizationManagerVisibility(self, in_state:bool) -> None:
        if self.__ins_optimization_task_manager.isVisible():
            self.__ins_optimization_task_manager.close()
        else:
            self.__ins_optimization_task_manager.show()
    def __slotClearMessage(self) -> None:
        ins_main_window = self.parent()
        ins_main_window.clearMessage()
    # endregion
    
    def setToolsEnabled(self, in_state:bool) -> None:
        ins_main_window = self.parent()
        
        ins_window_tools = ins_main_window.findChild(QtWidgets.QToolBar,'window-toolbar')
        ins_window_tools.setEnabled(in_state)
        ins_model_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'model-manager-toolbar')
        ins_model_toolbar.setEnabled(in_state)
        ins_result_tools = ins_main_window.findChild(QtWidgets.QToolBar,'result-manager-toolbar')
        ins_result_tools.setEnabled(in_state)
        ins_function_tools = ins_main_window.findChild(QtWidgets.QToolBar,'function-toolbar')
        ins_function_tools.setEnabled(in_state)
    def getRuningTaskNumber(self) -> int:
        fea_running_taks_number = self.__ins_task_manager.getRuningTaskNumber()
        optimization_running_taks_number = self.__ins_optimization_task_manager.getRuningTaskNumber()
        if fea_running_taks_number >= optimization_running_taks_number:
            running_task_numer = fea_running_taks_number
        else:
            running_task_numer = optimization_running_taks_number
        return running_task_numer
# region
class _CreateModelDialog(QtWidgets.QDialog):
    
    def __init__(self,in_parent:object):
        super().__init__(parent=in_parent,modal=True)
        
        self.setWindowTitle('Create Model')
        self.setFixedHeight(120)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeNameEdit(ins_dialog_layout)
        ins_dialog_layout.addStretch()
        self.__initializeModelDimension(ins_dialog_layout)
        ins_dialog_layout.addStretch()
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeNameEdit(self, in_ins_dialog_layout:object) -> None:
        ins_model_name_layout = QtWidgets.QHBoxLayout()
        
        ins_model_name_label = QtWidgets.QLabel('model name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_model_name_label.setFixedSize(90,30)
        ins_model_name_layout.addWidget(ins_model_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('model-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Model_','M_','model-','m-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckModelName)
        ins_model_name_layout.addWidget(ins_name_line_edit,1)

        in_ins_dialog_layout.addLayout(ins_model_name_layout)
    # region
    def __slotCheckModelName(self, in_model_name:str) -> None:
        ins_main_window = self.parent().parent()
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_model_manager = ins_manager_tab_widget.widget(0)
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        models_name_list = ins_model_manager.getModelsNameList()
        if in_model_name == '' or in_model_name in models_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion
    def __initializeModelDimension(self, in_ins_dialog_layout:object) -> None:
        ins_model_dimension_layout = QtWidgets.QHBoxLayout()
        
        ins_model_dimension_label = QtWidgets.QLabel('dimension',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_model_dimension_label.setFixedSize(90,30)
        ins_model_dimension_layout.addWidget(ins_model_dimension_label,0)
        
        ins_model_dimension_box = QtWidgets.QComboBox(self)
        ins_model_dimension_box.setObjectName('model-dimension-box')
        ins_model_dimension_box.addItems(['2D','3D'])
        ins_model_dimension_layout.addWidget(ins_model_dimension_box,1)
        
        in_ins_dialog_layout.addLayout(ins_model_dimension_layout)
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
    
    def getModelName(self) -> str:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'model-name-edit')
        model_name = ins_name_line_edit.text()
        
        return model_name
    def getModelDimension(self) -> str:
        ins_model_dimension_box = self.findChild(QtWidgets.QComboBox,'model-dimension-box')
        model_dimension = ins_model_dimension_box.currentText()
        
        return model_dimension

class _RenameModelDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_models_name_list:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__models_name_list = in_models_name_list
        
        self.setWindowTitle('Rename Model')
        self.setFixedHeight(90)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeNameEdit(ins_dialog_layout)
        ins_dialog_layout.addStretch()
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeNameEdit(self, in_ins_dialog_layout:object) -> None:
        ins_model_name_layout = QtWidgets.QHBoxLayout()
        
        ins_model_name_label = QtWidgets.QLabel('model name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_model_name_label.setFixedSize(90,30)
        ins_model_name_layout.addWidget(ins_model_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('model-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Model_','M_','model-','m-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckModelName)
        ins_model_name_layout.addWidget(ins_name_line_edit,1)

        in_ins_dialog_layout.addLayout(ins_model_name_layout)
    # region
    def __slotCheckModelName(self, in_model_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        if in_model_name == '' or in_model_name in self.__models_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
    
    def getModelName(self) -> str:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'model-name-edit')
        model_name = ins_name_line_edit.text()
        
        return model_name

class _ImportModelDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_models_by_dimension:dict):
        super().__init__(parent=in_parent,modal=True)
        
        self.__models_by_dimension = in_models_by_dimension
        
        self.setWindowTitle('Import Model')
        self.setFixedHeight(90)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeModelSelection(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeModelSelection(self, in_ins_dialog_layout:object) -> None:
        ins_model_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_model_selection_layout)
        
        ins_model_dimension_label = QtWidgets.QLabel('Dimension:',self,alignment=QtCore.Qt.AlignCenter)
        ins_model_dimension_label.setFixedSize(80,30)
        ins_model_selection_layout.addWidget(ins_model_dimension_label,0)
        
        ins_model_dimension_box = QtWidgets.QComboBox(self)
        ins_model_dimension_box.setFixedSize(45,30)
        ins_model_dimension_box.addItems(['2D','3D'])
        ins_model_dimension_box.currentTextChanged.connect(self.__slotSwitchModelDimension)
        ins_model_selection_layout.addWidget(ins_model_dimension_box,0)
        
        ins_model_name_label = QtWidgets.QLabel('Model:',self,alignment=QtCore.Qt.AlignCenter)
        ins_model_name_label.setFixedSize(50,30)
        ins_model_selection_layout.addWidget(ins_model_name_label,0)
        
        ins_model_name_box = QtWidgets.QComboBox(self)
        ins_model_name_box.setObjectName('models-box')
        ins_model_name_box.setFixedHeight(30)
        ins_model_name_box.addItems(self.__models_by_dimension['2D'])
        ins_model_selection_layout.addWidget(ins_model_name_box,1)
    # region
    def __slotSwitchModelDimension(self, in_model_dimension:str) -> None:
        ins_model_name_box = self.findChild(QtWidgets.QComboBox,'models-box')
        ins_model_name_box.clear()
        ins_model_name_box.addItems(self.__models_by_dimension[in_model_dimension])
    # endregion
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
    
    def getModelName(self) -> str:
        ins_model_name_box = self.findChild(QtWidgets.QComboBox,'models-box')
        model_name = ins_model_name_box.currentText()
        
        return model_name

class _CreateFiniteElementAnalysisTaskManager(QtWidgets.QDialog):
    def __init__(self,in_parent:object) -> None:
        super().__init__(parent=in_parent,f=QtCore.Qt.Window)

        self.setWindowTitle('FEA Task Manager')
        self.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint,False)
        self.setMinimumSize(450,200)
        
        ins_manager_layout = QtWidgets.QVBoxLayout()
        ins_manager_layout.setContentsMargins(5,5,5,5)
        self.setLayout(ins_manager_layout)

        self.__initializeToolButtons(ins_manager_layout)
        self.__initializeTaskTable(ins_manager_layout)

        self.__task_process_dict = {}
        self.__ins_task_process_queen = multiprocessing.Queue()
        
        self.__ins_task_state_check_timer = QtCore.QTimer(self)
        self.__ins_task_state_check_timer.setInterval(1000)
        self.__ins_task_state_check_timer.timeout.connect(self.__slotCheckTaskState)

    def __initializeToolButtons(self, in_ins_manager_layout:object) -> None:
        ins_tool_buttons_layout = QtWidgets.QHBoxLayout()
        ins_tool_buttons_layout.setSpacing(0)
        in_ins_manager_layout.addLayout(ins_tool_buttons_layout,0)
        
        ins_create_task_button = QtWidgets.QPushButton(self)
        ins_create_task_button.setIconSize(QtCore.QSize(27,27))
        ins_create_task_button.setIcon(QtGui.QIcon(':/image/images/TaskCreateTask.png'))
        ins_create_task_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_create_task_button.clicked.connect(self.__slotCreateFiniteElementAnalysisTask)
        ins_tool_buttons_layout.addWidget(ins_create_task_button,0)
        
        ins_import_task_button = QtWidgets.QPushButton(self)
        ins_import_task_button.setIconSize(QtCore.QSize(27,27))
        ins_import_task_button.setIcon(QtGui.QIcon(':/image/images/TaskImportTask.png'))
        ins_import_task_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_import_task_button.clicked.connect(self.__slotImportFiniteElementAnalysisTask)
        ins_tool_buttons_layout.addWidget(ins_import_task_button,0)
        
        ins_tool_buttons_layout.addStretch()
    # region
    def __slotCreateFiniteElementAnalysisTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        exist_tasks_name_list = [ins_task_table.item(i,0).text() for i in range(ins_task_table.rowCount())]
        
        if self.parent().ins_project_database is None:
            exist_models_name_list = []
        else:
            exist_models_name_list = self.parent().ins_project_database.getModels()
        
        ins_dialog = QtWidgets.QDialog(self)
        ins_dialog.setWindowTitle('Create Task')
        ins_dialog.setWindowModality(QtCore.Qt.WindowModal)
        ins_dialog.setFixedHeight(100)

        ins_dialog_layout = QtWidgets.QVBoxLayout()
        ins_dialog.setLayout(ins_dialog_layout)

        ins_selection_layout = QtWidgets.QHBoxLayout()
        ins_dialog_layout.addLayout(ins_selection_layout)
        
        ins_name_label = QtWidgets.QLabel('Name:',ins_dialog,alignment=QtCore.Qt.AlignCenter)
        ins_name_label.setFixedSize(50,30)
        ins_selection_layout.addWidget(ins_name_label,0)
        ins_name_edit = QtWidgets.QLineEdit(ins_dialog)
        ins_name_edit.setFixedHeight(30)
        ins_name_edit.setMaxLength(20)
        ins_name_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_selection_layout.addWidget(ins_name_edit,1)
        
        ins_model_label = QtWidgets.QLabel('Model:',ins_dialog)
        ins_model_label.setFixedSize(50,30)
        ins_selection_layout.addWidget(ins_model_label,0)
        ins_models_box = QtWidgets.QComboBox(ins_dialog)
        ins_models_box.setFixedHeight(30)
        ins_models_box.addItems(exist_models_name_list)
        ins_models_box.setCurrentIndex(-1)
        ins_selection_layout.addWidget(ins_models_box,1)
        
        ins_type_label = QtWidgets.QLabel('Type:',ins_dialog)
        ins_type_label.setFixedSize(50,30)
        ins_selection_layout.addWidget(ins_type_label,0)
        ins_type_box = QtWidgets.QComboBox(ins_dialog)
        ins_type_box.setFixedHeight(30)
        ins_type_box.addItems(['FEM'])
        ins_selection_layout.addWidget(ins_type_box,1)
        
        ins_buttons_layout = QtWidgets.QHBoxLayout()
        ins_dialog_layout.addLayout(ins_buttons_layout)
        ins_buttons_layout.addStretch()
        ins_accept_button = QtWidgets.QPushButton('Accept',ins_dialog)
        ins_accept_button.setFixedSize(75,30)
        ins_accept_button.setEnabled(False)
        ins_accept_button.clicked.connect(ins_dialog.accept)
        ins_buttons_layout.addWidget(ins_accept_button)
        ins_buttons_layout.addStretch()
        ins_cancel_button = QtWidgets.QPushButton('Cancel',ins_dialog)
        ins_cancel_button.setFixedSize(75,30)
        ins_cancel_button.clicked.connect(ins_dialog.close)
        ins_buttons_layout.addWidget(ins_cancel_button)
        ins_buttons_layout.addStretch()

        ins_name_edit.textChanged.connect(lambda: ins_accept_button.setEnabled(False) if ins_name_edit.text()=='' or ins_name_edit.text() in exist_tasks_name_list else ins_accept_button.setEnabled(True))

        ins_dialog.show()
        if ins_dialog.exec() == QtWidgets.QDialog.Accepted:
            if ins_models_box.currentText() == '':
                QtWidgets.QMessageBox.warning(self,'Create Finite Element Analysis Task Warning','None model exist!')
            else:
                ins_task_table.insertRow(ins_task_table.rowCount())
                
                ins_task_item = QtWidgets.QTableWidgetItem()
                ins_task_item.setTextAlignment(QtCore.Qt.AlignCenter)
                ins_task_item.setText(ins_name_edit.text())
                ins_task_table.setItem(ins_task_table.rowCount()-1,0,ins_task_item)
                
                ins_model_item = QtWidgets.QTableWidgetItem()
                ins_model_item.setTextAlignment(QtCore.Qt.AlignCenter)
                ins_model_item.setText('model:'+ins_models_box.currentText())
                ins_task_table.setItem(ins_task_table.rowCount()-1,1,ins_model_item)
                
                ins_type_item = QtWidgets.QTableWidgetItem()
                ins_type_item.setTextAlignment(QtCore.Qt.AlignCenter)
                ins_type_item.setText(ins_type_box.currentText())
                ins_task_table.setItem(ins_task_table.rowCount()-1,2,ins_type_item)
                
                ins_time_item = QtWidgets.QTableWidgetItem()
                ins_time_item.setTextAlignment(QtCore.Qt.AlignCenter)
                ins_time_item.setText('none')
                ins_task_table.setItem(ins_task_table.rowCount()-1,3,ins_time_item)
                
                ins_state_item = QtWidgets.QTableWidgetItem()
                ins_state_item.setTextAlignment(QtCore.Qt.AlignCenter)
                ins_state_item.setText('none')
                ins_task_table.setItem(ins_task_table.rowCount()-1,4,ins_state_item)

                ins_task_table.selectRow(ins_task_table.rowCount()-1)
        else:
            pass
        ins_dialog.deleteLater()
    def __slotImportFiniteElementAnalysisTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        task_name_list = [ins_task_table.item(i,0).text() for i in range(ins_task_table.rowCount())]

        ins_main_window = self.parent()
        imported_task_file_full_name, _ = QtWidgets.QFileDialog.getOpenFileName(self,'Select Task File',ins_main_window.work_path,'P4Struct Task File(*.task)')
        if imported_task_file_full_name == '':
            return None
        else:
            pass
        
        imported_task_name = os.path.basename(imported_task_file_full_name).split('.',1)[0]

        while imported_task_name in task_name_list:
            new_task_name,user_state = QtWidgets.QInputDialog.getText(self,'Import Task Waring','The task name already exist!\n Please input a new task name.')
            if user_state:
                if new_task_name in task_name_list:
                    continue
                else:
                    new_task_file_full_name = ins_main_window.work_path + os.sep + new_task_name + '.task'
                    if os.path.isfile(new_task_file_full_name):
                        ins_response_button = QtWidgets.QMessageBox.question(self,'Rename Import Task File Waring','The task file already exist,overwrite?')
                        if ins_response_button == QtWidgets.QMessageBox.Yes:
                            os.remove(new_task_file_full_name)
                            imported_task_name = new_task_name
                            
                            os.rename(imported_task_file_full_name, new_task_file_full_name)
                            imported_task_file_full_name = new_task_file_full_name
                        else:
                            continue
                    else:
                        pass
            else:
                return None
        
        with h5py.File(imported_task_file_full_name,'r') as ins_task_file:
            if 'basic' in  ins_task_file:
                task_type = str(ins_task_file['basic'][1],encoding='utf-8')
            else:
                QtWidgets.QMessageBox.critical(self,'Import Task Error','The format of task is error!')
                return None
        
        ins_task_table.insertRow(ins_task_table.rowCount())
        ins_task_name_item = QtWidgets.QTableWidgetItem()
        ins_task_name_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_task_name_item.setText(imported_task_name)
        ins_task_table.setItem(ins_task_table.rowCount()-1,0,ins_task_name_item)
        ins_source_item = QtWidgets.QTableWidgetItem()
        ins_source_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_source_item.setText('File:'+imported_task_file_full_name)
        ins_source_item.setToolTip(imported_task_file_full_name)
        ins_task_table.setItem(ins_task_table.rowCount()-1,1,ins_source_item)
        ins_type_item = QtWidgets.QTableWidgetItem()
        ins_type_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_type_item.setText(task_type)
        ins_task_table.setItem(ins_task_table.rowCount()-1,2,ins_type_item)
        ins_time_item = QtWidgets.QTableWidgetItem()
        ins_time_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_time_item.setText('none')
        ins_task_table.setItem(ins_task_table.rowCount()-1,3,ins_time_item)
        ins_state_item = QtWidgets.QTableWidgetItem()
        ins_state_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_state_item.setText('output')
        ins_task_table.setItem(ins_task_table.rowCount()-1,4,ins_state_item)

        ins_task_table.selectRow(ins_task_table.rowCount()-1)
    # endregion
    
    def __initializeTaskTable(self, in_ins_manager_layout:object) -> None:
        ins_task_table = QtWidgets.QTableWidget(self)
        in_ins_manager_layout.addWidget(ins_task_table,1)
        
        ins_task_table.setObjectName('fea-task-table')
        ins_task_table.setColumnCount(5)
        ins_task_table.setHorizontalHeaderLabels(['Name','Source','Type','Time','State'])
        ins_task_table.horizontalHeader().setSectionsClickable(False)
        ins_task_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_task_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ins_task_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        ins_task_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_task_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        ins_task_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        ins_task_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        ins_task_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        ins_task_table.customContextMenuRequested.connect(self.__slotTableRightMenu)
    # region
    def __slotTableRightMenu(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        if ins_task_table.currentRow() == -1:
            return None
        else:
            pass

        ins_item_right_menu = QtWidgets.QMenu(self)

        if ins_task_table.item(ins_task_table.currentRow(),4).text() == 'none':
            if ins_task_table.item(ins_task_table.currentRow(),1).text().split(":",1)[0] == 'File':
                ins_delete_task = ins_item_right_menu.addAction('delete task')
                ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
                
                ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
                ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
            else:
                ins_output_task = ins_item_right_menu.addAction('output')
                ins_output_task.triggered.connect(self.__slotOutputTaskFile)

                ins_item_right_menu.addSeparator()
                
                ins_rename_task = ins_item_right_menu.addAction('rename')
                ins_rename_task.triggered.connect(self.__slotRenameTask)
            
                ins_item_right_menu.addSeparator()
            
                ins_delete_task = ins_item_right_menu.addAction('delete task')
                ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
                ins_delete_task_file = ins_item_right_menu.addAction('delete(task file)')
                ins_delete_task_file.triggered.connect(self.__slotDeleteTaskFile)
                ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
                ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
                ins_delete_all = ins_item_right_menu.addAction('delete all')
                ins_delete_all.triggered.connect(self.__slotDeleteTaskAll)
        elif ins_task_table.item(ins_task_table.currentRow(),4).text() == 'output':
            ins_check_task = ins_item_right_menu.addAction('check')
            ins_check_task.triggered.connect(self.__slotCheckTask)
            
            ins_item_right_menu.addSeparator()
            
            if ins_task_table.item(ins_task_table.currentRow(),1).text().split(":",1)[0] == 'File':
                ins_delete_task = ins_item_right_menu.addAction('delete task')
                ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
                ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
                ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
            else:
                ins_output_task = ins_item_right_menu.addAction('output')
                ins_output_task.triggered.connect(self.__slotOutputTaskFile)
                
                ins_item_right_menu.addSeparator()
                
                ins_rename_task = ins_item_right_menu.addAction('rename')
                ins_rename_task.triggered.connect(self.__slotRenameTask)
            
                ins_item_right_menu.addSeparator()
            
                ins_delete_task = ins_item_right_menu.addAction('delete task')
                ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
                ins_delete_task_file = ins_item_right_menu.addAction('delete(task file)')
                ins_delete_task_file.triggered.connect(self.__slotDeleteTaskFile)
                ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
                ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
                ins_delete_all = ins_item_right_menu.addAction('delete all')
                ins_delete_all.triggered.connect(self.__slotDeleteTaskAll)
        elif ins_task_table.item(ins_task_table.currentRow(),4).text() == 'checked':
            ins_submit_task = ins_item_right_menu.addAction('submit')
            ins_submit_task.triggered.connect(self.__slotSubmitTask)
            
            ins_item_right_menu.addSeparator()
            
            if ins_task_table.item(ins_task_table.currentRow(),1).text().split(":",1)[0] == 'File':
                ins_check_task = ins_item_right_menu.addAction('check')
                ins_check_task.triggered.connect(self.__slotCheckTask)
                
                ins_item_right_menu.addSeparator()
                
                ins_delete_task = ins_item_right_menu.addAction('delete task')
                ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
                ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
                ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
            else:
                ins_output_task = ins_item_right_menu.addAction('output')
                ins_output_task.triggered.connect(self.__slotOutputTaskFile)
                
                ins_check_task = ins_item_right_menu.addAction('check')
                ins_check_task.triggered.connect(self.__slotCheckTask)
                
                ins_item_right_menu.addSeparator()
                
                ins_rename_task = ins_item_right_menu.addAction('rename')
                ins_rename_task.triggered.connect(self.__slotRenameTask)

                ins_item_right_menu.addSeparator()
            
                ins_delete_task = ins_item_right_menu.addAction('delete task')
                ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
                ins_delete_task_file = ins_item_right_menu.addAction('delete(task file)')
                ins_delete_task_file.triggered.connect(self.__slotDeleteTaskFile)
                ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
                ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
                ins_delete_all = ins_item_right_menu.addAction('delete all')
                ins_delete_all.triggered.connect(self.__slotDeleteTaskAll)
        elif ins_task_table.item(ins_task_table.currentRow(),4).text() == 'running':
            ins_stop_task = ins_item_right_menu.addAction('stop')
            ins_stop_task.triggered.connect(self.__slotStopRunningTask)
        elif ins_task_table.item(ins_task_table.currentRow(),4).text() == 'ready':
            ins_stop_task = ins_item_right_menu.addAction('cancel')
            ins_stop_task.triggered.connect(self.__slotCancelReadytask)
        elif ins_task_table.item(ins_task_table.currentRow(),4).text() in ['finished','check error','computation error']:
            if ins_task_table.item(ins_task_table.currentRow(),1).text().split(":",1)[0] == 'File':
                ins_check_task = ins_item_right_menu.addAction('check')
                ins_check_task.triggered.connect(self.__slotCheckTask)
                
                ins_delete_task = ins_item_right_menu.addAction('delete task')
                ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
                ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
                ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
            else:
                ins_output_task = ins_item_right_menu.addAction('output')
                ins_output_task.triggered.connect(self.__slotOutputTaskFile)
                
                ins_check_task = ins_item_right_menu.addAction('check')
                ins_check_task.triggered.connect(self.__slotCheckTask)

                ins_item_right_menu.addSeparator()
                
                ins_rename_task = ins_item_right_menu.addAction('rename')
                ins_rename_task.triggered.connect(self.__slotRenameTask)
            
                ins_item_right_menu.addSeparator()
            
                ins_delete_task = ins_item_right_menu.addAction('delete task')
                ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
                ins_delete_task_file = ins_item_right_menu.addAction('delete(task file)')
                ins_delete_task_file.triggered.connect(self.__slotDeleteTaskFile)
                ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
                ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
                ins_delete_all = ins_item_right_menu.addAction('delete all')
                ins_delete_all.triggered.connect(self.__slotDeleteTaskAll)
        else:
            pass

        ins_item_right_menu.exec(QtGui.QCursor.pos())
    
    def __slotOutputTaskFile(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        
        ins_main_window = self.parent()
        task_full_Name = ins_main_window.work_path + os.sep + task_name + '.task'

        if os.path.isfile(task_full_Name):
            ins_response_button = QtWidgets.QMessageBox.question(self,'Output Task File Waring','The task file already exist,overwrite?')
            if ins_response_button == QtWidgets.QMessageBox.Yes:
                try:
                    os.remove(task_full_Name)
                except:
                    QtWidgets.QMessageBox.information(self,"Output Task File Error","The file is being occupied!")
                    return None
                else:
                    pass
            else:
                return None
        else:
            pass

        if ins_main_window.ins_project_database is None:
            QtWidgets.QMessageBox.critical(self,'Output Task File Error','None project exist!')
            return None
        else:
            pass

        model_name = ins_task_table.item(ins_task_table.currentRow(),1).text().split(':',1)[1]
        models_name_list = ins_main_window.ins_project_database.getModels()
        if model_name in models_name_list:
            if ins_task_table.item(ins_task_table.currentRow(),2).text() == 'FEM':
                ins_main_window.ins_project_database.outpuFEMTaskFile(model_name,task_full_Name)
            else:
                pass
            
            ins_task_table.item(ins_task_table.currentRow(),3).setText('none')
            ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
        else:
            QtWidgets.QMessageBox.critical(self,'Output Task File Error',f"The model {model_name} doesn't exist in project!")
            return None
    def __slotCheckTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()

        ins_main_window = self.parent()
        task_full_Name = ins_main_window.work_path + os.sep + task_name + '.task'

        if os.path.isfile(task_full_Name):
            ins_task_table.item(ins_task_table.currentRow(),3).setText('none')

            checked_state_number = 0
            try:
                with h5py.File(task_full_Name,'r') as ins_task_file:
                    if len(ins_task_file['Mesh']) == 0:
                        checked_state_number = 1
                    else:
                        pass
                    
                    if checked_state_number == 0:
                        if numpy.any(ins_task_file['Mesh']['materials'][:]==0):
                            checked_state_number = 2
                        else:
                            pass
                    else:
                        pass
                    
                    if checked_state_number == 0:
                        if numpy.any(ins_task_file['Mesh']['attributes'][:]==0):
                            checked_state_number = 3
                        else:
                            pass
                    else:
                        pass
                    
                    if checked_state_number == 0:
                        if numpy.any(ins_task_file['Mesh']['type'][:]==0):
                            checked_state_number = 4
                        else:
                            pass
                    else:
                        pass
            
                    if checked_state_number == 0:
                        if len(ins_task_file['Steps']) == 0:
                            checked_state_number = 5
                        else:
                            pass
                    else:
                        pass
                    
                    if checked_state_number == 0:
                        if len(ins_task_file['Outputs']['Nodes']) == 0 and len(ins_task_file['Outputs']['Elements']) == 0:
                            checked_state_number = 6
                        else:
                            pass
                    else:
                        pass
            
                    if checked_state_number == 0:
                        if len(ins_task_file['Conditions']) == 0:
                            checked_state_number = 7
                        else:
                            pass
                    else:
                        pass
                    
                    if ins_task_file['basic'][1] == b'FEM':
                        pass
                    else:
                        pass
            except:
                QtWidgets.QMessageBox.critical(self,'Task Error','The format of task is error!')
                ins_task_table.item(ins_task_table.currentRow(),4).setText('check error')
            else:
                if checked_state_number == 0:
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('checked')
                elif checked_state_number == 1:
                    QtWidgets.QMessageBox.critical(self,'Task Error','The assembly of this task is empty!')
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('check error')
                elif checked_state_number == 2:
                    QtWidgets.QMessageBox.critical(self,'Task Error','The material data is incomplete!')
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('check error')
                elif checked_state_number == 3:
                    QtWidgets.QMessageBox.critical(self,'Task Error','The attribute of this task is incomplete!')
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('check error')
                elif checked_state_number == 4:
                    QtWidgets.QMessageBox.critical(self,'Task Error','The element type of this task is incomplete!')
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('check error')
                elif checked_state_number == 5:
                    QtWidgets.QMessageBox.critical(self,'Task Error','The step of this task is empty!')
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('check error')
                elif checked_state_number == 6:
                    QtWidgets.QMessageBox.critical(self,'Task Error','The output of this task is empty!')
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('check error')
                elif checked_state_number == 7:
                    QtWidgets.QMessageBox.critical(self,'Task Error','The boundary condition of this task is empty!')
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('check error')
                else:
                    pass
        else:
            QtWidgets.QMessageBox.critical(self,'Check Task Error','The task file could not be found!')
            
            ins_task_table.item(ins_task_table.currentRow(),3).setText('none')
            ins_task_table.item(ins_task_table.currentRow(),4).setText('none')
    def __slotRenameTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        task_name_list = [ins_task_table.item(i,0).text() for i in range(ins_task_table.rowCount())]

        while True:
            new_task_name,user_state = QtWidgets.QInputDialog.getText(self,'Rename Task Waring','The task name already exist!\n Please input a new task name.')
            if user_state:
                if new_task_name in task_name_list:
                    continue
                else:
                    ins_task_table.item(ins_task_table.currentRow(),0).setText(new_task_name)
                    ins_task_table.item(ins_task_table.currentRow(),3).setText('none')
                    if ins_task_table.item(ins_task_table.currentRow(),4).text() in ['none','checked']:
                        pass
                    else:
                        ins_task_table.item(ins_task_table.currentRow(),4).setText('none')
                    break
            else:
                return None
    def __slotSubmitTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        work_path = self.parent().work_path
        
        if self.__task_process_dict == {}:
            computer_memory_info = psutil.virtual_memory()
            memory_usage_ratio = computer_memory_info.used / computer_memory_info.total
            if memory_usage_ratio > 0.92:
                QtWidgets.QMessageBox.warning(self,'Submit Task Waring','The used memory greater than 92%!Unable to submit new task.')
                return None
            else:
                pass
            
            task_process_file_full_name = work_path + os.sep + task_name + '.pro'
            if os.path.isfile(task_process_file_full_name):
                os.remove(task_process_file_full_name)
            else:
                pass
            task_result_file_full_name = work_path + os.sep + task_name + '.res'
            if os.path.isfile(task_result_file_full_name):
                try:
                    os.remove(task_result_file_full_name)
                except:
                    QtWidgets.QMessageBox.warning(self,'Submit Task Error','The task result file has been opened!')
                    return None
                else:
                    pass
            else:
                pass
            for temp_file_full_name in glob.glob(work_path+os.sep+'*.femtemp'):
                if '-'.join(os.path.basename(temp_file_full_name).split('.')[0].split('-')[0:-1]) == task_name:
                    if os.path.isfile(temp_file_full_name):
                        os.remove(temp_file_full_name)
                    else:
                        pass
                else:
                    continue
            
            task_file_full_name = work_path + os.sep + task_name + '.task'
            if os.path.isfile(task_file_full_name):
                pass
            else:
                if ins_task_table.item(ins_task_table.currentRow(),1).text().split(':',1)[0] == 'File':
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                else:
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('none')
                
                QtWidgets.QMessageBox.warning(self,'Submit Task Error','The task file could not be found!')
                return None

            ins_current_time = datetime.datetime.now()
            current_time_text = str(ins_current_time.year) + '-' + str(ins_current_time.month) + '-' + str(ins_current_time.day) + ' ' + str(ins_current_time.hour) + ':' + str(ins_current_time.minute) + ':' + str(ins_current_time.second)
            ins_task_table.item(ins_task_table.currentRow(),3).setText(current_time_text)
            ins_task_table.item(ins_task_table.currentRow(),3).setToolTip(current_time_text)
            ins_task_table.item(ins_task_table.currentRow(),4).setText('running')
            
            task_type = ins_task_table.item(ins_task_table.currentRow(),2).text()
            if task_type == 'FEM':
                ins_task_process = multiprocessing.Process(target=intoFEAProcess,name=task_name,args=(task_file_full_name,self.__ins_task_process_queen,),)
            else:
                pass
            self.__task_process_dict[task_name] = ins_task_process
            ins_task_process.start()
            
            self.__ins_task_state_check_timer.start()
        else:
            ins_task_table.item(ins_task_table.currentRow(),4).setText('ready')
    def __slotStopRunningTask(self) -> None:
        ins_main_window = self.parent()
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        
        ins_task_table.item(ins_task_table.currentRow(),3).setText('none')
        ins_task_table.item(ins_task_table.currentRow(),4).setText('checked')

        if isinstance(self.__task_process_dict[task_name], multiprocessing.Process):
            if self.__task_process_dict[task_name].is_alive():
                for ins_subprocess in psutil.Process(self.__task_process_dict[task_name].pid).children(recursive=True):
                    ins_subprocess.terminate()
                    ins_subprocess.wait()

                self.__task_process_dict[task_name].terminate()
                self.__task_process_dict[task_name].join()
            else:
                pass

            self.__task_process_dict[task_name].close()
        else:
            pass
    
        del self.__task_process_dict[task_name]

        for temp_file_full_name in glob.glob(ins_main_window.work_path+os.sep+'*.femtemp'):
            if '-'.join(os.path.basename(temp_file_full_name).split('.')[0].split('-')[0:-1]) == task_name:
                if os.path.isfile(temp_file_full_name):
                    os.remove(temp_file_full_name)
                else:
                    pass
            else:
                continue
        for temp_file_full_name in glob.glob(ins_main_window.work_path+os.sep+'*.pro'):
            if os.path.basename(temp_file_full_name).split('.')[0] == task_name:
                if os.path.isfile(temp_file_full_name):
                    os.remove(temp_file_full_name)
                else:
                    pass
            else:
                continue
    def __slotCancelReadytask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        ins_task_table.item(ins_task_table.currentRow(),4).setText('checked')
    def __slotDeleteTaskRow(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        ins_task_table.removeRow(ins_task_table.currentRow())
    def __slotDeleteTaskFile(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Delete Task File Question','The task file will be deleted,continue?')
        if ins_response_button == QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        
        ins_main_window = self.parent()
        task_file_full_name = ins_main_window.work_path + os.sep + task_name + '.task'
        if os.path.isfile(task_file_full_name):
            os.remove(task_file_full_name)
        else:
            pass
        
        ins_task_table.item(ins_task_table.currentRow(),3).setText('none')
        ins_task_table.item(ins_task_table.currentRow(),4).setText('none')
    def __slotDeleteTaskResult(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Delete Result File Question','The result file will be deleted,continue?')
        if ins_response_button == QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None   
                
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        work_path = self.parent().work_path

        task_result_file_full_name = work_path + os.sep + task_name + ".res"
        if os.path.isfile(task_result_file_full_name):
            try:
                os.remove(task_result_file_full_name)
            except:
                QtWidgets.QMessageBox.critical(self,'Delete Result File Error','The result file already opened!')
                return None
            else:
                pass
        else:
            pass
    def __slotDeleteTaskAll(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Delete All Task File Question','All task file will be deleted,continue?')
        if ins_response_button == QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        
        work_path = self.parent().work_path
        
        task_file_full_name = work_path + os.sep + task_name + '.task'
        if os.path.isfile(task_file_full_name):
            os.remove(task_file_full_name)
        else:
            pass

        task_result_file_full_name = work_path + os.sep + task_name + ".res"
        if os.path.isfile(task_result_file_full_name):
            try:
                os.remove(task_result_file_full_name)
            except:
                QtWidgets.QMessageBox.critical(self,'Delete Result File Error','The result file already opened!')
                return None
            else:
                pass
        else:
            pass

        ins_task_table.removeRow(ins_task_table.currentRow())
    def __slotCheckTaskState(self) -> None:
        self.__ins_task_state_check_timer.stop()
        
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        work_path = self.parent().work_path
        
        if self.__ins_task_process_queen.empty():
            pass
        else:
            while True:
                if self.__ins_task_process_queen.empty():
                    break
                else:
                    task_name,task_time_string = self.__ins_task_process_queen.get()
                    
                    for row_index in range(ins_task_table.rowCount()):
                        if ins_task_table.item(row_index,0).text() == task_name:
                            if task_time_string == 'error':
                                ins_task_table.item(row_index,3).setText('none')
                                ins_task_table.item(row_index,3).setToolTip('none')
                                ins_task_table.item(row_index,4).setText('computation error')
                            else:
                                ins_task_table.item(row_index,3).setText(task_time_string)
                                ins_task_table.item(row_index,3).setToolTip(task_time_string)
                                ins_task_table.item(row_index,4).setText("finished")
                            break
                        else:
                            continue
                    
                    if isinstance(self.__task_process_dict[task_name], multiprocessing.Process):
                        if self.__task_process_dict[task_name].is_alive():
                            for ins_subprocess in psutil.Process(self.__task_process_dict[task_name].pid).children(recursive=True):
                                ins_subprocess.terminate()
                                ins_subprocess.wait()

                            self.__task_process_dict[task_name].terminate()
                            self.__task_process_dict[task_name].join()
                        else:
                            pass

                        self.__task_process_dict[task_name].close()
                        
                    else:
                        pass
                    del self.__task_process_dict[task_name]

                    task_process_file_full_name = work_path + os.sep + task_name + '.pro'
                    if os.path.isfile(task_process_file_full_name):
                        os.remove(task_process_file_full_name)
                    else:
                        pass
        
        if self.__task_process_dict == {}:
            for row_index in range(ins_task_table.rowCount()):
                if ins_task_table.item(row_index,4).text() == 'ready':
                    computer_memory_info = psutil.virtual_memory()
                    memory_usage_ratio = computer_memory_info.used / computer_memory_info.total
                    if memory_usage_ratio > 0.92:
                        ins_task_table.item(row_index,4).setText('checked')
                        continue
                    else:
                        pass
                    
                    task_name = ins_task_table.item(row_index,0).text()
                    
                    task_result_file_full_name = work_path + os.sep + task_name + '.res'
                    if os.path.isfile(task_result_file_full_name):
                        try:
                            os.remove(task_result_file_full_name)
                        except:
                            ins_task_table.item(row_index,4).setText('checked')
                            continue
                        else:
                            pass
                    else:
                        pass
                
                    task_file_full_name = work_path + os.sep + task_name + '.task'
                    if os.path.isfile(task_file_full_name):
                        pass
                    else:
                        if ins_task_table.item(row_index,1).text().split(':',1)[0] == 'File':
                            ins_task_table.item(row_index,4).setText('output')
                        else:
                            ins_task_table.item(row_index,4).setText('none')
                        continue
        
                    ins_current_time = datetime.datetime.now()
                    current_time_text = str(ins_current_time.year) + '-' + str(ins_current_time.month) + '-' + str(ins_current_time.day) + ' ' + str(ins_current_time.hour) + ':' + str(ins_current_time.minute) + ':' + str(ins_current_time.second)
                    ins_task_table.item(row_index,3).setText(current_time_text)
                    ins_task_table.item(row_index,3).setToolTip(current_time_text)
                    ins_task_table.item(row_index,4).setText('running')
                    
                    task_type = ins_task_table.item(ins_task_table.currentRow(),2).text()
                    if task_type == 'FEM':
                        ins_task_process = multiprocessing.Process(target=intoFEAProcess,name=task_name,args=(task_file_full_name,self.__ins_task_process_queen,),)
                    else:
                        pass
                    self.__task_process_dict[task_name] = ins_task_process
                    ins_task_process.start()
                    
                    break
                else:
                    continue
        else:
            pass
        
        if self.__task_process_dict == {}:
            pass
        else:
            self.__ins_task_state_check_timer.start()
    # endregion
    
    def getRuningTaskNumber(self) -> int:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'fea-task-table')
        
        running_task_number = 0
        for row_index in range(ins_task_table.rowCount()):
            if ins_task_table.item(row_index,4).text() == 'running':
                running_task_number += 1
            else:
                continue
        
        return running_task_number

class _CreateOptimizationTaskManager(QtWidgets.QDialog):
    def __init__(self,in_parent:object) -> None:
        super().__init__(parent=in_parent,f=QtCore.Qt.Window)

        self.setWindowTitle('Optimization Task Manager')
        self.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint,False)
        self.setMinimumSize(450,200)
        
        ins_manager_layout = QtWidgets.QVBoxLayout()
        ins_manager_layout.setContentsMargins(5,5,5,5)
        self.setLayout(ins_manager_layout)

        self.__initializeToolButtons(ins_manager_layout)
        self.__initializeTaskTable(ins_manager_layout)

        self.__task_process_dict = {}
        self.__ins_task_process_queen = multiprocessing.Queue()
        
        self.__ins_task_state_check_timer = QtCore.QTimer(self)
        self.__ins_task_state_check_timer.setInterval(1000)
        self.__ins_task_state_check_timer.timeout.connect(self.__slotCheckTaskState)
    
    def __initializeToolButtons(self, in_ins_manager_layout:object) -> None:
        ins_tool_buttons_layout = QtWidgets.QHBoxLayout()
        ins_tool_buttons_layout.setSpacing(0)
        in_ins_manager_layout.addLayout(ins_tool_buttons_layout,0)
        
        ins_create_optimization_task_button = QtWidgets.QPushButton(self)
        ins_create_optimization_task_button.setIconSize(QtCore.QSize(27,27))
        ins_create_optimization_task_button.setIcon(QtGui.QIcon(':/image/images/TaskCreateTask.png'))
        ins_create_optimization_task_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_create_optimization_task_button.clicked.connect(self.__slotCreateOptimizationTask)
        ins_tool_buttons_layout.addWidget(ins_create_optimization_task_button,0)
        
        ins_import_optimization_task_button = QtWidgets.QPushButton(self)
        ins_import_optimization_task_button.setIconSize(QtCore.QSize(27,27))
        ins_import_optimization_task_button.setIcon(QtGui.QIcon(':/image/images/TaskImportTask.png'))
        ins_import_optimization_task_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_import_optimization_task_button.clicked.connect(self.__slotImportOptimizationTask)
        ins_tool_buttons_layout.addWidget(ins_import_optimization_task_button,0)
        
        ins_tool_buttons_layout.addStretch()
    # region
    def __slotCreateOptimizationTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        exist_tasks_name_list = [ins_task_table.item(i,0).text() for i in range(ins_task_table.rowCount())]
        
        fea_tasks_full_name_list = []
        ins_main_window = self.parent()
        for dir_name in os.listdir(ins_main_window.work_path):
            if dir_name.endswith('.task'):
                fea_task_file_full_name = ins_main_window.work_path+os.sep+dir_name

                checked_state_number = 0
                try:
                    with h5py.File(fea_task_file_full_name,'r') as ins_fea_task_file:
                        if len(ins_fea_task_file['Mesh']) == 0:
                            checked_state_number = 1
                        else:
                            pass
                        
                        if checked_state_number == 0:
                            if numpy.any(ins_fea_task_file['Mesh']['materials'][:]==0):
                                checked_state_number = 2
                            else:
                                pass
                        else:
                            pass
                        
                        if checked_state_number == 0:
                            if numpy.any(ins_fea_task_file['Mesh']['attributes'][:]==0):
                                checked_state_number = 3
                            else:
                                pass
                        else:
                            pass
                        
                        if checked_state_number == 0:
                            if numpy.any(ins_fea_task_file['Mesh']['type'][:]==0):
                                checked_state_number = 4
                            else:
                                pass
                        else:
                            pass
                
                        if checked_state_number == 0:
                            if len(ins_fea_task_file['Steps']) == 0:
                                checked_state_number = 5
                            else:
                                pass
                        else:
                            pass
                        
                        if checked_state_number == 0:
                            if len(ins_fea_task_file['Outputs']['Nodes']) == 0 and len(ins_fea_task_file['Outputs']['Elements']) == 0:
                                checked_state_number = 6
                            else:
                                pass
                        else:
                            pass
                
                        if checked_state_number == 0:
                            if len(ins_fea_task_file['Conditions']) == 0:
                                checked_state_number = 7
                            else:
                                pass
                        else:
                            pass
                        
                        if ins_fea_task_file['basic'][1] == b'FEM':
                            pass
                        else:
                            pass
                except:
                    checked_state_number = -1
                else:
                    pass
                
                if checked_state_number == 0:
                    fea_tasks_full_name_list.append(fea_task_file_full_name)
                else:
                    pass
            else:   pass
        
        ins_create_task_dialog = _CreateOptimizationTaskDialog(self, exist_tasks_name_list, fea_tasks_full_name_list)
        ins_create_task_dialog.show()
        if ins_create_task_dialog.exec() == QtWidgets.QDialog.Accepted:
            optimization_information_dict = ins_create_task_dialog.getOptimizationInformation()
            
            optimization_type = optimization_information_dict['type']
            basic_parameters = optimization_information_dict['basic']
            optimization_parameters = optimization_information_dict['optimization']

            if optimization_type == '':
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','Optimization type is empty!')
                ins_create_task_dialog.deleteLater()
                return None
            elif basic_parameters[0] == '':
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','The finite element analysis task is empty!')
                ins_create_task_dialog.deleteLater()
                return None
            elif basic_parameters[1] == '':
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','The design domain is empty!')
                ins_create_task_dialog.deleteLater()
                return None
            elif basic_parameters[6] == []:
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','Objective is empty!')
                ins_create_task_dialog.deleteLater()
                return None
            elif len(basic_parameters[6]) > 1:
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','Currently only a single objective is supported.')
                ins_create_task_dialog.deleteLater()
                return None
            elif len(set([i[0]+i[1] for i in basic_parameters[6]])) < len([i[0]+i[1] for i in basic_parameters[6]]):
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','The objective cannot be duplicated!')
                ins_create_task_dialog.deleteLater()
                return None
            elif len(set([i[0]+i[1] for i in basic_parameters[7]])) < len([i[0]+i[1] for i in basic_parameters[7]]):
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','The constraint cannot be duplicated!')
                ins_create_task_dialog.deleteLater()
                return None
            elif set([i[0]+i[1] for i in basic_parameters[6]]) & set([i[0]+i[1] for i in basic_parameters[7]]) != set():
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','The objective and the constraint cannot be duplicated!')
                ins_create_task_dialog.deleteLater()
                return None
            else:
                pass
            
            if optimization_type == 'topology optimization' and optimization_parameters['Density'][1] >= optimization_parameters['Density'][2]:
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','Maximum limitation must be greater than minimum limitation!')
                ins_create_task_dialog.deleteLater()
                return None
            elif basic_parameters[7] == [] and optimization_parameters['Algorithm'][2] != 'ADAM':
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','The optimization with none constrain currently only supports ADAM algorithm!')
                ins_create_task_dialog.deleteLater()
                return None
            elif basic_parameters[7] != [] and optimization_parameters['Algorithm'][2] == 'ADAM':
                QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error','ADAM is an unconstrained optimization algorithm!')
                ins_create_task_dialog.deleteLater()
                return None
            else:
                pass
            if optimization_parameters['Binaryzation'][0] == 'volume constraint':
                optimization_parameters['Binaryzation'][0] = 'none'
                
                for i in basic_parameters[7]:
                    if i[0] == 'VOL':
                        optimization_parameters['Binaryzation'][0] = 'volume constraint'                            
                        optimization_parameters['Binaryzation'][1] = i[-1]

                        break
                    else:
                        pass
            else:
                pass
            
            optimization_folder_name = ins_main_window.work_path + os.sep + optimization_information_dict['name']
            if os.path.exists(optimization_folder_name):
                ins_response_button = QtWidgets.QMessageBox.question(self,'Create Optimization Task Waring','The optimization file already exist,overwrite?')
                if ins_response_button == QtWidgets.QMessageBox.Yes:
                    try:
                        shutil.rmtree(optimization_folder_name)
                    except:
                        QtWidgets.QMessageBox.information(self,'Create Optimization Task Waring',"The original optimizaotin files can't delete!")
                        ins_create_task_dialog.deleteLater()
                        return None
                    else:
                        pass
                else:
                    ins_create_task_dialog.deleteLater()
                    return None
            else:
                pass
            os.makedirs(optimization_folder_name)
            shutil.copy(basic_parameters[0],optimization_folder_name)
            
            task_file_full_name = optimization_folder_name + os.sep + optimization_information_dict['name'] + '.optim'
            fea_task_name = os.path.basename(basic_parameters[0]).split('.')[0]
            with h5py.File(task_file_full_name,'w') as ins_optim_file:
                ins_basic_group = ins_optim_file.create_group(name='Basic')
                # region
                ins_basic_parameters_set = ins_basic_group.create_dataset(name='parameters',shape=7,dtype=h5py.string_dtype(encoding='utf-8'))
                ins_basic_parameters_set[0] = optimization_type
                ins_basic_parameters_set[1] = fea_task_name
                ins_basic_parameters_set[2] = basic_parameters[1]
                ins_basic_parameters_set[3] = basic_parameters[2]
                ins_basic_parameters_set[4] = basic_parameters[3]
                ins_basic_parameters_set[5] = basic_parameters[4]
                ins_basic_parameters_set[6] = basic_parameters[5]
                
                ins_basic_objectives_set = ins_basic_group.create_dataset(name='objectives',shape=(len(basic_parameters[6]),len(basic_parameters[6][0])),dtype=h5py.string_dtype(encoding='utf-8'))
                for objective_index,objective_params_list in enumerate(basic_parameters[6]):
                    for param_index,param_value in enumerate(objective_params_list):
                        ins_basic_objectives_set[objective_index,param_index] = param_value

                if basic_parameters[7] == []:
                    pass
                else:
                    ins_basic_constrains_set = ins_basic_group.create_dataset(name='constrains',shape=(len(basic_parameters[7]),len(basic_parameters[7][0])),dtype=h5py.string_dtype(encoding='utf-8'))
                    for constrain_index,constrain_params_list in enumerate(basic_parameters[7]):
                        for param_index,param_value in enumerate(constrain_params_list):
                            ins_basic_constrains_set[constrain_index,param_index] = param_value
                # endregion
                
                if optimization_type == 'topology optimization':
                    ins_topology_optimization_group = ins_optim_file.create_group(name='TopologyOptimization')

                    ins_topology_optimization_group.create_dataset(name='density',data=numpy.asarray(optimization_parameters['Density']),dtype=numpy.dtype('float64'))
                    
                    ins_convergence_set = ins_topology_optimization_group.create_dataset(name='convergence',shape=4,dtype=h5py.string_dtype(encoding='utf-8'))
                    ins_convergence_set[0] = optimization_parameters['Convergence'][0]
                    ins_convergence_set[1] = str(optimization_parameters['Convergence'][1])
                    ins_convergence_set[2] = str(optimization_parameters['Convergence'][2])
                    ins_convergence_set[3] = str(optimization_parameters['Convergence'][3])
                    
                    ins_algorithm_set = ins_topology_optimization_group.create_dataset(name='algorithm',shape=3,dtype=h5py.string_dtype(encoding='utf-8'))
                    ins_algorithm_set[0] = optimization_parameters['Algorithm'][0]
                    ins_algorithm_set[1] = str(optimization_parameters['Algorithm'][1])
                    ins_algorithm_set[2] = optimization_parameters['Algorithm'][2]
                    
                    ins_filter_set = ins_topology_optimization_group.create_dataset(name='filter',shape=4,dtype=h5py.string_dtype(encoding='utf-8'))
                    ins_filter_set[0] = optimization_parameters['Filter'][0]
                    ins_filter_set[1] = optimization_parameters['Filter'][1]
                    ins_filter_set[2] = str(optimization_parameters['Filter'][2])
                    ins_filter_set[3] = str(optimization_parameters['Filter'][3])
                    
                    ins_binaryzation_set = ins_topology_optimization_group.create_dataset(name='binaryzation',shape=3,dtype=h5py.string_dtype(encoding='utf-8'))
                    ins_binaryzation_set[0] = optimization_parameters['Binaryzation'][0]
                    ins_binaryzation_set[1] = str(optimization_parameters['Binaryzation'][1])
                    ins_binaryzation_set[2] = str(optimization_parameters['Binaryzation'][2])
                else:
                    pass

            ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
            ins_task_table.insertRow(ins_task_table.rowCount())
            ins_name_item = QtWidgets.QTableWidgetItem()
            ins_name_item.setTextAlignment(QtCore.Qt.AlignCenter)
            ins_name_item.setText(optimization_information_dict['name'])
            ins_task_table.setItem(ins_task_table.rowCount()-1,0,ins_name_item)
            ins_source_item = QtWidgets.QTableWidgetItem()
            ins_source_item.setTextAlignment(QtCore.Qt.AlignCenter)
            ins_source_item.setText(os.path.basename(basic_parameters[0]).split('.')[0])
            ins_task_table.setItem(ins_task_table.rowCount()-1,1,ins_source_item)
            ins_type_item = QtWidgets.QTableWidgetItem()
            ins_type_item.setTextAlignment(QtCore.Qt.AlignCenter)
            ins_type_item.setText(optimization_type)
            ins_task_table.setItem(ins_task_table.rowCount()-1,2,ins_type_item)
            ins_time_item = QtWidgets.QTableWidgetItem()
            ins_time_item.setTextAlignment(QtCore.Qt.AlignCenter)
            ins_time_item.setText('none')
            ins_task_table.setItem(ins_task_table.rowCount()-1,3,ins_time_item)
            ins_state_item = QtWidgets.QTableWidgetItem()
            ins_state_item.setTextAlignment(QtCore.Qt.AlignCenter)
            ins_state_item.setText('output')
            ins_task_table.setItem(ins_task_table.rowCount()-1,4,ins_state_item)
            ins_task_table.selectRow(ins_task_table.rowCount()-1)
        else:
            pass
        ins_create_task_dialog.deleteLater()
    def __slotImportOptimizationTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        task_name_list = [ins_task_table.item(i,0).text() for i in range(ins_task_table.rowCount())]
        
        ins_main_window = self.parent()
        imported_task_file_full_name, _ = QtWidgets.QFileDialog.getOpenFileName(self,'Select Optimizatoin Task File',ins_main_window.work_path,'P4Struct Optimizatoin Task File(*.optim)')
        if imported_task_file_full_name == '':
            return None
        else:
            pass
        
        imported_task_name = os.path.basename(imported_task_file_full_name).split('.',1)[0]
        if imported_task_name in task_name_list:
            QtWidgets.QMessageBox.warning(self,'Import Optimization Task File Waring','The task already exist!')
            return None
        else:
            pass
        
        with h5py.File(imported_task_file_full_name,'r') as ins_task_file:
            optimization_type_name = str(ins_task_file['Basic']['parameters'][0],'utf-8')
            fea_task_name = str(ins_task_file['Basic']['parameters'][1],'utf-8')
            
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        ins_task_table.insertRow(ins_task_table.rowCount())
        ins_name_item = QtWidgets.QTableWidgetItem()
        ins_name_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_name_item.setText(imported_task_name)
        ins_task_table.setItem(ins_task_table.rowCount()-1,0,ins_name_item)
        ins_source_item = QtWidgets.QTableWidgetItem()
        ins_source_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_source_item.setText(fea_task_name)
        ins_task_table.setItem(ins_task_table.rowCount()-1,1,ins_source_item)
        ins_type_item = QtWidgets.QTableWidgetItem()
        ins_type_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_type_item.setText(optimization_type_name)
        ins_task_table.setItem(ins_task_table.rowCount()-1,2,ins_type_item)
        ins_time_item = QtWidgets.QTableWidgetItem()
        ins_time_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_time_item.setText('none')
        ins_task_table.setItem(ins_task_table.rowCount()-1,3,ins_time_item)
        ins_state_item = QtWidgets.QTableWidgetItem()
        ins_state_item.setTextAlignment(QtCore.Qt.AlignCenter)
        ins_state_item.setText('output')
        ins_task_table.setItem(ins_task_table.rowCount()-1,4,ins_state_item)
        ins_task_table.selectRow(ins_task_table.rowCount()-1)
    # endregion
    
    def __initializeTaskTable(self, in_ins_manager_layout:object) -> None:
        ins_task_table = QtWidgets.QTableWidget(self)
        in_ins_manager_layout.addWidget(ins_task_table,1)
        
        ins_task_table.setObjectName('optimization-task-table')
        ins_task_table.setColumnCount(5)
        ins_task_table.setHorizontalHeaderLabels(['Name','Source','Type','Time','State'])
        ins_task_table.horizontalHeader().setSectionsClickable(False)
        ins_task_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_task_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ins_task_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        ins_task_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_task_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        ins_task_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        ins_task_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        ins_task_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        ins_task_table.customContextMenuRequested.connect(self.__slotTableRightMenu)
    # region
    def __slotTableRightMenu(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        if ins_task_table.currentRow() == -1:
            return None
        else:
            pass

        ins_item_right_menu = QtWidgets.QMenu(self)

        if ins_task_table.item(ins_task_table.currentRow(),4).text() == 'output':
            ins_check_task = ins_item_right_menu.addAction('check')
            ins_check_task.triggered.connect(self.__slotCheckTask)
            
            ins_item_right_menu.addSeparator()
            
            ins_rename_task = ins_item_right_menu.addAction('rename')
            ins_rename_task.triggered.connect(self.__slotRenameTask)
            ins_edit_task = ins_item_right_menu.addAction('edit')
            ins_edit_task.triggered.connect(self.__slotEditTask)
            
            ins_item_right_menu.addSeparator()
                
            ins_delete_task = ins_item_right_menu.addAction('delete task')
            ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
            ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
            ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
            ins_delete_all = ins_item_right_menu.addAction('delete all')
            ins_delete_all.triggered.connect(self.__slotDeleteTaskAll)
        elif ins_task_table.item(ins_task_table.currentRow(),4).text() == 'checked':
            ins_submit_task = ins_item_right_menu.addAction('submit')
            ins_submit_task.triggered.connect(self.__slotSubmitTask)
            
            ins_item_right_menu.addSeparator()
            
            ins_check_task = ins_item_right_menu.addAction('check')
            ins_check_task.triggered.connect(self.__slotCheckTask)
            ins_rename_task = ins_item_right_menu.addAction('rename')
            ins_rename_task.triggered.connect(self.__slotRenameTask)
            ins_edit_task = ins_item_right_menu.addAction('edit')
            ins_edit_task.triggered.connect(self.__slotEditTask)
            
            ins_item_right_menu.addSeparator()
            
            ins_delete_task = ins_item_right_menu.addAction('delete task')
            ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
            ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
            ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
            ins_delete_all = ins_item_right_menu.addAction('delete all')
            ins_delete_all.triggered.connect(self.__slotDeleteTaskAll)
        elif ins_task_table.item(ins_task_table.currentRow(),4).text() == 'running':
            ins_stop_task = ins_item_right_menu.addAction('stop')
            ins_stop_task.triggered.connect(self.__slotStopRunningTask)
        elif ins_task_table.item(ins_task_table.currentRow(),4).text() == 'ready':
            ins_stop_task = ins_item_right_menu.addAction('cancel')
            ins_stop_task.triggered.connect(self.__slotCancelReadytask)
        elif ins_task_table.item(ins_task_table.currentRow(),4).text() in ['finished','check error','computation error']:
            ins_check_task = ins_item_right_menu.addAction('check')
            ins_check_task.triggered.connect(self.__slotCheckTask)
            
            ins_item_right_menu.addSeparator()
                
            ins_rename_task = ins_item_right_menu.addAction('rename')
            ins_rename_task.triggered.connect(self.__slotRenameTask)
            ins_edit_task = ins_item_right_menu.addAction('edit')
            ins_edit_task.triggered.connect(self.__slotEditTask)
            
            ins_item_right_menu.addSeparator()
            
            ins_delete_task = ins_item_right_menu.addAction('delete task')
            ins_delete_task.triggered.connect(self.__slotDeleteTaskRow)
            ins_delete_task_result = ins_item_right_menu.addAction('delete(result file)')
            ins_delete_task_result.triggered.connect(self.__slotDeleteTaskResult)
            ins_delete_all = ins_item_right_menu.addAction('delete all')
            ins_delete_all.triggered.connect(self.__slotDeleteTaskAll)
        else:
            pass

        ins_item_right_menu.exec(QtGui.QCursor.pos())
    
    def __slotCheckTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()

        ins_main_window = self.parent()
        task_folder_name = ins_main_window.work_path + os.sep + task_name
        if os.path.exists(task_folder_name):
            pass
        else:
            QtWidgets.QMessageBox.critical(self,'Check Optimization Task Error',"The work path doesn't contain optimization task folder!")
            return None
        
        task_file_full_name = task_folder_name + os.sep + task_name + '.optim'
        if os.path.exists(task_file_full_name):
            pass
        else:
            QtWidgets.QMessageBox.critical(self,'Check Optimization Task Error',"The optimization folder doesn't contain optimization task file with the same name!")
            return None

        fea_task_name = ins_task_table.item(ins_task_table.currentRow(),1).text()
        fea_task_file_full_name = task_folder_name + os.sep + fea_task_name + '.task'
        if os.path.exists(fea_task_file_full_name):
            pass
        else:
            QtWidgets.QMessageBox.critical(self,'Check Optimization Task Error',"The optimization folder doesn't contain selected task file of finite element analysus!")
            return None
        
        for dir_name in os.listdir(task_folder_name):
            dir_full_name = task_folder_name + os.sep + dir_name

            if os.path.isdir(dir_full_name):
                try:
                    shutil.rmtree(dir_full_name)
                except:
                    QtWidgets.QMessageBox.information(self,'Check Optimization Task Error',f"The optimization result folder -{dir_name} can't delete!")
                    return None
                else:
                    pass
            elif dir_name == task_name + '.pro':
                os.remove(dir_full_name)
            elif dir_name.split('.')[-1] == ".res":
                try:
                    os.remove(dir_full_name)
                except:
                    QtWidgets.QMessageBox.information(self,'Check Optimization Task Error',f"The optimization result can't delete!")
                    return None
                else:
                    pass
            else:
                continue
        
        ins_task_table.item(ins_task_table.currentRow(),3).setText('none')
        ins_task_table.item(ins_task_table.currentRow(),4).setText('checked')
    def __slotRenameTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        task_name_list = [ins_task_table.item(i,0).text() for i in range(ins_task_table.rowCount())]

        old_task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()

        ins_main_window = self.parent()
        while True:
            new_task_name,user_state = QtWidgets.QInputDialog.getText(self,'Rename Task Waring','The task name already exist!\n Please input a new task name.')
            if user_state:
                if new_task_name in task_name_list:
                    continue
                else:
                    old_task_folder_name = ins_main_window.work_path + os.sep + old_task_name
                    new_task_folder_name = ins_main_window.work_path + os.sep + new_task_name
                    os.rename(old_task_folder_name,new_task_folder_name)
                    
                    old_task_full_name = new_task_folder_name+os.sep + old_task_name+'.optim'
                    new_task_full_name = new_task_folder_name+os.sep + new_task_name+'.optim'
                    if os.path.exists(old_task_full_name):
                        os.rename(old_task_full_name,new_task_full_name)
                    else:
                        pass
                    
                    ins_task_table.item(ins_task_table.currentRow(),0).setText(new_task_name)
                    break
            else:
                return None
    def __slotEditTask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        
        ins_main_window = self.parent()
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        task_folder_name = ins_main_window.work_path + os.sep + task_name
        if os.path.exists(task_folder_name):
            pass
        else:
            QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error',"The optimization task folder doesn't exist!")
            return None
        task_file_full_name = task_folder_name + os.sep + task_name + '.optim'
        if os.path.exists(task_file_full_name):
            pass
        else:
            QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error',"The optimization task file doesn't exist!")
            return None
        
        fea_task_file_full_name = task_folder_name + os.sep + ins_task_table.item(ins_task_table.currentRow(),1).text() + '.task'
        if os.path.exists(fea_task_file_full_name):
            pass
        else:
            fea_task_file_full_name = None
        
        task_type = ins_task_table.item(ins_task_table.currentRow(),2).text()
        with h5py.File(task_file_full_name,'r') as ins_optim_file:
            optimization_information_dict = {'name':task_name,'type':None,'basic':[],'optimization':{}}
            
            if task_type == 'topology optimization':
                optimization_information_dict['type'] = 'topology optimization'
                
                ins_basic_parameters_set = ins_optim_file['Basic']['parameters']
                
                if fea_task_file_full_name is None:
                    optimization_information_dict['basic'].append('')
                    optimization_information_dict['basic'].append('')
                else:
                    optimization_information_dict['basic'].append(fea_task_file_full_name)
                    optimization_information_dict['basic'].append(str(ins_basic_parameters_set[2],'utf-8'))
                optimization_information_dict['basic'].append(str(ins_basic_parameters_set[3],'utf-8'))
                optimization_information_dict['basic'].append(str(ins_basic_parameters_set[4],'utf-8'))
                optimization_information_dict['basic'].append(str(ins_basic_parameters_set[5],'utf-8'))
                optimization_information_dict['basic'].append(str(ins_basic_parameters_set[6],'utf-8'))

                optimization_information_dict['basic'].append([])
                ins_basic_objectives_set = ins_optim_file['Basic']['objectives'][:]
                for objective_parameters_array in ins_basic_objectives_set:
                    optimization_information_dict['basic'][6].append([str(i,'utf-8') for i in objective_parameters_array])
                optimization_information_dict['basic'].append([])
                if 'constrains' in ins_optim_file['Basic']:
                    ins_basic_constrains_set = ins_optim_file['Basic']['constrains'][:]
                    for constrain_parameters_array in ins_basic_constrains_set:
                        optimization_information_dict['basic'][7].append([str(i,'utf-8') for i in constrain_parameters_array])
                else:
                    pass

                optimization_information_dict['optimization']['Density'] = [i for i in ins_optim_file['TopologyOptimization']['density'][:]]
                optimization_information_dict['optimization']['Convergence'] = [str(i,'utf-8') for i in ins_optim_file['TopologyOptimization']['convergence'][:]]
                optimization_information_dict['optimization']['Algorithm'] = [str(i,'utf-8') for i in ins_optim_file['TopologyOptimization']['algorithm'][:]]
                optimization_information_dict['optimization']['Filter'] = [str(i,'utf-8') for i in ins_optim_file['TopologyOptimization']['filter'][:]]
                optimization_information_dict['optimization']['Binaryzation'] = [str(i,'utf-8') for i in ins_optim_file['TopologyOptimization']['binaryzation'][:]]
            else:
                pass
        
        if optimization_information_dict['basic'][0] == '':
            fea_tasks_full_name_list = []
        else:
            fea_tasks_full_name_list = [optimization_information_dict['basic'][0]]
        ins_main_window = self.parent()
        for dir_name in os.listdir(ins_main_window.work_path):
            if dir_name.endswith('.task'):
                fea_task_file_full_name = ins_main_window.work_path+os.sep+dir_name

                checked_state_number = 0
                try:
                    with h5py.File(fea_task_file_full_name,'r') as ins_fea_task_file:
                        if len(ins_fea_task_file['Mesh']) == 0:
                            checked_state_number = 1
                        else:
                            pass
                        
                        if checked_state_number == 0:
                            if numpy.any(ins_fea_task_file['Mesh']['materials'][:]==0):
                                checked_state_number = 2
                            else:
                                pass
                        else:
                            pass
                        
                        if checked_state_number == 0:
                            if numpy.any(ins_fea_task_file['Mesh']['attributes'][:]==0):
                                checked_state_number = 3
                            else:
                                pass
                        else:
                            pass
                        
                        if checked_state_number == 0:
                            if numpy.any(ins_fea_task_file['Mesh']['type'][:]==0):
                                checked_state_number = 4
                            else:
                                pass
                        else:
                            pass
                
                        if checked_state_number == 0:
                            if len(ins_fea_task_file['Steps']) == 0:
                                checked_state_number = 5
                            else:
                                pass
                        else:
                            pass
                        
                        if checked_state_number == 0:
                            if len(ins_fea_task_file['Outputs']['Nodes']) == 0 and len(ins_fea_task_file['Outputs']['Elements']) == 0:
                                checked_state_number = 6
                            else:
                                pass
                        else:
                            pass
                
                        if checked_state_number == 0:
                            if len(ins_fea_task_file['Conditions']) == 0:
                                checked_state_number = 7
                            else:
                                pass
                        else:
                            pass
                        
                        if ins_fea_task_file['basic'][1] == b'FEM':
                            pass
                        else:
                            pass
                except:
                    checked_state_number = -1
                else:
                    pass
                
                if checked_state_number == 0:
                    fea_tasks_full_name_list.append(fea_task_file_full_name)
                else:
                    pass
            else:
                pass
        
        ins_create_task_dialog = _CreateOptimizationTaskDialog(self, [], fea_tasks_full_name_list)
        ins_create_task_dialog.setOptimizationInformation(optimization_information_dict)
        ins_create_task_dialog.show()
        if ins_create_task_dialog.exec() == QtWidgets.QDialog.Accepted:
            optimization_information_dict = ins_create_task_dialog.getOptimizationInformation()

            optimization_type = optimization_information_dict['type']
            basic_parameters = optimization_information_dict['basic']
            optimization_parameters = optimization_information_dict['optimization']

            if basic_parameters[0] == '':
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','The finite element analysis task is empty!')
                ins_create_task_dialog.deleteLater()
                return None
            elif basic_parameters[1] == '':
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','The design domain is empty!')
                ins_create_task_dialog.deleteLater()
                return None
            elif basic_parameters[6] == []:
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','Objective is empty!')
                ins_create_task_dialog.deleteLater()
                return None
            elif len(basic_parameters[6]) > 1:
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','Currently only a single objective is supported.')
                ins_create_task_dialog.deleteLater()
                return None
            elif len(set([i[0]+i[1] for i in basic_parameters[6]])) < len([i[0]+i[1] for i in basic_parameters[6]]):
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','The objective cannot be duplicated!')
                ins_create_task_dialog.deleteLater()
                return None
            elif len(set([i[0]+i[1] for i in basic_parameters[7]])) < len([i[0]+i[1] for i in basic_parameters[7]]):
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','The constraint cannot be duplicated!')
                ins_create_task_dialog.deleteLater()
                return None
            elif set([i[0]+i[1] for i in basic_parameters[6]]) & set([i[0]+i[1] for i in basic_parameters[7]]) != set():
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','The objective and the constraint cannot be duplicated!')
                ins_create_task_dialog.deleteLater()
                return None
            else:
                pass
            
            if optimization_type == 'topology optimization' and optimization_parameters['Density'][1] >= optimization_parameters['Density'][2]:
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','Maximum limitation must be greater than minimum limitation!')
                ins_create_task_dialog.deleteLater()
                return None
            elif basic_parameters[7] == [] and optimization_parameters['Algorithm'][2] != 'ADAM':
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','The optimization with none constrain currently only supports ADAM algorithm!')
                ins_create_task_dialog.deleteLater()
                return None
            elif basic_parameters[7] != [] and optimization_parameters['Algorithm'][2] == 'ADAM':
                QtWidgets.QMessageBox.critical(self,'Edit Optimization Task Error','ADAM is an unconstrained optimization algorithm!')
                ins_create_task_dialog.deleteLater()
                return None
            else:
                pass
            if optimization_parameters['Binaryzation'][0] == 'volume constraint':
                optimization_parameters['Binaryzation'][0] = 'none'
                
                for i in basic_parameters[7]:
                    if i[0] == 'VOL':
                        optimization_parameters['Binaryzation'][0] = 'volume constraint'                            
                        optimization_parameters['Binaryzation'][1] = i[-1]

                        break
                    else:
                        pass
            else:
                pass
            
            fea_task_name = os.path.basename(basic_parameters[0]).split('.')[0]
            if os.path.exists(task_folder_name + os.sep + fea_task_name + '.task'):
                pass
            else:
                shutil.copy(basic_parameters[0],task_folder_name)
            
            with h5py.File(task_file_full_name,'w') as ins_optim_file:
                ins_basic_group = ins_optim_file.create_group(name='Basic')
                # region
                ins_basic_parameters_set = ins_basic_group.create_dataset(name='parameters',shape=7,dtype=h5py.string_dtype(encoding='utf-8'))
                ins_basic_parameters_set[0] = optimization_type
                ins_basic_parameters_set[1] = fea_task_name
                ins_basic_parameters_set[2] = basic_parameters[1]
                ins_basic_parameters_set[3] = basic_parameters[2]
                ins_basic_parameters_set[4] = basic_parameters[3]
                ins_basic_parameters_set[5] = basic_parameters[4]
                ins_basic_parameters_set[6] = basic_parameters[5]
                
                ins_basic_objectives_set = ins_basic_group.create_dataset(name='objectives',shape=(len(basic_parameters[6]),len(basic_parameters[6][0])),dtype=h5py.string_dtype(encoding='utf-8'))
                for objective_index,objective_params_list in enumerate(basic_parameters[6]):
                    for param_index,param_value in enumerate(objective_params_list):
                        ins_basic_objectives_set[objective_index,param_index] = param_value

                if basic_parameters[7] == []:
                    pass
                else:
                    ins_basic_constrains_set = ins_basic_group.create_dataset(name='constrains',shape=(len(basic_parameters[7]),len(basic_parameters[7][0])),dtype=h5py.string_dtype(encoding='utf-8'))
                    for constrain_index,constrain_params_list in enumerate(basic_parameters[7]):
                        for param_index,param_value in enumerate(constrain_params_list):
                            ins_basic_constrains_set[constrain_index,param_index] = param_value
                # endregion
                
                if optimization_type == 'topology optimization':
                    ins_topology_optimization_group = ins_optim_file.create_group(name='TopologyOptimization')

                    ins_topology_optimization_group.create_dataset(name='density',data=numpy.asarray(optimization_parameters['Density']),dtype=numpy.dtype('float64'))
                    
                    ins_convergence_set = ins_topology_optimization_group.create_dataset(name='convergence',shape=4,dtype=h5py.string_dtype(encoding='utf-8'))
                    ins_convergence_set[0] = optimization_parameters['Convergence'][0]
                    ins_convergence_set[1] = str(optimization_parameters['Convergence'][1])
                    ins_convergence_set[2] = str(optimization_parameters['Convergence'][2])
                    ins_convergence_set[3] = str(optimization_parameters['Convergence'][3])
                    
                    ins_algorithm_set = ins_topology_optimization_group.create_dataset(name='algorithm',shape=3,dtype=h5py.string_dtype(encoding='utf-8'))
                    ins_algorithm_set[0] = optimization_parameters['Algorithm'][0]
                    ins_algorithm_set[1] = str(optimization_parameters['Algorithm'][1])
                    ins_algorithm_set[2] = optimization_parameters['Algorithm'][2]
                    
                    ins_filter_set = ins_topology_optimization_group.create_dataset(name='filter',shape=4,dtype=h5py.string_dtype(encoding='utf-8'))
                    ins_filter_set[0] = optimization_parameters['Filter'][0]
                    ins_filter_set[1] = optimization_parameters['Filter'][1]
                    ins_filter_set[2] = str(optimization_parameters['Filter'][2])
                    ins_filter_set[3] = str(optimization_parameters['Filter'][3])
                    
                    ins_binaryzation_set = ins_topology_optimization_group.create_dataset(name='binaryzation',shape=3,dtype=h5py.string_dtype(encoding='utf-8'))
                    ins_binaryzation_set[0] = optimization_parameters['Binaryzation'][0]
                    ins_binaryzation_set[1] = str(optimization_parameters['Binaryzation'][1])
                    ins_binaryzation_set[2] = str(optimization_parameters['Binaryzation'][2])
                else:
                    pass

            ins_task_table.item(ins_task_table.currentRow(),3).setText('none')
            ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
        else:
            pass
        ins_create_task_dialog.deleteLater()
    def __slotSubmitTask(self) -> None:
        if self.__task_process_dict == {}:
            computer_memory_info = psutil.virtual_memory()
            memory_usage_ratio = computer_memory_info.used / computer_memory_info.total
            if memory_usage_ratio > 0.92:
                QtWidgets.QMessageBox.warning(self,'Submit Optimization Task Waring','The used memory greater than 92%! Unable to submit new task.')
                return None
            else:
                pass
            
            ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
            task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
            task_folder_name = self.parent().work_path + os.sep + task_name
            
            if os.path.exists(task_folder_name):
                pass
            else:
                ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                
                QtWidgets.QMessageBox.critical(self,'Submit Optimization Task Error',"The work path doesn't contain optimization task folder!")
                return None
        
            task_file_full_name = task_folder_name + os.sep + task_name + '.optim'
            if os.path.exists(task_file_full_name):
                pass
            else:
                ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                
                QtWidgets.QMessageBox.critical(self,'Submit Optimization Task Error',"The optimization folder doesn't contain optimization task file with the same name!")
                return None

            fea_task_name = ins_task_table.item(ins_task_table.currentRow(),1).text()
            fea_task_file_full_name = task_folder_name + os.sep + fea_task_name + '.task'
            if os.path.exists(fea_task_file_full_name):
                pass
            else:
                ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                
                QtWidgets.QMessageBox.critical(self,'Submit Optimization Task Error',"The optimization folder doesn't contain selected task file of finite element analysis!")
                return None
        
            for dir_name in os.listdir(task_folder_name):
                dir_full_name = task_folder_name + os.sep + dir_name

                if os.path.isdir(dir_full_name):
                    try:
                        shutil.rmtree(dir_full_name)
                    except:
                        ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                        
                        QtWidgets.QMessageBox.information(self,'Submit Optimization Task Error',f"The optimization result folder -{dir_name} can't delete!")
                        return None
                    else:
                        pass
                elif dir_name == task_name + 'pro':
                    os.remove(dir_full_name)
                elif dir_name.split('.')[-1] == 'res':
                    try:
                        os.remove(dir_full_name)
                    except:
                        ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                        
                        QtWidgets.QMessageBox.information(self,'Submit Optimization Task Error',f"The optimization result has been opened!")
                        return None
                    else:
                        pass
                else:
                    continue
            for temp_file_full_name in glob.glob(self.parent().work_path+os.sep+task_name+os.sep+'*.femtemp'):
                if os.path.isfile(temp_file_full_name):
                    os.remove(temp_file_full_name)
                else:
                    continue
            for temp_file_full_name in glob.glob(self.parent().work_path+os.sep+task_name+os.sep+'*.opttemp'):
                if os.path.isfile(temp_file_full_name):
                    os.remove(temp_file_full_name)
                else:
                    continue
        
            ins_current_time = datetime.datetime.now()
            current_time_text = str(ins_current_time.year) + '-' + str(ins_current_time.month) + '-' + str(ins_current_time.day) + ' ' + str(ins_current_time.hour) + ':' + str(ins_current_time.minute) + ':' + str(ins_current_time.second)
            ins_task_table.item(ins_task_table.currentRow(),3).setText(current_time_text)
            ins_task_table.item(ins_task_table.currentRow(),3).setToolTip(current_time_text)
            ins_task_table.item(ins_task_table.currentRow(),4).setText('running')
            
            task_type = ins_task_table.item(ins_task_table.currentRow(),2).text()
            ins_task_process = multiprocessing.Process(target=intoOPTProcess,name=task_name,args=(task_type,task_file_full_name,self.__ins_task_process_queen,),)
            self.__task_process_dict[task_name] = ins_task_process
            ins_task_process.start()
            
            self.__ins_task_state_check_timer.start()
        else:
            ins_task_table.item(ins_task_table.currentRow(),4).setText('ready')
    def __slotStopRunningTask(self) -> None:
        ins_main_window = self.parent()
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        
        ins_task_table.item(ins_task_table.currentRow(),3).setText('none')
        ins_task_table.item(ins_task_table.currentRow(),4).setText('output')

        if isinstance(self.__task_process_dict[task_name], multiprocessing.Process):
            if self.__task_process_dict[task_name].is_alive():
                for ins_subprocess in psutil.Process(self.__task_process_dict[task_name].pid).children(recursive=True):
                    ins_subprocess.terminate()
                    ins_subprocess.wait()

                self.__task_process_dict[task_name].terminate()
                self.__task_process_dict[task_name].join()
            else:
                pass

            self.__task_process_dict[task_name].close()
        else:
            pass
        del self.__task_process_dict[task_name]

        for temp_file_full_name in glob.glob(ins_main_window.work_path+os.sep+task_name+os.sep+'*.femtemp'):
            if os.path.isfile(temp_file_full_name):
                os.remove(temp_file_full_name)
            else:
                continue
        for temp_file_full_name in glob.glob(ins_main_window.work_path+os.sep+task_name+os.sep+'*.opttemp'):
            if os.path.isfile(temp_file_full_name):
                os.remove(temp_file_full_name)
            else:
                continue
        for temp_file_full_name in glob.glob(ins_main_window.work_path+os.sep+task_name+os.sep+'*.pro'):
            if os.path.isfile(temp_file_full_name):
                os.remove(temp_file_full_name)
            else:
                pass
    def __slotCancelReadytask(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
    def __slotDeleteTaskRow(self) -> None:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        ins_task_table.removeRow(ins_task_table.currentRow())
    def __slotDeleteTaskResult(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Delete Optimization Result File Question','The result file will be deleted,continue?')
        if ins_response_button == QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None   
                
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        task_folder_name = self.parent().work_path + os.sep + task_name

        for dir_name in os.listdir(task_folder_name):
            dir_full_name = task_folder_name + os.sep + dir_name

            if os.path.isdir(dir_full_name):
                try:
                    shutil.rmtree(dir_full_name)
                except:
                    QtWidgets.QMessageBox.information(self,'Delete Optimization Results File Error',f"The optimization result folder -{dir_name} can't delete!")
                    return None
                else:
                    pass
            elif dir_name == task_name + '.pro':
                os.remove(dir_full_name)
            elif dir_name.split('.')[-1] == '.res':
                try:
                    os.remove(dir_full_name)
                except:
                    QtWidgets.QMessageBox.information(self,'Delete Optimization Result File Error',f"The optimization result can't delete!")
                    return None
                else:
                    pass
            else:
                    continue
    def __slotDeleteTaskAll(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Delete All Optimization Task File Question','All task file will be deleted,continue?')
        if ins_response_button == QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
        task_folder_name = self.parent().work_path + os.sep + task_name
        try:
            shutil.rmtree(task_folder_name)
            
            ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
            ins_task_table.removeRow(ins_task_table.currentRow())
        except:
            QtWidgets.QMessageBox.information(self,'Delete Optimization Folder File Error',f"The optimization folder -{task_folder_name} can't delete!")
        else:
            pass
            
    def __slotCheckTaskState(self) -> None:
        self.__ins_task_state_check_timer.stop()
        
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        work_path = self.parent().work_path
        
        if self.__ins_task_process_queen.empty():
            pass
        else:
            while True:
                if self.__ins_task_process_queen.empty():
                    break
                else:
                    task_name,task_time_string = self.__ins_task_process_queen.get()
                    
                    for row_index in range(ins_task_table.rowCount()):
                        if ins_task_table.item(row_index,0).text() == task_name:
                            if task_time_string == 'error':
                                ins_task_table.item(row_index,3).setText('none')
                                ins_task_table.item(row_index,3).setToolTip('none')
                                ins_task_table.item(row_index,4).setText('computation error')
                            else:
                                ins_task_table.item(row_index,3).setText(task_time_string)
                                ins_task_table.item(row_index,3).setToolTip(task_time_string)
                                ins_task_table.item(row_index,4).setText("finished")
                            break
                        else:
                            continue
                    
                    if isinstance(self.__task_process_dict[task_name], multiprocessing.Process):
                        if self.__task_process_dict[task_name].is_alive():
                            for ins_subprocess in psutil.Process(self.__task_process_dict[task_name].pid).children(recursive=True):
                                ins_subprocess.terminate()
                                ins_subprocess.wait()
                            
                            self.__task_process_dict[task_name].terminate()
                            self.__task_process_dict[task_name].join()
                        else:
                            pass

                        self.__task_process_dict[task_name].close()
                    else:
                        pass
                    del self.__task_process_dict[task_name]

                    task_process_file_full_name = work_path + os.sep + task_name + os.sep + task_name + '.pro'
                    if os.path.isfile(task_process_file_full_name):
                        os.remove(task_process_file_full_name)
                    else:
                        pass
        
        if self.__task_process_dict == {}:
            for row_index in range(ins_task_table.rowCount()):
                if ins_task_table.item(row_index,4).text() == 'ready':
                    computer_memory_info = psutil.virtual_memory()
                    memory_usage_ratio = computer_memory_info.used / computer_memory_info.total
                    if memory_usage_ratio > 0.92:
                        QtWidgets.QMessageBox.warning(self,'Submit Optimization Task Waring','The used memory greater than 92%!Unable to submit new task.')
                        return None
                    else:
                        pass
                    
                    ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
                    task_name = ins_task_table.item(ins_task_table.currentRow(),0).text()
                    task_folder_name = self.parent().work_path + os.sep + task_name
                    
                    if os.path.exists(task_folder_name):
                        pass
                    else:
                        ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                        
                        QtWidgets.QMessageBox.critical(self,'Submit Optimization Task Error',"The work path doesn't contain optimization task folder!")
                        return None
                
                    task_file_full_name = task_folder_name + os.sep + task_name + '.optim'
                    if os.path.exists(task_file_full_name):
                        pass
                    else:
                        ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                        
                        QtWidgets.QMessageBox.critical(self,'Submit Optimization Task Error',"The optimization folder doesn't contain optimization task file with the same name!")
                        return None

                    fea_task_name = ins_task_table.item(ins_task_table.currentRow(),1).text()
                    fea_task_file_full_name = task_folder_name + os.sep + fea_task_name + '.task'
                    if os.path.exists(fea_task_file_full_name):
                        pass
                    else:
                        ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                        
                        QtWidgets.QMessageBox.critical(self,'Submit Optimization Task Error',"The optimization folder doesn't contain selected task file of finite element analysus!")
                        return None
                
                    for dir_name in os.listdir(task_folder_name):
                        dir_full_name = task_folder_name + os.sep + dir_name

                        if os.path.isdir(dir_full_name):
                            try:
                                shutil.rmtree(dir_full_name)
                            except:
                                ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                                
                                QtWidgets.QMessageBox.information(self,'Submit Optimization Task Error',f"The optimization result folder -{dir_name} can't delete!")
                                return None
                            else:
                                pass
                        elif dir_name == task_name + '.pro':
                            os.remove(dir_full_name)
                        elif dir_name.split('.')[-1] == '.res':
                            try:
                                os.remove(dir_full_name)
                            except:
                                ins_task_table.item(ins_task_table.currentRow(),4).setText('output')
                                
                                QtWidgets.QMessageBox.information(self,'Submit Optimization Task Error',f"The optimization result can't delete!")
                                return None
                            else:
                                pass
                        else:
                            continue
                
                    ins_current_time = datetime.datetime.now()
                    current_time_text = str(ins_current_time.year) + '-' + str(ins_current_time.month) + '-' + str(ins_current_time.day) + ' ' + str(ins_current_time.hour) + ':' + str(ins_current_time.minute) + ':' + str(ins_current_time.second)
                    ins_task_table.item(ins_task_table.currentRow(),3).setText(current_time_text)
                    ins_task_table.item(ins_task_table.currentRow(),3).setToolTip(current_time_text)
                    ins_task_table.item(ins_task_table.currentRow(),4).setText('running')
                    
                    task_type = ins_task_table.item(ins_task_table.currentRow(),2).text()
                    ins_task_process = multiprocessing.Process(target=intoOPTProcess,name=task_name,args=(task_type,task_file_full_name,self.__ins_task_process_queen,),)
                    self.__task_process_dict[task_name] = ins_task_process
                    ins_task_process.start()
                    
                    break
                else:
                    continue
        else:
            pass
        
        if self.__task_process_dict == {}:
            pass
        else:
            self.__ins_task_state_check_timer.start()
    # endregion
    
    def getRuningTaskNumber(self) -> int:
        ins_task_table = self.findChild(QtWidgets.QTableWidget,'optimization-task-table')
        
        running_task_number = 0
        for row_index in range(ins_task_table.rowCount()):
            if ins_task_table.item(row_index,4).text() == 'running':
                running_task_number += 1
            else:
                continue
        
        return running_task_number
class _CreateOptimizationTaskDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_tasks_name:list, in_fea_tasks_full_name:list) -> None:
        super().__init__(parent=in_parent,f=QtCore.Qt.Window)

        self.setWindowTitle('Create Optimization Task')
        self.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint,False)
        self.setFixedSize(700,600)
        
        self.__exist_tasks_name_list = in_exist_tasks_name
        self.__fea_tasks_ful_name_list = in_fea_tasks_full_name
        self.__model_dimension =  None
        
        ins_manager_layout = QtWidgets.QVBoxLayout()
        ins_manager_layout.setContentsMargins(5,5,5,5)
        self.setLayout(ins_manager_layout)

        self.__initializeSelectionTools(ins_manager_layout)
        
        ins_setting_tab_widget = QtWidgets.QTabWidget(self)
        ins_setting_tab_widget.setObjectName('optimization-setting-tabs')
        ins_setting_tab_widget.setContentsMargins(0,0,0,0)
        ins_manager_layout.addWidget(ins_setting_tab_widget,1)
        self.__initializeBasicSettingWidget(ins_setting_tab_widget)
        self.__initializeTopologyOptimizationSettingWidget(ins_setting_tab_widget)
        self.__initializeUserButton(ins_manager_layout)
        
    def __initializeSelectionTools(self, in_ins_dialog_layout:object) -> None:
        ins_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_selection_layout) 
        
        ins_task_name_label = QtWidgets.QLabel('Name:',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignLeft)
        ins_task_name_label.setFixedSize(45,30)
        ins_selection_layout.addWidget(ins_task_name_label,0)
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('task-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Opt_','opt-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckTaskName)
        ins_selection_layout.addWidget(ins_name_line_edit,1)
        
        ins_optimization_type_label = QtWidgets.QLabel('Type:',self)
        ins_optimization_type_label.setFixedSize(40,30)
        ins_selection_layout.addWidget(ins_optimization_type_label,0)
        ins_optimization_type_box = QtWidgets.QComboBox(self)
        ins_optimization_type_box.setObjectName('optimization-type-box')
        ins_optimization_type_box.setFixedSize(220,30)
        ins_optimization_type_box.addItems(['topology optimization'])
        ins_optimization_type_box.setCurrentIndex(-1)
        ins_optimization_type_box.currentTextChanged.connect(self.__slotChangeOptimizationType)
        ins_selection_layout.addWidget(ins_optimization_type_box,0)
    # region
    def __slotCheckTaskName(self, in_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        if in_name in self.__exist_tasks_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    
    def __slotChangeOptimizationType(self, in_type:str) -> None:
        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        for tab_index in range(1,ins_setting_tab_widget.count()):
            if ins_setting_tab_widget.tabText(tab_index) == in_type:
                ins_setting_tab_widget.setTabVisible(tab_index,True)
            else:
                ins_setting_tab_widget.setTabVisible(tab_index,False)
    # endregion
    
    def __initializeBasicSettingWidget(self, in_ins_setting_tab_widget:object) -> None:
        ins_basic_setting_widget = QtWidgets.QWidget(in_ins_setting_tab_widget)
        in_ins_setting_tab_widget.addTab(ins_basic_setting_widget,'basic')
        
        ins_basic_setting_widget.setContentsMargins(0,0,0,0)
        ins_basic_layout = QtWidgets.QVBoxLayout()
        ins_basic_setting_widget.setLayout(ins_basic_layout)
        
        ins_hbox_layout1 = QtWidgets.QHBoxLayout()
        ins_basic_layout.addLayout(ins_hbox_layout1,0)
        ins_model_tip_label = QtWidgets.QLabel('finite element model:',ins_basic_setting_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_model_tip_label.setFixedSize(150,30)
        ins_hbox_layout1.addWidget(ins_model_tip_label,0)
        ins_finite_element_modes_box = QtWidgets.QComboBox(ins_basic_setting_widget)
        ins_finite_element_modes_box.setObjectName('finite-element-models-box')
        ins_finite_element_modes_box.addItems(self.__fea_tasks_ful_name_list)
        ins_finite_element_modes_box.setCurrentIndex(-1)
        ins_finite_element_modes_box.currentTextChanged.connect(self.__slotChangeFiniteElementModel)
        ins_hbox_layout1.addWidget(ins_finite_element_modes_box,1)
        
        ins_hbox_layout2 = QtWidgets.QHBoxLayout()
        ins_basic_layout.addLayout(ins_hbox_layout2,0)
        ins_design_domain_label = QtWidgets.QLabel('design domain:',ins_basic_setting_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_design_domain_label.setFixedSize(110,30)
        ins_hbox_layout2.addWidget(ins_design_domain_label,0)
        ins_elements_groups_box = QtWidgets.QComboBox(ins_basic_setting_widget)
        ins_elements_groups_box.setObjectName('design-domain-groups-box')
        ins_elements_groups_box.setFixedSize(120,30)
        ins_hbox_layout2.addWidget(ins_elements_groups_box,0)
        ins_maximum_cycles_label = QtWidgets.QLabel('maximum cycles:',ins_basic_setting_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_maximum_cycles_label.setFixedSize(122,30)
        ins_hbox_layout2.addWidget(ins_maximum_cycles_label,0)
        ins_maximum_cycles_edit = QtWidgets.QLineEdit(ins_basic_setting_widget)
        ins_maximum_cycles_edit.setObjectName('maximum-cycles-edit')
        ins_maximum_cycles_edit.setFixedSize(65,30)
        ins_maximum_cycles_edit.setMaxLength(5)
        ins_maximum_cycles_edit.setText('30')
        ins_maximum_cycles_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_INTEGER_FORMAT)))
        ins_hbox_layout2.addWidget(ins_maximum_cycles_edit,0)
        ins_data_save_tip_label = QtWidgets.QLabel('data save:',ins_basic_setting_widget,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_data_save_tip_label.setFixedSize(70,30)
        ins_hbox_layout2.addWidget(ins_data_save_tip_label)
        ins_data_save_type_box = QtWidgets.QComboBox(ins_basic_setting_widget)
        ins_data_save_type_box.setObjectName('data-save-type-box')
        ins_data_save_type_box.setFixedSize(60,30)
        ins_data_save_type_box.addItems(['none','last','every'])
        ins_hbox_layout2.addWidget(ins_data_save_type_box)
        ins_data_save_intervals_edit = QtWidgets.QLineEdit(ins_basic_setting_widget)
        ins_data_save_intervals_edit.setObjectName('data-save-intervals-edit')
        ins_data_save_intervals_edit.setFixedSize(60,30)
        ins_data_save_intervals_edit.setMaxLength(5)
        ins_data_save_intervals_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_INTEGER_FORMAT)))
        ins_hbox_layout2.addWidget(ins_data_save_intervals_edit,0)
        ins_hbox_layout2.addStretch()
        
        ins_hbox_layout3 = QtWidgets.QHBoxLayout()
        ins_basic_layout.addLayout(ins_hbox_layout3,0)
        ins_objective_tip_label = QtWidgets.QLabel('objective of whole model:',ins_basic_setting_widget,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_objective_tip_label.setFixedSize(185,30)
        ins_hbox_layout3.addWidget(ins_objective_tip_label)
        ins_target_type_box = QtWidgets.QComboBox(ins_basic_setting_widget)
        ins_target_type_box.setObjectName('target-type-box')
        ins_target_type_box.setFixedSize(120,30)
        ins_target_type_box.addItems(['minimize'])
        ins_hbox_layout3.addWidget(ins_target_type_box,0)
        ins_hbox_layout3.addStretch()
        ins_create_objective_button = QtWidgets.QPushButton('create',ins_basic_setting_widget)
        ins_create_objective_button.setFixedSize(65,30)
        ins_create_objective_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_create_objective_button.clicked.connect(self.__slotCreateObjective)
        ins_hbox_layout3.addWidget(ins_create_objective_button)
        ins_delete_objective_button = QtWidgets.QPushButton('delete',ins_basic_setting_widget)
        ins_delete_objective_button.setFixedSize(65,30)
        ins_delete_objective_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_delete_objective_button.clicked.connect(self.__slotDeleteObjective)
        ins_hbox_layout3.addWidget(ins_delete_objective_button)
        
        ins_objective_table = QtWidgets.QTableWidget(ins_basic_setting_widget)
        ins_objective_table.setObjectName('objective-table')
        ins_objective_table.setColumnCount(3)
        ins_objective_table.horizontalHeader().setFixedHeight(30)
        ins_objective_table.setHorizontalHeaderLabels(['variable','component','operator'])
        ins_objective_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ins_objective_table.horizontalHeader().setSectionsClickable(False)
        ins_objective_table.verticalHeader().setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        ins_objective_table.verticalHeader().setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        ins_basic_layout.addWidget(ins_objective_table,1)
        
        ins_hbox_layout4 = QtWidgets.QHBoxLayout()
        ins_basic_layout.addLayout(ins_hbox_layout4,0)
        ins_constrain_tip_label = QtWidgets.QLabel('whole model subject to:',ins_basic_setting_widget,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_constrain_tip_label.setFixedSize(180,30)
        ins_hbox_layout4.addWidget(ins_constrain_tip_label)
        ins_hbox_layout4.addStretch()
        ins_create_constrain_button = QtWidgets.QPushButton('create',ins_basic_setting_widget)
        ins_create_constrain_button.setFixedSize(65,30)
        ins_create_constrain_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_create_constrain_button.clicked.connect(self.__slotCreateConstrain)
        ins_hbox_layout4.addWidget(ins_create_constrain_button)
        ins_delete_constrain_button = QtWidgets.QPushButton('delete',ins_basic_setting_widget)
        ins_delete_constrain_button.setFixedSize(65,30)
        ins_delete_constrain_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_delete_constrain_button.clicked.connect(self.__slotDeleteConstrain)
        ins_hbox_layout4.addWidget(ins_delete_constrain_button)
        
        ins_constrain_table = QtWidgets.QTableWidget(ins_basic_setting_widget)
        ins_constrain_table.setObjectName('constrain-table')
        ins_constrain_table.setColumnCount(5)
        ins_constrain_table.horizontalHeader().setFixedHeight(30)
        ins_constrain_table.setHorizontalHeaderLabels(['variable','component','operator','constrain','value'])
        ins_constrain_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ins_constrain_table.horizontalHeader().setSectionsClickable(False)
        ins_constrain_table.verticalHeader().setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        ins_constrain_table.verticalHeader().setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        ins_basic_layout.addWidget(ins_constrain_table,1)
    # region
    def __slotChangeFiniteElementModel(self, in_fea_task_full_name:str) -> None:
        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        ins_basic_setting_widget = ins_setting_tab_widget.widget(0)
        
        ins_design_domain_groups_box = ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'design-domain-groups-box')
        ins_design_domain_groups_box.clear()
        
        ins_objective_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'objective-table')
        ins_objective_table.clearContents()
        for row_index in range(ins_objective_table.rowCount()-1,-1,-1):
            ins_objective_table.removeRow(row_index)

        ins_constrain_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'constrain-table')
        ins_constrain_table.clearContents()
        for row_index in range(ins_constrain_table.rowCount()-1,-1,-1):
            ins_constrain_table.removeRow(row_index)

        if os.path.exists(in_fea_task_full_name):
            with h5py.File(in_fea_task_full_name,'r') as ins_fea_task_file:
                self.__model_dimension = str(ins_fea_task_file['basic'][0],'utf-8')
                elements_groups_name_list = list(ins_fea_task_file['Mesh']['Groups']['Elements'].keys())
            
            ins_design_domain_groups_box.addItems(elements_groups_name_list)    
        else:
            QtWidgets.QMessageBox.critical(self,'Create Optimization Task Error',f'The task file "{in_fea_task_full_name}" does not exist!')
            
            ins_finite_element_modes_box = ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'finite-element-models-box')
            ins_finite_element_modes_box.currentTextChanged.disconnect(self.__slotChangeFiniteElementModel)
            ins_finite_element_modes_box.setCurrentIndex(-1)
            ins_finite_element_modes_box.currentTextChanged.connect(self.__slotChangeFiniteElementModel)

    def __slotCreateObjective(self) -> None:
        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        ins_basic_setting_widget = ins_setting_tab_widget.widget(0)
        
        fea_task_full_Name = ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'finite-element-models-box').currentText()
        if fea_task_full_Name == '':
            QtWidgets.QMessageBox.warning(ins_basic_setting_widget,'Create Optimization Task Waring','The finite element analysis task is none!')
            return None
        else:
            pass
        
        ins_objective_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'objective-table')

        current_row_index = ins_objective_table.rowCount()
        ins_objective_table.insertRow(current_row_index)

        ins_variables_box = QtWidgets.QComboBox()
        ins_variables_box.addItems(list(common.P4SOptimizationInfo.OBJECTIVE_VARIABLES[self.__model_dimension].keys()))
        ins_variables_box.setCurrentIndex(-1)
        ins_variables_box.currentTextChanged.connect(self.__slotChangeVariableOfObjective)
        ins_objective_table.setCellWidget(current_row_index,0,ins_variables_box)

        ins_components_box = QtWidgets.QComboBox()
        ins_objective_table.setCellWidget(current_row_index,1,ins_components_box)

        ins_operator_box = QtWidgets.QComboBox()
        ins_operator_box.addItems(['sum'])
        ins_objective_table.setCellWidget(current_row_index,2,ins_operator_box)
    def __slotChangeVariableOfObjective(self, in_variable_type:str) -> None:
        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        ins_basic_setting_widget = ins_setting_tab_widget.widget(0)
        ins_objective_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'objective-table')

        current_row_index = ins_objective_table.currentRow()
        
        ins_components_box = ins_objective_table.cellWidget(current_row_index,1)
        ins_components_box.clear()
        ins_components_box.addItems(common.P4SOptimizationInfo.OBJECTIVE_VARIABLES[self.__model_dimension][in_variable_type])
    
        ins_operator_box = ins_objective_table.cellWidget(current_row_index,2)
        ins_operator_box.clear()
        ins_operator_box.addItems(common.P4SOptimizationInfo.VARIABLES_OPERATORS[in_variable_type])
    def __slotDeleteObjective(self) -> None:
        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        ins_basic_setting_widget = ins_setting_tab_widget.widget(0)
        ins_objective_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'objective-table')

        selected_row_index_list = [ins_row_item.row() for ins_row_item in ins_objective_table.selectionModel().selectedRows()]
        selected_row_index_list = list(set(selected_row_index_list))
        selected_row_index_list.sort()
        selected_row_index_list.reverse()
        for row_index in selected_row_index_list:
            ins_objective_table.removeRow(row_index)

    def __slotCreateConstrain(self) -> None:
        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        ins_basic_setting_widget = ins_setting_tab_widget.widget(0)
        
        fea_task_full_Name = ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'finite-element-models-box').currentText()
        if fea_task_full_Name == '':
            QtWidgets.QMessageBox.warning(ins_basic_setting_widget,'Create Optimization Task Waring','The finite element analysis task is none!')
            return None
        else:
            pass
        
        ins_constrain_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'constrain-table')

        current_row_index = ins_constrain_table.rowCount()
        ins_constrain_table.insertRow(current_row_index)

        ins_variables_box = QtWidgets.QComboBox()
        ins_variables_box.addItems(list(common.P4SOptimizationInfo.CONSTRAIN_VARIABLES[self.__model_dimension].keys()))
        ins_variables_box.setCurrentIndex(-1)
        ins_variables_box.currentTextChanged.connect(self.__slotChangeVariableOfConstrain)
        ins_constrain_table.setCellWidget(current_row_index,0,ins_variables_box)

        ins_components_box = QtWidgets.QComboBox()
        ins_constrain_table.setCellWidget(current_row_index,1,ins_components_box)
        
        ins_operator_box = QtWidgets.QComboBox()
        ins_constrain_table.setCellWidget(current_row_index,2,ins_operator_box)

        ins_constrains_box = QtWidgets.QComboBox()
        ins_constrains_box.addItems(['<='])
        ins_constrain_table.setCellWidget(current_row_index,3,ins_constrains_box)

        ins_value_edit = QtWidgets.QLineEdit()
        ins_value_edit.setMaxLength(10)
        ins_value_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_constrain_table.setCellWidget(current_row_index,4,ins_value_edit)
    def __slotChangeVariableOfConstrain(self, in_variable_type:str) -> None:
        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        ins_basic_setting_widget = ins_setting_tab_widget.widget(0)
        ins_constrain_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'constrain-table')

        current_row_index = ins_constrain_table.currentRow()
        
        ins_components_box = ins_constrain_table.cellWidget(current_row_index,1)
        ins_components_box.clear()
        ins_components_box.addItems(common.P4SOptimizationInfo.CONSTRAIN_VARIABLES[self.__model_dimension][in_variable_type])

        ins_operator_box = ins_constrain_table.cellWidget(current_row_index,2)
        ins_operator_box.clear()
        ins_operator_box.addItems(common.P4SOptimizationInfo.VARIABLES_OPERATORS[in_variable_type])
    def __slotDeleteConstrain(self) -> None:
        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        ins_basic_setting_widget = ins_setting_tab_widget.widget(0)
        ins_constrain_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'constrain-table')

        selected_row_index_list = [ins_row_item.row() for ins_row_item in ins_constrain_table.selectionModel().selectedRows()]
        selected_row_index_list = list(set(selected_row_index_list))
        selected_row_index_list.sort()
        selected_row_index_list.reverse()
        for row_index in selected_row_index_list:
            ins_constrain_table.removeRow(row_index)
    # endregion
    
    def __initializeTopologyOptimizationSettingWidget(self, in_ins_setting_tab_widget:object) -> None:
        ins_topology_optimization_setting_widget = QtWidgets.QWidget(in_ins_setting_tab_widget)
        tab_index = in_ins_setting_tab_widget.addTab(ins_topology_optimization_setting_widget,'topology optimization')
        in_ins_setting_tab_widget.setTabVisible(tab_index,False)
        
        ins_topology_optimization_setting_widget.setContentsMargins(0,0,0,0)
        ins_topology_optimization_layout = QtWidgets.QVBoxLayout()
        ins_topology_optimization_setting_widget.setLayout(ins_topology_optimization_layout)
        ins_topology_optimization_layout.setSpacing(10)
        
        ins_density_tip_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_density_tip_layout)
        ins_density_tip_label = QtWidgets.QLabel('Density:', ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_density_tip_label.setFixedSize(90,20)
        ins_density_tip_layout.addWidget(ins_density_tip_label,0)
        ins_density_tip_layout.addStretch()
        # region
        ins_density_setting_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_density_setting_layout)
        ins_density_setting_layout.addSpacing(20)
        ins_initial_density_label = QtWidgets.QLabel('initial:',ins_topology_optimization_setting_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_initial_density_label.setFixedSize(42,30)
        ins_density_setting_layout.addWidget(ins_initial_density_label,0)
        ins_initial_density_spin_box = QtWidgets.QDoubleSpinBox(ins_topology_optimization_setting_widget)
        ins_initial_density_spin_box.setObjectName('initial-density-spin')
        ins_initial_density_spin_box.setFixedSize(80,30)
        ins_initial_density_spin_box.setSingleStep(0.01)
        ins_initial_density_spin_box.setDecimals(2)
        ins_initial_density_spin_box.setRange(0.01,1.0)
        ins_initial_density_spin_box.setValue(1.0)
        ins_density_setting_layout.addWidget(ins_initial_density_spin_box,0)
        ins_minimum_density_label = QtWidgets.QLabel('min:',ins_topology_optimization_setting_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_minimum_density_label.setFixedSize(32,30)
        ins_density_setting_layout.addWidget(ins_minimum_density_label,0)
        ins_minimum_density_double_spin_box = QtWidgets.QDoubleSpinBox(ins_topology_optimization_setting_widget)
        ins_minimum_density_double_spin_box.setObjectName('minimum-density-spin')
        ins_minimum_density_double_spin_box.setFixedSize(80,30)
        ins_minimum_density_double_spin_box.setSingleStep(0.01)
        ins_minimum_density_double_spin_box.setDecimals(2)
        ins_minimum_density_double_spin_box.setRange(0.01,1.0)
        ins_minimum_density_double_spin_box.setValue(0.01)
        ins_density_setting_layout.addWidget(ins_minimum_density_double_spin_box,0)
        ins_maximum_density_label = QtWidgets.QLabel('max:',ins_topology_optimization_setting_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_maximum_density_label.setFixedSize(34,30)
        ins_density_setting_layout.addWidget(ins_maximum_density_label,0)
        ins_maximum_density_double_spin_box = QtWidgets.QDoubleSpinBox(ins_topology_optimization_setting_widget)
        ins_maximum_density_double_spin_box.setObjectName('maximum-density-spin')
        ins_maximum_density_double_spin_box.setFixedSize(80,30)
        ins_maximum_density_double_spin_box.setSingleStep(0.01)
        ins_maximum_density_double_spin_box.setDecimals(2)
        ins_maximum_density_double_spin_box.setRange(0.01,1.0)
        ins_maximum_density_double_spin_box.setValue(1.0)
        ins_density_setting_layout.addWidget(ins_maximum_density_double_spin_box,0)
        ins_maximum_density_change_label = QtWidgets.QLabel("limitation of cycle:",ins_topology_optimization_setting_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_maximum_density_change_label.setFixedSize(128,30)
        ins_density_setting_layout.addWidget(ins_maximum_density_change_label,0)
        ins_maximum_density_change_double_spin_box = QtWidgets.QDoubleSpinBox(ins_topology_optimization_setting_widget)
        ins_maximum_density_change_double_spin_box.setObjectName('limitation-per-cycle-spin')
        ins_maximum_density_change_double_spin_box.setFixedSize(80,30)
        ins_maximum_density_change_double_spin_box.setSingleStep(0.01)
        ins_maximum_density_change_double_spin_box.setDecimals(2)
        ins_maximum_density_change_double_spin_box.setRange(0.01,1.0)
        ins_maximum_density_change_double_spin_box.setValue(0.2)
        ins_density_setting_layout.addWidget(ins_maximum_density_change_double_spin_box,0)
        ins_density_setting_layout.addStretch()
        # endregion

        ins_convergence_tip_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_convergence_tip_layout)
        ins_convergence_tip_Label = QtWidgets.QLabel('Convergence:', ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_convergence_tip_Label.setFixedSize(120,20)
        ins_convergence_tip_layout.addWidget(ins_convergence_tip_Label,0)
        ins_convergence_tip_layout.addStretch()
        # region
        ins_convergence_setting1_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_convergence_setting1_layout)
        ins_convergence_setting1_layout.addSpacing(20)
        ins_onvergence_criterion_label = QtWidgets.QLabel('criterion:',ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_onvergence_criterion_label.setFixedSize(62,30)
        ins_convergence_setting1_layout.addWidget(ins_onvergence_criterion_label,0)
        ins_convergence_criterion_box = QtWidgets.QComboBox(ins_topology_optimization_setting_widget)
        ins_convergence_criterion_box.setObjectName('criterion-type-box')
        ins_convergence_criterion_box.setFixedSize(100,30)
        ins_convergence_criterion_box.addItems(['density','objective','either','both'])
        ins_convergence_setting1_layout.addWidget(ins_convergence_criterion_box,0)
        ins_density_criterion_label = QtWidgets.QLabel('max |Δx|:',ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_density_criterion_label.setFixedSize(70,30)
        ins_convergence_setting1_layout.addWidget(ins_density_criterion_label,0)
        ins_density_criterion_spin_box = QtWidgets.QDoubleSpinBox(ins_topology_optimization_setting_widget)
        ins_density_criterion_spin_box.setObjectName('density-criterion-spin')
        ins_density_criterion_spin_box.setFixedSize(105,30)
        ins_density_criterion_spin_box.setSingleStep(0.00001)
        ins_density_criterion_spin_box.setDecimals(5)
        ins_density_criterion_spin_box.setRange(0.00001,0.5)
        ins_density_criterion_spin_box.setValue(0.05)
        ins_convergence_setting1_layout.addWidget(ins_density_criterion_spin_box,0)
        ins_objective_criterion_label = QtWidgets.QLabel('max |Δ(obj/obj0)|:',ins_topology_optimization_setting_widget)
        ins_objective_criterion_label.setFixedSize(135,30)
        ins_convergence_setting1_layout.addWidget(ins_objective_criterion_label,0)
        ins_objective_criterion_spin_box = QtWidgets.QDoubleSpinBox(ins_topology_optimization_setting_widget)
        ins_objective_criterion_spin_box.setObjectName('objective-criterion-spin')
        ins_objective_criterion_spin_box.setFixedSize(80,30)
        ins_objective_criterion_spin_box.setSingleStep(0.01)
        ins_objective_criterion_spin_box.setDecimals(2)
        ins_objective_criterion_spin_box.setRange(0.01,0.5)
        ins_objective_criterion_spin_box.setValue(0.01)
        ins_convergence_setting1_layout.addWidget(ins_objective_criterion_spin_box,0)
        ins_convergence_setting1_layout.addStretch()

        ins_convergence_setting2_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_convergence_setting2_layout)
        ins_convergence_setting2_layout.addSpacing(20)
        ins_convergence_numbe_label = QtWidgets.QLabel('number of continuous convergence:',ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_convergence_numbe_label.setFixedSize(255,30)
        ins_convergence_setting2_layout.addWidget(ins_convergence_numbe_label,0)
        ins_convergence_number_spin_box = QtWidgets.QSpinBox(ins_topology_optimization_setting_widget)
        ins_convergence_number_spin_box.setObjectName('convergence-number-spin')
        ins_convergence_number_spin_box.setFixedSize(65,30)
        ins_convergence_number_spin_box.setRange(2,10)
        ins_convergence_number_spin_box.setValue(3)
        ins_convergence_setting2_layout.addWidget(ins_convergence_number_spin_box,0)
        ins_convergence_setting2_layout.addStretch()
        # endregion

        ins_algorithm_tip_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_algorithm_tip_layout)
        ins_algorithm_tip_Label = QtWidgets.QLabel('Algorithm:', ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_algorithm_tip_Label.setFixedSize(120,20)
        ins_algorithm_tip_layout.addWidget(ins_algorithm_tip_Label,0)
        ins_algorithm_tip_layout.addStretch()
        # region
        ins_algorithm_setting_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_algorithm_setting_layout)
        ins_algorithm_setting_layout.addSpacing(20)
        ins_interpolation_model_label = QtWidgets.QLabel("interpolation model:",ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_interpolation_model_label.setFixedSize(143,30)
        ins_algorithm_setting_layout.addWidget(ins_interpolation_model_label,0)
        ins_interpolation_models_box = QtWidgets.QComboBox(ins_topology_optimization_setting_widget)
        ins_interpolation_models_box.setObjectName('interpolation-models-box')
        ins_interpolation_models_box.setFixedSize(70,30)
        ins_interpolation_models_box.addItems(['SIMP','RAMP'])
        ins_algorithm_setting_layout.addWidget(ins_interpolation_models_box,0)
        ins_penalty_factor_label = QtWidgets.QLabel('penalty factor:',ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_penalty_factor_label.setFixedSize(100,30)
        ins_algorithm_setting_layout.addWidget(ins_penalty_factor_label,0)
        ins_penalty_factor_spin_box = QtWidgets.QDoubleSpinBox(ins_topology_optimization_setting_widget)
        ins_penalty_factor_spin_box.setObjectName('penalty-factor-spin')
        ins_penalty_factor_spin_box.setFixedSize(70,30)
        ins_penalty_factor_spin_box.setSingleStep(0.1)
        ins_penalty_factor_spin_box.setDecimals(1)
        ins_penalty_factor_spin_box.setRange(1.0,10.0)
        ins_penalty_factor_spin_box.setValue(3.0)
        ins_algorithm_setting_layout.addWidget(ins_penalty_factor_spin_box,0)
        ins_optimizer_label = QtWidgets.QLabel('optimizer:',ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_optimizer_label.setFixedSize(70,30)
        ins_algorithm_setting_layout.addWidget(ins_optimizer_label,0)
        ins_optimizer_type_box = QtWidgets.QComboBox(ins_topology_optimization_setting_widget)
        ins_optimizer_type_box.setObjectName('optimizer-type-box')
        ins_optimizer_type_box.setFixedSize(95,30)
        ins_optimizer_type_box.addItems(['MMA','GCMMA','ADAM'])
        ins_algorithm_setting_layout.addWidget(ins_optimizer_type_box,0)
        ins_algorithm_setting_layout.addStretch()
        # endregion

        ins_filter_tip_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_filter_tip_layout)
        ins_filter_tip_Label = QtWidgets.QLabel('Filter:', ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_filter_tip_Label.setFixedSize(100,20)
        ins_filter_tip_layout.addWidget(ins_filter_tip_Label,0)
        ins_filter_tip_layout.addStretch()
        # region
        ins_filter_setting1_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_filter_setting1_layout)
        ins_filter_setting1_layout.addSpacing(20)
        ins_filter_type_label = QtWidgets.QLabel('type:',ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_filter_type_label.setFixedSize(34,30)
        ins_filter_setting1_layout.addWidget(ins_filter_type_label,0)
        ins_filter_type_box = QtWidgets.QComboBox(ins_topology_optimization_setting_widget)
        ins_filter_type_box.setObjectName('filter-type-box')
        ins_filter_type_box.setFixedSize(110,30)
        ins_filter_type_box.addItems(['sensitivity','density'])
        ins_filter_setting1_layout.addWidget(ins_filter_type_box,0)
        ins_calculator_label = QtWidgets.QLabel('calculator:',ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_calculator_label.setFixedSize(73,30)
        ins_filter_setting1_layout.addWidget(ins_calculator_label,0)
        ins_calculator_box = QtWidgets.QComboBox(ins_topology_optimization_setting_widget)
        ins_calculator_box.setObjectName('calculator-box')
        ins_calculator_box.setFixedSize(95,30)
        ins_calculator_box.addItems(['common','file'])
        ins_filter_setting1_layout.addWidget(ins_calculator_box,0)
        ins_filter_radius_label = QtWidgets.QLabel('radius:',ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_filter_radius_label.setFixedSize(48,30)
        ins_filter_setting1_layout.addWidget(ins_filter_radius_label,0)
        ins_filter_radius_double_spin = QtWidgets.QDoubleSpinBox(ins_topology_optimization_setting_widget)
        ins_filter_radius_double_spin.setObjectName('filter-radius-spin')
        ins_filter_radius_double_spin.setFixedSize(90,30)
        ins_filter_radius_double_spin.setSingleStep(1.0)
        ins_filter_radius_double_spin.setDecimals(3)
        ins_filter_radius_double_spin.setRange(0.0,9999.0)
        ins_filter_setting1_layout.addWidget(ins_filter_radius_double_spin,0)
        ins_filter_setting1_layout.addStretch()
        
        ins_filter_setting2_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_filter_setting2_layout)
        ins_filter_setting2_layout.addSpacing(20)
        ins_filter_include_nondesign_domain_label = QtWidgets.QLabel('include non-design domain:',ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_filter_include_nondesign_domain_label.setFixedSize(197,30)
        ins_filter_setting2_layout.addWidget(ins_filter_include_nondesign_domain_label,0)
        ins_filter_include_nondesign_domain_box = QtWidgets.QComboBox(ins_topology_optimization_setting_widget)
        ins_filter_include_nondesign_domain_box.setObjectName('filter-include-nondesign-box')
        ins_filter_include_nondesign_domain_box.setFixedSize(60,30)
        ins_filter_include_nondesign_domain_box.addItems(['No','Yes'])
        ins_filter_setting2_layout.addWidget(ins_filter_include_nondesign_domain_box,0)
        ins_filter_setting2_layout.addStretch()
        # endregion

        ins_binaryzation_tip_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_binaryzation_tip_layout)
        ins_binaryzation_tip_Label = QtWidgets.QLabel('Binaryzation:', ins_topology_optimization_setting_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_binaryzation_tip_Label.setFixedSize(140,20)
        ins_binaryzation_tip_layout.addWidget(ins_binaryzation_tip_Label,0)
        ins_binaryzation_tip_layout.addStretch()
        # region
        ins_binaryzation_setting_layout = QtWidgets.QHBoxLayout()
        ins_topology_optimization_layout.addLayout(ins_binaryzation_setting_layout)
        ins_binaryzation_setting_layout.addSpacing(20)
        ins_scheme_label = QtWidgets.QLabel('scheme:',ins_topology_optimization_setting_widget)
        ins_scheme_label.setFixedSize(60,30)
        ins_binaryzation_setting_layout.addWidget(ins_scheme_label,0)
        ins_binaryzation_scheme_box = QtWidgets.QComboBox(ins_topology_optimization_setting_widget)
        ins_binaryzation_scheme_box.setObjectName('binaryzation-shceme-box')
        ins_binaryzation_scheme_box.setFixedSize(170,30)
        ins_binaryzation_scheme_box.addItems(['none','density threshold','volume constraint','projection'])
        ins_binaryzation_setting_layout.addWidget(ins_binaryzation_scheme_box,0)
        ins_binaryzation_param1_label = QtWidgets.QLabel(ins_topology_optimization_setting_widget,text='xt:',alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_binaryzation_param1_label.setFixedSize(17,30)
        ins_binaryzation_setting_layout.addWidget(ins_binaryzation_param1_label,0)
        ins_binaryzation_param1_double_spin_box = QtWidgets.QDoubleSpinBox(ins_topology_optimization_setting_widget)
        ins_binaryzation_param1_double_spin_box.setObjectName('binaryzation-param1-spin')
        ins_binaryzation_param1_double_spin_box.setFixedSize(80,30)
        ins_binaryzation_param1_double_spin_box.setSingleStep(0.01)
        ins_binaryzation_param1_double_spin_box.setDecimals(2)
        ins_binaryzation_param1_double_spin_box.setRange(0.0,1.0)
        ins_binaryzation_param1_double_spin_box.setValue(0.5)
        ins_binaryzation_setting_layout.addWidget(ins_binaryzation_param1_double_spin_box,0)
        ins_binaryzation_param2_label = QtWidgets.QLabel(ins_topology_optimization_setting_widget,text='update interval(β):',alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_binaryzation_param2_label.setFixedSize(130,30)
        ins_binaryzation_setting_layout.addWidget(ins_binaryzation_param2_label,0)
        ins_binaryzation_param2_spin_box = QtWidgets.QSpinBox(ins_topology_optimization_setting_widget)
        ins_binaryzation_param2_spin_box.setObjectName('binaryzation-param2-spin')
        ins_binaryzation_param2_spin_box.setFixedSize(80,30)
        ins_binaryzation_param2_spin_box.setSingleStep(1)
        ins_binaryzation_param2_spin_box.setRange(1,999)
        ins_binaryzation_param2_spin_box.setValue(5)
        ins_binaryzation_setting_layout.addWidget(ins_binaryzation_param2_spin_box,0)
        ins_binaryzation_setting_layout.addStretch()
        # endregion

        ins_topology_optimization_layout.addStretch()
    
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
    
    def getOptimizationInformation(self) -> dict:
        optimization_information_dict = {}
        optimization_information_dict['name'] = self.findChild(QtWidgets.QLineEdit,'task-name-edit').text()
        optimization_information_dict['type'] = self.findChild(QtWidgets.QComboBox,'optimization-type-box').currentText()

        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        
        optimization_information_dict['basic'] = []
        ins_basic_setting_widget = ins_setting_tab_widget.widget(0)
        # region
        optimization_information_dict['basic'].append(ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'finite-element-models-box').currentText())
        optimization_information_dict['basic'].append(ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'design-domain-groups-box').currentText())
        optimization_information_dict['basic'].append(ins_basic_setting_widget.findChild(QtWidgets.QLineEdit,'maximum-cycles-edit').text())
        optimization_information_dict['basic'].append(ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'data-save-type-box').currentText())
        optimization_information_dict['basic'].append(ins_basic_setting_widget.findChild(QtWidgets.QLineEdit,'data-save-intervals-edit').text())
        optimization_information_dict['basic'].append(ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'target-type-box').currentText())
        
        optimization_information_dict['basic'].append([])
        ins_objective_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'objective-table')
        for row_index in range(ins_objective_table.rowCount()):
            objective_variable_name = ins_objective_table.cellWidget(row_index,0).currentText()
            objective_component_name = ins_objective_table.cellWidget(row_index,1).currentText()
            objective_operator_name = ins_objective_table.cellWidget(row_index,2).currentText()
            
            optimization_information_dict['basic'][6].append([objective_variable_name,objective_component_name,objective_operator_name])
            
        optimization_information_dict['basic'].append([])
        ins_constrain_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'constrain-table')
        for row_index in range(ins_constrain_table.rowCount()):
            constrain_variable_name = ins_constrain_table.cellWidget(row_index,0).currentText()
            constrain_component_name = ins_constrain_table.cellWidget(row_index,1).currentText()
            constrain_operator_name = ins_constrain_table.cellWidget(row_index,2).currentText()
            constrain_type_name = ins_constrain_table.cellWidget(row_index,3).currentText()
            constrain_value_string = ins_constrain_table.cellWidget(row_index,4).text()
            
            if constrain_value_string == '':
                constrain_value_string = '0.0'
            else:
                pass
            
            optimization_information_dict['basic'][7].append([constrain_variable_name,constrain_component_name,constrain_operator_name,constrain_type_name,constrain_value_string])
        # endregion

        if optimization_information_dict['type'] == 'topology optimization':
            ins_topology_optimization_setting_widget = ins_setting_tab_widget.widget(1)

            optimization_information_dict['optimization'] = {}

            optimization_information_dict['optimization']['Density'] = []
            optimization_information_dict['optimization']['Density'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'initial-density-spin').value())
            optimization_information_dict['optimization']['Density'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'minimum-density-spin').value())
            optimization_information_dict['optimization']['Density'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'maximum-density-spin').value())
            optimization_information_dict['optimization']['Density'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'limitation-per-cycle-spin').value())

            optimization_information_dict['optimization']['Convergence'] = []
            optimization_information_dict['optimization']['Convergence'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'criterion-type-box').currentText())
            optimization_information_dict['optimization']['Convergence'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'density-criterion-spin').value())
            optimization_information_dict['optimization']['Convergence'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'objective-criterion-spin').value())         
            optimization_information_dict['optimization']['Convergence'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QSpinBox,'convergence-number-spin').value())         
            
            optimization_information_dict['optimization']['Algorithm'] = []
            optimization_information_dict['optimization']['Algorithm'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'interpolation-models-box').currentText())
            optimization_information_dict['optimization']['Algorithm'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'penalty-factor-spin').value())
            optimization_information_dict['optimization']['Algorithm'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'optimizer-type-box').currentText())

            optimization_information_dict['optimization']['Filter'] = []
            optimization_information_dict['optimization']['Filter'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'filter-type-box').currentText())
            optimization_information_dict['optimization']['Filter'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'calculator-box').currentText())
            optimization_information_dict['optimization']['Filter'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'filter-radius-spin').value())
            optimization_information_dict['optimization']['Filter'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'filter-include-nondesign-box').currentText())

            optimization_information_dict['optimization']['Binaryzation'] = []
            optimization_information_dict['optimization']['Binaryzation'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'binaryzation-shceme-box').currentText())
            optimization_information_dict['optimization']['Binaryzation'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'binaryzation-param1-spin').value())
            optimization_information_dict['optimization']['Binaryzation'].append(ins_topology_optimization_setting_widget.findChild(QtWidgets.QSpinBox,'binaryzation-param2-spin').value())            
        else:
            pass
        
        return optimization_information_dict
    def setOptimizationInformation(self, in_optimization_information:dict) -> None:
        ins_name_edit = self.findChild(QtWidgets.QLineEdit,'task-name-edit')
        ins_name_edit.setText(in_optimization_information['name'])
        ins_name_edit.setEnabled(False)
        
        ins_optimization_type_box = self.findChild(QtWidgets.QComboBox,'optimization-type-box')
        ins_optimization_type_box.setCurrentText(in_optimization_information['type'])
        ins_optimization_type_box.setEnabled(False)

        ins_setting_tab_widget = self.findChild(QtWidgets.QTabWidget,'optimization-setting-tabs')
        ins_basic_setting_widget = ins_setting_tab_widget.widget(0)
        ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'finite-element-models-box').setCurrentText(in_optimization_information['basic'][0])
        if in_optimization_information['basic'][0] == '':
            pass
        else:
            with h5py.File(in_optimization_information['basic'][0],'r') as ins_fea_task_file:
                self.__model_dimension = str(ins_fea_task_file['basic'][0],'utf-8')
            ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'design-domain-groups-box').setCurrentText(in_optimization_information['basic'][1])
        ins_basic_setting_widget.findChild(QtWidgets.QLineEdit,'maximum-cycles-edit').setText(in_optimization_information['basic'][2])
        ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'data-save-type-box').setCurrentText(in_optimization_information['basic'][3])
        ins_basic_setting_widget.findChild(QtWidgets.QLineEdit,'data-save-intervals-edit').setText(in_optimization_information['basic'][4])
        ins_basic_setting_widget.findChild(QtWidgets.QComboBox,'target-type-box').setCurrentText(in_optimization_information['basic'][5])
        ins_objective_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'objective-table')
        for row_index,objective_parameters_list in enumerate(in_optimization_information['basic'][6]):
            ins_objective_table.insertRow(row_index)
            
            ins_variables_box = QtWidgets.QComboBox()
            ins_variables_box.addItems(list(common.P4SOptimizationInfo.OBJECTIVE_VARIABLES[self.__model_dimension].keys()))
            ins_variables_box.setCurrentIndex(-1)
            ins_variables_box.currentTextChanged.connect(self.__slotChangeVariableOfObjective)
            ins_objective_table.setCellWidget(row_index,0,ins_variables_box)

            ins_components_box = QtWidgets.QComboBox()
            ins_objective_table.setCellWidget(row_index,1,ins_components_box)

            ins_operator_box = QtWidgets.QComboBox()
            ins_operator_box.addItems(['sum'])
            ins_objective_table.setCellWidget(row_index,2,ins_operator_box)
            
            ins_objective_table.selectRow(row_index)
            ins_variables_box.setCurrentText(objective_parameters_list[0])
            ins_components_box.setCurrentText(objective_parameters_list[1])
            ins_operator_box.setCurrentText(objective_parameters_list[2])
        ins_objective_table.clearSelection()
        ins_constrain_table = ins_basic_setting_widget.findChild(QtWidgets.QTableWidget,'constrain-table')
        for row_index,constrain_parameters_list in enumerate(in_optimization_information['basic'][7]):
            ins_constrain_table.insertRow(row_index)
            
            ins_variables_box = QtWidgets.QComboBox()
            ins_variables_box.addItems(list(common.P4SOptimizationInfo.CONSTRAIN_VARIABLES[self.__model_dimension].keys()))
            ins_variables_box.setCurrentIndex(-1)
            ins_variables_box.currentTextChanged.connect(self.__slotChangeVariableOfConstrain)
            ins_constrain_table.setCellWidget(row_index,0,ins_variables_box)

            ins_components_box = QtWidgets.QComboBox()
            ins_constrain_table.setCellWidget(row_index,1,ins_components_box)

            ins_operator_box = QtWidgets.QComboBox()
            ins_operator_box.addItems(['sum'])
            ins_constrain_table.setCellWidget(row_index,2,ins_operator_box)

            ins_constrains_box = QtWidgets.QComboBox()
            ins_constrains_box.addItems(['<='])
            ins_constrain_table.setCellWidget(row_index,3,ins_constrains_box)

            ins_value_edit = QtWidgets.QLineEdit()
            ins_value_edit.setMaxLength(10)
            ins_value_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
            ins_constrain_table.setCellWidget(row_index,4,ins_value_edit)
            
            ins_constrain_table.selectRow(row_index)
            ins_variables_box.setCurrentText(constrain_parameters_list[0])
            ins_components_box.setCurrentText(constrain_parameters_list[1])
            ins_operator_box.setCurrentText(constrain_parameters_list[2])
            ins_constrains_box.setCurrentText(constrain_parameters_list[3])
            ins_value_edit.setText(constrain_parameters_list[4])
        ins_constrain_table.clearSelection()
        
        if in_optimization_information['type'] == 'topology optimization':
            ins_topology_optimization_setting_widget = ins_setting_tab_widget.widget(1)
            
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'initial-density-spin').setValue(in_optimization_information['optimization']['Density'][0])
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'minimum-density-spin').setValue(in_optimization_information['optimization']['Density'][1])
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'maximum-density-spin').setValue(in_optimization_information['optimization']['Density'][2])
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'limitation-per-cycle-spin').setValue(in_optimization_information['optimization']['Density'][3])
            
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'criterion-type-box').setCurrentText(in_optimization_information['optimization']['Convergence'][0])
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'density-criterion-spin').setValue(float(in_optimization_information['optimization']['Convergence'][1]))
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'objective-criterion-spin').setValue(float(in_optimization_information['optimization']['Convergence'][2]))         
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QSpinBox,'convergence-number-spin').setValue(int(in_optimization_information['optimization']['Convergence'][3]))        
            
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'interpolation-models-box').setCurrentText(in_optimization_information['optimization']['Algorithm'][0])
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'penalty-factor-spin').setValue(float(in_optimization_information['optimization']['Algorithm'][1]))
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'optimizer-type-box').setCurrentText(in_optimization_information['optimization']['Algorithm'][2])

            ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'filter-type-box').setCurrentText(in_optimization_information['optimization']['Filter'][0])
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'calculator-box').setCurrentText(in_optimization_information['optimization']['Filter'][1])
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'filter-radius-spin').setValue(float(in_optimization_information['optimization']['Filter'][2]))
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'filter-include-nondesign-box').setCurrentText(in_optimization_information['optimization']['Filter'][3])
            
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QComboBox,'binaryzation-shceme-box').setCurrentText(in_optimization_information['optimization']['Binaryzation'][0])
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QDoubleSpinBox,'binaryzation-param1-spin').setValue(float(in_optimization_information['optimization']['Binaryzation'][1]))
            ins_topology_optimization_setting_widget.findChild(QtWidgets.QSpinBox,'binaryzation-param2-spin').setValue(int(in_optimization_information['optimization']['Binaryzation'][2]))
        else:
            pass
# endregion

class P4SVisualizationToolbar(QtCore.QObject):

    def __init__(self, in_parent:object) -> None:
        super().__init__(parent=in_parent,objectName='visualization-toolbar')

        self.__initializeSelectionTools(in_parent)
        self.__initializeViewsTools(in_parent)
        self.__initializeRenderTools(in_parent)
        self.__initializeOptimizationTools(in_parent)
    
    def __initializeSelectionTools(self, in_parent:object) -> None:
        ins_selection_tools = QtWidgets.QToolBar(in_parent,allowedAreas=QtCore.Qt.RightToolBarArea,iconSize=QtCore.QSize(28,28))
        ins_selection_tools.setObjectName('selection-toolbar')
        ins_selection_tools.setMaximumHeight(220)
        in_parent.addToolBar(QtCore.Qt.RightToolBarArea,ins_selection_tools)
        
        ins_select_node_tool = ins_selection_tools.addAction(QtGui.QIcon(':/image/images/ToolSelectNode.png'),'','N')
        ins_select_node_tool.setToolTip('select node(N)')
        ins_select_node_tool.setCheckable(True)
        ins_select_node_tool.triggered.connect(self.__slotSetNodeSelectionMode)
        
        ins_select_element_tool = ins_selection_tools.addAction(QtGui.QIcon(':/image/images/ToolSelectElement.png'),'','E')
        ins_select_element_tool.setToolTip('select element(E)')
        ins_select_element_tool.setCheckable(True)
        ins_select_element_tool.triggered.connect(self.__slotSetElementSelectionMode)
        
        ins_selection_from_area_tool = ins_selection_tools.addAction(QtGui.QIcon(':/image/images/ToolSelectionFromArea.png'),'')
        ins_selection_from_area_tool.setToolTip('from area')
        ins_selection_from_area_tool.setCheckable(True)
        ins_selection_from_area_tool.setEnabled(False)
        ins_selection_from_area_tool.triggered.connect(self.__slotSetAreaSelectionMethod)
        
        ins_selection_from_edge_tool = ins_selection_tools.addAction(QtGui.QIcon(':/image/images/ToolSelectionFromEdge.png'),'')
        ins_selection_from_edge_tool.setToolTip('from edge')
        ins_selection_from_edge_tool.setCheckable(True)
        ins_selection_from_edge_tool.setEnabled(False)
        ins_selection_from_edge_tool.triggered.connect(self.__slotSetEdgeSelectionMethod)
        
        ins_selection_from_face_tool = ins_selection_tools.addAction(QtGui.QIcon(':/image/images/ToolSelectionFromFace.png'),'')
        ins_selection_from_face_tool.setToolTip('from face')
        ins_selection_from_face_tool.setCheckable(True)
        ins_selection_from_face_tool.setEnabled(False)
        ins_selection_from_face_tool.triggered.connect(self.__slotSetFaceSelectionMethod)

        ins_selection_from_entity_tool = ins_selection_tools.addAction(QtGui.QIcon(':/image/images/ToolSelectionFromEntity.png'),'')
        ins_selection_from_entity_tool.setToolTip('from entity')
        ins_selection_from_entity_tool.setCheckable(True)
        ins_selection_from_entity_tool.setEnabled(False)
        ins_selection_from_entity_tool.triggered.connect(self.__slotSetEntitySelectionMethod)
    # region
    def __slotSetNodeSelectionMode(self, in_state:bool) -> None:
        ins_main_window = self.parent()
        
        current_manager_index = ins_main_window.centralWidget().currentIndex()
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
                ins_select_node_tool = ins_selection_toolbar.actions()[0]
                ins_select_node_tool.triggered.disconnect(self.__slotSetNodeSelectionMode)
                ins_select_node_tool.setChecked(False)
                ins_select_node_tool.triggered.connect(self.__slotSetNodeSelectionMode)
                
                QtWidgets.QMessageBox.warning(ins_selection_toolbar,'Set Selection Mode Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass 
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
            ins_select_node_tool = ins_selection_toolbar.actions()[0]
            ins_select_node_tool.triggered.disconnect(self.__slotSetNodeSelectionMode)
            ins_select_node_tool.setChecked(False)
            ins_select_node_tool.triggered.connect(self.__slotSetNodeSelectionMode)
            
            QtWidgets.QMessageBox.warning(ins_selection_toolbar,'Set Selection Mode Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
                ins_select_node_tool = ins_selection_toolbar.actions()[0]
                ins_select_node_tool.triggered.disconnect(self.__slotSetNodeSelectionMode)
                ins_select_node_tool.setChecked(False)
                ins_select_node_tool.triggered.connect(self.__slotSetNodeSelectionMode)
                
                QtWidgets.QMessageBox.warning(ins_selection_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
        if in_state:
            ins_select_element_tool = ins_selection_toolbar.actions()[1]
            ins_select_element_tool.triggered.disconnect(self.__slotSetElementSelectionMode)
            if ins_select_element_tool.isChecked():
                ins_select_element_tool.setChecked(False)
            else:
                for ins_selection_method in ins_selection_toolbar.actions()[2:]:
                    ins_selection_method.setEnabled(True)
            ins_select_element_tool.triggered.connect(self.__slotSetElementSelectionMode) 
            
            ins_visual_window.setSelectionMode('node')
        else:
            for ins_selection_method in ins_selection_toolbar.actions()[2:]:
                ins_selection_method.setChecked(False)
                ins_selection_method.setEnabled(False)
            
            ins_visual_window.setSelectionMode(None)
    def __slotSetElementSelectionMode(self, in_state:bool) -> None:
        ins_main_window = self.parent()
        
        current_manager_index = ins_main_window.centralWidget().currentIndex()
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
                ins_select_element_tool = ins_selection_toolbar.actions()[1]
                ins_select_element_tool.triggered.disconnect(self.__slotSetElementSelectionMode)
                ins_select_element_tool.setChecked(False)
                ins_select_element_tool.triggered.connect(self.__slotSetElementSelectionMode)
                
                QtWidgets.QMessageBox.warning(ins_selection_toolbar,'Set Selection Mode Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass 
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
            ins_select_element_tool = ins_selection_toolbar.actions()[1]
            ins_select_element_tool.triggered.disconnect(self.__slotSetElementSelectionMode)
            ins_select_element_tool.setChecked(False)
            ins_select_element_tool.triggered.connect(self.__slotSetElementSelectionMode)
            
            QtWidgets.QMessageBox.warning(ins_selection_toolbar,'Set Selection Mode Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
                ins_select_element_tool = ins_selection_toolbar.actions()[1]
                ins_select_element_tool.triggered.disconnect(self.__slotSetElementSelectionMode)
                ins_select_element_tool.setChecked(False)
                ins_select_element_tool.triggered.connect(self.__slotSetElementSelectionMode)
                
                QtWidgets.QMessageBox.warning(ins_selection_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass
        
        ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
        if in_state:
            ins_select_node_tool = ins_selection_toolbar.actions()[0]
            ins_select_node_tool.triggered.disconnect(self.__slotSetNodeSelectionMode)
            if ins_select_node_tool.isChecked():
                ins_select_node_tool.setChecked(False)
            else:
                for ins_selection_method in ins_selection_toolbar.actions()[2:]:
                    ins_selection_method.setEnabled(True)
            ins_select_node_tool.triggered.connect(self.__slotSetNodeSelectionMode)
            
            ins_visual_window.setSelectionMode('element')
        else:
            for ins_selection_method in ins_selection_toolbar.actions()[2:]:
                ins_selection_method.setChecked(False)
                ins_selection_method.setEnabled(False)
        
            ins_visual_window.setSelectionMode(None)
    def __slotSetAreaSelectionMethod(self, in_state:bool) -> None:
        ins_main_window = self.parent()
        ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        
        if in_state:
            for ins_select_tool in ins_selection_toolbar.actions()[2:]:
                if ins_select_tool.isChecked():
                    if ins_select_tool.toolTip() == 'from edge':
                        ins_select_tool.triggered.disconnect(self.__slotSetEdgeSelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetEdgeSelectionMethod)
                    elif ins_select_tool.toolTip() == 'from face':
                        ins_select_tool.triggered.disconnect(self.__slotSetFaceSelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetFaceSelectionMethod)
                    elif ins_select_tool.toolTip() == 'from entity':
                        ins_select_tool.triggered.disconnect(self.__slotSetEntitySelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetEntitySelectionMethod)
                    else:
                        pass
                else:
                    continue
        
            ins_visual_window.setSelectionMethod('area')
        else:
            ins_visual_window.setSelectionMethod('single')    
    def __slotSetEdgeSelectionMethod(self, in_state:bool) -> None:
        ins_main_window = self.parent()
        ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        
        if in_state:
            for ins_select_tool in ins_selection_toolbar.actions()[2:]:
                if ins_select_tool.isChecked():
                    if ins_select_tool.toolTip() == 'from area':
                        ins_select_tool.triggered.disconnect(self.__slotSetAreaSelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetAreaSelectionMethod)
                    elif ins_select_tool.toolTip() == 'from face':
                        ins_select_tool.triggered.disconnect(self.__slotSetFaceSelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetFaceSelectionMethod)
                    elif ins_select_tool.toolTip() == 'from entity':
                        ins_select_tool.triggered.disconnect(self.__slotSetEntitySelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetEntitySelectionMethod)
                    else:
                        pass
                else:
                    continue
        
            ins_visual_window.setSelectionMethod('edge')
        else:
            ins_visual_window.setSelectionMethod('single')
    def __slotSetFaceSelectionMethod(self, in_state:bool) -> None:
        ins_main_window = self.parent()
        ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        
        if in_state:
            for ins_select_tool in ins_selection_toolbar.actions()[2:]:
                if ins_select_tool.isChecked():
                    if ins_select_tool.toolTip() == 'from edge':
                        ins_select_tool.triggered.disconnect(self.__slotSetEdgeSelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetEdgeSelectionMethod)
                    elif ins_select_tool.toolTip() == 'from area':
                        ins_select_tool.triggered.disconnect(self.__slotSetAreaSelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetAreaSelectionMethod)
                    elif ins_select_tool.toolTip() == 'from entity':
                        ins_select_tool.triggered.disconnect(self.__slotSetEntitySelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetEntitySelectionMethod)
                    else:
                        pass
                else:
                    continue
        
            ins_visual_window.setSelectionMethod('face')
        else:
            ins_visual_window.setSelectionMethod('single')
    def __slotSetEntitySelectionMethod(self, in_state:bool) -> None:
        ins_main_window = self.parent()
        ins_selection_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        
        if in_state:
            for ins_select_tool in ins_selection_toolbar.actions()[2:]:
                if ins_select_tool.isChecked():
                    if ins_select_tool.toolTip() == 'from edge':
                        ins_select_tool.triggered.disconnect(self.__slotSetEdgeSelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetEdgeSelectionMethod)
                    elif ins_select_tool.toolTip() == 'from face':
                        ins_select_tool.triggered.disconnect(self.__slotSetFaceSelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetFaceSelectionMethod)
                    elif ins_select_tool.toolTip() == 'from area':
                        ins_select_tool.triggered.disconnect(self.__slotSetAreaSelectionMethod)
                        ins_select_tool.setChecked(False)
                        ins_select_tool.triggered.connect(self.__slotSetAreaSelectionMethod)
                    else:
                        pass
                else:
                    continue
        
            ins_visual_window.setSelectionMethod('entity')
        else:
            ins_visual_window.setSelectionMethod('single')
    # endregion

    def __initializeViewsTools(self, in_parent:object) -> None:
        ins_views_tools = QtWidgets.QToolBar(in_parent,allowedAreas=QtCore.Qt.RightToolBarArea,iconSize=QtCore.QSize(28,28))
        ins_views_tools.setObjectName('views-toolbar')
        ins_views_tools.setMaximumHeight(285)
        in_parent.addToolBar(QtCore.Qt.RightToolBarArea, ins_views_tools)
        
        ins_front_view_tool = ins_views_tools.addAction(QtGui.QIcon(':/image/images/ToolViewsFront.png'),'')
        ins_front_view_tool.setToolTip('front view')
        ins_front_view_tool.triggered.connect(self.__slotSetFrontView)
        
        ins_back_view_tool = ins_views_tools.addAction(QtGui.QIcon(':/image/images/ToolViewsBack.png'),'')
        ins_back_view_tool.setToolTip('back view')
        ins_back_view_tool.triggered.connect(self.__slotSetBackView)
        
        ins_top_view_tool = ins_views_tools.addAction(QtGui.QIcon(':/image/images/ToolViewsTop.png'),'')
        ins_top_view_tool.setToolTip('top view')
        ins_top_view_tool.triggered.connect(self.__slotSetTopView)
        
        ins_bottom_view_tool = ins_views_tools.addAction(QtGui.QIcon(':/image/images/ToolViewsBottom.png'),'')
        ins_bottom_view_tool.setToolTip('bottom view')
        ins_bottom_view_tool.triggered.connect(self.__slotSetBottomView)

        ins_left_view_tool = ins_views_tools.addAction(QtGui.QIcon(':/image/images/ToolViewsLeft.png'),'')
        ins_left_view_tool.setToolTip('left view')
        ins_left_view_tool.triggered.connect(self.__slotSetLeftView)
        
        ins_right_view_tool = ins_views_tools.addAction(QtGui.QIcon(':/image/images/ToolViewsRight.png'),'')
        ins_right_view_tool.setToolTip('right view')
        ins_right_view_tool.triggered.connect(self.__slotSetRightView)
        
        ins_iso_view_tool = ins_views_tools.addAction(QtGui.QIcon(':/image/images/ToolViewsIso.png'),'')
        ins_iso_view_tool.setToolTip('iso view')
        ins_iso_view_tool.triggered.connect(self.__slotSetIsoView)
        
        ins_fit_view_tool = ins_views_tools.addAction(QtGui.QIcon(':/image/images/ToolViewsFit.png'),'')
        ins_fit_view_tool.setToolTip('fit view')
        ins_fit_view_tool.triggered.connect(self.__slotSetFitView)
    # region
    def __slotSetFrontView(self) -> None:
        ins_main_window = self.parent()
        
        ins_views_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'views-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
         
        ins_visual_window.setViewportView('front')
    def __slotSetBackView(self) -> None:
        ins_main_window = self.parent()
        
        ins_views_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'views-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_visual_window.setViewportView('back')
    def __slotSetTopView(self) -> None:
        ins_main_window = self.parent()
        
        ins_views_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'views-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_visual_window.setViewportView('top')
    def __slotSetBottomView(self) -> None:
        ins_main_window = self.parent()
        
        ins_views_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'views-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None project exist!')
                return None
            else:
                pass
        else:    
            pass
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_visual_window.setViewportView('bottom')
    def __slotSetLeftView(self) -> None:
        ins_main_window = self.parent()
        
        ins_views_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'views-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_visual_window.setViewportView('left')
    def __slotSetRightView(self) -> None:
        ins_main_window = self.parent()
        
        ins_views_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'views-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass
            
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_visual_window.setViewportView('right')
    def __slotSetIsoView(self) -> None:
        ins_main_window = self.parent()
        
        ins_views_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'views-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass   
            
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_visual_window.setViewportView('iso')
    def __slotSetFitView(self) -> None:
        ins_main_window = self.parent()
        
        ins_views_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'views-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set View Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_views_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_visual_window.setViewportView('fit')
    # endregion
    
    def __initializeRenderTools(self, in_parent:object) -> None:
        ins_render_tools = QtWidgets.QToolBar(in_parent,allowedAreas=QtCore.Qt.RightToolBarArea,iconSize=QtCore.QSize(28,28))
        ins_render_tools.setObjectName('render-toolbar')
        ins_render_tools.setMaximumHeight(220)
        in_parent.addToolBar(QtCore.Qt.RightToolBarArea,ins_render_tools)
        
        ins_normal_tool = ins_render_tools.addAction(QtGui.QIcon(':/image/images/ToolRenderNormal.png'),'')
        ins_normal_tool.setToolTip('normal')
        ins_normal_tool.triggered.connect(self.__slotSetNormalRender)
        
        ins_wireframe_tool= ins_render_tools.addAction(QtGui.QIcon(':/image/images/ToolRenderWireframe.png'),'')
        ins_wireframe_tool.setToolTip('wireframe')
        ins_wireframe_tool.triggered.connect(self.__slotSetWrieframeRender)
        
        ins_mesh_tool = ins_render_tools.addAction(QtGui.QIcon(':/image/images/ToolRenderMesh.png'),'')
        ins_mesh_tool.setToolTip('mesh')
        ins_mesh_tool.triggered.connect(self.__slotSetMeshRender)
        
        ins_color_tool = ins_render_tools.addAction(QtGui.QIcon(':/image/images/ToolRenderColor.png'),'')
        ins_color_tool.setToolTip('color')
        ins_color_tool.triggered.connect(self.__slotSetActorColor)
        
        ins_opacity_tool = ins_render_tools.addAction(QtGui.QIcon(':/image/images/ToolRenderOpacity.png'),'')
        ins_opacity_tool.setToolTip('opacity')
        ins_opacity_tool.triggered.connect(self.__slotSetActorOpacity)
        
        ins_visibility_tool = ins_render_tools.addAction(QtGui.QIcon(':/image/images/ToolRenderVisibility.png'),'')
        ins_visibility_tool.setToolTip('visibility')
        ins_visibility_tool.triggered.connect(self.__slotSetActorVisibility)
    # region
    def __slotSetNormalRender(self) -> None:
        ins_main_window = self.parent()
        
        ins_render_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'render-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Render Style Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Render Style Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass  
        
        ins_visual_window.setViewportRenderStyle('normal')
    def __slotSetWrieframeRender(self) -> None:
        ins_main_window = self.parent()
        
        ins_render_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'render-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Render Style Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Render Style Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass 
        
        ins_visual_window.setViewportRenderStyle('wireframe')
    def __slotSetMeshRender(self) -> None:
        ins_main_window = self.parent()
        
        ins_render_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'render-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Render Style Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass   
            
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Render Style Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass 
        
        ins_visual_window.setViewportRenderStyle('mesh')
    
    def __slotSetActorColor(self) -> None:
        ins_main_window = self.parent()
        
        ins_render_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'render-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Color Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Color Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass 
        
        actors_color_dict = ins_visual_window.getViewportActorsColor()
        if actors_color_dict == {}:
            return None
        else:
            pass
        
        ins_assign_actor_color_dialog = _AssignActorColor(ins_render_toolbar,actors_color_dict)
        ins_assign_actor_color_dialog.show()
        if ins_assign_actor_color_dialog.exec() == QtWidgets.QDialog.Accepted:
            actors_new_color_dict = ins_assign_actor_color_dialog.getActorsColor()
            if actors_new_color_dict == {}:
                pass
            else:
                ins_visual_window.setViewportActorsColor(actors_new_color_dict)
        else:
            pass
        ins_assign_actor_color_dialog.deleteLater()
    def __slotSetActorOpacity(self) -> None:
        ins_main_window = self.parent()
        
        ins_render_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'render-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Opacity Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass 
            
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Opacity Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass 
        
        actors_opacity_dict = ins_visual_window.getViewportActorsOpacity()
        if actors_opacity_dict == {}:
            return None
        else:
            pass
        
        ins_assign_actor_opacity_dialog = _AssignActorOpacity(ins_render_toolbar,actors_opacity_dict)
        ins_assign_actor_opacity_dialog.show()
        if ins_assign_actor_opacity_dialog.exec() == QtWidgets.QDialog.Accepted:
            actors_new_opacity_dict = ins_assign_actor_opacity_dialog.getActorsOpacity()
            if actors_new_opacity_dict == {}:
                pass
            else:
                ins_visual_window.setViewportActorsOpacity(actors_new_opacity_dict)
        else:
            pass
        ins_assign_actor_opacity_dialog.deleteLater()
    def __slotSetActorVisibility(self) -> None:
        ins_main_window = self.parent()
        
        ins_render_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,'render-toolbar')
        current_manager_index = ins_main_window.centralWidget().currentIndex() 
        if current_manager_index == 0:
            if ins_main_window.ins_project_database is None:
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Visibility Waring','None project exist!')
                return None
            else:
                pass
        else:
            pass
            
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Visibility Waring','None model exist!')
            return None
        else:
            pass
        
        if current_manager_index == 1:
            display_type = ins_visual_window.getDisplayTypeOfViewport()
            if display_type == 'graph':
                QtWidgets.QMessageBox.warning(ins_render_toolbar,'Set Selection Mode Waring','No available operation in graph state!')
                return None
            else:
                pass
        else:
            pass 
        
        actors_visibility_dict = ins_visual_window.getViewportActorsVisibility()
        if actors_visibility_dict == {}:
            return None
        else:
            pass
        
        ins_assign_actor_visibility_dialog = _AssignActorVisibility(ins_render_toolbar,actors_visibility_dict)
        ins_assign_actor_visibility_dialog.show()
        if ins_assign_actor_visibility_dialog.exec() == QtWidgets.QDialog.Accepted:
            actors_new_visibility_dict = ins_assign_actor_visibility_dialog.getActorsVisibility()
            if actors_new_visibility_dict == {}:
                pass
            else:
                ins_visual_window.setViewportActorsVisibiolity(actors_new_visibility_dict)
        else:
            pass
        ins_assign_actor_visibility_dialog.deleteLater()
    # endregion
    
    def __initializeOptimizationTools(self, in_parent:object) -> None:
        ins_optimization_tools = QtWidgets.QToolBar(in_parent,allowedAreas=QtCore.Qt.RightToolBarArea,iconSize=QtCore.QSize(28,28))
        ins_optimization_tools.setObjectName('optimization-toolbar')
        ins_optimization_tools.setMaximumHeight(45)
        in_parent.addToolBar(QtCore.Qt.RightToolBarArea,ins_optimization_tools)
        
        ins_binaryzation_tool = ins_optimization_tools.addAction(QtGui.QIcon(':/image/images/ToolOptimizationBinaryzation.png'),'')
        ins_binaryzation_tool.setToolTip('binaryzation')
        ins_binaryzation_tool.triggered.connect(self.__slotSetBinaryzationConfiguration)
    # region
    def __slotSetBinaryzationConfiguration(self) -> None:
        ins_main_window = self.parent()
        
        ins_optimization_tools = ins_main_window.findChild(QtWidgets.QToolBar,'optimization-toolbar')
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        if ins_manager_tab_widget.currentIndex() == 1:
            pass
        else:
            QtWidgets.QMessageBox.warning(ins_optimization_tools,'Set Binaryzation Waring',"No available operation in 'Models' state!")
            return None
        
        ins_mdi_area = ins_main_window.centralWidget().currentWidget()
        ins_visual_window = ins_mdi_area.currentSubWindow()
        if ins_visual_window is None:
            QtWidgets.QMessageBox.warning(ins_optimization_tools,'Set Binaryzation Waring','None database exist!')
            return None
        else:
            pass
        display_type = ins_visual_window.getDisplayTypeOfViewport()
        if display_type == 'graph':
            QtWidgets.QMessageBox.warning(ins_optimization_tools,'Set Binaryzation Waring','No available operation in graph state!')
            return None
        else:
            pass
        result_database_type = ins_visual_window.getDatabaseTypeOfViewport()
        if result_database_type is None:
            QtWidgets.QMessageBox.warning(ins_optimization_tools,'Set Binaryzation Waring','None database exist!')
            return None
        elif result_database_type != 'TOP':
            QtWidgets.QMessageBox.warning(ins_optimization_tools,'Set Binaryzation Waring','The operation is applicable exclusively to the topological configuration!')
            return None
        else:
            pass
        
        current_step,current_frame = ins_manager_tab_widget.widget(1).getCurrentStepAndFrame()
        if current_frame == '':
            QtWidgets.QMessageBox.warning(ins_optimization_tools,'Set Binaryzation Waring','Please select a resutls frame!')
            return None
        else:
            pass
        
        current_threshold_value = ins_visual_window.getTopologyDensityThresholdOfViewport()
        new_threshold_value, user_response = QtWidgets.QInputDialog.getDouble(ins_optimization_tools,'Binarization','Density threshold:',current_threshold_value,0.01,0.9,5)
        if user_response:
            if new_threshold_value == current_threshold_value:
                pass
            else:
                ins_visual_window.binarizeTopolotyDensityOfViewport(new_threshold_value,current_step,current_frame)
        else:
            pass
    # endregion

    def clearToolsState(self) -> None:
        ins_main_window = self.parent()
        
        ins_selection_tools = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
        if ins_selection_tools.actions()[0].isEnabled():
            pass
        else:
            ins_selection_tools.actions()[0].setEnabled(True)
        if ins_selection_tools.actions()[1].isEnabled():
            pass
        else:
            ins_selection_tools.actions()[1].setEnabled(True)
        
        if ins_selection_tools.actions()[0].isChecked():
            ins_selection_tools.actions()[0].trigger()
        elif ins_selection_tools.actions()[1].isChecked():
            ins_selection_tools.actions()[1].trigger()
        else:
            pass
    def setSelectionState(self, in_type:str, in_state:bool) -> None:
        ins_main_window = self.parent()
        ins_selection_tools = ins_main_window.findChild(QtWidgets.QToolBar,'selection-toolbar')
        
        if in_state:
            pass
        else:
            ins_selection_tools.actions()[0].setEnabled(True)
            ins_selection_tools.actions()[1].setEnabled(True)
            
        if in_type == 'node':
            ins_selection_tools.actions()[0].trigger()
        elif in_type == 'element':
            ins_selection_tools.actions()[1].trigger()
        else:
            pass
        
        if in_state:
            ins_selection_tools.actions()[0].setEnabled(False)
            ins_selection_tools.actions()[1].setEnabled(False)
        else:
            pass
    def collectVisualizationToolbar(self) -> None:
        ins_main_window = self.parent()
        
        for tool_name in ['selection-toolbar','views-toolbar','render-toolbar']:
            ins_visualization_toolbar = ins_main_window.findChild(QtWidgets.QToolBar,tool_name)
        
            ins_main_window.addToolBar(QtCore.Qt.RightToolBarArea,ins_visualization_toolbar)
# region
class _AssignActorColor(QtWidgets.QDialog):
    def __init__(self, in_parent:object, in_actors_color_dcit:dict):
        super().__init__(parent=in_parent, modal=True)
        
        self.__actors_color_dict = in_actors_color_dcit
        self.__actors_new_color_dict = {}

        self.setWindowTitle('Assign Color')
        self.setMinimumSize(210,300)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeActorList(ins_dialog_layout)
        
        self.__initializeUserButton(ins_dialog_layout)
        
    def __initializeActorList(self, in_ins_dialog_layout:object) -> None:
        ins_actors_list = QtWidgets.QListWidget(self)
        in_ins_dialog_layout.addWidget(ins_actors_list,1)
        
        ins_actors_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        for actor_name,actor_color in self.__actors_color_dict.items():
            ins_actor_item = QtWidgets.QListWidgetItem()
            ins_actor_item.setText(actor_name)
            
            ins_actor_color = QtGui.QColor()
            ins_actor_color.setRgbF(*actor_color)
            
            ins_actor_item.setBackground(ins_actor_color)
            ins_actors_list.addItem(ins_actor_item)
        
        ins_actors_list.itemDoubleClicked.connect(self.__slotSelectActorColor)
    # region
    def __slotSelectActorColor(self, in_selected_actor_item:object) -> None:
        ins_color_map = QtWidgets.QColorDialog()
        ins_color_map.setWindowIcon(QtGui.QIcon(":/image/images/ToolRenderColor.png"))
        if ins_color_map.exec() == QtWidgets.QColorDialog.Accepted:
            ins_selected_color = ins_color_map.selectedColor()
            if ins_selected_color.isValid():
                self.__actors_new_color_dict[in_selected_actor_item.text()] = ins_selected_color.getRgbF()[0:3]
                in_selected_actor_item.setBackground(ins_selected_color)
            else:
                pass
        
            self.findChild(QtWidgets.QPushButton,'accept-button').setEnabled(True)
        else:
            pass
        ins_color_map.deleteLater()
    # endregion
    def __initializeUserButton(self, in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.clicked.connect(self.accept)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getActorsColor(self) -> dict:
        return self.__actors_new_color_dict

class _AssignActorOpacity(QtWidgets.QDialog):
    def __init__(self, in_parent:object, in_actors_opacity_dcit:dict):
        super().__init__(parent=in_parent, modal=True)
        
        self.__actors_opacity_dict = in_actors_opacity_dcit
        self.__actors_new_opacity_dict = {}

        self.setWindowTitle('Assign Opacity')
        self.setMinimumSize(300,300)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeOpacitySilderArea(ins_dialog_layout)
        
        self.__initializeUserButton(ins_dialog_layout)
        
    def __initializeOpacitySilderArea(self, in_ins_dialog_layout:object) -> None:
        ins_actors_layout = QtWidgets.QFormLayout()
        in_ins_dialog_layout.addLayout(ins_actors_layout,1)
        
        for actor_name,actor_opacity in self.__actors_opacity_dict.items():
            ins_actor_label = QtWidgets.QLabel(actor_name,self,alignment=QtCore.Qt.AlignCenter)
            ins_actor_label.setFixedHeight(30)
            
            ins_actor_opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal,self)
            ins_actor_opacity_slider.setObjectName(actor_name)
            ins_actor_opacity_slider.setFixedHeight(30)
            ins_actor_opacity_slider.setRange(10,100)
            ins_actor_opacity_slider.setValue(actor_opacity*100)
            ins_actor_opacity_slider.setSingleStep(2)
            ins_actor_opacity_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
            ins_actor_opacity_slider.setTickInterval(10)
            ins_actor_opacity_slider.sliderMoved.connect(lambda: self.findChild(QtWidgets.QPushButton,'accept-button').setEnabled(True))
            
            ins_actors_layout.addRow(ins_actor_label,ins_actor_opacity_slider)
    
    def __initializeUserButton(self, in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.clicked.connect(self.accept)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getActorsOpacity(self) -> dict:
        for actor_name,actor_opacity in self.__actors_opacity_dict.items():
            current_actor_opacity = self.findChild(QtWidgets.QSlider,actor_name).value() * 0.01
            if actor_opacity == current_actor_opacity:
                continue
            else:
                self.__actors_new_opacity_dict[actor_name] = current_actor_opacity
        
        return self.__actors_new_opacity_dict

class _AssignActorVisibility(QtWidgets.QDialog):
    def __init__(self, in_parent:object, in_actors_visibility:dict):
        super().__init__(parent=in_parent, modal=True)
        
        self.__actors_visibility_dict = in_actors_visibility
        self.__actors_new_visibility_dict = {}

        self.setWindowTitle('Assign Visibility')
        self.setMinimumSize(150,300)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeActorVisibilityArea(ins_dialog_layout)
        
        self.__initializeUserButton(ins_dialog_layout)
        
    def __initializeActorVisibilityArea(self, in_ins_dialog_layout:object) -> None:
        ins_actors_layout = QtWidgets.QFormLayout()
        in_ins_dialog_layout.addLayout(ins_actors_layout,1)
        
        for actor_name,actor_visibility in self.__actors_visibility_dict.items():
            ins_actor_check_box = QtWidgets.QCheckBox(self)
            ins_actor_check_box.setObjectName(actor_name)
            ins_actor_check_box.setFixedSize(30,30)
            if actor_visibility == 1:
                ins_actor_check_box.setChecked(True)
            else:
                ins_actor_check_box.setChecked(False)
            
            ins_actor_label = QtWidgets.QLabel(actor_name,self,alignment=QtCore.Qt.AlignCenter)
            ins_actor_label.setFixedHeight(30)
            
            ins_actors_layout.addRow(ins_actor_check_box,ins_actor_label)
    
    def __initializeUserButton(self, in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton('Accept')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.clicked.connect(self.accept)
        ins_button_layout.addWidget(ins_accept_button)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton('Cancel')
        ins_cancel_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getActorsVisibility(self) -> dict:
        for actor_name,actor_visibility in self.__actors_visibility_dict.items():
            if self.findChild(QtWidgets.QCheckBox,actor_name).isChecked():
                current_actor_visibility = 1
            else:
                current_actor_visibility = 0
            if actor_visibility == current_actor_visibility:
                continue
            else:
                self.__actors_new_visibility_dict[actor_name] = current_actor_visibility
        
        return self.__actors_new_visibility_dict
# endregion

