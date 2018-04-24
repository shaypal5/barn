barn
####
.. .. |PyPI-Status| |PyPI-Versions| |Build-Status| |Codecov| |LICENCE|

Simple Python-based local/remote dataset store.

.. |barn_icon| image:: https://github.com/shaypal5/barn/blob/cc5595bbb78f784a3174a07157083f755fc93172/barn.png
   :height: 87
   :width: 40 px
   :scale: 50 %
   
.. .. image:: https://github.com/shaypal5/barn/blob/b10a19a28cb1fc41d0c596df5bcd8390e7c22ee7/barn.png

.. code-block:: python

  from barn import Dataset

.. contents::

.. section-numbering::


Installation
============

.. code-block:: bash

  pip install barn


Features
========

* Pure python.
* Supports Python 3.5+.


Use
===

TBA


Contributing
============

Package author and current maintainer is Shay Palachy (shay.palachy@gmail.com); You are more than welcome to approach him for help. Contributions are very welcomed.

Installing for development
----------------------------

Clone:

.. code-block:: bash

  git clone git@github.com:shaypal5/barn.git


Install in development mode, including test dependencies:

.. code-block:: bash

  cd barn
  pip install -e '.[test]'


Running the tests
-----------------

To run the tests use:

.. code-block:: bash

  cd barn
  pytest


Adding documentation
--------------------

The project is documented using the `numpy docstring conventions`_, which were chosen as they are perhaps the most widely-spread conventions that are both supported by common tools such as Sphinx and result in human-readable docstrings. When documenting code you add to this project, follow `these conventions`_.

.. _`numpy docstring conventions`: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt
.. _`these conventions`: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

Additionally, if you update this ``README.rst`` file,  use ``python setup.py checkdocs`` to validate it compiles.


Credits
=======

Created by `Shay Palachy <http://www.shaypalachy.com/>`_ (shay.palachy@gmail.com).


.. |PyPI-Status| image:: https://img.shields.io/pypi/v/barn.svg
  :target: https://pypi.python.org/pypi/barn

.. |PyPI-Versions| image:: https://img.shields.io/pypi/pyversions/barn.svg
   :target: https://pypi.python.org/pypi/barn

.. |Build-Status| image:: https://travis-ci.org/shaypal5/barn.svg?branch=master
  :target: https://travis-ci.org/shaypal5/barn

.. |LICENCE| image:: https://img.shields.io/github/license/shaypal5/barn.svg
  :target: https://github.com/shaypal5/barn/blob/master/LICENSE

.. |Codecov| image:: https://codecov.io/github/shaypal5/barn/coverage.svg?branch=master
   :target: https://codecov.io/github/shaypal5/barn?branch=master
