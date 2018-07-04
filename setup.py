#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

version = '0.0.1'

with open('README.rst', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='promesque',
    version=version,
    description='Configurable Prometheus exporter for results of Elasticsearch queries',
    long_description=long_description,
    keywords=['prometheus', 'prometheus-exporter', 'elasticsearch'],
    author='Carsten Rösnick-Neugebauer',
    author_email='croesnick@gmail.com',
    url='https://github.com/croesnick/promesque',
    download_url='https://github.com/croesnick/promesque/archive/v{}.tar.gz'.format(version),
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
    ],
    install_requires=[
        'PyYAML~=3.12',
        'click~=6.7',
        'ruamel.yaml~=0.15',
        'prometheus_client~=0.2',
        'requests~=2.19',
        'jsonpath-ng~=1.4',
    ],
    python_requires='~=3.6',
    packages=find_packages(exclude=['test']),
    entry_points={
        'console_scripts': [
            'promesque=promesque.cli:cli',
        ]
    },
)
