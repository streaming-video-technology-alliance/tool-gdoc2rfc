# -*- coding: utf-8 -*-
"""
@authors: SVTA Open Caching Working Group people
@license: MIT-license
"""

from lxml import etree as ET
from lxml import html

import collections

import json
import zipfile
import sys
import codecs
import os.path
import datetime

import configparser
import ast
import re

"""
Module that extract text from MS XML Word document (.docx).
(Inspired by python-docx <https://github.com/mikemaccana/python-docx>)
"""
sections = []
sections_list = {}



def title_case(title):
    
    for word in title.split(" "):
        for exclusion in ["MI.","FCI.","UCDN", "DCDN", "uCDN", "dCDN"]:
            if exclusion in word:
                return title

    new_title = title
    new_title = new_title.title()

    # Keep certain words all caps
    new_title = new_title.replace("Cdni", "CDNI")
    new_title = new_title.replace("Fci", "FCI")
    new_title = new_title.replace("Bnf", "BNF")
    return new_title

def anchor_this(text):
    return text.replace(" ","-").replace(">","").replace("<","").replace(":","").replace(")","").replace("(","")

def create_xml_from_chapter (chapter_doc, children=True):
    xml = ET.Element("section")
    title = chapter_doc['title']

    in_list = False
    in_property = False
    in_code = False
    
    #Main XML for this chapter
    xml = chapter_doc['xml']

    ## CREATE CHILDS SECTIONS AND ADD THEM TO THE SECTION AS sections
    if 'childs' in chapter_doc and children:
        for child in chapter_doc['childs']:
            xml_child = create_xml_from_chapter (child)
            xml.append(xml_child)

    return xml


def save_sections (xml_object, chapter='', recursive=False, filename=None):
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
            xmltext = ET.tostring(miobject, pretty_print = True, encoding='utf-8', method='xml')

            if not filename:
                filename = miobject.attrib['anchor'];
            with open(os.path.join(subdirectory, chapter + filename+".xml")  , 'wb') as f:
                f.write(xmltext)
                print (chapter + filename+".xml")
    else:
        xmltext = ET.tostring(xml_object, pretty_print = True, encoding='utf-8', method='xml')

        if not filename:
            filename = miobject.attrib['anchor'];

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
             "text": [], 
             "xml": None}

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

def encode_text (text):
    text = text.replace('\xa0',' ')
    text = text.replace('”','"')
    text = text.replace('“','"')
    text = text.replace('’',"'")
    text = text.lstrip('.')

    return text

def get_text_content (elem, text_blocks=None):
    text = ""

    if text_blocks is None:
        text_blocks = []
    
    if elem.findall('*/a') or elem.findall('a'):
        # Check if this element includes an internal link
        for e in elem.getchildren():
            if e.tag == 'a':
                # Check if this is an internal link
                if e.attrib['href'].startswith('#'):
                    # This is an internal link. So we need to set an xref
                    text = text + e.text_content()
                    text_blocks.append({"ref": True, "text": e.text_content(), 'href': e.attrib['href']})
                else:
                    text = text + e.text_content()
                    text_blocks.append({"ref": False, "text": e.text_content()})
            else:
                get_text_content(e,text_blocks)
    else:
        text_blocks.append({"ref": False, "text": elem.text_content()})
        return text_blocks

    return text_blocks

# This version analyzes the tags to find internal links
# If there are, it will append xref tags to the anchors
# Using lxm is somehow difficult to add tags in the middle of a <t> tag
# we need to control if we are tail or not.

def generate_internal_refs(lis, text):
    text_array = get_text_content(lis)
    
    tmpText = ""
    tail = None
    text.text = ''
    for i in text_array:
        if not i['ref']:
            if tail is not None:
                tail.tail = tail.tail + encode_text(i['text'])
            else:
                text.text = text.text + encode_text(i['text'])
        else:
            xref = ET.SubElement(text,'xref')
            xref.text = encode_text(title_case(i['text']))
            xref.attrib['target']=i['href'][1:]
            tail = xref
            tail.tail = ''

