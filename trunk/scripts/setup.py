from setuptools import setup, find_packages

setup(
    name='psjscripts',
    install_requires=[],
    py_modules = ['oooctl','prepare',],
    entry_points="""
    [console_scripts]
    oooctl = oooctl:main
    oooprepare = prepare:prepare
    ooorestore = prepare:restore
    
    """
    )
