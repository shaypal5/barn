barn |barn_icon|
################
|PyPI-Status| |PyPI-Versions| |Build-Status| |Codecov| |LICENCE|

.. |barn_icon| image:: https://github.com/shaypal5/barn/blob/6f814eb9b6721e70c657e28e1ca43576ff6c2704/barn.png

Simple local/remote dataset store for Python.

.. code-block:: python

  from barn import Dataset
  twitter_usa = Dataset(name='twitter_usa', task='NER')
  # download from an azure block blob storage and load into a dataframe
  twitter_usa.download(tags=['preprocessed'], version='20180305')
  df = twitter_usa.df(tags=['preprocessed'], version='20180305')

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
