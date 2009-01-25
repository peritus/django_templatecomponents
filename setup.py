#!/usr/bin/env python
from setuptools import setup, find_packages

version = '0.03'

setup(
    name='django-templatecomponents',
    version=version,
    description="django-templatecomponents",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
    keywords='templates,django',
    author='Filip Noetzel',
    url='http://j03.de/projects/django-templatecomponents/',
    license='Beerware',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
