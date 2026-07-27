# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import platform

from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore
import h5py
import vtk
import numpy

from config import common


class P4SMainMenubar(QtWidgets.QMenuBar):
    
    def __init__(self, in_parent:object=None):
        super().__init__(parent=in_parent)
        self.setObjectName("main-menubar")
        in_parent.setMenuBar(self)
        
        self.__initializeFileMenus()
        self.__initializeViewMenus()
        self.__initializeToolMenus()
        self.__initializeHelpMenus()
    
    def __initializeFileMenus(self) -> None:
        ins_file_bar = self.addMenu('File')
        
        ins_create_project = QtGui.QAction('Create Project', ins_file_bar)
        ins_create_project.setShortcut('Ctrl+N')
        ins_create_project.triggered.connect(self.__slotCreateProject)
        ins_file_bar.addAction(ins_create_project)
        
        
        ins_open_project = QtGui.QAction('Open Project', ins_file_bar)
        ins_open_project.setShortcut('Ctrl+O')
        ins_open_project.triggered.connect(self.__slotOpenProject)
        ins_file_bar.addAction(ins_open_project)
        
        ins_select_work_path = QtGui.QAction('Select Work Path', ins_file_bar)
        ins_select_work_path.setShortcut('Ctrl+W')
        ins_select_work_path.triggered.connect(self.__slotSelectWorkPath)
        ins_file_bar.addAction(ins_select_work_path)
        
        ins_file_bar.addSeparator()
        
        ins_save_project = QtGui.QAction('Save Project', ins_file_bar)
        ins_save_project.setShortcut('Ctrl+S')
        ins_save_project.triggered.connect(self.__slotSaveProject)
        ins_file_bar.addAction(ins_save_project)
        
        ins_save_as_project = QtGui.QAction('Save As ...', ins_file_bar)
        ins_save_as_project.setShortcut('Ctrl+Shift+S')
        ins_save_as_project.triggered.connect(self.__slotSaveAsProject)
        ins_file_bar.addAction(ins_save_as_project)
        
        ins_file_bar.addSeparator()
        
        ins_close_project = QtGui.QAction('Close Project', ins_file_bar)
        ins_close_project.triggered.connect(self.__slotCloseProject)
        ins_file_bar.addAction(ins_close_project)
        
        ins_file_bar.addSeparator()
        
        ins_exit_app = QtGui.QAction('Exit', ins_file_bar)
        ins_exit_app.triggered.connect(self.__slotExitApp)
        ins_file_bar.addAction(ins_exit_app)
    # region
    def __slotCreateProject(self) -> None:
        ins_main_window = self.parent()
        
        if ins_main_window.ins_project_database is None:
            if os.path.isdir(ins_main_window.work_path):
                pass
            else:
                QtWidgets.QMessageBox.critical(self,'Create Project Error',"The work path doesn't exist!")
                return None
        else:
            QtWidgets.QMessageBox.warning(self,'Create Project Waring','A project is currently open. Please close it first!')
            return None
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(0)
        
        ins_create_project_dialog = _CreateProjectDialog(self)
        ins_create_project_dialog.show()
        if ins_create_project_dialog.exec() == QtWidgets.QDialog.Accepted:
            project_name = ins_create_project_dialog.getPojectName()
            full_project_name = os.sep.join([ins_main_window.work_path,project_name])+'.p4st'

            ins_main_window.setWindowTitle(f'{common.P4SString.VERSION_NUMBER} | Path - {ins_main_window.work_path} |  Project - {project_name}')
            ins_main_window.createProjectDatabase(full_project_name)
            ins_main_window.printMessage(f'The project - "{project_name}" successfully created!')
        else:
            pass
        ins_create_project_dialog.deleteLater()
    def __slotOpenProject(self) -> None:
        ins_main_window = self.parent()
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(0)
        
        if ins_main_window.ins_project_database is None:
            pass
        else:
            QtWidgets.QMessageBox.warning(self,'Open Project Waring','Close the current project before opening another one!')
            return None
        
        if os.path.isdir(ins_main_window.work_path):
            pass
        else:
            QtWidgets.QMessageBox.critical(self,'Open Project Error',"The work path doesn't exist!")
            return None
        
        project_full_name,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Select Project File',ins_main_window.work_path,'P4Struct File(*.p4st)')
        if project_full_name == '':
            return None
        else:
            pass
        
        project_file_path = os.path.dirname(project_full_name)
        project_name = os.path.basename(project_full_name).split(".")[0]
        if os.path.samefile(ins_main_window.work_path,project_file_path):
            pass
        else:
            ins_response_button = QtWidgets.QMessageBox.question(self,'Change WorK Path Waring','Work path of the selected project different from original work path!\nDo you want to change the work path?')
            if ins_response_button == QtWidgets.QMessageBox.Yes:
                ins_main_window.work_path = project_file_path

                ins_main_window.printMessage(f'The work path - "{project_file_path}" successfully changed!')
            else:
                return None
        ins_main_window.setWindowTitle(f'{common.P4SString.VERSION_NUMBER} | Path - {project_file_path} | Project - {project_name}')

        ins_main_window.openProjectDatabase(project_full_name)
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_manager = ins_manager_tab_widget.currentWidget()
        
        from .visualization import P4SModelVisualWindow
        project_models_name_list = ins_main_window.ins_project_database.getModels()
        for model_name in project_models_name_list:
            
            P4SModelVisualWindow(ins_models_mdi_area,model_name)
        
            model_dimension = ins_main_window.ins_project_database.getModelDimension(model_name)
            ins_model_manager.ImportModelFromProject(model_name,model_dimension)
        del P4SModelVisualWindow

        ins_main_window.printMessage(f'The project - "{project_name}" successfully opened!')
    def __slotSelectWorkPath(self) -> None:
        ins_main_window = self.parent()
        if ins_main_window.ins_project_database is None:
            selected_work_path = QtWidgets.QFileDialog.getExistingDirectory(self,'Select Work Path',ins_main_window.work_path)
            if selected_work_path == '':
                pass
            elif os.path.samefile(selected_work_path,ins_main_window.work_path):
                pass
            else:
                ins_main_window.work_path = selected_work_path
                
                for file_name in os.listdir(selected_work_path):
                    if file_name.endswith(".p4st_temp") or file_name.endswith(".p4st_temp-journal"):
                        os.remove(os.sep.join([selected_work_path,file_name]))
                    else:   
                        continue
                
                ins_main_window.setWindowTitle(f'{common.P4SString.VERSION_NUMBER} | Path - {selected_work_path}')
                ins_main_window.printMessage(f'The work path - "{selected_work_path}" successfully changed!')
        else:
            QtWidgets.QMessageBox.warning(self,'Select Work Path Waring','A project is currently open. Please close it first!',QtWidgets.QMessageBox.Cancel)
            return None
    def __slotSaveProject(self) -> None:
        ins_main_window = self.parent()

        if ins_main_window.ins_project_database is None:
            QtWidgets.QMessageBox.warning(self,'Save Project Error','None project exist!')
            return None
        else:   pass

        ins_main_window.ins_project_database.saveProjectDatabase()
        ins_main_window.printMessage('The project successfully saved !')
    def __slotSaveAsProject(self) -> None:
        pass
    def __slotCloseProject(self) -> None:
        ins_main_window = self.parent()
        
        if ins_main_window.ins_project_database is None: 
            QtWidgets.QMessageBox.warning(self,'Close Project Waring',"None project exist!",QtWidgets.QMessageBox.Cancel)
            return None
        else:
            pass
        
        ins_manager_tab_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget').widget()
        ins_manager_tab_widget.setCurrentIndex(0)
        
        response_to_close_project = QtWidgets.QMessageBox.question(self,'Close Project Waring','Unsaved data will be lost,continue?',defaultButton=QtWidgets.QMessageBox.StandardButton.No)
        if response_to_close_project is QtWidgets.QMessageBox.StandardButton.Yes:
            ins_main_window.setWindowTitle(f"{common.P4SString.VERSION_NUMBER} | Path - {ins_main_window.work_path}")
            
            ins_main_window.ins_project_database.closeProjectDatabase()
            
            ins_model_manager = ins_manager_tab_widget.currentWidget()
            current_model_name = ins_model_manager.getCurrentModleName()
            if current_model_name == '':
                pass
            else:
                ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
    
                while current_model_name != '':
                    ins_model_manager.removeCurrentModel(in_enable_model_change=False)
                    
                    ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_model_name)
                    ins_model_visual_window.finalizeInteractor()
                    ins_model_visual_window.close()
                    ins_models_mdi_area.removeSubWindow(ins_model_visual_window)
                    ins_model_visual_window.setParent(None)
                    ins_model_visual_window.deleteLater()
                    del ins_model_visual_window
                    
                    current_model_name = ins_model_manager.getCurrentModleName()

            ins_main_window.printMessage('The project successfully closed!')
            
            del ins_main_window.ins_project_database
            ins_main_window.ins_project_database = None
        else:
            return None
    def __slotExitApp(self) -> None:
        ins_main_window = self.parent()
        ins_main_window.close()
    # endregion
    
    def __initializeViewMenus(self) -> None:
        ins_view_bar = self.addMenu('View')
        
        ins_show_manager = QtGui.QAction('Show Manager', ins_view_bar)
        ins_show_manager.setCheckable(True)
        ins_show_manager.setChecked(True)
        ins_show_manager.triggered.connect(self.__slotShowManager)
        ins_view_bar.addAction(ins_show_manager)
        
        ins_show_message = QtGui.QAction('Show Message', ins_view_bar)
        ins_show_message.setCheckable(True)
        ins_show_message.setChecked(True)
        ins_show_message.triggered.connect(self.__slotShowMessage)
        ins_view_bar.addAction(ins_show_message)
        
        ins_view_bar.addSeparator()
        
        ins_collect_toolbar = QtGui.QAction('Collect Toolbar', ins_view_bar)
        ins_collect_toolbar.triggered.connect(self.__slotCollectToolbar)
        ins_view_bar.addAction(ins_collect_toolbar)
    # region
    def __slotShowManager(self, in_state:bool) -> None:
        ins_main_window = self.parent()
        
        ins_manager_dock_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget')
        ins_manager_dock_widget.setVisible(in_state)
    def __slotShowMessage(self, in_state:bool) -> None:
        ins_main_window = self.parent()
        
        ins_message_dock_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'message-dock-widget')
        ins_message_dock_widget.setVisible(in_state)
    def __slotCollectToolbar(self) -> None:
        ins_main_window = self.parent()
        
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_visualization_toolbar.collectVisualizationToolbar()
    # endregion
    
    def __initializeToolMenus(self) -> None:
        ins_tool_bar = self.addMenu('Tool')
        
        ins_top2stl_manager = QtGui.QAction('Top to STL', ins_tool_bar)
        ins_top2stl_manager.triggered.connect(self.__slotTopToSTL)
        ins_tool_bar.addAction(ins_top2stl_manager)
    # region
    def __slotTopToSTL(self) -> None:
        ins_top2stl_dialog = _ExportTopToSTLDialog(self)
        ins_top2stl_dialog.show()
        if ins_top2stl_dialog.exec() == QtWidgets.QDialog.Accepted:
            pass
        else:
            pass
        ins_top2stl_dialog.deleteLater()
    # endregion
    
    def __initializeHelpMenus(self) -> None:
        ins_help_bar = self.addMenu('Help')

        ins_enter_website = QtGui.QAction('enter website',ins_help_bar)
        ins_enter_website.triggered.connect(self.__slotEnterWebsite)
        ins_help_bar.addAction(ins_enter_website)

        ins_about_license = QtGui.QAction('about license',ins_help_bar)
        ins_about_license.triggered.connect(self.__slotViewLicense)
        ins_help_bar.addAction(ins_about_license)
    # region
    def __slotEnterWebsite(self) -> None:
        url = QtCore.QUrl('https://github.com/HiPerStruct/P4Struct')
        if QtGui.QDesktopServices.openUrl(url):
            pass
        else:
            QtWidgets.QMessageBox.warning(self,'Enter Website','The webpage failed to load.')
    def __slotViewLicense(self) -> None:
        ins_license_dialog = QtWidgets.QDialog(self)
        
        ins_license_dialog.setWindowTitle('License')
        ins_license_dialog.setWindowModality(QtCore.Qt.WindowModal)
        ins_license_dialog.setFixedSize(320,310)

        ins_tip_label = QtWidgets.QLabel('P4Struct',ins_license_dialog,alignment=QtCore.Qt.AlignCenter)
        ins_tip_label.setGeometry(10,5,300,60)
        ins_tip_label.setStyleSheet('background-color: rgb(255,255,255); font-size: 25pt')

        ins_info_label = QtWidgets.QLabel('Info:',ins_license_dialog)
        ins_info_label.setGeometry(10,70,60,30)
        ins_info_label.setStyleSheet('font: bold')

        ins_version_label = QtWidgets.QLabel('Version: V1.0',ins_license_dialog)
        ins_version_label.setGeometry(30,105,260,20)
        ins_license_label = QtWidgets.QLabel('Type: AGLP-3.0',ins_license_dialog)
        ins_license_label.setGeometry(30,130,290,20)
        
        ins_author_label = QtWidgets.QLabel(f'Author: Huaiwang Ji',ins_license_dialog)
        ins_author_label.setGeometry(30,155,260,20)
        ins_contact_label = QtWidgets.QLabel(f'Contact: jihuaiwang@outlook.com',ins_license_dialog)
        ins_contact_label.setGeometry(30,180,260,20)

        ins_user_label = QtWidgets.QLabel(f'User: {os.getlogin()}',ins_license_dialog)
        ins_user_label.setGeometry(30,205,260,20)
        computer_message = platform.uname()
        ins_server_label = QtWidgets.QLabel(f'Server: {computer_message.node}',ins_license_dialog)
        ins_server_label.setGeometry(30,230,260,20)
        ins_system_label = QtWidgets.QLabel(f'System: {computer_message.system}',ins_license_dialog)
        ins_system_label.setGeometry(30,255,260,20)
        ins_machine_label = QtWidgets.QLabel(f'Machine: {computer_message.machine}',ins_license_dialog)
        ins_machine_label.setGeometry(30,280,260,20)

        ins_license_dialog.show()
        if ins_license_dialog.exec() == 0:
            pass
        else:
            pass
        ins_license_dialog.deleteLater()
    # endregion

