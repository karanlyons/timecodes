# -*- coding: utf-8 -*-

import timecodes


try:
	from setuptools import setup

except ImportError:
	from distutils.core import setup


setup(
	name="timecodes",
	version=timecodes.__version__,
	description="Automatically save only changed model data.",
	long_description="\n\n".join([open('README.rst', 'rU').read(), open('HISTORY.rst', 'rU').read()]),
	author=timecodes.__author__,
	author_email=timecodes.__contact__,
	url=timecodes.__homepage__,
	license=open('LICENSE', 'rU').read(),
	packages=['timecodes'],
	package_dir={'timecodes': 'timecodes'},
	package_data={'': ['README.rst', 'HISTORY.rst', 'LICENSE']},
	include_package_data=True,
	install_requires=[],
	zip_safe=False,
	classifiers=(
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: Apache Software License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.1',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
	),
	test_suite='test_timecodes',
)
