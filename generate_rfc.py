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

event_types = ("start", "end", "comment", "pi")

# Using readlines()
file1 = open('rfc_format.xml', 'r')
lines = file1.readlines()


def sections2text():
    xmlText = '';

    for section in sections:
        section_xml = build_xml (section)
        
        xmlText = xmlText + ET.tostring(section_xml,  encoding='utf-8', method='xml').decode('utf-8')

    return xmlText

generated_dir = config_parser['extract_docx']['work_directory'] + 'generated-xml/'
common_dir = config['common_dir']
sections = ast.literal_eval(output_sections.replace('\n',''))

def build_xml (section_dict):
    dir = generated_dir if section_dict['generated'] else common_dir
    parser = ET.XMLParser(strip_cdata=False)

    tree_chapter = ET.parse(dir + section_dict['chapter'],  parser=parser)
    root_chapter = tree_chapter.getroot()
    if 'childs' in section_dict:
        for child in section_dict['childs']:
            child_xml = build_xml(child)
            root_chapter.append(child_xml)
    return root_chapter


# Strips the newline character
text_xml = '';

for line in lines:
    if '<middle>' in line:
        text_xml = text_xml + "<middle>\n"+ sections2text()
    else:
        text_xml = text_xml + line;


try:
    os.mkdir('./'+output_dir)
except Exception:
    pass



with open(os.path.join('./'+output_dir+"/", draftname + '-' + config['version'] +'.xml')  , 'w') as f:
    #f.write(ET.tostring(root, encoding='utf-8', method='xml',  xml_declaration=True))
    f.write(text_xml)
