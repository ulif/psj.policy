from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n\n'
    + read('docs', 'HISTORY.txt')
    + '\n\n'
    + 'Download\n'
    + '********\n'
    )

setup(
    name='psj.policy',
    version='0.1.1dev',
    author='Uli Fouquet',
    author_email='uli@gnufix.de',
    url = 'https://svn.gnufix.de/repos/psj.policy',
    description='Plone Scientific Jounal - the site policy',
    long_description=long_description,
    license='GPL',
    keywords="zope policy journal plone plone3",
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Gnu Public License',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 'Framework :: Plone',
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['psj'],
    include_package_data = True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'ulif.plone.testsetup',
        # -*- Extra requirements: -*-
        'lxml',
        ],
    entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      ooo_convert = psj.policy.bin.ooo_convert:main
      """,
)
