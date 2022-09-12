'''Script for setup'''
import json
from setuptools import setup, find_namespace_packages

with open('azuredriver/pkg_info.json', encoding="utf-8") as fp:
    _pkg_info = json.load(fp)

with open("DESCRIPTION.md", "r",encoding="utf-8") as description_file:
    long_description = description_file.read()

setup(
    name='azuredriver',
    version=_pkg_info['version'],
    description='None',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=['azuredriver*']),
    include_package_data=True,
    install_requires=[
        'werkzeug==2.0.3',
        'ignition-framework=={0}'.format(_pkg_info['ignition-version']),
        'uwsgi>=2.0.18,<3.0',
        'gunicorn>=19.9.0,<20.0',
        'azure-mgmt-resource==19.0.0',
        'azure-mgmt-network==19.3.0',
        'azure-identity>=1.5.0',
        'azure-mgmt-compute~=23.0.0',
        'azure-core==1.19.1',
        'msrestazure==0.6.4',
        'jsonschema==3.2.0',
    ],
    entry_points='''
        [console_scripts]
        azuredriver-dev=azuredriver.__main__:main
    ''',
    scripts=['azuredriver/bin/azuredriver-uwsgi', 'azuredriver/bin/azuredriver-gunicorn', 'azuredriver/bin/azuredriver']
)
