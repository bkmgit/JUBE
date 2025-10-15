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

            def create_plot(data, table_data, ax, label=None):
                # plot function calls are created dynamically because certain
                # arguments are not mandatory and would cause an error
                label = label if label is not None else data.label
                if data.type == "line":
                    func_args = "table_data[data.x], table_data[data.y], label=label"
                    for attr in ['color', 'marker', 'linestyle']:
                        attr_val = getattr(data, attr)
                        if attr_val not in [None, ""]:
                            func_args += f", {attr}=data.{attr}"
                    eval(f'ax.plot({func_args})')
                elif data.type in ["bar", "stem"]:
                    plot_func = getattr(ax, data.type)
                    plot_func(table_data[data.x], table_data[data.y],
                                label=label)
                else:
                    # dynamically create plot function call (e.g. ax.scatter())
                    plot_func = getattr(ax, data.type)
                    func_args = "table_data[data.x], table_data[data.y], label=label"
                    for attr in ['color', 'marker', 'linestyle']:
                        attr_val = getattr(data, attr)
                        if attr_val not in [None, ""]:
                            func_args += f", {attr}=data.{attr}"
                    eval(f'ax.{data.type}({func_args})')
                if data.xscale not in [None, ""]: ax.set_xscale(data.xscale)
                if data.yscale not in [None, ""]: ax.set_yscale(data.yscale)


            table_data = {v.name:k for v,k in self._data.items()}

            for plot in self._plots[:]:
                for data in plot.plot_data[:]:
                    if data.x not in table_data.keys() or \
                        data.y not in table_data.keys():
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
                    if data.groupby not in [None, ""]:
                        for group in set(table_data[data.groupby]):
                            group_ids = [i for i, x in enumerate(table_data[data.groupby]) if x == group]
                            group_data = {data.x:list(), data.y:list()}
                            for key in group_data.keys():
                                for i in group_ids:
                                    group_data[key].append(table_data[key][i])
                            create_plot(data, group_data, ax, label=group)
                    else:
                        create_plot(data, table_data, ax)
                if plot._legend: ax.legend()

            # if "savefig" is set, then save figure in "savefig" file
            #    (-> use data of all benchmark ids specified on the CLI)
            # else save figure in "filename" (benchmark id result directory)
            #    (-> one figure per benchmark id)
            # Additional clauses are need to avoid multiple saving
            if self._savefig not in [None, ""] and show:
                file_path_ind = self._savefig.rfind('/')
                if file_path_ind != -1:
                    # create full directory path if it doesn't exist
                    path = os.path.expanduser(self._savefig[:file_path_ind])
                    Path(path).mkdir(parents=True, exist_ok=True)
                fig.savefig(os.path.expanduser(self._savefig))
                # Print Figure location to screen and result.log
                LOGGER.info("Figure location of id {}: {}".format(
                    set(self._benchmark_ids), os.path.expanduser(self._savefig)))
            elif self._savefig in [None, ""] and filename is not None:
                fig.savefig(filename.replace(".dat", ".png"))
                # Print Figure location to screen and result.log
                LOGGER.info("Figure location of id {}: {}".format(
                    self._benchmark_ids[0], os.path.expanduser(
                        filename.replace(".dat", ".png"))))

            # show figure if "showfig" attribute isn't set to False
            if show and self._showfig == "True":
                plt.show()
            plt.close()

    class Plot(GenericResult.DataKey):
        """A Plot type"""

        class Data():
            """Plot data"""
            def __init__(self, x, y, groupby, type, label, xscale, yscale,
                         color, marker, linestyle):
                self._x = x
                self._y = y
                self._groupby = groupby
                self._type = type
                self._label = label
                self._xscale = xscale
                self._yscale = yscale
                self._color = color
                self._marker = marker
                self._linestyle = linestyle

            @property
            def x(self):
                """Get 'x'"""
                return self._x

            @property
            def y(self):
                """Get 'y'"""
                return self._y

            @property
            def groupby(self):
                """Get 'groupby'"""
                return self._groupby

            @property
            def type(self):
                """Get 'type'"""
                return self._type

            @property
            def label(self):
                """Get 'label'"""
                return self._label

            @property
            def xscale(self):
                """Get 'xscale'"""
                return self._xscale

            @property
            def yscale(self):
                """Get 'yscale'"""
                return self._yscale

            @property
            def color(self):
                """Get 'color'"""
                return self._color

            @property
            def marker(self):
                """Get 'marker'"""
                return self._marker

            @property
            def linestyle(self):
                """Get 'linestyle'"""
                return self._linestyle

            def __str__(self):
                return f"Data: x: {self._x}; y: {self._y}; "\
                    f"groupby: {self._groupby}, type: {self._type}, "\
                    f"label: {self._label}, xscale: {self._xscale}, " \
                    f"yscale: {self._yscale}, color: {self._color}, " \
                    f"marker: {self._marker}, linestyle: {self._linestyle}"

            def etree_repr(self):
                """Return etree object representation"""
                data_etree = ET.Element("data")
                data_etree.attrib["x"] = self._x
                data_etree.attrib["y"] = self._y
                if self._groupby not in [None, ""]:
                    data_etree.attrib["groupby"] = self._groupby
                if self._type not in [None, ""]:
                    data_etree.attrib["type"] = self._type
                if self._label not in [None, ""]:
                    data_etree.attrib["label"] = self._label
                if self._xscale not in [None, ""]:
                    data_etree.attrib["xscale"] = self._xscale
                if self._yscale not in [None, ""]:
                    data_etree.attrib["yscale"] = self._yscale
                if self._color not in [None, ""]:
                    data_etree.attrib["color"] = self._color
                if self._marker not in [None, ""]:
                    data_etree.attrib["marker"] = self._marker
                if self._linestyle not in [None, ""]:
                    data_etree.attrib["linestyle"] = self._linestyle
                return data_etree

        def __init__(self, plot_data, legend=None, xlabel=None, ylabel=None, xscale=None, yscale=None,
                     name=None, title=None, unit=None):
            GenericResult.DataKey.__init__(self, name, title, unit)
            self._plot_data = list()
            for data in plot_data:
                self._plot_data.append(
                    Figure.Plot.Data(data['x'], data['y'], data['groupby'],
                                     data['type'], data['label'], 
                                     data['xscale'], data['yscale'],
                                     data['color'], data['marker'], 
                                     data['linestyle']))
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
            plot_etree = GenericResult.DataKey.etree_repr(self)
            plot_etree.tag = "plot"
            if self._legend not in [None, ""]:
                plot_etree.attrib["legend"] = self._legend
            if self._xlabel not in [None, ""]:
                plot_etree.attrib["xlabel"] = self._xlabel
            if self._ylabel not in [None, ""]:
                plot_etree.attrib["ylabel"] = self._ylabel
            if self._xscale not in [None, ""]:
                plot_etree.attrib["xscale"] = self._xscale
            if self._yscale not in [None, ""]:
                plot_etree.attrib["yscale"] = self._yscale
            for data in self._plot_data:
                plot_etree.append(data.etree_repr())
            return plot_etree

    def __init__(self, name, showfig="True", savefig=None, title=None, res_filter=None):
        GenericResult.__init__(self, name, res_filter)
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
        figure_etree = ET.SubElement(result_etree, "figure")
        figure_etree.attrib["name"] = self._name
        if self._title:
            figure_etree.attrib["title"] = self._title
        if self._savefig:
            figure_etree.attrib["savefig"] = self._savefig
        if self._showfig:
            figure_etree.attrib["showfig"] = self._showfig
        if self._res_filter:
            figure_etree.attrib["filter"] = self._res_filter
        for plot in self._plots:
            figure_etree.append(plot.etree_repr())
        return result_etree
