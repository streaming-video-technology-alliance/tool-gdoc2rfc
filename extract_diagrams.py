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


import os

config_parser = configparser.ConfigParser()
config_parser.read('configuration.conf')
config = config_parser['extract_docx']

location = config['work_directory'] +'/generated-xml/' # get present working directory location here


for filename in os.listdir(location):
    # Read in the file
    print (filename)
    with open(location + filename, 'r') as file :
      filedata = file.read()

    # Replace artwork
    filedata = filedata.replace('Figure 1: CDNI Metadata Model with Extensions', figure_1)
    filedata = filedata.replace('Figure 2: Processing Stages', figure_2_processing_stages)
    filedata = filedata.replace('Figure 3: CDNI ProcessingStages metadata model with contained objects', figure_3)

    # Write the file out again
    with open(location+filename, 'w') as file:
      file.write(filedata)

