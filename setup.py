from setuptools import setup


setup(
    name='tatoolkit',
    version='0.1',
    packages=['tatoolkit'],
    scripts=['bin/split_assgn'],
    url='',
    license='',
    author='Dan Zou',
    author_email='danzou12@umd.edu',
    description='Tools for TA\'ing with UMD services',
    install_requires=[
        'mossum @ git+https://github.com/danzou56/mossum.git#mossum'
    ]
)
