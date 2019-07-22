import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='python-elemental',
    author='cbsinteractive.com',
    author_email='tianchenmin@gmail.com',
    version='0.1',
    include_patckage_data=True,
    url='https://github.com/cbsinteractive/elemental.git',
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=requirements,
    packages=setuptools.find_packages(),
)
