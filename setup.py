from setuptools import setup, find_packages, Extension
from os import path
import numpy
import cython_gsl

try:

    import cython
    USE_CYTHON = True

except:

    USE_CYTHON = False

# Based on if there is cython
ext_c = '.pyx' if USE_CYTHON else '.c'

extensions = [
    Extension(
        "BATS.{}".format(filename),
        ["BATS/{}{}".format(filename, ext_c)] , libraries=cython_gsl.get_libraries(), library_dirs=[cython_gsl.get_library_dir()],
        include_dirs=[cython_gsl.get_cython_include_dir(), numpy.get_include()]) for filename in "AllocFinder CalPosteriorProbability CriticalValueCal FixedTrial FixedTrialData GammaGenerate InterimAnalysis PredictiveProbability".split()
]


if USE_CYTHON:

    from Cython.Build import cythonize
    from Cython.Distutils import build_ext
    extensions = cythonize(extensions, compiler_directives={
            'boundscheck': False,
            'wraparound': False,
            'nonecheck':False,
            'embedsignature': True,
            'cdivision': True,
    })


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    
    include_dirs=[numpy.get_include(), cython_gsl.get_include()],
    cmdclass = {'build_ext': build_ext},
    name='BATS',
    version='1.1.0a4',
    description='https://github.com/ContaTP/BATS-Bayesian-Adaptive-Trial-Simulator',
    long_description=long_description,
    url='https://github.com/ContaTP/BATS-Bayesian-Adaptive-Trial-Simulator',
    author='Zhenning Yu',
    author_email='yuzhenning.bio@gmail.com',
    zip_safe = False,
    license='GPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Cython',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='Bayesian, clinical trial, adaptive trial',
    packages=find_packages(),
    package_data={'BATS': ['*.pyx', '*.pxd',  '*.c', './documentation/*.pdf',  './resources/font/*', './resources/*.png', './resources/*.ico',  './resources/runmenu.gif' , '../README.rst']},
    install_requires=[
        'cython >= 0.24',
        'numpy',
        'matplotlib',
        'pandas',
        'cythonGSL'
    ],
    ext_modules = extensions,
)
