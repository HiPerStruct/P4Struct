# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import os

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
from vtkmodules.qt import QVTKRenderWindowInteractor
import vtk
from vtkmodules.util import numpy_support
from matplotlib import colors
from matplotlib import colormaps
import numpy

from config import common


class P4SModelVisualWindow(QtWidgets.QMdiSubWindow):
    def __init__(self,in_parent:object,in_model_name:str) -> None:
        super().__init__(parent=in_parent)
        self.setObjectName(in_model_name)

        self.setWindowTitle(f'Display Window From Model: {in_model_name}')
        self.setWindowIcon(QtGui.QPixmap(":/image/images/ManageViewport.png"))
        self.resize(500,500)
        self.showMaximized()
        self.actions()[-1].setShortcut("")
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.setSystemMenu(None)
        
        ins_model_vtk_interactor = _ModelVisualizationInteractor(self)
        self.setWidget(ins_model_vtk_interactor)
        ins_model_vtk_interactor.Start()
        
        self.__current_part_name = None

    def close(self,in_enable_hide:bool=True):
        if in_enable_hide:
            self.hide()
        else:
            return super().close()

    def finalizeInteractor(self) -> None:
        self.widget().Finalize()

    def renameModel(self, in_new_model_name:str) -> None:
        self.setObjectName(in_new_model_name)
        self.setWindowTitle(f'Display Window From Model: {in_new_model_name}')

    def getSelectionFromViewport(self) -> dict:
        return self.widget().getInteractorSelection()
    def setSelectionMode(self, in_mode:str) -> None:
        self.widget().setInteractorSelectionMode(in_mode)
    def setSelectionMethod(self, in_method:str) -> None:
        self.widget().setInteractorSelectionMethod(in_method)
    
    def setViewportView(self, in_view_orientation:str) -> None:
        self.widget().setInteractorViewOrientation(in_view_orientation)
    
    def setViewportRenderStyle(self, in_style:str) -> None:
        self.widget().setInteractorRenderStyle(in_style)
    
    def getViewportActorsColor(self) -> dict:
        return self.widget().getRendererIncludeActorsColor()
    def setViewportActorsColor(self,in_actors_color_dict:dict) -> None:
        self.widget().setInteractorRendererIncludeAcotrsColor(in_actors_color_dict)
    
    def getViewportActorsOpacity(self) -> dict:
        return self.widget().getRendererIncludeActorsOpacity()
    def setViewportActorsOpacity(self,in_actors_opacity_dict:dict) -> None:
        self.widget().setInteractorRendererIncludeAcotrsOpacity(in_actors_opacity_dict)
    
    def getViewportActorsVisibility(self) -> dict:
        return self.widget().getRendererIncludeActorsVisibility()
    def setViewportActorsVisibiolity(self,in_actors_visbility_dict:dict) -> dict:
        return self.widget().setRendererIncludeActorsVisibility(in_actors_visbility_dict)
    
    def switchModuleViewport(self,in_module_type:str) -> None:
        if in_module_type == 'Part':
            self.widget().switchModuleRenderer(in_module_type,self.__current_part_name)
        else:
            self.widget().switchModuleRenderer(in_module_type)
    
    def getCoordinateSystemsOfCurrentViewport(self) -> list:
        return self.widget().getCoordinateSystemsOfCurrentRenderer()
    def addCoordinateSystemToCurrentViewport(self, in_coordinate_system_name:str, in_coordinate_system_ifno:dict) -> None:
        self.widget().addCoordinateSystemToCurrentRenderer(in_coordinate_system_name, in_coordinate_system_ifno)
    def deleteCoordinateSystemToCurrentViewport(self, in_coordinate_system_name:str) -> None:
        self.widget().deleteCoordinateSystemOfCurrentRenderer(in_coordinate_system_name)
    def renameShownCoordinateSystemOfCurrentViewport(self, in_old_coordinate_system_name:str, in_new_coordinate_system_name:str) -> None:
        self.widget().renameCoordinateSystemOfCurrentRenderer(in_old_coordinate_system_name,in_new_coordinate_system_name)
    def editCoordinateSystemOfCurrentViewport(self, in_coordinate_system_name:str, in_type:str, in_reference_axis:str, in_value:float) -> None:
        self.widget().editCoordinateSystemOfCurrentRenderer(in_coordinate_system_name,in_type,in_reference_axis,in_value)

    def getCurrentPartName(self) -> str:
        return self.__current_part_name
    def switchPartViewport(self, in_part_name:str) -> None:
        self.widget().switchPartRenderer(in_part_name)
        self.__current_part_name = in_part_name
    def createPartViewport(self, in_ins_project_database:object, in_part_name:str) -> None:
        self.widget().createPartRenderer(in_ins_project_database, self.objectName(), in_part_name)
        self.__current_part_name = in_part_name
    def renamePartViewport(self, in_old_part_name:str, in_new_part_name:str) -> None:
        self.widget().renamePartRenderer(in_old_part_name, in_new_part_name)
        
        if self.__current_part_name == in_old_part_name:
            self.__current_part_name = in_new_part_name
        else:
            pass
    def removePartViewport(self, in_part_name:str) -> None:
        self.widget().removePartRenderer(in_part_name)
        
        if self.__current_part_name == in_part_name:
            self.__current_part_name = None
        else:
            pass
    def switchPartViewportAxesVisibility(self, in_part_name:str) -> None:
        self.widget().switchPartRendererAxesVisibility(in_part_name)
    def showPartViewportGroup(self, in_ins_project_database:object, in_part_name:str, in_group_type:str, in_group_name:str) -> None:
        self.widget().showGroupOfPartRenderer(in_ins_project_database,self.objectName(), in_part_name, in_group_type,in_group_name)
    def switchPartViewportElementsOrientationVisibility(self, in_ins_project_database:object, in_part_name:str, in_group_name:str) -> None:
        self.widget().switchPartRendererElementsOrientationVisibility(in_ins_project_database,self.objectName(),in_part_name,in_group_name)
    
    def switchAssemblyViewportAxesVisibility(self) -> None:
        self.widget().switchAssemblyRendererAxesVisibility()
    def addInstanceToViewport(self, in_part_name:str, in_instance_name:str, in_instance_orientation:list=[]) -> None:
        self.widget().addInstanceToAssemblyRenderer(in_part_name,in_instance_name,in_instance_orientation)
    def editInstanceOrientationOfAssemblyViewport(self, in_instance_name:str, in_type:str, in_assembly_coordinate_system:str, in_direction:str, in_value:float) -> None:
        self.widget().editInstanceOrientationOfAssemblyRenderer(in_instance_name, in_type, in_assembly_coordinate_system, in_direction, in_value)
    def renameInstanceViewport(self, in_old_instance_name:str, in_new_instance_name:str) -> None:
        self.widget().renameInstanceOfAssemblyRenderer(in_old_instance_name,in_new_instance_name)
    def removeInstanceOfAssemblyViewport(self, in_instance_name:str) -> None:
        self.widget().removeInstanceOfAssemblyRenderer(in_instance_name)
    def showAssemblyViewportGroup(self, in_ins_project_database:object, in_group_type:str, in_assembly_group_name:str) -> None:
        self.widget().showGroupOfAssemblyRenderer(in_ins_project_database,self.objectName(),in_group_type,in_assembly_group_name)

    def getShownBoundaryConditionsOfAssemblyViewport(self) -> list:
        return self.widget().getShownBoundaryConditionsOfAssemblyRenderer()
    def addBoundaryConditionToAssemblyViewport(self, in_ins_project_database:object, in_boundary_condition_name:str) -> None:
        self.widget().addBoundaryConditionToAssemblyRenderer(in_ins_project_database, self.objectName(), in_boundary_condition_name)
    def removeBoundaryConditionToAssemblyViewport(self, in_boundary_condition_name:str) -> None:
        self.widget().removeBoundaryConditionToAssemblyRenderer(in_boundary_condition_name)

