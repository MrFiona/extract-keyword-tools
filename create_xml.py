#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time    : 2017-05-10 09:01
# Author  : MrFiona
# File    : create_xml.py
# Software: PyCharm Community Edition

import os
import glob
import xml.dom.minidom as Dom
import xml.etree.ElementTree as ET

def create_xml(global_actual_file_list, combine_flag=False):
    result_path = os.getcwd() + os.sep + 'result_text'

    if not os.path.exists(result_path):
        raise UserWarning('存放数据的 [ %s ] 目录不存在' % result_path)

    # create xml file
    doc = Dom.Document()
    root_node = doc.createElement('text_result')
    doc.appendChild(root_node)

    #如果连接标志开启，则读取原始xml文件，添加xml数据
    if combine_flag:
        tree = ET.parse(result_path + os.sep + 'create_result_report.xml')
        root = tree.getroot()
        for child in root:
            # print child, child.tag
            file_node = doc.createElement(child.tag)
            for content in child:
                name = content.attrib['name']
                value = content.attrib['value']
                # print 'name: ', name, '\tvalue: ', value

                name_node = doc.createElement('content')
                name_node.setAttribute('name', name)
                name_node.setAttribute('value', value)

                file_node.appendChild(name_node)
                root_node.appendChild(file_node)

    global_actual_file_list.sort()
    # print 'global_actual_file_list:\t', global_actual_file_list
    for actual_file_name in global_actual_file_list:
        # print 'actual_file_name:\t', actual_file_name
        result_file_list = [ file for file in glob.glob(result_path + os.sep + '*') if 'result_' + actual_file_name in file ]
        tab_num_file_list = [ file for file in glob.glob(result_path + os.sep + 'tab_num_dir' + os.sep + '*') if actual_file_name in file ]
        # print 'result_file_list:\t', result_file_list
        # print 'tab_num_file_list:\t', tab_num_file_list

        for file in result_file_list:
            # get result data
            with open(file, 'r') as f:
                data = f.readlines()
            tab_num_file = [ num_file for num_file in tab_num_file_list if 'tab_num_' + actual_file_name in num_file ][0]
            # print tab_num_file

            with open(tab_num_file, 'r') as f:
                tab_num_data = f.readline().split(' ')

            tab_num_list = [ int(tab_num.strip('\n')) for tab_num in tab_num_data ]
            xml_data = [ data[i].strip('\n').split(' '*tab_num_list[i]) for i in range(len(data)) ]
            # print 'xml_data:\t', xml_data

            file_node = doc.createElement(os.path.split(file)[1].split('.')[0])

            for ele_data in xml_data:
                name_node = doc.createElement('content')
                name_node.setAttribute('name', ele_data[0])
                name_node.setAttribute('value', ele_data[1].lstrip())

                file_node.appendChild(name_node)
                root_node.appendChild(file_node)

    f = open(result_path + os.sep + "create_result_report.xml", "w")
    f.write(doc.toprettyxml(indent="\t", newl="\n", encoding="utf-8"))
    f.close()


if __name__ == '__main__':
    pass
    # create_xml(actual_file_name=actual_file_name)