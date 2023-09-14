# -*- coding: utf-8 -*-
"""
@authors: SVTA Open Caching Working Group people
@license: MIT-license
"""

from lxml import etree as ET

import collections

import json
import zipfile
import sys
import codecs
import os.path
import datetime

import configparser
import ast

#from jsonpath_ng import jsonpath, parse



#sys.stdout = codecs.getwriter('utf8')(sys.stdout)
#sys.stderr = codecs.getwriter('utf8')(sys.stderr)


"""
Module that extract text from MS XML Word document (.docx).
(Inspired by python-docx <https://github.com/mikemaccana/python-docx>)
"""

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'
RPR = WORD_NAMESPACE + 'rPr'
BOOKMARK = WORD_NAMESPACE + 'bookmarkStart'
NUMPR = WORD_NAMESPACE + 'numPr'
SHD = WORD_NAMESPACE + 'shd'
TAB = WORD_NAMESPACE + 'tab'
COMMENT = WORD_NAMESPACE + 'comment'
sections = []
sections_list = {}

def title_case(title):
    
    for word in title.split(" "):
        for exclusion in ["MI","FCI","UCDN", "DCDN", "uCDN", "dCDN"]:
            if exclusion in word:
                return title

    return title.title()


def create_xml_from_chapter (chapter_doc, children=True):
    xml = ET.Element("section")
    title = chapter_doc['title']


    xml.set('title',title_case(title))
    xml.set('anchor',chapter_doc['title'].replace(" ","-"))
    in_list = False
    in_property = False
    in_code = False

    ## CREATE MAIN SECTION PART

    for t in chapter_doc['text']:
        if '.....' not in t and '#####' not in t and 'Property:' not in t and not t.startswith("auth-type"):
            if in_code:
                in_code = False
                #cdata.text = cdata.text + ']]'
                artwork_section.text = ET.CDATA(cdata.replace("#####","").replace(",,,,,","  "))
            in_list = False
            in_property = False

            if not t.startswith('Code '):
                text_xml = ET.SubElement(xml, 't')
                text_xml.text = t.lstrip('.')

        else:
            if 'Property:' in t or t.startswith("auth-type"):
                if not in_property:
                    property_list = ET.SubElement(text_xml, 'list')
                property_list_text = ET.SubElement(property_list, 't')
                property_list_text.text = t
                in_list = False
                if in_code:
                    in_code = False
                    #cdata.text = cdata.text + ']]'
                    artwork_section.text = ET.CDATA(cdata.replace("#####","").replace(",,,,,","  "))

                in_property = True
                property_text = t
            elif '#####' in t:
                if not in_code:
                    in_code = True
                    figure_section = ET.SubElement(text_xml, 'figure')
                    artwork_section = ET.SubElement(figure_section,'sourcecode')
                    #cdata = ET.SubElement(artwork_section, '![CDATA[')
                    cdata = t+ '\n'
                    #cdata.text = t
                    #artwork_section.text = '<![CDATA['
                else:
                    #cdata.text = cdata.text + t
                    cdata = cdata + t + '\n'

            else:
                if in_code:
                    in_code = False
                    #cdata.text = cdata.text + ']]'
                    artwork_section.text = ET.CDATA(cdata.replace("#####","").replace(",,,,,","  "))
                if not in_list:
                    if in_property:
                        node = property_list_text
                    else:
                        text_xml = ET.SubElement(xml, 't')
                        text_xml.text = t.lstrip('.')
                        node = text_xml

                    list_xml = ET.SubElement(node, 'list')
                    if not in_property:
                        list_xml.set('style','numbers')
                    in_list = True

                text_list_xml = ET.SubElement(list_xml, 't')
                text_list_xml.text = t.lstrip('.')

    if in_code:
        in_code = False
        #cdata.text = cdata.text + ']]'
        artwork_section.text = ET.CDATA(cdata.replace("#####","").replace(",,,,,","  "))

    ## CREATE CHILDS SECTIONS AND ADD THEM TO THE SECTION AS sections
    if 'childs' in chapter_doc and children:
        for child in chapter_doc['childs']:
            xml_child = create_xml_from_chapter (child)
            xml.append(xml_child)

            #print (element.text)


    return xml


