# -*- coding: utf-8 -*-
"""
@authors: SVTA Open Caching Working Group people
@license: MIT-license
"""

import os
import re
import configparser

figure_1 = '''
<figure title="CDNI Metadata Model with Extensions">
    <artwork type="ascii-art"><![CDATA[
   +---------+      +---------+      +------------+
   |HostIndex++(*)+>+HostMatch++(1)+>+HostMetadata+------+(*)+-----+
   +---------+      +---------+      +------+-----+                |
                                            +                      |
                                           (*)                     +
                                            +                      V
   +-> Contains or references               V         *****************
   (1) One and only one                +---------+    *GenericMetadata*
   (*) Zero or more               +--->+PathMatch|    *     Objects   *<+
                                  |    +----+---++    ***************** |
                                  +         +   +                  ^    |
                                 (*)       (1) (1) +------------+  |    |
                                  +         +   +->+PatternMatch|  |    |
                                  |         V      +------------+  |    |
                                  |  +------------+                |    |
                                  +--+PathMetadata+------+(*)+-----+    |
                                     +------------+                     |
                                                                        |
                                                                        |
                                                                        |
                                +---------------------------------------+
                                |
                                +
          New GenericMetadata Object by Categories (SVA)
+-------------------+   +-------------------+  +---------------------+
|   Cache Control   |   |   Origin Access   |  |Client Access Control|
+-------------------+   +-------------------+  +---------------------+

+-------------------+   +-------------------+  +---------------------+
|   Edge  Control   |   | Processing Stages |  |   General Metadata  |
+-------------------+   +-------------------+  +---------------------+
  ]]></artwork>
</figure>
'''

figure_2_processing_stages = '''
					<figure title="Processing stages">
						<artwork type="ascii-art"><![CDATA[
        +-------+    +---------------+    +--------+
        |       +--->|A             B+--->|        |
        |       |    |               |    |  uCDN  |
        |  UA   |    |     dCDN      |    |        |
        |       |    |               |    | Source |
        |       |<---+D             C|<---+        |
        +-------+    +---------------+    +--------+
                      ]]></artwork>
					</figure>
'''

figure_3 = '''
<figure title="CDNi ProcessingStages metadata model with contained objects">
  <artwork type="ascii-art"><![CDATA[
                        +----------------+
                        |ProcessingStages|
                        +----------------+
                               (*)
                                |
       +----------------+-------+---------+----------------+
       |                |                 |                |
       v                v                 v                v
+-------------+ +-------------+ +--------------+ +--------------+
|ClientRequest| |OriginRequest| |OriginResponse| |ClientResponse|
+-------------+ +-------------+ +--------------+ +--------------+
      (*)             (*)              (*)              (*)
       |               |                |                |
       +---------------+----------------+----------------+
       |
       |                    +---------------+
       |          +-------->|ExpressionMatch|
       |          |         +---------------+
       |          |
       |          |                                 *****************
       |         (*)                           +--->*GenericMetadata*
       |    +----------+    +-------------+    |    *     Objects   *
       +--->+StageRules+--->|StageMetadata+(*)-+    *****************
            +----------+    +-------------+
                             (*)      (*)
                              |        |
                      +-------+        +-----------+
                      |                            |
                      v                            v
            +----------------+              +-----------------+
            |RequestTransform|(*)-+    +-(*)|ResponseTransform|
            +----------------+    |    |    +-----------------+
                    (*)           |    |
                     |            |    |
                     |            v    v
                     |       +---------------+
                     |       |HeaderTransform|(*)-+
                     |       +---------------+    |
                     |                            |
                     v                            |
             +-----------------+                  |
             |SyntheticResponse|(*)--+            v
             +-----------------+     |      +----------+
                                     +----->|HTTPHeader|
                                            +----------+
  ]]></artwork>
</figure>
'''

table_stagemetadata = '''
			<texttable align="left" style="all" title="StageMetadata stages">
			  <ttcol >Stage</ttcol>
			  <ttcol >request-transform</ttcol>
			  <ttcol >response-transform</ttcol>

			  <c>clientRequest</c>
              <c>yes</c>
              <c>yes</c>

			  <c>originRequest</c>
              <c>yes</c>
              <c>yes</c>

			  <c>originResponse</c>
              <c>no</c>
              <c>yes</c>

			  <c>clientResponse</c>
              <c>no</c>
              <c>yes</c>

			</texttable>
'''

import os #os module imported here

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
    print (filename)
    with open(location + filename, 'r') as file :
      filedata = file.read()

      print (re.findall('\[RFC[0-9].+\]', filedata))

    # Replace the target string
    filedata = filedata.replace('[RFC8006]', '<xref target="RFC8006" />')
    filedata = filedata.replace('[RFC8008]', '<xref target="RFC8008" />')
    filedata = filedata.replace('[RFC9110]', '<xref target="RFC9110" />')
    filedata = filedata.replace('[RFC9110]', '<xref target="RFC9110" />')
    filedata = filedata.replace('[RFC5861]', '<xref target="RFC5861" />')
    filedata = filedata.replace('[RFC1034]', '<xref target="RFC1034" />')
    filedata = filedata.replace('[RFC1123]', '<xref target="RFC1123" />')
    filedata = filedata.replace('[RFC7694]', '<xref target="RFC7694" />')
    filedata = filedata.replace('[RFC7736]', '<xref target="RFC7736" />')
    filedata = filedata.replace('[RFC5652]', '<xref target="RFC5652" />')
    filedata = filedata.replace('[CDNI-MEL]', '<xref target="CDNI-MEL" />')
    filedata = filedata.replace('[AWSv4Method]', '<xref target="AWSv4Method" />')
    filedata = filedata.replace('[X.509]', '<xref target="X.509" />')
    filedata = filedata.replace('[URI.signing]', '<xref target="URI.signing" />')
    filedata = filedata.replace('[W3C]', '<xref target="W3C" />')

    filedata = filedata.replace('[SVTA2032]', '<xref target="SVTA2032" />')
    filedata = filedata.replace('[SVTA2031]', '<xref target="SVTA2031" />')
    filedata = filedata.replace('[SVTA2038]', '<xref target="SVTA2038" />')

    # Replace artwork
    filedata = filedata.replace('Figure 1: CDNI Metadata Model with Extensions', figure_1)
    filedata = filedata.replace('Figure 2: Processing Stages', figure_2_processing_stages)
    filedata = filedata.replace('Figure 3: CDNI ProcessingStages metadata model with contained objects', figure_3)
    filedata = filedata.replace('Table 2: StageMetadata stages', '')

    # Write the file out again
    with open(location+filename, 'w') as file:
      file.write(filedata)


print ("DONT FORGET: ")
print ("STAGEMETADATA TABLE_2")
print (table_stagemetadata)
