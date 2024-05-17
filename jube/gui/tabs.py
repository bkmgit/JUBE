import tkinter as tk
from tkinter import ttk
from jube.gui.sortabletreeview import SortableTreeview
from jube.conf import BLUE, LIGHT_BLUE, GREY, LIGHT_GREY, WHITE, BLACK
from jube.fileset import Copy, Link, Prepare
from jube.result_types.database import Database
from jube.result_types.table import Table
from jube.result_types.syslog import SysloggedResult

class Tab(tk.Frame):
    def __init__(self, root, data, app):
        super().__init__(root)
        self.config(bg=WHITE)
        self._data = data
        self._app = app
        self.config(padx=10, pady=10)

        self._window = tk.PanedWindow(self, orient="horizontal",bd=0, sashwidth=10, bg=WHITE)
        self._menu = tk.Frame(self._window, bg=GREY, bd=0)
        self._title = tk.Label(self._menu, bg=GREY, font=("Arial",11,"bold"))
        self._listbox = tk.Listbox(self._menu, cursor="hand2", selectmode=tk.BROWSE, bd = 0, highlightthickness=0, bg=GREY, selectbackground=LIGHT_BLUE, width=0)
        self._menu_x = tk.Scrollbar(self._menu, orient=tk.HORIZONTAL, command=self._listbox.xview)
        self._page = tk.Frame(self._window, bg=WHITE, bd=0)
        self._canvas = tk.Canvas(self._page, bg=WHITE, highlightthickness=0)
        self._canvas_x = tk.Scrollbar(self._page, orient="horizontal", command=self._canvas.xview)
        self._content = tk.Frame(self._canvas, bg=WHITE)
        self._dict = dict()

        # configure the PanedWindow
        self._window.add(self._menu, minsize=220, width=220)
        self._window.add(self._page, minsize=220)
        self._window.pack(fill="both", expand="True")
        self._window.bind("<B1-ButtonRelease>", lambda e: self.event_generate("<Configure>"))
        self.bind('<Configure>', self.configure_scrollregion)

        # pack the menu region of the PanedWindow
        self._menu_x.pack(side="bottom", fill="x")
        self._listbox['xscrollcommand'] = self._menu_x.set
        self._title.pack(padx=10, pady=10, anchor="nw")
        self._listbox.pack(fill="both", padx=10, pady=10, anchor="nw")

        # pack the content region of the PanedWindow
        self._canvas_x.pack(side="bottom", fill="x")
        self._canvas.configure(xscrollcommand=self._canvas_x.set)
        self._canvas.create_window((0, 0), window=self._content, anchor="nw", tags="tab")
        self._canvas.pack(fill="both", expand=True)

    def configure_scrollregion(self, event = None):
        self.update_idletasks()
        main_height = self._content.winfo_reqheight()
        canvas_height = self._canvas.winfo_height()
        main_width = self._content.winfo_reqwidth()
        canvas_width = self._canvas.winfo_width()
        self._canvas.config(height=main_height)
        self._canvas.itemconfig("tab", width = main_width if main_width >= canvas_width else canvas_width, height = main_height)
        if main_width > canvas_width:
            self._canvas.configure(scrollregion=(0,0,main_width,canvas_height))
        else:
            self._canvas.configure(scrollregion=(0,0,canvas_width,canvas_height))
        self._canvas.update_idletasks()
        self._window.config(height=max(self._page.winfo_reqheight(), self._menu.winfo_reqheight()))
        self._window.update_idletasks()

