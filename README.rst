BATS
=========================
Bayesian Adaptive Trial Simulator (BATS) is a Qt-based software used to perform simulation for Bayeisan Multi-arm Multi-stage design.

Installation
------------

.. code-block:: bash

    $ pip install BATS

Dependencies:

* Numpy
* Pandas
* Matplotlib
* Cython
* `cythonGSL <https://github.com/twiecki/CythonGSL>`_
* PyQt5

Other dependencies:

The module requires GSL, `<https://www.gnu.org/software/gsl/>`_ to be installed on user's operating system, because it use the GSL module to draw random variables and calculate choose functions.

* `GSL For Windows Port: <https://code.google.com/archive/p/oscats/downloads>`_

Usage
-----

.. code-block:: python

   import BATS
   BATS.__init__()


Authors of the code: Zhenning Yu
Contact: yuzhenning.bio@gmail.com

License
-------
The software is distributed under GPLv3. See License for details