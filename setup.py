# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TDoTP.
#
# TDotDat is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""Gyrokinetic EM turbulence database"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('tdotdat', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='tdotdat',
    version=version,
    description=__doc__,
    long_description=readme,
    keywords='tdotdat Invenio',
    license='MIT',
    author='TDoTP',
    author_email='peter.hill@york.ac.uk',
    url='https://github.com/PlasmaFAIR/tdotdat',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'tdotdat = invenio_app.cli:cli',
        ],
        'invenio_base.apps': [
            'tdotdat_records = tdotdat.records:TDotDat',
        ],
        'invenio_base.blueprints': [
            'tdotdat = tdotdat.theme.views:blueprint',
            'tdotdat_records = tdotdat.records.views:blueprint',
        ],
        'invenio_assets.webpack': [
            'tdotdat_theme = tdotdat.theme.webpack:theme',
            'tdotdat_search_app = tdotdat.records.webpack:search_app',
        ],
        'invenio_config.module': [
            'tdotdat = tdotdat.config',
        ],
        'invenio_i18n.translations': [
            'messages = tdotdat',
        ],
        'invenio_base.api_apps': [
            'tdotdat = tdotdat.records:TDotDat',
         ],
        'invenio_jsonschemas.schemas': [
            'tdotdat = tdotdat.records.jsonschemas'
        ],
        'invenio_search.mappings': [
            'records = tdotdat.records.mappings'
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
    ],
)