class ParametersetTab(Tab):
    def __init__(self, root, parametersets, app):
        super().__init__(root, parametersets, app)
        self._title.config(text="Select a parameterset:")
        list_var = tk.Variable(value=sorted(self._data.keys()))
        self._listbox.config(height=len(self._data), listvariable=list_var)
        self._listbox.bind('<<ListboxSelect>>', self.item_selected)

        # Create the widgets for each parameterset
        for parameterset in self._data.values():
            label = tk.Label(self._content, text = parameterset.name, bg=WHITE, font=("Arial",11,"bold"))
            label_duplicate = tk.Label(self._content, text = "duplicate: " + f"{parameterset.duplicate!r}", bg=WHITE)
            columns = ["parameter","value","mode","type","separator","export","unit","update_mode","duplicate"]
            param_table = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(parameterset.parameter_dict), style="Custom.Treeview")
            for parameter in parameterset.parameter_dict.values():
                param_table.insert("","end",values=[f"{parameter.name!r}" if parameter.name is not None else "", 
                                                    f"{parameter.value!r}" if parameter.value is not None else "",
                                                    f"{parameter.mode!r}" if parameter.mode is not None else "",
                                                    f"{parameter.type!r}" if parameter.type is not None else "", 
                                                    f"{parameter.separator!r}" if parameter.separator is not None else "", 
                                                    f"{parameter.export!r}" if parameter.export is not None else "", 
                                                    f"{parameter.unit!r}" if parameter.unit is not None else "", 
                                                    f"{parameter.update_mode!r}" if parameter.update_mode is not None else "", 
                                                    f"{parameter.duplicate!r}" if parameter.duplicate is not None else ""])
            self._dict[parameterset.name] = {"label": label, "duplicate": label_duplicate, "table": param_table}
        
        # show the first parameterset
        if len(self._data) != 0:
            self._dict[sorted(self._data.keys())[0]]["label"].pack(anchor="w")
            self._dict[sorted(self._data.keys())[0]]["duplicate"].pack(anchor="w")
            self._dict[sorted(self._data.keys())[0]]["table"].pack(fill="both", expand="True", pady = 10)
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        if event.widget == self._listbox and self._listbox.curselection():
            for i in range(self._listbox.size()):
                self._listbox.itemconfig(i, bg=GREY)
            for child in self._content.pack_slaves():
                child.pack_forget()
            item = self._listbox.curselection()[0]
            self._listbox.itemconfig(item, bg=LIGHT_BLUE)
            parameterset = self._listbox.get(item)
            self._dict[parameterset]["label"].pack(anchor="w")
            self._dict[parameterset]["duplicate"].pack(anchor="w")
            self._dict[parameterset]["table"].pack(fill="both", expand="True", pady = 10)
            self.update_idletasks()
            self.configure_scrollregion()
        
class PatternsetTab(Tab):
    def __init__(self, root, patternsets, app):
        super().__init__(root, patternsets, app)
        self._title.config(text="Select a patternset:")
        list_var = tk.Variable(value=sorted(self._data.keys()))
        self._listbox.config(height=len(self._data), listvariable=list_var)
        self._listbox.bind('<<ListboxSelect>>', self.item_selected)

        # Create the widgets for each patternset
        for patternset in self._data.values():
            label = tk.Label(self._content, text = patternset.name, bg=WHITE, font=("Arial",11,"bold"))
            columns = ["pattern","value","default","unit","mode","type","dotall"]
            table = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(patternset.pattern_storage)+len(patternset.derived_pattern_storage), style="Custom.Treeview")
            for pattern in list(patternset.pattern_storage.parameter_dict.values()) + list(patternset.derived_pattern_storage.parameter_dict.values()):
                table.insert("","end",values=[f"{pattern.name!r}" if pattern.name is not None else "",  
                                                f"{pattern.value!r}" if pattern.value is not None else "",
                                                f"{pattern.default_value!r}" if pattern.default_value is not None else "",
                                                f"{pattern.unit!r}" if pattern._unit is not None else "", 
                                                f"{pattern.mode!r}" if pattern._mode is not None else "", 
                                                f"{pattern.type!r}" if pattern._type is not None else "", 
                                                f"{pattern.dotall!r}" if pattern.dotall is not None else ""])
            self._dict[patternset.name] = {"label": label, "table": table}
        
        # show the first patternset
        if len(self._data) != 0:
            self._dict[sorted(self._data.keys())[0]]["label"].pack(anchor="w")
            self._dict[sorted(self._data.keys())[0]]["table"].pack(fill="both", expand="True", pady = 10)
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        if event.widget == self._listbox and self._listbox.curselection():
            for i in range(self._listbox.size()):
                self._listbox.itemconfig(i, bg=GREY)
            for child in self._content.pack_slaves():
                child.pack_forget()
            item = self._listbox.curselection()[0]
            self._listbox.itemconfig(item, bg=LIGHT_BLUE)
            patternset = self._listbox.get(item)
            self._dict[patternset]["label"].pack(anchor="w")
            self._dict[patternset]["table"].pack(fill="both", expand="True", pady = 10)
            self.update_idletasks()
            self.configure_scrollregion()
        
