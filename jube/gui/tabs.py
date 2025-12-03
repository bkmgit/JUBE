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
"""notebook-tab definitions"""

import tkinter as tk
from tkinter import ttk
from jube.gui.sortabletreeview import SortableTreeview
from jube.conf import LIGHT_BLUE, GREY, WHITE
from jube.fileset import Copy, Link, Prepare
from jube.result_types.database import Database
from jube.result_types.table import Table
from jube.result_types.syslog import SysloggedResult
from jube.result_types.figure import Figure

class Tab(tk.Frame):

    """A Tab is part of a ttk.Notebook"""

    def __init__(self, root, data, app, title):
        super().__init__(root)
        self.config(bg=WHITE)
        self._data = data
        self._app = app
        self.config(padx=10, pady=10)
        self.widget_dict = dict()

        # Create necessary widgets
        self._window = tk.PanedWindow(self, 
                                      orient="horizontal",
                                      bd=0, 
                                      sashwidth=10, 
                                      bg=WHITE)
        self._menu = tk.Frame(self._window, 
                              bg=GREY, 
                              bd=0)
        self._title = tk.Label(self._menu, 
                               bg=GREY, 
                               font=("Arial",11,"bold"),
                               text = "Select a " + title + ":")
        list_var = tk.Variable(value=sorted(self._data.keys()))
        self._listbox = tk.Listbox(self._menu, 
                                   cursor="hand2", 
                                   selectmode=tk.BROWSE, 
                                   bd = 0, 
                                   highlightthickness=0, 
                                   bg=GREY, 
                                   selectbackground=LIGHT_BLUE, 
                                   width=0, 
                                   height=len(self._data), 
                                   listvariable=list_var)
        self._listbox.bind("<<ListboxSelect>>", self.item_selected)
        self._menu_x = tk.Scrollbar(self._menu, 
                                    orient=tk.HORIZONTAL, 
                                    command=self._listbox.xview)
        self._page = tk.Frame(self._window, 
                              bg=WHITE, 
                              bd=0)
        self._canvas = tk.Canvas(self._page, 
                                 bg=WHITE, 
                                 highlightthickness=0)
        self._canvas_x = tk.Scrollbar(self._page, 
                                      orient="horizontal", 
                                      command=self._canvas.xview)
        self._content = tk.Frame(self._canvas, 
                                 bg=WHITE)

        # Configure the PanedWindow
        self._window.add(self._menu, minsize=220, width=220)
        self._window.add(self._page, minsize=220)
        self._window.pack(fill="both", expand="True")
        self._window.bind("<B1-ButtonRelease>", lambda e: self.event_generate("<Configure>"))
        self.bind("<Configure>", self.configure_scrollregion)

        # Pack the menu region of the PanedWindow into the layout
        self._menu_x.pack(side="bottom", fill="x")
        self._listbox["xscrollcommand"] = self._menu_x.set
        self._title.pack(padx=10, pady=10, anchor="nw")
        self._listbox.pack(fill="both", padx=10, pady=10, anchor="nw")

        # pack the content region of the PanedWindow into the layout
        self._canvas_x.pack(side="bottom", fill="x")
        self._canvas.configure(xscrollcommand=self._canvas_x.set)
        self._canvas.create_window((0, 0), window=self._content, anchor="nw", tags="tab")
        self._canvas.pack(fill="both", expand=True)

    def configure_scrollregion(self, event = None):
        """Event Handler that is used if the the window size is changed.
        It configures the scrollregion so that the scrollbars work properly"""
        self.update_idletasks()
        main_height = self._content.winfo_reqheight()
        canvas_height = self._canvas.winfo_height()
        main_width = self._content.winfo_reqwidth()
        canvas_width = self._canvas.winfo_width()
        self._canvas.config(height=main_height)
        self._canvas.itemconfig("tab", 
                                width = main_width if main_width >= canvas_width else canvas_width, 
                                height = main_height)
        if main_width > canvas_width:
            self._canvas.configure(scrollregion=(0,0,main_width,canvas_height))
        else:
            self._canvas.configure(scrollregion=(0,0,canvas_width,canvas_height))
        self._canvas.update_idletasks()
        self._window.config(height=max(self._page.winfo_reqheight(), self._menu.winfo_reqheight()))
        self._window.update_idletasks()
    
    def item_selected(self, event):
        """Event Handler that is used if a item in the listbox is clicked
        It is used to display the correct set."""
        if event.widget == self._listbox and self._listbox.curselection():
            for i in range(self._listbox.size()):
                self._listbox.itemconfig(i, bg=GREY)
            for child in self._content.pack_slaves():
                child.pack_forget()
            item = self._listbox.curselection()[0]
            self._listbox.itemconfig(item, bg=LIGHT_BLUE)
            return item

