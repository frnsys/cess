from setuptools import setup, find_packages

setup(
    name='cess',
    version='0.0.1',
    description='a distributed agent-based modeling framework',
    url='https://github.com/frnsys/cess',
    author='Francis Tseng (@frnsys)',
    author_email='f@frnsys.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'click',
        'dill'
    ],
    entry_points='''
        [console_scripts]
        cess=cess.cli:cli
    '''
)