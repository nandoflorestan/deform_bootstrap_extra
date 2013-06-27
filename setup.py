#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
# http://peak.telecommunity.com/DevCenter/setuptools#developer-s-guide

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

try:
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except IOError:
    CHANGES = ''

requires = ['nine', 'bag>=0.3.4', 'deform_bootstrap==0.2.8', 'pyramid_deform']

setup(name='deform_bootstrap_extra',
    version='0.2.8',
    description="A complement to deform_bootstrap, which offers "
    "Twitter Bootstrap compatible widgets, templates and styles "
    "for the deform form library.",
    long_description='\n\n'.join([README, CHANGES]),
    author='Nando Florestan',
    author_email='nandoflorestan@gmail.com',
    url='https://github.com/nandoflorestan/deform_bootstrap_extra',
    keywords='twitter bootstrap deform styles css web forms form',
    classifiers=[  # http://pypi.python.org/pypi?:action=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: BSD License',
        "Environment :: Web Environment",
        "Framework :: Pyramid",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="deform_bootstrap_extra.jests",
)