def save_sections (xml_object, chapter='', recursive=False):
    # create directory for xml results
    mydate_str = datetime.datetime.now().strftime("%m-%d-%Y")

    subdirectory = config['work_directory'] + "/generated-xml"
    try:
        os.mkdir(subdirectory)
    except Exception:
        pass

    if chapter != '':
        chapter = chapter + "_"

    if recursive:
        for miobject in xml_object.iter('section'):
            xmltext = ET.tostring(miobject, pretty_print = True)

            filename = miobject.attrib['anchor'];
            with open(os.path.join(subdirectory, chapter + filename+".xml")  , 'wb') as f:
                f.write(xmltext)
                print (chapter + filename+".xml")
    else:
        xmltext = ET.tostring(xml_object, pretty_print = True)

        filename = xml_object.attrib['anchor'];
        with open(os.path.join(subdirectory, chapter + filename+".xml")  , 'wb') as f:
            f.write(xmltext)
            print (chapter + filename+".xml")



def extract_chapter (sections, chapter):
    rtn = None
    for section in sections:
        if section['chapter']== chapter:
            return  section
        if 'childs' in section:
            rtn =   extract_chapter (section['childs'], chapter)
            if rtn:
                return rtn
    return rtn

def extract_chapter_info(text):
    split = text.split(' ',1)
    chapter = split[0]
    title = split[1]

    return { "chapter": chapter,
             "title": title ,
             "sections": {},
             "text": []}

def get_doc_tree (sections):
    sections_map = {}
    for section in sections:
        sections_map[section['chapter']] = section

    sections_tree = []
    for section in sections:
        # section['parent'] = par_chap
        par_chap = section['chapter'].rsplit('.',1)
        if len(par_chap) == 1:
            sections_tree.append(section)
        else:
            parent = sections_map[par_chap[0]]
            if 'childs' not in parent:
                parent['childs'] = []
            parent['childs'].append(section)

    return sections_tree

def process_text (text):
    #Replace some situations in text. For instance, REFERENCES
    return text

def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    # xml_comments = document.read('word/comments.xml')
    document.close()

    # comments = []
    #
    # comments_tree = ET.fromstring(xml_comments)
    # # ET.dump(comments_tree)
    # for comment in comments_tree.findall (COMMENT):
    #     for text in comment.iter(TEXT):
    #         if text.text.startswith('RFCTABLE'):
    #             #print (text.text)
    #             comments.append({ 'id': comment.attrib[WORD_NAMESPACE+'id'], 'text': text.text})
    #
    tree = ET.fromstring(xml_content)

    #tree = XML(xml_content)

    paragraphs = []
    section = {}

    for paragraph in tree.iter(PARA):
        is_section_chapter = False

        # ET.dump(paragraph)
        for node in paragraph.iter(BOOKMARK):
            texts = [node.text
                 for node in paragraph.iter(TEXT)
                 if node.text]
            if texts:
                is_section_chapter = True
                paragraphs.append(''.join(texts))
                # New section
                if len(section)>0:
                    sections.append(section)
                section = extract_chapter_info(''.join(texts))
                # sections.append(section)

        bullet = ""
        tabprefix = ""
        for p in  paragraph.iter(NUMPR):
            bullet = "....."

        for c in paragraph.iter(SHD):

            if not c.attrib[WORD_NAMESPACE + 'fill'] ==  'auto':
                bullet = "#####"

#        for tab in paragraph.iter(TAB):
#            tabprefix = ",,,,,"

#        texts = [tabprefix + process_text(node2.text)
#             for node in paragraph.iter(WORD_NAMESPACE+"r")
#                for node2 in node.iter(TEXT)
#                if node2.text]
        texts = []
        for node in paragraph.iter(WORD_NAMESPACE+"r"):
            for node2 in node:
                if node2.tag in WORD_NAMESPACE+"br":
                    texts.append("\n")
                elif node2.tag in TEXT:
                    texts.append(node2.text)


        if texts and not is_section_chapter:
            texts[0] = bullet + texts[0]
            paragraphs.append(''.join(texts))
            if 'text' in section:
                section['text'].append(''.join(texts))

    return '\n'.join(paragraphs)



### MAIN
config_parser = configparser.ConfigParser()
config_parser.read('./configuration.conf')
config = config_parser['extract_docx']

document = config['work_directory'] + config['filename']
chapters_process = ast.literal_eval(config['chapters_process'])

txt = get_docx_text(document)
doc_tree = get_doc_tree(sections)
for chapter in chapters_process:
    recursive = False
    if 'r' in chapter:
        recursive = True

    chapter_doc = extract_chapter(doc_tree, chapter['c'])
    if chapter_doc:
        xml_rfc = create_xml_from_chapter(chapter_doc, recursive)
        save_sections(xml_rfc, chapter['c'])
