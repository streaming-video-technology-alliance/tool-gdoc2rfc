# GDOC HTML to RFC XML Converter

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

WARNING: This README.md has been generate by chat GPT. Until further notice, it can contain incorrect information. WIP


This open-source Python tool is designed to convert HTML versions from GDOC into the XML format used for publishing RFCs (Request for Comments) by the IETF (Internet Engineering Task Force). It consists of three main scripts that work together to facilitate the conversion process. The tool is distributed under the MIT License.

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

This project requires Python 3.x 

## Installation

To use this GDOC HTML to RFC XML Converter, follow these steps:

1. Clone the repository to your local machine in a working directory:

   ```bash
   git clone git@github.com:streaming-video-technology-alliance/tool-gdoc2rfc.git
   ```

2. Install the required Python dependencies:

   ```bash
   cd tool-gdoc2rfc
   pip3 install -r requirements.txt
   ```

3. In a directory of your convenience, Duplicate `draft_sample` directory with a significative name for your draft. 

   ```bash
   cp -pR draft-sample draft-smith-someinterestingthing-ietf118
   ```

## Configuration

### Configuration file

A sample configuration file named `configuration.conf` is included in the duplicated folder. The configuration file is common for all scripts, and is divided in sections.

1. `[extract_docx]` affects to `extract_html.py`, `extract_references.py` & `extract_figures.py` 


 Here's an example configuration file:

```python
[extract_docx]
work_directory=work/
filename_html=sample.html
chapters_process= [{'c':'2', 'r':False}, {'c':'2.1', 'r':False} {'c': '4', 'r':True}, {'c':'5', 'r':True}, {'c':'6', 'r':True}, {'c':'7', 'r':True}]
```

- `work_directory`: The directory containing the input DOCX file and where the script will place the generated files.
- `filename_html`: The name of the the input HTML file 
- `chapters_process`: List of chapters of the input DOCX file that will be processed. It is a json list with items that indicate the number of the chapter, and if the chapter will be processed including all its subchapters. In case `r` is `True`, the chapter will be processed as a whole, including all the subchapters. In case you want to only include some parts of a chapter, you need to set `r` to `False`, and include in the list all the subchapters you want to include in the RFC draft.

2. `[extract_figures]` affects to `extract_figures.py`
```python
[extract_figures]
work_directory=figures/
figures_process= [{'label':'Figure 1: name','filename':'figure_1.xml'},{'label':'Figure 2: name','filename':'figure_2.xml'}]
```

- `work_directory`: The directory containing the figure tags with embedded ascii-art and optional SVG art.
- `figures_process`: List of specifiers as pairs, where `label` is the name of the figure to replace, and `filename` is the name of the figure file in the figures directory.

Notes on use of figures:
- In the figures_process array, 'label' must exactly match the figure title text in the original input document.
- Each figure XML file MUST contain a <figure>...</figure> element as documented in https://authors.ietf.org/en/rfcxml-vocabulary.
- Each figure MUST contain an <artset> with at least one <artwork> of type "ascii-art".
- The <artset> MAY contain an additional <artwork> type "svg", with  "src" attribute referencing an SVG file that is publicly accessbile.
- SVG files must meet the IETF RFC strict criteria. Use of the IETF-provided svgcheck tool with the options "-r -g" can be used to conform files.

```python
<figure title="Figure Title">
   <artset>
      <artwork type="svg" src="https://me.com/figure_1.svg" />
      <artwork type="ascii-art">
      <![CDATA[
 ASCII ART WORK HERE
   ]]>
      </artwork>
   </artset>
</figure>
```

3. `[generate_rfc]` affects to `generate_rfc.py` 

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

`generate_rfc.py` script outputs an XML file based in IETF [RFC7991](https://datatracker.ietf.org/doc/rfc7991/), "The "xml2rfc" Version 3 Vocabulary", using the extracted text from the HTML file.

To build up the XML documents, it needs a specific XML scheleton including XML definitions and processing instructions. This is the mean of the `rfc_format.xml` file that is needed at the same level of `configuration.conf` file. This sample XML scheleton includes all the required elements for the draft to exists. The `generate_rfc.py` script takes this scheleton, and it fills the `<middle></middle>` node in it with the context extracted from the HTML document.

That means you need to manually modify the scheleton `rfc_format.xml` according to your draft. Specifically you should:
- Modify the `docName` property in the `rfc` tag  with the draft name and version: i.e.: `draft-smith-someinterestingthing-ietf118-00`
- Modify the `<title>` tag with the correct `abrev` property and value. i.e.: <br>
  ```<title abbrev="CDNI Edge Control Metadata">CDNI Edge Control Metadata</title>``` 

- Modify `<author>` node. Add as many `author` nodes as needed
- Modify the `<abstract>` node as needed
- Modify both the Normative References and Informative References. Add as many as required

Notes on References:
- `extract_references.py` has a table named external_docs that lists anchor names external specification references (example: [CTA-5007]. Add any new references here, and also add the appropriate document document reference information in the references sections of your rfc_format.xml file.
- `extract_references.py` has a table named svta_drafts that lists anchor names for SVTA documents that also exist as SVTA drafts. (example: [SVTA2031]. Add any new references here, and also add the appropriate document document reference information in the references sections of your rfc_format.xml file. This allows the tools to convert SVTA document references to IETF document references.

## Usage

To convert a HTML GDOC document to RFC XML format, you need to follow these steps:

1. Copy your input HTML file under the `work_dir` folder in your local system

2. Modify the `rfc_format.xml` accordingly to your draft information, as described in [RFC scheleton](#rfc-scheleton)

3. Update the `configuration.conf` file if needed, adding the filename of the html document, and the chapters to export into the draft.

2. you can execute the following command under the directory containing your draft `configuration.conf` file. The command will execute all scripts in the correct order. The result will be an xml file in the `output_dir` folder.


```bash
cd draft-smith-someinterestingthing-ietf118

python3 ../extract_html.py &&  \ 
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

- This project is inspired by the need to automate the conversion of html versions of Google Docs documents into RFC XML v3 format for IETF RFC publications.
- We would like to thank the open-source community for their contributions and support in developing this tool.
