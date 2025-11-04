.. # JUBE Benchmarking Environment
   # Copyright (C) 2008-2024
   # Forschungszentrum Juelich GmbH, Juelich Supercomputing Centre
   # http://www.fz-juelich.de/jsc/jube
   #
   # This program is free software: you can redistribute it and/or modify
   # it under the terms of the GNU General Public License as published by
   # the Free Software Foundation, either version 3 of the License, or
   # any later version.
   #
   # This program is distributed in the hope that it will be useful,
   # but WITHOUT ANY WARRANTY; without even the implied warranty of
   # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   # GNU General Public License for more details.
   #
   # You should have received a copy of the GNU General Public License
   # along with this program.  If not, see <http://www.gnu.org/licenses/>.

Developer documentation
=======================

.. highlight:: bash
   :linenothreshold: 5

Contributing
~~~~~~~~~~~~

We welcome contributions in the form of
`pull requests <https://github.com/FZJ-JSC/JUBE/pulls>`_. Contributions can
be anything from bug fixes to documentation to new features. Please ensure
that your contributions to JUBE comply with the
`CONTRIBUTING.md <https://github.com/FZJ-JSC/JUBE/blob/master/CONTRIBUTING.md>`_
and the following developer guidelines.

Coding standards
----------------

* *Python* code must be **pep8** conform
* check your code using **pylint**
* do not use tabs! Use four whitespaces instead
* avoid ``map``, ``filter`` or ``lambda`` commands
* use ``format`` instead of ``%``
* avoid very long methods
* use multiple files for completely different classes
* try to stay **Python3.2** conform
* ``import`` of package files should use the complete path (avoid ``from``)

* new include file features:

  * must be downward compatible
  * must be added to schema files
  * must be documented and there must be a small example
  * must be covered by tests

Pylint
------

In the top directory

  .. code-block:: sh

     pylint --rcfile devel-utils/pylint.rc jube


Flake8
------

In the top directory

  .. code-block:: sh

     flake8 --config devel-utils/flake8 jube

Another possibility is to copy or link the file to the default search
path ``~/.config/flake8`` to use it globally.


Coverage and testing
--------------------

To produce a coverage report the ``coverage`` packet must be
installed. Run

  .. code-block:: sh

     python -m coverage run ./run_all_tests.py
     python -m coverage html

in the ``test`` directory. The first command creates a coverage report
``.coverage`` in the current directory and the second one creates a
folder ``htmlcov`` with html files visualizing the code coverage by
adding colors for covered and uncovered regions of the code. The
summary can be viewed in ``index.html``.

Testing for multiprocessing parts need to be performed manually. The 
corresponding file is located in ``tests/multiprocessing_tests.py``

Make sure to add tests for your developments.


Documentation creation
----------------------

Inside the ``docs`` directory you can use::

   >>> make html        #create html docu files
   >>> make pdflatex    #create pdf  docu file
   >>> make update_help #update jube command line help

Create distribution
-------------------

Inside the main *JUBE* directory you can use::

   >>> python setup.py sdist

to update the ``tar.gz`` file inside the dist directory.

* Check version before running ``sdist``
* Store a completely new mayor version inside the tags area of the repository

Database documentation
----------------------
The database has been integrated into *JUBE* version 3.0.
This database stores the data previously stored using the ``configuration`` and
``workpackage`` XML files. As a result of this new introduction, the database
must be adapted when extending *JUBE* functionality that involves the insertion
of new tags or attributes. The following section explains the structure of
the database and the process for adding new values.

Firstly, the general database structure is created using an SQL file located
at ``jube/util/sql_create_queries.sql``. This file contains all the CREATE SQL
statements needed to create the database tables and their column values.
If new attributes or even new tags are to be added to *JUBE*'s input format,
the corresponding table must be extended by the attribute or a new table must
be created with the corresponding values.

The functions for inserting (INSERT), reading (SELECT) or other functions for modifying
the database are located in the file ``jube/util/database_interface.py``. These functions
must be passed the required table name and data to execute the corresponding SQL command
on the database. Only this file should handle direct access to the database, and if the
class is extended, further tests should be included in the corresponding testfile.
(``tests/database_interface_tests.py``)

All classes that previously stored their information in the XML files
(e.g. *Parameterset*, *Step* or *Workpackage*) contained the ``etree_repr()`` function.
This function collected all variables of the class and stored them in XML form in
the corresponding file. This function has been removed and the function
``add_information_to_database()`` has been implemented instead. This function
also collects all variables of the class and adds them to the database using the
interface. If an attribute is added, modified or removed, the corresponding variable
must be taken into account in this function. If new tags are added that are associated
with a new class, that class must also contain the ``add_information_to_database()``
function that adds the relevant variables to the database.

The call of the ``add_information_to_database()`` function is initiated by the
``add_benchmark_configuration_to_database()``, ``update_benchmark_configuration_in_database()``
and ``add_workpackage_information_to_database()`` functions of the *Benchmark* class. These
functions are called at the points where the earlier ``write_benchmark_information()`` and
``write_workpackage_information()`` functions have written the data to the XML files.

The last step is to ensure that the newly inserted value is also read from the
database if an existing run is to be processed further. The data is read from
the database in the ``jube/jubeio.py`` file using the ``_extract_<tag>_from_database()``
functions for each tag. This function should be extended or implemented to read
and analyse the new values from the database.

The following database ERM is intended to provide an overview of the database tables,
their attributes and relationships.

.. image:: database_erm.png

Lessons learned
^^^^^^^^^^^^^^^

In addition to a general explanation of how to extend or modify the database structure,
other issues that have arisen during implementation, known as 'lessons learned',
are explained here.

When inserting and especially when reading data from the database, it is important to
consider the format in which the data is required in the database and in the related class.
For example, data may be stored as a number in the database but required
as a string in the related class. In this case, care should be taken with the
conversion when inserting and reading from the database. In particular, the handling of
booleans should be mentioned here. Since SQLite has no storage type for booleans, they are
stored as integers (0 for false, 1 for true). Attention should also be paid here to correct
conversion to the required types.

Another peculiarity that can lead to errors is when reading data from the database.
When executing the SELECT command, you can also specify the column names to be output.
The return value for each database row found is a tuple containing the required column values.
For example, if 4 column names are specified in the SELECT command, you will get a tuple with
4 values for each database row. The special case is when only one column name is specified
in the SELECT command. In this case, you should also get a tuple with only one value per
database row, as only one column value was specified. The peculiarity here is that this tuple
has a second value which is empty and therefore contains an unwanted separator in the tuple
(e.g. ``[(0,), (1,)]``). If this list is to be used further, care must be taken to
ensure that no delimiters or empty values are processed.


Python package documentation
----------------------------

Here you will find the *Python* package documentation of *JUBE*: :doc:`Package doku <jube>`
