# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

import numpy
import vtk
import h5py


class P4SString():
    
    VERSION_NUMBER = r'P4StructV1.0'


class P4SFormat():

    NAME_FORMAT = r'[a-zA-Z0-9\@\#\%\^\_\-\+\=\:]+'
    POSTTIVE_FLOAT_FORMAT = r'[1-9]\d*\.\d*|0\.\d*[1-9]\d*'
    FLOAT_FORMAT = r'^-?(0|[1-9]\d*)\.\d*[1-9]\d*$'
    POSTTIVE_INTEGER_FORMAT = r'[1-9]\d*'
    DECIMAL_FORMAT = r'^-?0\.\d*[1-9]\d*'
    
    OPEN_MULTIPROCESS_NUM = 5000
    NUMERICAL_PRECISION = {'int':'int64', 'float':'float64'}


class P4SImportInfo():
    
    SUPPORTED_FILE_TYPE = '*.inp;;*.p4st;;*.task;;*.p4sres'
    
    SUPPORTED_INP_ELEMENTS_BY_DIMENSION = {
        '2D':["T2D2","T2D2H","B21","B21H","B23","B23H","PIPE21","PIPE21H","T2D2T",
                "CPS3","CPE3","CPE3H","CPEG3","CPEG3H","CPE3T","CPEG3T","CPS3T","CPEG3HT","WARP2D3",
                "CPS4","CPS4R","CPS4I","CPE4","CPE4H","CPE4R","CPE4I","CPE4RH","CPE4IH","CPEG4","CPEG4H","CPEG4R","CPEG4I","CPEG4RH","CPEG4IH","CPE4T","CPE4HT",
                "CPE4RT","CPE4RHT","CPEG4T","CPEG4HT","CPEG4RT","CPEG4RHT","CPS4T","CPS4RT","COH2D4T","COH2D4","WARP2D4"],
        '3D':["T3D2","T3D2H","B31","B31H","B31OS","B31OSH","B33","B33H","PIPE31","PIPE31H","ELBOW31","ELBOW31B","ELBOW31C","T3D2T",
                "S3","STRI3","SFM3D3","M3D3","S3T",
                "S4","S4R","S4R5","SHEAR4","SFM3D4","M3D4","M3D4R","S4T","S4RT",
                "C3D4","C3D4H","C3D4T",
                "C3D8","C3D8H","C3D8R","C3D8I","C3D8S","C3D8RH","C3D8IH","C3D8HS","COH3D8","COH3D8T","SC8R","CSS8","C3D8T","C3D8HT","C3D8RT","C3D8RHT"]
        }
    SUPPORTED_INP_ELEMENTS_BY_GEOMETRY_NUMBER = {
        '2D':{
            1:["T2D2","T2D2H","B21","B21H","B23","B23H","PIPE21","PIPE21H","T2D2T"],
            2:["CPS3","CPE3","CPE3H","CPEG3","CPEG3H","CPE3T","CPEG3T","CPS3T","CPEG3HT","WARP2D3"],
            3:["CPS4","CPS4R","CPS4I","CPE4","CPE4H","CPE4R","CPE4I","CPE4RH","CPE4IH","CPEG4","CPEG4H","CPEG4R","CPEG4I","CPEG4RH","CPEG4IH","CPE4T","CPE4HT",
                "CPE4RT","CPE4RHT","CPEG4T","CPEG4HT","CPEG4RT","CPEG4RHT","CPS4T","CPS4RT","COH2D4T","COH2D4","WARP2D4"],
            6:["T2D3","T2D3H","B22","B22H","PIPE22","PIPE22H","T2D3T"],
            7:["CPS6","CPS6M","CPE6","CPE6H","CPE6M","CPE6MH","CPEG6","CPEG6H","CPEG6M","CPEG6MH","CPE6MT","CPE6MHT","CPEG6MT","CPEG6MHT","CPS6MT","WARP2D3"],
            8:["CPS8","CPS8R","CPE8","CPE8H","CPE8R","CPE8RH","CPEG8","CPEG8H","CPEG8R","CPEG8RH","CPE8T","CPEG8T","CPS8T","CPE8HT","CPE8RHT","CPEG8HT",
                "CPEG8RHT","CPS8RT"]},
        '3D':{
            1:["T3D2","T3D2H","B31","B31H","B31OS","B31OSH","B33","B33H","","PIPE31","PIPE31H","ELBOW31","ELBOW31B","ELBOW31C","T3D2T"],
            2:["S3","STRI3","SFM3D3","M3D3","S3T"],
            3:["S4","S4R","S4R5","SHEAR4","SFM3D4","M3D4","M3D4R","S4T","S4RT"],
            4:["C3D4","C3D4H","C3D4T"],
            5:["C3D8","C3D8H","C3D8R","C3D8I","C3D8S","C3D8RH","C3D8IH","C3D8HS","COH3D8","COH3D8T","SC8R","CSS8","C3D8T","C3D8HT","C3D8RT","C3D8RHT"],
            6:["T3D3","T3D3H","PIPE32","PIPE32H","ELBOW32","T3D3T","B32","B32H","B32OS","B32OSH"],
            7:["STRI65","SFM3D6","M3D6"],
            8:["S8R5","S8R","SFM3D8","SFM3D8R","M3D8","M3D8R","S8RT"],
            9:["C3D10","C3D10H","C3D10M","C3D10HS","C3D10MH","C3D10MT"],
            10:["C3D20","C3D20H","C3D20R","C3D20RH","C3D20T","C3D20HT","C3D20RT","C3D20RHT"]}
        }


