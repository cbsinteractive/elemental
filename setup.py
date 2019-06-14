from distutils.core import setup
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='elemental',
    version='0.1dev',
    packages=['elemental',],
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=requirements,
)