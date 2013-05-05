# \file executor.py
# (c) Matthew Dugan
#
# \brief Runs embedded python code in custom xdra:source or xdra:action elements

import xmlio as ElementTree
import cache

class Executor:
	"""\brief Runs embedded python code in custom xdra:source or xdra:action elements

	Executor is used to store, process, and execute embedded python scripting
	that appears in xdra:source or xdra:action directives while using the
	\a custom attribute.  The compiled byte-code objects are stored in a cache
	according to an md5 hash of their source code and retrieved dynamically so
	that the byte-code compiling process is not recurring.  The execution is
	done in a local context, so two variables are available to the process:
	xdra_tree and xdra_outtext.  In addition, all system libraries and the
	XML object library are available.
	"""

	def __init__(self, name=None, code=None, tree=None):
		"""\brief Initializes an instance of the Executor class

		The executor object initializes an md5 cache object to store
		code objects according to an md5 hash of the source code.  Attributes
		it stores include a name attribute, the code data, and the current
		XML tree context.

		\param name the name of the source given in the xdra:source directive
		\param code the source code for the embedded python script
		\param tree the current tree context of the XML object
		"""
		self.__execCache=cache.Cache()
		self.setName(name)
		self.setCode(code)
		self.setTree(tree)
		self.out=None
		self.key=None

	def setName(self, name):
		"""\brief Sets the name attribute to the current Executor context

		\em setName() is used to provide the name attribute to the Executor
		instance after it has been initalized.

		\param name the value to set the name attribute
		"""
		self.name=name

	def setTree(self, tree):
		"""\brief Sets the tree XML object to the current Executor context

		\em setTree() is used to provide the XML object tree to the Executor
		instance after it has been initalized.

		\param tree the XML object tree to set as the local tree
		"""
		self.tree=tree

	def setCode(self, code):
		"""\brief Sets the source code to the current Executor context

		\em setCode() is used to provide the source code to the Executor
		instance after it has been initalized.  The code is set to include
		only single-byte new line characters, since two-byte carriage-return
		and newline formatting systems (win32) will not work in the exec
		library function.  The code is used to calculate a unique md5 hash
		which is returned to the calling program.

		\param code the source code to be use in the Executor object
		\return a md5 hash representing the source code from the code parameter
		"""
		if code:
			self.code=code.replace('\r\n','\n') # 2-byte returns break execution.
			self.key=self.__execCache.getkey(code)

	def runAction(self):
		"""\brief Executes code given within a custom xdra:action directive

		\em runAction() executes code given as the text property of an
		xdra:action element.  First, the current XML object tree, as pooled
		from the sources and query/getnode pairs is set to the local tree and
		the output text is initialized.  If the cache contains a pre-compiled
		object corresponding to the md5 hash of the current source code, then
		use that object.  Otherwise, compile the code and add it to the cache.
		Next, execute the compiled code (which may or may not modify the tree)
		and return any data stored into the xdra_outtext variable.

		\return any output text stored into the predefined xdra_outtext variable
		"""
		xdra_tree=self.tree
		xdra_outtext=""
		if not self.__execCache.contains(self.key):
			self.out = compile(self.code,'<string>','exec')
			self.__execCache.add(self.out,self.key)
		else:
			self.out = self.__execCache.retrieve(self.key)
		exec(self.out)
		return xdra_outtext

	def runSource(self):
		"""\brief Executes code given within a custom xdra:source directive

		\em runSource() executes code given as the text property of an
		xdra:source element.  First, the current XML object tree is made
		available, which will be populated during the code execution.  Next,
		the cache is checked to see if an object corresponding to the md5
		hash of the current source code is available, and, if so, it is used
		without being recompiled.  Otherwise, the code is compiled and stored
		into the cache.  Next, the code is executed and the XML object tree
		which should be populated by the code execution is returned.

		\return the modified XML object source tree
		"""
		xdra_tree=self.tree
		if not self.__execCache.contains(self.key):
			self.out = compile(self.code,'<string>','exec')
			self.__execCache.add(self.out,self.key)
		else:
			self.out = __execCache.retrieve(self.key)
		exec(self.out)
		return xdra_tree

if __name__=="__main__":
	"""\brief test main for Executor

	Using a file, 1.xml, the file is parsed into a document object and a
	procedure which compiles some code and performs operations on the
	output string is executed, then it is verified that the local context
	was enforced and the output string is modified.
	"""
	root = ElementTree.parse('1.xml').getroot()
	output=""
	ccode="""
    output=ElementTree.tostring(root)
    print output
    output="This is output"
  """
	print ccode
	ccode.replace('\r\n','\n')
	out=compile(ccode,'<string>','exec')
	exec(out)
	print output
