# coding=utf-8
# Copyright (C) 2026 Huaiwang Ji <jihuaiwang@outlook.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import sqlite3

import numpy
import vtk
import h5py

from config import common

class P4SProjectDatabase():
    def __init__(self,in_full_project_name:str, in_is_created:bool):
        if in_is_created:
            self.__full_project_name = in_full_project_name + '_temp'
            self.__ins_database = sqlite3.connect(self.__full_project_name,isolation_level=None)
            self.__ins_cursor = self.__ins_database.cursor()
        else:
            self.__full_project_name = in_full_project_name
            self.__ins_database = sqlite3.connect(self.__full_project_name,isolation_level=None)
        self.__ins_cursor = self.__ins_database.cursor()
        self.__ins_cursor.execute('BEGIN')

        if in_is_created:
            self.__ins_cursor.execute(f'CREATE TABLE models(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, dimension TEXT NOT NULL)')
            
            self.__ins_cursor.execute(f'CREATE TABLE parts(model INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, nodes INTEGER NOT NULL, elements INTEGER NOT NULL)')
            self.__ins_cursor.execute(f'CREATE TABLE assembly(model INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT, part INTEGER NOT NULL, name TEXT NOT NULL, ox REAL NOT NULL, oy REAL NOT NULL, oz REAL NOT NULL, ori1 REAL NOT NULL, ori2 REAL NOT NULL, ori3 REAL NOT NULL, ori4 REAL NOT NULL)')
            self.__ins_cursor.execute(f'CREATE TABLE groups(model INTEGER NOT NULL, sign INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, type INTEGER NOT NULL, number INTEGER NOT NULL)')
            self.__ins_cursor.execute(f'CREATE TABLE groups_instances_association(model INTEGER NOT NULL, agroup INTEGER NOT NULL, instance INTEGER NOT NULL)')
            
            self.__ins_cursor.execute(f'CREATE TABLE materials(model INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, elasticity INTEGETR NOT NULL, eparams TEXT NOT NULL)')
            self.__ins_cursor.execute(f'CREATE TABLE attributes(model INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, type INTEGETR NOT NULL, parameters TEXT)')
            self.__ins_cursor.execute(f'CREATE TABLE property_assignments(id INTEGER PRIMARY KEY AUTOINCREMENT,model INTEGER NOT NULL, part INTEGER NOT NULL, pgroup INTEGER NOT NULL,\
                                        geo1_attribute INTEGER, geo1_material INTEGER, geo1_etype INTEGER, geo2_attribute INTEGER, geo2_material INTEGER, geo2_etype INTEGER,\
                                        geo3_attribute INTEGER, geo3_material INTEGER, geo3_etype INTEGER, geo4_attribute INTEGER, geo4_material INTEGER, geo4_etype INTEGER,\
                                        geo5_attribute INTEGER, geo5_material INTEGER, geo5_etype INTEGER, geo6_attribute INTEGER, geo6_material INTEGER, geo6_etype INTEGER,\
                                        geo7_attribute INTEGER, geo7_material INTEGER, geo7_etype INTEGER, geo8_attribute INTEGER, geo8_material INTEGER, geo8_etype INTEGER,\
                                        geo9_attribute INTEGER, geo9_material INTEGER, geo9_etype INTEGER, geo10_attribute INTEGER, geo10_material INTEGER, geo10_etype INTEGER)')
            
            self.__ins_cursor.execute(f'CREATE TABLE coordinate_systems(model INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, source INTEGETR NOT NULL, type INTEGETR NOT NULL,\
                                        ox REAL NOT NULL, oy REAL NOT NULL, oz REAL NOT NULL, ori1 REAL NOT NULL, ori2 REAL NOT NULL, ori3 REAL NOT NULL, ori4 REAL NOT NULL)')
            self.__ins_cursor.execute(f'CREATE TABLE orientation_assignments(id INTEGER PRIMARY KEY AUTOINCREMENT,model INTEGER NOT NULL, part INTEGER NOT NULL, pgroup INTEGER NOT NULL, reference INTEGER NOT NULL, raxis INTEGER NOT NULL, angle REAL NOT NULL)')
            
            self.__ins_cursor.execute(f'CREATE TABLE steps(model INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, type INTEGER NOT NULL, sequence INTEGER NOT NULL, time REAL NOT NULL, nlgeom INTEGER NOT NULL, basic TEXT NOT NULL, lsolver TEXT NOT NULL)')
            
            self.__ins_cursor.execute(f'CREATE TABLE outputs(model INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, type INTEGER NOT NULL, bstep INTEGER NOT NULL, estep INTEGER NOT NULL, reference INTEGER NOT NULL, frequency REAL, agroup INTEGER NOT NULL, variables TEXT NOT NULL)')
            
            self.__ins_cursor.execute(f'CREATE TABLE boundary_conditions(model INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, type INTEGER NOT NULL, agroup INTEGER NOT NULL, csys integer NOT NULL, definition INTEGER NOT NULL, initial TEXT)')

            self.__ins_cursor.execute(f"CREATE TABLE functions(model INTEGER NOT NULL, id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, type INTEGER NOT NULL, parameters TEXT NOT NULL)")
        else:
            pass
    
    def getFullProjectName(self) -> str:
        return self.__full_project_name

    def saveProjectDatabase(self) -> None:
        self.__ins_cursor.execute("COMMIT")

        project_path_file_name,file_type = os.path.splitext(self.__full_project_name)
        if file_type == ".p4st_temp":
            self.__ins_cursor.close()
            self.__ins_database.close()

            saved_full_project_name = ".".join([project_path_file_name,"p4st"])
            os.rename(self.__full_project_name,saved_full_project_name)
            self.__full_project_name = saved_full_project_name

            self.__ins_database = sqlite3.connect(self.__full_project_name,isolation_level=None)
            self.__ins_cursor = self.__ins_database.cursor()
        else:   pass
        
        self.__ins_cursor.execute("BEGIN")
    def closeProjectDatabase(self) -> None:
        self.__ins_cursor.close()
        self.__ins_database.close()
        
        if self.__full_project_name.split('.')[-1] == 'p4st_temp':
            os.remove(self.__full_project_name)
        else:   pass

        work_path = os.path.dirname(self.__full_project_name)
        for file_name in os.listdir(work_path):
            if file_name.endswith(".p4st_temp"):
                os.remove(os.sep.join([work_path,file_name]))
            elif file_name.endswith(".p4st_temp-journal"):
                os.remove(os.sep.join([work_path,file_name]))
            elif file_name.endswith(".p4st-journal"):
                os.remove(os.sep.join([work_path,file_name]))
            else:   continue
        
        self.__full_project_name = None
        self.__ins_database = None
        self.__ins_cursor = None
    
    def getModelInformation(self, in_model_name:str) -> dict:
        model_information_dict = {'part':{},'property':{'materials':[],'attributes':[]},'assembly':{'instances':[],'nodes groups':[],'elements groups':[],'coordinate systems':[]},
                                  'step':[],'output':[],'boundary condition':[],'other':{'functions':[]}}
        
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id,name FROM parts WHERE model=?',[model_id])
        parts_info_list = self.__ins_cursor.fetchall()
        for part_id,part_name in parts_info_list:
            part_info_dict = {'nodes groups':[],'elements groups':[],'coordinate systems':[],'property assignments':[],'orientation assignments':[]}
            
            self.__ins_cursor.execute('SELECT name,type FROM groups WHERE model=? AND sign=?', [model_id,part_id])
            for group_name, group_type in self.__ins_cursor.fetchall():
                if group_type == 1:
                    part_info_dict['nodes groups'].append(group_name)
                else:
                    part_info_dict['elements groups'].append(group_name)

            self.__ins_cursor.execute('SELECT name FROM coordinate_systems WHERE model=? AND source=?', [model_id,part_id])
            for coordinate_system_name in self.__ins_cursor.fetchall():
                part_info_dict['coordinate systems'].append(coordinate_system_name[0])

            self.__ins_cursor.execute('SELECT pgroup FROM property_assignments WHERE model=? AND part=?', [model_id,part_id])
            property_assignments_associated_groups_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
            for group_id in property_assignments_associated_groups_id_list:
                self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=? AND id=?',[model_id,part_id,group_id])
                part_info_dict['property assignments'].append(self.__ins_cursor.fetchone()[0])
            
            self.__ins_cursor.execute('SELECT pgroup FROM orientation_assignments WHERE model=? AND part=?', [model_id,part_id])
            orientation_assignments_associated_groups_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
            for group_id in orientation_assignments_associated_groups_id_list:
                self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=? AND id=?',[model_id,part_id,group_id])
                part_info_dict['orientation assignments'].append(self.__ins_cursor.fetchone()[0])
            
            model_information_dict['part'][part_name] = part_info_dict
        
        self.__ins_cursor.execute('SELECT name FROM materials WHERE model=?',[model_id])
        model_information_dict['property']['materials'] = [i[0] for i in self.__ins_cursor.fetchall()]
        
        self.__ins_cursor.execute('SELECT name FROM attributes WHERE model=?',[model_id])
        model_information_dict['property']['attributes'] = [i[0] for i in self.__ins_cursor.fetchall()]
        
        self.__ins_cursor.execute('SELECT name FROM assembly WHERE model=?',[model_id])
        model_information_dict['assembly']['instances'] = [i[0] for i in self.__ins_cursor.fetchall()]
        self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=0 AND type=1',[model_id])
        model_information_dict['assembly']['nodes groups'] = [i[0] for i in self.__ins_cursor.fetchall()]
        self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=0 AND type=2',[model_id])
        model_information_dict['assembly']['elements groups'] = [i[0] for i in self.__ins_cursor.fetchall()]
        self.__ins_cursor.execute('SELECT name FROM coordinate_systems WHERE model=? AND source=0',[model_id])
        model_information_dict['assembly']['coordinate systems'] = [i[0] for i in self.__ins_cursor.fetchall()]
        
        self.__ins_cursor.execute('SELECT name FROM steps WHERE model=?',[model_id])
        model_information_dict['step'] = [i[0] for i in self.__ins_cursor.fetchall()]
        
        self.__ins_cursor.execute('SELECT name FROM outputs WHERE model=?',[model_id])
        model_information_dict['output'] = [i[0] for i in self.__ins_cursor.fetchall()]
        
        self.__ins_cursor.execute('SELECT name FROM boundary_conditions WHERE model=?',[model_id])
        model_information_dict['boundary condition'] = [i[0] for i in self.__ins_cursor.fetchall()]
        
        self.__ins_cursor.execute('SELECT name FROM functions WHERE model=?',[model_id])
        model_information_dict['other']['functions'] = [i[0] for i in self.__ins_cursor.fetchall()]
        
        return model_information_dict
    def getModels(self) -> list:
        self.__ins_cursor.execute('SELECT name FROM models')
        return [i[0] for i in self.__ins_cursor.fetchall()]
    def getModelDimension(self,in_model_name:str) -> str:
        self.__ins_cursor.execute('SELECT dimension FROM models where name=?',[in_model_name])
        return self.__ins_cursor.fetchone()[0]
    
    def createModel(self, in_model_name:str, in_model_dimension:str) -> None:
        self.__ins_cursor.execute('INSERT INTO models(name,dimension) VALUES(?,?)',[in_model_name,in_model_dimension])
    def renameModel(self, in_model_name:str, in_new_model_name:str) -> None:
        self.__ins_cursor.execute('UPDATE models SET name=? WHERE name=?',[in_new_model_name,in_model_name])
    def importModelDataToProject(self, in_project_full_name:str, in_model_name:str) -> None:
        ins_project_database = sqlite3.connect(in_project_full_name,isolation_level=None)
        ins_cursor = ins_project_database.cursor()
        
        ins_cursor.execute('SELECT id,dimension FROM models WHERE name=?',[in_model_name])
        import_model_id,import_model_dimension = ins_cursor.fetchone()
        self.__ins_cursor.execute('INSERT INTO models(name,dimension) VALUES(?,?)',[in_model_name,import_model_dimension])
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        import_parts_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT id,name,nodes,elements FROM parts WHERE model=?',[import_model_id])
        import_model_include_parts_info_list = ins_cursor.fetchall()
        if import_model_include_parts_info_list is None:
            pass
        else:
            for import_part_info_list in import_model_include_parts_info_list:
                import_part_info_list = list(import_part_info_list)
                
                self.__ins_cursor.execute('INSERT INTO parts(model,name,nodes,elements) VALUES(?,?,?,?)',[model_id,*import_part_info_list[1:]])
                
                self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,import_part_info_list[1]])
                part_id = self.__ins_cursor.fetchone()[0]
                import_parts_id_to_new_id_dict[import_part_info_list[0]] = part_id
                
                part_nodes_table_name = 'part_'+str(part_id) + '_nodes'
                self.__ins_cursor.execute(f'CREATE TABLE {part_nodes_table_name}(id INTEGER PRIMARY KEY, x REAL NOT NULL, y REAL NOT NULL, z REAL DEFAULT 0.0, elements TEXT NOT NULL)')
                import_part_nodes_table_name = 'part_'+str(import_part_info_list[0]) + '_nodes'
                read_nodes_number = 0
                while True:
                    ins_cursor.execute(f'SELECT x,y,z,elements FROM {import_part_nodes_table_name} WHERE id>? AND id<=?',[read_nodes_number,read_nodes_number+5000])
                    self.__ins_cursor.executemany(f'INSERT INTO {part_nodes_table_name}(x,y,z,elements) VALUES(?,?,?,?)',ins_cursor.fetchall())
                    
                    if read_nodes_number+5000 >= import_part_info_list[2]:
                        break
                    else:
                        read_nodes_number += 5000
                
                part_elements_table_name = 'part_'+str(part_id) + '_elements'
                self.__ins_cursor.execute(f'CREATE TABLE {part_elements_table_name}(id INTEGER PRIMARY KEY, geometry INTEGER NOT NULL, nodes TEXT NOT NULL,\
                                                    ox REAL NOT NULL, oy REAL NOT NULL, oz REAL NOT NULL, ori1 REAL NOT NULL, ori2 REAL NOT NULL, ori3 REAL NOT NULL, ori4 REAL NOT NULL,\
                                                    property INTEGER, orientation INTEGER DEFAULT -1 NOT NULL)')
                import_part_elements_table_name = 'part_'+str(import_part_info_list[0]) + '_elements'
                read_elements_number = 0
                while True:
                    ins_cursor.execute(f'SELECT geometry,nodes,ox,oy,oz,ori1,ori2,ori3,ori4 FROM {import_part_elements_table_name} WHERE id>? AND id<=?',[read_elements_number,read_elements_number+5000])
                    self.__ins_cursor.executemany(f'INSERT INTO {part_elements_table_name}(geometry,nodes,ox,oy,oz,ori1,ori2,ori3,ori4) VALUES(?,?,?,?,?,?,?,?,?)',ins_cursor.fetchall())
                    
                    if read_elements_number+5000 >= import_part_info_list[3]:
                        break
                    else:
                        read_elements_number += 5000
        del import_model_include_parts_info_list

        import_part_groups_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT id,sign,name,type,number FROM groups WHERE model=? AND sign!=0',[import_model_id])
        import_model_include_part_groups_info_list = ins_cursor.fetchall()
        if import_model_include_part_groups_info_list is None:
            pass
        else:
            for import_part_group_info_list in import_model_include_part_groups_info_list:
                import_part_group_info_list = list(import_part_group_info_list)
                
                part_id = import_parts_id_to_new_id_dict[import_part_group_info_list[1]]
                
                self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,part_id,*import_part_group_info_list[2:]])
                
                self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=?',[model_id,part_id,*import_part_group_info_list[2:4]])
                part_group_id = self.__ins_cursor.fetchone()[0]
                import_part_groups_id_to_new_id_dict[import_part_group_info_list[0]] = part_group_id
                
                if import_part_group_info_list[3] == 1:
                    part_nodes_table_name = 'part_'+str(part_id) + '_nodes'
                    self.__ins_cursor.execute(f'ALTER TABLE {part_nodes_table_name} ADD COLUMN {"pg_"+str(part_group_id)} INTEGER')
                    
                    import_part_nodes_table_name = 'part_'+str(import_part_group_info_list[1]) + '_nodes'
                    ins_cursor.execute(f'SELECT id FROM {import_part_nodes_table_name} WHERE {"pg_"+str(import_part_group_info_list[0])}=1')
                    
                    self.__ins_cursor.executemany(f'UPDATE {part_nodes_table_name} SET {"pg_"+str(part_group_id)}=1 WHERE id=?',ins_cursor.fetchall())
                elif import_part_group_info_list[3] == 2:
                    part_elements_table_name = 'part_'+str(part_id) + '_elements'
                    self.__ins_cursor.execute(f'ALTER TABLE {part_elements_table_name} ADD COLUMN {"pg_"+str(part_group_id)} INTEGER')
                    
                    import_part_elements_table_name = 'part_'+str(import_part_group_info_list[1]) + '_elements'
                    ins_cursor.execute(f'SELECT id FROM {import_part_elements_table_name} WHERE {"pg_"+str(import_part_group_info_list[0])}=1')
                    
                    self.__ins_cursor.executemany(f'UPDATE {part_elements_table_name} SET {"pg_"+str(part_group_id)}=1 WHERE id=?',ins_cursor.fetchall())
                else:
                    pass
        del import_model_include_part_groups_info_list

        import_materials_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT id,name,elasticity,eparams FROM materials WHERE model=?',[import_model_id])
        import_model_include_materials_info_list = ins_cursor.fetchall()
        if import_model_include_materials_info_list is None:
            pass
        else:
            for import_material_info_list in import_model_include_materials_info_list:
                import_material_info_list = list(import_material_info_list)
                
                self.__ins_cursor.execute('INSERT INTO materials(model,name,elasticity,eparams) VALUES(?,?,?,?)',[model_id,*import_material_info_list[1:]])
                
                self.__ins_cursor.execute('SELECT id FROM materials WHERE model=? AND name=?',[model_id,import_material_info_list[1]])
                material_id = self.__ins_cursor.fetchone()[0]
                import_materials_id_to_new_id_dict[import_material_info_list[0]] = material_id
        del import_model_include_materials_info_list
        
        import_attributes_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT id,name,type,parameters FROM attributes WHERE model=?',[import_model_id])
        import_model_include_attributes_info_list = ins_cursor.fetchall()
        if import_model_include_attributes_info_list is None:
            pass
        else:
            for import_attribute_info_list in import_model_include_attributes_info_list:
                import_attribute_info_list = list(import_attribute_info_list)
                
                self.__ins_cursor.execute('INSERT INTO attributes(model,name,type,parameters) VALUES(?,?,?,?)',[model_id,*import_attribute_info_list[1:]])
                
                self.__ins_cursor.execute('SELECT id FROM attributes WHERE model=? AND name=?',[model_id,import_attribute_info_list[1]])
                attribute_id = self.__ins_cursor.fetchone()[0]
                import_attributes_id_to_new_id_dict[import_attribute_info_list[0]] = attribute_id
        del import_model_include_attributes_info_list
        
        ins_cursor.execute('SELECT * FROM property_assignments WHERE model=?',[import_model_id])
        import_model_include_property_assignments_info_list = ins_cursor.fetchall()
        if import_model_include_property_assignments_info_list is None:
            pass
        else:
            for import_property_assignment_info_list in import_model_include_property_assignments_info_list:
                import_property_assignment_info_list = list(import_property_assignment_info_list)
                
                part_id = import_parts_id_to_new_id_dict[import_property_assignment_info_list[2]]
                group_id = import_part_groups_id_to_new_id_dict[import_property_assignment_info_list[3]]
                
                for column_index in [4,7,10,13,16,19,22,25,28,31]:
                    if import_property_assignment_info_list[column_index] is None:
                        continue
                    else:
                        import_property_assignment_info_list[column_index] = import_attributes_id_to_new_id_dict[import_property_assignment_info_list[column_index]]
                for column_index in [5,8,11,14,17,20,23,26,29,32]:
                    if import_property_assignment_info_list[column_index] is None:
                        continue
                    else:
                        import_property_assignment_info_list[column_index] = import_materials_id_to_new_id_dict[import_property_assignment_info_list[column_index]]
                self.__ins_cursor.execute('INSERT INTO property_assignments(model,part,pgroup,geo1_attribute, geo1_material, geo1_etype,\
                                            geo2_attribute,geo2_material,geo2_etype,geo3_attribute,geo3_material,geo3_etype,geo4_attribute,geo4_material,geo4_etype,\
                                            geo5_attribute,geo5_material,geo5_etype,geo6_attribute,geo6_material,geo6_etype,geo7_attribute,geo7_material,geo7_etype,\
                                            geo8_attribute,geo8_material,geo8_etype,geo9_attribute,geo9_material,geo9_etype,geo10_attribute,geo10_material, geo10_etype)\
                                            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',[model_id,part_id,group_id,*import_property_assignment_info_list[4:]])
                
                self.__ins_cursor.execute('SELECT id FROM property_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
                property_assignment_id = self.__ins_cursor.fetchone()[0]
                self.__ins_cursor.execute(f'UPDATE {"part_"+str(part_id)+"_elements"} SET property=? WHERE {"pg_"+str(group_id)}=1',[property_assignment_id])
        del import_model_include_property_assignments_info_list
        
        import_part_coordinate_systems_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT id,name,source,type,ox,oy,oz,ori1,ori2,ori3,ori4 FROM coordinate_systems WHERE model=? AND source!=0',[import_model_id])
        import_model_include_part_coordinate_systems_info_list = ins_cursor.fetchall()
        if import_model_include_part_coordinate_systems_info_list is None:
            pass
        else:
            for import_part_coordinate_system_info_list in import_model_include_part_coordinate_systems_info_list:
                import_part_coordinate_system_info_list = list(import_part_coordinate_system_info_list)
                
                part_id = import_parts_id_to_new_id_dict[import_part_coordinate_system_info_list[2]]
                
                self.__ins_cursor.execute('INSERT INTO coordinate_systems(model,name,source,type,ox,oy,oz,ori1,ori2,ori3,ori4) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                                          [model_id,import_part_coordinate_system_info_list[1],part_id,*import_part_coordinate_system_info_list[3:]])
                
                self.__ins_cursor.execute('SELECT id FROM coordinate_systems WHERE model=? AND source=? AND name=?',[model_id,part_id,import_part_coordinate_system_info_list[1]])
                coordinate_system_id = self.__ins_cursor.fetchone()[0]                
                import_part_coordinate_systems_id_to_new_id_dict[import_part_coordinate_system_info_list[0]] = coordinate_system_id
        del import_model_include_part_coordinate_systems_info_list
        
        ins_cursor.execute('SELECT id,part,pgroup,reference,raxis,angle FROM orientation_assignments WHERE model=?',[import_model_id])
        import_model_include_orientation_assignments_info_list = ins_cursor.fetchall()
        if import_model_include_orientation_assignments_info_list is None:
            pass
        else:
            for import_orientation_assignment_info_list in import_model_include_orientation_assignments_info_list:
                import_orientation_assignment_info_list = list(import_orientation_assignment_info_list)
                
                part_id = import_parts_id_to_new_id_dict[import_orientation_assignment_info_list[1]]
                group_id = import_part_groups_id_to_new_id_dict[import_orientation_assignment_info_list[2]]
                if import_orientation_assignment_info_list[3] == 0:
                    ref_csys_id = 0
                else:
                    ref_csys_id = import_part_coordinate_systems_id_to_new_id_dict[import_orientation_assignment_info_list[3]]
                
                self.__ins_cursor.execute('INSERT INTO orientation_assignments(model,part,pgroup,reference,raxis,angle) VALUES(?,?,?,?,?,?)',[model_id,part_id,group_id,ref_csys_id,*import_orientation_assignment_info_list[4:]])
                
                self.__ins_cursor.execute('SELECT id FROM orientation_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
                orientation_assignment_id = self.__ins_cursor.fetchone()[0]
                self.__ins_cursor.execute(f'UPDATE {"part_"+str(part_id)+"_elements"} SET orientation=? WHERE {"pg_"+str(group_id)}=1',[orientation_assignment_id])
        del import_model_include_orientation_assignments_info_list
        
        import_instances_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT * FROM assembly WHERE model=?',[import_model_id])
        import_model_include_instances_info_list = ins_cursor.fetchall()
        if import_model_include_instances_info_list is None:
            pass
        else:
            for import_instance_info_list in import_model_include_instances_info_list:
                import_instance_info_list = list(import_instance_info_list)
                
                part_id = import_parts_id_to_new_id_dict[import_instance_info_list[1]]
                self.__ins_cursor.execute('INSERT INTO assembly(model,part,name,ox,oy,oz,ori1,ori2,ori3,ori4) VALUES(?,?,?,?,?,?,?,?,?,?)',[model_id,part_id,import_instance_info_list[3],*import_instance_info_list[4:]])
                
                self.__ins_cursor.execute('SELECT id FROM assembly WHERE model=? AND part=? AND name=?',[model_id,part_id,import_instance_info_list[3]])
                instance_id = self.__ins_cursor.fetchone()[0]
                import_instances_id_to_new_id_dict[import_instance_info_list[2]] = instance_id
        del import_model_include_instances_info_list
        
        import_assembly_groups_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT id,sign,name,type,number FROM groups WHERE model=? AND sign=0',[import_model_id])
        import_model_include_assembly_groups_info_list = ins_cursor.fetchall()
        if import_model_include_assembly_groups_info_list is None:
            pass
        else:
            for import_assembly_group_info_list in import_model_include_assembly_groups_info_list:
                import_assembly_group_info_list = list(import_assembly_group_info_list)
                
                self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,0,?,?,?)',[model_id,*import_assembly_group_info_list[2:]])
                
                self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=0 AND name=? AND type=?',[model_id,*import_assembly_group_info_list[2:4]])
                assembly_group_id = self.__ins_cursor.fetchone()[0]
                import_assembly_groups_id_to_new_id_dict[import_assembly_group_info_list[0]] = assembly_group_id
        del import_model_include_assembly_groups_info_list
        
        ins_cursor.execute('SELECT agroup,instance FROM groups_instances_association WHERE model=?',[import_model_id])
        import_model_include_groups_instances_association_info_list = ins_cursor.fetchall()
        if import_model_include_groups_instances_association_info_list is None:
            pass
        else:
            for import_group_insrance_association_info_list in import_model_include_groups_instances_association_info_list:
                import_group_insrance_association_info_list = list(import_group_insrance_association_info_list)
                
                assembly_group_id = import_assembly_groups_id_to_new_id_dict[import_group_insrance_association_info_list[0]]
                instance_id = import_instances_id_to_new_id_dict[import_group_insrance_association_info_list[1]]
                
                self.__ins_cursor.execute('INSERT INTO groups_instances_association(model,agroup,instance) VALUES(?,?,?)',[model_id,assembly_group_id,instance_id])
                
                self.__ins_cursor.execute('SELECT part FROM assembly WHERE model=? AND id=?',[model_id,instance_id])
                part_id = self.__ins_cursor.fetchone()[0]
                
                self.__ins_cursor.execute('SELECT type FROM groups WHERE model=? AND sign=0 AND id=?',[model_id,assembly_group_id])
                agroup_type_number = self.__ins_cursor.fetchone()[0]
                if agroup_type_number == 1:
                    part_nodes_table_name = 'part_'+str(part_id) + '_nodes'
                    self.__ins_cursor.execute(f'ALTER TABLE {part_nodes_table_name} ADD COLUMN {"ag_"+str(instance_id)+"_"+str(assembly_group_id)} INTEGER')
                    
                    ins_cursor.execute('SELECT part FROM assembly WHERE model=? AND id=?',[import_model_id,import_group_insrance_association_info_list[1]])
                    improt_part_id = ins_cursor.fetchone()[0]
                    import_part_nodes_table_name = 'part_'+str(improt_part_id) + '_nodes'
                    ins_cursor.execute(f'SELECT id FROM {import_part_nodes_table_name} WHERE {"ag_"+str(import_group_insrance_association_info_list[1])+"_"+str(import_group_insrance_association_info_list[0])}=1')
                    
                    self.__ins_cursor.executemany(f'UPDATE {part_nodes_table_name} SET {"ag_"+str(instance_id)+"_"+str(assembly_group_id)}=1 WHERE id=?',ins_cursor.fetchall())
                elif agroup_type_number == 2:
                    part_elements_table_name = 'part_'+str(part_id) + '_elements'
                    self.__ins_cursor.execute(f'ALTER TABLE {part_elements_table_name} ADD COLUMN {"ag_"+str(instance_id)+"_"+str(assembly_group_id)} INTEGER')
                    
                    ins_cursor.execute('SELECT part FROM assembly WHERE model=? AND id=?',[import_model_id,import_group_insrance_association_info_list[1]])
                    improt_part_id = ins_cursor.fetchone()[0]
                    import_part_elements_table_name = 'part_'+str(improt_part_id) + '_elements'
                    ins_cursor.execute(f'SELECT id FROM {import_part_elements_table_name} WHERE {"ag_"+str(import_group_insrance_association_info_list[1])+"_"+str(import_group_insrance_association_info_list[0])}=1')
                    
                    self.__ins_cursor.executemany(f'UPDATE {part_elements_table_name} SET {"ag_"+str(instance_id)+"_"+str(assembly_group_id)}=1 WHERE id=?',ins_cursor.fetchall())
                else:
                    pass
        del import_model_include_groups_instances_association_info_list
        
        import_assembly_coordinate_systems_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT id,name,source,type,ox,oy,oz,ori1,ori2,ori3,ori4 FROM coordinate_systems WHERE model=? AND source=0',[import_model_id])
        import_model_include_assembly_coordinate_systems_info_list = ins_cursor.fetchall()
        if import_model_include_assembly_coordinate_systems_info_list is None:
            pass
        else:
            for import_assembly_coordinate_system_info_list in import_model_include_assembly_coordinate_systems_info_list:
                import_assembly_coordinate_system_info_list = list(import_assembly_coordinate_system_info_list)
                
                self.__ins_cursor.execute('INSERT INTO coordinate_systems(model,name,source,type,ox,oy,oz,ori1,ori2,ori3,ori4) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                                          [model_id,import_assembly_coordinate_system_info_list[1],0,*import_assembly_coordinate_system_info_list[3:]])
                
                self.__ins_cursor.execute('SELECT id FROM coordinate_systems WHERE model=? AND source=0 AND name=?',[model_id,import_assembly_coordinate_system_info_list[1]])
                coordinate_system_id = self.__ins_cursor.fetchone()[0]                
                import_assembly_coordinate_systems_id_to_new_id_dict[import_assembly_coordinate_system_info_list[0]] = coordinate_system_id
        del import_model_include_assembly_coordinate_systems_info_list

        import_steps_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT * FROM steps WHERE model=?',[import_model_id])
        import_model_include_steps_info_list = ins_cursor.fetchall()
        if import_model_include_steps_info_list is None:
            pass
        else:
            for import_step_info_list in import_model_include_steps_info_list:
                import_step_info_list = list(import_step_info_list)
                
                self.__ins_cursor.execute('INSERT INTO steps(model,name,type,sequence,time,nlgeom,basic,lsolver) VALUES(?,?,?,?,?,?,?,?)',[model_id,*import_step_info_list[2:]])
        
                self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND name=?',[model_id,import_step_info_list[2]])
                step_id  = self.__ins_cursor.fetchone()[0]
                import_steps_id_to_new_id_dict[import_step_info_list[1]] = step_id
        for import_step_id,step_id in import_steps_id_to_new_id_dict.items():
            self.__ins_cursor.execute(f'ALTER TABLE boundary_conditions ADD COLUMN {"step_"+str(step_id)} INTEGER')
        del import_model_include_steps_info_list
        
        ins_cursor.execute('SELECT * FROM outputs WHERE model=?',[import_model_id])
        import_model_include_outputs_info_list = ins_cursor.fetchall()
        if import_model_include_outputs_info_list is None:
            pass
        else:
            for import_output_info_list in import_model_include_outputs_info_list:
                import_output_info_list = list(import_output_info_list)
                
                bsetp_id = import_steps_id_to_new_id_dict[import_output_info_list[4]]
                esetp_id = import_steps_id_to_new_id_dict[import_output_info_list[5]]
                assembly_group_id = import_assembly_groups_id_to_new_id_dict[import_output_info_list[8]]
                
                self.__ins_cursor.execute('INSERT INTO outputs(model,name,type,bstep,estep,reference,frequency,agroup,variables) VALUES(?,?,?,?,?,?,?,?,?)',
                                            [model_id,*import_output_info_list[2:4],bsetp_id,esetp_id,*import_output_info_list[6:8],assembly_group_id,import_output_info_list[9]])
        del import_model_include_outputs_info_list
        
        import_functions_id_to_new_id_dict = {}
        ins_cursor.execute('SELECT * FROM functions WHERE model=?',[import_model_id])
        import_model_include_functions_info_list = ins_cursor.fetchall()
        if import_model_include_functions_info_list is None:
            pass
        else:
            for import_function_info_list in import_model_include_functions_info_list:
                import_function_info_list = list(import_function_info_list)
                
                self.__ins_cursor.execute('INSERT INTO functions(model,name,type,parameters) VALUES(?,?,?,?)',[model_id,*import_function_info_list[2:]])
        
                self.__ins_cursor.execute('SELECT id FROM functions WHERE model=? AND name=?',[model_id,import_function_info_list[2]])
                function_id = self.__ins_cursor.fetchone()[0]
                import_functions_id_to_new_id_dict[import_function_info_list[1]] = function_id
        del import_model_include_functions_info_list
        
        ins_cursor.execute('SELECT * FROM boundary_conditions WHERE model=?',[import_model_id])
        import_model_include_conditions_info_list = ins_cursor.fetchall()
        if import_model_include_conditions_info_list is None:
            pass
        else:
            for import_condition_info_list in import_model_include_conditions_info_list:
                import_condition_info_list = list(import_condition_info_list)
                
                if import_condition_info_list[5] == 0:
                    pass
                else:
                    import_condition_info_list[5] = import_assembly_coordinate_system_info_list[import_condition_info_list[5]]
                
                self.__ins_cursor.execute('INSERT INTO boundary_conditions(model,name,type,agroup,csys,definition,initial) VALUES(?,?,?,?,?,?,?)',[model_id,*import_condition_info_list[2:8]])
                
                for import_step_id,step_id in import_steps_id_to_new_id_dict.items():
                    ins_cursor.execute(f'SELECT {"step_"+str(import_step_id)} FROM boundary_conditions WHERE model=? AND name=?',[model_id,import_condition_info_list[2]])
                    step_components_string_list  = ins_cursor.fetchone()[0].split(',')
                    if step_components_string_list[-1] == 'None':
                        pass
                    else:
                        step_components_string_list[-1] = str(import_functions_id_to_new_id_dict[int(step_components_string_list[-1])])

                    self.__ins_cursor.execute(f'UPDATE boundary_conditions SET {"step_"+str(step_id)}=? WHERE model=? AND name=?',[','.join(step_components_string_list),model_id,import_condition_info_list[2]])
        del import_model_include_conditions_info_list
        
        ins_cursor.close()
        ins_project_database.close()
    def removeModel(self, in_model_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('DELETE FROM models WHERE id=?',[model_id])
        
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=?',[model_id])
        for i in self.__ins_cursor.fetchall():
            self.__ins_cursor.execute(f'DROP TABLE {"part_"+str(i[0])+"_nodes"}')
            self.__ins_cursor.execute(f'DROP TABLE {"part_"+str(i[0])+"_elements"}')
        self.__ins_cursor.execute('DELETE FROM parts WHERE model=?',[model_id])
        
        self.__ins_cursor.execute('DELETE FROM groups WHERE model=?',[model_id])
        self.__ins_cursor.execute('DELETE FROM property_assignments WHERE model=?',[model_id])
        self.__ins_cursor.execute('DELETE FROM coordinate_systems WHERE model=?',[model_id])
        self.__ins_cursor.execute('DELETE FROM orientation_assignments WHERE model=?',[model_id])
        
        self.__ins_cursor.execute('DELETE FROM assembly WHERE model=?',[model_id])
        self.__ins_cursor.execute('DELETE FROM groups_instances_association WHERE model=?',[model_id])
        self.__ins_cursor.execute('DELETE FROM steps WHERE model=?',[model_id])
        self.__ins_cursor.execute('DELETE FROM outputs WHERE model=?',[model_id])
        self.__ins_cursor.execute('DELETE FROM boundary_conditions WHERE model=?',[model_id])
        self.__ins_cursor.execute('DELETE FROM functions WHERE model=?',[model_id])

    def outpuFEMTaskFile(self, in_model_name:str, in_task_full_name:str) -> None:
        self.__ins_cursor.execute('SELECT id,dimension FROM models WHERE name=?',[in_model_name])
        model_id,model_dimension = self.__ins_cursor.fetchone()
        
        with h5py.File(in_task_full_name,'w') as ins_task_file:
            ins_task_basic_set = ins_task_file.create_dataset(name='basic',shape=(2,),dtype=h5py.string_dtype(encoding='utf-8'))
            ins_task_basic_set[0] = model_dimension
            ins_task_basic_set[1] = 'FEM'
            
            ins_mesh_group = ins_task_file.create_group(name='Mesh')
            # region
            parts_info_dict = {}
            self.__ins_cursor.execute('SELECT id,name,nodes,elements FROM parts WHERE model=?',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                return None
            else:
                parts_info_dict = {i[0]:[i[1],i[2],i[3]] for i in get_info_list}
            
            property_assignments_info_dict = {}
            self.__ins_cursor.execute('SELECT * FROM property_assignments WHERE model=?',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                pass
            else:
                property_assignments_info_dict = {i[0]:{1:[i[4],i[5],i[6]],2:[i[7],i[8],i[9]],3:[i[10],i[11],i[12]],
                                                    4:[i[13],i[14],i[15]],5:[i[16],i[17],i[18]],6:[i[19],i[20],i[21]],
                                                    7:[i[22],i[23],i[24]],8:[i[25],i[26],i[27]],9:[i[28],i[29],i[30]],
                                                    10:[i[31],i[32],i[33]]} for i in get_info_list}
            
            orientation_assignments_info_dict = {}
            self.__ins_cursor.execute('SELECT id,part,pgroup FROM orientation_assignments WHERE model=?',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                pass
            else:
                orientation_assignments_info_dict = {i[0]:[i[1],i[2]] for i in get_info_list}
            
            instances_info_dict = {}
            self.__ins_cursor.execute('SELECT id,part,name,ox,oy,oz,ori1,ori2,ori3,ori4 FROM assembly WHERE model=?',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                return None
            else:
                instances_info_dict = {i[0]:[i[1],i[2],[i[3],i[4],i[5]],[i[6],i[7],i[8],i[9]]] for i in get_info_list}
            
            all_nodes_number = sum([parts_info_dict[i[0]][1] for i in instances_info_dict.values()])
            all_elements_number = sum([parts_info_dict[i[0]][2] for i in instances_info_dict.values()])
            
            ins_nodes_set = ins_mesh_group.create_dataset(name='nodes',shape=(all_nodes_number,3),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            ins_association_set = ins_mesh_group.create_dataset(name='association',shape=(all_nodes_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
            ins_elements_set = ins_mesh_group.create_dataset(name='elements',shape=(all_elements_number,),dtype=h5py.vlen_dtype(common.P4SFormat.NUMERICAL_PRECISION['int']))
            ins_geometry_set = ins_mesh_group.create_dataset(name='geometry',shape=(all_elements_number,),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
            ins_materials_set = ins_mesh_group.create_dataset(name='materials',shape=(all_elements_number,),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
            ins_attributs_set = ins_mesh_group.create_dataset(name='attributes',shape=(all_elements_number,),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
            ins_type_set = ins_mesh_group.create_dataset(name='type',shape=(all_elements_number,),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
            ins_orientation_set = ins_mesh_group.create_dataset(name='orientation',shape=(all_elements_number,4),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            
            start_node_index, start_element_index = 0,0
            instance_start_index = {}
            ins_instances_group =ins_mesh_group.create_group(name='Instances')
            for instance_id,instance_info_list in instances_info_dict.items():
                instance_start_index[instance_id] = [start_node_index,start_element_index]
                
                ins_instance_transformer = vtk.vtkTransform()
                ins_instance_transformer.Translate(instance_info_list[2])
                ins_instance_transformer.RotateWXYZ(*instance_info_list[3])
                self.__ins_cursor.execute(f'SELECT x,y,z,elements FROM {"part_"+str(instance_info_list[0])+"_nodes"} ORDER BY id ASC')
                for node_index,node_info_list in enumerate(self.__ins_cursor.fetchall()):
                    ins_nodes_set[start_node_index+node_index] = ins_instance_transformer.TransformPoint(node_info_list[0:3])
                    ins_association_set[start_node_index+node_index] = start_element_index + numpy.asarray([int(i) for i in node_info_list[3].split(',')])
                del ins_instance_transformer
                
                self.__ins_cursor.execute(f'SELECT geometry,nodes FROM {"part_"+str(instance_info_list[0])+"_elements"} ORDER BY id ASC')
                for elements_index,element_info_list in enumerate(self.__ins_cursor.fetchall()):
                    ins_elements_set[start_element_index+elements_index] = start_node_index + numpy.asarray([int(i) for i in element_info_list[1].split(',')])
                    ins_geometry_set[start_element_index+elements_index] = element_info_list[0]
            
                for property_id, property_info_dict in property_assignments_info_dict.items():
                    self.__ins_cursor.execute(f'SELECT id,geometry FROM {"part_"+str(instance_info_list[0])+"_elements"} WHERE property=?',[property_id])
                    for element_label,geometry_number in self.__ins_cursor.fetchall():
                        ins_attributs_set[start_element_index+element_label-1] = property_info_dict[geometry_number][0]
                        ins_materials_set[start_element_index+element_label-1] = property_info_dict[geometry_number][1]
                        ins_type_set[start_element_index+element_label-1] = property_info_dict[geometry_number][2]
                
                self.__ins_cursor.execute(f'SELECT id,ori1,ori2,ori3,ori4 FROM {"part_"+str(instance_info_list[0])+"_elements"} WHERE orientation=-1')
                for element_label,ori1,ori2,ori3,ori4 in self.__ins_cursor.fetchall():
                    ins_orientation_set[start_element_index+element_label-1] = numpy.array([ori1,ori2,ori3,ori4])
                for part_id,pgroup_id in orientation_assignments_info_dict.values():
                    self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=? AND id=? AND type=2',[model_id,part_id,pgroup_id])
                    pgroup_name = self.__ins_cursor.fetchone()[0]
                    
                    elements_orientation_dict = self.getPartElementsOrientationParameters(in_model_name,parts_info_dict[part_id][0],pgroup_name)
                    for element_label, element_orientation_info_list in elements_orientation_dict.items():
                        ins_orientation_set[start_element_index+element_label-1] = numpy.array(element_orientation_info_list[3:])

                ins_instance_info_set = ins_instances_group.create_dataset(name=instances_info_dict[instance_id][1],shape=(4,),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])
                ins_instance_info_set[0] = start_node_index+1
                ins_instance_info_set[2] = start_element_index+1

                start_node_index += parts_info_dict[instance_info_list[0]][1]
                start_element_index += parts_info_dict[instance_info_list[0]][2]
                
                ins_instance_info_set[1] = start_node_index
                ins_instance_info_set[3] = start_element_index
            
            ins_groups_group = ins_mesh_group.create_group(name='Groups')
            
            ins_nodes_groups_group = ins_groups_group.create_group('Nodes')
            assembly_nodes_groups_info_dict = {}
            self.__ins_cursor.execute('SELECT id,name,number FROM groups WHERE model=?AND sign=0 AND type=1',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                pass
            else:
                assembly_nodes_groups_info_dict = {i[0]:[i[1],i[2]] for i in get_info_list}
            for agroup_id,agroup_info_list in assembly_nodes_groups_info_dict.items():
                ins_nodes_groups_set = ins_nodes_groups_group.create_dataset(name=agroup_info_list[0],shape=(agroup_info_list[1],),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])

                self.__ins_cursor.execute('SELECT instance FROM groups_instances_association WHERE model=? AND agroup=?',[model_id,agroup_id])
                agroup_include_instances_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
                agroup_node_index = 0
                for instance_id in agroup_include_instances_id_list:
                    part_id = instances_info_dict[instance_id][0]
                    self.__ins_cursor.execute(f'SELECT id FROM {"part_"+str(part_id)+"_nodes"} WHERE {"ag_"+str(instance_id)+"_"+str(agroup_id)}=1')
                    for node_label in self.__ins_cursor.fetchall():
                        ins_nodes_groups_set[agroup_node_index] = instance_start_index[instance_id][0] + node_label[0]
                        agroup_node_index += 1

                ins_nodes_groups_set[:] = numpy.sort(ins_nodes_groups_set[:])
              
            ins_elements_groups_group = ins_groups_group.create_group('Elements')
            assembly_elements_groups_info_dict = {}
            self.__ins_cursor.execute('SELECT id,name,number FROM groups WHERE model=?AND sign=0 AND type=2',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                pass
            else:
                assembly_elements_groups_info_dict = {i[0]:[i[1],i[2]] for i in get_info_list}
            for agroup_id,agroup_info_list in assembly_elements_groups_info_dict.items():
                ins_elements_groups_set = ins_elements_groups_group.create_dataset(name=agroup_info_list[0],shape=(agroup_info_list[1],),dtype=common.P4SFormat.NUMERICAL_PRECISION['int'])

                self.__ins_cursor.execute('SELECT instance FROM groups_instances_association WHERE model=? AND agroup=?',[model_id,agroup_id])
                agroup_include_instances_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
                agroup_element_index = 0
                for instance_id in agroup_include_instances_id_list:
                    part_id = instances_info_dict[instance_id][0]
                    self.__ins_cursor.execute(f'SELECT id FROM {"part_"+str(part_id)+"_elements"} WHERE {"ag_"+str(instance_id)+"_"+str(agroup_id)}=1')
                    for element_label in self.__ins_cursor.fetchall():
                        ins_elements_groups_set[agroup_element_index] = instance_start_index[instance_id][1] + element_label[0]
                        agroup_element_index += 1
                
                ins_elements_groups_set[:] = numpy.sort(ins_elements_groups_set[:])
            # endregion
            
            ins_property_group = ins_task_file.create_group(name='Property')
            # region
            assigned_attributes_id_list = []
            assigned_materials_id_list = []
            for property_assignment_info_dict in property_assignments_info_dict.values():
                for property_assignment_info_list in property_assignment_info_dict.values():
                    if property_assignment_info_list[0] is None:
                        continue
                    elif property_assignment_info_list[1] is None:
                        continue
                    else:
                        pass
                    
                    assigned_attributes_id_list.append(property_assignment_info_list[0])
                    assigned_materials_id_list.append(property_assignment_info_list[1])
            
            ins_materials_group = ins_property_group.create_group(name='Materials')
            for material_id in set(assigned_materials_id_list):
                self.__ins_cursor.execute('SELECT elasticity,eparams FROM materials WHERE model=? AND id=?',[model_id,material_id])
                elasticity_number,eparams_string = self.__ins_cursor.fetchone()
                
                if elasticity_number == 1:
                    constitutive_model_parameters_list = [float(i) for i in eparams_string.split(',')]
                    ins_materials_group.create_dataset(name=str(material_id),data=numpy.array([elasticity_number,*constitutive_model_parameters_list]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                else:
                    pass
            
            ins_attributes_group = ins_property_group.create_group(name='Attributes')
            for attribute_id in set(assigned_attributes_id_list):
                self.__ins_cursor.execute('SELECT type,parameters FROM attributes WHERE model=? AND id=?',[model_id,attribute_id])
                attribute_number,section_paramters_string = self.__ins_cursor.fetchone()
                
                if attribute_number in [1,3]:
                    section_paramter = float(section_paramters_string)
                    ins_attributes_group.create_dataset(name=str(attribute_id),data=numpy.array([attribute_number,section_paramter]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                elif attribute_number == 4:
                    section_paramters_list = [float(i) for i in section_paramters_string.split(',')]
                    ins_attributes_group.create_dataset(name=str(attribute_id),data=numpy.array([attribute_number,*section_paramters_list]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                elif attribute_number == 5:
                    section_paramters_list = [attribute_number]
                    for i in section_paramters_string.split(';'):
                        for j in i.split(','):
                            section_paramters_list.appene(float(j))
                    
                    ins_attributes_group.create_dataset(name=str(attribute_id),data=numpy.asarray(section_paramters_list),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                elif attribute_number == 6:
                    ins_attributes_group.create_dataset(name=str(attribute_id),data=numpy.array([attribute_number]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                else:
                    pass
            # endregion
            
            steps_info_dict = {}
            ins_steps_group = ins_task_file.create_group(name='Steps')
            # region
            self.__ins_cursor.execute('SELECT id,name,type,sequence,time,nlgeom,basic,lsolver FROM steps WHERE model=?',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                return None
            else:
                for step_id,name,type,sequence,time,nlgeom,basic,lsolver in get_info_list:
                    ins_step_group = ins_steps_group.create_group(name=name)
                    
                    steps_info_dict[step_id] = sequence
                    
                    ins_step_group.create_dataset(name='basic',data=numpy.array([sequence,type,time,nlgeom]),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
                    
                    step_parameters = [float(i) for i in basic.split(',')]
                    step_parameters.extend([float(i) for i in lsolver.split(',')])
                    ins_step_group.create_dataset(name='parameters',data=numpy.asarray(step_parameters),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            # endregion
            
            ins_outputs_group = ins_task_file.create_group(name='Outputs')
            # region
            ins_nodes_outputs_group = ins_outputs_group.create_group(name='Nodes')
            nodes_output_dict = {}
            self.__ins_cursor.execute('SELECT bstep,estep,reference,frequency,agroup,variables FROM outputs WHERE model=? AND type=1',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                return None
            else:
                for bstep,estep,reference,frequency,agroup,variables in get_info_list:
                    for variable_name in variables.split(','):
                        if variable_name in nodes_output_dict:
                            pass
                        else:
                            nodes_output_dict[variable_name] = {}
                        
                        begin_step_sequence = steps_info_dict[bstep]
                        end_step_sequence = steps_info_dict[estep]
                        group_name = assembly_nodes_groups_info_dict[agroup][0]
                        for step_sequence in range(begin_step_sequence,end_step_sequence+1,1):
                            if step_sequence in nodes_output_dict[variable_name]:
                                group_index = -1
                                for output_group_index in range(len(nodes_output_dict[variable_name][step_sequence])):
                                    if group_name == nodes_output_dict[variable_name][step_sequence][group_index][0]:
                                        group_index = output_group_index
                                        break
                                    else:
                                        continue
                                
                                if group_index == -1:
                                    if reference == 1:
                                        nodes_output_dict[variable_name][step_sequence].append([group_name,[],[-1]])
                                    elif reference == 2:
                                        nodes_output_dict[variable_name][step_sequence].append([group_name,[int(frequency)],[]])
                                    elif reference == 3:
                                        nodes_output_dict[variable_name][step_sequence].append([group_name,[],[frequency]])
                                    else:
                                        pass
                                else:
                                    if reference == 1:
                                        nodes_output_dict[variable_name][step_sequence][group_index][2].append(-1)
                                    elif reference == 2:
                                        nodes_output_dict[variable_name][step_sequence][group_index][1].append(int(frequency))
                                    elif reference == 3:
                                        nodes_output_dict[variable_name][step_sequence][group_index][2].append(frequency)
                                    else:
                                        pass
                            else:
                                nodes_output_dict[variable_name][step_sequence] = []

                                if reference == 1:
                                    nodes_output_dict[variable_name][step_sequence].append([group_name,[],[-1]])
                                elif reference == 2:
                                    nodes_output_dict[variable_name][step_sequence].append([group_name,[int(frequency)],[]])
                                elif reference == 3:
                                    nodes_output_dict[variable_name][step_sequence].append([group_name,[],[frequency]])
                                else:
                                    pass
            for variable_name in nodes_output_dict:
                ins_output_variable_group = ins_nodes_outputs_group.create_group(name=variable_name)
                for step_sequence in nodes_output_dict[variable_name]:
                    ins_output_variable_step_set = ins_output_variable_group.create_dataset(name=str(step_sequence),shape=(len(nodes_output_dict[variable_name][step_sequence]),3),dtype=h5py.string_dtype(encoding='utf-8'))
                    
                    for group_index,output_parameters_list in enumerate(nodes_output_dict[variable_name][step_sequence]):
                        ins_output_variable_step_set[group_index,0] = output_parameters_list[0]
                        
                        increments_intervals_list = list(set(output_parameters_list[1]))
                        increments_intervals_list.sort()
                        ins_output_variable_step_set[group_index,1] = ','.join([str(i) for i in increments_intervals_list])
                        
                        time_intervals_list = list(set(output_parameters_list[2]))
                        time_intervals_list.sort()
                        ins_output_variable_step_set[group_index,2] = ','.join([str(i) for i in time_intervals_list])
            
            ins_elements_outputs_group = ins_outputs_group.create_group(name='Elements')
            elements_output_dict = {}
            self.__ins_cursor.execute('SELECT bstep,estep,reference,frequency,agroup,variables FROM outputs WHERE model=? AND type=2',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                pass
            else:
                for bstep,estep,reference,frequency,agroup,variables in get_info_list:
                    for variable_name in variables.split(','):
                        if variable_name in elements_output_dict:
                            pass
                        else:
                            elements_output_dict[variable_name] = {}

                        begin_step_sequence = steps_info_dict[bstep]
                        end_step_sequence = steps_info_dict[estep]
                        group_name = assembly_elements_groups_info_dict[agroup][0]
                        for step_sequence in range(begin_step_sequence,end_step_sequence+1,1):
                            if step_sequence in elements_output_dict[variable_name]:
                                group_index = -1
                                for output_group_index in range(len(elements_output_dict[variable_name][step_sequence])):
                                    if group_name == elements_output_dict[variable_name][step_sequence][group_index][0]:
                                        group_index = output_group_index
                                        break
                                    else:
                                        continue
                                
                                if group_index == -1:
                                    if reference == 1:
                                        elements_output_dict[variable_name][step_sequence].append([group_name,[],[-1]])
                                    elif reference == 2:
                                        elements_output_dict[variable_name][step_sequence].append([group_name,[int(frequency)],[]])
                                    elif reference == 3:
                                        elements_output_dict[variable_name][step_sequence].append([group_name,[],[frequency]])
                                    else:
                                        pass
                                else:
                                    if reference == 1:
                                        elements_output_dict[variable_name][step_sequence][group_index][2].append(-1)
                                    elif reference == 2:
                                        elements_output_dict[variable_name][step_sequence][group_index][1].append(int(frequency))
                                    elif reference == 3:
                                        elements_output_dict[variable_name][step_sequence][group_index][2].append(frequency)
                                    else:
                                        pass
                            else:
                                elements_output_dict[variable_name][step_sequence] = []

                                if reference == 1:
                                    elements_output_dict[variable_name][step_sequence].append([group_name,[],[-1]])
                                elif reference == 2:
                                    elements_output_dict[variable_name][step_sequence].append([group_name,[frequency],[]])
                                elif reference == 3:
                                    elements_output_dict[variable_name][step_sequence].append([group_name,[],[frequency]])
                                else:
                                    pass
            for variable_name in elements_output_dict:
                ins_output_variable_group = ins_elements_outputs_group.create_group(name=variable_name)
                for step_sequence in elements_output_dict[variable_name]:
                    ins_output_variable_step_set = ins_output_variable_group.create_dataset(name=str(step_sequence),shape=(len(elements_output_dict[variable_name][step_sequence]),3),dtype=h5py.string_dtype(encoding='utf-8'))
                    
                    for group_index,output_parameters_list in enumerate(elements_output_dict[variable_name][step_sequence]):
                        ins_output_variable_step_set[group_index,0] = output_parameters_list[0]
                        
                        increments_intervals_list = list(set(output_parameters_list[1]))
                        increments_intervals_list.sort()
                        ins_output_variable_step_set[group_index,1] = ','.join([str(i) for i in increments_intervals_list])
                        
                        time_intervals_list = list(set(output_parameters_list[2]))
                        time_intervals_list.sort()
                        ins_output_variable_step_set[group_index,2] = ','.join([str(i) for i in time_intervals_list])
            # endregion
            
            ins_conditions_group = ins_task_file.create_group(name='Conditions')
            # region
            conditoins_info_dict = {'displacement':[],'concentrated force':[],'moment':[]}
            include_functions_id_list = []
            steps_column_string = ''
            for step_id in steps_info_dict:
                steps_column_string += f',step_{str(step_id)}'
            self.__ins_cursor.execute(f'SELECT type,agroup,csys,initial{steps_column_string} FROM boundary_conditions WHERE model=?',[model_id])
            get_info_list = self.__ins_cursor.fetchall()
            if get_info_list is None:
                return None
            else:
                for type,agroup_id,csys_id,initial,*steps_parameters_string_list in get_info_list:
                    if type == 1:
                        conditoins_info_dict['displacement'].append([agroup_id,csys_id,initial,*steps_parameters_string_list])
                    elif type == 2:
                        conditoins_info_dict['concentrated force'].append([agroup_id,csys_id,initial,*steps_parameters_string_list])
                    elif type == 3:
                        conditoins_info_dict['moment'].append([agroup_id,csys_id,initial,*steps_parameters_string_list])
                    else:
                        pass
            
            if conditoins_info_dict['displacement'] == []:
                pass
            else:
                ins_displacement_conditions_set = ins_conditions_group.create_dataset(name='displacement',shape=(len(conditoins_info_dict['displacement']),2+(len(steps_info_dict))),dtype=h5py.string_dtype(encoding='utf-8'))
                for cnodition_index,condition_info_list in enumerate(conditoins_info_dict['displacement']):
                    group_name = assembly_nodes_groups_info_dict[condition_info_list[0]][0]
                    ins_displacement_conditions_set[cnodition_index,0] = group_name
                    
                    csys_id = condition_info_list[1]
                    if csys_id == 0:
                        for step_index,step_parameters_string in enumerate(condition_info_list[2:]):
                            if step_parameters_string is None:
                                continue
                            else:
                                function_id = step_parameters_string.split(',')[-1]
                                if function_id == 'None':
                                    pass
                                elif function_id in include_functions_id_list:
                                    pass
                                else:
                                    include_functions_id_list.append(function_id)
                            
                                ins_displacement_conditions_set[cnodition_index,1+step_index] = step_parameters_string
                    else:
                        pass
            
            if conditoins_info_dict['concentrated force'] == []:
                pass
            else:
                ins_concentrated_force_conditions_set = ins_conditions_group.create_dataset(name='concentrated force',shape=(len(conditoins_info_dict['concentrated force']),2+(len(steps_info_dict))),dtype=h5py.string_dtype(encoding='utf-8'))
                for cnodition_index,condition_info_list in enumerate(conditoins_info_dict['concentrated force']):
                    group_name = assembly_nodes_groups_info_dict[condition_info_list[0]][0]
                    ins_concentrated_force_conditions_set[cnodition_index,0] = group_name
                    
                    csys_id = condition_info_list[1]
                    if csys_id == 0:
                        for step_index,step_parameters_string in enumerate(condition_info_list[2:]):
                            if step_parameters_string is None:
                                continue
                            else:
                                function_id = step_parameters_string.split(',')[-1]
                                if function_id == 'None':
                                    pass
                                elif function_id in include_functions_id_list:
                                    pass
                                else:
                                    include_functions_id_list.append(function_id)
                                    
                                ins_concentrated_force_conditions_set[cnodition_index,1+step_index] = step_parameters_string
                    else:
                        pass
            
            if conditoins_info_dict['moment'] == []:
                pass
            else:
                ins_moment_conditions_set = ins_conditions_group.create_dataset(name='moment',shape=(len(conditoins_info_dict['moment']),2+(len(steps_info_dict))),dtype=h5py.string_dtype(encoding='utf-8'))
                for cnodition_index,condition_info_list in enumerate(conditoins_info_dict['moment']):
                    group_name = assembly_nodes_groups_info_dict[condition_info_list[0]][0]
                    ins_moment_conditions_set[cnodition_index,0] = group_name
                    
                    csys_id = condition_info_list[1]
                    if csys_id == 0:
                        for step_index,step_parameters_string in enumerate(condition_info_list[2:]):
                            if step_parameters_string is None:
                                continue
                            else:
                                function_id = step_parameters_string.split(',')[-1]
                                if function_id == 'None':
                                    pass
                                elif function_id in include_functions_id_list:
                                    pass
                                else:
                                    include_functions_id_list.append(function_id)
                                    
                                ins_moment_conditions_set[cnodition_index,1+step_index] = step_parameters_string
                    else:
                        pass
            
            ins_conditions_functions_group = ins_conditions_group.create_group(name='Functions')
            for function_id in include_functions_id_list:
                conditions_function_info_list = []
                
                self.__ins_cursor.execute('SELECT type,parameters FROM functions WHERE model=? AND id=?',[model_id,int(function_id)])
                function_type_number,function_parameters_string = self.__ins_cursor.fetchone()
                conditions_function_info_list.append(function_type_number)
                for i in function_parameters_string.split(';'):
                    for j in i.split(','):
                        conditions_function_info_list.append(float(j))
                
                ins_conditions_functions_group.create_dataset(name=function_id,data=numpy.asarray(conditions_function_info_list),dtype=common.P4SFormat.NUMERICAL_PRECISION['float'])
            # endregion

    def getPartComponents(self, in_model_name:str, in_part_name:str) -> list:
        self.__ins_cursor.execute('SELECT id,dimension FROM models WHERE name=?',[in_model_name])
        model_id,model_dimension = self.__ins_cursor.fetchone()[0:2]
        
        self.__ins_cursor.execute('SELECT id,nodes,elements FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id, nodes_number, elements_number = self.__ins_cursor.fetchone()[0:3]
        
        if model_dimension == '2D':
            self.__ins_cursor.execute(f'SELECT x,y FROM {"part_"+str(part_id)+"_nodes"} ORDER BY id ASC')
            nodes_list = [[*nodes_info,0.0] for nodes_info in self.__ins_cursor.fetchall()]
        else:
            self.__ins_cursor.execute(f'SELECT x,y,z FROM {"part_"+str(part_id)+"_nodes"} ORDER BY id ASC')
            nodes_list = [[*nodes_info] for nodes_info in self.__ins_cursor.fetchall()]
        
        self.__ins_cursor.execute(f'SELECT geometry,nodes FROM {"part_"+str(part_id)+"_elements"} ORDER BY id ASC')
        elements_list = [[element_info[0],[int(node_label) for node_label in element_info[1].split(',')]] for element_info in self.__ins_cursor.fetchall()]
        
        return [nodes_list, elements_list, nodes_number, elements_number]
    def getPartGroupLabels(self, in_model_name:str, in_part_name:str, in_group_type:str, in_group_name:str) -> list:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        if in_group_type == 'node':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=1',[model_id,part_id,in_group_name])
            part_table_name = 'part_' + str(part_id) + '_nodes'
        elif in_group_type == 'element':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=2',[model_id,part_id,in_group_name])
            part_table_name = 'part_' + str(part_id) + '_elements'
        else:
            pass
        group_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute(f'SELECT id FROM {part_table_name} WHERE {"pg_"+str(group_id)}=1')
        
        return [i[0] for i in self.__ins_cursor.fetchall()]
    def importMeshParts(self, in_model_name:str, in_full_file_name:str, in_parts_name:list) -> dict:
        self.__ins_cursor.execute('SELECT id,dimension FROM models WHERE name=?',[in_model_name])
        model_id, model_dimension = self.__ins_cursor.fetchone()
        
        file_type = in_full_file_name.split('.')[1]
        parts_include_groups_dict = {part_name:{'nodes':[],'elements':[]} for part_name in in_parts_name}
        
        if file_type == 'inp':
            with open(in_full_file_name) as ins_inp_file:
                reading_part_name = None
                reading_data_type = None
                reading_element_geometry = None
                nodes_list, elements_list = [], []
                nodes_associate_elements_dict = {}

                reading_set_name = None
                part_nodes_set_dict, part_elements_set_dict = {}, {}
                
                reading_sign = True
                while reading_sign:
                    line_content = ins_inp_file.readline()
                    if '\n' in line_content:
                        pass
                    else:
                        reading_sign = False
                    
                    line_content = line_content.strip().strip(',').replace('\n','').replace(' ','')
                    if line_content == '':
                        continue
                    else:
                        pass
                    
                    keyword_content = line_content.split(',',1)
                    if keyword_content[0] == '*Part':
                        reading_part_name = keyword_content[1].split('=')[-1]
                        if reading_part_name in in_parts_name:
                            pass
                        else:
                            reading_part_name = None

                        continue
                    elif keyword_content[0] == '*Node':
                        if reading_part_name is None:
                            continue
                        else:
                            reading_data_type = 'node'
                        
                        continue
                    elif keyword_content[0] == '*Element':
                        if reading_part_name is None:
                            continue
                        else:
                            reading_data_type = 'element'
                        
                        elements_type = keyword_content[1].split('=')[1]
                        for element_geometry in common.P4SImportInfo.SUPPORTED_INP_ELEMENTS_BY_GEOMETRY_NUMBER[model_dimension]:
                            if elements_type in common.P4SImportInfo.SUPPORTED_INP_ELEMENTS_BY_GEOMETRY_NUMBER[model_dimension][element_geometry]:
                                reading_element_geometry = element_geometry
                            else:
                                continue
                    
                        continue
                    elif keyword_content[0] == '*Nset':
                        if reading_part_name is None:
                            continue
                        else:
                            nodes_set_infomation_list = keyword_content[1].split(',')
                            if len(nodes_set_infomation_list) == 1:
                                reading_data_type = 'nset-select'
                            else:
                                reading_data_type = 'nset-generate'

                            reading_set_name = nodes_set_infomation_list[0].split('=')[1]
                            part_nodes_set_dict[reading_set_name] = []
                        
                        continue
                    elif keyword_content[0] == '*Elset':
                        if reading_part_name is None:
                            continue
                        else:
                            elements_set_infomation_list = keyword_content[1].split(',')
                            if len(elements_set_infomation_list) == 1:
                                reading_data_type = "elset-select"
                            else:
                                reading_data_type = 'elset-generate'
                            
                            reading_set_name = elements_set_infomation_list[0].split('=')[1]
                            part_elements_set_dict[reading_set_name] = []
                        
                        continue
                    elif keyword_content[0] in ['*Orientation','*Transform'] or keyword_content[0].split(':',1)[0] == '**Section':
                        if reading_part_name is None:
                            continue
                        else:
                            reading_data_type = None
                        
                        continue
                    elif keyword_content[0] == '*EndPart':
                        if reading_part_name is None:
                            continue
                        else:
                            pass 
                        
                        nodes_number = len(nodes_list)
                        elements_number = len(elements_list)
                        nodes_label = list(set([node[0] for node in nodes_list]))
                        if max(nodes_label) == nodes_number and nodes_number == len(nodes_label):
                            pass
                        else:
                            del parts_include_groups_dict[reading_part_name]
                            
                            nodes_list = []
                            nodes_associate_elements_dict = {}
                            
                            reading_element_geometry = None
                            elements_list = []

                            part_nodes_set_dict = {}
                            part_elements_set_dict = {}
                            
                            reading_set_name = None
                            
                            reading_part_name = None
                            reading_data_type = None
                            
                            continue
                        del nodes_label
                        elements_label = list(set([element[0] for element in elements_list]))
                        if max(elements_label) == elements_number and elements_number == len(elements_label):
                            pass
                        else:
                            del parts_include_groups_dict[reading_part_name]
                            
                            nodes_list = []
                            nodes_associate_elements_dict = {}
                            
                            reading_element_geometry = None
                            elements_list = []

                            part_nodes_set_dict = {}
                            part_elements_set_dict = {}
                            
                            reading_set_name = None
                            
                            reading_part_name = None
                            reading_data_type = None
                            
                            continue
                        del elements_label
                        
                        self.__ins_cursor.execute('INSERT INTO parts(model,name,nodes,elements) VALUES(?,?,?,?)',[model_id, reading_part_name, nodes_number,elements_number])
                        
                        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,reading_part_name])
                        part_id = self.__ins_cursor.fetchone()[0]
                        
                        part_nodes_table_name = f'part_{str(part_id)}_nodes'
                        self.__ins_cursor.execute(f'CREATE TABLE {part_nodes_table_name}(id INTEGER PRIMARY KEY, x REAL NOT NULL, y REAL NOT NULL, z REAL DEFAULT 0.0, elements TEXT NOT NULL)')
                        if model_dimension == '2D':
                            self.__ins_cursor.executemany(f'INSERT INTO {part_nodes_table_name}(id,x,y,elements) VALUES(?,?,?,?)',[[node[0],node[1],node[2],','.join(nodes_associate_elements_dict[node[0]])] for node in nodes_list])
                        else:
                            self.__ins_cursor.executemany(f'INSERT INTO {part_nodes_table_name}(id,x,y,z,elements) VALUES(?,?,?,?,?)',[[*node,','.join(nodes_associate_elements_dict[node[0]])] for node in nodes_list])
                        nodes_list = []
                        nodes_associate_elements_dict = {}
                        
                        part_elements_table_name = f'part_{str(part_id)}_elements'
                        self.__ins_cursor.execute(f'CREATE TABLE {part_elements_table_name}(id INTEGER PRIMARY KEY, geometry INTEGER NOT NULL, nodes TEXT NOT NULL,\
                                                    ox REAL NOT NULL, oy REAL NOT NULL, oz REAL NOT NULL, ori1 REAL NOT NULL, ori2 REAL NOT NULL, ori3 REAL NOT NULL, ori4 REAL NOT NULL,\
                                                    property INTEGER, orientation INTEGER DEFAULT -1 NOT NULL)')
                        if model_dimension == '2D':
                            for element_index, element_info in enumerate(elements_list):
                                self.__ins_cursor.execute(f'SELECT x,y FROM {part_nodes_table_name} WHERE id IN ({element_info[2]})')
                                include_nodes_coordinates = [[node_coordinate[0],node_coordinate[1]] for node_coordinate in self.__ins_cursor.fetchall()]
                                center_coordinates = numpy.array([0.0,0.0,0.0])
                                for node_coordinates in include_nodes_coordinates:
                                    center_coordinates[0] += node_coordinates[0]
                                    center_coordinates[1] += node_coordinates[1]
                                center_coordinates = center_coordinates / len(element_info[2].split(','))
                                elements_list[element_index][3] = center_coordinates[0]
                                elements_list[element_index][4] = center_coordinates[1]
                                elements_list[element_index][5] = center_coordinates[2]

                                if element_info[1] in [1,6]:
                                    axis1_vector = numpy.array([0.0,0.0,0.0])
                                    axis1_vector[0] = include_nodes_coordinates[-1][0]-include_nodes_coordinates[0][0]
                                    axis1_vector[1] = include_nodes_coordinates[-1][1]-include_nodes_coordinates[0][1]
                                    axis1_unit_vector = axis1_vector / numpy.linalg.norm(axis1_vector)
                                    axis3_unit_vector = numpy.array([0.0,0.0,1.0])
                                    axis2_vector = numpy.cross(axis3_unit_vector, axis1_unit_vector)
                                    axis2_unit_vector = axis2_vector / numpy.linalg.norm(axis2_vector)

                                    ins_orientation_transform_matrix = vtk.vtkMatrix4x4()
                                    ins_orientation_transform_matrix.Zero()
                                    for i in range(3):
                                        ins_orientation_transform_matrix.SetElement(i,0,axis1_unit_vector[i])
                                    for i in range(3):
                                        ins_orientation_transform_matrix.SetElement(i,1,axis2_unit_vector[i])
                                    for i in range(3):
                                        ins_orientation_transform_matrix.SetElement(i,2,axis3_unit_vector[i])
                                    ins_orientation_transform_matrix.SetElement(0,3,center_coordinates[0])
                                    ins_orientation_transform_matrix.SetElement(1,3,center_coordinates[1])
                                    ins_orientation_transform_matrix.SetElement(2,3,center_coordinates[2])
                                    ins_orientation_transform_matrix.SetElement(3,3,1.0)
                                    ins_orientation_transformer = vtk.vtkTransform()
                                    ins_orientation_transformer.SetMatrix(ins_orientation_transform_matrix)
                                    orientation_wxyz = ins_orientation_transformer.GetOrientationWXYZ()
                                    elements_list[element_index][6] = orientation_wxyz[0]
                                    elements_list[element_index][7] = orientation_wxyz[1]
                                    elements_list[element_index][8] = orientation_wxyz[2]
                                    elements_list[element_index][9] = orientation_wxyz[3]
                                else:
                                    pass
                        else:
                            for element_index, element_info in enumerate(elements_list):
                                self.__ins_cursor.execute(f'SELECT x,y,z FROM {part_nodes_table_name} WHERE id IN ({element_info[2]})')
                                include_nodes_coordinates = [[node_coordinate[0],node_coordinate[1],node_coordinate[2]] for node_coordinate in self.__ins_cursor.fetchall()]
                            
                                center_coordinates = numpy.array([0.0,0.0,0.0])
                                for node_coordinates in include_nodes_coordinates:
                                    center_coordinates[0] += node_coordinates[0]
                                    center_coordinates[1] += node_coordinates[1]
                                    center_coordinates[2] += node_coordinates[2]
                                center_coordinates = center_coordinates / len(element_info[2].split(','))
                                elements_list[element_index][3] = center_coordinates[0]
                                elements_list[element_index][4] = center_coordinates[1]
                                elements_list[element_index][5] = center_coordinates[2]

                                if element_info[1] in [1,6]:
                                    axis1_vector = numpy.array([0.0,0.0,0.0])
                                    axis1_vector[0] = include_nodes_coordinates[-1][0]-include_nodes_coordinates[0][0]
                                    axis1_vector[1] = include_nodes_coordinates[-1][1]-include_nodes_coordinates[0][1]
                                    axis1_vector[2] = include_nodes_coordinates[-1][2]-include_nodes_coordinates[0][2]
                                    axis1_unit_vector = axis1_vector / numpy.linalg.norm(axis1_vector)
                                    for i in numpy.array([[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]):
                                        axis2_vector = i-numpy.dot(i,axis1_unit_vector) / numpy.dot(axis1_unit_vector,axis1_unit_vector) * axis1_unit_vector
                                        if numpy.all(axis2_vector==0.0):
                                            continue
                                        else:
                                            break
                                    axis2_unit_vector = axis2_vector / numpy.linalg.norm(axis2_vector)
                                    axis3_vector = numpy.cross(axis1_unit_vector, axis2_unit_vector)
                                    axis3_unit_vector = axis3_vector / numpy.linalg.norm(axis3_vector)

                                    ins_orientation_transform_matrix = vtk.vtkMatrix4x4()
                                    ins_orientation_transform_matrix.Zero()
                                    for i in range(3):
                                        ins_orientation_transform_matrix.SetElement(i,0,axis1_unit_vector[i])
                                    for i in range(3):
                                        ins_orientation_transform_matrix.SetElement(i,1,axis2_unit_vector[i])
                                    for i in range(3):
                                        ins_orientation_transform_matrix.SetElement(i,2,axis3_unit_vector[i])
                                    ins_orientation_transform_matrix.SetElement(0,3,center_coordinates[0])
                                    ins_orientation_transform_matrix.SetElement(1,3,center_coordinates[1])
                                    ins_orientation_transform_matrix.SetElement(2,3,center_coordinates[2])
                                    ins_orientation_transform_matrix.SetElement(3,3,1.0)
                                    ins_orientation_transformer = vtk.vtkTransform()
                                    ins_orientation_transformer.SetMatrix(ins_orientation_transform_matrix)
                                    orientation_wxyz = ins_orientation_transformer.GetOrientationWXYZ()
                                    elements_list[element_index][6] = orientation_wxyz[0]
                                    elements_list[element_index][7] = orientation_wxyz[1]
                                    elements_list[element_index][8] = orientation_wxyz[2]
                                    elements_list[element_index][9] = orientation_wxyz[3]
                                elif element_info[1] in [2,7,3,8]:
                                    vector_n1n2 = numpy.array([0.0,0.0,0.0])
                                    vector_n1n2[0] = include_nodes_coordinates[1][0]-include_nodes_coordinates[0][0]
                                    vector_n1n2[1] = include_nodes_coordinates[1][1]-include_nodes_coordinates[0][1]
                                    vector_n1n2[2] = include_nodes_coordinates[1][2]-include_nodes_coordinates[0][2]
                                    vector_n1n3 = numpy.array([0.0,0.0,0.0])
                                    vector_n1n3[0] = include_nodes_coordinates[2][0]-include_nodes_coordinates[0][0]
                                    vector_n1n3[1] = include_nodes_coordinates[2][1]-include_nodes_coordinates[0][1]
                                    vector_n1n3[2] = include_nodes_coordinates[2][2]-include_nodes_coordinates[0][2]
                                    axis3_vector = numpy.cross(vector_n1n2, vector_n1n3)
                                    axis3_unit_vector = axis3_vector / numpy.linalg.norm(axis3_vector)
                                    axis1_vector = numpy.array([1.0,0.0,0.0])-numpy.dot(numpy.array([1.0,0.0,0.0]),axis3_unit_vector) / numpy.dot(axis3_unit_vector,axis3_unit_vector) * axis3_unit_vector
                                    if numpy.all(axis1_vector==0):
                                        axis1_vector = numpy.array([0.0,1.0,0.0])-numpy.dot(numpy.array([0.0,1.0,0.0]),axis3_unit_vector) / numpy.dot(axis3_unit_vector,axis3_unit_vector) * axis3_unit_vector
                                    else:   pass
                                    axis1_unit_vector = axis1_vector / numpy.linalg.norm(axis1_vector)
                                    axis2_vector = numpy.cross(axis3_unit_vector, axis1_unit_vector)
                                    axis2_unit_vector = axis2_vector / numpy.linalg.norm(axis2_vector)

                                    ins_orientation_transform_matrix = vtk.vtkMatrix4x4()
                                    ins_orientation_transform_matrix.Zero()
                                    for i in range(3):
                                        ins_orientation_transform_matrix.SetElement(i,0,axis1_unit_vector[i])
                                    for i in range(3):
                                        ins_orientation_transform_matrix.SetElement(i,1,axis2_unit_vector[i])
                                    for i in range(3):
                                        ins_orientation_transform_matrix.SetElement(i,2,axis3_unit_vector[i])
                                    ins_orientation_transform_matrix.SetElement(0,3,center_coordinates[0])
                                    ins_orientation_transform_matrix.SetElement(1,3,center_coordinates[1])
                                    ins_orientation_transform_matrix.SetElement(2,3,center_coordinates[2])
                                    ins_orientation_transform_matrix.SetElement(3,3,1.0)
                                    ins_orientation_transformer = vtk.vtkTransform()
                                    ins_orientation_transformer.SetMatrix(ins_orientation_transform_matrix)
                                    orientation_wxyz = ins_orientation_transformer.GetOrientationWXYZ()
                                    elements_list[element_index][6] = orientation_wxyz[0]
                                    elements_list[element_index][7] = orientation_wxyz[1]
                                    elements_list[element_index][8] = orientation_wxyz[2]
                                    elements_list[element_index][9] = orientation_wxyz[3]                                    
                                else:
                                    pass
                        self.__ins_cursor.executemany(f'INSERT INTO {part_elements_table_name}(id,geometry,nodes,ox,oy,oz,ori1,ori2,ori3,ori4) VALUES(?,?,?,?,?,?,?,?,?,?)',elements_list)
                        reading_element_geometry = None
                        elements_list = []
                        
                        for set_name in part_nodes_set_dict:
                            self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,part_id,set_name,1,len(part_nodes_set_dict[set_name])])
                            
                            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND type=? AND name=?',[model_id,part_id,1,set_name])
                            group_id = self.__ins_cursor.fetchone()[0]
                            self.__ins_cursor.execute(f'ALTER TABLE {part_nodes_table_name} ADD COLUMN {"pg_"+str(group_id)} INTEGER')
                            self.__ins_cursor.executemany(f'UPDATE {part_nodes_table_name} SET {"pg_"+str(group_id)}=1 WHERE id=?',[[node_label] for node_label in part_nodes_set_dict[set_name]])
                        
                            parts_include_groups_dict[reading_part_name]['nodes'].append(set_name)
                        part_nodes_set_dict = {}
                        
                        for set_name in part_elements_set_dict:
                            self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,part_id,set_name,2,len(part_elements_set_dict[set_name])])
                            
                            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND type=? AND name=?',[model_id,part_id,2,set_name])
                            group_id = self.__ins_cursor.fetchone()[0]
                            self.__ins_cursor.execute(f'ALTER TABLE {part_elements_table_name} ADD COLUMN {"pg_"+str(group_id)} INTEGER')
                            self.__ins_cursor.executemany(f'UPDATE {part_elements_table_name} SET {"pg_"+str(group_id)}=1 WHERE id=?',[[element_label] for element_label in part_elements_set_dict[set_name]])

                            parts_include_groups_dict[reading_part_name]['elements'].append(set_name)
                        part_elements_set_dict = {}
                        
                        reading_set_name = None
                        reading_part_name = None
                        reading_data_type = None
                    elif keyword_content[0] in ['*Assembly','*Step']:
                        reading_sign = False
                        break
                    else:
                        pass
                    
                    if reading_data_type is None:
                        continue
                    else:
                        pass
                    
                    if reading_data_type == 'node':
                        node_label = int(keyword_content[0])
                        nodes_list.append([node_label,*[float(node_coordinate) for node_coordinate in keyword_content[1].split(",")]])
                        nodes_associate_elements_dict[node_label] = []
                    elif reading_data_type == 'element':
                        elements_list.append([int(keyword_content[0]), reading_element_geometry, keyword_content[1], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
                        
                        for node_label in keyword_content[1].split(','):
                            nodes_associate_elements_dict[int(node_label)].append(keyword_content[0])
                    elif reading_data_type == 'nset-generate':
                        generate_params_list = [int(param) for param in line_content.split(',')]
                        part_nodes_set_dict[reading_set_name] += list(range(generate_params_list[0],generate_params_list[1]+generate_params_list[2],generate_params_list[2]))
                    elif reading_data_type == 'nset-select':
                        part_nodes_set_dict[reading_set_name] += [int(node_label) for node_label in line_content.split(',')]
                    elif reading_data_type == 'elset-generate':
                        generate_params_list = [int(param) for param in line_content.split(',')]
                        part_elements_set_dict[reading_set_name] += list(range(generate_params_list[0],generate_params_list[1]+generate_params_list[2],generate_params_list[2]))
                    elif reading_data_type == 'elset-select':
                        part_elements_set_dict[reading_set_name] += [int(element_label) for element_label in line_content.split(',')]
                    else:
                        pass
        else:
            pass
        
        return parts_include_groups_dict
    def duplicateMeshPart(self, in_model_name:str, in_source_part_name:str, in_object_part_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id,nodes,elements FROM parts WHERE model=? AND name=?',[model_id,in_source_part_name])
        source_part_id,part_nodes_number,part_elements_number = self.__ins_cursor.fetchone()
        
        self.__ins_cursor.execute('INSERT INTO parts(model,name,nodes,elements) VALUES(?,?,?,?) ',[model_id,in_object_part_name,part_nodes_number,part_elements_number])
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_object_part_name])
        object_part_id = self.__ins_cursor.fetchone()[0]
        
        object_part_nodes_table_name = f'part_{str(object_part_id)}_nodes'
        self.__ins_cursor.execute(f'CREATE TABLE {object_part_nodes_table_name}(id INTEGER PRIMARY KEY, x REAL NOT NULL, y REAL NOT NULL, z REAL DEFAULT 0.0, elements TEXT NOT NULL)')
        source_part_nodes_table_name = f'part_{str(source_part_id)}_nodes'
        self.__ins_cursor.execute(f'INSERT INTO {object_part_nodes_table_name} (id,x,y,z,elements) SELECT id,x,y,z,elements FROM {source_part_nodes_table_name}')
        self.__ins_cursor.execute('SELECT id,name,number FROM groups WHERE model=? AND sign=? AND type=1',[model_id,source_part_id])
        source_part_nodes_groups_info_list = self.__ins_cursor.fetchall()
        for source_group_id,source_group_name,source_group_number in source_part_nodes_groups_info_list:
            self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,object_part_id,source_group_name,1,source_group_number])

            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=1',[model_id,object_part_id,source_group_name])
            object_group_id = self.__ins_cursor.fetchone()[0]
            self.__ins_cursor.execute(f'ALTER TABLE {object_part_nodes_table_name} ADD COLUMN {"pg_"+str(object_group_id)} INTEGER')
            self.__ins_cursor.execute(f'SELECT id FROM {source_part_nodes_table_name} WHERE {"pg_"+str(source_group_id)}=1')
            source_group_nodes_id = self.__ins_cursor.fetchall()
            self.__ins_cursor.executemany(f'UPDATE {object_part_nodes_table_name} SET {"pg_"+str(object_group_id)}=1 WHERE id=?',source_group_nodes_id)
        
        object_part_elements_table_name = f'part_{str(object_part_id)}_elements'
        self.__ins_cursor.execute(f'CREATE TABLE {object_part_elements_table_name}(id INTEGER PRIMARY KEY, geometry INTEGER NOT NULL, nodes TEXT NOT NULL,\
                                                    ox REAL NOT NULL, oy REAL NOT NULL, oz REAL NOT NULL, ori1 REAL NOT NULL, ori2 REAL NOT NULL, ori3 REAL NOT NULL, ori4 REAL NOT NULL,\
                                                    property INTEGER, orientation INTEGER DEFAULT -1 NOT NULL)')
        source_part_elements_table_name = f'part_{str(source_part_id)}_elements'
        self.__ins_cursor.execute(f'INSERT INTO {object_part_elements_table_name} (id,geometry,nodes,ox,oy,oz,ori1,ori2,ori3,ori4) SELECT id,geometry,nodes,ox,oy,oz,ori1,ori2,ori3,ori4 FROM {source_part_elements_table_name}')
        self.__ins_cursor.execute('SELECT id,name,number FROM groups WHERE model=? AND sign=? AND type=2',[model_id,source_part_id])
        source_part_elements_groups_info_list = self.__ins_cursor.fetchall()
        for source_group_id,source_group_name,source_group_number in source_part_elements_groups_info_list:
            self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,object_part_id,source_group_name,2,source_group_number])

            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=2',[model_id,object_part_id,source_group_name])
            object_group_id = self.__ins_cursor.fetchone()[0]
            self.__ins_cursor.execute(f'ALTER TABLE {object_part_elements_table_name} ADD COLUMN {"pg_"+str(object_group_id)} INTEGER')
            self.__ins_cursor.execute(f'SELECT id FROM {source_part_elements_table_name} WHERE {"pg_"+str(source_group_id)}=1')
            source_group_elements_id = self.__ins_cursor.fetchall()
            self.__ins_cursor.executemany(f'UPDATE {object_part_elements_table_name} SET {"pg_"+str(object_group_id)}=1 WHERE id=?',source_group_elements_id)
    def renamePart(self, in_model_name:str, in_old_part_name:str, in_new_part_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('UPDATE parts SET name=? WHERE model=? AND name=?',[in_new_part_name,model_id,in_old_part_name])
    def removePart(self, in_model_name:str, in_part_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('DELETE FROM parts WHERE id=?',[part_id])
        self.__ins_cursor.execute(f'DROP TABLE {"part_"+str(part_id)+"_nodes"}')
        self.__ins_cursor.execute(f'DROP TABLE {"part_"+str(part_id)+"_elements"}')
        self.__ins_cursor.execute('DELETE FROM groups WHERE model=? AND sign=?',[model_id,part_id])
        self.__ins_cursor.execute('DELETE FROM property_assignments WHERE model=? AND part=?',[model_id,part_id])
        self.__ins_cursor.execute('DELETE FROM coordinate_systems WHERE model=? AND source=?',[model_id,part_id])
        self.__ins_cursor.execute('DELETE FROM orientation_assignments WHERE model=? AND part=?',[model_id,part_id])
        
        association_info_dict = {'instances':[],'agroups':{'nodes':[],'elements':[]},'outputs':[],'conditions':[]}
        self.__ins_cursor.execute('SELECT id,name FROM assembly WHERE model=? AND part=?',[model_id,part_id])
        instances_info_list = self.__ins_cursor.fetchall()
        for instance_id,instance_name in instances_info_list:
            association_info_dict['instances'].append(instance_name)
            self.__ins_cursor.execute('DELETE FROM assembly WHERE model=? AND id=?',[model_id,instance_id])
            
            self.__ins_cursor.execute('SELECT agroup FROM groups_instances_association WHERE model=? AND instance=?',[model_id,instance_id])
            instance_associated_agroups_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
            for agroup_id in instance_associated_agroups_id_list:
                self.__ins_cursor.execute('SELECT COUNT(*) FROM groups_instances_association WHERE model=? AND agroup=?',[model_id,agroup_id])
                agroup_include_instances_number = self.__ins_cursor.fetchone()[0]
                if agroup_include_instances_number == 1:
                    self.__ins_cursor.execute('SELECT name,type FROM groups WHERE model=? AND id=?',[model_id,agroup_id])
                    agroup_name,agroup_type = self.__ins_cursor.fetchone()
                    if agroup_type == 1:
                        association_info_dict['agroups']['nodes'].append(agroup_name)
                    elif agroup_type == 2:
                        association_info_dict['agroups']['elements'].append(agroup_name)
                    else:
                        pass
                    self.__ins_cursor.execute('DELETE FROM groups WHERE model=? AND id=?',[model_id,agroup_id])
                    
                    self.__ins_cursor.execute('SELECT name FROM outputs WHERE model=? AND agroup=?',[model_id,agroup_id])
                    agroup_associated_outputs_list = [i[0] for i in self.__ins_cursor.fetchall()]
                    for output_name in agroup_associated_outputs_list:
                        if output_name in association_info_dict['outputs']:
                            continue
                        else:
                            association_info_dict['outputs'].append(output_name)
                    self.__ins_cursor.execute('DELETE FROM outputs WHERE model=? AND agroup=?',[model_id,agroup_id])
                    
                    self.__ins_cursor.execute('SELECT name FROM boundary_conditions WHERE model=? AND agroup=?',[model_id,agroup_id])
                    agroup_associated_conditions_list = [i[0] for i in self.__ins_cursor.fetchall()]
                    for condition_name in agroup_associated_conditions_list:
                        if condition_name in association_info_dict['conditions']:
                            continue
                        else:
                            association_info_dict['conditions'].append(condition_name)
                    self.__ins_cursor.execute('DELETE FROM boundary_conditions WHERE model=? AND agroup=?',[model_id,agroup_id])
                else:
                    pass

            self.__ins_cursor.execute('DELETE FROM groups_instances_association WHERE model=? AND instance=?',[model_id,instance_id])

        return association_info_dict
    
    def createPartGroupFromSelection(self, in_model_name:str, in_part_name:str,in_type:str,in_part_group_name:str,in_include_labels:list) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        if in_type == 'node':
            self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,part_id,in_part_group_name,1,len(in_include_labels)])
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND type=? AND name=?',[model_id,part_id,1,in_part_group_name])
            group_id = self.__ins_cursor.fetchone()[0]
            part_table_name = f'part_{str(part_id)}_nodes'
        elif in_type == 'element':
            self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,part_id,in_part_group_name,2,len(in_include_labels)])
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND type=? AND name=?',[model_id,part_id,2,in_part_group_name])
            group_id = self.__ins_cursor.fetchone()[0]
            part_table_name = f'part_{str(part_id)}_elements'
        else:
            pass      
        
        self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} ADD COLUMN {"pg_"+str(group_id)} INTEGER')
        self.__ins_cursor.executemany(f'UPDATE {part_table_name} SET {"pg_"+str(group_id)}=1 WHERE id=?',[[label] for label in in_include_labels])
    def renamePartGroup(self, in_model_name:str, in_part_name:str, in_group_type:str, in_old_group_name:str, in_new_group_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        if in_group_type == 'node':
            self.__ins_cursor.execute('UPDATE groups SET name=? WHERE model=? AND sign=? AND name=? AND type=1',[in_new_group_name,model_id,part_id,in_old_group_name])
        elif in_group_type == 'element':
            self.__ins_cursor.execute('UPDATE groups SET name=? WHERE model=? AND sign=? AND name=? AND type=2',[in_new_group_name,model_id,part_id,in_old_group_name])
        else:
            pass
    def editPartGroupFromSelection(self, in_model_name:str, in_part_name:str,in_type:str,in_part_group_name:str,in_include_labels:list) -> bool:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        if in_type == 'node':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND type=1 AND name=?',[model_id,part_id,in_part_group_name])
            group_id = self.__ins_cursor.fetchone()[0]
            
            part_table_name = f'part_{str(part_id)}_nodes'
            self.__ins_cursor.execute(f'UPDATE {part_table_name} SET {"pg_"+str(group_id)}=NULL')
            self.__ins_cursor.executemany(f'UPDATE {part_table_name} SET {"pg_"+str(group_id)}=1 WHERE id=?',[[label] for label in in_include_labels])
            self.__ins_cursor.execute('UPDATE groups SET number=? WHERE model=? AND id=?',[len(in_include_labels),model_id,group_id])
        elif in_type == 'element':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND type=2 AND name=?',[model_id,part_id,in_part_group_name])
            group_id = self.__ins_cursor.fetchone()[0]
            
            part_table_name = f'part_{str(part_id)}_elements'
            
            group_has_property_assignment = False
            self.__ins_cursor.execute('SELECT id FROM property_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
            property_assignment_id_list = self.__ins_cursor.fetchone()
            if property_assignment_id_list is None:
                pass
            else:
                group_has_property_assignment = True
            if group_has_property_assignment:
                self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} ADD COLUMN temp INTEGER')
                self.__ins_cursor.executemany(f'UPDATE {part_table_name} SET temp=1 WHERE id=?',[[label] for label in in_include_labels])

                self.__ins_cursor.execute(f'SELECT DISTINCT property FROM {part_table_name} WHERE temp=1')
                group_include_property_assignments_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
                if None in group_include_property_assignments_id_list:
                    group_include_property_assignments_id_list.remove(None)
                else:
                    pass
            else:
                pass
            
            group_has_orientation_assignment = False
            self.__ins_cursor.execute('SELECT id FROM orientation_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
            orientation_assignment_id_list = self.__ins_cursor.fetchone()
            if orientation_assignment_id_list is None:
                pass
            else:
                group_has_orientation_assignment = True
            if group_has_orientation_assignment:
                if group_has_property_assignment:
                    pass
                else:
                    self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} ADD COLUMN temp INTEGER')
                    self.__ins_cursor.executemany(f'UPDATE {part_table_name} SET temp=1 WHERE id=?',[[label] for label in in_include_labels])

                self.__ins_cursor.execute(f'SELECT DISTINCT orientation FROM {part_table_name} WHERE temp=1')
                group_include_orientation_assignments_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
                if None in group_include_orientation_assignments_id_list:
                    group_include_orientation_assignments_id_list.remove(None)
                else:
                    pass
                if -1 in group_include_orientation_assignments_id_list:
                    group_include_orientation_assignments_id_list.remove(-1)
                else:
                    pass
            else:
                pass
            
            if group_has_property_assignment:
                self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} DROP COLUMN temp')
                
                if len(group_include_property_assignments_id_list) > 1:
                    return False
                else:
                    pass
            elif group_has_orientation_assignment:
                self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} DROP COLUMN temp')
                
                if len(group_include_orientation_assignments_id_list) > 1:
                    return False
                else:
                    pass
            else:
                pass
        
            self.__ins_cursor.execute(f'UPDATE {part_table_name} SET {"pg_"+str(group_id)}=NULL')
            self.__ins_cursor.executemany(f'UPDATE {part_table_name} SET {"pg_"+str(group_id)}=1 WHERE id=?',[[label] for label in in_include_labels])
            self.__ins_cursor.execute('UPDATE groups SET number=? WHERE model=? AND id=?',[len(in_include_labels),model_id,group_id])
        
            if group_has_property_assignment:
                self.__ins_cursor.execute(f'UPDATE {part_table_name} SET property=? WHERE {"pg_"+str(group_id)}=1',[property_assignment_id_list[0]])
            else:
                pass
            
            if group_has_orientation_assignment:
                self.__ins_cursor.execute(f'UPDATE {part_table_name} SET orientation=? WHERE {"pg_"+str(group_id)}=1',[orientation_assignment_id_list[0]])
            else:
                pass
        else:
            pass      
        
        return True
    def removePartGroup(self, in_model_name:str, in_part_name:str, in_group_type:str, in_group_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        if in_group_type == 'node':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=1',[model_id,part_id,in_group_name])
            group_id = self.__ins_cursor.fetchone()[0]
            self.__ins_cursor.execute(f'DELETE FROM groups WHERE id=?',[group_id])
            
            part_nodes_table_name = 'part_'+str(part_id)+'_nodes'
            self.__ins_cursor.execute(f'ALTER TABLE {part_nodes_table_name} DROP COLUMN {"pg_"+str(group_id)}')
        elif in_group_type == 'element':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=2',[model_id,part_id,in_group_name])
            group_id = self.__ins_cursor.fetchone()[0]
            self.__ins_cursor.execute(f'DELETE FROM groups WHERE id=?',[group_id])
            
            part_elements_table_name = 'part_'+str(part_id)+'_elements'
            self.__ins_cursor.execute(f'ALTER TABLE {part_elements_table_name} DROP COLUMN {"pg_"+str(group_id)}')

            self.__ins_cursor.execute('SELECT id FROM property_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
            property_id_list = self.__ins_cursor.fetchone()
            if property_id_list is None:
                pass
            else:
                self.__ins_cursor.execute(f'UPDATE {part_elements_table_name} SET property=NULL WHERE property=?',[property_id_list[0]])
                self.__ins_cursor.execute(f'DELETE FROM property_assignments WHERE id=?',[property_id_list[0]])
            
            self.__ins_cursor.execute('SELECT id FROM orientation_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
            orientation_id_list = self.__ins_cursor.fetchone()
            if orientation_id_list is None:
                pass
            else:
                self.__ins_cursor.execute(f'UPDATE {part_elements_table_name} SET orientation=-1 WHERE orientation=?',[orientation_id_list[0]])
                self.__ins_cursor.execute(f'DELETE FROM orientation_assignments WHERE id=?',[orientation_id_list[0]])
        else:
            pass

    def getPartElementGroupsHaveProperty(self, in_model_name:str, in_part_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id,dimension FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id,name FROM groups WHERE model=? AND sign=? AND type=2',[model_id,part_id])
        part_element_groups_have_property_dict = {i[1]:i[0] for i in self.__ins_cursor.fetchall()}
        
        part_elements_table_name = f'part_{str(part_id)}_elements'
        for group_name,group_id in part_element_groups_have_property_dict.items():
            self.__ins_cursor.execute(f'SELECT COUNT(*) FROM {part_elements_table_name} WHERE {"pg_"+str(group_id)}=1 AND property IS NOT NULL')
            if self.__ins_cursor.fetchone()[0] > 0:
                part_element_groups_have_property_dict[group_name] = True
            else:
                part_element_groups_have_property_dict[group_name] = False
        
        return part_element_groups_have_property_dict
    def getPartElementGroupsIncludeGeometry(self, in_model_name:str, in_part_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id,dimension FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id,name FROM groups WHERE model=? AND sign=? AND type=2',[model_id,part_id])
        part_element_groups_include_geometry_dict = {i[1]:i[0] for i in self.__ins_cursor.fetchall()}

        part_elements_table_name = f'part_{str(part_id)}_elements'
        for group_name,group_id in part_element_groups_include_geometry_dict.items():
            self.__ins_cursor.execute(f'SELECT DISTINCT geometry FROM {part_elements_table_name} WHERE {"pg_"+str(group_id)}=1')
            
            part_element_groups_include_geometry_dict[group_name] = [common.P4SElementInfo.NUMBER_TO_GEOMETRY[i[0]] for i in self.__ins_cursor.fetchall()]
        
        return part_element_groups_include_geometry_dict
    def getPartElementsGroupPropertyAssignments(self, in_model_name:str, in_part_name:str, in_group_name:str, in_group_include_geometry:list) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]

        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=2',[model_id,part_id,in_group_name])
        group_id = self.__ins_cursor.fetchone()[0]
        
        property_assignments_dict_by_geometry = {}
        for geometry_type in in_group_include_geometry:
            geometry_type_number = common.P4SElementInfo.GEOMETRY_TO_NUMBER[geometry_type]
            self.__ins_cursor.execute(f'SELECT {"geo"+str(geometry_type_number)+"_attribute"},{"geo"+str(geometry_type_number)+"_material"},{"geo"+str(geometry_type_number)+"_etype"} FROM property_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
            attribute_id,material_id,element_type_number = self.__ins_cursor.fetchone()

            self.__ins_cursor.execute('SELECT name FROM attributes WHERE model=? AND id=?',[model_id,attribute_id])
            attribute_name = self.__ins_cursor.fetchone()[0]
            
            self.__ins_cursor.execute('SELECT name FROM materials WHERE model=? AND id=?',[model_id,material_id])
            material_name = self.__ins_cursor.fetchone()[0]

            property_assignments_dict_by_geometry[geometry_type] = [attribute_name,material_name,common.P4SElementInfo.ELEMENTS_NUMBER_TO_TYPE[element_type_number]]
        
        return property_assignments_dict_by_geometry
    def assignPartElementsPropertyByGeometry(self,in_model_name:str,in_part_name:str,in_property_assignments_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]

        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=?',[model_id,part_id,in_property_assignments_info['group'],2])
        group_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute(f'SELECT id FROM property_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
        if self.__ins_cursor.fetchone() is None:
            self.__ins_cursor.execute(f'INSERT INTO property_assignments(model,part,pgroup) VALUES(?,?,?)',[model_id,part_id,group_id])
            self.__ins_cursor.execute(f'SELECT id FROM property_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
            property_assignment_id = self.__ins_cursor.fetchone()[0]
            
            self.__ins_cursor.execute(f'UPDATE {"part_"+str(part_id)+"_elements"} SET property=? WHERE pg_{str(group_id)}=1',[property_assignment_id])
        else:
            self.__ins_cursor.execute(f'SELECT id FROM property_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
            property_assignment_id = self.__ins_cursor.fetchone()[0]

        for geometry_type,property_params in in_property_assignments_info['property'].items():
            self.__ins_cursor.execute('SELECT id,type FROM attributes WHERE model=? AND name=?',[model_id,property_params[0]])
            attribute_id = self.__ins_cursor.fetchone()[0]
            
            self.__ins_cursor.execute('SELECT id FROM materials WHERE model=? AND name=?',[model_id,property_params[1]])
            material_id = self.__ins_cursor.fetchone()[0]
            
            element_type_number = common.P4SElementInfo.ELEMENTS_TYPE_TO_NUMBER[property_params[2]]
            
            geometry_type_number = common.P4SElementInfo.GEOMETRY_TO_NUMBER[geometry_type]
            
            self.__ins_cursor.execute(f'UPDATE property_assignments SET {"geo"+str(geometry_type_number)+"_attribute"}=?,{"geo"+str(geometry_type_number)+"_material"}=?,{"geo"+str(geometry_type_number)+"_etype"}=? WHERE model=? AND id=?',[attribute_id,material_id,element_type_number,model_id,property_assignment_id])
    def removePartElementsPropertyAssignments(self, in_model_name:str, in_part_name:str, in_group_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]

        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=2',[model_id,part_id,in_group_name])
        group_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM property_assignments WHERE model=? AND part=? AND pgroup=?',[model_id,part_id,group_id])
        property_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute(f'UPDATE {"part_"+str(part_id)+"_elements"} SET property=NULL WHERE property=?',[property_id])
        self.__ins_cursor.execute(f'DELETE FROM property_assignments WHERE id=?',[property_id])

    def getPartElementsOrientationParameters(self, in_model_name:str, in_part_name:str, in_group_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id,dimension FROM models WHERE name=?',[in_model_name])
        model_id,model_dimensin = self.__ins_cursor.fetchone()

        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=2',[model_id,part_id,in_group_name])
        group_id = self.__ins_cursor.fetchone()[0]
        
        elements_orientation_parameters_dict = {}
        part_elements_table_name = 'part_'+str(part_id)+'_elements'
        
        self.__ins_cursor.execute(f'SELECT id,ox,oy,oz,ori1,ori2,ori3,ori4 FROM {part_elements_table_name} WHERE {"pg_"+str(group_id)}=1 AND orientation=-1')
        for element_label,*element_orientation_parameters_list in self.__ins_cursor.fetchall():
            elements_orientation_parameters_dict[element_label] = element_orientation_parameters_list
        
        self.__ins_cursor.execute(f'SELECT DISTINCT orientation FROM {part_elements_table_name} WHERE {"pg_"+str(group_id)}=1 AND orientation!=-1')
        orientation_assignments_parameters_dict = {i[0]:{'type':None,'origin':None,'rotation':None,'raxis':None,'angle':None} for i in self.__ins_cursor.fetchall()}
        for orientation_assignment_id in orientation_assignments_parameters_dict:
            self.__ins_cursor.execute('SELECT reference,raxis,angle FROM orientation_assignments WHERE id=? AND model=? AND part=?',[orientation_assignment_id,model_id,part_id])
            ref_csys_id,raxis_number,angle_value = self.__ins_cursor.fetchone()
            
            if ref_csys_id == 0:
                orientation_assignments_parameters_dict[orientation_assignment_id]['type'] = 1
                orientation_assignments_parameters_dict[orientation_assignment_id]['origin']= [0.0,0.0,0.0]
                orientation_assignments_parameters_dict[orientation_assignment_id]['rotation'] = [0.0,0.0,0.0,1.0]
            else:
                self.__ins_cursor.execute('SELECT type,ox,oy,oz,ori1,ori2,ori3,ori4 FROM coordinate_systems WHERE model=? AND id=? AND source=?',[ref_csys_id,model_id,part_id])
                ref_csys_info_list = self.__ins_cursor.fetchone()
                orientation_assignments_parameters_dict[orientation_assignment_id]['type'] = ref_csys_info_list[0]
                orientation_assignments_parameters_dict[orientation_assignment_id]['origin'] = [i for i in ref_csys_info_list[1:4]]
                orientation_assignments_parameters_dict[orientation_assignment_id]['rotation'] = [i for i in ref_csys_info_list[4:]]
            orientation_assignments_parameters_dict[orientation_assignment_id]['raxis'] = raxis_number
            orientation_assignments_parameters_dict[orientation_assignment_id]['angle'] = angle_value
        
        if model_dimensin == '2D':
            for orientation_assignment_id,orientation_assignment_info_dict in orientation_assignments_parameters_dict.items():
                self.__ins_cursor.execute(f'SELECT id,geometry,ox,oy,oz,ori1,ori2,ori3,ori4 FROM {part_elements_table_name} WHERE orientation=?',[orientation_assignment_id])
                
                if orientation_assignment_info_dict['type'] == 1:
                    for element_label,element_geometry_type_number,*element_orientation_parameters_list in self.__ins_cursor.fetchall():
                        if element_geometry_type_number in [1,6]:
                            elements_orientation_parameters_dict[element_label] = element_orientation_parameters_list
                        else:
                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                            ins_element_transformer.RotateZ(angle_value)
                            
                            elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                            del ins_element_transformer
                else:
                    for element_label,element_geometry_type_number,*element_orientation_parameters_list in self.__ins_cursor.fetchall():
                        if element_geometry_type_number in [1,6]:
                            elements_orientation_parameters_dict[element_label] = element_orientation_parameters_list
                        else:
                            element_axis1_vector = numpy.asarray(element_orientation_parameters_list[0:3]) - numpy.asarray(orientation_assignment_info_dict['origin'])
                            if numpy.all(element_axis1_vector==0.0):
                                ins_ref_csys_transformer = vtk.vtkTransform()
                                ins_ref_csys_transformer.Translate(orientation_assignment_info_dict['origin'])
                                ins_ref_csys_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                                element_axis1_vector = ins_ref_csys_transformer.TransformVector([1.0,0.0,0.0])
                                del ins_ref_csys_transformer
                            else:
                                pass
                            
                            element_axis1_unit_vector = element_axis1_vector / numpy.linalg.norm(element_axis1_vector)
                            element_axis3_unit_vector =  numpy.asarray([0.0,0.0,1.0])
                            element_axis2_vector = numpy.cross(element_axis3_unit_vector,element_axis1_unit_vector)
                            element_axis2_unit_vector = element_axis2_vector / numpy.linalg.norm(element_axis2_vector)
                            
                            ins_element_transform_matrix = vtk.vtkMatrix4x4()
                            ins_element_transform_matrix.Zero()
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,0,element_axis1_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,1,element_axis2_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,2,element_axis3_unit_vector[i])
                            ins_element_transform_matrix.SetElement(0,3,element_orientation_parameters_list[0])
                            ins_element_transform_matrix.SetElement(1,3,element_orientation_parameters_list[1])
                            ins_element_transform_matrix.SetElement(2,3,element_orientation_parameters_list[2])
                            ins_element_transform_matrix.SetElement(3,3,1.0)
                            
                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.SetMatrix(ins_element_transform_matrix)
                            ins_element_transformer.RotateZ(angle_value)
                            
                            elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                            
                            del ins_element_transformer
                            del ins_element_transform_matrix
        elif model_dimensin == '3D':
            for orientation_assignment_id,orientation_assignment_info_dict in orientation_assignments_parameters_dict.items():
                self.__ins_cursor.execute(f'SELECT id,geometry,ox,oy,oz,ori1,ori2,ori3,ori4 FROM {part_elements_table_name} WHERE orientation=?',[orientation_assignment_id])
                
                if orientation_assignment_info_dict['type'] == 1:
                    for element_label,element_geometry_type_number,*element_orientation_parameters_list in self.__ins_cursor.fetchall():
                        if element_geometry_type_number in [1,6]:
                            if raxis_number == 1:
                                ins_element_transformer = vtk.vtkTransform()
                                ins_element_transformer.RotateWXYZ(*element_orientation_parameters_list[3:])
                                ins_element_transformer.RotateX(angle_value)
                                
                                elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                                del ins_element_transformer
                            else:
                                elements_orientation_parameters_dict[element_label] = element_orientation_parameters_list
                        elif element_geometry_type_number in [2,3,7,8]:
                            ins_ref_csys_transformer = vtk.vtkTransform()
                            ins_ref_csys_transformer.Translate(orientation_assignment_info_dict['origin'])
                            ins_ref_csys_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                            ref_axis_x_vector = ins_ref_csys_transformer.TransformVector([1.0,0.0,0.0])
                            ref_axis_y_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                            del ins_ref_csys_transformer
                            
                            ins_element_reference_transformer = vtk.vtkTransform()
                            ins_element_reference_transformer.Translate(element_orientation_parameters_list[0:3])
                            ins_element_reference_transformer.RotateWXYZ(*element_orientation_parameters_list[3:])
                            element_axis3_vector = ins_element_reference_transformer.TransformVector([0.0,0.0,1.0])
                            element_axis3_unit_vector = element_axis3_vector / numpy.linalg.norm(element_axis3_vector)
                            element_axis1_vector = ref_axis_x_vector-numpy.dot(ref_axis_x_vector,element_axis3_unit_vector) / numpy.dot(element_axis3_unit_vector,element_axis3_unit_vector) * element_axis3_unit_vector
                            if numpy.all(element_axis1_vector==0.0):
                                element_axis1_vector = ref_axis_y_vector-numpy.dot(ref_axis_y_vector,element_axis3_unit_vector) / numpy.dot(element_axis3_unit_vector,element_axis3_unit_vector) * element_axis3_unit_vector
                            else:
                                pass
                            element_axis1_unit_vector = element_axis1_vector / numpy.linalg.norm(element_axis1_vector)
                            element_axis2_vector = numpy.cross(element_axis3_unit_vector,element_axis1_unit_vector)
                            element_axis2_unit_vector = element_axis2_vector / numpy.linalg.norm(element_axis2_vector)
                            del ins_element_reference_transformer

                            ins_element_transform_matrix = vtk.vtkMatrix4x4()
                            ins_element_transform_matrix.Zero()
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,0,element_axis1_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,1,element_axis2_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,2,element_axis3_unit_vector[i])
                            ins_element_transform_matrix.SetElement(0,3,element_orientation_parameters_list[0])
                            ins_element_transform_matrix.SetElement(1,3,element_orientation_parameters_list[1])
                            ins_element_transform_matrix.SetElement(2,3,element_orientation_parameters_list[2])
                            ins_element_transform_matrix.SetElement(3,3,1.0)
                            
                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.SetMatrix(ins_element_transform_matrix)
                            if raxis_number == 3:
                                ins_element_transformer.RotateZ(angle_value)
                            else:
                                pass
                            
                            elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                            
                            del ins_element_transformer
                            del ins_element_transform_matrix
                        else:
                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                            if raxis_number == 1:
                                ins_element_transformer.RotateX(angle_value)
                            elif raxis_number == 2:
                                ins_element_transformer.RotateY(angle_value)
                            elif raxis_number == 3:
                                ins_element_transformer.RotateZ(angle_value)
                            else:
                                pass
                            
                            elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                            del ins_element_transformer
                elif orientation_assignment_info_dict['type'] == 2:
                    for element_label,element_geometry_type_number,*element_orientation_parameters_list in self.__ins_cursor.fetchall():
                        if element_geometry_type_number in [1,6]:
                            if raxis_number == 1:
                                ins_element_transformer = vtk.vtkTransform()
                                ins_element_transformer.RotateWXYZ(*element_orientation_parameters_list[3:])
                                ins_element_transformer.RotateX(angle_value)
                                    
                                elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                                del ins_element_transformer
                            else:
                                elements_orientation_parameters_dict[element_label] = element_orientation_parameters_list
                        elif element_geometry_type_number in [2,3,7,8]:
                            ref_axis_r_vector = numpy.asarray(element_orientation_parameters_list[0:3]) - numpy.asarray(orientation_assignment_info_dict['origin'])
                            if numpy.all(ref_axis_r_vector==0.0):
                                ins_ref_csys_transformer = vtk.vtkTransform()
                                ins_ref_csys_transformer.Translate(orientation_assignment_info_dict['origin'])
                                ins_ref_csys_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                                ref_axis_r_vector = ins_ref_csys_transformer.TransformVector([1.0,0.0,0.0])
                                ref_axis_t_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                                del ins_ref_csys_transformer
                            else:
                                ins_ref_csys_transformer = vtk.vtkTransform()
                                ins_ref_csys_transformer.Translate(orientation_assignment_info_dict['origin'])
                                ins_ref_csys_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                                ref_axis_z_vector = ins_ref_csys_transformer.TransformVector([0.0,0.0,1.0])
                                
                                ref_axis_r_vector = ref_axis_r_vector-numpy.dot(ref_axis_r_vector,ref_axis_z_vector) / numpy.dot(ref_axis_z_vector,ref_axis_z_vector) * ref_axis_z_vector
                                if numpy.all(ref_axis_r_vector==0.0):
                                    ref_axis_r_vector = ins_ref_csys_transformer.TransformVector([1.0,0.0,0.0])
                                    ref_axis_t_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                                else:
                                    ref_axis_t_vector = numpy.cross(ref_axis_z_vector,ref_axis_r_vector)
                                
                                del ins_ref_csys_transformer
                                    
                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.Translate(element_orientation_parameters_list[0:3])
                            ins_element_transformer.RotateWXYZ(*element_orientation_parameters_list[3:])
                            
                            element_axis3_vector = ins_element_transformer.TransformVector([0.0,0.0,1.0])
                            element_axis3_unit_vector = element_axis3_vector / numpy.linalg.norm(element_axis3_vector)
                            element_axis1_vector = ref_axis_r_vector-numpy.dot(ref_axis_r_vector,element_axis3_unit_vector) / numpy.dot(element_axis3_unit_vector,element_axis3_unit_vector) * element_axis3_unit_vector
                            if numpy.all(element_axis1_vector==0.0):
                                element_axis1_vector = ref_axis_t_vector-numpy.dot(ref_axis_t_vector,element_axis3_unit_vector) / numpy.dot(element_axis3_unit_vector,element_axis3_unit_vector) * element_axis3_unit_vector
                            else:
                                pass
                            element_axis1_unit_vector = element_axis1_vector / numpy.linalg.norm(element_axis1_vector)
                            element_axis2_vector = numpy.cross(element_axis3_unit_vector,element_axis1_unit_vector)
                            element_axis2_unit_vector = element_axis2_vector / numpy.linalg.norm(element_axis2_vector)

                            ins_element_transform_matrix = vtk.vtkMatrix4x4()
                            ins_element_transform_matrix.Zero()
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,0,element_axis1_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,1,element_axis2_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,2,element_axis3_unit_vector[i])
                            ins_element_transform_matrix.SetElement(0,3,element_orientation_parameters_list[0])
                            ins_element_transform_matrix.SetElement(1,3,element_orientation_parameters_list[1])
                            ins_element_transform_matrix.SetElement(2,3,element_orientation_parameters_list[2])
                            ins_element_transform_matrix.SetElement(3,3,1.0)
                            
                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.SetMatrix(ins_element_transform_matrix)
                            if raxis_number == 3:
                                ins_element_transformer.RotateZ(angle_value)
                            else:
                                pass
                            
                            elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                            
                            del ins_element_transformer 
                            del ins_element_transform_matrix
                        else:
                            ins_ref_csys_transformer = vtk.vtkTransform()
                            ins_ref_csys_transformer.Translate(orientation_assignment_info_dict['origin'])
                            ins_ref_csys_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                            ref_axis_r_vector = ins_ref_csys_transformer.TransformVector([1.0,0.0,0.0])
                            ref_axis_t_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                            ref_axis_z_vector = ins_ref_csys_transformer.TransformVector([0.0,0.0,1.0])
                            del ins_ref_csys_transformer
                            
                            element_axis1_vector = numpy.asarray(element_orientation_parameters_list[0:3]) - numpy.asarray(orientation_assignment_info_dict['origin'])
                            if numpy.all(element_axis1_vector==0.0):
                                element_axis1_vector = ref_axis_r_vector
                            else:
                                element_axis1_vector = element_axis1_vector-numpy.dot(element_axis1_vector,ref_axis_z_vector) / numpy.dot(ref_axis_z_vector,ref_axis_z_vector) * ref_axis_z_vector
                                if numpy.all(element_axis1_vector==0.0):
                                    element_axis1_vector = ref_axis_r_vector
                                else:
                                    pass
                            element_axis1_unit_vector = element_axis1_vector / numpy.linalg.norm(element_axis1_vector)
                            
                            element_axis3_vector = ref_axis_z_vector
                            element_axis3_unit_vector = element_axis3_vector / numpy.linalg.norm(element_axis3_vector)
                            element_axis2_vector = numpy.cross(element_axis3_unit_vector,element_axis1_unit_vector)
                            element_axis2_unit_vector = element_axis2_vector / numpy.linalg.norm(element_axis2_vector)

                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.SetMatrix(ins_element_transform_matrix)
                            if raxis_number == 1:
                                ins_element_transformer.RotateX(angle_value)
                            elif raxis_number == 2:
                                ins_element_transformer.RotateY(angle_value)
                            elif raxis_number == 3:
                                ins_element_transformer.RotateZ(angle_value)
                            else:
                                pass
                            
                            elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                            
                            del ins_element_transformer
                            del ins_element_transform_matrix
                elif orientation_assignment_info_dict['type'] == 3:
                    for element_label,element_geometry_type_number,*element_orientation_parameters_list in self.__ins_cursor.fetchall():
                        if element_geometry_type_number in [1,6]:
                            if raxis_number == 1:
                                ins_element_transformer = vtk.vtkTransform()
                                ins_element_transformer.RotateWXYZ(*element_orientation_parameters_list[3:])
                                ins_element_transformer.RotateX(angle_value)
                                    
                                elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                                del ins_element_transformer
                            else:
                                elements_orientation_parameters_dict[element_label] = element_orientation_parameters_list
                        elif element_geometry_type_number in [2,3,7,8]:
                            ref_axis_r_vector = numpy.asarray(element_orientation_parameters_list[0:3]) - numpy.asarray(orientation_assignment_info_dict['origin'])
                            if numpy.all(ref_axis_r_vector==0.0):
                                ins_ref_csys_transformer = vtk.vtkTransform()
                                ins_ref_csys_transformer.Translate(orientation_assignment_info_dict['origin'])
                                ins_ref_csys_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                                ref_axis_r_vector = ins_ref_csys_transformer.TransformVector([1.0,0.0,0.0])
                                ref_axis_t_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                                ref_axis_p_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                                del ins_ref_csys_transformer
                            else:
                                ins_ref_csys_transformer = vtk.vtkTransform()
                                ins_ref_csys_transformer.Translate(orientation_assignment_info_dict['origin'])
                                ins_ref_csys_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                                ref_axis_p_vector = ins_ref_csys_transformer.TransformVector([0.0,0.0,1.0])
                                
                                ref_axis_r_vector = ref_axis_r_vector-numpy.dot(ref_axis_r_vector,ref_axis_p_vector) / numpy.dot(ref_axis_p_vector,ref_axis_p_vector) * ref_axis_p_vector
                                if numpy.all(ref_axis_r_vector==0.0):
                                    ref_axis_r_vector = ins_ref_csys_transformer.TransformVector([1.0,0.0,0.0])
                                    ref_axis_t_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                                else:
                                    ref_axis_t_vector = numpy.cross(ref_axis_p_vector,ref_axis_r_vector)
                                    ref_axis_p_vector = numpy.cross(ref_axis_r_vector,ref_axis_t_vector)
                                
                                del ins_ref_csys_transformer
                                    
                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.Translate(element_orientation_parameters_list[0:3])
                            ins_element_transformer.RotateWXYZ(*element_orientation_parameters_list[3:])
                            
                            element_axis3_vector = ins_element_transformer.TransformVector([0.0,0.0,1.0])
                            element_axis3_unit_vector = element_axis3_vector / numpy.linalg.norm(element_axis3_vector)
                            element_axis1_vector = ref_axis_r_vector-numpy.dot(ref_axis_r_vector,element_axis3_unit_vector) / numpy.dot(element_axis3_unit_vector,element_axis3_unit_vector) * element_axis3_unit_vector
                            if numpy.all(element_axis1_vector==0.0):
                                element_axis1_vector = ref_axis_t_vector-numpy.dot(ref_axis_t_vector,element_axis3_unit_vector) / numpy.dot(element_axis3_unit_vector,element_axis3_unit_vector) * element_axis3_unit_vector
                            else:
                                pass
                            element_axis1_unit_vector = element_axis1_vector / numpy.linalg.norm(element_axis1_vector)
                            element_axis2_vector = numpy.cross(element_axis3_unit_vector,element_axis1_unit_vector)
                            element_axis2_unit_vector = element_axis2_vector / numpy.linalg.norm(element_axis2_vector)

                            ins_element_transform_matrix = vtk.vtkMatrix4x4()
                            ins_element_transform_matrix.Zero()
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,0,element_axis1_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,1,element_axis2_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,2,element_axis3_unit_vector[i])
                            ins_element_transform_matrix.SetElement(0,3,element_orientation_parameters_list[0])
                            ins_element_transform_matrix.SetElement(1,3,element_orientation_parameters_list[1])
                            ins_element_transform_matrix.SetElement(2,3,element_orientation_parameters_list[2])
                            ins_element_transform_matrix.SetElement(3,3,1.0)
                            
                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.SetMatrix(ins_element_transform_matrix)
                            if raxis_number == 3:
                                ins_element_transformer.RotateZ(angle_value)
                            else:
                                pass
                            
                            elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                            
                            del ins_element_transformer
                            del ins_element_transform_matrix
                        else:
                            ref_axis_r_vector = numpy.asarray(element_orientation_parameters_list[0:3]) - numpy.asarray(orientation_assignment_info_dict['origin'])
                            if numpy.all(ref_axis_r_vector==0.0):
                                ins_ref_csys_transformer = vtk.vtkTransform()
                                ins_ref_csys_transformer.Translate(orientation_assignment_info_dict['origin'])
                                ins_ref_csys_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                                ref_axis_r_vector = ins_ref_csys_transformer.TransformVector([1.0,0.0,0.0])
                                ref_axis_t_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                                ref_axis_p_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                                del ins_ref_csys_transformer
                            else:
                                ins_ref_csys_transformer = vtk.vtkTransform()
                                ins_ref_csys_transformer.Translate(orientation_assignment_info_dict['origin'])
                                ins_ref_csys_transformer.RotateWXYZ(*orientation_assignment_info_dict['rotation'])
                                ref_axis_p_vector = ins_ref_csys_transformer.TransformVector([0.0,0.0,1.0])
                                
                                ref_axis_r_vector = ref_axis_r_vector-numpy.dot(ref_axis_r_vector,ref_axis_p_vector) / numpy.dot(ref_axis_p_vector,ref_axis_p_vector) * ref_axis_p_vector
                                if numpy.all(ref_axis_r_vector==0.0):
                                    ref_axis_r_vector = ins_ref_csys_transformer.TransformVector([1.0,0.0,0.0])
                                    ref_axis_t_vector = ins_ref_csys_transformer.TransformVector([0.0,1.0,0.0])
                                else:
                                    ref_axis_t_vector = numpy.cross(ref_axis_p_vector,ref_axis_r_vector)
                                    ref_axis_p_vector = numpy.cross(ref_axis_r_vector,ref_axis_t_vector)
                                
                                del ins_ref_csys_transformer
                            
                            element_axis1_vector = ref_axis_r_vector
                            element_axis2_vector = ref_axis_t_vector
                            element_axis3_vector = ref_axis_p_vector
                            
                            element_axis1_unit_vector = element_axis1_vector / numpy.linalg.norm(element_axis1_vector)
                            element_axis2_unit_vector = element_axis2_vector / numpy.linalg.norm(element_axis2_vector)
                            element_axis3_unit_vector = element_axis3_vector / numpy.linalg.norm(element_axis3_vector)

                            ins_element_transform_matrix = vtk.vtkMatrix4x4()
                            ins_element_transform_matrix.Zero()
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,0,element_axis1_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,1,element_axis2_unit_vector[i])
                            for i in range(3):
                                ins_element_transform_matrix.SetElement(i,2,element_axis3_unit_vector[i])
                            ins_element_transform_matrix.SetElement(0,3,element_orientation_parameters_list[0])
                            ins_element_transform_matrix.SetElement(1,3,element_orientation_parameters_list[1])
                            ins_element_transform_matrix.SetElement(2,3,element_orientation_parameters_list[2])
                            ins_element_transform_matrix.SetElement(3,3,1.0)
                            
                            ins_element_transformer = vtk.vtkTransform()
                            ins_element_transformer.SetMatrix(ins_element_transform_matrix)
                            if raxis_number == 1:
                                ins_element_transformer.RotateX(angle_value)
                            elif raxis_number == 2:
                                ins_element_transformer.RotateY(angle_value)
                            elif raxis_number == 3:
                                ins_element_transformer.RotateZ(angle_value)
                            else:
                                pass
                            
                            elements_orientation_parameters_dict[element_label] = [*element_orientation_parameters_list[0:3],*[i for i in ins_element_transformer.GetOrientationWXYZ()]]
                            
                            del ins_element_transformer
                            del ins_element_transform_matrix
                else:
                    pass
        else:
            pass
        
        return elements_orientation_parameters_dict
    
    def getMaterialInformation(self, in_model_name:str, in_material_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        material_info_dict = {}
        
        self.__ins_cursor.execute('SELECT elasticity,eparams FROM materials WHERE model=? AND name=?',[model_id,in_material_name])
        elasticity_type_number,elasticity_parameters_string = self.__ins_cursor.fetchone()
        if elasticity_type_number == 1:
            material_info_dict['elasticity'] = {'type':'elastic'}
            
            parameters_list = elasticity_parameters_string.split(',')
            if parameters_list[0] == '1':
                material_info_dict['elasticity']['constitutive model'] = 'isotropic'
            else:
                pass
            
            material_info_dict['elasticity']['constitutive parameters'] = [float(i) for i in parameters_list[1:]]
        else:
            pass
        
        return material_info_dict
    def createMaterial(self, in_model_name:str, in_material_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        if in_material_info['elasticity']['type'] == 'elastic':
            elasticity_type_number = 1
            
            if in_material_info['elasticity']['constitutive model'] == 'isotropic':
                elasticity_parameters = ','.join(['1',*[str(i) for i in in_material_info['elasticity']['constitutive parameters']]])
            else:
                pass
        else:
            pass
        
        self.__ins_cursor.execute('INSERT INTO materials(model,name,elasticity,eparams) VALUES(?,?,?,?)',[model_id,in_material_info['name'],elasticity_type_number,elasticity_parameters])
    def renameMaterial(self, in_model_name:str, in_old_material_name:str, in_new_material_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('UPDATE materials SET name=? WHERE model=? AND name=?',[in_new_material_name,model_id,in_old_material_name])
    def editMaterial(self, in_model_name:str, in_material_name:str, in_material_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        if in_material_info['elasticity']['type'] == 'elastic':
            elasticity_type_number = 1
            
            if in_material_info['elasticity']['constitutive model'] == 'isotropic':
                elasticity_parameters = ','.join(['1',*[str(i) for i in in_material_info['elasticity']['constitutive parameters']]])
            else:
                pass
        
            self.__ins_cursor.execute('UPDATE materials SET elasticity=?,eparams=? WHERE model=? AND name=?',[elasticity_type_number,elasticity_parameters,model_id,in_material_name])
        else:
            pass
    def removeMaterial(self, in_model_name:str, in_material_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM materials WHERE model=? AND name=?',[model_id,in_material_name])
        material_id = self.__ins_cursor.fetchone()[0]
        
        associated_property_assignments_gruops_dict_by_part = {}
        
        self.__ins_cursor.execute('SELECT id,part,pgroup FROM property_assignments WHERE model=? AND (geo1_material=? OR geo2_material=? OR \
                                    geo3_material=? OR geo4_material=? OR geo5_material=? OR geo6_material=? OR geo7_material=? OR geo8_material=? OR \
                                    geo9_material=? OR geo10_material=?)',[model_id,material_id,material_id,material_id,material_id,material_id,material_id,material_id,material_id,material_id,material_id])
        associated_property_assignments_info_list = self.__ins_cursor.fetchall()
        for property_assignment_id,part_id,group_id in associated_property_assignments_info_list:
            self.__ins_cursor.execute(f'DELETE FROM property_assignments WHERE model=? AND id=?',[model_id, property_assignment_id])

            self.__ins_cursor.execute(f'UPDATE {"part_"+str(part_id)+"_elements"} SET property=NULL WHERE {"pg_"+str(group_id)}=1')

            self.__ins_cursor.execute('SELECT name FROM parts WHERE model=? AND id=?',[model_id,part_id])
            part_name = self.__ins_cursor.fetchone()[0]
            self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=? AND id=? AND type=2',[model_id,part_id,group_id])
            group_name = self.__ins_cursor.fetchone()[0]
            if part_name in associated_property_assignments_gruops_dict_by_part:
                associated_property_assignments_gruops_dict_by_part[part_name].append(group_name)
            else:
                associated_property_assignments_gruops_dict_by_part[part_name] = [group_name]
        
        return associated_property_assignments_gruops_dict_by_part
        
    def getAttributesByType(self,in_model_name:str) -> None:
        self.__ins_cursor.execute('SELECT id,dimension FROM models WHERE name=?',[in_model_name])
        model_id,model_dimension = self.__ins_cursor.fetchone()[0:2]

        if model_dimension == '2D':
            attributes_by_type_dict = {flag_name:[] for flag_name in common.P4SElementInfo.FLAG_2D}
        elif model_dimension == '3D':
            attributes_by_type_dict = {flag_name:[] for flag_name in common.P4SElementInfo.FLAG_3D}
        else:
            pass
        
        self.__ins_cursor.execute('SELECT name,type FROM attributes WHERE model=?',[model_id])
        for i in self.__ins_cursor.fetchall():
            attributes_by_type_dict[common.P4SElementInfo.NUMBER_TO_FLAG[i[1]]].append(i[0])

        return attributes_by_type_dict
    def getAttributeInformation(self, in_model_name:str, in_attribute_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        attribute_info_dict = {}
        
        self.__ins_cursor.execute('SELECT type,parameters FROM attributes WHERE model=? AND name=?',[model_id,in_attribute_name])
        attribute_type_number,attribute_parameters_string = self.__ins_cursor.fetchone()
        attribute_info_dict['type'] = common.P4SElementInfo.NUMBER_TO_FLAG[attribute_type_number]
        
        if attribute_info_dict['type'] == 'truss':
            attribute_info_dict['parameters'] = [float(attribute_parameters_string)]
        elif attribute_info_dict['type'] == 'beam':
            pass
        elif attribute_info_dict['type'] == 'plane':
            attribute_info_dict['parameters'] = [float(attribute_parameters_string)]
        elif attribute_info_dict['type'] == 'shell':
            attribute_info_dict['parameters'] = [float(i) for i in attribute_parameters_string.split(',')]
            if len(attribute_info_dict['parameters']) == 1:
                pass
            else:
                attribute_info_dict['parameters'][0] = int(attribute_info_dict['parameters'][0])
                attribute_info_dict['parameters'][2] = int(attribute_info_dict['parameters'][2])
        elif attribute_info_dict['type'] == 'solid':
            pass
        else:
            pass
            
        return attribute_info_dict
    def createAttribute(self, in_model_name:str, in_attribute_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        attribute_type =  common.P4SElementInfo.FLAG_TO_NUMBER[in_attribute_info['type']]
        if in_attribute_info['type'] == 'solid':
            attribute_parameters_string = None
        else:
            attribute_parameters_string = ','.join([str(param) for param in in_attribute_info['parameters']])
        
        self.__ins_cursor.execute('INSERT INTO attributes(model,name,type,parameters) VALUES(?,?,?,?)',[model_id,in_attribute_info['name'],attribute_type,attribute_parameters_string])
    def renameAttribute(self, in_model_name:str, in_old_attribute_name:str, in_new_attribute_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('UPDATE attributes SET name=? WHERE model=? AND name=?',[in_new_attribute_name,model_id,in_old_attribute_name])
    def editAttribute(self, in_model_name:str, in_attribute_name:str, in_attribute_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        attribute_type =  common.P4SElementInfo.FLAG_TO_NUMBER[in_attribute_info['type']]
        if in_attribute_info['type'] == 'solid':
            attribute_parameters_string = None
        else:
            attribute_parameters_string = ','.join([str(param) for param in in_attribute_info['parameters']])
        
        self.__ins_cursor.execute('UPDATE attributes SET type=?,parameters=? WHERE model=? AND name=?',[attribute_type,attribute_parameters_string,model_id,in_attribute_name])
    def removeAttribute(self, in_model_name:str, in_attribute_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM attributes WHERE model=? AND name=?',[model_id,in_attribute_name])
        attribute_id = self.__ins_cursor.fetchone()[0]
        
        associated_property_assignments_gruops_dict_by_part = {}
        
        self.__ins_cursor.execute('SELECT id,part,pgroup FROM property_assignments WHERE model=? AND (geo1_attribute=? OR geo2_attribute=? OR \
                                    geo3_attribute=? OR geo4_attribute=? OR geo5_attribute=? OR geo6_attribute=? OR geo7_attribute=? OR geo8_attribute=? OR \
                                    geo9_attribute=? OR geo10_attribute=?)',[model_id,attribute_id,attribute_id,attribute_id,attribute_id,attribute_id,attribute_id,attribute_id,attribute_id,attribute_id,attribute_id])
        associated_property_assignments_info_list = self.__ins_cursor.fetchall()
        for property_assignment_id,part_id,group_id in associated_property_assignments_info_list:
            self.__ins_cursor.execute(f'DELETE FROM property_assignments WHERE model=? AND id=?',[model_id, property_assignment_id])

            self.__ins_cursor.execute(f'UPDATE {"part_"+str(part_id)+"_elements"} SET property=NULL WHERE {"pg_"+str(group_id)}=1')

            self.__ins_cursor.execute('SELECT name FROM parts WHERE model=? AND id=?',[model_id,part_id])
            part_name = self.__ins_cursor.fetchone()[0]
            self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=? AND id=? AND type=2',[model_id,part_id,group_id])
            group_name = self.__ins_cursor.fetchone()[0]
            if part_name in associated_property_assignments_gruops_dict_by_part:
                associated_property_assignments_gruops_dict_by_part[part_name].append(group_name)
            else:
                associated_property_assignments_gruops_dict_by_part[part_name] = [group_name]
        
        return associated_property_assignments_gruops_dict_by_part
    
    def getInstanceSourcePart(self, in_model_name:str, in_instance_name:str) -> str:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT part FROM assembly WHERE model=? AND name=?',[model_id,in_instance_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT name FROM parts WHERE model=? AND id=?',[model_id,part_id])
        return self.__ins_cursor.fetchone()[0]
    def getInstanceOrientation(self, in_model_name:str, in_instance_name:str) -> list:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT ox,oy,oz,ori1,ori2,ori3,ori4 FROM assembly WHERE model=? AND name=?',[model_id,in_instance_name])
        return [i for i in self.__ins_cursor.fetchone()]
    def createInstanceFromPart(self, in_model_name:str, in_part_name:str, in_instance_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM parts WHERE model=? AND name=?',[model_id,in_part_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute(f'INSERT INTO assembly(model,part,name,ox,oy,oz,ori1,ori2,ori3,ori4) VALUES(?,?,?,?,?,?,?,?,?,?)',[model_id,part_id,in_instance_name,0.0,0.0,0.0,0.0,0.0,0.0,1.0])
    def renameInstance(self, in_model_name:str, in_old_instance_name:str, in_new_instance_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('UPDATE assembly SET name=? WHERE model=? AND name=?',[in_new_instance_name,model_id,in_old_instance_name])
    def editInstanceOrientation(self, in_model_name:str, in_instance_name:str, in_type:str, in_assembly_coordinate_system_info:dict, in_direction:str, in_value:float) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT ox,oy,oz,ori1,ori2,ori3,ori4 FROM assembly WHERE model=? AND name=?',[model_id,in_instance_name])
        ox,oy,oz,ori1,ori2,ori3,ori4 = self.__ins_cursor.fetchone()
        ins_instance_transformer = vtk.vtkTransform()
        ins_instance_transformer.PostMultiply()
        ins_instance_transformer.RotateWXYZ(ori1,ori2,ori3,ori4)
        ins_instance_transformer.Translate(ox,oy,oz)
        
        ins_assembly_coordinate_system_transformer = vtk.vtkTransform()
        ins_assembly_coordinate_system_transformer.PostMultiply()
        ins_assembly_coordinate_system_transformer.Translate(in_assembly_coordinate_system_info['origin'])
        ins_assembly_coordinate_system_transformer.RotateWXYZ(*in_assembly_coordinate_system_info['orientation'])
        if in_type == 'translate':
            if in_direction == '1':
                global_translate_vector = ins_assembly_coordinate_system_transformer.TransformVector(in_value,0.0,0.0)
            elif in_direction == '2':
                global_translate_vector = ins_assembly_coordinate_system_transformer.TransformVector(0.0,in_value,0.0)
            elif in_direction == '3':
                global_translate_vector = ins_assembly_coordinate_system_transformer.TransformVector(0.0,0.0,in_value)
            else:
                pass
        
            ins_instance_transformer.Translate(global_translate_vector)
        elif in_type == 'rotate':
            ins_instance_transformer.Translate([-i for i in in_assembly_coordinate_system_info['origin']])
            
            if in_direction == '1':
                global_rotation_axis = ins_assembly_coordinate_system_transformer.TransformVector(1.0,0.0,0.0)
            elif in_direction == '2':
                global_rotation_axis = ins_assembly_coordinate_system_transformer.TransformVector(0.0,1.0,0.0)
            elif in_direction == '3':
                global_rotation_axis = ins_assembly_coordinate_system_transformer.TransformVector(0.0,0.0,1.0)
            else:
                pass
            ins_instance_transformer.RotateWXYZ(in_value,*global_rotation_axis)
            
            ins_instance_transformer.Translate(in_assembly_coordinate_system_info['origin'])
        else:
            pass
        
        self.__ins_cursor.execute('UPDATE assembly SET ox=?,oy=?,oz=?,ori1=?,ori2=?,ori3=?,ori4=? WHERE model=? AND name=?',[*ins_instance_transformer.GetPosition(),*ins_instance_transformer.GetOrientationWXYZ(),model_id,in_instance_name])
    def removeInstance(self, in_model_name:str, in_instance_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]

        self.__ins_cursor.execute('SELECT part,id FROM assembly WHERE model=? AND name=?',[model_id,in_instance_name])
        part_id,instance_id = self.__ins_cursor.fetchone()
        self.__ins_cursor.execute('DELETE FROM assembly WHERE model=? AND id=?',[model_id,instance_id])
        
        association_info_dict = {'agroups':{'nodes':[],'elements':[]},'outputs':[],'conditions':[]}
        self.__ins_cursor.execute('SELECT agroup FROM groups_instances_association WHERE model=? AND instance=?',[model_id,instance_id])
        instance_associated_agroups_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
        for agroup_id in instance_associated_agroups_id_list:
            self.__ins_cursor.execute('SELECT type FROM groups WHERE model=? AND id=?',[model_id,agroup_id])
            agroup_type_number = self.__ins_cursor.fetchone()[0]
            
            self.__ins_cursor.execute('SELECT COUNT(*) FROM groups_instances_association WHERE model=? AND agroup=?',[model_id,agroup_id])
            agroup_include_instances_number = self.__ins_cursor.fetchone()[0]
            if agroup_include_instances_number == 1:
                self.__ins_cursor.execute('SELECT name,type FROM groups WHERE model=? AND id=?',[model_id,agroup_id])
                agroup_name,agroup_type = self.__ins_cursor.fetchone()
                if agroup_type == 1:
                    association_info_dict['agroups']['nodes'].append(agroup_name)
                elif agroup_type == 2:
                    association_info_dict['agroups']['elements'].append(agroup_name)
                else:
                    pass
                self.__ins_cursor.execute('DELETE FROM groups WHERE model=? AND id=?',[model_id,agroup_id])
                
                self.__ins_cursor.execute('SELECT name FROM outputs WHERE model=? AND agroup=?',[model_id,agroup_id])
                agroup_associated_outputs_list = [i[0] for i in self.__ins_cursor.fetchall()]
                for output_name in agroup_associated_outputs_list:
                    if output_name in association_info_dict['outputs']:
                        continue
                    else:
                        association_info_dict['outputs'].append(output_name)
                self.__ins_cursor.execute('DELETE FROM outputs WHERE model=? AND agroup=?',[model_id,agroup_id])
                
                self.__ins_cursor.execute('SELECT name FROM boundary_conditions WHERE model=? AND agroup=?',[model_id,agroup_id])
                agroup_associated_conditions_list = [i[0] for i in self.__ins_cursor.fetchall()]
                for condition_name in agroup_associated_conditions_list:
                    if condition_name in association_info_dict['conditions']:
                        continue
                    else:
                        association_info_dict['conditions'].append(condition_name)
                self.__ins_cursor.execute('DELETE FROM boundary_conditions WHERE model=? AND agroup=?',[model_id,agroup_id])
            else:
                pass

            if agroup_type_number == 1:
                self.__ins_cursor.execute(f'ALTER TABLE {"part_"+str(part_id)+"_nodes"} DROP COLUMN {"ag_"+str(instance_id)+"_"+str(agroup_id)}')
            elif agroup_type_number == 2:
                self.__ins_cursor.execute(f'ALTER TABLE {"part_"+str(part_id)+"_elements"} DROP COLUMN {"ag_"+str(instance_id)+"_"+str(agroup_id)}')
            else:
                pass

        self.__ins_cursor.execute('DELETE FROM groups_instances_association WHERE model=? AND instance=?',[model_id,instance_id])
        return association_info_dict
    
    def getInstanceIncludePartGroups(self, in_model_name:str, in_group_type:str, in_instance_name:str) -> list:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT part FROM assembly WHERE model=? AND name=?',[model_id,in_instance_name])
        part_id = self.__ins_cursor.fetchone()[0]
        
        if in_group_type == 'node':
            self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=? AND type=?',[model_id,part_id,1])
        elif in_group_type == 'element':
            self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=? AND type=?',[model_id,part_id,2])
        else:
            pass
        
        return [i[0] for i in self.__ins_cursor.fetchall()]
    def getAssemblyGroupLabels(self, in_model_name:str, in_group_type:str, in_group_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        if in_group_type == 'node':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=0 AND name=? AND type=1',[model_id,in_group_name])
        elif in_group_type == 'element':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=0 AND name=? AND type=2',[model_id,in_group_name])
        else:
            pass
        group_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT instance FROM groups_instances_association WHERE agroup=?',[group_id])
        associated_instance_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
        associated_instance_include_labels_dict = {}
        for instance_id in associated_instance_id_list:
            self.__ins_cursor.execute('SELECT part,name FROM assembly WHERE model=? AND id=?',[model_id,instance_id])
            part_id,instance_name = self.__ins_cursor.fetchone()
            
            self.__ins_cursor.execute(f'SELECT id FROM {"part_"+str(part_id)+"_"+in_group_type+"s"} WHERE {"ag_"+str(instance_id)+"_"+str(group_id)}=1')
            associated_instance_include_labels_dict[instance_name] = [i[0] for i in self.__ins_cursor.fetchall()]
        
        return associated_instance_include_labels_dict
    def createAssemblyGroupFromSelection(self, in_model_name:str, in_type:str, in_assembly_group_name:str, in_include_labels:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        group_include_labels_number = 0
        for instance_labels in in_include_labels.values():
            group_include_labels_number += len(instance_labels)
        
        if in_type == 'node':
            self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,0,in_assembly_group_name,1,group_include_labels_number])
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=?',[model_id,0,in_assembly_group_name,1])
            group_id = self.__ins_cursor.fetchone()[0]
            
            for instance_name in in_include_labels:
                self.__ins_cursor.execute('SELECT part,id FROM assembly WHERE model=? AND name=?',[model_id,instance_name])
                part_id,instance_id = self.__ins_cursor.fetchone()
            
                self.__ins_cursor.execute('INSERT INTO groups_instances_association(model,agroup,instance) VALUES(?,?,?)',[model_id,group_id,instance_id])

                part_table_name = f'part_{str(part_id)}_nodes'
                self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} ADD COLUMN {"ag_"+str(instance_id)+"_"+str(group_id)} INTEGER')
                self.__ins_cursor.executemany(f'UPDATE {part_table_name} SET {"ag_"+str(instance_id)+"_"+str(group_id)}=1 WHERE id=?',[[label] for label in in_include_labels[instance_name]])        
        elif in_type == 'element':
            self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,0,in_assembly_group_name,2,group_include_labels_number])
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=?',[model_id,0,in_assembly_group_name,2])
            group_id = self.__ins_cursor.fetchone()[0]
            
            for instance_name in in_include_labels:
                self.__ins_cursor.execute('SELECT id,part FROM assembly WHERE model=? AND name=?',[model_id,instance_name])
                instance_id,part_id = self.__ins_cursor.fetchone()
                
                self.__ins_cursor.execute('INSERT INTO groups_instances_association(model,agroup,instance) VALUES(?,?,?)',[model_id,group_id,instance_id])
            
                part_table_name = f'part_{str(part_id)}_elements'
                self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} ADD COLUMN {"ag_"+str(instance_id)+"_"+str(group_id)} INTEGER')
                self.__ins_cursor.executemany(f'UPDATE {part_table_name} SET {"ag_"+str(instance_id)+"_"+str(group_id)}=1 WHERE id=?',[[label] for label in in_include_labels[instance_name]])        
        else:
            pass
    def createAssemblyGroupFromPart(self, in_model_name:str, in_type:str, in_group_info:list) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT part,id FROM assembly WHERE model=? AND name=?',[model_id,in_group_info[1]])
        part_id,instance_id = self.__ins_cursor.fetchone()
        
        
        if in_type == 'node':
            group_type_number = 1
            
            part_table_name = 'part_' + str(part_id) + '_nodes'
        elif in_type == 'element':
            group_type_number = 2
        
            part_table_name = 'part_' + str(part_id) + '_elements'
        else:
            pass
        self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=?',[model_id,part_id,in_group_info[2],group_type_number])
        part_group_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute(f'SELECT COUNT(id) FROM {part_table_name} WHERE {"pg_"+str(part_group_id)}=1')
        assembly_group_number = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('INSERT INTO groups(model,sign,name,type,number) VALUES(?,?,?,?,?)',[model_id,0,in_group_info[0],group_type_number,assembly_group_number])
        self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=?',[model_id,0,in_group_info[0],group_type_number])
        assembly_group_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} ADD COLUMN {"ag_"+str(instance_id)+"_"+str(assembly_group_id)} INTEGER')
        self.__ins_cursor.execute(f'UPDATE {part_table_name} SET {"ag_"+str(instance_id)+"_"+str(assembly_group_id)}={"pg_"+str(part_group_id)}')
        
        self.__ins_cursor.execute('INSERT INTO groups_instances_association(model,agroup,instance) VALUES(?,?,?)',[model_id,assembly_group_id,instance_id])
    def renameAssemblyGroup(self, in_model_name:str, in_group_type:str, in_old_group_name:str, in_new_group_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        if in_group_type == 'node':
            self.__ins_cursor.execute('UPDATE groups SET name=? WHERE model=? AND sign=0 AND name=? AND type=1',[in_new_group_name,model_id,in_old_group_name])
        elif in_group_type == 'element':
            self.__ins_cursor.execute('UPDATE groups SET name=? WHERE model=? AND sign=0 AND name=? AND type=2',[in_new_group_name,model_id,in_old_group_name])
        else:
            pass
    def editAssemblyGroupFromSelection(self, in_model_name:str, in_group_type:str, in_assembly_group_name:str, in_include_labels:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
     
        if in_group_type == 'node':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=0 AND name=? AND type=1',[model_id,in_assembly_group_name])
        elif in_group_type == 'element':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=0 AND name=? AND type=2',[model_id,in_assembly_group_name])
        else:
            pass
        group_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT instance FROM groups_instances_association WHERE model=? AND agroup=?',[model_id,group_id])
        instances_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
        for instance_id in instances_id_list:
            self.__ins_cursor.execute('SELECT part,name FROM assembly WHERE model=? AND id=?',[model_id,instance_id])
            part_id,instance_name = self.__ins_cursor.fetchone()
            if instance_name in in_include_labels:
                pass
            else:
                part_table_name = "part_"+str(part_id) +"_"+in_group_type+"s"
                group_column_name = "ag_"+str(instance_id)+"_"+str(group_id)
                
                self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} DROP COLUMN {group_column_name}')
        self.__ins_cursor.execute('DELETE FROM groups_instances_association WHERE model=? AND agroup=?',[model_id,group_id])
        
        for instance_name in in_include_labels:
            self.__ins_cursor.execute('SELECT part,id FROM assembly WHERE model=? AND name=?',[model_id,instance_name])
            part_id,instance_id = self.__ins_cursor.fetchone()
            
            self.__ins_cursor.execute('INSERT INTO groups_instances_association(model,agroup,instance) VALUES(?,?,?)',[model_id,group_id,instance_id])
            
            part_table_name = "part_"+str(part_id) +"_"+in_group_type+"s"
            group_column_name = "ag_"+str(instance_id)+"_"+str(group_id)
            if instance_id in instances_id_list:
                self.__ins_cursor.execute(f'UPDATE {part_table_name} SET {group_column_name}=NULL')
            else:
                self.__ins_cursor.execute(f'ALTER TABLE {part_table_name} ADD COLUMN {group_column_name} INTEGER')
            self.__ins_cursor.executemany(f'UPDATE {part_table_name} SET {group_column_name}=1 WHERE id=?',[[label] for label in in_include_labels[instance_name]])
        
        group_include_lables_number = 0
        for labels_list in in_include_labels.values():
            group_include_lables_number += len(labels_list)
        self.__ins_cursor.execute('UPDATE groups SET number=? WHERE model=? AND id=?',[group_include_lables_number,model_id,group_id])
    def removeAssemblyGroup(self, in_model_name:str, in_group_type:str, in_assembly_group_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        if in_group_type == 'node':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=0 AND name=? AND type=1',[model_id,in_assembly_group_name])
        elif in_group_type == 'element':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=0 AND name=? AND type=2',[model_id,in_assembly_group_name])
        else:
            pass
        agroup_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('DELETE FROM groups WHERE model=? AND id=?',[model_id,agroup_id])
        
        self.__ins_cursor.execute('SELECT instance FROM groups_instances_association WHERE model=? AND agroup=?',[model_id,agroup_id])
        agroup_include_instances_id_list = [i[0] for i in self.__ins_cursor.fetchall()]
        for instance_id in agroup_include_instances_id_list:
            self.__ins_cursor.execute('SELECT part FROM assembly WHERE model=? AND id=?',[model_id,instance_id])
            part_id = self.__ins_cursor.fetchone()[0]

            self.__ins_cursor.execute(f'ALTER TABLE {"part_"+str(part_id)+"_"+in_group_type+"s"} DROP COLUMN {"ag_"+str(instance_id)+"_"+str(agroup_id)}')
        self.__ins_cursor.execute('DELETE FROM groups_instances_association WHERE model=? AND agroup=?',[model_id,agroup_id])
        
        association_info_dict = {'outputs':[],'conditions':[]}
        self.__ins_cursor.execute('SELECT name FROM outputs WHERE model=? AND agroup=?',[model_id,agroup_id])
        group_associated_outputs_list = [i[0] for i in self.__ins_cursor.fetchall()]
        for output_name in group_associated_outputs_list:
            if output_name in association_info_dict['outputs']:
                continue
            else:
                association_info_dict['outputs'].append(output_name)
        self.__ins_cursor.execute('DELETE FROM outputs WHERE model=? AND agroup=?',[model_id,agroup_id])
        self.__ins_cursor.execute('SELECT name FROM boundary_conditions WHERE model=? AND agroup=?',[model_id,agroup_id])
        group_associated_conditions_list = [i[0] for i in self.__ins_cursor.fetchall()]
        for condition_name in group_associated_conditions_list:
            if condition_name in association_info_dict['conditions']:
                continue
            else:
                association_info_dict['conditions'].append(condition_name)
        self.__ins_cursor.execute('DELETE FROM boundary_conditions WHERE model=? AND agroup=?',[model_id,agroup_id])
        
        return association_info_dict

    def getAssemblyNodesCooridnates(self, in_model_name:str, in_instance_include_nodes_label:dict) -> list:
        self.__ins_cursor.execute('SELECT id,dimension FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        nodes_coordinates_list = []
        
        for instance_name,nodes_label in in_instance_include_nodes_label.items():
            self.__ins_cursor.execute('SELECT part,ox,oy,oz,ori1,ori2,ori3,ori4 FROM assembly WHERE model=? AND name=?',[model_id,instance_name])
            part_id,ox,oy,oz,ori1,ori2,ori3,ori4 = self.__ins_cursor.fetchone()
            
            ins_instance_transformer = vtk.vtkTransform()
            ins_instance_transformer.Translate(ox,oy,oz)
            ins_instance_transformer.RotateWXYZ(ori1,ori2,ori3,ori4)
            
            for node_label in nodes_label:
                self.__ins_cursor.execute(f'SELECT x,y,z FROM {"part_"+str(part_id)+"_nodes"} WHERE id=?',[node_label])
                part_node_x,part_node_y,part_node_z = self.__ins_cursor.fetchone()
                
                nodes_coordinates_list.append(ins_instance_transformer.TransformPoint(part_node_x,part_node_y,part_node_z))

        return nodes_coordinates_list
    def getAssemblyCoordinateSystemInfo(self, in_model_name:str, in_coordinate_system_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        if in_coordinate_system_name == 'global':
            assembly_coordinate_system_info_dict = {'type':1,'origin':[0.0,0.0,0.0],'orientation':[0.0,0.0,0.0,1.0]}
        else:
            self.__ins_cursor.execute('SELECT type,ox,oy,oz,ori1,ori2,ori3,ori4 FROM coordinate_systems WHERE model=? AND name=? AND source=?',[model_id,in_coordinate_system_name,0])
            assembly_coordinate_system_info_list = self.__ins_cursor.fetchone()
        
            assembly_coordinate_system_info_dict = {'type':assembly_coordinate_system_info_list[0],'origin':assembly_coordinate_system_info_list[1:4],'orientation':assembly_coordinate_system_info_list[4:]}
        
        return assembly_coordinate_system_info_dict
    def createAssemblyCoordinateSystem(self, in_model_name:str, in_coordinate_system_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        if in_coordinate_system_info['type'] == 'rectangular':
            coordinate_system_type_number = 1
        elif in_coordinate_system_info['type'] == 'cylindrical':
            coordinate_system_type_number = 2
        elif in_coordinate_system_info['type'] == 'spherical':
            coordinate_system_type_number = 3
        else:
            pass
        
        if in_coordinate_system_info['method'] == '3 points':
            point1_x,point1_y,point1_z = in_coordinate_system_info['parameters'][0]
            point2_x,point2_y,point2_z = in_coordinate_system_info['parameters'][1]
            point3_x,point3_y,point3_z = in_coordinate_system_info['parameters'][2]

            vector_x_axis = [point2_x-point1_x,point2_y-point1_y,point2_z-point1_z]
            unit_vector_x_axis = vector_x_axis / numpy.linalg.norm(vector_x_axis)
            vector_xy_plane = [point3_x-point1_x,point3_y-point1_y,point3_z-point1_z]
            vector_z_axis = numpy.cross(unit_vector_x_axis,vector_xy_plane)
            unit_vector_z_axis = vector_z_axis / numpy.linalg.norm(vector_z_axis)
            vector_y_axis = numpy.cross(unit_vector_z_axis, unit_vector_x_axis)
            unit_vector_y_axis = vector_y_axis / numpy.linalg.norm(vector_y_axis)
        
            ins_rotation_transform_matrix = vtk.vtkMatrix4x4()
            ins_rotation_transform_matrix.Zero()
            for i in range(3):
                ins_rotation_transform_matrix.SetElement(i,0,unit_vector_x_axis[i])
            for i in range(3):
                ins_rotation_transform_matrix.SetElement(i,1,unit_vector_y_axis[i])
            for i in range(3):
                ins_rotation_transform_matrix.SetElement(i,2,unit_vector_z_axis[i])
            ins_rotation_transform_matrix.SetElement(0,3,point1_x)
            ins_rotation_transform_matrix.SetElement(1,3,point1_y)
            ins_rotation_transform_matrix.SetElement(2,3,point1_z)
            ins_rotation_transform_matrix.SetElement(3,3,1.0)

            ins_rotation_transformer = vtk.vtkTransform()
            ins_rotation_transformer.SetMatrix(ins_rotation_transform_matrix)

            ori1,ori2,ori3,ori4  = ins_rotation_transformer.GetOrientationWXYZ()

            coordinate_system_data_list = [model_id,in_coordinate_system_info['name'],0,coordinate_system_type_number,point1_x,point1_y,point1_z,ori1,ori2,ori3,ori4]
        elif in_coordinate_system_info['method'] == 'offset':
            point_x,point_y,point_z = in_coordinate_system_info['parameters'][1]
            
            if in_coordinate_system_info['parameters'][0] == 'global':
                coordinate_system_data_list = [model_id,in_coordinate_system_info['name'],0,coordinate_system_type_number,point_x,point_y,point_z,0.0,0.0,0.0,1.0]
            else:
                self.__ins_cursor.execute('SELECT ori1,ori2,ori3,ori4 FROM coordinate_systems WHERE model=? AND source=? AND name=?',[model_id,0,in_coordinate_system_info['parameters'][0]])
                ori1,ori2,ori3,ori4 = self.__ins_cursor.fetchone()
                coordinate_system_data_list = [model_id,in_coordinate_system_info['name'],0,coordinate_system_type_number,point_x,point_y,point_z,ori1,ori2,ori3,ori4]
        else:
            pass
        self.__ins_cursor.execute(f'INSERT INTO coordinate_systems(model,name,source,type,ox,oy,oz,ori1,ori2,ori3,ori4) VALUES(?,?,?,?,?,?,?,?,?,?,?)',coordinate_system_data_list)
    def renameAssemblyCoordinateSystem(self, in_model_name:str, in_old_coordiante_system_name:str, in_new_coordiante_system_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('UPDATE coordinate_systems SET name=? WHERE model=? AND name=? AND source=?',[in_new_coordiante_system_name,model_id,in_old_coordiante_system_name,0])
    def editAssemblyCoordinateSystemLocation(self, in_model_name:str, in_coordinate_system_name:str, in_type:str, in_reference_axis:str, in_value: float) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT ox,oy,oz,ori1,ori2,ori3,ori4 FROM coordinate_systems WHERE model=? AND source=0 AND name=?',[model_id,in_coordinate_system_name])
        ox,oy,oz,ori1,ori2,ori3,ori4 = self.__ins_cursor.fetchone()
        
        ins_coordinate_system_transformer = vtk.vtkTransform()
        ins_coordinate_system_transformer.PostMultiply()
        ins_coordinate_system_transformer.RotateWXYZ(ori1,ori2,ori3,ori4)
        ins_coordinate_system_transformer.Translate(ox,oy,oz)
        
        if in_type == 'translate':
            if in_reference_axis == 'X':
                ins_coordinate_system_transformer.Translate(in_value,0.0,0.0)
            elif in_reference_axis == 'Y':
                ins_coordinate_system_transformer.Translate(0.0,in_value,0.0)
            elif in_reference_axis == 'Z':
                ins_coordinate_system_transformer.Translate(0.0,0.0,in_value)
            else:
                pass
            
            self.__ins_cursor.execute('UPDATE coordinate_systems SET ox=?,oy=?,oz=? WHERE model=? AND name=? AND source=0',[*ins_coordinate_system_transformer.GetPosition(),model_id,in_coordinate_system_name])
        elif in_type == 'rotate':
            if in_reference_axis == 'RX':
                ins_coordinate_system_transformer.RotateX(in_value)
            elif in_reference_axis == 'RY':
                ins_coordinate_system_transformer.RotateY(in_value)
            elif in_reference_axis == 'RZ':
                ins_coordinate_system_transformer.RotateZ(in_value)
            else:
                pass        
            
            self.__ins_cursor.execute('UPDATE coordinate_systems SET ori1=?,ori2=?,ori3=?,ori4=? WHERE model=? AND name=? AND source=0',[*ins_coordinate_system_transformer.GetOrientationWXYZ(),model_id,in_coordinate_system_name])
        else:
            pass
    def removeAssemblyCoordinateSystem(self, in_model_name:str, in_coordinate_system_name:str) -> list:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM coordinate_systems WHERE model=? AND name=? AND source=?',[model_id,in_coordinate_system_name,0])
        coordinate_system_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute(f'DELETE FROM coordinate_systems WHERE id=?',[coordinate_system_id])
        
        self.__ins_cursor.execute('UPDATE boundary_conditions SET csys=0 WHERE model=? AND csys=?',[model_id,coordinate_system_id])

    def getStepInformation(self, in_model_name:str, in_step_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT type,time,nlgeom,basic,lsolver FROM steps WHERE model=? AND name=?',[model_id,in_step_name])
        step_infomation_list = self.__ins_cursor.fetchone()
        
        step_info_dict = {'type':common.P4SStepInfo.NUMBER_TO_STEP_TYPE[step_infomation_list[0]]}       
        
        if step_infomation_list[2] == 1:
            step_info_dict['nlgeom'] = True
        else:
            step_info_dict['nlgeom'] = False
        
        if step_info_dict['type'] == 'static':
            step_info_dict['time'] = str(step_infomation_list[1])
            step_info_dict['basic'] = step_infomation_list[3].split(',')
            step_info_dict['lsolver'] = []
            
            step_info_dict['basic'][1] = common.P4SStepInfo.NUMBER_TO_INCREMENTATION_TYPE[int(step_info_dict['basic'][1])]

            lsolver_string_list = step_infomation_list[4].split(',')
            step_info_dict['lsolver'].append(common.P4SStepInfo.NUMBER_TO_LSOLVER_TYPE[int(lsolver_string_list[0])])
            step_info_dict['lsolver'].append(common.P4SStepInfo.NUMBER_TO_SOLVER_METHOD[int(lsolver_string_list[0])][int(lsolver_string_list[1])])
        else:
            pass
        
        return step_info_dict
    def createStep(self, in_model_name:str, in_step_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        step_type_number = common.P4SStepInfo.STEP_TYPE_TO_NUMBER[in_step_info['type']]
        
        self.__ins_cursor.execute('SELECT COUNT(id) FROM steps WHERE model=?',[model_id])
        step_sequence = self.__ins_cursor.fetchone()[0] + 1
        
        if in_step_info['nlgeom']:
            step_nlgeom = 1
        else:
            step_nlgeom = 0
        
        if step_type_number == 1:
            step_increments_number_string = str(in_step_info['basic'][0])
            step_incrementation_type_string = str(common.P4SStepInfo.INCREMENTATION_TYPE_TO_NUMBER[in_step_info['basic'][1]])
            step_increment_size_params_string = ','.join([str(i) for i in in_step_info['basic'][2:]])
            step_basic_string = step_increments_number_string + ',' + step_incrementation_type_string + ',' + step_increment_size_params_string

            step_lsolver_type_number = common.P4SStepInfo.LSOLVER_TYPE_TO_NUMBER[in_step_info['lsolver'][0]]
            step_lsolver_method_number = common.P4SStepInfo.SOLVER_METHOD_TO_NUMBER[step_lsolver_type_number][in_step_info['lsolver'][1]]
            step_lsolver_string = str(step_lsolver_type_number) + ',' + str(step_lsolver_method_number)
        else:
            pass
        
        self.__ins_cursor.execute('INSERT INTO steps(model,name,type,sequence,time,nlgeom,basic,lsolver) VALUES(?,?,?,?,?,?,?,?)',[model_id,in_step_info['name'],step_type_number,step_sequence,in_step_info['time'],step_nlgeom,step_basic_string,step_lsolver_string])

        self.__ins_cursor.execute('SELECT id,sequence FROM steps WHERE model=? AND name=?',[model_id,in_step_info['name']])
        step_id,step_sequence = self.__ins_cursor.fetchone()
        self.__ins_cursor.execute(f'ALTER TABLE boundary_conditions ADD COLUMN {"step_"+str(step_id)} TEXT')
        
        if step_sequence == 1:
            self.__ins_cursor.execute(f'UPDATE boundary_conditions SET {"step_"+str(step_id)}=initial WHERE model=?',[model_id])
        else:
            self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND sequence=?',[model_id,step_sequence-1])
            inherit_step_id = self.__ins_cursor.fetchone()[0]

            self.__ins_cursor.execute(f'UPDATE boundary_conditions SET {"step_"+str(step_id)}={"step_"+str(inherit_step_id)} WHERE model=?',[model_id])
    def renameStep(self, in_model_name:str, in_old_setp_name:str, in_new_step_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('UPDATE steps SET name=? WHERE model=? AND name=?',[in_new_step_name,model_id,in_old_setp_name])
    def editStep(self, in_model_name:str, in_step_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        step_type_number = common.P4SStepInfo.STEP_TYPE_TO_NUMBER[in_step_info['type']]
        
        if in_step_info['nlgeom']:
            step_nlgeom = 1
        else:
            step_nlgeom = 0
        
        if step_type_number == 1:
            step_increments_number_string = str(in_step_info['basic'][0])
            step_incrementation_type_string = str(common.P4SStepInfo.INCREMENTATION_TYPE_TO_NUMBER[in_step_info['basic'][1]])
            step_increment_size_params_string = ','.join([str(i) for i in in_step_info['basic'][2:]])
            step_basic_string = step_increments_number_string + ',' + step_incrementation_type_string + ',' + step_increment_size_params_string

            step_lsolver_type_number = common.P4SStepInfo.LSOLVER_TYPE_TO_NUMBER[in_step_info['lsolver'][0]]
            step_lsolver_method_number = common.P4SStepInfo.SOLVER_METHOD_TO_NUMBER[step_lsolver_type_number][in_step_info['lsolver'][1]]
            step_lsolver_string = str(step_lsolver_type_number) + ',' + str(step_lsolver_method_number)
        else:
            pass
        
        self.__ins_cursor.execute('UPDATE steps SET type=?,time=?,nlgeom=?,basic=?,lsolver=? WHERE model=? AND name=?',[step_type_number,in_step_info['time'],step_nlgeom,step_basic_string,step_lsolver_string,model_id,in_step_info['name']])
    def removeStep(self, in_model_name:str, in_step_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id,sequence FROM steps WHERE model=? AND name=?',[model_id,in_step_name])
        step_id,step_sequence_number = self.__ins_cursor.fetchone()
        self.__ins_cursor.execute(f'DELETE FROM steps WHERE id=?',[step_id])

        association_info_dict = {'outputs':[],'conditions':[]}
        
        self.__ins_cursor.execute('SELECT id,name FROM outputs WHERE model=? AND bstep=?',[model_id,step_id])
        for output_id,output_name in self.__ins_cursor.fetchall():
            association_info_dict['outputs'].append(output_name)
            
            self.__ins_cursor.execute(f'DELETE FROM steps WHERE id=?',[output_id])
        
        if step_sequence_number == 1:
            pass
        else:
            self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND sequence=?',[model_id,step_sequence_number-1])
            before_step_id = self.__ins_cursor.fetchone()[0]
            self.__ins_cursor.execute('UPDATE outputs SET estep=? WHERE model=? AND estep=?',[before_step_id,model_id,step_id])
        
        self.__ins_cursor.execute('SELECT id,name FROM boundary_conditions WHERE model=? AND definition=?',[model_id,step_id])
        for condition_id,condition_name in self.__ins_cursor.fetchall():
            association_info_dict['conditions'].append(condition_name)
            
            self.__ins_cursor.execute(f'DELETE FROM boundary_conditions WHERE id=?',[condition_id])

            self.__ins_cursor.execute(f'ALTER TABLE boundary_conditions DROP COLUMN {"step_"+str(step_id)}')
        
        return association_info_dict
    
    def getOutputInformation(self, in_model_name:str, in_output_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT type,bstep,estep,reference,frequency,agroup,variables FROM outputs WHERE model=? AND name=?',[model_id,in_output_name])
        output_infomation_list = self.__ins_cursor.fetchone()
    
        output_info_dict = {'type':None, 'steps':[],'frequency':[],'group':None,'variables':[]}

        if output_infomation_list[0] == 1:
            output_info_dict['type'] = 'node'
        elif output_infomation_list[0] == 2:
            output_info_dict['type'] = 'element'
        else:
            pass
        
        self.__ins_cursor.execute('SELECT name FROM steps WHERE model=? AND id=?',[model_id,output_infomation_list[1]])
        output_info_dict['steps'].append(self.__ins_cursor.fetchone()[0])
        self.__ins_cursor.execute('SELECT name FROM steps WHERE model=? AND id=?',[model_id,output_infomation_list[2]])
        output_info_dict['steps'].append(self.__ins_cursor.fetchone()[0])

        output_info_dict['frequency'].append(common.P4SOutputInfo.NUMBER_TO_FREQUENCY_REFERENCE[output_infomation_list[3]])
        output_info_dict['frequency'].append(output_infomation_list[4])
        
        self.__ins_cursor.execute('SELECT name FROM groups WHERE model=? AND sign=0 AND id=?',[model_id,output_infomation_list[5]])
        output_info_dict['group'] = self.__ins_cursor.fetchone()[0]
        
        output_info_dict['variables'] = output_infomation_list[6].split(',')
        
        return output_info_dict
    def createOutput(self, in_model_name:str, in_output_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        if in_output_info['group'][0] == 'node':
            group_type = 1
        elif in_output_info['group'][0] == 'element':
            group_type = 2
        else:
            pass
    
        self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND name=?',[model_id,in_output_info['steps'][0]])
        bstep_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND name=?',[model_id,in_output_info['steps'][1]])
        estep_id = self.__ins_cursor.fetchone()[0]
        
        frequency_reference_number = common.P4SOutputInfo.FREQUENCY_REFERENCE_TO_NUMBER[in_output_info['frequency'][0]]
        
        self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=?',[model_id,0,in_output_info['group'][1],group_type])
        group_id = self.__ins_cursor.fetchone()[0]
        
        variables_string = ','.join(in_output_info['variables'])
        
        self.__ins_cursor.execute('INSERT INTO outputs(model,name,type,bstep,estep,reference,frequency,agroup,variables) VALUES(?,?,?,?,?,?,?,?,?)',[model_id,in_output_info['name'],group_type,bstep_id,estep_id,frequency_reference_number,in_output_info['frequency'][1],group_id,variables_string])
    def renameOutput(self, in_model_name:str, in_old_output_name:str, in_new_output_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]

        self.__ins_cursor.execute('UPDATE outputs SET name=? WHERE model=? AND name=?',[in_new_output_name,model_id,in_old_output_name])
    def editOutput(self, in_model_name:str, in_output_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        if in_output_info['group'][0] == 'node':
            group_type = 1
        elif in_output_info['group'][0] == 'element':
            group_type = 2
        else:
            pass
    
        self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND name=?',[model_id,in_output_info['steps'][0]])
        bstep_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND name=?',[model_id,in_output_info['steps'][1]])
        estep_id = self.__ins_cursor.fetchone()[0]
        
        frequency_reference_number = common.P4SOutputInfo.FREQUENCY_REFERENCE_TO_NUMBER[in_output_info['frequency'][0]]
        
        self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=?',[model_id,0,in_output_info['group'][1],group_type])
        group_id = self.__ins_cursor.fetchone()[0]
        
        variables_string = ','.join(in_output_info['variables'])
        
        self.__ins_cursor.execute('UPDATE outputs SET type=?,bstep=?,estep=?,reference=?,frequency=?,agroup=?,variables=? WHERE model=? AND name=?',[group_type,bstep_id,estep_id,frequency_reference_number,in_output_info['frequency'][1],group_id,variables_string,model_id,in_output_info['name']])
    def removeOutput(self, in_model_name:str, in_output_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute(f'DELETE FROM outputs WHERE model=? AND name=?',[model_id,in_output_name])
    
    def getBoundaryConditionInformation(self, in_model_name:str, in_boundary_condition_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        condition_info_dict = {'type':None, 'group':[],'csys':[],'definition':[],'parameters':{}}
        
        self.__ins_cursor.execute('SELECT id,type,agroup,csys,definition FROM boundary_conditions WHERE model=? AND name=?',[model_id,in_boundary_condition_name])
        condition_id,condition_type_number, assembly_group_id, assembly_csys_id, definition_step_id = self.__ins_cursor.fetchone()
        
        condition_info_dict['type'] = common.P4SBCInfo.NUMBER_TO_BC[condition_type_number]
        
        self.__ins_cursor.execute('SELECT name,type FROM groups WHERE model=? AND id=?',[model_id,assembly_group_id])
        group_name,group_type_number = self.__ins_cursor.fetchone()
        if group_type_number == 1:
            condition_info_dict['group'].append('node')
        elif group_type_number == 2:
            condition_info_dict['group'].append('element')
        else:
            pass
        condition_info_dict['group'].append(group_name)
        
        if assembly_csys_id == 0:
            condition_info_dict['csys'] = 'global'
        else:
            self.__ins_cursor.execute('SELECT name FROM coordinate_systems WHERE model=? AND source=? AND id=?',[model_id,0,assembly_csys_id])
            condition_info_dict['csys'] = self.__ins_cursor.fetchone()[0]
        
        if definition_step_id == 0:
            definition_step_name, definition_step_sequence = 'Initial',0
        else:
            self.__ins_cursor.execute('SELECT name,sequence FROM steps WHERE model=? AND id=?',[model_id,definition_step_id])
            definition_step_name, definition_step_sequence = self.__ins_cursor.fetchone()
        condition_info_dict['definition'] = [definition_step_name,definition_step_sequence]
        
        if definition_step_id == 0:
            step_name = 'Initial'
            
            self.__ins_cursor.execute(f'SELECT Initial FROM boundary_conditions WHERE model=? AND id=?',[model_id,condition_id])
            step_paramters_string = self.__ins_cursor.fetchone()[0]
        else:
            self.__ins_cursor.execute('SELECT name FROM steps WHERE model=? AND id=?',[model_id,definition_step_id])
            step_name = self.__ins_cursor.fetchone()[0]
            
            self.__ins_cursor.execute(f'SELECT {"step_"+str(definition_step_id)} FROM boundary_conditions WHERE model=? AND id=?',[model_id,condition_id])
            step_paramters_string = self.__ins_cursor.fetchone()[0]
        condition_info_dict['parameters'][step_name] = step_paramters_string.split(',')
        if condition_info_dict['parameters'][step_name][-1] == 'None':
            pass
        else:
            self.__ins_cursor.execute('SELECT name FROM functions WHERE model=? AND id=?',[model_id, int(condition_info_dict['parameters'][step_name][-1])])
            condition_info_dict['parameters'][step_name][-1] = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id,name FROM steps WHERE model=? AND sequence>?',[model_id,definition_step_sequence])
        condition_parameters_associated_steps_info_list = self.__ins_cursor.fetchall()
        for step_id,step_name in condition_parameters_associated_steps_info_list:
            self.__ins_cursor.execute(f'SELECT {"step_"+str(step_id)} FROM boundary_conditions WHERE model=? AND id=?',[model_id,condition_id])
            step_paramters_string = self.__ins_cursor.fetchone()[0]
            
            condition_info_dict['parameters'][step_name] = step_paramters_string.split(',')
            
            if condition_info_dict['parameters'][step_name][-1] == 'None':
                pass
            else:
                self.__ins_cursor.execute('SELECT name FROM functions WHERE model=? AND id=?',[model_id, int(condition_info_dict['parameters'][step_name][-1])])
                condition_info_dict['parameters'][step_name][-1] = self.__ins_cursor.fetchone()[0]
        
        return condition_info_dict
    def getBoundaryConditionsByStep(self, in_model_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        boundary_conditions_dict_step = {}
        self.__ins_cursor.execute('SELECT name FROM boundary_conditions WHERE model=? AND definition=0',[model_id])
        boundary_conditions_info_list = self.__ins_cursor.fetchall()
        if boundary_conditions_info_list is None:
            pass
        else:
            boundary_conditions_dict_step['Initial'] = [i[0] for i in boundary_conditions_info_list]
        
        self.__ins_cursor.execute('SELECT id,name FROM steps WHERE model=?',[model_id])
        steps_info_list = self.__ins_cursor.fetchall()
        for step_id, step_name in steps_info_list:
            self.__ins_cursor.execute('SELECT name FROM boundary_conditions WHERE model=? AND definition=?',[model_id,step_id])
            boundary_conditions_info_list = self.__ins_cursor.fetchall()
            if boundary_conditions_info_list is None:
                pass
            else:
                boundary_conditions_dict_step[step_name] = [i[0] for i in boundary_conditions_info_list]
        
        return boundary_conditions_dict_step
    def createBoundaryCondition(self, in_model_name:str, in_condition_type:str, in_group_type:str, in_boundary_condition_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        condition_type_number = common.P4SBCInfo.BC_TO_NUMBER[in_condition_type]
        
        if in_group_type == 'node':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=0 AND name=? AND type=1',[model_id,in_boundary_condition_info['group']])
        elif in_group_type == 'element':
            self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=0 AND name=? AND type=2',[model_id,in_boundary_condition_info['group']])
        else:
            pass
        group_id = self.__ins_cursor.fetchone()[0]
        
        if in_boundary_condition_info['csys'] == 'global':
            csys_id = 0
        else:
            self.__ins_cursor.execute('SELECT id FROM coordinate_systems WHERE model=? AND name=? AND source=?',[model_id,in_boundary_condition_info['csys'],0])
            csys_id = self.__ins_cursor.fetchone()[0]
        
        if in_boundary_condition_info['definition'] == 'Initial':
            definition_step_id = 0
        else:
            self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND name=?',[model_id, in_boundary_condition_info['definition']])
            definition_step_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('INSERT INTO boundary_conditions(model,name,type,agroup,csys,definition) VALUES(?,?,?,?,?,?)',[model_id,in_boundary_condition_info['name'],condition_type_number,group_id,csys_id,definition_step_id])
        
        self.__ins_cursor.execute('SELECT id FROM boundary_conditions WHERE model=? AND name=?',[model_id, in_boundary_condition_info['name']])
        condition_id = self.__ins_cursor.fetchone()[0]
        for step_name,components_text_list in in_boundary_condition_info['steps'].items():
            if step_name == 'Initial':
                self.__ins_cursor.execute('UPDATE boundary_conditions SET initial=? WHERE model=? AND id=?',[','.join(components_text_list),model_id,condition_id])
            else:
                self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND name=?',[model_id, step_name])
                step_id = self.__ins_cursor.fetchone()[0]
                
                if components_text_list[-1] == 'None':
                    pass
                else:
                    self.__ins_cursor.execute('SELECT id FROM functions WHERE model=? AND name=?',[model_id, components_text_list[-1]])
                    components_text_list[-1] = str(self.__ins_cursor.fetchone()[0])
                
                self.__ins_cursor.execute(f'UPDATE boundary_conditions SET step_{step_id}=? WHERE model=? AND id=?',[','.join(components_text_list),model_id,condition_id])
    def renameBoundaryCondition(self, in_model_name:str, in_old_condition_name:str, in_new_condition_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('UPDATE boundary_conditions SET name=? WHERE model=? AND name=?',[in_new_condition_name,model_id,in_old_condition_name])
    def editBoundaryCondition(self, in_model_name:str, in_edit_boundary_condition_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT agroup FROM boundary_conditions WHERE model=? AND name=?',[model_id,in_edit_boundary_condition_info['name']])
        old_group_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT type FROM groups WHERE model=? AND id=?',[model_id,old_group_id])
        group_type = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute('SELECT id FROM groups WHERE model=? AND sign=? AND name=? AND type=?',[model_id,0,in_edit_boundary_condition_info['group'],group_type])
        group_id = self.__ins_cursor.fetchone()[0]
        
        if in_edit_boundary_condition_info['csys'] == 'global':
            csys_id = 0
        else:
            self.__ins_cursor.execute('SELECT id FROM coordinate_systems WHERE model=? AND name=? AND source=?',[model_id,in_edit_boundary_condition_info['csys'],0])
            csys_id = self.__ins_cursor.fetchone()[0]
        
        if in_edit_boundary_condition_info['definition'] == 'Initial':
            definition_step_id = 0
        else:
            self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND name=?',[model_id, in_edit_boundary_condition_info['definition']])
            definition_step_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM boundary_conditions WHERE model=? AND name=?',[model_id, in_edit_boundary_condition_info['name']])
        condition_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('UPDATE boundary_conditions SET agroup=?,csys=?,definition=? WHERE model=? AND id=?',[group_id,csys_id,definition_step_id,model_id,condition_id])
        
        self.__ins_cursor.execute('SELECT id FROM steps WHERE model=?',[model_id])
        steps_id_list = ['Initial=NULL']
        for i in self.__ins_cursor.fetchall():
            steps_id_list.append('step_'+str(i[0])+'=NULL')
        self.__ins_cursor.execute(f'UPDATE boundary_conditions SET {",".join(steps_id_list)} WHERE model=? AND id=?',[model_id,condition_id])
        
        for step_name,components_text_list in in_edit_boundary_condition_info['steps'].items():
            if step_name == 'Initial':
                self.__ins_cursor.execute('UPDATE boundary_conditions SET initial=? WHERE model=? AND id=?',[','.join(components_text_list),model_id,condition_id])
            else:
                self.__ins_cursor.execute('SELECT id FROM steps WHERE model=? AND name=?',[model_id, step_name])
                step_id = self.__ins_cursor.fetchone()[0]
                
                if components_text_list[-1] == 'None':
                    pass
                else:
                    self.__ins_cursor.execute('SELECT id FROM functions WHERE model=? AND name=?',[model_id, components_text_list[-1]])
                    components_text_list[-1] = str(self.__ins_cursor.fetchone()[0])
                
                self.__ins_cursor.execute(f'UPDATE boundary_conditions SET step_{step_id}=? WHERE model=? AND id=?',[','.join(components_text_list),model_id,condition_id])
    def removeBoundaryCondition(self, in_model_name:str, in_boundary_condition_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute(f'DELETE FROM boundary_conditions WHERE model=? AND name=?',[model_id,in_boundary_condition_name])
    
    def getFunctionInformation(self, in_model_name:str, in_function_name:str) -> dict:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        function_info_dict = {'type':None,'parameters':[]}
        self.__ins_cursor.execute('SELECT type,parameters FROM functions WHERE model=? AND name=?',[model_id,in_function_name])
        function_type_number, function_parameters_string = self.__ins_cursor.fetchone()
        
        function_info_dict['type'] = common.P4SOtherInfo.NUMBER_TO_FUNCTION_TYPE[function_type_number]
        
        for parameters_string in function_parameters_string.split(';'):
            function_info_dict['parameters'].append(parameters_string.split(','))
        
        return function_info_dict
    def createFunction(self, in_model_name:str, in_function_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        function_type_number = common.P4SOtherInfo.FUNCTION_TYPE_TO_NUMBER[in_function_info['type']]
        
        function_parameters_string_list = []
        for parameters_list in in_function_info['parameters']:
            function_parameters_string_list.append(','.join(parameters_list))
        function_parameters_string = ';'.join(function_parameters_string_list)

        self.__ins_cursor.execute('INSERT INTO functions(model,name,type,parameters) VALUES(?,?,?,?)',[model_id,in_function_info['name'],function_type_number,function_parameters_string])
    def renameFunction(self, in_model_name:str, in_old_function_name:str, in_new_function_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('UPDATE functions SET name=? WHERE model=? AND name=?',[in_new_function_name,model_id,in_old_function_name])
    def editFunction(self, in_model_name:str, in_function_info:dict) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        function_type_number = common.P4SOtherInfo.FUNCTION_TYPE_TO_NUMBER[in_function_info['type']]
        
        function_parameters_string_list = []
        for parameters_list in in_function_info['parameters']:
            function_parameters_string_list.append(','.join(parameters_list))
        function_parameters_string = ';'.join(function_parameters_string_list)

        self.__ins_cursor.execute('UPDATE functions SET type=?,parameters=? WHERE model=? AND name=?',[function_type_number,function_parameters_string,model_id,in_function_info['name']])
    def removeFunction(self, in_model_name:str, in_function_name:str) -> None:
        self.__ins_cursor.execute('SELECT id FROM models WHERE name=?',[in_model_name])
        model_id = self.__ins_cursor.fetchone()[0]
        
        self.__ins_cursor.execute('SELECT id FROM functions WHERE model=? AND name=?',[model_id, in_function_name])
        function_id = self.__ins_cursor.fetchone()[0]
        self.__ins_cursor.execute(f'DELETE FROM functions WHERE model=? AND name=?',[model_id,in_function_name])

        self.__ins_cursor.execute('SELECT id FROM steps WHERE model=?',[model_id])
        steps_id_list = self.__ins_cursor.fetchall()
        if steps_id_list is None:
            pass
        else:
            for step_id_list in steps_id_list:
                self.__ins_cursor.execute(f'SELECT id,{"step_"+str(step_id_list[0])} FROM boundary_conditions WHERE model=?',[model_id])
                step_parameters_info_list = self.__ins_cursor.fetchall()
                for condition_id, condition_step_parameters_string in step_parameters_info_list:
                    if condition_step_parameters_string is None:
                        continue
                    else:
                        pass
                    
                    condition_step_parameter_string_list = condition_step_parameters_string.split(',')
                    if condition_step_parameter_string_list[-1] == str(function_id):
                        condition_step_parameter_string_list[-1] = 'None'
                        self.__ins_cursor.execute(f'UPDATE boundary_conditions SET {"step_"+str(step_id_list[0])}=? WHERE model=? AND id=?',[','.join(condition_step_parameter_string_list),model_id,condition_id])
                    else:
                        continue
