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
"""definition of sortable ttk.Treeview"""

from tkinter import ttk
from jube.conf import GREY, LIGHT_GREY, WHITE


class SortableTreeview(ttk.Treeview):

    """A ttk.Treeview whose columns are sortable"""

    def __init__(self, parent, columns, *args, **kwargs):
        super().__init__(parent, columns=columns, *args, **kwargs)
        self._columns = columns
        for col in self._columns:
            self.heading(col, text=col)
            self.column(col, width=125, anchor="w")
        self._sort_column = self._columns[0]
        self._heading_clicked = True

        self.bind("<Button-1>", self.on_header_click)
        self.bind("<Motion>", self.on_heading_motion)

    def sort_by_column(self, col, descending=False):
        """Sorts the data in the column col descending/ascending"""
        data = [(self.set(child, col), child)
                for child in self.get_children("")]
        try:  # needed to allow numerical sorting in the TreeView
            data_converted = [(float(x), y) for x, y in data]
        except (ValueError, TypeError):
            data_converted = data
        data_converted.sort(reverse=not descending,
                            key=lambda x: x[0] if x[0] else x[0])
        for index, (val, child) in enumerate(data_converted):
            self.move(child, "", index)
        self._sort_column = col

        for column in self._columns:
            if column == col:
                if descending:
                    self.heading(column, text=str(column)+"   ▾")
                else:
                    self.heading(column, text=str(column)+"   ▴")
            else:
                self.heading(column, text=str(column))

    def on_header_click(self, event):
        """Event Handler that is used if the user clicks on a heading to sort the data by a column"""
        region = self.identify_region(event.x, event.y)
        if region == "heading":
            col = self.identify_column(event.x)
            if col:
                col = self._columns[int(col.lstrip("#")) - 1]
                if self._sort_column == col and self._heading_clicked:
                    self._heading_clicked = False
                    self.sort_by_column(col, self._heading_clicked)
                else:
                    self._heading_clicked = True
                    self.sort_by_column(col, self._heading_clicked)
        self.add_tags()

    def insert(self, parent, index, values):
        """Inserts a new row into the treeview"""
        iid = super().insert(parent, index,
                             values=[self._convert_value(value) for value in values])
        self.sort_by_column(self._sort_column, self._heading_clicked)
        self.add_tags()
        return iid

    def _convert_value(self, value):
        """converts a value to the format that should be displayed in the TreeView. 
        (internally the treeview saves all values as string)"""
        if value is None:
            return ""  # shows nothing
        elif isinstance(value, list) or isinstance(value, set):
            # '...','...','...'
            return ", ".join(f"{v!r}" for v in sorted(value))
        else:
            # escapes special characters such as \n
            return repr(str(value))[1:-1]

    def add_tags(self):
        """Creates alternating row colors"""
        if self["style"] == "Custom.Treeview":
            self.tag_configure("even", background=LIGHT_GREY)
            self.tag_configure("odd", background=GREY)
        elif self["style"] == "Grey.Custom.Treeview":
            self.tag_configure("even", background=LIGHT_GREY)
            self.tag_configure("odd", background=WHITE)
        else:
            self.tag_configure("even", background=WHITE)
            self.tag_configure("odd", background=GREY)

        for i, child_iid in enumerate(self.get_children()):
            if i % 2 == 0:
                self.item(child_iid, tags="even")
            else:
                self.item(child_iid, tags="odd")

    def on_heading_motion(self, event):
        """Event Handler that is used if the user hovers the mouse over the treeview"""
        if self.identify_region(event.x, event.y) == "heading":
            self.config(cursor="hand2")
        else:
            self.config(cursor="")