class _CreateProjectDialog(QtWidgets.QDialog):
    
    def __init__(self,in_parent:object):
        super().__init__(parent=in_parent,modal=True)
        
        self.setWindowTitle('Create Project')
        self.setFixedHeight(90)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeNameEdit(ins_dialog_layout)
        ins_dialog_layout.addStretch() 
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeNameEdit(self,in_ins_dialog_layout:object) -> None:
        ins_project_name_layout = QtWidgets.QHBoxLayout()
        
        ins_project_name_label = QtWidgets.QLabel('project name',self,alignment=QtCore.Qt.AlignCenter)
        ins_project_name_label.setFixedSize(100,30)
        ins_project_name_layout.addWidget(ins_project_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('project-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression("[a-zA-Z0-9_-]+")))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['P4S_','P4Struct_','Project_','P4S-','P4Struct-','Project-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckProjectName)
        ins_project_name_layout.addWidget(ins_name_line_edit,1)

        in_ins_dialog_layout.addLayout(ins_project_name_layout)
    # region
    def __slotCheckProjectName(self, in_project_name:str) -> None:
        ins_main_window = self.parent().parent()
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        if in_project_name == '':
            ins_accept_button.setEnabled(False)
        elif os.path.isfile(os.sep.join([ins_main_window.work_path,in_project_name])+'.p4st'):
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
    
    def getPojectName(self) -> str:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'project-name-edit')
        project_name = ins_name_line_edit.text()
        
        return project_name