class P4SElementInfo():

    SUPPORT_GEOMETRY_2D = ['line','triangle','quadrilateral','quadratic-line','quadratic-triangle','quadratic-quadrilateral']
    SUPPORT_GEOMETRY_3D = ['line','triangle','quadrilateral','tetrahedron','hexahedron','quadratic-line',
                        'quadratic-triangle','quadratic-quadrilateral','quadratic-tetrahedron','quadratic-hexahedron']
    
    FLAG_TO_NUMBER = {'truss':1,'plane':3,'shell':4,'solid':6}
    NUMBER_TO_FLAG = {1:'truss',3:'plane',4:'shell',6:'solid'}

    FLAG_2D = ['truss', 'plane']
    FLAG_3D = ['truss', 'shell', 'solid']

    GEOMETRY_TO_NUMBER = {'line':1,'triangle':2,'quadrilateral':3,'tetrahedron':4,'hexahedron':5,
                            'quadratic-line':6,'quadratic-triangle':7,'quadratic-quadrilateral':8,
                            'quadratic-tetrahedron':9,'quadratic-hexahedron':10}
    NUMBER_TO_GEOMETRY = {1:'line',2:'triangle',3:'quadrilateral',4:'tetrahedron',5:'hexahedron',
                            6:'quadratic-line',7:'quadratic-triangle',8:'quadratic-quadrilateral',
                            9:'quadratic-tetrahedron',10:'quadratic-hexahedron'}

    GEOMETRY_INCLUDE_FLAGS_2D = {'line':['truss'], 'triangle':['plane'], 'quadrilateral':['plane'], 'tetrahedron':['solid'], 'hexahedron':['solid'],
                                'quadratic-line':['truss'], 'quadratic-triangle':['plane'], 'quadratic-quadrilateral':['plane'],
                                'quadratic-tetrahedron':['solid'], 'quadratic-hexahedron':['solid']}
    GEOMETRY_INCLUDE_FLAGS_3D = {'line':['truss'], 'triangle':['shell'], 'quadrilateral':['shell'], 'tetrahedron':['solid'], 'hexahedron':['solid'],
                                'quadratic-line':['truss'], 'quadratic-triangle':['shell'], 'quadratic-quadrilateral':['shell'],
                                'quadratic-tetrahedron':['solid'], 'quadratic-hexahedron':['solid']}

    FLAG_INCLUDE_ELEMENTS_TYPE_2D = {'truss':['TCT2D2'],'beam':[],'plane':['PS3','PE3','PS4','PE4']}
    FLAG_INCLUDE_ELEMENTS_TYPE_3D = {'truss':['TCT3D2'],'beam':[],'shell':['S3','S4'],'solid':['SO4','SO8']}

    GEOMETRY_INCLUDE_ELEMENTS_TYPE_2D = {'line':['TCT2D2'],'quadratic-line':[],
                                         'triangle':['PS3','PE3'],'quadratic-triangle':[],
                                         'quadrilateral':['PS4','PE4'],'quadratic-quadrilateral':[]}
    GEOMETRY_INCLUDE_ELEMENTS_TYPE_3D = {'line':['TCT3D2'],'quadratic-line':[],
                                         'triangle':['S3'],'quadratic-triangle':[],
                                         'quadrilateral':['S4'],'quadratic-quadrilateral':[],
                                         'tetrahedron':['SO4'],'quadratic-tetrahedron':[],
                                         'hexahedron':['SO8'],'quadratic-hexahedron':[]}

    ELEMENTS_TYPE_DESCRIPTION = {
        'TCT2D2':'2D linear tension and compression truss element with 2 nodes',
        'PS3':'2D linear plane stress element with 3 nodes',
        'PE3':'2D linear plane strain element with 3 nodes',
        'PS4':'2D linear plane stress element with 4 nodes',
        'PE4':'2D linear plane strain element with 4 nodes,modified',
        
        'TCT3D2':'3D linear tension and compression truss element with 2 nodes',
        'S3':'3D linear general shell element with 3 node, using 6 degrees of freedom per node',
        'S4':'3D linear general shell element with 4 node, using 6 degrees of freedom per node',
        'SO4':'3D linear tetrahedron general element with 4 nodes',
        'SO8':'3D linear hexahedral general element with 8 nodes,modified'
        }
    ELEMENTS_TYPE_TO_NUMBER = {
        'TCT2D2':121,
        'PS3':321,'PE3':322,'PS4':323,'PE4':324,
        
        'TCT3D2':131,
        'S3':431,'S4':432,
        'SO4':631,'SO8':632
    }
    ELEMENTS_NUMBER_TO_TYPE = {
        121:'TCT2D2',
        321:'PS3',322:'PE3',323:'PS4',324:'PE4',
        
        131:'TCT3D2',
        431:'S3',432:'S4',
        631:'SO4',632:'SO8'
    }
    ELEMENT_NUMBER_TO_DOFS = {
        121:[1,2],
        321:[1,2],322:[1,2],323:[1,2],324:[1,2],
        
        131:[1,2,3],
        431:[1,2,3,4,5,6], 432:[1,2,3,4,5,6],
        631:[1,2,3],632:[1,2,3]
    }
    
    @staticmethod
    def getElementsTBDKMatrixes(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            ins_ready_elements_set = ins_file['readyelements']
            ins_all_nodes_set = ins_file['allnodes']
            ins_ready_elements_type_set = ins_file['readyelementstype']
            ins_ready_elements_attributes_set = ins_file['readyelementsattributes']
            ins_ready_elements_materials_set = ins_file['readyelementsmaterials']
            ins_ready_elements_geometry_number_set = ins_file['readyelementsgeomnum']
            ins_property_attributes_group = ins_file['PropAttributes']
            ins_property_materials_group = ins_file['PropMaterials']
            ins_ready_elements_material_ifa_set = ins_file['readyelementsifa']
            ins_ready_elements_orientation_set = ins_file['readyelementsorientation']
            
            ins_update_elements_geometry_set = ins_file['readyelementsgeometry']
            ins_update_elements_tm_set = ins_file['readyelementstm']
            ins_update_elements_dm_set = ins_file['readyelementsdm']
            ins_update_elements_bm_set = ins_file['readyelementsbm']
            ins_update_elements_km_set = ins_file['readyelementskm']
            
            elements_number = ins_ready_elements_set.shape[0]
            for local_index in range(elements_number):
                element_include_nodes_coordinate_list = []
                for node_label in ins_ready_elements_set[local_index][:]:
                    element_include_nodes_coordinate_list.append(ins_all_nodes_set[node_label-1])
                element_include_nodes_coordinate_array = numpy.asarray(element_include_nodes_coordinate_list)
            
                element_attribute_parameters_array = ins_property_attributes_group[str(ins_ready_elements_attributes_set[local_index])]
                element_type_number = ins_ready_elements_type_set[local_index]
                element_material_parameters_array = ins_property_materials_group[str(ins_ready_elements_materials_set[local_index])]
                
                element_geometry_array = P4SElementInfo.__calculateGeometryInfo(ins_ready_elements_geometry_number_set[local_index],element_include_nodes_coordinate_array,element_attribute_parameters_array)
                ins_update_elements_geometry_set[local_index] = element_geometry_array
                
                ins_update_elements_tm_set[local_index] = P4SElementInfo.__calculateElementTransformArray(element_type_number,element_geometry_array,element_include_nodes_coordinate_array)
                ins_update_elements_dm_set[local_index] = ins_ready_elements_material_ifa_set[local_index]*P4SElementInfo.__calculateElementConstitutiveArray(element_type_number,element_material_parameters_array,ins_ready_elements_orientation_set[local_index])
                ins_update_elements_bm_set[local_index],ins_update_elements_km_set[local_index] = P4SElementInfo.__calculateElementStrainAndGlobalStiffnessArray(element_type_number,element_include_nodes_coordinate_array,element_geometry_array,ins_update_elements_tm_set[local_index],ins_update_elements_dm_set[local_index])
    # region
    @staticmethod
    def __calculateGeometryInfo(in_geometry_number:int,in_nodes_coordinate:numpy.ndarray,in_attribute_parameters:numpy.ndarray) -> numpy.ndarray:
        if in_geometry_number == 1:
            line_length = numpy.sqrt(numpy.sum(numpy.square((in_nodes_coordinate[1] - in_nodes_coordinate[0]))))
            
            element_section_type_number = in_attribute_parameters[0]
            if element_section_type_number == 1:
                cross_sectional_area = in_attribute_parameters[1]
                line_volume =  line_length*cross_sectional_area
                
                geometry_info_array = numpy.array([line_volume,line_length],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            else:
                pass

            return geometry_info_array
        elif in_geometry_number == 2:
            surface_thickness = in_attribute_parameters[1]

            vector1 = in_nodes_coordinate[1] - in_nodes_coordinate[0]
            vector2 = in_nodes_coordinate[2] - in_nodes_coordinate[0]
            object_vector = numpy.cross(vector1,vector2)
            unit_object_vector = numpy.sqrt(object_vector[0]**2+object_vector[1]**2+object_vector[2]**2)
            surface_area = unit_object_vector*0.5
            
            surface_volume =  surface_thickness*surface_area

            return numpy.array([surface_volume,surface_area],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        elif in_geometry_number == 3:
            surface_thickness = in_attribute_parameters[1]

            vector1 = in_nodes_coordinate[1] - in_nodes_coordinate[0]
            vector2 = in_nodes_coordinate[2] - in_nodes_coordinate[0]
            object_vector = numpy.cross(vector1,vector2)
            unit_object_vector = numpy.sqrt(object_vector[0]**2+object_vector[1]**2+object_vector[2]**2)
            surface_area1 = unit_object_vector*0.5
            vector1 = in_nodes_coordinate[2] - in_nodes_coordinate[0]
            vector2 = in_nodes_coordinate[3] - in_nodes_coordinate[0]
            object_vector = numpy.cross(vector1,vector2)
            unit_object_vector = numpy.sqrt(object_vector[0]**2+object_vector[1]**2+object_vector[2]**2)
            surface_area2 = unit_object_vector*0.5
            surface_area = surface_area1+surface_area2

            surface_volume =  surface_thickness*surface_area

            return numpy.array([surface_volume,surface_area],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        elif in_geometry_number == 4:
            calculate_matrix = numpy.ones((4,4))
            calculate_matrix[0][1:4] = in_nodes_coordinate[0]
            calculate_matrix[1][1:4] = in_nodes_coordinate[1]
            calculate_matrix[2][1:4] = in_nodes_coordinate[2]
            calculate_matrix[3][1:4] = in_nodes_coordinate[3]
            solid_volume = numpy.linalg.det(calculate_matrix) / 6.0
            
            return numpy.array([solid_volume],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        elif in_geometry_number == 5:
            centroid_point_coordinates = numpy.sum(in_nodes_coordinate,axis=0) / 8.0
            
            calculate_matrix = numpy.ones((4,4))
            calculate_matrix[3][1:4] = centroid_point_coordinates
            calculate_matrix[0][1:4] = in_nodes_coordinate[0]
            calculate_matrix[1][1:4] = in_nodes_coordinate[1]
            calculate_matrix[2][1:4] = in_nodes_coordinate[2]
            solid_volume1 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[0]
            calculate_matrix[1][1:4] = in_nodes_coordinate[2]
            calculate_matrix[2][1:4] = in_nodes_coordinate[3]
            solid_volume2 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[4]
            calculate_matrix[1][1:4] = in_nodes_coordinate[5]
            calculate_matrix[2][1:4] = in_nodes_coordinate[6]
            solid_volume3 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[4]
            calculate_matrix[1][1:4] = in_nodes_coordinate[6]
            calculate_matrix[2][1:4] = in_nodes_coordinate[7]
            solid_volume4 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[0]
            calculate_matrix[1][1:4] = in_nodes_coordinate[1]
            calculate_matrix[2][1:4] = in_nodes_coordinate[5]
            solid_volume5 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[0]
            calculate_matrix[1][1:4] = in_nodes_coordinate[5]
            calculate_matrix[2][1:4] = in_nodes_coordinate[4]
            solid_volume6 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[3]
            calculate_matrix[1][1:4] = in_nodes_coordinate[2]
            calculate_matrix[2][1:4] = in_nodes_coordinate[6]
            solid_volume7 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[2]
            calculate_matrix[1][1:4] = in_nodes_coordinate[6]
            calculate_matrix[2][1:4] = in_nodes_coordinate[7]
            solid_volume8 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[0]
            calculate_matrix[1][1:4] = in_nodes_coordinate[3]
            calculate_matrix[2][1:4] = in_nodes_coordinate[7]
            solid_volume9 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[0]
            calculate_matrix[1][1:4] = in_nodes_coordinate[7]
            calculate_matrix[2][1:4] = in_nodes_coordinate[4]
            solid_volume10 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[1]
            calculate_matrix[1][1:4] = in_nodes_coordinate[2]
            calculate_matrix[2][1:4] = in_nodes_coordinate[6]
            solid_volume11 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            calculate_matrix[0][1:4] = in_nodes_coordinate[1]
            calculate_matrix[1][1:4] = in_nodes_coordinate[6]
            calculate_matrix[2][1:4] = in_nodes_coordinate[5]
            solid_volume12 = numpy.abs(numpy.linalg.det(calculate_matrix) / 6.0)
            solid_volume = solid_volume1 + solid_volume2 + solid_volume3 + solid_volume4 + solid_volume5 + solid_volume6
            solid_volume += solid_volume7 + solid_volume8 + solid_volume9 + solid_volume10 + solid_volume11 + solid_volume12
            
            return numpy.array([solid_volume],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        elif in_geometry_number == 6:
            pass
        elif in_geometry_number == 7:
            pass
        elif in_geometry_number == 8:
            pass
        elif in_geometry_number == 9:
            pass
        elif in_geometry_number == 10:
            pass
        else:
            pass
    @staticmethod
    def __calculateElementTransformArray(in_type_number:int,in_geometry_parameters:numpy.ndarray,in_nodes_coordinate:numpy.ndarray) -> numpy.ndarray:
        if in_type_number == 121:
            transform_matrix = numpy.zeros((2,4),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            transform_matrix[[0,1],[0,2]] = (in_nodes_coordinate[1,0] - in_nodes_coordinate[0,0]) / in_geometry_parameters[1]
            transform_matrix[[0,1],[1,3]] = (in_nodes_coordinate[1,1] - in_nodes_coordinate[0,1]) / in_geometry_parameters[1]
        elif in_type_number == 131:
            transform_matrix = numpy.zeros((2,6),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            transform_matrix[[0,1],[0,3]] = (in_nodes_coordinate[1,0] - in_nodes_coordinate[0,0]) / in_geometry_parameters[1]
            transform_matrix[[0,1],[1,4]] = (in_nodes_coordinate[1,1] - in_nodes_coordinate[0,1]) / in_geometry_parameters[1]
            transform_matrix[[0,1],[2,5]] = (in_nodes_coordinate[1,2] - in_nodes_coordinate[0,2]) / in_geometry_parameters[1]
        elif in_type_number in [431,432]:
            transform_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            element_local_x_axis_vector = in_nodes_coordinate[1,:] - in_nodes_coordinate[0,:]
            transform_matrix[0] = element_local_x_axis_vector / numpy.linalg.norm(element_local_x_axis_vector)
            element_local_z_axis_vector = numpy.cross(element_local_x_axis_vector,in_nodes_coordinate[2,:] - in_nodes_coordinate[0,:])
            transform_matrix[2] = element_local_z_axis_vector / numpy.linalg.norm(element_local_z_axis_vector)
            element_local_y_axis_vector = numpy.cross(element_local_z_axis_vector,element_local_x_axis_vector)
            transform_matrix[1] = element_local_y_axis_vector / numpy.linalg.norm(element_local_y_axis_vector)
        else:
            transform_matrix = numpy.array([1.0],dtype=P4SFormat.NUMERICAL_PRECISION['float'])

        return transform_matrix.flatten()
    @staticmethod
    def __calculateElementConstitutiveArray(in_type_number:int,in_material_parameters:numpy.ndarray,in_orientation:numpy.ndarray) -> numpy.ndarray:
        elasticity_type_number = in_material_parameters[0]
        constitutive_model_number = in_material_parameters[1]
        constitutive_parameters_array = in_material_parameters[2:]
        
        if in_type_number in [121,131]:
            if elasticity_type_number == 1:
                constitutive_stiffness_matrix = numpy.zeros((1,1),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                
                if constitutive_model_number == 1:
                    constitutive_stiffness_matrix[0,0] = constitutive_parameters_array[0]
                else:
                    pass
            else:
                pass
        elif in_type_number in [321,323]:
            if elasticity_type_number == 1:
                constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                
                if constitutive_model_number == 1:
                    constitutive_stiffness_matrix[[0,1],[0,1]] = 1.0
                    constitutive_stiffness_matrix[[0,1],[1,0]] = constitutive_parameters_array[1]
                    constitutive_stiffness_matrix[2,2] = (1.0 - constitutive_parameters_array[1]) * 0.5
                    constitutive_stiffness_matrix = constitutive_stiffness_matrix * (constitutive_parameters_array[0] / (1.0 - constitutive_parameters_array[1]**2))
                else:
                    pass
            else:
                pass
        elif in_type_number in [322,324]:
            if elasticity_type_number == 1:
                constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                
                if constitutive_model_number == 1:
                    constitutive_stiffness_matrix[[0,1],[0,1]] = 1.0
                    constitutive_stiffness_matrix[[0,1],[1,0]] = constitutive_parameters_array[1] / (1.0-constitutive_parameters_array[1])
                    constitutive_stiffness_matrix[2,2] = 0.5*(1.0 - 2.0*constitutive_parameters_array[1]) / (1.0-constitutive_parameters_array[1])
                    constitutive_stiffness_matrix = constitutive_stiffness_matrix * constitutive_parameters_array[0] * (1.0-constitutive_parameters_array[1]) / ((1.0+constitutive_parameters_array[1])*(1.0-2.0*constitutive_parameters_array[1]))
                else:
                    pass
            else:
                pass
        elif in_type_number in [431,432]:
            if elasticity_type_number == 1:
                constitutive_stiffness_matrix = numpy.zeros((1,9),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                
                if constitutive_model_number == 1:
                    constitutive_stiffness_matrix[[0,0],[0,3]] = 1.0 * (constitutive_parameters_array[0] / (1.0 - constitutive_parameters_array[1]**2))
                    constitutive_stiffness_matrix[0,1] = constitutive_parameters_array[1] * (constitutive_parameters_array[0] / (1.0 - constitutive_parameters_array[1]**2))
                    constitutive_stiffness_matrix[[0,0],[2,4]] = 0.0
                    constitutive_stiffness_matrix[0,5] = (1.0-constitutive_parameters_array[1])*0.5 * (constitutive_parameters_array[0] / (1.0 - constitutive_parameters_array[1]**2))
                    constitutive_stiffness_matrix[[0,0],[6,8]] = constitutive_parameters_array[0] / (2.0*(1.0 + constitutive_parameters_array[1]))
                    constitutive_stiffness_matrix[0,7] = 0.0
                else:
                    pass
            else:
                pass
        elif in_type_number in [631,632]:
            if elasticity_type_number == 1:
                constitutive_stiffness_matrix = numpy.zeros((6,6),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                
                if constitutive_model_number == 1:
                    constitutive_stiffness_matrix[[0,1,2],[0,1,2]] = 1.0 - constitutive_parameters_array[1]
                    constitutive_stiffness_matrix[[0,0,1,1,2,2],[1,2,0,2,0,1]] = constitutive_parameters_array[1]
                    constitutive_stiffness_matrix[[3,4,5],[3,4,5]] = (1.0 - 2.0 * constitutive_parameters_array[1]) * 0.5
                    constitutive_stiffness_matrix = constitutive_stiffness_matrix * (constitutive_parameters_array[0] / ((1.0 + constitutive_parameters_array[1])*(1.0 - 2.0 * constitutive_parameters_array[1])))
                else:
                    pass
            else:
                pass
        else:
            pass
        
        return constitutive_stiffness_matrix.flatten()
    @staticmethod
    def __calculateElementStrainAndGlobalStiffnessArray(in_type_number:int,in_nodes_coordinate:numpy.ndarray,in_geometry_parameters:numpy.ndarray,in_transform_array:numpy.ndarray,in_constitutive_array:numpy.ndarray) -> numpy.ndarray:
        if in_type_number == 121:
            strain_displacement_matrix =  numpy.true_divide(numpy.array([-1.0,1.0],dtype=P4SFormat.NUMERICAL_PRECISION['float']),in_geometry_parameters[1])
            
            local_stiffness_matrix = numpy.array([[1.0,-1.0],[-1.0,1.0]],dtype=P4SFormat.NUMERICAL_PRECISION['float'])*in_constitutive_array[0]*in_geometry_parameters[0]/in_geometry_parameters[1]**2
            transform_matrix = in_transform_array.reshape((2,4))
            global_stiffness_matrix = numpy.dot(numpy.dot(transform_matrix.T,local_stiffness_matrix),transform_matrix)        
        elif in_type_number in [321,322]:
            strain_displacement_matrix = numpy.zeros((3,6),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            strain_displacement_matrix[[0,2],[0,1]] = in_nodes_coordinate[1,1] - in_nodes_coordinate[2,1]
            strain_displacement_matrix[[0,2],[2,3]] = in_nodes_coordinate[2,1] - in_nodes_coordinate[0,1]
            strain_displacement_matrix[[0,2],[4,5]] = in_nodes_coordinate[0,1] - in_nodes_coordinate[1,1]
            strain_displacement_matrix[[1,2],[1,0]] = in_nodes_coordinate[2,0] - in_nodes_coordinate[1,0]
            strain_displacement_matrix[[1,2],[3,2]] = in_nodes_coordinate[0,0] - in_nodes_coordinate[2,0]
            strain_displacement_matrix[[1,2],[5,4]] = in_nodes_coordinate[1,0] - in_nodes_coordinate[0,0]
            strain_displacement_matrix = numpy.true_divide(strain_displacement_matrix,2.0 * in_geometry_parameters[1])
            
            constitutive_stiffness_matrix = in_constitutive_array.reshape((3,3))
            global_stiffness_matrix = numpy.dot(numpy.dot(strain_displacement_matrix.T, constitutive_stiffness_matrix),strain_displacement_matrix) * in_geometry_parameters[0]
        elif in_type_number == 323:
            constitutive_stiffness_matrix = in_constitutive_array.reshape((3,3))
            
            natural_coordinates_coefficient_list = [(-1,-1),(1,-1),(1,1),(-1,1)]
            strain_matrixes_list = []
            global_stiffness_matrix = numpy.zeros((8,8),dtype=P4SFormat.NUMERICAL_PRECISION['float'])

            integration_points_number1,integration_points_number2 = 2,2
            integration_points_array1, weights_array1 = numpy.polynomial.legendre.leggauss(integration_points_number1)
            integration_points_array2, weights_array2 = numpy.polynomial.legendre.leggauss(integration_points_number2)
            for i2 in range(integration_points_number2):
                for i1 in range(integration_points_number1):
                    natural_shape_derivative_func = numpy.empty((2,4),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(4):
                        natural_shape_derivative_func[0,i] = 0.25*natural_coordinates_coefficient_list[i][0]*(1.0+integration_points_array2[i2]*natural_coordinates_coefficient_list[i][1])
                        natural_shape_derivative_func[1,i] = 0.25*(1.0+integration_points_array1[i1]*natural_coordinates_coefficient_list[i][0])*natural_coordinates_coefficient_list[i][1]
                    
                    jacobi_matrix = numpy.empty((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    jacobi_matrix[0,0] = numpy.dot(natural_shape_derivative_func[0],in_nodes_coordinate[:,0])
                    jacobi_matrix[0,1] = numpy.dot(natural_shape_derivative_func[0],in_nodes_coordinate[:,1])
                    jacobi_matrix[1,0] = numpy.dot(natural_shape_derivative_func[1],in_nodes_coordinate[:,0])
                    jacobi_matrix[1,1] = numpy.dot(natural_shape_derivative_func[1],in_nodes_coordinate[:,1])
                    jacobi_det = numpy.linalg.det(jacobi_matrix)
                    
                    strain_displacement_matrix = numpy.zeros((3,8),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(4):
                        strain_displacement_matrix[[0,2],[i*2,i*2+1]] = jacobi_matrix[1,1] * natural_shape_derivative_func[0,i] - jacobi_matrix[0,1] * natural_shape_derivative_func[1,i]
                        strain_displacement_matrix[[1,2],[i*2+1,i*2]] = jacobi_matrix[0,0] * natural_shape_derivative_func[1,i] - jacobi_matrix[1,0] * natural_shape_derivative_func[0,i]
                    strain_displacement_matrix = strain_displacement_matrix / jacobi_det
                    strain_matrixes_list.append(strain_displacement_matrix)
                    inner_function = numpy.dot(numpy.dot(strain_displacement_matrix.T,constitutive_stiffness_matrix),strain_displacement_matrix) * jacobi_det
                    global_stiffness_matrix += weights_array2[i2] * weights_array1[i1] * inner_function
                integration_points_array1 = numpy.flipud(integration_points_array1)
                weights_array1 = numpy.flipud(weights_array1)
            global_stiffness_matrix = global_stiffness_matrix * in_geometry_parameters[0] / in_geometry_parameters[1]
            
            strain_displacement_matrix = numpy.empty(shape=(12,8),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            for i in range(4):
                strain_displacement_matrix[i*3:3*(i+1),0:8] = strain_matrixes_list[i]
        elif in_type_number == 324:
            constitutive_stiffness_matrix = in_constitutive_array.reshape((3,3))
        
            natural_coordinates_coefficient_list = [(-1,-1),(1,-1),(1,1),(-1,1)]
            strain_matrixes_list = []
            global_stiffness_matrix = numpy.zeros((8,8))

            integration_points_number1,integration_points_number2 = 2,2
            integration_points_array1, weights_array1 = numpy.polynomial.legendre.leggauss(integration_points_number1)
            integration_points_array2, weights_array2 = numpy.polynomial.legendre.leggauss(integration_points_number2)
            for i2 in range(integration_points_number2):
                for i1 in range(integration_points_number1):
                    natural_shape_derivative_func = numpy.empty((2,4))
                    for i in range(4):
                        natural_shape_derivative_func[0,i] = 0.25*natural_coordinates_coefficient_list[i][0]*(1.0+integration_points_array2[i2]*natural_coordinates_coefficient_list[i][1])
                        natural_shape_derivative_func[1,i] = 0.25*(1.0+integration_points_array1[i1]*natural_coordinates_coefficient_list[i][0])*natural_coordinates_coefficient_list[i][1]
                    
                    jacobi_matrix = numpy.empty((2,2))
                    jacobi_matrix[0,0] = numpy.dot(natural_shape_derivative_func[0],in_nodes_coordinate[:,0])
                    jacobi_matrix[0,1] = numpy.dot(natural_shape_derivative_func[0],in_nodes_coordinate[:,1])
                    jacobi_matrix[1,0] = numpy.dot(natural_shape_derivative_func[1],in_nodes_coordinate[:,0])
                    jacobi_matrix[1,1] = numpy.dot(natural_shape_derivative_func[1],in_nodes_coordinate[:,1])
                    jacobi_det = numpy.linalg.det(jacobi_matrix)
                    
                    one_strain_matrix = numpy.zeros((3,8))
                    for i in range(4):
                        one_strain_matrix[[0,2],[i*2,i*2+1]] = jacobi_matrix[1,1] * natural_shape_derivative_func[0,i] - jacobi_matrix[0,1] * natural_shape_derivative_func[1,i]
                        one_strain_matrix[[1,2],[i*2+1,i*2]] = jacobi_matrix[0,0] * natural_shape_derivative_func[1,i] - jacobi_matrix[1,0] * natural_shape_derivative_func[0,i]
                    one_strain_matrix = one_strain_matrix / jacobi_det
                    dil_strain_matrix = numpy.zeros((3,8))
                    for i in range(4):
                        dil_strain_matrix[[0,1],[i*2,i*2]] = jacobi_matrix[1,1] * natural_shape_derivative_func[0,i] - jacobi_matrix[0,1] * natural_shape_derivative_func[1,i]
                        dil_strain_matrix[[0,1],[i*2+1,i*2+1]] = jacobi_matrix[0,0] * natural_shape_derivative_func[1,i] - jacobi_matrix[1,0] * natural_shape_derivative_func[0,i]
                    dil_strain_matrix = dil_strain_matrix / (2.0 * jacobi_det)
                    
                    dev_strain_matrix = one_strain_matrix - dil_strain_matrix
                    strain_matrixes_list.append(dev_strain_matrix)
                    inner_function = numpy.dot(numpy.dot(dev_strain_matrix.T,constitutive_stiffness_matrix),dev_strain_matrix) * jacobi_det
                    global_stiffness_matrix += weights_array2[i2] * weights_array1[i1] * inner_function * in_geometry_parameters[0] / in_geometry_parameters[1]
                integration_points_array1 = numpy.flipud(integration_points_array1)
                weights_array1 = numpy.flipud(weights_array1)

            integration_points_number1,integration_points_number2 = 1,1
            integration_points_array1, weights_array1 = numpy.polynomial.legendre.leggauss(integration_points_number1)
            integration_points_array2, weights_array2 = numpy.polynomial.legendre.leggauss(integration_points_number2)
            for i2 in range(integration_points_number2):
                for i1 in range(integration_points_number1):
                    natural_shape_derivative_func = numpy.empty((2,4))
                    for i in range(4):
                        natural_shape_derivative_func[0,i] = 0.25*natural_coordinates_coefficient_list[i][0]*(1.0+integration_points_array2[i2]*natural_coordinates_coefficient_list[i][1])
                        natural_shape_derivative_func[1,i] = 0.25*(1.0+integration_points_array1[i1]*natural_coordinates_coefficient_list[i][0])*natural_coordinates_coefficient_list[i][1]
                    
                    jacobi_matrix = numpy.empty((2,2))
                    jacobi_matrix[0,0] = numpy.dot(natural_shape_derivative_func[0],in_nodes_coordinate[:,0])
                    jacobi_matrix[0,1] = numpy.dot(natural_shape_derivative_func[0],in_nodes_coordinate[:,1])
                    jacobi_matrix[1,0] = numpy.dot(natural_shape_derivative_func[1],in_nodes_coordinate[:,0])
                    jacobi_matrix[1,1] = numpy.dot(natural_shape_derivative_func[1],in_nodes_coordinate[:,1])
                    jacobi_det = numpy.linalg.det(jacobi_matrix)
                    
                    bar_dil_strain_matrix = numpy.zeros((3,8))
                    for i in range(4):
                        bar_dil_strain_matrix[[0,1],[i*2,i*2]] = jacobi_matrix[1,1] * natural_shape_derivative_func[0,i] - jacobi_matrix[0,1] * natural_shape_derivative_func[1,i]
                        bar_dil_strain_matrix[[0,1],[i*2+1,i*2+1]] = jacobi_matrix[0,0] * natural_shape_derivative_func[1,i] - jacobi_matrix[1,0] * natural_shape_derivative_func[0,i]
                    bar_dil_strain_matrix = bar_dil_strain_matrix / (2.0 * jacobi_det)
                    
                    inner_function = numpy.dot(numpy.dot(bar_dil_strain_matrix.T,constitutive_stiffness_matrix),bar_dil_strain_matrix) * jacobi_det
                    global_stiffness_matrix += weights_array2[i2] * weights_array1[i1] * inner_function * in_geometry_parameters[0] / in_geometry_parameters[1]
                integration_points_array1 = numpy.flipud(integration_points_array1)
                weights_array1 = numpy.flipud(weights_array1)
            
            strain_displacement_matrix = numpy.empty(shape=(12,8))
            for i in range(4):
                strain_displacement_matrix[i*3:3*(i+1),0:8] = strain_matrixes_list[i] + bar_dil_strain_matrix
        elif in_type_number == 131:
            strain_displacement_matrix =  numpy.true_divide(numpy.array([-1.0,1.0],dtype=P4SFormat.NUMERICAL_PRECISION['float']),in_geometry_parameters[1])
            
            transform_matrix = in_transform_array.reshape((2,6))
            local_stiffness_matrix = numpy.outer(numpy.outer(strain_displacement_matrix,in_constitutive_array),strain_displacement_matrix) * in_geometry_parameters[0]
            global_stiffness_matrix = numpy.dot(numpy.dot(transform_matrix.T,local_stiffness_matrix),transform_matrix)
        elif in_type_number == 431:
            membrane_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            membrane_constitutive_stiffness_matrix[0,0] = in_constitutive_array[0]
            membrane_constitutive_stiffness_matrix[[0,1],[1,0]] = in_constitutive_array[1]
            membrane_constitutive_stiffness_matrix[[0,2],[2,0]] = in_constitutive_array[2]
            membrane_constitutive_stiffness_matrix[1,1] = in_constitutive_array[3]
            membrane_constitutive_stiffness_matrix[[1,2],[2,1]] = in_constitutive_array[4]
            membrane_constitutive_stiffness_matrix[2,2] = in_constitutive_array[5]
            plate_bending_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            plate_bending_constitutive_stiffness_matrix[0,0] = in_constitutive_array[0]
            plate_bending_constitutive_stiffness_matrix[[0,1],[1,0]] = in_constitutive_array[1]
            plate_bending_constitutive_stiffness_matrix[[0,2],[2,0]] = in_constitutive_array[2]
            plate_bending_constitutive_stiffness_matrix[1,1] = in_constitutive_array[3]
            plate_bending_constitutive_stiffness_matrix[[1,2],[2,1]] = in_constitutive_array[4]
            plate_bending_constitutive_stiffness_matrix[2,2] = in_constitutive_array[5]
            plate_shear_constitutive_stiffness_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            plate_shear_constitutive_stiffness_matrix[0,0] = in_constitutive_array[6]
            plate_shear_constitutive_stiffness_matrix[[0,1],[1,0]] = in_constitutive_array[7]
            plate_shear_constitutive_stiffness_matrix[1,1] = in_constitutive_array[8]
            
            direction_cosine_matrix = in_transform_array.reshape((3,3))
            local_nodes_coordinate = numpy.dot(direction_cosine_matrix,(in_nodes_coordinate-in_nodes_coordinate[0]).T).T
            membrane_bc_values = numpy.zeros((2,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            membrane_bc_values[0,0] = local_nodes_coordinate[1,1]-local_nodes_coordinate[2,1]
            membrane_bc_values[0,1] = local_nodes_coordinate[2,1]-local_nodes_coordinate[0,1]
            membrane_bc_values[0,2] = local_nodes_coordinate[0,1]-local_nodes_coordinate[1,1]
            membrane_bc_values[1,0] = local_nodes_coordinate[2,0]-local_nodes_coordinate[1,0]
            membrane_bc_values[1,1] = local_nodes_coordinate[0,0]-local_nodes_coordinate[2,0]
            membrane_bc_values[1,2] = local_nodes_coordinate[1,0]-local_nodes_coordinate[0,0]
            plate_shear_abcd_values = numpy.zeros(4,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            plate_shear_abcd_values[0] = local_nodes_coordinate[1,0]-local_nodes_coordinate[0,0]
            plate_shear_abcd_values[1] = local_nodes_coordinate[1,1]-local_nodes_coordinate[0,1]
            plate_shear_abcd_values[2] = local_nodes_coordinate[2,1]-local_nodes_coordinate[0,1]
            plate_shear_abcd_values[3] = local_nodes_coordinate[2,0]-local_nodes_coordinate[0,0]
            natural_to_local_transform_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            alpha_angle_kexi_to_x = numpy.atan2(local_nodes_coordinate[1,1]-local_nodes_coordinate[0,1],local_nodes_coordinate[1,0]-local_nodes_coordinate[0,0])
            beta_angle_eta_to_y = 0.5*numpy.pi-numpy.atan2(local_nodes_coordinate[2,0]-local_nodes_coordinate[0,0],local_nodes_coordinate[2,1]-local_nodes_coordinate[0,1])
            natural_to_local_transform_matrix[0,0] =  numpy.sin(beta_angle_eta_to_y)
            natural_to_local_transform_matrix[0,1] = -numpy.sin(alpha_angle_kexi_to_x)
            natural_to_local_transform_matrix[1,0] = -numpy.cos(beta_angle_eta_to_y)
            natural_to_local_transform_matrix[1,1] =  numpy.cos(alpha_angle_kexi_to_x)
            
            integration_points_array = numpy.array([[1.0/3.0,1.0/3.0]])
            weights_array = numpy.array([[0.5,0.5]])
            strain_displacement_matrix = numpy.zeros((8,9),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            membrane_local_stiffness_matrix = numpy.zeros((9,9),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            plate_local_stiffness_matrix = numpy.zeros((9,9),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            for natural_coordinates,weights in zip(integration_points_array,weights_array):
                natural_basic_shape_dfunc = numpy.array([[-1.0,1.0,0.0],[-1.0,0.0,1.0]],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                
                jacobi_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                jacobi_matrix[0,0] = numpy.dot(natural_basic_shape_dfunc[0,:],local_nodes_coordinate[:,0])
                jacobi_matrix[0,1] = numpy.dot(natural_basic_shape_dfunc[0,:],local_nodes_coordinate[:,1])
                jacobi_matrix[1,0] = numpy.dot(natural_basic_shape_dfunc[1,:],local_nodes_coordinate[:,0])
                jacobi_matrix[1,1] = numpy.dot(natural_basic_shape_dfunc[1,:],local_nodes_coordinate[:,1])
                jacobi_det = jacobi_matrix[0,0]*jacobi_matrix[1,1]-jacobi_matrix[0,1]*jacobi_matrix[1,0]
                jacobi_inv_matrix = numpy.array([[jacobi_matrix[1,1],-jacobi_matrix[0,1]],[-jacobi_matrix[1,0],jacobi_matrix[0,0]]]) / jacobi_det
                local_basic_shape_dfunc = numpy.dot(jacobi_inv_matrix,natural_basic_shape_dfunc)
                
                natural_membrane_drilling_shape_dfun = numpy.zeros((2,6),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                natural_membrane_drilling_shape_dfun[0,0] = 0.5*(-2.0*membrane_bc_values[0,2]*natural_coordinates[0]+(membrane_bc_values[0,1]-membrane_bc_values[0,2])*natural_coordinates[1]+membrane_bc_values[0,2])
                natural_membrane_drilling_shape_dfun[0,3] = 0.5*(-2.0*membrane_bc_values[1,2]*natural_coordinates[0]+(membrane_bc_values[1,1]-membrane_bc_values[1,2])*natural_coordinates[1]+membrane_bc_values[1,2])
                natural_membrane_drilling_shape_dfun[1,0] = 0.5*((membrane_bc_values[0,1]-membrane_bc_values[0,2])*natural_coordinates[0]+2.0*membrane_bc_values[0,1]*natural_coordinates[1]-membrane_bc_values[0,1])
                natural_membrane_drilling_shape_dfun[1,3] = 0.5*((membrane_bc_values[1,1]-membrane_bc_values[1,2])*natural_coordinates[0]+2.0*membrane_bc_values[1,1]*natural_coordinates[1]-membrane_bc_values[1,1])
                natural_membrane_drilling_shape_dfun[0,1] = 0.5*(2.0*membrane_bc_values[0,2]*natural_coordinates[0]+(membrane_bc_values[0,0]+membrane_bc_values[0,2])*natural_coordinates[1]-membrane_bc_values[0,2])
                natural_membrane_drilling_shape_dfun[0,4] = 0.5*(2.0*membrane_bc_values[1,2]*natural_coordinates[0]+(membrane_bc_values[1,0]+membrane_bc_values[1,2])*natural_coordinates[1]-membrane_bc_values[1,2])
                natural_membrane_drilling_shape_dfun[1,1] = 0.5*(membrane_bc_values[0,0]+membrane_bc_values[0,2])*natural_coordinates[0]
                natural_membrane_drilling_shape_dfun[1,4] = 0.5*(membrane_bc_values[1,0]+membrane_bc_values[1,2])*natural_coordinates[0]
                natural_membrane_drilling_shape_dfun[0,2] = -0.5*(membrane_bc_values[0,0]+membrane_bc_values[0,1])*natural_coordinates[1]
                natural_membrane_drilling_shape_dfun[0,5] = -0.5*(membrane_bc_values[1,0]+membrane_bc_values[1,1])*natural_coordinates[1]
                natural_membrane_drilling_shape_dfun[1,2] = 0.5*(-(membrane_bc_values[0,0]+membrane_bc_values[0,1])*natural_coordinates[0]-2.0*membrane_bc_values[0,1]*natural_coordinates[1]+membrane_bc_values[0,1])
                natural_membrane_drilling_shape_dfun[1,5] = 0.5*(-(membrane_bc_values[1,0]+membrane_bc_values[1,1])*natural_coordinates[0]-2.0*membrane_bc_values[1,1]*natural_coordinates[1]+membrane_bc_values[1,1])
                local_membrane_drilling_shape_dfun = numpy.dot(jacobi_inv_matrix,natural_membrane_drilling_shape_dfun)
                membrane_strain_displacement_matrix = numpy.zeros((3,9),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                for i in range(3):
                    membrane_strain_displacement_matrix[[0,2],[3*i,3*i+1]] = local_basic_shape_dfunc[0,i]
                    membrane_strain_displacement_matrix[[1,2],[3*i+1,3*i]] = local_basic_shape_dfunc[1,i]
                    
                    membrane_strain_displacement_matrix[0,3*i+2] = local_membrane_drilling_shape_dfun[0,i]
                    membrane_strain_displacement_matrix[1,3*i+2] = local_membrane_drilling_shape_dfun[1,3+i]
                    membrane_strain_displacement_matrix[2,3*i+2] = local_membrane_drilling_shape_dfun[1,i]+local_membrane_drilling_shape_dfun[0,3+i]
                membrane_local_stiffness_matrix += numpy.dot(numpy.dot(membrane_strain_displacement_matrix.T,membrane_constitutive_stiffness_matrix),membrane_strain_displacement_matrix) * (in_geometry_parameters[0]/in_geometry_parameters[1]) * weights[0] * weights[1] * jacobi_det
                
                plate_bending_strain_displacement_matrix = numpy.zeros((3,9),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                for i in range(3):
                    plate_bending_strain_displacement_matrix[0,3*i+2] =  local_basic_shape_dfunc[0,i]
                    plate_bending_strain_displacement_matrix[1,3*i+1] = -local_basic_shape_dfunc[1,i]
                    plate_bending_strain_displacement_matrix[2,3*i+1] = -local_basic_shape_dfunc[0,i]
                    plate_bending_strain_displacement_matrix[2,3*i+2] =  local_basic_shape_dfunc[1,i]
                plate_local_stiffness_matrix += numpy.dot(numpy.dot(plate_bending_strain_displacement_matrix.T,plate_bending_constitutive_stiffness_matrix),plate_bending_strain_displacement_matrix) * (in_geometry_parameters[0]/in_geometry_parameters[1])**3 * weights[0] * weights[1] * jacobi_det / 12.0
                plate_shear_strain_displacement_matrix = numpy.zeros((2,9),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                plate_shear_strain_displacement_matrix[0,0] = plate_shear_abcd_values[1]-plate_shear_abcd_values[2]
                plate_shear_strain_displacement_matrix[1,0] = plate_shear_abcd_values[3]-plate_shear_abcd_values[0]
                plate_shear_strain_displacement_matrix[0,1] = (plate_shear_abcd_values[1]-plate_shear_abcd_values[2])*(plate_shear_abcd_values[1]+plate_shear_abcd_values[2])/6.0
                plate_shear_strain_displacement_matrix[1,1] = -in_geometry_parameters[1]-(plate_shear_abcd_values[1]-plate_shear_abcd_values[2])*(plate_shear_abcd_values[0]+plate_shear_abcd_values[3])/6.0
                plate_shear_strain_displacement_matrix[0,2] =  in_geometry_parameters[1]+(plate_shear_abcd_values[3]-plate_shear_abcd_values[0])*(plate_shear_abcd_values[1]+plate_shear_abcd_values[2])/6.0
                plate_shear_strain_displacement_matrix[1,2] = -(plate_shear_abcd_values[3]-plate_shear_abcd_values[0])*(plate_shear_abcd_values[0]+plate_shear_abcd_values[3])/6.0
                plate_shear_strain_displacement_matrix[0,3] =  plate_shear_abcd_values[2]
                plate_shear_strain_displacement_matrix[1,3] = -plate_shear_abcd_values[3]
                plate_shear_strain_displacement_matrix[0,4] = -plate_shear_abcd_values[1]*plate_shear_abcd_values[2]/2.0+plate_shear_abcd_values[2]*(plate_shear_abcd_values[1]+plate_shear_abcd_values[2])/6.0
                plate_shear_strain_displacement_matrix[1,4] =  plate_shear_abcd_values[1]*plate_shear_abcd_values[3]/2.0-plate_shear_abcd_values[2]*(plate_shear_abcd_values[0]+plate_shear_abcd_values[3])/6.0
                plate_shear_strain_displacement_matrix[0,5] =  plate_shear_abcd_values[0]*plate_shear_abcd_values[2]/2.0-plate_shear_abcd_values[3]*(plate_shear_abcd_values[1]+plate_shear_abcd_values[2])/6.0
                plate_shear_strain_displacement_matrix[1,5] = -plate_shear_abcd_values[0]*plate_shear_abcd_values[3]/2.0+plate_shear_abcd_values[3]*(plate_shear_abcd_values[0]+plate_shear_abcd_values[3])/6.0
                plate_shear_strain_displacement_matrix[0,6] = -plate_shear_abcd_values[1]
                plate_shear_strain_displacement_matrix[1,6] =  plate_shear_abcd_values[0]
                plate_shear_strain_displacement_matrix[0,7] =  plate_shear_abcd_values[1]*plate_shear_abcd_values[2]/2.0-plate_shear_abcd_values[1]*(plate_shear_abcd_values[1]+plate_shear_abcd_values[2])/6.0
                plate_shear_strain_displacement_matrix[1,7] = -plate_shear_abcd_values[0]*plate_shear_abcd_values[2]/2.0+plate_shear_abcd_values[1]*(plate_shear_abcd_values[0]+plate_shear_abcd_values[3])/6.0
                plate_shear_strain_displacement_matrix[0,8] = -plate_shear_abcd_values[1]*plate_shear_abcd_values[3]/2.0+plate_shear_abcd_values[0]*(plate_shear_abcd_values[1]+plate_shear_abcd_values[2])/6.0
                plate_shear_strain_displacement_matrix[1,8] =  plate_shear_abcd_values[0]*plate_shear_abcd_values[3]/2.0-plate_shear_abcd_values[0]*(plate_shear_abcd_values[0]+plate_shear_abcd_values[3])/6.0
                plate_shear_strain_displacement_matrix = plate_shear_strain_displacement_matrix / (2.0*in_geometry_parameters[1])
                plate_local_stiffness_matrix += numpy.dot(numpy.dot(plate_shear_strain_displacement_matrix.T,plate_shear_constitutive_stiffness_matrix*5.0/6.0),plate_shear_strain_displacement_matrix) * (in_geometry_parameters[0]/in_geometry_parameters[1]) * weights[0] * weights[1] * jacobi_det      

                strain_displacement_matrix[0:3] = membrane_strain_displacement_matrix
                strain_displacement_matrix[3:6] = plate_bending_strain_displacement_matrix
                strain_displacement_matrix[6:8] = plate_shear_strain_displacement_matrix

            local_stiffness_matrix = numpy.zeros((18,18),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            for row in range(1,4):
                for col in range(1,4):
                    local_stiffness_matrix[(row-1)*6,(col-1)*6] = membrane_local_stiffness_matrix[3*row-3,3*col-3]
                    local_stiffness_matrix[(row-1)*6,(col-1)*6+1] = membrane_local_stiffness_matrix[3*row-3,3*col-2]
                    local_stiffness_matrix[(row-1)*6,(col-1)*6+5] = membrane_local_stiffness_matrix[3*row-3,3*col-1]
                    local_stiffness_matrix[(row-1)*6+1,(col-1)*6] = membrane_local_stiffness_matrix[3*row-2,3*col-3]
                    local_stiffness_matrix[(row-1)*6+1,(col-1)*6+1] = membrane_local_stiffness_matrix[3*row-2,3*col-2]
                    local_stiffness_matrix[(row-1)*6+1,(col-1)*6+5] = membrane_local_stiffness_matrix[3*row-2,3*col-1]
                    local_stiffness_matrix[(row-1)*6+5,(col-1)*6] = membrane_local_stiffness_matrix[3*row-1,3*col-3]
                    local_stiffness_matrix[(row-1)*6+5,(col-1)*6+1] = membrane_local_stiffness_matrix[3*row-1,3*col-2]
                    local_stiffness_matrix[(row-1)*6+5,(col-1)*6+5] = membrane_local_stiffness_matrix[3*row-1,3*col-1]
                    
                    local_stiffness_matrix[(row-1)*6+2,(col-1)*6+2] = plate_local_stiffness_matrix[3*row-3,3*col-3]
                    local_stiffness_matrix[(row-1)*6+2,(col-1)*6+3] = plate_local_stiffness_matrix[3*row-3,3*col-2]
                    local_stiffness_matrix[(row-1)*6+2,(col-1)*6+4] = plate_local_stiffness_matrix[3*row-3,3*col-1]
                    local_stiffness_matrix[(row-1)*6+3,(col-1)*6+2] = plate_local_stiffness_matrix[3*row-2,3*col-3]
                    local_stiffness_matrix[(row-1)*6+3,(col-1)*6+3] = plate_local_stiffness_matrix[3*row-2,3*col-2]
                    local_stiffness_matrix[(row-1)*6+3,(col-1)*6+4] = plate_local_stiffness_matrix[3*row-2,3*col-1]              
                    local_stiffness_matrix[(row-1)*6+4,(col-1)*6+2] = plate_local_stiffness_matrix[3*row-1,3*col-3]
                    local_stiffness_matrix[(row-1)*6+4,(col-1)*6+3] = plate_local_stiffness_matrix[3*row-1,3*col-2]
                    local_stiffness_matrix[(row-1)*6+4,(col-1)*6+4] = plate_local_stiffness_matrix[3*row-1,3*col-1]
            transform_matrix = numpy.zeros((18,18),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            transform_matrix[0:3,0:3] = direction_cosine_matrix
            transform_matrix[3:6,3:6] = direction_cosine_matrix
            transform_matrix[6:9,6:9] = direction_cosine_matrix
            transform_matrix[9:12,9:12] = direction_cosine_matrix
            transform_matrix[12:15,12:15] = direction_cosine_matrix
            transform_matrix[15:18,15:18] = direction_cosine_matrix
            global_stiffness_matrix = numpy.dot(numpy.dot(transform_matrix.T,local_stiffness_matrix),transform_matrix)
        elif in_type_number == 432:
            membrane_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            membrane_constitutive_stiffness_matrix[0,0] = in_constitutive_array[0]
            membrane_constitutive_stiffness_matrix[[0,1],[1,0]] = in_constitutive_array[1]
            membrane_constitutive_stiffness_matrix[[0,2],[2,0]] = in_constitutive_array[2]
            membrane_constitutive_stiffness_matrix[1,1] = in_constitutive_array[3]
            membrane_constitutive_stiffness_matrix[[1,2],[2,1]] = in_constitutive_array[4]
            membrane_constitutive_stiffness_matrix[2,2] = in_constitutive_array[5]
            plate_bending_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            plate_bending_constitutive_stiffness_matrix[0,0] = in_constitutive_array[0]
            plate_bending_constitutive_stiffness_matrix[[0,1],[1,0]] = in_constitutive_array[1]
            plate_bending_constitutive_stiffness_matrix[[0,2],[2,0]] = in_constitutive_array[2]
            plate_bending_constitutive_stiffness_matrix[1,1] = in_constitutive_array[3]
            plate_bending_constitutive_stiffness_matrix[[1,2],[2,1]] = in_constitutive_array[4]
            plate_bending_constitutive_stiffness_matrix[2,2] = in_constitutive_array[5]
            plate_shear_constitutive_stiffness_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            plate_shear_constitutive_stiffness_matrix[0,0] = in_constitutive_array[6]
            plate_shear_constitutive_stiffness_matrix[[0,1],[1,0]] = in_constitutive_array[7]
            plate_shear_constitutive_stiffness_matrix[1,1] = in_constitutive_array[8]

            direction_cosine_matrix = in_transform_array.reshape((3,3))
            local_nodes_coordinate = numpy.dot(direction_cosine_matrix,(in_nodes_coordinate-in_nodes_coordinate[0]).T).T
            natural_coordinates_coefficient = numpy.array([[-1.0,-1.0],[1.0,-1.0],[1.0,1.0],[-1.0,1.0]],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            membrane_ab_values = numpy.zeros((2,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            membrane_ab_values[0,0] = 0.25*numpy.sum(natural_coordinates_coefficient[:,0]*local_nodes_coordinate[:,0])
            membrane_ab_values[0,1] = 0.25*numpy.sum(natural_coordinates_coefficient[:,1]*local_nodes_coordinate[:,0])
            membrane_ab_values[0,2] = 0.25*numpy.sum(natural_coordinates_coefficient[:,0]*natural_coordinates_coefficient[:,1]*local_nodes_coordinate[:,0])
            membrane_ab_values[1,0] = 0.25*numpy.sum(natural_coordinates_coefficient[:,0]*local_nodes_coordinate[:,1])
            membrane_ab_values[1,1] = 0.25*numpy.sum(natural_coordinates_coefficient[:,1]*local_nodes_coordinate[:,1])
            membrane_ab_values[1,2] = 0.25*numpy.sum(natural_coordinates_coefficient[:,0]*natural_coordinates_coefficient[:,1]*local_nodes_coordinate[:,1])
            plate_shear_abc_values = numpy.zeros((2,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            plate_shear_abc_values[0,0] = numpy.sum(natural_coordinates_coefficient[:,0]*local_nodes_coordinate[:,0])
            plate_shear_abc_values[0,1] = numpy.sum(natural_coordinates_coefficient[:,0]*natural_coordinates_coefficient[:,1]*local_nodes_coordinate[:,0])
            plate_shear_abc_values[0,2] = numpy.sum(natural_coordinates_coefficient[:,1]*local_nodes_coordinate[:,0])
            plate_shear_abc_values[1,0] = numpy.sum(natural_coordinates_coefficient[:,0]*local_nodes_coordinate[:,1])
            plate_shear_abc_values[1,1] = numpy.sum(natural_coordinates_coefficient[:,0]*natural_coordinates_coefficient[:,1]*local_nodes_coordinate[:,1])
            plate_shear_abc_values[1,2] = numpy.sum(natural_coordinates_coefficient[:,1]*local_nodes_coordinate[:,1])
            plate_shear_G_matrix = numpy.zeros((4,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            plate_shear_G_matrix[[0,1,2,3],[0,0,3,9]] = -0.5
            plate_shear_G_matrix[[0,1,2,3],[9,3,6,6]] = 0.5
            plate_shear_G_matrix[[0,0],[1,10]] = -0.25*(local_nodes_coordinate[3,1]-local_nodes_coordinate[0,1])
            plate_shear_G_matrix[[0,0],[2,11]] =  0.25*(local_nodes_coordinate[3,0]-local_nodes_coordinate[0,0])
            plate_shear_G_matrix[[1,1],[1,4]] = -0.25*(local_nodes_coordinate[1,1]-local_nodes_coordinate[0,1])
            plate_shear_G_matrix[[1,1],[2,5]] =  0.25*(local_nodes_coordinate[1,0]-local_nodes_coordinate[0,0])
            plate_shear_G_matrix[[2,2],[4,7]] = -0.25*(local_nodes_coordinate[2,1]-local_nodes_coordinate[1,1])
            plate_shear_G_matrix[[2,2],[5,8]] =  0.25*(local_nodes_coordinate[2,0]-local_nodes_coordinate[1,0])
            plate_shear_G_matrix[[3,3],[7,10]] = -0.25*(local_nodes_coordinate[2,1]-local_nodes_coordinate[3,1])
            plate_shear_G_matrix[[3,3],[8,11]] =  0.25*(local_nodes_coordinate[2,0]-local_nodes_coordinate[3,0])
            natural_to_local_transform_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            alpha_angle_kexi_to_x = numpy.atan2(plate_shear_abc_values[1,0],plate_shear_abc_values[0,0])
            beta_angle_eta_to_y = 0.5*numpy.pi-numpy.atan2(plate_shear_abc_values[0,2],plate_shear_abc_values[1,2])
            natural_to_local_transform_matrix[0,0] =  numpy.sin(beta_angle_eta_to_y)
            natural_to_local_transform_matrix[0,1] = -numpy.sin(alpha_angle_kexi_to_x)
            natural_to_local_transform_matrix[1,0] = -numpy.cos(beta_angle_eta_to_y)
            natural_to_local_transform_matrix[1,1] =  numpy.cos(alpha_angle_kexi_to_x)
            
            integration_points_number1,integration_points_number2 = 2,2
            integration_points_array1, weights_array1 = numpy.polynomial.legendre.leggauss(integration_points_number1)
            integration_points_array2, weights_array2 = numpy.polynomial.legendre.leggauss(integration_points_number2)
            strain_matrixes_list = []
            membrane_local_stiffness_matrix = numpy.zeros((12,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            plate_local_stiffness_matrix = numpy.zeros((12,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            for i2 in range(integration_points_number2):
                for i1 in range(integration_points_number1):
                    natural_basic_shape_dfunc = numpy.zeros((2,4),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(4):
                        natural_basic_shape_dfunc[0,i] = 0.25*natural_coordinates_coefficient[i,0]*(1.0+natural_coordinates_coefficient[i,1]*integration_points_array2[i2])
                        natural_basic_shape_dfunc[1,i] = 0.25*natural_coordinates_coefficient[i,1]*(1.0+natural_coordinates_coefficient[i,0]*integration_points_array1[i1])
                    
                    jacobi_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    jacobi_matrix[0,0] = numpy.dot(natural_basic_shape_dfunc[0,:],local_nodes_coordinate[:,0])
                    jacobi_matrix[0,1] = numpy.dot(natural_basic_shape_dfunc[0,:],local_nodes_coordinate[:,1])
                    jacobi_matrix[1,0] = numpy.dot(natural_basic_shape_dfunc[1,:],local_nodes_coordinate[:,0])
                    jacobi_matrix[1,1] = numpy.dot(natural_basic_shape_dfunc[1,:],local_nodes_coordinate[:,1])
                    jacobi_det = jacobi_matrix[0,0]*jacobi_matrix[1,1]-jacobi_matrix[0,1]*jacobi_matrix[1,0]
                    jacobi_inv_matrix = numpy.array([[jacobi_matrix[1,1],-jacobi_matrix[0,1]],[-jacobi_matrix[1,0],jacobi_matrix[0,0]]]) / jacobi_det
                    local_basic_shape_dfunc = numpy.dot(jacobi_inv_matrix,natural_basic_shape_dfunc)
                    
                    natural_membrane_drilling_shape_dfun = numpy.zeros((2,8),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(4):
                        natural_membrane_drilling_shape_dfun[0,i] = 0.125 * natural_coordinates_coefficient[i,0] * (-2.0*integration_points_array1[i1]) * (membrane_ab_values[1,0]+membrane_ab_values[1,2]*natural_coordinates_coefficient[i,1]) * (1.0+natural_coordinates_coefficient[i,1]*integration_points_array2[i2]) + \
                                                                    0.125 * natural_coordinates_coefficient[i,0] * natural_coordinates_coefficient[i,1] * (membrane_ab_values[1,1]+membrane_ab_values[1,2]*natural_coordinates_coefficient[i,0]) * (1.0-integration_points_array2[i2]**2)
                        natural_membrane_drilling_shape_dfun[1,i] = 0.125 * natural_coordinates_coefficient[i,1] * natural_coordinates_coefficient[i,0] * (membrane_ab_values[1,0]+membrane_ab_values[1,2]*natural_coordinates_coefficient[i,1]) * (1.0-integration_points_array1[i1]**2) + \
                                                                    0.125 * natural_coordinates_coefficient[i,1] * (-2.0*integration_points_array2[i2]) * (membrane_ab_values[1,1]+membrane_ab_values[1,2]*natural_coordinates_coefficient[i,0]) * (1.0+natural_coordinates_coefficient[i,0]*integration_points_array1[i1])
                        
                        natural_membrane_drilling_shape_dfun[0,4+i] = - 0.125 * natural_coordinates_coefficient[i,0] * (-2.0*integration_points_array1[i1]) * (membrane_ab_values[0,0]+membrane_ab_values[0,2]*natural_coordinates_coefficient[i,1]) * (1.0+natural_coordinates_coefficient[i,1]*integration_points_array2[i2]) + \
                                                                      - 0.125 * natural_coordinates_coefficient[i,0] * natural_coordinates_coefficient[i,1] * (membrane_ab_values[0,1]+membrane_ab_values[0,2]*natural_coordinates_coefficient[i,0]) * (1.0-integration_points_array2[i2]**2)
                        natural_membrane_drilling_shape_dfun[1,4+i] = - 0.125 * natural_coordinates_coefficient[i,1] * natural_coordinates_coefficient[i,0] * (membrane_ab_values[0,0]+membrane_ab_values[0,2]*natural_coordinates_coefficient[i,1]) * (1.0-integration_points_array1[i1]**2) + \
                                                                      - 0.125 * natural_coordinates_coefficient[i,1] * (-2.0*integration_points_array2[i2]) * (membrane_ab_values[0,1]+membrane_ab_values[0,2]*natural_coordinates_coefficient[i,0]) * (1.0+natural_coordinates_coefficient[i,0]*integration_points_array1[i1])
                    local_membrane_drilling_shape_dfun = numpy.dot(jacobi_inv_matrix,natural_membrane_drilling_shape_dfun)
                    membrane_strain_displacement_matrix = numpy.zeros((3,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(4):
                        membrane_strain_displacement_matrix[[0,2],[3*i,3*i+1]] = local_basic_shape_dfunc[0,i]
                        membrane_strain_displacement_matrix[[1,2],[3*i+1,3*i]] = local_basic_shape_dfunc[1,i]
                        
                        membrane_strain_displacement_matrix[0,3*i+2] = local_membrane_drilling_shape_dfun[0,i]
                        membrane_strain_displacement_matrix[1,3*i+2] = local_membrane_drilling_shape_dfun[1,4+i]
                        membrane_strain_displacement_matrix[2,3*i+2] = local_membrane_drilling_shape_dfun[1,i]+local_membrane_drilling_shape_dfun[0,4+i]
                    membrane_local_stiffness_matrix += numpy.dot(numpy.dot(membrane_strain_displacement_matrix.T,membrane_constitutive_stiffness_matrix),membrane_strain_displacement_matrix) * (in_geometry_parameters[0]/in_geometry_parameters[1]) * weights_array2[i2] * weights_array1[i1] * jacobi_det
                    
                    plate_bending_strain_displacement_matrix = numpy.zeros((3,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(4):
                        plate_bending_strain_displacement_matrix[0,3*i+2] =  local_basic_shape_dfunc[0,i]
                        plate_bending_strain_displacement_matrix[1,3*i+1] = -local_basic_shape_dfunc[1,i]
                        plate_bending_strain_displacement_matrix[2,3*i+1] = -local_basic_shape_dfunc[0,i]
                        plate_bending_strain_displacement_matrix[2,3*i+2] =  local_basic_shape_dfunc[1,i]
                    plate_local_stiffness_matrix += numpy.dot(numpy.dot(plate_bending_strain_displacement_matrix.T,plate_bending_constitutive_stiffness_matrix),plate_bending_strain_displacement_matrix) * (in_geometry_parameters[0]/in_geometry_parameters[1])**3 * weights_array2[i2] * weights_array1[i1] * jacobi_det / 12.0
                    plate_shear_coefficient_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_shear_coefficient_matrix[0,0] = ((plate_shear_abc_values[0,2] + integration_points_array1[i1]*plate_shear_abc_values[0,1])**2 + (plate_shear_abc_values[1,2] + integration_points_array1[i1]*plate_shear_abc_values[1,1])**2)**0.5/(8.0*jacobi_det)
                    plate_shear_coefficient_matrix[1,1] = ((plate_shear_abc_values[0,0] + integration_points_array2[i2]*plate_shear_abc_values[0,1])**2 + (plate_shear_abc_values[1,0] + integration_points_array2[i2]*plate_shear_abc_values[1,1])**2)**0.5/(8.0*jacobi_det)
                    plate_shear_kexi_eta_matrix = numpy.zeros((2,4),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_shear_kexi_eta_matrix[0,1] = 1.0-integration_points_array2[i2]
                    plate_shear_kexi_eta_matrix[0,3] = 1.0+integration_points_array2[i2]
                    plate_shear_kexi_eta_matrix[1,0] = 1.0-integration_points_array1[i1]
                    plate_shear_kexi_eta_matrix[1,2] = 1.0+integration_points_array1[i1]
                    plate_shear_strain_displacement_matrix = numpy.dot(natural_to_local_transform_matrix,numpy.dot(numpy.dot(plate_shear_coefficient_matrix,plate_shear_kexi_eta_matrix),plate_shear_G_matrix))
                    plate_local_stiffness_matrix += numpy.dot(numpy.dot(plate_shear_strain_displacement_matrix.T,plate_shear_constitutive_stiffness_matrix*5.0/6.0),plate_shear_strain_displacement_matrix) * (in_geometry_parameters[0]/in_geometry_parameters[1]) * weights_array2[i2] * weights_array1[i1] * jacobi_det
                    
                    integration_point_strain_displacement_matrix = numpy.zeros((8,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    integration_point_strain_displacement_matrix[0:3,:] = membrane_strain_displacement_matrix
                    integration_point_strain_displacement_matrix[3:6,:] = plate_bending_strain_displacement_matrix
                    integration_point_strain_displacement_matrix[6:8,:] = plate_shear_strain_displacement_matrix
                    strain_matrixes_list.append(integration_point_strain_displacement_matrix)
                    
                integration_points_array1 = numpy.flipud(integration_points_array1)
                weights_array1 = numpy.flipud(weights_array1)
                
            local_stiffness_matrix = numpy.zeros((24,24),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            for row in range(1,5):
                for col in range(1,5):
                    local_stiffness_matrix[(row-1)*6,(col-1)*6] = membrane_local_stiffness_matrix[3*row-3,3*col-3]
                    local_stiffness_matrix[(row-1)*6,(col-1)*6+1] = membrane_local_stiffness_matrix[3*row-3,3*col-2]
                    local_stiffness_matrix[(row-1)*6,(col-1)*6+5] = membrane_local_stiffness_matrix[3*row-3,3*col-1]
                    local_stiffness_matrix[(row-1)*6+1,(col-1)*6] = membrane_local_stiffness_matrix[3*row-2,3*col-3]
                    local_stiffness_matrix[(row-1)*6+1,(col-1)*6+1] = membrane_local_stiffness_matrix[3*row-2,3*col-2]
                    local_stiffness_matrix[(row-1)*6+1,(col-1)*6+5] = membrane_local_stiffness_matrix[3*row-2,3*col-1]
                    local_stiffness_matrix[(row-1)*6+5,(col-1)*6] = membrane_local_stiffness_matrix[3*row-1,3*col-3]
                    local_stiffness_matrix[(row-1)*6+5,(col-1)*6+1] = membrane_local_stiffness_matrix[3*row-1,3*col-2]
                    local_stiffness_matrix[(row-1)*6+5,(col-1)*6+5] = membrane_local_stiffness_matrix[3*row-1,3*col-1]
                    
                    local_stiffness_matrix[(row-1)*6+2,(col-1)*6+2] = plate_local_stiffness_matrix[3*row-3,3*col-3]
                    local_stiffness_matrix[(row-1)*6+2,(col-1)*6+3] = plate_local_stiffness_matrix[3*row-3,3*col-2]
                    local_stiffness_matrix[(row-1)*6+2,(col-1)*6+4] = plate_local_stiffness_matrix[3*row-3,3*col-1]
                    local_stiffness_matrix[(row-1)*6+3,(col-1)*6+2] = plate_local_stiffness_matrix[3*row-2,3*col-3]
                    local_stiffness_matrix[(row-1)*6+3,(col-1)*6+3] = plate_local_stiffness_matrix[3*row-2,3*col-2]
                    local_stiffness_matrix[(row-1)*6+3,(col-1)*6+4] = plate_local_stiffness_matrix[3*row-2,3*col-1]              
                    local_stiffness_matrix[(row-1)*6+4,(col-1)*6+2] = plate_local_stiffness_matrix[3*row-1,3*col-3]
                    local_stiffness_matrix[(row-1)*6+4,(col-1)*6+3] = plate_local_stiffness_matrix[3*row-1,3*col-2]
                    local_stiffness_matrix[(row-1)*6+4,(col-1)*6+4] = plate_local_stiffness_matrix[3*row-1,3*col-1]
            
            transform_matrix = numpy.zeros((24,24),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            for i in range(8):
                transform_matrix[3*i:3*i+3,3*i:3*i+3] = direction_cosine_matrix
            global_stiffness_matrix = numpy.dot(numpy.dot(transform_matrix.T,local_stiffness_matrix),transform_matrix)
            
            strain_displacement_matrix = numpy.zeros((32,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            for i in range(4):
                strain_displacement_matrix[8*i:8*(i+1),:] = strain_matrixes_list[i]
        elif in_type_number == 631:
            temp_array = numpy.ones((4,4))
            temp_array[:,1:] = in_nodes_coordinate
            shape_derivative_function = numpy.empty((3,4))
            shape_derivative_function[0,0] = - numpy.linalg.det(temp_array[1:,[0,2,3]])
            shape_derivative_function[0,1] = numpy.linalg.det(numpy.array([temp_array[0,[0,2,3]], temp_array[2,[0,2,3]],temp_array[3,[0,2,3]]]))
            shape_derivative_function[0,2] = - numpy.linalg.det(numpy.array([temp_array[0,[0,2,3]], temp_array[1,[0,2,3]],temp_array[3,[0,2,3]]]))
            shape_derivative_function[0,3] = numpy.linalg.det(numpy.array([temp_array[0,[0,2,3]], temp_array[1,[0,2,3]],temp_array[2,[0,2,3]]]))
            shape_derivative_function[1,0] = numpy.linalg.det(temp_array[1:,[0,1,3]])
            shape_derivative_function[1,1] = - numpy.linalg.det(numpy.array([temp_array[0,[0,1,3]], temp_array[2,[0,1,3]],temp_array[3,[0,1,3]]]))
            shape_derivative_function[1,2] = numpy.linalg.det(numpy.array([temp_array[0,[0,1,3]], temp_array[1,[0,1,3]],temp_array[3,[0,1,3]]]))
            shape_derivative_function[1,3] = - numpy.linalg.det(numpy.array([temp_array[0,[0,1,3]], temp_array[1,[0,1,3]],temp_array[2,[0,1,3]]]))
            shape_derivative_function[2,0] = -numpy.linalg.det(temp_array[1:,[0,1,2]])
            shape_derivative_function[2,1] = numpy.linalg.det(numpy.array([temp_array[0,[0,1,2]], temp_array[2,[0,1,2]],temp_array[3,[0,1,2]]]))
            shape_derivative_function[2,2] = -numpy.linalg.det(numpy.array([temp_array[0,[0,1,2]], temp_array[1,[0,1,2]],temp_array[3,[0,1,2]]]))
            shape_derivative_function[2,3] = numpy.linalg.det(numpy.array([temp_array[0,[0,1,2]], temp_array[1,[0,1,2]],temp_array[2,[0,1,2]]]))
            shape_derivative_function = shape_derivative_function  / (6.0 * in_geometry_parameters[0])

            strain_displacement_matrix = numpy.zeros((6,12))
            strain_displacement_matrix[[0,3,5],[0,1,2]] = shape_derivative_function[0,0]
            strain_displacement_matrix[[0,3,5],[3,4,5]] = shape_derivative_function[0,1]
            strain_displacement_matrix[[0,3,5],[6,7,8]] = shape_derivative_function[0,2]
            strain_displacement_matrix[[0,3,5],[9,10,11]] = shape_derivative_function[0,3]
            strain_displacement_matrix[[1,3,4],[1,0,2]] = shape_derivative_function[1,0]
            strain_displacement_matrix[[1,3,4],[4,3,5]] = shape_derivative_function[1,1]
            strain_displacement_matrix[[1,3,4],[7,6,8]] = shape_derivative_function[1,2]
            strain_displacement_matrix[[1,3,4],[10,9,11]] = shape_derivative_function[1,3]
            strain_displacement_matrix[[2,4,5],[2,1,0]] = shape_derivative_function[2,0]
            strain_displacement_matrix[[2,4,5],[5,4,3]] = shape_derivative_function[2,1]
            strain_displacement_matrix[[2,4,5],[8,7,6]] = shape_derivative_function[2,2]
            strain_displacement_matrix[[2,4,5],[11,10,9]] = shape_derivative_function[2,3]

            constitutive_stiffness_matrix = in_constitutive_array.reshape((6,6))
            global_stiffness_matrix = numpy.dot(numpy.dot(strain_displacement_matrix.T,constitutive_stiffness_matrix),strain_displacement_matrix) * in_geometry_parameters[0]
        elif in_type_number == 632:
            constitutive_stiffness_matrix = in_constitutive_array.reshape((6,6))
            
            natural_coordinates_coefficient_list = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
            strain_matrixes_list = []
            global_stiffness_matrix = numpy.zeros((24,24))
            
            integration_points_number1,integration_points_number2,integration_points_number3 = 2, 2, 2
            integration_points_array1, weights_array1 = numpy.polynomial.legendre.leggauss(integration_points_number1)
            integration_points_array2, weights_array2 = numpy.polynomial.legendre.leggauss(integration_points_number2)
            integration_points_array3, weights_array3 = numpy.polynomial.legendre.leggauss(integration_points_number3)
            for i3 in range(integration_points_number3):
                for i2 in range(integration_points_number2):
                    for i1 in range(integration_points_number1):
                        local_shape_derivative_function = numpy.empty((3,8))
                        for i in range(8):
                            local_shape_derivative_function[0,i] = 0.125*natural_coordinates_coefficient_list[i][0]*(1.0+natural_coordinates_coefficient_list[i][1]*integration_points_array2[i2])*(1.0+natural_coordinates_coefficient_list[i][2]*integration_points_array3[i3])
                            local_shape_derivative_function[1,i] = 0.125*natural_coordinates_coefficient_list[i][1]*(1.0+natural_coordinates_coefficient_list[i][0]*integration_points_array1[i1])*(1.0+natural_coordinates_coefficient_list[i][2]*integration_points_array3[i3])
                            local_shape_derivative_function[2,i] = 0.125*natural_coordinates_coefficient_list[i][2]*(1.0+natural_coordinates_coefficient_list[i][0]*integration_points_array1[i1])*(1.0+natural_coordinates_coefficient_list[i][1]*integration_points_array2[i2])

                        jacobi_matrix = numpy.dot(local_shape_derivative_function,in_nodes_coordinate)
                        jacobi_det = numpy.linalg.det(jacobi_matrix)
                        inv_jacobi_matrix = numpy.linalg.inv(jacobi_matrix)
                        
                        global_shape_derivative_function = numpy.dot(inv_jacobi_matrix,local_shape_derivative_function)
                        one_strain_matrix = numpy.zeros((6,24))
                        for i in range(8):
                            one_strain_matrix[[0,3,4],[i*3,i*3+1,i*3+2]] = global_shape_derivative_function[0,i]
                            one_strain_matrix[[1,3,5],[i*3+1,i*3,i*3+2]] = global_shape_derivative_function[1,i]
                            one_strain_matrix[[2,4,5],[i*3+2,i*3,i*3+1]] = global_shape_derivative_function[2,i]
                        dil_strain_matrix = numpy.zeros((6,24))
                        for i in range(8):
                            dil_strain_matrix[[0,1,2],[i*3,i*3,i*3]] = global_shape_derivative_function[0,i] / 3.0
                            dil_strain_matrix[[0,1,2],[i*3+1,i*3+1,i*3+1]] = global_shape_derivative_function[1,i] / 3.0
                            dil_strain_matrix[[0,1,2],[i*3+2,i*3+2,i*3+2]] = global_shape_derivative_function[2,i] / 3.0

                        dev_strain_matrix = one_strain_matrix - dil_strain_matrix
                        strain_matrixes_list.append(dev_strain_matrix)
                        inner_function = numpy.dot(numpy.dot(dev_strain_matrix.T,constitutive_stiffness_matrix),dev_strain_matrix) * jacobi_det
                        global_stiffness_matrix += weights_array3[i3] * weights_array2[i2] * weights_array1[i1] * inner_function
                    integration_points_array1 = numpy.flipud(integration_points_array1)
                    weights_array1 = numpy.flipud(weights_array1)
            
            integration_points_number1,integration_points_number2,integration_points_number3 = 1, 1, 1
            integration_points_array1, weights_array1 = numpy.polynomial.legendre.leggauss(integration_points_number1)
            integration_points_array2, weights_array2 = numpy.polynomial.legendre.leggauss(integration_points_number2)
            integration_points_array3, weights_array3 = numpy.polynomial.legendre.leggauss(integration_points_number3)
            for i3 in range(integration_points_number3):
                for i2 in range(integration_points_number2):
                    for i1 in range(integration_points_number1):
                        local_shape_derivative_function = numpy.empty((3,8))
                        for i in range(8):
                            local_shape_derivative_function[0,i] = 0.125*natural_coordinates_coefficient_list[i][0]*(1.0+natural_coordinates_coefficient_list[i][1]*integration_points_array2[i2])*(1.0+natural_coordinates_coefficient_list[i][2]*integration_points_array3[i3])
                            local_shape_derivative_function[1,i] = 0.125*natural_coordinates_coefficient_list[i][1]*(1.0+natural_coordinates_coefficient_list[i][0]*integration_points_array1[i1])*(1.0+natural_coordinates_coefficient_list[i][2]*integration_points_array3[i3])
                            local_shape_derivative_function[2,i] = 0.125*natural_coordinates_coefficient_list[i][2]*(1.0+natural_coordinates_coefficient_list[i][0]*integration_points_array1[i1])*(1.0+natural_coordinates_coefficient_list[i][1]*integration_points_array2[i2])

                        jacobi_matrix = numpy.dot(local_shape_derivative_function,in_nodes_coordinate)
                        jacobi_det = numpy.linalg.det(jacobi_matrix)
                        inv_jacobi_matrix = numpy.linalg.inv(jacobi_matrix)
                        
                        global_shape_derivative_function = numpy.dot(inv_jacobi_matrix,local_shape_derivative_function)
                        bar_dil_strain_matrix = numpy.zeros((6,24))
                        for i in range(8):
                            bar_dil_strain_matrix[[0,1,2],[i*3,i*3,i*3]] = global_shape_derivative_function[0,i] / 3.0
                            bar_dil_strain_matrix[[0,1,2],[i*3+1,i*3+1,i*3+1]] = global_shape_derivative_function[1,i] / 3.0
                            bar_dil_strain_matrix[[0,1,2],[i*3+2,i*3+2,i*3+2]] = global_shape_derivative_function[2,i] / 3.0

                        inner_function = numpy.dot(numpy.dot(bar_dil_strain_matrix.T,constitutive_stiffness_matrix),bar_dil_strain_matrix) * jacobi_det
                        global_stiffness_matrix += weights_array3[i3] * weights_array2[i2] * weights_array1[i1] * inner_function
                    integration_points_array1 = numpy.flipud(integration_points_array1)
                    weights_array1 = numpy.flipud(weights_array1)
            
            strain_displacement_matrix = numpy.empty(shape=(48,24))
            for i in range(8):
                strain_displacement_matrix[i*6:6*(i+1),0:24] = strain_matrixes_list[i] + bar_dil_strain_matrix
        else:
            pass
        
        return strain_displacement_matrix.flatten(),global_stiffness_matrix.flatten()
    # endregion
    @staticmethod
    def getAssembleGlobalStiffnessMatrixSparseInformation(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            ins_ready_elements_set = ins_file['readyelements']
            ins_ready_elements_type_set = ins_file['readyelementstype']
            ins_all_nodes_first_dof_loc_set = ins_file['allnodesfirstdoflocation']
            ins_all_nodes_dofs_set = ins_file['allnodesdofs']
            ins_ready_elements_km_set = ins_file['readyelementskm']
            
            ins_ready_elements_sparse_gkm_values_set = ins_file['readyelementsvalues']
            ins_ready_elements_sparse_gkm_rows_set = ins_file['readyelementsrows']
            ins_ready_elements_sparse_gkm_columns_set = ins_file['readyelementscolumns']

            elements_number = ins_ready_elements_set.shape[0]
            for local_index in range(elements_number):
                element_type_number = ins_ready_elements_type_set[local_index]
                element_dofs_list = P4SElementInfo.ELEMENT_NUMBER_TO_DOFS[element_type_number]
                
                element_stiffness_matrix_dofs_location_list = []
                for node_label in ins_ready_elements_set[local_index][:]:
                    node_start_dof_location = ins_all_nodes_first_dof_loc_set[node_label-1]
                    for dof_index in numpy.searchsorted(ins_all_nodes_dofs_set[node_label-1],numpy.asarray(element_dofs_list)):
                        element_stiffness_matrix_dofs_location_list.append(node_start_dof_location+dof_index)
                
                element_nonzero_values_list = []
                element_nonzero_rows_list = []
                element_nonzero_columns_list = []
                
                element_stiffness_matrix_array = ins_ready_elements_km_set[local_index]
                for column_index,column_dof_location in enumerate(element_stiffness_matrix_dofs_location_list):
                    for row_index,row_dof_location in enumerate(element_stiffness_matrix_dofs_location_list):
                        stiffness_value = element_stiffness_matrix_array[column_index*len(element_stiffness_matrix_dofs_location_list)+row_index]
                        if stiffness_value == 0.0:
                            continue
                        else:
                            element_nonzero_values_list.append(stiffness_value)
                            element_nonzero_rows_list.append(row_dof_location)
                            element_nonzero_columns_list.append(column_dof_location)
                
                ins_ready_elements_sparse_gkm_values_set[local_index] = numpy.asarray(element_nonzero_values_list,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                ins_ready_elements_sparse_gkm_rows_set[local_index] = numpy.asarray(element_nonzero_rows_list,dtype=P4SFormat.NUMERICAL_PRECISION['int'])
                ins_ready_elements_sparse_gkm_columns_set[local_index] = numpy.asarray(element_nonzero_columns_list,dtype=P4SFormat.NUMERICAL_PRECISION['int'])
    @staticmethod
    def getElementIntegrationPointsNumber(in_type_number) -> int:
        if in_type_number in [121,321,322,131,431,631]:
            integration_points_number = 1
        elif in_type_number in [323,324,432]:
            integration_points_number = 4
        elif in_type_number in [632]:
            integration_points_number = 8
        else:
            pass
        
        return integration_points_number
    @staticmethod
    def getElementIntegrationPointsStrainAndStress(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            ins_ready_elements_set = ins_file['readyelements']
            ins_ready_elements_tm_set = ins_file['readyelementstm']
            ins_ready_elements_bm_set = ins_file['readyelementsbm']
            ins_ready_elements_dm_set = ins_file['readyelementsdm']
            ins_ready_elements_type_set = ins_file['readyelementstype']
            ins_all_nodes_first_dof_loc_set = ins_file['allnodesfirstdoflocation']
            ins_all_nodes_dofs_set = ins_file['allnodesdofs']
            ins_ready_elements_geometry_set = ins_file['readyelementsgeometry']
            ins_all_dofs_deltau_set = ins_file['alldofsdeltau']
            
            ins_ready_elements_ipee_set = ins_file['readyelementsipee']
            ins_ready_elements_ipes_set = ins_file['readyelementsipes']
            
            for local_index in range(ins_ready_elements_set.shape[0]):
                element_type_number = ins_ready_elements_type_set[local_index]
                element_geometry_parameters = ins_ready_elements_geometry_set[local_index]
                element_transform_array = ins_ready_elements_tm_set[local_index]
                element_strain_displacement_array = ins_ready_elements_bm_set[local_index]
                element_constitutive_array = ins_ready_elements_dm_set[local_index]
                
                element_dofs_list = P4SElementInfo.ELEMENT_NUMBER_TO_DOFS[element_type_number]
                element_include_delta_u_array = numpy.array([],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                element_include_nodes_label = ins_ready_elements_set[local_index]
                for node_label in element_include_nodes_label:
                    node_start_dof_location = ins_all_nodes_first_dof_loc_set[node_label-1]
                    element_include_dofs_location = node_start_dof_location + numpy.searchsorted(ins_all_nodes_dofs_set[node_label-1],numpy.asarray(element_dofs_list))
                    element_include_delta_u_array = numpy.concatenate((element_include_delta_u_array,ins_all_dofs_deltau_set[element_include_dofs_location]),axis=None)
            
                if element_type_number == 121:
                    transform_matrix = element_transform_array.reshape((2,4))
                    strain_displacement_matrix = element_strain_displacement_array.reshape((1,2))            
                    constitutive_stiffness_matrix = element_constitutive_array

                    ipee_array = numpy.zeros(shape=4,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipee_array[0] = numpy.dot(strain_displacement_matrix,numpy.dot(transform_matrix,element_include_delta_u_array.reshape(4,1)))[0,0]

                    ipes_array = numpy.zeros(shape=4,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipes_array = ipee_array * constitutive_stiffness_matrix[0]
                elif element_type_number == 131:
                    transform_matrix = element_transform_array.reshape((2,6))
                    strain_displacement_matrix = element_strain_displacement_array.reshape((1,2))
                    constitutive_stiffness_matrix = element_constitutive_array

                    ipee_array = numpy.zeros(shape=6,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipee_array[0] = numpy.dot(strain_displacement_matrix,numpy.dot(transform_matrix,element_include_delta_u_array))[0,0]

                    ipes_array = numpy.zeros(shape=6,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipes_array[0] = ipee_array * constitutive_stiffness_matrix[0]
                elif element_type_number == 321:
                    strain_displacement_matrix = element_strain_displacement_array.reshape((3,6))
                    constitutive_stiffness_matrix = element_constitutive_array.reshape((3,3))

                    temp_ipee_array = numpy.dot(strain_displacement_matrix,element_include_delta_u_array)
                    temp_ipes_array = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array)
                    
                    ipee_array = numpy.zeros(shape=4,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipee_array[0:2] = temp_ipee_array[0:2]
                    ipee_array[3] = temp_ipee_array[2]
                    
                    ipes_array = numpy.zeros(shape=4,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipes_array[0:2] = temp_ipes_array[0:2]
                    ipes_array[3] = temp_ipes_array[2]
                elif element_type_number == 322:
                    strain_displacement_matrix = element_strain_displacement_array.reshape((3,6))
                    constitutive_stiffness_matrix = element_constitutive_array.reshape((3,3))

                    temp_ipee_array = numpy.dot(strain_displacement_matrix,element_include_delta_u_array)
                    temp_ipes_array = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array)
                    
                    ipee_array = numpy.zeros(shape=4,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipee_array[0:2] = temp_ipee_array[0:2]
                    ipee_array[3] = temp_ipee_array[2]
                    
                    ipes_array = numpy.zeros(shape=4,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipes_array[0:2] = temp_ipes_array[0:2]
                    ipes_array[2] = (temp_ipes_array[0]+temp_ipes_array[1])*0.5*constitutive_stiffness_matrix[0,1] / (constitutive_stiffness_matrix[0,1] + constitutive_stiffness_matrix[2,2])
                    ipes_array[3] = temp_ipes_array[2]
                elif element_type_number == 323:
                    strain_displacement_matrix = element_strain_displacement_array.reshape((12,8))
                    constitutive_stiffness_matrix = element_constitutive_array.reshape((3,3))

                    temp_ipee_array = numpy.dot(strain_displacement_matrix,element_include_delta_u_array)
                    temp_ipes_array = numpy.zeros(shape=temp_ipee_array.shape[0],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    temp_ipes_array[0:3] = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array[0:3])
                    temp_ipes_array[3:6] = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array[3:6])
                    temp_ipes_array[6:9] = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array[6:9])
                    temp_ipes_array[9:12] = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array[9:12])
                    
                    ipee_array = numpy.zeros(shape=16,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipee_array[0:2] = temp_ipee_array[0:2]
                    ipee_array[3] = temp_ipee_array[2]
                    ipee_array[4:6] = temp_ipee_array[3:5]
                    ipee_array[7] = temp_ipee_array[5]
                    ipee_array[8:10] = temp_ipee_array[6:8]
                    ipee_array[11] = temp_ipee_array[8]
                    ipee_array[12:14] = temp_ipee_array[9:11]
                    ipee_array[15] = temp_ipee_array[11]
                    
                    ipes_array = numpy.zeros(shape=16,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipes_array[0:2] = temp_ipes_array[0:2]
                    ipes_array[3] = temp_ipes_array[2]
                    ipes_array[4:6] = temp_ipes_array[3:5]
                    ipes_array[7] = temp_ipes_array[5]
                    ipes_array[8:10] = temp_ipes_array[6:8]
                    ipes_array[11] = temp_ipes_array[8]
                    ipes_array[12:14] = temp_ipes_array[9:11]
                    ipes_array[15] = temp_ipes_array[11]
                elif element_type_number == 324:
                    strain_displacement_matrix = element_strain_displacement_array.reshape((12,8))
                    constitutive_stiffness_matrix = element_constitutive_array.reshape((3,3))

                    temp_ipee_array = numpy.dot(strain_displacement_matrix,element_include_delta_u_array)
                    temp_ipes_array = numpy.zeros(shape=temp_ipee_array.shape[0],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    temp_ipes_array[0:3] = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array[0:3])
                    temp_ipes_array[3:6] = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array[3:6])
                    temp_ipes_array[6:9] = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array[6:9])
                    temp_ipes_array[9:12] = numpy.dot(constitutive_stiffness_matrix,temp_ipee_array[9:12])
                    
                    ipee_array = numpy.zeros(shape=16,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipee_array[0:2] = temp_ipee_array[0:2]
                    ipee_array[3] = temp_ipee_array[2]
                    ipee_array[4:6] = temp_ipee_array[3:5]
                    ipee_array[7] = temp_ipee_array[5]
                    ipee_array[8:10] = temp_ipee_array[6:8]
                    ipee_array[11] = temp_ipee_array[8]
                    ipee_array[12:14] = temp_ipee_array[9:11]
                    ipee_array[15] = temp_ipee_array[11]
                    
                    ipes_array = numpy.zeros(shape=16,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipes_array[0:2] = temp_ipes_array[0:2]
                    ipes_array[2] = (temp_ipes_array[0]+temp_ipes_array[1])*0.5*constitutive_stiffness_matrix[0,1] / (constitutive_stiffness_matrix[0,1] + constitutive_stiffness_matrix[2,2])
                    ipes_array[3] = temp_ipes_array[2]
                    ipes_array[4:6] = temp_ipes_array[3:5]
                    ipes_array[6] = (temp_ipes_array[3]+temp_ipes_array[4])*0.5*constitutive_stiffness_matrix[0,1] / (constitutive_stiffness_matrix[0,1] + constitutive_stiffness_matrix[2,2])
                    ipes_array[7] = temp_ipes_array[5]
                    ipes_array[8:10] = temp_ipes_array[6:8]
                    ipes_array[10] = (temp_ipes_array[6]+temp_ipes_array[7])*0.5*constitutive_stiffness_matrix[0,1] / (constitutive_stiffness_matrix[0,1] + constitutive_stiffness_matrix[2,2])
                    ipes_array[11] = temp_ipes_array[8]
                    ipes_array[12:14] = temp_ipes_array[9:11]
                    ipes_array[14] = (temp_ipes_array[9]+temp_ipes_array[10])*0.5*constitutive_stiffness_matrix[0,1] / (constitutive_stiffness_matrix[0,1] + constitutive_stiffness_matrix[2,2])
                    ipes_array[15] = temp_ipes_array[11]
                elif element_type_number == 431:
                    membrane_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    membrane_constitutive_stiffness_matrix[0,0] = element_constitutive_array[0]
                    membrane_constitutive_stiffness_matrix[[0,1],[1,0]] = element_constitutive_array[1]
                    membrane_constitutive_stiffness_matrix[[0,2],[2,0]] = element_constitutive_array[2]
                    membrane_constitutive_stiffness_matrix[1,1] = element_constitutive_array[3]
                    membrane_constitutive_stiffness_matrix[[1,2],[2,1]] = element_constitutive_array[4]
                    membrane_constitutive_stiffness_matrix[2,2] = element_constitutive_array[5]
                    plate_bending_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_bending_constitutive_stiffness_matrix[0,0] = element_constitutive_array[0]
                    plate_bending_constitutive_stiffness_matrix[[0,1],[1,0]] = element_constitutive_array[1]
                    plate_bending_constitutive_stiffness_matrix[[0,2],[2,0]] = element_constitutive_array[2]
                    plate_bending_constitutive_stiffness_matrix[1,1] = element_constitutive_array[3]
                    plate_bending_constitutive_stiffness_matrix[[1,2],[2,1]] = element_constitutive_array[4]
                    plate_bending_constitutive_stiffness_matrix[2,2] = element_constitutive_array[5]
                    plate_shear_constitutive_stiffness_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_shear_constitutive_stiffness_matrix[0,0] = element_constitutive_array[6]
                    plate_shear_constitutive_stiffness_matrix[[0,1],[1,0]] = element_constitutive_array[7]
                    plate_shear_constitutive_stiffness_matrix[1,1] = element_constitutive_array[8]
                    
                    direction_cosine_matrix = element_transform_array.reshape((3,3))
                    local_delta_u_array = numpy.zeros(18,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(6):
                        local_delta_u_array[3*i:3*i+3] = numpy.dot(direction_cosine_matrix,element_include_delta_u_array[3*i:3*i+3])                
                    
                    ipee_array = numpy.zeros(shape=6,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipes_array = numpy.zeros(shape=6,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    shell_thickness = element_geometry_parameters[0] / element_geometry_parameters[1]
                    strain_displacement_matrix = element_strain_displacement_array.reshape((8,9))
                    membrane_local_ipee_array = numpy.dot(strain_displacement_matrix[0:3,:],local_delta_u_array[[0,1,5,6,7,11,12,13,17]])
                    plate_bending_local_ipee_array = -shell_thickness*0.5*numpy.dot(strain_displacement_matrix[3:6,:],local_delta_u_array[[2,3,4,8,9,10,14,15,16]])
                    plate_shear_local_ipee_array = numpy.dot(strain_displacement_matrix[6:8,:],local_delta_u_array[[2,3,4,8,9,10,14,15,16]])
                    ipee_array[[0,1,3]] = membrane_local_ipee_array+plate_bending_local_ipee_array
                    ipee_array[[4,5]] = plate_shear_local_ipee_array
                    ipes_array[[0,1,3]] = numpy.dot(membrane_constitutive_stiffness_matrix,ipee_array[[0,1,3]])
                    ipes_array[[4,5]] = numpy.dot(plate_shear_constitutive_stiffness_matrix,ipee_array[[4,5]])
                elif element_type_number == 432:
                    membrane_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    membrane_constitutive_stiffness_matrix[0,0] = element_constitutive_array[0]
                    membrane_constitutive_stiffness_matrix[[0,1],[1,0]] = element_constitutive_array[1]
                    membrane_constitutive_stiffness_matrix[[0,2],[2,0]] = element_constitutive_array[2]
                    membrane_constitutive_stiffness_matrix[1,1] = element_constitutive_array[3]
                    membrane_constitutive_stiffness_matrix[[1,2],[2,1]] = element_constitutive_array[4]
                    membrane_constitutive_stiffness_matrix[2,2] = element_constitutive_array[5]
                    plate_bending_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_bending_constitutive_stiffness_matrix[0,0] = element_constitutive_array[0]
                    plate_bending_constitutive_stiffness_matrix[[0,1],[1,0]] = element_constitutive_array[1]
                    plate_bending_constitutive_stiffness_matrix[[0,2],[2,0]] = element_constitutive_array[2]
                    plate_bending_constitutive_stiffness_matrix[1,1] = element_constitutive_array[3]
                    plate_bending_constitutive_stiffness_matrix[[1,2],[2,1]] = element_constitutive_array[4]
                    plate_bending_constitutive_stiffness_matrix[2,2] = element_constitutive_array[5]
                    plate_shear_constitutive_stiffness_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_shear_constitutive_stiffness_matrix[0,0] = element_constitutive_array[6]
                    plate_shear_constitutive_stiffness_matrix[[0,1],[1,0]] = element_constitutive_array[7]
                    plate_shear_constitutive_stiffness_matrix[1,1] = element_constitutive_array[8]

                    direction_cosine_matrix = element_transform_array.reshape((3,3))
                    local_delta_u_array = numpy.zeros(24,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(8):
                        local_delta_u_array[3*i:3*i+3] = numpy.dot(direction_cosine_matrix,element_include_delta_u_array[3*i:3*i+3])                
                    
                    ipee_array = numpy.zeros(shape=24,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipes_array = numpy.zeros(shape=24,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    shell_thickness = element_geometry_parameters[0] / element_geometry_parameters[1]
                    strain_displacement_matrix = element_strain_displacement_array.reshape((32,12))
                    for i in range(4):
                        membrane_local_ipee_array = numpy.dot(strain_displacement_matrix[8*i:8*i+3,:],local_delta_u_array[[0,1,5,6,7,11,12,13,17,18,19,23]])
                        plate_bending_local_ipee_array = -shell_thickness*0.5*numpy.dot(strain_displacement_matrix[8*i+3:8*i+6,:],local_delta_u_array[[2,3,4,8,9,10,14,15,16,20,21,22]])
                        plate_shear_local_ipee_array = numpy.dot(strain_displacement_matrix[8*i+6:8*i+8,:],local_delta_u_array[[2,3,4,8,9,10,14,15,16,20,21,22]])
                        
                        ipee_array[[6*i,6*i+1,6*i+3]] = membrane_local_ipee_array+plate_bending_local_ipee_array
                        ipee_array[[6*i+4,6*i+5]] = plate_shear_local_ipee_array
                        
                        ipes_array[[6*i,6*i+1,6*i+3]] = numpy.dot(membrane_constitutive_stiffness_matrix,ipee_array[[6*i,6*i+1,6*i+3]])
                        ipes_array[[6*i+4,6*i+5]] = numpy.dot(plate_shear_constitutive_stiffness_matrix,ipee_array[[6*i+4,6*i+5]])
                elif element_type_number == 631:
                    strain_displacement_matrix = element_strain_displacement_array.reshape((6,12))
                    constitutive_stiffness_matrix = element_constitutive_array.reshape((6,6))

                    ipee_array = numpy.dot(strain_displacement_matrix,element_include_delta_u_array)
                    ipes_array = numpy.dot(constitutive_stiffness_matrix,ipee_array)
                elif element_type_number == 632:
                    strain_displacement_matrix = element_strain_displacement_array.reshape((48,24))
                    constitutive_stiffness_matrix = element_constitutive_array.reshape((6,6))
                    
                    ipee_array = numpy.dot(strain_displacement_matrix,element_include_delta_u_array)
                    ipes_array = numpy.zeros(shape=ipee_array.shape[0],dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    ipes_array[0:6] = numpy.dot(constitutive_stiffness_matrix,ipee_array[0:6])
                    ipes_array[6:12] = numpy.dot(constitutive_stiffness_matrix,ipee_array[6:12])
                    ipes_array[12:18] = numpy.dot(constitutive_stiffness_matrix,ipee_array[12:18])
                    ipes_array[18:24] = numpy.dot(constitutive_stiffness_matrix,ipee_array[18:24])
                    ipes_array[24:30] = numpy.dot(constitutive_stiffness_matrix,ipee_array[24:30])
                    ipes_array[30:36] = numpy.dot(constitutive_stiffness_matrix,ipee_array[30:36])
                    ipes_array[36:42] = numpy.dot(constitutive_stiffness_matrix,ipee_array[36:42])
                    ipes_array[42:48] = numpy.dot(constitutive_stiffness_matrix,ipee_array[42:48])
                else:
                    pass
                
                ins_ready_elements_ipee_set[local_index] = ipee_array
                ins_ready_elements_ipes_set[local_index] = ipes_array


class P4SStepInfo():
    STEP_TYPE_TO_NUMBER = {'static':1}
    NUMBER_TO_STEP_TYPE = {1:'static'}
    
    INCREMENTATION_TYPE_TO_NUMBER = {'fixed':1,'automatic':2}
    NUMBER_TO_INCREMENTATION_TYPE = {1:'fixed',2:'automatic'}
    
    LSOLVER_TYPE_TO_NUMBER = {'direct':1,'iterative':2}
    NUMBER_TO_LSOLVER_TYPE = {1:'direct',2:'iterative'}
    SOLVER_METHOD_TO_NUMBER = {1:{'pardiso':1},
                               2:{'cg':1,'bicgstab':2,'minres':3,'gcrotmk':4,'tfqmr':5,'lsmr':6}}
    NUMBER_TO_SOLVER_METHOD = {1:{1:'pardiso'},
                               2:{1:'cg',2:'bicgstab',3:'minres',4:'gcrotmk',5:'tfqmr',6:'lsmr'}}


class P4SOutputInfo():
    
    FREQUENCY_REFERENCE_TO_NUMBER = {'last increment':1, 'every n increments':2, 'every n seconds':3}
    NUMBER_TO_FREQUENCY_REFERENCE = {1:'last increment', 2:'every n increments', 3:'every n seconds'}
    
    NODE_VARIABLES_DESCRIPTION = {
            'COORD': 'nodal coordinates',
            'U': 'translations and rotations',
            'CF': 'concentrated forces and moments',
            'RF': 'reaction forces and moments'
            }
    ELEMENT_VARIABLES_DESCRIPTION = {
            'CE':'strain components of centroid',
            'CS':'stress components of centroid',
            'VOL': 'element volume',
            'SE':'strain energy of element',
            }
    OPTIMIZATION_VARIABLES_DESCRIPTION = {
        'node': {},
        'element':{'X': 'topological density of element'}
    }
    VARIABLE_INCLUDE_COMPONENTS = {
        '2D':{
                'COORD':['X','Y'],
                'U':['U1','U2','UR3'],
                'CFM':['CF1','CF2','CM3'],
                'RFM':['RF1','RF2','RM3'],
                
                'CE':['E11','E22','E33','E12','PriE1','PriE2','PriE3'],
                'CS':['S11','S22','S33','S12','PriS1','PriS2','PriS3','Mises'],
                'VOL':['EVOL'],
                'SE':['ESE'],
                
                'X':['EX'],
                'O':['ALPHA']
            },
        
        '3D':{
                'COORD':['X','Y','Z'],
                'U':['U1','U2','U3','UR1','UR2','UR3'],
                'CFM':['CF1','CF2','CF3','CM1','CM2','CM3'],
                'RFM':['RF1','RF2','RF3','RM1','RM2','RM3'],
                
                'CE':['E11','E22','E33','E12','E13','E23','PriE1','PriE2','PriE3'],
                'CS':['S11','S22','S33','S12','S13','S23','PriS1','PriS2','PriS3','Mises'],
                'VOL':['EVOL'],
                'SE':['ESE'],
                
                'X':['EX'],
                'O':['ALPHA']
            }
    }
    
    @staticmethod
    def _addCOORD(in_dimension:str,in_step_name:str,in_group_name:str,in_frame_number:int,in_ins_result_file:object,in_ins_process_file:object)-> None:
        ins_result_step_include_frames_group = in_ins_result_file['Nodes']['COORD'][in_step_name]
        if str(in_frame_number) in ins_result_step_include_frames_group:
            ins_result_frame_set = ins_result_step_include_frames_group[str(in_frame_number)]
        else:
            nodes_number = in_ins_result_file['Mesh']['nodes'].shape[0]
            if in_dimension == '2D':
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(2,nodes_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            else:
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(3,nodes_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        
        ins_nodes_coordinates_set = in_ins_result_file['Mesh']['nodes']
        ins_group_include_labels_set = in_ins_result_file['Mesh']['Groups']['Nodes'][in_group_name]
        
        ins_process_constant_dloc_set = in_ins_process_file['Constant']['dloc']
        ins_process_record_u_set = in_ins_process_file['Record']['u']
        
        if in_dimension == '2D':
            for nodel_label in ins_group_include_labels_set[:]:
                nodel_index = nodel_label-1
                
                node_coordinates = ins_nodes_coordinates_set[nodel_index]
                node_start_dof_location = ins_process_constant_dloc_set[nodel_index]
                
                ins_result_frame_set[0,nodel_index] = node_coordinates[0] + ins_process_record_u_set[node_start_dof_location]
                ins_result_frame_set[1,nodel_index] = node_coordinates[1] + ins_process_record_u_set[node_start_dof_location+1]
        else:
            for nodel_label in ins_group_include_labels_set[:]:
                nodel_index = nodel_label-1
                
                node_coordinates = ins_nodes_coordinates_set[nodel_index]
                node_start_dof_location = ins_process_constant_dloc_set[nodel_index]
                
                ins_result_frame_set[0,nodel_index] = node_coordinates[0] + ins_process_record_u_set[node_start_dof_location]
                ins_result_frame_set[1,nodel_index] = node_coordinates[1] + ins_process_record_u_set[node_start_dof_location+1]
                ins_result_frame_set[2,nodel_index] = node_coordinates[2] + ins_process_record_u_set[node_start_dof_location+2]
    @staticmethod
    def _addU(in_dimension:str,in_step_name:str,in_group_name:str,in_frame_number:int,in_ins_result_file:object,in_ins_process_file:object)-> None:
        ins_result_step_include_frames_group = in_ins_result_file['Nodes']['U'][in_step_name]
        if str(in_frame_number) in ins_result_step_include_frames_group:
            ins_result_frame_set = ins_result_step_include_frames_group[str(in_frame_number)]
        else:
            nodes_number = in_ins_result_file['Mesh']['nodes'].shape[0]
            if in_dimension == '2D':
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(3,nodes_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            else:
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(6,nodes_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        
        ins_group_include_labels_set = in_ins_result_file['Mesh']['Groups']['Nodes'][in_group_name]
        
        ins_process_constant_dloc_set = in_ins_process_file['Constant']['dloc']
        ins_process_constant_dof_set = in_ins_process_file['Constant']['dof']
        ins_process_record_u_set = in_ins_process_file['Record']['u']
        
        if in_dimension == '2D':
            for nodel_label in ins_group_include_labels_set[:]:
                nodel_index = nodel_label - 1
                
                node_start_dof_location = ins_process_constant_dloc_set[nodel_index]
                node_include_dofs = ins_process_constant_dof_set[nodel_index]
                
                ins_result_frame_set[0,nodel_index] = ins_process_record_u_set[node_start_dof_location]
                ins_result_frame_set[1,nodel_index] = ins_process_record_u_set[node_start_dof_location+1]
                if 6 in node_include_dofs:
                    ins_result_frame_set[2,nodel_index] = ins_process_record_u_set[node_start_dof_location+2]
                else:
                    pass
        else:
            for nodel_label in ins_group_include_labels_set[:]:
                nodel_index = nodel_label-1
                
                node_start_dof_location = ins_process_constant_dloc_set[nodel_index]
                node_include_dofs = ins_process_constant_dof_set[nodel_index]
                
                for loc,dof in enumerate(node_include_dofs):
                    ins_result_frame_set[dof-1,nodel_index] = ins_process_record_u_set[node_start_dof_location+loc]
    @staticmethod
    def _addCFM(in_dimension:str,in_step_name:str,in_group_name:str,in_frame_number:int,in_ins_result_file:object,in_ins_process_file:object)-> None:
        ins_result_step_include_frames_group = in_ins_result_file['Nodes']['CFM'][in_step_name]
        if str(in_frame_number) in ins_result_step_include_frames_group:
            ins_result_frame_set = ins_result_step_include_frames_group[str(in_frame_number)]
        else:
            nodes_number = in_ins_result_file['Mesh']['nodes'].shape[0]
            if in_dimension == '2D':
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(3,nodes_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            else:
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(6,nodes_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        
        ins_group_include_labels_set = in_ins_result_file['Mesh']['Groups']['Nodes'][in_group_name]
        
        ins_process_constant_dloc_set = in_ins_process_file['Constant']['dloc']
        ins_process_constant_dof_set = in_ins_process_file['Constant']['dof']
        ins_process_record_fm_set = in_ins_process_file['Record']['fm']
         
        if in_dimension == '2D':
            for nodel_label in ins_group_include_labels_set[:]:
                nodel_index = nodel_label-1
                
                node_start_dof_location = ins_process_constant_dloc_set[nodel_index]
                node_include_dofs = ins_process_constant_dof_set[nodel_index]
                
                ins_result_frame_set[0,nodel_index] = ins_process_record_fm_set[node_start_dof_location]
                ins_result_frame_set[1,nodel_index] = ins_process_record_fm_set[node_start_dof_location+1]
                if 6 in node_include_dofs:
                    ins_result_frame_set[2,nodel_index] = ins_process_record_fm_set[node_start_dof_location+2]
                else:
                    pass
        else:
            for nodel_index in ins_group_include_labels_set[:]:
                nodel_index = nodel_label-1
                
                node_start_dof_location = ins_process_constant_dloc_set[nodel_index]
                node_include_dofs = ins_process_constant_dof_set[nodel_index]
                
                for loc,dof in enumerate(node_include_dofs):
                    ins_result_frame_set[dof-1,nodel_index] = ins_process_record_fm_set[node_start_dof_location+loc]
    @staticmethod
    def _addRFM(in_dimension:str,in_step_name:str,in_group_name:str,in_frame_number:int,in_ins_result_file:object,in_ins_process_file:object)-> None:
        ins_result_step_include_frames_group = in_ins_result_file['Nodes']['RFM'][in_step_name]
        if str(in_frame_number) in ins_result_step_include_frames_group:
            ins_result_frame_set = ins_result_step_include_frames_group[str(in_frame_number)]
        else:
            nodes_number = in_ins_result_file['Mesh']['nodes'].shape[0]
            if in_dimension == '2D':
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(3,nodes_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            else:
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(6,nodes_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        
        ins_group_include_labels_set = in_ins_result_file['Mesh']['Groups']['Nodes'][in_group_name]
        
        ins_process_constant_dloc_set = in_ins_process_file['Constant']['dloc']
        ins_process_constant_dof_set = in_ins_process_file['Constant']['dof']
        ins_process_record_rfm_set = in_ins_process_file['Record']['rfm']
        
        if in_dimension == '2D':
            for nodel_label in ins_group_include_labels_set[:]:
                nodel_index = nodel_label-1
                
                node_start_dof_location = ins_process_constant_dloc_set[nodel_index]
                node_include_dofs = ins_process_constant_dof_set[nodel_index]
                
                ins_result_frame_set[0,nodel_index] = ins_process_record_rfm_set[node_start_dof_location]
                ins_result_frame_set[1,nodel_index] = ins_process_record_rfm_set[node_start_dof_location+1]
                if 6 in node_include_dofs:
                    ins_result_frame_set[2,nodel_index] = ins_process_record_rfm_set[node_start_dof_location+2]
                else:
                    pass
        else:
            for nodel_label in range(ins_group_include_labels_set.shape[0]):
                nodel_index = nodel_label-1
                
                node_start_dof_location = ins_process_constant_dloc_set[nodel_index]
                node_include_dofs = ins_process_constant_dof_set[nodel_index]
                
                for loc,dof in enumerate(node_include_dofs):
                    ins_result_frame_set[dof-1,nodel_index] = ins_process_record_rfm_set[node_start_dof_location+loc]
    @staticmethod
    def _addCE(in_dimension:str,in_step_name:str,in_group_name:str,in_frame_number:int,in_ins_result_file:object,in_ins_process_file:object)-> None:
        ins_result_step_include_frames_group = in_ins_result_file['Elements']['CE'][in_step_name]
        if str(in_frame_number) in ins_result_step_include_frames_group:
            ins_result_frame_set = ins_result_step_include_frames_group[str(in_frame_number)]
        else:
            elements_number = in_ins_result_file['Mesh']['elements'].shape[0]
            if in_dimension == '2D':
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(7,elements_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            else:
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(9,elements_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        
        ins_group_include_labels_set = in_ins_result_file['Mesh']['Groups']['Elements'][in_group_name]
        
        ins_process_record_ipee_set = in_ins_process_file['Record']['ipee']
        
        if in_dimension == '2D':
            for element_label in ins_group_include_labels_set[:]:
                element_index = element_label-1
                
                ce11,ce22,ce33,ce12 = 0.0,0.0,0.0,0.0
                element_integration_points_components_array = ins_process_record_ipee_set[element_index]
                for point_index in range(int(element_integration_points_components_array.shape[0]/4)):
                    ce11 += element_integration_points_components_array[point_index*4]
                    ce22 += element_integration_points_components_array[point_index*4+1]
                    ce33 += element_integration_points_components_array[point_index*4+2]
                    ce12 += element_integration_points_components_array[point_index*4+3]
                ce11 = ce11/(point_index+1)
                ce22 = ce22/(point_index+1)
                ce33 = ce33/(point_index+1)
                ce12 = ce12/(point_index+1)
                ins_result_frame_set[0,element_index] = ce11
                ins_result_frame_set[1,element_index] = ce22
                ins_result_frame_set[2,element_index] = ce33
                ins_result_frame_set[3,element_index] = ce12
                
                principal_strain_array = numpy.zeros(shape=3,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                strain_results_matrix = numpy.zeros(shape=(2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                strain_results_matrix[0,0] = ce11
                strain_results_matrix[1,1] = ce22
                strain_results_matrix[[0,1],[1,0]] = ce12 * 0.5
                principal_strain_array[0:2] = numpy.linalg.eigvals(strain_results_matrix)
                principal_strain_array.sort()
                ins_result_frame_set[4,element_index] = principal_strain_array[2]
                ins_result_frame_set[5,element_index] = principal_strain_array[1]
                ins_result_frame_set[6,element_index] = principal_strain_array[0]
        else:
            for element_label in ins_group_include_labels_set[:]:
                element_index = element_label-1
                
                ce11,ce22,ce33,ce12,ce13,ce23 = 0.0,0.0,0.0,0.0,0.0,0.0
                element_integration_points_components_array = ins_process_record_ipee_set[element_index]
                for point_index in range(int(element_integration_points_components_array.shape[0]/6)):
                    ce11 += element_integration_points_components_array[point_index*6]
                    ce22 += element_integration_points_components_array[point_index*6+1]
                    ce33 += element_integration_points_components_array[point_index*6+2]
                    ce12 += element_integration_points_components_array[point_index*6+3]
                    ce13 += element_integration_points_components_array[point_index*6+4]
                    ce23 += element_integration_points_components_array[point_index*6+5]
                ce11 = ce11/(point_index+1)
                ce22 = ce22/(point_index+1)
                ce33 = ce33/(point_index+1)
                ce12 = ce12/(point_index+1)
                ce13 = ce13/(point_index+1)
                ce23 = ce23/(point_index+1)
                
                ins_result_frame_set[0,element_index] = ce11
                ins_result_frame_set[1,element_index] = ce22
                ins_result_frame_set[2,element_index] = ce33
                ins_result_frame_set[3,element_index] = ce12
                ins_result_frame_set[4,element_index] = ce13
                ins_result_frame_set[5,element_index] = ce23
                
                strain_results_matrix = numpy.zeros(shape=(3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                strain_results_matrix[0,0] = ce11
                strain_results_matrix[1,1] = ce22
                strain_results_matrix[2,2] = ce33
                strain_results_matrix[[0,1],[1,0]] = ce12 * 0.5
                strain_results_matrix[[0,2],[2,0]] = ce13 * 0.5
                strain_results_matrix[[1,2],[2,1]] = ce23 * 0.5
                principal_strain_array = numpy.linalg.eigvals(strain_results_matrix)
                principal_strain_array.sort()
                ins_result_frame_set[6,element_index] = principal_strain_array[2]
                ins_result_frame_set[7,element_index] = principal_strain_array[1]
                ins_result_frame_set[8,element_index] = principal_strain_array[0]
    @staticmethod
    def _addCS(in_dimension:str,in_step_name:str,in_group_name:str,in_frame_number:int,in_ins_result_file:object,in_ins_process_file:object)-> None:
        ins_result_step_include_frames_group = in_ins_result_file['Elements']['CS'][in_step_name]
        if str(in_frame_number) in ins_result_step_include_frames_group:
            ins_result_frame_set = ins_result_step_include_frames_group[str(in_frame_number)]
        else:
            elements_number = in_ins_result_file['Mesh']['elements'].shape[0]
            if in_dimension == '2D':
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(8,elements_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            else:
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(10,elements_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        
        ins_group_include_labels_set = in_ins_result_file['Mesh']['Groups']['Elements'][in_group_name]
        
        ins_process_record_ipes_set = in_ins_process_file['Record']['ipes']
        
        if in_dimension == '2D':
            for element_label in ins_group_include_labels_set[:]:
                element_index = element_label-1
                
                cs11,cs22,cs33,cs12 = 0.0,0.0,0.0,0.0
                element_integration_points_components_array = ins_process_record_ipes_set[element_index]
                for point_index in range(int(element_integration_points_components_array.shape[0]/4)):
                    cs11 += element_integration_points_components_array[point_index*4]
                    cs22 += element_integration_points_components_array[point_index*4+1]
                    cs33 += element_integration_points_components_array[point_index*4+2]
                    cs12 += element_integration_points_components_array[point_index*4+3]
                cs11 = cs11/(point_index+1)
                cs22 = cs22/(point_index+1)
                cs33 = cs33/(point_index+1)
                cs12 = cs12/(point_index+1)
                ins_result_frame_set[0,element_index] = cs11
                ins_result_frame_set[1,element_index] = cs22
                ins_result_frame_set[2,element_index] = cs33
                ins_result_frame_set[3,element_index] = cs12
                
                principal_stress_array = numpy.zeros(shape=3,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                stress_results_matrix = numpy.zeros(shape=(3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                stress_results_matrix[0,0] = cs11
                stress_results_matrix[1,1] = cs22
                stress_results_matrix[[0,1],[1,0]] = cs12
                stress_results_matrix[2,2] = cs33
                principal_stress_array[0:3] = numpy.linalg.eigvals(stress_results_matrix)
                principal_stress_array.sort()
                ins_result_frame_set[4,element_index] = principal_stress_array[2]
                ins_result_frame_set[5,element_index] = principal_stress_array[1]
                ins_result_frame_set[6,element_index] = principal_stress_array[0]
                ins_result_frame_set[7,element_index] = numpy.sqrt(((principal_stress_array[0]-principal_stress_array[1])**2 + (principal_stress_array[1]-principal_stress_array[2])**2 + (principal_stress_array[2]-principal_stress_array[0])**2)*0.5)
        else:
            for element_label in ins_group_include_labels_set[:]:
                element_index = element_label-1
                
                cs11,cs22,cs33,cs12,cs13,cs23 = 0.0,0.0,0.0,0.0,0.0,0.0
                element_integration_points_components_array = ins_process_record_ipes_set[element_index]
                for point_index in range(int(element_integration_points_components_array.shape[0]/6)):
                    cs11 += element_integration_points_components_array[point_index*6]
                    cs22 += element_integration_points_components_array[point_index*6+1]
                    cs33 += element_integration_points_components_array[point_index*6+2]
                    cs12 += element_integration_points_components_array[point_index*6+3]
                    cs13 += element_integration_points_components_array[point_index*6+4]
                    cs23 += element_integration_points_components_array[point_index*6+5]
                cs11 = cs11/(point_index+1)
                cs22 = cs22/(point_index+1)
                cs33 = cs33/(point_index+1)
                cs12 = cs12/(point_index+1)
                cs13 = cs13/(point_index+1)
                cs23 = cs23/(point_index+1)
                
                ins_result_frame_set[0,element_index] = cs11
                ins_result_frame_set[1,element_index] = cs22
                ins_result_frame_set[2,element_index] = cs33
                ins_result_frame_set[3,element_index] = cs12
                ins_result_frame_set[4,element_index] = cs13
                ins_result_frame_set[5,element_index] = cs23
                
                stress_results_matrix = numpy.zeros(shape=(3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                stress_results_matrix[0,0] = cs11
                stress_results_matrix[1,1] = cs22
                stress_results_matrix[2,2] = cs33
                stress_results_matrix[[0,1],[1,0]] = cs12
                stress_results_matrix[[0,2],[2,0]] = cs13
                stress_results_matrix[[1,2],[2,1]] = cs23
                
                principal_stress_array = numpy.linalg.eigvals(stress_results_matrix)
                principal_stress_array.sort()
                ins_result_frame_set[6,element_index] = principal_stress_array[2]
                ins_result_frame_set[7,element_index] = principal_stress_array[1]
                ins_result_frame_set[8,element_index] = principal_stress_array[0]
                ins_result_frame_set[9,element_index] = numpy.sqrt(((principal_stress_array[0]-principal_stress_array[1])**2 + (principal_stress_array[1]-principal_stress_array[2])**2 + (principal_stress_array[2]-principal_stress_array[0])**2)*0.5)
    @staticmethod
    def _addVOL(in_dimension:str,in_step_name:str,in_group_name:str,in_frame_number:int,in_ins_result_file:object,in_ins_process_file:object)-> None:
        ins_result_step_include_frames_group = in_ins_result_file['Elements']['VOL'][in_step_name]
        if str(in_frame_number) in ins_result_step_include_frames_group:
            ins_result_frame_set = ins_result_step_include_frames_group[str(in_frame_number)]
        else:
            elements_number = in_ins_result_file['Mesh']['elements'].shape[0]
            ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(1,elements_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        
        ins_group_include_labels_set = in_ins_result_file['Mesh']['Groups']['Elements'][in_group_name]
        
        ins_process_update_geometry_set = in_ins_process_file['Update']['geometry']
        
        for element_label in ins_group_include_labels_set[:]:
            element_index = element_label-1
            ins_result_frame_set[0,element_index] = ins_process_update_geometry_set[element_index][0]
    @staticmethod
    def __addSE(in_dimension:str,in_step_name:str,in_group_name:str,in_frame_number:int,in_ins_result_file:object,in_ins_process_file:object) -> None:
        ins_result_step_include_frames_group = in_ins_result_file['Elements']['SE'][in_step_name]
        if str(in_frame_number) in ins_result_step_include_frames_group:
            ins_result_frame_set = ins_result_step_include_frames_group[str(in_frame_number)]
        else:
            elements_number = in_ins_result_file['Mesh']['elements'].shape[0]
            if in_dimension == '2D':
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(1,elements_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
            else:
                ins_result_frame_set = ins_result_step_include_frames_group.create_dataset(name=str(in_frame_number),shape=(1,elements_number),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
        
        ins_group_include_labels_set = in_ins_result_file['Mesh']['Groups']['Elements'][in_group_name]
        
        ins_process_record_ipee_set = in_ins_process_file['Record']['ipee']
        ins_process_record_ipes_set = in_ins_process_file['Record']['ipes']
        ins_process_update_geometry_set = in_ins_process_file['Update']['geometry']
        
        if in_dimension == '2D':
            for element_label in ins_group_include_labels_set[:]:
                element_index = element_label-1
                
                element_se_value = 0.0
                integration_points_ipee_components_array = ins_process_record_ipee_set[element_index]
                integration_points_ipes_components_array = ins_process_record_ipes_set[element_index]
                for point_index in range(int(integration_points_ipee_components_array.shape[0]/4)):
                    ce11 = integration_points_ipee_components_array[point_index*4]
                    ce22 = integration_points_ipee_components_array[point_index*4+1]
                    ce33 = integration_points_ipee_components_array[point_index*4+2]
                    ce12 = 0.5*integration_points_ipee_components_array[point_index*4+3]
                    
                    cs11 = integration_points_ipes_components_array[point_index*4]
                    cs22 = integration_points_ipes_components_array[point_index*4+1]
                    cs33 = integration_points_ipes_components_array[point_index*4+2]
                    cs12 = integration_points_ipes_components_array[point_index*4+3]
                    
                    element_se_value += 0.5*(ce11*cs11+ce22*cs22+ce33*cs33+2.0*ce12*cs12)
                element_se_value =  element_se_value*ins_process_update_geometry_set[element_index][0] / (point_index+1)
                
                ins_result_frame_set[0,element_index] = element_se_value
        else:
            for element_label in ins_group_include_labels_set[:]:
                element_index = element_label-1
                
                element_se_value = 0.0
                integration_points_ipee_components_array = ins_process_record_ipee_set[element_index]
                integration_points_ipes_components_array = ins_process_record_ipes_set[element_index]
                for point_index in range(int(integration_points_ipee_components_array.shape[0]/6)):
                    ce11 = integration_points_ipee_components_array[point_index*6]
                    ce22 = integration_points_ipee_components_array[point_index*6+1]
                    ce33 = integration_points_ipee_components_array[point_index*6+2]
                    ce12 = 0.5*integration_points_ipee_components_array[point_index*6+3]
                    ce13 = 0.5*integration_points_ipee_components_array[point_index*6+4]
                    ce23 = 0.5*integration_points_ipee_components_array[point_index*6+5]
                    
                    cs11 = integration_points_ipes_components_array[point_index*6]
                    cs22 = integration_points_ipes_components_array[point_index*6+1]
                    cs33 = integration_points_ipes_components_array[point_index*6+2]
                    cs12 = integration_points_ipes_components_array[point_index*6+3]
                    cs13 = integration_points_ipes_components_array[point_index*6+4]
                    cs23 = integration_points_ipes_components_array[point_index*6+5]
                    
                    element_se_value += 0.5*(ce11*cs11+ce22*cs22+ce33*cs33+2.0*ce12*cs12+2.0*ce23*cs23+2.0*ce13*cs13)
                element_se_value =  element_se_value*ins_process_update_geometry_set[element_index][0] / (point_index+1)  
                
                ins_result_frame_set[0,element_index] = element_se_value
    add_data_to_result_file = {
                    'COORD':_addCOORD,
                    'U':_addU,
                    'CFM':_addCFM,
                    'RFM':_addRFM,
                    'CE':_addCE,
                    'CS':_addCS,
                    'VOL':_addVOL,
                    'SE':__addSE
    }


class P4SBCInfo():
    BC_TO_NUMBER = {'displacement':1,'concentrated force':2,'moment':3}
    NUMBER_TO_BC = {1:'displacement',2:'concentrated force',3:'moment'}
    
    BC_TO_GROUP_TYPE = {'displacement':'node','concentrated force':'node','moment':'node'}
    
    BC_COMPONENTS_2D = {'displacement':['U1','U2','UR3'],'concentrated force':['F1','F2'],'moment':['M3']}
    BC_COMPONENTS_3D = {'displacement':['U1','U2','U3','UR1','UR2','UR3'],'concentrated force':['F1','F2','F3'],'moment':['M1','M2','M3']}


class P4SOtherInfo():
    
    FUNCTION_TYPE_TO_NUMBER = {'piecewise':1,'periodic':2,'smooth':3}
    NUMBER_TO_FUNCTION_TYPE = {1:'piecewise',2:'periodic',3:'smooth'}


class P4SOptimizationInfo():
    OBJECTIVE_VARIABLES = {'2D':{'SE':['ESE'],'VOL':['EVOL'],'CS':['Mises']},
                           '3D':{'SE':['ESE'],'VOL':['EVOL'],'CS':['Mises']}
                           }
    CONSTRAIN_VARIABLES = {'2D':{'VOL':['EVOL'],'CS':['Mises'],'SE':['ESE']},
                           '3D':{'VOL':['EVOL'],'CS':['Mises'],'SE':['ESE']},
                           }
    VARIABLES_OPERATORS = {'SE':['sum'],'VOL':['sum'],'CS':['maximum']}
    
    @staticmethod
    def getElementsCenter(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            ins_ready_elements_set = ins_file['readyelements']
            start_node_label = ins_file['startnodelabel'][0]
            ins_instance_nodes_set = ins_file['instancenodes']
            
            ins_ready_elements_center_set = ins_file['readyelementscenter']
            for local_index in range(ins_ready_elements_set.shape[0]):
                center_coordinate_array = numpy.zeros(shape=3,dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                
                include_nodes_index_in_instance_array = ins_ready_elements_set[local_index]-start_node_label
                for node_index_in_instance in include_nodes_index_in_instance_array:
                    center_coordinate_array += ins_instance_nodes_set[node_index_in_instance]
                    
                ins_ready_elements_center_set[local_index,:] = center_coordinate_array / include_nodes_index_in_instance_array.shape[0]
    @staticmethod
    def getElementsNeighborsAndWeights(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            ready_elements_number = ins_file['readyelementsnumber'][0]
            ins_other_elements_label_set = ins_file['otherelementslabel']
            ins_other_elements_center_set = ins_file['otherelementscenter']
            filter_radius = ins_file['radius'][0]
            
            ins_other_elements_neighbors_set = ins_file['otherelementsneighbors']
            ins_other_elements_weight_set = ins_file['otherelementsweight']

            for local_index in range(ready_elements_number):
                central_element_label = ins_other_elements_label_set[local_index]
                central_element_center_coordinate = ins_other_elements_center_set[local_index]
                
                ins_other_elements_neighbors_set[local_index] = numpy.concatenate((ins_other_elements_neighbors_set[local_index][:],central_element_label),axis=None)
                ins_other_elements_weight_set[local_index] = numpy.concatenate((ins_other_elements_weight_set[local_index][:],filter_radius),axis=None)
                
                for other_local_index in range(local_index+1,ins_other_elements_label_set.shape[0]):
                    other_element_label = ins_other_elements_label_set[other_local_index]
                    other_element_center_coordinate = ins_other_elements_center_set[other_local_index]

                    centers_distance = numpy.linalg.norm(central_element_center_coordinate-other_element_center_coordinate)
                    distance_weight = filter_radius-centers_distance
                    
                    if distance_weight >= 0.0:
                        ins_other_elements_neighbors_set[local_index] = numpy.concatenate((ins_other_elements_neighbors_set[local_index][:],other_element_label),axis=None)
                        ins_other_elements_weight_set[local_index] = numpy.concatenate((ins_other_elements_weight_set[local_index][:],distance_weight),axis=None)
                        
                        ins_other_elements_neighbors_set[other_local_index] = numpy.concatenate((ins_other_elements_neighbors_set[other_local_index][:],central_element_label),axis=None)
                        ins_other_elements_weight_set[other_local_index] = numpy.concatenate((ins_other_elements_weight_set[other_local_index][:],distance_weight),axis=None)
                    else:
                        continue
    @staticmethod
    def getGlobalConstrainedDOFsLocation(in_fea_task_file_full_name:str, in_fea_process_file_full_name:str, in_ins_process_topopt_group:object) -> None:
        displacement_constrains_dict = {}
        with h5py.File(in_fea_task_file_full_name,'r') as ins_fea_task_file:
            model_dimension = str(ins_fea_task_file['basic'][0],encoding='utf-8')
            if model_dimension == '2D':
                allowed_components_dofs_list = [1,2,6]
            else:
                allowed_components_dofs_list = [1,2,3,4,5,6]
            
            for nodes_group,initial_components,first_step_components,*other in ins_fea_task_file['Conditions']['displacement'][:]:
                nodes_group = str(nodes_group,'utf-8')

                if nodes_group in displacement_constrains_dict:
                    for i,j,component_dof in zip([i for i in str(initial_components,'utf-8').split(',')[:-1]],[i for i in str(first_step_components,'utf-8').split(',')[:-1]],allowed_components_dofs_list):
                        if i == 'N' and j == 'N':
                            continue
                        else:
                            if component_dof in displacement_constrains_dict[nodes_group]:
                                continue
                            else:
                                displacement_constrains_dict[nodes_group].append(component_dof)
                else:
                    displacement_constrains_dict[nodes_group] = []
                    for i,j,component_dof in zip([i for i in str(initial_components,'utf-8').split(',')[:-1]],[i for i in str(first_step_components,'utf-8').split(',')[:-1]],allowed_components_dofs_list):
                        if i == 'N' and j == 'N':
                            continue
                        else:
                            displacement_constrains_dict[nodes_group].append(component_dof)
            
            del allowed_components_dofs_list
            del initial_components
            del first_step_components
        
        constrained_nodal_dofs_list = []
        with h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file:
            for nodes_group, component_dofs_list in displacement_constrains_dict.items():
                for node_lable in ins_fea_process_file['Constant']['NGroups'][nodes_group]:
                    node_include_dofs_array = ins_fea_process_file['Constant']['dof'][node_lable-1]
                    
                    constrained_dofs_location_in_node_array = numpy.intersect1d(node_include_dofs_array,component_dofs_list,assume_unique=True,return_indices=True)[1]
                    constrained_nodal_dofs_list.append(ins_fea_process_file['Constant']['dloc'][node_lable-1]+constrained_dofs_location_in_node_array)

            del nodes_group
            del component_dofs_list
        
        constrained_dofs_array = numpy.unique(numpy.concatenate(constrained_nodal_dofs_list,dtype=P4SFormat.NUMERICAL_PRECISION['int']))
        del constrained_nodal_dofs_list
        in_ins_process_topopt_group.create_dataset(name='gcdloc',data=constrained_dofs_array,dtype=P4SFormat.NUMERICAL_PRECISION['int'])
    @staticmethod
    def getElementsDOFs(in_fea_task_file_full_name:str, in_fea_process_file_full_name:str, in_ins_process_topopt_group:object) -> None:
        with h5py.File(in_fea_task_file_full_name,'r') as ins_fea_task_file, h5py.File(in_fea_process_file_full_name,'r') as ins_fea_process_file: 
            ins_elements_set = ins_fea_task_file['Mesh']['elements']
            ins_elements_type_set = ins_fea_task_file['Mesh']['type']
            ins_nodal_dofs_set = ins_fea_process_file['Constant']['dof']
            ins_nodes_sloc_set = ins_fea_process_file['Constant']['dloc']
        
            ins_elements_dofs_set = in_ins_process_topopt_group.create_dataset(name='elmsdofs',shape=(ins_elements_set.shape[0],),dtype=h5py.vlen_dtype(P4SFormat.NUMERICAL_PRECISION['int']))
            for element_index in range(ins_elements_set.shape[0]):
                element_type_number = ins_elements_type_set[element_index]
                element_dofs = P4SElementInfo.ELEMENT_NUMBER_TO_DOFS[element_type_number]
                
                nodes_label = ins_elements_set[element_index]
                nodes_dofs_location = numpy.empty(len(element_dofs)*len(nodes_label),dtype=P4SFormat.NUMERICAL_PRECISION['int'])
                for node_index_in_element,node_label in enumerate(nodes_label):
                    node_dofs = ins_nodal_dofs_set[node_label-1]
                    nodes_dofs_location[node_index_in_element*len(element_dofs):(node_index_in_element+1)*len(element_dofs)] = ins_nodes_sloc_set[node_label-1] + numpy.intersect1d(node_dofs,element_dofs,assume_unique=True,return_indices=True)[1]
                ins_elements_dofs_set[element_index] = nodes_dofs_location
    
    @staticmethod
    def getElementsFilteredDensityAndChainGradientInformation(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            ins_ready_elements_neighbor_set = ins_file['readyelementsneighbor']
            ins_ready_elements_weight_set = ins_file['readyelementsweight']
            ins_all_elements_design_x_set = ins_file['allelementsdesignx']
            ins_all_elements_volume_set = ins_file['allelementsvolume']
            
            ins_ready_elements_xphy_set = ins_file['readyelementsxphy']
            ins_ready_elements_xphy_chaingrad_set = ins_file['readyxphychaingrad']
            for local_index in range(ins_ready_elements_xphy_set.shape[0]):
                neighbor_elements_design_x_array = numpy.asarray([ins_all_elements_design_x_set[neighbor_elements_label-1] for neighbor_elements_label in ins_ready_elements_neighbor_set[local_index]])
                neighbor_elements_volume_array = numpy.asarray([ins_all_elements_volume_set[neighbor_elements_label-1] for neighbor_elements_label in ins_ready_elements_neighbor_set[local_index]])
                neighbor_elements_weight_array = ins_ready_elements_weight_set[local_index][:]
                neighbor_elements_sum_weight_and_volume_product = numpy.sum(neighbor_elements_weight_array*neighbor_elements_volume_array)
                ins_ready_elements_xphy_set[local_index] = numpy.sum(neighbor_elements_weight_array*neighbor_elements_volume_array*neighbor_elements_design_x_array) / neighbor_elements_sum_weight_and_volume_product

                ins_ready_elements_xphy_chaingrad_set[local_index] = neighbor_elements_sum_weight_and_volume_product
    @staticmethod
    def getElementsProjectionDensityAndChainGradientInformation(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            projection_beta,projection_eta = ins_file['projectionparameters']
            ins_ready_elements_xphy_set = ins_file['readyelementsxphy']

            projection_temp_param1 = numpy.tanh(projection_beta*projection_eta)
            projection_temp_param2 = numpy.tanh(projection_beta*(1.0-projection_eta))

            ins_ready_elements_xpro_set = ins_file['readyelementsxpro']
            ins_ready_elements_xpro_chaingrad_set = ins_file['readyxprochaingrad']
            ins_ready_elements_xpro_set[:] =  numpy.maximum((projection_temp_param1+numpy.tanh(projection_beta*(ins_ready_elements_xphy_set[:]-projection_eta))) / (projection_temp_param1+projection_temp_param2),0.01)
            ins_ready_elements_xpro_chaingrad_set[:] = projection_beta*(1.0-numpy.square(numpy.tanh(projection_beta*(ins_ready_elements_xphy_set[:]-projection_eta)))) / (projection_temp_param1+projection_temp_param2)
    @staticmethod
    def getElementsInterpolationFunction(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            interpolation_type_num,penalty_factor = ins_file['interpolationparameters']
            ins_ready_elements_xphy_set = ins_file['readyelementsxphy']
            
            ins_ready_elements_ifa_set = ins_file['readyelementsinterpolationfunction']
            if interpolation_type_num == 1.0:
                ins_ready_elements_ifa_set[:] = ins_ready_elements_xphy_set[:]**penalty_factor
            elif interpolation_type_num == 2.0:
                ins_ready_elements_ifa_set[:] = ins_ready_elements_xphy_set[:] / (1.0+penalty_factor*(1.0-ins_ready_elements_xphy_set[:]))
            else:
                pass
    
    @staticmethod
    def getElementsSEValue(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            ins_ready_elements_volume_set = ins_file['readyelementsvolume']
            ins_ready_elements_ipee_set = ins_file['readyelementsipee']
            ins_ready_elements_ipes_set = ins_file['readyelementsipes']
            model_dimension = ins_file['modeldimension'][0]

            ins_ready_elements_se_set = ins_file['readyelementsse']
            if model_dimension == 2:
                for local_index in range(ins_ready_elements_se_set.shape[0]):
                    element_ese_value = 0.0
                    
                    integration_points_ipee_components_array = ins_ready_elements_ipee_set[local_index][:]
                    integration_points_ipes_components_array = ins_ready_elements_ipes_set[local_index][:]
                    for point_index in range(int(integration_points_ipee_components_array.shape[0] / 4)):
                        ce11 = integration_points_ipee_components_array[point_index*4]
                        ce22 = integration_points_ipee_components_array[point_index*4+1]
                        ce33 = integration_points_ipee_components_array[point_index*4+2]
                        ce12 = 0.5*integration_points_ipee_components_array[point_index*4+3]
                        
                        cs11 = integration_points_ipes_components_array[point_index*4]
                        cs22 = integration_points_ipes_components_array[point_index*4+1]
                        cs33 = integration_points_ipes_components_array[point_index*4+2]
                        cs12 = integration_points_ipes_components_array[point_index*4+3]
                        
                        element_ese_value += 0.5*(ce11*cs11+ce22*cs22+ce33*cs33+2.0*ce12*cs12)
                    ins_ready_elements_se_set[local_index] = element_ese_value*ins_ready_elements_volume_set[local_index] / (point_index+1)
            elif model_dimension == 3:
                for local_index in range(ins_ready_elements_se_set.shape[0]):
                    element_ese_value = 0.0
                    
                    integration_points_ipee_components_array = ins_ready_elements_ipee_set[local_index][:]
                    integration_points_ipes_components_array = ins_ready_elements_ipes_set[local_index][:]
                    for point_index in range(int(integration_points_ipee_components_array.shape[0] / 6)):
                        ce11 = integration_points_ipee_components_array[point_index*6]
                        ce22 = integration_points_ipee_components_array[point_index*6+1]
                        ce33 = integration_points_ipee_components_array[point_index*6+2]
                        ce12 = 0.5*integration_points_ipee_components_array[point_index*6+3]
                        ce23 = 0.5*integration_points_ipee_components_array[point_index*6+4]
                        ce13 = 0.5*integration_points_ipee_components_array[point_index*6+5]
                        
                        cs11 = integration_points_ipes_components_array[point_index*6]
                        cs22 = integration_points_ipes_components_array[point_index*6+1]
                        cs33 = integration_points_ipes_components_array[point_index*6+2]
                        cs12 = integration_points_ipes_components_array[point_index*6+3]
                        cs23 = integration_points_ipes_components_array[point_index*6+4]
                        cs13 = integration_points_ipes_components_array[point_index*6+5]
                            
                        element_ese_value += 0.5*(ce11*cs11+ce22*cs22+ce33*cs33+2.0*ce12*cs12+2.0*ce23*cs23+2.0*ce13*cs13)
                    ins_ready_elements_se_set[local_index] =  element_ese_value*ins_ready_elements_volume_set[local_index] / (point_index+1)     
            else:
                pass
    @staticmethod
    def getElementsSESensitivity(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            interpolation_type_num,penalty_factor = ins_file['interpolationparameters']
            filter_type_num = ins_file['filter'][0]
            operator_type_num = ins_file['operator'][0]
            ins_ready_elements_label_set = ins_file['readyelementslabel']
            ins_all_elements_xphy_set = ins_file['allelementsxphy']
            ins_all_elements_se_set = ins_file['allelementsse']
            ins_all_elements_chaingrad_set = ins_file['allelementschaingrad']
    
            ins_ready_elements_se_sensitivity_set = ins_file['readyelementssesensitivity']
            if interpolation_type_num == 1 and filter_type_num == 1:
                for local_index in range(ins_ready_elements_label_set.shape[0]):
                    element_index = ins_ready_elements_label_set[local_index] - 1
                    
                    element_xphy = ins_all_elements_xphy_set[element_index]
                    element_se = ins_all_elements_se_set[element_index]
                    element_projection_chaingrad = ins_all_elements_chaingrad_set[1,element_index]
                    ins_ready_elements_se_sensitivity_set[local_index] = -penalty_factor*element_se*element_projection_chaingrad / element_xphy
            elif interpolation_type_num == 1 and filter_type_num == 2:
                ins_ready_elements_neighbor_set = ins_file['readyelementsneighbor']
                ins_ready_elements_weight_set = ins_file['readyelementsweight']
                ins_ready_elements_volume_set = ins_file['readyelementsvolume']
                
                for local_index in range(ins_ready_elements_label_set.shape[0]):
                    sensitivity_value = 0.0
                    central_element_volume = ins_ready_elements_volume_set[local_index]
                    for neighbor_element_label,neighbor_element_weight in zip(ins_ready_elements_neighbor_set[local_index],ins_ready_elements_weight_set[local_index]):
                        neighbor_element_index = neighbor_element_label-1
                        
                        neighbor_element_xphy = ins_all_elements_xphy_set[neighbor_element_index]
                        neighbor_element_projection_chaingrad = ins_all_elements_chaingrad_set[1,neighbor_element_index]
                        neighbor_element_se = ins_all_elements_se_set[neighbor_element_index]
                        neighbor_element_filtering_changrad = central_element_volume*neighbor_element_weight / ins_all_elements_chaingrad_set[0,neighbor_element_index]

                        sensitivity_value += -penalty_factor*neighbor_element_se*neighbor_element_projection_chaingrad*neighbor_element_filtering_changrad / neighbor_element_xphy
                    
                    ins_ready_elements_se_sensitivity_set[local_index] = sensitivity_value
            elif interpolation_type_num == 2 and filter_type_num == 1:
                for local_index in range(ins_ready_elements_label_set.shape[0]):
                    element_index = ins_ready_elements_label_set[local_index] - 1
                    
                    element_xphy = ins_all_elements_xphy_set[element_index]
                    element_se = ins_all_elements_se_set[element_index]
                    element_projection_chaingrad = ins_all_elements_chaingrad_set[1,element_index]
                    ins_ready_elements_se_sensitivity_set[local_index] = -(1.0+penalty_factor)*element_se*element_projection_chaingrad / ((1.0+penalty_factor-penalty_factor*element_xphy)*element_xphy)
            elif interpolation_type_num == 2 and filter_type_num == 2:
                ins_ready_elements_neighbor_set = ins_file['readyelementsneighbor']
                ins_ready_elements_weight_set = ins_file['readyelementsweight']
                ins_ready_elements_volume_set = ins_file['readyelementsvolume']
                
                for local_index in range(ins_ready_elements_label_set.shape[0]):
                    sensitivity_value = 0.0
                    central_element_volume = ins_ready_elements_volume_set[local_index]
                    for neighbor_element_label,neighbor_element_weight in zip(ins_ready_elements_neighbor_set[local_index],ins_ready_elements_weight_set[local_index]):
                        neighbor_element_index = neighbor_element_label-1
                        
                        neighbor_element_xphy = ins_all_elements_xphy_set[neighbor_element_index]
                        neighbor_element_projection_chaingrad = ins_all_elements_chaingrad_set[1,neighbor_element_index]
                        neighbor_element_se = ins_all_elements_se_set[neighbor_element_index]
                        neighbor_element_filtering_changrad = central_element_volume*neighbor_element_weight / ins_all_elements_chaingrad_set[0,neighbor_element_index]

                        sensitivity_value += -(1.0+penalty_factor)*neighbor_element_se*neighbor_element_projection_chaingrad*neighbor_element_filtering_changrad / ((1.0+penalty_factor-penalty_factor*neighbor_element_xphy)*neighbor_element_xphy)
                    
                    ins_ready_elements_se_sensitivity_set[local_index] = sensitivity_value    
            else:
                pass
    
    @staticmethod
    def getElementsVOLSensitivity(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            filter_type_num = ins_file['filter'][0]
            operator_type_num = ins_file['operator'][0]
            ins_ready_elements_label_set = ins_file['readyelementslabel']
            ins_all_elements_volume_set = ins_file['allelementsvolume']
            ins_all_elements_chaingrad_set = ins_file['allelementschaingrad']
    
            ins_ready_elements_vol_sensitivity_set = ins_file['readyelementsvolsensitivity']
            if filter_type_num == 1:
                for local_index in range(ins_ready_elements_label_set.shape[0]):
                    element_index = ins_ready_elements_label_set[local_index] - 1
                    
                    element_vol = ins_all_elements_volume_set[element_index]
                    element_projection_chaingrad = ins_all_elements_chaingrad_set[1,element_index]
                    ins_ready_elements_vol_sensitivity_set[local_index] = element_vol*element_projection_chaingrad
            elif filter_type_num == 2:
                ins_ready_elements_neighbor_set = ins_file['readyelementsneighbor']
                ins_ready_elements_weight_set = ins_file['readyelementsweight']
                ins_ready_elements_volume_set = ins_file['readyelementsvolume']
                
                for local_index in range(ins_ready_elements_label_set.shape[0]):
                    sensitivity_value = 0.0
                    central_element_volume = ins_ready_elements_volume_set[local_index]
                    for neighbor_element_label,neighbor_element_weight in zip(ins_ready_elements_neighbor_set[local_index],ins_ready_elements_weight_set[local_index]):
                        neighbor_element_index = neighbor_element_label-1
                        
                        neighbor_element_projection_chaingrad = ins_all_elements_chaingrad_set[1,neighbor_element_index]
                        neighbor_element_vol = ins_all_elements_volume_set[neighbor_element_index]
                        neighbor_element_filtering_changrad = central_element_volume*neighbor_element_weight / ins_all_elements_chaingrad_set[0,neighbor_element_index]

                        sensitivity_value += neighbor_element_vol*neighbor_element_projection_chaingrad*neighbor_element_filtering_changrad
                    
                    ins_ready_elements_vol_sensitivity_set[local_index] = sensitivity_value
            else:
                pass
    
    @staticmethod
    def getElementsCSValue(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            component_num = ins_file['stresscomponent'][0]
            ins_ready_elements_ipes_set = ins_file['readyelementsipes']
            
            ins_ready_elements_csc_set = ins_file['readyelementscsc']
            if ins_ready_elements_csc_set.shape[0] == 3:
                model_dimension = 2
            else:
                model_dimension = 3
            ins_ready_elements_cs_set = ins_file['readyelementscs']
            
            if component_num == 1:
                if model_dimension == 2:
                    for local_index in range(ins_ready_elements_cs_set.shape[0]):
                        cs11,cs22,cs12 = 0.0,0.0,0.0
                        integration_points_ipes_components_array = ins_ready_elements_ipes_set[local_index][:]
                        for point_index in range(int(integration_points_ipes_components_array.shape[0] / 4)):
                            cs11 += integration_points_ipes_components_array[point_index*4]
                            cs22 += integration_points_ipes_components_array[point_index*4+1]
                            cs12 += integration_points_ipes_components_array[point_index*4+3]
                        cs11 = cs11/(point_index+1)
                        cs22 = cs22/(point_index+1)
                        cs12 = cs12/(point_index+1)
                        
                        ins_ready_elements_cs_set[local_index] = numpy.sqrt(cs11**2+cs22**2-cs11*cs22+3.0*cs12**2)
                        
                        ins_ready_elements_csc_set[0,local_index] = cs11
                        ins_ready_elements_csc_set[1,local_index] = cs22
                        ins_ready_elements_csc_set[2,local_index] = cs12
                elif model_dimension == 3:
                    for local_index in range(ins_ready_elements_cs_set.shape[0]):
                        cs11,cs22,cs33,cs12,cs13,cs23 = 0.0,0.0,0.0,0.0,0.0,0.0
                        integration_points_ipes_components_array = ins_ready_elements_ipes_set[local_index][:]
                        for point_index in range(int(integration_points_ipes_components_array.shape[0] / 6)):
                            cs11 += integration_points_ipes_components_array[point_index*6]
                            cs22 += integration_points_ipes_components_array[point_index*6+1]
                            cs33 += integration_points_ipes_components_array[point_index*6+2]
                            cs12 += integration_points_ipes_components_array[point_index*6+3]
                            cs13 += integration_points_ipes_components_array[point_index*6+4]
                            cs23 += integration_points_ipes_components_array[point_index*6+5]
                        cs11 = cs11/(point_index+1)
                        cs22 = cs22/(point_index+1)
                        cs33 = cs33/(point_index+1)
                        cs12 = cs12/(point_index+1)
                        cs13 = cs13/(point_index+1)
                        cs23 = cs23/(point_index+1)
                        
                        ins_ready_elements_cs_set[local_index] = numpy.sqrt(cs11**2+cs22**2+cs33**2-cs11*cs22-cs22*cs33-cs11*cs33+3.0*cs12**2+3.0*cs23**2+3.0*cs13**2)
                        
                        ins_ready_elements_csc_set[0,local_index] = cs11
                        ins_ready_elements_csc_set[1,local_index] = cs22
                        ins_ready_elements_csc_set[2,local_index] = cs33
                        ins_ready_elements_csc_set[3,local_index] = cs12
                        ins_ready_elements_csc_set[4,local_index] = cs13
                        ins_ready_elements_csc_set[5,local_index] = cs23  
                else:
                    pass
            else:
                pass
    @staticmethod
    def getElementsMulMatrix(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            ins_ready_elements_csc = ins_file['readyelementscsc']
            if ins_ready_elements_csc.shape[0] == 3:
                mises_h_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                mises_h_matrix[[0,1],[0,1]] = 1.0
                mises_h_matrix[[0,1],[1,0]] = -0.5
                mises_h_matrix[2,2] = 3.0
            else:
                mises_h_matrix = numpy.zeros((6,6),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                mises_h_matrix[[0,1,2],[0,1,2]] = 1.0
                mises_h_matrix[[0,1,0,2,1,2],[1,0,2,0,2,1]] = -0.5
                mises_h_matrix[[3,4,5],[3,4,5]] = 3.0
            ins_ready_elements_type_num_set = ins_file['readyelementstype']
            
            ins_ready_elements_dm_set = ins_file['readyelementsdm']
            ins_ready_elements_bm_set = ins_file['readyelementsbm']
            ins_ready_elements_tm_set = ins_file['readyelementstm']
            ins_ready_elements_geometry_set = ins_file['readyelementsgeometry']
        
            ins_ready_elements_mulmatrix_set = ins_file['readyelementsmulmatrix']
            for local_index in range(ins_ready_elements_mulmatrix_set.shape[0]):
                element_type_num = ins_ready_elements_type_num_set[local_index]
                
                csc_vector = numpy.reshape(ins_ready_elements_csc[:,local_index],(-1,1))
                if element_type_num == 121:
                    constitutive_stiffness_matrix = ins_ready_elements_dm_set[local_index].reshape((1,1))
                    strain_displacement_matrix = ins_ready_elements_bm_set[local_index].reshape((1,2))
                    coordinates_transform_array = ins_ready_elements_tm_set[local_index].reshape((2,4))
                    
                    ins_ready_elements_mulmatrix_set[local_index] = csc_vector.T.dot(mises_h_matrix).dot(constitutive_stiffness_matrix).dot(strain_displacement_matrix).dot(coordinates_transform_array).flatten()
                elif element_type_num == 131:
                    constitutive_stiffness_matrix = ins_ready_elements_dm_set[local_index].reshape((1,1))
                    strain_displacement_matrix = ins_ready_elements_bm_set[local_index].reshape((1,2))
                    coordinates_transform_array = ins_ready_elements_tm_set[local_index].reshape((2,6))
                    
                    ins_ready_elements_mulmatrix_set[local_index] = csc_vector.T.dot(mises_h_matrix).dot(constitutive_stiffness_matrix).dot(strain_displacement_matrix).dot(coordinates_transform_array).flatten()
                elif element_type_num in [321,322]:
                    constitutive_stiffness_matrix = ins_ready_elements_dm_set[local_index].reshape((3,3))
                    strain_displacement_matrix = ins_ready_elements_bm_set[local_index].reshape((3,6))
                    ins_ready_elements_mulmatrix_set[local_index] = csc_vector.T.dot(mises_h_matrix).dot(constitutive_stiffness_matrix).dot(strain_displacement_matrix).flatten()
                elif element_type_num in [323,324]:
                    constitutive_stiffness_matrix = ins_ready_elements_dm_set[local_index].reshape((3,3))
                    
                    integration_points_strain_displacement_matrixes = ins_ready_elements_bm_set[local_index].reshape((12,8))
                    strain_displacement_matrix = numpy.zeros((3,8),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for ip_num in range(4):
                        strain_displacement_matrix += 0.25*integration_points_strain_displacement_matrixes[3*ip_num:3*(ip_num+1),:]
                
                    ins_ready_elements_mulmatrix_set[local_index] = csc_vector.T.dot(mises_h_matrix).dot(constitutive_stiffness_matrix).dot(strain_displacement_matrix).flatten()
                elif element_type_num == 431:
                    constitutive_array = ins_ready_elements_dm_set[local_index]
                    strain_displacement_array = ins_ready_elements_bm_set[local_index]
                    coordinates_transform_array = ins_ready_elements_tm_set[local_index]
                    geometry_parameters_array = ins_ready_elements_geometry_set[local_index]
                    
                    membrane_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    membrane_constitutive_stiffness_matrix[0,0] = constitutive_array[0]
                    membrane_constitutive_stiffness_matrix[[0,1],[1,0]] = constitutive_array[1]
                    membrane_constitutive_stiffness_matrix[[0,2],[2,0]] = constitutive_array[2]
                    membrane_constitutive_stiffness_matrix[1,1] = constitutive_array[3]
                    membrane_constitutive_stiffness_matrix[[1,2],[2,1]] = constitutive_array[4]
                    membrane_constitutive_stiffness_matrix[2,2] = constitutive_array[5]
                    plate_bending_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_bending_constitutive_stiffness_matrix[0,0] = constitutive_array[0]
                    plate_bending_constitutive_stiffness_matrix[[0,1],[1,0]] = constitutive_array[1]
                    plate_bending_constitutive_stiffness_matrix[[0,2],[2,0]] = constitutive_array[2]
                    plate_bending_constitutive_stiffness_matrix[1,1] = constitutive_array[3]
                    plate_bending_constitutive_stiffness_matrix[[1,2],[2,1]] = constitutive_array[4]
                    plate_bending_constitutive_stiffness_matrix[2,2] = constitutive_array[5]
                    plate_shear_constitutive_stiffness_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_shear_constitutive_stiffness_matrix[0,0] = constitutive_array[6]
                    plate_shear_constitutive_stiffness_matrix[[0,1],[1,0]] = constitutive_array[7]
                    plate_shear_constitutive_stiffness_matrix[1,1] = constitutive_array[8]
                    shell_total_strain_matrix = strain_displacement_array.reshape((8,9))
                    membrane_strain_displacement_matrix = shell_total_strain_matrix[0:3,:]
                    plate_bending_strain_displacement_matrix = shell_total_strain_matrix[3:6,:]
                    plate_shear_strain_displacement_matrix = shell_total_strain_matrix[6:8,:]
                    
                    membrane_db_matrix = numpy.dot(membrane_constitutive_stiffness_matrix,membrane_strain_displacement_matrix)
                    shell_thickness = geometry_parameters_array[0] / geometry_parameters_array[1]
                    plate_bending_db_matrix = -shell_thickness*0.5*numpy.dot(plate_bending_constitutive_stiffness_matrix,plate_bending_strain_displacement_matrix)
                    plate_shear_db_matrix = numpy.dot(plate_shear_constitutive_stiffness_matrix,plate_shear_strain_displacement_matrix)
                    db_matrix = numpy.zeros((6,18),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(3):
                        db_matrix[0:2,6*i:6*i+2] = membrane_db_matrix[0:2,3*i:3*i+2]
                        db_matrix[0:2,6*i+5] = membrane_db_matrix[0:2,3*i+2]
                        db_matrix[3,6*i:6*i+2] = membrane_db_matrix[2,3*i:3*i+2]
                        db_matrix[3,6*i+5] = membrane_db_matrix[2,3*i+2]
                        
                        db_matrix[0:2,6*i+2:6*i+5] = plate_bending_db_matrix[0:2,3*i:3*i+3]
                        db_matrix[3,6*i+2:6*i+5] = plate_bending_db_matrix[2,3*i:3*i+3]
                        
                        db_matrix[4:6,6*i+2:6*i+5] = plate_shear_db_matrix[0:2,3*i:3*i+3]
                    
                    direction_cosine_matrix = coordinates_transform_array.reshape((3,3))
                    coordinates_transform_matrix = numpy.zeros((18,18),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(6):
                        coordinates_transform_matrix[3*i:3*i+3,3*i:3*i+3] = direction_cosine_matrix
                    
                    ins_ready_elements_mulmatrix_set[local_index] = csc_vector.T.dot(mises_h_matrix).dot(db_matrix).dot(coordinates_transform_matrix).flatten()
                elif element_type_num == 432:
                    constitutive_array = ins_ready_elements_dm_set[local_index]
                    strain_displacement_array = ins_ready_elements_bm_set[local_index]
                    coordinates_transform_array = ins_ready_elements_tm_set[local_index]
                    geometry_parameters_array = ins_ready_elements_geometry_set[local_index]
                    
                    membrane_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    membrane_constitutive_stiffness_matrix[0,0] = constitutive_array[0]
                    membrane_constitutive_stiffness_matrix[[0,1],[1,0]] = constitutive_array[1]
                    membrane_constitutive_stiffness_matrix[[0,2],[2,0]] = constitutive_array[2]
                    membrane_constitutive_stiffness_matrix[1,1] = constitutive_array[3]
                    membrane_constitutive_stiffness_matrix[[1,2],[2,1]] = constitutive_array[4]
                    membrane_constitutive_stiffness_matrix[2,2] = constitutive_array[5]
                    plate_bending_constitutive_stiffness_matrix = numpy.zeros((3,3),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_bending_constitutive_stiffness_matrix[0,0] = constitutive_array[0]
                    plate_bending_constitutive_stiffness_matrix[[0,1],[1,0]] = constitutive_array[1]
                    plate_bending_constitutive_stiffness_matrix[[0,2],[2,0]] = constitutive_array[2]
                    plate_bending_constitutive_stiffness_matrix[1,1] = constitutive_array[3]
                    plate_bending_constitutive_stiffness_matrix[[1,2],[2,1]] = constitutive_array[4]
                    plate_bending_constitutive_stiffness_matrix[2,2] = constitutive_array[5]
                    plate_shear_constitutive_stiffness_matrix = numpy.zeros((2,2),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_shear_constitutive_stiffness_matrix[0,0] = constitutive_array[6]
                    plate_shear_constitutive_stiffness_matrix[[0,1],[1,0]] = constitutive_array[7]
                    plate_shear_constitutive_stiffness_matrix[1,1] = constitutive_array[8]

                    integration_points_shell_total_strain_matrixes = strain_displacement_array.reshape((32,12))
                    membrane_strain_displacement_matrix = numpy.zeros((3,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_bending_strain_displacement_matrix = numpy.zeros((3,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    plate_shear_strain_displacement_matrix = numpy.zeros((2,12),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for ip_num in range(4):
                        membrane_strain_displacement_matrix += 0.25*integration_points_shell_total_strain_matrixes[8*ip_num:8*ip_num+3,:]
                        plate_bending_strain_displacement_matrix += 0.25*integration_points_shell_total_strain_matrixes[8*ip_num+3:8*ip_num+6,:]
                        plate_shear_strain_displacement_matrix += 0.25*integration_points_shell_total_strain_matrixes[8*ip_num+6:8*ip_num+8,:]
                    
                    membrane_db_matrix = numpy.dot(membrane_constitutive_stiffness_matrix,membrane_strain_displacement_matrix)
                    shell_thickness = geometry_parameters_array[0] / geometry_parameters_array[1]
                    plate_bending_db_matrix = -shell_thickness*0.5*numpy.dot(plate_bending_constitutive_stiffness_matrix,plate_bending_strain_displacement_matrix)
                    plate_shear_db_matrix = numpy.dot(plate_shear_constitutive_stiffness_matrix,plate_shear_strain_displacement_matrix)
                    db_matrix = numpy.zeros((6,24),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(4):
                        db_matrix[0:2,6*i:6*i+2] = membrane_db_matrix[0:2,3*i:3*i+2]
                        db_matrix[0:2,6*i+5] = membrane_db_matrix[0:2,3*i+2]
                        db_matrix[3,6*i:6*i+2] = membrane_db_matrix[2,3*i:3*i+2]
                        db_matrix[3,6*i+5] = membrane_db_matrix[2,3*i+2]
                        
                        db_matrix[0:2,6*i+2:6*i+5] = plate_bending_db_matrix[0:2,3*i:3*i+3]
                        db_matrix[3,6*i+2:6*i+5] = plate_bending_db_matrix[2,3*i:3*i+3]
                        
                        db_matrix[4:6,6*i+2:6*i+5] = plate_shear_db_matrix[0:2,3*i:3*i+3]
                    
                    direction_cosine_matrix = coordinates_transform_array.reshape((3,3))
                    coordinates_transform_matrix = numpy.zeros((24,24),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for i in range(8):
                        coordinates_transform_matrix[3*i:3*i+3,3*i:3*i+3] = direction_cosine_matrix
                    
                    ins_ready_elements_mulmatrix_set[local_index] = csc_vector.T.dot(mises_h_matrix).dot(db_matrix).dot(coordinates_transform_matrix).flatten()
                elif element_type_num == 631:
                    constitutive_stiffness_matrix = ins_ready_elements_dm_set[local_index].reshape((6,6))
                    strain_displacement_matrix = ins_ready_elements_bm_set[local_index].reshape((6,12))
                    ins_ready_elements_mulmatrix_set[local_index] = csc_vector.T.dot(mises_h_matrix).dot(constitutive_stiffness_matrix).dot(strain_displacement_matrix).flatten()
                elif element_type_num == 632:
                    constitutive_stiffness_matrix = ins_ready_elements_dm_set[local_index].reshape((6,6))
                    integration_points_strain_displacement_matrixes = ins_ready_elements_bm_set[local_index].reshape((48,24))
                    strain_displacement_matrix = numpy.zeros((6,24),dtype=P4SFormat.NUMERICAL_PRECISION['float'])
                    for ip_num in range(8):
                        strain_displacement_matrix += 0.125*integration_points_strain_displacement_matrixes[6*ip_num:6*(ip_num+1)]
                    ins_ready_elements_mulmatrix_set[local_index] = csc_vector.T.dot(mises_h_matrix).dot(constitutive_stiffness_matrix).dot(strain_displacement_matrix).flatten()
                else:
                    pass
    @staticmethod
    def getElementsMisesPNGradient(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            ins_dpndrcs_set = ins_file['readyelementsdpndrcs']
            interpolation_type_num,penalty_factor = ins_file['interpolationparameters']
            ins_ready_elements_xphy_set = ins_file['readyelementsxphy']
            ins_ready_elements_ifa_set = ins_file['readyelementsifa']
            ins_ready_elements_mulmatrix_set = ins_file['readyelementsmulmatrix']
            ins_ready_elements_u_set = ins_file['readyelementsu']
            ins_ready_elements_cs_set = ins_file['readyelementscs']
            ins_ready_elements_adjoint_set = ins_file['readyelementsadjoint']
            ins_ready_elements_km_set = ins_file['readyelementskm']
            
            relaxation_factor = penalty_factor*0.8
            
            ins_ready_elements_dpndxphy_set = ins_file['readyelementsdpndxphy']
            if interpolation_type_num == 1:
                for local_index in range(ins_ready_elements_dpndxphy_set.shape[0]):
                    element_dpndrcs_value = ins_dpndrcs_set[local_index]
                    element_xphy_value = ins_ready_elements_xphy_set[local_index]
                    element_ifa_value = ins_ready_elements_ifa_set[local_index]
                    element_difa_value = penalty_factor*element_xphy_value**(penalty_factor-1.0)
                    element_rfa_value = element_xphy_value**relaxation_factor
                    element_drfa_value = relaxation_factor*element_xphy_value**(relaxation_factor-1.0)
                    element_cs_value = ins_ready_elements_cs_set[local_index]
                    
                    element_mulmatrix_vector = numpy.reshape(ins_ready_elements_mulmatrix_set[local_index],(-1,1))
                    element_u_vector = numpy.reshape(ins_ready_elements_u_set[local_index],(-1,1))
                    element_adjoint_vector = numpy.reshape(ins_ready_elements_adjoint_set[local_index],(-1,1))
                    element_km = numpy.reshape(ins_ready_elements_km_set[local_index],(element_u_vector.shape[0],element_u_vector.shape[0]))
                    
                    temp_1 = element_dpndrcs_value*numpy.dot(element_mulmatrix_vector.T,element_u_vector)[0,0]*element_difa_value / (element_ifa_value*element_rfa_value*element_cs_value)
                    temp_2 = numpy.dot(numpy.dot(element_adjoint_vector.T,element_km),element_u_vector)[0,0] * element_difa_value / element_ifa_value
                    temp_3 = element_dpndrcs_value*element_cs_value*element_drfa_value / element_rfa_value**2
                    
                    ins_ready_elements_dpndxphy_set[local_index] = temp_1 - temp_2 - temp_3
            elif interpolation_type_num == 2:
                for local_index in range(ins_ready_elements_dpndxphy_set.shape[0]):
                    element_dpndrcs_value = ins_dpndrcs_set[local_index]
                    element_xphy_value = ins_ready_elements_xphy_set[local_index]
                    element_ifa_value = ins_ready_elements_ifa_set[local_index]
                    element_difa_value = (1.0+penalty_factor) / (1.0+penalty_factor-penalty_factor*element_xphy_value)**2
                    element_rfa_value = element_xphy_value / (1.0+relaxation_factor-relaxation_factor*element_xphy_value)
                    element_drfa_value = (1.0+relaxation_factor) / (1.0+relaxation_factor-relaxation_factor*element_xphy_value)**2
                    element_cs_value = ins_ready_elements_cs_set[local_index]
                    
                    element_mulmatrix_vector = numpy.reshape(ins_ready_elements_mulmatrix_set[local_index],(-1,1))
                    element_u_vector = numpy.reshape(ins_ready_elements_u_set[local_index],(-1,1))
                    element_adjoint_vector = numpy.reshape(ins_ready_elements_adjoint_set[local_index],(-1,1))
                    element_km = numpy.reshape(ins_ready_elements_km_set[local_index],(element_u_vector.shape[0],element_u_vector.shape[0]))
                    
                    temp_1 = element_dpndrcs_value*numpy.dot(element_mulmatrix_vector.T,element_u_vector)[0,0]*element_difa_value / (element_ifa_value*element_rfa_value*element_cs_value)
                    temp_2 = numpy.dot(numpy.dot(element_adjoint_vector.T,element_km),element_u_vector)[0,0] * element_difa_value / element_ifa_value
                    temp_3 = element_dpndrcs_value*element_cs_value*element_drfa_value / element_rfa_value**2
                    
                    ins_ready_elements_dpndxphy_set[local_index] = temp_1 - temp_2 - temp_3
            else:
                pass
    @staticmethod
    def getElementsCSSensitivity(in_temp_file_full_name:str) -> None:
        with h5py.File(in_temp_file_full_name,'r+') as ins_file:
            filter_type_num = ins_file['filter'][0]
            ins_ready_elements_label_set = ins_file['readyelementslabel']
            ins_all_elements_dpndxphy_set = ins_file['allelementsdpndxphy']
            ins_all_elements_chaingrad_set = ins_file['allelementschaingrad']
            
            ins_ready_elements_cs_sensitivity_set = ins_file['readyelementscssensitivity']
            if filter_type_num == 1:
                for local_index in range(ins_ready_elements_label_set.shape[0]):
                    element_index = ins_ready_elements_label_set[local_index] - 1
                    
                    element_dpndxphy = ins_all_elements_dpndxphy_set[element_index]
                    element_projection_chaingrad = ins_all_elements_chaingrad_set[1,element_index]
                    ins_ready_elements_cs_sensitivity_set[local_index] = element_dpndxphy*element_projection_chaingrad
            elif filter_type_num == 2:
                ins_ready_elements_neighbor_set = ins_file['readyelementsneighbor']
                ins_ready_elements_weight_set = ins_file['readyelementsweight']
                ins_ready_elements_volume_set = ins_file['readyelementsvolume']
                
                for local_index in range(ins_ready_elements_label_set.shape[0]):
                    sensitivity_value = 0.0
                    central_element_volume = ins_ready_elements_volume_set[local_index]
                    for neighbor_element_label,neighbor_element_weight in zip(ins_ready_elements_neighbor_set[local_index],ins_ready_elements_weight_set[local_index]):
                        neighbor_element_index = neighbor_element_label-1
                        
                        neighbor_element_projection_chaingrad = ins_all_elements_chaingrad_set[1,neighbor_element_index]
                        neighbor_element_dpndxphy = ins_all_elements_dpndxphy_set[neighbor_element_index]
                        neighbor_element_filtering_changrad = central_element_volume*neighbor_element_weight / ins_all_elements_chaingrad_set[0,neighbor_element_index]

                        sensitivity_value += neighbor_element_dpndxphy*neighbor_element_projection_chaingrad*neighbor_element_filtering_changrad
                    
                    ins_ready_elements_cs_sensitivity_set[local_index] = sensitivity_value
            else:
                pass
