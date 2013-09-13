# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function, unicode_literals

import os
import sys

sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('_themes'))

import timecodes


project = timecodes.__title__
copyright = timecodes.__copyright__
version = release = timecodes.__version__
language = 'English'

extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.intersphinx',
	'sphinx.ext.viewcode',
	'sphinx.ext.coverage'
]
intersphinx_mapping = {
	'python': ('http://docs.python.org/2.7', None),
}
templates_path = ['_templates']
exclude_patterns = ['_build']
html_theme_path = ['_themes']
html_static_path = ['_static']
source_suffix = '.rst'
master_doc = 'index'

add_function_parentheses = True
add_module_names = True
pygments_style = 'sphinx'

htmlhelp_basename = '{package}_docs'.format(package=timecodes.__name__)
html_title = "{project} {version} Documentation".format(project=project, version=version)
html_short_title = project
html_last_updated_fmt = ''
html_show_sphinx = False

if os.environ.get('READTHEDOCS', None) == 'True':
	html_theme = 'default'

else:
	html_theme = 'flask'
	html_theme_options = {
		'index_logo': '',
		'index_logo_height': '0px',
	}
