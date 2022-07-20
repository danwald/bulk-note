#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'requests==2.26.0' ]

test_requirements = ['pytest>=3', ]

setup(
    author="danny crasto",
    author_email='danwald79@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="send bulk messages via api",
    entry_points={
        'console_scripts': [
            'bulk_note=bulk_note.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='bulk_note',
    name='bulk_note',
    packages=find_packages(include=['bulk_note', 'bulk_note.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/danwald/bulk_note',
    version='0.1.0',
    zip_safe=False,
)
