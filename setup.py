#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.1.0'

setup(
    name='labAdmin',
    version=version,
    description="""A django app to manage your Fablab""",
    author='Fablab Torino',
    author_email='info@fablabtorino.org',
    url='https://github.com/FablabTorino/LabAdmin',
    packages=[
        'labAdmin',
    ],
    include_package_data=True,
    install_requires=[
       'django<1.11,>=1.8',
       'djangorestframework>3,<4',
       'django-cors-middleware==1.3.1',
       'django-oauth-toolkit==0.10.0',
       'paho-mqtt>1,<2',
    ],
    zip_safe=False,
    keywords='Fablab, lab, admin',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
