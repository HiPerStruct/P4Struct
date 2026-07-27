# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import datetime
import csv
import shutil
import psutil
import multiprocessing
import glob

import h5py
import numpy
import scipy.sparse

from config import common
from .finite_element_analysis import _femTaskAnalysisSystem
from .tools import lsolver_dict,osolver_dict


def intoOPTProcess(in_optimization_type:str, in_task_flie_full_name:str, in_ins_task_process_queen:object):
    tak_folder_name = os.path.dirname(in_task_flie_full_name)
    task_name = os.path.basename(in_task_flie_full_name).split('.')[0]

    with h5py.File(in_task_flie_full_name,'r') as ins_optim_file:
        fea_task_name = str(ins_optim_file['Basic']['parameters'][1],'utf-8')
    fea_task_file_full_name = tak_folder_name + os.sep + fea_task_name + '.task'
    task_process_file_full_name = tak_folder_name + os.sep + task_name + '.pro'
    task_result_file_full_name = tak_folder_name + os.sep + task_name + '.res'

    if in_optimization_type == 'topology optimization':
        ins_optimization_task_analysis_system = _topologyOptTaskAnalysisSystem(fea_task_file_full_name,in_task_flie_full_name,task_process_file_full_name,task_result_file_full_name)
    else:
        pass
    optimization_system_state = ins_optimization_task_analysis_system.initializeSystems()
    process_file_state = ins_optimization_task_analysis_system.initializeProcessFile()
    result_file_state = ins_optimization_task_analysis_system.initializeResultFile()
    if optimization_system_state and process_file_state and result_file_state:
        pass
    else:
        in_ins_task_process_queen.put([task_name,'error'])
        return None
    
    start_time_point = datetime.datetime.now()
    try:
        ins_optimization_task_analysis_system.startAnalysis()
    except:
        in_ins_task_process_queen.put([task_name,'error'])
    else:
        end_time_point = datetime.datetime.now()
        total_analysis_time = end_time_point - start_time_point
        in_ins_task_process_queen.put([task_name,str(total_analysis_time)])

