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
    # decision for matplotlib instead of pandas because Pandas is based on Matplotlib and therefore two dependencies would be necessary
except ImportError:
    pass
from pathlib import Path

from jube.result_types.genericresult import GenericResult
from jube.result import Result
import xml.etree.ElementTree as ET
import jube.log
import jube.conf

LOGGER = jube.log.get_logger(__name__)


class Figure(GenericResult):

    """A Figure result"""

    class FigureData(GenericResult.KeyValuesData):

        """Figure data"""

        def __init__(self, name_or_other, plots, savefig, title, showfig, nrows=0, ncols=0):
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
            self._nrows = nrows
            self._ncols = ncols

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
                x_data = sorted(table_data[data.x]) if data.sort else table_data[data.x]
                if data.type == "line":
                    func_args = "x_data, table_data[data.y], label=label"
                    for attr in ['color', 'marker', 'linestyle']:
                        attr_val = getattr(data, attr)
                        if attr_val:
                            func_args += f", {attr}=data.{attr}"
                    eval(f'ax.plot({func_args})')
                elif data.type in ["bar", "stem"]:
                    plot_func = getattr(ax, data.type)
                    plot_func(x_data, table_data[data.y],
                                label=label)
                else:
                    # dynamically create plot function call (e.g. ax.scatter())
                    plot_func = getattr(ax, data.type)
                    func_args = "x_data, table_data[data.y], label=label"
                    for attr in ['color', 'marker', 'linestyle']:
                        attr_val = getattr(data, attr)
                        if attr_val:
                            func_args += f", {attr}=data.{attr}"
                    eval(f'ax.{data.type}({func_args})')


            table_data = {v.name:k for v,k in self._data.items()}

            for plot in self._plots[:]:
                for data in plot.plot_data[:]:
                    if data.x not in table_data.keys() or \
                        data.y not in table_data.keys():
                        plot.plot_data.remove(data)
                if len(plot.plot_data) == 0:
                    self._plots.remove(plot)

            if len(self._plots) == 0:
                LOGGER.debug("No plotable data was found \n")
                return

            if self._nrows == 0 and self._ncols == 0:
                rows = 1
                cols= len(self._plots)
            elif self._nrows == 0:
                rows = (len(self._plots) + self._ncols - 1) // self._ncols
                cols= self._ncols
            elif self._ncols == 0:
                rows = self._nrows
                cols= (len(self._plots) + self._nrows - 1) // self._nrows
            elif self._nrows * self._ncols >= len(self._plots):
                rows = self._nrows
                cols= self._ncols
            else:
                LOGGER.error("There are too many plots for the specified number of rows (={0}) and columns (={1})".format(self._nrows, self._ncols))
                exit()
            try:
                fig, axes = plt.subplots(rows, cols)
            except NameError:
                LOGGER.error("If you want to use the figure result option, you have to install the matplotlib "
                             "package. See https://matplotlib.org/stable/install/index.html")
                exit()
            axes = axes.flatten() if rows*cols > 1 else [axes]
            fig.suptitle(self._title)
            for i, plot in enumerate(self._plots):
                if plot.xlabel: axes[i].set_xlabel(plot.xlabel)
                if plot.ylabel: axes[i].set_ylabel(plot.ylabel)
                if plot.xscale: axes[i].set_xscale(plot.xscale)
                if plot.yscale: axes[i].set_yscale(plot.yscale)
                for data in plot.plot_data:
                    if data.groupby:
                        groups = list(zip(*[table_data[g] for g in data.groupby]))
                        for group in sorted(set(groups)):
                            group_ids = [i for i, x in enumerate(groups) if x == group]
                            group_data = {
                                data.x: [table_data[data.x][i] for i in group_ids],
                                data.y: [table_data[data.y][i] for i in group_ids]
                            }
                            label = ", ".join(f"{value}" for value in group)
                            create_plot(data, group_data, axes[i], label=label)
                    else:
                        create_plot(data, table_data, axes[i])
                if plot.legend: axes[i].legend()

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
                    Path(path).mkdir(parents=True, exist_ok=True)
                fig.savefig(os.path.expanduser(self._savefig))
                # Print Figure location to screen and result.log
                LOGGER.info("Figure location of id {}: {}".format(
                    set(self._benchmark_ids), os.path.expanduser(self._savefig)))
            elif not self._savefig and filename is not None:
                fig.savefig(filename.replace(".dat", ".png"))
                # Print Figure location to screen and result.log
                LOGGER.info("Figure location of id {}: {}".format(
                    self._benchmark_ids[0], os.path.expanduser(
                        filename.replace(".dat", ".png"))))

            # show figure if "showfig" attribute isn't set to False
            if show and self._showfig:
                plt.show()
            plt.close()

    class Plot(GenericResult.DataKey):
        """A Plot type"""

        class Data():
            """Plot data"""
            def __init__(self, x, y, groupby, type, label,
                         color, marker, linestyle, sort_data):
                self._x = x
                self._y = y
                self._groupby = groupby
                self._type = type
                self._label = label
                self._color = color
                self._marker = marker
                self._linestyle = linestyle
                self._sort = sort_data

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

            @property
            def sort(self):
                """Get 'sort'"""
                return self._sort

            def __str__(self):
                return f"Data: x: {self._x}; y: {self._y}; "\
                    f"groupby: {self._groupby}, type: {self._type}, "\
                    f"label: {self._label}, color: {self._color}, " \
                    f"marker: {self._marker}, linestyle: {self._linestyle}"

            def add_information_to_database(self, db, plot_id):
                """Store plot data information in database"""
                data = dict()
                data["x"] = self._x
                data["y"] = self._y
                if self._groupby:
                    data["groupby"] = jube.conf.DEFAULT_SEPARATOR.join(self._groupby)
                if self._type:
                    data["plot_type"] = self._type
                if self._label:
                    data["label"] = self._label
                if self._color:
                    data["color"] = self._color
                if self._marker:
                    data["marker"] = self._marker
                if self._linestyle:
                    data["linestyle"] = self._linestyle
                if self._sort:
                    data["sort"] = 1
                data["plot_id"] = plot_id
                db.insert("ResultFigurePlotData", data)

        def __init__(self, plot_data, legend=False, xlabel=None, ylabel=None, xscale=None, yscale=None,
                     name=None, title=None, unit=None):
            GenericResult.DataKey.__init__(self, name, title, unit)
            self._plot_data = list()
            for data in plot_data:
                self._plot_data.append(
                    Figure.Plot.Data(data['x'], data['y'], data['groupby'],
                                     data['type'], data['label'],
                                     data['color'], data['marker'], 
                                     data['linestyle'],data['sort']))
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
                plot_str += f"{data}\n"
            return plot_str
            
        def add_information_to_database(self, db, figure_name):
            """Store plot information in database"""
            plot_data = dict()
            plot_data["figure_name"] = figure_name
            if self._legend:
                plot_data["legend"] = 1
            if self._xlabel:
                plot_data["xlabel"] = self._xlabel
            if self._ylabel:
                plot_data["ylabel"] = self._ylabel
            if self._xscale:
                plot_data["xscale"] = self._xscale
            if self._yscale:
                plot_data["yscale"] = self._yscale
            plot_id = db.insert("ResultFigurePlot", plot_data)
            for data in self._plot_data:
                data.add_information_to_database(db, plot_id)

    def __init__(self, name, showfig=True, savefig=None, title=None, res_filter=None, nrows=0, ncols=0):
        GenericResult.__init__(self, name, res_filter)
        self._showfig = showfig
        self._savefig = savefig
        self._title = title
        self._plots = list()
        self._nrows = nrows
        self._ncols = ncols

    @property
    def showfig(self):
        """Get 'showfig'"""
        return self._showfig

    @property
    def savefig(self):
        """Get 'savefig'"""
        return self._savefig

    @property
    def title(self):
        """Get 'title'"""
        return self._title

    @property
    def plots(self):
        """Get 'plots'"""
        return self._plots

    @property
    def nrows(self):
        """Get 'nrows'"""
        return self._nrows

    @property
    def ncols(self):
        """Get 'ncols'"""
        return self._ncols

    def add_key(self, name, title=None, unit=None):
        """Add an additional key to the dataset if it is not already in the set"""
        if name not in [key.name for key in self._keys]:
            self._keys.append(GenericResult.DataKey(name, title, unit))

    def add_plot(self, plot_data, legend, xlabel, ylabel, xscale, yscale):
        """Add an additional plot to the dataset"""
        self._plots.append(Figure.Plot(plot_data, legend, xlabel, ylabel, xscale, yscale))

    def create_result_data(self, style=None, select=None, exclude=None):
        """Create result data"""
        result_data = GenericResult.create_result_data(self, select, exclude)
        return Figure.FigureData(result_data, self._plots, self._savefig,
                                 self._title, self._showfig, self._nrows, self._ncols)
    
    def add_information_to_database(self, db, benchmark_id, update=False):
        """Store figure information in database"""
        try:
            db.start_transaction()
            result_id = Result.add_information_to_database(self, db, benchmark_id, update)
            figure_data = {
                "figure_name": self._name,
                "result_id": result_id
            }
            if self._title:
                figure_data["title"] = self._title
            if self._savefig:
                figure_data["savefig"] = self._savefig
            if self._showfig:
                figure_data["showfig"] = 1
            if self._res_filter is not None:
                figure_data["filter"] = self._res_filter
            if self._nrows > 0:
                figure_data["nrows"] = self._nrows
            if self._ncols > 0:
                figure_data["ncols"] = self._ncols
            db.insert("ResultFigure", figure_data)
            for plot in self._plots:
                plot.add_information_to_database(db, self._name)
            db.commit_transaction()
        except Exception as e:
            LOGGER.warning(str(e))
            db.rollback_transaction()
            db.disconnect()
            raise e
