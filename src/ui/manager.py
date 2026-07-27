# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtCharts
import numpy
import h5py

from config import common

class P4SModelManager(QtWidgets.QWidget):
    
    def __init__(self, in_parent:object):
        super().__init__(parent=in_parent)
        self.setObjectName('model-manager')
        
        ins_model_manager_layout = QtWidgets.QVBoxLayout()
        ins_model_manager_layout.setContentsMargins(2,5,0,0)
        self.setLayout(ins_model_manager_layout)
        self.__initializeModelInformationLayout(ins_model_manager_layout)
        
        ins_model_tree_layout = QtWidgets.QStackedLayout()
        ins_model_tree_layout.setContentsMargins(0,0,0,0)
        ins_model_tree_layout.setObjectName('model-tree-stacked-layout')
        ins_model_manager_layout.addLayout(ins_model_tree_layout,1)
    def __initializeModelInformationLayout(self,in_model_manager_layout:object) -> None:
        ins_model_information_layout = QtWidgets.QHBoxLayout()
        ins_model_information_layout.setContentsMargins(0,0,0,0)
        
        ins_model_label = QtWidgets.QLabel('model:',self,alignment=QtCore.Qt.AlignCenter)
        ins_model_label.setObjectName('model-label')
        ins_model_label.setFixedSize(80,32)
        ins_model_information_layout.addWidget(ins_model_label,0)
        
        ins_models_box = QtWidgets.QComboBox(self)
        ins_models_box.setObjectName('models-box')
        ins_models_box.setMinimumWidth(190)
        ins_models_box.setFixedHeight(35)
        ins_models_box.currentTextChanged.connect(self.__slotChangeModel)
        ins_model_information_layout.addWidget(ins_models_box,1)
        
        ins_model_type = QtWidgets.QLabel(self,alignment=QtCore.Qt.AlignCenter,text="structure")
        ins_model_type.setObjectName('model-type-label')
        ins_model_type.setFixedSize(100,32)
        ins_model_information_layout.addWidget(ins_model_type,0)
        
        ins_model_dimension = QtWidgets.QLabel(self,alignment=QtCore.Qt.AlignCenter)
        ins_model_dimension.setObjectName('model-dimension-label')
        ins_model_dimension.setFixedSize(60,32)
        ins_model_information_layout.addWidget(ins_model_dimension,0)
        
        in_model_manager_layout.addLayout(ins_model_information_layout,0)
    # region
    def __slotChangeModel(self, in_model_name:str) -> None:
        ins_main_window = self.parent().parent().parent().parent()
        
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_visualization_toolbar.clearToolsState()

        ins_model_dimension = self.findChild(QtWidgets.QLabel,'model-dimension-label')
        if in_model_name == '':
            ins_model_dimension.setText('')
        else:
            model_dimension = ins_main_window.ins_project_database.getModelDimension(in_model_name)
            ins_model_dimension.setText(model_dimension)

            ins_model_tree_layout = self.findChild(QtWidgets.QStackedLayout,'model-tree-stacked-layout')
            ins_model_tree = self.findChild(QtWidgets.QTreeWidget,in_model_name)
            ins_model_tree_layout.setCurrentWidget(ins_model_tree)
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            for ins_model_visual_window in ins_models_mdi_area.subWindowList():
                ins_model_visual_window.close()
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,in_model_name)
            ins_model_visual_window.showMaximized()
    # endregion

    def getModelsNameList(self) -> list:
        ins_models_box = self.findChild(QtWidgets.QComboBox,'models-box')
        
        models_name = []
        for item_index in range(ins_models_box.count()):
            models_name.append(ins_models_box.itemText(item_index))
        
        return models_name
    def getCurrentModleName(self) -> str:
        ins_models_box = self.findChild(QtWidgets.QComboBox,'models-box')
        return ins_models_box.currentText()
    
    def ImportModelFromProject(self, in_model_name:str, in_model_dimension:str) -> None:
        ins_model_dimension = self.findChild(QtWidgets.QLabel,'model-dimension-label')
        ins_model_dimension.setText(in_model_dimension)
        
        ins_model_tree_layout = self.findChild(QtWidgets.QStackedLayout,'model-tree-stacked-layout')
        ins_model_tree = _ModelTree(self, in_model_name, in_model_dimension)
        ins_model_tree_layout.addWidget(ins_model_tree)
        ins_model_tree.importModelData()
        
        ins_models_box = self.findChild(QtWidgets.QComboBox,'models-box')
        ins_models_box.addItem(in_model_name)
        if ins_models_box.currentText() == in_model_name:
            pass
        else:
            ins_models_box.setCurrentText(in_model_name)

    def createModelManager(self, in_model_name:str, in_model_dimension:str) -> None:
        ins_model_dimension = self.findChild(QtWidgets.QLabel,'model-dimension-label')
        ins_model_dimension.setText(in_model_dimension)
        
        ins_model_tree_layout = self.findChild(QtWidgets.QStackedLayout,'model-tree-stacked-layout')
        ins_model_tree = _ModelTree(self,in_model_name, in_model_dimension)
        ins_model_tree_layout.addWidget(ins_model_tree)
        
        ins_models_box = self.findChild(QtWidgets.QComboBox,'models-box')
        ins_models_box.addItem(in_model_name)
        
        if ins_models_box.currentText() == in_model_name:
            pass
        else:
            ins_models_box.setCurrentText(in_model_name)
    def renameCurrentModel(self, in_new_model_name:str) -> None:
        ins_models_box = self.findChild(QtWidgets.QComboBox,'models-box')
        ins_models_box.currentTextChanged.disconnect(self.__slotChangeModel)
        ins_models_box.setItemText(ins_models_box.currentIndex(),in_new_model_name)
        ins_models_box.currentTextChanged.connect(self.__slotChangeModel)
        
        ins_model_tree_layout = self.findChild(QtWidgets.QStackedLayout,'model-tree-stacked-layout')
        ins_model_tree_layout.currentWidget().setObjectName(in_new_model_name)
    def removeCurrentModel(self, in_enable_model_change:bool=True) -> None:
        ins_models_box = self.findChild(QtWidgets.QComboBox,'models-box')
        
        if in_enable_model_change:
            pass
        else:
            ins_models_box.currentTextChanged.disconnect(self.__slotChangeModel)
        
        ins_models_box.removeItem(ins_models_box.currentIndex())
        
        ins_model_tree_layout = self.findChild(QtWidgets.QStackedLayout,'model-tree-stacked-layout')
        ins_model_tree = ins_model_tree_layout.currentWidget()
        ins_model_tree.setParent(None)
        ins_model_tree_layout.removeWidget(ins_model_tree)
        ins_model_tree.deleteLater()  
        
        if in_enable_model_change:
            pass
        else:
            ins_models_box.currentTextChanged.connect(self.__slotChangeModel)   

class _ModelTree(QtWidgets.QTreeWidget):
    def __init__(self,in_parent:object, in_model_name:str, in_model_dimension:str) -> None:
        super().__init__(parent=in_parent, columnCount=1)
        self.setObjectName(in_model_name)
        
        self.__model_dimension = in_model_dimension

        self.setHeaderHidden(True)
        # region
        ins_part_top_item = QtWidgets.QTreeWidgetItem(self)
        ins_part_top_item.setText(0,'Part')
        
        ins_property_top_item = QtWidgets.QTreeWidgetItem(self)
        ins_property_top_item.setText(0,'Property')
        ins_materials_second_item = QtWidgets.QTreeWidgetItem(ins_property_top_item)
        ins_materials_second_item.setText(0,'Materials')
        ins_materials_second_item.setData(1,0,'materials')
        ins_attributes_second_item = QtWidgets.QTreeWidgetItem(ins_property_top_item)
        ins_attributes_second_item.setText(0,'Attributes')
        ins_attributes_second_item.setData(1,0,'attributes')

        ins_assembly_top_item = QtWidgets.QTreeWidgetItem(self)
        ins_assembly_top_item.setIcon(0, QtGui.QIcon(":/image/images/ModulePosition.png"))
        ins_assembly_top_item.setText(0,"Assembly")
        ins_instances_second_item = QtWidgets.QTreeWidgetItem(ins_assembly_top_item)
        ins_instances_second_item.setText(0,'Instances')
        ins_instances_second_item.setData(1,0,'instances')
        ins_assembly_nodes_groups_second_item = QtWidgets.QTreeWidgetItem(ins_assembly_top_item)
        ins_assembly_nodes_groups_second_item.setText(0,'Nodes Groups')
        ins_assembly_nodes_groups_second_item.setData(1,0,'assembly-nodes-groups')
        ins_assembly_elements_groups_second_item = QtWidgets.QTreeWidgetItem(ins_assembly_top_item)
        ins_assembly_elements_groups_second_item.setText(0,"Elements Groups")
        ins_assembly_elements_groups_second_item.setData(1,0,'assembly-elements-groups')
        ins_assembly_coordinate_systems_second_item = QtWidgets.QTreeWidgetItem(ins_assembly_top_item)
        ins_assembly_coordinate_systems_second_item.setText(0,'Coordinate Systems')
        ins_assembly_coordinate_systems_second_item.setData(1,0,'assembly-coordinate-systems')
        
        ins_step_top_item = QtWidgets.QTreeWidgetItem(self)
        ins_step_top_item.setText(0,'Step')
        ins_initial_step_second_item = QtWidgets.QTreeWidgetItem(ins_step_top_item)
        ins_initial_step_second_item.setText(0,'Initial')
        ins_initial_step_second_item.setData(1,0,'initial-step')

        ins_output_top_item = QtWidgets.QTreeWidgetItem(self)
        ins_output_top_item.setText(0,'Output')

        ins_interaction_top_item = QtWidgets.QTreeWidgetItem(self)
        ins_interaction_top_item.setText(0,'Interaction')
        ins_contact_second_item = QtWidgets.QTreeWidgetItem(ins_interaction_top_item)
        ins_contact_second_item.setText(0,'Contact')
        ins_contact_second_item.setData(1,0,'contacts')
        ins_constraint_second_item = QtWidgets.QTreeWidgetItem(ins_interaction_top_item)
        ins_constraint_second_item.setText(0,'Constraint')
        ins_constraint_second_item.setData(1,0,'constraints')

        ins_bc_top_item = QtWidgets.QTreeWidgetItem(self)
        ins_bc_top_item.setText(0,'Boundary Condition')

        ins_other_top_item = QtWidgets.QTreeWidgetItem(self)
        ins_other_top_item.setText(0,'Other')
        ins_functions_second_item = QtWidgets.QTreeWidgetItem(ins_other_top_item)
        ins_functions_second_item.setText(0,'Functions')
        ins_functions_second_item.setData(1,0,'functions')
        # endregion

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__slotRightClickMenu)

    def __slotRightClickMenu(self, in_click_point:object) -> None:
        ins_clicked_item = self.itemAt(in_click_point)
        if ins_clicked_item is None:  
            return None
        else:   
            pass 
        
        ins_right_menu = QtWidgets.QMenu()
        ins_right_menu.deleteLater()

        clicked_item_text = ins_clicked_item.text(0)
        
        is_top_item = True if ins_clicked_item.parent() is None else False
        if is_top_item:
            if clicked_item_text == 'Part' and ins_clicked_item.childCount() != 0:
                ins_switch_module = ins_right_menu.addAction('switch module')
                ins_switch_module.triggered.connect(self.__slotSwitchModule)
                ins_right_menu.addSeparator()
            elif clicked_item_text == 'Assembly':
                ins_switch_module = ins_right_menu.addAction('switch module')
                ins_switch_module.triggered.connect(self.__slotSwitchModule)
                ins_right_menu.addSeparator()
            else:
                pass
            
            if clicked_item_text == 'Part':
                ins_import_mesh_parts = ins_right_menu.addAction('import mesh parts')
                ins_import_mesh_parts.triggered.connect(self.__slotImportMeshParts)
                
                ins_duplicate_part = ins_right_menu.addAction('duplicate part')
                ins_duplicate_part.triggered.connect(self.__slotDuplicatePart)

                ins_right_menu.addSeparator()
            elif clicked_item_text == 'Assembly':
                ins_assembly_axes_visibility = ins_right_menu.addAction('show/hide axes')
                ins_assembly_axes_visibility.triggered.connect(self.__slotSwitchAssemblyAxesVisibility)

                ins_right_menu.addSeparator()
            elif clicked_item_text == 'Step':
                ins_create_step = ins_right_menu.addAction('create step')
                ins_create_step.triggered.connect(self.__slotCreateStep)

                ins_right_menu.addSeparator()
            elif clicked_item_text == 'Output':
                ins_create_output = ins_right_menu.addAction('create output')
                ins_create_output.triggered.connect(self.__slotCreateOutput)
            elif clicked_item_text == 'Boundary Condition':
                ins_create_displacement_boundary = ins_right_menu.addAction('create displacement boundary')
                ins_create_displacement_boundary.triggered.connect(lambda: self.__slotCreateBoundaryCondition('displacement'))
                
                ins_right_menu.addSeparator()
                
                ins_create_concentrated_force = ins_right_menu.addAction('create concentrated force')
                ins_create_concentrated_force.triggered.connect(lambda: self.__slotCreateBoundaryCondition('concentrated force'))
                
                ins_create_moment = ins_right_menu.addAction('create moment')
                ins_create_moment.triggered.connect(lambda: self.__slotCreateBoundaryCondition('moment'))
                
                ins_right_menu.addSeparator()

                ins_show_boundary_conditions = ins_right_menu.addAction('show boundary conditions')
                ins_show_boundary_conditions.triggered.connect(self.__slotSwitchSetBoundaryConditionsVisibility)

                ins_right_menu.addSeparator()
            else: pass
            
            if clicked_item_text in ['Step','Output','Boundary Condition']:
                pass
            else:
                ins_expand_all_items = ins_right_menu.addAction('expand all')
                ins_expand_all_items.triggered.connect(lambda: self.__slotExpandAllItems(ins_clicked_item))
                ins_collapse_all_items = ins_right_menu.addAction('collapse all')
                ins_collapse_all_items.triggered.connect(lambda: self.__slotCollapseAllItems(ins_clicked_item))
            
            ins_right_menu.exec(QtGui.QCursor.pos())
            
            return None
        else:   pass
        
        clicked_item_type = ins_clicked_item.data(1,0)
        
        is_second_item = True if ins_clicked_item.parent().parent() is None else False
        if is_second_item:
            if clicked_item_type == 'part':
                ins_switch_part = ins_right_menu.addAction('switch part')
                ins_switch_part.triggered.connect(self.__slotSwitchPart)
                
                ins_right_menu.addSeparator()

                ins_rename_part = ins_right_menu.addAction('rename')
                ins_rename_part.triggered.connect(self.__slotRenamePart)

                ins_right_menu.addSeparator()

                ins_remove_part = ins_right_menu.addAction('remove')
                ins_remove_part.triggered.connect(self.__slotRemovePart)

                ins_right_menu.addSeparator()

                ins_part_axes_visibility = ins_right_menu.addAction('show/hide axes')
                ins_part_axes_visibility.triggered.connect(self.__slotSwitchPartAxesVisibility)
                
                ins_right_menu.addSeparator()

                ins_expand_all_items = ins_right_menu.addAction('expand all')
                ins_expand_all_items.triggered.connect(lambda: self.__slotExpandAllItems(ins_clicked_item))
                ins_collapse_all_items = ins_right_menu.addAction('collapse all')
                ins_collapse_all_items.triggered.connect(lambda: self.__slotCollapseAllItems(ins_clicked_item))
            elif clicked_item_type == 'materials':
                ins_create_material = ins_right_menu.addAction('create material')
                ins_create_material.triggered.connect(self.__slotCreateMaterial)
            elif clicked_item_type == 'attributes':
                ins_create_attribute = ins_right_menu.addAction('create attribute')
                ins_create_attribute.triggered.connect(self.__slotCreateAttribute)
            elif clicked_item_type == 'instances':
                ins_create_instances = ins_right_menu.addAction('create instances')
                ins_create_instances.triggered.connect(self.__slotCreateInstances)
            elif clicked_item_type == 'assembly-nodes-groups':
                ins_create_assembly_nodes_group_from_selection = ins_right_menu.addAction('create nodes group from selection')
                ins_create_assembly_nodes_group_from_selection.triggered.connect(self.__slotCreateAssemblyGroupFromSelection)
                
                ins_create_assembly_nodes_group_from_source_part = ins_right_menu.addAction('create group from part')
                ins_create_assembly_nodes_group_from_source_part.triggered.connect(self.__slotCreateAssemblyGroupFromSourcePart)
            elif clicked_item_type == 'assembly-elements-groups':
                ins_create_assembly_elements_group_from_selection = ins_right_menu.addAction('create elements group from selection')
                ins_create_assembly_elements_group_from_selection.triggered.connect(self.__slotCreateAssemblyGroupFromSelection)
                
                ins_create_assembly_elements_group_from_source_part = ins_right_menu.addAction('create group from part')
                ins_create_assembly_elements_group_from_source_part.triggered.connect(self.__slotCreateAssemblyGroupFromSourcePart)
            elif clicked_item_type == 'assembly-coordinate-systems':
                ins_create_assembly_coordinate_system = ins_right_menu.addAction('create coordinate system')
                ins_create_assembly_coordinate_system.triggered.connect(self.__slotCreateAssemblyCoordinateSystem)
                
                ins_switch_assembly_coordinate_systems_visibility = ins_right_menu.addAction('show/hide cordiante systems')
                ins_switch_assembly_coordinate_systems_visibility.triggered.connect(self.__slotSwitchAssemblyCoordinateSystemsVisibility)
            elif clicked_item_type == 'step':
                if clicked_item_text == 'Initial':   
                    pass
                else:
                    ins_rename_step = ins_right_menu.addAction('rename')
                    ins_rename_step.triggered.connect(self.__slotRenameStep)
                    
                    ins_edit_step = ins_right_menu.addAction('edit')
                    ins_edit_step.triggered.connect(self.__slotEditStep)

                    ins_right_menu.addSeparator()

                    ins_remove_step = ins_right_menu.addAction('remove')
                    ins_remove_step.triggered.connect(self.__slotRemoveStep)
            elif clicked_item_type == 'output':
                ins_rename_output = ins_right_menu.addAction('rename')
                ins_rename_output.triggered.connect(self.__slotRenameOutput)
                
                ins_edit_output = ins_right_menu.addAction('edit')
                ins_edit_output.triggered.connect(self.__slotEditOutput)
                
                ins_remove_output = ins_right_menu.addAction('remove')
                ins_remove_output.triggered.connect(self.__slotRemoveOutput)
            elif clicked_item_type == 'contacts':  pass
            elif clicked_item_type == 'constraints':  pass
            elif clicked_item_type == 'boundary-condition':
                ins_rename_boundary_condition = ins_right_menu.addAction('rename')
                ins_rename_boundary_condition.triggered.connect(self.__slotRenameBoundaryCondition)
                
                ins_edit_boundary_condition= ins_right_menu.addAction('edit')
                ins_edit_boundary_condition.triggered.connect(self.__slotEditBoundaryCondition)
                
                ins_remvoe_boundary_condition = ins_right_menu.addAction('remove')
                ins_remvoe_boundary_condition.triggered.connect(self.__slotRemoveBoundaryCondition)
            elif clicked_item_type == 'functions':
                ins_create_function = ins_right_menu.addAction('create function')
                ins_create_function.triggered.connect(self.__slotCreateFunction)
            else:   pass
            
            ins_right_menu.exec(QtGui.QCursor.pos())

            return None
        else:   pass
        
        is_third_item = True if ins_clicked_item.parent().parent().parent() is None else False
        if is_third_item:
            if clicked_item_type == 'part-nodes-groups':
                ins_create_part_nodes_group = ins_right_menu.addAction('create nodes group from selection')
                ins_create_part_nodes_group.triggered.connect(self.__slotCreatePartGroupFromSelection)
            elif clicked_item_type == 'part-elements-groups':
                ins_create_part_elements_group_from_selection = ins_right_menu.addAction('create elements group from selection')
                ins_create_part_elements_group_from_selection.triggered.connect(self.__slotCreatePartGroupFromSelection)
            elif clicked_item_type == 'part-property-assignments':
                ins_assign_part_property = ins_right_menu.addAction('assign property')
                ins_assign_part_property.triggered.connect(self.__slotAssignPartElementsProperty)
                
                ins_right_menu.addSeparator()
                
                ins_switch_part_property_visibility = ins_right_menu.addAction('show/hide property')
                ins_switch_part_property_visibility.triggered.connect(self.__slotSwitchPartPropertyVisibility)
                ins_switch_part_property_visibility.setEnabled(False)
            elif clicked_item_type == 'material':
                ins_rename_material = ins_right_menu.addAction('rename')
                ins_rename_material.triggered.connect(self.__slotRenameMaterial)
                
                ins_edit_material = ins_right_menu.addAction('edit')
                ins_edit_material.triggered.connect(self.__slotEditMaterial)
                
                ins_remvoe_material = ins_right_menu.addAction('remove')
                ins_remvoe_material.triggered.connect(self.__slotRemoveMaterial)
            elif clicked_item_type == 'attribute':
                ins_rename_attribute = ins_right_menu.addAction('rename')
                ins_rename_attribute.triggered.connect(self.__slotRenameAttribute)
                
                ins_edit_attribute = ins_right_menu.addAction('edit')
                ins_edit_attribute.triggered.connect(self.__slotEditAttribute)
                
                ins_remvoe_attribute = ins_right_menu.addAction('remove')
                ins_remvoe_attribute.triggered.connect(self.__slotRemoveAttribute)
            elif clicked_item_type == 'instance':
                ins_rename_instance = ins_right_menu.addAction('rename')
                ins_rename_instance.triggered.connect(self.__slotRenameInstance)
                
                ins_edit_instance_orientation = ins_right_menu.addAction('edit orientation')
                ins_edit_instance_orientation.triggered.connect(self.__slotEditInstanceOrientation)
                
                ins_remove_instance = ins_right_menu.addAction('remove')
                ins_remove_instance.triggered.connect(self.__slotRemoveInstance)
            elif clicked_item_type == 'assembly-nodes-group':
                ins_rename_assembly_nodes_group = ins_right_menu.addAction('rename')
                ins_rename_assembly_nodes_group.triggered.connect(self.__slotRenameAssemblyGroup)
                
                ins_edit_assembly_nodes_group = ins_right_menu.addAction('edit')
                ins_edit_assembly_nodes_group.triggered.connect(self.__slotEditAssemblyGroup)
                
                ins_remove_assembly_nodes_group = ins_right_menu.addAction('remove')
                ins_remove_assembly_nodes_group.triggered.connect(self.__slotRemoveAssemblyGroup)
            elif clicked_item_type == 'assembly-elements-group':
                ins_rename_assembly_elements_group = ins_right_menu.addAction('rename')
                ins_rename_assembly_elements_group.triggered.connect(self.__slotRenameAssemblyGroup)
                
                ins_edit_assembly_elements_group = ins_right_menu.addAction('edit')
                ins_edit_assembly_elements_group.triggered.connect(self.__slotEditAssemblyGroup)
                
                ins_remove_assembly_elements_group = ins_right_menu.addAction('remove')
                ins_remove_assembly_elements_group.triggered.connect(self.__slotRemoveAssemblyGroup)
            elif clicked_item_type == 'assembly-coordinate-system':
                ins_rename_assembly_coordinate_system = ins_right_menu.addAction('rename')
                ins_rename_assembly_coordinate_system.triggered.connect(self.__slotRenameAssemblyCoordinateSystem)
                
                ins_edit_assembly_coordinate_system = ins_right_menu.addAction('edit')
                ins_edit_assembly_coordinate_system.triggered.connect(self.__slotEditAssemblyCoordinateSystem)
                
                ins_remove_assembly_coordinate_system = ins_right_menu.addAction('remove')
                ins_remove_assembly_coordinate_system.triggered.connect(self.__slotRemoveAssemblyCoordinateSystem)
            elif clicked_item_type == 'function':
                ins_rename_function = ins_right_menu.addAction('rename')
                ins_rename_function.triggered.connect(self.__slotRenameFunction)
                
                ins_edit_function = ins_right_menu.addAction('edit')
                ins_edit_function.triggered.connect(self.__slotEditFunction)
                
                ins_remove_function = ins_right_menu.addAction('remove')
                ins_remove_function.triggered.connect(self.__slotRemoveFunction)
            else:   pass
            
            ins_right_menu.exec(QtGui.QCursor.pos())
            
            return None
        else:   pass
        
        is_fourth_item = True if ins_clicked_item.parent().parent().parent().parent() is None else False
        if is_fourth_item:
            if clicked_item_type == 'part-nodes-group':
                ins_rename_part_nodes_group = ins_right_menu.addAction('rename')
                ins_rename_part_nodes_group.triggered.connect(self.__slotRenamePartGroup)
                
                ins_edit_part_nodes_group = ins_right_menu.addAction('edit')
                ins_edit_part_nodes_group.triggered.connect(self.__slotEditPartGroup)
                
                ins_remove_part_nodes_group = ins_right_menu.addAction('remove')
                ins_remove_part_nodes_group.triggered.connect(self.__slotRemovePartGroup)
            elif clicked_item_type == 'part-elements-group':
                ins_rename_part_elements_group = ins_right_menu.addAction('rename')
                ins_rename_part_elements_group.triggered.connect(self.__slotRenamePartGroup)
                
                ins_edit_part_elements_group = ins_right_menu.addAction('edit')
                ins_edit_part_elements_group.triggered.connect(self.__slotEditPartGroup)
                
                ins_remove_part_elements_group = ins_right_menu.addAction('remove')
                ins_remove_part_elements_group.triggered.connect(self.__slotRemovePartGroup)
            elif clicked_item_type == 'part-property-assignment':
                ins_edit_part_property_assignment = ins_right_menu.addAction('edit')
                ins_edit_part_property_assignment.triggered.connect(self.__slotEditPartPropertyAssignments)
                
                ins_remove_part_property_assignment = ins_right_menu.addAction('remove')
                ins_remove_part_property_assignment.triggered.connect(self.__slotRemovePartPropertyAssignment)
            elif clicked_item_type == 'part-coordinate-system':
                pass
            else:   pass

            ins_right_menu.exec(QtGui.QCursor.pos())
            
            return None
        else:   pass
    
    def __slotExpandAllItems(self, in_expand_item:object) -> None:
        in_expand_item.setExpanded(True)
        for child_index in range(in_expand_item.childCount()):
            self.__slotExpandAllItems(in_expand_item.child(child_index))
    def __slotCollapseAllItems(self,in_collapse_item:object) -> None:
        in_collapse_item.setExpanded(False)
        for child_index in range(in_collapse_item.childCount()):  
            self.__slotCollapseAllItems(in_collapse_item.child(child_index))

    def importModelData(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_visualization_toolbar.clearToolsState()
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        model_information_dict = ins_main_window.ins_project_database.getModelInformation(self.objectName())
        
        ins_part_top_itme = self.topLevelItem(0)
        for part_name,part_info_dict in model_information_dict['part'].items():
            ins_part_item = QtWidgets.QTreeWidgetItem()
            ins_part_item.setText(0,part_name)
            ins_part_item.setData(1,0,'part')
                
            ins_part_nodes_groups_item = QtWidgets.QTreeWidgetItem()
            ins_part_nodes_groups_item.setText(0,'Nodes Groups')
            ins_part_nodes_groups_item.setData(1,0,'part-nodes-groups')
            for group_name in part_info_dict['nodes groups']:
                ins_part_nodes_group_item = QtWidgets.QTreeWidgetItem()
                ins_part_nodes_group_item.setText(0,group_name)
                ins_part_nodes_group_item.setData(1,0,'part-nodes-group')
                ins_part_nodes_groups_item.addChild(ins_part_nodes_group_item)
            
            ins_part_elements_groups_item = QtWidgets.QTreeWidgetItem()
            ins_part_elements_groups_item.setText(0,'Elements Groups')
            ins_part_elements_groups_item.setData(1,0,'part-elements-groups')
            for group_name in part_info_dict['elements groups']:
                ins_part_elements_group_item = QtWidgets.QTreeWidgetItem()
                ins_part_elements_group_item.setText(0,group_name)
                ins_part_elements_group_item.setData(1,0,'part-elements-group')
                ins_part_elements_groups_item.addChild(ins_part_elements_group_item)
            
            ins_part_property_assignments_item = QtWidgets.QTreeWidgetItem()
            ins_part_property_assignments_item.setText(0,'Property Assignmentts')
            ins_part_property_assignments_item.setData(1,0,'part-property-assignments')
            for group_name in part_info_dict['property assignments']:
                ins_propert_assignment_item = QtWidgets.QTreeWidgetItem()
                ins_propert_assignment_item.setText(0,group_name)
                ins_propert_assignment_item.setData(1,0,'part-property-assignment')
                ins_part_property_assignments_item.addChild(ins_propert_assignment_item)
            
            ins_part_item.addChildren([ins_part_nodes_groups_item,ins_part_elements_groups_item,ins_part_property_assignments_item])    
            
            ins_part_top_itme.addChild(ins_part_item)
            
            ins_model_visual_window.createPartViewport(ins_main_window.ins_project_database,part_name)
        
        ins_materials_item = self.topLevelItem(1).child(0)
        for material_name in model_information_dict["property"]["materials"]:
            ins_material_item = QtWidgets.QTreeWidgetItem()
            ins_material_item.setText(0,material_name)
            ins_material_item.setData(1,0,'material')
            ins_materials_item.addChild(ins_material_item)
        ins_attributes_item = self.topLevelItem(1).child(1)
        for attribute_name in model_information_dict["property"]["attributes"]:
            ins_attribute_item = QtWidgets.QTreeWidgetItem()
            ins_attribute_item.setText(0,attribute_name)
            ins_attribute_item.setData(1,0,'attribute')
            ins_attributes_item.addChild(ins_attribute_item)
        
        ins_instances_item = self.topLevelItem(2).child(0)
        for instance_name in model_information_dict['assembly']['instances']:
            ins_instance_item = QtWidgets.QTreeWidgetItem()
            ins_instance_item.setText(0,instance_name)
            ins_instance_item.setData(1,0,'instance')
            ins_instances_item.addChild(ins_instance_item)
            
            part_name = ins_main_window.ins_project_database.getInstanceSourcePart(self.objectName(),instance_name)
            instance_orientation_list = ins_main_window.ins_project_database.getInstanceOrientation(self.objectName(),instance_name)
            ins_model_visual_window.addInstanceToViewport(part_name,instance_name,instance_orientation_list)
        
        ins_assembly_nodes_groups_item = self.topLevelItem(2).child(1)
        for gorup_name in model_information_dict['assembly']['nodes groups']:
            ins_assembly_group_item = QtWidgets.QTreeWidgetItem()
            ins_assembly_group_item.setText(0,gorup_name)
            ins_assembly_group_item.setData(1,0,'assembly-nodes-group')
            ins_assembly_nodes_groups_item.addChild(ins_assembly_group_item)
        ins_assembly_elements_groups_item = self.topLevelItem(2).child(2)
        for gorup_name in model_information_dict['assembly']['elements groups']:
            ins_assembly_group_item = QtWidgets.QTreeWidgetItem()
            ins_assembly_group_item.setText(0,gorup_name)
            ins_assembly_group_item.setData(1,0,'assembly-elements-group')
            ins_assembly_elements_groups_item.addChild(ins_assembly_group_item)
        ins_assembly_coordinate_systems_item = self.topLevelItem(2).child(3)
        for coordinate_system_name in model_information_dict['assembly']['coordinate systems']:
            ins_assembly_coordiante_system_item = QtWidgets.QTreeWidgetItem()
            ins_assembly_coordiante_system_item.setText(0,coordinate_system_name)
            ins_assembly_coordiante_system_item.setData(1,0,'assembly-coordinate-system')
            ins_assembly_coordinate_systems_item.addChild(ins_assembly_coordiante_system_item)
        
        ins_step_top_item = self.topLevelItem(3)
        for step_name in model_information_dict['step']:
            ins_step_item = QtWidgets.QTreeWidgetItem()
            ins_step_item.setText(0,step_name)
            ins_step_item.setData(1,0,'step')
            ins_step_top_item.addChild(ins_step_item)
        
        ins_output_top_item = self.topLevelItem(4)
        for output_name in model_information_dict['output']:
            ins_output_item = QtWidgets.QTreeWidgetItem()
            ins_output_item.setText(0,output_name)
            ins_output_item.setData(1,0,'output')
            ins_output_top_item.addChild(ins_output_item)
        
        ins_boundary_condition_top_item = self.topLevelItem(6)
        for condition_name in model_information_dict['boundary condition']:
            ins_boundary_condition_item = QtWidgets.QTreeWidgetItem()
            ins_boundary_condition_item.setText(0,condition_name)
            ins_boundary_condition_item.setData(1,0,'boundary-condition')
            ins_boundary_condition_top_item.addChild(ins_boundary_condition_item)
        
        ins_functions_top_item = self.topLevelItem(7).child(0)
        for function_name in model_information_dict['other']['functions']:
            ins_function_item = QtWidgets.QTreeWidgetItem()
            ins_function_item.setText(0,function_name)
            ins_function_item.setData(1,0,'function')
            ins_functions_top_item.addChild(ins_function_item)
        
        self.setCurrentItem(self.topLevelItem(2))

    def __slotSwitchModule(self) -> None:
        ins_current_top_item = self.currentItem()
        
        for top_item_index in range(self.topLevelItemCount()):
            if self.topLevelItem(top_item_index).icon(0).isNull():   
                continue
            else:
                if self.topLevelItem(top_item_index) is ins_current_top_item:
                    return None
                else:
                    self.topLevelItem(top_item_index).setIcon(0,QtGui.QIcon())
                break
        ins_current_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_visualization_toolbar.clearToolsState()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_model_visual_window.switchModuleViewport(ins_current_top_item.text(0))

    def __slotSwitchPart(self) -> None:
        current_part_name = self.currentItem().text(0)
        
        ins_part_top_item = self.currentItem().parent()
        if ins_part_top_item.icon(0).isNull():
            self.topLevelItem(2).setIcon(0,QtGui.QIcon())
            ins_part_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
        else:
            pass
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_visualization_toolbar.clearToolsState()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_model_visual_window.switchPartViewport(current_part_name)
    def __slotImportMeshParts(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        
        full_mesh_file_name,file_type = QtWidgets.QFileDialog.getOpenFileName(self,'Import Mesh File',ins_main_window.work_path,common.P4SImportInfo.SUPPORTED_FILE_TYPE)
        if full_mesh_file_name == '':
            return None
        elif os.path.samefile(full_mesh_file_name,ins_main_window.ins_project_database.getFullProjectName()):
            QtWidgets.QMessageBox.critical(self,'Import Mesh Part Error',"The project file is already open!")
            return None
        else:   pass
        
        parts_name_list = []
        if file_type.lower() == '*.inp':
            try:
                with open(full_mesh_file_name,"r") as ins_inp_file:
                    file_model_dimension = None
                    while True:
                        line_content = ins_inp_file.readline()
                        
                        if '\n' in line_content:
                            pass
                        else:   break

                        line_content = line_content.strip().replace('\n','').replace(' ','')
                        if line_content == '*Node':
                            line_content = ins_inp_file.readline()
                            
                            if len(line_content.split(',')) == 3:
                                file_model_dimension = '2D'
                            elif len(line_content.split(',')) == 4:
                                file_model_dimension = '3D'
                            else:   
                                pass
                            
                            break
                        else:
                            continue
                        
                    if file_model_dimension == self.__model_dimension:
                        ins_inp_file.seek(0,0)
                        read_part_name = None
                        while True:
                            line_content = ins_inp_file.readline()
                            if '\n' in line_content:
                                pass
                            else:
                                break

                            line_content = line_content.strip().replace('\n','').replace(' ','')
                            keyword_contents = line_content.split(',',1)
                            if keyword_contents[0] == '*Part':
                                read_part_name = keyword_contents[1].split('=')[1]
                                parts_name_list.append(read_part_name)
                            elif keyword_contents[0] == '*Element':
                                if keyword_contents[1].split('=',1)[1] in common.P4SImportInfo.SUPPORTED_INP_ELEMENTS_BY_DIMENSION[self.__model_dimension]:
                                    pass
                                elif read_part_name in parts_name_list:
                                    parts_name_list.remove(read_part_name)
                                else:
                                    pass
                            elif keyword_contents[0] == '*Assembly':
                                break
                            else:
                                continue
                    else:
                        pass
            except:
                parts_name_list = []
            else:
                pass
        else:
            QtWidgets.QMessageBox.warning(self,'Import Mesh Part Waring','This file type is currently unsupported!')
            return None
        
        ins_import_mesh_parts_dialog = _ImportMeshPartsDialog(self,parts_name_list)
        ins_import_mesh_parts_dialog.show()
        if ins_import_mesh_parts_dialog.exec() == QtWidgets.QDialog.Accepted:
            selected_name_list = ins_import_mesh_parts_dialog.getSelectedPartsName()
            if selected_name_list == []:
                ins_import_mesh_parts_dialog.deleteLater()
                return None
            else:
                pass
            
            ins_part_top_item = self.topLevelItem(0)
            exist_parts_name_list = [ins_part_top_item.child(part_index).text(0) for part_index in range(ins_part_top_item.childCount())]
            if len(set(selected_name_list)&set(exist_parts_name_list)) == 0:
                import_parts_name_list = selected_name_list
            else:
                QtWidgets.QMessageBox.warning(self,'Import Mesh Part Waring','Existing parts cannot be re-imported!')
                import_parts_name_list = list(set(selected_name_list) - set(exist_parts_name_list))
            if import_parts_name_list == []:
                ins_import_mesh_parts_dialog.deleteLater()
                return None
            else:
                pass
            
            parts_include_groups_dict = ins_main_window.ins_project_database.importMeshParts(self.objectName(),full_mesh_file_name,import_parts_name_list)
            unimported_parts_list = list(set(import_parts_name_list)-set(parts_include_groups_dict.keys()))
            if len(unimported_parts_list) == 0:
                pass
            else:
                QtWidgets.QMessageBox.warning(self, 'Import Mesh Part Waring', f'Please check the label of nodes or elements in [{",".join(unimported_parts_list)}]')
            
            if parts_include_groups_dict == {}:
                ins_import_mesh_parts_dialog.deleteLater()
                return None
            else:
                pass
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
            for part_name in parts_include_groups_dict:
                ins_part_item = QtWidgets.QTreeWidgetItem()
                ins_part_item.setText(0,part_name)
                ins_part_item.setData(1,0,'part')
                
                ins_part_nodes_groups_item = QtWidgets.QTreeWidgetItem()
                ins_part_nodes_groups_item.setText(0,'Nodes Groups')
                ins_part_nodes_groups_item.setData(1,0,'part-nodes-groups')
                for group_name in parts_include_groups_dict[part_name]['nodes']:
                    ins_part_nodes_group_item = QtWidgets.QTreeWidgetItem()
                    ins_part_nodes_group_item.setText(0,group_name)
                    ins_part_nodes_group_item.setData(1,0,'part-nodes-group')
                    ins_part_nodes_groups_item.addChild(ins_part_nodes_group_item)
                
                ins_part_elements_groups_item = QtWidgets.QTreeWidgetItem()
                ins_part_elements_groups_item.setText(0,'Elements Groups')
                ins_part_elements_groups_item.setData(1,0,'part-elements-groups')
                for group_name in parts_include_groups_dict[part_name]['elements']:
                    ins_part_elements_group_item = QtWidgets.QTreeWidgetItem()
                    ins_part_elements_group_item.setText(0,group_name)
                    ins_part_elements_group_item.setData(1,0,'part-elements-group')
                    ins_part_elements_groups_item.addChild(ins_part_elements_group_item)
                
                ins_part_property_assignments_item = QtWidgets.QTreeWidgetItem()
                ins_part_property_assignments_item.setText(0,'Property Assignmentts')
                ins_part_property_assignments_item.setData(1,0,'part-property-assignments')

                ins_part_item.addChildren([ins_part_nodes_groups_item,ins_part_elements_groups_item,ins_part_property_assignments_item])
                
                ins_part_top_item.addChild(ins_part_item)
                
                ins_model_visual_window.createPartViewport(ins_main_window.ins_project_database,part_name)

            ins_part_top_item.setExpanded(True)
            
            self.__slotSwitchModule()
            ins_model_visual_window.switchPartViewport(part_name)

            ins_main_window.printMessage(f'Model "{self.objectName()}": Mesh parts [{",".join(list(parts_include_groups_dict.keys()))}] are successfully imported!')
        else:
            pass
        ins_import_mesh_parts_dialog.deleteLater()
    def __slotDuplicatePart(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        
        ins_part_top_item = self.topLevelItem(0)
        exist_parts_include_gourps_dict = {}
        for item_index in range(ins_part_top_item.childCount()):
            ins_part_item = ins_part_top_item.child(item_index)
            
            exist_parts_include_gourps_dict[ins_part_item.text(0)] = {}
            nodes_groups_item = ins_part_item.child(0)
            exist_parts_include_gourps_dict[ins_part_item.text(0)]['nodes'] = [nodes_groups_item.child(group_item_index).text(0) for group_item_index in range(nodes_groups_item.childCount())]
            elements_groups_item = ins_part_item.child(1)
            exist_parts_include_gourps_dict[ins_part_item.text(0)]['elements'] = [elements_groups_item.child(group_item_index).text(0) for group_item_index in range(elements_groups_item.childCount())]
        
        ins_duplicate_mesh_parts_dialog = _DuplicateMeshPartsDialog(self,list(exist_parts_include_gourps_dict.keys()))
        ins_duplicate_mesh_parts_dialog.show()
        if ins_duplicate_mesh_parts_dialog.exec() == QtWidgets.QDialog.Accepted:
            selected_name_list = ins_duplicate_mesh_parts_dialog.getSelectedPartsName()
            
            if selected_name_list == []:
                ins_duplicate_mesh_parts_dialog.deleteLater()
                return None
            else:
                pass
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
            for part_name in selected_name_list:
                duplicated_part_number = 1
                while True:
                    duplicated_part_name = part_name + '_copy' + str(duplicated_part_number)
                    
                    if duplicated_part_name in list(exist_parts_include_gourps_dict.keys()):
                        duplicated_part_number += 1
                        continue
                    else:
                        break
                
                ins_main_window.ins_project_database.duplicateMeshPart(self.objectName(),part_name,duplicated_part_name)            
            
                ins_part_item = QtWidgets.QTreeWidgetItem()
                ins_part_item.setText(0,duplicated_part_name)
                ins_part_item.setData(1,0,'part')
                
                ins_part_nodes_groups_item = QtWidgets.QTreeWidgetItem()
                ins_part_nodes_groups_item.setText(0,'Nodes Groups')
                ins_part_nodes_groups_item.setData(1,0,'part-nodes-groups')
                for group_name in exist_parts_include_gourps_dict[part_name]['nodes']:
                    ins_part_nodes_group_item = QtWidgets.QTreeWidgetItem()
                    ins_part_nodes_group_item.setText(0,group_name)
                    ins_part_nodes_group_item.setData(1,0,'part-nodes-group')
                    ins_part_nodes_groups_item.addChild(ins_part_nodes_group_item)
                ins_part_elements_groups_item = QtWidgets.QTreeWidgetItem()
                ins_part_elements_groups_item.setText(0,'Elements Groups')
                ins_part_elements_groups_item.setData(1,0,'part-elements-groups')
                for group_name in exist_parts_include_gourps_dict[part_name]['elements']:
                    ins_part_elements_group_item = QtWidgets.QTreeWidgetItem()
                    ins_part_elements_group_item.setText(0,group_name)
                    ins_part_elements_group_item.setData(1,0,'part-elements-group')
                    ins_part_elements_groups_item.addChild(ins_part_elements_group_item)
                
                ins_part_property_assignments_item = QtWidgets.QTreeWidgetItem()
                ins_part_property_assignments_item.setText(0,'Property Assignmentts')
                ins_part_property_assignments_item.setData(1,0,'part-property-assignments')
                
                ins_part_item.addChildren([ins_part_nodes_groups_item,ins_part_elements_groups_item,ins_part_property_assignments_item])    

                ins_part_top_item.addChild(ins_part_item)
                ins_part_item.setExpanded(True)
                
                ins_model_visual_window.createPartViewport(ins_main_window.ins_project_database,duplicated_part_name)

            ins_part_top_item.setExpanded(True)
            
            self.__slotSwitchModule()
            ins_model_visual_window.switchPartViewport(duplicated_part_name)

            if len(selected_name_list) == 1:
                ins_main_window.printMessage(f'Model "{self.objectName()}": Mesh part "{selected_name_list[0]}" is successfully duplicated!')
            else:
                ins_main_window.printMessage(f'Model "{self.objectName()}": Mesh parts "{",".join(selected_name_list)}" are successfully duplicated!')
        else:
            pass
        ins_duplicate_mesh_parts_dialog.deleteLater()
    def __slotRenamePart(self) -> None:
        ins_part_top_item = self.topLevelItem(0)
        exist_parts_name_list = [ins_part_top_item.child(item_index).text(0) for item_index in range(ins_part_top_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_parts_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_part_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            old_part_name = self.currentItem().text(0)
            ins_main_window.ins_project_database.renamePart(self.objectName(),old_part_name,new_part_name)
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
            ins_model_visual_window.renamePartViewport(old_part_name,new_part_name)
            
            self.currentItem().setText(0,new_part_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Part "{old_part_name}" has been renamed to "{new_part_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotRemovePart(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Remove Part',f'Associated instances,groups,outputs and boundary\n conditions that completely depend on this part will\n also be removed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_part_item = self.currentItem()
        remove_part_name = ins_part_item.text(0)
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        current_shown_part = ins_model_visual_window.getCurrentPartName()
        if current_shown_part == remove_part_name:
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
        else:
            pass
        
        ins_part_top_item = self.topLevelItem(0)
        if ins_part_top_item.icon(0).isNull():
            pass
        else:
            exist_parts_name_list = [ins_part_top_item.child(item_index).text(0) for item_index in range(ins_part_top_item.childCount())]
            exist_parts_name_list.remove(remove_part_name)
        
            if exist_parts_name_list == []:
                ins_part_top_item.setIcon(0,QtGui.QIcon())
                self.topLevelItem(2).setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
                ins_model_visual_window.switchModuleViewport('Assembly')
            else:
                ins_model_visual_window.switchPartViewport(exist_parts_name_list[-1])

            del exist_parts_name_list
        
        ins_model_visual_window.removePartViewport(remove_part_name)
        ins_part_top_item.removeChild(ins_part_item)
        del ins_part_item
        
        part_association_info_dict = ins_main_window.ins_project_database.removePart(self.objectName(),remove_part_name)
        
        ins_instances_item = self.topLevelItem(2).child(0)
        for instance_name in part_association_info_dict['instances']:
            ins_model_visual_window.removeInstanceOfAssemblyViewport(instance_name)

            for item_index in range(ins_instances_item.childCount()):
                ins_instance_item = ins_instances_item.child(item_index)
                if ins_instance_item.text(0) == instance_name:
                    break
                else:
                    continue
            ins_instances_item.removeChild(ins_instance_item)
            del ins_instance_item
        
        ins_assembly_nodes_groups_item = self.topLevelItem(2).child(1)
        for group_name in part_association_info_dict['agroups']['nodes']:
            for item_index in range(ins_assembly_nodes_groups_item.childCount()):
                ins_assembly_nodes_group_item = ins_assembly_nodes_groups_item.child(item_index)
                if ins_assembly_nodes_group_item.text(0) == group_name:
                    break
                else:
                    continue
            ins_assembly_nodes_groups_item.removeChild(ins_assembly_nodes_group_item)
            del ins_assembly_nodes_group_item
        ins_assembly_elements_groups_item = self.topLevelItem(2).child(2)
        for group_name in part_association_info_dict['agroups']['elements']:
            for item_index in range(ins_assembly_elements_groups_item.childCount()):
                ins_assembly_elements_group_item = ins_assembly_elements_groups_item.child(item_index)
                if ins_assembly_elements_group_item.text(0) == group_name:
                    break
                else:
                    continue
            ins_assembly_elements_groups_item.removeChild(ins_assembly_elements_group_item)
            del ins_assembly_elements_group_item
        
        ins_outputs_item = self.topLevelItem(4)
        for output_name in part_association_info_dict['outputs']:
            for item_index in range(ins_outputs_item.childCount()):
                ins_output_item = ins_outputs_item.child(item_index)
                if ins_output_item.text(0) == output_name:
                    break
                else:
                    continue
            ins_outputs_item.removeChild(ins_output_item)
            del ins_output_item
        
        ins_conditions_item = self.topLevelItem(6)
        for condition_name in part_association_info_dict['conditions']:
            for item_index in range(ins_conditions_item.childCount()):
                ins_condition_item = ins_conditions_item.child(item_index)
                if ins_condition_item.text(0) == condition_name:
                    break
                else:
                    continue
            ins_conditions_item.removeChild(ins_condition_item)
            del ins_condition_item
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Part "{remove_part_name}" successfully removed!')
    def __slotSwitchPartAxesVisibility(self) -> None:
        part_name = self.currentItem().text(0)
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_model_visual_window.switchPartViewportAxesVisibility(part_name)

    def __slotCreatePartGroupFromSelection(self) -> None:
        ins_part_groups_item = self.currentItem()
        if ins_part_groups_item.text(0) == 'Nodes Groups':
            group_type = 'node'
        elif ins_part_groups_item.text(0) == 'Elements Groups':
            group_type = 'element'
        else:
            pass
        
        ins_part_item = ins_part_groups_item.parent()
        part_name = ins_part_item.text(0)

        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        if self.topLevelItem(0).icon(0).isNull():
            self.topLevelItem(2).setIcon(0,QtGui.QIcon())
            self.topLevelItem(0).setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))

            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchPartViewport(part_name)
        else:
            pass
        if part_name != ins_model_visual_window.getCurrentPartName():
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchPartViewport(part_name)
        else:
            pass
        
        labels_selection_dict = ins_model_visual_window.getSelectionFromViewport()
        if labels_selection_dict == {}:
            QtWidgets.QMessageBox.warning(self,'Create Part Group Waring',f'None selected {group_type}!')
            return None
        else:
            part_labels_list = labels_selection_dict[part_name]
            labels_selection_dict = {}
            del labels_selection_dict
    
        exist_groups_name_list = [ins_part_groups_item.child(item_index).text(0) for item_index in range(ins_part_groups_item.childCount())]
        ins_part_group_dialog = _CreateGroupFromSelectionDialog(self,'Part',exist_groups_name_list)
        ins_part_group_dialog.show()
        if ins_part_group_dialog.exec() == QtWidgets.QDialog.Accepted:
            part_group_name = ins_part_group_dialog.getGroupName()
            
            ins_main_window.ins_project_database.createPartGroupFromSelection(self.objectName(),part_name,group_type,part_group_name,part_labels_list)

            ins_part_group_item = QtWidgets.QTreeWidgetItem()
            ins_part_group_item.setText(0,part_group_name)
            ins_part_group_item.setData(1,0,f'part-{group_type}s-group')
            
            ins_part_groups_item.addChild(ins_part_group_item)
            ins_part_groups_item.setExpanded(True)

            ins_main_window.printMessage(f'Model "{self.objectName()}": The {group_type}s group of part "{part_name}" successfully created!')
        else:
            pass
        ins_part_group_dialog.deleteLater()
    def __slotRenamePartGroup(self) -> None:
        ins_part_group_item = self.currentItem()
        
        ins_part_groups_item = ins_part_group_item.parent()
        if ins_part_groups_item.text(0) == 'Nodes Groups':
            group_type = 'node'
        elif ins_part_groups_item.text(0) == 'Elements Groups':
            group_type = 'element'
        else:
            pass
        
        exist_part_groups_name_list = [ins_part_groups_item.child(item_index).text(0) for item_index in range(ins_part_groups_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_part_groups_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_part_group_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            part_name = ins_part_groups_item.parent().text(0)
            old_part_group_name = ins_part_group_item.text(0)
            ins_main_window.ins_project_database.renamePartGroup(self.objectName(),part_name,group_type,old_part_group_name,new_part_group_name)
            
            ins_part_group_item.setText(0,new_part_group_name)
            
            if group_type == 'element':
                ins_part_property_assignments_item = ins_part_groups_item.parent().child(3)
                for item_index in range(ins_part_property_assignments_item.childCount()):
                    if ins_part_property_assignments_item.child(item_index).text(0) == old_part_group_name:
                        ins_property_assignment_item = ins_part_property_assignments_item.child(item_index)
                        ins_property_assignment_item.setText(0,new_part_group_name)
                        break
                    else:
                        continue
            else:
                pass
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Part "{part_name}" {group_type}s group "{old_part_group_name}" has been renamed to "{new_part_group_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditPartGroup(self) -> None:
        ins_part_group_item = self.currentItem()
        
        ins_part_groups_item = ins_part_group_item.parent()
        if ins_part_groups_item.text(0) == 'Nodes Groups':
            group_type = 'node'
        elif ins_part_groups_item.text(0) == 'Elements Groups':
            group_type = 'element'
        else:
            pass
        
        ins_part_item = ins_part_groups_item.parent()
        part_name = ins_part_item.text(0)

        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        if ins_part_item.parent().icon(0).isNull():
            self.topLevelItem(2).setIcon(0,QtGui.QIcon())
            self.topLevelItem(0).setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_model_visual_window.switchPartViewport(part_name)
        else:
            pass
        if part_name != ins_model_visual_window.getCurrentPartName():
            ins_model_visual_window.switchPartViewport(part_name)
        else:
            pass
        
        ins_main_toolbar = ins_main_window.findChild(QtCore.QObject,'main-toolbar')
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_manager_dock_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget')
        ins_main_menubar = ins_main_window.menuBar()
        
        ins_main_toolbar.setToolsEnabled(False)
        ins_visualization_toolbar.clearToolsState()
        ins_visualization_toolbar.setSelectionState(group_type,True)
        ins_manager_dock_widget.setEnabled(False)
        ins_main_menubar.setEnabled(False)
        
        part_group_name = ins_part_group_item.text(0)
        ins_model_visual_window.showPartViewportGroup(ins_main_window.ins_project_database,part_name,group_type,part_group_name)
        
        ins_edit_group_dialog = _EditGroupDialog(self, group_type, 'editing part group ...')
        ins_edit_group_dialog.show()
        if ins_edit_group_dialog.exec() == QtWidgets.QDialog.Accepted:
            labels_selection_dict = ins_model_visual_window.getSelectionFromViewport()
            if labels_selection_dict == {}:
                QtWidgets.QMessageBox.warning(self,'Edit Part Group Waring',f'None selected {group_type}!')
            else:
                part_labels_list = labels_selection_dict[part_name]
                labels_selection_dict = {}
                del labels_selection_dict

                assignment_state = ins_main_window.ins_project_database.editPartGroupFromSelection(self.objectName(),part_name,group_type,part_group_name,part_labels_list)   
                if assignment_state:
                    pass
                else:
                    QtWidgets.QMessageBox.critical(self,'Edit Part Group Error','The elements being added already have a property/orientation assignment. Duplicate assignment is not permitted!')
        else:
            pass
        ins_edit_group_dialog.deleteLater()
        
        ins_main_toolbar.setToolsEnabled(True)
        ins_visualization_toolbar.setSelectionState(group_type,False)
        ins_manager_dock_widget.setEnabled(True)
        ins_main_menubar.setEnabled(True)
    def __slotRemovePartGroup(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Remove Part Group',f'Associated assignments that depend on this group will also be removed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_part_group_item = self.currentItem()
        
        ins_part_groups_item = ins_part_group_item.parent()
        if ins_part_groups_item.text(0) == 'Nodes Groups':
            group_type = 'node'
        elif ins_part_groups_item.text(0) == 'Elements Groups':
            group_type = 'element'
        else:
            pass
        
        ins_part_item = ins_part_groups_item.parent()
        part_name = ins_part_item.text(0)
        part_group_name = ins_part_group_item.text(0)
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_main_window.ins_project_database.removePartGroup(self.objectName(),part_name,group_type,part_group_name)
        
        ins_part_groups_item.removeChild(ins_part_group_item)
        del ins_part_group_item
        
        if group_type == 'element':
            ins_part_property_assignments_item = ins_part_item.child(3)
            for item_index in range(ins_part_property_assignments_item.childCount()):
                if ins_part_property_assignments_item.child(item_index).text(0) == part_group_name:
                    ins_property_assignment_item = ins_part_property_assignments_item.child(item_index)
                    ins_part_property_assignments_item.removeChild(ins_property_assignment_item)
                    del ins_property_assignment_item
                    break
                else:
                    continue
        else:
            pass
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": {group_type.capitalize()}s group "{part_group_name}" of part "{part_name}" successfully removed!')

    def __slotAssignPartElementsProperty(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        
        ins_part_property_assignments_item = self.currentItem()
        ins_part_item = ins_part_property_assignments_item.parent()
        part_name = ins_part_item.text(0)
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        if ins_part_item.parent().icon(0).isNull():
            self.topLevelItem(2).setIcon(0,QtGui.QIcon())
            self.topLevelItem(0).setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_model_visual_window.switchPartViewport(part_name)
        else:
            pass
        if part_name != ins_model_visual_window.getCurrentPartName():
            ins_model_visual_window.switchPartViewport(part_name)
        else:
            pass
        
        part_elements_groups_have_property_dict = ins_main_window.ins_project_database.getPartElementGroupsHaveProperty(self.objectName(),part_name)
        part_elements_groups_include_geometry_dict = ins_main_window.ins_project_database.getPartElementGroupsIncludeGeometry(self.objectName(),part_name)
        attributes_by_type_dict = ins_main_window.ins_project_database.getAttributesByType(self.objectName())
        ins_materials_item = self.topLevelItem(1).child(0)
        materials_name_list = [ins_materials_item.child(item_index).text(0) for item_index in range(ins_materials_item.childCount())]

        ins_assign_part_property_dialog = _AssignPartElementsProperty(self,self.__model_dimension,part_elements_groups_have_property_dict,part_elements_groups_include_geometry_dict,attributes_by_type_dict,materials_name_list)
        ins_assign_part_property_dialog.show()
        if ins_assign_part_property_dialog.exec() == QtWidgets.QDialog.Accepted:
            property_assignments_info_dict = ins_assign_part_property_dialog.getPropertyAssignments()
            
            for geometry_type,property_params in property_assignments_info_dict['property'].items():
                if '' in property_params:
                    QtWidgets.QMessageBox.critical(self,'Assign Property Error',f'The paremeters of {geometry_type} elemnets are missing in group "{property_assignments_info_dict['group']}"!')
                    ins_assign_part_property_dialog.deleteLater()
                    return None
                else:
                    continue
            
            ins_main_window.ins_project_database.assignPartElementsPropertyByGeometry(self.objectName(),part_name,property_assignments_info_dict)
            
            ins_propert_assignment_item = QtWidgets.QTreeWidgetItem()
            ins_propert_assignment_item.setText(0,property_assignments_info_dict['group'])
            ins_propert_assignment_item.setData(1,0,'part-property-assignment')
            ins_part_property_assignments_item.addChild(ins_propert_assignment_item)
            
            ins_part_property_assignments_item.setExpanded(True)
        else:
            pass
        ins_assign_part_property_dialog.deleteLater() 
    def __slotSwitchPartPropertyVisibility(self) -> None:
        pass
    def __slotEditPartPropertyAssignments(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        
        ins_part_property_assignment_item = self.currentItem()
        assigned_part_group_name = ins_part_property_assignment_item.text(0)
        
        ins_part_item = ins_part_property_assignment_item.parent().parent()
        part_name = ins_part_item.text(0)
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        if self.topLevelItem(0).icon(0).isNull():
            self.topLevelItem(2).setIcon(0,QtGui.QIcon())
            self.topLevelItem(0).setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_model_visual_window.switchPartViewport(part_name)
        else:
            pass
        if part_name != ins_model_visual_window.getCurrentPartName():
            ins_model_visual_window.switchPartViewport(part_name)
        else:
            pass
        
        part_elements_groups_have_property_dict = ins_main_window.ins_project_database.getPartElementGroupsHaveProperty(self.objectName(),part_name)
        part_elements_groups_have_property_dict[assigned_part_group_name] = False
        part_elements_groups_include_geometry_dict = ins_main_window.ins_project_database.getPartElementGroupsIncludeGeometry(self.objectName(),part_name)
        attributes_by_type_dict = ins_main_window.ins_project_database.getAttributesByType(self.objectName())
        ins_materials_item = self.topLevelItem(1).child(0)
        materials_name_list = [ins_materials_item.child(item_index).text(0) for item_index in range(ins_materials_item.childCount())]
        
        ins_assign_part_property_dialog = _AssignPartElementsProperty(self,self.__model_dimension,part_elements_groups_have_property_dict,part_elements_groups_include_geometry_dict,attributes_by_type_dict,materials_name_list)
        group_include_property_assignments_dict_by_geometry = ins_main_window.ins_project_database.getPartElementsGroupPropertyAssignments(self.objectName(),part_name,assigned_part_group_name,part_elements_groups_include_geometry_dict[assigned_part_group_name])
        ins_assign_part_property_dialog.setPropertyAssignments(assigned_part_group_name,group_include_property_assignments_dict_by_geometry)
        ins_assign_part_property_dialog.show()
        if ins_assign_part_property_dialog.exec() == QtWidgets.QDialog.Accepted:
            property_assignments_info_dict = ins_assign_part_property_dialog.getPropertyAssignments()
            
            for geometry_type in group_include_property_assignments_dict_by_geometry:
                if property_assignments_info_dict['property'][geometry_type] == group_include_property_assignments_dict_by_geometry[geometry_type]:
                    property_assignments_info_dict['property'][geometry_type] = None
                    del property_assignments_info_dict['property'][geometry_type]
                else:
                    continue
            
            if property_assignments_info_dict['property'] == {}:
                pass
            else:
                ins_main_window.ins_project_database.assignPartElementsPropertyByGeometry(self.objectName(),part_name,property_assignments_info_dict)
        else:
            pass
        ins_assign_part_property_dialog.deleteLater()
    def __slotRemovePartPropertyAssignment(self) -> None:
        ins_property_assignment_item = self.currentItem()
        assigned_part_group_name = ins_property_assignment_item.text(0)
        
        ins_part_property_assignments_item = ins_property_assignment_item.parent()
        
        ins_part_item = ins_part_property_assignments_item.parent()
        part_name = ins_part_item.text(0)
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_main_window.ins_project_database.removePartElementsPropertyAssignments(self.objectName(),part_name,assigned_part_group_name)
        
        ins_part_property_assignments_item.removeChild(ins_property_assignment_item)
        del ins_property_assignment_item

    def __slotCreateMaterial(self) -> None:
        ins_materials_item = self.currentItem()
        exist_materials_name_list = [ins_materials_item.child(material_index).text(0) for material_index in range(ins_materials_item.childCount())]

        ins_material_dialog = _CreateMaterialDialog(self,exist_materials_name_list)
        ins_material_dialog.show()
        if ins_material_dialog.exec() == QtWidgets.QDialog.Accepted:
            material_information_dict = ins_material_dialog.getMaterialInformation()

            if len(material_information_dict) == 1:
                QtWidgets.QMessageBox.critical(self,'Create Material Error',"Material is empty!")
                ins_material_dialog.deleteLater()
                return None
            else:
                pass
            
            if 'elasticity' in material_information_dict:
                elasticity_type = material_information_dict['elasticity']['type']
                
                if elasticity_type == 'elastic':
                    constitutive_model = material_information_dict['elasticity']['constitutive model']
                    constitutive_parameters = material_information_dict['elasticity']['constitutive parameters']
                    
                    if constitutive_model == 'isotropic':
                        E = constitutive_parameters[0]
                        u = constitutive_parameters[1]
                        
                        if E == 0.0:
                            QtWidgets.QMessageBox.critical(self,'Create Material Error',"Young's modulus should be greater than zero!")
                            ins_material_dialog.deleteLater()
                            return None
                        else:   pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
            
            if 'density' in material_information_dict:
                pass
            else:
                pass
            if 'plasticity' in material_information_dict:
                pass
            else:
                pass
            if 'strength' in material_information_dict:
                pass
            else:
                pass
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            ins_main_window.ins_project_database.createMaterial(self.objectName(),material_information_dict)

            ins_material_item = QtWidgets.QTreeWidgetItem()
            ins_material_item.setText(0,material_information_dict['name'])
            ins_material_item.setData(1,0,'material')
            ins_materials_item.addChild(ins_material_item)
            ins_materials_item.setExpanded(True)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Material "{material_information_dict['name']}" successfully created!')
        else:
            pass
        ins_material_dialog.deleteLater()
    def __slotRenameMaterial(self) -> None:
        ins_material_item = self.currentItem()
        
        ins_materials_item = ins_material_item.parent()
        
        exist_materials_name_list = [ins_materials_item.child(item_index).text(0) for item_index in range(ins_materials_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_materials_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_material_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            old_material_name = ins_material_item.text(0)
            ins_main_window.ins_project_database.renameMaterial(self.objectName(),old_material_name,new_material_name)
            
            ins_material_item.setText(0,new_material_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Matreial "{old_material_name}" has been renamed to "{new_material_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditMaterial(self) -> None:
        ins_material_item = self.currentItem()
        material_name = ins_material_item.text(0)

        ins_main_window = self.parent().parent().parent().parent().parent()

        ins_edit_material_dialog = _CreateMaterialDialog(self,[])
        material_information_dict = ins_main_window.ins_project_database.getMaterialInformation(self.objectName(),material_name)
        ins_edit_material_dialog.setMaterialInformation(material_name,material_information_dict)
        ins_edit_material_dialog.show()
        if ins_edit_material_dialog.exec() == QtWidgets.QDialog.Accepted:
            edit_material_information_dict = ins_edit_material_dialog.getMaterialInformation()
        
            if len(edit_material_information_dict) == 1:
                QtWidgets.QMessageBox.critical(self,'Edit Material Error',"Material is empty!")
                ins_edit_material_dialog.deleteLater()
                return None
            else:
                pass
        
            if 'elasticity' in edit_material_information_dict:
                elasticity_type = edit_material_information_dict['elasticity']['type']
                
                if elasticity_type == 'elastic':
                    constitutive_model = edit_material_information_dict['elasticity']['constitutive model']
                    constitutive_parameters = edit_material_information_dict['elasticity']['constitutive parameters']
                    
                    if constitutive_model == 'isotropic':
                        E = constitutive_parameters[0]
                        u = constitutive_parameters[1]
                        
                        if E == 0.0:
                            QtWidgets.QMessageBox.critical(self,'Edit Material Error',"Young's modulus should be greater than zero!")
                            ins_edit_material_dialog.deleteLater()
                            return None
                        else:   pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
            
            if 'density' in edit_material_information_dict:
                pass
            else:
                pass
            if 'plasticity' in edit_material_information_dict:
                pass
            else:
                pass
            if 'strength' in edit_material_information_dict:
                pass
            else:
                pass
        
            ins_main_window.ins_project_database.editMaterial(self.objectName(),material_name,edit_material_information_dict)
        else:
            pass
        ins_edit_material_dialog.deleteLater()
    def __slotRemoveMaterial(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Remove Material',f'Associated assignments that depend on this material will also be removed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_material_item = self.currentItem()
        material_name = ins_material_item.text(0)

        ins_main_window = self.parent().parent().parent().parent().parent()
        associated_property_assignments_gruops_dict_by_part = ins_main_window.ins_project_database.removeMaterial(self.objectName(),material_name)

        ins_materials_item = ins_material_item.parent()
        ins_materials_item.removeChild(ins_material_item)
        del ins_material_item
        
        ins_part_top_item = self.topLevelItem(0)
        for part_item_index in range(ins_part_top_item.childCount()):
            ins_part_item = ins_part_top_item.child(part_item_index)
            if ins_part_item.text(0) in associated_property_assignments_gruops_dict_by_part:
                ins_part_property_assignments_item = ins_part_item.child(3)
                for assignment_item_index in range(ins_part_property_assignments_item.childCount()-1,-1,-1):
                    ins_property_assignment_item = ins_part_property_assignments_item.child(assignment_item_index)
                    if ins_property_assignment_item.text(0) in associated_property_assignments_gruops_dict_by_part[ins_part_item.text(0)]:
                        ins_part_property_assignments_item.removeChild(ins_property_assignment_item)
                        del ins_property_assignment_item
                    else:
                        continue
            else:
                continue
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Material "{material_name}" successfully removed!')

    def __slotCreateAttribute(self) -> None:
        ins_attributes_item = self.currentItem()
        exist_attributes_name_list = [ins_attributes_item.child(attribute_index).text(0) for attribute_index in range(ins_attributes_item.childCount())]
        
        ins_attribute_dialog = _CreateAttributeDialog(self,exist_attributes_name_list,self.__model_dimension)
        ins_attribute_dialog.show()
        if ins_attribute_dialog.exec() == QtWidgets.QDialog.Accepted:
            attribute_information_dict = ins_attribute_dialog.getAttributeInformation()
            
            if attribute_information_dict['type'] == 'truss':
                if attribute_information_dict['parameters'][0] == 0.0:
                    QtWidgets.QMessageBox.critical(self, 'Create Line Attribute Error', 'The sectional area of truss must be greate than zero!')
                    ins_attribute_dialog.deleteLater()
                    return None
                else:
                    pass
            elif attribute_information_dict['type'] == 'plane':
                if attribute_information_dict['parameters'][0] == 0.0:
                    QtWidgets.QMessageBox.critical(self, 'Create Surface Attribute Error', 'The thickness of plane must be greate than zero!')
                    ins_attribute_dialog.deleteLater()
                    return None
                else:
                    pass
            elif attribute_information_dict['type'] == 'shell':
                if len(attribute_information_dict['parameters']) == 1:
                    if attribute_information_dict['parameters'][0] == 0.0:
                        QtWidgets.QMessageBox.critical(self, 'Create Surface Attribute Error', 'The thickness of shell must be greate than zero!')
                        ins_attribute_dialog.deleteLater()
                        return None
                    else:
                        pass
                else:
                    if attribute_information_dict['parameters'][1] == 0.0:
                        QtWidgets.QMessageBox.critical(self, 'Create Surface Attribute Error', 'The thickness of shell must be greate than zero!')
                        ins_attribute_dialog.deleteLater()
                        return None
                    else:
                        pass
            elif attribute_information_dict['type'] == 'solid':
                pass
            else:
                pass

            ins_main_window = self.parent().parent().parent().parent().parent()
            ins_main_window.ins_project_database.createAttribute(self.objectName(), attribute_information_dict)

            ins_attribute_item = QtWidgets.QTreeWidgetItem()
            ins_attribute_item.setText(0,attribute_information_dict['name'])
            ins_attribute_item.setData(1,0,'attribute')
            ins_attributes_item.addChild(ins_attribute_item)
            ins_attributes_item.setExpanded(True)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Attribute "{attribute_information_dict['name']}" successfully created!')
        else:
            pass
        ins_attribute_dialog.deleteLater()
    def __slotRenameAttribute(self) -> None:
        ins_attribue_item = self.currentItem()
        
        ins_attributes_item = ins_attribue_item.parent()
        
        exist_attributes_name_list = [ins_attributes_item.child(item_index).text(0) for item_index in range(ins_attributes_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_attributes_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_attribute_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            old_attribute_name = ins_attribue_item.text(0)
            ins_main_window.ins_project_database.renameAttribute(self.objectName(),old_attribute_name,new_attribute_name)
            
            ins_attribue_item.setText(0,new_attribute_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Attribute "{old_attribute_name}" has been renamed to "{new_attribute_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditAttribute(self) -> None:
        ins_attribute_item = self.currentItem()
        attribute_name = ins_attribute_item.text(0)
        
        ins_main_window = self.parent().parent().parent().parent().parent()

        ins_edit_attribute_dialog = _CreateAttributeDialog(self,[],self.__model_dimension)
        attribute_information_dict = ins_main_window.ins_project_database.getAttributeInformation(self.objectName(),attribute_name)
        ins_edit_attribute_dialog.setAttributeInformation(attribute_name,attribute_information_dict)
        ins_edit_attribute_dialog.show()
        if ins_edit_attribute_dialog.exec() == QtWidgets.QDialog.Accepted:
            edit_material_information_dict = ins_edit_attribute_dialog.getAttributeInformation()

            if edit_material_information_dict['type'] == 'truss':
                if edit_material_information_dict['parameters'][0] == 0.0:
                    QtWidgets.QMessageBox.critical(self, 'Edit Line Attribute Error', 'The sectional area of truss must be greate than zero!')
                    ins_edit_attribute_dialog.deleteLater()
                    return None
                else:
                    pass
            elif edit_material_information_dict['type'] == 'plane':
                if edit_material_information_dict['parameters'][0] == 0.0:
                    QtWidgets.QMessageBox.critical(self, 'Edit Surface Attribute Error', 'The thickness of plane must be greate than zero!')
                    ins_edit_attribute_dialog.deleteLater()
                    return None
                else:
                    pass
            elif edit_material_information_dict['type'] == 'shell':
                if len(edit_material_information_dict['parameters']) == 1:
                    if edit_material_information_dict['parameters'][0] == 0.0:
                        QtWidgets.QMessageBox.critical(self, 'Edit Surface Attribute Error', 'The thickness of shell must be greate than zero!')
                        ins_edit_attribute_dialog.deleteLater()
                        return None
                    else:
                        pass
                else:
                    if edit_material_information_dict['parameters'][1] == 0.0:
                        QtWidgets.QMessageBox.critical(self, 'Edit Surface Attribute Error', 'The thickness of shell must be greate than zero!')
                        ins_edit_attribute_dialog.deleteLater()
                        return None
                    else:
                        pass
            elif edit_material_information_dict['type'] == 'solid':
                pass
            else:
                pass

            ins_main_window.ins_project_database.editAttribute(self.objectName(), attribute_name, edit_material_information_dict)            
        else:
            pass
        ins_edit_attribute_dialog.deleteLater()
    def __slotRemoveAttribute(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Remove Attribute',f'Associated assignments that depend on this material will also be removed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_attribute_item = self.currentItem()
        attribute_name = ins_attribute_item.text(0)

        ins_main_window = self.parent().parent().parent().parent().parent()
        associated_property_assignments_gruops_dict_by_part = ins_main_window.ins_project_database.removeAttribute(self.objectName(),attribute_name)

        ins_attributes_item = ins_attribute_item.parent()
        ins_attributes_item.removeChild(ins_attribute_item)
        del ins_attribute_item
        
        ins_part_top_item = self.topLevelItem(0)
        for part_item_index in range(ins_part_top_item.childCount()):
            ins_part_item = ins_part_top_item.child(part_item_index)
            if ins_part_item.text(0) in associated_property_assignments_gruops_dict_by_part:
                ins_part_property_assignments_item = ins_part_item.child(3)
                for assignment_item_index in range(ins_part_property_assignments_item.childCount()-1,-1,-1):
                    ins_property_assignment_item = ins_part_property_assignments_item.child(assignment_item_index)
                    if ins_property_assignment_item.text(0) in associated_property_assignments_gruops_dict_by_part[ins_part_item.text(0)]:
                        ins_part_property_assignments_item.removeChild(ins_property_assignment_item)
                        del ins_property_assignment_item
                    else:
                        continue
            else:
                continue
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Attribute "{attribute_name}" successfully removed!')

    def __slotSwitchAssemblyAxesVisibility(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_model_visual_window.switchAssemblyViewportAxesVisibility()
    
    def __slotCreateInstances(self) -> None:
        ins_instances_item = self.currentItem()
        
        ins_assembly_top_item = ins_instances_item.parent()
        ins_main_window = self.parent().parent().parent().parent().parent()
        if ins_assembly_top_item.icon(0).isNull():
            for top_item_index in range(self.topLevelItemCount()):
                if self.topLevelItem(top_item_index).icon(0).isNull():   
                    continue
                else:
                    self.topLevelItem(top_item_index).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        part_name_list = [self.topLevelItem(0).child(part_index).text(0) for part_index in range(self.topLevelItem(0).childCount())]
        exist_instances_name_list = [ins_instances_item.child(instances_index).text(0) for instances_index in range(ins_instances_item.childCount())]
        
        ins_instances_dialog = _CreateInstancesDialog(self,part_name_list,exist_instances_name_list)
        ins_instances_dialog.show()
        if ins_instances_dialog.exec() == QtWidgets.QDialog.Accepted:
            instances_by_part_dict = ins_instances_dialog.getInstancesInformation()
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
            for part_name,instances_name_list in instances_by_part_dict.items():
                for instance_name in instances_name_list:
                    ins_main_window.ins_project_database.createInstanceFromPart(self.objectName(),part_name,instance_name)
            
                    ins_model_visual_window.addInstanceToViewport(part_name,instance_name)
                    
                    ins_instance_item = QtWidgets.QTreeWidgetItem()
                    ins_instance_item.setText(0,instance_name)
                    ins_instance_item.setData(1,0,'instance')
                    ins_instances_item.addChild(ins_instance_item)
                    
            ins_instances_item.setExpanded(True)
        else:
            pass
        ins_instances_dialog.deleteLater()
    def __slotRenameInstance(self) -> None:
        ins_instance_item = self.currentItem()
        
        ins_instances_item = ins_instance_item.parent()
        
        exist_instances_name_list = [ins_instances_item.child(item_index).text(0) for item_index in range(ins_instances_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_instances_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_instance_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            old_instance_name = ins_instance_item.text(0)
            ins_main_window.ins_project_database.renameInstance(self.objectName(),old_instance_name,new_instance_name)
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
            ins_model_visual_window.renameInstanceViewport(old_instance_name,new_instance_name)
            
            ins_instance_item.setText(0,new_instance_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Instance "{old_instance_name}" has been renamed to "{new_instance_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditInstanceOrientation(self) -> None:
        ins_instance_item = self.currentItem()
        
        ins_instances_item = ins_instance_item.parent()
        
        ins_assembly_top_item = ins_instances_item.parent()
        ins_main_window = self.parent().parent().parent().parent().parent()
        if ins_assembly_top_item.icon(0).isNull():
            for top_item_index in range(self.topLevelItemCount()):
                if self.topLevelItem(top_item_index).icon(0).isNull():   
                    continue
                else:
                    self.topLevelItem(top_item_index).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        ins_main_toolbar = ins_main_window.findChild(QtCore.QObject,'main-toolbar')
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_manager_dock_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget')
        ins_main_menubar = ins_main_window.menuBar()
        
        ins_main_toolbar.setToolsEnabled(False)
        ins_visualization_toolbar.clearToolsState()
        ins_manager_dock_widget.setEnabled(False)
        ins_main_menubar.setEnabled(False)
        
        instance_name = ins_instance_item.text(0)
        
        ins_assembly_coordinate_systems_item = ins_assembly_top_item.child(3)
        exist_assembly_coordinate_systems_name_list = [ins_assembly_coordinate_systems_item.child(item_index).text(0) for item_index in range(ins_assembly_coordinate_systems_item.childCount())]
        exist_assembly_coordinate_systems_name_list.insert(0,'global')
        
        ins_edit_instacne_orientation_dialog = _EditInstanceOrientation(self,self.__model_dimension,instance_name,exist_assembly_coordinate_systems_name_list)
        ins_edit_instacne_orientation_dialog.show()
        if ins_edit_instacne_orientation_dialog.exec() == QtWidgets.QDialog.Accepted:
            pass
        else:
            pass
        ins_edit_instacne_orientation_dialog.deleteLater()
        
        ins_main_toolbar.setToolsEnabled(True)
        ins_manager_dock_widget.setEnabled(True)
        ins_main_menubar.setEnabled(True)
    def __slotRemoveInstance(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Remove Intance',f'Associated groups,outputs and boundary conditions\n that completely depend on this instance will\n also be removed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_instance_item = self.currentItem()
        remove_instance_name = ins_instance_item.text(0)
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        ins_model_visual_window.removeInstanceOfAssemblyViewport(remove_instance_name)
        
        ins_instances_item = ins_instance_item.parent()
        ins_instances_item.removeChild(ins_instance_item)
        del ins_instance_item

        association_info_dict = ins_main_window.ins_project_database.removeInstance(self.objectName(),remove_instance_name)
        
        ins_assembly_nodes_groups_item = self.topLevelItem(2).child(1)
        for group_name in association_info_dict['agroups']['nodes']:
            for item_index in range(ins_assembly_nodes_groups_item.childCount()):
                ins_assembly_nodes_group_item = ins_assembly_nodes_groups_item.child(item_index)
                if ins_assembly_nodes_group_item.text(0) == group_name:
                    break
                else:
                    continue
            ins_assembly_nodes_groups_item.removeChild(ins_assembly_nodes_group_item)
            del ins_assembly_nodes_group_item
        ins_assembly_elements_groups_item = self.topLevelItem(2).child(2)
        for group_name in association_info_dict['agroups']['elements']:
            for item_index in range(ins_assembly_elements_groups_item.childCount()):
                ins_assembly_elements_group_item = ins_assembly_elements_groups_item.child(item_index)
                if ins_assembly_elements_group_item.text(0) == group_name:
                    break
                else:
                    continue
            ins_assembly_elements_groups_item.removeChild(ins_assembly_elements_group_item)
            del ins_assembly_elements_group_item
        
        ins_outputs_item = self.topLevelItem(4)
        for output_name in association_info_dict['outputs']:
            for item_index in range(ins_outputs_item.childCount()):
                ins_output_item = ins_outputs_item.child(item_index)
                if ins_output_item.text(0) == output_name:
                    break
                else:
                    continue
            ins_outputs_item.removeChild(ins_output_item)
            del ins_output_item
        
        ins_conditions_item = self.topLevelItem(6)
        for condition_name in association_info_dict['conditions']:
            for item_index in range(ins_conditions_item.childCount()):
                ins_condition_item = ins_conditions_item.child(item_index)
                if ins_condition_item.text(0) == condition_name:
                    break
                else:
                    continue
            ins_conditions_item.removeChild(ins_condition_item)
            del ins_condition_item
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Instance "{remove_instance_name}" successfully removed!')
    
    def __slotCreateAssemblyGroupFromSelection(self) -> None:
        ins_assembly_groups_item = self.currentItem()
        if ins_assembly_groups_item.text(0) == 'Nodes Groups':
            group_type = 'node'
        elif ins_assembly_groups_item.text(0) == 'Elements Groups':
            group_type = 'element'
        else:
            pass
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        ins_assembly_top_item = ins_assembly_groups_item.parent()
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        labels_selection_dict = ins_model_visual_window.getSelectionFromViewport()
        if labels_selection_dict == {}:
            QtWidgets.QMessageBox.warning(self,'Create Assembly Group Waring',f'None selected {group_type}!')
            return None
        else:
            pass
        
        exist_groups_name_list = [ins_assembly_groups_item.child(item_index).text(0) for item_index in range(ins_assembly_groups_item.childCount())]
        ins_assembly_group_dialog = _CreateGroupFromSelectionDialog(self,'Assembly',exist_groups_name_list)
        ins_assembly_group_dialog.show()
        if ins_assembly_group_dialog.exec() == QtWidgets.QDialog.Accepted:
            assembly_group_name = ins_assembly_group_dialog.getGroupName()
            
            ins_main_window.ins_project_database.createAssemblyGroupFromSelection(self.objectName(),group_type,assembly_group_name,labels_selection_dict)

            ins_assembly_group_item = QtWidgets.QTreeWidgetItem()
            ins_assembly_group_item.setText(0,assembly_group_name)
            ins_assembly_group_item.setData(1,0,f'assembly-{group_type}s-group')
            
            ins_assembly_groups_item.addChild(ins_assembly_group_item)
            ins_assembly_groups_item.setExpanded(True)

            ins_main_window.printMessage(f'Model "{self.objectName()}": The {group_type}s group "{assembly_group_name}" of assembly successfully created!')
        else:
            pass
        ins_assembly_group_dialog.deleteLater()
    def __slotCreateAssemblyGroupFromSourcePart(self) -> None:
        ins_assembly_groups_item = self.currentItem()
        if ins_assembly_groups_item.text(0) == 'Nodes Groups':
            group_type = 'node'
        elif ins_assembly_groups_item.text(0) == 'Elements Groups':
            group_type = 'element'
        else:
            pass
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        ins_assembly_top_item = ins_assembly_groups_item.parent()
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        exist_groups_name_list = [ins_assembly_groups_item.child(item_index).text(0) for item_index in range(ins_assembly_groups_item.childCount())]
        
        ins_instances_item = ins_assembly_groups_item.parent().child(0)
        instances_include_part_groups_dict = {ins_instances_item.child(item_index).text(0):[] for item_index in range(ins_instances_item.childCount())}
        for instance_name in instances_include_part_groups_dict:
            instances_include_part_groups_dict[instance_name] = ins_main_window.ins_project_database.getInstanceIncludePartGroups(self.objectName(),group_type,instance_name)
        
        ins_assembly_group_dialog = _CreateAssemblyGroupFromPart(self,exist_groups_name_list,instances_include_part_groups_dict)
        ins_assembly_group_dialog.show()
        if ins_assembly_group_dialog.exec() == QtWidgets.QDialog.Accepted:
            group_info_list = ins_assembly_group_dialog.getGroupsInfomation()
            
            if '' in group_info_list:
                ins_assembly_group_dialog.deleteLater()
                return None
            else:
                pass
            
            ins_main_window.ins_project_database.createAssemblyGroupFromPart(self.objectName(),group_type,group_info_list)
            
            ins_assembly_group_item = QtWidgets.QTreeWidgetItem()
            ins_assembly_group_item.setText(0,group_info_list[0])
            ins_assembly_group_item.setData(1,0,f'assembly-{group_type}s-group')
            
            ins_assembly_groups_item.addChild(ins_assembly_group_item)
            ins_assembly_groups_item.setExpanded(True)

            ins_main_window.printMessage(f'Model "{self.objectName()}": The {group_type}s group "{group_info_list[0]}" of assembly successfully created!')
        else:
            pass
        ins_assembly_group_dialog.deleteLater()
    def __slotRenameAssemblyGroup(self) -> None:
        ins_assembly_group_item = self.currentItem()
        
        ins_assembly_groups_item = ins_assembly_group_item.parent()
        if ins_assembly_groups_item.text(0) == 'Nodes Groups':
            group_type = 'node'
        elif ins_assembly_groups_item.text(0) == 'Elements Groups':
            group_type = 'element'
        else:
            pass
        
        exist_assembly_groups_name_list = [ins_assembly_groups_item.child(item_index).text(0) for item_index in range(ins_assembly_groups_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_assembly_groups_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_assembly_group_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            old_assembly_group_name = ins_assembly_group_item.text(0)
            ins_main_window.ins_project_database.renameAssemblyGroup(self.objectName(),group_type,old_assembly_group_name,new_assembly_group_name)
            
            ins_assembly_group_item.setText(0,new_assembly_group_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Assembly {group_type}s group "{old_assembly_group_name}" has been renamed to "{new_assembly_group_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditAssemblyGroup(self) -> None:
        ins_assembly_group_item = self.currentItem()
        
        ins_assembly_groups_item = ins_assembly_group_item.parent()
        if ins_assembly_groups_item.text(0) == 'Nodes Groups':
            group_type = 'node'
        elif ins_assembly_groups_item.text(0) == 'Elements Groups':
            group_type = 'element'
        else:
            pass
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        ins_assembly_top_item = ins_assembly_groups_item.parent()
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        ins_main_toolbar = ins_main_window.findChild(QtCore.QObject,'main-toolbar')
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_manager_dock_widget = ins_main_window.findChild(QtWidgets.QDockWidget,'manager-dock-widget')
        ins_main_menubar = ins_main_window.menuBar()
        
        ins_main_toolbar.setToolsEnabled(False)
        ins_visualization_toolbar.clearToolsState()
        ins_visualization_toolbar.setSelectionState(group_type,True)
        ins_manager_dock_widget.setEnabled(False)
        ins_main_menubar.setEnabled(False)
        
        assembly_group_name = ins_assembly_group_item.text(0)
        ins_model_visual_window.showAssemblyViewportGroup(ins_main_window.ins_project_database,group_type,assembly_group_name)
        
        ins_edit_group_dialog = _EditGroupDialog(self, group_type, 'editing assembly group ...')
        ins_edit_group_dialog.show()
        if ins_edit_group_dialog.exec() == QtWidgets.QDialog.Accepted:
            labels_selection_dict = ins_model_visual_window.getSelectionFromViewport()
            if labels_selection_dict == {}:
                QtWidgets.QMessageBox.warning(self,'Edit Assembly Group Waring',f'None selected {group_type}!')
            else:
                ins_main_window.ins_project_database.editAssemblyGroupFromSelection(self.objectName(),group_type,assembly_group_name,labels_selection_dict)   
        
                ins_conditions_item = self.topLevelItem(6)
                for item_index in range(ins_conditions_item.childCount()):
                    condition_name = ins_conditions_item.child(item_index).text(0)
                    
                    condition_group_type, condition_group_name = ins_main_window.ins_project_database.getBoundaryConditionInformation(self.objectName(),condition_name)['group']
                    if group_type == condition_group_type and assembly_group_name == condition_group_name:
                        ins_model_visual_window.removeBoundaryConditionToAssemblyViewport(condition_name)
                        ins_model_visual_window.addBoundaryConditionToAssemblyViewport(ins_main_window.ins_project_database,condition_name)
                    else:
                        continue
        else:
            pass
        ins_edit_group_dialog.deleteLater()
        
        ins_main_toolbar.setToolsEnabled(True)
        ins_visualization_toolbar.setSelectionState(group_type,False)
        ins_manager_dock_widget.setEnabled(True)
        ins_main_menubar.setEnabled(True)
    def __slotRemoveAssemblyGroup(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Remove Assembly Group',f'Associated outputs and boundary conditions\n that completely depend on this part will\n also be removed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_assembly_group_item = self.currentItem()
        assembly_group_name = ins_assembly_group_item.text(0)
        
        ins_assembly_groups_item = ins_assembly_group_item.parent()
        if ins_assembly_groups_item.text(0) == 'Nodes Groups':
            group_type = 'node'
        elif ins_assembly_groups_item.text(0) == 'Elements Groups':
            group_type = 'element'
        else:
            pass
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        assconiation_info_dict = ins_main_window.ins_project_database.removeAssemblyGroup(self.objectName(),group_type,assembly_group_name)
        
        ins_assembly_groups_item.removeChild(ins_assembly_group_item)
        del ins_assembly_group_item
        
        ins_outputs_item = self.topLevelItem(4)
        for output_name in assconiation_info_dict['outputs']:
            for item_index in range(ins_outputs_item.childCount()):
                ins_output_item = ins_outputs_item.child(item_index)
                if ins_output_item.text(0) == output_name:
                    break
                else:
                    continue
            ins_outputs_item.removeChild(ins_output_item)
            del ins_output_item
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_conditions_item = self.topLevelItem(6)
        for condition_name in assconiation_info_dict['conditions']:
            for item_index in range(ins_conditions_item.childCount()):
                ins_condition_item = ins_conditions_item.child(item_index)
                if ins_condition_item.text(0) == condition_name:
                    break
                else:
                    continue
            ins_conditions_item.removeChild(ins_condition_item)
            del ins_condition_item
            
            ins_model_visual_window.removeBoundaryConditionToAssemblyViewport(condition_name)
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Assembly {group_type}s group "{assembly_group_name}" successfully removed!')
    
    def __slotCreateAssemblyCoordinateSystem(self) -> None:
        ins_assembly_coordinate_systems_item = self.currentItem()

        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_assembly_top_item = ins_assembly_coordinate_systems_item.parent()
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        exist_coordinate_systems_name_list = [ins_assembly_coordinate_systems_item.child(item_index).text(0) for item_index in range(ins_assembly_coordinate_systems_item.childCount())]
        exist_coordinate_systems_name_list.insert(0,'global')
        ins_assembly_coordinate_system_dialog = _CreateAssemblyCoordinateSystem(self,self.__model_dimension,exist_coordinate_systems_name_list)
        ins_assembly_coordinate_system_dialog.show()
        if ins_assembly_coordinate_system_dialog.exec() == QtWidgets.QDialog.Accepted:
            coordinate_system_information_dict = ins_assembly_coordinate_system_dialog.getAssemblyCoordinateSystemInformation()
            
            if coordinate_system_information_dict['method'] == '3 points':
                point1_x_string = coordinate_system_information_dict['parameters'][0][0]
                if point1_x_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point1_x = float(point1_x_string)
                point1_y_string = coordinate_system_information_dict['parameters'][0][1]
                if point1_y_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point1_y = float(point1_y_string)
                point1_z_string = coordinate_system_information_dict['parameters'][0][2]
                if point1_z_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point1_z = float(point1_z_string)
                point2_x_string = coordinate_system_information_dict['parameters'][1][0]
                if point2_x_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point2_x = float(point2_x_string)
                point2_y_string = coordinate_system_information_dict['parameters'][1][1]
                if point2_y_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point2_y = float(point2_y_string)
                point2_z_string = coordinate_system_information_dict['parameters'][1][2]
                if point2_z_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point2_z = float(point2_z_string)
                point3_x_string = coordinate_system_information_dict['parameters'][2][0]
                if point3_x_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point3_x = float(point3_x_string)
                point3_y_string = coordinate_system_information_dict['parameters'][2][1]
                if point3_y_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point3_y = float(point3_y_string)
                point3_z_string = coordinate_system_information_dict['parameters'][2][2]
                if point3_z_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point3_z = float(point3_z_string)
                
                vector_p1p2 = [point2_x-point1_x,point2_y-point1_y,point2_z-point1_z]
                vector_p1p3 = [point3_x-point1_x,point3_y-point1_y,point3_z-point1_z]
                cross_product = vector_p1p2[1]*vector_p1p3[2]-vector_p1p2[2]*vector_p1p3[1] + vector_p1p2[2]*vector_p1p3[0]-vector_p1p2[0]*vector_p1p3[2] + vector_p1p2[0]*vector_p1p3[1]-vector_p1p2[1]*vector_p1p3[0]
                if cross_product == 0:
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Selected nodes are collinear!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    pass    
            
                coordinate_system_information_dict['parameters'] = [[point1_x,point1_y,point1_z],[point2_x,point2_y,point2_z],[point3_x,point3_y,point3_z]]
            elif coordinate_system_information_dict['method'] == 'offset':
                point_x_string = coordinate_system_information_dict['parameters'][1][0]
                if point_x_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point_x = float(point_x_string)
                point_y_string = coordinate_system_information_dict['parameters'][1][1]
                if point_y_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point_y = float(point_y_string)
                point_z_string = coordinate_system_information_dict['parameters'][1][2]
                if point_z_string == '':
                    QtWidgets.QMessageBox.critical(self,'Create Assembly Coordinate System Error','Coordinate data cannot be empty!')
                    ins_assembly_coordinate_system_dialog.deleteLater()
                    return None
                else:
                    point_z = float(point_z_string)
                
                coordinate_system_information_dict['parameters'][1] = [point_x,point_y,point_z]
            else:
                pass
        
            ins_main_window.ins_project_database.createAssemblyCoordinateSystem(self.objectName(),coordinate_system_information_dict)
            
            assembly_coordinate_system_info_dict = ins_main_window.ins_project_database.getAssemblyCoordinateSystemInfo(self.objectName(),coordinate_system_information_dict['name'])
            ins_model_visual_window.addCoordinateSystemToCurrentViewport(coordinate_system_information_dict['name'],assembly_coordinate_system_info_dict)
            
            ins_assembly_coordinate_system_item = QtWidgets.QTreeWidgetItem()
            ins_assembly_coordinate_system_item.setText(0,coordinate_system_information_dict['name'])
            ins_assembly_coordinate_system_item.setData(1,0,'assembly-coordinate-system')
            ins_assembly_coordinate_systems_item.addChild(ins_assembly_coordinate_system_item)
            
            ins_assembly_coordinate_systems_item.setExpanded(True)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": The {coordinate_system_information_dict["type"]} coordiante system of assembly successfully created!')
        else:
            pass
        ins_assembly_coordinate_system_dialog.deleteLater()
    def __slotSwitchAssemblyCoordinateSystemsVisibility(self) -> None:
        ins_assembly_coordinate_systems_item = self.currentItem()

        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_assembly_top_item = ins_assembly_coordinate_systems_item.parent()
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        exist_assembly_coordinate_systems_name_list = [ins_assembly_coordinate_systems_item.child(item_index).text(0) for item_index in range(ins_assembly_coordinate_systems_item.childCount())]
        shown_coordinate_systems_name_list = ins_model_visual_window.getCoordinateSystemsOfCurrentViewport()
        ins_switch_coordinate_systems_visibility_dialog = _SwitchCoordinateSystemsVisibility(self,exist_assembly_coordinate_systems_name_list,shown_coordinate_systems_name_list)
        ins_switch_coordinate_systems_visibility_dialog.show()
        if ins_switch_coordinate_systems_visibility_dialog.exec() == QtWidgets.QDialog.Accepted:
            coordinate_systems_visibility_dict = ins_switch_coordinate_systems_visibility_dialog.getCoordinateSystemsVisibility()
            
            for coordinate_system_name in coordinate_systems_visibility_dict['show']:
                if coordinate_system_name in shown_coordinate_systems_name_list:
                    continue
                else:
                    assembly_coordinate_system_info_dict = ins_main_window.ins_project_database.getAssemblyCoordinateSystemInfo(self.objectName(),coordinate_system_name)
                    ins_model_visual_window.addCoordinateSystemToCurrentViewport(coordinate_system_name,assembly_coordinate_system_info_dict)
            
            for coordinate_system_name in coordinate_systems_visibility_dict['hide']:
                if coordinate_system_name in shown_coordinate_systems_name_list:
                    ins_model_visual_window.deleteCoordinateSystemToCurrentViewport(coordinate_system_name)
                else:
                    continue
        else:
            pass
        ins_switch_coordinate_systems_visibility_dialog.deleteLater()
    def __slotRenameAssemblyCoordinateSystem(self) -> None:
        ins_assembly_coordinate_system_item = self.currentItem()
        
        ins_assembly_coordinate_systems_item = ins_assembly_coordinate_system_item.parent()
        exist_assembly_coordinate_systems_name_list = [ins_assembly_coordinate_systems_item.child(item_index).text(0) for item_index in range(ins_assembly_coordinate_systems_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_assembly_coordinate_systems_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_coordinate_system_name = ins_rename_dialog.getNewName()
            
            old_coordinate_system_name = ins_assembly_coordinate_system_item.text(0)
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            
            ins_main_window.ins_project_database.renameAssemblyCoordinateSystem(self.objectName(),old_coordinate_system_name,new_coordinate_system_name)
                        
            ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
            ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
            shown_coordinate_systems_name_list = ins_model_visual_window.getCoordinateSystemsOfCurrentViewport()
            if old_coordinate_system_name in shown_coordinate_systems_name_list:
                ins_model_visual_window.renameShownCoordinateSystemOfCurrentViewport(old_coordinate_system_name,new_coordinate_system_name)
            else:
                pass
            
            ins_assembly_coordinate_system_item.setText(0,new_coordinate_system_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Assembly coordinate system "{old_coordinate_system_name}" has been renamed to "{new_coordinate_system_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditAssemblyCoordinateSystem(self) -> None:
        ins_assembly_coordinate_system_item = self.currentItem()
        
        ins_assembly_coordinate_systems_item = ins_assembly_coordinate_system_item.parent()
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_assembly_top_item = ins_assembly_coordinate_systems_item.parent()
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        assembly_coordinate_system_name = ins_assembly_coordinate_system_item.text(0)
        shown_coordinate_systems_name_list = ins_model_visual_window.getCoordinateSystemsOfCurrentViewport()
        if assembly_coordinate_system_name in shown_coordinate_systems_name_list:
            pass
        else:
            assembly_coordinate_system_info_dict = ins_main_window.ins_project_database.getAssemblyCoordinateSystemInfo(self.objectName(),assembly_coordinate_system_name)
            ins_model_visual_window.addCoordinateSystemToCurrentViewport(assembly_coordinate_system_name,assembly_coordinate_system_info_dict)

        ins_edit_coordiante_system_dialog = _EditCoordinateSystem(self,self.__model_dimension,assembly_coordinate_system_name)
        ins_edit_coordiante_system_dialog.show()
        if ins_edit_coordiante_system_dialog.exec() == QtWidgets.QDialog.Accepted:
            pass
        else:
            pass
        ins_edit_coordiante_system_dialog.deleteLater()
    def __slotRemoveAssemblyCoordinateSystem(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Remove Assembly Coordinate System',f'Associated boundary conditions will also be changed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_assembly_coordinate_system_item = self.currentItem()
        
        ins_assembly_coordinate_systems_item = ins_assembly_coordinate_system_item.parent()
        
        ins_main_window = self.parent().parent().parent().parent().parent()
        assembly_coordinate_system_name = ins_assembly_coordinate_system_item.text(0)
        ins_main_window.ins_project_database.removeAssemblyCoordinateSystem(self.objectName(),assembly_coordinate_system_name)
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_model_visual_window.deleteCoordinateSystemToCurrentViewport(assembly_coordinate_system_name)
        
        ins_assembly_coordinate_systems_item.removeChild(ins_assembly_coordinate_system_item)
        del ins_assembly_coordinate_system_item
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Coordinate system "{assembly_coordinate_system_name}" of assembly successfully removed!')

    def __slotCreateStep(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        ins_assembly_top_item = self.topLevelItem(2)
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        ins_steps_top_item = self.currentItem()
        exist_steps_name_list = [ins_steps_top_item.child(item_index).text(0) for item_index in range(ins_steps_top_item.childCount())]
        
        ins_step_dialog = _CreateStepDialog(self,exist_steps_name_list)
        ins_step_dialog.show()
        if ins_step_dialog.exec() == QtWidgets.QDialog.Accepted:
            step_info_dict = ins_step_dialog.getStepInformation()

            if step_info_dict['type'] in ['static']:
                if step_info_dict['time'] == 0.0:
                    QtWidgets.QMessageBox.critical(self,'Create Step Error','Step time must be greate than zero!')
                    ins_step_dialog.deleteLater()
                    return None
                elif 0.0 in step_info_dict['basic']:
                    QtWidgets.QMessageBox.critical(self,'Create Step Error','Increment size must be greate than zero!')
                    ins_step_dialog.deleteLater()
                    return None
                else:
                    pass
                
                if step_info_dict['basic'][2] > step_info_dict['time']:
                    step_info_dict['basic'][2] = step_info_dict['time']
                else:
                    pass
                
                if step_info_dict['basic'][1] == 'automatic':
                    if step_info_dict['basic'][3] > step_info_dict['basic'][4]:
                        QtWidgets.QMessageBox.critical(self,'Create Step Error','Minimum increment size must be less than or equal to maximum increment size!')
                        ins_step_dialog.deleteLater()
                        return None
                    else:
                        pass
                else:
                    pass
            else:
                pass
        
            ins_main_window.ins_project_database.createStep(self.objectName(), step_info_dict)

            ins_step_item = QtWidgets.QTreeWidgetItem()
            ins_step_item.setText(0,step_info_dict['name'])
            ins_step_item.setData(1,0,'step')
            ins_steps_top_item.addChild(ins_step_item)
            ins_steps_top_item.setExpanded(True)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Step "{step_info_dict['name']}" successfully created!')
        else:
            pass
        ins_step_dialog.deleteLater()
    def __slotRenameStep(self) -> None:
        ins_step_item = self.currentItem()
        
        ins_steps_item = ins_step_item.parent()
        exist_steps_name_list = [ins_steps_item.child(item_index).text(0) for item_index in range(ins_steps_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_steps_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_step_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            old_step_name = ins_step_item.text(0)
            ins_main_window.ins_project_database.renameStep(self.objectName(),old_step_name,new_step_name)
            
            ins_step_item.setText(0,new_step_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Step "{old_step_name}" has been renamed to "{new_step_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditStep(self) -> None:
        ins_step_item = self.currentItem()
        step_name = ins_step_item.text(0)
        
        ins_main_window = self.parent().parent().parent().parent().parent()

        ins_edit_step_dialog = _CreateStepDialog(self,[])
        step_information_dict = ins_main_window.ins_project_database.getStepInformation(self.objectName(),step_name)
        ins_edit_step_dialog.setStepInformation(step_name,step_information_dict)
        ins_edit_step_dialog.show()
        if ins_edit_step_dialog.exec() == QtWidgets.QDialog.Accepted:
            edit_step_information_dict = ins_edit_step_dialog.getStepInformation()

            if edit_step_information_dict['type'] in ['static']:
                if edit_step_information_dict['time'] == 0.0:
                    QtWidgets.QMessageBox.critical(self,'Edit Step Error','Step time must be greate than zero!')
                    ins_edit_step_dialog.deleteLater()
                    return None
                elif 0.0 in edit_step_information_dict['basic']:
                    QtWidgets.QMessageBox.critical(self,'Edit Step Error','Increment size must be greate than zero!')
                    ins_edit_step_dialog.deleteLater()
                    return None
                else:
                    pass
                
                if edit_step_information_dict['basic'][2] > edit_step_information_dict['time']:
                    edit_step_information_dict['basic'][2] = edit_step_information_dict['time']
                else:
                    pass
                
                if edit_step_information_dict['basic'][1] == 'automatic':
                    if edit_step_information_dict['basic'][3] > edit_step_information_dict['basic'][4]:
                        QtWidgets.QMessageBox.critical(self,'Edit Step Error','Minimum increment size must be less than or equal to maximum increment size!')
                        ins_edit_step_dialog.deleteLater()
                        return None
                    else:
                        pass
                else:
                    pass
            else:
                pass
        
            ins_main_window.ins_project_database.editStep(self.objectName(), edit_step_information_dict)            
        else:
            pass
        ins_edit_step_dialog.deleteLater()
    def __slotRemoveStep(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Remove Step',f'Associated outputs and boundary conditions that completely depend on this step will also be removed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_step_item = self.currentItem()
        remove_step_name = ins_step_item.text(0)
        
        ins_steps_item = ins_step_item.parent()
        ins_steps_item.removeChild(ins_step_item)
        del ins_step_item

        ins_main_window = self.parent().parent().parent().parent().parent()
        association_info_dict = ins_main_window.ins_project_database.removeStep(self.objectName(),remove_step_name)
        
        ins_outputs_item = self.topLevelItem(4)
        for output_name in association_info_dict['outputs']:
            for item_index in range(ins_outputs_item.childCount()):
                ins_output_item = ins_outputs_item.child(item_index)
                if ins_output_item.text(0) == output_name:
                    break
                else:
                    continue
            ins_outputs_item.removeChild(ins_output_item)
            del ins_output_item
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_conditions_item = self.topLevelItem(6)
        for condition_name in association_info_dict['conditions']:
            for item_index in range(ins_conditions_item.childCount()):
                ins_condition_item = ins_conditions_item.child(item_index)
                if ins_condition_item.text(0) == condition_name:
                    break
                else:
                    continue
            ins_conditions_item.removeChild(ins_condition_item)
            del ins_condition_item
            
            ins_model_visual_window.removeBoundaryConditionToAssemblyViewport(condition_name)
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Step "{remove_step_name}" successfully removed!')
    
    def __slotCreateOutput(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        ins_assembly_top_item = self.topLevelItem(2)
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        ins_outputs_top_item = self.currentItem()
        exist_outputs_name_list = [ins_outputs_top_item.child(item_index).text(0) for item_index in range(ins_outputs_top_item.childCount())]
        ins_steps_top_item = self.topLevelItem(3)
        exist_steps_name_list = [ins_steps_top_item.child(item_index).text(0) for item_index in range(ins_steps_top_item.childCount())]
        exist_steps_name_list.remove('Initial')
        exist_groups_name_dict = {}
        ins_assembly_nodes_groups_item = self.topLevelItem(2).child(1)
        exist_groups_name_dict['node'] = [ins_assembly_nodes_groups_item.child(item_index).text(0) for item_index in range(ins_assembly_nodes_groups_item.childCount())]
        ins_assembly_elements_groups_item = self.topLevelItem(2).child(2)
        exist_groups_name_dict['element'] = [ins_assembly_elements_groups_item.child(item_index).text(0) for item_index in range(ins_assembly_elements_groups_item.childCount())]
        
        ins_output_dialog = _CreateOutputDialog(self,exist_outputs_name_list,exist_steps_name_list,exist_groups_name_dict)
        ins_output_dialog.show()
        if ins_output_dialog.exec() == QtWidgets.QDialog.Accepted:
            output_info_dict = ins_output_dialog.getOutputInformation()
            
            if '' in output_info_dict['steps']:
                QtWidgets.QMessageBox.critical(self,'Create Output Error','Output must specify begin-step and end-step!')
                ins_output_dialog.deleteLater()
                return None
            elif output_info_dict['frequency'][0] != 'last increment' and output_info_dict['frequency'][1] is None:
                QtWidgets.QMessageBox.critical(self,'Create Output Error','The interval of increments/time is empty!!')
                ins_output_dialog.deleteLater()
                return None
            elif output_info_dict['group'][1] == '':
                QtWidgets.QMessageBox.critical(self,'Create Output Error','Output must specify a group!')
                ins_output_dialog.deleteLater()
                return None
            elif output_info_dict['variables'] == []:
                QtWidgets.QMessageBox.critical(self,'Create Output Error','Output variables is empty!')
                ins_output_dialog.deleteLater()
                return None
            else:
                pass
            
            ins_main_window.ins_project_database.createOutput(self.objectName(), output_info_dict)

            ins_output_item = QtWidgets.QTreeWidgetItem()
            ins_output_item.setText(0,output_info_dict['name'])
            ins_output_item.setData(1,0,'output')
            ins_outputs_top_item.addChild(ins_output_item)
            ins_outputs_top_item.setExpanded(True)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Output "{output_info_dict['name']}" successfully created!')
        else:
            pass
        ins_output_dialog.deleteLater()
    def __slotRenameOutput(self) -> None:
        ins_output_item = self.currentItem()
        
        ins_outputs_item = ins_output_item.parent()
        exist_outputs_name_list = [ins_outputs_item.child(item_index).text(0) for item_index in range(ins_outputs_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_outputs_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_output_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            old_output_name = ins_output_item.text(0)
            ins_main_window.ins_project_database.renameOutput(self.objectName(),old_output_name,new_output_name)
            
            ins_output_item.setText(0,new_output_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Output "{old_output_name}" has been renamed to "{new_output_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditOutput(self) -> None:
        ins_output_item = self.currentItem()
        output_name = ins_output_item.text(0)
        
        ins_steps_top_item = self.topLevelItem(3)
        exist_steps_name_list = [ins_steps_top_item.child(item_index).text(0) for item_index in range(ins_steps_top_item.childCount())]
        exist_steps_name_list.remove('Initial')
        exist_groups_name_dict = {}
        ins_assembly_nodes_groups_item = self.topLevelItem(2).child(1)
        exist_groups_name_dict['node'] = [ins_assembly_nodes_groups_item.child(item_index).text(0) for item_index in range(ins_assembly_nodes_groups_item.childCount())]
        ins_assembly_elements_groups_item = self.topLevelItem(2).child(2)
        exist_groups_name_dict['element'] = [ins_assembly_elements_groups_item.child(item_index).text(0) for item_index in range(ins_assembly_elements_groups_item.childCount())]
        
        ins_main_window = self.parent().parent().parent().parent().parent()

        ins_edit_output_dialog = _CreateOutputDialog(self,[],exist_steps_name_list,exist_groups_name_dict)
        output_information_dict = ins_main_window.ins_project_database.getOutputInformation(self.objectName(),output_name)
        ins_edit_output_dialog.setOutputInformation(output_name,output_information_dict)
        ins_edit_output_dialog.show()
        if ins_edit_output_dialog.exec() == QtWidgets.QDialog.Accepted:
            edit_output_information_dict = ins_edit_output_dialog.getOutputInformation()

            if '' in edit_output_information_dict['steps']:
                QtWidgets.QMessageBox.critical(self,'Edit Output Error','Output must specify begin-step and end-step!')
                ins_edit_output_dialog.deleteLater()
                return None
            elif edit_output_information_dict['frequency'][0] != 'last increment' and edit_output_information_dict['frequency'][1] is None:
                QtWidgets.QMessageBox.critical(self,'Edit Output Error','The interval of increments/time is empty!!')
                ins_edit_output_dialog.deleteLater()
                return None
            elif edit_output_information_dict['group'][1] == '':
                QtWidgets.QMessageBox.critical(self,'Edit Output Error','Output must specify a group!')
                ins_edit_output_dialog.deleteLater()
                return None
            elif edit_output_information_dict['variables'] == []:
                QtWidgets.QMessageBox.critical(self,'Edit Output Error','Output variables is empty!')
                ins_edit_output_dialog.deleteLater()
                return None
            else:
                pass
            
            ins_main_window.ins_project_database.editOutput(self.objectName(), edit_output_information_dict)            
        else:
            pass
        ins_edit_output_dialog.deleteLater()
    def __slotRemoveOutput(self) -> None:
        ins_output_item = self.currentItem()
        remove_output_name = ins_output_item.text(0)
        
        ins_outputs_item = ins_output_item.parent()
        ins_outputs_item.removeChild(ins_output_item)
        del ins_output_item

        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_main_window.ins_project_database.removeOutput(self.objectName(),remove_output_name)
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Output "{remove_output_name}" successfully removed!')

    def __slotCreateBoundaryCondition(self, in_condition_type:str) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        ins_assembly_top_item = self.topLevelItem(2)
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        ins_boundary_conditions_top_item = self.currentItem()
        exist_boundary_conditions_name_list = [ins_boundary_conditions_top_item.child(item_index).text(0) for item_index in range(ins_boundary_conditions_top_item.childCount())]
        group_type = common.P4SBCInfo.BC_TO_GROUP_TYPE[in_condition_type]
        if group_type == 'node':
            ins_assembly_groups_item = self.topLevelItem(2).child(1)
        elif group_type == 'element':
            ins_assembly_groups_item = self.topLevelItem(2).child(2)
        else:
            pass
        exist_groups_name_list = [ins_assembly_groups_item.child(item_index).text(0) for item_index in range(ins_assembly_groups_item.childCount())]
        ins_steps_top_item = self.topLevelItem(3)
        exist_steps_name_list = [ins_steps_top_item.child(item_index).text(0) for item_index in range(ins_steps_top_item.childCount())]

        exist_assembly_coordinate_systems_name_list = ['global']
        
        ins_functions_item = self.topLevelItem(7).child(0)
        exist_functions_name_list = [ins_functions_item.child(item_index).text(0) for item_index in range(ins_functions_item.childCount())]
        exist_functions_name_list.append('None')
        
        if exist_groups_name_list == []:
            QtWidgets.QMessageBox.warning(self,'Create Boundary Condition Waring',f'None {group_type}s group exist!')
            return None
        elif len(exist_steps_name_list) == 1:
            QtWidgets.QMessageBox.warning(self,'Create Boundary Condition Waring',f'None step exist!')
            return None
        else:
            pass
        
        ins_create_boundary_condition_dialog = _CreateBoundaryConditionDialog(self,self.__model_dimension,in_condition_type,exist_boundary_conditions_name_list,exist_groups_name_list,exist_steps_name_list,exist_assembly_coordinate_systems_name_list,exist_functions_name_list)
        ins_create_boundary_condition_dialog.show()
        if ins_create_boundary_condition_dialog.exec() == QtWidgets.QDialog.Accepted:
            boundary_condition_info_dict = ins_create_boundary_condition_dialog.getBoundaryConditionInformation()
            
            if boundary_condition_info_dict['steps'] == {}:
                QtWidgets.QMessageBox.critical(self,'Create Boundary Condition Error','The data of "Definition/Edit" are empty!')
                ins_create_boundary_condition_dialog.deleteLater()
                return None
            else:
                pass
                                
            ins_main_window.ins_project_database.createBoundaryCondition(self.objectName(), in_condition_type, group_type, boundary_condition_info_dict)

            ins_model_visual_window.addBoundaryConditionToAssemblyViewport(ins_main_window.ins_project_database,boundary_condition_info_dict['name'])
            
            ins_boundaty_condition_item = QtWidgets.QTreeWidgetItem()
            ins_boundaty_condition_item.setText(0,boundary_condition_info_dict['name'])
            ins_boundaty_condition_item.setData(1,0,'boundary-condition')
            ins_boundary_conditions_top_item.addChild(ins_boundaty_condition_item)
            ins_boundary_conditions_top_item.setExpanded(True)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Boundary conditoin "{boundary_condition_info_dict['name']}" successfully created!')
        else:
            pass
        ins_create_boundary_condition_dialog.deleteLater()
    def __slotSwitchSetBoundaryConditionsVisibility(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        ins_assembly_top_item = self.topLevelItem(2)
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        boundary_conditions_dict_by_step = ins_main_window.ins_project_database.getBoundaryConditionsByStep(self.objectName())
        shown_boundary_conditions_name_list = ins_model_visual_window.getShownBoundaryConditionsOfAssemblyViewport()
        ins_show_boundary_conditoins_dialog = _SwithBoundaryConditionsVisibility(self, boundary_conditions_dict_by_step,shown_boundary_conditions_name_list)
        ins_show_boundary_conditoins_dialog.show()
        if ins_show_boundary_conditoins_dialog.exec() == QtWidgets.QDialog.Accepted:
            pass
        else:
            pass
        ins_show_boundary_conditoins_dialog.deleteLater()
    def __slotRenameBoundaryCondition(self) -> None:
        ins_condition_item = self.currentItem()
        
        ins_conditions_item = ins_condition_item.parent()
        exist_conditions_name_list = [ins_conditions_item.child(item_index).text(0) for item_index in range(ins_conditions_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_conditions_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_condition_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            old_condition_name = ins_condition_item.text(0)
            ins_main_window.ins_project_database.renameBoundaryCondition(self.objectName(),old_condition_name,new_condition_name)
            
            ins_condition_item.setText(0,new_condition_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Boundary condition "{old_condition_name}" has been renamed to "{new_condition_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditBoundaryCondition(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        
        ins_assembly_top_item = self.topLevelItem(2)
        if ins_assembly_top_item.icon(0).isNull():
            self.topLevelItem(0).setIcon(0,QtGui.QIcon())
            
            ins_assembly_top_item.setIcon(0,QtGui.QIcon(":/image/images/ModulePosition.png"))
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
            
            ins_model_visual_window.switchModuleViewport(ins_assembly_top_item.text(0))    
        else:
            pass
        
        ins_boundary_conditions_top_item = self.currentItem()
        boundary_condition_name = ins_boundary_conditions_top_item.text(0)
        boundary_condition_information_dict = ins_main_window.ins_project_database.getBoundaryConditionInformation(self.objectName(),boundary_condition_name)
        
        group_type = boundary_condition_information_dict['group'][0]
        if group_type == 'node':
            ins_assembly_groups_item = self.topLevelItem(2).child(1)
        elif group_type == 'element':
            ins_assembly_groups_item = self.topLevelItem(2).child(2)
        else:
            pass
        exist_groups_name_list = [ins_assembly_groups_item.child(item_index).text(0) for item_index in range(ins_assembly_groups_item.childCount())]
        ins_steps_top_item = self.topLevelItem(3)
        exist_steps_name_list = [ins_steps_top_item.child(item_index).text(0) for item_index in range(ins_steps_top_item.childCount())]
        
        exist_assembly_coordinate_systems_name_list = ['global']
        ins_functions_item = self.topLevelItem(7).child(0)
        exist_functions_name_list = [ins_functions_item.child(item_index).text(0) for item_index in range(ins_functions_item.childCount())]
        exist_functions_name_list.append('None')
        
        if exist_groups_name_list == []:
            QtWidgets.QMessageBox.warning(self,'Edit Boundary Condition Waring',f'None {group_type}s group exist!')
            return None
        elif len(exist_steps_name_list) == 1:
            QtWidgets.QMessageBox.warning(self,'Edit Boundary Condition Waring',f'None step exist!')
            return None
        else:
            pass
        
        ins_edit_boundary_condition_dialog = _CreateBoundaryConditionDialog(self,self.__model_dimension,boundary_condition_information_dict['type'],[],exist_groups_name_list,exist_steps_name_list,exist_assembly_coordinate_systems_name_list,exist_functions_name_list)
        ins_edit_boundary_condition_dialog.setBoundaryConditionInformation(boundary_condition_name, boundary_condition_information_dict)
        ins_edit_boundary_condition_dialog.show()
        if ins_edit_boundary_condition_dialog.exec() == QtWidgets.QDialog.Accepted:
            edit_boundary_condition_info_dict = ins_edit_boundary_condition_dialog.getBoundaryConditionInformation()
            
            if edit_boundary_condition_info_dict['steps'] == {}:
                QtWidgets.QMessageBox.critical(self,'Edit Boundary Condition Error','The data of "Definition/Edit" are empty!')
                ins_edit_boundary_condition_dialog.deleteLater()
                return None
            else:
                pass
            
            ins_main_window.ins_project_database.editBoundaryCondition(self.objectName(), edit_boundary_condition_info_dict)

            ins_model_visual_window.removeBoundaryConditionToAssemblyViewport(boundary_condition_name)
            ins_model_visual_window.addBoundaryConditionToAssemblyViewport(ins_main_window.ins_project_database,boundary_condition_name)
        else:
            pass
        ins_edit_boundary_condition_dialog.deleteLater()
    def __slotRemoveBoundaryCondition(self) -> None:
        ins_boundary_condition_item = self.currentItem()
        remove_boundary_condition_name = ins_boundary_condition_item.text(0)
        
        ins_boundary_conditions_item = ins_boundary_condition_item.parent()
        ins_boundary_conditions_item.removeChild(ins_boundary_condition_item)
        del ins_boundary_condition_item

        ins_main_window = self.parent().parent().parent().parent().parent()
        ins_main_window.ins_project_database.removeBoundaryCondition(self.objectName(),remove_boundary_condition_name)
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.objectName())
        ins_model_visual_window.removeBoundaryConditionToAssemblyViewport(remove_boundary_condition_name)
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Boundary condition "{remove_boundary_condition_name}" successfully removed!')

    def __slotCreateFunction(self) -> None:
        ins_functions_item = self.currentItem()
        exist_functions_name_list = [ins_functions_item.child(attribute_index).text(0) for attribute_index in range(ins_functions_item.childCount())]
        
        ins_function_dialog = _CreateFunctionDialog(self,exist_functions_name_list)
        ins_function_dialog.show()
        if ins_function_dialog.exec() == QtWidgets.QDialog.Accepted:
            function_info_dict = ins_function_dialog.getFunctionInformation()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            ins_main_window.ins_project_database.createFunction(self.objectName(), function_info_dict)

            ins_function_item = QtWidgets.QTreeWidgetItem()
            ins_function_item.setText(0,function_info_dict['name'])
            ins_function_item.setData(1,0,'function')
            ins_functions_item.addChild(ins_function_item)
            ins_functions_item.setExpanded(True)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Function "{function_info_dict['name']}" successfully created!')
        else:
            pass
        ins_function_dialog.deleteLater()
    def __slotRenameFunction(self) -> None:
        ins_function_item = self.currentItem()
        
        ins_functions_item = ins_function_item.parent()
        exist_functions_name_list = [ins_functions_item.child(item_index).text(0) for item_index in range(ins_functions_item.childCount())]
        
        ins_rename_dialog = _RenameObjectDialog(self,exist_functions_name_list)
        ins_rename_dialog.show()
        if ins_rename_dialog.exec() == QtWidgets.QDialog.Accepted:
            new_function_name = ins_rename_dialog.getNewName()
            
            ins_main_window = self.parent().parent().parent().parent().parent()
            old_function_name = ins_function_item.text(0)
            ins_main_window.ins_project_database.renameFunction(self.objectName(),old_function_name,new_function_name)
            
            ins_function_item.setText(0,new_function_name)
            
            ins_main_window.printMessage(f'Model "{self.objectName()}": Function "{old_function_name}" has been renamed to "{new_function_name}".')
        else:
            pass
        ins_rename_dialog.deleteLater()
    def __slotEditFunction(self) -> None:
        ins_function_item = self.currentItem()
        function_name = ins_function_item.text(0)

        ins_main_window = self.parent().parent().parent().parent().parent()

        ins_edit_function_dialog = _CreateFunctionDialog(self,[])
        function_information_dict = ins_main_window.ins_project_database.getFunctionInformation(self.objectName(),function_name)
        ins_edit_function_dialog.setFunctionInformation(function_name,function_information_dict)
        ins_edit_function_dialog.show()
        if ins_edit_function_dialog.exec() == QtWidgets.QDialog.Accepted:
            edit_function_information_dict = ins_edit_function_dialog.getFunctionInformation()
            
            ins_main_window.ins_project_database.editFunction(self.objectName(), edit_function_information_dict)                       
        else:
            pass
        ins_edit_function_dialog.deleteLater()
    def __slotRemoveFunction(self) -> None:
        ins_response_button = QtWidgets.QMessageBox.question(self,'Remove Function',f'Associated boundary condition will be changed! Continue?')
        if ins_response_button is QtWidgets.QMessageBox.Yes:
            pass
        else:
            return None
        
        ins_function_item = self.currentItem()
        remove_function_name = ins_function_item.text(0)
        
        ins_functions_item = ins_function_item.parent()
        ins_functions_item.removeChild(ins_function_item)
        del ins_function_item
        
        ins_main_window = self.parent().parent().parent().parent().parent()

        ins_main_window.ins_project_database.removeFunction(self.objectName(),remove_function_name)
        
        ins_main_window.printMessage(f'Model "{self.objectName()}": Function "{remove_function_name}" successfully removed!')

class _RenameObjectDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_name:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_name_list = in_exist_name
        
        self.setWindowTitle('Rename')
        self.setFixedHeight(80)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeNameList(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeNameList(self, in_ins_dialog_layout:object) -> None:
        ins_name_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_name_layout)
        
        ins_new_name_label = QtWidgets.QLabel('New Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_new_name_label.setFixedSize(80,30)
        ins_name_layout.addWidget(ins_new_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('new-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit.textChanged.connect(self.__slotCheckNewName)
        ins_name_layout.addWidget(ins_name_line_edit,1)
    # region
    def __slotCheckNewName(self, in_new_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')

        if in_new_name == '' or in_new_name in self.__exist_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion
    
    def __initializeUserButton(self, in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.clicked.connect(self.accept)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getNewName(self) -> str:
        return self.findChild(QtWidgets.QLineEdit,'new-name-edit').text()
class _CreateGroupFromSelectionDialog(QtWidgets.QDialog):
    
    def __init__(self,in_parent:object, in_module_name:str, in_exist_groups_name:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_groups_name_list = in_exist_groups_name
        
        self.setWindowTitle(f'Create {in_module_name} Group')
        self.setFixedHeight(90)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeNameEdit(ins_dialog_layout)
        ins_dialog_layout.addStretch()
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeNameEdit(self, in_ins_dialog_layout:object) -> None:
        ins_group_name_layout = QtWidgets.QHBoxLayout()
        
        ins_group_name_label = QtWidgets.QLabel('group name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_group_name_label.setFixedSize(90,30)
        ins_group_name_layout.addWidget(ins_group_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('group-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Group_','G_','group-','g-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckGroupName)
        ins_group_name_layout.addWidget(ins_name_line_edit,1)

        in_ins_dialog_layout.addLayout(ins_group_name_layout)
    # region
    def __slotCheckGroupName(self, in_group_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        if in_group_name == '' or in_group_name in self.__exist_groups_name_list:
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
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
    
    def getGroupName(self) -> str:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'group-name-edit')
        group_name = ins_name_line_edit.text()
        
        return group_name
class _EditGroupDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_group_type:str, in_tip_content:str):
        super().__init__(parent=in_parent,modal=False)
        
        self.__tip_content = in_tip_content
        
        self.setWindowTitle(f'Edit {in_group_type.capitalize()}s Group')
        self.setFixedSize(300,90)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeTipLabel(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeTipLabel(self, in_ins_dialog_layout:object) -> None:
        ins_tip_label = QtWidgets.QLabel(self.__tip_content,self, alignment=QtCore.Qt.AlignCenter)
        ins_tip_label.setFixedHeight(30)
        in_ins_dialog_layout.addWidget(ins_tip_label,0)
    
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
class _SwitchCoordinateSystemsVisibility(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_coordinate_systems_name:list, in_shown_coordinate_systems_name:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_coordinate_systems_name_list = in_exist_coordinate_systems_name
        self.__shown_coordinate_systems_name_list = in_shown_coordinate_systems_name
        
        self.setWindowTitle(f'Show/Hide Coordinate Systems')
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeCoordinateSystemsList(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeCoordinateSystemsList(self, in_ins_dialog_layout:object) -> None:
        ins_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_selection_layout,1)
        
        ins_coordinate_systems_name_list = QtWidgets.QListWidget(self)
        ins_selection_layout.addWidget(ins_coordinate_systems_name_list,1)
        ins_coordinate_systems_name_list.setObjectName('coordinate-systems-name-list')
        ins_coordinate_systems_name_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        for coordinate_system_name in self.__exist_coordinate_systems_name_list:
            ins_coordiante_system_item = QtWidgets.QListWidgetItem()
            ins_coordiante_system_item.setData(1,coordinate_system_name)
            ins_coordinate_systems_name_list.addItem(ins_coordiante_system_item)
            ins_coordinate_system_check_box = QtWidgets.QCheckBox(self)
            ins_coordinate_system_check_box.setText(coordinate_system_name)
            if coordinate_system_name in self.__shown_coordinate_systems_name_list:
                ins_coordinate_system_check_box.setChecked(True)
            else:
                pass
            ins_coordinate_systems_name_list.setItemWidget(ins_coordiante_system_item,ins_coordinate_system_check_box)
    
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getCoordinateSystemsVisibility(self) -> dict:
        coordinate_systems_visibility_dict = {'show':[],'hide':[]}
        
        ins_coordinate_systems_name_list = self.findChild(QtWidgets.QListWidget,'coordinate-systems-name-list')
        for coordinate_system_index in range(ins_coordinate_systems_name_list.count()):
            if ins_coordinate_systems_name_list.itemWidget(ins_coordinate_systems_name_list.item(coordinate_system_index)).isChecked():
                coordinate_systems_visibility_dict['show'].append(ins_coordinate_systems_name_list.item(coordinate_system_index).data(1))
            else:
                coordinate_systems_visibility_dict['hide'].append(ins_coordinate_systems_name_list.item(coordinate_system_index).data(1))

        return coordinate_systems_visibility_dict
class _EditCoordinateSystem(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_model_dimensino:str, in_coordinate_system_name:str):
        super().__init__(parent=in_parent,modal=True)
        
        self.__model_name = self.parent().objectName()
        self.__model_dimension = in_model_dimensino
        self.__coordinate_system_name = in_coordinate_system_name
        self.__part_name = in_part_name
        
        self.setWindowTitle(f'Edit Coordinate Systems')
        self.setFixedHeight(100)
        self.setMaximumWidth(500)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeTranslationWidget(ins_dialog_layout)
        self.__initializeRotationWidget(ins_dialog_layout)
    
    def __initializeTranslationWidget(self, in_ins_dialog_layout:object):
        ins_translation_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_translation_layout,0)
        
        ins_translation_label = QtWidgets.QLabel('Translate:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_translation_label.setFixedSize(70,30)
        ins_translation_layout.addWidget(ins_translation_label,0)
        
        ins_translation_direction_box = QtWidgets.QComboBox(self)
        ins_translation_direction_box.setObjectName('translation-directions-box')
        ins_translation_direction_box.setFixedSize(50,30)
        if self.__model_dimension == '2D':
            ins_translation_direction_box.addItems(['X','Y'])
        else:
            ins_translation_direction_box.addItems(['X','Y','Z'])
        ins_translation_layout.addWidget(ins_translation_direction_box,0)
        
        ins_translation_edit = QtWidgets.QLineEdit(self)
        ins_translation_edit.setObjectName('translation-value-edit')
        ins_translation_edit.setFixedHeight(30)
        ins_translation_edit.setMaxLength(20)
        ins_translation_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_translation_layout.addWidget(ins_translation_edit,1)
        
        ins_translation_apply = QtWidgets.QPushButton('Apply',self)
        ins_translation_apply.setFixedSize(60,30)
        ins_translation_apply.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_translation_apply.clicked.connect(self.__slotTranslateCoordinateSystemOrigin)
        ins_translation_layout.addWidget(ins_translation_apply,0)
    # region
    def __slotTranslateCoordinateSystemOrigin(self) -> None:
        translation_direction = self.findChild(QtWidgets.QComboBox,'translation-directions-box').currentText()
        translation_value_string = self.findChild(QtWidgets.QLineEdit,'translation-value-edit').text()
        
        if translation_value_string == '':
            return None
        elif float(translation_value_string) == 0.0:
            return None
        else:
            pass
        
        ins_main_window = self.parent().parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.__model_name)
        ins_model_visual_window.editCoordinateSystemOfCurrentViewport(self.__coordinate_system_name,'translate',translation_direction,float(translation_value_string))

        ins_main_window.ins_project_database.editAssemblyCoordinateSystemLocation(self.__model_name,self.__coordinate_system_name,'translate',translation_direction,float(translation_value_string))
    # endregion
    
    def __initializeRotationWidget(self, in_ins_dialog_layout:object):
        ins_rotation_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_rotation_layout,0)
        
        ins_rotation_label = QtWidgets.QLabel('Rotate:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_rotation_label.setFixedSize(70,30)
        ins_rotation_layout.addWidget(ins_rotation_label,0)
        
        ins_rotation_direction_box = QtWidgets.QComboBox(self)
        ins_rotation_direction_box.setObjectName('rotation-directions-box')
        ins_rotation_direction_box.setFixedSize(50,30)
        if self.__model_dimension == '2D':
            ins_rotation_direction_box.addItems(['RZ'])
        else:
            ins_rotation_direction_box.addItems(['RX','RY','RZ'])
        ins_rotation_layout.addWidget(ins_rotation_direction_box,0)
        
        ins_rotation_edit = QtWidgets.QLineEdit(self)
        ins_rotation_edit.setObjectName('rotation-value-edit')
        ins_rotation_edit.setFixedHeight(30)
        ins_rotation_edit.setMaxLength(20)
        ins_rotation_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_rotation_layout.addWidget(ins_rotation_edit,1)
        
        ins_rotation_apply = QtWidgets.QPushButton('Apply',self)
        ins_rotation_apply.setFixedSize(60,30)
        ins_rotation_apply.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_rotation_apply.clicked.connect(self.__slotRotateCoordinateSystemOrientation)
        ins_rotation_layout.addWidget(ins_rotation_apply,0)
    # region
    def __slotRotateCoordinateSystemOrientation(self) -> None:
        rotation_direction = self.findChild(QtWidgets.QComboBox,'rotation-directions-box').currentText()
        rotation_value_string = self.findChild(QtWidgets.QLineEdit,'rotation-value-edit').text()
        
        if rotation_value_string == '':
            return None
        elif float(rotation_value_string) == 0.0:
            return None
        else:
            pass
        
        ins_main_window = self.parent().parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.__model_name)
        ins_model_visual_window.editCoordinateSystemOfCurrentViewport(self.__coordinate_system_name,'rotate',rotation_direction,float(rotation_value_string))

        ins_main_window.ins_project_database.editAssemblyCoordinateSystemLocation(self.__model_name,self.__coordinate_system_name,'rotate',rotation_direction,float(rotation_value_string))
    # endregion

class _ImportMeshPartsDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_parts_name:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__parts_name_list = in_parts_name
        
        self.setWindowTitle('Import Mesh Part')
        self.setMinimumHeight(200)
        self.setMinimumWidth(200)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeNameList(ins_dialog_layout)
        ins_dialog_layout.addStretch()
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeNameList(self, in_ins_dialog_layout:object) -> None:
        ins_name_list = QtWidgets.QListWidget(self)
        ins_name_list.setObjectName('parts-name-list')
        ins_name_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        ins_name_list.addItems(self.__parts_name_list)
        
        in_ins_dialog_layout.addWidget(ins_name_list,1)
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
    
    def getSelectedPartsName(self) -> list:
        ins_name_list = self.findChild(QtWidgets.QListWidget,'parts-name-list')
        selected_parts_name_list = [ins_name_item.text() for ins_name_item in ins_name_list.selectedItems()]
        
        return selected_parts_name_list
class _DuplicateMeshPartsDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_parts_name:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_parts_name_list = in_exist_parts_name
        
        self.setWindowTitle('Duplicate Mesh Part')
        self.setMinimumHeight(200)
        self.setMinimumWidth(200)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        self.__initializeNameList(ins_dialog_layout)
        ins_dialog_layout.addStretch()
        self.__initializeUserButton(ins_dialog_layout)
    
    def __initializeNameList(self, in_ins_dialog_layout:object) -> None:
        ins_name_list = QtWidgets.QListWidget(self)
        ins_name_list.setObjectName('parts-name-list')
        ins_name_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        ins_name_list.addItems(self.__exist_parts_name_list)
        
        in_ins_dialog_layout.addWidget(ins_name_list,1)
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setFixedHeight(30)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
    
    def getSelectedPartsName(self) -> list:
        ins_name_list = self.findChild(QtWidgets.QListWidget,'parts-name-list')
        selected_parts_name_list = [ins_name_item.text() for ins_name_item in ins_name_list.selectedItems()]
        
        return selected_parts_name_list
class _AssignPartElementsProperty(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_model_dimension:str,in_groups_have_property:dict, in_groups_include_geometry:dict,in_attributes_by_type:dict,in_materials_name:list):
        super().__init__(parent=in_parent,modal=True)

        self.__model_dimension = in_model_dimension
        self.__groups_have_property_dict = in_groups_have_property
        self.__groups_include_geometry_dict = in_groups_include_geometry
        self.__attributes_by_type_dict = in_attributes_by_type
        self._materials_name_list = in_materials_name
        
        self.setWindowTitle(f'Assign Part Elements Property')
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)

        self.__initializeGroupGeometryTabWidget(ins_dialog_layout)        
        self.__initializeUserButton(ins_dialog_layout)

    def __initializeGroupGeometryTabWidget(self,in_ins_dialog_layout:object) -> None:
        ins_group_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_group_selection_layout,0)
        
        ins_group_name_label = QtWidgets.QLabel(text='Group Name', parent=self, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_group_name_label.setFixedSize(90,30)
        ins_group_selection_layout.addWidget(ins_group_name_label,0)
        ins_groups_name_box = QtWidgets.QComboBox(self)
        ins_groups_name_box.setObjectName('groups-box')
        ins_groups_name_box.setFixedSize(150,30)
        ins_groups_name_box.addItems(list(self.__groups_have_property_dict.keys()))
        ins_groups_name_box.setCurrentIndex(-1)
        ins_groups_name_box.currentTextChanged.connect(self.__slotSwitchPartElementsGroup)
        ins_group_selection_layout.addWidget(ins_groups_name_box,0)
        ins_group_selection_layout.addStretch()
        
        ins_geometry_tab_widget = QtWidgets.QTabWidget(self)
        ins_geometry_tab_widget.setObjectName('geometry-tab-widget')
        in_ins_dialog_layout.addWidget(ins_geometry_tab_widget,1)

        if self.__model_dimension == '2D':
            geometry_type_list = common.P4SElementInfo.SUPPORT_GEOMETRY_2D
        else:
            geometry_type_list = common.P4SElementInfo.SUPPORT_GEOMETRY_3D
        for tab_index,geometry_name in enumerate(geometry_type_list):
            ins_geometry_widget = QtWidgets.QWidget(ins_geometry_tab_widget)
            ins_geometry_tab_widget.addTab(ins_geometry_widget,geometry_name)
            ins_geometry_tab_widget.setCurrentIndex(tab_index)
            ins_geometry_tab_widget.setTabVisible(tab_index,False)

            ins_geometry_widget_layout = QtWidgets.QVBoxLayout()
            ins_geometry_widget.setLayout(ins_geometry_widget_layout)

            ins_property_layout = QtWidgets.QHBoxLayout()
            ins_geometry_widget_layout.addLayout(ins_property_layout,0)
            ins_attributes_type_label= QtWidgets.QLabel(text='Attribute Type:',parent=ins_geometry_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            ins_attributes_type_label.setFixedSize(105,30)
            ins_property_layout.addWidget(ins_attributes_type_label,0)
            ins_attribute_type_box = QtWidgets.QComboBox(ins_geometry_widget)
            ins_attribute_type_box.setObjectName('attribute-type-box')
            ins_attribute_type_box.setFixedSize(100,30)
            ins_property_layout.addWidget(ins_attribute_type_box,0)
            ins_attribute_name_label= QtWidgets.QLabel(text='Attribute Name:',parent=ins_geometry_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            ins_attribute_name_label.setFixedSize(115,30)
            ins_property_layout.addWidget(ins_attribute_name_label,0)
            ins_attributes_name_box = QtWidgets.QComboBox(ins_geometry_widget)
            ins_attributes_name_box.setObjectName('attributes-name-box')
            ins_attributes_name_box.setFixedSize(150,30)
            ins_property_layout.addWidget(ins_attributes_name_box,0)
            ins_material_name_label= QtWidgets.QLabel(text='Material Name:',parent=ins_geometry_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            ins_material_name_label.setFixedSize(115,30)
            ins_property_layout.addWidget(ins_material_name_label,0)
            ins_materials_name_box = QtWidgets.QComboBox(ins_geometry_widget)
            ins_materials_name_box.setObjectName('materials-name-box')
            ins_materials_name_box.setFixedSize(150,30)
            ins_materials_name_box.addItems(self._materials_name_list)
            ins_property_layout.addWidget(ins_materials_name_box,0) 
            ins_property_layout.addStretch()

            ins_split_line = QtWidgets.QFrame(parent=ins_geometry_widget,frameShape=QtWidgets.QFrame.Shape.HLine)
            ins_split_line.setLineWidth(1)
            ins_geometry_widget_layout.addWidget(ins_split_line,0)
            
            ins_elements_type_layout = QtWidgets.QHBoxLayout()
            ins_geometry_widget_layout.addLayout(ins_elements_type_layout,0)
            ins_elements_type_label = QtWidgets.QLabel(text='Element Type:',parent=ins_geometry_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            ins_elements_type_label.setFixedSize(100,30)
            ins_elements_type_layout.addWidget(ins_elements_type_label,0)
            ins_geometry_elements_type_box = QtWidgets.QComboBox(ins_geometry_widget)
            ins_geometry_elements_type_box.setObjectName('elements-type-box')
            ins_geometry_elements_type_box.setFixedSize(100,30)
            ins_geometry_elements_type_box.currentTextChanged.connect(self.__slotSwitchElementsType)
            ins_elements_type_layout.addWidget(ins_geometry_elements_type_box,0)
            ins_elements_type_description_label = QtWidgets.QLabel(parent=ins_geometry_widget, alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            ins_elements_type_description_label.setObjectName('element-type-description-label')
            ins_elements_type_description_label.setFixedHeight(30)
            ins_elements_type_layout.addWidget(ins_elements_type_description_label,1)
            
            ins_geometry_widget_layout.addStretch()
            
            ins_attribute_type_box.currentTextChanged.connect(self.__slotSwitchAttributeType)
            if self.__model_dimension == '2D':
                ins_attribute_type_box.addItems(common.P4SElementInfo.GEOMETRY_INCLUDE_FLAGS_2D[geometry_name])
            elif self.__model_dimension == '3D':
                ins_attribute_type_box.addItems(common.P4SElementInfo.GEOMETRY_INCLUDE_FLAGS_3D[geometry_name])
            else:
                pass
    # region
    def __slotSwitchPartElementsGroup(self, in_group_name:str) -> None:
        ins_geometry_tab_widget = self.findChild(QtWidgets.QTabWidget,'geometry-tab-widget')
        for tab_index in range(ins_geometry_tab_widget.count()):
            ins_geometry_widget = ins_geometry_tab_widget.widget(tab_index)
            
            ins_attribute_type_box = ins_geometry_widget.findChild(QtWidgets.QComboBox,'attribute-type-box')
            ins_attribute_type_box.setCurrentIndex(0)
            
            if ins_geometry_tab_widget.tabText(tab_index) in self.__groups_include_geometry_dict[in_group_name]:
                ins_geometry_tab_widget.setTabVisible(tab_index,True)
            else:
                ins_geometry_tab_widget.setTabVisible(tab_index,False)
        
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        if self.__groups_have_property_dict[in_group_name]:
            QtWidgets.QMessageBox.warning(self,'Assign Property Waring','This group contains elements that have already been assigned!')
            ins_accept_button.setEnabled(False)
            
            for tab_index in range(ins_geometry_tab_widget.count()):
                ins_geometry_tab_widget.setTabVisible(tab_index,False)

            return None
        else:
            ins_accept_button.setEnabled(True)
        
    def __slotSwitchAttributeType(self, in_type:str) -> None:
        ins_geometry_tab_widget = self.findChild(QtWidgets.QTabWidget,'geometry-tab-widget')
        ins_current_geometry_widget = ins_geometry_tab_widget.currentWidget()
        
        ins_attributes_name_box = ins_current_geometry_widget.findChild(QtWidgets.QComboBox,'attributes-name-box')
        ins_attributes_name_box.clear()
        
        if in_type in self.__attributes_by_type_dict:
            ins_attributes_name_box.addItems(self.__attributes_by_type_dict[in_type])
        else:
            pass
        
        current_tab_indx = ins_geometry_tab_widget.indexOf(ins_current_geometry_widget)
        current_geometry = ins_geometry_tab_widget.tabText(current_tab_indx)
        ins_geometry_elements_type_box = ins_current_geometry_widget.findChild(QtWidgets.QComboBox,'elements-type-box')
        ins_geometry_elements_type_box.clear()
        if self.__model_dimension == '2D':
            geometry_include_elements_type = common.P4SElementInfo.GEOMETRY_INCLUDE_ELEMENTS_TYPE_2D[current_geometry]
            flag_include_element_type = common.P4SElementInfo.FLAG_INCLUDE_ELEMENTS_TYPE_2D[in_type]
        elif self.__model_dimension == '3D':
            geometry_include_elements_type = common.P4SElementInfo.GEOMETRY_INCLUDE_ELEMENTS_TYPE_3D[current_geometry]
            flag_include_element_type = common.P4SElementInfo.FLAG_INCLUDE_ELEMENTS_TYPE_3D[in_type]
        else:
            pass
        ins_geometry_elements_type_box.addItems(list(set(geometry_include_elements_type)&set(flag_include_element_type)))
    
    def __slotSwitchElementsType(self, in_type:str) -> None:
        ins_geometry_tab_widget = self.findChild(QtWidgets.QTabWidget,'geometry-tab-widget')
        ins_current_geometry_widget = ins_geometry_tab_widget.currentWidget()
        
        ins_elements_type_description_label = ins_current_geometry_widget.findChild(QtWidgets.QLabel,'element-type-description-label')
        ins_elements_type_description_label.setText('')
        if in_type == '':
            pass
        elif in_type not in common.P4SElementInfo.ELEMENTS_TYPE_DESCRIPTION:
            pass
        else:
            ins_elements_type_description_label.setText(common.P4SElementInfo.ELEMENTS_TYPE_DESCRIPTION[in_type])
    # endregion

    def __initializeUserButton(self, in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.clicked.connect(self.accept)
        ins_accept_button.setEnabled(True)
        ins_button_layout.addWidget(ins_accept_button)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getPropertyAssignments(self) -> dict:
        property_assignments_info_dict = {}
        
        current_group_name = self.findChild(QtWidgets.QComboBox,'groups-box').currentText()
        
        property_assignments_info_dict['group'] = current_group_name
        
        property_assignments_info_dict['property'] = {}
        ins_geometry_tab_widget = self.findChild(QtWidgets.QTabWidget,'geometry-tab-widget')
        for tab_index in range(ins_geometry_tab_widget.count()):
            if ins_geometry_tab_widget.isTabVisible(tab_index):
                ins_geometry_widget = ins_geometry_tab_widget.widget(tab_index)
                
                attribute_name = ins_geometry_widget.findChild(QtWidgets.QComboBox,'attributes-name-box').currentText()
                material_name = ins_geometry_widget.findChild(QtWidgets.QComboBox,'materials-name-box').currentText()
                element_type = ins_geometry_widget.findChild(QtWidgets.QComboBox,'elements-type-box').currentText()
                
                property_assignments_info_dict['property'][ins_geometry_tab_widget.tabText(tab_index)]=[attribute_name,material_name,element_type]
            else:
                continue

        return property_assignments_info_dict
    def setPropertyAssignments(self, in_group_name:str, in_property_assignments:dict) -> None:
        ins_groups_name_box = self.findChild(QtWidgets.QComboBox,'groups-box')
        ins_groups_name_box.setCurrentText(in_group_name)
        ins_groups_name_box.setEnabled(False)
        
        ins_geometry_tab_widget = self.findChild(QtWidgets.QTabWidget,'geometry-tab-widget')
        for tab_index in range(ins_geometry_tab_widget.count()):
            if ins_geometry_tab_widget.isTabVisible(tab_index):
                ins_geometry_widget = ins_geometry_tab_widget.widget(tab_index)
                
                property_assignment_info_list = in_property_assignments[ins_geometry_tab_widget.tabText(tab_index)]
                
                ins_geometry_widget.findChild(QtWidgets.QComboBox,'attributes-name-box').setCurrentText(property_assignment_info_list[0])
                ins_geometry_widget.findChild(QtWidgets.QComboBox,'materials-name-box').setCurrentText(property_assignment_info_list[1])
                ins_geometry_widget.findChild(QtWidgets.QComboBox,'elements-type-box').setCurrentText(property_assignment_info_list[2])
            else:
                continue

class _CreateMaterialDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_materials_name_list:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_materials_name_list = in_exist_materials_name_list
        
        self.setWindowTitle('Create Material')
        self.setMinimumSize(500,400)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeNameList(ins_dialog_layout)
        
        self.__initializeAttributesButton(ins_dialog_layout)
        
        ins_attributes_tab_widget = QtWidgets.QTabWidget(self)
        ins_attributes_tab_widget.setObjectName('attributes-tab-widget')
        ins_attributes_tab_widget.setContentsMargins(0,0,0,0)
        ins_dialog_layout.addWidget(ins_attributes_tab_widget,1)
        ins_elasticity_widget = self.__initializeElasticityWidget()
        ins_attributes_tab_widget.addTab(ins_elasticity_widget,'Elasticity')
        ins_attributes_tab_widget.setTabVisible(0,False)
        ins_density_widget = self.__initializeDensityWidget()
        ins_attributes_tab_widget.addTab(ins_density_widget,'Density')
        ins_attributes_tab_widget.setTabVisible(1,False)
        ins_plasticity_widget = self.__initializePlasticiytWidget()
        ins_attributes_tab_widget.addTab(ins_plasticity_widget,'Plasticity')
        ins_attributes_tab_widget.setTabVisible(2,False)
        ins_strength_widget = self.__initializeStrengthWidget()
        ins_attributes_tab_widget.addTab(ins_strength_widget,'Strength')
        ins_attributes_tab_widget.setTabVisible(3,False)
        
        self.__initializeUserButton(ins_dialog_layout)

    def __initializeNameList(self, in_ins_dialog_layout:object) -> None:
        ins_material_name_layout = QtWidgets.QHBoxLayout()
        
        ins_material_name_label = QtWidgets.QLabel('Material Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_material_name_label.setFixedSize(100,30)
        ins_material_name_layout.addWidget(ins_material_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('material-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Material_','Mat_','material-','mat-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckMaterialName)
        ins_material_name_layout.addWidget(ins_name_line_edit,1)

        in_ins_dialog_layout.addLayout(ins_material_name_layout)
    # region
    def __slotCheckMaterialName(self, in_material_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')

        if in_material_name == '' or in_material_name in self.__exist_materials_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion
    
    def __initializeAttributesButton(self, in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.setSpacing(5)
        ins_button_layout.addStretch()
        
        ins_elasticity_button = QtWidgets.QPushButton()
        ins_elasticity_button.setText('Elasticity')
        ins_elasticity_button.setObjectName('elasticity-button')
        ins_elasticity_button.setFixedSize(80,30)
        ins_elasticity_button.setCheckable(True)
        ins_elasticity_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_elasticity_button.toggled.connect(self.__slotActivateElasticity)
        ins_button_layout.addWidget(ins_elasticity_button)

        ins_density_button = QtWidgets.QPushButton()
        ins_density_button.setText('Density')
        ins_density_button.setObjectName("density-button")
        ins_density_button.setFixedSize(80,30)
        ins_density_button.setCheckable(True)
        ins_density_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_density_button.toggled.connect(self.__slotActivateDensity)
        ins_button_layout.addWidget(ins_density_button)
        ins_density_button.setEnabled(False)
        
        ins_plasticity_button = QtWidgets.QPushButton()
        ins_plasticity_button.setText('Plasticity')
        ins_plasticity_button.setObjectName('plasticity-button')
        ins_plasticity_button.setFixedSize(80,30)
        ins_plasticity_button.setCheckable(True)
        ins_plasticity_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_plasticity_button.toggled.connect(self.__slotActivatePlasticity)
        ins_button_layout.addWidget(ins_plasticity_button)
        ins_plasticity_button.setEnabled(False)
        
        ins_strength_button = QtWidgets.QPushButton()
        ins_strength_button.setText('Strength')
        ins_strength_button.setObjectName('strength-button')
        ins_strength_button.setFixedSize(80,30)
        ins_strength_button.setCheckable(True)
        ins_strength_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_strength_button.toggled.connect(self.__slotActivateStrength)
        ins_button_layout.addWidget(ins_strength_button)
        ins_strength_button.setEnabled(False)
        
        in_ins_dialog_layout.addLayout(ins_button_layout,0)
    # region
    def __slotActivateElasticity(self, in_enable_state:bool) -> None:
        ins_attributes_tab_widget = self.findChild(QtWidgets.QTabWidget,'attributes-tab-widget')
        ins_attributes_tab_widget.setTabVisible(0,in_enable_state)
    def __slotActivateDensity(self, in_enable_state:bool) -> None:
        ins_attributes_tab_widget = self.findChild(QtWidgets.QTabWidget,'attributes-tab-widget')
        ins_attributes_tab_widget.setTabVisible(1,in_enable_state)
    def __slotActivatePlasticity(self, in_enable_state:bool) -> None:
        ins_attributes_tab_widget = self.findChild(QtWidgets.QTabWidget,'attributes-tab-widget')
        ins_attributes_tab_widget.setTabVisible(2,in_enable_state)
    def __slotActivateStrength(self, in_enable_state:bool) -> None:
        ins_attributes_tab_widget = self.findChild(QtWidgets.QTabWidget,'attributes-tab-widget')
        ins_attributes_tab_widget.setTabVisible(3,in_enable_state)
    # endregion
    
    def __initializeElasticityWidget(self) -> object:
        ins_elasticity_widget = QtWidgets.QWidget()
        
        ins_elasticity_widget_layout = QtWidgets.QVBoxLayout()
        ins_elasticity_widget.setLayout(ins_elasticity_widget_layout)
        
        ins_elasticity_type_layout = QtWidgets.QHBoxLayout()
        ins_elasticity_widget_layout.addLayout(ins_elasticity_type_layout,0)
        ins_elasticity_type_label = QtWidgets.QLabel('Type:',ins_elasticity_widget,alignment=QtCore.Qt.AlignCenter)
        ins_elasticity_type_label.setFixedSize(45,30)
        ins_elasticity_type_layout.addWidget(ins_elasticity_type_label)
        ins_elasticity_type_box = QtWidgets.QComboBox(ins_elasticity_widget)
        ins_elasticity_type_box.setObjectName('elasticity-type')
        ins_elasticity_type_box.setFixedSize(150,30)
        ins_elasticity_type_box.addItem('elastic')
        ins_elasticity_type_box.currentTextChanged.connect(self.__slotSwitchElasticityType)
        ins_elasticity_type_layout.addWidget(ins_elasticity_type_box)
        ins_elasticity_type_layout.addStretch()
        
        ins_elasticity_type_setacked_layout = QtWidgets.QStackedLayout()
        ins_elasticity_type_setacked_layout.setObjectName('elasticity-stacked-layout')
        ins_elasticity_widget_layout.addLayout(ins_elasticity_type_setacked_layout,1)
        ins_elastic_widget = self.__initializeElasticWidget()
        ins_elasticity_type_setacked_layout.addWidget(ins_elastic_widget)
        
        return ins_elasticity_widget
    # region
    def __slotSwitchElasticityType(self, in_elasticity_type: str) -> None:
        ins_elasticity_widget = self.findChild(QtWidgets.QTabWidget,'attributes-tab-widget').widget(0)
        ins_elasticity_type_setacked_layout = ins_elasticity_widget.findChild(QtWidgets.QStackedLayout,'elasticity-stacked-layout')
        
        if in_elasticity_type == 'elastic':
            ins_elasticity_type_setacked_layout.setCurrentIndex(0)
        else:
            pass

    def __initializeElasticWidget(self) -> None:
        ins_elastic_widget = QtWidgets.QWidget()
        
        ins_elastic_widget_layout = QtWidgets.QVBoxLayout()
        ins_elastic_widget.setLayout(ins_elastic_widget_layout)
        
        ins_elastic_constitutive_model_layout = QtWidgets.QHBoxLayout()
        ins_elastic_widget_layout.addLayout(ins_elastic_constitutive_model_layout,0)
        ins_elastic_constitutive_model_label = QtWidgets.QLabel('constitutive model:',alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_elastic_constitutive_model_label.setFixedSize(135,30)
        ins_elastic_constitutive_model_layout.addWidget(ins_elastic_constitutive_model_label)
        ins_elastic_constitutive_model_box = QtWidgets.QComboBox()
        ins_elastic_constitutive_model_box.setObjectName('elastic-constitutive-model-box')
        ins_elastic_constitutive_model_box.setFixedSize(190,30)
        ins_elastic_constitutive_model_box.addItems(['isotropic'])
        ins_elastic_constitutive_model_box.currentIndexChanged.connect(self.__slotSwitchElasticConstitutiveModel)
        ins_elastic_constitutive_model_layout.addWidget(ins_elastic_constitutive_model_box)
        ins_elastic_constitutive_model_layout.addStretch()
        
        ins_elastic_constitutive_model_stacked_layout = QtWidgets.QStackedLayout()
        ins_elastic_constitutive_model_stacked_layout.setObjectName('elastic-constitutive-model-stacked-layout')
        ins_elastic_widget_layout.addLayout(ins_elastic_constitutive_model_stacked_layout,1)
        ins_elastic_isotropic_table = self.__initializeIsotropicModelParamsTable()
        ins_elastic_constitutive_model_stacked_layout.addWidget(ins_elastic_isotropic_table)
        
        return ins_elastic_widget
    def __initializeIsotropicModelParamsTable(self) -> None:
        ins_params_table = QtWidgets.QTableWidget()
        ins_params_table.horizontalHeader().setSectionsClickable(False)
        ins_params_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ins_params_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_params_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        ins_params_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        
        ins_params_table.setRowCount(1)
        ins_params_table.setColumnCount(2)
        ins_params_table.setHorizontalHeaderLabels(['E','u'])
        
        ins_E_spin_box = QtWidgets.QDoubleSpinBox()
        ins_E_spin_box.setObjectName('spin-box-without-arrow')
        ins_E_spin_box.setRange(0.0,999999999999999)
        ins_E_spin_box.setDecimals(3)
        ins_E_spin_box.setAlignment(QtCore.Qt.AlignCenter)
        ins_params_table.setCellWidget(0,0,ins_E_spin_box)
        
        ins_u_spin_box = QtWidgets.QDoubleSpinBox()
        ins_u_spin_box.setObjectName('spin-box-without-arrow')
        ins_u_spin_box.setRange(-1.0,0.5)
        ins_u_spin_box.setDecimals(3)
        ins_u_spin_box.setAlignment(QtCore.Qt.AlignCenter)
        ins_params_table.setCellWidget(0,1,ins_u_spin_box)
        
        return ins_params_table

    def __slotSwitchElasticConstitutiveModel(self, in_constitutive_model_index:int) -> None:
        ins_elasticity_widget = self.findChild(QtWidgets.QTabWidget,'attributes-tab-widget').widget(0)
        ins_elastic_widget = ins_elasticity_widget.findChild(QtWidgets.QStackedLayout,'elasticity-stacked-layout').widget(0)
        ins_elastic_constitutive_model_stacked_layout = ins_elastic_widget.findChild(QtWidgets.QStackedLayout,'elastic-constitutive-model-stacked-layout')
        ins_elastic_constitutive_model_stacked_layout.setCurrentIndex(in_constitutive_model_index)
    # endregion
    def __initializeDensityWidget(self) -> object:
        ins_density_widget = QtWidgets.QWidget()
        return ins_density_widget
    def __initializePlasticiytWidget(self) -> object:
        ins_plasticity_widget = QtWidgets.QWidget()
        return ins_plasticity_widget
    def __initializeStrengthWidget(self) -> object:
        ins_strength_widget = QtWidgets.QWidget()
        return ins_strength_widget
    
    def __initializeUserButton(self, in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.clicked.connect(self.accept)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getMaterialInformation(self) -> dict:
        material_information_dict = {}

        material_information_dict['name'] = self.findChild(QtWidgets.QLineEdit,'material-name-edit').text()

        if self.findChild(QtWidgets.QPushButton,'elasticity-button').isChecked():
            material_information_dict['elasticity'] = {}
            
            ins_elasticity_widget = self.findChild(QtWidgets.QTabWidget,'attributes-tab-widget').widget(0)
            material_information_dict['elasticity']['type'] = ins_elasticity_widget.findChild(QtWidgets.QComboBox,'elasticity-type').currentText()
            
            if material_information_dict['elasticity']['type'] == 'elastic':
                ins_elastic_widget = ins_elasticity_widget.findChild(QtWidgets.QStackedLayout,'elasticity-stacked-layout').currentWidget()
                
                elastic_constitutive_model = ins_elastic_widget.findChild(QtWidgets.QComboBox,'elastic-constitutive-model-box').currentText()
                material_information_dict['elasticity']['constitutive model'] = elastic_constitutive_model
                
                ins_elastic_constitutive_model_params_table = ins_elastic_widget.findChild(QtWidgets.QStackedLayout,'elastic-constitutive-model-stacked-layout').currentWidget()
                material_information_dict['elasticity']['constitutive parameters'] = []
                for column_index in range(ins_elastic_constitutive_model_params_table.columnCount()):
                    material_information_dict['elasticity']['constitutive parameters'].append(ins_elastic_constitutive_model_params_table.cellWidget(0,column_index).value())       
            else:
                pass
        else:
            pass
        
        if self.findChild(QtWidgets.QPushButton,'density-button').isChecked():
            pass
        else:
            pass
        if self.findChild(QtWidgets.QPushButton,'plasticity-button').isChecked():
            pass
        else:
            pass
        if self.findChild(QtWidgets.QPushButton,'strength-button').isChecked():
            pass
        else:
            pass
        
        return material_information_dict
    def setMaterialInformation(self, in_material_name:str, in_material_information:dict) -> None:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'material-name-edit')
        ins_name_line_edit.setText(in_material_name)
        ins_name_line_edit.setEnabled(False)
        
        if 'elasticity' in in_material_information:
            self.findChild(QtWidgets.QPushButton,'elasticity-button').toggle()

            ins_elasticity_widget = self.findChild(QtWidgets.QTabWidget,'attributes-tab-widget').widget(0)
            ins_elasticity_widget.findChild(QtWidgets.QComboBox,'elasticity-type').setCurrentText(in_material_information['elasticity']['type'])

            if in_material_information['elasticity']['type'] == 'elastic':
                ins_elastic_widget = ins_elasticity_widget.findChild(QtWidgets.QStackedLayout,'elasticity-stacked-layout').currentWidget()
                
                ins_elastic_widget.findChild(QtWidgets.QComboBox,'elastic-constitutive-model-box').setCurrentText(in_material_information['elasticity']['constitutive model'])
                
                ins_elastic_constitutive_model_params_table = ins_elastic_widget.findChild(QtWidgets.QStackedLayout,'elastic-constitutive-model-stacked-layout').currentWidget()
                for column_index in range(ins_elastic_constitutive_model_params_table.columnCount()):
                    ins_elastic_constitutive_model_params_table.cellWidget(0,column_index).setValue(in_material_information['elasticity']['constitutive parameters'][column_index])     
            else:
                pass
        else:
            pass
class _CreateAttributeDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_attributes_name_list:list,in_model_dimension:str):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_attributes_name_list = in_exist_attributes_name_list
        self.__model_dimension = in_model_dimension
        
        self.setWindowTitle(f'Create Attribute')
        if in_model_dimension == '2D':
            self.setMinimumSize(400,400)
        else:
            self.setMinimumSize(740,400)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeNameList(ins_dialog_layout)
        
        self.__initializeAttributeTabWidget(ins_dialog_layout)
        
        self.__initializeUserButton(ins_dialog_layout)

    def __initializeNameList(self, in_ins_dialog_layout:object) -> None:
        ins_attribute_name_layout = QtWidgets.QHBoxLayout()
        
        ins_attribute_name_label = QtWidgets.QLabel('Attribute Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_attribute_name_label.setFixedSize(110,30)
        ins_attribute_name_layout.addWidget(ins_attribute_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('attribute-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Attribute_','At_','attribute-','at-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckAttributeName)
        ins_attribute_name_layout.addWidget(ins_name_line_edit,1)

        in_ins_dialog_layout.addLayout(ins_attribute_name_layout,0)
    # region
    def __slotCheckAttributeName(self, in_attribute_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')

        if in_attribute_name == '' or in_attribute_name in self.__exist_attributes_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion

    def __initializeAttributeTabWidget(self, in_ins_dialog_layout) -> None:
        ins_attribute_tab_widget = QtWidgets.QTabWidget()
        ins_attribute_tab_widget.setObjectName('attribute-tab-widget')
        in_ins_dialog_layout.addWidget(ins_attribute_tab_widget,1)
        
        ins_line_attribute_widget = self.__initializeLineAttributeWiget()
        ins_attribute_tab_widget.addTab(ins_line_attribute_widget,'Line')
        ins_surface_attribute_widget = self.__initializeSurfaceAttributeWiget()
        ins_attribute_tab_widget.addTab(ins_surface_attribute_widget,'Surface')
        if self.__model_dimension == '2D':
            pass
        else:
            ins_entity_attribute_widget = self.__initializeEntityAttributeWiget()
            ins_attribute_tab_widget.addTab(ins_entity_attribute_widget,'Entity')
    # region
    def __initializeLineAttributeWiget(self) -> object:
        ins_line_attribute_widget = QtWidgets.QWidget()
        ins_line_attribute_layout = QtWidgets.QVBoxLayout()
        ins_line_attribute_widget.setLayout(ins_line_attribute_layout)
        
        ins_attribute_type_layout = QtWidgets.QHBoxLayout()
        ins_line_attribute_layout.addLayout(ins_attribute_type_layout,0)
        ins_attribute_type_label = QtWidgets.QLabel(text='Type:',alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_attribute_type_label.setFixedSize(38,30)
        ins_attribute_type_layout.addWidget(ins_attribute_type_label)
        ins_attribute_type_box = QtWidgets.QComboBox()
        ins_attribute_type_box.setObjectName('attribute-type-box')
        ins_attribute_type_box.setFixedSize(100,30)
        ins_attribute_type_box.addItems(['truss'])
        ins_attribute_type_box.currentTextChanged.connect(self.__slotChangeAttributeType)
        ins_attribute_type_layout.addWidget(ins_attribute_type_box)
        ins_attribute_type_layout.addStretch()
        
        ins_attribute_parameters_stacked_layout = QtWidgets.QStackedLayout()
        ins_attribute_parameters_stacked_layout.setObjectName('parameters-satcked-layout')
        ins_line_attribute_layout.addLayout(ins_attribute_parameters_stacked_layout,1)
        
        ins_truss_table = QtWidgets.QTableWidget()
        ins_truss_table.setObjectName('attribute-parameters-table')
        ins_attribute_parameters_stacked_layout.addWidget(ins_truss_table)
        # region
        ins_truss_table.horizontalHeader().setSectionsClickable(False)
        ins_truss_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_truss_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        ins_truss_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        
        ins_truss_table.setRowCount(1)
        ins_truss_table.setColumnCount(1)
        ins_truss_table.setHorizontalHeaderLabels(['sectional area'])
        ins_truss_table.setColumnWidth(0,180)
        
        ins_sectional_area_spin_box = QtWidgets.QDoubleSpinBox()
        ins_sectional_area_spin_box.setObjectName('spin-box-without-arrow')
        ins_sectional_area_spin_box.setRange(0.0,999999999999999)
        ins_sectional_area_spin_box.setDecimals(5)
        ins_sectional_area_spin_box.setAlignment(QtCore.Qt.AlignCenter)
        ins_truss_table.setCellWidget(0,0,ins_sectional_area_spin_box)
        # endregion
        
        return ins_line_attribute_widget
    def __initializeSurfaceAttributeWiget(self) -> object:
        ins_surface_attribute_widget = QtWidgets.QWidget()
        ins_surface_attribute_layout = QtWidgets.QVBoxLayout()
        ins_surface_attribute_widget.setLayout(ins_surface_attribute_layout)
        
        ins_attribute_type_layout = QtWidgets.QHBoxLayout()
        ins_surface_attribute_layout.addLayout(ins_attribute_type_layout,0)
        ins_attribute_type_label = QtWidgets.QLabel(text='Type:',alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_attribute_type_label.setFixedSize(38,30)
        ins_attribute_type_layout.addWidget(ins_attribute_type_label)
        ins_attribute_type_box = QtWidgets.QComboBox()
        ins_attribute_type_box.setObjectName('attribute-type-box')
        ins_attribute_type_box.setFixedSize(110,30)
        if self.__model_dimension == '2D':
            ins_attribute_type_box.addItems(['plane'])
        else:
            ins_attribute_type_box.addItems(['shell'])
        ins_attribute_type_box.currentTextChanged.connect(self.__slotChangeAttributeType)
        ins_attribute_type_layout.addWidget(ins_attribute_type_box)
        ins_attribute_type_layout.addStretch()
        
        if self.__model_dimension == '2D':
            pass
        else:
            ins_3D_surface_section_integration_layout = QtWidgets.QHBoxLayout()
            ins_surface_attribute_layout.addLayout(ins_3D_surface_section_integration_layout,0)
            
            ins_integration_update_label = QtWidgets.QLabel(text='update section integration',alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            ins_integration_update_label.setFixedSize(185,30)
            ins_3D_surface_section_integration_layout.addWidget(ins_integration_update_label,0)
            ins_integration_update_radio_button = QtWidgets.QRadioButton()
            ins_integration_update_radio_button.setObjectName('integeration-update-radio')
            ins_integration_update_radio_button.setFixedSize(17,30)
            ins_integration_update_radio_button.toggled.connect(self.__slotChangeSectionIntegrationState)
            ins_3D_surface_section_integration_layout.addWidget(ins_integration_update_radio_button,0)
            ins_3D_surface_section_integration_layout.addSpacing(10)
            ins_integration_update_radio_button.setEnabled(False)
            
            ins_thickness_integration_rule_label = QtWidgets.QLabel(text='integration rule',alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignRight,)
            ins_thickness_integration_rule_label.setFixedSize(109,30)
            ins_3D_surface_section_integration_layout.addWidget(ins_thickness_integration_rule_label,0)
            ins_thickness_integration_rule_box = QtWidgets.QComboBox()
            ins_thickness_integration_rule_box.setObjectName('integration-rule-box')
            ins_thickness_integration_rule_box.addItems(['Simpson','Gauss'])
            ins_thickness_integration_rule_box.setFixedSize(90,30)
            ins_thickness_integration_rule_box.setEnabled(False)
            ins_3D_surface_section_integration_layout.addWidget(ins_thickness_integration_rule_box,0)
            ins_3D_surface_section_integration_layout.addSpacing(10)
            
            ins_reference_surface_label = QtWidgets.QLabel(text='reference surface',alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            ins_reference_surface_label.setFixedSize(120,30)
            ins_3D_surface_section_integration_layout.addWidget(ins_reference_surface_label,0)
            ins_reference_surface_box = QtWidgets.QComboBox()
            ins_reference_surface_box.setObjectName('reference-surface-box')
            ins_reference_surface_box.setEnabled(False)
            ins_reference_surface_box.setFixedSize(80,30)
            ins_reference_surface_box.addItems(['middle','top','bottom'])
            ins_3D_surface_section_integration_layout.addWidget(ins_reference_surface_box,0)
            
            ins_3D_surface_section_integration_layout.addStretch()
        
        ins_attribute_parameters_stacked_layout = QtWidgets.QStackedLayout()
        ins_attribute_parameters_stacked_layout.setObjectName('parameters-satcked-layout')
        ins_surface_attribute_layout.addLayout(ins_attribute_parameters_stacked_layout,1)
        
        if self.__model_dimension == '2D':
            ins_plane_table = QtWidgets.QTableWidget()
            ins_plane_table.setObjectName('attribute-parameters-table')
            ins_attribute_parameters_stacked_layout.addWidget(ins_plane_table)
            # region
            ins_plane_table.horizontalHeader().setSectionsClickable(False)
            ins_plane_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
            ins_plane_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
            ins_plane_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
            
            ins_plane_table.setRowCount(1)
            ins_plane_table.setColumnCount(1)
            ins_plane_table.setHorizontalHeaderLabels(['thickness'])
            ins_plane_table.setColumnWidth(0,180)
            
            ins_thickness_spin_box = QtWidgets.QDoubleSpinBox()
            ins_thickness_spin_box.setObjectName('spin-box-without-arrow')
            ins_thickness_spin_box.setRange(0.0,999999999999999)
            ins_thickness_spin_box.setDecimals(5)
            ins_thickness_spin_box.setAlignment(QtCore.Qt.AlignCenter)
            ins_plane_table.setCellWidget(0,0,ins_thickness_spin_box)
            # endregion
        else:
            ins_shell_table = QtWidgets.QTableWidget()
            ins_shell_table.setObjectName('attribute-parameters-table')
            ins_attribute_parameters_stacked_layout.addWidget(ins_shell_table)
            # region
            ins_shell_table.horizontalHeader().setSectionsClickable(False)
            ins_shell_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
            ins_shell_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
            ins_shell_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
            
            ins_shell_table.setRowCount(1)
            ins_shell_table.setColumnCount(1)
            ins_shell_table.setHorizontalHeaderLabels(['thickness'])
            ins_shell_table.setColumnWidth(0,100)
            
            ins_thickness_spin_box = QtWidgets.QDoubleSpinBox()
            ins_thickness_spin_box.setObjectName('spin-box-without-arrow')
            ins_thickness_spin_box.setAlignment(QtCore.Qt.AlignCenter)
            ins_thickness_spin_box.setRange(0.0,999999999999999)
            ins_thickness_spin_box.setDecimals(5)
            ins_thickness_spin_box.setAlignment(QtCore.Qt.AlignCenter)
            ins_shell_table.setCellWidget(0,0,ins_thickness_spin_box)
            # endregion

        return ins_surface_attribute_widget
    def __initializeEntityAttributeWiget(self) -> object:
        ins_entity_attribute_widget = QtWidgets.QWidget()
        ins_entity_attribute_layout = QtWidgets.QVBoxLayout()
        ins_entity_attribute_widget.setLayout(ins_entity_attribute_layout)
        
        ins_attribute_type_layout = QtWidgets.QHBoxLayout()
        ins_entity_attribute_layout.addLayout(ins_attribute_type_layout,0)
        ins_attribute_type_label = QtWidgets.QLabel(text='Type:',alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_attribute_type_label.setFixedSize(38,30)
        ins_attribute_type_layout.addWidget(ins_attribute_type_label)
        ins_attribute_type_box = QtWidgets.QComboBox()
        ins_attribute_type_box.setObjectName('attribute-type-box')
        ins_attribute_type_box.setFixedSize(100,30)
        ins_attribute_type_box.addItems(['solid'])
        ins_attribute_type_box.currentTextChanged.connect(self.__slotChangeAttributeType)
        ins_attribute_type_layout.addWidget(ins_attribute_type_box)
        ins_attribute_type_layout.addStretch()
        
        ins_attribute_parameters_stacked_layout = QtWidgets.QStackedLayout()
        ins_attribute_parameters_stacked_layout.setObjectName('parameters-satcked-layout')
        ins_entity_attribute_layout.addLayout(ins_attribute_parameters_stacked_layout,1)
        
        ins_solid_table = QtWidgets.QTableWidget()
        ins_solid_table.setObjectName('attribute-parameters-table')
        ins_attribute_parameters_stacked_layout.addWidget(ins_solid_table)
        # region
        ins_solid_table.horizontalHeader().setSectionsClickable(False)
        ins_solid_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_solid_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        ins_solid_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        
        ins_solid_table.setRowCount(0)
        ins_solid_table.setColumnCount(0)
        # endregion

        return ins_entity_attribute_widget
    
    def __slotChangeAttributeType(self, in_type:str) -> None:
        ins_attribute_tab_widget = self.findChild(QtWidgets.QTabWidget,'attribute-tab-widget')
        ins_attribute_widget = ins_attribute_tab_widget.currentWidget()
        ins_attribute_parameters_stacked_layout = ins_attribute_widget.findChild(QtWidgets.QStackedLayout,'parameters-satcked-layout')
        
        if in_type == 'truss':
            ins_attribute_parameters_stacked_layout.setCurrentIndex(0)
        elif in_type == 'plane':
            ins_attribute_parameters_stacked_layout.setCurrentIndex(0)
        elif in_type == 'shell':
            ins_attribute_parameters_stacked_layout.setCurrentIndex(0)
            
            ins_attribute_parameters_stacked_layout = ins_attribute_widget.findChild(QtWidgets.QStackedLayout,'parameters-satcked-layout')
            ins_parameters_table = ins_attribute_parameters_stacked_layout.currentWidget()
            ins_integration_update_radio_button = ins_attribute_widget.findChild(QtWidgets.QRadioButton,'integeration-update-radio')
            ins_integration_update_radio_button.toggled.disconnect(self.__slotChangeSectionIntegrationState)
            if ins_parameters_table.columnCount() == 2:
                if ins_integration_update_radio_button.isChecked():
                    pass
                else:
                    ins_integration_update_radio_button.setChecked(True)
                    
                    ins_thickness_integration_rule_box = ins_attribute_widget.findChild(QtWidgets.QComboBox,'integration-rule-box')
                    ins_thickness_integration_rule_box.setEnabled(True)
            else:
                if ins_integration_update_radio_button.isChecked():
                    ins_integration_update_radio_button.setChecked(False)
                    
                    ins_thickness_integration_rule_box = ins_attribute_widget.findChild(QtWidgets.QComboBox,'integration-rule-box')
                    ins_thickness_integration_rule_box.setEnabled(False)
                else:
                    pass
            ins_integration_update_radio_button.toggled.connect(self.__slotChangeSectionIntegrationState)
            
            ins_attribute_widget.findChild(QtWidgets.QComboBox,'reference-surface-box').setEnabled(False)
        elif in_type == 'solid':
            ins_attribute_parameters_stacked_layout.setCurrentIndex(0)
        else:
            pass
    
    def __slotChangeSectionIntegrationState(self, in_state:bool) -> None:
        ins_attribute_tab_widget = self.findChild(QtWidgets.QTabWidget,'attribute-tab-widget')
        ins_attribute_widget = ins_attribute_tab_widget.currentWidget()
        ins_thickness_integration_rule_box = ins_attribute_widget.findChild(QtWidgets.QComboBox,'integration-rule-box')
        ins_attribute_parameters_stacked_layout = ins_attribute_widget.findChild(QtWidgets.QStackedLayout,'parameters-satcked-layout')
        ins_parameters_table = ins_attribute_parameters_stacked_layout.currentWidget()
        
        attribute_type = ins_attribute_widget.findChild(QtWidgets.QComboBox,'attribute-type-box').currentText()
        if in_state:
            ins_thickness_integration_rule_box.setEnabled(True)
            
            if attribute_type == 'shell':
                ins_parameters_table.insertColumn(1)
                ins_parameters_table.setHorizontalHeaderItem(1,QtWidgets.QTableWidgetItem('integration points'))
                ins_parameters_table.setColumnWidth(1,150)
                
                ins_integration_points_spin_box = QtWidgets.QSpinBox()
                ins_integration_points_spin_box.setObjectName('spin-box-without-arrow')
                ins_integration_points_spin_box.setAlignment(QtCore.Qt.AlignCenter)
                ins_integration_points_spin_box.setRange(1,999)
                ins_integration_points_spin_box.setValue(3)
                ins_parameters_table.setCellWidget(0,1,ins_integration_points_spin_box)
            else:
                pass
        else:
            ins_thickness_integration_rule_box.setEnabled(False)
            
            if attribute_type == 'shell':
                ins_cell_widget = ins_parameters_table.cellWidget(0,1)
                ins_parameters_table.removeCellWidget(0,1)
                ins_cell_widget.deleteLater()
                
                ins_parameters_table.removeColumn(1)
            else:
                pass
    # endregion

    def __initializeUserButton(self, in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.clicked.connect(self.accept)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getAttributeInformation(self) -> dict:
        attribute_information_dict = {}

        attribute_information_dict['name'] = self.findChild(QtWidgets.QLineEdit,'attribute-name-edit').text()
        
        ins_attribute_tab_widget = self.findChild(QtWidgets.QTabWidget,'attribute-tab-widget')
        ins_attribute_widget = ins_attribute_tab_widget.currentWidget()
        ins_attribute_parameters_table = ins_attribute_widget.findChild(QtWidgets.QStackedLayout,'parameters-satcked-layout').currentWidget()
        attribute_information_dict['type'] = ins_attribute_widget.findChild(QtWidgets.QComboBox,'attribute-type-box').currentText()
        if attribute_information_dict['type'] == 'truss':
            attribute_information_dict['parameters'] = [ins_attribute_parameters_table.cellWidget(0,0).value()]
        elif attribute_information_dict['type'] == 'plane':
            attribute_information_dict['parameters'] = [ins_attribute_parameters_table.cellWidget(0,0).value()]
        elif attribute_information_dict['type'] == 'shell':
            attribute_information_dict['parameters'] = []
            
            if ins_attribute_widget.findChild(QtWidgets.QRadioButton,'integeration-update-radio').isChecked():
                attribute_information_dict['parameters'].append(ins_attribute_widget.findChild(QtWidgets.QComboBox,'integration-rule-box').currentIndex())

                attribute_information_dict['parameters'].append(ins_attribute_parameters_table.cellWidget(0,0).value())
                attribute_information_dict['parameters'].append(ins_attribute_parameters_table.cellWidget(0,1).value())
            else:
                attribute_information_dict['parameters'].append(ins_attribute_parameters_table.cellWidget(0,0).value())
        elif attribute_information_dict['type'] == 'solid':
            attribute_information_dict['parameters'] = []
        else:
            pass
        
        return attribute_information_dict
    def setAttributeInformation(self, in_attribute_name:str, in_attribute_information:dict) -> None:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'attribute-name-edit')
        ins_name_line_edit.setText(in_attribute_name)
        ins_name_line_edit.setEnabled(False)
        
        ins_attribute_tab_widget = self.findChild(QtWidgets.QTabWidget,'attribute-tab-widget')
        for tab_index in range(ins_attribute_tab_widget.count()):
            ins_attribute_widget = ins_attribute_tab_widget.widget(tab_index)
            
            ins_attribute_type_box = ins_attribute_widget.findChild(QtWidgets.QComboBox,'attribute-type-box')
            if ins_attribute_type_box.findText(in_attribute_information['type']) == -1:
                continue
            else:
                ins_attribute_tab_widget.setCurrentIndex(tab_index)
            ins_attribute_type_box.setCurrentText(in_attribute_information['type'])

            ins_attribute_parameters_table = ins_attribute_widget.findChild(QtWidgets.QStackedLayout,'parameters-satcked-layout').currentWidget()
            if in_attribute_information['type'] == 'truss':
                ins_attribute_parameters_table.cellWidget(0,0).setValue(in_attribute_information['parameters'][0])
            elif in_attribute_information['type'] == 'plane':
                ins_attribute_parameters_table.cellWidget(0,0).setValue(in_attribute_information['parameters'][0])
            elif in_attribute_information['type'] == 'shell':
                if len(in_attribute_information['parameters']) == 1:
                    ins_attribute_parameters_table.cellWidget(0,0).setValue(in_attribute_information['parameters'][0])
                else:
                    ins_attribute_widget.findChild(QtWidgets.QRadioButton,'integeration-update-radio').setChecked(True)
                    ins_attribute_widget.findChild(QtWidgets.QComboBox,'integration-rule-box').setCurrentIndex(in_attribute_information['parameters'][0])
                    ins_attribute_parameters_table.cellWidget(0,0).setValue(in_attribute_information['parameters'][1])
                    ins_attribute_parameters_table.cellWidget(0,1).setValue(in_attribute_information['parameters'][2])
            elif in_attribute_information['type'] == 'solid':
                pass
            else:
                pass

class _CreateInstancesDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_parts_name:list,in_exist_instances_name:str):
        super().__init__(parent=in_parent,modal=True)
        
        self.__parts_name_list = in_parts_name
        self.__exist_instances_name_list = in_exist_instances_name
        
        self.setWindowTitle(f'Create Instances')
        self.setMinimumSize(500,340)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeSelectionList(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)
        
        self.__instances_by_part_dict = {}

    def __initializeSelectionList(self, in_ins_dialog_layout:object) -> None:
        ins_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_selection_layout,1)
        
        ins_parts_name_list = QtWidgets.QListWidget(self)
        ins_parts_name_list.setObjectName('parts-name-list')
        ins_parts_name_list.addItems(self.__parts_name_list)
        ins_parts_name_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        ins_selection_layout.addWidget(ins_parts_name_list,1)
        
        ins_buttons_layout = QtWidgets.QVBoxLayout()
        ins_selection_layout.addLayout(ins_buttons_layout,0)
        ins_buttons_layout.addStretch()
        ins_import_instance_button = QtWidgets.QPushButton('>>',self)
        ins_import_instance_button.clicked.connect(self.__slotImportInstances)
        ins_buttons_layout.addWidget(ins_import_instance_button)
        ins_output_instance_button = QtWidgets.QPushButton('<<',self)
        ins_buttons_layout.addSpacing(30)
        ins_output_instance_button.clicked.connect(self.__slotRemoveInstances)
        ins_buttons_layout.addWidget(ins_output_instance_button)
        ins_buttons_layout.addStretch()

        ins_instances_name_list = QtWidgets.QListWidget(self)
        ins_instances_name_list.setObjectName('instances-name-list')
        ins_instances_name_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        ins_selection_layout.addWidget(ins_instances_name_list,1)
    # region
    def __slotImportInstances(self) -> None:
        ins_instances_name_list = self.findChild(QtWidgets.QListWidget,'instances-name-list')
        imported_instances_name_list = []
        for item_index in range(ins_instances_name_list.count()):
            ins_instances_name_item = ins_instances_name_list.item(item_index)
            imported_instances_name_list.append(ins_instances_name_item.text())
        
        ins_parts_name_list = self.findChild(QtWidgets.QListWidget,'parts-name-list')
        for ins_part_name_item in ins_parts_name_list.selectedItems():
            imported_part_name = ins_part_name_item.text()
            
            instance_number = 1
            while True:
                instance_name = imported_part_name + '_' + str(instance_number)
                
                if instance_name in self.__exist_instances_name_list:
                    instance_number += 1
                elif instance_name in imported_instances_name_list:
                    instance_number += 1
                else:
                    ins_instances_name_list.addItem(instance_name)
                    
                    if imported_part_name in self.__instances_by_part_dict:
                        self.__instances_by_part_dict[imported_part_name].append(instance_name)
                    else:
                        self.__instances_by_part_dict[imported_part_name] = [instance_name]

                    break
    
    def __slotRemoveInstances(self) -> None:
        ins_instances_name_list = self.findChild(QtWidgets.QListWidget,'instances-name-list')

        remvoe_instances_row_index_list = [ins_instances_name_list.row(ins_instance_name_item) for ins_instance_name_item in ins_instances_name_list.selectedItems()]
        remvoe_instances_row_index_list.sort()
        remvoe_instances_row_index_list.reverse()
        for row_index in remvoe_instances_row_index_list:
            remove_instance_item = ins_instances_name_list.takeItem(row_index)
            removed_instance_name = remove_instance_item.text()
            del remove_instance_item
            
            for part_name in self.__instances_by_part_dict:
                if removed_instance_name in self.__instances_by_part_dict[part_name]:
                    self.__instances_by_part_dict[part_name].remove(removed_instance_name)
                    
                    if self.__instances_by_part_dict[part_name] == []:
                        del self.__instances_by_part_dict[part_name]
                    else:
                        pass
                    
                    break
                else:
                    continue
    # endregion
    
    def __initializeUserButton(self, in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.clicked.connect(self.accept)
        ins_button_layout.addWidget(ins_accept_button)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getInstancesInformation(self) -> dict:
        return self.__instances_by_part_dict
class _EditInstanceOrientation(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_model_dimension:str, in_instance_name:str, in_exist_assembly_coordinate_systems_name:list):
        super().__init__(parent=in_parent,modal=False)
        
        self.__model_name = self.parent().objectName()
        self.__model_dimension = in_model_dimension
        self.__instance_name = in_instance_name
        self.__exist_assembly_coordinate_systems_name_list = in_exist_assembly_coordinate_systems_name
        
        self.setWindowTitle(f'Edit Instance Orientation')
        self.setFixedHeight(120)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeReferenceCoordinateSystemSelection(ins_dialog_layout)
        self.__initializeTranslationSelection(ins_dialog_layout)
        self.__initializeRotationSelection(ins_dialog_layout)
        
    def __initializeReferenceCoordinateSystemSelection(self, in_ins_dialog_layout:object) -> None:
        ins_coordinate_systems_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_coordinate_systems_layout,1)
        
        ins_coordinate_system_label = QtWidgets.QLabel(self, text='Coordiante System:',alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_coordinate_system_label.setFixedSize(140,30)
        ins_coordinate_systems_layout.addWidget(ins_coordinate_system_label,0)
        
        ins_coordinate_system_box = QtWidgets.QComboBox(self)
        ins_coordinate_system_box.setObjectName('coordiante-systems-box')
        ins_coordinate_system_box.setFixedHeight(30)
        ins_coordinate_system_box.addItems(self.__exist_assembly_coordinate_systems_name_list)
        ins_coordinate_systems_layout.addWidget(ins_coordinate_system_box,1)
        
    def __initializeTranslationSelection(self, in_ins_dialog_layout:object) -> None:
        ins_translation_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_translation_layout,0)
        
        ins_translation_label = QtWidgets.QLabel(self, text='Translation:',alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_translation_label.setFixedSize(140,30)
        ins_translation_layout.addWidget(ins_translation_label,0)

        ins_translation_direction_box = QtWidgets.QComboBox(self)
        ins_translation_direction_box.setObjectName('translation-directions-box')
        ins_translation_direction_box.setFixedSize(40,30)
        if self.__model_dimension == '2D':
            ins_translation_direction_box.addItems(['1','2'])
        elif self.__model_dimension == '3D':
            ins_translation_direction_box.addItems(['1','2','3'])
        else:
            pass
        ins_translation_layout.addWidget(ins_translation_direction_box,1)
    
        ins_translation_value_edit = QtWidgets.QLineEdit(self)
        ins_translation_value_edit.setObjectName('translation-value-edit')
        ins_translation_value_edit.setFixedHeight(30)
        ins_translation_value_edit.setMaxLength(20)
        ins_translation_value_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_translation_layout.addWidget(ins_translation_value_edit,1)
    
        ins_translation_apply_button = QtWidgets.QPushButton("Accept")
        ins_translation_apply_button.setFixedSize(80,30)
        ins_translation_apply_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_translation_apply_button.clicked.connect(self.__slotTranslateInstance)
        ins_translation_layout.addWidget(ins_translation_apply_button,0)
    # region
    def __slotTranslateInstance(self) -> None:
        assembly_coordinate_system_name = self.findChild(QtWidgets.QComboBox,'coordiante-systems-box').currentText()
        translation_direction = self.findChild(QtWidgets.QComboBox,'translation-directions-box').currentText()
        translation_value_string = self.findChild(QtWidgets.QLineEdit,'translation-value-edit').text()
        if translation_value_string == '':
            translation_value = 0.0
        else:
            translation_value = float(translation_value_string)
        
        ins_main_window = self.parent().parent().parent().parent().parent().parent()
        assembly_coordinate_system_info_dict = ins_main_window.ins_project_database.getAssemblyCoordinateSystemInfo(self.__model_name, assembly_coordinate_system_name)
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.__model_name)
        ins_model_visual_window.editInstanceOrientationOfAssemblyViewport(self.__instance_name,'translate',assembly_coordinate_system_info_dict,translation_direction,translation_value)
        ins_main_window.ins_project_database.editInstanceOrientation(self.__model_name,self.__instance_name,'translate',assembly_coordinate_system_info_dict,translation_direction,translation_value)
    # endregion
    
    def __initializeRotationSelection(self, in_ins_dialog_layout:object) -> None:
        ins_rotation_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_rotation_layout,0)
        
        ins_rotation_label = QtWidgets.QLabel(self, text='Rotation:',alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_rotation_label.setFixedSize(140,30)
        ins_rotation_layout.addWidget(ins_rotation_label,0)

        ins_rotation_direction_box = QtWidgets.QComboBox(self)
        ins_rotation_direction_box.setObjectName('rotation-directions-box')
        ins_rotation_direction_box.setFixedSize(40,30)
        if self.__model_dimension == '2D':
            ins_rotation_direction_box.addItems(['3'])
        elif self.__model_dimension == '3D':
            ins_rotation_direction_box.addItems(['1','2','3'])
        else:
            pass
        ins_rotation_layout.addWidget(ins_rotation_direction_box,1)
    
        ins_rotation_value_edit = QtWidgets.QLineEdit(self)
        ins_rotation_value_edit.setObjectName('rotation-value-edit')
        ins_rotation_value_edit.setFixedHeight(30)
        ins_rotation_value_edit.setMaxLength(20)
        ins_rotation_value_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_rotation_value_edit.setPlaceholderText('degree')
        ins_rotation_layout.addWidget(ins_rotation_value_edit,1)
        
        ins_rotation_apply_button = QtWidgets.QPushButton("Accept")
        ins_rotation_apply_button.setFixedSize(80,30)
        ins_rotation_apply_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_rotation_apply_button.clicked.connect(self.__slotRotateInstance)
        ins_rotation_layout.addWidget(ins_rotation_apply_button,0)
    # region
    def __slotRotateInstance(self) -> None:
        assembly_coordinate_system_name = self.findChild(QtWidgets.QComboBox,'coordiante-systems-box').currentText()
        rotation_direction = self.findChild(QtWidgets.QComboBox,'rotation-directions-box').currentText()
        rotation_value_string = self.findChild(QtWidgets.QLineEdit,'rotation-value-edit').text()
        if rotation_value_string == '':
            rotation_value = 0.0
        else:
            rotation_value = float(rotation_value_string)

        ins_main_window = self.parent().parent().parent().parent().parent().parent()
        assembly_coordinate_system_info_dict = ins_main_window.ins_project_database.getAssemblyCoordinateSystemInfo(self.__model_name, assembly_coordinate_system_name)
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.__model_name)
        ins_model_visual_window.editInstanceOrientationOfAssemblyViewport(self.__instance_name,'rotate',assembly_coordinate_system_info_dict,rotation_direction,rotation_value)
        ins_main_window.ins_project_database.editInstanceOrientation(self.__model_name,self.__instance_name,'rotate',assembly_coordinate_system_info_dict,rotation_direction,rotation_value)
    # endregion
class _CreateAssemblyGroupFromPart(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_groups_name:str, instances_include_part_groups:dict,):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_groups_name_list = in_exist_groups_name
        self.__instances_include_part_groups_dict = instances_include_part_groups
        
        self.setWindowTitle(f'Create Assembly Group')
        self.setFixedHeight(120)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeNameEdit(ins_dialog_layout)
        self.__initializeInstancesSelection(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)

    def __initializeNameEdit(self, in_ins_dialog_layout:object) -> None:
        ins_group_name_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_group_name_layout,0)
        
        ins_group_name_label = QtWidgets.QLabel('Group Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_group_name_label.setFixedSize(90,30)
        ins_group_name_layout.addWidget(ins_group_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('group-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Group_','G_','group-','g-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckGroupName)
        ins_group_name_layout.addWidget(ins_name_line_edit,1)        
    # region
    def __slotCheckGroupName(self, in_group_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        if in_group_name == '' or in_group_name in self.__exist_groups_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion
    
    def __initializeInstancesSelection(self, in_ins_dialog_layout:object) -> None:
        ins_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_selection_layout,0)
        
        ins_instance_label = QtWidgets.QLabel('instance:',self,alignment=QtCore.Qt.AlignCenter)
        ins_instance_label.setFixedSize(85,30)
        ins_selection_layout.addWidget(ins_instance_label,0)
        ins_instances_box = QtWidgets.QComboBox(self)
        ins_instances_box.setObjectName('instances-box')
        ins_instances_box.setFixedHeight(30)
        ins_instances_box.currentTextChanged.connect(self.__slotSwitchInstance)
        ins_selection_layout.addWidget(ins_instances_box,1)
        
        ins_part_group_label = QtWidgets.QLabel('part group:',self,alignment=QtCore.Qt.AlignCenter)
        ins_part_group_label.setFixedSize(100,30)
        ins_selection_layout.addWidget(ins_part_group_label,0)
        ins_part_groups_box = QtWidgets.QComboBox(self)
        ins_part_groups_box.setObjectName('part-groups-box')
        ins_part_groups_box.setFixedHeight(30)
        ins_selection_layout.addWidget(ins_part_groups_box,1)
        
        ins_instances_box.addItems(list(self.__instances_include_part_groups_dict.keys()))
    # region
    def __slotSwitchInstance(self, in_instance_name:str) -> None:
        ins_part_groups_box = self.findChild(QtWidgets.QComboBox,'part-groups-box')
        ins_part_groups_box.clear()
        ins_part_groups_box.addItems(self.__instances_include_part_groups_dict[in_instance_name])
    # endregion

    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
    
    def getGroupsInfomation(self) -> list:
        assembly_group_name = self.findChild(QtWidgets.QLineEdit,'group-name-edit').text()
        instance_name = self.findChild(QtWidgets.QComboBox,'instances-box').currentText()
        part_group_name = self.findChild(QtWidgets.QComboBox,'part-groups-box').currentText()
        
        return [assembly_group_name,instance_name,part_group_name]
class _CreateAssemblyCoordinateSystem(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_model_dimension:str, in_exist_coordinate_systems_name_list:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__model_name = self.parent().objectName()
        self.__model_dimension = in_model_dimension
        self.__exist_coordinate_systems_name_list = in_exist_coordinate_systems_name_list
        
        self.setWindowTitle('Create Assembly Coordinate System')
        self.setFixedHeight(300)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeNameEdit(ins_dialog_layout)
        self.__initializeTypeAndMethod(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)
        
    def __initializeNameEdit(self, in_ins_dialog_layout:object) -> None:
        ins_coordinate_system_name_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_coordinate_system_name_layout)
        
        ins_coordinate_system_name_label = QtWidgets.QLabel('Coordinate System Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_coordinate_system_name_label.setFixedSize(180,30)
        ins_coordinate_system_name_layout.addWidget(ins_coordinate_system_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('assembly-csys-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['CSYS_','csys_'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckCoordinateSystemName)
        ins_coordinate_system_name_layout.addWidget(ins_name_line_edit,1)
    # region
    def __slotCheckCoordinateSystemName(self, in_coordinate_system_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        if in_coordinate_system_name == '' or in_coordinate_system_name in self.__exist_coordinate_systems_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion  
    
    def __initializeTypeAndMethod(self,in_ins_dialog_layout:object) -> None:
        ins_type_and_method_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_type_and_method_layout)
        
        ins_coordinate_system_type_label = QtWidgets.QLabel('Type:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_coordinate_system_type_label.setFixedSize(40,30)
        ins_type_and_method_layout.addWidget(ins_coordinate_system_type_label)
        ins_coordinate_system_type_box = QtWidgets.QComboBox(self)
        ins_coordinate_system_type_box.setObjectName('csys-type-box')
        ins_coordinate_system_type_box.setFixedSize(110,30)
        ins_coordinate_system_type_box.addItems(['rectangular','cylindrical','spherical'])
        ins_type_and_method_layout.addWidget(ins_coordinate_system_type_box)
        
        ins_coordinate_system_method_label = QtWidgets.QLabel('Method:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_coordinate_system_method_label.setFixedSize(60,30)
        ins_type_and_method_layout.addWidget(ins_coordinate_system_method_label)
        ins_coordinate_system_methods_box = QtWidgets.QComboBox(self)
        ins_coordinate_system_methods_box.setObjectName('csys-methods-box')
        ins_coordinate_system_methods_box.setFixedSize(100,30)
        ins_coordinate_system_methods_box.addItems(['3 points','offset'])
        ins_coordinate_system_methods_box.currentIndexChanged.connect(self.__slotSwitchMethod)
        ins_type_and_method_layout.addWidget(ins_coordinate_system_methods_box)
        
        ins_type_and_method_layout.addStretch()
        
        ins_methods_stacked_layout = QtWidgets.QStackedLayout()
        ins_methods_stacked_layout.setObjectName('methods-stacked-layout')
        in_ins_dialog_layout.addLayout(ins_methods_stacked_layout)
        
        ins_method_3_points_widget = QtWidgets.QWidget(self)
        # region
        ins_method_3_points_widget.setObjectName('widget-with-border')
        
        ins_3_points_widget_layout = QtWidgets.QVBoxLayout()
        ins_method_3_points_widget.setLayout(ins_3_points_widget_layout)
        
        ins_from_selected_3nodes_button = QtWidgets.QPushButton('from selcted 3 nodes',ins_method_3_points_widget)
        ins_from_selected_3nodes_button.setFixedHeight(30)
        ins_from_selected_3nodes_button.setFocusPolicy((QtCore.Qt.NoFocus))
        ins_from_selected_3nodes_button.clicked.connect(self.__slotGetPointsFrom3Nodes)
        ins_3_points_widget_layout.addWidget(ins_from_selected_3nodes_button)
        
        ins_point1_layout = QtWidgets.QHBoxLayout()
        ins_3_points_widget_layout.addLayout(ins_point1_layout)
        ins_point1_label = QtWidgets.QLabel('Point1:',ins_method_3_points_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_point1_label.setFixedSize(60,30)
        ins_point1_layout.addWidget(ins_point1_label)
        ins_point1_x_edit = QtWidgets.QLineEdit(ins_method_3_points_widget)
        ins_point1_x_edit.setObjectName('point1-x-edit')
        ins_point1_x_edit.setFixedHeight(30)
        ins_point1_x_edit.setMinimumWidth(100)
        ins_point1_x_edit.setMaxLength(20)
        ins_point1_x_edit.setPlaceholderText('X')
        ins_point1_x_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_point1_layout.addWidget(ins_point1_x_edit,1)
        ins_point1_y_edit = QtWidgets.QLineEdit(ins_method_3_points_widget)
        ins_point1_y_edit.setObjectName('point1-y-edit')
        ins_point1_y_edit.setFixedHeight(30)
        ins_point1_y_edit.setMinimumWidth(100)
        ins_point1_y_edit.setMaxLength(20)
        ins_point1_y_edit.setPlaceholderText('Y')
        ins_point1_y_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_point1_layout.addWidget(ins_point1_y_edit,1)
        ins_point1_z_edit = QtWidgets.QLineEdit(ins_method_3_points_widget)
        ins_point1_z_edit.setObjectName('point1-z-edit')
        ins_point1_z_edit.setFixedHeight(30)
        ins_point1_z_edit.setMinimumWidth(100)
        ins_point1_z_edit.setMaxLength(20)
        ins_point1_z_edit.setPlaceholderText('Z')
        ins_point1_z_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        if self.__model_dimension == '2D':
            ins_point1_z_edit.setText('0.0')
            ins_point1_z_edit.setEnabled(False)
        else:
            pass
        ins_point1_layout.addWidget(ins_point1_z_edit,1)
        
        ins_point2_layout = QtWidgets.QHBoxLayout()
        ins_3_points_widget_layout.addLayout(ins_point2_layout)
        ins_point2_label = QtWidgets.QLabel('Point2:',ins_method_3_points_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_point2_label.setFixedSize(60,30)
        ins_point2_layout.addWidget(ins_point2_label)
        ins_point2_x_edit = QtWidgets.QLineEdit(ins_method_3_points_widget)
        ins_point2_x_edit.setObjectName('point2-x-edit')
        ins_point2_x_edit.setFixedHeight(30)
        ins_point2_x_edit.setMinimumWidth(100)
        ins_point2_x_edit.setMaxLength(20)
        ins_point2_x_edit.setPlaceholderText('X')
        ins_point2_x_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_point2_layout.addWidget(ins_point2_x_edit,1)
        ins_point2_y_edit = QtWidgets.QLineEdit(ins_method_3_points_widget)
        ins_point2_y_edit.setObjectName('point2-y-edit')
        ins_point2_y_edit.setFixedHeight(30)
        ins_point2_y_edit.setMinimumWidth(100)
        ins_point2_y_edit.setMaxLength(20)
        ins_point2_y_edit.setPlaceholderText('Y')
        ins_point2_y_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_point2_layout.addWidget(ins_point2_y_edit,1)
        ins_point2_z_edit = QtWidgets.QLineEdit(ins_method_3_points_widget)
        ins_point2_z_edit.setObjectName('point2-z-edit')
        ins_point2_z_edit.setFixedHeight(30)
        ins_point2_z_edit.setMinimumWidth(100)
        ins_point2_z_edit.setMaxLength(20)
        ins_point2_z_edit.setPlaceholderText('Z')
        ins_point2_z_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        if self.__model_dimension == '2D':
            ins_point2_z_edit.setText('0.0')
            ins_point2_z_edit.setEnabled(False)
        else:
            pass
        ins_point2_layout.addWidget(ins_point2_z_edit,1)
        
        ins_point3_layout = QtWidgets.QHBoxLayout()
        ins_3_points_widget_layout.addLayout(ins_point3_layout)
        ins_point3_label = QtWidgets.QLabel('Point3:',ins_method_3_points_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_point3_label.setFixedSize(60,30)
        ins_point3_layout.addWidget(ins_point3_label)
        ins_point3_x_edit = QtWidgets.QLineEdit(ins_method_3_points_widget)
        ins_point3_x_edit.setObjectName('point3-x-edit')
        ins_point3_x_edit.setFixedHeight(30)
        ins_point3_x_edit.setMinimumWidth(100)
        ins_point3_x_edit.setMaxLength(20)
        ins_point3_x_edit.setPlaceholderText('X')
        ins_point3_x_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_point3_layout.addWidget(ins_point3_x_edit,1)
        ins_point3_y_edit = QtWidgets.QLineEdit(ins_method_3_points_widget)
        ins_point3_y_edit.setObjectName('point3-y-edit')
        ins_point3_y_edit.setFixedHeight(30)
        ins_point3_y_edit.setMinimumWidth(100)
        ins_point3_y_edit.setMaxLength(20)
        ins_point3_y_edit.setPlaceholderText('Y')
        ins_point3_y_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_point3_layout.addWidget(ins_point3_y_edit,1)
        ins_point3_z_edit = QtWidgets.QLineEdit(ins_method_3_points_widget)
        ins_point3_z_edit.setObjectName('point3-z-edit')
        ins_point3_z_edit.setFixedHeight(30)
        ins_point3_z_edit.setMinimumWidth(100)
        ins_point3_z_edit.setMaxLength(20)
        ins_point3_z_edit.setPlaceholderText('Z')
        ins_point3_z_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        if self.__model_dimension == '2D':
            ins_point3_z_edit.setText('0.0')
            ins_point3_z_edit.setEnabled(False)
        else:
            pass
        ins_point3_layout.addWidget(ins_point3_z_edit,1)
        
        ins_3_points_widget_layout.addStretch()
        # endregion
        ins_methods_stacked_layout.addWidget(ins_method_3_points_widget)
        
        ins_method_offset_widget = QtWidgets.QWidget(self)
        # region
        ins_method_offset_widget.setObjectName('widget-with-border')
        
        ins_offset_widget_layout = QtWidgets.QVBoxLayout()
        ins_method_offset_widget.setLayout(ins_offset_widget_layout)
        
        ins_reference_coordinate_system_layout = QtWidgets.QHBoxLayout()
        ins_offset_widget_layout.addLayout(ins_reference_coordinate_system_layout)
        ins_reference_coordinate_system_label = QtWidgets.QLabel('Reference:',ins_method_offset_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_reference_coordinate_system_label.setFixedSize(85,30)
        ins_reference_coordinate_system_layout.addWidget(ins_reference_coordinate_system_label)
        ins_reference_coordinate_systems_box = QtWidgets.QComboBox(ins_method_offset_widget)
        ins_reference_coordinate_systems_box.setObjectName('reference-csys-box')
        ins_reference_coordinate_systems_box.setFixedSize(150,30)
        ins_reference_coordinate_systems_box.addItems(self.__exist_coordinate_systems_name_list)
        ins_reference_coordinate_system_layout.addWidget(ins_reference_coordinate_systems_box,1)
        ins_reference_coordinate_system_layout.addStretch()
        
        ins_movement_setting_layout = QtWidgets.QHBoxLayout()
        ins_offset_widget_layout.addLayout(ins_movement_setting_layout)
        ins_move_to_label = QtWidgets.QLabel('Move to:',ins_method_offset_widget,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        ins_move_to_label.setFixedSize(75,30)
        ins_movement_setting_layout.addWidget(ins_move_to_label)
        ins_selected_node_button = QtWidgets.QPushButton('selected node',ins_method_offset_widget)
        ins_selected_node_button.setFixedSize(115,30)
        ins_selected_node_button.setFocusPolicy((QtCore.Qt.NoFocus))
        ins_selected_node_button.clicked.connect(self.__slotGetPointFromNode)
        ins_movement_setting_layout.addWidget(ins_selected_node_button)
        ins_point_x_edit = QtWidgets.QLineEdit(ins_method_offset_widget)
        ins_point_x_edit.setObjectName('point-x-edit')
        ins_point_x_edit.setFixedHeight(30)
        ins_point_x_edit.setMinimumWidth(100)
        ins_point_x_edit.setMaxLength(20)
        ins_point_x_edit.setPlaceholderText('X')
        ins_point_x_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_movement_setting_layout.addWidget(ins_point_x_edit,1)
        ins_point_y_edit = QtWidgets.QLineEdit(ins_method_offset_widget)
        ins_point_y_edit.setObjectName('point-y-edit')
        ins_point_y_edit.setFixedHeight(30)
        ins_point_y_edit.setMinimumWidth(100)
        ins_point_y_edit.setMaxLength(20)
        ins_point_y_edit.setPlaceholderText('Y')
        ins_point_y_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_movement_setting_layout.addWidget(ins_point_y_edit,1)
        ins_point_z_edit = QtWidgets.QLineEdit(ins_method_offset_widget)
        ins_point_z_edit.setObjectName('point-z-edit')
        ins_point_z_edit.setFixedHeight(30)
        ins_point_z_edit.setMinimumWidth(100)
        ins_point_z_edit.setMaxLength(20)
        ins_point_z_edit.setPlaceholderText('Z')
        ins_point_z_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        if self.__model_dimension == '2D':
            ins_point_z_edit.setText('0.0')
            ins_point_z_edit.setEnabled(False)
        else:
            pass
        ins_movement_setting_layout.addWidget(ins_point_z_edit,1)
        
        ins_offset_widget_layout.addStretch()
        # endregion
        ins_methods_stacked_layout.addWidget(ins_method_offset_widget)
    # region
    def __slotSwitchMethod(self, in_method_index:str) -> None:
        ins_methods_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'methods-stacked-layout')
        ins_methods_stacked_layout.setCurrentIndex(in_method_index)
    
    def __slotGetPointsFrom3Nodes(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent().parent()
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.__model_name)
        nodes_selection_dict = ins_model_visual_window.getSelectionFromViewport()
        if nodes_selection_dict == {}:
            QtWidgets.QMessageBox.warning(self,'Create Assembly Coordinate System Waring','None selected node!')
            return None
        else:
            pass
        
        selected_nodes_number = 0
        for labels_list in nodes_selection_dict.values():
            selected_nodes_number += len(labels_list)
        if selected_nodes_number < 3:
            QtWidgets.QMessageBox.warning(self,'Create Assembly Coordinate System Waring','The number of selected nodes must be 3!')
            return None
        else:
            pass
        
        selection_include_3_nodes_dict = {}
        selected_nodes_number = 0
        for instacne_name,labels_list in nodes_selection_dict.items(): 
            for label in labels_list:
                if instacne_name in selection_include_3_nodes_dict:
                    selection_include_3_nodes_dict[instacne_name].append(label)
                else:
                    selection_include_3_nodes_dict[instacne_name] = [label]
                
                selected_nodes_number += 1
                
                if selected_nodes_number == 3:
                    break
                else:
                    pass
            
            if selected_nodes_number == 3:
                    break
            else:
                pass

        del nodes_selection_dict
        selected_nodes_coordinates_list = ins_main_window.ins_project_database.getAssemblyNodesCooridnates(self.__model_name,selection_include_3_nodes_dict)
        
        self.findChild(QtWidgets.QLineEdit,'point1-x-edit').setText(str(selected_nodes_coordinates_list[0][0]))
        self.findChild(QtWidgets.QLineEdit,'point1-y-edit').setText(str(selected_nodes_coordinates_list[0][1]))
        self.findChild(QtWidgets.QLineEdit,'point2-x-edit').setText(str(selected_nodes_coordinates_list[1][0]))
        self.findChild(QtWidgets.QLineEdit,'point2-y-edit').setText(str(selected_nodes_coordinates_list[1][1]))
        self.findChild(QtWidgets.QLineEdit,'point3-x-edit').setText(str(selected_nodes_coordinates_list[2][0]))
        self.findChild(QtWidgets.QLineEdit,'point3-y-edit').setText(str(selected_nodes_coordinates_list[2][1]))
        if self.__model_dimension == '2D':
            self.findChild(QtWidgets.QLineEdit,'point1-z-edit').setText(str(selected_nodes_coordinates_list[0][2]))
            self.findChild(QtWidgets.QLineEdit,'point2-z-edit').setText(str(selected_nodes_coordinates_list[1][2]))
            self.findChild(QtWidgets.QLineEdit,'point3-z-edit').setText(str(selected_nodes_coordinates_list[2][2]))
        else:
            pass
    
    def __slotGetPointFromNode(self) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent().parent()
        
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.__model_name)
        nodes_selection_dict = ins_model_visual_window.getSelectionFromViewport()
        if nodes_selection_dict == {}:
            QtWidgets.QMessageBox.warning(self,'Create Assembly Coordinate System Waring','None selected node!')
            return None
        else:
            pass
        
        selected_nodes_number = 0
        for labels_list in nodes_selection_dict.values():
            selected_nodes_number += len(labels_list)
        if selected_nodes_number < 1:
            QtWidgets.QMessageBox.warning(self,'Create Assembly Coordinate System Waring','None selected node!')
            return None
        else:
            pass
        
        selection_include_node_dict = {}
        selected_nodes_number = 0
        for instacne_name,labels_list in nodes_selection_dict.items(): 
            for label in labels_list:
                if instacne_name in selection_include_node_dict:
                    selection_include_node_dict[instacne_name].append(label)
                else:
                    selection_include_node_dict[instacne_name] = [label]
                
                selected_nodes_number += 1
                
                if selected_nodes_number == 1:
                    break
                else:
                    pass
            
            if selected_nodes_number == 1:
                    break
            else:
                pass

        selected_nodes_coordinates_list = ins_main_window.ins_project_database.getAssemblyNodesCooridnates(self.__model_name,selection_include_node_dict)
        self.findChild(QtWidgets.QLineEdit,'point-x-edit').setText(str(selected_nodes_coordinates_list[0][0]))
        self.findChild(QtWidgets.QLineEdit,'point-y-edit').setText(str(selected_nodes_coordinates_list[0][1]))
        if self.__model_dimension == '2D':
            self.findChild(QtWidgets.QLineEdit,'point-z-edit').setText(str(selected_nodes_coordinates_list[0][2]))
        else:
            pass
    # endregion
    
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)
    
    def getAssemblyCoordinateSystemInformation(self) -> dict:
        coordinate_system_information_dict = {}
        
        coordinate_system_information_dict['name'] = self.findChild(QtWidgets.QLineEdit,'assembly-csys-name-edit').text()
        coordinate_system_information_dict['type'] = self.findChild(QtWidgets.QComboBox,'csys-type-box').currentText()
        coordinate_system_information_dict['method'] = self.findChild(QtWidgets.QComboBox,'csys-methods-box').currentText()

        if coordinate_system_information_dict['method'] == '3 points':
            coordinate_system_information_dict['parameters'] = [[],[],[]]
            coordinate_system_information_dict['parameters'][0].append(self.findChild(QtWidgets.QLineEdit,'point1-x-edit').text())
            coordinate_system_information_dict['parameters'][0].append(self.findChild(QtWidgets.QLineEdit,'point1-y-edit').text())
            coordinate_system_information_dict['parameters'][0].append(self.findChild(QtWidgets.QLineEdit,'point1-z-edit').text())
            coordinate_system_information_dict['parameters'][1].append(self.findChild(QtWidgets.QLineEdit,'point2-x-edit').text())
            coordinate_system_information_dict['parameters'][1].append(self.findChild(QtWidgets.QLineEdit,'point2-y-edit').text())
            coordinate_system_information_dict['parameters'][1].append(self.findChild(QtWidgets.QLineEdit,'point2-z-edit').text())
            coordinate_system_information_dict['parameters'][2].append(self.findChild(QtWidgets.QLineEdit,'point3-x-edit').text())
            coordinate_system_information_dict['parameters'][2].append(self.findChild(QtWidgets.QLineEdit,'point3-y-edit').text())
            coordinate_system_information_dict['parameters'][2].append(self.findChild(QtWidgets.QLineEdit,'point3-z-edit').text())
        elif coordinate_system_information_dict['method'] == 'offset':
            coordinate_system_information_dict['parameters'] = [None,[]]
            
            coordinate_system_information_dict['parameters'][0] = self.findChild(QtWidgets.QComboBox,'reference-csys-box').currentText()
            coordinate_system_information_dict['parameters'][1].append(self.findChild(QtWidgets.QLineEdit,'point-x-edit').text())
            coordinate_system_information_dict['parameters'][1].append(self.findChild(QtWidgets.QLineEdit,'point-y-edit').text())
            coordinate_system_information_dict['parameters'][1].append(self.findChild(QtWidgets.QLineEdit,'point-z-edit').text())
        else:
            pass

        return coordinate_system_information_dict

class _CreateStepDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_steps_name:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_steps_name_list = in_exist_steps_name
        
        self.setWindowTitle(f'Create Step')
        self.setFixedHeight(350)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeNameEdit(ins_dialog_layout)
        self.__initializeParametersWidget(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)

    def __initializeNameEdit(self, in_ins_dialog_layout:object) -> None:
        ins_group_name_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_group_name_layout,0)
        
        ins_step_name_label = QtWidgets.QLabel('Step Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_step_name_label.setFixedSize(80,30)
        ins_group_name_layout.addWidget(ins_step_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('step-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Step_','S_','Step-','step-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckStepName)
        ins_group_name_layout.addWidget(ins_name_line_edit,1)        
    # region
    def __slotCheckStepName(self, in_step_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        if in_step_name == '':
            ins_accept_button.setEnabled(False)
        elif in_step_name.lower() == 'initial':
            ins_accept_button.setEnabled(False)
        elif in_step_name in self.__exist_steps_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion
    
    def __initializeParametersWidget(self,in_ins_dialog_layout:object) -> None:
        in_ins_dialog_layout.addSpacing(10)
        
        ins_split_line = QtWidgets.QFrame(parent=self,frameShape=QtWidgets.QFrame.Shape.HLine)
        ins_split_line.setLineWidth(1)
        in_ins_dialog_layout.addWidget(ins_split_line,0)
        
        ins_setp_type_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_setp_type_layout)
        
        ins_step_type_label = QtWidgets.QLabel('Type',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_step_type_label.setFixedSize(40,30)
        ins_setp_type_layout.addWidget(ins_step_type_label,0)
        ins_step_type_box = QtWidgets.QComboBox(self)
        ins_step_type_box.setFixedSize(100,30)
        ins_step_type_box.setObjectName('step-type-box')
        ins_step_type_box.currentIndexChanged.connect(self.__slotSwitchStepType)
        ins_setp_type_layout.addWidget(ins_step_type_box,0)
        ins_setp_type_layout.addStretch()
        
        ins_step_type_stacked_layout = QtWidgets.QStackedLayout()
        ins_step_type_stacked_layout.setObjectName('step-type-stacked-layout')
        in_ins_dialog_layout.addLayout(ins_step_type_stacked_layout,1)
        
        ins_static_step_widget = self.__initializeStaticStepWidget()
        ins_step_type_stacked_layout.addWidget(ins_static_step_widget)
        
        ins_step_type_box.addItems(['static'])
    # region
    def __slotSwitchStepType(self,in_step_index:str) -> None:
        ins_step_type_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'step-type-stacked-layout')
        ins_step_type_stacked_layout.setCurrentIndex(in_step_index)
    
    def __initializeStaticStepWidget(self) -> object:
        ins_static_step_widget = QtWidgets.QWidget(self)
        
        ins_params_layput = QtWidgets.QVBoxLayout()
        ins_params_layput.setContentsMargins(0,0,0,0)
        ins_static_step_widget.setLayout(ins_params_layput)
        
        ins_layout1 = QtWidgets.QHBoxLayout()
        ins_params_layput.addLayout(ins_layout1)
        ins_time_label = QtWidgets.QLabel('time:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_time_label.setFixedSize(40,30)
        ins_layout1.addWidget(ins_time_label,0)
        ins_time_edit = QtWidgets.QLineEdit(self)
        ins_time_edit.setObjectName('step-time-edit')
        ins_time_edit.setFixedHeight(30)
        ins_time_edit.setMaxLength(12)
        ins_time_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_FLOAT_FORMAT)))
        ins_layout1.addWidget(ins_time_edit,1)
        ins_nlgeom_label = QtWidgets.QLabel('nlgeom',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_nlgeom_label.setFixedSize(60,30)
        ins_layout1.addWidget(ins_nlgeom_label,0)
        ins_nlgeom_check_box = QtWidgets.QCheckBox(self)
        ins_nlgeom_check_box.setObjectName('step-nlgeom-box')
        ins_nlgeom_check_box.setFixedSize(30,30)
        ins_nlgeom_check_box.setEnabled(False)
        ins_layout1.addWidget(ins_nlgeom_check_box,0)
        
        ins_layout2 = QtWidgets.QHBoxLayout()
        ins_params_layput.addLayout(ins_layout2)
        ins_maximum_increments_number_label = QtWidgets.QLabel('increments number ≤',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_maximum_increments_number_label.setFixedSize(150,30)
        ins_layout2.addWidget(ins_maximum_increments_number_label,0)
        ins_maximum_increments_number_edit = QtWidgets.QLineEdit(self)
        ins_maximum_increments_number_edit.setObjectName('increments-number-edit')
        ins_maximum_increments_number_edit.setFixedHeight(30)
        ins_maximum_increments_number_edit.setMaxLength(4)
        ins_maximum_increments_number_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_INTEGER_FORMAT)))
        ins_maximum_increments_number_edit.setText('100')
        ins_layout2.addWidget(ins_maximum_increments_number_edit,1)
        
        ins_layout3 = QtWidgets.QHBoxLayout()
        ins_params_layput.addLayout(ins_layout3)
        ins_increment_type_label = QtWidgets.QLabel('increment size type:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_increment_type_label.setFixedSize(150,30)
        ins_layout3.addWidget(ins_increment_type_label,0)
        ins_increment_type_box = QtWidgets.QComboBox(self)
        ins_increment_type_box.setObjectName('increment-type-box')
        ins_increment_type_box.setFixedHeight(30)
        ins_increment_type_box.addItems(['fixed','automatic'])
        ins_increment_type_box.setItemData(1,0,QtCore.Qt.UserRole-1)
        ins_increment_type_box.currentTextChanged.connect(self.__slotChangeIncrementType)
        ins_layout3.addWidget(ins_increment_type_box,1)
        
        ins_layout4 = QtWidgets.QHBoxLayout()
        ins_params_layput.addLayout(ins_layout4)
        ins_increment_size_edit = QtWidgets.QLineEdit(self)
        ins_increment_size_edit.setObjectName('increment-size-edit')
        ins_increment_size_edit.setFixedHeight(30)
        ins_increment_size_edit.setMaxLength(12)
        ins_increment_size_edit.setPlaceholderText('fixed size/initial')
        ins_increment_size_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_FLOAT_FORMAT)))
        ins_layout4.addWidget(ins_increment_size_edit,1)
        ins_increment_minimum_size_edit = QtWidgets.QLineEdit(self)
        ins_increment_minimum_size_edit.setObjectName('increment-minimum-size-edit')
        ins_increment_minimum_size_edit.setFixedHeight(30)
        ins_increment_minimum_size_edit.setMaxLength(12)
        ins_increment_minimum_size_edit.setPlaceholderText('minimum')
        ins_increment_minimum_size_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_FLOAT_FORMAT)))
        ins_increment_minimum_size_edit.setEnabled(False)
        ins_layout4.addWidget(ins_increment_minimum_size_edit,1)
        ins_increment_maximum_size_edit = QtWidgets.QLineEdit(self)
        ins_increment_maximum_size_edit.setObjectName('increment-maximum-size-edit')
        ins_increment_maximum_size_edit.setFixedHeight(30)
        ins_increment_maximum_size_edit.setMaxLength(12)
        ins_increment_maximum_size_edit.setPlaceholderText('maximum')
        ins_increment_maximum_size_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_FLOAT_FORMAT)))
        ins_increment_maximum_size_edit.setEnabled(False)
        ins_layout4.addWidget(ins_increment_maximum_size_edit,1)
        
        ins_layout5 = QtWidgets.QHBoxLayout()
        ins_params_layput.addLayout(ins_layout5)
        ins_linear_equations_solver_label = QtWidgets.QLabel('linear solver:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_linear_equations_solver_label.setFixedSize(90,30)
        ins_layout5.addWidget(ins_linear_equations_solver_label,0)
        ins_linear_equations_solver_type_box = QtWidgets.QComboBox(self)
        ins_linear_equations_solver_type_box.setObjectName('linear-solver-type-box')
        ins_linear_equations_solver_type_box.setFixedSize(80,30)
        ins_linear_equations_solver_type_box.addItems(['direct','iterative'])
        ins_linear_equations_solver_type_box.currentTextChanged.connect(self.__slotChangeLinearSolverType)
        ins_layout5.addWidget(ins_linear_equations_solver_type_box,0)
        ins_linear_equations_solver_box = QtWidgets.QComboBox(self)
        ins_linear_equations_solver_box.setObjectName('linear-solver-box')
        ins_linear_equations_solver_box.setFixedHeight(30)
        ins_linear_equations_solver_box.addItems(list(common.P4SStepInfo.SOLVER_METHOD_TO_NUMBER[1].keys()))
        ins_layout5.addWidget(ins_linear_equations_solver_box,1)
        
        return ins_static_step_widget
    def __slotChangeIncrementType(self, in_type:str) -> None:
        ins_increment_minimum_size_edit = self.findChild(QtWidgets.QLineEdit,'increment-minimum-size-edit')
        ins_increment_maximum_size_edit = self.findChild(QtWidgets.QLineEdit,'increment-maximum-size-edit')
        if in_type == 'fixed':
            ins_increment_minimum_size_edit.clear()
            ins_increment_minimum_size_edit.setEnabled(False)
            
            ins_increment_maximum_size_edit.clear()
            ins_increment_maximum_size_edit.setEnabled(False)
        elif in_type == 'automatic':
            ins_increment_minimum_size_edit.clear()
            ins_increment_minimum_size_edit.setEnabled(True)
            
            ins_increment_maximum_size_edit.clear()
            ins_increment_maximum_size_edit.setEnabled(True)
        else:
            pass
    def __slotChangeLinearSolverType(self,in_type:str) -> None:
        ins_linear_equations_solver_box = self.findChild(QtWidgets.QComboBox,'linear-solver-box')
        ins_linear_equations_solver_box.clear()
        if in_type == 'direct':
            ins_linear_equations_solver_box.addItems(list(common.P4SStepInfo.SOLVER_METHOD_TO_NUMBER[1].keys()))
        elif in_type == 'iterative':
            ins_linear_equations_solver_box.addItems(list(common.P4SStepInfo.SOLVER_METHOD_TO_NUMBER[2].keys()))
        else:
            pass   
    # endregion
        
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getStepInformation(self) -> dict:
        step_info_dict = {}
        
        step_info_dict['name'] = self.findChild(QtWidgets.QLineEdit,'step-name-edit').text()
        step_info_dict['type'] = self.findChild(QtWidgets.QComboBox,'step-type-box').currentText()
        if step_info_dict['type'] in ['static']:
            step_time_string = self.findChild(QtWidgets.QLineEdit,'step-time-edit').text()
            if step_time_string == '':
                step_info_dict['time'] = 0.0
            else:
                step_info_dict['time'] = float(step_time_string)

            step_info_dict['nlgeom'] = self.findChild(QtWidgets.QCheckBox,'step-nlgeom-box').isChecked()
        
            incrementation_parameters_list = []
            increments_number_string = self.findChild(QtWidgets.QLineEdit,'increments-number-edit').text()
            if increments_number_string == '':
                incrementation_parameters_list.append(0)
            else:
                incrementation_parameters_list.append(int(increments_number_string))
            
            incrementation_parameters_list.append(self.findChild(QtWidgets.QComboBox,'increment-type-box').currentText())
            if incrementation_parameters_list[1] == 'fixed':
                increment_size_string = self.findChild(QtWidgets.QLineEdit,'increment-size-edit').text()
                if increment_size_string == '':
                    incrementation_parameters_list.append(0.0)
                else:
                    incrementation_parameters_list.append(float(increment_size_string))
            elif incrementation_parameters_list[1] == 'automatic':
                increment_size_string = self.findChild(QtWidgets.QLineEdit,'increment-size-edit').text()
                if increment_size_string == '':
                    incrementation_parameters_list.append(0.0)
                else:
                    incrementation_parameters_list.append(float(increment_size_string))
                
                increment_minimum_size_string = self.findChild(QtWidgets.QLineEdit,'increment-minimum-size-edit').text()
                if increment_minimum_size_string == '':
                    incrementation_parameters_list.append(0.0)
                else:
                    incrementation_parameters_list.append(float(increment_minimum_size_string))
                    
                increment_maximum_size_string = self.findChild(QtWidgets.QLineEdit,'increment-maximum-size-edit').text()
                if increment_maximum_size_string == '':
                    incrementation_parameters_list.append(0.0)
                else:
                    incrementation_parameters_list.append(float(increment_maximum_size_string))
            else:
                pass
            step_info_dict['basic'] = incrementation_parameters_list
            
            incrementation_lsolver_list = [self.findChild(QtWidgets.QComboBox,'linear-solver-type-box').currentText()]
            incrementation_lsolver_list.append(self.findChild(QtWidgets.QComboBox,'linear-solver-box').currentText())
            step_info_dict['lsolver'] = incrementation_lsolver_list
        else:
            step_info_dict['time'] = -1
        
        return step_info_dict
    def setStepInformation(self, in_step_name:str, in_step_information:dict) -> None:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'step-name-edit')
        ins_name_line_edit.setText(in_step_name)
        ins_name_line_edit.setEnabled(False)
        
        self.findChild(QtWidgets.QComboBox,'step-type-box').setCurrentText(in_step_information['type'])
        if in_step_information['type'] in ['static']:
            self.findChild(QtWidgets.QLineEdit,'step-time-edit').setText(in_step_information['time'])
            
            self.findChild(QtWidgets.QCheckBox,'step-nlgeom-box').setChecked(in_step_information['nlgeom'])
            
            self.findChild(QtWidgets.QLineEdit,'increments-number-edit').setText(in_step_information['basic'][0])
            self.findChild(QtWidgets.QComboBox,'increment-type-box').setCurrentText(in_step_information['basic'][1])
            
            if in_step_information['basic'][1] == 'fixed':
                self.findChild(QtWidgets.QLineEdit,'increment-size-edit').setText(in_step_information['basic'][2])
            elif in_step_information['basic'][1] == 'automatic':
                self.findChild(QtWidgets.QLineEdit,'increment-size-edit').setText(in_step_information['basic'][2])
                self.findChild(QtWidgets.QLineEdit,'increment-minimum-size-edit').setText(in_step_information['basic'][3])
                self.findChild(QtWidgets.QLineEdit,'increment-maximum-size-edit').setText(in_step_information['basic'][4])
            else:
                pass
            
            self.findChild(QtWidgets.QComboBox,'linear-solver-type-box').setCurrentText(in_step_information['lsolver'][0])
            self.findChild(QtWidgets.QComboBox,'linear-solver-box').setCurrentText(in_step_information['lsolver'][1])
        else:
            pass

class _CreateOutputDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_outputs_name:list, in_exist_steps_name:list, in_exist_groups_name:dict):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_outputs_name_list = in_exist_outputs_name
        self.__exist_steps_name_list = in_exist_steps_name
        self.__exist_groups_name_dict = in_exist_groups_name
        
        self.setWindowTitle(f'Create Output')
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeNameEdit(ins_dialog_layout)
        self.__initializeSelection(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)

    def __initializeNameEdit(self, in_ins_dialog_layout:object) -> None:
        ins_group_name_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_group_name_layout,0)
        
        ins_output_name_label = QtWidgets.QLabel('Output Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_output_name_label.setFixedSize(95,30)
        ins_group_name_layout.addWidget(ins_output_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('output-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Output_','output_','Output-','output-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckOutputName)
        ins_group_name_layout.addWidget(ins_name_line_edit,1)        
    # region
    def __slotCheckOutputName(self, in_output_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        if in_output_name == '':
            ins_accept_button.setEnabled(False)
        elif in_output_name in self.__exist_outputs_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion
    
    def __initializeSelection(self,in_ins_dialog_layout:object) -> None:
        in_ins_dialog_layout.addSpacing(10)
        
        ins_split_line = QtWidgets.QFrame(parent=self,frameShape=QtWidgets.QFrame.Shape.HLine)
        ins_split_line.setLineWidth(1)
        in_ins_dialog_layout.addWidget(ins_split_line,0)
        
        ins_steps_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_steps_selection_layout,0)
        ins_begin_step_label = QtWidgets.QLabel('begin:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_begin_step_label.setFixedSize(45,30)
        ins_steps_selection_layout.addWidget(ins_begin_step_label,0)
        ins_begin_step_box = QtWidgets.QComboBox(self)
        ins_begin_step_box.setObjectName('begin-step-box')
        ins_begin_step_box.setFixedHeight(30)
        ins_begin_step_box.addItems(self.__exist_steps_name_list)
        ins_begin_step_box.currentIndexChanged.connect(self.__slotChangeBeginStep)
        ins_steps_selection_layout.addWidget(ins_begin_step_box,1)
        ins_end_step_label = QtWidgets.QLabel('end:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_end_step_label.setFixedSize(30,30)
        ins_steps_selection_layout.addWidget(ins_end_step_label,0)
        ins_end_step_box = QtWidgets.QComboBox(self)
        ins_end_step_box.setObjectName('end-step-box')
        ins_end_step_box.setFixedHeight(30)
        ins_end_step_box.addItems(self.__exist_steps_name_list)
        ins_end_step_box.currentIndexChanged.connect(self.__slotChangeEndStep)
        ins_steps_selection_layout.addWidget(ins_end_step_box,1)
        
        ins_frequency_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_frequency_selection_layout,0)
        ins_frequency_label = QtWidgets.QLabel('frequency:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_frequency_label.setFixedSize(75,30)
        ins_frequency_selection_layout.addWidget(ins_frequency_label,0)
        ins_frequency_reference_box = QtWidgets.QComboBox(self)
        ins_frequency_reference_box.setObjectName('frequency-reference-box')
        ins_frequency_reference_box.setFixedSize(180,30)
        ins_frequency_reference_box.addItems(['last increment','every n increments','every n seconds'])
        ins_frequency_reference_box.currentTextChanged.connect(self.__slotChangeFrequencyReference)
        ins_frequency_selection_layout.addWidget(ins_frequency_reference_box,0)
        ins_frequency_value_label = QtWidgets.QLabel('n:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_frequency_value_label.setFixedSize(15,30)
        ins_frequency_selection_layout.addWidget(ins_frequency_value_label,0)
        ins_frequency_value_edit = QtWidgets.QLineEdit(self)
        ins_frequency_value_edit.setObjectName('frequency-value-edit')
        ins_frequency_value_edit.setFixedHeight(30)
        ins_frequency_value_edit.setEnabled(False)
        ins_frequency_selection_layout.addWidget(ins_frequency_value_edit,1)
        
        ins_group_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_group_selection_layout,0)
        ins_group_label = QtWidgets.QLabel('group:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_group_label.setFixedSize(50,30)
        ins_group_selection_layout.addWidget(ins_group_label,0)
        ins_group_type_box = QtWidgets.QComboBox(self)
        ins_group_type_box.setObjectName('group-type-box')
        ins_group_type_box.setFixedSize(80,30)
        ins_group_type_box.addItems(['node','element'])
        ins_group_type_box.currentTextChanged.connect(self.__slotChangeGroupType)
        ins_group_selection_layout.addWidget(ins_group_type_box,0)
        ins_group_name_box = QtWidgets.QComboBox(self)
        ins_group_name_box.setObjectName('groups-box')
        ins_group_name_box.setFixedHeight(30)
        ins_group_name_box.addItems(self.__exist_groups_name_dict['node'])
        ins_group_selection_layout.addWidget(ins_group_name_box,1)
        
        ins_variables_selection_layout = QtWidgets.QStackedLayout()
        ins_variables_selection_layout.setObjectName('variables-stacked-layout')
        in_ins_dialog_layout.addLayout(ins_variables_selection_layout,1)
        ins_node_variables_list = QtWidgets.QListWidget(self)
        ins_node_variables_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        for variable_name,variable_description in common.P4SOutputInfo.NODE_VARIABLES_DESCRIPTION.items():
            ins_variable_item = QtWidgets.QListWidgetItem()
            ins_variable_item.setData(1,variable_name)
            ins_node_variables_list.addItem(ins_variable_item)
            ins_variable_check_box = QtWidgets.QCheckBox(self)
            ins_variable_check_box.setText(variable_name+','+variable_description)
            ins_node_variables_list.setItemWidget(ins_variable_item,ins_variable_check_box)
        ins_variables_selection_layout.addWidget(ins_node_variables_list)
        ins_element_variables_list = QtWidgets.QListWidget(self)
        ins_element_variables_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        for variable_name,variable_description in common.P4SOutputInfo.ELEMENT_VARIABLES_DESCRIPTION.items():
            ins_variable_item = QtWidgets.QListWidgetItem()
            ins_variable_item.setData(1,variable_name)
            ins_element_variables_list.addItem(ins_variable_item)
            ins_variable_check_box = QtWidgets.QCheckBox(self)
            ins_variable_check_box.setText(variable_name+','+variable_description)
            ins_element_variables_list.setItemWidget(ins_variable_item,ins_variable_check_box)
        ins_variables_selection_layout.addWidget(ins_element_variables_list)
    # region
    def __slotChangeBeginStep(self, in_step_index:int) -> None:
        ins_end_step_box = self.findChild(QtWidgets.QComboBox,'end-step-box')
        if in_step_index > ins_end_step_box.currentIndex():
            ins_end_step_box.setCurrentIndex(in_step_index)
        else:
            pass
    def __slotChangeEndStep(self, in_step_index:int) -> None:
        ins_begin_step_box = self.findChild(QtWidgets.QComboBox,'begin-step-box')
        if in_step_index < ins_begin_step_box.currentIndex():
            ins_begin_step_box.setCurrentIndex(in_step_index)
        else:
            pass
    def __slotChangeFrequencyReference(self, in_reference:str) -> None:
        ins_frequency_value_edit = self.findChild(QtWidgets.QLineEdit,'frequency-value-edit')
        ins_frequency_value_edit.clear()
        if in_reference == 'last increment':
            ins_frequency_value_edit.setEnabled(False)
        elif in_reference == 'every n increments':
            ins_frequency_value_edit.setEnabled(True)
            ins_frequency_value_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_INTEGER_FORMAT)))
        elif in_reference == 'every n seconds':
            ins_frequency_value_edit.setEnabled(True)
            ins_frequency_value_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_FLOAT_FORMAT)))
        else:
            ins_frequency_value_edit.setEnabled(True)
    def __slotChangeGroupType(self,in_group_type:str) -> None:
        ins_group_name_box = self.findChild(QtWidgets.QComboBox,'groups-box')
        ins_group_name_box.clear()
        ins_group_name_box.addItems(self.__exist_groups_name_dict[in_group_type])
        
        ins_variables_selection_layout = self.findChild(QtWidgets.QStackedLayout,'variables-stacked-layout')
        if in_group_type == 'node':
            ins_variables_selection_layout.setCurrentIndex(0)
        elif in_group_type == 'element':
            ins_variables_selection_layout.setCurrentIndex(1)
        else:
            pass
    # endregion
     
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getOutputInformation(self) -> dict:
        output_info_dict = {}
        
        output_info_dict['name'] = self.findChild(QtWidgets.QLineEdit,'output-name-edit').text()
        output_info_dict['steps'] = [self.findChild(QtWidgets.QComboBox,'begin-step-box').currentText(),self.findChild(QtWidgets.QComboBox,'end-step-box').currentText()]
        
        output_info_dict['frequency'] = [self.findChild(QtWidgets.QComboBox,'frequency-reference-box').currentText(),self.findChild(QtWidgets.QLineEdit,'frequency-value-edit').text()]
        if output_info_dict['frequency'][0] == 'last increment':
            output_info_dict['frequency'][1] = None
        else:
            if output_info_dict['frequency'][1] == '':
                output_info_dict['frequency'][1] = None
            else:
                output_info_dict['frequency'][1] = float(output_info_dict['frequency'][1])
        
        output_info_dict['group'] = [self.findChild(QtWidgets.QComboBox,'group-type-box').currentText(),self.findChild(QtWidgets.QComboBox,'groups-box').currentText()]
        
        output_info_dict['variables'] = []
        ins_variables_selection_layout = self.findChild(QtWidgets.QStackedLayout,'variables-stacked-layout')
        ins_variables_list = ins_variables_selection_layout.currentWidget()
        for variable_index in range(ins_variables_list.count()):
            if ins_variables_list.itemWidget(ins_variables_list.item(variable_index)).isChecked():
                output_info_dict['variables'].append(ins_variables_list.item(variable_index).data(1))
            else:
                continue
        
        return output_info_dict
    def setOutputInformation(self, in_output_name:str, in_output_information:dict) -> None:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'output-name-edit')
        ins_name_line_edit.setText(in_output_name)
        ins_name_line_edit.setEnabled(False)
        
        self.findChild(QtWidgets.QComboBox,'begin-step-box').setCurrentText(in_output_information['steps'][0])
        self.findChild(QtWidgets.QComboBox,'end-step-box').setCurrentText(in_output_information['steps'][1])
        
        self.findChild(QtWidgets.QComboBox,'frequency-reference-box').setCurrentText(in_output_information['frequency'][0])
        if in_output_information['frequency'][1] is None:
            pass
        else:
            if in_output_information['frequency'][0] == 'every n increments':
                self.findChild(QtWidgets.QLineEdit,'frequency-value-edit').setText(str(int(in_output_information['frequency'][1])))
            else:
                self.findChild(QtWidgets.QLineEdit,'frequency-value-edit').setText(str(in_output_information['frequency'][1]))
        
        self.findChild(QtWidgets.QComboBox,'group-type-box').setCurrentText(in_output_information['type'])
        self.findChild(QtWidgets.QComboBox,'groups-box').setCurrentText(in_output_information['group'])
        
        ins_variables_selection_layout = self.findChild(QtWidgets.QStackedLayout,'variables-stacked-layout')
        ins_variables_list = ins_variables_selection_layout.currentWidget()
        for variable_index in range(ins_variables_list.count()):
            if ins_variables_list.item(variable_index).data(1) in in_output_information['variables']:
                ins_variables_list.itemWidget(ins_variables_list.item(variable_index)).setChecked(True)
            else:
                continue

class _CreateBoundaryConditionDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_model_dimension:str, in_condition_type:str,in_exist_boundary_conditions_name:list, 
                 in_exist_groups_name:list, in_exist_steps_name:list, in_exist_assembly_coordinate_systems_name:list, in_exist_functions_name:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__model_dimension = in_model_dimension
        self.__condition_type = in_condition_type
        self.__exist_conditions_name = in_exist_boundary_conditions_name
        self.__exist_groups_name_list = in_exist_groups_name
        self.__exist_steps_name_list = in_exist_steps_name
        self.__exist_csys_name_list = in_exist_assembly_coordinate_systems_name
        self.__exist_functions_name_list = in_exist_functions_name
        
        self.setWindowTitle(f'Create Boundary Condition - {in_condition_type}')
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeNameEdit(ins_dialog_layout)
        self.__initializeSelection(ins_dialog_layout)
        self.__initializeParemsTable(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)
        
        self.__definition_step_index = 0
        self.__being_update_components = True
        
        if in_condition_type in ['concentrated force','moment']:
            ins_definition_steps_box = self.findChild(QtWidgets.QComboBox,'definition-steps-box')
            if len(self.__exist_steps_name_list) > 1:
                ins_definition_steps_box.setCurrentIndex(1)
            else:
                pass
            ins_definition_steps_box.setItemData(0,0,QtCore.Qt.UserRole-1)
            
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'parameters-table')
            for row_index in range(1,ins_params_table.rowCount()-1):
                ins_params_table.cellWidget(row_index,0).setEnabled(False)
        else:
            pass
 
    def __initializeNameEdit(self, in_ins_dialog_layout:object) -> None:
        ins_group_name_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_group_name_layout,0)
        
        ins_condition_name_label = QtWidgets.QLabel('Boundary Condition Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_condition_name_label.setFixedSize(185,30)
        ins_group_name_layout.addWidget(ins_condition_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('condition-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Condition_','condition_','BC_','bc-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckConditionName)
        ins_group_name_layout.addWidget(ins_name_line_edit,1)        
    # region
    def __slotCheckConditionName(self, in_condition_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        if in_condition_name == '':
            ins_accept_button.setEnabled(False)
        elif in_condition_name in self.__exist_conditions_name:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    # endregion
    
    def __initializeSelection(self, in_ins_dialog_layout:object) -> None:
        ins_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_selection_layout)
        
        ins_coordinate_system_label = QtWidgets.QLabel('CSYS:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft) 
        ins_coordinate_system_label.setFixedSize(45,30)
        ins_selection_layout.addWidget(ins_coordinate_system_label,0)
        ins_coordinate_systems_box = QtWidgets.QComboBox(self)
        ins_coordinate_systems_box.setObjectName('csys-box')
        ins_coordinate_systems_box.setFixedHeight(30)
        ins_coordinate_systems_box.addItems(self.__exist_csys_name_list)
        ins_selection_layout.addWidget(ins_coordinate_systems_box,1)
        
        ins_group_label = QtWidgets.QLabel('group:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft) 
        ins_group_label.setFixedSize(50,30)
        ins_selection_layout.addWidget(ins_group_label,0)
        ins_groups_box = QtWidgets.QComboBox(self)
        ins_groups_box.setObjectName('groups-box')
        ins_groups_box.setFixedHeight(30)
        ins_groups_box.addItems(self.__exist_groups_name_list)
        ins_selection_layout.addWidget(ins_groups_box,1)
        
        ins_definition_step_label = QtWidgets.QLabel('definition step:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft) 
        ins_definition_step_label.setFixedSize(105,30)
        ins_selection_layout.addWidget(ins_definition_step_label,0)
        ins_definition_steps_box = QtWidgets.QComboBox(self)
        ins_definition_steps_box.setObjectName('definition-steps-box')
        ins_definition_steps_box.setFixedHeight(30)
        ins_definition_steps_box.addItems(self.__exist_steps_name_list)
        ins_definition_steps_box.currentTextChanged.connect(self.__slotChangeDefinitionStep)
        ins_selection_layout.addWidget(ins_definition_steps_box,1)

    def __initializeParemsTable(self, in_ins_dialog_layout:object) -> None:
        ins_params_table = QtWidgets.QTableWidget(self)
        ins_params_table.setObjectName('parameters-table')
        in_ins_dialog_layout.addWidget(ins_params_table,1)
        
        ins_params_table.setColumnCount(len(self.__exist_steps_name_list))
        ins_params_table.horizontalHeader().setFixedHeight(30)
        ins_params_table.setHorizontalHeaderLabels(self.__exist_steps_name_list)
        ins_params_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        ins_params_table.horizontalHeader().setSectionsClickable(False)
        ins_params_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        if self.__model_dimension == "2D":
            conditon_include_components_list = common.P4SBCInfo.BC_COMPONENTS_2D[self.__condition_type]
        else:
            conditon_include_components_list = common.P4SBCInfo.BC_COMPONENTS_3D[self.__condition_type]
        ins_params_table.setRowCount(2+len(conditon_include_components_list))
        ins_params_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        ins_params_table.setVerticalHeaderLabels(['Sat',*conditon_include_components_list,'func'])
        
        ins_params_table.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
        ins_params_table.verticalHeader().setSectionsClickable(False)
        ins_params_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        ins_params_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        for column_index in range(1,ins_params_table.columnCount()):
            ins_params_table.setCellWidget(0,column_index,QtWidgets.QComboBox())
            ins_params_table.cellWidget(0,column_index).addItems(['Edit','Inherited','Disabled'])
            ins_params_table.cellWidget(0,column_index).setCurrentIndex(1)
            ins_params_table.cellWidget(0,column_index).currentTextChanged.connect(self.__slotChangeStepState)

            ins_params_table.setCellWidget(ins_params_table.rowCount()-1,column_index,QtWidgets.QComboBox())
            ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).addItems(self.__exist_functions_name_list)
            ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setCurrentText('None')
            ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setEnabled(False)
            ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).currentTextChanged.connect(self.__slotChangeFunction)
        for row_index in range(1,ins_params_table.rowCount()-1):
            ins_params_table.setCellWidget(row_index,0, QtWidgets.QLineEdit())
            ins_params_table.cellWidget(row_index,0).setMaxLength(20)
            ins_params_table.cellWidget(row_index,0).setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('[0]')))
            ins_params_table.cellWidget(row_index,0).textChanged.connect(self.__slotChangeComponent)
        for row_index in range(1,ins_params_table.rowCount()-1):
            for column_index in range(1,ins_params_table.columnCount()):
                ins_params_table.setCellWidget(row_index,column_index, QtWidgets.QLineEdit())
                ins_params_table.cellWidget(row_index,column_index).setMaxLength(20)
                ins_params_table.cellWidget(row_index,column_index).setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
                ins_params_table.cellWidget(row_index,column_index).setReadOnly(True)
                ins_params_table.cellWidget(row_index,column_index).textChanged.connect(self.__slotChangeComponent)
    # region
    def __slotChangeDefinitionStep(self, in_step_name:str) -> None:
        ins_params_table = self.findChild(QtWidgets.QTableWidget,'parameters-table')
        new_definition_step_index = self.__exist_steps_name_list.index(in_step_name)
        
        if new_definition_step_index == self.__definition_step_index:
            return None
        else:
            pass

        step_include_components_list = []
        for row_index in range(1,ins_params_table.rowCount()-1):
            step_include_components_list.append(ins_params_table.cellWidget(row_index,self.__definition_step_index).text())
        if self.__definition_step_index == 0:
            step_function_name = 'None'
        else:
            step_function_name = ins_params_table.cellWidget(ins_params_table.rowCount()-1,self.__definition_step_index).currentText()

        self.__being_update_components = False
        
        if new_definition_step_index > 0:
            for column_index in range(1,new_definition_step_index):
                ins_params_table.cellWidget(0,column_index).setCurrentIndex(-1)
                ins_params_table.cellWidget(0,column_index).setEnabled(False)
                ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setCurrentText('None')
                ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setEnabled(False)
        else:
            pass
        for column_index in range(new_definition_step_index):
            for row_index in range(1,ins_params_table.rowCount()-1):
                ins_params_table.cellWidget(row_index,column_index).clear()
                ins_params_table.cellWidget(row_index,column_index).setReadOnly(True)

        if new_definition_step_index < self.__definition_step_index:
            if new_definition_step_index == 0:
                for component_text in step_include_components_list:
                    if component_text == '':
                        continue
                    else:
                        if float(component_text) == 0.0:
                            continue
                        else:
                            ins_definition_steps_box = self.findChild(QtWidgets.QComboBox,'definition-steps-box')
                            ins_definition_steps_box.setCurrentIndex(self.__definition_step_index)
                            
                            QtWidgets.QMessageBox.critical(self,'Create Boundary Condition Error','Component of "Initial" must be zero!')
                            return None

                for row_index in range(1,ins_params_table.rowCount()-1):
                    ins_params_table.cellWidget(row_index,new_definition_step_index).setReadOnly(False)
                    
                    if step_include_components_list[row_index-1] == '':
                        continue
                    else:
                        ins_params_table.cellWidget(row_index,new_definition_step_index).setText('0')      
            else:
                ins_params_table.cellWidget(0,new_definition_step_index).setCurrentText('Edit')
                ins_params_table.cellWidget(0,new_definition_step_index).setEnabled(False)
                
                for row_index in range(1,ins_params_table.rowCount()-1):
                    ins_params_table.cellWidget(row_index,new_definition_step_index).setReadOnly(False)
                    ins_params_table.cellWidget(row_index,new_definition_step_index).setText(step_include_components_list[row_index-1])
                ins_params_table.cellWidget(ins_params_table.rowCount()-1,new_definition_step_index).setEnabled(True)
                ins_params_table.cellWidget(ins_params_table.rowCount()-1,new_definition_step_index).setCurrentText(step_function_name)
        
            ins_params_table.cellWidget(0,self.__definition_step_index).setCurrentText('Inherited')
            ins_params_table.cellWidget(0,self.__definition_step_index).setEnabled(True)
            for row_index in range(1,ins_params_table.rowCount()-1):
                ins_params_table.cellWidget(row_index,self.__definition_step_index).setReadOnly(True)
            ins_params_table.cellWidget(ins_params_table.rowCount()-1,self.__definition_step_index).setEnabled(False)
        else:
            ins_params_table.cellWidget(0,new_definition_step_index).setCurrentText('Edit')
            ins_params_table.cellWidget(0,new_definition_step_index).setEnabled(False)
            for row_index in range(1,ins_params_table.rowCount()-1):
                ins_params_table.cellWidget(row_index,new_definition_step_index).setReadOnly(False)
            ins_params_table.cellWidget(ins_params_table.rowCount()-1,new_definition_step_index).setEnabled(True)
        
        if new_definition_step_index == ins_params_table.columnCount()-1:
            pass
        else:
            if ins_params_table.cellWidget(0,new_definition_step_index+1).currentIndex() == -1:
                for column_index in range(new_definition_step_index+1,ins_params_table.columnCount()):
                    if ins_params_table.cellWidget(0,column_index).currentIndex() == -1:
                        ins_params_table.cellWidget(0,column_index).setCurrentText('Inherited')
                        ins_params_table.cellWidget(0,column_index).setEnabled(True)
                        for row_index in range(1,ins_params_table.rowCount()-1):
                            ins_params_table.cellWidget(row_index,column_index).setText(step_include_components_list[row_index-1])
                            ins_params_table.cellWidget(row_index,column_index).setReadOnly(True)
                        ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setCurrentText(step_function_name)
                        ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setEnabled(False)
                    else:
                        break
            else:
                pass

        self.__being_update_components = True
        self.__definition_step_index = new_definition_step_index
    
    def __slotChangeStepState(self, in_state:str) -> None:
        if self.__being_update_components:
            pass
        else:
            return None

        ins_params_table = self.findChild(QtWidgets.QTableWidget,'parameters-table')
        current_column_index = ins_params_table.currentColumn()
        
        if in_state == 'Edit':
            for row_index in range(1,ins_params_table.rowCount()-1):
                ins_params_table.cellWidget(row_index,current_column_index).setReadOnly(False)
            ins_params_table.cellWidget(ins_params_table.rowCount()-1,current_column_index).setEnabled(True)

            if current_column_index == ins_params_table.columnCount()-1:
                pass
            elif ins_params_table.cellWidget(0,current_column_index+1).currentIndex() == -1:
                step_include_components_list = []
                for row_index in range(1,ins_params_table.rowCount()-1):
                    step_include_components_list.append(ins_params_table.cellWidget(row_index,current_column_index).text())
                setp_function_name = ins_params_table.cellWidget(ins_params_table.rowCount()-1,current_column_index).currentText()

                self.__being_update_components = False
                for column_index in range(current_column_index+1,ins_params_table.columnCount()):
                    ins_params_table.cellWidget(0,column_index).setEnabled(True)
                    ins_params_table.cellWidget(0,column_index).setCurrentText('Inherited')
                    
                    for row_index in range(1,ins_params_table.rowCount()-1):
                        ins_params_table.cellWidget(row_index,column_index).setText(step_include_components_list[row_index-1])
                        ins_params_table.cellWidget(row_index,column_index).setReadOnly(True)
                    
                    ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setCurrentText(setp_function_name)
                    ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setEnabled(False)
                
                self.__being_update_components = True
            else:
                pass
        elif in_state == 'Inherited':
            before_step_include_components_list = []
            for row_index in range(1,ins_params_table.rowCount()-1):
                before_step_include_components_list.append(ins_params_table.cellWidget(row_index,current_column_index-1).text())
            if current_column_index-1 == 0:
                before_step_function_name = 'None'
            else:
                before_step_function_name = ins_params_table.cellWidget(ins_params_table.rowCount()-1,current_column_index-1).currentText()

            self.__being_update_components = False
            
            for row_index in range(1,ins_params_table.rowCount()-1):
                ins_params_table.cellWidget(row_index,current_column_index).setText(before_step_include_components_list[row_index-1])
                ins_params_table.cellWidget(row_index,current_column_index).setReadOnly(True)
            ins_params_table.cellWidget(ins_params_table.rowCount()-1,current_column_index).setCurrentText(before_step_function_name)
            ins_params_table.cellWidget(ins_params_table.rowCount()-1,current_column_index).setEnabled(False)

            if current_column_index == ins_params_table.columnCount()-1:
                pass
            elif ins_params_table.cellWidget(0,current_column_index+1).currentText() == 'Inherited':
                for column_index in range(current_column_index+1,ins_params_table.columnCount()):
                    if ins_params_table.cellWidget(0,column_index).currentText() == 'Inherited':
                        pass
                    else:
                        break

                    for row_index in range(1,ins_params_table.rowCount()-1):
                        ins_params_table.cellWidget(row_index,column_index).setText(before_step_include_components_list[row_index-1])
                        ins_params_table.cellWidget(row_index,column_index).setReadOnly(True)
                    
                    ins_params_table.cellWidget(ins_params_table.rowCount()-1,current_column_index).setCurrentText(before_step_function_name)
                    ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setEnabled(False)
            elif ins_params_table.cellWidget(0,current_column_index+1).currentIndex() == -1:
                for column_index in range(current_column_index+1,ins_params_table.columnCount()):
                    ins_params_table.cellWidget(0,column_index).setEnabled(True)
                    ins_params_table.cellWidget(0,column_index).setCurrentText("Inherited")

                    for row_index in range(1,ins_params_table.rowCount()-1):
                        ins_params_table.cellWidget(row_index,column_index).setText(before_step_include_components_list[row_index-1])
                        ins_params_table.cellWidget(row_index,column_index).setReadOnly(True)

                    ins_params_table.cellWidget(ins_params_table.rowCount()-1,current_column_index).setCurrentText(before_step_function_name)
                    ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setEnabled(False)
            else:
                pass
            
            self.__being_update_components = True
        elif in_state == 'Disabled':
            self.__being_update_components = False
            
            if current_column_index == ins_params_table.columnCount()-1:
                pass
            else:
                for column_index in range(current_column_index+1,ins_params_table.columnCount()):
                    ins_params_table.cellWidget(0,column_index).setEnabled(False)
                    ins_params_table.cellWidget(0,column_index).setCurrentIndex(-1)

            for column_index in range(current_column_index,ins_params_table.columnCount()):
                for row_index in range(1,ins_params_table.rowCount()-1):
                    ins_params_table.cellWidget(row_index,column_index).clear()
                    ins_params_table.cellWidget(row_index,column_index).setReadOnly(True)
                
                ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setCurrentText('None')
                ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setEnabled(False)
            
            self.__being_update_components = True
        else:
            return None
    def __slotChangeFunction(self, in_function_name:str) -> None:
        if self.__being_update_components:
            pass
        else:
            return None

        ins_params_table = self.findChild(QtWidgets.QTableWidget,'parameters-table')
        current_row_index = ins_params_table.currentRow()
        current_column_index = ins_params_table.currentColumn()

        if current_column_index == ins_params_table.columnCount()-1:
            return None
        else:
            pass

        self.__being_update_components = False
        
        for column_index in range(current_column_index+1,ins_params_table.columnCount()):
            if ins_params_table.cellWidget(0,column_index).currentText() == 'Inherited':
                ins_params_table.cellWidget(current_row_index,column_index).setCurrentText(in_function_name)
            else:
                break
        
        self.__being_update_components = True
    def __slotChangeComponent(self, in_component_text:str) -> None:
        if self.__being_update_components:
            pass
        else:
            return None

        ins_params_table = self.findChild(QtWidgets.QTableWidget,'parameters-table')
        current_row_index = ins_params_table.currentRow()
        current_column_index = ins_params_table.currentColumn()

        if current_column_index == ins_params_table.columnCount()-1:
            return None
        else:
            pass

        self.__being_update_components = False
        
        for column_index in range(current_column_index+1,ins_params_table.columnCount()):
            if ins_params_table.cellWidget(0,column_index).currentText() == 'Inherited':
                ins_params_table.cellWidget(current_row_index,column_index).setText(in_component_text)
            else:
                break
        
        self.__being_update_components = True
    # endregion
    
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getBoundaryConditionInformation(self) -> dict:
        boundary_condition_info_dict= {}
        
        boundary_condition_info_dict['name'] = self.findChild(QtWidgets.QLineEdit,'condition-name-edit').text()
        
        boundary_condition_info_dict['csys'] = self.findChild(QtWidgets.QComboBox,'csys-box').currentText()
        
        boundary_condition_info_dict['group'] = self.findChild(QtWidgets.QComboBox,'groups-box').currentText()
        
        boundary_condition_info_dict['definition'] = self.findChild(QtWidgets.QComboBox,'definition-steps-box').currentText()
        
        boundary_condition_info_dict['steps'] = {}
        step_column_index = self.__exist_steps_name_list.index(boundary_condition_info_dict['definition'])
        ins_params_table = self.findChild(QtWidgets.QTableWidget,'parameters-table')
        for column_index in range(step_column_index,ins_params_table.columnCount()):
            components_text_list = []
            
            for row_index in range(1,ins_params_table.rowCount()-1):
                component_text = ins_params_table.cellWidget(row_index,column_index).text()
                if component_text == '':
                    components_text_list.append('N')
                else:
                    if self.__condition_type in ['concentrated force','moment'] and float(component_text) == 0.0:
                        components_text_list.append('N')
                    else:
                        components_text_list.append(component_text)
            
            function_name = 'None'
            if column_index == 0:
                pass
            else:
                function_name = ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).currentText()
            components_text_list.append(function_name)
            
            boundary_condition_info_dict['steps'][self.__exist_steps_name_list[column_index]] = components_text_list

            if self.__exist_steps_name_list[column_index] == boundary_condition_info_dict['definition']:
                if list(set(components_text_list[0:-1])) == ['N']:
                    boundary_condition_info_dict['steps'] = {}
                    break
                else:
                    pass
            elif ins_params_table.cellWidget(0,column_index).currentText() == 'Edit':
                if list(set(components_text_list[0:-1])) == ['N']:
                    boundary_condition_info_dict['steps'] = {}
                    break
                else:
                    pass
            else:
                pass
 
        return  boundary_condition_info_dict
    def setBoundaryConditionInformation(self, in_boundary_condition_name:str, in_boundary_condition_information:dict) -> None:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'condition-name-edit')
        ins_name_line_edit.setText(in_boundary_condition_name)
        ins_name_line_edit.setEnabled(False)
        
        self.findChild(QtWidgets.QComboBox,'csys-box').setCurrentText(in_boundary_condition_information['csys'])
        
        self.findChild(QtWidgets.QComboBox,'groups-box').setCurrentText(in_boundary_condition_information['group'][1])
        
        self.findChild(QtWidgets.QComboBox,'definition-steps-box').setCurrentText(in_boundary_condition_information['definition'][0])
        
        step_column_index = in_boundary_condition_information['definition'][1]
        ins_params_table = self.findChild(QtWidgets.QTableWidget,'parameters-table')
        before_step_name = None
        for column_index in range(step_column_index,ins_params_table.columnCount()):
            if column_index == 0:
                step_name = 'Initial'
                
                components_text_list = in_boundary_condition_information['parameters'][step_name]
                for row_index in range(1,ins_params_table.rowCount()-1):
                    if components_text_list[row_index-1] == 'N':
                        continue
                    else:
                        ins_params_table.setCurrentCell(row_index,column_index)
                        ins_params_table.cellWidget(row_index,column_index).setText(components_text_list[row_index-1])         
            else:
                step_name = ins_params_table.horizontalHeaderItem(column_index).text()
                components_text_list = in_boundary_condition_information['parameters'][step_name]
                
                if before_step_name is None:
                    ins_params_table.setCurrentCell(0,column_index)
                    ins_params_table.cellWidget(0,column_index).setCurrentText('Edit')
                    
                    ins_params_table.setCurrentCell(ins_params_table.rowCount()-1,column_index)
                    ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setCurrentText(components_text_list[-1])
                    
                    for row_index in range(1,ins_params_table.rowCount()-1):
                        if components_text_list[row_index-1] == 'N':
                            continue
                        else:
                            ins_params_table.setCurrentCell(row_index,column_index)
                            ins_params_table.cellWidget(row_index,column_index).setText(components_text_list[row_index-1])
                else:
                    if list(set(components_text_list[:-1])) == ['N']:
                        ins_params_table.setCurrentCell(0,column_index)
                        ins_params_table.cellWidget(0,column_index).setCurrentText('Disabled')
                        break
                    elif components_text_list == in_boundary_condition_information['parameters'][before_step_name]:
                        before_step_name = step_name
                        continue
                    else:
                        ins_params_table.setCurrentCell(0,column_index)
                        ins_params_table.cellWidget(0,column_index).setCurrentText('Edit')
                        
                        ins_params_table.setCurrentCell(ins_params_table.rowCount()-1,column_index)
                        ins_params_table.cellWidget(ins_params_table.rowCount()-1,column_index).setCurrentText(components_text_list[-1])
                        
                        for row_index in range(1,ins_params_table.rowCount()-1):
                            ins_params_table.setCurrentCell(row_index,column_index)
                            if components_text_list[row_index-1] == 'N':
                                ins_params_table.cellWidget(row_index,column_index).setText('')
                            else:
                                ins_params_table.cellWidget(row_index,column_index).setText(components_text_list[row_index-1])
            
            before_step_name = step_name
class _SwithBoundaryConditionsVisibility(QtWidgets.QDialog):
    def __init__(self, in_parent:object, in_conditions_by_step:dict,in_shown_conditions_name:list):
        super().__init__(parent=in_parent, modal=True)
        
        self.__model_name = self.parent().objectName()
        self.__conditions_by_step_dict = in_conditions_by_step
        self.__shown_conditions_name_list = in_shown_conditions_name
        
        self.setWindowTitle('Show/Hide Boundary Conditions')
        self.setMinimumSize(150,300)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeStepSelection(ins_dialog_layout)
        self.__initializeConditionsSelection(ins_dialog_layout)
        
    def __initializeStepSelection(self, in_ins_dialog_layout:object) -> None:
        ins_step_selection_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_step_selection_layout,0)
        
        ins_step_label = QtWidgets.QLabel('Step:',self,alignment=QtCore.Qt.AlignCenter)
        ins_step_label.setFixedSize(60,30)
        ins_step_selection_layout.addWidget(ins_step_label,0)
        
        ins_steps_box = QtWidgets.QComboBox(self)
        ins_steps_box.setObjectName('steps-box')
        ins_steps_box.setFixedHeight(30)
        ins_steps_box.addItems(self.__conditions_by_step_dict)
        ins_steps_box.currentTextChanged.connect(self.__slotChangeStep)
        ins_step_selection_layout.addWidget(ins_steps_box,1)
    # region
    def __slotChangeStep(self, in_step_name:str) -> None:
        ins_conditions_selection_layout = self.findChild(QtWidgets.QStackedLayout,'steps-conditions-stacked-layout')
        ins_conditions_list = self.findChild(QtWidgets.QListWidget,in_step_name)
        
        ins_conditions_selection_layout.setCurrentWidget(ins_conditions_list)
    # endregion
        
    def __initializeConditionsSelection(self, in_ins_dialog_layout:object) -> None:
        ins_conditions_selection_layout = QtWidgets.QStackedLayout()
        ins_conditions_selection_layout.setObjectName('steps-conditions-stacked-layout')
        in_ins_dialog_layout.addLayout(ins_conditions_selection_layout,1)
        
        for step_name, conditions_name_list in self.__conditions_by_step_dict.items():
            ins_conditions_list = QtWidgets.QListWidget(self)
            ins_conditions_list.setObjectName(step_name)
            ins_conditions_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
            ins_conditions_selection_layout.addWidget(ins_conditions_list)
            
            for condition_name in conditions_name_list:
                ins_condition_item = QtWidgets.QListWidgetItem()
                ins_condition_item.setText(condition_name)
                ins_conditions_list.addItem(ins_condition_item)
                
                if condition_name in self.__shown_conditions_name_list:
                    ins_condition_item.setSelected(True)
                else:
                    pass
            
            ins_conditions_list.itemClicked.connect(self.__slotChangeConditionVisibility)
    # region
    def __slotChangeConditionVisibility(self, in_ins_condition_item:object) -> None:
        ins_main_window = self.parent().parent().parent().parent().parent().parent()
        ins_models_mdi_area = ins_main_window.centralWidget().widget(0)
        ins_model_visual_window = ins_models_mdi_area.findChild(QtWidgets.QMdiSubWindow,self.__model_name)

        if in_ins_condition_item.isSelected():
            ins_model_visual_window.addBoundaryConditionToAssemblyViewport(ins_main_window.ins_project_database,in_ins_condition_item.text())
        else:
            ins_model_visual_window.removeBoundaryConditionToAssemblyViewport(in_ins_condition_item.text())
    # endregion        

class _CreateFunctionDialog(QtWidgets.QDialog):
    def __init__(self,in_parent:object, in_exist_functions_name:list):
        super().__init__(parent=in_parent,modal=True)
        
        self.__exist_functions_name_list = in_exist_functions_name
        
        self.setWindowTitle(f'Create Function')
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeNameEdit(ins_dialog_layout)
        
        ins_central_layout = QtWidgets.QHBoxLayout()
        ins_central_layout.setContentsMargins(0,0,0,0)
        ins_dialog_layout.addLayout(ins_central_layout,1)
        self.__initializeParametersTables(ins_central_layout)
        self.__initializeDisplayChart(ins_central_layout)
        
        self.__initializeUserButton(ins_dialog_layout)
        
        self.__name_state = False
        self.__check_state = False

    def __initializeNameEdit(self, in_ins_dialog_layout:object) -> None:
        ins_group_name_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_group_name_layout,0)
        
        ins_function_name_label = QtWidgets.QLabel('Function Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_function_name_label.setFixedSize(105,30)
        ins_group_name_layout.addWidget(ins_function_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('function-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Function_','Func_','func-','f-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckFunctionName)
        ins_group_name_layout.addWidget(ins_name_line_edit,1)        
    # region
    def __slotCheckFunctionName(self, in_function_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        if in_function_name == '':
            self.__name_state = False
        elif in_function_name.lower() == 'none':
            self.__name_state = False
        elif in_function_name in self.__exist_functions_name_list:
            self.__name_state = False
        else:
            self.__name_state = True
    
        if self.__name_state and self.__check_state:
            ins_accept_button.setEnabled(True)
        else:
            ins_accept_button.setEnabled(False)
    # endregion
    
    def __initializeParametersTables(self, in_ins_central_layout:object) -> None:
        ins_parameters_layout = QtWidgets.QVBoxLayout()
        in_ins_central_layout.addLayout(ins_parameters_layout,1)
        
        ins_parameters_layout.setContentsMargins(0,0,0,0)
        
        ins_function_type_layout = QtWidgets.QHBoxLayout()
        ins_parameters_layout.addLayout(ins_function_type_layout,0)
        ins_function_type_label = QtWidgets.QLabel('Type:',self,alignment=QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        ins_function_type_label.setFixedSize(45,30)
        ins_function_type_layout.addWidget(ins_function_type_label,1)
        ins_function_type_box = QtWidgets.QComboBox(self)
        ins_function_type_box.setObjectName('function-type-box')
        ins_function_type_box.setFixedSize(120,30)
        ins_function_type_box.addItems(['piecewise','periodic','smooth'])
        ins_function_type_box.setItemData(1,0,QtCore.Qt.UserRole-1) ##
        ins_function_type_box.setItemData(2,0,QtCore.Qt.UserRole-1) ##
        ins_function_type_box.currentIndexChanged.connect(self.__slotChangeFunctionType)
        ins_function_type_layout.addWidget(ins_function_type_box,0)
        ins_check_function_button = QtWidgets.QPushButton(self)
        ins_check_function_button.setFixedSize(80,30)
        ins_check_function_button.setText('check')
        ins_check_function_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_check_function_button.clicked.connect(self.__slotCheckParameters)
        ins_function_type_layout.addWidget(ins_check_function_button,0)
        ins_function_type_layout.addStretch()
        
        ins_tables_stacked_layout = QtWidgets.QStackedLayout()
        ins_tables_stacked_layout.setContentsMargins(0,0,0,0)
        ins_tables_stacked_layout.setObjectName('tables-stacked-layout')
        ins_parameters_layout.addLayout(ins_tables_stacked_layout,1)
        self.__initializePiecewiseTable(ins_tables_stacked_layout)
        self.__initializePriodicTable(ins_tables_stacked_layout)
        self.__initializeSmoothTable(ins_tables_stacked_layout)
    # region
    def __initializePiecewiseTable(self, in_stacked_layout:object) -> None:
        ins_params_table = QtWidgets.QTableWidget(self)
        in_stacked_layout.addWidget(ins_params_table)
        
        ins_params_table.setObjectName('piecewise-table')
        ins_params_table.setColumnCount(2)
        ins_params_table.horizontalHeader().setFixedHeight(30)
        ins_params_table.setHorizontalHeaderLabels(['Point','Scale'])
        ins_params_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ins_params_table.horizontalHeader().setSectionsClickable(False)
        ins_params_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_params_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_params_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        ins_params_table.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
        ins_params_table.verticalHeader().setSectionsClickable(True)
        ins_params_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        ins_params_table.setRowCount(2)
        for row_index in range(2):
            ins_params_table.setItem(row_index,0,QtWidgets.QTableWidgetItem())
            ins_params_table.setItem(row_index,1,QtWidgets.QTableWidgetItem())
        
        ins_params_table.itemChanged.connect(self.__slotClearViewChat)
        ins_params_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        ins_params_table.customContextMenuRequested.connect(self.__slotTableRightMenu)
    def __initializePriodicTable(self, in_stacked_layout:object) -> None:
        ins_parameters_widget = QtWidgets.QWidget(self)
        in_stacked_layout.addWidget(ins_parameters_widget)
        
        ins_widgets_layout = QtWidgets.QVBoxLayout()
        ins_widgets_layout.setContentsMargins(0,0,0,0)
        ins_parameters_widget.setLayout(ins_widgets_layout)
        
        ins_form_layout = QtWidgets.QFormLayout()
        ins_widgets_layout.addLayout(ins_form_layout,0)
        ins_form_layout.setContentsMargins(0,0,0,0)
        ins_form_layout.setLabelAlignment(QtCore.Qt.AlignCenter)
        ins_initial_amplitude_edit = QtWidgets.QLineEdit(self)
        ins_initial_amplitude_edit.setObjectName('initial-amplitude-edit')
        ins_initial_amplitude_edit.setFixedHeight(30)
        ins_initial_amplitude_edit.setMaxLength(20)
        ins_initial_amplitude_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_initial_amplitude_edit.textChanged.connect(self.__slotClearViewChat)
        ins_form_layout.addRow('initial amplitude:',ins_initial_amplitude_edit)
        ins_start_point_edit = QtWidgets.QLineEdit(self)
        ins_start_point_edit.setObjectName('initial-percentage-edit')
        ins_start_point_edit.setFixedHeight(30)
        ins_start_point_edit.setMaxLength(20)
        ins_start_point_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r'^(0(\.\d+)?|1(\.0+)?)$')))
        ins_start_point_edit.textChanged.connect(self.__slotClearViewChat)
        ins_form_layout.addRow('initial percentage:',ins_start_point_edit)
        ins_circular_frequency_edit = QtWidgets.QLineEdit(self)
        ins_circular_frequency_edit.setObjectName('circular-frequency-edit')
        ins_circular_frequency_edit.setFixedHeight(30)
        ins_circular_frequency_edit.setMaxLength(20)
        ins_circular_frequency_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_FLOAT_FORMAT)))
        ins_circular_frequency_edit.textChanged.connect(self.__slotClearViewChat)
        ins_form_layout.addRow('circular frequency:',ins_circular_frequency_edit)
        
        ins_params_table = QtWidgets.QTableWidget(self)
        ins_widgets_layout.addWidget(ins_params_table,1)
        ins_params_table.setObjectName('priodic-table')
        ins_params_table.setColumnCount(2)
        ins_params_table.horizontalHeader().setFixedHeight(30)
        ins_params_table.setHorizontalHeaderLabels(['A','B'])
        ins_params_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ins_params_table.horizontalHeader().setSectionsClickable(False)
        ins_params_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_params_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_params_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        ins_params_table.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
        ins_params_table.verticalHeader().setSectionsClickable(True)
        ins_params_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        ins_params_table.setRowCount(1)
        ins_params_table.setItem(0,0,QtWidgets.QTableWidgetItem())
        ins_params_table.setItem(0,1,QtWidgets.QTableWidgetItem())
        
        ins_params_table.itemChanged.connect(self.__slotClearViewChat)
        ins_params_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        ins_params_table.customContextMenuRequested.connect(self.__slotTableRightMenu)
    def __initializeSmoothTable(self, in_stacked_layout:object) -> None:
        ins_params_table = QtWidgets.QTableWidget(self)
        in_stacked_layout.addWidget(ins_params_table)
        
        ins_params_table.setObjectName('smooth-table')
        ins_params_table.setColumnCount(2)
        ins_params_table.horizontalHeader().setFixedHeight(30)
        ins_params_table.setHorizontalHeaderLabels(['Point','Scale'])
        ins_params_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        ins_params_table.horizontalHeader().setSectionsClickable(False)
        ins_params_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_params_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        ins_params_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        ins_params_table.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)
        ins_params_table.verticalHeader().setSectionsClickable(True)
        ins_params_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        ins_params_table.setRowCount(2)
        for row_index in range(2):
            ins_params_table.setItem(row_index,0,QtWidgets.QTableWidgetItem())
            ins_params_table.setItem(row_index,1,QtWidgets.QTableWidgetItem())
        
        ins_params_table.itemChanged.connect(self.__slotClearViewChat) 
        ins_params_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        ins_params_table.customContextMenuRequested.connect(self.__slotTableRightMenu)
    
    def __slotChangeFunctionType(self, in_type:str) -> None:
        ins_tables_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'tables-stacked-layout')
        ins_tables_stacked_layout.setCurrentIndex(in_type)
        
        self.__slotClearViewChat()
    def __slotCheckParameters(self) -> None:
        ins_plot_chart = self.findChild(QtCharts.QChartView,'function-chart-view').chart()
        ins_plot_chart.series()[0].clear()
        
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        ins_tables_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'tables-stacked-layout')
        if ins_tables_stacked_layout.currentIndex() == 0:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'piecewise-table')

            if ins_params_table.rowCount() < 2:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f'The table should have at least two rows!')
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None
            else:
                pass
            point_list,scale_list = [],[]
            for row_index in range(ins_params_table.rowCount()):
                try:
                    point_value = float(ins_params_table.item(row_index,0).text())
                    scale_value = float(ins_params_table.item(row_index,1).text())
                except:
                    QtWidgets.QMessageBox.critical(self,'Create Function Error',f'Row "{str(row_index+1)}" data error!')
                    self.__check_state = False
                    ins_accept_button.setEnabled(False)
                    return None
                else:
                    point_list.append(point_value)
                    scale_list.append(scale_value)
            if min(point_list) < 0 or max(point_list) > 1:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f'Point value should be in [0,1]!')
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None
            else:   pass
            if len(set(point_list)) == len(point_list):
                pass
            else:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f'Invalid point values,expected monotonically increasing numbers!')
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None

            sorted_point_list = point_list.copy()
            sorted_point_list.sort()
            if point_list == sorted_point_list:
                pass
            else:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f'Invalid point values,expected monotonically increasing numbers!')
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None
        
            xy_data_list = []
            if point_list[0] > 0.0:
                xy_data_list.append(QtCore.QPointF(0.0,scale_list[0]))
            else:
                pass
            for point_value,scale_value in zip(point_list,scale_list):
                xy_data_list.append(QtCore.QPointF(point_value,scale_value))
            if point_list[-1] < 1.0:
                xy_data_list.append(QtCore.QPointF(1.0,scale_list[-1]))
            else:
                pass
            min_y_data,max_y_data = min(scale_list),max(scale_list)
            if min_y_data == max_y_data:
                if min_y_data == 0.0:
                    ins_plot_chart.axisY().setRange(-0.2,0.2)
                else:
                    ins_plot_chart.axisY().setRange(min_y_data-abs(min_y_data)*0.1,max_y_data+abs(min_y_data)*0.1)
            else:
                ins_plot_chart.axisY().setRange(min_y_data-(max_y_data-min_y_data)*0.1,max_y_data+(max_y_data-min_y_data)*0.1)

            ins_plot_chart.series()[0].replace(xy_data_list)
            ins_plot_chart.series()[0].setPointsVisible(True)
        elif ins_tables_stacked_layout.currentIndex() == 1:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'priodic-table')

            if ins_params_table.rowCount() < 1:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f"The table should have at least one rows!")
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None
            else:
                pass

            an_list,bn_list = [],[]
            for row_index in range(ins_params_table.rowCount()):
                try:
                    an_value = float(ins_params_table.item(row_index,0).text())
                    bn_value = float(ins_params_table.item(row_index,1).text())
                except:
                    QtWidgets.QMessageBox.critical(self,'Create Function Error',f'Row "{str(row_index+1)}" data error!')
                    self.__check_state = False
                    ins_accept_button.setEnabled(False)
                    return None
                else:
                    an_list.append(an_value)
                    bn_list.append(bn_value)
        
            try:
                a0 = float(self.findChild(QtWidgets.QLineEdit,'initial-amplitude-edit').text())
                p0 = float(self.findChild(QtWidgets.QLineEdit,'initial-percentage-edit').text())
                cf = float(self.findChild(QtWidgets.QLineEdit,'circular-frequency-edit').text())
            except:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f'A0/P0/cf must be float number!')
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None
            else:
                pass

            if p0 == 1.0:
                xy_data_list = [QtCore.QPointF(0.0,a0),QtCore.QPointF(1.0,a0)]
                
                if a0 == 0:
                    ins_plot_chart.axisY().setRange(-0.2,0.2)
                else:
                    ins_plot_chart.axisY().setRange(a0-abs(a0)*0.1,a0+abs(a0)*0.1)
            elif p0 > 0.0:
                xy_data_list = [QtCore.QPointF(0.0,a0),QtCore.QPointF(p0,a0)]

                x_data_list = numpy.linspace(p0,1.0,50)
                y_data_list = []
                for x_data in x_data_list:
                    y_data = a0
                    for row_index in range(ins_params_table.rowCount()):
                        y_data += an_list[row_index]*numpy.cos((row_index+1)*cf*(x_data-p0)) + bn_list[row_index]*numpy.sin((row_index+1)*cf*(x_data-p0))
                    y_data_list.append(y_data)
                
                for x_data,y_data in zip(x_data_list,y_data_list):
                    xy_data_list.append(QtCore.QPointF(x_data,y_data))
            
                ins_plot_chart.axisY().setRange(min(y_data_list)-(max(y_data_list)-min(y_data_list))*0.1,max(y_data_list)+(max(y_data_list)-min(y_data_list))*0.1)
            else:
                xy_data_list = []

                x_data_list = numpy.linspace(0.0,1.0,50)
                y_data_list = []
                for x_data in x_data_list:
                    y_data = a0
                    for row_index in range(ins_params_table.rowCount()):
                        y_data += an_list[row_index]*numpy.cos((row_index+1)*cf*x_data) + bn_list[row_index]*numpy.sin((row_index+1)*cf*x_data)
                    y_data_list.append(y_data)

                for x_data,y_data in zip(x_data_list,y_data_list):
                    xy_data_list.append(QtCore.QPointF(x_data,y_data))
                
                ins_plot_chart.axisY().setRange(min(y_data_list)-(max(y_data_list)-min(y_data_list))*0.1,max(y_data_list)+(max(y_data_list)-min(y_data_list))*0.1)

            ins_plot_chart.series()[0].replace(xy_data_list)
            ins_plot_chart.series()[0].setPointsVisible(False)
        elif ins_tables_stacked_layout.currentIndex() == 2:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'piecewise-table')

            if ins_params_table.rowCount() < 2:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f'The table should have at least two rows!')
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None
            else:
                pass
            point_list,scale_list = [],[]
            for row_index in range(ins_params_table.rowCount()):
                try:
                    point_value = float(ins_params_table.item(row_index,0).text())
                    scale_value = float(ins_params_table.item(row_index,1).text())
                except:
                    QtWidgets.QMessageBox.critical(self,'Create Function Error',f'Row "{str(row_index+1)}" data error!')
                    self.__check_state = False
                    ins_accept_button.setEnabled(False)
                    return None
                else:
                    point_list.append(point_value)
                    scale_list.append(scale_value)
            if min(point_list) < 0 or max(point_list) > 1:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f'Point value should be in [0,1]!')
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None
            else:
                pass
            if len(set(point_list)) == len(point_list):
                pass
            else:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f'Invalid point values,expected monotonically increasing numbers!')
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None

            sorted_point_list = point_list.copy()
            sorted_point_list.sort()
            if point_list == sorted_point_list:
                pass
            else:
                QtWidgets.QMessageBox.critical(self,'Create Function Error',f'Invalid point values,expected monotonically increasing numbers!')
                self.__check_state = False
                ins_accept_button.setEnabled(False)
                return None
        
            xy_data_list = []
            if point_list[0] > 0:
                xy_data_list.append(QtCore.QPointF(0.0,scale_list[0]))
            else:
                pass
            for row_index in range(1,ins_params_table.rowCount()):
                x_data_list = numpy.linspace(point_list[row_index-1],point_list[row_index],20)
                if row_index == 1:
                    xy_data_list.append(QtCore.QPointF(point_list[0],scale_list[0]))
                else:
                    pass

                for x_data in x_data_list[1:]:
                    xi = (x_data-point_list[row_index-1]) / (point_list[row_index]-point_list[row_index-1])
                    y_data = scale_list[row_index-1] + (scale_list[row_index]-scale_list[row_index-1]) * xi**3 * (10.0-15.0*xi+6*xi**2)
                    xy_data_list.append(QtCore.QPointF(x_data,y_data))
            if point_list[-1] < 1.0:
                xy_data_list.append(QtCore.QPointF(1.0,scale_list[-1]))
            else:   pass
            min_y_data,max_y_data = min(scale_list),max(scale_list)
            if min_y_data == max_y_data:
                if min_y_data == 0.0:
                    ins_plot_chart.axisY().setRange(-0.2,0.2)
                else:
                    ins_plot_chart.axisY().setRange(min_y_data-abs(min_y_data)*0.1,max_y_data+abs(min_y_data)*0.1)
            else:
                ins_plot_chart.axisY().setRange(min_y_data-(max_y_data-min_y_data)*0.1,max_y_data+(max_y_data-min_y_data)*0.1)

            ins_plot_chart.series()[0].replace(xy_data_list)
            ins_plot_chart.series()[0].setPointsVisible(False)
        else:
            pass
        
        self.__check_state = True
        if self.__name_state and self.__check_state:
            ins_accept_button.setEnabled(True)
        else:
            ins_accept_button.setEnabled(False)
    
    def __slotTableRightMenu(self) -> None:
        ins_right_menu = QtWidgets.QMenu()
        ins_right_menu.deleteLater()

        ins_insert_row_before_action = ins_right_menu.addAction('insert row before')
        ins_insert_row_before_action.triggered.connect(self.__slotActionInsertRowBefore)

        ins_insert_row_after_action = ins_right_menu.addAction('insert row after')
        ins_insert_row_after_action.triggered.connect(self.__slotActionInsertRowAfter)

        ins_delete_row_content_action = ins_right_menu.addAction('delele row(s)')
        ins_delete_row_content_action.triggered.connect(self.__slotActionDeleteRows)

        ins_right_menu.addSeparator()

        ins_clear_table_action = ins_right_menu.addAction('clear table content')
        ins_clear_table_action.triggered.connect(self.__slotActionClearTableContent)

        ins_clear_table_action = ins_right_menu.addAction('remove all rows')
        ins_clear_table_action.triggered.connect(self.__slotActionRemoveAllRows)

        ins_right_menu.exec(QtGui.QCursor.pos())
    def __slotActionInsertRowBefore(self) -> None:
        ins_tables_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'tables-stacked-layout')
        if ins_tables_stacked_layout.currentIndex() == 0:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'piecewise-table')
        elif ins_tables_stacked_layout.currentIndex() == 1:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'priodic-table')
        elif ins_tables_stacked_layout.currentIndex() == 2:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'smooth-table')
        else:
            pass
        
        selected_rows_list = list(set([ins_item.row() for ins_item in ins_params_table.selectedItems()]))
        selected_rows_list.sort()
        if selected_rows_list == []:
            insert_row_index = 0
        else:   
            insert_row_index = selected_rows_list[0]

        ins_params_table.insertRow(insert_row_index)
        ins_params_table.setItem(insert_row_index,0,QtWidgets.QTableWidgetItem())
        ins_params_table.setItem(insert_row_index,1,QtWidgets.QTableWidgetItem())
        
        self.__slotClearViewChat()
    def __slotActionInsertRowAfter(self) -> None:
        ins_tables_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'tables-stacked-layout')
        if ins_tables_stacked_layout.currentIndex() == 0:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'piecewise-table')
        elif ins_tables_stacked_layout.currentIndex() == 1:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'priodic-table')
        elif ins_tables_stacked_layout.currentIndex() == 2:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'smooth-table')
        else:
            pass

        selected_rows_list = list(set([ins_item.row() for ins_item in ins_params_table.selectedItems()]))
        selected_rows_list.sort()
        if selected_rows_list == []:
            insert_row_index = ins_params_table.rowCount()
        else:
            insert_row_index = selected_rows_list[-1]+1

        ins_params_table.insertRow(insert_row_index)
        ins_params_table.setItem(insert_row_index,0,QtWidgets.QTableWidgetItem())
        ins_params_table.setItem(insert_row_index,1,QtWidgets.QTableWidgetItem())
        
        self.__slotClearViewChat()
    def __slotActionDeleteRows(self) -> None:
        ins_tables_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'tables-stacked-layout')
        if ins_tables_stacked_layout.currentIndex() == 0:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'piecewise-table')
        elif ins_tables_stacked_layout.currentIndex() == 1:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'priodic-table')
        elif ins_tables_stacked_layout.currentIndex() == 2:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'smooth-table')
        else:
            pass

        selected_rows_list = list(set([ins_item.row() for ins_item in ins_params_table.selectedItems()]))
        selected_rows_list.sort()
        selected_rows_list.reverse()
        for row_index in selected_rows_list:
            ins_params_table.removeRow(row_index)
    
        self.__slotClearViewChat()
    def __slotActionClearTableContent(self) -> None:
        ins_tables_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'tables-stacked-layout')
        if ins_tables_stacked_layout.currentIndex() == 0:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'piecewise-table')
        elif ins_tables_stacked_layout.currentIndex() == 1:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'priodic-table')
        elif ins_tables_stacked_layout.currentIndex() == 2:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'smooth-table')
        else:
            pass

        ins_params_table.clearContents()
        
        self.__slotClearViewChat()
    def __slotActionRemoveAllRows(self) -> None:
        ins_tables_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'tables-stacked-layout')
        if ins_tables_stacked_layout.currentIndex() == 0:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'piecewise-table')
        elif ins_tables_stacked_layout.currentIndex() == 1:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'priodic-table')
        elif ins_tables_stacked_layout.currentIndex() == 2:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'smooth-table')
        else:
            pass

        for row_index in range(ins_params_table.rowCount()-1,-1,-1):
            ins_params_table.removeRow(row_index)
    
        self.__slotClearViewChat()
    def __slotClearViewChat(self) -> None:
        ins_plot_chart = self.findChild(QtCharts.QChartView,'function-chart-view').chart()
        ins_plot_chart.series()[0].clear()
        
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        ins_accept_button.setEnabled(False)
        self.__check_state = False
    # endregion
    
    def __initializeDisplayChart(self, in_ins_central_layout:object) -> None:
        ins_chart_view = QtCharts.QChartView(self)
        in_ins_central_layout.addWidget(ins_chart_view,2)
   
        ins_chart_view.setObjectName('function-chart-view')
        ins_chart_view.setContentsMargins(0,0,0,0)
        ins_chart_view.setMinimumSize(450,400)
        
        ins_plot_chart = ins_chart_view.chart()
        ins_plot_chart.legend().hide()
        ins_plot_chart.setContentsMargins(0,0,0,0)
        
        ins_chart_axis_x = QtCharts.QValueAxis()
        ins_chart_axis_x.setRange(0,1.0)
        ins_chart_axis_x.setLabelFormat('%.1f')
        ins_chart_axis_x.setTickCount(10)
        ins_chart_axis_x.setTitleText('Normalized Points')
        ins_chart_axis_x.setGridLineVisible(True)
        ins_plot_chart.setAxisX(ins_chart_axis_x)
        ins_chart_axis_y = QtCharts.QValueAxis()
        ins_chart_axis_y.setRange(0,1.0)
        ins_chart_axis_y.setLabelFormat('%.2f')
        ins_chart_axis_y.setTickCount(10)
        ins_chart_axis_y.setTitleText('Scale Factor')
        ins_chart_axis_y.setGridLineVisible(True)
        ins_plot_chart.setAxisY(ins_chart_axis_y)
        
        ins_data_series = QtCharts.QLineSeries()
        ins_plot_chart.addSeries(ins_data_series)
        ins_data_series.attachAxis(ins_chart_axis_x)
        ins_data_series.attachAxis(ins_chart_axis_y)
      
    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getFunctionInformation(self) -> dict:
        function_info_dict = {}
        
        function_info_dict['name'] = self.findChild(QtWidgets.QLineEdit,'function-name-edit').text()
        function_info_dict['type'] = self.findChild(QtWidgets.QComboBox,'function-type-box').currentText()
        
        ins_tables_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'tables-stacked-layout')
        if ins_tables_stacked_layout.currentIndex() == 0:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'piecewise-table')
            
            point_list,scale_list = [],[]
            for row_index in range(ins_params_table.rowCount()):
                point_list.append(ins_params_table.item(row_index,0).text())
                scale_list.append(ins_params_table.item(row_index,1).text())
            
            function_info_dict['parameters'] = [point_list,scale_list]
        elif ins_tables_stacked_layout.currentIndex() == 1:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'priodic-table')
            
            initial_amplitude = self.findChild(QtWidgets.QLineEdit,'initial-amplitude-edit').text()
            initial_percentag = self.findChild(QtWidgets.QLineEdit,'initial-percentage-edit').text()
            circular_frequenc = self.findChild(QtWidgets.QLineEdit,'circular-frequency-edit').text()
            
            an_list,bn_list = [],[]
            for row_index in range(ins_params_table.rowCount()):
                an_list.append(ins_params_table.item(row_index,0).text())
                bn_list.append(ins_params_table.item(row_index,1).text())
            
            function_info_dict['parameters'] = [[initial_amplitude,initial_percentag,circular_frequenc],an_list,bn_list]
        elif ins_tables_stacked_layout.currentIndex() == 2:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'smooth-table')
            
            point_list,scale_list = [],[]
            for row_index in range(ins_params_table.rowCount()):
                point_list.append(ins_params_table.item(row_index,0).text())
                scale_list.append(ins_params_table.item(row_index,1).text())
            
            function_info_dict['parameters'] = [point_list,scale_list]
        else:
            pass
        
        return function_info_dict
    def setFunctionInformation(self, in_function_name:str, in_function_information:dict) -> None:
        ins_name_line_edit = self.findChild(QtWidgets.QLineEdit,'function-name-edit')
        ins_name_line_edit.setText(in_function_name)
        ins_name_line_edit.setEnabled(False)
        
        self.findChild(QtWidgets.QComboBox,'function-type-box').setCurrentText(in_function_information['type'])
        
        ins_tables_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'tables-stacked-layout')
        if ins_tables_stacked_layout.currentIndex() == 0:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'piecewise-table')
            
            ins_params_table.setRowCount(len(in_function_information['parameters'][0]))
            for row_index in range(2,ins_params_table.rowCount()):
                ins_params_table.setItem(row_index,0,QtWidgets.QTableWidgetItem())
                ins_params_table.setItem(row_index,1,QtWidgets.QTableWidgetItem())
            for row_index in range(ins_params_table.rowCount()):
                ins_params_table.item(row_index,0).setText(in_function_information['parameters'][0][row_index])
                ins_params_table.item(row_index,1).setText(in_function_information['parameters'][1][row_index])
        elif ins_tables_stacked_layout.currentIndex() == 1:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'priodic-table')
            
            self.findChild(QtWidgets.QLineEdit,'initial-amplitude-edit').setText(in_function_information[0][0])
            self.findChild(QtWidgets.QLineEdit,'initial-percentage-edit').setText(in_function_information[0][1])
            self.findChild(QtWidgets.QLineEdit,'circular-frequency-edit').setText(in_function_information[0][2])
            
            ins_params_table.setRowCount(len(in_function_information['parameters'][1]))
            for row_index in range(ins_params_table.rowCount()):
                ins_params_table.item(row_index,0).setText(in_function_information['parameters'][1][row_index])
                ins_params_table.item(row_index,1).setText(in_function_information['parameters'][2][row_index])
        elif ins_tables_stacked_layout.currentIndex() == 2:
            ins_params_table = self.findChild(QtWidgets.QTableWidget,'smooth-table')
            
            ins_params_table.setRowCount(len(in_function_information['parameters'][0]))
            for row_index in range(ins_params_table.rowCount()):
                ins_params_table.item(row_index,0).setText(in_function_information['parameters'][0][row_index])
                ins_params_table.item(row_index,1).setText(in_function_information['parameters'][1][row_index])
        else:
            pass


class P4SResultManager(QtWidgets.QWidget):
    
    def __init__(self, in_parent:object):
        super().__init__(parent=in_parent)
        self.setObjectName('result-manager')
        
        self.__database_pointer_dict = {}
        self.__contour_selection_mode = None
        self.__contour_selected_labels_dict = {}
        
        ins_result_manager_layout = QtWidgets.QVBoxLayout()
        ins_result_manager_layout.setContentsMargins(2,5,0,0)
        self.setLayout(ins_result_manager_layout)
        self.__initializeResultInformationLayout(ins_result_manager_layout)
        
        ins_manager_stacked_layout = QtWidgets.QStackedLayout()
        ins_manager_stacked_layout.setObjectName('manager-stacked-layout')
        ins_result_manager_layout.addLayout(ins_manager_stacked_layout,0)
    def __initializeResultInformationLayout(self, in_ins_result_manager_layout:object) -> None:
        ins_result_information_layout = QtWidgets.QHBoxLayout()
        in_ins_result_manager_layout.addLayout(ins_result_information_layout,0)
        
        ins_result_database_label = QtWidgets.QLabel('result database:',self,alignment=QtCore.Qt.AlignCenter)
        ins_result_database_label.setObjectName('result-database-label')
        ins_result_database_label.setFixedSize(140,32)
        ins_result_information_layout.addWidget(ins_result_database_label,0)
        
        ins_result_database_box = QtWidgets.QComboBox(self)
        ins_result_database_box.setObjectName('result-database-box')
        ins_result_database_box.setFixedHeight(35)
        ins_result_database_box.currentTextChanged.connect(self.__slotChangeResultDatabase)
        ins_result_information_layout.addWidget(ins_result_database_box,1)
    # region
    def __slotChangeResultDatabase(self, in_database_full_name:str) -> None:
        ins_main_window = self.parent().parent().parent().parent()
        
        ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
        ins_visualization_toolbar.clearToolsState()
        
        if in_database_full_name == '':
            return None
        else:
            pass
        
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = self.findChild(QtWidgets.QWidget,in_database_full_name)
        ins_manager_stacked_layout.setCurrentWidget(ins_setting_widget)
        
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        for ins_database_visual_window in ins_results_mdi_area.subWindowList():
            ins_database_visual_window.close()
        ins_database_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,in_database_full_name)
        ins_database_visual_window.showMaximized()
    # endregion

    def getExistResultDatabaseFullName(self) -> list:
        return list(self.__database_pointer_dict.keys())
    def getCurrentStepAndFrame(self) -> list:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        
        ins_steps_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'steps-box')
        ins_step_frames_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'step-frames-box')
        
        return [ins_steps_box.currentText(),ins_step_frames_box.currentText()]
    
    def createResultManager(self,in_result_full_name:str) -> None:
        self.__database_pointer_dict[in_result_full_name] = h5py.File(in_result_full_name,'r')
        
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        from .visualization import P4SResultVisualWindow
        P4SResultVisualWindow(ins_results_mdi_area,in_result_full_name,self.__database_pointer_dict[in_result_full_name])
        del P4SResultVisualWindow
        
        ins_setting_widget = QtWidgets.QWidget(self)
        ins_setting_widget.setObjectName(in_result_full_name)
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_manager_stacked_layout.addWidget(ins_setting_widget)
        ins_setting_layout = QtWidgets.QVBoxLayout()
        ins_setting_layout.setContentsMargins(0,0,0,0)
        ins_setting_widget.setLayout(ins_setting_layout)
        
        # region
        ins_variable_information_layout = QtWidgets.QHBoxLayout()
        ins_setting_layout.addLayout(ins_variable_information_layout)
        ins_variables_box = QtWidgets.QComboBox(ins_setting_widget)
        ins_variables_box.setObjectName('variables-box')
        ins_variables_box.setFixedSize(120,30)
        variables_name_list = []
        for variable_name in self.__database_pointer_dict[in_result_full_name]['Nodes'].keys():
            variables_name_list.append(variable_name)
        for variable_name in self.__database_pointer_dict[in_result_full_name]['Elements'].keys():
            variables_name_list.append(variable_name)
        ins_variables_box.addItems(variables_name_list)
        ins_variables_box.setCurrentIndex(-1)
        ins_variables_box.currentTextChanged.connect(self.__slotChangeVariable)
        ins_variable_information_layout.addWidget(ins_variables_box)
        ins_variable_components_box = QtWidgets.QComboBox(ins_setting_widget)
        ins_variable_components_box.setObjectName('variable-components-box')
        ins_variable_components_box.setFixedSize(120,30)
        ins_variable_components_box.currentTextChanged.connect(self.__slotChangeVariableComponent)
        ins_variable_information_layout.addWidget(ins_variable_components_box)
        ins_variable_information_layout.addStretch()
        
        ins_step_information_layout = QtWidgets.QHBoxLayout()
        ins_setting_layout.addLayout(ins_step_information_layout)
        ins_steps_box = QtWidgets.QComboBox(ins_setting_widget)
        ins_steps_box.setObjectName('steps-box')
        ins_steps_box.setFixedSize(120,30)
        ins_steps_box.currentTextChanged.connect(self.__slotChangeStep)
        ins_step_information_layout.addWidget(ins_steps_box)
        ins_step_frames_box = QtWidgets.QComboBox(ins_setting_widget)
        ins_step_frames_box.setObjectName('step-frames-box')
        ins_step_frames_box.setFixedSize(120,30)
        ins_step_frames_box.currentTextChanged.connect(self.__slotChangeFrame)
        ins_step_information_layout.addWidget(ins_step_frames_box)
        ins_left_move_frame_button = QtWidgets.QPushButton(ins_setting_widget)
        ins_left_move_frame_button.setObjectName('left-move-button')
        ins_left_move_frame_button.setText('<<')
        ins_left_move_frame_button.setFixedSize(70,30)
        ins_left_move_frame_button.clicked.connect(self.__slotLeftMoveFrame)
        ins_step_information_layout.addWidget(ins_left_move_frame_button)
        ins_right_move_frame_button = QtWidgets.QPushButton(ins_setting_widget)
        ins_right_move_frame_button.setObjectName('right-move-button')
        ins_right_move_frame_button.setText('>>')
        ins_right_move_frame_button.setFixedSize(70,30)
        ins_right_move_frame_button.clicked.connect(self.__slotRightMoveFrame)
        ins_step_information_layout.addWidget(ins_right_move_frame_button)
        ins_step_information_layout.addStretch()
        
        ins_deformation_information_layout = QtWidgets.QHBoxLayout()
        ins_setting_layout.addLayout(ins_deformation_information_layout)
        ins_deformation_type_box = QtWidgets.QComboBox(ins_setting_widget)
        ins_deformation_type_box.setObjectName('deformation-type-box')
        ins_deformation_type_box.addItems(['undeformed','deformed'])
        ins_deformation_type_box.setFixedSize(120,30)
        ins_deformation_type_box.currentTextChanged.connect(self.__slotChangeDeformationType)
        ins_deformation_information_layout.addWidget(ins_deformation_type_box)
        ins_deform_factor_edit = QtWidgets.QLineEdit(ins_setting_widget)
        ins_deform_factor_edit.setObjectName('deform-factor-edit')
        ins_deform_factor_edit.setMaxLength(8)
        ins_deform_factor_edit.setPlaceholderText('factor')
        ins_deform_factor_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.FLOAT_FORMAT)))
        ins_deform_factor_edit.setText('1.0')
        ins_deform_factor_edit.setFixedSize(120,30)
        ins_deformation_information_layout.addWidget(ins_deform_factor_edit)
        ins_apply_deform_fator = QtWidgets.QPushButton(ins_setting_widget)
        ins_apply_deform_fator.setObjectName('apply-factor-button')
        ins_apply_deform_fator.setText('apply')
        ins_apply_deform_fator.setFixedSize(70,30)
        ins_apply_deform_fator.clicked.connect(self.__slotApplyDeformation)
        ins_deformation_information_layout.addWidget(ins_apply_deform_fator)
        ins_deformation_information_layout.addStretch()
        if 'U' in variables_name_list:
            pass
        else:
            ins_deformation_type_box.setEnabled(False)
            ins_deform_factor_edit.setEnabled(False)
            ins_apply_deform_fator.setEnabled(False)
        
        ins_style_information_layout = QtWidgets.QHBoxLayout()
        ins_setting_layout.addLayout(ins_style_information_layout)
        ins_color_map_box = QtWidgets.QComboBox(ins_setting_widget)
        ins_color_map_box.setObjectName('color-map-box')
        ins_color_map_box.addItems(['rainbow','jet','Greys','cool'])
        ins_color_map_box.setFixedSize(120,30)
        ins_color_map_box.currentTextChanged.connect(self.__slotChangeColorMap)
        ins_style_information_layout.addWidget(ins_color_map_box)
        ins_color_number_box = QtWidgets.QComboBox(ins_setting_widget)
        ins_color_number_box.setObjectName('color-number-box')
        ins_color_number_box.setFixedSize(70,30)
        ins_color_number_box.addItems([str(i) for i in list(range(2,25,1))])
        ins_color_number_box.setCurrentText('12')
        ins_color_number_box.currentTextChanged.connect(self.__slotChangeColorNumber)
        ins_style_information_layout.addWidget(ins_color_number_box)
        ins_style_information_layout.addStretch()
        
        ins_export_buttons_layout = QtWidgets.QHBoxLayout()
        ins_setting_layout.addLayout(ins_export_buttons_layout)
        ins_export_to_cvs_button = QtWidgets.QPushButton(ins_setting_widget)
        ins_export_to_cvs_button.setObjectName('contour-to-csv-button')
        ins_export_to_cvs_button.setFixedSize(90,30)
        ins_export_to_cvs_button.setText('to csv')
        ins_export_to_cvs_button.clicked.connect(self.__slotExportContourDataToCSV)
        ins_export_buttons_layout.addWidget(ins_export_to_cvs_button)
        ins_export_to_image_button = QtWidgets.QPushButton(ins_setting_widget)
        ins_export_to_image_button.setFixedSize(90,30)
        ins_export_to_image_button.setObjectName('contour-to-image-button')
        ins_export_to_image_button.setText('to image')
        ins_export_to_image_button.clicked.connect(self.__slotExportContourDataToImage)
        ins_export_buttons_layout.addWidget(ins_export_to_image_button)
        ins_export_buttons_layout.addStretch()
        # endregion
            
        ins_graph_list = QtWidgets.QListWidget(ins_setting_widget)
        ins_graph_list.setObjectName('graphs-list')
        ins_graph_list.setContentsMargins(0,0,0,0)
        ins_graph_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        ins_graph_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        ins_graph_list.customContextMenuRequested.connect(self.__slotRightClickMenu)
        ins_graph_list.currentItemChanged.connect(self.__slotSwitchGraph)
        ins_setting_layout.addWidget(ins_graph_list,1)
        ins_graph_list.setEnabled(False)
        
        ins_result_database_box = self.findChild(QtWidgets.QComboBox,'result-database-box')
        ins_result_database_box.addItem(in_result_full_name)
        ins_result_database_box.setCurrentText(in_result_full_name)
    # region
    def __slotChangeVariable(self,in_variable_name:str) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        ins_variable_components_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'variable-components-box')
        ins_variable_components_box.currentTextChanged.disconnect(self.__slotChangeVariableComponent)
        ins_variable_components_box.clear()
        model_dimension = str(self.__database_pointer_dict[current_database_full_name]['basic'][0],'utf=8')
        ins_variable_components_box.addItems(common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name])
        ins_variable_components_box.currentTextChanged.connect(self.__slotChangeVariableComponent)
        
        ins_steps_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'steps-box')
        ins_step_frames_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'step-frames-box')
        ins_steps_box.currentTextChanged.disconnect(self.__slotChangeStep)
        ins_step_frames_box.currentTextChanged.disconnect(self.__slotChangeFrame)
        # region
        ins_steps_box.clear()
        steps_name_list = list(self.__database_pointer_dict[current_database_full_name]['Steps'].keys())
        ins_steps_box.addItems(steps_name_list)
        
        ins_step_frames_box.clear()
        if in_variable_name in self.__database_pointer_dict[current_database_full_name]['Nodes']:
            frames_name_list = list(self.__database_pointer_dict[current_database_full_name]['Nodes'][in_variable_name][steps_name_list[0]].keys())
        elif in_variable_name in self.__database_pointer_dict[current_database_full_name]['Elements']:
            frames_name_list = list(self.__database_pointer_dict[current_database_full_name]['Elements'][in_variable_name][steps_name_list[0]].keys())
        else:
            pass
        frames_number_list = [int(frame_name) for frame_name in frames_name_list]
        frames_number_list.sort()
        ins_step_frames_box.addItems([str(frame_number) for frame_number in frames_number_list])
        # endregion
        ins_steps_box.currentTextChanged.connect(self.__slotChangeStep)
        ins_step_frames_box.currentTextChanged.connect(self.__slotChangeFrame)

        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        ins_result_visual_window.changeVariableOfViewport(in_variable_name)
    def __slotChangeVariableComponent(self,in_component_name:str) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        
        current_step_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'steps-box').currentText()
        current_frame_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'step-frames-box').currentText()
        
        current_database_full_name = current_database_full_name = ins_setting_widget.objectName()
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        ins_result_visual_window.changeVariableComponent(current_step_name, current_frame_name, in_component_name)
    
    def __slotChangeStep(self,in_step_name:str) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        ins_step_frames_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'step-frames-box')
        ins_step_frames_box.currentTextChanged.disconnect(self.__slotChangeFrame)
        ins_step_frames_box.clear()
        ins_step_frames_box.currentTextChanged.connect(self.__slotChangeFrame)
        
        ins_variables_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'variables-box')
        variable_name = ins_variables_box.currentText()
        if variable_name in self.__database_pointer_dict[current_database_full_name]['Nodes']:
            frames_list = (self.__database_pointer_dict[current_database_full_name]['Nodes'][variable_name][in_step_name].keys())
        elif variable_name in self.__database_pointer_dict[current_database_full_name]['Elements']:
            frames_list = (self.__database_pointer_dict[current_database_full_name]['Elements'][variable_name][in_step_name].keys())
        else:
            pass
        frames_number_list = [int(frame) for frame in frames_list]
        frames_number_list.sort()
        ins_step_frames_box.addItems([str(frame_number) for frame_number in frames_number_list])
    def __slotChangeFrame(self,in_frame_name:str) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        variable_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'variables-box').currentText()
        component_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'variable-components-box').currentText()
        step_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'steps-box').currentText()
        
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        ins_result_visual_window.changeFrameOfViewport(variable_name,component_name,step_name,in_frame_name)
    def __slotLeftMoveFrame(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        variable_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'variables-box').currentText()
        if variable_name == '':
            return
        else:
            pass
        component_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'variable-components-box').currentText()
        
        ins_steps_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'steps-box')
        ins_step_frames_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'step-frames-box')
        ins_steps_box.currentTextChanged.disconnect(self.__slotChangeStep)
        ins_step_frames_box.currentTextChanged.disconnect(self.__slotChangeFrame)
        
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        if ins_step_frames_box.currentIndex() == 0:
            if ins_steps_box.currentIndex() == 0:
                pass
            else:
                before_step_name = ins_steps_box.itemText(ins_steps_box.currentIndex()-1)
                ins_steps_box.setCurrentText(before_step_name)
                
                if variable_name in self.__database_pointer_dict[current_database_full_name]['Nodes']:
                    frames_list = (self.__database_pointer_dict[current_database_full_name]['Nodes'][variable_name][before_step_name].keys())
                elif variable_name in self.__database_pointer_dict[current_database_full_name]['Elements']:
                    frames_list = (self.__database_pointer_dict[current_database_full_name]['Elements'][variable_name][before_step_name].keys())
                else:
                    pass
                frames_number_list = [int(frame) for frame in frames_list]
                frames_number_list.sort()
                ins_step_frames_box.clear()
                ins_step_frames_box.addItems([str(frame_number) for frame_number in frames_number_list])
                ins_step_frames_box.setCurrentText(str(frames_number_list[-1]))
            
                ins_result_visual_window.changeFrameOfViewport(variable_name,component_name,before_step_name,str(frames_number_list[-1]))
        else:
            current_step_name = ins_steps_box.currentText()
            
            before_frame_name = ins_step_frames_box.itemText(ins_step_frames_box.currentIndex()-1)
            ins_step_frames_box.setCurrentText(before_frame_name)
            
            ins_result_visual_window.changeFrameOfViewport(variable_name,component_name,current_step_name,before_frame_name)
        
        ins_steps_box.currentTextChanged.connect(self.__slotChangeStep)
        ins_step_frames_box.currentTextChanged.connect(self.__slotChangeFrame)
    def __slotRightMoveFrame(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        variable_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'variables-box').currentText()
        if variable_name == '':
            return None
        else:
            pass
        component_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'variable-components-box').currentText()
        
        ins_steps_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'steps-box')
        ins_step_frames_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'step-frames-box')
        ins_steps_box.currentTextChanged.disconnect(self.__slotChangeStep)
        ins_step_frames_box.currentTextChanged.disconnect(self.__slotChangeFrame)
        
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        if ins_step_frames_box.currentIndex() == ins_step_frames_box.count()-1:
            if ins_steps_box.currentIndex() == ins_steps_box.count()-1:
                pass
            else:
                after_step_name = ins_steps_box.itemText(ins_steps_box.currentIndex()+1)
                ins_steps_box.setCurrentText(after_step_name)
                
                if variable_name in self.__database_pointer_dict[current_database_full_name]['Nodes']:
                    frames_list = (self.__database_pointer_dict[current_database_full_name]['Nodes'][variable_name][after_step_name].keys())
                elif variable_name in self.__database_pointer_dict[current_database_full_name]['Elements']:
                    frames_list = (self.__database_pointer_dict[current_database_full_name]['Elements'][variable_name][after_step_name].keys())
                else:
                    pass
                frames_number_list = [int(frame) for frame in frames_list]
                frames_number_list.sort()
                ins_step_frames_box.clear()
                ins_step_frames_box.addItems([str(frame_number) for frame_number in frames_number_list])
                
                ins_result_visual_window.changeFrameOfViewport(variable_name,component_name,after_step_name,'0')
        else:
            current_step_name = ins_steps_box.currentText()
            
            after_frame_name = ins_step_frames_box.itemText(ins_step_frames_box.currentIndex()+1)
            ins_step_frames_box.setCurrentText(after_frame_name)
            
            ins_result_visual_window.changeFrameOfViewport(variable_name,component_name,current_step_name,after_frame_name)
        
        ins_steps_box.currentTextChanged.connect(self.__slotChangeStep)
        ins_step_frames_box.currentTextChanged.connect(self.__slotChangeFrame)
    
    def __slotChangeDeformationType(self, in_type:str) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()

        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        if in_type == 'undeformed':
            ins_result_visual_window.changeDeformationStateOfViewport()
        elif in_type == 'deformed':
            current_step_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'steps-box').currentText()
            current_frame_name = self.findChild(QtWidgets.QComboBox,'step-frames-box').currentText()
            deform_factor = float(ins_setting_widget.findChild(QtWidgets.QLineEdit,'deform-factor-edit').text())

            ins_result_visual_window.changeDeformationStateOfViewport([current_step_name,current_frame_name,deform_factor])
        else:
            pass
    def __slotApplyDeformation(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        deformation_type = ins_setting_widget.findChild(QtWidgets.QComboBox,'deformation-type-box').currentText()
        if deformation_type == 'deformed':
            deform_factor = float(ins_setting_widget.findChild(QtWidgets.QLineEdit,'deform-factor-edit').text())
            
            current_step_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'steps-box').currentText()
            current_frame_name = self.findChild(QtWidgets.QComboBox,'step-frames-box').currentText()
            deform_factor = float(ins_setting_widget.findChild(QtWidgets.QLineEdit,'deform-factor-edit').text())
            
            ins_main_window = self.parent().parent().parent().parent()
            ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
            ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)

            ins_result_visual_window.changeDeformationStateOfViewport([current_step_name,current_frame_name,deform_factor])
        else:
            return
        
    def __slotChangeColorMap(self, in_map_name:str) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        ins_result_visual_window.changeColorMapOfViewport(in_map_name)
    def __slotChangeColorNumber(self, in_color_number:str) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        color_map_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'color-map-box').currentText()
        
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        ins_result_visual_window.changeColorNumberOfViewport(color_map_name,int(in_color_number))
    
    def __slotExportContourDataToCSV(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        variable_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'variables-box').currentText()
        if variable_name == '':
            return None
        else:
            pass
        
        ins_main_window = self.parent().parent().parent().parent()
        csv_file_full_name = QtWidgets.QFileDialog.getSaveFileName(ins_setting_widget,'Export Data To CSV File',ins_main_window.work_path,'*.csv')[0]
        if csv_file_full_name == '':
            return None
        else:
            ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
            ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
            ins_result_visual_window.exportContourDataToCSVOfViewport(csv_file_full_name)
    def __slotExportContourDataToImage(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        variable_name = ins_setting_widget.findChild(QtWidgets.QComboBox,'variables-box').currentText()
        if variable_name == '':
            return None
        else:
            pass
        
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        ins_result_visual_window.exportContourDataToImageOfViewport(ins_main_window.work_path)
    # endregion
    def __slotRightClickMenu(self, in_click_point:object) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        ins_graph_list = ins_setting_widget.findChild(QtWidgets.QListWidget,'graphs-list')
        
        ins_clicked_item = ins_graph_list.itemAt(in_click_point)
        
        ins_right_menu = QtWidgets.QMenu()
        ins_right_menu.deleteLater()
        
        ins_create_graph = ins_right_menu.addAction('create')
        ins_create_graph.triggered.connect(self.__slotCreateGraph)
        
        ins_right_menu.addSeparator()
        
        if ins_clicked_item is None:
            pass
        else:
            ins_rename_graph = ins_right_menu.addAction('rename')
            ins_rename_graph.triggered.connect(self.__slotRenameGraph)
            
            ins_to_csv_graph = ins_right_menu.addAction('to csv')
            ins_to_csv_graph.triggered.connect(self.__slotGraphDataToCSV)
            
            ins_to_image_graph = ins_right_menu.addAction('to image')
            ins_to_image_graph.triggered.connect(self.__slotGraphDataToImage)
            
            ins_delete_graph = ins_right_menu.addAction('delete')
            ins_delete_graph.triggered.connect(self.__slotDeleteGraph)
                                                        
        ins_right_menu.exec(QtGui.QCursor.pos())
    # region
    def __slotCreateGraph(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        ins_graph_list = ins_setting_widget.findChild(QtWidgets.QListWidget,'graphs-list')
        exist_graphs_name_list = [ins_graph_list.item(item_index).text() for item_index in range(ins_graph_list.count())]
        
        ins_create_graph_dialog = _CreateGraphDialog(ins_graph_list,self.__database_pointer_dict[current_database_full_name],exist_graphs_name_list,self.__contour_selection_mode,self.__contour_selected_labels_dict)
        ins_create_graph_dialog.show()
        if ins_create_graph_dialog.exec() == QtWidgets.QDialog.Accepted:
            graph_infomation_dict = ins_create_graph_dialog.getGraphInformation()
            if graph_infomation_dict['data'] ==[]:
                QtWidgets.QMessageBox.critical(self,'Create Graph Error','Output data is empty!')
                ins_create_graph_dialog.deleteLater()
                return None
            elif graph_infomation_dict['object'][0] == 'group' and graph_infomation_dict['object'][1] == '':
                QtWidgets.QMessageBox.critical(self,'Create Graph Error','Group is empty!')
                ins_create_graph_dialog.deleteLater()
                return None
            elif graph_infomation_dict['object'][0] == 'label' and '' in graph_infomation_dict['object'][1:]:
                if graph_infomation_dict["object"][1] == '':
                    QtWidgets.QMessageBox.critical(self,'Create Graph Error',"Instance is empty!")
                    ins_create_graph_dialog.deleteLater()
                    return None
                elif graph_infomation_dict["object"][2] == '':
                    QtWidgets.QMessageBox.critical(self,'Create Graph Error',"Label is empty!")
                    ins_create_graph_dialog.deleteLater()
                    return None
                else:
                    pass
            else:
                pass
            
            if graph_infomation_dict['position'] == 'Node' and graph_infomation_dict['object'][0] == 'label':
                graph_infomation_dict['object'][2] = int(graph_infomation_dict['object'][2])
                
                instance_location_array = self.__database_pointer_dict[current_database_full_name]['Mesh']['Instances'][graph_infomation_dict['object'][1]]
                if graph_infomation_dict['object'][2] > (instance_location_array[1]-instance_location_array[0]+1):
                    QtWidgets.QMessageBox.critical(self,'Create Graph Error','Node label more than maximum value!')
                    ins_create_graph_dialog.deleteLater()
                    return None
                else:
                    pass
            elif graph_infomation_dict['position'] == 'Element' and graph_infomation_dict['object'][0] == 'label':
                graph_infomation_dict['object'][2] = int(graph_infomation_dict['object'][2])
                
                instance_location_array = self.__database_pointer_dict[current_database_full_name]['Mesh']['Instances'][graph_infomation_dict['object'][1]]
                if graph_infomation_dict['object'][2] > (instance_location_array[3]-instance_location_array[2]+1):
                    QtWidgets.QMessageBox.critical(self,'Create Graph Error','Element label more than maximum value!')
                    ins_create_graph_dialog.deleteLater()
                    return None
                else:
                    pass
            else:
                pass
            
            if graph_infomation_dict['object'][0] == 'view':
                graph_infomation_dict['object'].append(self.__contour_selected_labels_dict)
            else:
                pass
            
            ins_main_window = self.parent().parent().parent().parent()
            ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
            ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
            ins_result_visual_window.createGraphOfViewport(graph_infomation_dict)

            ins_graph_item = QtWidgets.QListWidgetItem()
            ins_graph_item.setText(graph_infomation_dict['name'])
            ins_graph_list.addItem(ins_graph_item)
            ins_graph_list.setCurrentItem(ins_graph_item)
        else:
            pass
        ins_create_graph_dialog.deleteLater()
    def __slotRenameGraph(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        ins_graph_list = ins_setting_widget.findChild(QtWidgets.QListWidget,'graphs-list')
        exist_graphs_name_list = [ins_graph_list.item(item_index).text() for item_index in range(ins_graph_list.count())]
        
        graph_new_name, response_state = QtWidgets.QInputDialog.getText(ins_graph_list,'Rename Graph','New Name:')
        if response_state:
            pass
        else:
            return None
        if graph_new_name in exist_graphs_name_list:
            QtWidgets.QMessageBox.critical(ins_graph_list,'Rename Graph Error','The name already exist!')
            return None
        else:
            pass
        
        ins_current_graph_item = ins_graph_list.currentItem()
        graph_old_name = ins_current_graph_item.text()
        ins_current_graph_item.setText(graph_new_name)
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        ins_result_visual_window.renameGraphOfViewport(graph_old_name,graph_new_name)
    def __slotGraphDataToCSV(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()

        ins_graph_list = ins_setting_widget.findChild(QtWidgets.QListWidget,'graphs-list')
        ins_current_graph_item = ins_graph_list.currentItem()
        
        ins_main_window = self.parent().parent().parent().parent()
        
        csv_file_full_name = QtWidgets.QFileDialog.getSaveFileName(ins_graph_list,'Export Data To CSV File',ins_main_window.work_path,'*.csv')[0]
        if csv_file_full_name == '':
            return None
        else:
            ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
            ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
            ins_result_visual_window.exportGraphDataToCSVOfViewport(ins_current_graph_item.text(),csv_file_full_name)
    def __slotGraphDataToImage(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()

        ins_graph_list = ins_setting_widget.findChild(QtWidgets.QListWidget,'graphs-list')
        ins_current_graph_item = ins_graph_list.currentItem()
        
        ins_current_graph_item = ins_graph_list.currentItem()
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        ins_result_visual_window.exportGraphToImageOfViewport(ins_current_graph_item.text(),ins_main_window.work_path)
    def __slotDeleteGraph(self) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()

        ins_graph_list = ins_setting_widget.findChild(QtWidgets.QListWidget,'graphs-list')
        ins_current_graph_item = ins_graph_list.takeItem(ins_graph_list.currentRow())
        
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
        ins_result_visual_window.deleteGraphOfViewport(ins_current_graph_item.text())
        
        del ins_current_graph_item
    # endregion
    def __slotSwitchGraph(self, in_current_item:object) -> None:
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        current_database_full_name = ins_setting_widget.objectName()
        
        if in_current_item is None:
            return None
        else:
            ins_main_window = self.parent().parent().parent().parent()
            ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
            ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_database_full_name)
            ins_result_visual_window.switchGraphOfViewport(in_current_item.text())

    def closeCurrentResultManager(self) -> None:
        ins_result_database_box = self.findChild(QtWidgets.QComboBox,'result-database-box')
        current_result_full_name = ins_result_database_box.currentText()
        current_result_database_index = ins_result_database_box.currentIndex()
        ins_result_database_box.removeItem(current_result_database_index)
        
        ins_main_window = self.parent().parent().parent().parent()
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,current_result_full_name)
        ins_result_visual_window.finalizeInteractor()
        ins_result_visual_window.close(in_enable_hide=False)
        ins_result_visual_window.setParent(None)
        if ins_result_visual_window not in ins_results_mdi_area.subWindowList():
            pass
        else:
            ins_results_mdi_area.removeSubWindow(ins_result_visual_window)
            ins_result_visual_window.deleteLater()
        
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = self.findChild(QtWidgets.QWidget,current_result_full_name)
        ins_setting_widget.setParent(None)
        ins_manager_stacked_layout.removeWidget(ins_setting_widget)
        ins_setting_widget.deleteLater() 

        self.__database_pointer_dict[current_result_full_name].close()
        del self.__database_pointer_dict[current_result_full_name]
    
    def changeResultMode(self) -> None:
        ins_main_window = self.parent().parent().parent().parent()
        
        ins_manager_stacked_layout = self.findChild(QtWidgets.QStackedLayout,'manager-stacked-layout')
        ins_setting_widget = ins_manager_stacked_layout.currentWidget()
        
        ins_variables_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'variables-box')
        ins_variable_components_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'variable-components-box')
        ins_steps_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'steps-box')
        ins_step_frames_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'step-frames-box')
        ins_left_move_frame_button = ins_setting_widget.findChild(QtWidgets.QPushButton,'left-move-button')
        ins_right_move_frame_button = ins_setting_widget.findChild(QtWidgets.QPushButton,'right-move-button')
        ins_deformation_type_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'deformation-type-box')
        ins_deform_factor_edit = ins_setting_widget.findChild(QtWidgets.QLineEdit,'deform-factor-edit')
        ins_apply_deform_fator = ins_setting_widget.findChild(QtWidgets.QPushButton,'apply-factor-button')
        ins_color_map_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'color-map-box')
        ins_color_number_box = ins_setting_widget.findChild(QtWidgets.QComboBox,'color-number-box')
        ins_export_to_csv_button = ins_setting_widget.findChild(QtWidgets.QPushButton,'contour-to-csv-button')
        ins_export_to_image_button = ins_setting_widget.findChild(QtWidgets.QPushButton,'contour-to-image-button')
        
        ins_graph_list = ins_setting_widget.findChild(QtWidgets.QListWidget,'graphs-list')
        
        ins_results_mdi_area = ins_main_window.centralWidget().widget(1)
        ins_result_visual_window = ins_results_mdi_area.findChild(QtWidgets.QMdiSubWindow,ins_setting_widget.objectName())
        if ins_graph_list.isEnabled():
            self.__contour_selection_mode = None
            self.__contour_selected_labels_dict.clear()
        else:
            self.__contour_selection_mode = ins_result_visual_window.getSelectionModeFromViewport()
            if self.__contour_selection_mode is None:
                pass
            else:
                self.__contour_selected_labels_dict = ins_result_visual_window.getSelectionFromViewport()
            
            ins_visualization_toolbar = ins_main_window.findChild(QtCore.QObject,'visualization-toolbar')
            ins_visualization_toolbar.clearToolsState()
                  
        if ins_graph_list.isEnabled():
            ins_variables_box.setEnabled(True)
            ins_variable_components_box.setEnabled(True)
            ins_steps_box.setEnabled(True)
            ins_step_frames_box.setEnabled(True)
            ins_left_move_frame_button.setEnabled(True)
            ins_right_move_frame_button.setEnabled(True)
            ins_right_move_frame_button.setEnabled(True)
            ins_deformation_type_box.setEnabled(True)
            ins_deform_factor_edit.setEnabled(True)
            ins_apply_deform_fator.setEnabled(True)
            ins_color_map_box.setEnabled(True)
            ins_color_number_box.setEnabled(True)
            ins_export_to_csv_button.setEnabled(True)
            ins_export_to_image_button.setEnabled(True)
            
            ins_graph_list.setEnabled(False)
            
            ins_result_visual_window.switchDisplayTypeOfViewport('contour')
        else:
            ins_variables_box.setEnabled(False)
            ins_variable_components_box.setEnabled(False)
            ins_steps_box.setEnabled(False)
            ins_step_frames_box.setEnabled(False)
            ins_left_move_frame_button.setEnabled(False)
            ins_right_move_frame_button.setEnabled(False)
            ins_right_move_frame_button.setEnabled(False)
            ins_deformation_type_box.setEnabled(False)
            ins_deform_factor_edit.setEnabled(False)
            ins_apply_deform_fator.setEnabled(False)
            ins_color_map_box.setEnabled(False)
            ins_color_number_box.setEnabled(False)
            ins_export_to_csv_button.setEnabled(False)
            ins_export_to_image_button.setEnabled(False)
            
            ins_graph_list.setEnabled(True)
            
            ins_result_visual_window.switchDisplayTypeOfViewport('graph')

class _CreateGraphDialog(QtWidgets.QDialog):
    def __init__(self, input_parent:object, in_ins_database_pointer:object, in_exist_graphs_name:list, in_selection_mode:str, in_selected_labels:dict) -> None:
        super().__init__(input_parent)

        self.__ins_database_pointer = in_ins_database_pointer
        self.__exist_graphs_name_list = in_exist_graphs_name
        self.__selection_mode = in_selection_mode
        self.__selected_labels_dict = in_selected_labels
        
        self.setWindowTitle('Create Graph')
        self.setWindowModality(QtCore.Qt.WindowModal)
        
        ins_dialog_layout = QtWidgets.QVBoxLayout()
        self.setLayout(ins_dialog_layout)
        
        self.__initializeSelectionLayout(ins_dialog_layout)
        self.__initializeUserButton(ins_dialog_layout)

    def __initializeSelectionLayout(self, in_ins_dialog_layout:object) -> None:
        ins_name_seleciton_layout =  QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_name_seleciton_layout,0)
        # region
        ins_graph_name_label = QtWidgets.QLabel('Graph Name',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignRight)
        ins_graph_name_label.setFixedSize(90,30)
        ins_name_seleciton_layout.addWidget(ins_graph_name_label,0)
        
        ins_name_line_edit =  QtWidgets.QLineEdit(self)
        ins_name_line_edit.setObjectName('graph-name-edit')
        ins_name_line_edit.setMinimumWidth(150)
        ins_name_line_edit.setFixedHeight(30)
        ins_name_line_edit.setMaxLength(20)
        ins_name_line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.NAME_FORMAT)))
        ins_name_line_edit_completer = QtWidgets.QCompleter(['Graph_','graph-'])
        ins_name_line_edit.setCompleter(ins_name_line_edit_completer)
        ins_name_line_edit.textChanged.connect(self.__slotCheckGraphName)
        ins_name_seleciton_layout.addWidget(ins_name_line_edit,1)
        # endregion

        ins_position_seleciton_layout =  QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_position_seleciton_layout,0)
        # region
        ins_position_label = QtWidgets.QLabel('Position:',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignLeft)
        ins_position_label.setFixedSize(65,30)
        ins_position_seleciton_layout.addWidget(ins_position_label,0)
        
        ins_output_position_box = QtWidgets.QComboBox(self)
        ins_output_position_box.setObjectName('output-position-box')
        ins_output_position_box.setFixedSize(100,30)
        ins_output_position_box.addItems(['Node','Element'])
        ins_output_position_box.currentTextChanged.connect(self.__slotChangeOutputPosition)
        ins_position_seleciton_layout.addWidget(ins_output_position_box,0)
        
        ins_position_seleciton_layout.addStretch()
        # endregion
        
        ins_output_data_stacked_Layout = QtWidgets.QStackedLayout()
        ins_output_data_stacked_Layout.setObjectName('output-data-stacked-layout')
        ins_output_data_stacked_Layout.setContentsMargins(0,0,0,0)
        in_ins_dialog_layout.addLayout(ins_output_data_stacked_Layout,1)
        # region
        model_dimension = str(self.__ins_database_pointer['basic'][0],'utf-8')
        
        ins_node_data_tree = QtWidgets.QTreeWidget(self)
        ins_node_data_tree.setHeaderHidden(True)
        ins_output_data_stacked_Layout.addWidget(ins_node_data_tree)
        for variable_name in self.__ins_database_pointer['Nodes'].keys():
            ins_variable_item = QtWidgets.QTreeWidgetItem()
            ins_variable_item.setText(0,variable_name)
            ins_variable_item.setFlags(ins_variable_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            ins_variable_item.setCheckState(0, QtCore.Qt.Unchecked)

            for component_name in common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][variable_name]:
                ins_component_item = QtWidgets.QTreeWidgetItem()
                ins_component_item.setText(0,component_name)
                ins_component_item.setFlags(ins_component_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                ins_component_item.setCheckState(0, QtCore.Qt.Unchecked)

                ins_variable_item.addChild(ins_component_item)
            
            ins_node_data_tree.addTopLevelItem(ins_variable_item)
        ins_node_data_tree.itemClicked.connect(self.__slotSelectedDataItem)
        
        ins_element_data_tree = QtWidgets.QTreeWidget(self)
        ins_element_data_tree.setHeaderHidden(True)
        ins_output_data_stacked_Layout.addWidget(ins_element_data_tree)
        for variable_name in self.__ins_database_pointer['Elements'].keys():
            ins_variable_item = QtWidgets.QTreeWidgetItem()
            ins_variable_item.setText(0,variable_name)
            ins_variable_item.setFlags(ins_variable_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            ins_variable_item.setCheckState(0, QtCore.Qt.Unchecked)

            for component_name in common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][variable_name]:
                ins_component_item = QtWidgets.QTreeWidgetItem()
                ins_component_item.setText(0,component_name)
                ins_component_item.setFlags(ins_component_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                ins_component_item.setCheckState(0, QtCore.Qt.Unchecked)

                ins_variable_item.addChild(ins_component_item)
            
            ins_element_data_tree.addTopLevelItem(ins_variable_item)
        ins_element_data_tree.itemClicked.connect(self.__slotSelectedDataItem)
        # endregion
        
        ins_output_object_label_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_output_object_label_layout,0)
        ins_output_object_label = QtWidgets.QLabel('Object:',self,alignment=QtCore.Qt.AlignVCenter| QtCore.Qt.AlignLeft)
        ins_output_object_label.setFixedSize(60,25)
        ins_output_object_label_layout.addWidget(ins_output_object_label,0)
        ins_output_object_label_layout.addStretch()
        
        ins_output_object_from_group_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_output_object_from_group_layout,0)
        ins_output_object_from_group_layout.addSpacing(20)
        ins_output_object_from_group_radio = QtWidgets.QRadioButton('Group:',self)
        ins_output_object_from_group_radio.setFixedSize(68,25)
        ins_output_object_from_group_radio.setChecked(True)
        ins_output_object_from_group_layout.addWidget(ins_output_object_from_group_radio,0)
        ins_groups_box = QtWidgets.QComboBox(self)
        ins_groups_box.setObjectName('groups-box')
        ins_groups_box.addItems(list(self.__ins_database_pointer['Mesh']['Groups']['Nodes'].keys()))
        ins_output_object_from_group_layout.addWidget(ins_groups_box,1)
        
        ins_output_object_from_label_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_output_object_from_label_layout,0)
        ins_output_object_from_label_layout.addSpacing(20)
        ins_output_object_from_label_radio = QtWidgets.QRadioButton('Label:',self)
        ins_output_object_from_label_radio.setFixedSize(68,25)
        ins_output_object_from_label_layout.addWidget(ins_output_object_from_label_radio,0)
        ins_instances_box = QtWidgets.QComboBox(self)
        ins_instances_box.setObjectName('instances-box')
        ins_instances_box.addItems(list(self.__ins_database_pointer['Mesh']['Instances'].keys()))
        ins_output_object_from_label_layout.addWidget(ins_instances_box,1)
        ins_instance_label_edit = QtWidgets.QLineEdit(self)
        ins_instance_label_edit.setObjectName('object-label-edit')
        ins_instance_label_edit.setMaxLength(12)
        ins_instance_label_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(common.P4SFormat.POSTTIVE_INTEGER_FORMAT)))
        ins_output_object_from_label_layout.addWidget(ins_instance_label_edit,1)
        
        ins_output_object_from_view_layout = QtWidgets.QHBoxLayout()
        in_ins_dialog_layout.addLayout(ins_output_object_from_view_layout,0)
        ins_output_object_from_view_layout.addSpacing(20)
        ins_output_object_from_view_radio = QtWidgets.QRadioButton('View:',self)
        ins_output_object_from_view_radio.setObjectName('from-view-raido')
        ins_output_object_from_view_radio.setFixedSize(68,25)
        if self.__selection_mode == 'node' and len(self.__selected_labels_dict)>0:
            pass
        else:
            ins_output_object_from_view_radio.setEnabled(False)
        ins_output_object_from_view_layout.addWidget(ins_output_object_from_view_radio,0)
        ins_output_object_from_view_layout.addStretch()
        
        ins_output_object_group = QtWidgets.QButtonGroup(self)
        ins_output_object_group.setObjectName('object-type-buttons')
        ins_output_object_group.addButton(ins_output_object_from_group_radio,0)
        ins_output_object_group.addButton(ins_output_object_from_label_radio,1)
        ins_output_object_group.addButton(ins_output_object_from_view_radio,2)
    # region
    def __slotCheckGraphName(self, in_graph_name:str) -> None:
        ins_accept_button = self.findChild(QtWidgets.QPushButton,'accept-button')
        
        if in_graph_name == '':
            ins_accept_button.setEnabled(False)
        elif in_graph_name in self.__exist_graphs_name_list:
            ins_accept_button.setEnabled(False)
        else:
            ins_accept_button.setEnabled(True)
    
    def __slotChangeOutputPosition(self, in_position_type:str) -> None:
        ins_output_data_stacked_Layout = self.findChild(QtWidgets.QStackedLayout,'output-data-stacked-layout')
        
        ins_groups_box = self.findChild(QtWidgets.QComboBox,'groups-box')
        ins_groups_box.clear()
        
        ins_output_object_from_view_radio = self.findChild(QtWidgets.QRadioButton,'from-view-raido')
        
        if in_position_type == 'Node':
            ins_output_data_stacked_Layout.setCurrentIndex(0)
            
            ins_groups_box.addItems(list(self.__ins_database_pointer['Mesh']['Groups']['Nodes'].keys()))
            
            if self.__selection_mode == 'node' and len(self.__selected_labels_dict)>0:
                ins_output_object_from_view_radio.setEnabled(True)
            else:
                ins_output_object_from_view_radio.setEnabled(False)
        else:
            ins_output_data_stacked_Layout.setCurrentIndex(1)
            
            ins_groups_box.addItems(list(self.__ins_database_pointer['Mesh']['Groups']['Elements'].keys()))
            
            if self.__selection_mode == 'element' and len(self.__selected_labels_dict)>0:
                ins_output_object_from_view_radio.setEnabled(True)
            else:
                ins_output_object_from_view_radio.setEnabled(False)
    
    def __slotSelectedDataItem(self,in_ins_clicked_item:object) -> None:
        ins_output_data_stacked_Layout = self.findChild(QtWidgets.QStackedLayout,'output-data-stacked-layout')
        ins_data_tree = ins_output_data_stacked_Layout.currentWidget()

        ins_data_tree.itemClicked.disconnect(self.__slotSelectedDataItem)
        
        ins_clicked_item_parent = in_ins_clicked_item.parent()
        if ins_clicked_item_parent is None:
            if in_ins_clicked_item.checkState(0) == QtCore.Qt.Checked:
                for component_itme_index in range(in_ins_clicked_item.childCount()):
                    in_ins_clicked_item.child(component_itme_index).setCheckState(0,QtCore.Qt.Checked)
            else:
                for component_itme_index in range(in_ins_clicked_item.childCount()):
                    in_ins_clicked_item.child(component_itme_index).setCheckState(0,QtCore.Qt.Unchecked)
        
            for variable_itme_index in range(ins_data_tree.topLevelItemCount()):
                ins_variable_item = ins_data_tree.topLevelItem(variable_itme_index)
                if ins_variable_item is in_ins_clicked_item:
                    continue
                else:
                    if ins_variable_item.checkState(0) == QtCore.Qt.Checked:
                        ins_variable_item.setCheckState(0,QtCore.Qt.Unchecked)
                        for component_item_index in range(ins_variable_item.childCount()):
                            ins_variable_item.child(component_item_index).setCheckState(0,QtCore.Qt.Unchecked)
                    else:
                        continue
        else:
            has_clicked_item = False
            for component_item_index in range(ins_clicked_item_parent.childCount()):
                if ins_clicked_item_parent.child(component_item_index).checkState(0) == QtCore.Qt.Checked:
                    has_clicked_item = True
                    break
                else:
                    pass
            
            if has_clicked_item:
                ins_clicked_item_parent.setCheckState(0,QtCore.Qt.Checked)
            else:
                ins_clicked_item_parent.setCheckState(0,QtCore.Qt.Unchecked)
    
            for variable_item_index in range(ins_data_tree.topLevelItemCount()):
                ins_variable_item = ins_data_tree.topLevelItem(variable_item_index)
                if ins_variable_item is ins_clicked_item_parent:
                    continue
                else:
                    if ins_variable_item.checkState(0) == QtCore.Qt.Checked:
                        ins_variable_item.setCheckState(0,QtCore.Qt.Unchecked)
                        for component_item_index in range(ins_variable_item.childCount()):
                            ins_variable_item.child(component_item_index).setCheckState(0,QtCore.Qt.Unchecked)
                    else:
                        continue
        
        ins_data_tree.itemClicked.connect(self.__slotSelectedDataItem)
    # endregion

    def __initializeUserButton(self,in_ins_dialog_layout:object) -> None:
        ins_button_layout = QtWidgets.QHBoxLayout()
        ins_button_layout.addStretch()
        
        ins_accept_button = QtWidgets.QPushButton("Accept")
        ins_accept_button.setObjectName('accept-button')
        ins_accept_button.setFixedHeight(30)
        ins_accept_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_accept_button.setEnabled(False)
        ins_button_layout.addWidget(ins_accept_button)
        ins_accept_button.clicked.connect(self.accept)
        
        ins_button_layout.addStretch()
        
        ins_cancel_button = QtWidgets.QPushButton("Cancel")
        ins_cancel_button.setFixedHeight(30)
        ins_cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        ins_button_layout.addWidget(ins_cancel_button)
        ins_cancel_button.clicked.connect(self.close)
        
        ins_button_layout.addStretch()
        
        in_ins_dialog_layout.addLayout(ins_button_layout)

    def getGraphInformation(self) -> dict:
        graph_infomation_dict = {'name':None,'position':None,'data':[],'object':[]}

        graph_infomation_dict['name'] = self.findChild(QtWidgets.QLineEdit,'graph-name-edit').text()
        
        graph_infomation_dict['position'] = self.findChild(QtWidgets.QComboBox,'output-position-box').currentText()

        ins_output_data_stacked_Layout = self.findChild(QtWidgets.QStackedLayout,'output-data-stacked-layout')
        ins_data_tree = ins_output_data_stacked_Layout.currentWidget()
        for variable_item_index in range(ins_data_tree.topLevelItemCount()):
            ins_variable_item = ins_data_tree.topLevelItem(variable_item_index)
            
            selected_components_list = []
            for component_item_index in range(ins_variable_item.childCount()):
                ins_component_item = ins_variable_item.child(component_item_index)
                if ins_component_item.checkState(0) == QtCore.Qt.Checked:
                    selected_components_list.append(ins_component_item.text(0))
                else:
                    continue
            
            if selected_components_list == []:
                continue
            else:
                graph_infomation_dict['data'].append(ins_variable_item.text(0))
                graph_infomation_dict['data'].append(selected_components_list)
                break

        ins_output_object_group = self.findChild(QtWidgets.QButtonGroup,'object-type-buttons')
        if ins_output_object_group.checkedId() == 0:
            graph_infomation_dict['object'].append('group')
            graph_infomation_dict['object'].append(self.findChild(QtWidgets.QComboBox,'groups-box').currentText())
        elif ins_output_object_group.checkedId() == 1:
            graph_infomation_dict['object'].append('label')

            graph_infomation_dict['object'].append(self.findChild(QtWidgets.QComboBox,'instances-box').currentText())
            graph_infomation_dict['object'].append(self.findChild(QtWidgets.QLineEdit,'object-label-edit').text())
        elif ins_output_object_group.checkedId() == 2:
            graph_infomation_dict['object'].append('view')
        else:   pass
        
        return graph_infomation_dict
