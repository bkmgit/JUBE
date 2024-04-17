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
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass

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
                self._data = name_or_other.data
                self._benchmark_ids = name_or_other.benchmark_ids
            else:
                GenericResult.KeyValuesData.__init__(self, name_or_other)
            self._plots = plots
            self._savefig = savefig
            self._title = title
            self._showfig = showfig

        def create_result(self, show=True, filename=None, **kwargs):
            """Place for the magic: generate the figures
            this function is called twice for `jube result` command
            (see main.benchmarks_results())
                1. show=False, filename=*/*/result/*.dat
                2. show=True, filename=None
            or `jube run *xml/yaml -r` with the following args:
                show=True, filename=*/*/result/*.dat
            """
            table_data = {v.name:k for v,k in self._data.items()}

            for plot in self._plots[:]:
                for data in plot.plot_data[:]:
                    if data["x"] not in table_data.keys() or \
                        data["y"] not in table_data.keys():
                        plot.plot_data.remove(data)
                if len(plot.plot_data) == 0:
                    self._plots.remove(plot)

            if len(self._plots) == 0:
                return

            try:
                fig, ax = plt.subplots()
            except NameError:
                LOGGER.error("If you want to use the figure result option, you have to install the matplotlib "
                             "package. See https://matplotlib.org/stable/install/index.html")
                exit()
            fig.suptitle(self._title)
            for plot in self._plots:
                if plot.xlabel: ax.set_xlabel(plot.xlabel)
                if plot.ylabel: ax.set_ylabel(plot.ylabel)
                if plot.xscale: ax.set_xscale(plot.xscale)
                if plot.yscale: ax.set_yscale(plot.yscale)
                for data in plot.plot_data:
                    # plot function calls are created dynamically because certain
                    # arguments are not mandatory and would cause an error
                    plot_func = data["type"] if data["type"] != "line" else "plot"
                    func_args = "table_data[data['x']], table_data[data['y']], label=data['label']"
                    if data["type"] in ["line", "scatter", "step"]:
                        for attr in ['color', 'marker', 'linestyle']:
                            if data[attr] is not None:
                                func_args += f", {attr}=data['{attr}']"
                    eval(f"ax.{plot_func}({func_args})")
                if plot._legend: ax.legend()

            # if "savefig" is set, then save figure in "savefig" file
            #    (-> use data of all benchmark ids specified on the CLI)
            # else save figure in "filename" (benchmark id result directory)
            #    (-> one figure per benchmark id)
            # Additional clauses are need to avoid multiple saving
            if self._savefig and show:
                file_path_ind = self._savefig.rfind('/')
                if file_path_ind != -1:
                    # create full directory path if it doesn't exist
                    path = os.path.expanduser(self._savefig[:file_path_ind])
                    os.mkdir(path, parents=True, exist_ok=True)
                fig.savefig(os.path.expanduser(self._savefig))
                # Print Figure location to screen and result.log
                LOGGER.info("Figure location of id {}: {}".format(
                    self._benchmark_ids[0], os.path.expanduser(self._savefig)))
            elif self._savefig is None and filename is not None:
                fig.savefig(filename.replace(".dat", ".png"))
                # Print Figure location to screen and result.log
                LOGGER.info("Figure location of id {}: {}".format(
                    self._benchmark_ids[0], os.path.expanduser(
                        filename.replace(".dat", ".png"))))

            # show figure if "showfig" attribute isn't set to False
            if show and self._showfig:
                plt.show()
            plt.close()

    class Plot():
        """A Plot type"""

        def __init__(self, plot_data, legend=None, xlabel=None, ylabel=None, xscale=None, yscale=None):
            self._plot_data = plot_data
            self._legend = legend
            self._xlabel = xlabel
            self._ylabel = ylabel
            self._xscale = xscale
            self._yscale = yscale

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
        def xscale(self):
            """Get 'xlabel'"""
            return self._xscale

        @property
        def yscale(self):
            """Get 'ylabel'"""
            return self._yscale
        
        @property
        def plot_data(self):
            """Get 'plot_data'"""
            return self._plot_data
        
        def __str__(self):
            plot_str = f"IN PLOT: legend: {self._legend}, xlabel: {self._xlabel}, "\
                       f"ylabel: {self._ylabel}, xscale: {self._xscale}, "\
                       f"yscale: {self._yscale}\n"
            for data in self._plot_data:
                plot_str += f"Data: x: {data['x']}; y: {data['y']}; type: {data['type']}, "\
                            f"label: {data['label']}, color: {data['color']}," \
                            f"marker: {data['marker']}, linestyle: {data['linestyle']}\n"
            return plot_str
        
        def etree_repr(self):
            """Return etree object representation"""
            plot_etree = ET.Element("plot")
            if self._legend:
                plot_etree.attrib["legend"] = "true"
            if self._xlabel:
                plot_etree.attrib["xlabel"] = self._xlabel
            if self._ylabel:
                plot_etree.attrib["ylabel"] = self._ylabel
            for data in self._plot_data:
                data_etree = ET.SubElement(plot_etree, "data")
                # Add all data attributes to ET attributes
                data_etree.attrib = {k:v for k,v in data.items() if v is not None}
            return plot_etree

    def __init__(self, name, showfig=True, savefig=None, title=None):
        GenericResult.__init__(self, name, None)
        self._showfig = showfig
        self._savefig = savefig
        self._title = title
        self._plots = list()

    def add_key(self, name, title=None, unit=None):
        """Add an additional key to the dataset if it is not alread in the set"""
        if name not in [key.name for key in self._keys]:
            self._keys.append(GenericResult.DataKey(name, title, unit))

    def add_plot(self, plot_data, legend, xlabel, ylabel, xscale, yscale):
        """Add an additional plot to the dataset"""
        self._plots.append(Figure.Plot(plot_data, legend, xlabel, ylabel, xscale, yscale))

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
        if self._title:
            figure_etree.attrib["title"] = self._title
        if self._savefig:
            figure_etree.attrib["savefig"] = self._savefig
        if not self._showfig:
            figure_etree.attrib["showfig"] = "false"
        for plot in self._plots:
            figure_etree.append(plot.etree_repr())
        return result_etree