class FilesetTab(Tab):
    def __init__(self, root, filesets, app):
        super().__init__(root, filesets, app)
        self._title.config(text="Select a fileset:")
        list_var = tk.Variable(value=sorted(self._data.keys()))
        self._listbox.config(height=len(self._data), listvariable=list_var)
        self._listbox.bind('<<ListboxSelect>>', self.item_selected)

        # Create the widgets for each fileset
        for fileset in self._data.values():
            label = tk.Label(self._content, text = fileset.name, bg=WHITE, font=("Arial",11,"bold"))
            links = [file for file in fileset if isinstance(file, Link)]
            copies = [file for file in fileset if isinstance(file, Copy)]
            prepares = [file for file in fileset if isinstance(file, Prepare)]
            link_label = None
            link_tree = None
            if len(links) != 0:
                link_label = tk.Label(self._content, text="Links:", bg=WHITE)
                columns  =["file","source_dir","target_dir","name","rel_path_ref","active"]
                link_tree = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(links), style="Custom.Treeview")
                for link in links:
                    link_tree.insert("","end",values=[f"{link.path!r}" if link.path is not None else "", 
                                                        f"{link.source_dir!r}" if link.source_dir is not None else "", 
                                                        f"{link.target_dir!r}" if link.target_dir is not None else "", 
                                                        f"{link.name!r}" if link.name is not None else "", 
                                                        fr"internal" if link.is_internal_ref else fr"external", 
                                                        f"{link.active!r}" if link.active is not None else ""])
            copy_label = None
            copy_tree = None
            if len(copies) != 0:
                copy_label = tk.Label(self._content, text="Copies:", bg=WHITE)
                columns  =["file","source_dir","target_dir","name","rel_path_ref","active"]
                copy_tree = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(copies), style="Custom.Treeview")
                for copy in copies:
                    copy_tree.insert("","end",values=[f"{copy.path!r}" if copy.path is not None else "", 
                                                        f"{copy.source_dir!r}" if copy.source_dir is not None else "", 
                                                        f"{copy.target_dir!r}" if copy.target_dir is not None else "", 
                                                        f"{copy.name!r}" if copy.name is not None else "", 
                                                        fr"internal" if copy.is_internal_ref else fr"external", 
                                                        f"{copy.active!r}" if copy.active is not None else ""])
            prepare_label = None
            prepare_tree = None
            if len(prepares) != 0:
                prepare_label = tk.Label(self._content, text="Prepare:", bg=WHITE)
                columns = ["prepare","stdout","stderr","work_dir","active"]
                prepare_tree = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(prepares), style="Custom.Treeview")
                for prepare in prepares:
                    prepare_tree.insert("","end",values=[f"{prepare.do!r}" if prepare.do is not None else "", 
                                                            f"{prepare.stdout_filename!r}" if prepare.stdout_filename is not None else "", 
                                                            f"{prepare.stderr_filename!r}" if prepare.stderr_filename is not None else "", 
                                                            f"{prepare._work_dir!r}" if prepare._work_dir is not None else "", 
                                                            f"{prepare._active!r}" if prepare._active is not None else ""])
            self._dict[fileset._name] = {"label": label, "link_label": link_label, "link_tree": link_tree, "copy_label": copy_label, "copy_tree": copy_tree, "prepare_label": prepare_label, "prepare_tree": prepare_tree}
        
        # show the first fileset
        if len(self._data) != 0:
            if self._dict[sorted(self._data.keys())[0]]["label"]: self._dict[sorted(self._data.keys())[0]]["label"].pack(anchor="w")
            if self._dict[sorted(self._data.keys())[0]]["link_label"]: self._dict[sorted(self._data.keys())[0]]["link_label"].pack(anchor="w", pady=(10,0))
            if self._dict[sorted(self._data.keys())[0]]["link_tree"]: self._dict[sorted(self._data.keys())[0]]["link_tree"].pack(fill="both", pady = (0,10))
            if self._dict[sorted(self._data.keys())[0]]["copy_label"]: self._dict[sorted(self._data.keys())[0]]["copy_label"].pack(anchor="w", pady=(10,0))
            if self._dict[sorted(self._data.keys())[0]]["copy_tree"]: self._dict[sorted(self._data.keys())[0]]["copy_tree"].pack(fill="both", pady = (0,10))
            if self._dict[sorted(self._data.keys())[0]]["prepare_label"]: self._dict[sorted(self._data.keys())[0]]["prepare_label"].pack(anchor="w", pady=(10,0))
            if self._dict[sorted(self._data.keys())[0]]["prepare_tree"]: self._dict[sorted(self._data.keys())[0]]["prepare_tree"].pack(fill="both", pady = (0,10))
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        if event.widget == self._listbox and self._listbox.curselection():
            for i in range(self._listbox.size()):
                self._listbox.itemconfig(i, bg=GREY)
            for child in self._content.pack_slaves():
                child.pack_forget()
            item = self._listbox.curselection()[0]
            self._listbox.itemconfig(item, bg=LIGHT_BLUE)
            fileset = self._listbox.get(item)
            if self._dict[fileset]["label"]: self._dict[fileset]["label"].pack(anchor="w")
            if self._dict[fileset]["link_label"]: self._dict[fileset]["link_label"].pack(anchor="w", pady=(10,0))
            if self._dict[fileset]["link_tree"]: self._dict[fileset]["link_tree"].pack(fill="both", pady = (0,10))
            if self._dict[fileset]["copy_label"]: self._dict[fileset]["copy_label"].pack(anchor="w", pady=(10,0))
            if self._dict[fileset]["copy_tree"]: self._dict[fileset]["copy_tree"].pack(fill="both", pady = (0,10))
            if self._dict[fileset]["prepare_label"]: self._dict[fileset]["prepare_label"].pack(anchor="w", pady=(10,0))
            if self._dict[fileset]["prepare_tree"]: self._dict[fileset]["prepare_tree"].pack(fill="both", pady = (0,10))
            self.update_idletasks()
            self.configure_scrollregion()

