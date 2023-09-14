# -*- coding: utf-8 -*-
"""
@authors: SVTA Open Caching Working Group people
@license: MIT-license
"""

import os
from lxml import etree as ET
import configparser 
import ast

config_parser = configparser.ConfigParser()
config_parser.read('configuration.conf')
config = config_parser['generate_rfc']

draftname = config['draft_name']
output_dir = config['output_dir']
output_sections = config['output_sections']



#FILENAME = 'draft-rosenblum-cdni-protected-secrets-metadata-00.xml'
tree = ET.parse('./rfc_format.xml')
root = tree.getroot()

middle = root.find('middle')

generated_dir = config_parser['extract_docx']['work_directory'] + 'generated-xml/'
common_dir = config['common_dir']
sections = ast.literal_eval(output_sections.replace('\n',''))

def build_xml (section_dict):
    dir = generated_dir if section_dict['generated'] else common_dir
    tree_chapter = ET.parse(dir + section_dict['chapter'])
    root_chapter = tree_chapter.getroot()
    if 'childs' in section_dict:
        for child in section_dict['childs']:
            child_xml = build_xml(child)
            root_chapter.append(child_xml)
    return root_chapter

for section in sections:
    section_xml = build_xml (section)
    
    middle.append(section_xml)

try:
    os.mkdir('./'+output_dir)
except Exception:
    pass

with open(os.path.join('./'+output_dir+"/", draftname + '-' + config['version'] +'.xml')  , 'wb') as f:
    f.write(ET.tostring(root))
