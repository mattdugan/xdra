#!/bin/env python
# \file modelparser.py
# (c) Matt Dugan
#
# \brief Parses the XDRA model document for commands


import xmlio as ElementTree
import conglomerator, sort, executor
import os

_debug = os.environ.get("DEBUG",0)

class ModelParser:
  """\brief Parses the XDRA model document for commands

  The fundamental methods of ModelParser include \em parseModel() and
  \em reset().  Together, they will perform a complete execution and
  generation cycle of the output document, which is returned as a string.
  \em parseModel() is called on a \em ModelParser object to analyze the
  model and embedded XML tags and perform any processing necessary before
  returning the output document.  \em reset() is used to clear the current
  model and parse a new one without having to declare a new instance of the
  parser.  The model can handle sources of files and URL types,
  along with a myriad of options, see the individual methods and the
  documentation for more explanations.
  """

  modelTAG="{xdra}model"
  sourceTAG="{xdra}source"
  queryTAG="{xdra}query"
  actionTAG="{xdra}action"
  getnodeTAG="{xdra}getnode"
  getcontentTAG="{xdra}getcontent"
  literalTAG="{xdra}literal"

  def __init__(self, globalsources=[], localsources=[]):
    """\brief Initializes a new ModelParser instance

    Init requires no arguments, and simply sets up the parsing environment.
    These include empty lists for global, and local sources, an
    instance of the code executor, and the default "tab size".  The only
    attribute you may want to modify is \a tabSize which is set to 4 spaces
    by default.
    """
    self.tabSize="    " #4 spaces
    self.globalsources=globalsources
    self.localsources=localsources
    self.runner=executor.Executor()
    self.conglomerator=conglomerator.FileInput()
    self.sort=sort.Sort()
    self.reset()

  def reset(self, keepsources=False):
    """\brief Resets the current ModelParser instance to defaults

    \em reset() will return the current ModelParser to its initial settings,
    preparing it for use with another model without requiring a new instance
    to be used.  The fundamental reason for this was to make ModelParser
    session safe, if not explicitly session aware, so that a given code path
    could rely on it's own instance of ModelParser without eating up memory
    making several instances.  \em keepsources is initialized to \em False,
    and will clear all sources from the current ModelParser context.  However,
    this may be changed to \em True if multiple models should use the same
    sources without explicitly redeclaring them.

    \param keepsources (False) Clear the sources when the parser is reset
    """
    if not keepsources:
      self.globalsources=[]
      self.localsources=[]
    self.querypath=""
    self.level=0
    self.atype="" #the current action to be performed
    self.skey="" #a key to sort against for an action

  def parseXML(self,node,item=None):
    """\brief Parse and arbitrary XML node encountered in the model

    \em parseXML() works very similarly to the parseModel() method except
    that the current node should be an un-recognized node in the XDRA
    system.  In this way arbitrary nodes (such as HTML or XML markup) can
    be preserved in the output document, making a very easy and intuitive
    way to structure the output document using XML style tags.  Note that
    the text attributes of arbitrary tags are SILENTLY IGNORED.  If you
    want text to appear directly in the output, place it inside of
    <xdra:literal></xdra:literal> tags.  The item parameter is used
    internally to carry the current iteration of a getnode result, if there
    is one.

    \param node The current non-XDRA tag to parse
    \param item A carry variable containing a current getnode source item
    \return a string containing the output of this node and any child nodes
    """
    datalist=[]
    if self.level>1: datalist.append("\n")
    for count in range(1,self.level): datalist.append(self.tabSize)
    datalist.append("<"+node.tag)
    for key in node.keys():
      datalist.append(" "+key+"=\""+node.attrib[key]+"\"")
    if not node._children: datalist.append(" />")
    else:
      datalist.append(">")
      #if node.text: datalist.append(node.text)
      for child in node.getchildren():
        data=""
        if child.tag == self.sourceTAG:
          if _debug: print "parseXML: calling parseSource for "+child.tag
          self.parseSource(child)
        elif child.tag == self.queryTAG:
          if _debug: print "parseXML: calling parseQuery for "+child.tag
          data=self.parseQuery(child)
        elif child.tag == self.literalTAG:
          if _debug: print "parseXML: calling parseLiteral for "+child.tag
          data=self.parseLiteral(child)
        elif child.tag == self.actionTAG:
          if _debug: print "parseXML: calling parseAction for "+child.tag
          data=self.parseAction(child)
        elif child.tag == self.getnodeTAG:
          if _debug: print "parseXML: calling parseGetNode for "+child.tag
          data=self.parseGetNode(child)
          if data: datalist.append("\n")
        elif child.tag == self.getcontentTAG:
          if _debug: print "parseXML: calling parseGetContent for "+child.tag
          data=self.parseGetContent(child,item)
          if data: datalist.append("\n")
        elif child.tag == self.modelTAG:
          path=child.attrib.get("path")
          if path:
            try:
              cmodel=ElementTree.parse(path).getroot()
              if _debug: print "parseXML: calling parseModel for "+child.tag
              #new instance just in case
              parser=ModelParser(self.globalsources,self.localsources)
              data=parser.parseModel(cmodel)
              parser.reset() #just in case
              print "Outputting data\n",data
              if data: datalist.append("\n")
            except:
              if _debug: print "parseXML: invalid child model at "+path
          elif not child.getchildren():
            if _debug: print "parseXML: if no path, xdra:model must have children"
          else:
            try:
              if _debug: print "parseXML: calling parseModel for "+child.tag
              #new instance just in case
              parser=ModelParser(self.globalsources,self.localsources)
              data=parser.parseModel(child)
              parser.reset() #just in case
              if data: datalist.append("\n")
            except:
              if _debug: print "parseXML: invalid child model "+child.tag
        else:
          if _debug: print "parseXML: calling parseXML for "+child.tag
          data=self.parseXML(child,item)
        if data: datalist.append(data)
        #if child.tail: datalist.append(child.tail)
      datalist.append("\n")
      for count in range(1,self.level): datalist.append(self.tabSize)
      datalist.append("</"+node.tag+">")
    if datalist: data="".join(datalist)
    return data

  def parseGetContent(self,node,source):
    """\brief Parses an xdra:getcontent for node text from source

    \em parseGetContent() retrieves the text information contained in an
    individual source element according to the relative path given in the
    xdra:getcontent attributes.  Only the text is retrieved, not necessarily
    the full contents of the source node including sub-nodes (if they exist)

    \param node The current xdra:getcontent node
    \param source The current source item to retrieve text from
    \return a string containing the output of this node
    """
    path = node.attrib.get("path")
    if not path:
      if _debug: print "No path in parseGetContent"
      return None
    if _debug: print "parseGetContent: calling source.findtext for "+path
    data = source.findtext(path)
    if _debug: print data
    return data

  def parseLiteral(self,node):
    """\brief Parses an xdra:literal for its contents into the output

    \em parseLiteral() echos its textual and well-formed XML contents
    directly into the the current output.  Since the form is <xdra:literal>
    </xdra:literal>, any tags placed with the xdra:literal elements must be
    well-formed, i.e. all child nodes must be terminated within their parent
    element.  If a single tag is desired, then the HTML escape sequences
    should be used to construct them, for example &lt;child&gt; will echo
    a single unterminated <child> tag into the output without producing an
    error.

    \param node The current xdra:literal node
    \return a string containing the contents of the xdra:literal node
    """
    datalist = []
    if node.text: datalist.append(node.text)
    for child in node.getchildren():
      datalist.append(ElementTree.tostring(child))
    data = "".join(datalist)
    return data

  def parseGetNode(self,node):
    """\brief Parses an xdra:getnode directive and returns the sum of its output

    \em parseGetNode() handles the fetching of sources defined in the model
    and sets the local context for the getnode operation and child
    getcontent directives.  File and URL sources are all-inclusive.  The i
    results to query/getnode path pair are appended to a large list of
    "matched nodes" which is then iterated over according to the processing
    instructions contained with the xdra:getnode element, or echoed verbatim
    to the output where xdra:getnode has no child elements.

    \param node the current xdra:getnode element
    \return a string containing the output of this node and any child nodes
    """
    path = node.attrib.get("path")
    datalist = []
    itemlist=[]
    if not path:
      if _debug: print "No path in parseGetNode, setting path to ",self.querypath
      path=self.querypath
    for source in self.globalsources:
      if _debug: print "parseGetNode checking path",path,"in source",source
      itemlist.extend(source.findall(path))
    if _debug: print "parseGetNode itemlist:",itemlist

    if self.atype:
      if self.atype.endswith("sort"):
        if self.skey:
          if self.atype=="reversesort":
            if _debug: print "parseGetNode: calling sort reversesort",itemlist
            self.sort.sort(itemlist,self.skey,reverse=True)
          elif self.atype=="sort":
            if _debug: print "parseGetNode: calling sort",itemlist
            self.sort.sort(itemlist,self.skey,reverse=False)
          else:
            if _debug: print "parseGetNode: invalid sort type ",atype
        else:
          if _debug: print "parseGetNode: missing key for sort"
      elif self.atype=="custom":
        xdra_root=ElementTree.Element("root")
        for item in itemlist:
          xdra_root.append(item)
        self.runner.setTree(xdra_root)
        datalist.append(self.runner.runAction()) #itemlist is now updated
        itemlist=[item for item in xdra_root.getchildren()]
    if node.getchildren():
      for item in itemlist:
        for child in node.getchildren():
          if child.tag == self.getcontentTAG:
            if _debug: print "parseGetNode: calling parseGetContent for "+child.tag
            if item:
              data=self.parseGetContent(child, item)
              if data: datalist.append(data)
          elif child.tag == self.literalTAG:
            if _debug: print "parseGetNode: calling parseLiteral for "+child.tag
            if item:
              data=self.parseLiteral(child)
              if data: datalist.append(data)
          else:
            if _debug: print "parseGetNode: calling parseXML for "+child.tag
            if item:
              self.level+=1
              data=self.parseXML(child, item)
              self.level-=1
              if data: datalist.append(data)
    else:
      for item in itemlist:
        if item: datalist.append(ElementTree.tostring(item))
    if datalist:
      data="".join(datalist)
      return data
    else:
      return None

  def parseAction(self,node):
    """\brief Parses an xdra:action directive and returns the output

    \em parseAction() provides the functionality to modify the document
    tree in place during model execution.  The environment is set up
    here and executed during the \em parseGetNode() call where all result
    items are available.  If the source type is detected to be "custom",
    then a model-level instance of the \em executor class is set up with
    the source code (the text element of a custom action) so that it may
    be executed in place when the result tree is available from the sources.

    \param node The current xdra:action element
    \return a string containing the output of this node and any child nodes
    """
    datalist=[]
    childlist=node._children
    self.atype=node.attrib.get("type")
    self.skey=node.attrib.get("key")
    if _debug: print "parseAction: action type is ",self.atype
    if self.atype=="custom":
      self.runner.setName(node.attrib.get("name"))
      self.runner.setCode(node.text)
    for child in childlist:
      if child.tag==self.getnodeTAG:
        if _debug: print "parseAction: calling parseGetNode for "+child.tag
        data=self.parseGetNode(child)
        if data: datalist.append(data)
      elif child.tag == self.literalTAG:
        if _debug: print "parseModel: calling parseLiteral for "+child.tag
        data=self.parseLiteral(child)
        if data: datalist.append(data)
      else:
        if _debug: print "parseAction: calling parseXML for "+child.tag
        data=self.parseXML(child)
        if data: datalist.append(data)
    self.atype=""
    self.skey=""
    if datalist:
      data="".join(datalist)
      return data
    else:
      return None

  def parseQuery(self,node):
    """\brief Parses an xdra:query directive and returns the output

    \em parseQuery() handles setting the path context for subsequent
    calls to \em parseGetNode().  Currently the only supported query
    directive is \em fetch, where all matching sources to the \a path
    attribute are placed into a list to be modified and restructured
    using the xdra:action, xdra:getnode, and xdra:getcontent directives,
    as well as liberal use of xdra:literal and arbitrary XML elements.

    \param node the current xdra:query element
    \return a string containing the output of this node and any child nodes
    """
    self.querypath=node.attrib.get("path")
    if self.querypath:
      if self.querypath.endswith("/"):
        self.querypath = self.querypath[:-1]
    else:
      if _debug: print "parseQuery: no path in query!"

    self.localsources=[]
    datalist=[]
    qtype=node.attrib.get("type")
    if _debug: print "parseQuery: setting global path to ",self.querypath
    for child in node.getchildren():
      if child.tag==self.actionTAG:
        if _debug: print "parseQuery: calling parseAction for "+child.tag
        data=self.parseAction(child)
        if data: datalist.append(data)
      elif child.tag==self.sourceTAG:
        if _debug: print "parseQuery: calling parseSource for "+child.tag
        localsources.append(self.parseSource(child, local=True))
      elif child.tag == self.literalTAG:
        if _debug: print "parseModel: calling parseLiteral for "+child.tag
        data=self.parseLiteral(child)
        if data: datalist.append(data)
      else:
        if _debug: print "parseQuery: calling parseXML for "+child.tag
        self.level+=1
        data=self.parseXML(child)
        self.level-=1
        if data: datalist.append(data)
    if datalist:
      data="".join(datalist)
      return data
    else:
      return None

  def parseSource(self,node,local=False):
    """\brief Parses an xdra:source declaration and stores for future use

    \em parseSource() handles the declaration of valid xdra:source
    elements including file sources (from directories containing XML files)
    and URL sources When declaring file sources, there is an attribute to
    process the path directory recursively.  When declaring URL sources, the
    URL must be valid.  When a valid source is encountered it is added to the
    class level source list to be processed in response to query/getnode pairs.

    \param node the current xdra:source element
    \param local defines if the source is local to the current query or not
    """
    stype=node.attrib.get("type")
    if stype=="files":
      path = node.attrib.get("path")
      rootname = node.attrib.get("name")
      if not (path and rootname):
        if _debug: print "parseSource: no path or rootname found"
      else:
        if node.attrib.get("recursive") in ("1","yes"):
          source=self.conglomerator.getDocObj(path,rootname,recursive=True)
        else:
          source=self.conglomerator.getDocObj(path,rootname,recursive=False)
        if not local:
          if source: self.globalsources.append(source)
        else:
          if source: self.localsources.append(source)
        if _debug:
          print "parseSource: new source list: ",self.globalsources,self.localsources
    elif stype=="custom":
      sname=node.attrib.get("name")
      if _debug: print "parseSource: processing custom source",sname
      self.runner.setName(sname)
      self.runner.setCode(node.text)
      sroot=ElementTree.Element(sname)
      self.runner.setTree(sroot)
      sroot=self.runner.runSource() #get xdra_tree
      self.globalsources.append(sroot) #add the new source tree
      if _debug: print "parseSource: new source list: ",self.globalsources,self.localsources
    elif stype=="url":
      rootname=node.attrib.get("name")
      path=node.attrib.get("path")
      source=self.conglomerator.getDocObj(path,rootname,url=True)
      if not local:
        if source: self.globalsources.append(source)
      else:
        if source: self.localsources.append(source)
      if _debug:
        print "parseSource: from url ",path,"\n",ElementTree.tostring(source)
        print "parseSource: new source list: ",self.globalsources,self.localsources
    else:
      if _debug: print "parseSource: Undefined source type ",stype

  def parseModel(self,doc):
    """\brief Parses an xdra:model set given as the root node of doc

    \em parseModel() is the central controlling method for obtaining the
    output of an xdra:model document.  It expects the top level node in
    the \a doc xml object to be an xdra:model tag, and will not execute
    otherwise.  During execution, child nodes are parsed in document order,
    where valid tags are xdra:source, xdra:query, and xdra:literal.  Other
    tags may be included, of course, but they will be processed as
    arbitrary XML nodes and not as xdra directives.  The entire output of
    the model is aggregated and returned as a string.

    \param doc an XML object where xdra:model is the root node
    \return a string containing the final output of the model
    """
    if doc.tag != self.modelTAG: return None
    output=[]
    #if doc.text: output.append(doc.text)
    for child in doc.getchildren():
      if child.tag == self.sourceTAG:
        if _debug: print "parseModel: calling parseSource for "+child.tag
        self.parseSource(child, local=False)
      elif child.tag == self.queryTAG:
        if _debug: print "parseModel: calling parseQuery for "+child.tag
        data=self.parseQuery(child)
        if data: output.append(data)
      elif child.tag == self.literalTAG:
        if _debug: print "parseModel: calling parseLiteral for "+child.tag
        data=self.parseLiteral(child)
        if data: output.append(data)
      elif child.tag == self.modelTAG:
        path=child.attrib.get("path")
        if path:
          try:
            cmodel=ElementTree.parse(path).getroot()
            if _debug: print "parseModel: calling parseModel for "+child.tag
            #new instance just in case
            parser=ModelParser(self.globalsources,self.localsources)
            data=parser.parseModel(cmodel)
            if data: output.append(data)
          except:
            if _debug: print "parseModel: invalid child model at "+path
        elif not child.getchildren():
          try:
            if _debug: print "parseModel: calling parseModel for "+child.tag
            #new instance just in case
            parser=ModelParser(self.globalsources,self.localsources)
            data=parser.parseModel(child)
            if data: output.append(data)
          except:
            if _debug: print "parseModel: invalid child model "+child.tag
      else:
        if _debug: print "parseModel: calling parseXML for "+child.tag
        self.level+=1
        data=self.parseXML(child)
        self.level-=1
        if data: output.append(data)
    if doc.tail: output.append(doc.tail)
    if output: data="".join(output)
    else: data="No output was generated using the current model."
    file=doc.attrib.get("output")
    if file:
      fp=open(file,'w')
      fp.write(data)
    return data


if __name__ == "__main__":
  import sys

  if len(sys.argv) != 2:
    print """
          Usage: modelparser.py <model_definition.xml>
          """
    exit(2)


  doc=ElementTree.XML(open(sys.argv[1],'r').read())
  parser=ModelParser()
  data=parser.parseModel(doc)
  print data
