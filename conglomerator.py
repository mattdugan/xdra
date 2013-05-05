# \file congolmerator.py
# (c) Matt Dugan
#
# \brief Brings several xml files into one big xmlio object


import os, glob, operator
import xmlio as ElementTree

class FileInput:
  """\brief Brings several xml files into one big xmlio object

  The File Input module retrieves a comprehensize list of all .xml files
  matching a particular base path, with optional recursion, and reads
  them in one by one into an XML tree structure.  The root tag of the
  new XML tree is given as a parameter and the tree is returned after all
  .xml files have been sucessfully parsed and their contents added to the
  XML tree.  The filelist is kept in case it needs to be re-referenced.
  """

  def __init__(self):
    """\brief Initializes a new FileInput session

    Creates a file list to hold the absolute paths of the filenames
    found by the wildcard match and sets up the XML doc to be used
    later by a call to /em getDocObj().
    """
    self.filelist=[]
    self.doc=None

  def getDocObj( self, path, rootname, recursive=False, url=False ):
    """\brief Retrieves an XML object for *.xml in /em path

    Returns an in-memory document object representing the combined
    contents of several files on disk, where the search is (optionally)
    recursive, and appends the parsed content of each XML file to the
    parent document having the tag \em rootname.

    \param path The path at which to start the search
    \param rootname The name of the root node of the output XML tree
    \param recursive A boolean defining whether a recursive search should be performed.
    \return the aggregated output XML document object
    """
    self.doc = ElementTree.Element(rootname)
    tree=None
    if not url:
      if recursive:
        self._getFilesRecursive( path )
      else:
        self._getFiles( path )
      for filename in self.filelist:
        tree = ElementTree.XML( self._openanything(filename).read() )
        self.doc.append(tree)
    else:
      tree=ElementTree.XML( self._openanything(path).read() )
      self.doc.append(tree)
    return self.doc

  def _getFilesRecursive( self, path ):
    """\brief Performs the recursive matching operation to \em filelist

    Does a simple recursive accumulation of the files in a starting
    directory and all files below the directory.  All filenames are
    stored with their full path into \em filelist.

    \param path The path at which to start the search
    """
    for root, dirs, files in os.walk( path ):
      for name in files:
        if name.endswith('.xml'):
          self.filelist.append(os.path.normpath(os.path.join(root, name)))

  def _getFiles( self, path ):
    """\brief Performs the non-recursive matching operation to \em filelist

    Stores all matching filenames immediately withing the starting path
    into \em filelist.  No recursion is performed.

    \param path The path from which to retrieve the .xml files
    """
    self.filelist = glob.glob(os.path.normpath(operator.concat(path, '/*.xml')))

  def _openanything(self,source):
    """URI, filename, or string --> stream (c) Mark Pilgrim - Dive Into Python

    This function lets you define parsers that take any input source
    (URL, pathname to local or network file, or actual data as a string)
    and deal with it in a uniform manner.  Returned object is guaranteed
    to have all the basic stdio read methods (read, readline, readlines).
    Just .close() the object when you're done with it.

    \param source the URI to attempt to read, be it a file, URL, or other
    """
    if hasattr(source, "read"):
      return source

    if source == '-':
      import sys
      return sys.stdin

    # try to open with urllib (if source is http, ftp, or file URL)
    import urllib
    try:
      return urllib.urlopen(source)
    except (IOError, OSError):
      pass

    # try to open with native open function (if source is pathname)
    try:
      return open(source)
    except (IOError, OSError):
      pass

    # treat source as string
    import StringIO
    return StringIO.StringIO(str(source))
