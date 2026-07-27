# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import psutil
import multiprocessing
import glob

import h5py
import numpy
import datetime
import scipy
import scipy.sparse

from config import common
from . import tools


def intoFEAProcess(in_task_flie_full_name:str, in_ins_task_process_queen:object):
    work_path = os.path.dirname(in_task_flie_full_name)
    task_name = os.path.basename(in_task_flie_full_name).split('.')[0]
    
    task_process_file_full_name = work_path + os.sep + task_name + '.pro'
    task_result_file_full_name = work_path + os.sep + task_name + '.res'

    ins_fem_task_analysis_system = _femTaskAnalysisSystem(in_task_flie_full_name,task_process_file_full_name,task_result_file_full_name)
    process_file_state = ins_fem_task_analysis_system.initializeProcessFile()
    result_file_state = ins_fem_task_analysis_system.initializeResultFile()
    analysis_system_state = ins_fem_task_analysis_system.initializeSystems()
    if process_file_state and result_file_state and analysis_system_state:
        pass
    else:
        in_ins_task_process_queen.put([task_name,'error'])
        return None
    
    start_time_point = datetime.datetime.now()
    try:
        ins_fem_task_analysis_system.startAnalysis()
    except:
        in_ins_task_process_queen.put([task_name,'error'])
    else:
        end_time_point = datetime.datetime.now()
        total_analysis_time = end_time_point - start_time_point
        in_ins_task_process_queen.put([task_name,str(total_analysis_time)])

