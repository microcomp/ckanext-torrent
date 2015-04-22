from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-torrent',
    version=version,
    description="CKAN extension",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Dominik Kapisinsky',
    author_email='kapisinsky@microcomp.sk',
    url='http://github.com/microcomp',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.torrent'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'celery'
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        torrent = ckanext.torrent.plugin:TorrentPlugin  
        [paste.paster_command]
        torrent-cmd = ckanext.torrent.torrent_cmd:TorrentCmd
        [ckan.celery_task]
        tasks = ckanext.torrent.celery_import:task_imports
    ''',
)
