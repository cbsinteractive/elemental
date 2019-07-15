import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='elemental',
    version='0.1',
    url='https://github.com/cbsinteractive/elemental.git',
    license='unlicense',
    long_description=open('README.md').read(),
    install_requires=requirements,
    packages=setuptools.find_packages(),
)
