# \file cache.py
# (c) Matthew Dugan
#
# \brief Keeps a cache of objects with md5 checksums

import md5

class Cache:
	"""\brief Keeps a cache of objects with md5 checksums
	
	The Cache module utilizes the md5 library to generate unique
	checksums on arbitrary objects.  Optionally, the key can be
	generated from a custom object (potentially a string).  Ideally
	this is used when generating a key from the object that should
	be stored in the cache would be expensive, so we can instead
	use a unique string to describe it and make the key from the 
	string instead.  The normal usage is getkey(keytext), add(item,key),
	if contains(key): retrieve(key), remove(key).
	"""	
	
	def __init__(self, maxsize=0):
		"""\brief Initialize a new cache object
		
		Creates an attribute \a cache as a dictionary to store objects
		matched by a key (an md5 checksum string).  \em maxsize is present
		to limit the cache to less than a specific number of commonly
		reference elements, but it is currently not enforced, since no
		method to perform access profiling is currently implemented in this
		module.
		
		\a cache The dictionary of key: object pairs
		\param maxsize The maximum size of the cache, currently not enforced.
		"""
		self.cache={}
		self.__maxsize=maxsize #currently not enforced, need use profiling first

	def getkey(self, keytext):
		"""\brief Retrieve an md5 checksum based on the value \em keytext
		
		Creates a new md5 checksum from the value of the \em keytext
		parameter and returns the checksum string.  \em keytext can be any
		object, but is commonly a string that uniquely represents the 
		object to be stored later.
		
		\param keytext The object to generate a new md5 checksum from
		\return the md5 checksum string
		"""
		key=md5.new(keytext)
		return key
			
	def add(self, item, key=None):
		"""\brief Adds a new object to the cache
		
		An object, given by \em item, is added to the cache dictionary.  If 
		a \em key is given then the given key will be used and no new key
		will be created.  This is useful when combined with the \em getkey()
		function above.  If no key is given, one will be generated for 
		\em item and returned.
		
		\param item The object to add to the cache
		\param key Use as the key for \em item in the cache
		\return the key used to place \em item in the cache
		"""
		if not key:
			key=md5.new(item)
		self.cache[key]=item
		return key

	def remove(self, key):
		"""\brief Removes an object from the cache
		
		The object matching the given \em key is removed from the cache. If
		the \em key does not exist then the action to remove is silently
		discarded.
		
		/param key The key corresponding to the object to remove
		"""
		try:
			del self.cache[key]
		except:
			return
	
	def contains(self, key):
		"""\brief Checks for the existence of a key: object pair
		
		Given a \em key to match in the cache, return \em True if a
		corresponding object exists, or \em False if not.  
		
		\param key The key to match in the cache
		\return True or False if the key is matched or not
		"""
		try:
			if self.cache[key]:
				return True
			else:
				return False
		except:
			return False
	
	def retrieve(self, key):
		"""\brief Retrieves the object having a particular key
		
		Given a \em key to match in the cache, return the corresponding
		object item stored in the cache.  If no item matching the 
		\em key is found in the cache, then \em None is returned as a
		null object.
		
		\param key The key to match in the cache
		\return the object matching key or None if not found
		"""
		try:
			return self.cache[key]
		except:
			return None
