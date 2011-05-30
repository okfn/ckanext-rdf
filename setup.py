from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(
	name='ckanext-rdf',
	version=version,
	description="RDF/LinkedData support package",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Open Knowledge Foundation',
	author_email='info@okfn.org',
	url='http://okfn.org',
	license='AGPL v3',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.rdf'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
        "rdflib>=3.0.0",
        "rdfextras>=0.1"
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	# myplugin=ckanext.rdf:PluginClass
	""",
)
