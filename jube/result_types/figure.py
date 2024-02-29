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
import os
from pathlib import Path

from jube.result_types.genericresult import GenericResult
from jube.result import Result
import xml.etree.ElementTree as ET
import jube.log

LOGGER = jube.log.get_logger(__name__)


class Figure(GenericResult):

    """A Figure result"""

    class FigureData(GenericResult.KeyValuesData):

        """Figure data"""

        def __init__(self, name_or_other, plots, savefig, title, showfig):
            if type(name_or_other) is GenericResult.KeyValuesData:
                self._name = name_or_other.name
                #self._keys = name_or_other.keys
                self._data = name_or_other.data
                self._benchmark_ids = name_or_other.benchmark_ids
            else:
                GenericResult.KeyValuesData.__init__(self, name_or_other)
            self._plots = plots
            self._savefig = savefig
            self._title = title
            self._showfig = showfig

        def create_result(self, show=True, filename=None, **kwargs):
            """Place for the magic: generate the figures"""

            import matplotlib.pyplot as plt

            table_data = {v.name:k for v,k in self._data.items()}

            fig, ax = plt.subplots()
            fig.suptitle(self._title)
            for plot in self._plots:
                ax.set_xlabel(plot._xlabel)
                ax.set_ylabel(plot._ylabel)
                for data in plot.plot_data:
                    if data.type == "line":
                        ax.plot(table_data[data.x], table_data[data.y],
                                label=data.label)
                    else:
                        # dynamically create plot function call (e.g. ax.scatter())
                        plot_func = getattr(ax, data.type)
                        plot_func(table_data[data.x], table_data[data.y],
                                  label=data.label)

                if plot._legend == "True":
                    ax.legend()

            # save figure in "savefig" file or
            # if not given in filename (benchmark id result directory)
            if self._savefig not in [None, ""]:
                file_path_ind = self._savefig.rfind('/')
                if file_path_ind != -1:
                    # create full directory path if it doesn't exist
                    Path(os.path.expanduser(
                        self._savefig[:file_path_ind])).mkdir(
                            parents=True, exist_ok=True)
                fig.savefig(os.path.expanduser(self._savefig))
                # Print Figure location to screen and result.log
                LOGGER.info("Figure location of id {}: {}".format(
                    self._benchmark_ids[0], os.path.expanduser(self._savefig)))
            elif filename is not None:
                fig.savefig(filename.replace(".dat", ".png"))
                # Print Figure location to screen and result.log
                LOGGER.info("Figure location of id {}: {}".format(
                    self._benchmark_ids[0], os.path.expanduser(
                        filename.replace(".dat", ".png"))))

            # show figure if "showfig" attribute isn't set to False
            if self._showfig == "True":
                plt.show()
            plt.close()

    class Plot(GenericResult.DataKey):
        """A Plot type"""

        class Data():
            """Plot data"""
            def __init__(self, x, y, type, label):
                self._x = x
                self._y = y
                self._type = type
                self._label = label

            @property
            def x(self):
                """Get 'x'"""
                return self._x

            @property
            def y(self):
                """Get 'y'"""
                return self._y

            @property
            def type(self):
                """Get 'type'"""
                return self._type

            @property
            def label(self):
                """Get 'label'"""
                return self._label

            def __str__(self):
                return f"Data: x: {self._x}; y: {self._y}; type: {self._type}, label: {self._label}"

            def etree_repr(self):
                """Return etree object representation"""
                data_etree = ET.Element("data")
                data_etree.attrib["x"] = self._x
                data_etree.attrib["y"] = self._y
                if self._type not in [None, ""]:
                    data_etree.attrib["type"] = self._type
                if self._label not in [None, ""]:
                    data_etree.attrib["label"] = self._label
                return data_etree

        def __init__(self, plot_data, legend=None, xlabel=None, ylabel=None, name=None, title=None, unit=None):
            GenericResult.DataKey.__init__(self, name, title, unit)
            self._plot_data = list()
            for data in plot_data:
                self._plot_data.append(Figure.Plot.Data(data['x'], data['y'],
                                                        data['type'], data['label']))
            self._legend = legend
            if self._legend is None: self._legend = ""
            self._xlabel = xlabel
            if self._xlabel is None: self._xlabel = ""
            self._ylabel = ylabel
            if self._ylabel is None: self._ylabel = ""

        @property
        def legend(self):
            """Get 'legend'"""
            return self._legend

        @property
        def xlabel(self):
            """Get 'xlabel'"""
            return self._xlabel
        
        @property
        def ylabel(self):
            """Get 'ylabel'"""
            return self._ylabel
        
        @property
        def plot_data(self):
            """Get 'plot_data'"""
            return self._plot_data
        
        def __str__(self):
            return f"""IN PLOT: legend: {self._legend}; xlabel: {self._xlabel};
                    y: {self._ylabel}, data: {self._plot_data}"""
        
        def etree_repr(self):
            """Return etree object representation"""
            plot_etree = GenericResult.DataKey.etree_repr(self)
            plot_etree.tag = "plot"
            if self._legend not in [None, ""]:
                plot_etree.attrib["legend"] = self._legend
            if self._xlabel not in [None, ""]:
                plot_etree.attrib["xlabel"] = self._xlabel
            if self._ylabel not in [None, ""]:
                plot_etree.attrib["ylabel"] = self._ylabel
            for data in self._plot_data:
                plot_etree.append(data.etree_repr())
            return plot_etree

    def __init__(self, name, savefig=None, title=None, showfig=None, res_filter=None):
        GenericResult.__init__(self, name, res_filter)
        self._savefig = savefig
        self._title = title
        self._showfig = showfig
        self._plots = list()

    def add_key(self, name, title=None, unit=None):
        """Add an additional key to the dataset if it is not alread in the set"""
        if name not in [key.name for key in self._keys]:
            self._keys.append(GenericResult.DataKey(name, title, unit))

    def add_plot(self, legend, xlabel, ylabel, plot_data):
        """Add an additional plot to the dataset"""
        self._plots.append(Figure.Plot(plot_data, legend, xlabel, ylabel))

    def create_result_data(self, style=None, select=None, exclude=None):
        """Create result data"""
        result_data = GenericResult.create_result_data(self, select, exclude)
        return Figure.FigureData(result_data, self._plots, self._savefig,
                                 self._title, self._showfig)

    def etree_repr(self):
        """Return etree object representation"""
        result_etree = Result.etree_repr(self)
        figure_etree = ET.SubElement(result_etree, "Figure")
        figure_etree.attrib["name"] = self._name
        if self._title not in [None, ""]:
            figure_etree.attrib["title"] = self._title
        if self._savefig not in [None, ""]:
            figure_etree.attrib["savefig"] = self._savefig
        if self._showfig not in [None, ""]:
            figure_etree.attrib["showfig"] = self._showfig
        if self._res_filter not in [None, ""]:
            figure_etree.attrib["filter"] = self._res_filter
        for plot in self._plots:
            figure_etree.append(plot.etree_repr())
        return result_etree
