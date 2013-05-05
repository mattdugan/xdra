#!/bin/env python
import xmlio as ElementTree
from modelparser import ModelParser

if __name__ == "__main__":
  """\brief test main for ModelParser

  Tries a number of test models in order and prints their output along with
  debugging information to the console window.  It searches for model#.xml
  in the current directory where # is an integer 1-6.
  """
  _debug=1
  sourceTXT="""
  <blog>
    <post>
      <title>Title1</title>
      <date>01012001</date>
      <content>Post 1</content>
    </post>
    <post>
      <title>Title2</title>
      <date>01022001</date>
      <content>Post 2</content>
    </post>
    <post>
      <title>Title3</title>
      <date>01032001</date>
      <content>Post 3</content>
    </post>
    <post>
      <title>Title4</title>
      <date>01042001</date>
      <content>Post 4</content>
    </post>
  </blog>"""

  modelTXT="""
  <xdra:model xmlns:xdra="xdra">
    <xdra:source type="files" path="samples/data" name="blog" recursive="0" />
    <xdra:literal>&lt;blog&gt;</xdra:literal>
    <xdra:query type="fetch" path=".//blog">
    <xdra:action>
      <xdra:getnode path="./post">
      <xdra:literal>&lt;post&gt;</xdra:literal>
        <xdra:literal>&lt;para&gt;</xdra:literal>
        <xdra:getcontent path="./title" />
        <xdra:literal>&lt;/para&gt;</xdra:literal>
        <xdra:literal>&lt;para&gt;</xdra:literal>
        <xdra:getcontent path="./content" />
        <xdra:literal>&lt;/para&gt;</xdra:literal>
      <xdra:literal>&lt;/post&gt;</xdra:literal>
      </xdra:getnode>
    </xdra:action>
    </xdra:query>
    <xdra:literal>&lt;/blog&gt;</xdra:literal>
  </xdra:model>"""

  modelTXT_2="""
  <xdra:model xmlns:xdra="xdra">
    <xdra:source type="files" path="samples/data" name="blog" recursive="0" />
    <blog>
    <xdra:query type="fetch" path=".//blog">
    <xdra:action>
      <xdra:getnode path="./post">
      <post>
        <para>
        <xdra:getcontent path="./title" />
        </para>
        <para>
        <xdra:getcontent path="./content" />
        </para>
      </post>
      </xdra:getnode>
    </xdra:action>
    </xdra:query>
    </blog>
  </xdra:model>"""
  source=ElementTree.XML(sourceTXT)
  doc=ElementTree.XML(modelTXT)
  parser=ModelParser(globalsources=[source])
  print "\n----------------------\nParsing doc1\n----------------------\n"
  data=parser.parseModel(doc)
  print "result=",data
  parser.reset()
  print "\n----------------------\nParsing doc2\n----------------------\n"
  doc=ElementTree.XML(modelTXT_2)
  data=parser.parseModel(doc)
  print "result=",data
  parser.reset()
  print "\n----------------------\nParsing doc3\n----------------------\n"
  doc=ElementTree.XML(open('samples/model1.xml','r').read())
  data=parser.parseModel(doc)
  print "result=",data
  parser.reset()
  print "\n----------------------\nParsing doc4\n----------------------\n"
  doc=ElementTree.XML(open('samples/model2.xml','r').read())
  data=parser.parseModel(doc)
  print "result=",data
  parser.reset()
  print "\n----------------------\nParsing doc5\n----------------------\n"
  doc=ElementTree.XML(open('samples/model3.xml','r').read())
  data=parser.parseModel(doc)
  print "result=",data
  parser.reset()
  print "\n----------------------\nParsing doc6\n----------------------\n"
  doc=ElementTree.XML(open('samples/model4.xml','r').read())
  data=parser.parseModel(doc)
  print "result=",data
  parser.reset()
  print "\n----------------------\nParsing doc7\n----------------------\n"
  doc=ElementTree.XML(open('samples/model5.xml','r').read())
  data=parser.parseModel(doc)
  print "result=",data
  parser.reset()
