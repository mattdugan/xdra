xdra
====

Note:  This is a very old project experimenting with XML parsing via 
an XML based execution language.

XDRA is an acronym for "XML Document Re-Aggregator" which is a fancy way
of saying that it turns a bunch of existing well-formed tag-based markup
data into data sources which can be queried, transformed, selected and
eventually written to standard out or to an output file of choice.

The XDRA model file defines all parameters for sourcing input files
(even recursively) or input URL (such as an RSS feed).  For sample
model files, see the samples directory.

The source is composed of only a few classes.  The only directly
executable files are test.py and modelparser.py.

Usage:

./modelparser.py name_of_model.xml


