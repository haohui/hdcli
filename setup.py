from distutils.core import setup

setup(
    name='hdcli',
    version='0.1.0',
    author='Haohui Mai',
    author_email='wheat9@apache.org',
    packages=['hdcli'],
    scripts=['bin/hdcli'],
    url='http://github.com/haohui/hdcli',
    license='LICENSE',
    description='A bunch of scripts that help commiting and resolving Hadoop JIRAs.',
    long_description=open('README.txt').read(),
    install_requires=[
        "quik >= 0.2.2",
        "requests >= 2.2.1",
        "PyYAML >= 3.1.0"
    ],
)