class SubstitutesetTab(Tab):
    def __init__(self, root, substitutesets, app):
        super().__init__(root, substitutesets, app)
        self._title.config(text="Select a substituteset:")
        list_var = tk.Variable(value=sorted(self._data.keys()))
        self._listbox.config(height=len(self._data), listvariable=list_var)
        self._listbox.bind('<<ListboxSelect>>', self.item_selected)

        # Create the widgets for each substituteset
        for substituteset in self._data.values():
            label = tk.Label(self._content, text = substituteset.name, bg=WHITE, font=("Arial",11,"bold"))
            io_label = None
            io_tree = None
            if len(substituteset.files) != 0:
                io_label = tk.Label(self._content, text="IO-Files:", bg=WHITE)
                columns = ["file_in", "file_out", "out_mode"]
                io_tree = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(substituteset.files), style="Custom.Treeview")
                for iofile in substituteset.files:
                    io_tree.insert("", "end", values=[f"{iofile[1]!r}" if iofile[1] is not None else "", 
                                                        f"{iofile[0]!r}" if iofile[0] is not None else "", 
                                                        f"{iofile[2]!r}" if iofile[2] is not None else ""])
            sub_label = None
            sub_tree = None
            if len(substituteset.substitute_dict) != 0:
                sub_label = tk.Label(self._content, text="Sub:", bg=WHITE)
                columns = ["source","dest","mode"]
                sub_tree = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(substituteset.substitute_dict), style="Custom.Treeview")
                for sub in substituteset.substitute_dict.values():
                    sub_tree.insert("", "end", values=[f"{sub.source!r}" if sub.source is not None else "", 
                                                        f"{sub.dest!r}" if sub.dest is not None else "", 
                                                        f"{sub.mode!r}" if sub.mode is not None else ""])
            self._dict[substituteset._name] = {"label": label, "io_label": io_label, "io_tree": io_tree, "sub_label": sub_label, "sub_tree": sub_tree}
        
        # show the first substituteset
        if len(self._data) != 0:
            if self._dict[sorted(self._data.keys())[0]]["label"]: self._dict[sorted(self._data.keys())[0]]["label"].pack(anchor="w")
            if self._dict[sorted(self._data.keys())[0]]["io_label"]: self._dict[sorted(self._data.keys())[0]]["io_label"].pack(anchor="w", pady=(10,0))
            if self._dict[sorted(self._data.keys())[0]]["io_tree"]: self._dict[sorted(self._data.keys())[0]]["io_tree"].pack(fill="both", pady = (0,10))
            if self._dict[sorted(self._data.keys())[0]]["sub_label"]: self._dict[sorted(self._data.keys())[0]]["sub_label"].pack(anchor="w", pady=(10,0))
            if self._dict[sorted(self._data.keys())[0]]["sub_tree"]: self._dict[sorted(self._data.keys())[0]]["sub_tree"].pack(fill="both", pady = (0,10))
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        if event.widget == self._listbox and self._listbox.curselection():
            for i in range(self._listbox.size()):
                self._listbox.itemconfig(i, bg=GREY)
            for child in self._content.pack_slaves():
                child.pack_forget()
            item = self._listbox.curselection()[0]
            self._listbox.itemconfig(item, bg=LIGHT_BLUE)
            substituteset = self._listbox.get(item)
            if self._dict[substituteset]["label"]: self._dict[substituteset]["label"].pack(anchor="w")
            if self._dict[substituteset]["io_label"]: self._dict[substituteset]["io_label"].pack(anchor="w", pady=(10,0))
            if self._dict[substituteset]["io_tree"]: self._dict[substituteset]["io_tree"].pack(fill="both", pady = (0,10))
            if self._dict[substituteset]["sub_label"]: self._dict[substituteset]["sub_label"].pack(anchor="w", pady=(10,0))
            if self._dict[substituteset]["sub_tree"]: self._dict[substituteset]["sub_tree"].pack(fill="both", pady = (0,10))
            self.update_idletasks()
            self.configure_scrollregion()

