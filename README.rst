BATS - Bayesian Adaptive Trial Simulator
=========================
Bayesian Adaptive Trial Simulator (BATS) is a Qt-based software used to perform simulation for Bayeisan Multi-arm Multi-stage design.

Installation
------------

Users can install BATS through an installer (DL:, only available for Windows now, the Linux version is under development) orthrough PyPI, which requires Python 3.4 + to better support PyQt5, several packages and GNU Scientific Library (GSL):

.. code-block:: bash

    $ pip install BATS

Dependencies:

* Numpy
* Pandas
* Matplotlib
* Cython
* `cythonGSL <https://github.com/twiecki/CythonGSL>`
* `PyQt5 <https://www.riverbankcomputing.com/software/pyqt/download5>`

Other dependencies:

The module requires GNU Scientific Library (GSL, ` <https://www.gnu.org/software/gsl/>`) to be installed on user's operating system, because it use the GSL module to draw random variables and calculate choose functions.

* `GSL For Windows Port: <https://code.google.com/archive/p/oscats/downloads>`

To install cythonGSL, download the source from `Thomas Wiecki's repository <https://github.com/twiecki/CythonGSL>`, follows the instructions for installation under the page. 

To install the Python dependencies and GSL under Windows (with Python 3.4 +):
.. code-block:: bash

    $ pip install numpy pandas matplotlib cython PyQt5 

Download GSL from the link above, following the `instructions <http://joonro.github.io/blog/posts/installing-gsl-and-cythongsl-in-windows.html>`, Cython will also require a `C/C++ compiler <https://github.com/cython/cython/wiki/CythonExtensionsOnWindows>` to complie the code into Python module.

To install the Python dependencies and GSL under Linux:
.. code-block:: shell

    $ pip3 install numpy pandas matplotlib cython PyQt5
    
    $ apt-get install libgsl2


Usage
-----

.. code-block:: python

   import BATS
   BATS.__init__()


Authors of the code: Zhenning Yu

Contact:yuzhenning.bio@gmail.com

License
-------
The software is distributed under GPLv3. See License for details