def get_html_text(tree):
    paragraphs = []
    section = {}

    # Main Iterator in the HTML content generated by GDOC
    # HTML is processed in linear mode
    section = None
    text_xml = None

    # Detect the styles of the lists to handled the nested unordered lists
    list_styles_regex = r"\.([^.]+)>li:before{([^}]*)"
    list_styles = re.findall(list_styles_regex, tree.find("head").find("style").text_content())
    list_code_regex = r"\.([^.]*){([^}]*)}"
    list_code_styles = re.findall(list_code_regex,tree.find("head").find("style").text_content() )

    first_level_list = [k
                 for k,v in list_styles
                 if v == 'content:"\\0025ba   "' or v == 'content:"\\0025cf   "' or v == 'content:"\\0025b6   "']

    second_level_list = [k
                 for k,v in list_styles
                 if v == 'content:"o  "']

    code_style_classes = [k 
                          for k,v in list_code_styles
                          if 'background-color' in v and 'f8f8f8' in v ]


    in_list = False
    last_list = None
    last_list_item = None
    table_xml = None

    # Iterate on the HTML body only for first level tags. Not valid for structured html files
    for node in tree.find('body').getchildren():

        is_section_chapter = False
        # Avoid taking the span content, but the <p> text content directly
        if node.tag != "span":
            True

        # Remove all the sup tags that are comments in the GDOC document
        for sup in node.findall('.//sup'):
            sup.getparent().remove(sup)

        # Chapter titles
        if node.tag == "h1" or node.tag == "h2" or node.tag == "h3" or node.tag == "h4" or node.tag == "h5":
            in_list = False

            if node.text_content() != '':
                # a new section
                is_section_chapter = True

                # New section
                section = extract_chapter_info(''.join(node.text_content()))
                section["xml"] =  ET.Element("section")
                title = section['title']

                # title attribute is deprecated for sections. Let's be future-proof with the name tag
                name = ET.SubElement(section["xml"],'name')
                name.text = title_case(title)

                # section["xml"].set('title',title_case(title))

                # In older versions, the anchor was a transformation of the title. Now we use the HTML id, so it can be linked
                section["xml"].set('anchor',node.get('id'))

                in_property = False
                in_code = False

    ## CREATE MAIN SECTION PART
                if len(section)>0:
                    sections.append(section)

        if node.tag == "p":
            in_list = False
            # this is a paragraph as <t>
            if section:
                tmpText = node.text_content()
                if tmpText != '':
                    tmpText = encode_text(tmpText)
                    
                    section['text'].append(tmpText)
                    text_xml = ET.SubElement(section["xml"], 't')