class _topologyOptTaskAnalysisSystem():
    def __init__(self, in_fea_task_file_full_name:str, in_task_file_full_name:str,in_task_process_file_full_name:str,in_task_result_file_full_name:str) -> None:
        self.__fea_task_file_full_name = in_fea_task_file_full_name
        self.__task_file_full_name = in_task_file_full_name
        self.__task_process_file_full_name = in_task_process_file_full_name
        self.__task_result_file_full_name = in_task_result_file_full_name

        self.__task_folder_name = os.path.dirname(in_task_file_full_name)
        self.__model_dimension = None
        
        self.__design_domain_name = None
        self.__maximum_iteration_number = None
        self.__data_save_list = []
        self.__target = None
        
        self.__objectives_list = []
        self.__constrains_list = []
        
        self.__density_list = []
        self.__convergence_list = []
        self.__interpolation_model = []
        self.__optimizer = None
        self.__filter_list = []
        self.__binaryzation_list = []

    def initializeSystems(self) -> bool:
        try:
            with h5py.File(self.__fea_task_file_full_name,'r') as ins_fea_task_file:
                self.__model_dimension = str(ins_fea_task_file['basic'][0],'utf-8')
            
            with h5py.File(self.__task_file_full_name,'r') as ins_optim_file:
                ins_basic_group = ins_optim_file['Basic']
                self.__design_domain_name = str(ins_basic_group['parameters'][2],'utf-8')
                self.__maximum_iteration_number =  int(str(ins_basic_group['parameters'][3],'utf-8'))
                self.__data_save_list.append(str(ins_basic_group['parameters'][4],'utf-8'))
                self.__data_save_list.append(str(ins_basic_group['parameters'][5],'utf-8'))
                self.__target = str(ins_basic_group['parameters'][6],'utf-8')
                
                if self.__data_save_list[1] == '':
                    self.__data_save_list[1] = 0
                else:
                    self.__data_save_list[1] = int(self.__data_save_list[1])
                
                for parameters_array in ins_basic_group['objectives'][:]:
                    parameters_list = []
                    
                    parameters_list.append(str(parameters_array[0],'utf-8'))
                    parameters_list.append(str(parameters_array[1],'utf-8'))
                    parameters_list.append(str(parameters_array[2],'utf-8'))
                    
                    self.__objectives_list.append(parameters_list)
                if 'constrains' in ins_basic_group:
                    for parameters_array in ins_basic_group['constrains'][:]:
                        parameters_list = []
                        
                        parameters_list.append(str(parameters_array[0],'utf-8'))
                        parameters_list.append(str(parameters_array[1],'utf-8'))
                        parameters_list.append(str(parameters_array[2],'utf-8'))
                        parameters_list.append(str(parameters_array[3],'utf-8'))
                        parameters_list.append(float(str(parameters_array[4],'utf-8')))
                        
                        self.__constrains_list.append(parameters_list)
                else:
                    pass
                
                ins_topopt_group = ins_optim_file['TopologyOptimization']
                self.__density_list = [i for i in ins_topopt_group['density'][:]]
                self.__convergence_list.append(str(ins_topopt_group['convergence'][0],'utf-8'))
                self.__convergence_list.append(float(str(ins_topopt_group['convergence'][1],'utf-8')))
                self.__convergence_list.append(float(str(ins_topopt_group['convergence'][2],'utf-8')))
                self.__convergence_list.append(int(str(ins_topopt_group['convergence'][3],'utf-8')))
                self.__interpolation_model.append(str(ins_topopt_group['algorithm'][0],'utf-8'))
                self.__interpolation_model.append(float(str(ins_topopt_group['algorithm'][1],'utf-8')))
                self.__optimizer = str(ins_topopt_group['algorithm'][2],'utf-8')
                self.__filter_list.append(str(ins_topopt_group['filter'][0],'utf-8'))
                self.__filter_list.append(str(ins_topopt_group['filter'][1],'utf-8'))
                self.__filter_list.append(float(str(ins_topopt_group['filter'][2],'utf-8')))
                self.__filter_list.append(str(ins_topopt_group['filter'][3],'utf-8'))
                self.__binaryzation_list.append(str(ins_topopt_group['binaryzation'][0],'utf-8'))
                self.__binaryzation_list.append(float(str(ins_topopt_group['binaryzation'][1],'utf-8')))
                self.__binaryzation_list.append(int(str(ins_topopt_group['binaryzation'][2],'utf-8')))
        except:
            system_generate_state = False
        else:
            system_generate_state = True
        
        return system_generate_state
    def initializeProcessFile(self) -> bool:
        ins_fea_task_file = h5py.File(self.__fea_task_file_full_name,'r')
        ins_model_mesh_group = ins_fea_task_file['Mesh']
        ins_design_domain_elements_lable_group_set = ins_model_mesh_group['Groups']['Elements'][self.__design_domain_name]
        elements_number = ins_model_mesh_group['elements'].shape[0]
        
        try:
            with h5py.File(self.__task_process_file_full_name, 'w') as ins_process_file:
                ins_instances_design_domain_group = ins_process_file.create_group(name='Domains')
                for instance_name in ins_model_mesh_group['Instances']:
                    start_element_label = ins_model_mesh_group['Instances'][instance_name][2]
                    design_elements_label_array = ins_design_domain_elements_lable_group_set[ins_design_domain_elements_lable_group_set[:]>=start_element_label]
                    end_element_label = ins_model_mesh_group['Instances'][instance_name][3]
                    design_elements_label_array = design_elements_label_array[design_elements_label_array<=end_element_label]
                    ins_instances_design_domain_group.create_dataset(name=instance_name,data=numpy.sort(design_elements_label_array),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                del start_element_label,end_element_label
                del design_elements_label_array
                
                ins_topopt_group = ins_process_file.create_group(name='TopOpt')
                ins_topopt_group.create_dataset(name='x',data=numpy.ones(shape=(4,elements_number)),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                ins_topopt_group.create_dataset(name='chaingrad',data=numpy.ones(shape=(2,elements_number)),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                ins_neighbor_set = ins_topopt_group.create_dataset(name='neighbor',shape=(elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                ins_weight_set = ins_topopt_group.create_dataset(name='weight',shape=(elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                if self.__filter_list[1] == 'common':
                    if self.__filter_list[2] == 0.0:
                        if self.__filter_list[3] == 'No':
                            for ins_design_elements_label_set in ins_instances_design_domain_group.values():
                                for element_label in ins_design_elements_label_set[:]:
                                    ins_neighbor_set[element_label-1] = numpy.array([element_label],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                                    ins_weight_set[element_label-1] = numpy.array([1.0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                        else:
                            for instance_label_range in ins_model_mesh_group['Instances'].values():
                                for element_index in range(instance_label_range[2]-1,instance_label_range[3]):
                                    ins_neighbor_set[element_index] = numpy.array([element_index+1],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                                    ins_weight_set[element_index] = numpy.array([1.0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    else:
                        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
                        if available_cpu_number <= 0:
                            print(f"The CPU usage is too high!")
                            raise ChildProcessError()
                        else:
                            pass
                        if elements_number < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
                            available_cpu_number = 1
                        else:
                            pass
                        
                        temp_file_head_name = self.__task_file_full_name.split('.')[0]
                        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
                        
                        ins_center_set = ins_topopt_group.create_dataset(name='center',shape=(elements_number,3),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                        for instance_name,ins_design_elements_label_set in ins_instances_design_domain_group.items():
                            ins_instance_label_range_set = ins_model_mesh_group['Instances'][instance_name]
                            
                            if self.__filter_list[3] == 'No':
                                process_local_index_range_list = [[0,int(ins_design_elements_label_set.shape[0]/available_cpu_number)]]
                                for process_index in range(1,available_cpu_number):
                                    process_local_index_range_list.append([process_local_index_range_list[process_index-1][1],process_local_index_range_list[process_index-1][1]+process_local_index_range_list[0][1]])
                                process_local_index_range_list[-1][1] = ins_design_elements_label_set.shape[0]
                                
                                processes_list = []
                                for process_id,index_range in enumerate(process_local_index_range_list):
                                    temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                                    with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                                        ins_opt_temp_file.create_dataset(name='readyelements',data=ins_model_mesh_group['elements'][ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                                        ins_opt_temp_file.create_dataset(name='startnodelabel',data=numpy.array([ins_instance_label_range_set[0]],dtype=common.P4SFormat.NUMERICAL_PRECISION['int']))
                                        ins_opt_temp_file.create_dataset(name='instancenodes',data=ins_model_mesh_group['nodes'][ins_instance_label_range_set[0]-1:ins_instance_label_range_set[1]])
                                        
                                        ins_opt_temp_file.create_dataset(name='readyelementscenter',shape=(index_range[1]-index_range[0],3),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                                        
                                    ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsCenter,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                                    processes_list.append(ins_process)

                                    ins_process.start()
                                for ins_process in processes_list:
                                    ins_process.join()
                                
                                for ins_process in processes_list:
                                    process_id_string = ins_process.name.split('-')[-1]
                                    ins_process.close()
                                    
                                    temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                                    index_range = process_local_index_range_list[int(process_id_string)]
                                    
                                    with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                                        ins_center_set[ins_design_elements_label_set[index_range[0]:index_range[1]]-1,:] = ins_opt_temp_file['readyelementscenter'][:]
                                    os.remove(temp_file_full_name)
                                del processes_list
                            else:
                                process_local_index_range_list = [[0,int((ins_instance_label_range_set[3]-ins_instance_label_range_set[2]+1)/available_cpu_number)]]
                                for process_index in range(1,available_cpu_number):
                                    process_local_index_range_list.append([process_local_index_range_list[process_index-1][1],process_local_index_range_list[process_index-1][1]+process_local_index_range_list[0][1]])
                                process_local_index_range_list[-1][1] = ins_instance_label_range_set[3]-ins_instance_label_range_set[2]+1
                                
                                processes_list = []
                                for process_id,index_range in enumerate(process_local_index_range_list):
                                    temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                                    with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                                        ins_opt_temp_file.create_dataset(name='readyelements',data=ins_model_mesh_group['elements'][ins_instance_label_range_set[2]-1+index_range[0]:ins_instance_label_range_set[2]-1+index_range[1]])
                                        ins_opt_temp_file.create_dataset(name='startnodelabel',data=numpy.array([ins_instance_label_range_set[0]],dtype=common.P4SFormat.NUMERICAL_PRECISION['int']))
                                        ins_opt_temp_file.create_dataset(name='instancenodes',data=ins_model_mesh_group['nodes'][ins_instance_label_range_set[0]-1:ins_instance_label_range_set[1]])
                                        
                                        ins_opt_temp_file.create_dataset(name='readyelementscenter',shape=(index_range[1]-index_range[0],3),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                                        
                                    ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsCenter,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                                    processes_list.append(ins_process)

                                    ins_process.start()
                                for ins_process in processes_list:
                                    ins_process.join()
                                
                                for ins_process in processes_list:
                                    process_id_string = ins_process.name.split('-')[-1]
                                    ins_process.close()
                                    
                                    temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                                    index_range = process_local_index_range_list[int(process_id_string)]
                                    
                                    with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                                        ins_center_set[ins_instance_label_range_set[2]-1+index_range[0]:ins_instance_label_range_set[2]-1+index_range[1],:] = ins_opt_temp_file['readyelementscenter'][:]
                                            
                                    os.remove(temp_file_full_name)
                                del processes_list  
                        
                        for instance_name,ins_design_elements_label_set in ins_instances_design_domain_group.items():
                            ins_instance_label_range_set = ins_model_mesh_group['Instances'][instance_name]
                            
                            if self.__filter_list[3] == 'No':
                                process_local_index_range_list = [[0,int(ins_design_elements_label_set.shape[0]/available_cpu_number)]]
                                for process_index in range(1,available_cpu_number):
                                    process_local_index_range_list.append([process_local_index_range_list[process_index-1][1],process_local_index_range_list[process_index-1][1]+process_local_index_range_list[0][1]])
                                process_local_index_range_list[-1][1] = ins_design_elements_label_set.shape[0]
                                
                                processes_list = []
                                for process_id,index_range in enumerate(process_local_index_range_list):
                                    temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                                    with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                                        ins_opt_temp_file.create_dataset(name='readyelementsnumber',data=numpy.array([index_range[1]-index_range[0]],dtype=common.P4SFormat.NUMERICAL_PRECISION['int']))
                                        ins_opt_temp_file.create_dataset(name='otherelementslabel',data=ins_design_elements_label_set[index_range[0]:])
                                        ins_opt_temp_file.create_dataset(name='otherelementscenter',data=ins_center_set[ins_design_elements_label_set[index_range[0]:]-1])
                                        ins_opt_temp_file.create_dataset(name='radius',data=numpy.array([self.__filter_list[2]]))
                                        
                                        ins_opt_temp_file.create_dataset(name='otherelementsneighbors',shape=(ins_design_elements_label_set.shape[0]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                                        ins_opt_temp_file.create_dataset(name='otherelementsweight',shape=(ins_design_elements_label_set.shape[0]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                                    
                                    ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsNeighborsAndWeights,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                                    processes_list.append(ins_process)
                                
                                    ins_process.start()
                                for ins_process in processes_list:
                                    ins_process.join()
                                
                                for ins_process in processes_list:
                                    process_id_string = ins_process.name.split('-')[-1]
                                    ins_process.close()
                                    
                                    temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                                    index_range = process_local_index_range_list[int(process_id_string)]
                                    
                                    with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                                        ins_other_elements_label_set = ins_opt_temp_file['otherelementslabel']
                                        ins_other_elements_neighbors_set = ins_opt_temp_file['otherelementsneighbors']
                                        ins_other_elements_weight_set = ins_opt_temp_file['otherelementsweight']
                                
                                        for local_index in range(ins_other_elements_label_set.shape[0]):
                                            element_index = ins_other_elements_label_set[local_index]-1
                                            
                                            ins_neighbor_set[element_index] = numpy.concatenate((ins_neighbor_set[element_index][:],ins_other_elements_neighbors_set[local_index][:]),axis=None)
                                            ins_weight_set[element_index] = numpy.concatenate((ins_weight_set[element_index][:],ins_other_elements_weight_set[local_index][:]),axis=None)  
                                    os.remove(temp_file_full_name)
                                del processes_list
                            else:
                                process_local_index_range_list = [[0,int((ins_instance_label_range_set[3]-ins_instance_label_range_set[2]+1)/available_cpu_number)]]
                                for process_index in range(1,available_cpu_number):
                                    process_local_index_range_list.append([process_local_index_range_list[process_index-1][1],process_local_index_range_list[process_index-1][1]+process_local_index_range_list[0][1]])
                                process_local_index_range_list[-1][1] = ins_instance_label_range_set[3]-ins_instance_label_range_set[2]+1
                                
                                processes_list = []
                                for process_id,index_range in enumerate(process_local_index_range_list):
                                    temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                                    with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                                        ins_opt_temp_file.create_dataset(name='readyelementsnumber',data=numpy.array([index_range[1]-index_range[0]],dtype=common.P4SFormat.NUMERICAL_PRECISION['int']))
                                        ins_opt_temp_file.create_dataset(name='otherelementslabel',data=numpy.arange(ins_instance_label_range_set[2]+index_range[0],ins_instance_label_range_set[3]+1,1,dtype=common.P4SFormat.NUMERICAL_PRECISION['int']))
                                        ins_opt_temp_file.create_dataset(name='otherelementscenter',data=ins_center_set[ins_instance_label_range_set[2]-1+index_range[0]:ins_instance_label_range_set[3]])
                                        ins_opt_temp_file.create_dataset(name='radius',data=numpy.array([self.__filter_list[2]]))
                                        
                                        ins_opt_temp_file.create_dataset(name='otherelementsneighbors',shape=(ins_instance_label_range_set[3]-ins_instance_label_range_set[2]+1-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                                        ins_opt_temp_file.create_dataset(name='otherelementsweight',shape=(ins_instance_label_range_set[3]-ins_instance_label_range_set[2]+1-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))

                                    ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsNeighborsAndWeights,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                                    processes_list.append(ins_process)

                                    ins_process.start()
                                for ins_process in processes_list:
                                    ins_process.join()
                                
                                for ins_process in processes_list:
                                    process_id_string = ins_process.name.split('-')[-1]
                                    ins_process.close()
                                    
                                    temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                                    
                                    with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                                        ins_other_elements_label_set = ins_opt_temp_file['otherelementslabel']
                                        ins_other_elements_neighbors_set = ins_opt_temp_file['otherelementsneighbors']
                                        ins_other_elements_weight_set = ins_opt_temp_file['otherelementsweight']
                                
                                        for local_index in range(ins_other_elements_label_set.shape[0]):
                                            element_index = ins_other_elements_label_set[local_index]-1
                                            
                                            ins_neighbor_set[element_index] = numpy.concatenate((ins_neighbor_set[element_index][:],ins_other_elements_neighbors_set[local_index][:]),axis=None)
                                            ins_weight_set[element_index] = numpy.concatenate((ins_weight_set[element_index][:],ins_other_elements_weight_set[local_index][:]),axis=None)
                                    os.remove(temp_file_full_name)
                                del processes_list
                    
                    with h5py.File(os.path.dirname(self.__task_file_full_name) + os.sep +  'filter.infom','w') as ins_file:
                        ins_record_filter_neighbor_inform_set = ins_file.create_dataset(name='neighbor',shape=(elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                        ins_record_filter_weight_inform_set = ins_file.create_dataset(name='weight',shape=(elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
                        for local_index in range(elements_number):
                            ins_record_filter_neighbor_inform_set[local_index] = ins_neighbor_set[local_index]
                            ins_record_filter_weight_inform_set[local_index] = ins_weight_set[local_index]
                elif self.__filter_list[1] == 'file':
                    record_filter_information_file_full_name = os.path.dirname(self.__task_file_full_name) + os.sep +  'filter.infom'
                    if os.path.exists(record_filter_information_file_full_name):
                        with h5py.File(record_filter_information_file_full_name,'r') as ins_file:
                            ins_record_filter_neighbor_inform_set = ins_file['neighbor']
                            ins_record_filter_weight_inform_set = ins_file['weight']

                            for ins_design_elements_set in ins_instances_design_domain_group.values():
                                for local_index in range(ins_design_elements_set.shape[0]):
                                    if ins_record_filter_neighbor_inform_set[ins_design_elements_set[local_index]-1].shape[0] == 0:
                                        print("There is empty filter-information of design element in the filter file")

                                        raise ValueError()
                                    else:
                                        continue
                            
                            if ins_record_filter_neighbor_inform_set.shape[0] == ins_record_filter_weight_inform_set.shape[0] == elements_number:
                                for local_index in range(elements_number):
                                    ins_neighbor_set[local_index] = ins_record_filter_neighbor_inform_set[local_index]
                                    ins_weight_set[local_index] = ins_record_filter_weight_inform_set[local_index]
                            else:
                                print('The filter information file format error!')
                                raise ValueError()
                    else:
                        print('None filter information file!')
                        raise ValueError()
                else:
                    pass
                
                ins_topopt_group.create_dataset(name='ifa',data=numpy.ones(shape=elements_number),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                
                ins_sensitivity_group = ins_topopt_group.create_group(name='Sensitivity')
                for variable_name,component_name,*other in self.__objectives_list:
                    if variable_name in ins_sensitivity_group:
                        ins_sensitivity_variable_group = ins_sensitivity_group[variable_name]
                    else:
                        ins_sensitivity_variable_group = ins_sensitivity_group.create_group(name=variable_name)
                    ins_sensitivity_variable_group.create_dataset(name=component_name,data=numpy.zeros(shape=(3,elements_number)),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                for variable_name,component_name,*other in self.__constrains_list:
                        if variable_name in ins_sensitivity_group:
                            ins_sensitivity_variable_group = ins_sensitivity_group[variable_name]
                        else:
                            ins_sensitivity_variable_group = ins_sensitivity_group.create_group(name=variable_name)
                        ins_sensitivity_variable_group.create_dataset(name=component_name,data=numpy.zeros(shape=(3,elements_number)),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
        except:
            temp_files_name_list = glob.glob(os.path.dirname(self.__task_file_full_name)+os.sep+'*.opttemp')
            if temp_files_name_list == []:
                pass
            else:
                temp_file_base_name = os.path.basename(self.__task_file_full_name).split('.')[0]
                for temp_file_name in temp_files_name_list:
                    if os.path.basename(temp_file_name).split('.')[0].split('-')[0] == temp_file_base_name:
                        os.remove(temp_file_name)
                    else:
                        continue

            file_generate_state = False
        else:
            file_generate_state = True
        
        ins_fea_task_file.close()
        
        return file_generate_state
    def initializeResultFile(self) -> bool:
        ins_fea_task_file = h5py.File(self.__fea_task_file_full_name,'r')
        ins_model_mesh_group = ins_fea_task_file['Mesh']
        ins_model_outputs_group = ins_fea_task_file['Outputs'] 
        try:
            with h5py.File(self.__task_result_file_full_name,'w') as ins_task_result_file:
                ins_result_basic_set = ins_task_result_file.create_dataset(name='basic',shape=(2,),dtype=h5py.string_dtype(encoding='utf-8'))
                ins_result_basic_set[0] = ins_fea_task_file['basic'][0]
                ins_result_basic_set[1] = 'OPT'

                ins_result_mesh_group = ins_task_result_file.create_group(name='Mesh')
                # region
                ins_result_mesh_instances_group = ins_result_mesh_group.create_group(name='Instances')
                for instance_name in ins_model_mesh_group['Instances']:
                    ins_result_mesh_instances_group.create_dataset(name=instance_name,data=ins_model_mesh_group['Instances'][instance_name][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                
                ins_result_mesh_group.create_dataset(name='nodes',data=ins_model_mesh_group['nodes'][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                ins_result_mesh_group.create_dataset(name='association',data=ins_model_mesh_group['association'][:],dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                ins_result_mesh_group.create_dataset(name='elements',data=ins_model_mesh_group['elements'][:],dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
                ins_result_mesh_group.create_dataset(name='geometry',data=ins_model_mesh_group['geometry'][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                ins_result_mesh_group.create_dataset(name='type',data=ins_model_mesh_group['type'][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                
                ins_result_mesh_groups_group = ins_result_mesh_group.create_group(name='Groups')
                ins_result_mesh_nodes_groups_group = ins_result_mesh_groups_group.create_group(name='Nodes')
                for group_name in ins_model_mesh_group['Groups']['Nodes']:
                    ins_result_mesh_nodes_groups_group.create_dataset(name=group_name,data=ins_model_mesh_group['Groups']['Nodes'][group_name][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                ins_result_mesh_elements_groups_group = ins_result_mesh_groups_group.create_group(name='Elements')
                for group_name in ins_model_mesh_group['Groups']['Elements']:
                    ins_result_mesh_elements_groups_group.create_dataset(name=group_name,data=ins_model_mesh_group['Groups']['Elements'][group_name][:],dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                # endregion

                ins_task_result_file.create_group(name='Steps')
                ins_task_result_file['Steps'].create_dataset(name='optimum',shape=1,dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))

                ins_result_nodes_group = ins_task_result_file.create_group(name='Nodes')
                # region
                for variable_name in ins_model_outputs_group['Nodes']:
                    ins_result_variable_group = ins_result_nodes_group.create_group(name=variable_name)
                    ins_result_variable_group.create_group(name='optimum')
                # endregion
                
                ins_result_elements_group = ins_task_result_file.create_group(name='Elements')
                # region
                for variable_name in ins_model_outputs_group['Elements']:
                    ins_result_variable_group = ins_result_elements_group.create_group(name=variable_name)
                    ins_result_variable_group.create_group(name='optimum')
                
                for optimize_variable_name in ['X']:
                    ins_result_variable_group = ins_result_elements_group.create_group(name=optimize_variable_name)
                    ins_result_variable_group.create_group(name='optimum')
                # endregion
        except:
            file_generate_state = False
        else:
            file_generate_state = True
        ins_fea_task_file.close()
        
        return file_generate_state
    
    def startAnalysis(self) -> None:
        task_name = os.path.basename(self.__task_file_full_name).split('.')[0]
        
        print(f"The topology optimization - {task_name} is ready to run:")
        
        ins_process_file = h5py.File(self.__task_process_file_full_name, 'r+')
        ins_process_domains_group = ins_process_file['Domains']
        ins_process_topopt_group = ins_process_file['TopOpt']
        
        ins_csv_file = open(self.__task_folder_name + os.sep + task_name + '.csv', 'w', newline='', encoding='utf-8')
        ins_csv_writer = csv.writer(ins_csv_file)
        csv_head_list = [[],[]]
        for parameters_list in self.__objectives_list:
            if parameters_list[0] == 'CS':
                csv_head_list[0].append(parameters_list[0]+','+parameters_list[1]+'(Pnorm):')
            else:
                csv_head_list[0].append(parameters_list[0]+','+parameters_list[1]+':')
        for parameters_list in self.__constrains_list:
            if parameters_list[0] == 'CS':
                csv_head_list[1].append(parameters_list[0]+','+parameters_list[1]+'(Pnorm):')
            else:
                csv_head_list[1].append(parameters_list[0]+','+parameters_list[1]+':')
        ins_csv_writer.writerow(['Iter:',*csv_head_list[0],*csv_head_list[1],'maximum |delta x|:'])
        del csv_head_list
        ins_csv_file.close()

        fea_folder_name = self.__task_folder_name + os.sep + 'Opt-0'
        if os.path.exists(fea_folder_name):
            shutil.rmtree(fea_folder_name)
        else:
            pass
        os.mkdir(fea_folder_name)
        fea_process_file_full_name = fea_folder_name + os.sep + 'Opt-0.pro'
        fea_result_file_full_name = fea_folder_name + os.sep + 'Opt-0.res'
        ins_fea_system = _femTaskAnalysisSystem(self.__fea_task_file_full_name,fea_process_file_full_name,fea_result_file_full_name)
        fea_process_state = ins_fea_system.initializeProcessFile()
        fea_result_state = ins_fea_system.initializeResultFile()
        fea_system_state = ins_fea_system.initializeSystems()
        if fea_process_state and fea_result_state and fea_system_state:
            pass
        else:
            os.remove(fea_process_file_full_name)
            os.remove(fea_result_file_full_name)
            
            raise ValueError()
        try:
            ins_fea_system.startAnalysis()
        except:
            os.remove(fea_process_file_full_name)
            os.remove(fea_result_file_full_name)

            print(f"Iter 0 - finite element analysis error!")
            
            raise ValueError()
        else:
            pass
        del ins_fea_system
        
        with h5py.File(self.__task_result_file_full_name, 'r+') as ins_result_file: 
            ins_fea_result_file = h5py.File(fea_result_file_full_name, 'r')
            final_step_name = list(ins_fea_result_file['Steps'].keys())[-1]
            for variable_name in ins_fea_result_file['Nodes']:
                ins_fea_step_result_group = ins_fea_result_file['Nodes'][variable_name][final_step_name]
                frames_number_list = [int(i) for i in ins_fea_step_result_group.keys()]
                frames_number_list.sort()
                
                ins_fea_frame_result_set = ins_fea_step_result_group[str(frames_number_list[-1])]
                ins_result_file['Nodes'][variable_name]['optimum'].create_dataset(name='0',data=ins_fea_frame_result_set[:],dtype=ins_fea_frame_result_set.dtype)
            for variable_name in ins_fea_result_file['Elements']:
                ins_fea_step_result_group = ins_fea_result_file['Elements'][variable_name][final_step_name]
                frames_number_list = [int(i) for i in ins_fea_step_result_group.keys()]
                frames_number_list.sort()
                
                ins_fea_frame_result_set = ins_fea_step_result_group[str(frames_number_list[-1])]
                ins_result_file['Elements'][variable_name]['optimum'].create_dataset(name='0',data=ins_fea_frame_result_set[:],dtype=ins_fea_frame_result_set.dtype)                
            ins_fea_result_file.close()
            
            ins_result_file['Elements']['X']['optimum'].create_dataset(name='0',data=numpy.ones(shape=(1,ins_process_topopt_group['x'].shape[1])),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])                
            
            ins_result_file['Steps']['optimum'][0] = numpy.concatenate((ins_result_file['Steps']['optimum'][0],0),axis=None)
        
        if 'CS' in [i[0] for i in self.__objectives_list] or 'CS' in [i[0] for i in self.__constrains_list]:
            common.P4SOptimizationInfo.getGlobalConstrainedDOFsLocation(self.__fea_task_file_full_name, fea_process_file_full_name,ins_process_topopt_group)
            common.P4SOptimizationInfo.getElementsDOFs(self.__fea_task_file_full_name, fea_process_file_full_name,ins_process_topopt_group)
            
            ins_process_topopt_group.create_dataset(name='dpndrcs',shape=ins_process_topopt_group['x'].shape[1],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            if 'Mises' in [i[1] for i in self.__objectives_list] or 'Mises' in [i[1] for i in self.__constrains_list]:
                if self.__model_dimension == '2D':
                    ins_process_topopt_group.create_dataset(name='csc',shape=(3,ins_process_topopt_group['x'].shape[1]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                else:
                    ins_process_topopt_group.create_dataset(name='csc',shape=(6,ins_process_topopt_group['x'].shape[1]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            else:
                pass
            ins_process_topopt_group.create_dataset(name='mulmatrix',shape=(ins_process_topopt_group['x'].shape[1],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
            with h5py.File(fea_process_file_full_name,'r') as ins_fea_process_file:
                ins_process_topopt_group.create_dataset(name='adjoint',shape=(2,ins_fea_process_file['Update']['deltau'].shape[0]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            ins_process_topopt_group.create_dataset(name='elmsu',shape=(ins_process_topopt_group['x'].shape[1],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
            ins_process_topopt_group.create_dataset(name='elmsadjoint',shape=(ins_process_topopt_group['x'].shape[1],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))
            ins_process_topopt_group.create_dataset(name='dpndxphy',shape=ins_process_topopt_group['x'].shape[1],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
        else:
            pass
        
        objectives_value_list = []
        for parameters_list in self.__objectives_list:
            if parameters_list[0] == 'SE':
                objectives_value_list.append(self.__calculateSEResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
            elif parameters_list[0] == 'VOL':
                objectives_value_list.append(self.__calculateVOLResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
            elif parameters_list[0] == 'CS':
                objectives_value_list.append(self.__calculateCSResults(parameters_list, ins_process_domains_group, ins_process_topopt_group, fea_process_file_full_name))
            else:
                pass    
        constrains_value_list = []
        for parameters_list in self.__constrains_list:
            if parameters_list[0] == 'SE':
                constrains_value_list.append(self.__calculateSEResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
            elif parameters_list[0] == 'VOL':
                constrains_value_list.append(self.__calculateVOLResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
            elif parameters_list[0] == 'CS':
                constrains_value_list.append(self.__calculateCSResults(parameters_list, ins_process_domains_group, ins_process_topopt_group, fea_process_file_full_name))
            else:
                pass
        
        initial_objectives_value_list = [objective_value for objective_value in objectives_value_list]
        initial_constrains_value_list = [constrain_value for constrain_value in constrains_value_list]
        
        ins_csv_file = open(self.__task_folder_name + os.sep + task_name + '.csv', 'a', newline='', encoding='utf-8')
        ins_csv_writer = csv.writer(ins_csv_file)
        ins_csv_writer.writerow(['0',*[str(i) for i in objectives_value_list],*[str(i) for i in constrains_value_list],''])
        ins_csv_file.close()
        
        print_information_string = '\tIt:0'
        for parameters_list, objective_value in zip(self.__objectives_list,objectives_value_list):
            if parameters_list[0] == 'CS':
                print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+'(Pnorm):'+str(numpy.around(objective_value,5))
            else:
                print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+':'+str(numpy.around(objective_value,5))
        for parameters_list, constrain_value in zip(self.__constrains_list,constrains_value_list):
            if parameters_list[0] == 'CS':
                print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+'(Pnorm):'+str(numpy.around(constrain_value,5))
            else:
                print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+':'+str(numpy.around(constrain_value,5))
        print(print_information_string)
        
        for ins_design_elements_label_set in ins_process_domains_group.values():
            design_elements_index_array = ins_design_elements_label_set[:]-1
            ins_process_topopt_group['x'][0,design_elements_index_array] = self.__density_list[0]
            ins_process_topopt_group['x'][2,design_elements_index_array] = self.__density_list[0]
            ins_process_topopt_group['x'][3,design_elements_index_array] = self.__density_list[0]
            del design_elements_index_array
        if self.__filter_list[0] == 'density':
            self.__calculateFilteredDensityAndChainGradientInformation(ins_process_domains_group,ins_process_topopt_group,fea_process_file_full_name)
        else:
            ins_process_topopt_group['x'][1,:] = ins_process_topopt_group['x'][0,:]
        os.remove(fea_process_file_full_name)
        
        before_objectives_proportion_value_list = [1.0 for _ in objectives_value_list]
        ins_process_optimizer_group = ins_process_file.create_group(name='Optimizer')
        if self.__optimizer == 'ADAM':
            ins_process_optimizer_group.create_dataset(name='m',data=numpy.zeros(shape=ins_process_topopt_group['x'].shape[1]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            ins_process_optimizer_group.create_dataset(name='v',data=numpy.zeros(shape=ins_process_topopt_group['x'].shape[1]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])

            ins_process_optimizer_group.create_dataset(name='alpha',data=numpy.array([self.__density_list[3]*0.2]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            ins_process_optimizer_group.create_dataset(name='beta',data=numpy.array([0.9,0.999]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            ins_process_optimizer_group.create_dataset(name='eps',data=numpy.array([1e-8]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
        elif self.__optimizer == 'MMA':
            ins_process_optimizer_group.create_dataset(name='low',data=numpy.full(shape=ins_process_topopt_group['x'].shape[1],fill_value=self.__density_list[1]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            ins_process_optimizer_group.create_dataset(name='upp',data=numpy.full(shape=ins_process_topopt_group['x'].shape[1],fill_value=self.__density_list[2]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
        elif self.__optimizer == 'GCMMA':
            ins_process_optimizer_group.create_dataset(name='low',data=numpy.full(shape=ins_process_topopt_group['x'].shape[1],fill_value=self.__density_list[1]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            ins_process_optimizer_group.create_dataset(name='upp',data=numpy.full(shape=ins_process_topopt_group['x'].shape[1],fill_value=self.__density_list[2]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])

            ins_process_optimizer_group.create_dataset(name='raa0',data=numpy.array([0.01]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            ins_process_optimizer_group.create_dataset(name='raa',data=numpy.full(shape=(len(self.__constrains_list),1),fill_value=0.01),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
        else:
            pass

        if self.__binaryzation_list[0] == 'projection':
            projection_beta = 1.0
            beta_iter_number = 1
            self.__calculateProjectionDensityAndChainGradientInformation(ins_process_domains_group,ins_process_topopt_group,projection_beta)

            print(f'\tParameter beta is {str(numpy.around(projection_beta,5))}')
        else:
            pass
        
        convergence_number = 0
        iter_number = 1
        while True:
            fea_folder_name = self.__task_folder_name + os.sep + 'Opt-' + str(iter_number)
            if os.path.exists(fea_folder_name):
                shutil.rmtree(fea_folder_name)
            else:
                pass
            os.mkdir(fea_folder_name)
            
            self.__calculateInterpolationFunction(ins_process_domains_group,ins_process_topopt_group)
            
            fea_process_file_full_name = fea_folder_name + os.sep + 'Opt-'+str(iter_number) + '.pro'
            fea_result_file_full_name = fea_folder_name + os.sep + 'Opt-'+str(iter_number) + '.res'
            ins_fea_system = _femTaskAnalysisSystem(self.__fea_task_file_full_name,fea_process_file_full_name,fea_result_file_full_name)
            fea_process_state = ins_fea_system.initializeProcessFile(ins_process_topopt_group['ifa'])
            fea_result_state = ins_fea_system.initializeResultFile()
            fea_system_state = ins_fea_system.initializeSystems()
            if fea_process_state and fea_result_state and fea_system_state:
                pass
            else:
                os.remove(fea_process_file_full_name)
                os.remove(fea_result_file_full_name)
                
                raise ValueError()
            try:
                ins_fea_system.startAnalysis()
            except:
                os.remove(fea_process_file_full_name)
                os.remove(fea_result_file_full_name)

                print(f"Iter {str(iter_number)} - finite element analysis error!")
                
                raise ValueError()
            else:
                pass
            
            with h5py.File(self.__task_result_file_full_name, 'r+') as ins_result_file:
                ins_fea_result_file = h5py.File(fea_result_file_full_name, 'r')
                for variable_name in ins_fea_result_file['Nodes']:
                    ins_fea_step_result_group = ins_fea_result_file['Nodes'][variable_name][final_step_name]
                    frames_number_list = [int(i) for i in ins_fea_step_result_group.keys()]
                    frames_number_list.sort()
                    
                    ins_fea_frame_result_set = ins_fea_step_result_group[str(frames_number_list[-1])]
                    ins_result_file['Nodes'][variable_name]['optimum'].create_dataset(name=str(iter_number),data=ins_fea_frame_result_set[:],dtype=ins_fea_frame_result_set.dtype)
                for variable_name in ins_fea_result_file['Elements']:
                    ins_fea_step_result_group = ins_fea_result_file['Elements'][variable_name][final_step_name]
                    frames_number_list = [int(i) for i in ins_fea_step_result_group.keys()]
                    frames_number_list.sort()
                    
                    ins_fea_frame_result_set = ins_fea_step_result_group[str(frames_number_list[-1])]
                    ins_result_file['Elements'][variable_name]['optimum'].create_dataset(name=str(iter_number),data=ins_fea_frame_result_set[:],dtype=ins_fea_frame_result_set.dtype)                
                ins_fea_result_file.close()
                
                ins_iteration_x_result_set = ins_result_file['Elements']['X']['optimum'].create_dataset(name=str(iter_number),shape=(1,ins_process_topopt_group['x'].shape[1]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                ins_iteration_x_result_set[0,:] = ins_process_topopt_group['x'][1,:]
                
                ins_result_file['Steps']['optimum'][0] = numpy.concatenate((ins_result_file['Steps']['optimum'][0],iter_number),axis=None)
            
            objectives_value_list = []
            for parameters_list in self.__objectives_list:
                if parameters_list[0] == 'SE':
                    objectives_value_list.append(self.__calculateSEResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
                elif parameters_list[0] == 'VOL':
                    objectives_value_list.append(self.__calculateVOLResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
                elif parameters_list[0] == 'CS':
                    objectives_value_list.append(self.__calculateCSResults(parameters_list, ins_process_domains_group, ins_process_topopt_group, fea_process_file_full_name))
                else:
                    pass    
            constrains_value_list = []
            for parameters_list in self.__constrains_list:
                if parameters_list[0] == 'SE':
                    constrains_value_list.append(self.__calculateSEResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
                elif parameters_list[0] == 'VOL':
                    constrains_value_list.append(self.__calculateVOLResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
                elif parameters_list[0] == 'CS':
                    constrains_value_list.append(self.__calculateCSResults(parameters_list, ins_process_domains_group, ins_process_topopt_group, fea_process_file_full_name))
                else:
                    pass
            del ins_fea_system
            if iter_number == 1:
                maximum_delat_x = 1.0 - self.__density_list[0]
            else:
                maximum_delat_x =  numpy.abs(numpy.max(ins_process_topopt_group['x'][0]-ins_process_topopt_group['x'][2]))
            
            ins_csv_file = open(self.__task_folder_name + os.sep + task_name + '.csv', 'a', newline='', encoding='utf-8')
            ins_csv_writer = csv.writer(ins_csv_file)
            ins_csv_writer.writerow([str(iter_number),*[str(i) for i in objectives_value_list],*[str(i) for i in constrains_value_list],str(maximum_delat_x)])
            ins_csv_file.close()
            
            print_information_string = f'\tIt:{str(iter_number)}'
            for parameters_list, objective_value in zip(self.__objectives_list,objectives_value_list):
                if parameters_list[0] == 'CS':
                    print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+'(Pnorm):'+str(numpy.around(objective_value,5))
                else:
                    print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+':'+str(numpy.around(objective_value,5))
            for parameters_list, constrain_value in zip(self.__constrains_list,constrains_value_list):
                if parameters_list[0] == 'CS':
                    print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+'(Pnorm):'+str(numpy.around(constrain_value,5))
                else:
                    print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+':'+str(numpy.around(constrain_value,5))
            print_information_string +=',maximum |ΔX|:'+str(numpy.around(maximum_delat_x,5))
            print(print_information_string)
            
            if self.__convergence_list[0] == 'density':
                if maximum_delat_x <= self.__convergence_list[1]:
                    convergence_number += 1
                else:
                    convergence_number = 0
            elif self.__convergence_list[0] == 'objective':
                objectives_proportion_value_list = [objective_value/initial_objective_value for objective_value,initial_objective_value in zip(objectives_value_list,initial_objectives_value_list)]
                maximum_delta_objectives_proportion_value = numpy.max((numpy.abs(numpy.asarray(objectives_proportion_value_list)-numpy.asarray(before_objectives_proportion_value_list))))
                before_objectives_proportion_value_list = objectives_proportion_value_list
                
                if maximum_delta_objectives_proportion_value <= self.__convergence_list[2]:
                    convergence_number += 1
                else:
                    convergence_number = 0
            elif self.__convergence_list[0] == 'either':
                objectives_proportion_value_list = [objective_value/initial_objective_value for objective_value,initial_objective_value in zip(objectives_value_list,initial_objectives_value_list)]
                maximum_delta_objectives_proportion_value = numpy.max((numpy.abs(numpy.asarray(objectives_proportion_value_list)-numpy.asarray(before_objectives_proportion_value_list))))
                before_objectives_proportion_value_list = objectives_proportion_value_list
                
                if maximum_delat_x <= self.__convergence_list[1] or maximum_delta_objectives_proportion_value <= self.__convergence_list[2]:
                    convergence_number += 1
                else:
                    convergence_number = 0
            elif self.__convergence_list[0] == 'both':
                objectives_proportion_value_list = [objective_value/initial_objective_value for objective_value,initial_objective_value in zip(objectives_value_list,initial_objectives_value_list)]
                maximum_delta_objectives_proportion_value = numpy.max((numpy.abs(numpy.asarray(objectives_proportion_value_list)-numpy.asarray(before_objectives_proportion_value_list))))
                before_objectives_proportion_value_list = objectives_proportion_value_list
                
                if maximum_delat_x <= self.__convergence_list[1] and maximum_delta_objectives_proportion_value <= self.__convergence_list[2]:
                    convergence_number += 1
                else:
                    convergence_number = 0
            else:
                pass
            
            if convergence_number >= self.__convergence_list[-1] or iter_number >= self.__maximum_iteration_number:
                if self.__binaryzation_list[0] == 'none':
                    os.remove(fea_process_file_full_name)
                    if self.__data_save_list[0] == 'none':
                        shutil.rmtree(fea_folder_name)
                    else:
                        pass
                elif self.__binaryzation_list[0] in ['density threshold','volume constraint']:
                    binaryzation_folder_name = self.__task_folder_name + os.sep + 'Opt-binaryzation'
                    if os.path.exists(binaryzation_folder_name):
                        shutil.rmtree(binaryzation_folder_name)
                    else:
                        pass
                    os.mkdir(binaryzation_folder_name)
                    
                    if self.__binaryzation_list[0] == 'density threshold':
                        ins_process_topopt_group['x'][1,numpy.where(ins_process_topopt_group['x'][1]>=self.__binaryzation_list[1])[0]] = 1.0
                        ins_process_topopt_group['x'][1,numpy.where(ins_process_topopt_group['x'][1]<self.__binaryzation_list[1])[0]] = 0.01
                    elif self.__binaryzation_list[0] == 'volume constraint':
                        self.__calculateBinarizedStructureFrmoVolumeConstrain(ins_process_topopt_group['x'],fea_process_file_full_name,self.__binaryzation_list[1])
                    else:
                        pass
                    self.__calculateInterpolationFunction(ins_process_domains_group,ins_process_topopt_group)
                    os.remove(fea_process_file_full_name)
                    if self.__data_save_list[0] == 'none':
                        shutil.rmtree(fea_folder_name)
                    else:
                        pass
                    
                    fea_process_file_full_name = binaryzation_folder_name + os.sep + 'Opt-binaryzation.pro'
                    fea_result_file_full_name = binaryzation_folder_name + os.sep + 'Opt-binaryzation.res'
                    ins_fea_system = _femTaskAnalysisSystem(self.__fea_task_file_full_name,fea_process_file_full_name,fea_result_file_full_name)
                    fea_process_state = ins_fea_system.initializeProcessFile(ins_process_topopt_group['ifa'])
                    fea_result_state = ins_fea_system.initializeResultFile()
                    fea_system_state = ins_fea_system.initializeSystems()
                    if fea_process_state and fea_result_state and fea_system_state:
                        pass
                    else:
                        raise ValueError()
                    try:
                        ins_fea_system.startAnalysis()
                    except:
                        os.remove(fea_process_file_full_name)
                        os.remove(fea_result_file_full_name)

                        print(f"Iter binaryzation - finite element analysis error!")
                        
                        raise ValueError()
                    else:
                        pass
                    
                    iter_number += 1
                    with h5py.File(self.__task_result_file_full_name, 'r+') as ins_result_file:
                        ins_fea_result_file = h5py.File(fea_result_file_full_name, 'r')
                        for variable_name in ins_fea_result_file['Nodes']:
                            ins_fea_step_result_group = ins_fea_result_file['Nodes'][variable_name][final_step_name]
                            frames_number_list = [int(i) for i in ins_fea_step_result_group.keys()]
                            frames_number_list.sort()
                            
                            ins_fea_frame_result_set = ins_fea_step_result_group[str(frames_number_list[-1])]
                            ins_result_file['Nodes'][variable_name]['optimum'].create_dataset(name=str(iter_number),data=ins_fea_frame_result_set[:],dtype=ins_fea_frame_result_set.dtype)
                        for variable_name in ins_fea_result_file['Elements']:
                            ins_fea_step_result_group = ins_fea_result_file['Elements'][variable_name][final_step_name]
                            frames_number_list = [int(i) for i in ins_fea_step_result_group.keys()]
                            frames_number_list.sort()
                            
                            ins_fea_frame_result_set = ins_fea_step_result_group[str(frames_number_list[-1])]
                            ins_result_file['Elements'][variable_name]['optimum'].create_dataset(name=str(iter_number),data=ins_fea_frame_result_set[:],dtype=ins_fea_frame_result_set.dtype)                
                        ins_fea_result_file.close()
                        
                        ins_iteration_x_result_set = ins_result_file['Elements']['X']['optimum'].create_dataset(name=str(iter_number),shape=(1,ins_process_topopt_group['x'].shape[1]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                        ins_iteration_x_result_set[0,:] = ins_process_topopt_group['x'][1,:]
                    
                        ins_result_file['Steps']['optimum'][0] = numpy.concatenate((ins_result_file['Steps']['optimum'][0],iter_number),axis=None)
                    
                    objectives_value_list = []
                    for parameters_list in self.__objectives_list:
                        if parameters_list[0] == 'SE':
                            objectives_value_list.append(self.__calculateSEResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
                        elif parameters_list[0] == 'VOL':
                            objectives_value_list.append(self.__calculateVOLResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
                        elif parameters_list[0] == 'CS':
                            objectives_value_list.append(self.__calculateCSResults(parameters_list, ins_process_domains_group, ins_process_topopt_group, fea_process_file_full_name))
                        else:
                            pass
                    constrains_value_list = []
                    for parameters_list in self.__constrains_list:
                        if parameters_list[0] == 'SE':
                            constrains_value_list.append(self.__calculateSEResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
                        elif parameters_list[0] == 'VOL':
                            constrains_value_list.append(self.__calculateVOLResults(parameters_list, ins_process_topopt_group, fea_process_file_full_name))
                        elif parameters_list[0] == 'CS':
                            constrains_value_list.append(self.__calculateCSResults(parameters_list, ins_process_domains_group, ins_process_topopt_group, fea_process_file_full_name))
                        else:
                            pass
                    del ins_fea_system
                    os.remove(fea_process_file_full_name)
                    
                    ins_csv_file = open(self.__task_folder_name + os.sep + task_name + '.csv', 'a', newline='', encoding='utf-8')
                    ins_csv_writer = csv.writer(ins_csv_file)
                    ins_csv_writer.writerow(['binaryzation',*[str(i) for i in objectives_value_list],*[str(i) for i in constrains_value_list],''])
                    ins_csv_file.close()
                    
                    print_information_string = '\tIt:binaryzation'
                    for parameters_list, objective_value in zip(self.__objectives_list,objectives_value_list):
                        if parameters_list[1] == '':
                            print_information_string += ','+parameters_list[0]+':'+str(numpy.around(objective_value,5))
                        elif parameters_list[0] == 'CS':
                            print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+'(Pnorm):'+str(numpy.around(objective_value,5))
                        else:
                            print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+':'+str(numpy.around(objective_value,5))
                    for parameters_list, constrain_value in zip(self.__constrains_list,constrains_value_list):
                        if parameters_list[1] == '':
                            print_information_string += ','+parameters_list[0]+':'+str(numpy.around(constrain_value,5))
                        elif parameters_list[0] == 'CS':
                            print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+'(Pnorm):'+str(numpy.around(constrain_value,5))
                        else:
                            print_information_string += ','+parameters_list[0]+'-'+parameters_list[1]+':'+str(numpy.around(constrain_value,5))
                    print(print_information_string)
                else:
                    pass
                
                if convergence_number >= self.__convergence_list[-1]:
                    print(f'The topology optimization - {task_name} has converged!')
                else:
                    print(f"The topology optimization - {task_name} has finished because of maximum iterations!")
                
                break
            else:
                pass
            
            ins_process_topopt_group['x'][3,:] = ins_process_topopt_group['x'][2][:]
            ins_process_topopt_group['x'][2,:] = ins_process_topopt_group['x'][0][:]
            
            for parameters_list in self.__objectives_list:
                if parameters_list[0] == 'SE':
                    self.__calculateSensitivityOfSE(parameters_list,ins_process_domains_group,ins_process_topopt_group,fea_process_file_full_name)
                elif parameters_list[0] == 'VOL':
                    self.__calculateSensitivityOfVOL(parameters_list,ins_process_domains_group,ins_process_topopt_group,fea_process_file_full_name)
                elif parameters_list[0] == 'CS':
                    self.__calculateSensitivityOfCS(parameters_list, ins_process_domains_group, ins_process_topopt_group, fea_process_file_full_name)
                else:
                    pass
            for parameters_list in self.__constrains_list:
                if parameters_list[0] == 'SE':
                    self.__calculateSensitivityOfSE(parameters_list,ins_process_domains_group,ins_process_topopt_group,fea_process_file_full_name)
                elif parameters_list[0] == 'VOL':
                    self.__calculateSensitivityOfVOL(parameters_list,ins_process_domains_group,ins_process_topopt_group,fea_process_file_full_name)
                elif parameters_list[0] == 'CS':
                    self.__calculateSensitivityOfCS(parameters_list, ins_process_domains_group, ins_process_topopt_group, fea_process_file_full_name)
                else:
                    pass    
            
            if self.__filter_list[0] == 'sensitivity':
                for parameters_list in self.__objectives_list:
                    ins_sensitivity_set = ins_process_topopt_group['Sensitivity'][parameters_list[0]][parameters_list[1]]
                    for ins_design_elements_label_set in ins_process_domains_group.values():
                        for element_index in ins_design_elements_label_set[:]-1:
                            neighbor_elements_index_array = ins_process_topopt_group['neighbor'][element_index]-1
                            ins_sensitivity_set[2,element_index] = numpy.sum(ins_process_topopt_group['weight'][element_index][:]*ins_process_topopt_group['x'][0,neighbor_elements_index_array]*ins_sensitivity_set[1,neighbor_elements_index_array]) / numpy.sum(ins_process_topopt_group['weight'][element_index][:]*ins_process_topopt_group['x'][0,neighbor_elements_index_array])

                for parameters_list in self.__constrains_list:
                    ins_sensitivity_set = ins_process_topopt_group['Sensitivity'][parameters_list[0]][parameters_list[1]]
                    for ins_design_elements_label_set in ins_process_domains_group.values():
                        for element_index in ins_design_elements_label_set[:]-1:
                            neighbor_elements_index_array = ins_process_topopt_group['neighbor'][element_index]-1
                            ins_sensitivity_set[2,element_index] = numpy.sum(ins_process_topopt_group['weight'][element_index][:]*ins_process_topopt_group['x'][0,neighbor_elements_index_array]*ins_sensitivity_set[1,neighbor_elements_index_array]) / numpy.sum(ins_process_topopt_group['weight'][element_index][:]*ins_process_topopt_group['x'][0,neighbor_elements_index_array])
            elif self.__filter_list[0] == 'density':
                for parameters_list in self.__objectives_list:
                    ins_sensitivity_set = ins_process_topopt_group['Sensitivity'][parameters_list[0]][parameters_list[1]]
                    for ins_design_elements_label_set in ins_process_domains_group.values():
                        elements_index_array = ins_design_elements_label_set[:]-1
                        ins_sensitivity_set[2,elements_index_array] = ins_sensitivity_set[1,elements_index_array]
                
                for parameters_list in self.__constrains_list:
                    ins_sensitivity_set = ins_process_topopt_group['Sensitivity'][parameters_list[0]][parameters_list[1]]
                    for ins_design_elements_label_set in ins_process_domains_group.values():
                        elements_index_array = ins_design_elements_label_set[:]-1
                        ins_sensitivity_set[2,elements_index_array] = ins_sensitivity_set[1,elements_index_array]
            else:
                pass
        
            if self.__optimizer == 'ADAM':
                ins_objective_sensivity_set = ins_process_topopt_group['Sensitivity'][self.__objectives_list[0][0]][self.__objectives_list[0][1]]
                for ins_design_elements_label_set in ins_process_domains_group.values():
                    elements_index_array = ins_design_elements_label_set[:]-1
                    
                    update_m_array,update_v_array,update_x_array = osolver_dict['ADAM'](
                        iter=iter_number, alpha=ins_process_optimizer_group['alpha'][0], beta=ins_process_optimizer_group['beta'][:], eps=ins_process_optimizer_group['eps'][0],
                        m=ins_process_optimizer_group['m'][elements_index_array], v=ins_process_optimizer_group['v'][elements_index_array],
                        df0dx=ins_objective_sensivity_set[2,elements_index_array], x=ins_process_topopt_group['x'][0,elements_index_array],
                        xmin=self.__density_list[1],xmax=self.__density_list[2],xmove=self.__density_list[3])
                    
                    ins_process_optimizer_group['m'][elements_index_array] = update_m_array
                    ins_process_optimizer_group['v'][elements_index_array] = update_v_array
                    ins_process_topopt_group['x'][0,elements_index_array] = update_x_array
                    del update_m_array
                    del update_v_array
                    del update_x_array
            elif self.__optimizer == 'MMA':
                for ins_design_elements_label_set in ins_process_domains_group.values():
                    elements_index_array = ins_design_elements_label_set[:]-1
                    
                    normalized_df0dx_vectors = numpy.zeros(shape=(elements_index_array.shape[0],len(self.__objectives_list)),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    for objective_index,parameters_list in enumerate(self.__objectives_list):
                        normalized_df0dx_vectors[:,objective_index] = ins_process_topopt_group['Sensitivity'][parameters_list[0]][parameters_list[1]][2,elements_index_array] / initial_objectives_value_list[objective_index]
                    normalized_fval_vector = numpy.zeros(shape=(len(self.__constrains_list),1),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    normalized_dfdx_array = numpy.zeros(shape=(len(self.__constrains_list),elements_index_array.shape[0]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    for constrain_index,parameters_list in enumerate(self.__constrains_list):
                        normalized_fval_vector[constrain_index,0] = (constrains_value_list[constrain_index]-parameters_list[-1]) / initial_constrains_value_list[constrain_index]
                        normalized_dfdx_array[constrain_index] = ins_process_topopt_group['Sensitivity'][parameters_list[0]][parameters_list[1]][2,elements_index_array] / initial_constrains_value_list[constrain_index]
                    
                    update_x_array,previous_low_bounds_array,previous_upp_bounds_array = osolver_dict['MMA'](
                        m=len(self.__constrains_list),n=elements_index_array.shape[0],iter=iter_number,
                        xval=ins_process_topopt_group['x'][0,elements_index_array].reshape(-1,1),
                        xmin=numpy.full(shape=(elements_index_array.shape[0],1),fill_value=self.__density_list[1]),xmax=numpy.full(shape=(elements_index_array.shape[0],1),fill_value=self.__density_list[2]),
                        xold1=ins_process_topopt_group['x'][2,elements_index_array].reshape(-1,1),xold2=ins_process_topopt_group['x'][3,elements_index_array].reshape(-1,1),
                        df0dx=normalized_df0dx_vectors,
                        fval=normalized_fval_vector,dfdx=normalized_dfdx_array,
                        low=ins_process_optimizer_group['low'][elements_index_array].reshape(-1,1),upp=ins_process_optimizer_group['upp'][elements_index_array].reshape(-1,1),
                        move=self.__density_list[3])
                    
                    del normalized_df0dx_vectors
                    del normalized_fval_vector
                    del normalized_dfdx_array
                    
                    ins_process_optimizer_group['low'][elements_index_array] = previous_low_bounds_array.flatten()
                    ins_process_optimizer_group['upp'][elements_index_array] = previous_upp_bounds_array.flatten()                  
                    ins_process_topopt_group['x'][0,elements_index_array] = update_x_array.flatten()
                    del update_x_array
                    del previous_low_bounds_array
                    del previous_upp_bounds_array
            elif self.__optimizer == 'GCMMA':
                for ins_design_elements_label_set in ins_process_domains_group.values():
                    elements_index_array = ins_design_elements_label_set[:]-1
                    
                    normalized_f0val_vector = numpy.zeros(shape=(len(self.__objectives_list),1),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    normalized_df0dx_vectors = numpy.zeros(shape=(elements_index_array.shape[0],len(self.__objectives_list)),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    for objective_index,parameters_list in enumerate(self.__objectives_list):
                        normalized_f0val_vector[objective_index,0] = objectives_value_list[objective_index] / initial_objectives_value_list[objective_index]
                        normalized_df0dx_vectors[:,objective_index] = ins_process_topopt_group['Sensitivity'][parameters_list[0]][parameters_list[1]][2,elements_index_array] / initial_objectives_value_list[objective_index]
                    normalized_fval_vector = numpy.zeros(shape=(len(self.__constrains_list),1),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    normalized_dfdx_array = numpy.zeros(shape=(len(self.__constrains_list),elements_index_array.shape[0]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    for constrain_index,parameters_list in enumerate(self.__constrains_list):
                        normalized_fval_vector[constrain_index,0] = (constrains_value_list[constrain_index]-parameters_list[-1]) / initial_constrains_value_list[objective_index]
                        normalized_dfdx_array[constrain_index] = ins_process_topopt_group['Sensitivity'][parameters_list[0]][parameters_list[1]][2,elements_index_array] / initial_constrains_value_list[objective_index]

                    previous_low_bounds_array,previous_upp_bounds_array, previous_raa0, previous_raa_array = osolver_dict['ASYMP'](
                        outeriter=iter_number,n=elements_index_array.shape[0],
                        xval=ins_process_topopt_group['x'][0,elements_index_array].reshape(-1,1),
                        xold1=ins_process_topopt_group['x'][2,elements_index_array].reshape(-1,1),xold2=ins_process_topopt_group['x'][3,elements_index_array].reshape(-1,1),
                        xmin=numpy.full(shape=(elements_index_array.shape[0],1),fill_value=self.__density_list[1]),xmax=numpy.full(shape=(elements_index_array.shape[0],1),fill_value=self.__density_list[2]),
                        low=ins_process_optimizer_group['low'][elements_index_array].reshape(-1,1),upp=ins_process_optimizer_group['upp'][elements_index_array].reshape(-1,1),
                        raa0=ins_process_optimizer_group['raa0'][0], raa=ins_process_optimizer_group['raa'][:],
                        df0dx=normalized_df0dx_vectors,
                        dfdx=normalized_dfdx_array)
                    update_x_array, f0app, fapp_array = osolver_dict['GCMMA'](
                        m=len(self.__constrains_list),n=elements_index_array.shape[0],iter=iter_number,
                        xval=ins_process_topopt_group['x'][0,elements_index_array].reshape(-1,1),
                        xmin=numpy.full(shape=(elements_index_array.shape[0],1),fill_value=self.__density_list[1]),xmax=numpy.full(shape=(elements_index_array.shape[0],1),fill_value=self.__density_list[2]),
                        low=previous_low_bounds_array,upp=previous_upp_bounds_array,
                        raa0=previous_raa0,raa=previous_raa_array,
                        f0val=normalized_f0val_vector,df0dx=normalized_df0dx_vectors,
                        fval=normalized_fval_vector,dfdx=normalized_dfdx_array,
                        move=self.__density_list[3])
                    
                    del normalized_f0val_vector
                    del normalized_df0dx_vectors
                    del normalized_fval_vector
                    del normalized_dfdx_array
                    
                    ins_process_optimizer_group['low'][elements_index_array] = previous_low_bounds_array.flatten()
                    ins_process_optimizer_group['upp'][elements_index_array] = previous_upp_bounds_array.flatten()                  
                    ins_process_topopt_group['x'][0,elements_index_array] = update_x_array.flatten()
                    del update_x_array
                    del previous_low_bounds_array
                    del previous_upp_bounds_array
            else:
                pass
            
            if self.__binaryzation_list[0] == 'projection' and projection_beta<512 and beta_iter_number>=self.__binaryzation_list[2]:
                projection_beta = 2.0 * projection_beta
                beta_iter_number = 0
                
                print(f'\tParameter beta increased to {str(numpy.around(projection_beta,5))}')
            else:
                pass
            
            if self.__filter_list[0] == 'sensitivity':
                for ins_design_elements_label_set in ins_process_domains_group.values():
                    elements_index_array = ins_design_elements_label_set[:]-1
                    ins_process_topopt_group['x'][1,elements_index_array] = ins_process_topopt_group['x'][0,elements_index_array]
            elif self.__filter_list[0] == 'density':
                self.__calculateFilteredDensityAndChainGradientInformation(ins_process_domains_group,ins_process_topopt_group,fea_process_file_full_name)
            else:
                pass
            os.remove(fea_process_file_full_name)
            
            if self.__binaryzation_list[0] == 'projection':
                self.__calculateProjectionDensityAndChainGradientInformation(ins_process_domains_group,ins_process_topopt_group,projection_beta)
            else:
                pass
            
            if self.__data_save_list[0] == 'none':
                shutil.rmtree(fea_folder_name)
            elif self.__data_save_list[0] == 'last':
                shutil.rmtree(fea_folder_name)
            elif self.__data_save_list[0] == 'every':
                if self.__data_save_list[0] == 0:
                    shutil.rmtree(fea_folder_name)
                elif iter_number%self.__data_save_list[1] != 0:
                    shutil.rmtree(fea_folder_name)
                else:
                    pass
            else:
                pass
            
            iter_number += 1
            if self.__binaryzation_list[0] == 'projection':
                beta_iter_number += 1
            else:
                pass
            
        ins_process_file.close()
    
    def __calculateSEResults(self, in_parameters_list:list, in_ins_process_topopt_group:object, in_fea_process_file_full_name:str) -> float:
        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
        if available_cpu_number <= 0:
            print(f"The CPU usage is too high!")
            raise ChildProcessError()
        else:
            pass
        
        ins_sensitivity_set = in_ins_process_topopt_group['Sensitivity'][in_parameters_list[0]][in_parameters_list[1]]
        if ins_sensitivity_set.shape[1] < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
            available_cpu_number = 1
        else:
            pass
        
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        
        process_local_index_range_list = [[0,int(ins_sensitivity_set.shape[1]/available_cpu_number)]]
        for process_index in range(1,available_cpu_number):
            process_local_index_range_list.append([process_local_index_range_list[process_index-1][1],process_local_index_range_list[process_index-1][1]+process_local_index_range_list[0][1]])
        process_local_index_range_list[-1][1] = ins_sensitivity_set.shape[1]
        processes_list = []
        for process_id,index_range in enumerate(process_local_index_range_list):
            temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
            with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
                    ins_opt_temp_file.create_dataset(name='readyelementsvolume',data=numpy.asarray([ins_fea_process_file['Update']['geometry'][i][0] for i in range(index_range[0],index_range[1])])) 
                    ins_opt_temp_file.create_dataset(name='readyelementsipee',data=ins_fea_process_file['Record']['ipee'][index_range[0]:index_range[1]])
                    ins_opt_temp_file.create_dataset(name='readyelementsipes',data=ins_fea_process_file['Record']['ipes'][index_range[0]:index_range[1]])
                if self.__model_dimension == '2D':
                    ins_opt_temp_file.create_dataset(name='modeldimension',data=numpy.array([2]))
                elif self.__model_dimension == '3D':
                    ins_opt_temp_file.create_dataset(name='modeldimension',data=numpy.array([3]))
                else:
                    pass
                
                ins_opt_temp_file.create_dataset(name='readyelementsse',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            
            ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsSEValue,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
            processes_list.append(ins_process)

            ins_process.start()
        for ins_process in processes_list:
            ins_process.join()
        for ins_process in processes_list:
            process_id_string = ins_process.name.split('-')[-1]
            ins_process.close()
            
            temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
            index_range = process_local_index_range_list[int(process_id_string)]
        
            with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                ins_sensitivity_set[0,index_range[0]:index_range[1]] = ins_opt_temp_file['readyelementsse'][:]
            os.remove(temp_file_full_name)
        del processes_list
        
        if in_parameters_list[2] == 'sum':
            result_value =  numpy.sum(ins_sensitivity_set[0,:])
        else:
            pass
        return result_value
    def __calculateVOLResults(self, in_parameters_list:list, in_ins_process_topopt_group:object, in_fea_process_file_full_name:str) -> float:
        ins_sensitivity_set = in_ins_process_topopt_group['Sensitivity'][in_parameters_list[0]][in_parameters_list[1]]
        ins_elements_x_set = in_ins_process_topopt_group['x']
        
        with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
            ins_elements_geometry_set = ins_fea_process_file['Update']['geometry']
            elements_volume_array = numpy.asarray([ins_elements_geometry_set[i][0] for i in range(ins_sensitivity_set.shape[1])])
            ins_sensitivity_set[0,:] = ins_elements_x_set[1,:]*elements_volume_array
    
        if in_parameters_list[2] == 'sum':
            result_value = numpy.sum(ins_sensitivity_set[0,:])
        else:
            pass
        return result_value
    def __calculateCSResults(self, in_parameters_list:list, in_ins_process_domains_group:object, in_ins_process_topopt_group:object, in_fea_process_file_full_name:str) -> float:
        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
        if available_cpu_number <= 0:
            print(f"The CPU usage is too high!")
            raise ChildProcessError()
        else:
            pass
        
        ins_sensitivity_set = in_ins_process_topopt_group['Sensitivity'][in_parameters_list[0]][in_parameters_list[1]]
        if ins_sensitivity_set.shape[1] < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
            available_cpu_number = 1
        else:
            pass
        
        process_local_index_range_list = [[0,int(ins_sensitivity_set.shape[1]/available_cpu_number)]]
        for process_index in range(1,available_cpu_number):
            process_local_index_range_list.append([process_local_index_range_list[process_index-1][1],process_local_index_range_list[process_index-1][1]+process_local_index_range_list[0][1]])
        process_local_index_range_list[-1][1] = ins_sensitivity_set.shape[1]
        
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        
        processes_list = []
        for process_id,index_range in enumerate(process_local_index_range_list):
            temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
            with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
                    ins_opt_temp_file.create_dataset(name='readyelementsipes',data=ins_fea_process_file['Record']['ipes'][index_range[0]:index_range[1]])
                
                if in_parameters_list[1] == 'Mises':
                    ins_opt_temp_file.create_dataset(name='stresscomponent',data=numpy.array([1]))
                    
                    if self.__model_dimension == '2D':
                        ins_opt_temp_file.create_dataset(name='readyelementscsc',shape=(3,index_range[1]-index_range[0]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    elif self.__model_dimension == '3D':
                        ins_opt_temp_file.create_dataset(name='readyelementscsc',shape=(6,index_range[1]-index_range[0]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    else:
                        pass
                else:
                    pass
                ins_opt_temp_file.create_dataset(name='readyelementscs',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                
            ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsCSValue,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
            processes_list.append(ins_process)

            ins_process.start()
        for ins_process in processes_list:
            ins_process.join()
        for ins_process in processes_list:
            process_id_string = ins_process.name.split('-')[-1]
            ins_process.close()
            
            temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
            index_range = process_local_index_range_list[int(process_id_string)]
        
            with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                ins_sensitivity_set[0,index_range[0]:index_range[1]] = ins_opt_temp_file['readyelementscs'][:]

                if in_parameters_list[1] == 'Mises':
                    in_ins_process_topopt_group['csc'][:,index_range[0]:index_range[1]] = ins_opt_temp_file['readyelementscsc'][:]
                else:
                    pass
            os.remove(temp_file_full_name)
        del processes_list
        
        ins_dpndrcs_set = in_ins_process_topopt_group['dpndrcs']
        ins_dpndrcs_set[:] = ins_sensitivity_set[0,:]
        relaxation_factor = self.__interpolation_model[1]*0.8
        for ins_design_elements_label_set in in_ins_process_domains_group.values():
            elements_index_array = ins_design_elements_label_set[:] - 1
            if self.__interpolation_model[0] == 'SIMP':
                ins_dpndrcs_set[elements_index_array] = ins_sensitivity_set[0,elements_index_array] / in_ins_process_topopt_group['x'][1,elements_index_array]**relaxation_factor
            elif self.__interpolation_model[0] == 'RAMP':
                ins_dpndrcs_set[elements_index_array] = ins_sensitivity_set[0,elements_index_array] * (1.0+relaxation_factor-relaxation_factor*in_ins_process_topopt_group['x'][1,elements_index_array]) / in_ins_process_topopt_group['x'][1,elements_index_array]
            else:
                pass
        
        aggregation_factor = 5.0
        aggregated_cs_value = numpy.linalg.norm(ins_dpndrcs_set[:],aggregation_factor)
        result_value = aggregated_cs_value
        
        return result_value
    
    def __calculateFilteredDensityAndChainGradientInformation(self, in_ins_process_domains_group:object, in_ins_process_topopt_group:object, in_fea_process_file_full_name:str) -> None:
        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
        if available_cpu_number <= 0:
            print(f"The CPU usage is too high!")
            raise ChildProcessError()
        else:
            pass
        
        ins_x_set = in_ins_process_topopt_group['x']
        ins_chaingrad_set = in_ins_process_topopt_group['chaingrad']
        if ins_x_set.shape[1] < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
            available_cpu_number = 1
        else:
            pass
        
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        for ins_design_elements_label_set in in_ins_process_domains_group.values():
            process_local_index_range_list = [[0,int(ins_design_elements_label_set.shape[0]/available_cpu_number)]]
            for process_index in range(1,available_cpu_number):
                process_local_index_range_list.append([process_local_index_range_list[process_index-1][1],process_local_index_range_list[process_index-1][1]+process_local_index_range_list[0][1]])
            process_local_index_range_list[-1][1] = ins_design_elements_label_set.shape[0]
            
            processes_list = []
            for process_id,index_range in enumerate(process_local_index_range_list):
                temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file, h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
                    ins_opt_temp_file.create_dataset(name='readyelementsneighbor',data=in_ins_process_topopt_group['neighbor'][ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                    ins_opt_temp_file.create_dataset(name='readyelementsweight',data=in_ins_process_topopt_group['weight'][ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                    ins_opt_temp_file.create_dataset(name='allelementsdesignx',data=ins_x_set[0,:])
                    ins_opt_temp_file.create_dataset(name='allelementsvolume',data=numpy.asarray([ins_fea_process_file['Update']['geometry'][i][0] for i in range(ins_fea_process_file['Update']['geometry'].shape[0])]))
                    
                    ins_opt_temp_file.create_dataset(name='readyelementsxphy',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    ins_opt_temp_file.create_dataset(name='readyxphychaingrad',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                
                ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsFilteredDensityAndChainGradientInformation,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                processes_list.append(ins_process)

                ins_process.start()
            for ins_process in processes_list:
                ins_process.join()
                
            for ins_process in processes_list:
                process_id_string = ins_process.name.split('-')[-1]
                ins_process.close()
                
                temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                index_range = process_local_index_range_list[int(process_id_string)]
                
                with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                    ins_ready_elements_xphy_set = ins_opt_temp_file['readyelementsxphy']
                    ins_ready_elements_xphy_chaingrad_set = ins_opt_temp_file['readyxphychaingrad']
                    
                    for local_index1,local_index2 in enumerate(range(index_range[0],index_range[1])):
                        element_index = ins_design_elements_label_set[local_index2] - 1
                        
                        ins_x_set[1,element_index] = ins_ready_elements_xphy_set[local_index1]
                        ins_chaingrad_set[0,element_index] = ins_ready_elements_xphy_chaingrad_set[local_index1]
                os.remove(temp_file_full_name)
            del processes_list
    def __calculateProjectionDensityAndChainGradientInformation(self, in_ins_process_domains_group:object, in_ins_process_topopt_group:object, in_projection_beta:float) -> None:
        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
        if available_cpu_number <= 0:
            print(f"The CPU usage is too high!")
            raise ChildProcessError()
        else:
            pass
        
        ins_x_set = in_ins_process_topopt_group['x']
        ins_chaingrad_set = in_ins_process_topopt_group['chaingrad']
        if ins_x_set.shape[1] < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
            available_cpu_number = 1
        else:
            pass
        
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        for ins_design_elements_label_set in in_ins_process_domains_group.values():
            process_elements_index_range_list = [[0,int(ins_design_elements_label_set.shape[0]/available_cpu_number)]]
            for process_index in range(1,available_cpu_number):
                process_elements_index_range_list.append([process_elements_index_range_list[process_index-1][1],process_elements_index_range_list[process_index-1][1]+process_elements_index_range_list[0][1]])
            process_elements_index_range_list[-1][1] = ins_design_elements_label_set.shape[0]

            processes_list = []
            for process_id,index_range in enumerate(process_elements_index_range_list):
                temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                    ins_opt_temp_file.create_dataset(name='projectionparameters',data=numpy.asarray([in_projection_beta,self.__binaryzation_list[1]]))
                    ins_opt_temp_file.create_dataset(name='readyelementsxphy',data=ins_x_set[1,ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                    
                    ins_opt_temp_file.create_dataset(name='readyelementsxpro',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    ins_opt_temp_file.create_dataset(name='readyxprochaingrad',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                
                ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsProjectionDensityAndChainGradientInformation,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                processes_list.append(ins_process)

                ins_process.start()
            for ins_process in processes_list:
                ins_process.join()
                        
            for ins_process in processes_list:
                process_id_string = ins_process.name.split('-')[-1]
                ins_process.close()
                
                temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                index_range = process_elements_index_range_list[int(process_id_string)]
            
                with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                    ready_elements_index_array = ins_design_elements_label_set[index_range[0]:index_range[1]]-1
                    ins_x_set[1,ready_elements_index_array] = ins_opt_temp_file['readyelementsxpro'][:]
                    ins_chaingrad_set[1,ready_elements_index_array] = ins_opt_temp_file['readyxprochaingrad'][:]
                os.remove(temp_file_full_name)
            del processes_list
    def __calculateInterpolationFunction(self, in_ins_process_domains_group:object, in_ins_process_topopt_group:object) -> None:
        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
        if available_cpu_number <= 0:
            print(f"The CPU usage is too high!")
            raise ChildProcessError()
        else:
            pass
        
        ins_x_set = in_ins_process_topopt_group['x']
        ins_ifa_set = in_ins_process_topopt_group['ifa']
        if ins_x_set.shape[1] < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
            available_cpu_number = 1
        else:
            pass
        
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        for ins_design_elements_label_set in in_ins_process_domains_group.values():
            process_local_index_range_list = [[0,int(ins_design_elements_label_set.shape[0]/available_cpu_number)]]
            for process_index in range(1,available_cpu_number):
                process_local_index_range_list.append([process_local_index_range_list[process_index-1][1],process_local_index_range_list[process_index-1][1]+process_local_index_range_list[0][1]])
            process_local_index_range_list[-1][1] = ins_design_elements_label_set.shape[0]

            processes_list = []
            for process_id,index_range in enumerate(process_local_index_range_list):
                temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                    if self.__interpolation_model[0] == 'SIMP':
                        ins_opt_temp_file.create_dataset(name='interpolationparameters',data=numpy.asarray([1.0,self.__interpolation_model[1]]))
                    elif self.__interpolation_model[0] == 'RAMP':
                        ins_opt_temp_file.create_dataset(name='interpolationparameters',data=numpy.asarray([2.0,self.__interpolation_model[1]]))
                    else:
                        pass
                    ins_opt_temp_file.create_dataset(name='readyelementsxphy',data=ins_x_set[1,ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                    
                    ins_opt_temp_file.create_dataset(name='readyelementsinterpolationfunction',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    
                ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsInterpolationFunction,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                processes_list.append(ins_process)

                ins_process.start()
            for ins_process in processes_list:
                ins_process.join()
                        
            for ins_process in processes_list:
                process_id_string = ins_process.name.split('-')[-1]
                ins_process.close()
                
                temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                index_range = process_local_index_range_list[int(process_id_string)]
            
                with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                    ready_elements_index_array = ins_design_elements_label_set[index_range[0]:index_range[1]]-1
                    ins_ifa_set[ready_elements_index_array] = ins_opt_temp_file['readyelementsinterpolationfunction'][:]
                os.remove(temp_file_full_name)
            del processes_list
    
    def __calculateSensitivityOfSE(self, in_parameters_list:list, in_ins_process_domains_group:object, in_ins_process_topopt_group:object, in_fea_process_file_full_name:str) -> None:
        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
        if available_cpu_number <= 0:
            print(f"The CPU usage is too high!")
            raise ChildProcessError()
        else:
            pass
        
        ins_sensitivity_set = in_ins_process_topopt_group['Sensitivity'][in_parameters_list[0]][in_parameters_list[1]]
        if ins_sensitivity_set.shape[1] < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
            available_cpu_number = 1
        else:
            pass
        
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        for ins_design_elements_label_set in in_ins_process_domains_group.values():
            process_elements_index_range_list = [[0,int(ins_design_elements_label_set.shape[0]/available_cpu_number)]]
            for process_index in range(1,available_cpu_number):
                process_elements_index_range_list.append([process_elements_index_range_list[process_index-1][1],process_elements_index_range_list[process_index-1][1]+process_elements_index_range_list[0][1]])
            process_elements_index_range_list[-1][1] = ins_design_elements_label_set.shape[0]

            processes_list = []
            for process_id,index_range in enumerate(process_elements_index_range_list):
                temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                    if self.__interpolation_model[0] == 'SIMP':
                        ins_opt_temp_file.create_dataset(name='interpolationparameters',data=numpy.asarray([1.0,self.__interpolation_model[1]]))
                    elif self.__interpolation_model[0] == 'RAMP':
                        ins_opt_temp_file.create_dataset(name='interpolationparameters',data=numpy.asarray([2.0,self.__interpolation_model[1]]))
                    else:
                        pass
                    if self.__filter_list[0] == 'sensitivity':
                        ins_opt_temp_file.create_dataset(name='filter',data=numpy.asarray([1]))
                    elif self.__filter_list[0] == 'density':
                        ins_opt_temp_file.create_dataset(name='filter',data=numpy.asarray([2]))
                        ins_opt_temp_file.create_dataset(name='readyelementsneighbor',data=in_ins_process_topopt_group['neighbor'][ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                        ins_opt_temp_file.create_dataset(name='readyelementsweight',data=in_ins_process_topopt_group['weight'][ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                        with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
                            ins_opt_temp_file.create_dataset(name='readyelementsvolume',data=numpy.asarray([ins_fea_process_file['Update']['geometry'][i][0] for i in ins_design_elements_label_set[index_range[0]:index_range[1]]-1]))
                    else:
                        pass
                    if in_parameters_list[2] == 'sum':
                        ins_opt_temp_file.create_dataset(name='operator',data=numpy.asarray([1]))
                    else:
                        pass
                    ins_opt_temp_file.create_dataset(name='readyelementslabel',data=ins_design_elements_label_set[index_range[0]:index_range[1]])
                    ins_opt_temp_file.create_dataset(name='allelementsxphy',data=in_ins_process_topopt_group['x'][1,:])
                    ins_opt_temp_file.create_dataset(name='allelementsse',data=ins_sensitivity_set[0,:])
                    ins_opt_temp_file.create_dataset(name='allelementschaingrad',data=in_ins_process_topopt_group['chaingrad'][0:2])
                    
                    ins_opt_temp_file.create_dataset(name='readyelementssesensitivity',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                
                ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsSESensitivity,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                processes_list.append(ins_process)

                ins_process.start()
            for ins_process in processes_list:
                ins_process.join()
                        
            for ins_process in processes_list:
                process_id_string = ins_process.name.split('-')[-1]
                ins_process.close()
                
                temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                index_range = process_elements_index_range_list[int(process_id_string)]
            
                with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                    ready_elements_index_array = ins_design_elements_label_set[index_range[0]:index_range[1]]-1
                    ins_sensitivity_set[1,ready_elements_index_array] = ins_opt_temp_file['readyelementssesensitivity'][:]
                os.remove(temp_file_full_name)
            del processes_list
    def __calculateSensitivityOfVOL(self, in_parameters_list:list, in_ins_process_domains_group:object, in_ins_process_topopt_group:object, in_fea_process_file_full_name:str) -> None:
        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
        if available_cpu_number <= 0:
            print(f"The CPU usage is too high!")
            raise ChildProcessError()
        else:
            pass
        
        ins_sensitivity_set = in_ins_process_topopt_group['Sensitivity'][in_parameters_list[0]][in_parameters_list[1]]
        if ins_sensitivity_set.shape[1] < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
            available_cpu_number = 1
        else:
            pass
        
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        for ins_design_elements_label_set in in_ins_process_domains_group.values():
            process_elements_index_range_list = [[0,int(ins_design_elements_label_set.shape[0]/available_cpu_number)]]
            for process_index in range(1,available_cpu_number):
                process_elements_index_range_list.append([process_elements_index_range_list[process_index-1][1],process_elements_index_range_list[process_index-1][1]+process_elements_index_range_list[0][1]])
            process_elements_index_range_list[-1][1] = ins_design_elements_label_set.shape[0]

            processes_list = []
            for process_id,index_range in enumerate(process_elements_index_range_list):
                temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                    if self.__filter_list[0] == 'sensitivity':
                        ins_opt_temp_file.create_dataset(name='filter',data=numpy.asarray([1]))
                    elif self.__filter_list[0] == 'density':
                        ins_opt_temp_file.create_dataset(name='filter',data=numpy.asarray([2]))
                        ins_opt_temp_file.create_dataset(name='readyelementsneighbor',data=in_ins_process_topopt_group['neighbor'][ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                        ins_opt_temp_file.create_dataset(name='readyelementsweight',data=in_ins_process_topopt_group['weight'][ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                        with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
                            ins_opt_temp_file.create_dataset(name='readyelementsvolume',data=numpy.asarray([ins_fea_process_file['Update']['geometry'][i][0] for i in ins_design_elements_label_set[index_range[0]:index_range[1]]-1]))
                    else:
                        pass
                    if in_parameters_list[2] == 'sum':
                        ins_opt_temp_file.create_dataset(name='operator',data=numpy.asarray([1]))
                    else:
                        pass
                    ins_opt_temp_file.create_dataset(name='readyelementslabel',data=ins_design_elements_label_set[index_range[0]:index_range[1]])
                    with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
                            ins_opt_temp_file.create_dataset(name='allelementsvolume',data=numpy.asarray([ins_fea_process_file['Update']['geometry'][i][0] for i in range(ins_fea_process_file['Update']['geometry'].shape[0])]))
                    ins_opt_temp_file.create_dataset(name='allelementschaingrad',data=in_ins_process_topopt_group['chaingrad'][0:2])
                    
                    ins_opt_temp_file.create_dataset(name='readyelementsvolsensitivity',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                
                ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsVOLSensitivity,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                processes_list.append(ins_process)

                ins_process.start()
            for ins_process in processes_list:
                ins_process.join()
                        
            for ins_process in processes_list:
                process_id_string = ins_process.name.split('-')[-1]
                ins_process.close()
                
                temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                index_range = process_elements_index_range_list[int(process_id_string)]
            
                with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                    ready_elements_index_array = ins_design_elements_label_set[index_range[0]:index_range[1]]-1
                    ins_sensitivity_set[1,ready_elements_index_array] = ins_opt_temp_file['readyelementsvolsensitivity'][:]
                os.remove(temp_file_full_name)
            del processes_list
    def __calculateSensitivityOfCS(self, in_parameters_list:list, in_ins_process_domains_group:object, in_ins_process_topopt_group:object, in_fea_process_file_full_name:str) -> None:
        available_cpu_number = len([None for i in psutil.cpu_percent(1.0,True) if i < 40.0])-2
        if available_cpu_number <= 0:
            print(f"The CPU usage is too high!")
            raise ChildProcessError()
        else:
            pass
        ins_sensitivity_set = in_ins_process_topopt_group['Sensitivity'][in_parameters_list[0]][in_parameters_list[1]]
        if ins_sensitivity_set.shape[1] < common.P4SFormat.OPEN_MULTIPROCESS_NUM:
            available_cpu_number = 1
        else:
            pass
        
        ins_dpndrcs_set = in_ins_process_topopt_group['dpndrcs']
        aggregation_factor = 5.0
        dpndrcs_temp_value = numpy.sum(ins_dpndrcs_set[:]**aggregation_factor)**(1.0/aggregation_factor-1.0)
        ins_dpndrcs_set[:] = dpndrcs_temp_value*ins_dpndrcs_set[:]**(aggregation_factor-1.0)
        del dpndrcs_temp_value
        
        ins_mulmatrix_set = in_ins_process_topopt_group['mulmatrix']
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        process_local_index_range_list = [[0,int(ins_mulmatrix_set.shape[0]/available_cpu_number)]]
        for process_index in range(1,available_cpu_number):
            process_local_index_range_list.append([process_local_index_range_list[process_index-1][1],process_local_index_range_list[process_index-1][1]+process_local_index_range_list[0][1]])
        process_local_index_range_list[-1][1] = ins_mulmatrix_set.shape[0]
        processes_list = []
        for process_id,index_range in enumerate(process_local_index_range_list):
            temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'

            if in_parameters_list[1] == 'Mises':
                with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                    ins_opt_temp_file.create_dataset(name='readyelementscsc',data=in_ins_process_topopt_group['csc'][:,index_range[0]:index_range[1]])
                    with h5py.File(self.__task_result_file_full_name,'r') as ins_opt_result_file:
                        ins_opt_temp_file.create_dataset(name='readyelementstype',data=ins_opt_result_file['Mesh']['type'][index_range[0]:index_range[1]])
                    with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
                        ins_opt_temp_file.create_dataset(name='readyelementsdm',data=ins_fea_process_file['Update']['dm'][index_range[0]:index_range[1]])
                        ins_opt_temp_file.create_dataset(name='readyelementsbm',data=ins_fea_process_file['Update']['bm'][index_range[0]:index_range[1]])  
                        ins_opt_temp_file.create_dataset(name='readyelementstm',data=ins_fea_process_file['Update']['tm'][index_range[0]:index_range[1]])
                        ins_opt_temp_file.create_dataset(name='readyelementsgeometry',data=ins_fea_process_file['Update']['geometry'][index_range[0]:index_range[1]])
                        
                    ins_opt_temp_file.create_dataset(name='readyelementsmulmatrix',shape=(index_range[1]-index_range[0],),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['float']))  
            else:
                pass

            ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsMulMatrix,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
            processes_list.append(ins_process)

            ins_process.start()
        for ins_process in processes_list:
            ins_process.join()
        for ins_process in processes_list:
            process_id_string = ins_process.name.split('-')[-1]
            ins_process.close()
            
            temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
            index_range = process_local_index_range_list[int(process_id_string)]
        
            with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                for lcoal_index,element_index in enumerate(range(index_range[0],index_range[1])):
                    ins_mulmatrix_set[element_index] = ins_opt_temp_file['readyelementsmulmatrix'][lcoal_index]
            os.remove(temp_file_full_name)
        del processes_list
        del process_local_index_range_list
        
        ins_adjoint_set = in_ins_process_topopt_group['adjoint']
        ins_x_set = in_ins_process_topopt_group['x']
        relaxation_factor = self.__interpolation_model[1]*0.8
        ins_elements_dofs_set = in_ins_process_topopt_group['elmsdofs']
        if self.__interpolation_model[0] == 'SIMP':
            for element_index in range(ins_x_set.shape[1]):
                element_adjoint_right_array = ins_dpndrcs_set[element_index]/(ins_sensitivity_set[0,element_index]*ins_x_set[1,element_index]**relaxation_factor) * ins_mulmatrix_set[element_index]
                for local_index,dof_location in enumerate(ins_elements_dofs_set[element_index]):
                    ins_adjoint_set[0,dof_location] += element_adjoint_right_array[local_index]
        elif self.__interpolation_model[0] == 'RAMP':
            for element_index in range(ins_x_set.shape[1]):
                element_adjoint_right_array = ins_dpndrcs_set[element_index]/(ins_sensitivity_set[0,element_index]*ins_x_set[1,element_index]/(1.0+relaxation_factor-relaxation_factor*ins_x_set[1,element_index])) * ins_mulmatrix_set[element_index]
                for local_index,dof_location in enumerate(ins_elements_dofs_set[element_index]):
                    ins_adjoint_set[0,dof_location] += element_adjoint_right_array[local_index]
        else:
            pass
        ins_constrained_dofs_location_set = in_ins_process_topopt_group['gcdloc']
        ins_adjoint_set[0,ins_constrained_dofs_location_set[:]] = 0.0
        with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
            global_stiffness_matrix = scipy.sparse.coo_matrix((ins_fea_process_file['Update']['gkm'][0,:],(ins_fea_process_file['Update']['gkm'][1,:],ins_fea_process_file['Update']['gkm'][2,:])),shape=(ins_adjoint_set.shape[1],ins_adjoint_set.shape[1]))
            
            for constrained_dof_location in ins_constrained_dofs_location_set[:]:
                global_stiffness_matrix.data[numpy.where(global_stiffness_matrix.row == constrained_dof_location)] = 0.0
                global_stiffness_matrix.data[numpy.where(global_stiffness_matrix.col == constrained_dof_location)] = 0.0
            global_stiffness_matrix = global_stiffness_matrix.todok()
            for constrained_dof_location in ins_constrained_dofs_location_set[:]:
                global_stiffness_matrix[constrained_dof_location,constrained_dof_location] = 1.0
            
            global_stiffness_matrix = global_stiffness_matrix.tocsr()
            for instnace_dofs_loc_range in ins_fea_process_file['Constant']['Instances'].values():
                instance_include_global_stiffness_matrix = global_stiffness_matrix[instnace_dofs_loc_range[0]:instnace_dofs_loc_range[1]+1,:][:,instnace_dofs_loc_range[0]:instnace_dofs_loc_range[1]+1]
                
                matrix_non_all_zero_rows_index_array = numpy.where(instance_include_global_stiffness_matrix.getnnz(axis=0) > 0)[0]
                solved_stiffness_matrix = instance_include_global_stiffness_matrix[matrix_non_all_zero_rows_index_array,:][:,matrix_non_all_zero_rows_index_array]
                solved_adjoint_right_array = ins_adjoint_set[0,instnace_dofs_loc_range[0]+matrix_non_all_zero_rows_index_array]
                
                ins_adjoint_set[1,instnace_dofs_loc_range[0]+matrix_non_all_zero_rows_index_array] = lsolver_dict[1][1](solved_stiffness_matrix,solved_adjoint_right_array)
            
            del global_stiffness_matrix
            del solved_stiffness_matrix
            del solved_adjoint_right_array
            del matrix_non_all_zero_rows_index_array
            del instance_include_global_stiffness_matrix
        
        ins_elements_u_set = in_ins_process_topopt_group['elmsu']
        ins_elements_adjoint_set = in_ins_process_topopt_group['elmsadjoint']
        with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
            ins_dofs_u_set = ins_fea_process_file['Record']['u']
            for element_index in range(ins_elements_u_set.shape[0]):
                ins_elements_u_set[element_index] = numpy.array([ins_dofs_u_set[i] for i in ins_elements_dofs_set[element_index]])
                ins_elements_adjoint_set[element_index] = numpy.array([ins_adjoint_set[1,i] for i in ins_elements_dofs_set[element_index]])
        
        ins_dpndxphy_set = in_ins_process_topopt_group['dpndxphy']
        ins_ifa_set = in_ins_process_topopt_group['ifa']
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        for ins_design_elements_label_set in in_ins_process_domains_group.values():
            process_elements_index_range_list = [[0,int(ins_design_elements_label_set.shape[0]/available_cpu_number)]]
            for process_index in range(1,available_cpu_number):
                process_elements_index_range_list.append([process_elements_index_range_list[process_index-1][1],process_elements_index_range_list[process_index-1][1]+process_elements_index_range_list[0][1]])
            process_elements_index_range_list[-1][1] = ins_design_elements_label_set.shape[0]

            processes_list = []
            for process_id,index_range in enumerate(process_elements_index_range_list):
                temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                
                elements_index_array = ins_design_elements_label_set[index_range[0]:index_range[1]]-1
                with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                    if in_parameters_list[1] == 'Mises':
                        ins_opt_temp_file.create_dataset(name='readyelementsdpndrcs',data=ins_dpndrcs_set[elements_index_array])
                        if self.__interpolation_model[0] == 'SIMP':
                            ins_opt_temp_file.create_dataset(name='interpolationparameters',data=numpy.asarray([1.0,self.__interpolation_model[1]]))
                        elif self.__interpolation_model[0] == 'RAMP':
                            ins_opt_temp_file.create_dataset(name='interpolationparameters',data=numpy.asarray([2.0,self.__interpolation_model[1]]))
                        else:
                            pass
                        ins_opt_temp_file.create_dataset(name='readyelementsxphy',data=ins_x_set[1,elements_index_array])
                        ins_opt_temp_file.create_dataset(name='readyelementsifa',data=ins_ifa_set[elements_index_array])
                        ins_opt_temp_file.create_dataset(name='readyelementsmulmatrix',data=ins_mulmatrix_set[elements_index_array])
                        ins_opt_temp_file.create_dataset(name='readyelementsu',data=ins_elements_u_set[elements_index_array])
                        ins_opt_temp_file.create_dataset(name='readyelementscs',data=ins_sensitivity_set[0,elements_index_array])
                        ins_opt_temp_file.create_dataset(name='readyelementsadjoint',data=ins_elements_adjoint_set[elements_index_array])
                        with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
                            ins_opt_temp_file.create_dataset(name='readyelementskm',data=ins_fea_process_file['Update']['km'][elements_index_array])
                        
                        ins_opt_temp_file.create_dataset(name='readyelementsdpndxphy',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])  

                        ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsMisesPNGradient,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                    else:
                        pass
                processes_list.append(ins_process)

                ins_process.start()
            for ins_process in processes_list:
                ins_process.join()
                        
            for ins_process in processes_list:
                process_id_string = ins_process.name.split('-')[-1]
                ins_process.close()
                
                temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                index_range = process_elements_index_range_list[int(process_id_string)]
            
                with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                    ins_dpndxphy_set[ins_design_elements_label_set[index_range[0]:index_range[1]]-1] = ins_opt_temp_file['readyelementsdpndxphy'][:]
                os.remove(temp_file_full_name)
            del processes_list
        
        temp_file_head_name = self.__task_file_full_name.split('.')[0]
        process_base_name = os.path.basename(self.__task_file_full_name).split('.')[0] + '-'
        for ins_design_elements_label_set in in_ins_process_domains_group.values():
            process_elements_index_range_list = [[0,int(ins_design_elements_label_set.shape[0]/available_cpu_number)]]
            for process_index in range(1,available_cpu_number):
                process_elements_index_range_list.append([process_elements_index_range_list[process_index-1][1],process_elements_index_range_list[process_index-1][1]+process_elements_index_range_list[0][1]])
            process_elements_index_range_list[-1][1] = ins_design_elements_label_set.shape[0]

            processes_list = []
            for process_id,index_range in enumerate(process_elements_index_range_list):
                temp_file_full_name = temp_file_head_name + '-' + str(process_id) + '.opttemp'
                with h5py.File(temp_file_full_name,'w') as ins_opt_temp_file:
                    if self.__filter_list[0] == 'sensitivity':
                        ins_opt_temp_file.create_dataset(name='filter',data=numpy.array([1]))
                    elif self.__filter_list[0] == 'density':
                        ins_opt_temp_file.create_dataset(name='filter',data=numpy.array([2]))
                        ins_opt_temp_file.create_dataset(name='readyelementsneighbor',data=in_ins_process_topopt_group['neighbor'][ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                        ins_opt_temp_file.create_dataset(name='readyelementsweight',data=in_ins_process_topopt_group['weight'][ins_design_elements_label_set[index_range[0]:index_range[1]]-1])
                        with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
                            ins_opt_temp_file.create_dataset(name='readyelementsvolume',data=numpy.asarray([ins_fea_process_file['Update']['geometry'][i][0] for i in ins_design_elements_label_set[index_range[0]:index_range[1]]-1]))
                    else:
                        pass
                    ins_opt_temp_file.create_dataset(name='readyelementslabel',data=ins_design_elements_label_set[index_range[0]:index_range[1]])
                    ins_opt_temp_file.create_dataset(name='allelementsdpndxphy',data=ins_dpndxphy_set[:])
                    ins_opt_temp_file.create_dataset(name='allelementschaingrad',data=in_ins_process_topopt_group['chaingrad'][0:2])
                    
                    ins_opt_temp_file.create_dataset(name='readyelementscssensitivity',shape=index_range[1]-index_range[0],dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                
                ins_process = multiprocessing.Process(target=common.P4SOptimizationInfo.getElementsCSSensitivity,name=process_base_name+str(process_id),args=[temp_file_full_name,],)
                processes_list.append(ins_process)

                ins_process.start()
            for ins_process in processes_list:
                ins_process.join()
                        
            for ins_process in processes_list:
                process_id_string = ins_process.name.split('-')[-1]
                ins_process.close()
                
                temp_file_full_name = temp_file_head_name + '-' + process_id_string + '.opttemp'
                index_range = process_elements_index_range_list[int(process_id_string)]
            
                with h5py.File(temp_file_full_name,'r') as ins_opt_temp_file:
                    ins_sensitivity_set[1,ins_design_elements_label_set[index_range[0]:index_range[1]]-1] = ins_opt_temp_file['readyelementscssensitivity'][:]
                os.remove(temp_file_full_name)
            del processes_list
    
    def __calculateBinarizedStructureFrmoVolumeConstrain(self, in_ins_x_set:object,in_fea_process_file_full_name:str,in_constrain_value:float) -> None:
        with h5py.File(in_fea_process_file_full_name, 'r') as in_fea_process_file:
            ins_elements_geometry_set = in_fea_process_file['Update']['geometry']
            binaryzation_threshold = 1.0
            while binaryzation_threshold >= 0.0:
                volume_value = 0.0
                
                solid_elements_index_array = numpy.where(in_ins_x_set[1,:]>=binaryzation_threshold)[0]
                for element_index in solid_elements_index_array:
                    volume_value += ins_elements_geometry_set[element_index][0]

                if volume_value >= in_constrain_value:
                    break
                else:
                    binaryzation_threshold -= 0.0001
            in_ins_x_set[1,:] = 0.01
            in_ins_x_set[1,solid_elements_index_array] = 1.0