class _ModelVisualizationInteractor(QVTKRenderWindowInteractor.QVTKRenderWindowInteractor):
    def __init__(self, in_parent):
        super().__init__(parent=in_parent)

        self.__selection_mode = None
        self.__selection_method = 'single'
        self.__point_picker = vtk.vtkPointPicker()
        self.__point_picker.SetTolerance(0.005)
        self.__cell_picker = vtk.vtkCellPicker()
        self.__cell_picker.SetTolerance(0.005)
        self.__area_picker = vtk.vtkAreaPicker()
        self.__prop_picker = self.GetPicker()
        self.__picked_labels_dict = {}

        ins_default_interactor_style = self.GetInteractorStyle()
        self.SetInteractorStyle(vtk.vtkInteractorStyleRubberBandPick())
        del ins_default_interactor_style
        self.__is_rubber_selection = False
        
        self.__ins_attached_renderer = self.__initializeAxesLayer()
        self.__ins_assembly_renderer = self.__initializeAssemblyRenderer()
        self.__parts_renderer_dict = {}
        self.__ins_current_renderer = self.__ins_assembly_renderer
        
        self.__axes_visibility_dict = {'parts':{},'assembly':True}

    def __initializeAxesLayer(self) -> object:
        ins_axes_renderer = vtk.vtkRenderer()
        ins_axes_renderer.SetLayer(1)
        ins_axes_actor = vtk.vtkAxesActor()
        ins_axes_actor.SetObjectName('GCSYS')
        ins_axes_actor.SetConeRadius(0)
        ins_axes_x_text_actor = ins_axes_actor.GetXAxisCaptionActor2D().GetTextActor()
        ins_axes_x_text_actor.SetTextScaleModeToNone()
        ins_axes_x_text_actor.GetTextProperty().SetFontSize(50)
        ins_axes_y_text_actor = ins_axes_actor.GetYAxisCaptionActor2D().GetTextActor()
        ins_axes_y_text_actor.SetTextScaleModeToNone()
        ins_axes_y_text_actor.GetTextProperty().SetFontSize(50)
        ins_axes_z_text_actor = ins_axes_actor.GetZAxisCaptionActor2D().GetTextActor()
        ins_axes_z_text_actor.SetTextScaleModeToNone()
        ins_axes_z_text_actor.GetTextProperty().SetFontSize(50)
        ins_axes_renderer.AddActor(ins_axes_actor)
        ins_axes_renderer.GetActiveCamera().ParallelProjectionOn()
        ins_axes_renderer.ResetCamera()
        
        ins_render_window = self.GetRenderWindow()
        ins_render_window.SetNumberOfLayers(2)
        ins_render_window.AddRenderer(ins_axes_renderer)
        
        return ins_axes_renderer
    def __initializeAssemblyRenderer(self) -> object:
        ins_assembly_renderer = vtk.vtkRenderer()
        ins_assembly_renderer.SetLayer(0)
        ins_assembly_renderer.SetBackground(178/255,187/255,190/255)
        ins_assembly_renderer.SetBackground2(138/255,152/255,142/255)
        ins_assembly_renderer.SetGradientBackground(1)
        ins_assembly_renderer.GetActiveCamera().ParallelProjectionOn()
        ins_assembly_renderer.ResetCamera()
        
        ins_module_tip = vtk.vtkCornerAnnotation()
        ins_module_tip.SetText(1,'Assembly')
        ins_module_tip.SetLinearFontScaleFactor(6)
        ins_module_tip.GetTextProperty().SetColor(1, 1, 0)
        ins_assembly_renderer.AddViewProp(ins_module_tip)

        ins_render_window = self.GetRenderWindow()
        ins_render_window.AddRenderer(ins_assembly_renderer)
        self.__ins_attached_renderer.SetActiveCamera(ins_assembly_renderer.GetActiveCamera())
        ins_render_window.Render()

        return ins_assembly_renderer
    
    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.MiddleButton:
            if self.GetControlKey() == 1:
                self.GetInteractorStyle().StartPan()
            else:
                self.GetInteractorStyle().StartRotate()

            return None
        elif ev.button() == QtCore.Qt.RightButton:
            if self.GetControlKey() == 1:
                self.GetInteractorStyle().StartSpin()
            else:
                self.GetInteractorStyle().StartDolly()
            
            return None
        elif ev.button() == QtCore.Qt.LeftButton:
            if self.__selection_mode is None:
                return None
            elif self.__selection_method == 'area' and self.__is_rubber_selection:
                super().mousePressEvent(ev)
                return None
            else:
                pass
        else:
            return None
        
        ins_current_picker = self.GetPicker()
        ins_current_picker.Pick(self.GetEventPosition()[0],self.GetEventPosition()[1],0.0,self.__ins_current_renderer)
        ins_picked_actor = ins_current_picker.GetActor()
    
        if self.GetControlKey() == 1 and self.GetShiftKey() == 0:
            if ins_picked_actor is None:
                return None
            else:
                pass
            
            picked_actor_object_name = ins_picked_actor.GetObjectName()
            picked_actor_name = picked_actor_object_name.split('>',1)[1]
            highlight_actor_object_name = 'highlight>'+ picked_actor_name
            
            ins_highlight_actor = None
            for ins_acotr in  self.__ins_attached_renderer.GetActors():
                if ins_acotr.GetObjectName() == highlight_actor_object_name:
                    ins_highlight_actor = ins_acotr
                    break
                else:
                    continue
            
            if self.__selection_method == 'single':
                if self.__selection_mode == 'node':
                    picked_point_id = ins_current_picker.GetPointId()
                    
                    if ins_highlight_actor is None:
                        self.__picked_labels_dict[picked_actor_name] = [picked_point_id+1]
                        
                        ins_highlight_actor_points = vtk.vtkPoints()
                        picked_point_coordinates = ins_picked_actor.GetMapper().GetInput().GetPoint(picked_point_id)
                        ins_highlight_actor_points.InsertNextPoint(picked_point_coordinates)
                        ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                        ins_highlight_actor_grid.SetPoints(ins_highlight_actor_points)
                        ins_highlight_actor_grid.InsertNextCell(1,1,[0])
                        ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                        ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                        ins_highlight_actor = vtk.vtkActor()
                        ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                        ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                        ins_highlight_actor.GetProperty().SetColor(1,0,0)
                        ins_highlight_actor.GetProperty().SetPointSize(10)
                        ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
                        self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                    else:
                        if picked_point_id+1 in self.__picked_labels_dict[picked_actor_name]:
                            return None
                        else:
                            self.__picked_labels_dict[picked_actor_name].append(picked_point_id+1)

                        ins_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                        
                        ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                        picked_point_coordinates = ins_picked_actor.GetMapper().GetInput().GetPoint(picked_point_id)
                        point_id = ins_highlight_actor_points.InsertNextPoint(picked_point_coordinates)
                        ins_highlight_actor_grid.InsertNextCell(1,1,[point_id])
                        
                        ins_highlight_actor_grid.Modified()
                elif self.__selection_mode == 'element':
                    picked_cell_id = ins_current_picker.GetCellId()
                    
                    if ins_highlight_actor is None:
                        self.__picked_labels_dict[picked_actor_name] = [picked_cell_id+1]
                        
                        ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                    
                        ins_extract_cells = vtk.vtkExtractCells()
                        ins_extract_cells.SetInputData(ins_picked_actor_grid)
                        ins_extract_cells.AddCellIds([picked_cell_id],1)
                        ins_extract_cells.Update()
                        
                        ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
                        ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
                        ins_extract_cells.SetInputData(None)
                        del ins_extract_cells
                    
                        ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                        ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                        ins_highlight_actor = vtk.vtkActor()
                        ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                        ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                        ins_highlight_actor.GetProperty().SetColor(1,0,0)
                        ins_highlight_actor.GetProperty().SetLineWidth(3)
                        ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
                        self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                    else:
                        if picked_cell_id+1 in self.__picked_labels_dict[picked_actor_name]:
                            return None
                        else:
                            self.__picked_labels_dict[picked_actor_name].append(picked_cell_id+1)

                        ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()

                        ins_extract_cells = vtk.vtkExtractCells()
                        ins_extract_cells.SetInputData(ins_picked_actor_grid)
                        ins_extract_cells.AddCellIds([cell_label-1 for cell_label in self.__picked_labels_dict[picked_actor_name]],len(self.__picked_labels_dict[picked_actor_name]))
                        ins_extract_cells.Update()
                        
                        ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
                        ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
                        ins_extract_cells.SetInputData(None)
                        del ins_extract_cells
                        
                        ins_old_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                        ins_highlight_actor.GetMapper().SetInputData(ins_highlight_actor_grid)
                        
                        ins_old_highlight_actor_points = ins_old_highlight_actor_grid.GetPoints()
                        ins_old_highlight_actor_grid.SetPoints(None)
                        ins_old_highlight_actor_grid.Initialize()
                        del ins_old_highlight_actor_grid
                        ins_old_highlight_actor_points.Initialize()
                        del ins_old_highlight_actor_points
                else:
                    pass
            elif self.__selection_method == 'edge':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'face':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'entity':
                ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                
                if ins_highlight_actor is None:
                    if self.__selection_mode == 'node':
                        self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfPoints()+1,1))
                    elif self.__selection_mode == 'element':
                        self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfCells()+1,1))
                    else:
                        pass
                    
                    ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.DeepCopy(ins_picked_actor_grid)
                    ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                    ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                    ins_highlight_actor = vtk.vtkActor()
                    ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                    ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                    ins_highlight_actor.GetProperty().SetColor(1,0,0)
                    if self.__selection_mode == 'node':
                        ins_highlight_actor.GetProperty().SetPointSize(10)
                        ins_highlight_actor.GetProperty().SetRepresentationToPoints()
                        ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
                    elif self.__selection_mode == 'element':
                        ins_highlight_actor.GetProperty().SetLineWidth(3)
                        ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
                    self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                elif ins_picked_actor_grid.GetNumberOfCells() > len(self.__picked_labels_dict[picked_actor_name]):
                    if self.__selection_mode == 'node':
                        self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfPoints()+1,1))
                    elif self.__selection_mode == 'element':
                        self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfCells()+1,1))
                    else:
                        pass
                    
                    ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.DeepCopy(ins_picked_actor_grid)
                    
                    ins_old_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                    ins_highlight_actor.GetMapper().SetInputData(ins_highlight_actor_grid)
                    
                    ins_old_highlight_actor_points = ins_old_highlight_actor_grid.GetPoints()
                    ins_old_highlight_actor_grid.SetPoints(None)
                    ins_old_highlight_actor_grid.Initialize()
                    del ins_old_highlight_actor_grid
                    ins_old_highlight_actor_points.Initialize()
                    del ins_old_highlight_actor_points
                else:
                    pass
            else:
                return None
            
            self.GetRenderWindow().Render()
        elif self.GetControlKey() == 0 and self.GetShiftKey() == 1:
            if ins_picked_actor is None:
                return None
            else:
                pass
            
            picked_actor_object_name = ins_picked_actor.GetObjectName()
            picked_actor_name = picked_actor_object_name.split('>',1)[1]
            highlight_actor_object_name = 'highlight>'+ picked_actor_name
            
            if picked_actor_name in self.__picked_labels_dict:
                pass
            else:
                return None
            
            if self.__selection_method == 'single':
                if self.__selection_mode == 'node':
                    picked_point_id = ins_current_picker.GetPointId()
                    
                    if picked_point_id+1 in self.__picked_labels_dict[picked_actor_name]:
                        self.__picked_labels_dict[picked_actor_name].remove(picked_point_id+1)
                        
                        for ins_acotr in  self.__ins_attached_renderer.GetActors():
                            if ins_acotr.GetObjectName() == highlight_actor_object_name:
                                ins_highlight_actor = ins_acotr
                                break
                            else:
                                continue
            
                        if self.__picked_labels_dict[picked_actor_name] == []:
                            self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
                
                            ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
                            ins_highlight_actor.SetMapper(None)
                            del ins_highlight_actor
                            
                            ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
                            ins_highlight_actor_mapper.SetInputData(None)
                            ins_highlight_actor_mapper.RemoveAllInputs()
                            del ins_highlight_actor_mapper
                    
                            ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                            ins_highlight_actor_grid.SetPoints(None)
                            ins_highlight_actor_grid.Initialize()
                            del ins_highlight_actor_grid
                            
                            ins_highlight_actor_points.Initialize()
                            del ins_highlight_actor_points
                            
                            self.__picked_labels_dict[picked_actor_name] = None
                            del self.__picked_labels_dict[picked_actor_name]
                        else:
                            ins_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                            ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                            ins_highlight_actor_grid.Reset()
                            ins_highlight_actor_points.Reset()
                            
                            ins_picked_actor_points = ins_picked_actor.GetMapper().GetInput().GetPoints()
                            for node_lable in self.__picked_labels_dict[picked_actor_name]:
                                point_id = ins_highlight_actor_points.InsertNextPoint(ins_picked_actor_points.GetPoint(node_lable-1))
                                ins_highlight_actor_grid.InsertNextCell(1,1,[point_id])
                            
                            ins_highlight_actor_grid.Modified()
                    else:
                        return None
                elif self.__selection_mode == 'element':
                    picked_cell_id = ins_current_picker.GetCellId()
                    
                    if picked_cell_id+1 in self.__picked_labels_dict[picked_actor_name]:
                        self.__picked_labels_dict[picked_actor_name].remove(picked_cell_id+1)
                        
                        for ins_acotr in  self.__ins_attached_renderer.GetActors():
                            if ins_acotr.GetObjectName() == highlight_actor_object_name:
                                ins_highlight_actor = ins_acotr
                                break
                            else:
                                continue
                        
                        if self.__picked_labels_dict[picked_actor_name] == []:
                            self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
                            
                            ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
                            ins_highlight_actor.SetMapper(None)
                            del ins_highlight_actor
                            
                            ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
                            ins_highlight_actor_mapper.SetInputData(None)
                            ins_highlight_actor_mapper.RemoveAllInputs()
                            del ins_highlight_actor_mapper
                    
                            ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                            ins_highlight_actor_grid.SetPoints(None)
                            ins_highlight_actor_grid.Initialize()
                            del ins_highlight_actor_grid
                            
                            ins_highlight_actor_points.Initialize()
                            del ins_highlight_actor_points
                            
                            self.__picked_labels_dict[picked_actor_name] = None
                            del self.__picked_labels_dict[picked_actor_name]
                        else:
                            ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                            
                            ins_extract_cells = vtk.vtkExtractCells()
                            ins_extract_cells.SetInputData(ins_picked_actor_grid)
                            ins_extract_cells.AddCellIds([cell_label-1 for cell_label in self.__picked_labels_dict[picked_actor_name]],len(self.__picked_labels_dict[picked_actor_name]))
                            ins_extract_cells.Update()
                            
                            ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
                            ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
                            ins_extract_cells.SetInputData(None)
                            del ins_extract_cells
                            
                            ins_old_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                            ins_highlight_actor.GetMapper().SetInputData(ins_highlight_actor_grid)
                            
                            ins_old_highlight_actor_points = ins_old_highlight_actor_grid.GetPoints()
                            ins_old_highlight_actor_grid.SetPoints(None)
                            ins_old_highlight_actor_grid.Initialize()
                            del ins_old_highlight_actor_grid
                            ins_old_highlight_actor_points.Initialize()
                            del ins_old_highlight_actor_points
                    else:
                        return None
                else:
                    pass
            elif self.__selection_method == 'edge':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'face':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'entity':
                self.__picked_labels_dict[picked_actor_name] = None
                del self.__picked_labels_dict[picked_actor_name]
                
                for ins_acotr in  self.__ins_attached_renderer.GetActors():
                    if ins_acotr.GetObjectName() == highlight_actor_object_name:
                        ins_highlight_actor = ins_acotr
                        break
                    else:
                        continue
                
                self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
                
                ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
                ins_highlight_actor.SetMapper(None)
                del ins_highlight_actor
                
                ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
                ins_highlight_actor_mapper.SetInputData(None)
                ins_highlight_actor_mapper.RemoveAllInputs()
                del ins_highlight_actor_mapper
        
                ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                ins_highlight_actor_grid.SetPoints(None)
                ins_highlight_actor_grid.Initialize()
                del ins_highlight_actor_grid
                
                ins_highlight_actor_points.Initialize()
                del ins_highlight_actor_points
            else:
                return None
            
            self.GetRenderWindow().Render()
        else:
            highlight_actors_list = []
            for ins_acotr in  self.__ins_attached_renderer.GetActors():
                actor_object_name = ins_acotr.GetObjectName()
                if actor_object_name == '':
                    continue
                else:
                    pass
                if actor_object_name.split('>',1)[0] == 'highlight':
                    highlight_actors_list.append(ins_acotr)
                else:
                    continue
            while len(highlight_actors_list) > 0:
                ins_highlight_actor = highlight_actors_list.pop()
                highlight_actor_name = ins_highlight_actor.GetObjectName().split('>',1)[1]
                self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
                
                ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
                ins_highlight_actor.SetMapper(None)
                del ins_highlight_actor
                
                ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
                ins_highlight_actor_mapper.SetInputData(None)
                ins_highlight_actor_mapper.RemoveAllInputs()
                del ins_highlight_actor_mapper
        
                ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                ins_highlight_actor_grid.SetPoints(None)
                ins_highlight_actor_grid.Initialize()
                del ins_highlight_actor_grid
                
                ins_highlight_actor_points.Initialize()
                del ins_highlight_actor_points
                
                self.__picked_labels_dict[highlight_actor_name] = None
                del self.__picked_labels_dict[highlight_actor_name]
            self.GetRenderWindow().Render()
            
            if ins_picked_actor is None:
                return None
            else:
                pass
            
            picked_actor_object_name = ins_picked_actor.GetObjectName()
            picked_actor_name = picked_actor_object_name.split('>',1)[1]
            highlight_actor_object_name = 'highlight>'+ picked_actor_name
            
            if self.__selection_method == 'single':
                if self.__selection_mode == 'node':
                    picked_point_id = ins_current_picker.GetPointId()
                    
                    self.__picked_labels_dict = {}
                    self.__picked_labels_dict[picked_actor_name] = [picked_point_id+1]
                    
                    ins_highlight_actor_points = vtk.vtkPoints()
                    picked_point_coordinates = ins_picked_actor.GetMapper().GetInput().GetPoint(picked_point_id)
                    ins_highlight_actor_points.InsertNextPoint(picked_point_coordinates)
                    ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.SetPoints(ins_highlight_actor_points)
                    ins_highlight_actor_grid.InsertNextCell(1,1,[0])
                    ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                    ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                    ins_highlight_actor = vtk.vtkActor()
                    ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                    ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                    ins_highlight_actor.GetProperty().SetColor(1,0,0)
                    ins_highlight_actor.GetProperty().SetPointSize(10)
                    ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
                    self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                elif self.__selection_mode == 'element':
                    picked_cell_id = ins_current_picker.GetCellId()
                    
                    self.__picked_labels_dict = {}
                    self.__picked_labels_dict[picked_actor_name] = [picked_cell_id+1]

                    ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                    
                    ins_extract_cells = vtk.vtkExtractCells()
                    ins_extract_cells.SetInputData(ins_picked_actor_grid)
                    ins_extract_cells.AddCellIds([picked_cell_id],1)
                    ins_extract_cells.Update()
                    
                    ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
                    ins_extract_cells.SetInputData(None)
                    del ins_extract_cells
                    
                    ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                    ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                    ins_highlight_actor = vtk.vtkActor()
                    ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                    ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                    ins_highlight_actor.GetProperty().SetColor(1,0,0)
                    ins_highlight_actor.GetProperty().SetLineWidth(3)
                    ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
                    self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                else:
                    pass
            elif self.__selection_method == 'edge':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'face':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'entity':
                ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                
                self.__picked_labels_dict = {}
                if self.__selection_mode == 'node':
                    self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfPoints()+1,1))
                elif self.__selection_mode == 'element':
                    self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfCells()+1,1))
                else:
                    pass
                
                ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                ins_highlight_actor_grid.DeepCopy(ins_picked_actor_grid)
                ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                ins_highlight_actor = vtk.vtkActor()
                ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                ins_highlight_actor.GetProperty().SetColor(1,0,0)
                if self.__selection_mode == 'node':
                    ins_highlight_actor.GetProperty().SetPointSize(10)
                    ins_highlight_actor.GetProperty().SetRepresentationToPoints()
                    ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
                elif self.__selection_mode == 'element':
                    ins_highlight_actor.GetProperty().SetLineWidth(3)
                    ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
                else:
                    pass
                
                self.__ins_attached_renderer.AddActor(ins_highlight_actor)
            else:
                pass
            
            self.GetRenderWindow().Render()
    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.MiddleButton:
            self.GetInteractorStyle().EndRotate()
            self.GetInteractorStyle().EndPan()
            
            return None
        elif ev.button() == QtCore.Qt.RightButton:
            self.GetInteractorStyle().EndSpin()
            self.GetInteractorStyle().EndDolly()
            
            return None
        elif ev.button() == QtCore.Qt.LeftButton:
            if self.__selection_mode is None:
                return None
            elif self.__selection_method == 'area' and self.__is_rubber_selection:
                super().mouseReleaseEvent(ev)
            else:
                return None
        else:
            return None  

        print("Coming soon!")
        return None
    
    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Control:
            self.SetControlKey(1)
        elif ev.key() == QtCore.Qt.Key_Shift:
            self.SetShiftKey(1)
        elif ev.key() == QtCore.Qt.Key_R:
            if self.__selection_mode is None:
                return None
            elif self.__selection_method == 'area':
                super().keyPressEvent(ev)
                
                if self.__is_rubber_selection:
                    self.__is_rubber_selection = False
                else:
                    self.__is_rubber_selection = True
            else:
                pass
        else:
            pass
    def keyReleaseEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Control:
            self.SetControlKey(0)
        elif ev.key() == QtCore.Qt.Key_Shift:
            self.SetShiftKey(0)
        else:
            pass
    
    def getInteractorSelection(self) -> dict:
        return self.__picked_labels_dict
    def setInteractorSelectionMode(self, in_mode:str) -> None:
        highlight_actors_list = []
        for ins_acotr in  self.__ins_attached_renderer.GetActors():
            actor_object_name = ins_acotr.GetObjectName()
            if actor_object_name == '':
                continue
            else:
                pass
            if actor_object_name.split('>',1)[0] == 'highlight':
                highlight_actors_list.append(ins_acotr)
            else:
                continue
        while len(highlight_actors_list) > 0:
            ins_highlight_actor = highlight_actors_list.pop()
            self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
            
            ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
            ins_highlight_actor.SetMapper(None)
            del ins_highlight_actor
            
            ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
            ins_highlight_actor_mapper.SetInputData(None)
            ins_highlight_actor_mapper.RemoveAllInputs()
            del ins_highlight_actor_mapper
    
            ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
            ins_highlight_actor_grid.SetPoints(None)
            ins_highlight_actor_grid.Initialize()
            del ins_highlight_actor_grid
            
            ins_highlight_actor_points.Initialize()
            del ins_highlight_actor_points
        self.GetRenderWindow().Render()
        
        if self.__picked_labels_dict == {}:
            pass
        else:
            self.__picked_labels_dict = {}
        
        if in_mode == 'node':
            if self.__selection_mode == 'node':
                pass
            else:
                if self.__selection_method == 'single':
                    self.SetPicker(self.__point_picker)
                else: 
                    pass
        elif in_mode == 'element':
            if self.__selection_mode == 'element':
                pass
            else:
                self.SetPicker(self.__cell_picker)
        else:
            if in_mode is None and self.__is_rubber_selection:
                self.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress,QtCore.Qt.Key.Key_R,QtCore.Qt.KeyboardModifier.NoModifier))
            else:
                pass
            
            self.__selection_method = 'single'
        
        self.__selection_mode = in_mode
    def setInteractorSelectionMethod(self, in_mehtod:str) -> None:
        if self.__selection_mode == 'node':
            if in_mehtod == self.__selection_method:
                pass
            elif in_mehtod in ['single','edge','face']:
                self.SetPicker(self.__point_picker)
            elif in_mehtod == 'area':
                self.SetPicker(self.__area_picker)
            elif in_mehtod == 'entity':
                self.SetPicker(self.__prop_picker)
            else:
                pass    
        elif self.__selection_mode == 'element':
            if in_mehtod == self.__selection_method:
                pass
            elif in_mehtod in ['single','edge','face']:
                self.SetPicker(self.__cell_picker)
            elif in_mehtod == 'area':
                self.SetPicker(self.__area_picker)
            elif in_mehtod == 'entity':
                self.SetPicker(self.__prop_picker)
            else:
                pass 
        else:
            pass
        
        if self.__selection_method == 'area' and in_mehtod != 'area' and self.__is_rubber_selection:
            self.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress,QtCore.Qt.Key.Key_R,QtCore.Qt.KeyboardModifier.NoModifier))
        else:
            pass
        
        self.__selection_method = in_mehtod
    def setInteractorViewOrientation(self, in_view_orientation:str) -> None:
        ins_current_renderer_camera = self.__ins_current_renderer.GetActiveCamera()
        ins_current_renderer_camera.SetFocalPoint(0,0,0)
        if in_view_orientation == 'front':
            ins_current_renderer_camera.SetPosition(0,0,10)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'back':
            ins_current_renderer_camera.SetPosition(0,0,-10)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'top':
            ins_current_renderer_camera.SetPosition(0,10,0)
            ins_current_renderer_camera.SetViewUp(0, 0, -1)
        elif in_view_orientation == 'bottom':
            ins_current_renderer_camera.SetPosition(0,-10,0)
            ins_current_renderer_camera.SetViewUp(0, 0, 1)
        elif in_view_orientation == 'left':
            ins_current_renderer_camera.SetPosition(-10,0,0)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'right':
            ins_current_renderer_camera.SetPosition(10,0,0)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'iso':
            ins_current_renderer_camera.SetPosition(10,10,10)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'fit':
            pass
        else:
            return None

        self.__ins_current_renderer.ResetCamera()
        ins_current_renderer_camera.ComputeViewPlaneNormal()
        self.GetRenderWindow().Render()
    
    def setInteractorRenderStyle(self, in_style:str) -> None:
        ins_render_window = self.GetRenderWindow()
        if in_style == 'normal':
            for ins_actor in self.__ins_current_renderer.GetActors():
                if ins_actor.GetObjectName().split('>',1)[0] == 'object':
                    ins_actor.GetProperty().EdgeVisibilityOff()
                    ins_actor.GetProperty().SetRepresentationToSurface()
                else: continue
        elif in_style == 'wireframe':
            for ins_actor in self.__ins_current_renderer.GetActors():
                if ins_actor.GetObjectName().split('>',1)[0] == 'object':
                    ins_actor.GetProperty().EdgeVisibilityOff()
                    ins_actor.GetProperty().SetRepresentationToWireframe()
                else: continue
        elif in_style == 'mesh':
            for ins_actor in self.__ins_current_renderer.GetActors():
                if ins_actor.GetObjectName().split('>',1)[0] == 'object':
                    ins_actor.GetProperty().EdgeVisibilityOn()
                    ins_actor.GetProperty().SetRepresentationToSurface()
                else: continue
        else:
            return None
        ins_render_window.Render()
    
    def getRendererIncludeActorsColor(self) -> dict:
        actors_color_dict = {}
        for ins_actor in self.__ins_current_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                actors_color_dict[actor_object_name_info_list[1]] = ins_actor.GetProperty().GetColor()
            else:
                continue
        return actors_color_dict
    def setInteractorRendererIncludeAcotrsColor(self, in_actors_color_dict:dict) -> None:
        for ins_actor in self.__ins_current_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object' and actor_object_name_info_list[1] in in_actors_color_dict:
                ins_actor.GetProperty().SetColor(in_actors_color_dict[actor_object_name_info_list[1]])
            else:
                continue
        self.GetRenderWindow().Render()
    
    def getRendererIncludeActorsOpacity(self) -> dict:
        actors_opacity_dict = {}
        for ins_actor in self.__ins_current_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                actors_opacity_dict[actor_object_name_info_list[1]] = ins_actor.GetProperty().GetOpacity()
            else:
                continue
        return actors_opacity_dict
    def setInteractorRendererIncludeAcotrsOpacity(self, in_actors_opacity_dict:dict) -> None:
        for ins_actor in self.__ins_current_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object' and actor_object_name_info_list[1] in in_actors_opacity_dict:
                ins_actor.GetProperty().SetOpacity(in_actors_opacity_dict[actor_object_name_info_list[1]])
            else:
                continue
        self.GetRenderWindow().Render()
    
    def getRendererIncludeActorsVisibility(self) -> dict:
        actors_visibility_dict = {}
        for ins_actor in self.__ins_current_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                actors_visibility_dict[actor_object_name_info_list[1]] = ins_actor.GetVisibility()
            else:
                continue
        return actors_visibility_dict
    def setRendererIncludeActorsVisibility(self, in_actors_visibility_dict:dict) -> None:
        for ins_actor in self.__ins_current_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object' and actor_object_name_info_list[1] in in_actors_visibility_dict:
                ins_actor.SetVisibility(in_actors_visibility_dict[actor_object_name_info_list[1]])
            else:
                continue
        self.GetRenderWindow().Render()
    
    def switchModuleRenderer(self, in_module_type:str, in_part_name:str=None) -> None:
        ins_render_window = self.GetRenderWindow()
        
        ins_render_window.RemoveRenderer(self.__ins_current_renderer)
        if in_module_type == 'Part':
            ins_render_window.AddRenderer(self.__parts_renderer_dict[in_part_name])
            self.__ins_current_renderer = self.__parts_renderer_dict[in_part_name]
            
            for ins_view_prpo in self.__ins_attached_renderer.GetViewProps():
                if ins_view_prpo.GetObjectName() == 'GCSYS':
                    if ins_view_prpo.GetVisibility() == self.__axes_visibility_dict['parts'][in_part_name]:
                        pass
                    else:
                        if self.__axes_visibility_dict['parts'][in_part_name]:
                            ins_view_prpo.VisibilityOn()
                        else:
                            ins_view_prpo.VisibilityOff()
                    break
                else:
                    continue
        else:
            ins_render_window.AddRenderer(self.__ins_assembly_renderer)
            self.__ins_current_renderer = self.__ins_assembly_renderer
            
            for ins_view_prpo in self.__ins_attached_renderer.GetViewProps():
                if ins_view_prpo.GetObjectName() == 'GCSYS':
                    if ins_view_prpo.GetVisibility() == self.__axes_visibility_dict['assembly']:
                        pass
                    else:
                        if self.__axes_visibility_dict['assembly']:
                            ins_view_prpo.VisibilityOn()
                        else:
                            ins_view_prpo.VisibilityOff()
                    break
                else:
                    continue

        max_bound_size = max([abs(bound_size) for bound_size in list(self.__ins_current_renderer.ComputeVisiblePropBounds())])
        coordinate_systems_actor_list = []
        boundary_conditions_actor_list = []
        for ins_actor in self.__ins_attached_renderer.GetViewProps():
            if ins_actor.GetObjectName() == '':
                continue
            else:
                pass
            
            if ins_actor.GetObjectName() == 'GCSYS':
                ins_actor.SetTotalLength(max_bound_size,max_bound_size,max_bound_size)
            elif ins_actor.GetObjectName().split('>',1)[0] == 'csys':
                coordinate_systems_actor_list.append(ins_actor)
            elif ins_actor.GetObjectName().split('>',1)[0] == 'eori':
                coordinate_systems_actor_list.append(ins_actor)
            elif ins_actor.GetObjectName().split('>',1)[0] == 'bc':
                boundary_conditions_actor_list.append(ins_actor)
            else:
                continue
        for ins_coordinate_system_axes_viewprop in coordinate_systems_actor_list:
            self.__ins_attached_renderer.RemoveViewProp(ins_coordinate_system_axes_viewprop)
        del coordinate_systems_actor_list
        for ins_boundary_conditon_actor in boundary_conditions_actor_list:
            self.__ins_attached_renderer.RemoveActor(ins_boundary_conditon_actor)
        del boundary_conditions_actor_list
        
        self.__ins_attached_renderer.SetActiveCamera(self.__ins_current_renderer.GetActiveCamera())        
        
        ins_render_window.Render()
    def getCoordinateSystemsOfCurrentRenderer(self) -> list:
        coordinate_systems_name_list = []
        for ins_actor in self.__ins_attached_renderer.GetViewProps():
            actor_object_name = ins_actor.GetObjectName()
            if actor_object_name == '':
                continue
            else:
                pass
            
            if actor_object_name.split('>',1)[0] == 'csys':
                coordinate_systems_name_list.append(actor_object_name.split('>',1)[1])
            else:
                continue
        return coordinate_systems_name_list
    def addCoordinateSystemToCurrentRenderer(self, in_coordinate_system_name:str, in_coordinate_system_ifno:dict) -> None:
        ins_coordinate_system_actor = vtk.vtkAxesActor()
        ins_coordinate_system_actor.SetObjectName('csys>'+in_coordinate_system_name)
        ins_coordinate_system_actor.SetConeRadius(0)
        
        for ins_view_prop in self.__ins_attached_renderer.GetViewProps():
            if ins_view_prop.GetObjectName() == 'GCSYS':
                axes_length_list = [axes_length*0.2 for axes_length in ins_view_prop.GetTotalLength()]
                axes_text_font_size = int(ins_view_prop.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().GetFontSize()*0.5)
                break
            else:
                continue
        ins_coordinate_system_actor.SetTotalLength(axes_length_list)
        
        ins_coordinate_system_transformer = vtk.vtkTransform()
        ins_coordinate_system_transformer.Translate(in_coordinate_system_ifno['origin'])
        ins_coordinate_system_transformer.RotateWXYZ(*in_coordinate_system_ifno['orientation'])
        ins_coordinate_system_actor.SetUserTransform(ins_coordinate_system_transformer)
        if in_coordinate_system_ifno['type'] == 1:
            ins_coordinate_system_actor.SetXAxisLabelText('x')
            ins_coordinate_system_actor.SetYAxisLabelText('y')
            ins_coordinate_system_actor.SetZAxisLabelText('z')
        elif in_coordinate_system_ifno['type'] == 2:
            ins_coordinate_system_actor.SetXAxisLabelText('r')
            ins_coordinate_system_actor.SetYAxisLabelText('t')
            ins_coordinate_system_actor.SetZAxisLabelText('z')
        elif in_coordinate_system_ifno['type'] == 3:
            ins_coordinate_system_actor.SetXAxisLabelText('r')
            ins_coordinate_system_actor.SetYAxisLabelText('t')
            ins_coordinate_system_actor.SetZAxisLabelText('p')
        else:
            pass  
        
        ins_axes_x_text_actor = ins_coordinate_system_actor.GetXAxisCaptionActor2D().GetTextActor()
        ins_axes_x_text_actor.SetTextScaleModeToNone()
        ins_axes_x_text_actor.GetTextProperty().SetFontSize(axes_text_font_size)
        ins_axes_x_text_actor.GetTextProperty().SetColor(0,0,0)
        ins_axes_y_text_actor = ins_coordinate_system_actor.GetYAxisCaptionActor2D().GetTextActor()
        ins_axes_y_text_actor.SetTextScaleModeToNone()
        ins_axes_y_text_actor.GetTextProperty().SetFontSize(axes_text_font_size)
        ins_axes_y_text_actor.GetTextProperty().SetColor(0,0,0)
        ins_axes_z_text_actor = ins_coordinate_system_actor.GetZAxisCaptionActor2D().GetTextActor()
        ins_axes_z_text_actor.SetTextScaleModeToNone()
        ins_axes_z_text_actor.GetTextProperty().SetFontSize(axes_text_font_size)
        ins_axes_z_text_actor.GetTextProperty().SetColor(0,0,0)
    
        self.__ins_attached_renderer.AddActor(ins_coordinate_system_actor)
        self.GetRenderWindow().Render()
    def deleteCoordinateSystemOfCurrentRenderer(self, in_coordinate_system_name:str) -> None:
        for ins_actor in self.__ins_attached_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'csys>'+in_coordinate_system_name:
                self.__ins_attached_renderer.RemoveViewProp(ins_actor)
                del ins_actor
                break
            else:
                continue
        
        self.GetRenderWindow().Render()
    def renameCoordinateSystemOfCurrentRenderer(self, in_old_coordinate_system_name:str, in_new_coordinate_system_name:str) -> None:
        for ins_actor in self.__ins_attached_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'csys>'+in_old_coordinate_system_name:
                ins_actor.SetObjectName('csys>'+in_new_coordinate_system_name)
                break
            else:
                continue
    def editCoordinateSystemOfCurrentRenderer(self, in_coordinate_system_name:str, in_type:str, in_reference_axis:str, in_value: float) -> None:
        for ins_actor in self.__ins_attached_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'csys>'+in_coordinate_system_name:
                ins_coordinate_system_transformer = ins_actor.GetUserTransform()
                break
            else:
                continue
    
        if in_type == 'translate':
            if in_reference_axis == 'X':
                ins_coordinate_system_transformer.Translate(in_value,0.0,0.0)
            elif in_reference_axis == 'Y':
                ins_coordinate_system_transformer.Translate(0.0,in_value,0.0)
            elif in_reference_axis == 'Z':
                ins_coordinate_system_transformer.Translate(0.0,0.0,in_value)
            else:
                pass
        elif in_type == 'rotate':
            if in_reference_axis == 'RX':
                ins_coordinate_system_transformer.RotateX(in_value)
            elif in_reference_axis == 'RY':
                ins_coordinate_system_transformer.RotateY(in_value)
            elif in_reference_axis == 'RZ':
                ins_coordinate_system_transformer.RotateZ(in_value)
            else:
                pass        
        else:
            pass
        
        self.GetRenderWindow().Render()
    def switchPartRenderer(self, in_part_name:str) -> None:
        ins_render_window = self.GetRenderWindow()
        
        if self.__ins_current_renderer is self.__parts_renderer_dict[in_part_name]:
            return None
        else:
            pass
        
        ins_render_window.RemoveRenderer(self.__ins_current_renderer)
        ins_render_window.AddRenderer(self.__parts_renderer_dict[in_part_name])
        self.__ins_current_renderer = self.__parts_renderer_dict[in_part_name]

        max_bound_size = max([abs(bound_size) for bound_size in list(self.__ins_current_renderer.ComputeVisiblePropBounds())])
        coordinate_systems_actor_list = []
        boundary_conditions_actor_list = []
        for ins_actor in self.__ins_attached_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'GCSYS':
                ins_actor.SetTotalLength(max_bound_size,max_bound_size,max_bound_size)
            elif ins_actor.GetObjectName().split('>',1)[0] == 'csys':
                coordinate_systems_actor_list.append(ins_actor)
            elif ins_actor.GetObjectName().split('>',1)[0] == 'eori':
                coordinate_systems_actor_list.append(ins_actor)
            elif ins_actor.GetObjectName().split('>',1)[0] == 'bc':
                boundary_conditions_actor_list.append(ins_actor)
            else:
                continue
        for ins_coordinate_system_axes_viewprop in coordinate_systems_actor_list:
            self.__ins_attached_renderer.RemoveViewProp(ins_coordinate_system_axes_viewprop)
        del coordinate_systems_actor_list
        for ins_boundary_conditon_actor in boundary_conditions_actor_list:
            self.__ins_attached_renderer.RemoveActor(ins_boundary_conditon_actor)
        del boundary_conditions_actor_list

        self.__ins_attached_renderer.SetActiveCamera(self.__ins_current_renderer.GetActiveCamera())
        
        for ins_view_prpo in self.__ins_attached_renderer.GetViewProps():
            if ins_view_prpo.GetObjectName() == 'GCSYS':
                if ins_view_prpo.GetVisibility() == self.__axes_visibility_dict['parts'][in_part_name]:
                    pass
                else:
                    if self.__axes_visibility_dict['parts'][in_part_name]:
                        ins_view_prpo.VisibilityOn()
                    else:
                        ins_view_prpo.VisibilityOff()
                break
            else:
                continue
        
        ins_render_window.Render()
    def createPartRenderer(self, in_ins_project_database:object, in_model_name:str, in_part_name:str) -> None:
        ins_part_renderer = vtk.vtkRenderer()
        ins_part_renderer.SetLayer(0)
        ins_part_renderer.SetBackground(178/255,187/255,190/255)
        ins_part_renderer.SetBackground2(138/255,152/255,142/255)
        ins_part_renderer.GetActiveCamera().ParallelProjectionOn()
        ins_part_renderer.SetGradientBackground(1)
        
        ins_module_tip = vtk.vtkCornerAnnotation()
        ins_module_tip.SetText(1,'Part')
        ins_module_tip.SetLinearFontScaleFactor(6)
        ins_module_tip.GetTextProperty().SetColor(1, 1, 0)
        ins_part_renderer.AddViewProp(ins_module_tip)
        
        nodes_list, elements_list, nodes_number, elemetns_number = in_ins_project_database.getPartComponents(in_model_name,in_part_name)

        ins_informatiopn_tips = vtk.vtkCornerAnnotation()
        ins_informatiopn_tips.SetObjectName('part-tips')
        ins_informatiopn_tips.SetText(2,f'Name:{in_part_name}\nNoes:{str(nodes_number)}\nElements:{str(elemetns_number)}')
        ins_informatiopn_tips.SetLinearFontScaleFactor(4)
        ins_informatiopn_tips.GetTextProperty().SetColor(1, 1, 1)
        ins_part_renderer.AddViewProp(ins_informatiopn_tips)
        
        ins_part_nodes = vtk.vtkPoints()
        ins_part_nodes.SetNumberOfPoints(nodes_number)
        for node_index,node_coordinates in enumerate(nodes_list):
            ins_part_nodes.SetPoint(node_index,node_coordinates)
        del nodes_list
        
        ins_part_mesh = vtk.vtkUnstructuredGrid()
        ins_part_mesh.SetPoints(ins_part_nodes)
        cell_type_from_geometry = {1:3, 6:21, 2:5, 7:22, 3:9, 8:23, 4:10, 9:24, 5:12, 10:25}
        for element_info in elements_list:
            ins_part_mesh.InsertNextCell(cell_type_from_geometry[element_info[0]],len(element_info[1]),[node_index-1 for node_index in element_info[1]])
        del elements_list
        
        ins_part_mapper = vtk.vtkDataSetMapper()
        ins_part_mapper.SetInputData(ins_part_mesh)
        ins_part_actor = vtk.vtkActor()
        ins_part_actor.SetObjectName('object>'+in_part_name)
        ins_part_actor.SetMapper(ins_part_mapper)
        ins_part_actor.PickableOn()
        ins_part_renderer.AddActor(ins_part_actor)
        ins_part_renderer.ResetCamera()
        
        self.__parts_renderer_dict[in_part_name] = ins_part_renderer
        
        self.__axes_visibility_dict['parts'][in_part_name] = True
    def renamePartRenderer(self, in_old_part_name:str, in_new_part_name:str) -> None:
        ins_part_renderer = self.__parts_renderer_dict[in_old_part_name]
        self.__parts_renderer_dict[in_old_part_name] = None
        del self.__parts_renderer_dict[in_old_part_name]
        self.__parts_renderer_dict[in_new_part_name] = ins_part_renderer
        
        for ins_view_prop in ins_part_renderer.GetViewProps():
            if ins_view_prop.GetObjectName() == 'part-tips':
                tips_text_list = ins_view_prop.GetText(2).split('\n')
                tips_text_list[0] = f'Name:{in_new_part_name}'
                ins_view_prop.SetText(2,'\n'.join(tips_text_list))
            else:
                continue

        for ins_part_actor in ins_part_renderer.GetActors():
            if ins_part_actor.GetObjectName() == 'object>'+in_old_part_name:
                ins_part_actor.SetObjectName('object>'+in_new_part_name)
                break
            else:
                continue
        for ins_part_actor in self.__ins_attached_renderer.GetActors():
            if ins_part_actor.GetObjectName() == 'highlight>'+in_old_part_name:
                ins_part_actor.SetObjectName('highlight>'+in_new_part_name)
                break
            else:
                continue

        if in_old_part_name in self.__picked_labels_dict:
            part_selection_label_list = self.__picked_labels_dict[in_old_part_name]
            self.__picked_labels_dict[in_old_part_name] = None
            del self.__picked_labels_dict[in_old_part_name]
            self.__picked_labels_dict[in_new_part_name] = part_selection_label_list
        else:
            pass

        self.GetRenderWindow().Render()
        
        self.__axes_visibility_dict['parts'][in_new_part_name] = self.__axes_visibility_dict['parts'][in_old_part_name]
        self.__axes_visibility_dict['parts'][in_old_part_name] = None
        del self.__axes_visibility_dict['parts'][in_old_part_name]
    def removePartRenderer(self, in_part_name:str) -> None:
        ins_part_renderer = self.__parts_renderer_dict[in_part_name]
        self.__parts_renderer_dict[in_part_name] = None
        del self.__parts_renderer_dict[in_part_name]
        
        for ins_actor in ins_part_renderer.GetActors():
            if ins_actor.GetObjectName() == 'object>'+in_part_name:
                ins_part_object_actor = ins_actor
                break
            else:
                continue
        ins_part_renderer.RemoveActor(ins_part_object_actor)
        ins_part_renderer.RemoveAllViewProps()
        del ins_part_renderer
        ins_object_actor_mapper = ins_part_object_actor.GetMapper()
        ins_part_object_actor.SetMapper(None)
        del ins_part_object_actor
        ins_object_actor_grid = ins_object_actor_mapper.GetInput()
        ins_object_actor_mapper.SetInputData(None)
        ins_object_actor_mapper.RemoveAllInputs()
        del ins_object_actor_mapper
        ins_object_actor_points = ins_object_actor_grid.GetPoints()
        ins_object_actor_grid.SetPoints(None)
        ins_object_actor_grid.Initialize()
        del ins_object_actor_grid
        ins_object_actor_points.Initialize()
        del ins_object_actor_points
        
        self.__axes_visibility_dict['parts'][in_part_name] = None
        del self.__axes_visibility_dict['parts'][in_part_name]
    def switchPartRendererAxesVisibility(self, in_part_name:str) -> None:
        if self.__ins_current_renderer is self.__parts_renderer_dict[in_part_name]:
            for ins_view_prpo in self.__ins_attached_renderer.GetViewProps():
                if ins_view_prpo.GetObjectName() == 'GCSYS':
                    if ins_view_prpo.GetVisibility():
                        ins_view_prpo.VisibilityOff()
                    else:
                        ins_view_prpo.VisibilityOn()
                    break
                else:
                    continue
        else:
            pass
        
        if self.__axes_visibility_dict['parts'][in_part_name]:
            self.__axes_visibility_dict['parts'][in_part_name] = False
        else:
            self.__axes_visibility_dict['parts'][in_part_name] = True
        
        self.GetRenderWindow().Render()
    def showGroupOfPartRenderer(self, in_ins_project_database:object, in_model_name:str, in_part_name:str, in_group_type:str, in_group_name:str) -> None:
        self.__picked_labels_dict[in_part_name] = in_ins_project_database.getPartGroupLabels(in_model_name,in_part_name,in_group_type,in_group_name)
        
        for ins_actor in self.__parts_renderer_dict[in_part_name].GetActors():
            if ins_actor.GetObjectName() == f'object>{in_part_name}':
                ins_object_actor = ins_actor
                break
            else:
                continue
        
        if in_group_type == 'node':
            ins_highlight_actor_points = vtk.vtkPoints()
            ins_object_actor_grid = ins_object_actor.GetMapper().GetInput()
            for node_label in self.__picked_labels_dict[in_part_name]:
                point_coordinates = ins_object_actor_grid.GetPoint(node_label-1)
                ins_highlight_actor_points.InsertNextPoint(point_coordinates)
            ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
            ins_highlight_actor_grid.SetPoints(ins_highlight_actor_points)
            for point_index in range(len(self.__picked_labels_dict[in_part_name])):
                ins_highlight_actor_grid.InsertNextCell(1,1,[point_index])
            ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
            ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
            ins_highlight_actor = vtk.vtkActor()
            ins_highlight_actor.SetObjectName('highlight>'+in_part_name)
            ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
            ins_highlight_actor.GetProperty().SetColor(1,0,0)
            ins_highlight_actor.GetProperty().SetPointSize(10)
            ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
            self.__ins_attached_renderer.AddActor(ins_highlight_actor)
        elif in_group_type == 'element':
            ins_object_actor_grid = ins_object_actor.GetMapper().GetInput()
            
            ins_extract_cells = vtk.vtkExtractCells()
            ins_extract_cells.SetInputData(ins_object_actor_grid)
            ins_extract_cells.AddCellIds([cell_label-1 for cell_label in self.__picked_labels_dict[in_part_name]],len(self.__picked_labels_dict[in_part_name]))
            ins_extract_cells.Update()
            
            ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
            ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
            ins_extract_cells.SetInputData(None)
            del ins_extract_cells
            
            ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
            ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
            ins_highlight_actor = vtk.vtkActor()
            ins_highlight_actor.SetObjectName('highlight>'+in_part_name)
            ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
            ins_highlight_actor.GetProperty().SetColor(1,0,0)
            ins_highlight_actor.GetProperty().SetLineWidth(3)
            ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
            self.__ins_attached_renderer.AddActor(ins_highlight_actor)
        else:
            pass
        
        self.GetRenderWindow().Render()
    def switchPartRendererElementsOrientationVisibility(self, in_ins_project_database:object, in_model_name:str, in_part_name:str, in_group_name:str) -> None:
        remove_elements_orientation_actor_list = []
        for ins_actor in self.__ins_attached_renderer.GetViewProps():
            if ins_actor.GetObjectName().split('>',1)[0] == 'eori':
                remove_elements_orientation_actor_list.append(ins_actor)
            else:
                continue
        for _ in range(len(remove_elements_orientation_actor_list)):
            ins_element_orientation_actor = remove_elements_orientation_actor_list.pop()
            self.__ins_attached_renderer.RemoveViewProp(ins_element_orientation_actor)
            del ins_element_orientation_actor
        del remove_elements_orientation_actor_list
    
        if in_group_name is None:
            pass
        else:
            elements_orientation_parameters_dict = in_ins_project_database.getPartElementsOrientationParameters(in_model_name,in_part_name,in_group_name)
            
            for element_index, element_label in enumerate(elements_orientation_parameters_dict):
                if len(elements_orientation_parameters_dict) > 100:
                    if element_index % 5 == 0.0:
                        pass
                    else:
                        continue
                else:
                    pass
                
                element_orientation_parameters_list = elements_orientation_parameters_dict[element_label]
                
                ins_axes_actor = vtk.vtkAxesActor()
                ins_axes_actor.SetObjectName(f'eori>{str(element_label)}')
                ins_axes_actor.SetConeRadius(0)
                ins_axes_actor.SetXAxisLabelText('1')
                ins_axes_x_text_actor = ins_axes_actor.GetXAxisCaptionActor2D().GetTextActor()
                ins_axes_x_text_actor.SetTextScaleModeToNone()
                ins_axes_x_text_actor.GetTextProperty().SetFontSize(10)
                ins_axes_actor.SetYAxisLabelText('2')
                ins_axes_y_text_actor = ins_axes_actor.GetYAxisCaptionActor2D().GetTextActor()
                ins_axes_y_text_actor.SetTextScaleModeToNone()
                ins_axes_y_text_actor.GetTextProperty().SetFontSize(10)
                ins_axes_actor.SetZAxisLabelText('3')
                ins_axes_z_text_actor = ins_axes_actor.GetZAxisCaptionActor2D().GetTextActor()
                ins_axes_z_text_actor.SetTextScaleModeToNone()
                ins_axes_z_text_actor.GetTextProperty().SetFontSize(10)
                
                ins_orientation_transformer = vtk.vtkTransform()
                ins_orientation_transformer.Translate(element_orientation_parameters_list[0:3])
                ins_orientation_transformer.RotateWXYZ(*element_orientation_parameters_list[3:])
                ins_axes_actor.SetUserTransform(ins_orientation_transformer)
                
                self.__ins_attached_renderer.AddActor(ins_axes_actor)

        self.GetRenderWindow().Render()

    def switchAssemblyRendererAxesVisibility(self) -> None:
        if self.__ins_current_renderer is self.__ins_assembly_renderer:
            for ins_view_prpo in self.__ins_attached_renderer.GetViewProps():
                if ins_view_prpo.GetObjectName() == 'GCSYS':
                    if ins_view_prpo.GetVisibility():
                        ins_view_prpo.VisibilityOff()
                    else:
                        ins_view_prpo.VisibilityOn()
                    break
                else:
                    continue
        else:
            pass
        
        if self.__axes_visibility_dict['assembly']:
            self.__axes_visibility_dict['assembly'] = False
        else:
            self.__axes_visibility_dict['assembly'] = True
        
        self.GetRenderWindow().Render()
    def addInstanceToAssemblyRenderer(self, in_part_name:str, in_instance_name:str, in_instance_orientation:list) -> None:
        for ins_actor in self.__parts_renderer_dict[in_part_name].GetActors():
            if ins_actor.GetObjectName() == f'object>{in_part_name}':
                ins_part_actor = ins_actor
                break
            else:
                continue
        
        ins_instance_mesh = vtk.vtkUnstructuredGrid()
        ins_instance_mesh.DeepCopy(ins_part_actor.GetMapper().GetInput())
        
        ins_instance_mapper = vtk.vtkDataSetMapper()
        
        if in_instance_orientation == []:
            ins_instance_mapper.SetInputData(ins_instance_mesh)
        else:
            ins_instance_transformer = vtk.vtkTransform()
            ins_instance_transformer.PostMultiply()
            ins_instance_transformer.RotateWXYZ(*in_instance_orientation[3:])
            ins_instance_transformer.Translate(in_instance_orientation[0:3])
            
            ins_instance_transformer_filter = vtk.vtkTransformFilter()
            ins_instance_transformer_filter.SetTransform(ins_instance_transformer)
            ins_instance_transformer_filter.SetInputData(ins_instance_mesh)
            ins_instance_transformer_filter.Update()
            ins_instance_mapper.SetInputData(ins_instance_transformer_filter.GetOutput())
        
        ins_instance_actor = vtk.vtkActor()
        ins_instance_actor.SetObjectName('object>'+in_instance_name)
        ins_instance_actor.SetMapper(ins_instance_mapper)
        ins_instance_actor.PickableOn()
        self.__ins_assembly_renderer.AddActor(ins_instance_actor)
        
        self.__ins_assembly_renderer.ResetCamera()

        max_bound_size = max([abs(bound_size) for bound_size in list(self.__ins_assembly_renderer.ComputeVisiblePropBounds())])
        for ins_actor in self.__ins_attached_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'GCSYS':
                ins_actor.SetTotalLength(max_bound_size,max_bound_size,max_bound_size)
                break
            else:
                continue

        self.GetRenderWindow().Render()
    def renameInstanceOfAssemblyRenderer(self, in_old_instance_name:str,in_new_instance_name:str) -> None:
        for ins_instance_actor in self.__ins_assembly_renderer.GetActors():
            if ins_instance_actor.GetObjectName() == 'object>'+in_old_instance_name:
                ins_instance_actor.SetObjectName('object>'+in_new_instance_name)
                break
            else:
                continue
        for ins_instance_actor in self.__ins_attached_renderer.GetActors():
            if ins_instance_actor.GetObjectName() == 'highlight>'+in_old_instance_name:
                ins_instance_actor.SetObjectName('highlight>'+in_new_instance_name)
                break
            else:
                continue

        if in_old_instance_name in self.__picked_labels_dict:
            instance_selection_label_list = self.__picked_labels_dict[in_old_instance_name]
            self.__picked_labels_dict[in_old_instance_name] = None
            del self.__picked_labels_dict[in_old_instance_name]
            self.__picked_labels_dict[in_new_instance_name] = instance_selection_label_list
        else:
            pass
    def editInstanceOrientationOfAssemblyRenderer(self,in_instance_name:str, in_type:str, in_assembly_coordinate_system_info:dict, in_direction:str, in_value:float) -> None:
        for ins_instance_actor in self.__ins_assembly_renderer.GetActors():
            if ins_instance_actor.GetObjectName() == 'object>'+in_instance_name:
                ins_object_instance_actor = ins_instance_actor
                break
            else:
                continue
        
        ins_assembly_coordinate_system_transformer = vtk.vtkTransform()
        ins_assembly_coordinate_system_transformer.PostMultiply()
        ins_assembly_coordinate_system_transformer.Translate(in_assembly_coordinate_system_info['origin'])
        ins_assembly_coordinate_system_transformer.RotateWXYZ(*in_assembly_coordinate_system_info['orientation'])
        
        ins_new_instance_transformer = vtk.vtkTransform()
        ins_new_instance_transformer.PostMultiply()
        if in_type == 'translate':
            if in_direction == '1':
                global_translate_vector = ins_assembly_coordinate_system_transformer.TransformVector(in_value,0.0,0.0)
            elif in_direction == '2':
                global_translate_vector = ins_assembly_coordinate_system_transformer.TransformVector(0.0,in_value,0.0)
            elif in_direction == '3':
                global_translate_vector = ins_assembly_coordinate_system_transformer.TransformVector(0.0,0.0,in_value)
            else:
                pass
        
            ins_new_instance_transformer.Translate(global_translate_vector)
        elif in_type == 'rotate':
            ins_new_instance_transformer.Translate([-i for i in in_assembly_coordinate_system_info['origin']])
            
            if in_direction == '1':
                global_rotation_axis = ins_assembly_coordinate_system_transformer.TransformVector(1.0,0.0,0.0)
            elif in_direction == '2':
                global_rotation_axis = ins_assembly_coordinate_system_transformer.TransformVector(0.0,1.0,0.0)
            elif in_direction == '3':
                global_rotation_axis = ins_assembly_coordinate_system_transformer.TransformVector(0.0,0.0,1.0)
            else:
                pass
            ins_new_instance_transformer.RotateWXYZ(in_value,*global_rotation_axis)
            
            ins_new_instance_transformer.Translate(in_assembly_coordinate_system_info['origin'])
        else:
            pass
        
        ins_instance_transformer_filter = vtk.vtkTransformFilter()
        ins_instance_transformer_filter.SetTransform(ins_new_instance_transformer)
        ins_instance_transformer_filter.SetInputData(ins_object_instance_actor.GetMapper().GetInput())
        ins_instance_transformer_filter.Update()
        ins_object_instance_actor.GetMapper().SetInputData(ins_instance_transformer_filter.GetOutput())
        
        self.__ins_assembly_renderer.ResetCamera()
        
        self.GetRenderWindow().Render()
    def removeInstanceOfAssemblyRenderer(self, in_instance_name:str) -> None:
        for ins_actor in self.__ins_assembly_renderer.GetActors():
            if ins_actor.GetObjectName() == 'object>'+in_instance_name:
                ins_instance_object_actor = ins_actor
                break
            else:
                continue
        self.__ins_assembly_renderer.RemoveActor(ins_instance_object_actor)
        ins_object_actor_mapper = ins_instance_object_actor.GetMapper()
        ins_instance_object_actor.SetMapper(None)
        del ins_instance_object_actor
        ins_object_actor_grid = ins_object_actor_mapper.GetInput()
        ins_object_actor_mapper.SetInputData(None)
        ins_object_actor_mapper.RemoveAllInputs()
        del ins_object_actor_mapper
        ins_object_actor_points = ins_object_actor_grid.GetPoints()
        ins_object_actor_grid.SetPoints(None)
        ins_object_actor_grid.Initialize()
        del ins_object_actor_grid
        ins_object_actor_points.Initialize()
        del ins_object_actor_points
        
        ins_instance_highlight_actor = None
        for ins_actor in self.__ins_attached_renderer.GetActors():
            if ins_actor.GetObjectName() == 'highlight>'+in_instance_name:
                ins_instance_highlight_actor = ins_actor
                break
            else:
                continue
        if ins_instance_highlight_actor is None:
            pass
        else:
            self.__ins_attached_renderer.RemoveActor(ins_instance_highlight_actor)
            ins_highlight_actor_mapper = ins_instance_highlight_actor.GetMapper()
            ins_instance_highlight_actor.SetMapper(None)
            del ins_instance_highlight_actor
            ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
            ins_highlight_actor_mapper.SetInputData(None)
            ins_highlight_actor_mapper.RemoveAllInputs()
            del ins_highlight_actor_mapper
            ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
            ins_highlight_actor_grid.SetPoints(None)
            ins_highlight_actor_grid.Initialize()
            del ins_highlight_actor_grid
            ins_highlight_actor_points.Initialize()
            del ins_highlight_actor_points
        
        if in_instance_name in self.__picked_labels_dict:
            self.__picked_labels_dict[in_instance_name] = None
            del self.__picked_labels_dict[in_instance_name]
        else:
            pass
        
        instance_actor_number = 0
        for ins_actor in self.__ins_assembly_renderer.GetActors():
            if ins_actor.GetObjectName().split('>',1)[0] == 'object':
                instance_actor_number += 1
            else:
                continue
        if instance_actor_number == 0:
            self.__ins_attached_renderer.ResetCamera()
        else:
            self.__ins_assembly_renderer.ResetCamera()
            
            max_bound_size = max([abs(bound_size) for bound_size in list(self.__ins_assembly_renderer.ComputeVisiblePropBounds())])
            for ins_actor in self.__ins_attached_renderer.GetViewProps():
                if ins_actor.GetObjectName() == 'GCSYS':
                    ins_actor.SetTotalLength(max_bound_size,max_bound_size,max_bound_size)
                    break
                else:
                    continue

        self.GetRenderWindow().Render()
    def showGroupOfAssemblyRenderer(self, in_ins_project_database:object, in_model_name:str, in_group_type:str, in_group_name:str) -> None:
        self.__picked_labels_dict = in_ins_project_database.getAssemblyGroupLabels(in_model_name,in_group_type,in_group_name)
        
        for ins_actor in self.__ins_assembly_renderer.GetActors():
            if ins_actor.GetObjectName() == '':
                continue
            else:
                pass
            
            actor_sign,actor_name = ins_actor.GetObjectName().split('>',1)
            if actor_sign == 'object':
                pass
            else:
                continue
            
            if actor_name in self.__picked_labels_dict:
                ins_object_actor = ins_actor
                
                if in_group_type == 'node':
                    ins_highlight_actor_points = vtk.vtkPoints()
                    ins_object_actor_grid = ins_object_actor.GetMapper().GetInput()
                    for node_label in self.__picked_labels_dict[actor_name]:
                        point_coordinates = ins_object_actor_grid.GetPoint(node_label-1)
                        ins_highlight_actor_points.InsertNextPoint(point_coordinates)
                    ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.SetPoints(ins_highlight_actor_points)
                    for point_index in range(len(self.__picked_labels_dict[actor_name])):
                        ins_highlight_actor_grid.InsertNextCell(1,1,[point_index])
                    ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                    ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                    ins_highlight_actor = vtk.vtkActor()
                    ins_highlight_actor.SetObjectName('highlight>'+actor_name)
                    ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                    ins_highlight_actor.GetProperty().SetColor(1,0,0)
                    ins_highlight_actor.GetProperty().SetPointSize(10)
                    ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
                    self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                elif in_group_type == 'element':
                    ins_object_actor_grid = ins_object_actor.GetMapper().GetInput()
                    
                    ins_extract_cells = vtk.vtkExtractCells()
                    ins_extract_cells.SetInputData(ins_object_actor_grid)
                    ins_extract_cells.AddCellIds([cell_label-1 for cell_label in self.__picked_labels_dict[actor_name]],len(self.__picked_labels_dict[actor_name]))
                    ins_extract_cells.Update()
                    
                    ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
                    ins_extract_cells.SetInputData(None)
                    del ins_extract_cells
                    
                    ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                    ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                    ins_highlight_actor = vtk.vtkActor()
                    ins_highlight_actor.SetObjectName('highlight>'+actor_name)
                    ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                    ins_highlight_actor.GetProperty().SetColor(1,0,0)
                    ins_highlight_actor.GetProperty().SetLineWidth(3)
                    ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
                    self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                else:
                    pass
            else:
                continue
        
        self.GetRenderWindow().Render()

    def getShownBoundaryConditionsOfAssemblyRenderer(self) -> list:
        boundary_conditions_name_list = []
        
        for ins_instance_actor in self.__ins_attached_renderer.GetActors():
            actor_object_name = ins_instance_actor.GetObjectName()
            if actor_object_name == '':
                continue
            else:
                pass
            
            actor_type, actor_name = actor_object_name.split('>',1)
            if actor_type == 'bc':
                boundary_conditions_name_list.append(actor_name)
            else:
                continue
            
        return list(set(boundary_conditions_name_list))
    def addBoundaryConditionToAssemblyRenderer(self, in_ins_project_database:object, in_model_name:str, in_boundary_condition_name:str) -> None:
        for ins_view_prop in self.__ins_attached_renderer.GetViewProps():
            if ins_view_prop.GetObjectName() == 'GCSYS':
                axes_length_list = [axes_length*0.2 for axes_length in ins_view_prop.GetTotalLength()]
                break
            else:
                continue
        vector_size_scale = min(axes_length_list)*0.5
        
        condition_info_dict = in_ins_project_database.getBoundaryConditionInformation(in_model_name,in_boundary_condition_name)
        
        if condition_info_dict['type'] in ['displacement','concentrated force','moment']:
            group_associated_nodes_label_dict = in_ins_project_database.getAssemblyGroupLabels(in_model_name,condition_info_dict['group'][0],condition_info_dict['group'][1])
            nodes_cordinates_list = in_ins_project_database.getAssemblyNodesCooridnates(in_model_name,group_associated_nodes_label_dict)
            ins_group_points = vtk.vtkPoints()
            for node_coordinates_list in nodes_cordinates_list:
                ins_group_points.InsertNextPoint(node_coordinates_list)

            components_value_list = []
            components_value_string_list = condition_info_dict['parameters'][condition_info_dict['definition'][0]]
            for components_value_string in components_value_string_list[0:-1]:
                if components_value_string == 'N':
                    components_value_list.append(components_value_string)
                else:
                    components_value_list.append(float(components_value_string))
            model_dimension = in_ins_project_database.getModelDimension(in_model_name)
            if model_dimension == '2D':
                components_name_list = common.P4SBCInfo.BC_COMPONENTS_2D[condition_info_dict['type']]
            elif model_dimension == '3D':
                components_name_list = common.P4SBCInfo.BC_COMPONENTS_3D[condition_info_dict['type']]
            else:
                pass
            
            reference_assembly_coordinate_system_info_dict = in_ins_project_database.getAssemblyCoordinateSystemInfo(in_model_name,condition_info_dict['csys'])
            ins_reference_coordinate_system_transformer = vtk.vtkTransform()
            ins_reference_coordinate_system_transformer.Translate(reference_assembly_coordinate_system_info_dict['origin'])
            ins_reference_coordinate_system_transformer.RotateWXYZ(*reference_assembly_coordinate_system_info_dict['orientation'])
            if reference_assembly_coordinate_system_info_dict['type'] == 1:
                for component_name,component_value in zip(components_name_list,components_value_list):
                    if component_value == 'N':
                        continue
                    else:
                        pass
                    
                    component_direction_vector_array = vtk.vtkDoubleArray()
                    component_direction_vector_array.SetName(component_name)
                    component_direction_vector_array.SetNumberOfComponents(3)
                    component_direction_vector_array.SetNumberOfTuples(ins_group_points.GetNumberOfPoints())
                    
                    ins_component_poly_data = vtk.vtkPolyData()
                    ins_component_poly_data.SetPoints(ins_group_points)
                    ins_component_points_data = ins_component_poly_data.GetPointData()
                    
                    if component_name in ['U1','UR1','F1','M1']:
                        if component_value > 0.0:
                            point_vector = ins_reference_coordinate_system_transformer.TransformVector([1.0,0.0,0.0])
                        elif component_value == 0.0:
                            point_vector = ins_reference_coordinate_system_transformer.TransformVector([-1.0,0.0,0.0])
                        else:
                            point_vector = ins_reference_coordinate_system_transformer.TransformVector([-1.0,0.0,0.0])
                    elif component_name in ['U2','UR2','F2','M2']:
                        if component_value > 0.0:
                            point_vector = ins_reference_coordinate_system_transformer.TransformVector([0.0,1.0,0.0])
                        elif component_value == 0.0:
                            point_vector = ins_reference_coordinate_system_transformer.TransformVector([0.0,-1.0,0.0])
                        else:
                            point_vector = ins_reference_coordinate_system_transformer.TransformVector([0.0,-1.0,0.0])
                    elif component_name in ['U3','UR3','F3','M3']:
                        if component_value > 0.0:
                            point_vector = ins_reference_coordinate_system_transformer.TransformVector([0.0,0.0,1.0])
                        elif component_value == 0.0:
                            point_vector = ins_reference_coordinate_system_transformer.TransformVector([0.0,0.0,-1.0])
                        else:
                            point_vector = ins_reference_coordinate_system_transformer.TransformVector([0.0,0.0,-1.0])
                    else:
                        pass
                    
                    ins_arrow_geometry_source = vtk.vtkArrowSource()
                    if component_value == 0.0:
                        ins_arrow_geometry_source.SetTipLength(1)
                        if component_name in ['UR1','UR2','UR3','M1','M2','M3']:
                            ins_arrow_geometry_source.SetTipRadius(0.6)
                        else:
                            ins_arrow_geometry_source.SetTipRadius(0.4)
                        ins_arrow_geometry_source.InvertOn()
                    else:
                        pass
                        
                    component_direction_vector_array.FillComponent(0,point_vector[0])
                    component_direction_vector_array.FillComponent(1,point_vector[1])
                    component_direction_vector_array.FillComponent(2,point_vector[2])
                    ins_component_points_data.AddArray(component_direction_vector_array)
                    ins_component_points_data.SetVectors(component_direction_vector_array)
                    
                    ins_component_glyph_3D = vtk.vtkGlyph3D()
                    ins_component_glyph_3D.SetSourceConnection(ins_arrow_geometry_source.GetOutputPort())
                    ins_component_glyph_3D.SetInputData(ins_component_poly_data)
                    if component_value == 0.0:
                        ins_component_glyph_3D.SetScaleFactor(vector_size_scale*0.3)
                    else:
                        ins_component_glyph_3D.SetScaleFactor(vector_size_scale)
                    
                    ins_component_actor_mapper = vtk.vtkPolyDataMapper()
                    ins_component_actor_mapper.SetInputConnection(ins_component_glyph_3D.GetOutputPort())
                    
                    ins_component_actor = vtk.vtkActor()
                    ins_component_actor.SetObjectName('bc>'+in_boundary_condition_name)
                    ins_component_actor.SetMapper(ins_component_actor_mapper)
                    if component_name in ['UR1','UR2','UR3','M1','M2','M3']:
                        ins_component_actor.GetProperty().SetRepresentationToWireframe()
                    else:
                        pass
                    if condition_info_dict['type'] == 'displacement':
                        ins_component_actor.GetProperty().SetColor(0,1,0)
                    elif condition_info_dict['type'] in ['concentrated force','moment']:
                        ins_component_actor.GetProperty().SetColor(1,0,0)
                    else:
                        pass
                    self.__ins_attached_renderer.AddActor(ins_component_actor)
            elif reference_assembly_coordinate_system_info_dict['type'] == 2:
                pass
            elif reference_assembly_coordinate_system_info_dict['type'] == 3:
                pass
            else:
                pass
        else:
            pass
        
        self.GetRenderWindow().Render()
    def removeBoundaryConditionToAssemblyRenderer(self, in_boundary_condition_name:str) -> None:
        for ins_actor in self.__ins_attached_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'bc>'+in_boundary_condition_name:
                self.__ins_attached_renderer.RemoveActor(ins_actor)
                del ins_actor
            else:
                continue
        
        self.GetRenderWindow().Render()