class AnalyserTab(Tab):
    def __init__(self, root, analyser, app):
        super().__init__(root, analyser, app)
        self._title.config(text="Select an analyser:")
        list_var = tk.Variable(value=sorted(self._data.keys()))
        self._listbox.config(height=len(self._data), listvariable=list_var)
        self._listbox.bind('<<ListboxSelect>>', self.item_selected)

        # Create the widgets for each analyser
        for analyser in self._data.values():
            label = tk.Label(self._content, text = analyser.name, bg=WHITE, font=("Arial",11,"bold"))

            tree = ttk.Treeview(self._content, selectmode="none", show="tree", style="Custom.Treeview", height = len(analyser.use) + 1)
            tree.insert("", "end", text="reduce: " + f"{analyser.reduce_iteration!r}")
            for use in analyser.use:
                tree.insert("", "end", text="use: " + f"{use!r}")

            analyse_list = list()
            for step, files in sorted(analyser.analyser.items(), key=lambda x: x[0]):
                analyse_label = tk.Label(self._content, text="Step: " + f"{step!r}", bg=WHITE)
                table = None
                if len(files) != 0:
                    columns = ["file","use"]
                    table = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(files), style="Custom.Treeview")
                    for file in files:
                        table.insert("","end",values=[f"{file.path!r}", ', '.join(f"{use!r}" for use in file.use)])
                analyse_list.append({"label": analyse_label, "table": table})
            self._dict[analyser.name] = {"label": label, "tree": tree, "analyse": analyse_list}
        
        # show the first analyser
        if len(self._data) != 0:
            self._dict[sorted(self._data.keys())[0]]["label"].pack(anchor="w")
            self._dict[sorted(self._data.keys())[0]]["tree"].pack(fill="both")
            for analyse in self._dict[sorted(self._data.keys())[0]]["analyse"]:
                if analyse["table"]:
                    analyse["label"].pack(anchor="w", pady=(10,0))
                    analyse["table"].pack(fill="both", pady=(0,10))
                else:
                    analyse["label"].pack(anchor="w", pady=10)
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        if event.widget == self._listbox and self._listbox.curselection():
            # Remove the analyser contents from the layout
            for i in range(self._listbox.size()):
                self._listbox.itemconfig(i, bg=GREY)
            for child in self._content.pack_slaves():
                child.pack_forget()
            # Pack the new analyser contents into the layout
            item = self._listbox.curselection()[0]
            self._listbox.itemconfig(item, bg=LIGHT_BLUE)
            analyser = self._listbox.get(item)
            self._dict[analyser]["label"].pack(anchor="w")
            self._dict[analyser]["tree"].pack(fill="both")
            for analyse in self._dict[analyser]["analyse"]:
                if analyse["table"]:
                    analyse["label"].pack(anchor="w", pady=(10,0))
                    analyse["table"].pack(fill="both", pady=(0,10))
                else:
                    analyse["label"].pack(anchor="w", pady=10)
            self.update_idletasks()
            self.configure_scrollregion()
        
