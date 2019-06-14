from distutils.core import setup
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='elemental',
    version='0.1',
    url='https://github.com/cbsinteractive/elemental.git',
    license='unlicense',
    long_description=open('README.md').read(),
    install_requires=requirements,
)