class P4SResultVisualWindow(QtWidgets.QMdiSubWindow):
    def __init__(self,in_parent:object,in_result_full_name:str,in_ins_database_pointer:object) -> None:
        super().__init__(parent=in_parent)
        self.setObjectName(in_result_full_name)

        self.setWindowTitle(f'Display Window From Result: {in_result_full_name}')
        self.setWindowIcon(QtGui.QPixmap(":/image/images/ManageViewport.png"))
        self.resize(500,500)
        self.showMaximized()
        self.actions()[-1].setShortcut("")
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.setSystemMenu(None)
        
        ins_result_vtk_interactor = _ResultVisualizationInteractor(self,in_ins_database_pointer)
        self.setWidget(ins_result_vtk_interactor)
        ins_result_vtk_interactor.Start()

    def close(self,in_enable_hide:bool=True):
        if in_enable_hide:
            self.hide()
        else:
            return super().close()

    def finalizeInteractor(self) -> None:
        self.widget().Finalize()

    def getSelectionModeFromViewport(self) -> str:
        return self.widget().getInteractorSelectionMode()
    def getSelectionFromViewport(self) -> dict:
        return self.widget().getInteractorSelection()
    def setSelectionMode(self, in_mode:str) -> None:
        self.widget().setInteractorSelectionMode(in_mode)
    def setSelectionMethod(self, in_method:str) -> None:
        self.widget().setInteractorSelectionMethod(in_method)
    
    def setViewportView(self, in_view_orientation:str) -> None:
        self.widget().setInteractorViewOrientation(in_view_orientation)
    
    def setViewportRenderStyle(self, in_style:str) -> None:
        self.widget().setInteractorRenderStyle(in_style)
    
    def getViewportActorsColor(self) -> dict:
        return self.widget().getRendererIncludeActorsColor()
    def setViewportActorsColor(self,in_actors_color_dict:dict) -> None:
        self.widget().setInteractorRendererIncludeAcotrsColor(in_actors_color_dict)
    
    def getViewportActorsOpacity(self) -> dict:
        return self.widget().getRendererIncludeActorsOpacity()
    def setViewportActorsOpacity(self,in_actors_opacity_dict:dict) -> None:
        self.widget().setInteractorRendererIncludeAcotrsOpacity(in_actors_opacity_dict)
    
    def getViewportActorsVisibility(self) -> dict:
        return self.widget().getRendererIncludeActorsVisibility()
    def setViewportActorsVisibiolity(self,in_actors_visbility_dict:dict) -> dict:
        return self.widget().setRendererIncludeActorsVisibility(in_actors_visbility_dict)

    def changeVariableOfViewport(self, in_variable_name:str) -> None:
        self.widget().changeVariableOfCountorRenderer(in_variable_name)
    def changeVariableComponent(self, in_step_name:str, in_frame_name:str, in_componetn_name:str) -> None:
        self.widget().changeVariableComponentOfCountorRenderer(in_step_name, in_frame_name, in_componetn_name)
    
    def changeFrameOfViewport(self, in_variable_name:str, in_component_name:str, in_step_name:str, in_frame_name:str) -> None:
        self.widget().changeFrameOfCountorRenderer(in_variable_name, in_component_name, in_step_name,in_frame_name)
    
    def changeDeformationStateOfViewport(self, in_deformation_infomation:list=[]) -> None:
        self.widget().changeDeformationStateOfCountorRenderer(in_deformation_infomation)
        
    def changeColorMapOfViewport(self, in_map_name:str) -> None:
        self.widget().changeColorMapOfCountorRenderer(in_map_name)
    def changeColorNumberOfViewport(self, in_map_name:str, in_color_number:int) -> None:
        self.widget().changeColorNumberOfCountorRenderer(in_map_name, in_color_number)

    def getDisplayTypeOfViewport(self) -> str:
        return self.widget().getDisplayTypeOfRenderWindow()
    def switchDisplayTypeOfViewport(self, in_type:str) -> None:
        self.widget().switchDisplayTypeOfRenderWindow(in_type)
    
    def exportContourDataToCSVOfViewport(self, in_csv_file_full_name:str) -> None:
        self.widget().exportContourDataToCSVOfContourRenderer(in_csv_file_full_name)
    def exportContourDataToImageOfViewport(self, in_work_path:str) -> None:
        self.widget().exportContourDataToImageOfContourRenderer(in_work_path)
    
    def createGraphOfViewport(self, in_graph_infomation:dict) -> None:
        self.widget().createGraphOfGraphRenderer(in_graph_infomation)
    def switchGraphOfViewport(self, in_graph_name:str) -> None:
        self.widget().switchGraphOfGraphRenderer(in_graph_name)
    def renameGraphOfViewport(self, in_old_name:str, in_new_name:str) -> None:
        self.widget().renameGraphOfGraphRenderer(in_old_name, in_new_name)
    def exportGraphDataToCSVOfViewport(self, in_graph_name:str, in_csv_file_full_name:str) -> None:
        self.widget().exportGraphDataToCSVOfGraphRenderer(in_graph_name, in_csv_file_full_name)
    def exportGraphToImageOfViewport(self, in_graph_name:str, in_work_path:str) -> None:
        self.widget().exportGraphToImageOfGraphRenderer(in_graph_name, in_work_path)
    def deleteGraphOfViewport(self, in_graph_name:str) -> None:
        self.widget().deleteGraphOfGraphRenderer(in_graph_name)

    def getDatabaseTypeOfViewport(self) -> str:
        return self.widget().getDisplayDatabaseType()
    def getTopologyDensityThresholdOfViewport(self) -> float:
        return self.widget().getTopologyDensityThresholdOfCountorRenderer()
    def binarizeTopolotyDensityOfViewport(self, in_threshold:float, in_step_name:str, in_frame_name:str) -> None:
        return self.widget().binarizeTopolotyDensityOfCountorRenderer(in_threshold,in_step_name,in_frame_name)

