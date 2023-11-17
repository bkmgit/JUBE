# JUBE Benchmarking Environment
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
"""Database Interface"""

from __future__ import (print_function,
                        unicode_literals,
                        division)

import jube.log
import os
import sqlite3

LOGGER = jube.log.get_logger(__name__)


class Database_Interface(object):

    """Interface to run all database options"""

    def __init__(self, name='database.db'):
        self._name = name

    def connect(self):
        self._connection = sqlite3.connect(self._name)
        self._connection.isolation_level = None
        self._cursor = self._connection.cursor()

    def disconnect(self):
        self._connection.close()

    def create_database(self):
        path = os.path.join(jube.util.__path__[0], "sql_create_queries.sql")
        with open(path, 'r') as sql_file:
            sql_queries = sql_file.read()

        try:
            self._cursor.executescript(sql_queries)
        except sqlite3.Error as er:
            raise RuntimeError("Something went wrong when creating the "
                               "database: {0}".format(er))

    def insert(self, table_name, data):
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({', '.join(['?'] * len(data))})"

        self._cursor.execute(query, values)

        return self._cursor.lastrowid

    def select(self, table_name, columns=None, condition=None):
        if columns is None:
            columns = "*"
        else:
            columns = ", ".join(columns)

        query = f"SELECT {columns} FROM {table_name}"

        if condition:
            query += f" WHERE {condition}"

        self._cursor.execute(query)
        rows = self._cursor.fetchall()

        return rows

    def update(self, table_name, data, condition):
        columns = ", ".join(f"{column} = ?" for column in data.keys())
        values = tuple(data.values())

        query = f"UPDATE {table_name} SET {columns} WHERE {condition}"

        self._cursor.execute(query, values)

    def delete(self, table_name, condition):
        query = f"DELETE FROM {table_name}"
        if condition is not None:
            query +=  f" WHERE {condition}"

        self._cursor.execute(query)

    def start_transaction(self):
        self._connection.execute('BEGIN')

    def commit_transaction(self):
        self._connection.commit()

    def rollback_transaction(self):
        self._connection.rollback()
