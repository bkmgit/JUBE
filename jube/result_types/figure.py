# JUBE Benchmarking Environment
# Copyright (C) 2008-2023
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
"""Figuretype definition"""

from __future__ import (print_function,
                        unicode_literals,
                        division)
import sqlite3
import ast
import os

from jube.result_types.genericresult import GenericResult
from jube.result import Result
import xml.etree.ElementTree as ET
import jube.log
import matplotlib.pyplot as plt

LOGGER = jube.log.get_logger(__name__)


class Figure(GenericResult):

    """A Figure result"""

    class FigureData(GenericResult.KeyValuesData):

        """Figure data"""

        def __init__(self, name_or_other, plots, title):
            if type(name_or_other) is GenericResult.KeyValuesData:
                self._name = name_or_other.name
                #self._keys = name_or_other.keys
                self._data = name_or_other.data
                self._benchmark_ids = name_or_other.benchmark_ids
            else:
                GenericResult.KeyValuesData.__init__(self, name_or_other)
            self._plots = plots
            self._title = title

        def create_result(self, show=True, filename=None, **kwargs):
            """Place for the magic: generate the figures"""

            table_data = {v.name:k for v,k in self._data.items()}

            fig, ax = plt.subplots()
            ax.set_title(self._title)
            for plot in self._plots:
                for y in plot.y:
                    if plot.type == "line":
                        ax.plot(table_data[plot.x], table_data[y])
                    elif plot.type == "scatter":
                        ax.scatter(table_data[plot.x], table_data[y])
            plt.show()
            fig.savefig(filename[:-4]) # without .dat extension
            # Print Figure location to screen and result.log
            LOGGER.info("Figure location of id {}: {}".format(
                self._benchmark_ids[0], filename[:-4]))

    class Plot(GenericResult.DataKey):
        """A Plot type"""

        def __init__(self, type, x=None, y=None, name=None, title=None, unit=None):
            GenericResult.DataKey.__init__(self, name, title, unit)
            self._type = type
            self._x = x
            if y is None:
                self._y = [] 
            elif isinstance(y, list):
                self._y = y
            else:
                raise TypeError("Plot.y has to be a list or None!")
        
        @property
        def type(self):
            """Get 'type'"""
            return self._type

        @property
        def x(self):
            """Get 'x'"""
            return self._x
        
        @x.setter
        def x(self, x):
            """Set 'x'"""
            self._x = x

        @property
        def y(self):
            """Get 'y'"""
            return self._y
        
        @property
        def keys(self):
            """Get 'type'"""
            return [self._x] + self._y
        
        def __str__(self):
            return f"IN PLOT: type: {self._type}; x: {self._x}; y: {self._y}"
        
        def etree_repr(self):
            """Return etree object representation"""
            plot_etree = GenericResult.DataKey.etree_repr(self)
            plot_etree.tag = "plot"
            if self._type is not None:
                plot_etree.attrib["type"] = str(self._type)

            x_elem = ET.SubElement(plot_etree, 'x')
            x_elem.text = self._x
            for y in self._y:
                y_elem = ET.SubElement(plot_etree, 'y')
                y_elem.text = y
            return plot_etree

    def __init__(self, savefig, title=None, res_filter=None):
        GenericResult.__init__(self, savefig, res_filter)
        # HINT: self._name = savefig
        self._title = title
        self._plots = list()

    def add_key(self, name, title=None, unit=None):
        """Add an additional key to the dataset if it is not alread in the set"""
        if name not in [key.name for key in self._keys]:
            self._keys.append(GenericResult.DataKey(name, title, unit))

    def add_plot(self, type, x, y):
        """Add an additional plot to the dataset"""
        self._plots.append(Figure.Plot(type, x, y))

    def create_result_data(self, style=None, select=None, exclude=None):
        """Create result data"""
        result_data = GenericResult.create_result_data(self, select, exclude)
        return Figure.FigureData(result_data, self._plots, self._title)

    def etree_repr(self):
        """Return etree object representation"""
        result_etree = Result.etree_repr(self)
        figure_etree = ET.SubElement(result_etree, "Figure")
        if self._name not in [None, ""]:
            figure_etree.attrib["title"] = self._name
        if self._res_filter not in [None, ""]:
            figure_etree.attrib["filter"] = self._res_filter
        for plot in self._plots:
            figure_etree.append(plot.etree_repr())
        return result_etree
