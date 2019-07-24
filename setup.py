import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='python-elemental',
    author='CBS Interactive',
    author_email='video-processing-team@cbsinteractive.com',
    version='0.3',
    include_patckage_data=True,
    url='https://github.com/cbsinteractive/elemental.git',
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=requirements,
    packages=setuptools.find_packages(),
    package_data={'elemental': ['templates/*']}
)
