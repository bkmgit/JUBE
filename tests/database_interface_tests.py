#!/usr/bin/env python3
# JUBE Benchmarking Environment
# Copyright (C) 2008-2022
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
"""Database Interface related tests"""

import unittest
import os
import jube.util.database_interface


class TestDatabaseInterface(unittest.TestCase):
    """Class for testing the database interface"""

    def setUp(self):
        """Create and connect to database"""
        self.db = jube.util.database_interface.Database_Interface()
        self.db.connect()
        self.db.create_database()

    def test_database_commands(self):
        """Test database commands"""
        # Test INSERT
        check_content = [("BeispielName", "BeispielKommentar")]
        self.db.insert("Benchmark", {"name": "BeispielName",
                                     "comment": "BeispielKommentar",
                                     "outpath": "/path",
                                     "file_path_ref": "/path",
                                     "version": "1"})
        actual_content = self.db.select("Benchmark", ["name", "comment"])
        self.assertEqual(actual_content, check_content, "")

        # Test UPDATE
        check_content = [("BeispielName2", "BeispielKommentar")]
        self.db.update("Benchmark", {"name": "BeispielName2"}, {"name": "BeispielName"})
        actual_content = self.db.select("Benchmark", ["name", "comment"])
        self.assertEqual(actual_content, check_content, "")

        # Test DELETE
        check_content = []
        self.db.delete("Benchmark", {"name": "BeispielName2"})
        actual_content = self.db.select("Benchmark", ["name", "comment"])
        self.assertEqual(actual_content, check_content, "")

    def tearDown(self):
        """Disconnect and remove database"""
        self.db.disconnect()
        os.remove("database.db")

if __name__ == "__main__":
    unittest.main()
