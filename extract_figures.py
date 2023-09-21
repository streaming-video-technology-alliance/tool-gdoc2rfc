import os
import re
import configparser
import ast
from pathlib import Path

import os

config_parser = configparser.ConfigParser()
config_parser.read('configuration.conf')
config = config_parser['extract_docx']
location = config['work_directory'] +'/generated-xml/' # get present working directory location here

figures_process = []
try:
  config_diagrams = config_parser['extract_figures']
  figure_directory =  config_diagrams['figure_directory']
  figures_process = ast.literal_eval(config_diagrams['figures_process'])
except Exception:
  pass

for filename in os.listdir(location):
    # Read in the file
    with open(location + filename, 'r') as file :
      filedata = file.read()

    # Replace all the figures
    for fig in figures_process:
        label = fig['label']
        fname = fig['filename']
        art_filepath = figure_directory + fname
        figure_replacement = Path(art_filepath).read_text()
        filedata = filedata.replace(label, figure_replacement)

    # Write the file out again
    with open(location+filename, 'w') as file:
      file.write(filedata)

