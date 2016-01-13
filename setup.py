from setuptools import setup

from nandy.meta import version

setup(
    name="nandy",
    version=version,
    author="james absalon",
    author_email="james.absalon@rackspace.com",
    packages=['nandy'],
    package_data={'nandy': ['nandy/*']},
    long_description="Tool for retrieving resource usage information.",
    data_files=[
        ('/etc/nandy', ['nandy.yaml']),
        ('/etc/init.d', ['service/nandy'])
    ],
    scripts=['bin/nandy']
)