class ParametersetTab(Tab):

    "A parameterset-tab displays the information about all parametersets"

    def __init__(self, root, parametersets, app):
        super().__init__(root, parametersets, app, "parameterset")

        # Create the widgets for each parameterset
        for parameterset in self._data.values():
            label = tk.Label(self._content, 
                             text = parameterset.name, 
                             bg=WHITE, 
                             font=("Arial",11,"bold"))
            label_duplicate = tk.Label(self._content, 
                                       text = "duplicate: " + f"{parameterset.duplicate!r}", 
                                       bg=WHITE)
            columns = ["parameter",
                       "value",
                       "mode",
                       "type",
                       "separator",
                       "export",
                       "unit",
                       "update_mode",
                       "duplicate"]
            param_table = SortableTreeview(self._content, 
                                           columns, 
                                           selectmode="none", 
                                           show="headings", 
                                           height=len(parameterset.parameter_dict), 
                                           style="Custom.Treeview")
            for parameter in parameterset.parameter_dict.values():
                param_table.insert("","end", values=[parameter.name,
                                                     parameter.value,
                                                     parameter.mode,
                                                     parameter.type,
                                                     parameter.separator,
                                                     parameter.export, 
                                                     parameter.unit, 
                                                     parameter.update_mode, 
                                                     parameter.duplicate])
            self.widget_dict[parameterset.name] = {"label": label, 
                                                   "duplicate": label_duplicate, 
                                                   "table": param_table}
        
        # Show the first parameterset
        if len(self._data) != 0:
            first = sorted(self._data.keys())[0]
            self.widget_dict[first]["label"].pack(anchor="w")
            self.widget_dict[first]["duplicate"].pack(anchor="w")
            self.widget_dict[first]["table"].pack(fill="both", expand="True", pady = 10)
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        item = super().item_selected(event)
        if item is not None:
            parameterset = self._listbox.get(item)
            self.widget_dict[parameterset]["label"].pack(anchor="w")
            self.widget_dict[parameterset]["duplicate"].pack(anchor="w")
            self.widget_dict[parameterset]["table"].pack(fill="both", expand="True", pady = 10)
            self.configure_scrollregion()
        
class PatternsetTab(Tab):

    "A patternset-tab displays the information about all patternsets"

    def __init__(self, root, patternsets, app):
        super().__init__(root, patternsets, app, "patternset")

        # Create the widgets for each patternset
        for patternset in self._data.values():
            label = tk.Label(self._content, 
                             text = patternset.name, 
                             bg=WHITE, 
                             font=("Arial",11,"bold"))
            columns = ["pattern",
                       "value",
                       "default",
                       "unit",
                       "mode",
                       "type",
                       "dotall"]
            table = SortableTreeview(self._content, 
                                     columns, 
                                     selectmode="none", 
                                     show="headings", 
                                     height=len(patternset.pattern_storage)+
                                            len(patternset.derived_pattern_storage), 
                                     style="Custom.Treeview")
            pattern_storage = patternset.pattern_storage.parameter_dict
            pattern_storage.update(patternset.derived_pattern_storage.parameter_dict)
            for pattern in pattern_storage.values():
                table.insert("","end",values=[pattern.name,
                                              pattern.value,
                                              pattern.default_value,
                                              pattern._unit, 
                                              pattern._mode, 
                                              pattern._type, 
                                              pattern.dotall])
            self.widget_dict[patternset.name] = {"label": label, 
                                                 "table": table}
        
        # show the first patternset
        if len(self._data) != 0:
            first = sorted(self._data.keys())[0]
            self.widget_dict[first]["label"].pack(anchor="w")
            self.widget_dict[first]["table"].pack(fill="both", expand="True", pady = 10)
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        item = super().item_selected(event)
        if event.widget == self._listbox and self._listbox.curselection():
            patternset = self._listbox.get(item)
            self.widget_dict[patternset]["label"].pack(anchor="w")
            self.widget_dict[patternset]["table"].pack(fill="both", expand="True", pady = 10)
            self.configure_scrollregion()
        
