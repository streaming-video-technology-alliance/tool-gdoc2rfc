# DOCX to RFC XML Converter

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

WARNING: This README.md has been generate by chat GPT. Until further notice, it can contain incorrect information. WIP


This open-source Python tool is designed to convert DOCX documents into the XML format used for publishing RFCs (Request for Comments) by the IETF (Internet Engineering Task Force). It consists of three main scripts that work together to facilitate the conversion process. The tool is distributed under the MIT License.

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
    - [Configuration file](#configuration-file)
    - [RFC scheleton](#rfc-scheleton)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)

## Requirements

This project requires Python 3.x >

## Installation

To use this DOCX to RFC XML Converter, follow these steps:

1. Clone the repository to your local machine in a working directory:

   ```bash
   git clone git@github.com:streaming-video-technology-alliance/tool-gdoc2rfc.git
   ```

2. Install the required Python dependencies:

   ```bash
   cd tool-gdoc2rfc
   pip3 install -r requirements.txt
   ```

3. Duplicate `draft_sample` directory with a significative name for your draft. 

   ```bash
   cp -pR draft-sample draft-smith-someinterestingthing-ietf118
   ```

## Configuration

### Configuration file

A sample configuration file named `configuration.conf` is included in the duplicated folder. The configuration file is common for all scripts, and is divided in sections.

1. `[extract_docx]` affects to `extract_docx.py`, `extract_references.py` & `extract_figures.py` 


 Here's an example configuration file:

```python
[extract_docx]
work_directory=work/
filename=sample.docx
chapters_process= [{'c':'2', 'r':False}, {'c':'2.1', 'r':False} {'c': '4', 'r':True}, {'c':'5', 'r':True}, {'c':'6', 'r':True}, {'c':'7', 'r':True}]
```

- `work_directory`: The directory containing the input DOCX file and where the script will place the generated files.
- `filename`: The name of the the input DOCX file 
- `chapters_process`: List of chapters of the input DOCX file that will be processed. It is a json list with items that indicate the number of the chapter, and if the chapter will be processed including all its subchapters. In case `r` is `True`, the chapter will be processed as a whole, including all the subchapters. In case you want to only include some parts of a chapter, you need to set `r` to `False`, and include in the list all the subchapters you want to include in the RFC draft.

```python
[extract_figures]
work_directory=figures/
figures_process= [{'label':'Figure 1: name','filename':'figure_1.xml'},{'label':'Figure 2: name','filename':'figure_2.xml'}]
```

- `work_directory`: The directory containing the figure tags with embedded ascii-art and optional SVG art.
- `figures_process`: List of specifiers as pairs, where `label` is the name of the figure to replace, and `filename` is the name of the figure file in the figures directory.


2. `[generate_rfc]` affects to `generate_rfc.py` 

```python
[generate_rfc]
output_dir=out/
common_dir=./common/
draft_name=draft-smith-someinterestingthing
version=00
output_sections = [
    {'generated': True, 'chapter': '2_INTRODUCTION.xml', 'childs': []},
    {'generated': False, 'chapter': 'requirements.xml', 'childs': []},
    {'generated': True, 'chapter': '4_MI.CrossoriginPolicy.xml', 'childs': []},
    {'generated': True, 'chapter': '5_MI.AllowCompress.xml', 'childs': []},
    {'generated': True, 'chapter': '6_MI.ClientConnectionControl.xml', 'childs': []},
    {'generated': True, 'chapter': '7_CONCLUSION.xml', 'childs': []},
    {'generated': False, 'chapter': 'Security.xml', 'childs': []},
    {'generated': False, 'chapter': 'IANA.xml', 'childs': []},
    {'generated': False, 'chapter': 'ack.xml', 'childs': []}
    ]
```

- `output_dir`: The directory where the converted RFC XML file will be saved.
- `draft_name`: The name of the file for the generated RFC XML file. It should follow the IETF rules to upload a RFCs
- `version`: The version of the RFC you want to create. It will be used as part of the generated RFC XML filename.
- `common_dir`: Directory that contains a list of XML files that are not generated by the `extract_xxx.py` scripts but are needed for the RFC. For example, `requirements` sections from IETF that are not in your input document but are required for a proper IETF RFC document. See below for more information
- `output_sections`: The order in which chapters are to be inserted into the final RFC document. A JSON list of objects that have 3 properties:
  - `generated`: A Boolean to indicate if the file to be included is a generated XML from the input document, or a common XML file
  - `chapter`: Filename corresponding to one section to be generated in the RFC XML file
  - `childs`: A list with the same structure of objects, in case you need to include recursively other sections as part of a main section. For instance, in a case you want to include section 2, and a section 2.1 in the RFC XML file under the first one. Only needed if you configured `chapter_process` including non-recursive chapters.


### RFC scheleton

TBD


## Usage

To convert a DOCX document to RFC XML format, you need to follow these steps:

1. Copy your input DOCX file under the `work_dir` folder in your local system

2. Modify the `rfc_format.xml` accordingly to your draft information

3. Update the `configuration.conf` file if needed

2. you can execute the following command under the directory containing your draft `configuration.conf` file. The command will execute all scripts in the correct order. The result will be an xml file in the `output_dir` folder.


```bash
cd draft-smith-someinterestingthing-ietf118

python3 ../extract_docx.py &&  \ 
python3 ../extract_figures.py && \ 
python3 ../extract_references.py && \
python3 ../generate_rfc.py
```

In case any script generates an error, please check the situation. You can execute them individually if necessary.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions from the community. If you have suggestions, feature requests, or would like to report issues, please create a GitHub issue or submit a pull request.

## Acknowledgments

- This project is inspired by the need to automate the conversion of DOCX documents into RFC XML format for IETF RFC publications.
- We would like to thank the open-source community for their contributions and support in developing this tool.