class _ResultVisualizationInteractor(QVTKRenderWindowInteractor.QVTKRenderWindowInteractor):
    def __init__(self, in_parent, in_ins_database_pointer:object):
        super().__init__(parent=in_parent)
        
        self.__ins_database_pointer = in_ins_database_pointer

        self.__selection_mode = None
        self.__selection_method = 'single'
        self.__point_picker = vtk.vtkPointPicker()
        self.__point_picker.SetTolerance(0.005)
        self.__cell_picker = vtk.vtkCellPicker()
        self.__cell_picker.SetTolerance(0.005)
        self.__area_picker = vtk.vtkAreaPicker()
        self.__prop_picker = self.GetPicker()
        self.__picked_labels_dict = {}

        ins_default_interactor_style = self.GetInteractorStyle()
        self.SetInteractorStyle(vtk.vtkInteractorStyleRubberBandPick())
        del ins_default_interactor_style
        self.__is_rubber_selection = False
        
        self.__ins_attached_marker = None
        self.__ins_attached_renderer= None
        self.__ins_contour_renderer = None
        self.__initializeContourRenderer()
        
        self.__ins_graph_renderer = None
        self.__initializeGraphRenderer()
        
        self.__topology_density_threshold = 0.01
    
    def __initializeContourRenderer(self) -> None:
        ins_render_window = self.GetRenderWindow()
        ins_render_window.SetNumberOfLayers(2)
        
        self.__ins_attached_renderer = vtk.vtkRenderer()
        self.__ins_attached_renderer.SetLayer(1)
        ins_render_window.AddRenderer(self.__ins_attached_renderer)
        
        self.__ins_contour_renderer = vtk.vtkRenderer()
        self.__ins_contour_renderer.SetLayer(0)
        ins_render_window.AddRenderer(self.__ins_contour_renderer)
        # region
        self.__ins_contour_renderer.SetBackground(208/255,223/255,230/255)
        self.__ins_contour_renderer.GetActiveCamera().ParallelProjectionOn()
        
        ins_renderer_tip = vtk.vtkCornerAnnotation()
        ins_renderer_tip.SetText(1, 'Results')
        ins_renderer_tip.SetLinearFontScaleFactor(6)
        ins_renderer_tip.GetTextProperty().SetColor(0, 0, 0)
        self.__ins_contour_renderer.AddViewProp(ins_renderer_tip)
        
        ins_axes_actor = vtk.vtkAxesActor()
        ins_axes_actor.SetShaftTypeToCylinder()
        ins_axes_actor.SetNormalizedLabelPosition(1.3,1.3,1.3)
        ins_axes_actor.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().BoldOn()
        ins_axes_actor.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().ShadowOff()
        ins_axes_actor.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(0.0,0.0,0.0)
        ins_axes_actor.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().BoldOn()
        ins_axes_actor.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().ShadowOff()
        ins_axes_actor.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(0.0,0.0,0.0)
        ins_axes_actor.GetZAxisCaptionActor2D().GetTextActor().GetTextProperty().BoldOn()
        ins_axes_actor.GetZAxisCaptionActor2D().GetTextActor().GetTextProperty().ShadowOff()
        ins_axes_actor.GetZAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(0.0,0.0,0.0)
        self.__ins_attached_marker = vtk.vtkOrientationMarkerWidget()
        self.__ins_attached_marker.SetOrientationMarker(ins_axes_actor)
        self.__ins_attached_marker.SetInteractor(ins_render_window.GetInteractor())
        self.__ins_attached_marker.SetViewport(0.0, 0.0, 0.2, 0.2)
        self.__ins_attached_marker.EnabledOn()
        self.__ins_attached_marker.InteractiveOff()
        # endregion
        
        ins_scalars_bar = vtk.vtkScalarBarActor()
        # region
        ins_scalars_bar.SetObjectName('scalar-bar')
        ins_scalars_bar.SetNumberOfLabels(13)
        ins_scalars_bar.GetPositionCoordinate().SetCoordinateSystemToDisplay()
        ins_scalars_bar.GetPosition2Coordinate().SetCoordinateSystemToDisplay()
        ins_scalars_bar.GetPositionCoordinate().SetValue(10,200)
        ins_scalars_bar.GetPosition2Coordinate().SetValue(150,500)
        ins_scalars_bar.GetTitleTextProperty().SetColor(0.0,0.0,0.0)
        ins_scalars_bar.GetTitleTextProperty().SetFontFamilyToTimes()
        ins_scalars_bar.GetTitleTextProperty().BoldOff()
        ins_scalars_bar.GetTitleTextProperty().ItalicOff()
        ins_scalars_bar.SetVerticalTitleSeparation(10)
        ins_scalars_bar.DrawFrameOn()
        ins_scalars_bar.GetFrameProperty().SetColor(0.0,0.0,0.0)
        ins_scalars_bar.GetFrameProperty().SetLineWidth(2)
        ins_scalars_bar.SetTextPad(2)
        ins_scalars_bar.SetBarRatio(0.3)
        ins_scalars_bar.GetLabelTextProperty().SetFontFamilyToTimes()
        ins_scalars_bar.GetLabelTextProperty().SetColor(0.0,0.0,0.0)
        ins_scalars_bar.GetLabelTextProperty().BoldOn()
        ins_scalars_bar.SetLabelFormat("%.4e")
        
        ins_scalar_bar_lookup_table = vtk.vtkLookupTable()
        ins_scalar_bar_lookup_table.SetNumberOfTableValues(12)
        ins_color_map = colormaps.get_cmap('rainbow')
        ins_color_norm = colors.Normalize(0,11)
        for color_index in range(12):
            ins_scalar_bar_lookup_table.SetTableValue(color_index,*ins_color_map(ins_color_norm(color_index)))
        ins_scalar_bar_lookup_table.Build()
        ins_scalars_bar.SetLookupTable(ins_scalar_bar_lookup_table)
        # endregion
        self.__ins_contour_renderer.AddActor2D(ins_scalars_bar)
        ins_scalars_bar.SetVisibility(0)
        
        ins_assembly_includ_nodes_set = self.__ins_database_pointer['Mesh']['nodes']
        ins_assembly_includ_elements_set = self.__ins_database_pointer['Mesh']['elements']
        ins_assembly_includ_elements_geometry_set = self.__ins_database_pointer['Mesh']['geometry']
        cell_type_from_geometry = {1:3, 6:21, 2:5, 7:22, 3:9, 8:23, 4:10, 9:24, 5:12, 10:25}
        for instance_name,instance_location_array in self.__ins_database_pointer['Mesh']['Instances'].items():
            ins_instance_points = vtk.vtkPoints()
            ins_instance_points.SetNumberOfPoints(instance_location_array[1]-instance_location_array[0]+1)
            for node_index,node_coordinates in enumerate(ins_assembly_includ_nodes_set[instance_location_array[0]-1:instance_location_array[1]]):
                ins_instance_points.SetPoint(node_index,node_coordinates)
            
            ins_instance_mesh = vtk.vtkUnstructuredGrid()
            ins_instance_mesh.SetPoints(ins_instance_points)
            for element_geometry_type_number,element_include_nodes_label in zip(ins_assembly_includ_elements_geometry_set[instance_location_array[2]-1:instance_location_array[3]],ins_assembly_includ_elements_set[instance_location_array[2]-1:instance_location_array[3]]):
                ins_instance_mesh.InsertNextCell(cell_type_from_geometry[element_geometry_type_number],len(element_include_nodes_label),element_include_nodes_label-1)
            
            ins_instance_mapper = vtk.vtkDataSetMapper()
            ins_instance_mapper.SetInputData(ins_instance_mesh)
            ins_instance_mapper.UseLookupTableScalarRangeOn()
            ins_instance_mapper.SetLookupTable(ins_scalar_bar_lookup_table)
            ins_instance_mapper.InterpolateScalarsBeforeMappingOn()
            
            ins_instance_actor = vtk.vtkActor()
            ins_instance_actor.SetObjectName('object>'+instance_name)
            ins_instance_actor.SetMapper(ins_instance_mapper)
            ins_instance_actor.PickableOn()
            self.__ins_contour_renderer.AddActor(ins_instance_actor)
        
        self.__ins_attached_renderer.SetActiveCamera(self.__ins_contour_renderer.GetActiveCamera())
        self.__ins_contour_renderer.ResetCamera()
        
        ins_render_window.Render()
    def __initializeGraphRenderer(self) -> None:
        ins_context_scene = vtk.vtkContextScene()

        ins_context_actor = vtk.vtkContextActor()
        ins_context_actor.SetObjectName('context-actor')
        ins_context_actor.SetScene(ins_context_scene)

        self.__ins_graph_renderer = vtk.vtkRenderer()
        self.__ins_graph_renderer.SetBackground(1.0,1.0,1.0)
        self.__ins_graph_renderer.AddActor(ins_context_actor)
    
    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.MiddleButton:
            if self.GetControlKey() == 1:
                self.GetInteractorStyle().StartPan()
            else:
                self.GetInteractorStyle().StartRotate()

            return None
        elif ev.button() == QtCore.Qt.RightButton:
            if self.GetControlKey() == 1:
                self.GetInteractorStyle().StartSpin()
            else:
                self.GetInteractorStyle().StartDolly()
            
            return None
        elif ev.button() == QtCore.Qt.LeftButton:
            if self.__selection_mode is None:
                return None
            elif self.__selection_method == 'area' and self.__is_rubber_selection:
                super().mousePressEvent(ev)
                return None
            else:
                pass
        else:
            return None
        
        ins_current_picker = self.GetPicker()
        ins_current_picker.Pick(self.GetEventPosition()[0],self.GetEventPosition()[1],0.0,self.__ins_contour_renderer)
        ins_picked_actor = ins_current_picker.GetActor()
    
        if self.GetControlKey() == 1 and self.GetShiftKey() == 0:
            if ins_picked_actor is None:
                return None
            else:
                pass
            
            picked_actor_object_name = ins_picked_actor.GetObjectName()
            picked_actor_name = picked_actor_object_name.split('>',1)[1]
            highlight_actor_object_name = 'highlight>'+ picked_actor_name
            
            ins_highlight_actor = None
            for ins_acotr in  self.__ins_attached_renderer.GetActors():
                if ins_acotr.GetObjectName() == highlight_actor_object_name:
                    ins_highlight_actor = ins_acotr
                    break
                else:
                    continue
            
            if self.__selection_method == 'single':
                if self.__selection_mode == 'node':
                    picked_point_id = ins_current_picker.GetPointId()
                    
                    if ins_highlight_actor is None:
                        self.__picked_labels_dict[picked_actor_name] = [picked_point_id+1]
                        
                        ins_highlight_actor_points = vtk.vtkPoints()
                        picked_point_coordinates = ins_picked_actor.GetMapper().GetInput().GetPoint(picked_point_id)
                        ins_highlight_actor_points.InsertNextPoint(picked_point_coordinates)
                        ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                        ins_highlight_actor_grid.SetPoints(ins_highlight_actor_points)
                        ins_highlight_actor_grid.InsertNextCell(1,1,[0])
                        ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                        ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                        ins_highlight_actor = vtk.vtkActor()
                        ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                        ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                        ins_highlight_actor.GetProperty().SetColor(1,0,0)
                        ins_highlight_actor.GetProperty().SetPointSize(10)
                        ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
                        self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                    else:
                        if picked_point_id+1 in self.__picked_labels_dict[picked_actor_name]:
                            return None
                        else:
                            self.__picked_labels_dict[picked_actor_name].append(picked_point_id+1)

                        ins_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                        
                        ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                        picked_point_coordinates = ins_picked_actor.GetMapper().GetInput().GetPoint(picked_point_id)
                        point_id = ins_highlight_actor_points.InsertNextPoint(picked_point_coordinates)
                        ins_highlight_actor_grid.InsertNextCell(1,1,[point_id])
                        
                        ins_highlight_actor_grid.Modified()
                elif self.__selection_mode == 'element':
                    picked_cell_id = ins_current_picker.GetCellId()
                    
                    if ins_highlight_actor is None:
                        self.__picked_labels_dict[picked_actor_name] = [picked_cell_id+1]
                        
                        ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                    
                        ins_extract_cells = vtk.vtkExtractCells()
                        ins_extract_cells.SetInputData(ins_picked_actor_grid)
                        ins_extract_cells.AddCellIds([picked_cell_id],1)
                        ins_extract_cells.Update()
                        
                        ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
                        ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
                        ins_extract_cells.SetInputData(None)
                        del ins_extract_cells
                    
                        ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                        ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                        ins_highlight_actor = vtk.vtkActor()
                        ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                        ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                        ins_highlight_actor.GetProperty().SetColor(1,0,0)
                        ins_highlight_actor.GetProperty().SetLineWidth(3)
                        ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
                        self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                    else:
                        if picked_cell_id+1 in self.__picked_labels_dict[picked_actor_name]:
                            return None
                        else:
                            self.__picked_labels_dict[picked_actor_name].append(picked_cell_id+1)

                        ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()

                        ins_extract_cells = vtk.vtkExtractCells()
                        ins_extract_cells.SetInputData(ins_picked_actor_grid)
                        ins_extract_cells.AddCellIds([cell_label-1 for cell_label in self.__picked_labels_dict[picked_actor_name]],len(self.__picked_labels_dict[picked_actor_name]))
                        ins_extract_cells.Update()
                        
                        ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
                        ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
                        ins_extract_cells.SetInputData(None)
                        del ins_extract_cells
                        
                        ins_old_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                        ins_highlight_actor.GetMapper().SetInputData(ins_highlight_actor_grid)
                        
                        ins_old_highlight_actor_points = ins_old_highlight_actor_grid.GetPoints()
                        ins_old_highlight_actor_grid.SetPoints(None)
                        ins_old_highlight_actor_grid.Initialize()
                        del ins_old_highlight_actor_grid
                        ins_old_highlight_actor_points.Initialize()
                        del ins_old_highlight_actor_points
                else:
                    pass
            elif self.__selection_method == 'edge':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'face':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'entity':
                ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                
                if ins_highlight_actor is None:
                    if self.__selection_mode == 'node':
                        self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfPoints()+1,1))
                    elif self.__selection_mode == 'element':
                        self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfCells()+1,1))
                    else:
                        pass
                    
                    ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.DeepCopy(ins_picked_actor_grid)
                    ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                    ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                    ins_highlight_actor = vtk.vtkActor()
                    ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                    ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                    ins_highlight_actor.GetProperty().SetColor(1,0,0)
                    if self.__selection_mode == 'node':
                        ins_highlight_actor.GetProperty().SetPointSize(10)
                        ins_highlight_actor.GetProperty().SetRepresentationToPoints()
                        ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
                    elif self.__selection_mode == 'element':
                        ins_highlight_actor.GetProperty().SetLineWidth(3)
                        ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
                    self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                elif ins_picked_actor_grid.GetNumberOfCells() > len(self.__picked_labels_dict[picked_actor_name]):
                    if self.__selection_mode == 'node':
                        self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfPoints()+1,1))
                    elif self.__selection_mode == 'element':
                        self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfCells()+1,1))
                    else:
                        pass
                    
                    ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.DeepCopy(ins_picked_actor_grid)
                    
                    ins_old_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                    ins_highlight_actor.GetMapper().SetInputData(ins_highlight_actor_grid)
                    
                    ins_old_highlight_actor_points = ins_old_highlight_actor_grid.GetPoints()
                    ins_old_highlight_actor_grid.SetPoints(None)
                    ins_old_highlight_actor_grid.Initialize()
                    del ins_old_highlight_actor_grid
                    ins_old_highlight_actor_points.Initialize()
                    del ins_old_highlight_actor_points
                else:
                    pass
            else:
                return None
            
            self.GetRenderWindow().Render()
        elif self.GetControlKey() == 0 and self.GetShiftKey() == 1:
            if ins_picked_actor is None:
                return None
            else:
                pass
            
            picked_actor_object_name = ins_picked_actor.GetObjectName()
            picked_actor_name = picked_actor_object_name.split('>',1)[1]
            highlight_actor_object_name = 'highlight>'+ picked_actor_name
            
            if picked_actor_name in self.__picked_labels_dict:
                pass
            else:
                return None
            
            if self.__selection_method == 'single':
                if self.__selection_mode == 'node':
                    picked_point_id = ins_current_picker.GetPointId()
                    
                    if picked_point_id+1 in self.__picked_labels_dict[picked_actor_name]:
                        self.__picked_labels_dict[picked_actor_name].remove(picked_point_id+1)
                        
                        for ins_acotr in  self.__ins_attached_renderer.GetActors():
                            if ins_acotr.GetObjectName() == highlight_actor_object_name:
                                ins_highlight_actor = ins_acotr
                                break
                            else:
                                continue
            
                        if self.__picked_labels_dict[picked_actor_name] == []:
                            self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
                
                            ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
                            ins_highlight_actor.SetMapper(None)
                            del ins_highlight_actor
                            
                            ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
                            ins_highlight_actor_mapper.SetInputData(None)
                            ins_highlight_actor_mapper.RemoveAllInputs()
                            del ins_highlight_actor_mapper
                    
                            ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                            ins_highlight_actor_grid.SetPoints(None)
                            ins_highlight_actor_grid.Initialize()
                            del ins_highlight_actor_grid
                            
                            ins_highlight_actor_points.Initialize()
                            del ins_highlight_actor_points
                            
                            self.__picked_labels_dict[picked_actor_name] = None
                            del self.__picked_labels_dict[picked_actor_name]
                        else:
                            ins_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                            ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                            ins_highlight_actor_grid.Reset()
                            ins_highlight_actor_points.Reset()
                            
                            ins_picked_actor_points = ins_picked_actor.GetMapper().GetInput().GetPoints()
                            for node_lable in self.__picked_labels_dict[picked_actor_name]:
                                point_id = ins_highlight_actor_points.InsertNextPoint(ins_picked_actor_points.GetPoint(node_lable-1))
                                ins_highlight_actor_grid.InsertNextCell(1,1,[point_id])
                            
                            ins_highlight_actor_grid.Modified()
                    else:
                        return None
                elif self.__selection_mode == 'element':
                    picked_cell_id = ins_current_picker.GetCellId()
                    
                    if picked_cell_id+1 in self.__picked_labels_dict[picked_actor_name]:
                        self.__picked_labels_dict[picked_actor_name].remove(picked_cell_id+1)
                        
                        for ins_acotr in  self.__ins_attached_renderer.GetActors():
                            if ins_acotr.GetObjectName() == highlight_actor_object_name:
                                ins_highlight_actor = ins_acotr
                                break
                            else:
                                continue
                        
                        if self.__picked_labels_dict[picked_actor_name] == []:
                            self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
                            
                            ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
                            ins_highlight_actor.SetMapper(None)
                            del ins_highlight_actor
                            
                            ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
                            ins_highlight_actor_mapper.SetInputData(None)
                            ins_highlight_actor_mapper.RemoveAllInputs()
                            del ins_highlight_actor_mapper
                    
                            ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                            ins_highlight_actor_grid.SetPoints(None)
                            ins_highlight_actor_grid.Initialize()
                            del ins_highlight_actor_grid
                            
                            ins_highlight_actor_points.Initialize()
                            del ins_highlight_actor_points
                            
                            self.__picked_labels_dict[picked_actor_name] = None
                            del self.__picked_labels_dict[picked_actor_name]
                        else:
                            ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                            
                            ins_extract_cells = vtk.vtkExtractCells()
                            ins_extract_cells.SetInputData(ins_picked_actor_grid)
                            ins_extract_cells.AddCellIds([cell_label-1 for cell_label in self.__picked_labels_dict[picked_actor_name]],len(self.__picked_labels_dict[picked_actor_name]))
                            ins_extract_cells.Update()
                            
                            ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
                            ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
                            ins_extract_cells.SetInputData(None)
                            del ins_extract_cells
                            
                            ins_old_highlight_actor_grid = ins_highlight_actor.GetMapper().GetInput()
                            ins_highlight_actor.GetMapper().SetInputData(ins_highlight_actor_grid)
                            
                            ins_old_highlight_actor_points = ins_old_highlight_actor_grid.GetPoints()
                            ins_old_highlight_actor_grid.SetPoints(None)
                            ins_old_highlight_actor_grid.Initialize()
                            del ins_old_highlight_actor_grid
                            ins_old_highlight_actor_points.Initialize()
                            del ins_old_highlight_actor_points
                    else:
                        return None
                else:
                    pass
            elif self.__selection_method == 'edge':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'face':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'entity':
                self.__picked_labels_dict[picked_actor_name] = None
                del self.__picked_labels_dict[picked_actor_name]
                
                for ins_acotr in  self.__ins_attached_renderer.GetActors():
                    if ins_acotr.GetObjectName() == highlight_actor_object_name:
                        ins_highlight_actor = ins_acotr
                        break
                    else:
                        continue
                
                self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
                
                ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
                ins_highlight_actor.SetMapper(None)
                del ins_highlight_actor
                
                ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
                ins_highlight_actor_mapper.SetInputData(None)
                ins_highlight_actor_mapper.RemoveAllInputs()
                del ins_highlight_actor_mapper
        
                ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                ins_highlight_actor_grid.SetPoints(None)
                ins_highlight_actor_grid.Initialize()
                del ins_highlight_actor_grid
                
                ins_highlight_actor_points.Initialize()
                del ins_highlight_actor_points
            else:
                return None
            
            self.GetRenderWindow().Render()
        else:
            highlight_actors_list = []
            for ins_acotr in  self.__ins_attached_renderer.GetActors():
                actor_object_name = ins_acotr.GetObjectName()
                if actor_object_name == '':
                    continue
                else:
                    pass
                if actor_object_name.split('>',1)[0] == 'highlight':
                    highlight_actors_list.append(ins_acotr)
                else:
                    continue
            while len(highlight_actors_list) > 0:
                ins_highlight_actor = highlight_actors_list.pop()
                highlight_actor_name = ins_highlight_actor.GetObjectName().split('>',1)[1]
                self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
                
                ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
                ins_highlight_actor.SetMapper(None)
                del ins_highlight_actor
                
                ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
                ins_highlight_actor_mapper.SetInputData(None)
                ins_highlight_actor_mapper.RemoveAllInputs()
                del ins_highlight_actor_mapper
        
                ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
                ins_highlight_actor_grid.SetPoints(None)
                ins_highlight_actor_grid.Initialize()
                del ins_highlight_actor_grid
                
                ins_highlight_actor_points.Initialize()
                del ins_highlight_actor_points
                
                self.__picked_labels_dict[highlight_actor_name] = None
                del self.__picked_labels_dict[highlight_actor_name]
            self.GetRenderWindow().Render()
            
            if ins_picked_actor is None:
                return None
            else:
                pass
            
            picked_actor_object_name = ins_picked_actor.GetObjectName()
            picked_actor_name = picked_actor_object_name.split('>',1)[1]
            highlight_actor_object_name = 'highlight>'+ picked_actor_name
            
            if self.__selection_method == 'single':
                if self.__selection_mode == 'node':
                    picked_point_id = ins_current_picker.GetPointId()
                    
                    self.__picked_labels_dict = {}
                    self.__picked_labels_dict[picked_actor_name] = [picked_point_id+1]
                    
                    ins_highlight_actor_points = vtk.vtkPoints()
                    picked_point_coordinates = ins_picked_actor.GetMapper().GetInput().GetPoint(picked_point_id)
                    ins_highlight_actor_points.InsertNextPoint(picked_point_coordinates)
                    ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.SetPoints(ins_highlight_actor_points)
                    ins_highlight_actor_grid.InsertNextCell(1,1,[0])
                    ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                    ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                    ins_highlight_actor = vtk.vtkActor()
                    ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                    ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                    ins_highlight_actor.GetProperty().SetColor(1,0,0)
                    ins_highlight_actor.GetProperty().SetPointSize(10)
                    ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
                    self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                elif self.__selection_mode == 'element':
                    picked_cell_id = ins_current_picker.GetCellId()
                    
                    self.__picked_labels_dict = {}
                    self.__picked_labels_dict[picked_actor_name] = [picked_cell_id+1]

                    ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                    
                    ins_extract_cells = vtk.vtkExtractCells()
                    ins_extract_cells.SetInputData(ins_picked_actor_grid)
                    ins_extract_cells.AddCellIds([picked_cell_id],1)
                    ins_extract_cells.Update()
                    
                    ins_highlight_actor_grid =  vtk.vtkUnstructuredGrid()
                    ins_highlight_actor_grid.DeepCopy(ins_extract_cells.GetOutput())
                    ins_extract_cells.SetInputData(None)
                    del ins_extract_cells
                    
                    ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                    ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                    ins_highlight_actor = vtk.vtkActor()
                    ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                    ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                    ins_highlight_actor.GetProperty().SetColor(1,0,0)
                    ins_highlight_actor.GetProperty().SetLineWidth(3)
                    ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
                    self.__ins_attached_renderer.AddActor(ins_highlight_actor)
                else:
                    pass
            elif self.__selection_method == 'edge':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'face':
                print("Coming soon!")
                return None
            elif self.__selection_method == 'entity':
                ins_picked_actor_grid = ins_picked_actor.GetMapper().GetInput()
                
                self.__picked_labels_dict = {}
                if self.__selection_mode == 'node':
                    self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfPoints()+1,1))
                elif self.__selection_mode == 'element':
                    self.__picked_labels_dict[picked_actor_name] = list(range(1,ins_picked_actor_grid.GetNumberOfCells()+1,1))
                else:
                    pass
                
                ins_highlight_actor_grid = vtk.vtkUnstructuredGrid()
                ins_highlight_actor_grid.DeepCopy(ins_picked_actor_grid)
                ins_highlight_actor_mapper = vtk.vtkDataSetMapper()
                ins_highlight_actor_mapper.SetInputData(ins_highlight_actor_grid)
                ins_highlight_actor = vtk.vtkActor()
                ins_highlight_actor.SetObjectName(highlight_actor_object_name)
                ins_highlight_actor.SetMapper(ins_highlight_actor_mapper)
                ins_highlight_actor.GetProperty().SetColor(1,0,0)
                if self.__selection_mode == 'node':
                    ins_highlight_actor.GetProperty().SetPointSize(10)
                    ins_highlight_actor.GetProperty().SetRepresentationToPoints()
                    ins_highlight_actor.GetProperty().SetRenderPointsAsSpheres(True)
                elif self.__selection_mode == 'element':
                    ins_highlight_actor.GetProperty().SetLineWidth(3)
                    ins_highlight_actor.GetProperty().SetRepresentationToWireframe()
                else:
                    pass
                
                self.__ins_attached_renderer.AddActor(ins_highlight_actor)
            else:
                pass
            
            self.GetRenderWindow().Render()
    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.MiddleButton:
            self.GetInteractorStyle().EndRotate()
            self.GetInteractorStyle().EndPan()
            
            return None
        elif ev.button() == QtCore.Qt.RightButton:
            self.GetInteractorStyle().EndSpin()
            self.GetInteractorStyle().EndDolly()
            
            return None
        elif ev.button() == QtCore.Qt.LeftButton:
            if self.__selection_mode is None:
                return None
            elif self.__selection_method == 'area' and self.__is_rubber_selection:
                super().mouseReleaseEvent(ev)
            else:
                return None
        else:
            return None  

        print("Coming soon!")
        return None
    
    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Control:
            self.SetControlKey(1)
        elif ev.key() == QtCore.Qt.Key_Shift:
            self.SetShiftKey(1)
        elif ev.key() == QtCore.Qt.Key_R:
            if self.__selection_mode is None:
                return None
            elif self.__selection_method == 'area':
                super().keyPressEvent(ev)
                
                if self.__is_rubber_selection:
                    self.__is_rubber_selection = False
                else:
                    self.__is_rubber_selection = True
            else:
                pass
        else:
            pass
    def keyReleaseEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Control:
            self.SetControlKey(0)
        elif ev.key() == QtCore.Qt.Key_Shift:
            self.SetShiftKey(0)
        else:
            pass
    
    def getInteractorSelectionMode(self) -> str:
        return self.__selection_mode
    def getInteractorSelection(self) -> dict:
        return self.__picked_labels_dict
    def setInteractorSelectionMode(self, in_mode:str) -> None:
        highlight_actors_list = []
        for ins_acotr in  self.__ins_attached_renderer.GetActors():
            actor_object_name = ins_acotr.GetObjectName()
            if actor_object_name == '':
                continue
            else:
                pass
            if actor_object_name.split('>',1)[0] == 'highlight':
                highlight_actors_list.append(ins_acotr)
            else:
                continue
        while len(highlight_actors_list) > 0:
            ins_highlight_actor = highlight_actors_list.pop()
            self.__ins_attached_renderer.RemoveActor(ins_highlight_actor)
            
            ins_highlight_actor_mapper = ins_highlight_actor.GetMapper()
            ins_highlight_actor.SetMapper(None)
            del ins_highlight_actor
            
            ins_highlight_actor_grid = ins_highlight_actor_mapper.GetInput()
            ins_highlight_actor_mapper.SetInputData(None)
            ins_highlight_actor_mapper.RemoveAllInputs()
            del ins_highlight_actor_mapper
    
            ins_highlight_actor_points = ins_highlight_actor_grid.GetPoints()
            ins_highlight_actor_grid.SetPoints(None)
            ins_highlight_actor_grid.Initialize()
            del ins_highlight_actor_grid
            
            ins_highlight_actor_points.Initialize()
            del ins_highlight_actor_points
        self.GetRenderWindow().Render()
        
        if self.__picked_labels_dict == {}:
            pass
        else:
            self.__picked_labels_dict = {}
        
        if in_mode == 'node':
            if self.__selection_mode == 'node':
                pass
            else:
                if self.__selection_method == 'single':
                    self.SetPicker(self.__point_picker)
                else: 
                    pass
        elif in_mode == 'element':
            if self.__selection_mode == 'element':
                pass
            else:
                self.SetPicker(self.__cell_picker)
        else:
            if in_mode is None and self.__is_rubber_selection:
                self.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress,QtCore.Qt.Key.Key_R,QtCore.Qt.KeyboardModifier.NoModifier))
            else:
                pass
            
            self.__selection_method = 'single'
        
        self.__selection_mode = in_mode
    def setInteractorSelectionMethod(self, in_mehtod:str) -> None:
        if self.__selection_mode == 'node':
            if in_mehtod == self.__selection_method:
                pass
            elif in_mehtod in ['single','edge','face']:
                self.SetPicker(self.__point_picker)
            elif in_mehtod == 'area':
                self.SetPicker(self.__area_picker)
            elif in_mehtod == 'entity':
                self.SetPicker(self.__prop_picker)
            else:
                pass    
        elif self.__selection_mode == 'element':
            if in_mehtod == self.__selection_method:
                pass
            elif in_mehtod in ['single','edge','face']:
                self.SetPicker(self.__cell_picker)
            elif in_mehtod == 'area':
                self.SetPicker(self.__area_picker)
            elif in_mehtod == 'entity':
                self.SetPicker(self.__prop_picker)
            else:
                pass 
        else:
            pass
        
        if self.__selection_method == 'area' and in_mehtod != 'area' and self.__is_rubber_selection:
            self.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.Type.KeyPress,QtCore.Qt.Key.Key_R,QtCore.Qt.KeyboardModifier.NoModifier))
        else:
            pass
        
        self.__selection_method = in_mehtod
    def setInteractorViewOrientation(self, in_view_orientation:str) -> None:
        ins_current_renderer_camera = self.__ins_contour_renderer.GetActiveCamera()
        ins_current_renderer_camera.SetFocalPoint(0,0,0)
        if in_view_orientation == 'front':
            ins_current_renderer_camera.SetPosition(0,0,10)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'back':
            ins_current_renderer_camera.SetPosition(0,0,-10)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'top':
            ins_current_renderer_camera.SetPosition(0,10,0)
            ins_current_renderer_camera.SetViewUp(0, 0, -1)
        elif in_view_orientation == 'bottom':
            ins_current_renderer_camera.SetPosition(0,-10,0)
            ins_current_renderer_camera.SetViewUp(0, 0, 1)
        elif in_view_orientation == 'left':
            ins_current_renderer_camera.SetPosition(-10,0,0)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'right':
            ins_current_renderer_camera.SetPosition(10,0,0)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'iso':
            ins_current_renderer_camera.SetPosition(10,10,10)
            ins_current_renderer_camera.SetViewUp(0, 1, 0)
        elif in_view_orientation == 'fit':
            pass
        else:
            return None

        self.__ins_contour_renderer.ResetCamera()
        ins_current_renderer_camera.ComputeViewPlaneNormal()
        self.GetRenderWindow().Render()
    
    def setInteractorRenderStyle(self, in_style:str) -> None:
        ins_render_window = self.GetRenderWindow()
        if in_style == 'normal':
            for ins_actor in self.__ins_contour_renderer.GetActors():
                if ins_actor.GetObjectName().split('>',1)[0] == 'object':
                    ins_actor.GetProperty().EdgeVisibilityOff()
                    ins_actor.GetProperty().SetRepresentationToSurface()
                else: continue
        elif in_style == 'wireframe':
            for ins_actor in self.__ins_contour_renderer.GetActors():
                if ins_actor.GetObjectName().split('>',1)[0] == 'object':
                    ins_actor.GetProperty().EdgeVisibilityOff()
                    ins_actor.GetProperty().SetRepresentationToWireframe()
                else: continue
        elif in_style == 'mesh':
            for ins_actor in self.__ins_contour_renderer.GetActors():
                if ins_actor.GetObjectName().split('>',1)[0] == 'object':
                    ins_actor.GetProperty().EdgeVisibilityOn()
                    ins_actor.GetProperty().SetRepresentationToSurface()
                else: continue
        else:
            return None
        ins_render_window.Render()
    
    def getRendererIncludeActorsColor(self) -> dict:
        actors_color_dict = {}
        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                actors_color_dict[actor_object_name_info_list[1]] = ins_actor.GetProperty().GetColor()
            else:
                continue
        return actors_color_dict
    def setInteractorRendererIncludeAcotrsColor(self, in_actors_color_dict:dict) -> None:
        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object' and actor_object_name_info_list[1] in in_actors_color_dict:
                ins_actor.GetProperty().SetColor(in_actors_color_dict[actor_object_name_info_list[1]])
            else:
                continue
        self.GetRenderWindow().Render()
    
    def getRendererIncludeActorsOpacity(self) -> dict:
        actors_opacity_dict = {}
        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                actors_opacity_dict[actor_object_name_info_list[1]] = ins_actor.GetProperty().GetOpacity()
            else:
                continue
        return actors_opacity_dict
    def setInteractorRendererIncludeAcotrsOpacity(self, in_actors_opacity_dict:dict) -> None:
        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object' and actor_object_name_info_list[1] in in_actors_opacity_dict:
                ins_actor.GetProperty().SetOpacity(in_actors_opacity_dict[actor_object_name_info_list[1]])
            else:
                continue
        self.GetRenderWindow().Render()
    
    def getRendererIncludeActorsVisibility(self) -> dict:
        actors_visibility_dict = {}
        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                actors_visibility_dict[actor_object_name_info_list[1]] = ins_actor.GetVisibility()
            else:
                continue
        return actors_visibility_dict
    def setRendererIncludeActorsVisibility(self, in_actors_visibility_dict:dict) -> None:
        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object' and actor_object_name_info_list[1] in in_actors_visibility_dict:
                ins_actor.SetVisibility(in_actors_visibility_dict[actor_object_name_info_list[1]])
            else:
                continue
        self.GetRenderWindow().Render()
    
    def changeVariableOfCountorRenderer(self, in_variable_name:str) -> None:
        first_step_name = list(self.__ins_database_pointer['Steps'].keys())[0]
        if in_variable_name in common.P4SOutputInfo.NODE_VARIABLES_DESCRIPTION:
            data_type = 'node'
            
            ins_first_frame_results_set = self.__ins_database_pointer['Nodes'][in_variable_name][first_step_name]['0']
        elif in_variable_name in common.P4SOutputInfo.ELEMENT_VARIABLES_DESCRIPTION:
            data_type = 'element'
            
            ins_first_frame_results_set = self.__ins_database_pointer['Elements'][in_variable_name][first_step_name]['0']
        elif in_variable_name in common.P4SOutputInfo.OPTIMIZATION_VARIABLES_DESCRIPTION['node']:
            data_type = 'node'
            
            ins_first_frame_results_set = self.__ins_database_pointer['Nodes'][in_variable_name][first_step_name]['0']
        elif in_variable_name in common.P4SOutputInfo.OPTIMIZATION_VARIABLES_DESCRIPTION['element']:
            data_type = 'element'
            
            ins_first_frame_results_set = self.__ins_database_pointer['Elements'][in_variable_name][first_step_name]['0']
        else:
            pass
        
        model_dimension = str(self.__ins_database_pointer['basic'][0],'utf-8')
        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                ins_instance_mapper = ins_actor.GetMapper()
                
                ins_instance_mesh = ins_instance_mapper.GetInput()
                ins_instance_points_data = ins_instance_mesh.GetPointData()
                ins_instance_points_data.Initialize()
                ins_instance_cells_data = ins_instance_mesh.GetCellData()
                ins_instance_cells_data.Initialize()
                
                instance_location_array = self.__ins_database_pointer['Mesh']['Instances'][actor_object_name_info_list[1]]
                
                if data_type == 'node':
                    for component_index, component_name in enumerate(common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name]):
                        points_vtk_data_array = numpy_support.numpy_to_vtk(ins_first_frame_results_set[component_index,instance_location_array[0]-1:instance_location_array[1]+1])
                        points_vtk_data_array.SetName(component_name)
                        ins_instance_points_data.AddArray(points_vtk_data_array)
                    ins_instance_points_data.SetActiveScalars(common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name][0])

                    ins_instance_mapper.SetScalarModeToUsePointData()
                elif data_type =='element':
                    for component_index, component_name in enumerate(common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name]):
                        cells_vtk_data_array = numpy_support.numpy_to_vtk(ins_first_frame_results_set[component_index,instance_location_array[2]-1:instance_location_array[3]+1])
                        cells_vtk_data_array.SetName(component_name)
                        ins_instance_cells_data.AddArray(cells_vtk_data_array)
                    ins_instance_cells_data.SetActiveScalars(common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name][0])
                
                    ins_instance_mapper.SetScalarModeToUseCellData()
                else:
                    pass
            else:
                continue
        
        min_value = min(ins_first_frame_results_set[0])
        max_value = max(ins_first_frame_results_set[0])
        for ins_actor in self.__ins_contour_renderer.GetActors2D():
            if ins_actor.GetObjectName() == 'scalar-bar':
                ins_actor.SetTitle(','.join([in_variable_name,common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name][0]]))
                ins_scalar_bar = ins_actor
                break
            else:
                continue
        ins_scalar_bar.SetVisibility(1)
        ins_scalar_bar_lookup_table = ins_scalar_bar.GetLookupTable()
        ins_scalar_bar_lookup_table.SetRange(min_value,max_value)
        
        self.GetRenderWindow().Render()
    def changeVariableComponentOfCountorRenderer(self, in_step_name:str, in_frame_name:str, in_component_name:str) -> None:
        for ins_actor in self.__ins_contour_renderer.GetActors2D():
            if ins_actor.GetObjectName() == 'scalar-bar':
                ins_scalar_bar = ins_actor
                break
            else:
                continue
        variable_name = ins_scalar_bar.GetTitle().split(',')[0]
        ins_scalar_bar.SetTitle(','.join([variable_name,in_component_name]))

        if variable_name in common.P4SOutputInfo.NODE_VARIABLES_DESCRIPTION:
            ins_first_frame_results_set = self.__ins_database_pointer['Nodes'][variable_name][in_step_name][in_frame_name]
        elif variable_name in common.P4SOutputInfo.ELEMENT_VARIABLES_DESCRIPTION:
            ins_first_frame_results_set = self.__ins_database_pointer['Elements'][variable_name][in_step_name][in_frame_name]
        else:
            pass
        model_dimension = str(self.__ins_database_pointer['basic'][0],'utf-8')
        component_index = common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][variable_name].index(in_component_name)
        min_value = min(ins_first_frame_results_set[component_index])
        max_value = max(ins_first_frame_results_set[component_index])
        ins_scalar_bar_lookup_table = ins_scalar_bar.GetLookupTable()
        ins_scalar_bar_lookup_table.SetRange(min_value,max_value)

        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                ins_instance_mesh = ins_actor.GetMapper().GetInput()
                
                ins_instance_points_data = ins_instance_mesh.GetPointData()
                ins_instance_points_data.SetActiveScalars(in_component_name)
                
                ins_instance_cells_data = ins_instance_mesh.GetCellData()
                ins_instance_cells_data.SetActiveScalars(in_component_name)
            else:
                continue
        
        self.GetRenderWindow().Render()
    
    def changeFrameOfCountorRenderer(self, in_variable_name:str, in_component_name:str, in_step_name:str, in_frame_name:str) -> None:    
        if in_variable_name in common.P4SOutputInfo.NODE_VARIABLES_DESCRIPTION:
            data_type = 'node'
            
            ins_first_frame_results_set = self.__ins_database_pointer['Nodes'][in_variable_name][in_step_name][in_frame_name]
        elif in_variable_name in common.P4SOutputInfo.ELEMENT_VARIABLES_DESCRIPTION:
            data_type = 'element'
            
            ins_first_frame_results_set = self.__ins_database_pointer['Elements'][in_variable_name][in_step_name][in_frame_name]
        elif in_variable_name in common.P4SOutputInfo.OPTIMIZATION_VARIABLES_DESCRIPTION['node']:
            data_type = 'node'
            
            ins_first_frame_results_set = self.__ins_database_pointer['Nodes'][in_variable_name][in_step_name][in_frame_name]
        elif in_variable_name in common.P4SOutputInfo.OPTIMIZATION_VARIABLES_DESCRIPTION['element']:
            data_type = 'element'
            
            ins_first_frame_results_set = self.__ins_database_pointer['Elements'][in_variable_name][in_step_name][in_frame_name]
        else:
            pass
        
        model_dimension = str(self.__ins_database_pointer['basic'][0],'utf-8')
        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                ins_instance_mesh = ins_actor.GetMapper().GetInput()
                ins_instance_points_data = ins_instance_mesh.GetPointData()
                ins_instance_points_data.Initialize()
                ins_instance_cells_data = ins_instance_mesh.GetCellData()
                ins_instance_cells_data.Initialize()
                
                instance_location_array = self.__ins_database_pointer['Mesh']['Instances'][actor_object_name_info_list[1]]
                
                if data_type == 'node':
                    for component_index, component_name in enumerate(common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name]):
                        points_vtk_data_array = numpy_support.numpy_to_vtk(ins_first_frame_results_set[component_index,instance_location_array[0]-1:instance_location_array[1]+1])
                        points_vtk_data_array.SetName(component_name)
                        ins_instance_points_data.AddArray(points_vtk_data_array)
                    ins_instance_points_data.SetActiveScalars(in_component_name)
                elif data_type =='element':
                    for component_index, component_name in enumerate(common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name]):
                        cells_vtk_data_array = numpy_support.numpy_to_vtk(ins_first_frame_results_set[component_index,instance_location_array[2]-1:instance_location_array[3]+1])
                        cells_vtk_data_array.SetName(component_name)
                        ins_instance_cells_data.AddArray(cells_vtk_data_array)
                    ins_instance_cells_data.SetActiveScalars(in_component_name)
                else:
                    pass
            
                if self.__topology_density_threshold == 0.01:
                    pass
                else:
                    self.binarizeTopolotyDensityOfCountorRenderer(self.__topology_density_threshold,in_step_name,in_frame_name)
            else:
                continue
        
        component_index = common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name].index(in_component_name)
        min_value = min(ins_first_frame_results_set[component_index])
        max_value = max(ins_first_frame_results_set[component_index])
        for ins_actor in self.__ins_contour_renderer.GetActors2D():
            if ins_actor.GetObjectName() == 'scalar-bar':
                ins_actor.SetTitle(','.join([in_variable_name,common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_variable_name][0]]))
                ins_scalar_bar = ins_actor
                break
            else:
                continue
        ins_scalar_bar.SetTitle(','.join([in_variable_name, in_component_name]))
        ins_scalar_bar_lookup_table = ins_scalar_bar.GetLookupTable()
        ins_scalar_bar_lookup_table.SetRange(min_value,max_value)
        
        self.GetRenderWindow().Render()
    
    def changeDeformationStateOfCountorRenderer(self, in_deformation_infomation) -> None:
        if in_deformation_infomation == []:
            for ins_actor in self.__ins_contour_renderer.GetActors():
                actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
                if actor_object_name_info_list[0] == 'object':
                    ins_instance_points = ins_actor.GetMapper().GetInput().GetPoints()
                    
                    instance_node_start_label,instance_node_end_label = self.__ins_database_pointer['Mesh']['Instances'][actor_object_name_info_list[1]][0:2]
                    for node_index,node_coordinates in enumerate(self.__ins_database_pointer['Mesh']['nodes'][instance_node_start_label-1:instance_node_end_label]):
                        ins_instance_points.SetPoint(node_index,node_coordinates)
                    ins_instance_points.Modified()
                else:
                    continue
        else:
            ins_result_u_frames_group = self.__ins_database_pointer['Nodes']['U'][in_deformation_infomation[0]]
            if in_deformation_infomation[1] in ins_result_u_frames_group:
                ins_result_u_frame_set = ins_result_u_frames_group[in_deformation_infomation[1]]
            else:
                frames_number_list = [int(frame_name) for frame_name in ins_result_u_frames_group.keys()]
                frames_number_list.append(int(in_deformation_infomation[1]))
                frames_number_list.sort()
                output_frame_number = frames_number_list[frames_number_list.index(int(in_deformation_infomation[1]))-1]
                
                ins_result_u_frame_set = ins_result_u_frames_group[str(output_frame_number)]
    
            model_dimension = str(self.__ins_database_pointer['basic'][0],'utf-8')
            if model_dimension == '2D':
                for ins_actor in self.__ins_contour_renderer.GetActors():
                    actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
                    if actor_object_name_info_list[0] == 'object':
                        ins_instance_points = ins_actor.GetMapper().GetInput().GetPoints()
                        
                        instance_node_start_label,instance_node_end_label = self.__ins_database_pointer['Mesh']['Instances'][actor_object_name_info_list[1]][0:2]
                        for node_index,node_coordinates in enumerate(self.__ins_database_pointer['Mesh']['nodes'][instance_node_start_label-1:instance_node_end_label]):
                            deformable_node_coordinates = node_coordinates[:]
                            deformable_node_coordinates[0] += ins_result_u_frame_set[0,instance_node_start_label-1+node_index]*in_deformation_infomation[2]
                            deformable_node_coordinates[1] += ins_result_u_frame_set[1,instance_node_start_label-1+node_index]*in_deformation_infomation[2]
                            
                            ins_instance_points.SetPoint(node_index,deformable_node_coordinates)
                        ins_instance_points.Modified()
                    else:
                        continue
            else:
                for ins_actor in self.__ins_contour_renderer.GetActors():
                    actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
                    if actor_object_name_info_list[0] == 'object':
                        ins_instance_points = ins_actor.GetMapper().GetInput().GetPoints()
                        
                        instance_node_start_label,instance_node_end_label = self.__ins_database_pointer['Mesh']['Instances'][actor_object_name_info_list[1]][0:2]
                        for node_index,node_coordinates in enumerate(self.__ins_database_pointer['Mesh']['nodes'][instance_node_start_label-1:instance_node_end_label]):
                            deformable_node_coordinates = node_coordinates[:]
                            deformable_node_coordinates[0] += ins_result_u_frame_set[0,instance_node_start_label-1+node_index]*in_deformation_infomation[2]
                            deformable_node_coordinates[1] += ins_result_u_frame_set[1,instance_node_start_label-1+node_index]*in_deformation_infomation[2]
                            deformable_node_coordinates[2] += ins_result_u_frame_set[2,instance_node_start_label-1+node_index]*in_deformation_infomation[2]
                            
                            ins_instance_points.SetPoint(node_index,deformable_node_coordinates)
                        ins_instance_points.Modified()
                    else:
                        continue
        
        self.GetRenderWindow().Render()
    
    def changeColorMapOfCountorRenderer(self, in_map_name:str) -> None:
        for ins_actor in self.__ins_contour_renderer.GetActors2D():
            if ins_actor.GetObjectName() == 'scalar-bar':
                ins_scalar_bar_lookup_table = ins_actor.GetLookupTable()
                break
            else:
                continue
        
        colors_number = ins_scalar_bar_lookup_table.GetNumberOfColors()
        ins_color_map = colormaps.get_cmap(in_map_name)
        ins_color_norm = colors.Normalize(0,colors_number)
        for color_index in range(colors_number):
            ins_scalar_bar_lookup_table.SetTableValue(color_index,*ins_color_map(ins_color_norm(color_index)))
        ins_scalar_bar_lookup_table.Build()
        
        self.GetRenderWindow().Render()
    def changeColorNumberOfCountorRenderer(self, in_map_name:str, in_color_number:int) -> None:
        for ins_actor in self.__ins_contour_renderer.GetActors2D():
            if ins_actor.GetObjectName() == 'scalar-bar':
                ins_scalar_bar_lookup_table = ins_actor.GetLookupTable()
                break
            else:
                continue
        
        ins_scalar_bar_lookup_table.SetNumberOfTableValues(in_color_number)
        ins_color_map = colormaps.get_cmap(in_map_name)
        ins_color_norm = colors.Normalize(0,in_color_number-1)
        for color_index in range(in_color_number):
            ins_scalar_bar_lookup_table.SetTableValue(color_index,*ins_color_map(ins_color_norm(color_index)))
        ins_scalar_bar_lookup_table.Build()
        
        self.GetRenderWindow().Render()
    
    def exportContourDataToCSVOfContourRenderer(self, in_csv_file_full_name:str) -> None:
        for ins_actor in self.__ins_contour_renderer.GetActors2D():
            if ins_actor.GetObjectName() == 'scalar-bar':
                variable_name, component_name = ins_actor.GetTitle().split(',')
                break
            else:
                continue
        
        contour_data_by_instance_dict = {}
        max_labels_number = 0
        if variable_name in common.P4SOutputInfo.NODE_VARIABLES_DESCRIPTION:
            for ins_actor in self.__ins_contour_renderer.GetActors():
                actor_name_info_list = ins_actor.GetObjectName().split('>',1)
                if actor_name_info_list[0] == 'object':
                    contour_data_by_instance_dict[actor_name_info_list[1]] = ins_actor.GetMapper().GetInput().GetPointData().GetArray(component_name)
                    
                    instance_nodes_number = ins_actor.GetMapper().GetInput().GetNumberOfPoints()
                    if instance_nodes_number > max_labels_number:
                        max_labels_number = instance_nodes_number
                    else:
                        pass
                else:
                    continue
        elif variable_name in common.P4SOutputInfo.ELEMENT_VARIABLES_DESCRIPTION:
            for ins_actor in self.__ins_contour_renderer.GetActors():
                actor_name_info_list = ins_actor.GetObjectName().split('>',1)
                if actor_name_info_list[0] == 'object':
                    contour_data_by_instance_dict[actor_name_info_list[1]] = ins_actor.GetMapper().GetInput().GetCellData().GetArray(component_name)
                
                    instance_elements_number = ins_actor.GetMapper().GetInput().GetNumberOfCells()
                    if instance_elements_number > max_labels_number:
                        max_labels_number = instance_elements_number
                    else:
                        pass
                else:
                    continue
        else:
            pass
        
        with open(in_csv_file_full_name,'w',newline='',encoding='utf-8') as ins_csv_file:
            ins_csv_writer = csv.writer(ins_csv_file)
            
            initial_tip_list = []
            for instance_name in contour_data_by_instance_dict:
                initial_tip_list.append(instance_name)
                initial_tip_list.append(variable_name+','+component_name)
            ins_csv_writer.writerow(initial_tip_list)
            
            for data_index in range(max_labels_number):
                data_label = data_index+1
                output_data_list = []
                
                for ins_instance_data in contour_data_by_instance_dict.values():
                    if ins_instance_data.GetNumberOfValues() < data_label:
                        output_data_list.append('')
                        output_data_list.append('')
                    else:
                        output_data_list.append(data_label)
                        output_data_list.append(ins_instance_data.GetVariantValue(data_index).ToString())
                        
                ins_csv_writer.writerow(output_data_list)   
    def exportContourDataToImageOfContourRenderer(self, in_work_path:str) -> None:
        ins_image_filter = vtk.vtkWindowToImageFilter()
        ins_image_filter.SetInput(self.GetRenderWindow())
        ins_image_filter.SetScale(1)
        ins_image_filter.Update()

        for ins_actor in self.__ins_contour_renderer.GetActors2D():
            if ins_actor.GetObjectName() == 'scalar-bar':
                variable_name, component_name = ins_actor.GetTitle().split(',')
                break
            else:
                continue

        ins_png_image_writer = vtk.vtkPNGWriter()
        ins_png_image_writer.SetFileName(in_work_path+os.sep+variable_name+'-'+component_name+'.png')
        ins_png_image_writer.SetInputConnection(ins_image_filter.GetOutputPort())
        ins_png_image_writer.Write()

    def getDisplayTypeOfRenderWindow(self) -> str:
        if self.GetRenderWindow().GetRenderers().GetItemAsObject(1) is self.__ins_graph_renderer:
            display_type = 'graph'
        else:
            display_type = 'contour'

        return display_type
    
    def switchDisplayTypeOfRenderWindow(self, in_type:str) -> None:
        ins_render_window = self.GetRenderWindow()
        
        if in_type == 'contour':
            self.__ins_attached_marker.EnabledOn()
            
            ins_render_window.RemoveRenderer(self.__ins_graph_renderer)
            ins_render_window.AddRenderer(self.__ins_contour_renderer)
        elif in_type == 'graph':
            self.__ins_attached_marker.EnabledOff()
            
            ins_render_window.RemoveRenderer(self.__ins_contour_renderer)
            ins_render_window.AddRenderer(self.__ins_graph_renderer)
        else:
            pass
        
        ins_render_window.Render()
    def createGraphOfGraphRenderer(self, in_graph_infomation:dict) -> None:
        time_points_array = numpy.array([0.0],dtype=numpy.float64)
        steps_start_time_point_index_dict = {}
        step_start_time_point_index = 0
        for step_name in self.__ins_database_pointer['Steps']:
            step_time_points_array = self.__ins_database_pointer['Steps'][step_name][0]
            
            steps_start_time_point_index_dict[step_name] = step_start_time_point_index
            step_start_time_point_index += len(step_time_points_array)-1
            
            time_points_array = numpy.concatenate((time_points_array,time_points_array[-1]+step_time_points_array[1:]),axis=None)
        del step_start_time_point_index
        
        ins_data_table = vtk.vtkTable()
        ins_data_table.SetNumberOfRows(time_points_array.shape[0])
        time_VTK_data_array = numpy_support.numpy_to_vtk(time_points_array)
        time_VTK_data_array.SetName('time')
        ins_data_table.AddColumn(time_VTK_data_array)
        
        if in_graph_infomation['position'] == 'Node':
            ins_variable_results_group = self.__ins_database_pointer['Nodes'][in_graph_infomation['data'][0]]
        else:
            ins_variable_results_group = self.__ins_database_pointer['Elements'][in_graph_infomation['data'][0]]
        
        model_dimension = str(self.__ins_database_pointer['basic'][0],'utf-8')
        if in_graph_infomation['object'][0] == 'group':
            if in_graph_infomation['position'] == 'Node':
                ins_group_include_labels_of_assembly_set = self.__ins_database_pointer['Mesh']['Groups']['Nodes'][in_graph_infomation['object'][1]]
            else:
                ins_group_include_labels_of_assembly_set = self.__ins_database_pointer['Mesh']['Groups']['Elements'][in_graph_infomation['object'][1]]
            
            for instance_name,instance_location_array in self.__ins_database_pointer['Mesh']['Instances'].items():
                if in_graph_infomation['position'] == 'Node':
                    start_label, end_label = instance_location_array[0:2]
                else:
                    start_label, end_label = instance_location_array[2:]
                
                instance_include_assembly_labels_array = ins_group_include_labels_of_assembly_set[(ins_group_include_labels_of_assembly_set[:]>=start_label) & (ins_group_include_labels_of_assembly_set[:]<=end_label)]
                for assembly_label in instance_include_assembly_labels_array:
                    instance_label = assembly_label-start_label+1
                    
                    for component_name in in_graph_infomation['data'][1]:
                        component_value_array = numpy.zeros(shape=time_points_array.shape[0],dtype=numpy.float64)

                        component_index = common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_graph_infomation['data'][0]].index(component_name)
                        for step_name,step_time_point_start_index in steps_start_time_point_index_dict.items():
                            if step_time_point_start_index == 0:
                                component_value_array[0] = ins_variable_results_group[step_name]['0'][component_index,assembly_label-1]
                            else:
                                pass
                            
                            for frame_name in ins_variable_results_group[step_name]:
                                frame_number = int(frame_name)
                                if frame_number == 0:
                                    continue
                                else:
                                    component_value_array[step_time_point_start_index+frame_number] = ins_variable_results_group[step_name][frame_name][component_index,assembly_label-1]
                                    
                        component_VTK_data_array = numpy_support.numpy_to_vtk(component_value_array)
                        component_VTK_data_array.SetName(','.join([in_graph_infomation['data'][0],component_name,instance_name,in_graph_infomation['position'],str(instance_label)]))
                        ins_data_table.AddColumn(component_VTK_data_array)
        elif in_graph_infomation['object'][0] == 'label':
            if in_graph_infomation['position'] == 'Node':
                start_label, end_label = self.__ins_database_pointer['Mesh']['Instances'][in_graph_infomation['object'][1]][0:2]
            else:
                start_label, end_label =self.__ins_database_pointer['Mesh']['Instances'][in_graph_infomation['object'][1]][2:]
            
            instance_label = in_graph_infomation['object'][2]-start_label+1
            for component_name in in_graph_infomation['data'][1]:
                component_value_array = numpy.zeros(shape=time_points_array.shape[0],dtype=numpy.float64)

                component_index = common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_graph_infomation['data'][0]].index(component_name)
                for step_name,step_time_point_start_index in steps_start_time_point_index_dict.items():
                    if step_time_point_start_index == 0:
                        component_value_array[0] = ins_variable_results_group[step_name]['0'][component_index,in_graph_infomation['object'][2]-1]
                    else:
                        pass
                    
                    for frame_name in ins_variable_results_group[step_name]:
                        frame_number = int(frame_name)
                        if frame_number == 0:
                            continue
                        else:
                            component_value_array[step_time_point_start_index+frame_number] = ins_variable_results_group[step_name][frame_name][component_index,in_graph_infomation['object'][2]-1]
                            
                component_VTK_data_array = numpy_support.numpy_to_vtk(component_value_array)
                component_VTK_data_array.SetName(','.join([in_graph_infomation['data'][0],component_name,in_graph_infomation['object'][1],in_graph_infomation['position'],str(instance_label)]))
                ins_data_table.AddColumn(component_VTK_data_array)
        elif in_graph_infomation['object'][0] == 'view':
            for instance_name,instance_location_array in self.__ins_database_pointer['Mesh']['Instances'].items():
                if instance_name in in_graph_infomation['object'][1]:
                    pass
                else:
                    continue
                
                if in_graph_infomation['position'] == 'Node':
                    start_label, end_label = instance_location_array[0:2]
                else:
                    start_label, end_label = instance_location_array[2:]
                
                for instance_label in in_graph_infomation['object'][1][instance_name]:
                    assembly_label = instance_label+start_label-1
                    
                    for component_name in in_graph_infomation['data'][1]:
                        component_value_array = numpy.zeros(shape=time_points_array.shape[0],dtype=numpy.float64)

                        component_index = common.P4SOutputInfo.VARIABLE_INCLUDE_COMPONENTS[model_dimension][in_graph_infomation['data'][0]].index(component_name)
                        for step_name,step_time_point_start_index in steps_start_time_point_index_dict.items():
                            if step_time_point_start_index == 0:
                                component_value_array[0] = ins_variable_results_group[step_name]['0'][component_index,assembly_label-1]
                            else:
                                pass
                            
                            for frame_name in ins_variable_results_group[step_name]:
                                frame_number = int(frame_name)
                                if frame_number == 0:
                                    continue
                                else:
                                    component_value_array[step_time_point_start_index+frame_number] = ins_variable_results_group[step_name][frame_name][component_index,assembly_label-1]
                                    
                        component_VTK_data_array = numpy_support.numpy_to_vtk(component_value_array)
                        component_VTK_data_array.SetName(','.join([in_graph_infomation['data'][0],component_name,instance_name,in_graph_infomation['position'],str(instance_label)]))
                        ins_data_table.AddColumn(component_VTK_data_array)
        else:
            pass

        ins_xy_chart = vtk.vtkChartXY()
        ins_xy_chart.SetObjectName(in_graph_infomation['name'])
        ins_xy_chart.GetAxis(1).SetTitle('Time')
        ins_xy_chart.GetAxis(1).SetRange(0.0,time_points_array[-1])
        ins_xy_chart.GetAxis(1).GetTitleProperties().SetFontSize(20)
        ins_xy_chart.GetAxis(1).GetLabelProperties().SetFontSize(15)
        ins_xy_chart.GetAxis(1).SetLabelOffset(10)
        ins_xy_chart.GetAxis(0).SetTitle(in_graph_infomation['data'][0])
        ins_xy_chart.GetAxis(0).GetTitleProperties().SetFontSize(20)
        ins_xy_chart.GetAxis(0).GetLabelProperties().SetFontSize(15)
        ins_xy_chart.GetAxis(0).SetLabelOffset(10)
        ins_xy_chart.GetLegend().SetVisible(True)
        ins_xy_chart.GetLegend().SetLabelSize(20)
        ins_xy_chart.GetLegend().SetHorizontalAlignment(vtk.vtkChartLegend.CUSTOM)
        ins_xy_chart.GetLegend().SetVerticalAlignment(vtk.vtkChartLegend.CUSTOM)

        for column_index in range(1,ins_data_table.GetNumberOfColumns()):
            ins_plot_line = ins_xy_chart.AddPlot(vtk.vtkChart.LINE)
            ins_plot_line.SetInputData(ins_data_table,0,column_index)
            
            line_color = numpy.random.randint(0,255,3) / 255.0
            ins_plot_line.SetColorF(*line_color)
            ins_plot_line.SetWidth(2.0)
            ins_plot_line.SetLabel(ins_data_table.GetColumnName(column_index))

        for ins_actor in self.__ins_graph_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'context-actor':
                ins_context_scene = ins_actor.GetScene()
                break
            else:
                continue
        ins_xy_chart.SetVisible(False)
        ins_context_scene.AddItem(ins_xy_chart)
  
        self.GetRenderWindow().Render()
    def switchGraphOfGraphRenderer(self, in_graph_name:str) -> None:
        for ins_actor in self.__ins_graph_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'context-actor':
                ins_context_scene = ins_actor.GetScene()
            else:
                continue
        
        for item_index in range(ins_context_scene.GetNumberOfItems()):
            ins_xy_chart = ins_context_scene.GetItem(item_index)
            if ins_xy_chart.GetObjectName() == in_graph_name:
                ins_xy_chart.SetVisible(True)
            elif ins_xy_chart.GetVisible():
                ins_xy_chart.SetVisible(False)
            else:
                continue

        self.GetRenderWindow().Render()
    def renameGraphOfGraphRenderer(self, in_old_name:str, in_new_name:str) -> None:
        for ins_actor in self.__ins_graph_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'context-actor':
                ins_context_scene = ins_actor.GetScene()
            else:
                continue
        
        for item_index in range(ins_context_scene.GetNumberOfItems()):
            ins_xy_chart = ins_context_scene.GetItem(item_index)
            if ins_xy_chart.GetObjectName() == in_old_name:
                ins_xy_chart.SetObjectName(in_new_name)
                break
            else:
                continue
    def exportGraphDataToCSVOfGraphRenderer(self, in_graph_name:str, in_csv_file_full_name:str) -> None:
        for ins_actor in self.__ins_graph_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'context-actor':
                ins_context_scene = ins_actor.GetScene()
            else:
                continue
        for item_index in range(ins_context_scene.GetNumberOfItems()):
            ins_xy_chart = ins_context_scene.GetItem(item_index)
            if ins_xy_chart.GetObjectName() == in_graph_name:
                break
            else:
                continue
        ins_data_table = ins_xy_chart.GetPlot(0).GetInput()
        
        with open(in_csv_file_full_name,'w',newline='',encoding='utf-8') as ins_csv_file:
            ins_csv_writer = csv.writer(ins_csv_file)

            columns_name_list = [ins_data_table.GetColumnName(i) for i in range(ins_data_table.GetNumberOfColumns())]
            ins_csv_writer.writerow(columns_name_list)

            for i in range(ins_data_table.GetNumberOfRows()):
                ins_csv_writer.writerow([ins_data_table.GetValue(i,j) for j in range(ins_data_table.GetNumberOfColumns())])
    def exportGraphToImageOfGraphRenderer(self, in_graph_name:str, in_work_path:str) -> None:
        ins_image_filter = vtk.vtkWindowToImageFilter()
        ins_image_filter.SetInput(self.GetRenderWindow())
        ins_image_filter.SetScale(1)
        ins_image_filter.Update()

        ins_png_image_writer = vtk.vtkPNGWriter()
        ins_png_image_writer.SetFileName(in_work_path+os.sep+in_graph_name+'.png')
        ins_png_image_writer.SetInputConnection(ins_image_filter.GetOutputPort())
        ins_png_image_writer.Write()
    def deleteGraphOfGraphRenderer(self, in_graph_name:str) -> None:
        for ins_actor in self.__ins_graph_renderer.GetViewProps():
            if ins_actor.GetObjectName() == 'context-actor':
                ins_context_scene = ins_actor.GetScene()
            else:
                continue
        for item_index in range(ins_context_scene.GetNumberOfItems()):
            ins_xy_chart = ins_context_scene.GetItem(item_index)
            if ins_xy_chart.GetObjectName() == in_graph_name:
                break
            else:
                continue
        
        ins_xy_chart.RemoveAllPlots
        ins_context_scene.RemoveItem(ins_xy_chart)
        del ins_xy_chart
        
        self.GetRenderWindow().Render()
    
    def getDisplayDatabaseType(self) -> str:
        if self.__ins_database_pointer['basic'][1] == b'FEM':
            result_database_type = 'FEM'
        elif self.__ins_database_pointer['basic'][1] == b'OPT':
            if 'Elements' in self.__ins_database_pointer:
                if 'X' in self.__ins_database_pointer['Elements']:
                    result_database_type = 'TOP'
                else:
                    pass
            else:
                pass
        else:
            pass
        
        return result_database_type
    def getTopologyDensityThresholdOfCountorRenderer(self) -> float:
        return self.__topology_density_threshold
    def binarizeTopolotyDensityOfCountorRenderer(self,in_threshold, in_step_name:str, in_frame_name:str) -> None:
        ins_elements_x_set = self.__ins_database_pointer['Elements']['X'][in_step_name][in_frame_name]
        
        for ins_actor in self.__ins_contour_renderer.GetActors():
            actor_object_name_info_list = ins_actor.GetObjectName().split('>',1)
            if actor_object_name_info_list[0] == 'object':
                element_start_label,element_end_label = self.__ins_database_pointer['Mesh']['Instances'][actor_object_name_info_list[1]][2:]
                
                ins_instance_mapper = ins_actor.GetMapper()
                ins_instance_mesh = ins_instance_mapper.GetInput()
                ins_instance_cells_data = ins_instance_mesh.GetCellData()
                ghost_array = ins_instance_cells_data.GetGhostArray()
                if ghost_array is None:
                    pass
                else:
                    ins_instance_cells_data.RemoveArray('vtkGhostType')
                    ins_instance_cells_data.Update()
                
                ghost_array = vtk.vtkUnsignedCharArray()
                ghost_array.SetNumberOfComponents(1)
                ghost_array.SetName('vtkGhostType')
                ghost_array.SetNumberOfValues(element_end_label-element_start_label+1)
                ghost_array.Fill(0)
                ins_instance_mesh.GetCellData().AddArray(ghost_array)

                hide_element_index_array = numpy.where(ins_elements_x_set[0,element_start_label-1:element_end_label] < in_threshold)[0]
                for element_index in hide_element_index_array:
                    ghost_array.SetValue(element_index,vtk.vtkDataSetAttributes.HIDDENCELL)
            else:
                pass
        self.__topology_density_threshold = in_threshold
        
        self.GetRenderWindow().Render()