class FilesetTab(Tab):

    "A fileset-tab displays the information about all filesets"

    def __init__(self, root, filesets, app):
        super().__init__(root, filesets, app, "fileset")

        # Create the widgets for each fileset
        for fileset in self._data.values():
            label = tk.Label(self._content, 
                             text = fileset.name, 
                             bg=WHITE, 
                             font=("Arial",11,"bold"))
            links = [file for file in fileset if isinstance(file, Link)]
            copies = [file for file in fileset if isinstance(file, Copy)]
            prepares = [file for file in fileset if isinstance(file, Prepare)]

            # Create table for the link tags
            link_label = None
            link_tree = None
            if len(links) != 0:
                link_label = tk.Label(self._content, 
                                      text="Links:", 
                                      bg=WHITE)
                columns  =["file",
                           "source_dir",
                           "target_dir",
                           "name",
                           "rel_path_ref",
                           "active"]
                link_tree = SortableTreeview(self._content, 
                                             columns, 
                                             selectmode="none", 
                                             show="headings", 
                                             height=len(links), 
                                             style="Custom.Treeview")
                for link in links:
                    link_tree.insert("","end",values=[link.path,
                                                      link.source_dir, 
                                                      link.target_dir, 
                                                      link.name, 
                                                      link.is_internal_ref, 
                                                      link.active])

            # Create table for the copy tags
            copy_label = None
            copy_tree = None
            if len(copies) != 0:
                copy_label = tk.Label(self._content, 
                                      text="Copies:", 
                                      bg=WHITE)
                columns  =["file",
                           "source_dir",
                           "target_dir",
                           "name",
                           "rel_path_ref",
                           "active"]
                copy_tree = SortableTreeview(self._content, 
                                             columns, 
                                             selectmode="none", 
                                             show="headings", 
                                             height=len(copies), 
                                             style="Custom.Treeview")
                for copy in copies:
                    copy_tree.insert("","end",values=[copy.path,
                                                      copy.source_dir, 
                                                      copy.target_dir, 
                                                      copy.name, 
                                                      "internal" if copy.is_internal_ref else "external", 
                                                      copy.active])
            
            # Create table or prepare tags
            prepare_label = None
            prepare_tree = None
            if len(prepares) != 0:
                prepare_label = tk.Label(self._content, 
                                         text="Prepare:", 
                                         bg=WHITE)
                columns = ["prepare",
                           "stdout",
                           "stderr",
                           "work_dir",
                           "active"]
                prepare_tree = SortableTreeview(self._content, 
                                                columns, 
                                                selectmode="none", 
                                                show="headings", 
                                                height=len(prepares), 
                                                style="Custom.Treeview")
                for prepare in prepares:
                    prepare_tree.insert("","end",values=[prepare.do,
                                                         prepare.stdout_filename, 
                                                         prepare.stderr_filename, 
                                                         prepare._work_dir, 
                                                         prepare._active])
            self.widget_dict[fileset._name] = {"label": label,
                                               "link_label": link_label,
                                               "link_tree": link_tree,
                                               "copy_label": copy_label, 
                                               "copy_tree": copy_tree, 
                                               "prepare_label": prepare_label, 
                                               "prepare_tree": prepare_tree}
        
        # show the first fileset
        if len(self._data) != 0:
            first = sorted(self._data.keys())[0]
            if self.widget_dict[first]["label"]: 
                self.widget_dict[first]["label"].pack(anchor="w")
            if self.widget_dict[first]["link_label"]: 
                self.widget_dict[first]["link_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[first]["link_tree"]: 
                self.widget_dict[first]["link_tree"].pack(fill="both", pady = (0,10))
            if self.widget_dict[first]["copy_label"]: 
                self.widget_dict[first]["copy_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[first]["copy_tree"]: 
                self.widget_dict[first]["copy_tree"].pack(fill="both", pady = (0,10))
            if self.widget_dict[first]["prepare_label"]: 
                self.widget_dict[first]["prepare_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[first]["prepare_tree"]: 
                self.widget_dict[first]["prepare_tree"].pack(fill="both", pady = (0,10))
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        item = super().item_selected(event)
        if event.widget == self._listbox and self._listbox.curselection():
            fileset = self._listbox.get(item)
            if self.widget_dict[fileset]["label"]: 
                self.widget_dict[fileset]["label"].pack(anchor="w")
            if self.widget_dict[fileset]["link_label"]: 
                self.widget_dict[fileset]["link_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[fileset]["link_tree"]: 
                self.widget_dict[fileset]["link_tree"].pack(fill="both", pady = (0,10))
            if self.widget_dict[fileset]["copy_label"]: 
                self.widget_dict[fileset]["copy_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[fileset]["copy_tree"]: 
                self.widget_dict[fileset]["copy_tree"].pack(fill="both", pady = (0,10))
            if self.widget_dict[fileset]["prepare_label"]: 
                self.widget_dict[fileset]["prepare_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[fileset]["prepare_tree"]: 
                self.widget_dict[fileset]["prepare_tree"].pack(fill="both", pady = (0,10))
            self.configure_scrollregion()

class SubstitutesetTab(Tab):

    "A substituteset-tab displays the information about all substitutesets"

    def __init__(self, root, substitutesets, app):
        super().__init__(root, substitutesets, app, "substituteset")

        # Create the widgets for each substituteset
        for substituteset in self._data.values():
            label = tk.Label(self._content, 
                             text = substituteset.name, 
                             bg=WHITE, 
                             font=("Arial",11,"bold"))
            
            # Create table for the iofile tags
            io_label = None
            io_tree = None
            if len(substituteset.files) != 0:
                io_label = tk.Label(self._content, 
                                    text="IO-Files:", 
                                    bg=WHITE)
                columns = ["file_in", 
                           "file_out", 
                           "out_mode"]
                io_tree = SortableTreeview(self._content, 
                                           columns, 
                                           selectmode="none", 
                                           show="headings", 
                                           height=len(substituteset.files), 
                                           style="Custom.Treeview")
                for iofile in substituteset.files:
                    io_tree.insert("", "end", values=[iofile[1],
                                                      iofile[0], 
                                                      iofile[2]])
            
            # Create table for the sub tags
            sub_label = None
            sub_tree = None
            if len(substituteset.substitute_dict) != 0:
                sub_label = tk.Label(self._content, 
                                     text="Sub:", 
                                     bg=WHITE)
                columns = ["source",
                           "dest",
                           "mode"]
                sub_tree = SortableTreeview(self._content, 
                                            columns, 
                                            selectmode="none", 
                                            show="headings", 
                                            height=len(substituteset.substitute_dict), 
                                            style="Custom.Treeview")
                for sub in substituteset.substitute_dict.values():
                    sub_tree.insert("", "end", values=[sub.source,
                                                       sub.dest, 
                                                       sub.mode])
            self.widget_dict[substituteset._name] = {"label": label, 
                                                     "io_label": io_label, 
                                                     "io_tree": io_tree, 
                                                     "sub_label": sub_label, 
                                                     "sub_tree": sub_tree}
        
        # show the first substituteset
        if len(self._data) != 0:
            first = sorted(self._data.keys())[0]
            if self.widget_dict[first]["label"]: 
                self.widget_dict[first]["label"].pack(anchor="w")
            if self.widget_dict[first]["io_label"]: 
                self.widget_dict[first]["io_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[first]["io_tree"]: 
                self.widget_dict[first]["io_tree"].pack(fill="both", pady = (0,10))
            if self.widget_dict[first]["sub_label"]: 
                self.widget_dict[first]["sub_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[first]["sub_tree"]: 
                self.widget_dict[first]["sub_tree"].pack(fill="both", pady = (0,10))
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        item = super().item_selected(event)
        if event.widget == self._listbox and self._listbox.curselection():
            substituteset = self._listbox.get(item)
            if self.widget_dict[substituteset]["label"]: 
                self.widget_dict[substituteset]["label"].pack(anchor="w")
            if self.widget_dict[substituteset]["io_label"]: 
                self.widget_dict[substituteset]["io_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[substituteset]["io_tree"]: 
                self.widget_dict[substituteset]["io_tree"].pack(fill="both", pady = (0,10))
            if self.widget_dict[substituteset]["sub_label"]: 
                self.widget_dict[substituteset]["sub_label"].pack(anchor="w", pady=(10,0))
            if self.widget_dict[substituteset]["sub_tree"]: 
                self.widget_dict[substituteset]["sub_tree"].pack(fill="both", pady = (0,10))
            self.configure_scrollregion()

class AnalyserTab(Tab):

    "An analyser-tab displays the information about all analysers"

    def __init__(self, root, analyser, app):
        super().__init__(root, analyser, app, "analyser")

        # Create the widgets for each analyser
        for analyser in self._data.values():
            label = tk.Label(self._content, 
                             text = analyser.name, 
                             bg=WHITE, 
                             font=("Arial",11,"bold"))

            tree = ttk.Treeview(self._content, 
                                selectmode="none", 
                                show="tree", 
                                style="Custom.Treeview", 
                                height = len(analyser.use) + 1)
            tree.insert("", "end", text="reduce: " + f"{analyser.reduce_iteration!r}")
            for use in analyser.use:
                tree.insert("", "end", text="use: " + f"{use!r}")

            analyse_list = list()
            for step, files in sorted(analyser.analyser.items(), key=lambda x: x[0]):
                analyse_label = tk.Label(self._content, 
                                         text="Step: " + f"{step!r}", 
                                         bg=WHITE)
                table = None
                if len(files) != 0:
                    columns = ["file","use"]
                    table = SortableTreeview(self._content, 
                                             columns, 
                                             selectmode="none", 
                                             show="headings", 
                                             height=len(files), 
                                             style="Custom.Treeview")
                    for file in files:
                        table.insert("","end",values=[file.path, file.use])
                analyse_list.append({"label": analyse_label, 
                                     "table": table})
            self.widget_dict[analyser.name] = {"label": label, 
                                               "tree": tree, 
                                               "analyse": analyse_list}
        
        # show the first analyser
        if len(self._data) != 0:
            first = sorted(self._data.keys())[0]
            self.widget_dict[first]["label"].pack(anchor="w")
            self.widget_dict[first]["tree"].pack(fill="both")
            for analyse in self.widget_dict[first]["analyse"]:
                if analyse["table"]:
                    analyse["label"].pack(anchor="w", pady=(10,0))
                    analyse["table"].pack(fill="both", pady=(0,10))
                else:
                    analyse["label"].pack(anchor="w", pady=10)
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        item = super().item_selected(event)
        if event.widget == self._listbox and self._listbox.curselection():
            analyser = self._listbox.get(item)
            self.widget_dict[analyser]["label"].pack(anchor="w")
            self.widget_dict[analyser]["tree"].pack(fill="both")
            for analyse in self.widget_dict[analyser]["analyse"]:
                if analyse["table"]:
                    analyse["label"].pack(anchor="w", pady=(10,0))
                    analyse["table"].pack(fill="both", pady=(0,10))
                else:
                    analyse["label"].pack(anchor="w", pady=10)
            self.configure_scrollregion()
        
class ResultTab(Tab):

    "A result-tab displays the information about all results"

    def __init__(self, root, results, app):
        super().__init__(root, results, app, "result")

        # Create the widgets for each result
        for result in self._data.values():
            if isinstance(result, Table): text = "Table: "
            elif isinstance(result, SysloggedResult): text = "Syslog: "
            elif isinstance(result, Database): text = "Database: "
            elif isinstance(result, Figure): text = "Figure: "
            label = tk.Label(self._content, 
                             text = text + result.name, 
                             bg=WHITE, 
                             font=("Arial",11,"bold"))
            tree_general = ttk.Treeview(self._content, 
                                        selectmode="none", 
                                        show="tree", 
                                        style="Custom.Treeview", 
                                        height = len(result.use) + 
                                                (1 if result.result_dir is not None else 0))
            tree_result = None
            table = None
            if result.result_dir is not None: 
                tree_general.insert("", "end", text="result_dir: " + f"{result.result_dir!r}")
            for use in result.use:
                tree_general.insert("", "end", text="use: " + f"{use!r}")

            # Create result table for a table result
            if isinstance(result, Table):
                tree_result = ttk.Treeview(self._content, 
                                           selectmode="none", 
                                           show="tree", 
                                           style="Custom.Treeview", 
                                           height = 3 + 
                                                    (1 if result.sort is not None else 0) + 
                                                    (1 if result.res_filter is not None else 0))
                tree_result.insert("", "end", text="style: " + f"{result.style!r}")
                if len(result.sort) != 0: 
                    tree_result.insert("", "end", text="sort: " + 
                                                        ", ".join(f"{sort!r}" for sort in result.sort))
                tree_result.insert("", "end", text="separator: " + f"{result.separator!r}")
                tree_result.insert("", "end", text="transpose: " + f"{result.transpose!r}")
                if result.res_filter is not None: 
                    tree_result.insert("", "end", text="filter: " + f"{result.res_filter!r}")
                columns = ["column",
                           "format",
                           "title",
                           "colw"]
                table = SortableTreeview(self._content, 
                                         columns, 
                                         selectmode="none", 
                                         show="headings", 
                                         height=len(result.keys), 
                                         style="Custom.Treeview")
                for column in result.keys:
                    table.insert("","end",values=[column.name,
                                                  column.format, 
                                                  column.title, 
                                                  column.colw])
                
            # Create result table for a syslogged result
            elif isinstance(result, SysloggedResult): 
                tree_result = ttk.Treeview(self._content, 
                                           selectmode="none", 
                                           show="tree", 
                                           style="Custom.Treeview", 
                                           height = (1 if result.address is not None else 0) +
                                                    (1 if result.host is not None else 0) +
                                                    (1 if result.port is not None else 0) +
                                                    (1 if len(result.sort) != 0 else 0) +
                                                    (1 if result.syslog_string is not None else 0) +
                                                    (1 if result.res_filter is not None else 0))
                if result.address is not None: 
                    tree_result.insert("", "end", text="address: " + result.address)
                if result.host is not None: 
                    tree_result.insert("", "end", text="host: " + result.host)
                if result.port is not None: 
                    tree_result.insert("", "end", text="port: " + result.port)
                if len(result.sort) != 0: 
                    tree_result.insert("", "end", text="sort: " + 
                                                        ", ".join(f"{sort!r}" for sort in result.sort))
                if result.syslog_string is not None: 
                    tree_result.insert("", "end", text="format: " + result.syslog_string)
                if result.res_filter is not None: 
                    tree_result.insert("", "end", text="filter: " + result.res_filter)
                columns = ["key",
                           "format",
                           "title"]
                table = SortableTreeview(self._content, 
                                         columns, 
                                         selectmode="none", 
                                         show="headings", 
                                         height=len(result.keys), 
                                         style="Custom.Treeview")
                for key in result.keys:
                    table.insert("","end",values=[key.name,
                                                  key.format,
                                                  key.title])
                
            # Create result table for a database result
            elif isinstance(result, Database): 
                tree_result = ttk.Treeview(self._content, 
                                           selectmode="none", 
                                           show="tree", 
                                           style="Custom.Treeview", 
                                           height = 1 + 
                                                    (1 if len(result.primekeys) != 0 else 0) + 
                                                    (1 if result.res_filter is not None else 0))
                if len(result.primekeys) != 0: 
                    tree_result.insert("", "end", text="primekeys: " + 
                                                        f"{', '.join(result.primekeys)!r}")
                tree_result.insert("", "end", text="file: " + f"{result.file!r}")
                if result.res_filter is not None: 
                    tree_result.insert("", "end", text="filter: " + f"{result.res_filter!r}")
                columns = ["key",
                           "format",
                           "title"]
                table = SortableTreeview(self._content, 
                                         columns, 
                                         selectmode="none", 
                                         show="headings", 
                                         height=len(result.keys), 
                                         style="Custom.Treeview")
                for key in result.keys:
                    table.insert("","end",values=[key.name,
                                                  key.title, 
                                                  key.unit])
                    
            # Create result table for a figure result
            if isinstance(result, Figure):
                tree_result = ttk.Treeview(self._content, 
                                           selectmode="none", 
                                           show="tree", 
                                           style="Custom.Treeview", 
                                           height = 1 + 
                                                    (1 if result.title is not None else 0) + 
                                                    (1 if result.savefig is not None else 0) + 
                                                    (1 if result.showfig is not None else 0) + 
                                                    (1 if result.res_filter is not None else 0))
                if result.title is not None: 
                    tree_result.insert("", "end", text="title: " + f"{result.title!r}")
                if result.savefig is not None: 
                    tree_result.insert("", "end", text="savefig: " + f"{result.savefig!r}")
                if result.showfig is not None: 
                    tree_result.insert("", "end", text="showfig: " + f"{result.showfig!r}")
                if result.res_filter is not None: 
                    tree_result.insert("", "end", text="filter: " + f"{result.res_filter!r}")
                columns = ["Plot","legend","xlabel","ylabel","xscale","yscale","x","y","groupby","type","label","color","marker","linestyle"]
                height = sum([len(plot.plot_data) for plot in result.plots])
                table = SortableTreeview(self._content, 
                                         columns, 
                                         selectmode="none", 
                                         show="headings", 
                                         height=height, 
                                         style="Custom.Treeview")
                for i, plot in enumerate(result.plots):
                    for data in plot.plot_data:
                        table.insert("","end",values=[i, 
                                                      plot.legend, 
                                                      plot.xlabel, 
                                                      plot.ylabel, 
                                                      plot.xscale, 
                                                      plot.yscale, 
                                                      data.x, 
                                                      data.y, 
                                                      data.groupby, 
                                                      data.type, 
                                                      data.label, 
                                                      data.color, 
                                                      data.marker, 
                                                      data.linestyle])
                    
            self.widget_dict[result.name] = {"label": label, 
                                             "tree_general": tree_general, 
                                             "tree_result": tree_result, 
                                             "table": table}
        
        # show the first result
        if len(self._data) != 0:
            first = sorted(self._data.keys())[0]
            self.widget_dict[first]["label"].pack(anchor="w")
            self.widget_dict[first]["tree_general"].pack(fill="both")
            self.widget_dict[first]["tree_result"].pack(fill="both")
            self.widget_dict[first]["table"].pack(fill="both", pady = 10)
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        item = super().item_selected(event)
        if event.widget == self._listbox and self._listbox.curselection():
            result = self._listbox.get(item)
            self.widget_dict[result]["label"].pack(anchor="w")
            self.widget_dict[result]["tree_general"].pack(fill="both")
            self.widget_dict[result]["tree_result"].pack(fill="both")
            self.widget_dict[result]["table"].pack(fill="both", pady = 10)
            self.configure_scrollregion()
        