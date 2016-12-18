BATS - Bayesian Adaptive Trial Simulator
=========================

.. image:: https://raw.githubusercontent.com/ContaTP/BATS-Bayesian-Adaptive-Trial-Simulator/master/BATS/resources/Icon.ico  
   :align: left
   :alt:
   
Introduction
-----------

.. image:: https://badge.fury.io/py/BATS.svg
    :target: https://badge.fury.io/py/BATS
    
.. image:: https://img.shields.io/pypi/l/bats.svg
    :target: http://www.gnu.org/licenses/gpl-3.0
    
.. image:: https://img.shields.io/pypi/status/bats.svg
    :target: https://badge.fury.io/py/BATS
    
.. image:: https://img.shields.io/pypi/pyversions/bats.svg
    :target: https://badge.fury.io/py/BATS

Bayesian Adaptive Trial Simulator (BATS) is a Qt-based software used to perform simulation for Bayeisan Multi-arm Multi-stage design.

Installation
------------

+---------------------+-------------------------------------------------------------------------------------------------------+
| Downloads           |  URL                                                                                                  |
+=====================+=======================================================================================================+
| Windows Installer   | `BATS-1.0.0-win32.msi <https://sourceforge.net/projects/bats/files/BATS-1.0.0-win32.msi/download>`_   | 
+---------------------+-------------------------------------------------------------------------------------------------------+
| Source Code         | `BATS-1.0.0.tar.gz <https://sourceforge.net/projects/bats/files/BATS-1.0.0b7.tar.gz/download>`_       | 
+---------------------+-------------------------------------------------------------------------------------------------------+
``* The Windows users are encouraged to use the Windows Installer because the installation is easy.``

Users can install BATS through an installer with no dependencies (The msi installer only works in Windows now), or through PyPI, which requires Python 3.4 +, several packages and GNU Scientific Library (GSL):

.. code-block:: bash

    $ pip install BATS

**Dependencies**:

* Numpy
* Pandas
* Matplotlib
* Cython
* `cythonGSL <https://github.com/twiecki/CythonGSL>`_
* `PyQt5 <https://www.riverbankcomputing.com/software/pyqt/download5>`_

**Other dependencies**:

The module requires GNU Scientific Library (`GSL <https://www.gnu.org/software/gsl/>`_) to be installed on user's operating system, because it use the GSL module to draw random variables and calculate choose functions.

* `GSL <https://code.google.com/archive/p/oscats/downloads>`_ For Windows Port.

**Install cythonGSL**

To install cythonGSL, download the source from `Thomas Wiecki's repository <https://github.com/twiecki/CythonGSL>`_, follows the instructions for installation under the page. 

**Install Python Dependencies on Windows (Python 3.4 required)**

.. code-block:: bash

    $ pip install numpy pandas matplotlib cython PyQt5 

**Install GSL on Windows (Python 3.4 required)**

Download GSL from the link above, following the `instructions <http://joonro.github.io/blog/posts/installing-gsl-and-cythongsl-in-windows.html>`_, Cython will also require a `C/C++ compiler <https://github.com/cython/cython/wiki/CythonExtensionsOnWindows>`_ to complie the code into Python module.

**Install the Python Dependencies and GSL on Linux**:

.. code-block:: bash

    $ pip3 install numpy pandas matplotlib cython PyQt5
    
    $ apt-get install libgsl2


Usage
-----

.. code-block:: python

   import BATS
   BATS.__init__()


See `documentation <https://github.com/ContaTP/BATS-Bayesian-Adaptive-Trial-Simulator/blob/master/BATS/documentation/Documentation.pdf>`_ for detailed settings


License
-------
The software is distributed under GPLv3. See License for details

Contact: yuzhenning.bio@gmail.com
