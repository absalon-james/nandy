from setuptools import setup

from nandy.meta import version

setup(
    name="nandy",
    version="version",
    author="james absalon",
    author_email="james.absalon@rackspace.com",
    packages=['nandy'],
    package_data={'nandy': ['nandy/*']},
    long_description="Tool for retrieving resource usage information.",
    data_files=[('/etc/nandy', ['nandy.yaml'])],
    scripts=['bin/nandy'],
    install_requires=[
        'python-novaclient',
        'python-keystoneclient',
        'sqlalchemy==1.0.11',
        'MySQL-python'
    ]
)
