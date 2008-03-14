from setuptools import setup, find_packages

setup(
    name='psjscripts',
    install_requires=[],
    py_modules = ['oooctl',],
    entry_points="""
    [console_scripts]
    oooctl = oooctl:main
    """
    )
