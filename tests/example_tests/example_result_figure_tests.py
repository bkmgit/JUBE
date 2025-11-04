#!/usr/bin/env python3
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
"""Test the result figure example"""

import unittest
import sqlite3
import os
from examples_tests import TestCase

class TestResultFigureExample(TestCase.TestExample):

    """Class for testing the result_database example"""

    @classmethod
    def setUpClass(cls):
        '''
        Automatically called method before tests in the class are run.

        Create the necessary variables and paths for the specific example
        '''
        cls._name = "result_figure"
        cls._stdout = ["x: 0; x2: 10; y: 1; y2: 5; y3: 12", "x: 1; x2: 11; y: 2; y2: 5; y3: 10", "x: 2; x2: 12; y: 4; y2: 5; y3: 8"]
        cls._stdout = [cls._stdout, cls._stdout]
        super(TestResultFigureExample, cls).setUpClass()
        super(TestResultFigureExample, cls)._execute_commands(["-r"])

    def test_for_equal_result_data(self):
        '''
        Overwrites the original test (TestExample.test_for_equal_result_data())
        for the result output to allow an example specific test.
        '''
        fig_names = ["../../../../first_fig.png", "result/2_fig.png"]
        for run_path, command_wps in self._wp_paths.items():
            for fig_name in fig_names:
                # Test if result figure exists
                fig_path = os.path.join(run_path, fig_name)
                self.assertTrue(os.path.isfile(fig_path), "Error: Figure in path {0} "
                               "does not exist".format(fig_path))

if __name__ == "__main__":
    unittest.main()