class _ExportTopToSTLDialog(QtWidgets.QDialog):
    
    def __init__(self,in_parent:object):
        super().__init__(parent=in_parent,modal=True)
        
        self.setWindowTitle('Export Topological Configuration to STL File')
        self.setFixedHeight(275)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeFileSelection(ins_dialog_layout)
        self.__initializeInstanceSelection(ins_dialog_layout)
        self.__initializeSmoothFilterSelection(ins_dialog_layout)
        self.__initializeSurfaceThicknessSelection(ins_dialog_layout)
        self.__initializeReservedDomainSelection(ins_dialog_layout)
        self.__initializeOutputFrameSelection(ins_dialog_layout)
        self.__initializeThresholdSelection(ins_dialog_layout)
        self.__initializeExportButton(ins_dialog_layout)
        
    def __initializeFileSelection(self,in_ins_dialog_layout:object) -> None:
        ins_setting_layout = QtWidgets.QHBoxLayout()
        
        ins_file_name_label = QtWidgets.QLabel('Topological data',self,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_file_name_label.setFixedSize(125,30)
        ins_setting_layout.addWidget(ins_file_name_label,0)
        ins_colon_label = QtWidgets.QLabel(':',self,alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        ins_colon_label.setFixedSize(4,30)
        ins_setting_layout.addWidget(ins_colon_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('file-name-edit')
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(100)
        ins_name_line_edit.setReadOnly(True)
        ins_setting_layout.addWidget(ins_name_line_edit,1)
        
        ins_file_selection_button =  QtWidgets.QPushButton(self)
        ins_file_selection_button.setFixedSize(60,30)
        ins_file_selection_button.setText('select')
        ins_file_selection_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_file_selection_button.clicked.connect(self.__slotSelectResultFile)
        ins_setting_layout.addWidget(ins_file_selection_button,0)

        in_ins_dialog_layout.addLayout(ins_setting_layout,0)
    # region
    def __slotSelectResultFile(self) -> None:
        ins_main_window = self.parent().parent()
        work_path = ins_main_window.work_path

        self.findChild(QtWidgets.QLineEdit,'file-name-edit').clear()
        self.findChild(QtWidgets.QComboBox,'instance-box').clear()
        self.findChild(QtWidgets.QComboBox,'smooth-filter-box').setCurrentIndex(0)
        self.findChild(QtWidgets.QComboBox,'output-frame-box').clear()
        
        full_file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(parent=self,caption='select file',dir=work_path,filter='*.res')
        if full_file_name == '':
            return None
        elif file_type == '*.res':
            if full_file_name == '':
                QtWidgets.QMessageBox.critical(self,'Export STL Error','No file has been selected!')
                return None
            elif not os.path.isfile(full_file_name):
                QtWidgets.QMessageBox.critical(self,'Export STL Error',"The file doesn't exist!")
                return None
            else:
                pass
        
            with h5py.File(full_file_name,'r') as ins_top_results_file:
                instance_name_list = []
                if 'Mesh' in ins_top_results_file:
                    if 'Instances' in ins_top_results_file['Mesh']:
                        instance_name_list = list(ins_top_results_file['Mesh']['Instances'].keys())
                    else:
                        pass
                else:
                    pass
            
                maximum_result_frame = None
                if 'Elements' in ins_top_results_file:
                    if 'X' in ins_top_results_file['Elements']:
                        maximum_result_frame = max([int(i) for i in ins_top_results_file['Elements']['X']['optimum'].keys()])
                    else:
                        pass
                else:
                    pass
            if len(instance_name_list) == 0:
                QtWidgets.QMessageBox.critical(self,'Export STL Error',"The file format error!")
                return None
            elif maximum_result_frame == None:
                QtWidgets.QMessageBox.critical(self,'Export STL Error',"The file format error!")
                return None
            else:
                pass

            self.findChild(QtWidgets.QComboBox,'instance-box').addItems(instance_name_list)
            self.findChild(QtWidgets.QComboBox,'output-frame-box').addItems([str(i) for i in range(maximum_result_frame+1)])
            self.findChild(QtWidgets.QLineEdit,'file-name-edit').setText(full_file_name)
        else:
            QtWidgets.QMessageBox.warning(self,'Export STL Waring','File type error!')
            return None

        self.findChild(QtWidgets.QLabel,'propress-label').setText('Ready')
    # endregion
    
    def __initializeInstanceSelection(self,in_ins_dialog_layout:object) -> None:
        ins_setting_layout = QtWidgets.QHBoxLayout()
        
        ins_instance_selection_label = QtWidgets.QLabel('Instance name',self,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_instance_selection_label.setFixedSize(125,30)
        ins_setting_layout.addWidget(ins_instance_selection_label,0)
        ins_colon_label = QtWidgets.QLabel(':',self,alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        ins_colon_label.setFixedSize(4,30)
        ins_setting_layout.addWidget(ins_colon_label,0)

        ins_instance_selection_box =  QtWidgets.QComboBox(self)
        ins_instance_selection_box.setObjectName('instance-box')
        ins_instance_selection_box.setFixedHeight(30)
        ins_instance_selection_box.setPlaceholderText('None Selection')
        ins_setting_layout.addWidget(ins_instance_selection_box,1)

        in_ins_dialog_layout.addLayout(ins_setting_layout,0)

    def __initializeSmoothFilterSelection(self,in_ins_dialog_layout:object) -> None:
        ins_setting_layout = QtWidgets.QHBoxLayout()
        
        ins_smooth_filter_label = QtWidgets.QLabel('Smooth filter',self,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_smooth_filter_label.setFixedSize(125,30)
        ins_setting_layout.addWidget(ins_smooth_filter_label,0)
        ins_colon_label = QtWidgets.QLabel(':',self,alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        ins_colon_label.setFixedSize(4,30)
        ins_setting_layout.addWidget(ins_colon_label,0)

        ins_filter_selection_box =  QtWidgets.QComboBox(self)
        ins_filter_selection_box.setObjectName('smooth-filter-box')
        ins_filter_selection_box.setFixedHeight(30)
        ins_filter_selection_box.addItems(['On','Off'])
        ins_setting_layout.addWidget(ins_filter_selection_box,1)

        in_ins_dialog_layout.addLayout(ins_setting_layout,0)

    def __initializeSurfaceThicknessSelection(self,in_ins_dialog_layout:object) -> None:
        ins_setting_layout = QtWidgets.QHBoxLayout()
        
        ins_surface_thickness_label = QtWidgets.QLabel('Surface thickness',self,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_surface_thickness_label.setFixedSize(125,30)
        ins_setting_layout.addWidget(ins_surface_thickness_label,0)
        ins_colon_label = QtWidgets.QLabel(':',self,alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        ins_colon_label.setFixedSize(4,30)
        ins_setting_layout.addWidget(ins_colon_label,0)
        
        ins_thickness_value_spin =  QtWidgets.QDoubleSpinBox(self)
        ins_thickness_value_spin.setObjectName('thickness-spin')
        ins_thickness_value_spin.setFixedSize(120,30)
        ins_thickness_value_spin.setRange(0.0,999.0)
        ins_thickness_value_spin.setDecimals(3)
        ins_thickness_value_spin.setSingleStep(1.0)
        ins_thickness_value_spin.setValue(0.0)
        ins_setting_layout.addWidget(ins_thickness_value_spin,0)
        
        ins_surface_location_box =  QtWidgets.QComboBox(self)
        ins_surface_location_box.setObjectName('surface-location-box')
        ins_surface_location_box.setFixedSize(100,30)
        ins_surface_location_box.addItems(['bottom','top'])
        ins_setting_layout.addWidget(ins_surface_location_box,0)
        
        ins_setting_layout.addStretch()

        in_ins_dialog_layout.addLayout(ins_setting_layout,0)
    
    def __initializeReservedDomainSelection(self, in_ins_dialog_layout:object) -> None:
        ins_setting_layout = QtWidgets.QHBoxLayout()
        
        ins_reserved_domain_label = QtWidgets.QLabel('Reserved domain',self,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_reserved_domain_label.setFixedSize(125,30)
        ins_setting_layout.addWidget(ins_reserved_domain_label,0)
        ins_colon_label = QtWidgets.QLabel(':',self,alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        ins_colon_label.setFixedSize(4,30)
        ins_setting_layout.addWidget(ins_colon_label,0)

        ins_domain_selection_box =  QtWidgets.QComboBox(self)
        ins_domain_selection_box.setObjectName('reserved-domain-box')
        ins_domain_selection_box.setFixedSize(120,30)
        ins_domain_selection_box.addItems(['inside','outside'])
        ins_setting_layout.addWidget(ins_domain_selection_box,0)

        ins_setting_layout.addStretch()

        in_ins_dialog_layout.addLayout(ins_setting_layout,0)

    def __initializeOutputFrameSelection(self,in_ins_dialog_layout:object) -> None:
        ins_setting_layout = QtWidgets.QHBoxLayout()
        
        ins_output_frame_label = QtWidgets.QLabel('Output frame',self,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_output_frame_label.setFixedSize(125,30)
        ins_setting_layout.addWidget(ins_output_frame_label,0)
        ins_colon_label = QtWidgets.QLabel(':',self,alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        ins_colon_label.setFixedSize(4,30)
        ins_setting_layout.addWidget(ins_colon_label,0)

        ins_frame_selection_box =  QtWidgets.QComboBox(self)
        ins_frame_selection_box.setObjectName('output-frame-box')
        ins_frame_selection_box.setFixedSize(120,30)
        ins_frame_selection_box.setPlaceholderText('Last Frame')
        ins_setting_layout.addWidget(ins_frame_selection_box,1)

        ins_setting_layout.addStretch()

        in_ins_dialog_layout.addLayout(ins_setting_layout,0)

    def __initializeThresholdSelection(self,in_ins_dialog_layout:object) -> None:
        ins_setting_layout = QtWidgets.QHBoxLayout()
        
        ins_threshold_value_label = QtWidgets.QLabel('Threshold value',self,alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        ins_threshold_value_label.setFixedSize(125,30)
        ins_setting_layout.addWidget(ins_threshold_value_label,0)
        ins_colon_label = QtWidgets.QLabel(':',self,alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        ins_colon_label.setFixedSize(4,30)
        ins_setting_layout.addWidget(ins_colon_label,0)
        
        ins_threshold_value_spin =  QtWidgets.QDoubleSpinBox(self)
        ins_threshold_value_spin.setObjectName('threshold-spin')
        ins_threshold_value_spin.setFixedSize(120,30)
        ins_threshold_value_spin.setRange(0.01,0.9)
        ins_threshold_value_spin.setDecimals(3)
        ins_threshold_value_spin.setSingleStep(0.001)
        ins_threshold_value_spin.setValue(0.5)
        ins_setting_layout.addWidget(ins_threshold_value_spin,0)
        
        ins_setting_layout.addStretch()

        in_ins_dialog_layout.addLayout(ins_setting_layout,0)

    def __initializeExportButton(self,in_ins_dialog_layout:object) -> None:
        ins_setting_layout = QtWidgets.QHBoxLayout()

        ins_export_button =  QtWidgets.QPushButton(self)
        ins_export_button.setFixedSize(80,30)
        ins_export_button.setText('export')
        ins_export_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_export_button.clicked.connect(self.__slotExportFile)
        ins_setting_layout.addWidget(ins_export_button,0)

        ins_setting_layout.addStretch()
        
        ins_propress_state_label = QtWidgets.QLabel('state:',self,alignment=QtCore.Qt.AlignCenter)
        ins_propress_state_label.setFixedSize(55,30)
        ins_setting_layout.addWidget(ins_propress_state_label,0)
        
        ins_propress_label = QtWidgets.QLabel('Ready',self,alignment=QtCore.Qt.AlignCenter)
        ins_propress_label.setObjectName('propress-label')
        ins_propress_label.setFixedSize(95,30)
        ins_setting_layout.addWidget(ins_propress_label,0)

        in_ins_dialog_layout.addLayout(ins_setting_layout,0)
    # region
    def __slotExportFile(self) -> None:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'file-name-edit')
        full_file_name = ins_name_line_edit.text()
        
        if full_file_name == '':
            QtWidgets.QMessageBox.critical(self,'Export STL Error','No file has been selected!')
            return None
        elif full_file_name.split('.')[-1] != 'res':
            QtWidgets.QMessageBox.critical(self,'Export STL Error','File type error!')
            return None
        elif not os.path.isfile(full_file_name):
            QtWidgets.QMessageBox.critical(self,'Export STL Error',"The file doesn't exist!")
            return None
        else:
            pass
        
        instance_name = self.findChild(QtWidgets.QComboBox,'instance-box').currentText()
        smooth_filter = self.findChild(QtWidgets.QComboBox,'smooth-filter-box').currentText()
        thickness_value = self.findChild(QtWidgets.QDoubleSpinBox,'thickness-spin').value()
        surface_location = self.findChild(QtWidgets.QComboBox,'surface-location-box').currentText()
        reserved_type_num = self.findChild(QtWidgets.QComboBox,'reserved-domain-box').currentIndex()
        output_frame = self.findChild(QtWidgets.QComboBox,'output-frame-box').currentText()
        threshold_value = self.findChild(QtWidgets.QDoubleSpinBox,'threshold-spin').value()

        if instance_name == '':
            QtWidgets.QMessageBox.critical(self,'Export STL Waring','Select an instance')
            return None
        else:
            pass
        
        elements_geometry_num_list = []
        with h5py.File(full_file_name,'r') as ins_top_results_file:
            if 'basic' not in ins_top_results_file:
                pass
            elif 'Mesh' not in ins_top_results_file:
                pass
            elif instance_name not in ins_top_results_file['Mesh']['Instances']:
                pass
            elif 'Elements' not in ins_top_results_file:
                pass
            elif ins_top_results_file['basic'][1] != b'OPT':
                pass
            elif 'X' not in ins_top_results_file['Elements']:
                pass
            else:
                instance_elements_label_range = ins_top_results_file['Mesh']['Instances'][instance_name][2:4]
                elements_geometry_num_list = [int(i) for i in numpy.unique(ins_top_results_file['Mesh']['geometry'][instance_elements_label_range[0]-1:instance_elements_label_range[1]])]

                model_dimension = str(ins_top_results_file['basic'][0],encoding='utf-8')

                if output_frame == '':
                    output_frame = str(ins_top_results_file['Steps']['optimum'][0][-1])
                else:
                    pass
        
        instance_include_geometry_list = []
        if model_dimension == '2D':
            if 2 in elements_geometry_num_list or 3 in elements_geometry_num_list or 7 in elements_geometry_num_list or 8 in elements_geometry_num_list:
                instance_include_geometry_list.append('surface')
            else:
                pass

            if 1 in elements_geometry_num_list or 6 in elements_geometry_num_list:
                instance_include_geometry_list = []
                print('Currently, the line element is not supported!')
            else:
                pass
        elif model_dimension == '3D':
            if 2 in elements_geometry_num_list or 3 in elements_geometry_num_list or 7 in elements_geometry_num_list or 8 in elements_geometry_num_list:
                instance_include_geometry_list.append('surface')
            else:
                pass
            if 4 in elements_geometry_num_list or 9 in elements_geometry_num_list or 5 in elements_geometry_num_list or 10 in elements_geometry_num_list:
                instance_include_geometry_list.append('solid')
            else:
                pass

            if 1 in elements_geometry_num_list or 6 in elements_geometry_num_list:
                instance_include_geometry_list = []
                print('Currently, the line element is not supported!')
            else:
                pass
        else:
            pass
        del elements_geometry_num_list
        if len(instance_include_geometry_list) == 0:
            QtWidgets.QMessageBox.critical(self,'Export STL Error',"The file format error!")
            return None
        else:
            pass
        
        ins_propress_label = self.findChild(QtWidgets.QLabel,'propress-label')
        ins_propress_label.setText('In progress...')
        
        file_basename = full_file_name.split('.')[0]
        try:
            with h5py.File(full_file_name,'r') as ins_top_results_file:
                ins_assembly_include_nodes_set = ins_top_results_file['Mesh']['nodes']
                ins_assembly_include_elements_set = ins_top_results_file['Mesh']['elements']
                ins_assembly_include_elements_geometry_set = ins_top_results_file['Mesh']['geometry']
                ins_output_frame_result_set = ins_top_results_file['Elements']['X']['optimum'][output_frame]

                instance_nodes_label_range = ins_top_results_file['Mesh']['Instances'][instance_name][0:2]
                instance_elements_label_range = ins_top_results_file['Mesh']['Instances'][instance_name][2:4]
                trans_vtk_surface_geometry_dict = {2:5, 3:9, 7:22, 8:23}
                trans_vtk_solid_geometry_dict = {4:10, 9:24, 5:12, 10:25}

                if len(instance_include_geometry_list) == 1 and 'surface' in instance_include_geometry_list:
                    ins_whole_points = vtk.vtkPoints()
                    ins_whole_points.SetNumberOfPoints(instance_nodes_label_range[1]-instance_nodes_label_range[0]+1)
                    for node_index,node_coordinates in enumerate(ins_assembly_include_nodes_set[instance_nodes_label_range[0]-1:instance_nodes_label_range[1]]):
                        ins_whole_points.SetPoint(node_index,node_coordinates)

                    if smooth_filter == 'On':
                        ins_whole_ugrid = vtk.vtkUnstructuredGrid()
                        ins_whole_ugrid.SetPoints(ins_whole_points)
                        ins_whole_result_array = vtk.vtkDoubleArray()
                        ins_whole_result_array.SetName('EX')
                        for element_label in range(instance_elements_label_range[0],instance_elements_label_range[1]+1):
                            element_geometry_type_number = ins_assembly_include_elements_geometry_set[element_label-1]
                            element_include_nodes_label = ins_assembly_include_elements_set[element_label-1]
                            
                            ins_whole_ugrid.InsertNextCell(trans_vtk_surface_geometry_dict[element_geometry_type_number],len(element_include_nodes_label),element_include_nodes_label-1)
                            ins_whole_result_array.InsertNextValue(ins_output_frame_result_set[0,element_label-1])
                        ins_whole_ugrid.GetCellData().AddArray(ins_whole_result_array)
                        
                        ins_whole_data_to_points_transformer = vtk.vtkCellDataToPointData()
                        ins_whole_data_to_points_transformer.SetInputData(ins_whole_ugrid)
                        ins_whole_data_to_points_transformer.AddCellDataArray('EX')
                        ins_whole_data_to_points_transformer.SetPassCellData(0)
                        ins_whole_data_to_points_transformer.Update()
                        ins_whole_data_to_points_transformer.GetOutput().GetPointData().SetActiveScalars('EX')

                        ins_whole_domain_clipper = vtk.vtkClipDataSet()
                        ins_whole_domain_clipper.SetInputData(ins_whole_data_to_points_transformer.GetOutput())
                        ins_whole_domain_clipper.SetValue(threshold_value)
                        ins_whole_domain_clipper.SetInsideOut(reserved_type_num)
                        ins_whole_domain_clipper.Update()
                        if ins_whole_domain_clipper.GetOutput().GetNumberOfCells() == 0:
                            print('Export Failed: The threshold value is too large!')
                            raise ValueError()
                        else:
                            pass
                        
                        ins_output_domain_cleaner = vtk.vtkCleanUnstructuredGrid()
                        ins_output_domain_cleaner.SetInputData(ins_whole_domain_clipper.GetOutput())
                        ins_output_domain_cleaner.SetTolerance(1e-6)
                        ins_output_domain_cleaner.RemovePointsWithoutCellsOn()
                        ins_output_domain_cleaner.Update()
                        
                        ins_output_domain_geometry_filter = vtk.vtkGeometryFilter()
                        ins_output_domain_geometry_filter.SetInputData(ins_output_domain_cleaner.GetOutput())
                        ins_output_domain_geometry_filter.Update()
                        ins_output_domain_connectivity_filter = vtk.vtkPolyDataConnectivityFilter()
                        ins_output_domain_connectivity_filter.SetInputData(ins_output_domain_geometry_filter.GetOutput())
                        ins_output_domain_connectivity_filter.SetExtractionModeToLargestRegion()
                        ins_output_domain_connectivity_filter.Update()
                        ins_output_domain_triangle_filter = vtk.vtkTriangleFilter()
                        ins_output_domain_triangle_filter.SetInputData(ins_output_domain_connectivity_filter.GetOutput())
                        ins_output_domain_triangle_filter.SetPassVerts(0)
                        ins_output_domain_triangle_filter.SetPassLines(0)
                        ins_output_domain_triangle_filter.Update()
                        ins_output_domain_triangle_cleaner = vtk.vtkCleanPolyData()
                        ins_output_domain_triangle_cleaner.SetInputData(ins_output_domain_triangle_filter.GetOutput())
                        ins_output_domain_triangle_cleaner.SetTolerance(1e-4)
                        ins_output_domain_triangle_cleaner.PointMergingOn()
                        ins_output_domain_triangle_cleaner.ConvertStripsToPolysOn()
                        ins_output_domain_triangle_cleaner.ConvertPolysToLinesOn()
                        ins_output_domain_triangle_cleaner.ConvertLinesToPointsOn()
                        ins_output_domain_triangle_cleaner.Update()
                        ins_output_domain_extract_triangle_cells = vtk.vtkExtractCellsByType()
                        ins_output_domain_extract_triangle_cells.SetInputData(ins_output_domain_triangle_cleaner.GetOutput())
                        ins_output_domain_extract_triangle_cells.AddCellType(5)
                        ins_output_domain_extract_triangle_cells.Update()
                        ins_output_domain_triangle_subdivision_filter = vtk.vtkLoopSubdivisionFilter()
                        ins_output_domain_triangle_subdivision_filter.SetInputData(ins_output_domain_extract_triangle_cells.GetOutput())
                        ins_output_domain_triangle_subdivision_filter.SetNumberOfSubdivisions(2)
                        ins_output_domain_triangle_subdivision_filter.Update()
                        ins_output_domain_triangle_normals_filter = vtk.vtkPolyDataNormals()
                        ins_output_domain_triangle_normals_filter.SetInputData(ins_output_domain_triangle_subdivision_filter.GetOutput())
                        ins_output_domain_triangle_normals_filter.AutoOrientNormalsOn()
                        ins_output_domain_triangle_normals_filter.ConsistencyOn()
                        ins_output_domain_triangle_normals_filter.SplittingOff()
                        ins_output_domain_triangle_normals_filter.Update()
                        ins_output_domain_triangle_smooth_filter = vtk.vtkWindowedSincPolyDataFilter()
                        ins_output_domain_triangle_smooth_filter.SetInputData(ins_output_domain_triangle_normals_filter.GetOutput())
                        ins_output_domain_triangle_smooth_filter.SetNumberOfIterations(30)
                        ins_output_domain_triangle_smooth_filter.SetPassBand(0.01)
                        ins_output_domain_triangle_smooth_filter.SetFeatureAngle(20)
                        ins_output_domain_triangle_smooth_filter.SetEdgeAngle(5)
                        ins_output_domain_triangle_smooth_filter.BoundarySmoothingOn()
                        ins_output_domain_triangle_smooth_filter.FeatureEdgeSmoothingOff()
                        ins_output_domain_triangle_smooth_filter.NonManifoldSmoothingOn()
                        ins_output_domain_triangle_smooth_filter.NormalizeCoordinatesOn()
                        ins_output_domain_triangle_smooth_filter.Update()

                        if thickness_value == 0.0:
                            ins_stl_writer = vtk.vtkSTLWriter()
                            ins_stl_writer.SetFileName(file_basename + '-' + instance_name + '.stl')
                            ins_stl_writer.SetInputData(ins_output_domain_triangle_smooth_filter.GetOutput())
                            ins_stl_writer.SetFileTypeToBinary()
                            ins_stl_writer.Write()
                        else:
                            ins_output_domain_extrude_filter = vtk.vtkLinearExtrusionFilter()
                            ins_output_domain_extrude_filter.SetInputData(ins_output_domain_triangle_smooth_filter.GetOutput())
                            ins_output_domain_extrude_filter.SetExtrusionTypeToNormalExtrusion()
                            if surface_location == 'bottom':
                                ins_output_domain_extrude_filter.SetScaleFactor(thickness_value)
                            else:
                                ins_output_domain_extrude_filter.SetScaleFactor(-thickness_value)
                            ins_output_domain_extrude_filter.CappingOn()
                            ins_output_domain_extrude_filter.Update()
                        
                            ins_stl_writer = vtk.vtkSTLWriter()
                            ins_stl_writer.SetFileName(file_basename + '-' + instance_name + '.stl')
                            ins_stl_writer.SetInputData(ins_output_domain_extrude_filter.GetOutput())
                            ins_stl_writer.SetFileTypeToBinary()
                            ins_stl_writer.Write()
                    else:
                        ins_output_ugrid = vtk.vtkUnstructuredGrid()
                        ins_output_ugrid.SetPoints(ins_whole_points)
                        for element_label in range(instance_elements_label_range[0],instance_elements_label_range[1]+1):
                            element_geometry_type_number = ins_assembly_include_elements_geometry_set[element_label-1]
                            element_include_nodes_label = ins_assembly_include_elements_set[element_label-1]
                            
                            if ins_output_frame_result_set[0,element_label-1] >= threshold_value:
                                ins_output_ugrid.InsertNextCell(trans_vtk_surface_geometry_dict[element_geometry_type_number],len(element_include_nodes_label),element_include_nodes_label-1)
                            else:
                                continue
                        if ins_output_ugrid.GetNumberOfCells() == 0:
                            print('Export Failed: The threshold value is too large!')
                            raise ValueError()
                        else:
                            pass

                        ins_other_points_cleaner = vtk.vtkCleanUnstructuredGrid()
                        ins_other_points_cleaner.SetInputData(ins_output_ugrid)
                        ins_other_points_cleaner.SetTolerance(1e-6)
                        ins_other_points_cleaner.RemovePointsWithoutCellsOn()
                        ins_other_points_cleaner.Update()

                        ins_output_domain_geometry_filter = vtk.vtkGeometryFilter()
                        ins_output_domain_geometry_filter.SetInputData(ins_other_points_cleaner.GetOutput())
                        ins_output_domain_geometry_filter.Update()

                        ins_output_domain_connectivity_filter = vtk.vtkPolyDataConnectivityFilter()
                        ins_output_domain_connectivity_filter.SetInputData(ins_output_domain_geometry_filter.GetOutput())
                        ins_output_domain_connectivity_filter.SetExtractionModeToLargestRegion()
                        ins_output_domain_connectivity_filter.Update()

                        if thickness_value == 0.0:
                            ins_stl_writer = vtk.vtkSTLWriter()
                            ins_stl_writer.SetFileName(file_basename + '-' + instance_name + '.stl')
                            ins_stl_writer.SetInputData(ins_output_domain_connectivity_filter.GetOutput())
                            ins_stl_writer.SetFileTypeToBinary()
                            ins_stl_writer.Write()
                        else:
                            ins_output_domain_normals_filter = vtk.vtkPolyDataNormals()
                            ins_output_domain_normals_filter.SetInputData(ins_output_domain_connectivity_filter.GetOutput())
                            ins_output_domain_normals_filter.AutoOrientNormalsOn()
                            ins_output_domain_normals_filter.ConsistencyOn()
                            ins_output_domain_normals_filter.SplittingOff()
                            ins_output_domain_normals_filter.Update()

                            ins_output_domain_extrude_filter = vtk.vtkLinearExtrusionFilter()
                            ins_output_domain_extrude_filter.SetInputData(ins_output_domain_normals_filter.GetOutput())
                            ins_output_domain_extrude_filter.SetExtrusionTypeToNormalExtrusion()
                            if surface_location == 'bottom':
                                ins_output_domain_extrude_filter.SetScaleFactor(thickness_value)
                            else:
                                ins_output_domain_extrude_filter.SetScaleFactor(-thickness_value)
                            ins_output_domain_extrude_filter.CappingOn()
                            ins_output_domain_extrude_filter.Update()
                        
                            ins_stl_writer = vtk.vtkSTLWriter()
                            ins_stl_writer.SetFileName(file_basename + '-' + instance_name + '.stl')
                            ins_stl_writer.SetInputData(ins_output_domain_extrude_filter.GetOutput())
                            ins_stl_writer.SetFileTypeToBinary()
                            ins_stl_writer.Write()
                elif len(instance_include_geometry_list) == 1 and 'solid' in instance_include_geometry_list:
                    ins_whole_points = vtk.vtkPoints()
                    ins_whole_points.SetNumberOfPoints(instance_nodes_label_range[1]-instance_nodes_label_range[0]+1)
                    for node_index,node_coordinates in enumerate(ins_assembly_include_nodes_set[instance_nodes_label_range[0]-1:instance_nodes_label_range[1]]):
                        ins_whole_points.SetPoint(node_index,node_coordinates)

                    if smooth_filter == 'On':
                        ins_whole_ugrid = vtk.vtkUnstructuredGrid()
                        ins_whole_ugrid.SetPoints(ins_whole_points)
                        ins_whole_result_array = vtk.vtkDoubleArray()
                        ins_whole_result_array.SetName('EX')
                        for element_label in range(instance_elements_label_range[0],instance_elements_label_range[1]+1):
                            element_geometry_type_number = ins_assembly_include_elements_geometry_set[element_label-1]
                            element_include_nodes_label = ins_assembly_include_elements_set[element_label-1]
                            
                            ins_whole_ugrid.InsertNextCell(trans_vtk_solid_geometry_dict[element_geometry_type_number],len(element_include_nodes_label),element_include_nodes_label-1)
                            ins_whole_result_array.InsertNextValue(ins_output_frame_result_set[0,element_label-1])
                        ins_whole_ugrid.GetCellData().AddArray(ins_whole_result_array)
                        ins_cells_data_to_points_transformer = vtk.vtkCellDataToPointData()
                        ins_cells_data_to_points_transformer.SetInputData(ins_whole_ugrid)
                        ins_cells_data_to_points_transformer.AddCellDataArray('EX')
                        ins_cells_data_to_points_transformer.SetPassCellData(0)
                        ins_cells_data_to_points_transformer.Update()
                        ins_cells_data_to_points_transformer.GetOutput().GetPointData().SetActiveScalars('EX')

                        ins_domain_contour_filter = vtk.vtkMarchingContourFilter()
                        ins_domain_contour_filter.SetInputData(ins_cells_data_to_points_transformer.GetOutput())
                        ins_domain_contour_filter.SetValue(0, threshold_value)
                        ins_domain_contour_filter.ComputeNormalsOn()
                        ins_domain_contour_filter.Update()
                        if ins_domain_contour_filter.GetOutput().GetNumberOfCells() == 0:
                            print('Export Failed: The threshold value is too large!')
                            raise ValueError()
                        else:
                            pass
                        ins_contour_surface_cleaner = vtk.vtkCleanPolyData()
                        ins_contour_surface_cleaner.SetInputData(ins_domain_contour_filter.GetOutput())
                        ins_contour_surface_cleaner.SetTolerance(1e-4)
                        ins_contour_surface_cleaner.PointMergingOn()
                        ins_contour_surface_cleaner.ConvertStripsToPolysOn()
                        ins_contour_surface_cleaner.ConvertPolysToLinesOn()
                        ins_contour_surface_cleaner.ConvertLinesToPointsOn()
                        ins_contour_surface_cleaner.Update()
                        ins_contour_surface_triangle_filter = vtk.vtkTriangleFilter()
                        ins_contour_surface_triangle_filter.SetInputData(ins_contour_surface_cleaner.GetOutput())
                        ins_contour_surface_triangle_filter.SetPassLines(0)
                        ins_contour_surface_triangle_filter.SetPassVerts(0)
                        ins_contour_surface_triangle_filter.Update()
                        ins_contour_surface_triangle_cleaner = vtk.vtkCleanPolyData()
                        ins_contour_surface_triangle_cleaner.SetInputData(ins_contour_surface_triangle_filter.GetOutput())
                        ins_contour_surface_triangle_cleaner.SetTolerance(1e-4)
                        ins_contour_surface_triangle_cleaner.PointMergingOn()
                        ins_contour_surface_triangle_cleaner.ConvertStripsToPolysOff()
                        ins_contour_surface_triangle_cleaner.ConvertPolysToLinesOff()
                        ins_contour_surface_triangle_cleaner.ConvertLinesToPointsOff()
                        ins_contour_surface_triangle_cleaner.Update()

                        ins_implicit_surface = vtk.vtkImplicitPolyDataDistance()
                        ins_implicit_surface.SetInput(ins_contour_surface_triangle_cleaner.GetOutput())
                        ins_whole_ugrid_clipper = vtk.vtkClipDataSet()
                        ins_whole_ugrid_clipper.SetInputData(ins_whole_ugrid)
                        ins_whole_ugrid_clipper.SetClipFunction(ins_implicit_surface)
                        ins_whole_ugrid_clipper.SetInsideOut(reserved_type_num)
                        ins_whole_ugrid_clipper.Update()

                        ins_output_domain_geometry_filter = vtk.vtkGeometryFilter()
                        ins_output_domain_geometry_filter.SetInputData(ins_whole_ugrid_clipper.GetOutput())
                        ins_output_domain_geometry_filter.Update()
                        ins_output_domain_connectivity_filter = vtk.vtkPolyDataConnectivityFilter()
                        ins_output_domain_connectivity_filter.SetInputData(ins_output_domain_geometry_filter.GetOutput())
                        ins_output_domain_connectivity_filter.SetExtractionModeToLargestRegion()
                        ins_output_domain_connectivity_filter.Update()
                        ins_output_domain_triangle_filter = vtk.vtkTriangleFilter()
                        ins_output_domain_triangle_filter.SetInputData(ins_output_domain_connectivity_filter.GetOutput())
                        ins_output_domain_triangle_filter.SetPassVerts(0)
                        ins_output_domain_triangle_filter.SetPassLines(0)
                        ins_output_domain_triangle_filter.Update()
                        ins_output_domain_triangle_cleaner = vtk.vtkCleanPolyData()
                        ins_output_domain_triangle_cleaner.SetInputData(ins_output_domain_triangle_filter.GetOutput())
                        ins_output_domain_triangle_cleaner.SetTolerance(1e-6)
                        ins_output_domain_triangle_cleaner.PointMergingOn()
                        ins_output_domain_triangle_cleaner.ConvertStripsToPolysOff()
                        ins_output_domain_triangle_cleaner.ConvertPolysToLinesOff()
                        ins_output_domain_triangle_cleaner.ConvertLinesToPointsOff()
                        ins_output_domain_triangle_cleaner.Update()
                        ins_output_domain_triangle_subdivision_filter = vtk.vtkLoopSubdivisionFilter()
                        ins_output_domain_triangle_subdivision_filter.SetInputData(ins_output_domain_triangle_cleaner.GetOutput())
                        ins_output_domain_triangle_subdivision_filter.SetNumberOfSubdivisions(2)
                        ins_output_domain_triangle_subdivision_filter.Update()
                        ins_output_domain_triangle_normals_filter = vtk.vtkPolyDataNormals()
                        ins_output_domain_triangle_normals_filter.SetInputData(ins_output_domain_triangle_subdivision_filter.GetOutput())
                        ins_output_domain_triangle_normals_filter.AutoOrientNormalsOn()
                        ins_output_domain_triangle_normals_filter.ConsistencyOn()
                        ins_output_domain_triangle_normals_filter.SplittingOff()
                        ins_output_domain_triangle_normals_filter.Update()
                        ins_output_domain_triangle_smooth_filter = vtk.vtkWindowedSincPolyDataFilter()
                        ins_output_domain_triangle_smooth_filter.SetInputData(ins_output_domain_triangle_normals_filter.GetOutput())
                        ins_output_domain_triangle_smooth_filter.SetNumberOfIterations(25)
                        ins_output_domain_triangle_smooth_filter.SetPassBand(0.05)
                        ins_output_domain_triangle_smooth_filter.SetFeatureAngle(20)
                        ins_output_domain_triangle_smooth_filter.SetEdgeAngle(10)
                        ins_output_domain_triangle_smooth_filter.BoundarySmoothingOn()
                        ins_output_domain_triangle_smooth_filter.FeatureEdgeSmoothingOff()
                        ins_output_domain_triangle_smooth_filter.NonManifoldSmoothingOn()
                        ins_output_domain_triangle_smooth_filter.NormalizeCoordinatesOn()
                        ins_output_domain_triangle_smooth_filter.Update()

                        ins_stl_writer = vtk.vtkSTLWriter()
                        ins_stl_writer.SetFileName(file_basename + '-' + instance_name + '.stl')
                        ins_stl_writer.SetInputData(ins_output_domain_triangle_smooth_filter.GetOutput())
                        ins_stl_writer.SetFileTypeToBinary()
                        ins_stl_writer.Write()
                    else:
                        ins_output_ugrid = vtk.vtkUnstructuredGrid()
                        ins_output_ugrid.SetPoints(ins_whole_points)
                        for element_label in range(instance_elements_label_range[0],instance_elements_label_range[1]+1):
                            element_geometry_type_number = ins_assembly_include_elements_geometry_set[element_label-1]
                            element_include_nodes_label = ins_assembly_include_elements_set[element_label-1]
                            
                            if ins_output_frame_result_set[0,element_label-1] >= threshold_value:
                                ins_output_ugrid.InsertNextCell(trans_vtk_solid_geometry_dict[element_geometry_type_number],len(element_include_nodes_label),element_include_nodes_label-1)
                            else:
                                continue
                        if ins_output_ugrid.GetNumberOfCells() == 0:
                            print('Export Failed: The threshold value is too large!')
                            raise ValueError()
                        else:
                            pass

                        ins_other_points_cleaner = vtk.vtkCleanUnstructuredGrid()
                        ins_other_points_cleaner.SetInputData(ins_output_ugrid)
                        ins_other_points_cleaner.SetTolerance(1e-6)
                        ins_other_points_cleaner.RemovePointsWithoutCellsOn()
                        ins_other_points_cleaner.Update()

                        ins_output_domain_geometry_filter = vtk.vtkGeometryFilter()
                        ins_output_domain_geometry_filter.SetInputData(ins_other_points_cleaner.GetOutput())
                        ins_output_domain_geometry_filter.Update()

                        ins_output_domain_connectivity_filter = vtk.vtkPolyDataConnectivityFilter()
                        ins_output_domain_connectivity_filter.SetInputData(ins_output_domain_geometry_filter.GetOutput())
                        ins_output_domain_connectivity_filter.SetExtractionModeToLargestRegion()
                        ins_output_domain_connectivity_filter.Update()

                        ins_stl_writer = vtk.vtkSTLWriter()
                        ins_stl_writer.SetFileName(file_basename + '-' + instance_name + '.stl')
                        ins_stl_writer.SetInputData(ins_output_domain_connectivity_filter.GetOutput())
                        ins_stl_writer.SetFileTypeToBinary()
                        ins_stl_writer.Write()
                elif len(instance_include_geometry_list) == 2 and 'surface' in instance_include_geometry_list and 'solid' in instance_include_geometry_list:
                    print("Export Error: Don't support model with the surface and solid")
                    raise ValueError()
                else:
                    pass
        except:
            ins_propress_label.setText('Error...')
        else:
            pass
        ins_propress_label.setText('Finished!')
    # endregion
