# -*- coding: utf-8 -*-
"""
@authors: SVTA Open Caching Working Group people
@license: MIT-license
"""
import os
import re
import configparser


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
    print ("RFC document references:", re.findall('\[RFC(\d{4})\]', filedata))
    pattern = r'\[RFC(\d{4})\]'
    filedata = re.sub(pattern, r'<xref target="RFC\1" />', filedata)
 
    # Replace all [SVTAxxx] references
    print ("SVTA document references:", re.findall('\[SVTA(\d{4})\]', filedata))
    pattern = r'\[SVTA(\d{4})\]'
    filedata = re.sub(pattern, r'<xref target="SVTA\1" />', filedata)

   # Replace all [ietf*] references
    print ("IETF draft document references:", re.findall('\[ietf([^\]]*)\]', filedata))
    pattern = r'\[ietf([^\]]*)\]'
    filedata = re.sub(pattern, r'<xref target="ietf\1" />', filedata)

    # Replace other misc references  
    filedata = filedata.replace('[CDNI-MEL]', '<xref target="CDNI-MEL" />')
    filedata = filedata.replace('[AWSv4]', '<xref target="AWSv4" />')
    filedata = filedata.replace('[X.509]', '<xref target="X.509" />')
    filedata = filedata.replace('[HCVAULT]', '<xref target="HCVAULT" />')
    filedata = filedata.replace('[URI.signing]', '<xref target="URI.signing" />')
    filedata = filedata.replace('[W3C]', '<xref target="W3C" />')
    filedata = filedata.replace('[PCRE]', '<xref target="PCRE" />')


    # Write the file out again
    with open(location+filename, 'w') as file:
      file.write(filedata)
