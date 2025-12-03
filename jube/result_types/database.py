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
"""Databasetype definition"""

import os

from jube.result_types.keyvaluesresult import KeyValuesResult
from jube.result import Result
import jube.log
import jube.util.database_interface

LOGGER = jube.log.get_logger(__name__)


class Database(KeyValuesResult):

    """A database result"""

    class DatabaseData(KeyValuesResult.KeyValuesData):

        """Database data"""

        def __init__(self, name_or_other, primekeys, db_file):
            if type(name_or_other) is KeyValuesResult.KeyValuesData:
                self._name = name_or_other.name
                self._keys = name_or_other.keys
                self._data = name_or_other.data
                self._benchmark_ids = name_or_other.benchmark_ids
            else:
                KeyValuesResult.KeyValuesData.__init__(self, name_or_other)
            self._primekeys = primekeys
            self._db_file = None if db_file == "None" else db_file

        def create_result(self, show=True, filename=None, **kwargs):
            # Place for the magic #
            # show = If False do not show something on screen (result
            # only into file)
            # filename = name of standard output/database file
            # All keys: print([key.name for key in self._keys])
            #col_names = [key.name for key in self._keys]
            # All data: print(self.data)
            keys = [k.resulting_name for k in self.keys]

            # check if all primekeys are in keys
            if not set(self._primekeys).issubset(set(keys)):
                raise ValueError("primekeys are not included in <key>!")

            # define database file
            if self._db_file is not None and filename is not None:
                file_handle = open(filename, "w")
                file_handle.write(self._db_file)
                file_handle.close()
                # create directory path to db file, if it does not exist
                file_path_ind = self._db_file.rfind('/')
                if file_path_ind != -1:
                    # modify when Python2.7 support is dropped (potential race condition)
                    if not os.path.exists(os.path.expanduser(self._db_file[:file_path_ind])):
                        os.makedirs(os.path.expanduser(
                            self._db_file[:file_path_ind]))
                db_file = os.path.expanduser(self._db_file)
            elif filename is not None:
                db_file = filename
            else:
                return None

            # create database and insert the data
            db = jube.util.database_interface.Database_Interface(
                os.path.join(db_file))
            db.connect()

            try:
                db.start_transaction()
                # create a dictionary of keys and their data type to create the database table
                key_dtypes = {keys[i]: type(self.data[0][i]).__name__.replace(
                              'str', 'text') for i in range(len(self.keys))}

                # Add key with primekey=true to primekeys and use set to remove duplicates
                self._primekeys = list(set(self._primekeys + [k.resulting_name for k in self._keys if k.primekey]))

                if len(self._primekeys) > 0:
                    LOGGER.warning("The `primekeys` attribute of the `<database>`-tag is deprecated. "
                                   "Instead, use the new `primekey` attribute of the `<key>`-tag. "
                                   "(<key primekey=\"true\"|\"false\">..</key>)")

                # create new table with a name of stored in variable self.name if it does not exists
                db.create_database_table(self.name, key_dtypes, self._primekeys)

                # check for primary keys in database table
                db_pragma = db.pragma("table_info", self.name)
                db_primary_keys = [i[1] for i in db_pragma if i[5] != 0]
                if not set(self._primekeys) == set(db_primary_keys):
                    raise ValueError("Modification of primary values is not "
                                     "supported. Primary keys of table {} are "
                                     "{}".format(self.name, db_primary_keys))

                # compare self._keys with columns in db and add new column in the database if it does not exist
                db_col_names = [i[1] for i in db_pragma]

                # delete columns, which were removed as keys in this execution
                diff_col_list = list(set(db_col_names).difference(keys))
                if len(diff_col_list) != 0:
                    db.alter_table("DROP", self.name, diff_col_list)

                # add columns, which were added as keys in this execution
                diff_col_list = list(set(keys).difference(db_col_names))
                if len(diff_col_list) != 0:
                    db.alter_table("ADD", self.name, diff_col_list)

                # insert or replace self.data in database
                for value in self.data:
                    data = {keys[i]: value[i] for i in range(len(keys))}
                    db.insert(self.name, data, "REPLACE")

                db.commit_transaction()

                # Print database location to screen and result.log
                LOGGER.info("Database location of id {}: {}".format(
                    self._benchmark_ids[0], db_file))
            except Exception as e:
                db.rollback_transaction()
                db.disconnect()
                raise e
            db.disconnect()

    class Column(KeyValuesResult.DataKey):

        """Class represents one database column"""

        def __init__(self, name, title=None, format_string=None, primekey=False):
            KeyValuesResult.DataKey.__init__(self, name, title, format_string,
                                             None)
            self._primekey = primekey

        @property
        def primekey(self):
            """Column width"""
            return self._primekey

    def __init__(self, name, res_filter=None, primekeys=None, db_file=None):
        KeyValuesResult.__init__(self, name, None, res_filter)
        self._primekeys = primekeys
        self._db_file = db_file

    @property
    def file(self):
        """Return the database file"""
        return self._db_file

    @property
    def primekeys(self):
        """Return the database primekeys"""
        return self._primekeys

    def add_key(self, name, format_string=None, title=None, primekey=False):
        """Add an additional key to the dataset"""
        self._keys.append(Database.Column(name, title, format_string,
                                                  primekey))

    def create_result_data(self, style=None, select=None, exclude=None):
        """Create result data"""
        result_data = KeyValuesResult.create_result_data(self, select, exclude,
                                                         preserve_datatype=True)
        return Database.DatabaseData(result_data, self._primekeys, self._db_file)

    def add_information_to_database(self, db, benchmark_id, update=False):
        """Store database information in database"""
        try:
            db.start_transaction()
            result_id = Result.add_information_to_database(self, db, benchmark_id, update)
            database_data = {
                "database_name": self._name,
                "file": str(self._db_file),
                "result_id": result_id
            }
            if self._db_file is not None:
                database_data["file"] = self._db_file
            if self._res_filter is not None:
                database_data["filter"] = self._res_filter
            db.insert("ResultDatabase", database_data)
            for key in self._keys:
                key_data = key.get_information_for_database()
                if key_data["name"] in self._primekeys or key.primekey:
                    key_data["is_primary"] = 1
                key_data["databasekey_name"] = key_data.pop("name")
                key_data["database_name"] = self._name
                db.insert("ResultDatabaseKey", key_data)
            db.commit_transaction()
        except Exception as e:
            LOGGER.warning(str(e))
            db.rollback_transaction()
            db.disconnect()
            raise e