#                    text_xml.text = node.text_content().lstrip('.')

                    generate_internal_refs(node,text_xml)

        if node.tag == "ul" or node.tag == 'ol':
            # Take the previous generated text_xml and append the list
            
            if text_xml is not None:
                # Check style for this list and detect the nesting level
                if node.tag == 'ul':
                    # This only applies to unordered lists.
                    style_classes = node.get("class").split(" ")
                    for cls in style_classes:
                        if cls in first_level_list or cls in second_level_list:
                            if cls in first_level_list:
                                if not in_list:
                                    in_list = True
                                    # This is the first list after some text.
                                    last_list = ET.SubElement(section["xml"],'ul')
                                else:
                                    # WE got an element of a previous list, formatted as ul
                                    # get the parent of the parent to return back to the main list 
                                    # and insert this as an li element of that
                                    last_list = last_list.getparent().getparent()
                            elif cls in second_level_list:
                                last_list = ET.SubElement(last_list_item,'ul')

                            for lis in node.getchildren():
                                if lis.tag == 'li':
                                    last_list_item = ET.SubElement(last_list,'li')
                                    text = ET.SubElement(last_list_item,"t")

                                    generate_internal_refs(lis,text)

                else:
                    ol = ET.SubElement(section["xml"],'ol')
                    for lis in node.getchildren():
                        if lis.tag == 'li':
                            last_list_item = ET.SubElement(ol,'li')
                            text = ET.SubElement(last_list_item,"t")
                            text.text = encode_text(lis.text_content())

        def parse_table_tr(tr, destination, c_tag="td"):
            # Get the columns in this row
            # Clean the text and tags
            tr_xml = ET.SubElement(destination,'tr')
            
            for td in tr.findall('td'):
                td_xml = ET.SubElement(tr_xml, c_tag)
                td_xml.text = td.text_content()
                td.getparent().remove(td)

            # tr.getparent().remove(tr)
            return True

        if node.tag == "table":
            in_list = False
            is_code = False
            is_table = False
            # This can correspond to a proper table, or to a code block
            # We can identify them using the styles
            # Check for the first td class.
            block_class = node.findall("tr")
            first_td_clss = node.findall("tr")[0].find('td').get("class").split(" ")
            for cls in first_td_clss:
                if cls in code_style_classes:
                    is_code = True

            if is_code:
                figure_section = ET.SubElement(section["xml"], 'figure')
                artwork_section = ET.SubElement(figure_section,'sourcecode')

                # Try to get the content formatted correctly (somehow)
                def get_code_text(text, lines):
                    text = ''
                    for element in lines:
                        if text != '':
                            text = text + '\n'
                        for child in element.getchildren():
                            if child.text:
                                tmpText = child.text
                            else:
                                tmpText = ''
                            
                            for subelem in child.getchildren():
                            # if child.getchildren():
                                for ch in ET.tostring(subelem):
                                    if ch == b'\xa0':
                                        tmpText = tmpText + '\n'
                                    elif ch == b'\xc2':
                                        tmpText = tmpText + '\t'
                                    elif ch == b'\x201c':
                                        True
                                        # TODO: Fix quote symbols
                                    else:
                                        tmpText = tmpText + chr(ch)
                                
                            tmpText = tmpText.replace("<br/>","\n")
                            tmpText = tmpText.replace(u'&#160;', u' ')
                            tmpText = tmpText.replace('&lt;','<');
                            tmpText = tmpText.replace('&gt;','>');

                            text = text + tmpText

                    return text
                artwork_section.text = ET.CDATA( get_code_text("",node.findall("tr")[0].find('td').findall('p')))

            else:

                if text_xml is not None:
                    table_xml = ET.SubElement(section["xml"],'table')
                    # First Row in table will be the thead in the RFC XML
                    # Following rows will be the tbody
                    trs = node.findall('tr')
                    thead_xml = ET.SubElement(table_xml, 'thead')
                    parse_table_tr(trs[0], thead_xml,'th')
                    
                    tbody_xml = ET.SubElement(table_xml, 'tbody')
                    for cnt in range(1,len(trs)):
                        parse_table_tr(trs[cnt], tbody_xml)

    return


### MAIN
config_parser = configparser.ConfigParser()
config_parser.read('./configuration.conf')
config = config_parser['extract_docx']

document = config['work_directory'] + config['filename_html']
chapters_process = ast.literal_eval(config['chapters_process'])
doc_tree = None

tree = html.parse(document)

# HTML generated by GDOC does not include an outline so the html is linear
# We can take leverage of the tags to identify the different elements
# extract sections from hx tags

get_html_text(tree)
doc_tree = get_doc_tree(sections)
if doc_tree:
    for chapter in chapters_process:

        recursive = chapter['r']

        chapter_doc = extract_chapter(doc_tree, chapter['c'])
        if chapter_doc:
            xml_rfc = create_xml_from_chapter(chapter_doc, recursive)
            #Pass the title as in previous versions
            save_sections(xml_rfc, chapter['c'], filename=anchor_this(chapter_doc['title']))