class ResultTab(Tab):
    def __init__(self, root, results, app):
        super().__init__(root, results, app)
        self._title.config(text="Select a result:")
        list_var = tk.Variable(value=sorted(self._data.keys()))
        self._listbox.config(height=len(self._data), listvariable=list_var)
        self._listbox.bind('<<ListboxSelect>>', self.item_selected)

        # Create the widgets for each result
        for result in self._data.values():
            if isinstance(result, Table): text = "Table: "
            elif isinstance(result, SysloggedResult): text = "Syslog: "
            elif isinstance(result, Database): text = "Database: "
            label = tk.Label(self._content, text = text + result.name, bg=WHITE, font=("Arial",11,"bold"))
            tree_general = ttk.Treeview(self._content, selectmode="none", show="tree", style="Custom.Treeview", height = len(result.use) + (1 if result.result_dir is not None else 0))
            tree_result = None
            table = None
            if result.result_dir is not None: tree_general.insert("", "end", text="result_dir: " + f"{result.result_dir!r}")
            for use in result.use:
                tree_general.insert("", "end", text="use: " + f"{use!r}")
            # Table
            if isinstance(result, Table):
                tree_result = ttk.Treeview(self._content, selectmode="none", show="tree", style="Custom.Treeview", height = 3 + (1 if result.sort is not None else 0) + (1 if result.res_filter is not None else 0))
                tree_result.insert("", "end", text="style: " + f"{result.style!r}")
                if len(result.sort) != 0: tree_result.insert("", "end", text="sort: " + ', '.join(f"{sort!r}" for sort in result.sort))
                tree_result.insert("", "end", text="separator: " + f"{result.separator!r}")
                tree_result.insert("", "end", text="transpose: " + f"{result.transpose!r}")
                if result.res_filter is not None: tree_result.insert("", "end", text="filter: " + f"{result.res_filter!r}")
                columns = ["column","format","title","colw"]
                table = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(result.keys), style="Custom.Treeview")
                for column in result.keys:
                    table.insert("","end",values=[f"{column.name!r}" if column.name is not None else "", 
                                                    f"{column.format!r}" if column.format is not None else "", 
                                                    f"{column.title!r}" if column.title is not None else "", 
                                                    f"{column.colw!r}" if column.colw is not None else ""])
            # Syslog
            elif isinstance(result, SysloggedResult): 
                tree_result = ttk.Treeview(self._content, selectmode="none", show="tree", style="Custom.Treeview", height = (1 if result.address is not None else 0) +
                                                                                                                    (1 if result.host is not None else 0) +
                                                                                                                    (1 if result.port is not None else 0) +
                                                                                                                    (1 if len(result.sort) != 0 else 0) +
                                                                                                                    (1 if result.syslog_string is not None else 0) +
                                                                                                                    (1 if result.res_filter is not None else 0))
                if result.address is not None: tree_result.insert("", "end", text="address: " + result.address)
                if result.host is not None: tree_result.insert("", "end", text="host: " + result.host)
                if result.port is not None: tree_result.insert("", "end", text="port: " + result.port)
                if len(result.sort) != 0: tree_result.insert("", "end", text="sort: " + ', '.join(f"{sort!r}" for sort in result.sort))
                if result.syslog_string is not None: tree_result.insert("", "end", text="format: " + result.syslog_string)
                if result.res_filter is not None: tree_result.insert("", "end", text="filter: " + result.res_filter)
                columns = ["key","format","title"]
                table = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(result.keys), style="Custom.Treeview")
                for key in result.keys:
                    table.insert("","end",values=[f"{key.name!r}" if key.name is not None else "", 
                                                    f"{key.format!r}" if key.format is not None else "", 
                                                    f"{key.title!r}" if key.title is not None else ""])
            # Database
            elif isinstance(result, Database): 
                tree_result = ttk.Treeview(self._content, selectmode="none", show="tree", style="Custom.Treeview", height = 1 + (1 if len(result.primekeys) != 0 else 0) + (1 if result.res_filter is not None else 0))
                if len(result.primekeys) != 0: tree_result.insert("", "end", text="primekeys: " + f"{', '.join(result.primekeys)!r}")
                tree_result.insert("", "end", text="file: " + f"{result.file!r}")
                if result.res_filter is not None: tree_result.insert("", "end", text="filter: " + f"{result.res_filter!r}")
                columns = ["key","format","title"]
                table = SortableTreeview(self._content, columns, selectmode="none", show="headings", height=len(result.keys), style="Custom.Treeview")
                for key in result.keys:
                    table.insert("","end",values=[f"{key.name!r}" if key.name is not None else "", 
                                                    f"{key.title!r}" if key.title is not None else "", 
                                                    f"{key.unit!r}" if key.unit is not None else ""])
            self._dict[result.name] = {"label": label, "tree_general": tree_general, "tree_result": tree_result, "table": table}
        
        # show the first result
        if len(self._data) != 0:
            self._dict[sorted(self._data.keys())[0]]["label"].pack(anchor="w")
            self._dict[sorted(self._data.keys())[0]]["tree_general"].pack(fill="both")
            self._dict[sorted(self._data.keys())[0]]["tree_result"].pack(fill="both")
            self._dict[sorted(self._data.keys())[0]]["table"].pack(fill="both", pady = 10)
            self._listbox.itemconfig(0, bg=LIGHT_BLUE)

    def item_selected(self, event):
        if event.widget == self._listbox and self._listbox.curselection():
            for i in range(self._listbox.size()):
                self._listbox.itemconfig(i, bg=GREY)
            for child in self._content.pack_slaves():
                child.pack_forget()
            item = self._listbox.curselection()[0]
            self._listbox.itemconfig(item, bg=LIGHT_BLUE)
            result = self._listbox.get(item)
            self._dict[result]["label"].pack(anchor="w")
            self._dict[result]["tree_general"].pack(fill="both")
            self._dict[result]["tree_result"].pack(fill="both")
            self._dict[result]["table"].pack(fill="both", pady = 10)
            self.update_idletasks()
            self.configure_scrollregion()
        