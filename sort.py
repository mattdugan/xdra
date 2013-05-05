# \file sort.py
# (c) Matt Dugan
#
# \brief Sorts a list of XML objects according to a common key node

import xmlio as ElementTree

class Sort:
	"""\brief Sorts a list of XML objects according to a common key node

	The Sort class is used to perform sorting on lists of results from
	the ModelParser in response to the \a sort and \a reversesort attributes
	of the xdra:action directive in a xdra:model.  In either case the datalist
	is sorted according to the value of the text contents of a key node.
	"""

	def sort(self, datalist, key, reverse):
		"""\brief Sorts a list of XML objects by the text value of child <key>

		\em sort() performs either an ascending or descending sort of
		\a datalist according to the boolean value of \a reverse.  If
		\a reverse is false, then an ascending sort is performed.  Otherwise,
		a descending sort is performed on datalist.  When a sort is
		executed, the text value of a child node with tag 'key' is matched
		and used as the value which to sort against.  In this way, nodes are
		placed in "key order" before the list is returned to the controlling
		program.

		\param datalist a list of nodes in response to a query/action/getnode triplet
		\param key the tag name of the node to sort against
		\param reverse boolean flag controlling ascending (False) or descending sorts
		"""
		if len(datalist) > 1:
			if reverse:
				#descending sort
				datalist.sort(lambda x, y: cmp(y.findtext(".//"+key).lower(), \
						x.findtext(".//"+key).lower()))
				#datalist.reverse() not needed when you switch x and y!
				return datalist
			else:
				#ascending sort
				datalist.sort(lambda x, y: cmp(x.findtext(".//"+key).lower(), \
						y.findtext(".//"+key).lower()))
				return datalist
		else:
			return datalist