class _femTaskAnalysisSystem():
    
    def __init__(self, in_task_file_full_name:str,in_task_process_file_full_name:str,in_task_result_file_full_name:str) -> None:
        self.__task_file_full_name = in_task_file_full_name
        self.__task_process_file_full_name = in_task_process_file_full_name
        self.__task_result_file_full_name = in_task_result_file_full_name
        
        self.__model_dimension = None
        
        self.__instances_location_dict  = {}
        self.__steps_info_dict = {}

        self.__displacement_info_dict = {'groups':[]}
        self.__concentrated_force_info_dict = {'groups':[]}
        self.__moment_info_dict = {'groups':[]}

        self.__nodes_outputs_info_dict = {}
        self.__elements_outputs_info_dict = {}

    def initializeProcessFile(self, in_ins_material_ifa_set:object=None) -> bool:
        ins_task_file = h5py.File(self.__task_file_full_name,'r')
        self.__model_dimension = str(ins_task_file['basic'][0],'utf-8')
        ins_task_mesh_group = ins_task_file['Mesh']
        ins_task_property_group = ins_task_file['Property']
        ins_task_conditions_group = ins_task_file['Conditions']

        all_nodes_number = ins_task_mesh_group['nodes'].shape[0]
        all_elements_number = ins_task_mesh_group['elements'].shape[0]
        
        try:
            with h5py.File(self.__task_process_file_full_name,'w') as in_task_process_file:
                ins_process_constant_group = in_task_process_file.create_group(name='Constant')
                # region
                ins_process_constant_dof_set = ins_process_constant_group.create_dataset(name='dof',shape=(all_nodes_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                ins_process_constant_dloc_set = ins_process_constant_group.create_dataset(name='dloc',shape=(all_nodes_number,),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                dof_loc = 0
                for node_index,node_associated_elements_label_array in enumerate(ins_task_mesh_group['association'][:]):
                    node_associated_elements_type_number_array = numpy.unique(numpy.array([ins_task_mesh_group['type'][i-1] for i in node_associated_elements_label_array]))
                    
                    node_include_dofs_list = []
                    for elements_type_number in node_associated_elements_type_number_array:
                        node_include_dofs_list.extend(common.P4SElementInfo.ELEMENT_NUMBER_TO_DOFS[elements_type_number])
                    node_include_dofs_list = list(set(node_include_dofs_list))
                    node_include_dofs_list.sort()
                    
                    ins_process_constant_dof_set[node_index] = numpy.asarray(node_include_dofs_list)
                    
                    ins_process_constant_dloc_set[node_index] = dof_loc
                    dof_loc += len(node_include_dofs_list)
                
                ins_process_constant_instances_group = ins_process_constant_group.create_group(name='Instances')
                for instnace_name in ins_task_mesh_group['Instances']:
                    start_dof_location = ins_process_constant_dloc_set[ins_task_mesh_group['Instances'][instnace_name][0]-1]
                    end_dof_location = ins_process_constant_dloc_set[ins_task_mesh_group['Instances'][instnace_name][1]-1] + len(ins_process_constant_dof_set[ins_task_mesh_group['Instances'][instnace_name][1]-1])-1
                    ins_process_constant_instances_group.create_dataset(name=instnace_name,data=numpy.array([start_dof_location,end_dof_location]),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])

                ins_process_constant_ngroups_group = ins_process_constant_group.create_group(name='NGroups')
                conditions_include_nodes_groups_name_list = []
                conditions_include_functions_name_list = []
                if 'displacement' in ins_task_conditions_group:
                    for group_name_btype_string in ins_task_conditions_group['displacement'][:,0]:
                        conditions_include_nodes_groups_name_list.append(str(group_name_btype_string,'utf-8'))
                    
                    for steps_components_array in ins_task_conditions_group['displacement'][:,1:]:
                        for setp_components_byte_string in steps_components_array[:]:
                            if setp_components_byte_string == b'':
                                continue
                            else:
                                function_name = str(setp_components_byte_string,'utf-8').split(',')[-1]
                                if function_name == 'None':
                                    continue
                                else:
                                    conditions_include_functions_name_list.append(function_name)
                else:
                    pass
                if 'concentrated force' in ins_task_conditions_group:
                    for group_name_btype_string in ins_task_conditions_group['concentrated force'][:,0]:
                        conditions_include_nodes_groups_name_list.append(str(group_name_btype_string,'utf-8'))

                    for steps_components_array in ins_task_conditions_group['concentrated force'][:,1:]:
                        for setp_components_byte_string in steps_components_array[:]:
                            if setp_components_byte_string == b'':
                                continue
                            else:
                                function_name = str(setp_components_byte_string,'utf-8').split(',')[-1]
                                if function_name == 'None':
                                    continue
                                else:
                                    conditions_include_functions_name_list.append(function_name)
                else:
                    pass
                if 'moment' in ins_task_conditions_group:
                    for group_name_btype_string in ins_task_conditions_group['moment'][:,0]:
                        conditions_include_nodes_groups_name_list.append(str(group_name_btype_string,'utf-8'))
                        
                    for steps_components_array in ins_task_conditions_group['moment'][:,1:]:
                        for setp_components_byte_string in steps_components_array[:]:
                            if setp_components_byte_string == b'':
                                continue
                            else:
                                function_name = str(setp_components_byte_string,'utf-8').split(',')[-1]
                                if function_name == 'None':
                                    continue
                                else:
                                    conditions_include_functions_name_list.append(function_name)
                else:
                    pass
                conditions_include_nodes_groups_name_list = list(set(conditions_include_nodes_groups_name_list))
                for group_name in conditions_include_nodes_groups_name_list:
                    ins_process_constant_ngroups_group.create_dataset(name=group_name,data=ins_task_mesh_group['Groups']['Nodes'][group_name][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                conditions_include_functions_name_list = list(set(conditions_include_functions_name_list))
                ins_process_constant_functions_group = ins_process_constant_group.create_group(name='Functions')
                for function_name in conditions_include_functions_name_list:
                    ins_process_constant_functions_group.create_dataset(name=function_name,data=ins_task_conditions_group['Functions'][function_name][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                # endregion
                
                ins_process_update_group = in_task_process_file.create_group(name='Update')
                # region
                ins_process_update_group.create_dataset(name='orientation',data=ins_task_mesh_group['orientation'],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                
                available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
                if available_cpu_number <= 0:
                    print(f"The CPU usage is too high!")
                    raise ChildProcessError()
                else:
                    pass
                if all_elements_number < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
                    available_cpu_number = 1
                else:
                    pass
                process_elements_index_range_list = [[0,int(all_elements_number/available_cpu_number)]]
                for process_index in range(1,available_cpu_number):
                    process_elements_index_range_list.append([process_elements_index_range_list[process_index-1][1],process_elements_index_range_list[process_index-1][1]+process_elements_index_range_list[0][1]])
                process_elements_index_range_list[-1][1] = all_elements_number
                
                processes_list = []
                temp_file_head_name = self.__task_file_full_name.split('.')[0]
                process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
                for process_id,index_range in enumerate(process_elements_index_range_list):
                    temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.femtemp'
                    with h5py.File(temp_file_full_name,'w') as ins_fem_temp_file:
                        ins_fem_temp_file.create_dataset(name='readyelements',data=ins_task_mesh_group['elements'][index_range[0]:index_range[1]])
                        ins_fem_temp_file.create_dataset(name='allnodes',data=ins_task_mesh_group['nodes'][:])
                        ins_fem_temp_file.create_dataset(name='readyelementstype',data=ins_task_mesh_group['type'][index_range[0]:index_range[1]])
                        ins_fem_temp_file.create_dataset(name='readyelementsattributes',data=ins_task_mesh_group['attributes'][index_range[0]:index_range[1]])
                        ins_fem_temp_file.create_dataset(name='readyelementsmaterials',data=ins_task_mesh_group['materials'][index_range[0]:index_range[1]])
                        ins_fem_temp_file.create_dataset(name='readyelementsgeomnum',data=ins_task_mesh_group['geometry'][index_range[0]:index_range[1]])
                        ins_fem_temp_property_attributes_group = ins_fem_temp_file.create_group(name='PropAttributes')
                        for i,j in ins_task_property_group['Attributes'].items():
                            ins_fem_temp_property_attributes_group.create_dataset(name=i,data=j[:])
                        ins_fem_temp_property_materials_group = ins_fem_temp_file.create_group(name='PropMaterials')
                        for i,j in ins_task_property_group['Materials'].items():
                            ins_fem_temp_property_materials_group.create_dataset(name=i,data=j[:])
                        if in_ins_material_ifa_set is None:
                            ins_fem_temp_file.create_dataset(name='readyelementsifa',data=numpy.full(shape=(index_range[1]-index_range[0]),fill_value=1.0),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                        else:
                            ins_fem_temp_file.create_dataset(name='readyelementsifa',data=in_ins_material_ifa_set[index_range[0]:index_range[1]])
                        ins_fem_temp_file.create_dataset(name='readyelementsorientation',data=ins_task_mesh_group['orientation'][index_range[0]:index_range[1]])
                        
                        ins_fem_temp_file.create_dataset(name='readyelementsgeometry',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                        ins_fem_temp_file.create_dataset(name='readyelementstm',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                        ins_fem_temp_file.create_dataset(name='readyelementsdm',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                        ins_fem_temp_file.create_dataset(name='readyelementsbm',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                        ins_fem_temp_file.create_dataset(name='readyelementskm',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                
                    ins_process = multiprocessing.Process(target=common.P4SElementInfo.getElementsTBDKMatrixes,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                    
                    processes_list.append(ins_process)
                    ins_process.start()
                for ins_process in processes_list:
                    ins_process.join()
                ins_process_update_elements_geometry_set = ins_process_update_group.create_dataset(name='geometry',shape=(all_elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                ins_process_update_elements_tm_set = ins_process_update_group.create_dataset(name='tm',shape=(all_elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                ins_process_update_elements_dm_set = ins_process_update_group.create_dataset(name='dm',shape=(all_elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                ins_process_update_elements_bm_set = ins_process_update_group.create_dataset(name='bm',shape=(all_elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                ins_process_update_elements_km_set = ins_process_update_group.create_dataset(name='km',shape=(all_elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                for ins_process in processes_list:
                    process_id_string = ins_process.name.split('-')[-1]
                    ins_process.close()
                    
                    temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.femtemp'
                    index_range = process_elements_index_range_list[int(process_id_string)]
                    
                    with h5py.File(temp_file_full_name,'r') as ins_fem_temp_file:
                        for lcoal_index,element_index in enumerate(range(index_range[0],index_range[1])):
                            ins_process_update_elements_geometry_set[element_index] = ins_fem_temp_file['readyelementsgeometry'][lcoal_index]
                            ins_process_update_elements_tm_set[element_index] = ins_fem_temp_file['readyelementstm'][lcoal_index]
                            ins_process_update_elements_dm_set[element_index] = ins_fem_temp_file['readyelementsdm'][lcoal_index]
                            
                            ins_process_update_elements_bm_set[element_index] = ins_fem_temp_file['readyelementsbm'][lcoal_index]
                            ins_process_update_elements_km_set[element_index] = ins_fem_temp_file['readyelementskm'][lcoal_index]
                    os.remove(temp_file_full_name)
                del processes_list
                
                processes_list = []
                temp_file_head_name = self.__task_file_full_name.split('.')[0]
                for process_id,index_range in enumerate(process_elements_index_range_list):
                    temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.femtemp'
                    with h5py.File(temp_file_full_name,'w') as ins_fem_temp_file:
                        ins_fem_temp_file.create_dataset(name='readyelements',data=ins_task_mesh_group['elements'][index_range[0]:index_range[1]])
                        ins_fem_temp_file.create_dataset(name='readyelementstype',data=ins_task_mesh_group['type'][index_range[0]:index_range[1]])
                        ins_fem_temp_file.create_dataset(name='allnodesfirstdoflocation',data=ins_process_constant_dloc_set[:])
                        ins_fem_temp_file.create_dataset(name='allnodesdofs',data=ins_process_constant_dof_set[:])
                        ins_fem_temp_file.create_dataset(name='readyelementskm',data=ins_process_update_elements_km_set[index_range[0]:index_range[1]])

                        ins_fem_temp_file.create_dataset(name='readyelementsvalues',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                        ins_fem_temp_file.create_dataset(name='readyelementsrows',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                        ins_fem_temp_file.create_dataset(name='readyelementscolumns',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                
                    ins_process = multiprocessing.Process(target=common.P4SElementInfo.getAssembleGlobalStiffnessMatrixSparseInformation,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                    
                    processes_list.append(ins_process)
                    ins_process.start()
                for ins_process in processes_list:
                    ins_process.join()
                global_stiffness_matrix_values_array = numpy.array([],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                global_stiffness_matrixe_rows_array = numpy.array([],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                global_stiffness_matrixe_columns_array = numpy.array([],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                for ins_process in processes_list:
                    process_id_string = ins_process.name.split('-')[-1]
                    ins_process.close()
                    
                    temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.femtemp'

                    with h5py.File(temp_file_full_name,'r') as ins_fem_temp_file:
                        global_stiffness_matrix_values_array = numpy.concatenate([global_stiffness_matrix_values_array,numpy.concatenate(ins_fem_temp_file['readyelementsvalues'][:])])
                        global_stiffness_matrixe_rows_array = numpy.concatenate([global_stiffness_matrixe_rows_array,numpy.concatenate(ins_fem_temp_file['readyelementsrows'][:])])
                        global_stiffness_matrixe_columns_array = numpy.concatenate([global_stiffness_matrixe_columns_array,numpy.concatenate(ins_fem_temp_file['readyelementscolumns'][:])])
                    os.remove(temp_file_full_name)
                del processes_list

                total_dofs_number = 0
                for node_index in range(all_nodes_number):
                    total_dofs_number += ins_process_constant_dof_set[node_index].shape[0]
                global_stiffness_matrix = scipy.sparse.coo_matrix((global_stiffness_matrix_values_array,(global_stiffness_matrixe_rows_array,global_stiffness_matrixe_columns_array)),shape=(total_dofs_number,total_dofs_number),dtype=common.P4SFormat.NUMERICAL_PRECISION['float']).todok().tocoo()
                del global_stiffness_matrix_values_array,global_stiffness_matrixe_rows_array,global_stiffness_matrixe_columns_array
                global_stiffness_matrix.eliminate_zeros()
                ins_process_update_group.create_dataset(name='gkm',data=numpy.array([global_stiffness_matrix.data,global_stiffness_matrix.row,global_stiffness_matrix.col]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                del global_stiffness_matrix

                ins_process_update_group.create_dataset(name='deltau',shape=(total_dofs_number,),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                ins_process_update_group.create_dataset(name='deltaf',shape=(total_dofs_number,),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                # endregion

                ins_process_record_group = in_task_process_file.create_group(name='Record')
                # region
                for record_varibale in ['u0','u','fm','rfm']:
                    ins_process_record_group.create_dataset(name=record_varibale,shape=(total_dofs_number,),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])

                if self.__model_dimension == '2D':
                    integration_point_variable_components_number = 4
                elif self.__model_dimension == '3D':
                    integration_point_variable_components_number = 6
                else:
                    pass
                for record_varibale in ['ipee','ipes']:
                    ins_record_variable_set = ins_process_record_group.create_dataset(name=record_varibale,shape=(all_elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                    for element_index in range(all_elements_number):
                        element_include_integration_points_number = common.P4SElementInfo.getElementIntegrationPointsNumber(ins_task_mesh_group['type'][element_index])
                        ins_record_variable_set[element_index] = numpy.zeros(shape=element_include_integration_points_number*integration_point_variable_components_number,dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                # endregion
        except:
            temp_files_name_list = glob.glob(os.path.dirname(self.__task_file_full_name)+os.sep+'*.femtemp')
            if temp_files_name_list == []:
                pass
            else:
                temp_file_base_name = os.path.basename(self.__task_file_full_name).split('.')[0]
                for temp_file_name in temp_files_name_list:
                    if os.path.basename(temp_file_name).split('.')[0].split('-')[0] == temp_file_base_name:
                        os.remove(temp_file_name)
                    else:
                        continue
            
            process_file_state = False
        else:
            process_file_state = True
        
        ins_task_file.close()
        
        return process_file_state
    def initializeResultFile(self) -> bool:
        ins_task_file = h5py.File(self.__task_file_full_name,'r')
        self.__model_dimension = str(ins_task_file['basic'][0],'utf-8')
        ins_task_mesh_group = ins_task_file['Mesh']
        ins_task_steps_group = ins_task_file['Steps']
        ins_task_outputs_group = ins_task_file['Outputs']
        
        try:
            with h5py.File(self.__task_result_file_full_name,'w') as ins_task_result_file:
                ins_result_basic_set = ins_task_result_file.create_dataset(name='basic',shape=(2,),dtype=h5py.string_dtype(encoding='utf-8'))
                ins_result_basic_set[0] = self.__model_dimension
                ins_result_basic_set[1] = 'FEM'

                ins_result_mesh_group = ins_task_result_file.create_group(name='Mesh')
                # region
                ins_result_mesh_instances_group = ins_result_mesh_group.create_group(name='Instances')
                for instance_name in ins_task_mesh_group['Instances']:
                    ins_result_mesh_instances_group.create_dataset(name=instance_name,data=ins_task_mesh_group['Instances'][instance_name][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                
                ins_result_mesh_group.create_dataset(name='nodes',data=ins_task_mesh_group['nodes'][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                ins_result_mesh_group.create_dataset(name='association',data=ins_task_mesh_group['association'][:],dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                ins_result_mesh_group.create_dataset(name='elements',data=ins_task_mesh_group['elements'][:],dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                ins_result_mesh_group.create_dataset(name='geometry',data=ins_task_mesh_group['geometry'][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                ins_result_mesh_group.create_dataset(name='type',data=ins_task_mesh_group['type'][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                
                ins_result_mesh_groups_group = ins_result_mesh_group.create_group(name='Groups')
                ins_result_mesh_nodes_groups_group = ins_result_mesh_groups_group.create_group(name='Nodes')
                for group_name in ins_task_mesh_group['Groups']['Nodes']:
                    ins_result_mesh_nodes_groups_group.create_dataset(name=group_name,data=ins_task_mesh_group['Groups']['Nodes'][group_name][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                ins_result_mesh_elements_groups_group = ins_result_mesh_groups_group.create_group(name='Elements')
                for group_name in ins_task_mesh_group['Groups']['Elements']:
                    ins_result_mesh_elements_groups_group.create_dataset(name=group_name,data=ins_task_mesh_group['Groups']['Elements'][group_name][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                # endregion

                ins_result_setps_group = ins_task_result_file.create_group(name='Steps')
                # region
                for step_name in ins_task_steps_group:
                    ins_result_setps_group.create_dataset(name=step_name,shape=(1,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                # endregion
                
                ins_result_nodes_group = ins_task_result_file.create_group(name='Nodes')
                # region
                for variable_name in ins_task_outputs_group['Nodes']:
                    ins_result_variable_group = ins_result_nodes_group.create_group(name=variable_name)
                    for step_name in ins_task_steps_group:
                        ins_result_variable_group.create_group(name=step_name)
                # endregion
                
                ins_result_elements_group = ins_task_result_file.create_group(name='Elements')
                # region
                for variable_name in ins_task_outputs_group['Elements']:
                    ins_result_variable_group = ins_result_elements_group.create_group(name=variable_name)
                    for step_name in ins_task_steps_group:
                        ins_result_variable_group.create_group(name=step_name)
                # endregion
        except: 
            result_file_state = False
        else:
            result_file_state = True
        
        ins_task_file.close()
        
        return result_file_state
    def initializeSystems(self) -> bool:
        ins_task_file = h5py.File(self.__task_file_full_name,'r')
        ins_task_process_file = h5py.File(self.__task_process_file_full_name,'r')
        
        ins_task_instances_group = ins_task_file['Mesh']['Instances']
        ins_process_constant_group = ins_task_process_file['Constant']
        ins_task_steps_group = ins_task_file['Steps']
        ins_task_conditions_group = ins_task_file['Conditions']
        ins_task_outputs_group = ins_task_file['Outputs']
    
        try:
            for instance_name,instance_location_array in ins_task_instances_group.items():
                self.__instances_location_dict[instance_name] = [[instance_location_array[0],instance_location_array[1]],[instance_location_array[2],instance_location_array[3]],[0,0]]
                
                self.__instances_location_dict[instance_name][2][0] = ins_process_constant_group['dloc'][instance_location_array[0]-1]
                self.__instances_location_dict[instance_name][2][1] = ins_process_constant_group['dloc'][instance_location_array[1]-1] + len(ins_process_constant_group['dof'][instance_location_array[1]-1])

            for step_name in ins_task_steps_group:
                self.__steps_info_dict[step_name] = {}
                
                self.__steps_info_dict[step_name]['sequence'] = int(ins_task_steps_group[step_name]['basic'][0])
                self.__steps_info_dict[step_name]['type'] = int(ins_task_steps_group[step_name]['basic'][1])
                self.__steps_info_dict[step_name]['time'] = float(ins_task_steps_group[step_name]['basic'][2])
                self.__steps_info_dict[step_name]['nlgeom'] = True if ins_task_steps_group[step_name]['basic'][3] == 1.0 else False

                self.__steps_info_dict[step_name]['increments'] = list(ins_task_steps_group[step_name]['parameters'][0:-2])
                self.__steps_info_dict[step_name]['increments'][0] = int(self.__steps_info_dict[step_name]['increments'][0])
                self.__steps_info_dict[step_name]['increments'][1] = int(self.__steps_info_dict[step_name]['increments'][1])
                
                self.__steps_info_dict[step_name]['lsolver'] = [int(i) for i in ins_task_steps_group[step_name]['parameters'][-2:]]

            for step_sequence in range(len(self.__steps_info_dict)+1):
                self.__displacement_info_dict[step_sequence] = []
                self.__concentrated_force_info_dict[step_sequence] = []
                self.__moment_info_dict[step_sequence] = []
            if 'displacement' in ins_task_conditions_group:
                for condition_info_array in ins_task_conditions_group['displacement']:
                    self.__displacement_info_dict['groups'].append(str(condition_info_array[0],'utf-8'))

                    for step_sequence,condition_components_btype_string in enumerate(condition_info_array[1:]):
                        if condition_components_btype_string == b'':
                            self.__displacement_info_dict[step_sequence].append([])
                        else:
                            condition_components_string_list = str(condition_components_btype_string,'utf-8').split(',')
                            self.__displacement_info_dict[step_sequence].append([*[component_string if component_string == 'N' else float(component_string) for component_string in condition_components_string_list[0:-1]],condition_components_string_list[-1]])
            else:
                pass    
            if 'concentrated force' in ins_task_conditions_group:
                for condition_info_array in ins_task_conditions_group['concentrated force']:
                    self.__concentrated_force_info_dict['groups'].append(str(condition_info_array[0],'utf-8'))

                    for step_sequence,condition_components_btype_string in enumerate(condition_info_array[1:]):
                        if condition_components_btype_string == b'':
                            self.__concentrated_force_info_dict[step_sequence].append([])
                        else:
                            condition_components_string_list = str(condition_components_btype_string,'utf-8').split(',')
                            self.__concentrated_force_info_dict[step_sequence].append([*[component_string if component_string == 'N' else float(component_string) for component_string in condition_components_string_list[0:-1]],condition_components_string_list[-1]])
            else:
                pass    
            if 'moment' in ins_task_conditions_group:
                for condition_info_array in ins_task_conditions_group['moment']:
                    self.__moment_info_dict['groups'].append(str(condition_info_array[0],'utf-8'))

                    for step_sequence,condition_components_btype_string in enumerate(condition_info_array[1:]):
                        if condition_components_btype_string == b'':
                            self.__moment_info_dict[step_sequence].append([])
                        else:
                            condition_components_string_list = str(condition_components_btype_string,'utf-8').split(',')
                            self.__moment_info_dict[step_sequence].append([*[component_string if component_string == 'N' else float(component_string) for component_string in condition_components_string_list[0:-1]],condition_components_string_list[-1]])
            else:
                pass    
            
            for variable_name in ins_task_outputs_group['Nodes']:
                self.__nodes_outputs_info_dict[variable_name] = {}
                
                ins_nodes_variable_output_group = ins_task_outputs_group['Nodes'][variable_name]

                for step_sequence in range(len(self.__steps_info_dict)+1):
                    self.__nodes_outputs_info_dict[variable_name][step_sequence] = []
                    
                    if str(step_sequence) in ins_nodes_variable_output_group:
                        for output_info_array in ins_nodes_variable_output_group[str(step_sequence)][:]:
                            group_name = str(output_info_array[0],'utf-8')
                            
                            if output_info_array[1] == b'':
                                increments_intervals_list = []
                            else:
                                increments_intervals_list = [float(i) for i in str(output_info_array[1],'utf-8').split(',')]
                            
                            if output_info_array[2] == b'':
                                time_intervals_list = []
                            else:
                                time_intervals_list = [float(i) for i in str(output_info_array[2],'utf-8').split(',')]
                            self.__nodes_outputs_info_dict[variable_name][step_sequence].append([group_name,increments_intervals_list,time_intervals_list])
                    else:
                        continue
            for variable_name in ins_task_outputs_group['Elements']:
                self.__elements_outputs_info_dict[variable_name] = {}
                
                ins_elements_variable_output_group = ins_task_outputs_group['Elements'][variable_name]

                for step_sequence in range(len(self.__steps_info_dict)+1):
                    self.__elements_outputs_info_dict[variable_name][step_sequence] = []
                    
                    if str(step_sequence) in ins_elements_variable_output_group:
                        for output_info_array in ins_elements_variable_output_group[str(step_sequence)][:]:
                            group_name = str(output_info_array[0],'utf-8')
                            
                            if output_info_array[1] == b'':
                                increments_intervals_list = []
                            else:
                                increments_intervals_list = [float(i) for i in str(output_info_array[1],'utf-8').split(',')]
                            
                            if output_info_array[2] == b'':
                                time_intervals_list = []
                            else:
                                time_intervals_list = [float(i) for i in str(output_info_array[2],'utf-8').split(',')]
                            self.__elements_outputs_info_dict[variable_name][step_sequence].append([group_name,increments_intervals_list,time_intervals_list])
                    else:
                        continue
        except:
            analysis_system_state = False
        else:
            analysis_system_state = True
        
        ins_task_file.close()
        ins_task_process_file.close()

        return analysis_system_state
    
    def startAnalysis(self) -> None:
        steps_name_by_sequence_list = [None for _ in self.__steps_info_dict]
        for step_name in self.__steps_info_dict:
            steps_name_by_sequence_list[self.__steps_info_dict[step_name]['sequence']-1] = step_name
        
        for step_name in steps_name_by_sequence_list:
            step_type_number = self.__steps_info_dict[step_name]['type']
            
            if step_type_number == 1:
                self.__analysis_static_step(step_name)
            else:
                pass
    def __analysis_static_step(self, in_step_name:str) -> None:
        step_sequence = self.__steps_info_dict[in_step_name]['sequence']
        step_time = self.__steps_info_dict[in_step_name]['time']
        step_nlgeom = self.__steps_info_dict[in_step_name]['nlgeom']
        step_increments_params_list = self.__steps_info_dict[in_step_name]['increments']
        step_lsolver_params_list = self.__steps_info_dict[in_step_name]['lsolver']
        
        ins_task_process_file = h5py.File(self.__task_process_file_full_name,'r+')
        ins_task_process_constant_group = ins_task_process_file['Constant']
        ins_task_process_update_group = ins_task_process_file['Update']
        ins_task_process_record_group = ins_task_process_file['Record']
        
        computing_time, increments_number = 0.0, 0
        increment_time = step_increments_params_list[2]
        
        before_step_include_displacement_conditions_list = self.__displacement_info_dict[step_sequence-1]
        current_step_include_displacement_conditions_list = self.__displacement_info_dict[step_sequence]
        if self.__model_dimension == '2D':
            displacement_components_dof_list = [1,2,6]
        elif self.__model_dimension == '3D':
            displacement_components_dof_list = [1,2,3,4,5,6]
        else:
            pass
        dofs_initial_location_array = ins_task_process_record_group['u'][:]
        current_step_release_dof_list, current_step_release_reaction_force =  [], []
        for condition_index,group_name in enumerate(self.__displacement_info_dict['groups']):
            before_components_list = before_step_include_displacement_conditions_list[condition_index]
            current_components_list = current_step_include_displacement_conditions_list[condition_index]
            if current_components_list == []:
                continue
            elif before_components_list == []:
                continue
            else:
                pass
            
            for component_dof,before_component,current_component in zip(displacement_components_dof_list,before_components_list,current_components_list):
                if before_component != 'N' and current_component == 'N':
                    for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                        node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                        if component_dof in node_include_dofs_array:
                            component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]
                            
                            current_step_release_dof_list.append(component_dof_location)
                            current_step_release_reaction_force.append(ins_task_process_record_group['rfm'][component_dof_location])
                            ins_task_process_record_group['rfm'][component_dof_location] = 0.0
                        else:
                            continue
                else:
                    continue
        ins_task_process_record_group['fm'][current_step_release_dof_list] += numpy.asarray(current_step_release_reaction_force)

        before_step_include_concentrated_force_conditions_list = self.__concentrated_force_info_dict[step_sequence-1]
        current_step_include_concentrated_force_conditions_list = self.__concentrated_force_info_dict[step_sequence]
        if self.__model_dimension == '2D':
            concentrated_force_components_dof_list = [1,2]
        elif self.__model_dimension == '3D':
            concentrated_force_components_dof_list = [1,2,3]
        else:
            pass
        
        before_step_include_moment_conditions_list = self.__moment_info_dict[step_sequence-1]
        current_step_include_moment_conditions_list = self.__moment_info_dict[step_sequence]
        if self.__model_dimension == '2D':
            moment_components_dof_list = [6]
        elif self.__model_dimension == '3D':
            moment_components_dof_list = [4,5,6]
        else:
            pass
        
        total_dofs_number = ins_task_process_update_group['deltau'].shape[0]
        
        ins_task_result_file = h5py.File(self.__task_result_file_full_name,'r+')
        ins_task_resutl_mesh_group = ins_task_result_file['Mesh']
        ins_task_resutl_steps_group = ins_task_result_file['Steps']
        
        current_step_include_nodes_outputs_dict = {}
        for variable_name in self.__nodes_outputs_info_dict:
            if step_sequence in self.__nodes_outputs_info_dict[variable_name]:
                current_step_include_nodes_outputs_dict[variable_name] = self.__nodes_outputs_info_dict[variable_name][step_sequence]
            else:
                continue
        current_step_include_elements_outputs_dict = {}
        for variable_name in self.__elements_outputs_info_dict:
            if step_sequence in self.__elements_outputs_info_dict[variable_name]:
                current_step_include_elements_outputs_dict[variable_name] = self.__elements_outputs_info_dict[variable_name][step_sequence]
            else:
                continue
        for variable_name,outputs_parameters_list in current_step_include_nodes_outputs_dict.items():
            for output_parameters_list in outputs_parameters_list:
                common.P4SOutputInfo.add_data_to_result_file[variable_name](self.__model_dimension,in_step_name,output_parameters_list[0],0,ins_task_result_file,ins_task_process_file)
        for variable_name,outputs_parameters_list in current_step_include_elements_outputs_dict.items():
            for output_parameters_list in outputs_parameters_list:
                common.P4SOutputInfo.add_data_to_result_file[variable_name](self.__model_dimension,in_step_name,output_parameters_list[0],0,ins_task_result_file,ins_task_process_file)
        
        step_include_time_points = [0.0]
        while True:
            increments_number += 1

            ins_task_process_update_group['deltau'][:] = 0.0
            fixed_dof_list = []
            for condition_index,group_name in enumerate(self.__displacement_info_dict['groups']):
                current_components_list = current_step_include_displacement_conditions_list[condition_index]
                if current_components_list == []:
                    continue
                else:
                    pass
                before_components_list = before_step_include_displacement_conditions_list[condition_index]
                
                current_function_name = current_step_include_displacement_conditions_list[condition_index][-1]
                if current_function_name == 'None':
                    current_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint((computing_time+increment_time)/step_time,numpy.array([0.0,1.0,0.0,1.0]))
                    before_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint(computing_time/step_time,numpy.array([0.0,1.0,0.0,1.0]))
                else:
                    function_type_number,*function_params_list = ins_task_process_constant_group['Functions'][current_function_name][:]
                    if function_type_number == 1:
                        current_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint((computing_time+increment_time)/step_time,function_params_list)
                        before_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint(computing_time/step_time,function_params_list)
                    elif function_type_number == 2:
                        pass
                    elif function_type_number == 3:
                        pass
                    else:
                        pass
                
                for component_index,component_dof in enumerate(displacement_components_dof_list):
                    current_component = current_components_list[component_index]
                    if current_component == 'N':
                        continue
                    else:
                        pass
                    
                    if current_component == 0.0:
                        for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                            node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                            if component_dof in node_include_dofs_array:
                                component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                if dofs_initial_location_array[component_dof_location]==0.0:
                                    fixed_dof_list.append(component_dof_location)
                                else:
                                    ins_task_process_update_group['deltau'][component_dof_location] = -dofs_initial_location_array[component_dof_location]*(increment_time/step_time)
                            else:
                                continue
                    elif increments_number == 1:
                        if current_function_name == 'None': 
                            for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                                node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                                if component_dof in node_include_dofs_array:
                                    component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                    if current_component == dofs_initial_location_array[component_dof_location]:
                                        fixed_dof_list.append(component_dof_location)
                                    else:
                                        ins_task_process_update_group['deltau'][component_dof_location] = (current_component-dofs_initial_location_array[component_dof_location])*(current_increment_function_amplitude-before_increment_function_amplitude)
                                else:
                                    continue
                        else:
                            current_component *= current_increment_function_amplitude
                            for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                                node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                                if component_dof in node_include_dofs_array:
                                    component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                    if current_component == dofs_initial_location_array[component_dof_location]:
                                        fixed_dof_list.append(component_dof_location)
                                    else:
                                        ins_task_process_update_group['deltau'][component_dof_location] = current_component-dofs_initial_location_array[component_dof_location]
                                else:
                                    continue
                    else:
                        if current_function_name == 'None': 
                            for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                                node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                                if component_dof in node_include_dofs_array:
                                    component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                    if current_component == dofs_initial_location_array[component_dof_location]:
                                        fixed_dof_list.append(component_dof_location)
                                    else:
                                        ins_task_process_update_group['deltau'][component_dof_location] = (current_component-dofs_initial_location_array[component_dof_location])*(current_increment_function_amplitude-before_increment_function_amplitude)
                                else:
                                    continue
                        else:
                            current_component *= (current_increment_function_amplitude-before_increment_function_amplitude)
                            if current_component == 0.0:
                                for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                                    node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                                    if component_dof in node_include_dofs_array:
                                        component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                        fixed_dof_list.append(component_dof_location)
                                    else:
                                        continue
                            else:
                                for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                                    node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                                    if component_dof in node_include_dofs_array:
                                        component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                        ins_task_process_update_group['deltau'][component_dof_location] = current_component
                                    else:
                                        continue
            fixed_dof_list.sort()
            
            ins_task_process_update_group['deltaf'][:] = 0.0
            for condition_index,group_name in enumerate(self.__concentrated_force_info_dict['groups']):
                current_components_list = current_step_include_concentrated_force_conditions_list[condition_index]
                if current_components_list == []:
                    continue
                else:
                    pass
                
                before_components_list = before_step_include_concentrated_force_conditions_list[condition_index]
                if before_components_list == []:
                    initial_componens_list = [0.0 for _ in concentrated_force_components_dof_list]
                else:
                    initial_componens_list = [0.0 if component_value == 'N' else component_value for component_value in before_components_list[0:-1]]
                    if before_components_list[-1] == 'None':
                        pass
                    else:
                        function_type_number,*function_params_list = ins_task_process_constant_group['Functions'][before_components_list[-1]][:]
                        if function_type_number == 1:
                            initial_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint(1.0,function_params_list)
                        elif function_type_number == 2:
                            pass
                        elif function_type_number == 3:
                            pass
                        else:
                            pass
                
                        initial_componens_list = [initial_function_amplitude*component_value for component_value in initial_componens_list]
                
                current_function_name = current_step_include_concentrated_force_conditions_list[condition_index][-1]
                if current_function_name == 'None':
                    current_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint((computing_time+increment_time)/step_time,numpy.array([0.0,1.0,0.0,1.0]))
                    before_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint(computing_time/step_time,numpy.array([0.0,1.0,0.0,1.0]))
                else:
                    function_type_number,*function_params_list = ins_task_process_constant_group['Functions'][current_function_name][:]
                    if function_type_number == 1:
                        current_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint((computing_time+increment_time)/step_time,function_params_list)
                        before_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint(computing_time/step_time,function_params_list)
                    elif function_type_number == 2:
                        pass
                    elif function_type_number == 3:
                        pass
                    else:
                        pass
                
                for component_index,component_dof in enumerate(concentrated_force_components_dof_list):
                    current_component = 0.0 if current_components_list[component_index] == 'N' else current_components_list[component_index]
                    initial_component = initial_componens_list[component_index]
                    
                    if current_component == 0.0:
                        if initial_component == 0.0:
                            continue
                        else:
                            increment_component = -initial_component*(current_increment_function_amplitude-before_increment_function_amplitude)

                            for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                                node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                                if component_dof in node_include_dofs_array:
                                    component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                    ins_task_process_update_group['deltaf'][component_dof_location] += increment_component
                                else:
                                    continue
                    elif increments_number == 1:
                        if current_function_name == 'None':
                            pass
                        else:
                            current_component *= current_increment_function_amplitude
                        
                        if current_component == initial_component:
                            continue
                        else:
                            increment_component = (current_component-initial_component)*(current_increment_function_amplitude-before_increment_function_amplitude)

                            for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                                node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                                if component_dof in node_include_dofs_array:
                                    component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                    ins_task_process_update_group['deltaf'][component_dof_location] += increment_component
                                else:
                                    continue
                    else:
                        if current_function_name == 'None' and current_component == initial_component:
                            continue
                        else:
                            pass
                        
                        increment_component = (current_component-initial_component)*(current_increment_function_amplitude-before_increment_function_amplitude)
                        
                        for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                            node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                            if component_dof in node_include_dofs_array:
                                component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                ins_task_process_update_group['deltaf'][component_dof_location] += increment_component
                            else:
                                continue
            for condition_index,group_name in enumerate(self.__moment_info_dict['groups']):
                current_components_list = current_step_include_moment_conditions_list[condition_index]
                if current_components_list == []:
                    continue
                else:
                    pass
                
                before_components_list = before_step_include_moment_conditions_list[condition_index]
                if before_components_list == []:
                    initial_componens_list = [0.0 for _ in moment_components_dof_list]
                else:
                    initial_componens_list = [0.0 if component_value == 'N' else component_value for component_value in before_components_list[0:-1]]
                    if before_components_list[-1] == 'None':
                        pass
                    else:
                        function_type_number,*function_params_list = ins_task_process_constant_group['Functions'][before_components_list[-1]][:]
                        if function_type_number == 1:
                            initial_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint(1.0,function_params_list)
                        elif function_type_number == 2:
                            pass
                        elif function_type_number == 3:
                            pass
                        else:
                            pass
                
                        initial_componens_list = [initial_function_amplitude*component_value for component_value in initial_componens_list]
                
                current_function_name = current_step_include_moment_conditions_list[condition_index][-1]
                if current_function_name == 'None':
                    current_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint((computing_time+increment_time)/step_time,numpy.array([0.0,1.0,0.0,1.0]))
                    before_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint(computing_time/step_time,numpy.array([0.0,1.0,0.0,1.0]))
                else:
                    function_type_number,*function_params_list = ins_task_process_constant_group['Functions'][current_function_name][:]
                    if function_type_number == 1:
                        current_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint((computing_time+increment_time)/step_time,function_params_list)
                        before_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint(computing_time/step_time,function_params_list)
                    elif function_type_number == 2:
                        pass
                    elif function_type_number == 3:
                        pass
                    else:
                        pass
                
                for component_index,component_dof in enumerate(moment_components_dof_list):
                    current_component = 0.0 if current_components_list[component_index] == 'N' else current_components_list[component_index]
                    initial_component = initial_componens_list[component_index]
                    
                    if current_component == 0.0:
                        if initial_component == 0.0:
                            continue
                        else:
                            increment_component = -initial_component*(current_increment_function_amplitude-before_increment_function_amplitude)

                            for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                                node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                                if component_dof in node_include_dofs_array:
                                    component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                    ins_task_process_update_group['deltaf'][component_dof_location] += increment_component
                                else:
                                    continue
                    elif increments_number == 1:
                        if current_function_name == 'None':
                            pass
                        else:
                            current_component *= current_increment_function_amplitude
                        
                        if current_component == initial_component:
                            continue
                        else:
                            increment_component = (current_component-initial_component)*(current_increment_function_amplitude-before_increment_function_amplitude)

                            for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                                node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                                if component_dof in node_include_dofs_array:
                                    component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                    ins_task_process_update_group['deltaf'][component_dof_location] += increment_component
                                else:
                                    continue
                    else:
                        if current_function_name == 'None' and current_component == initial_component:
                            continue
                        else:
                            pass
                        
                        increment_component = (current_component-initial_component)*(current_increment_function_amplitude-before_increment_function_amplitude)
                        
                        for node_label in ins_task_process_constant_group['NGroups'][group_name]:
                            node_include_dofs_array = ins_task_process_constant_group['dof'][node_label-1]
                            if component_dof in node_include_dofs_array:
                                component_dof_location = ins_task_process_constant_group['dloc'][node_label-1] + numpy.where(node_include_dofs_array==component_dof)[0][0]    

                                ins_task_process_update_group['deltaf'][component_dof_location] += increment_component
                            else:
                                continue
            
            current_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint((computing_time+increment_time)/step_time,numpy.array([0.0,1.0,0.0,1.0]))
            before_increment_function_amplitude = tools.getPiecewiseFunctionAmplitudeFromPoint(computing_time/step_time,numpy.array([0.0,1.0,0.0,1.0]))
            for release_dof_location,release_dof_reaction_force in zip(current_step_release_dof_list, current_step_release_reaction_force):
                ins_task_process_update_group['deltaf'][release_dof_location] += -release_dof_reaction_force*(current_increment_function_amplitude-before_increment_function_amplitude)
            
            global_stiffness_matrix = scipy.sparse.coo_matrix((ins_task_process_update_group['gkm'][0,:],(ins_task_process_update_group['gkm'][1,:],ins_task_process_update_group['gkm'][2,:])),shape=(total_dofs_number,total_dofs_number))

            processed_delta_f_array = ins_task_process_update_group['deltaf'][:]
            processed_delta_f_array -= global_stiffness_matrix.dot(ins_task_process_update_group['deltau'][:])
            
            moved_delta_u_dofs_location_array = numpy.where(ins_task_process_update_group['deltau'][:] != 0.0)[0]
            processed_delta_f_array[moved_delta_u_dofs_location_array] = ins_task_process_update_group['deltau'][moved_delta_u_dofs_location_array]
            for moved_delta_u_dof_location in moved_delta_u_dofs_location_array:
                global_stiffness_matrix.data[numpy.where(global_stiffness_matrix.row == moved_delta_u_dof_location)] = 0.0
                global_stiffness_matrix.data[numpy.where(global_stiffness_matrix.col == moved_delta_u_dof_location)] = 0.0
            
            processed_delta_f_array[fixed_dof_list] = 0.0
            for fixed_delta_u_dof_location in fixed_dof_list:
                global_stiffness_matrix.data[numpy.where(global_stiffness_matrix.row == fixed_delta_u_dof_location)] = 0.0
                global_stiffness_matrix.data[numpy.where(global_stiffness_matrix.col == fixed_delta_u_dof_location)] = 0.0
            
            global_stiffness_matrix = global_stiffness_matrix.todok()
            for moved_delta_u_dof_location in moved_delta_u_dofs_location_array:
                global_stiffness_matrix[moved_delta_u_dof_location,moved_delta_u_dof_location] = 1.0
            for fixed_delta_u_dof_location in fixed_dof_list:
                global_stiffness_matrix[fixed_delta_u_dof_location,fixed_delta_u_dof_location] = 1.0
            
            global_stiffness_matrix = global_stiffness_matrix.tocsr()
            for instance_name in ins_task_process_constant_group['Instances']:
                instance_start_dof_location,instance_end_dof_location = ins_task_process_constant_group['Instances'][instance_name][:]

                instance_include_global_stiffness_matrix = global_stiffness_matrix[instance_start_dof_location:instance_end_dof_location+1,:][:,instance_start_dof_location:instance_end_dof_location+1]
                matrix_non_all_zero_rows_index_array = numpy.where(instance_include_global_stiffness_matrix.getnnz(axis=0) > 0)[0]
                
                solved_global_stiffness_matrix = instance_include_global_stiffness_matrix[matrix_non_all_zero_rows_index_array,:][:,matrix_non_all_zero_rows_index_array]
                
                solved_delta_f_array = processed_delta_f_array[instance_start_dof_location+matrix_non_all_zero_rows_index_array]
                
                solved_non_zero_rows_delta_u_array = tools.lsolver_dict[step_lsolver_params_list[0]][step_lsolver_params_list[1]](solved_global_stiffness_matrix,solved_delta_f_array)
                
                ins_task_process_update_group['deltau'][instance_start_dof_location+matrix_non_all_zero_rows_index_array] = solved_non_zero_rows_delta_u_array
            
            ins_task_process_record_group['u'][:] += ins_task_process_update_group['deltau']
            ins_task_process_record_group['fm'][:] += ins_task_process_update_group['deltaf']
            
            global_stiffness_matrix = scipy.sparse.csr_matrix((ins_task_process_update_group['gkm'][0,:],(ins_task_process_update_group['gkm'][1,:],ins_task_process_update_group['gkm'][2,:])),shape=(total_dofs_number,total_dofs_number))
            ins_task_process_record_group['rfm'][fixed_dof_list] += global_stiffness_matrix[fixed_dof_list,:].dot(ins_task_process_update_group['deltau'][:])
            ins_task_process_record_group['rfm'][moved_delta_u_dofs_location_array] += global_stiffness_matrix[moved_delta_u_dofs_location_array,:].dot(ins_task_process_update_group['deltau'][:])
            
            self.__calculateIntegerationPointsStrainAndStress(ins_task_resutl_mesh_group,ins_task_process_update_group,ins_task_process_constant_group,ins_task_process_record_group)
            
            computing_time += increment_time
            step_include_time_points.append(computing_time)
            
            for variable_name,outputs_parameters_list in current_step_include_nodes_outputs_dict.items():
                for output_parameters_list in outputs_parameters_list:
                    output_state = False
                    for increment_interval in output_parameters_list[1]:
                        if increments_number%increment_interval == 0.0:
                            output_state = True
                            break
                        else:
                            continue
                    for time_interval in output_parameters_list[2]:
                        if time_interval == -1 and abs(computing_time-step_time) <= 1e-10:
                            output_state = True
                            break
                        elif computing_time%time_interval == 0.0:
                            output_state = True
                            break
                        else:
                            continue
                    
                    if output_state:
                        common.P4SOutputInfo.add_data_to_result_file[variable_name](self.__model_dimension,in_step_name,output_parameters_list[0],increments_number,ins_task_result_file,ins_task_process_file)
                    else:
                        continue
            
            for variable_name,outputs_parameters_list in current_step_include_elements_outputs_dict.items():
                for output_parameters_list in outputs_parameters_list:
                    output_state = False
                    for increment_interval in output_parameters_list[1]:
                        if increments_number%increment_interval == 0.0:
                            output_state = True
                            break
                        else:
                            continue
                    for time_interval in output_parameters_list[2]:
                        if time_interval == -1 and abs(computing_time-step_time) <= 1e-10:
                            output_state = True
                            break
                        elif computing_time%time_interval == 0.0:
                            output_state = True
                            break
                        else:
                            continue
                    
                    if output_state:
                        common.P4SOutputInfo.add_data_to_result_file[variable_name](self.__model_dimension,in_step_name,output_parameters_list[0],increments_number,ins_task_result_file,ins_task_process_file)
                    else:
                        continue
            
            if abs(computing_time-step_time) <= 1e-10 or increments_number >= step_increments_params_list[0]:
                break
            else:
                pass
            
            if step_increments_params_list[1] == 1:
                increment_time = step_increments_params_list[2]
                if computing_time + increment_time > step_time:
                    increment_time = step_time - computing_time
                else:
                    pass
            elif step_increments_params_list[1] == 2:
                pass
            else:
                pass

        ins_task_resutl_steps_group[in_step_name][:] = numpy.asarray(step_include_time_points)

        ins_task_result_file.close()
        ins_task_process_file.close()

    def __calculateIntegerationPointsStrainAndStress(self, in_ins_task_resutl_mesh_group:object, in_ins_task_process_update_group:object, in_ins_task_process_constant_group:object, in_ins_task_process_record_group:object) -> None:
        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
        if available_cpu_number <= 0:
            print(f"The CPU usage is too high!")
            raise ChildProcessError()
        else:
            pass
        
        all_elements_number = in_ins_task_resutl_mesh_group['elements'].shape[0]
        if all_elements_number < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
            available_cpu_number = 1
        else:
            pass
        process_elements_index_range_list = [[0,int(all_elements_number/available_cpu_number)]]
        for process_index in range(1,available_cpu_number):
            process_elements_index_range_list.append([process_elements_index_range_list[process_index-1][1],process_elements_index_range_list[process_index-1][1]+process_elements_index_range_list[0][1]])
        process_elements_index_range_list[-1][1] = all_elements_number
        
        processes_list = []
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        for process_id,index_range in enumerate(process_elements_index_range_list):
            temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.femtemp'
            with h5py.File(temp_file_full_name,'w') as ins_fem_temp_file:
                ins_fem_temp_file.create_dataset(name='readyelements',data=in_ins_task_resutl_mesh_group['elements'][index_range[0]:index_range[1]])
                ins_fem_temp_file.create_dataset(name='readyelementstm',data=in_ins_task_process_update_group['tm'][index_range[0]:index_range[1]])
                ins_fem_temp_file.create_dataset(name='readyelementsbm',data=in_ins_task_process_update_group['bm'][index_range[0]:index_range[1]])
                ins_fem_temp_file.create_dataset(name='readyelementsdm',data=in_ins_task_process_update_group['dm'][index_range[0]:index_range[1]])
                ins_fem_temp_file.create_dataset(name='readyelementstype',data=in_ins_task_resutl_mesh_group['type'][index_range[0]:index_range[1]])
                ins_fem_temp_file.create_dataset(name='allnodesfirstdoflocation',data=in_ins_task_process_constant_group['dloc'][:])
                ins_fem_temp_file.create_dataset(name='allnodesdofs',data=in_ins_task_process_constant_group['dof'][:])
                ins_fem_temp_file.create_dataset(name='readyelementsgeometry',data=in_ins_task_process_update_group['geometry'][index_range[0]:index_range[1]])
                ins_fem_temp_file.create_dataset(name='alldofsdeltau',data=in_ins_task_process_update_group['deltau'][:])
                
                ins_fem_temp_file.create_dataset(name='readyelementsipee',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                ins_fem_temp_file.create_dataset(name='readyelementsipes',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
        
            ins_process = multiprocessing.Process(target=common.P4SElementInfo.getElementIntegrationPointsStrainAndStress,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
            
            processes_list.append(ins_process)
            ins_process.start()
        for ins_process in processes_list:
            ins_process.join()
        
        for ins_process in processes_list:
            process_id_string = ins_process.name.split('-')[-1]
            ins_process.close()
            
            temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.femtemp'
            index_range = process_elements_index_range_list[int(process_id_string)]
            
            with h5py.File(temp_file_full_name,'r') as ins_fem_temp_file:
                for lcoal_index,element_index in enumerate(range(index_range[0],index_range[1])):
                    in_ins_task_process_record_group['ipee'][element_index] += ins_fem_temp_file['readyelementsipee'][lcoal_index]
                    in_ins_task_process_record_group['ipes'][element_index] += ins_fem_temp_file['readyelementsipes'][lcoal_index]
            os.remove(temp_file_full_name)
        del processes_list
