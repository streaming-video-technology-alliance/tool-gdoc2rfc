# -*- coding: utf-8 -*-
"""
@authors: SVTA Open Caching Working Group people
@license: MIT-license
"""
import os
import re
import configparser

# Dictionary of referenced SVTA docs that have IETF drafts
svta_drafts = {
  "[SVTA2031]": "power-metadata-expression-language",
  "[SVTA2032]": "goldstein-processing-stages-metadata",
  "[SVTA2033]": "ietf-cdni-cache-control-metadata",
  "[SVTA2034]": "chaudhari-source-access-control-metadata",
  "[SVTA2035]": "ietf-cdni-client-access-control-metadata",
  "[SVTA2036]": "ietf-cdni-edge-control-metadata",
  "[SVTA2037]": "bichot-delivery-metadata",
  "[SVTA2038]": "warshavsky-private-features-metadata",
  "[SVTA2039]": "ietf-cdni-protected-secrets-metadata"
}

# List of external documents to link to the reference section
external_docs = {
  "[CDNI-MEL]",
  "[AWSv4]",
  "[X.509]",
  "[HCVAULT]",
  "[URI.signing]",
  "[W3C]",
  "[PCRE]",
  "[WHATWG-FETCH]",
  "[CTA-5007-A]"
  }


def replace_svta_draft_references(filedata):
  for key, value in svta_drafts.items():
    if (key in filedata):
      print (f'\nReplacing {key} with IETF draft reference {value}')
      print (f'Be sure to add reference in rfc_format.xml for <xi:include href="https://bib.ietf.org/public/rfc/bibxml3/reference.I-D.{value}.xml"/>')
     
      replacement = f'<xref target="I-D.{value}"/>'
      filedata = filedata.replace(key, replacement)
  
  return filedata

def replace_external_doc_references(filedata):
  for value in external_docs:
    if (value in filedata):
      start = value.index('[') + 1
      end = value.index(']')
      anchor = value[start:end]
      print (f'\nReplacing {value} with link to external reference.')
      print (f'Be sure to add reference in rfc_format.xml with anchor="{anchor}"')

      replacement = f'<xref target="{anchor}"/>'
      filedata = filedata.replace(value, replacement)
  
  return filedata


# Main program
config_parser = configparser.ConfigParser()
config_parser.read('configuration.conf')
config = config_parser['extract_docx']

location = config['work_directory'] +'/generated-xml/' # get present working directory location here
counter = 0 #keep a count of all files found
csvfiles = [] #list to store all csv files found at location
filebeginwithhello = [] # list to keep all files that begin with 'hello'
otherfiles = [] #list to keep any other file that do not match the criteria


for filename in os.listdir(location):
    # Read in the file
    print ('\nExtracting references for:', filename)
    with open(location + filename, 'r') as file :
      filedata = file.read()

    # Replace all [RFCxxx] references
    refs = re.findall('\[RFC(\d{4})\]', filedata)
    if (refs):
      print ("RFC document references:", refs)
      pattern = r'\[RFC(\d{4})\]'
      filedata = re.sub(pattern, r'<xref target="RFC\1" />', filedata)
 
    # Replace all [ietf*] references
    refs = re.findall('\[ietf([^\]]*)\]', filedata)
    if (refs):
      print ("IETF draft document references:", refs)
      pattern = r'\[ietf([^\]]*)\]'
      filedata = re.sub(pattern, r'<xref target="ietf\1" />', filedata)

    # Replace [SVTAxxxx] references with internet draft references for SVTA docs that have IETF drafts
    refs = re.findall('\[SVTA(\d{4})\]', filedata)
    if (refs):
      print ("SVTA document references:", refs)
      filedata = replace_svta_draft_references(filedata)

      # Replace all remaining [SVTAxxx] references with an XREF
      pattern = r'\[SVTA(\d{4})\]'
      filedata = re.sub(pattern, r'<xref target="SVTA\1" />', filedata)

    # Replace other misc references
    filedata =  replace_external_doc_references(filedata)

    # Write the file out again
    with open(location+filename, 'w') as file:
      file.write(filedata)
