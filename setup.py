#!/usr/bin/env python

from setuptools import setup, find_packages

import aospy.ibaprobelib


setup(
    name='apstra-aospy-ibaprobelib',
    packages=find_packages(),
    version=aospy.ibaprobelib.__version__,
    description="AOS IBA probe library",
    author='support@apstra.com',
    license='Apstra Community',
    # keywords=('serialization', 'rest', 'json', 'api', 'marshal',
    #           'marshalling', 'deserialization', 'validation', 'schema',
    #           'jsonschema', 'swagger', 'openapi', 'networking', 'automation'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ]
)
