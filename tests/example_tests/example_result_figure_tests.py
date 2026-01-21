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
import os
from examples_tests import TestCase

class TestResultFigureExample(TestCase.TestExample):

    """Class for testing the result_database example"""

    @classmethod
    def setUpClass(cls):
        """
        Automatically called method before tests in the class are run.

        Create the necessary variables and paths for the specific example
        """
        cls._name = "result_figure"
        cls._stdout = ["x2: 0; y2: 10","x2: 2; y2: 11","x2: 4; y2: 8","x2: 6; y2: 9",
                       "type: Typ1 ; x: 0; y: 11","type: Typ1 ; x: 1; y: 12","type: Typ1 ; x: 2; y: 11","type: Typ1 ; x: 3; y: 13","type: Typ2 ; x: 0; y: 19","type: Typ2 ; x: 1; y: 18","type: Typ2 ; x: 2; y: 19","type: Typ2 ; x: 3; y: 22","type: Typ3 ; x: 0; y: 40","type: Typ3 ; x: 1; y: 20","type: Typ3 ; x: 2; y: 35","type: Typ3 ; x: 3; y: 25"]
        cls._stdout = [cls._stdout, cls._stdout]
        super(TestResultFigureExample, cls).setUpClass()
        super(TestResultFigureExample, cls)._execute_commands(["-r"])

    def test_for_equal_result_data(self):
        """
        Overwrites the original test (TestExample.test_for_equal_result_data())
        for the result output to allow an example specific test.
        """
        for run_path, command_wps in self._wp_paths.items():
            fig_paths = [os.path.join(os.getcwd(), "group_fig.png"), os.path.join(run_path, "result/fig.png")]
            for fig_path in fig_paths:
                # Test if result figure exists
                self.assertTrue(os.path.isfile(fig_path), "Error: Figure in path {0} "
                               "does not exist".format(fig_path))

    @classmethod
    def tearDownClass(cls):
        """
        Automatically called method after all tests in the class have run.

        Deletes the group_fig.png
        """
        fig_path = os.path.abspath(os.path.join(os.getcwd(), "group_fig.png"))
        os.remove(fig_path)

if __name__ == "__main__":
    unittest.main()
