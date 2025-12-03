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
"""page definitions"""

from tkinter import ttk
import tkinter as tk
import jube.gui.tabs as tabs
import math
from jube.conf import BLUE, LIGHT_BLUE, GREY, LIGHT_GREY, WHITE
from jube.gui.sortabletreeview import SortableTreeview

class Page(tk.Frame):

    """A Page of the JUBE GUI"""

    def __init__(self, root):
        super().__init__(root)
        self._x_stay = list()
        self._y_stay = list()

        self.bind_all("<Button-4>", self.on_y_mousewheel)
        self.bind_all("<Button-5>", self.on_y_mousewheel)
        self.bind_all("<Shift-Button-4>", self.on_x_mousewheel)
        self.bind_all("<Shift-Button-5>", self.on_x_mousewheel)
        self.bind('<Configure>', self.configure_scrollregion)

    def step_clicked(self, name):
        """Open the step page for the specified step"""
        self.master.master.open_step_page(name)

    def wp_clicked(self, iid):
        """Open the workpackage page for the specified workpackage"""
        self.master.master.open_wp_page(iid)

    def bind_widget(self, label, func, text):
        """Configure the command of a button"""
        label.config(command=lambda : func(text))

    def on_y_mousewheel(self, event):
        """Event Handler that is used if the user scroll vertically with the mousewheel.
        It moves the content up/down"""
        parent = event.widget
        while parent:
            if isinstance(parent, tk.Canvas) and not parent in self._y_stay:
                if event.num == 4:
                    parent.yview_scroll(-1, 'units')
                elif event.num == 5:
                    parent.yview_scroll(1, 'units')
                break
            else:
                parent = parent.master

    def on_x_mousewheel(self, event):
        """Event Handler that is used if the user scroll horizontally with the mousewheel.
        It moves the content left/right"""
        parent = event.widget
        while parent:
            if isinstance(parent, tk.Canvas) and not parent in self._x_stay:
                if event.num == 4:
                    parent.xview_scroll(-1, 'units')
                elif event.num == 5:
                    parent.xview_scroll(1, 'units')
                break
            else:
                parent = parent.master

    def configure_scrollregion(self, event=None):
        """Event Handler that is used if the the window size is changed.
        It configures the scrollregion so that the scrollbars work properly"""
        pass

class MainPage(Page):

    """A page for all the main information of a benchmark (parametersets, patternsets, ...)"""

    def __init__(self, root, benchmark):
        super().__init__(root)
        self._benchmark = benchmark

        # Create necessary widgets
        self._label_file_path_ref = tk.Label(self, 
                                             text = "file_path_ref: " + f"{self._benchmark.file_path_ref!r}", 
                                             bg=WHITE)
        self._label_outpath = tk.Label(self, 
                                       text = "outpath: " + f"{self._benchmark.outpath!r}", 
                                       bg=WHITE)
        self._label_tag_docu = tk.Label(self, 
                                   text="\nTag Documentation:", 
                                   font=("Arial", 11, "bold"), 
                                   bg=WHITE)
        self._tree_tag_docu = ttk.Treeview(self, 
                                      selectmode="none", 
                                      show="tree", 
                                      style='Custom.Treeview')
        self._label_tag = tk.Label(self, 
                                   text="\nUsed Tags:", 
                                   font=("Arial", 11, "bold"), 
                                   bg=WHITE)
        self._tree_tag = ttk.Treeview(self, 
                                      selectmode="none", 
                                      show="tree", 
                                      style='Custom.Treeview')
        self._label_comment = tk.Label(self, 
                                       bg=WHITE)
        self._notebook = ttk.Notebook(self)
        self._parametersets = tabs.ParametersetTab(self, 
                                                   self._benchmark.parametersets, 
                                                   self.master.master)
        self._patternsets = tabs.PatternsetTab(self, 
                                               self._benchmark.patternsets, 
                                               self.master.master)
        self._filesets = tabs.FilesetTab(self, 
                                         self._benchmark.filesets, 
                                         self.master.master)
        self._substitutesets = tabs.SubstitutesetTab(self, 
                                                     self._benchmark.substitutesets, 
                                                     self.master.master)
        self._analyser = tabs.AnalyserTab(self, 
                                          self._benchmark.analyser, 
                                          self.master.master)
        self._results = tabs.ResultTab(self, 
                                       self._benchmark.results, 
                                       self.master.master)
        self._label_step = tk.Label(self, 
                                    text="Steps:", 
                                    font=("Arial", 11, "bold"), 
                                    bg=WHITE)
        self._canvas_steps = tk.Canvas(self, 
                                       bg=WHITE, 
                                       borderwidth=0, 
                                       highlightthickness=0)
        self._frames_steps = dict()
        self._scrollbar_x = tk.Scrollbar(self, 
                                         orient="horizontal", 
                                         command=self._canvas_steps.xview)

        self.config(bg=WHITE)
        self._x_stay = [self._canvas_steps]
        self._y_stay = [self._canvas_steps,
                        self._parametersets._canvas, 
                        self._patternsets._canvas, 
                        self._substitutesets._canvas, 
                        self._filesets._canvas, 
                        self._analyser._canvas, 
                        self._results._canvas]
        self.place_widgets()

    def place_widgets(self):
        """Places the widgets in the layout"""
        # pack the widgets with the general benchmark information into the layout
        self._label_file_path_ref.pack(anchor="w")
        self._label_outpath.pack(anchor="w")
        if self._benchmark._comment is not None: 
            self._label_comment.config(text="comment: "+f"{self._benchmark._comment!r}")
        self._label_comment.pack(anchor="w")
        if len(self._benchmark._tags) != 0:
            self._label_tag_docu.pack(anchor="w")
            for tag, desc in self._benchmark._tag_docu.items():
                self._tree_tag_docu.insert("","end",text=f"{tag}: {desc}" if tag is not None else "")
            self._tree_tag_docu.config(height=len(self._benchmark._tag_docu))
            self._tree_tag_docu.pack(anchor="w", fill="x")
        if len(self._benchmark._tags) != 0:
            self._label_tag.pack(anchor="w")
            for tag in self._benchmark._tags:
                self._tree_tag.insert("","end",text=f"{tag!r}" if tag is not None else "")
            self._tree_tag.config(height=len(self._benchmark._tags))
            self._tree_tag.pack(anchor="w", fill="x")

        # fill the notebook with tabs and pack it into the layout
        if len(self._benchmark._parametersets) != 0: 
            self._notebook.add(self._parametersets, text="Parametersets")
        if len(self._benchmark._patternsets) != 0: 
            self._notebook.add(self._patternsets, text="Patternsets")
        if len(self._benchmark._filesets) != 0: 
            self._notebook.add(self._filesets, text="Filesets")
        if len(self._benchmark._substitutesets) != 0: 
            self._notebook.add(self._substitutesets, text="Substitutesets")
        if len(self._benchmark._analyser) != 0: 
            self._notebook.add(self._analyser, text="Analyser")
        if len(self._benchmark._results) != 0: 
            self._notebook.add(self._results, text="Result")
        self._notebook.pack(fill="both", padx=10, pady=25)
        self._notebook.pack_propagate(True)
        self._notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # create the step graph and pack the widgets into the layout
        if len(self._benchmark._steps):
            self._label_step.pack(anchor="w")
            self.create_graph()
            canvas_bbox = self._canvas_steps.bbox("all")
            self._canvas_steps.config(width=canvas_bbox[2] - canvas_bbox[0], 
                                      height=canvas_bbox[3] - canvas_bbox[1])
            self._canvas_steps.pack(anchor="center", padx = 25, pady = 25)
            self._scrollbar_x.pack(side="bottom", fill="x")
            self._canvas_steps.configure(xscrollcommand=self._scrollbar_x.set)

    def get_levels(self):
        """Calculates for each step on which height/level (of the dependency graph) it needs to be"""
        levels = {}
        level_len = 0 
        for step in self._benchmark._steps.values():
            j = -1
            for depend in step.depend:
                level = level_len - 1
                while(level >= 0 and depend not in [step.name for step in levels[level]]):
                    level = level -1
                if level > j: j = level
            if j + 1== level_len:
                levels[j + 1] = [step]
                level_len = level_len + 1
            else:
                levels[j + 1].append(step)
        return levels
    
    def create_graph(self):
        """Creates the dependency graph for the steps of a benchmark"""
        levels = self.get_levels()
        max_columns = 2 * max([len(levels[level]) for level in levels]) - 1
        for level in levels.keys():
            length = len(levels[level])
            for i in enumerate(levels[level]):
                # add a step to the graph
                label = tk.Button(self._canvas_steps, 
                                  text=i[1].name, 
                                  highlightbackground=BLUE, 
                                  activebackground=BLUE, 
                                  activeforeground=WHITE, 
                                  cursor="hand2", 
                                  bg=LIGHT_BLUE)
                self.bind_widget(label, self.step_clicked, i[1].name)
                column = math.floor(max_columns/2)+2*(i[0]-math.floor(length/2))
                if length % 2 == 0: column = column + 1
                self._frames_steps[i[1].name] = self._canvas_steps.create_window(
                    column * 150, 2 * level * 50, 
                    window = label, 
                    anchor="nw", 
                    width=150, 
                    height=50)
                # draw the dependencies for the current step
                for depend in i[1].depend:
                    coord1 = self._canvas_steps.coords(self._frames_steps[depend])
                    coord2 = self._canvas_steps.coords(self._frames_steps[i[1].name])
                    self._canvas_steps.create_line(coord1[0] + 75, 
                                                   coord1[1] + 50, 
                                                   coord2[0] + 75, 
                                                   coord2[1], 
                                                   arrow="last")

    def configure_scrollregion(self, event):
        canvas_height = self._canvas_steps.winfo_height()
        main_bbox = self._canvas_steps.bbox("all")
        main_width = main_bbox[2]-main_bbox[0] if main_bbox else 0
        canvas_width = self._canvas_steps.winfo_reqwidth()
        if main_width > canvas_width:
            self._canvas_steps.configure(scrollregion=(0,0,main_width,canvas_height))
            self._scrollbar_x.pack(side="bottom",fill="x")
        else:
            self._canvas_steps.configure(scrollregion=(0,0,canvas_width,canvas_height))
            self._scrollbar_x.pack_forget()

    def on_tab_changed(self, event):
        widget = event.widget.nametowidget(event.widget.select())
        widget.configure_scrollregion()
        widget.configure_scrollregion()

class StepPage(Page):

    """A page for the information of a specific step (used sets, operations, ...)"""

    def __init__(self, root, step, benchmark):
        super().__init__(root)
        self._step = step
        self._benchmark = benchmark
        self._parents_arrow = tk.Canvas(self, 
                                        bg=WHITE, 
                                        borderwidth=0,
                                        highlightthickness=0, 
                                        width=50)
        self._parents_canvas = tk.Canvas(self, 
                                         bg=WHITE, 
                                         borderwidth=0, 
                                         highlightthickness=0, 
                                         width=200)
        self._parents_scrollbar = tk.Scrollbar(self, 
                                               orient=tk.VERTICAL, 
                                               command=self._parents_canvas.yview)
        self._step_frame = tk.LabelFrame(self, 
                                         text=self._step.name, 
                                         bg=GREY, 
                                         font=("Arial", 11, "bold"))
        self._mid_canvas = tk.Canvas(self._step_frame, 
                                     bg=GREY, 
                                     borderwidth=0, 
                                     highlightthickness=0, 
                                     width=250)
        self._mid_scrollbar_y = tk.Scrollbar(self._step_frame, 
                                             orient=tk.VERTICAL, 
                                             command=self._mid_canvas.yview)
        self._mid_scrollbar_x = tk.Scrollbar(self._step_frame, 
                                             orient=tk.HORIZONTAL, 
                                             command=self._mid_canvas.xview)
        self._mid = tk.Frame(self._mid_canvas, 
                             bg=GREY)
        self._step_tree = ttk.Treeview(self._mid, 
                                       selectmode="none", 
                                       show="tree", 
                                       style="Grey.Custom.Treeview")
        self._use_label = tk.Label(self._mid, 
                                   text="\nUse:", 
                                   font=("Arial", 11, "bold"), 
                                   bg=GREY)
        self._use_tree = ttk.Treeview(self._mid, 
                                      selectmode="none", 
                                      show="tree", 
                                      style="Grey.Custom.Treeview")
        self._do_label = tk.Label(self._mid, 
                                  text="\nDo:", 
                                  font=("Arial", 12, "bold"), 
                                  bg=GREY)
        columns = ["do",
                   "break_file",
                   "shared",
                   "active",
                   "stdout",
                   "stderr",
                   "done_file",
                   "error_file",
                   "work_dir"]
        self._do_tree = SortableTreeview(self._mid, 
                                         columns, 
                                         selectmode="none", 
                                         show="headings", 
                                         style="Grey.Custom.Treeview")
        self._step_separator = ttk.Separator(self._mid, 
                                             orient="horizontal")
        self._step_label_wp = tk.Label(self._mid, 
                                       text="Workpackages:", 
                                       font=("Arial", 11, "bold"), 
                                       bg=GREY)
        self._step_canvas = tk.Canvas(self._mid, 
                                      bg=GREY, 
                                      borderwidth=0, 
                                      highlightthickness=0)
        self._step_frames = dict()
        self._children_arrow = tk.Canvas(self, 
                                         bg=WHITE, 
                                         borderwidth=0, 
                                         highlightthickness=0, 
                                         width=50)
        self._children_canvas = tk.Canvas(self, 
                                          bg=WHITE, 
                                          borderwidth=0, 
                                          highlightthickness=0, 
                                          width=200)
        self._children_scrollbar = tk.Scrollbar(self, 
                                                orient=tk.VERTICAL, 
                                                command=self._children_canvas.yview)
        self.config(bg=WHITE)
        self._x_stay = [self._children_arrow, 
                        self._parents_arrow,
                        self._step_canvas, 
                        self._parents_canvas, 
                        self._children_canvas]
        self._y_stay = [self._children_arrow,
                        self._parents_arrow, 
                        self._step_canvas]
        self.place_widgets()

    def place_widgets(self):
        """Places all the widgets in the layout"""
        # pack the widgets for the parents region into the layout
        self.plot_parents()
        canvas_bbox = self._parents_canvas.bbox("all")
        if canvas_bbox:
            self._parents_arrow.create_line(0, 10, 25, 10, 
                                            arrow="last", 
                                            arrowshape=(16,20,6), 
                                            width=10)
            self._parents_arrow.config(height=20)
            self._parents_canvas.configure(yscrollcommand=self._parents_scrollbar.set)
        self._parents_canvas.pack(anchor="center", side="left", pady=25)
        self._parents_arrow.pack(anchor="center", side="left", pady=25)

        # pack the widgets for the children region into the layout
        self.plot_children()
        canvas_bbox = self._children_canvas.bbox("all")
        if canvas_bbox:
            self._children_arrow.create_line(25, 10, 50, 10, 
                                             arrow="last", 
                                             arrowshape=(16,20,6), 
                                             width=10)
            self._children_arrow.config(height=20)
            self._children_canvas.configure(yscrollcommand=self._children_scrollbar.set)
        self._children_canvas.pack(anchor="center", side="right", pady=25)
        self._children_arrow.pack(anchor="center", side="right", pady=25)

        # pack the widgets for the mid region into the layout
        self._step_frame.pack(anchor="center", fill = "both", side="right", expand="True", pady=25)
        self._mid_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self._mid_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self._mid_canvas.configure(yscrollcommand=self._mid_scrollbar_y.set)
        self._mid_canvas.configure(xscrollcommand=self._mid_scrollbar_x.set)
        self._mid_canvas.create_window((0,0), window=self._mid, anchor="nw", tags="mid")
        self._mid_canvas.pack(anchor="center", fill="both", expand="true")
        self.show_data() # fills the treeviews with data
        
        # pack the step tree into the layout
        self._step_tree.config(height = len([element for element in [self._step.alt_work_dir,
                                                                     self._step.suffix,
                                                                     self._step.shared_link_name,
                                                                     self._step.active,
                                                                     self._step.export,
                                                                     self._step.max_wps,
                                                                     self._step.iterations,
                                                                     self._step.cycles,
                                                                     self._step.procs,
                                                                     self._step.do_log_file] 
                                                                     if element is not None]))
        
        self._step_tree.pack(fill="both", expand="True")
        
        # pack the widgets for the used sets into the layout
        uses = [use for uselist in self._step.use for use in uselist]
        for stepname in self._step.get_depend_history(self._benchmark):
            step = self._benchmark._steps[stepname]
            uses.extend([use for use in 
                         [use for uselist in step.use for use in uselist] 
                         if use not in uses])
        if len(uses)  != 0:
            self._use_label.pack(anchor="w")
            self._use_tree.config(height = len(uses))
            self._use_tree.pack(fill="both", expand="True")
        
        # pack the widgets for the dos into the layout
        if len(self._step.operations) != 0:
            self._do_label.pack(anchor="w")
            self._do_tree.config(height = len(self._step.operations))
            self._do_tree.pack(fill="both", expand="True", padx=25)

        # pack the widgets for the workpackages into the layout
        self._step_separator.pack(fill="x", padx=25, pady=25)
        self._step_label_wp.pack(anchor="w")
        self.plot_frames()
        canvas_bbox = self._step_canvas.bbox("all")
        if canvas_bbox:
            self._step_canvas.config(width=canvas_bbox[2] - canvas_bbox[0], 
                                     height=canvas_bbox[3] - canvas_bbox[1] + 50)
        self._step_canvas.pack(anchor="w", expand="True", padx=25)

    def plot_parents(self):
        """Plots the parent steps in the layout"""
        for i, stepname in enumerate(self._step.depend):
            step = self._benchmark._steps[stepname]
            label = tk.Button(self._parents_canvas, 
                              text=step.name, 
                              highlightbackground=BLUE, 
                              activebackground=BLUE, 
                              activeforeground=WHITE, 
                              cursor="hand2", 
                              bg=LIGHT_BLUE)
            self.bind_widget(label, self.step_clicked, step.name)
            self._step_frames[step.name] = self._parents_canvas.create_window(25, 75 * i , 
                                                                              window = label, 
                                                                              anchor="nw", 
                                                                              width=150, 
                                                                              height=50)

    def plot_children(self):
        """Plots the dependent steps in the layout"""
        children = list()
        for step in self._benchmark._steps.values():
            if (self._step.name in step.depend): children.append(step)
        for i, step in enumerate(children):
            label = tk.Button(self._children_canvas, 
                              text=step.name, 
                              highlightbackground=BLUE, 
                              activebackground=BLUE, 
                              activeforeground=WHITE, 
                              cursor="hand2", 
                              bg=LIGHT_BLUE)
            self.bind_widget(label, self.step_clicked, step.name)
            self._step_frames[step.name] = self._children_canvas.create_window(25, 75 * i , 
                                                                               window = label, 
                                                                               anchor="nw", 
                                                                               width=150, 
                                                                               height=50)

    def show_data(self):
        """Fills the treeview on this page with data"""
        # fill the step Treeview with data
        if self._step.alt_work_dir is not None: 
            self._step_tree.insert("", "end", text="work_dir: " + f"{self._step.alt_work_dir!r}")
        if self._step.suffix is not None: 
            self._step_tree.insert("", "end", text="suffix: " + f"{self._step.suffix!r}")
        if self._step.shared_link_name is not None: 
            self._step_tree.insert("", "end", text="shared: " + f"{self._step.shared_link_name!r}")
        if self._step.active is not None: 
            self._step_tree.insert("", "end", text="active: " + f"{self._step.active!r}")
        if self._step.export is not None: 
            self._step_tree.insert("", "end", text="export: " + f"{self._step.export!r}")
        if self._step.max_wps is not None: 
            self._step_tree.insert("", "end", text="max_async: " + f"{self._step.max_wps!r}")
        if self._step.iterations is not None: 
            self._step_tree.insert("", "end", text="iterations: " + f"{self._step.iterations!r}")
        if self._step.cycles is not None: 
            self._step_tree.insert("", "end", text="cycles: " + f"{self._step.cycles!r}")
        if self._step.procs is not None: 
            self._step_tree.insert("", "end", text="procs: " + f"{self._step.procs!r}")
        if self._step.do_log_file is not None: 
            self._step_tree.insert("", "end", text="do_log_file: " + f"{self._step.do_log_file!r}")

        # fill the use Treeview with data
        uses = [use for uselist in self._step.use for use in uselist]
        for stepname in self._step.get_depend_history(self._benchmark):
            step = self._benchmark._steps[stepname]
            uses.extend([use for use in 
                         [use for uselist in step.use for use in uselist] 
                         if use not in uses])
        for use in sorted(uses):
            self._use_tree.insert("", "end", text=f"{use!r}")

        # fill the do Treeview with data
        for do in self._step.operations:
            self._do_tree.insert("","end",values=[do.do,
                                                  do.break_filename, 
                                                  do.shared, 
                                                  do.is_active, 
                                                  do.stdout_filename, 
                                                  do.stderr_filename, 
                                                  do.async_filename, 
                                                  do.error_filename, 
                                                  do.work_dir])

    def plot_frames(self):
        """Plots the workpackages that belong to the current step"""
        self.update_idletasks()
        wp_per_row = math.floor(max(self._step_tree.winfo_reqwidth(),
                                    self._use_label.winfo_reqwidth(),
                                    self._use_tree.winfo_reqwidth(),
                                    self._do_label.winfo_reqwidth(),
                                    self._do_tree.winfo_reqwidth(),
                                    self._mid_canvas.winfo_width()-50) / 175)
        self._step_canvas.delete("all")
        if wp_per_row == 0: wp_per_row+=1
        for i, wp in enumerate(self._benchmark._workpackages[self._step.name]):
            label = tk.Button(self._step_canvas, 
                              text="Workpackage " +str(wp.id), 
                              highlightbackground=BLUE, 
                              activebackground=BLUE, 
                              activeforeground=WHITE, 
                              cursor="hand2", 
                              bg=wp.status_color())
            self.bind_widget(label, self.wp_clicked, wp.id)
            column = i%wp_per_row
            self._step_frames[wp.id] = self._step_canvas.create_window(column * 175, 
                                                                       75 * math.floor(i/wp_per_row), 
                                                                       window = label, 
                                                                       anchor="nw", 
                                                                       width=150, 
                                                                       height=50)

    def configure_scrollregion(self, event=None):
        self.plot_frames()
        canvas_bbox = self._step_canvas.bbox("all")
        if canvas_bbox:
            self._step_canvas.config(width=canvas_bbox[2] - canvas_bbox[0], 
                                     height=canvas_bbox[3] - canvas_bbox[1] + 50)
        self.update_idletasks()

        # Get measurements
        mid_canvas_height = self._mid_canvas.winfo_height() 
        mid_height = self._mid.winfo_reqheight()
        mid_canvas_width = self._mid_canvas.winfo_width()
        mid_width = self._mid.winfo_reqwidth()
        window_height = self.winfo_height() - 50

        parent_bbox = self._parents_canvas.bbox("all")
        parents_height = parent_bbox[3] - parent_bbox[1] if parent_bbox is not None else 0

        children_bbox = self._children_canvas.bbox("all")
        children_height = children_bbox[3] - children_bbox[1] if children_bbox is not None else 0

        # Configure the parent canvas
        if parents_height <= window_height:
            parents_canvas_height = parents_height
            self._parents_scrollbar.pack_forget()
        else:
            parents_canvas_height = window_height
            self._parents_scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=25)
        self._parents_canvas.config(height=parents_canvas_height, scrollregion=(0,0,200, parents_height))

        # Configure the children canvas
        if children_height <= window_height:
            children_canvas_height = children_height
            self._children_scrollbar.pack_forget()
        else:
            children_canvas_height = window_height
            self._children_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=25, before=self._children_canvas)
        self._children_canvas.config(height=children_canvas_height, scrollregion=(0,0,200, children_height))

        # configure the scrollregion of the mid_canvas
        self._mid_canvas.itemconfig("mid", 
                                    width = mid_width if mid_width >= mid_canvas_width else mid_canvas_width)
        if mid_height >= mid_canvas_height and mid_width >= mid_canvas_width:
            self._mid_canvas.configure(scrollregion=(0,0,mid_width,mid_height))
        elif mid_height >= mid_canvas_height:
            self._mid_canvas.configure(scrollregion=(0,0,mid_canvas_width,mid_height))
        elif mid_width >= mid_canvas_width:
            self._mid_canvas.configure(scrollregion=(0,0,mid_width,mid_canvas_height))
        else:
            self._mid_canvas.configure(scrollregion=(0,0,mid_canvas_width,mid_canvas_height))


class WorkpackagePage(Page):

    """Page for the information of a specific workpackage (used parameters with values, environment variables, ...)"""

    def __init__(self, root, wp):
        super().__init__(root)
        self._wp = wp

        self._parents_arrow = tk.Canvas(self, 
                                        bg=WHITE, 
                                        borderwidth=0, 
                                        highlightthickness=0, 
                                        width=50)
        self._parents_canvas = tk.Canvas(self, 
                                         bg=WHITE, 
                                         borderwidth=0, 
                                         highlightthickness=0, 
                                         width=200)
        self._parents_scrollbar = tk.Scrollbar(self, 
                                               orient=tk.VERTICAL, 
                                               command=self._parents_canvas.yview)
        self._wp_frame = tk.LabelFrame(self, 
                                       text="Workpackage "+str(self._wp.id), 
                                       bg=GREY,
                                       font=("Arial", 11, "bold"))
        self._mid_canvas = tk.Canvas(self._wp_frame, 
                                     bg=GREY, 
                                     borderwidth=0, 
                                     highlightthickness=0, 
                                     width=250)
        self._mid = tk.Frame(self._mid_canvas, 
                             bg=GREY)
        self._mid_scrollbar_y = tk.Scrollbar(self._wp_frame, 
                                             orient=tk.VERTICAL, 
                                             command=self._mid_canvas.yview)
        self._mid_scrollbar_x = tk.Scrollbar(self._wp_frame, 
                                             orient=tk.HORIZONTAL, 
                                             command=self._mid_canvas.xview)
        self._step_frame_label = tk.Frame(self._mid, 
                                          bg=GREY)
        self._step_label = tk.Label(self._step_frame_label, 
                                    text="Step:", 
                                    bg=GREY, 
                                    padx=4)
        self._step_button = tk.Button(self._step_frame_label, 
                                      text=self._wp.step.name, 
                                      highlightbackground=BLUE, 
                                      bg=LIGHT_BLUE, 
                                      activebackground=BLUE, 
                                      activeforeground=WHITE, 
                                      cursor="hand2")
        self._status = tk.Canvas(self._step_frame_label, 
                                     bg=GREY, 
                                     borderwidth=0, 
                                     highlightthickness=0, 
                                     width=22,
                                     height=22)
        self._step_button.config(command=lambda: self.step_clicked(self._wp.step.name))
        self._step_tree = ttk.Treeview(self._mid, 
                                       selectmode="none", 
                                       show="tree", 
                                       style="Grey.Custom.Treeview", 
                                       height=2)
        self._param_label = tk.Label(self._mid, 
                                     text="\nParametersets:", 
                                     font=("Arial", 11, "bold"), 
                                     bg=GREY)
        self._param_notebook = ttk.Notebook(self._mid, 
                                            style="Grey.TNotebook")
        self._env_label = tk.Label(self._mid, 
                                   text="\nEnvironments:", 
                                   font=("Arial", 11, "bold"), 
                                   bg=GREY)
        columns = ["environment",
                   "value",
                   "env/nonenv"]
        self._env_tree = SortableTreeview(self._mid, 
                                          columns, 
                                          selectmode="none", 
                                          show="headings", 
                                          style = "Grey.Custom.Treeview")
        self._wp_separator = ttk.Separator(self._mid, 
                                           orient="horizontal")
        self._wp_label_siblings = tk.Label(self._mid, 
                                           text="Iteration Siblings:", 
                                           font=("Arial", 11, "bold"), 
                                           bg=GREY)
        self._wp_canvas = tk.Canvas(self._mid, 
                                    bg=GREY, 
                                    borderwidth=0, 
                                    highlightthickness=0)
        self._wp_frames = dict()
        self._children_arrow = tk.Canvas(self, 
                                         bg=WHITE, 
                                         borderwidth=0, 
                                         highlightthickness=0, 
                                         width=50)
        self._children_canvas = tk.Canvas(self, 
                                          bg=WHITE, 
                                          borderwidth=0, 
                                          highlightthickness=0, 
                                          width=200)
        self._children_scrollbar = tk.Scrollbar(self, 
                                                orient=tk.VERTICAL, 
                                                command=self._children_canvas.yview)
        
        self.config(bg=WHITE)
        self._x_stay = [self._children_arrow, 
                        self._parents_arrow, 
                        self._wp_canvas, 
                        self._parents_canvas, 
                        self._children_canvas]
        self._y_stay = [self._children_arrow, 
                       self._parents_arrow, 
                       self._wp_canvas]
        self.place_widgets()

    def place_widgets(self):
        """Place all the widgets inside the layout"""
        # pack the widgets for the parents region into the layout
        self.plot_parents()
        canvas_bbox = self._parents_canvas.bbox("all")
        if canvas_bbox:
            self._parents_arrow.create_line(0,10,25, 10, 
                                            arrow="last", 
                                            arrowshape=(16,20,6), 
                                            width=10)
            self._parents_arrow.config(height=20)
            self._parents_canvas.configure(yscrollcommand=self._parents_scrollbar.set)
        self._parents_canvas.pack(anchor="center", side="left", pady=25)
        self._parents_arrow.pack(anchor="center", side="left", pady=25)

        # pack the widgets for the children region into the layout
        self.plot_children()
        canvas_bbox = self._children_canvas.bbox("all")
        if canvas_bbox:
            self._children_arrow.create_line(25,10,50,10, 
                                             arrow="last", 
                                             arrowshape=(16,20,6), 
                                             width=10)
            self._children_arrow.config(height=20)
            self._children_canvas.configure(yscrollcommand=self._children_scrollbar.set)
        self._children_canvas.pack(anchor="center", side="right", pady=25)
        self._children_arrow.pack(anchor="center", side="right", pady=25)

        # pack the widgets for the mid region into the layout
        self._wp_frame.pack(anchor="center", fill = "both", side="right", expand="True", pady=25)
        self._mid_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self._mid_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self._mid_canvas.configure(yscrollcommand=self._mid_scrollbar_y.set)
        self._mid_canvas.configure(xscrollcommand=self._mid_scrollbar_x.set)
        self._mid_canvas.create_window((0,0), window=self._mid, anchor="nw", tags="mid")
        self._mid_canvas.pack(anchor="center", fill="both", expand="true")
        self.show_data()


        # pack the widgets for the step information into the layout
        self._step_frame_label.pack(anchor="w", fill="both")
        self._step_label.pack(side="left", anchor="center")
        self._step_button.pack(side='left', anchor="center")
        self._status.create_oval(1,1,21,21, fill=self._wp.status_color())
        self._status.pack(side='left', anchor="center", padx=(20,0))
        self._step_tree.pack(anchor="w", fill="both", expand="True")

        # pack the widgets for the parametersets into the layout and fill the notebook
        local_parameter = self._wp.local_parameterset.parameter_dict
        for wp in reversed(self._wp.parent_history):
            for parameter in wp.local_parameterset.parameter_dict.values():
                if parameter.name not in local_parameter:
                    local_parameter[parameter.name] = parameter
        parametersets = dict()
        for parameterset in self._wp.benchmark.parametersets.values():
            parameterlist = list()
            for parameter in parameterset.parameter_dict.values():
                if (parameter.name in local_parameter and 
                        parameter.is_equivalent(local_parameter[parameter.name])):
                    parameterlist.append(local_parameter[parameter.name])
            if len(parameterlist) != 0:
                parametersets[parameterset.name] = parameterlist
        
        if len(local_parameter) != 0:
            self._param_label.pack(anchor="w")
            for parameterset, parameter_list in sorted(parametersets.items(), 
                                                       key=lambda x: x[0]):
                tab = tk.Frame(self._param_notebook, 
                               bg=LIGHT_GREY, 
                               padx=10)
                label_duplicate = tk.Label(tab, 
                                           text = "duplicate: " + 
                                                  f"{self._wp.benchmark.parametersets[parameterset].duplicate!r}", 
                                                  bg=LIGHT_GREY)
                columns = ["parameter",
                           "selection",
                           "idx",
                           "value",
                           "mode",
                           "type",
                           "separator",
                           "export",
                           "unit",
                           "update_mode",
                           "duplicate"]
                param_table = SortableTreeview(tab, 
                                               columns, 
                                               selectmode="none", 
                                               show="headings", 
                                               height=len(parameter_list), 
                                               style="LightGrey.Custom.Treeview")
                for parameter in parameter_list:
                    param_table.insert("","end",values=[parameter.name, 
                                                        parameter.value, 
                                                        parameter.idx if parameter.idx else 0, 
                                                        parameter.based_on_value,
                                                        parameter.based_on_mode, 
                                                        parameter.type, 
                                                        parameter.separator, 
                                                        parameter.export, 
                                                        parameter.unit, 
                                                        parameter.update_mode, 
                                                        parameter.duplicate])
                label_duplicate.pack(anchor="w")
                param_table.pack(fill="both", expand="True", pady = 10)
                self._param_notebook.add(tab, 
                                         text = self._wp.benchmark.parametersets[parameterset].name)
            self._param_notebook.pack(fill="both", padx=25)
        
        # pack the widgets for the environments into the layout
        if len(self._wp.env)+len(self._wp.nonenv) != 0:
            self._env_label.pack(anchor="w")
            self._env_tree.config(height = len(self._wp.env)+len(self._wp.nonenv))
            self._env_tree.pack(fill="both", expand=True, padx=25, pady=10)

        # pack the widgets for the iteration siblings into the layout
        if len(self._wp.iteration_siblings) > 1:
            self._wp_separator.pack(fill="x", padx=25, pady=25)
            self._wp_label_siblings.pack(anchor="w")
            self.plot_frames()
            canvas_bbox = self._wp_canvas.bbox("all")
            if canvas_bbox:
                self._wp_canvas.config(width=canvas_bbox[2] - canvas_bbox[0], 
                                       height=canvas_bbox[3] - canvas_bbox[1] + 50)
            self._wp_canvas.pack(anchor="w", expand="True", padx=25)

    def plot_parents(self):
        """Plot the parent workpackages into the parent canvas"""
        for i, wp in enumerate(self._wp.parents):
            label = tk.Button(self._parents_canvas, 
                              text="Workpackage "+str(wp.id), 
                              highlightbackground=BLUE, 
                              activebackground=BLUE, 
                              activeforeground=WHITE, 
                              cursor="hand2", 
                              bg=wp.status_color())
            self.bind_widget(label, self.wp_clicked, wp.id)
            self._wp_frames[wp.id] = self._parents_canvas.create_window(25, 75 * i , 
                                                                        window = label, 
                                                                        anchor="nw", 
                                                                        width=150, 
                                                                        height=50)

    def plot_children(self):
        """Plot the dependent workpackages into the children canvas"""
        for i, wp in enumerate(self._wp.children):
            label = tk.Button(self._children_canvas, 
                              text="Workpackage "+str(wp.id), 
                              highlightbackground=BLUE, 
                              activebackground=BLUE, 
                              activeforeground=WHITE, 
                              cursor="hand2", 
                              bg=wp.status_color())
            self.bind_widget(label, self.wp_clicked, wp.id)
            self._wp_frames[wp.id] = self._children_canvas.create_window(25, 75 * i , 
                                                                         window = label, 
                                                                         anchor="nw", 
                                                                         width=150, 
                                                                         height=50)

    def show_data(self):
        """Fills the treeviews with data"""
        self._step_tree.insert("", "end", text = "iteration: "+ f"{self._wp.iteration!r}")
        self._step_tree.insert("", "end", text = "cycle: "+ f"{self._wp.cycle!r}")
        for name, value in self._wp.env.items():
            self._env_tree.insert("","end",values=[name, 
                                                   value, 
                                                   "env"])
        for name in self._wp.nonenv:
            self._env_tree.insert("","end",values=[name, "", "nonenv"])

    def plot_frames(self):
        """Plots the iteration siblings of the current workpackage in the wp_canvas"""
        wp_per_row = math.floor((self._mid_canvas.winfo_width()-50)/175)
        if wp_per_row == 0: wp_per_row += 1
        self._wp_canvas.delete("all")
        for i, wp in enumerate([wp for wp in self._wp.iteration_siblings if wp.id != self._wp.id]):
            label = tk.Button(self._wp_canvas, 
                              text="Workpackage "+str(wp.id), 
                              highlightbackground=BLUE, 
                              activebackground=BLUE, 
                              activeforeground=WHITE, 
                              cursor="hand2", 
                              bg=wp.status_color())
            self.bind_widget(label, self.wp_clicked, wp.id)
            column = i%wp_per_row
            self._wp_frames[wp.id] = self._wp_canvas.create_window(175 * column, 
                                                                   75 * math.floor(i/wp_per_row), 
                                                                   window = label, 
                                                                   anchor="nw", 
                                                                   width=150, 
                                                                   height=50)
    
    def configure_scrollregion(self, event=None):
        self.plot_frames()
        canvas_bbox= self._wp_canvas.bbox("all")
        if canvas_bbox:
            self._wp_canvas.config(width=canvas_bbox[2] - canvas_bbox[0], 
                                   height=canvas_bbox[3] - canvas_bbox[1] + 50)
        self.update_idletasks()

        # Get measurements
        mid_canvas_height = self._mid_canvas.winfo_height() 
        mid_height = self._mid.winfo_reqheight()
        mid_canvas_width = self._mid_canvas.winfo_width()
        mid_width = self._mid.winfo_reqwidth()
        window_height = self.winfo_height() - 50

        parent_bbox = self._parents_canvas.bbox("all")
        parents_height = parent_bbox[3] - parent_bbox[1] if parent_bbox is not None else 0

        children_bbox = self._children_canvas.bbox("all")
        children_height = children_bbox[3] - children_bbox[1] if children_bbox is not None else 0
        
        # Configure the parent canvas
        if parents_height <= window_height:
            parents_canvas_height = parents_height
            self._parents_scrollbar.pack_forget()
        else:
            parents_canvas_height = window_height
            self._parents_scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=25)
        self._parents_canvas.config(height=parents_canvas_height, scrollregion=(0,0,200, parents_height))
        
        # Configure the children canvas
        if children_height <= window_height:
            children_canvas_height = children_height
            self._children_scrollbar.pack_forget()
        else:
            children_canvas_height = window_height
            self._children_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=25, before=self._children_canvas)
        self._children_canvas.config(height=children_canvas_height, scrollregion=(0,0,200, children_height))

        # configure the scrollregion of the mid_canvas
        self._mid_canvas.itemconfig("mid", 
                                    width = mid_width if mid_width >= mid_canvas_width else mid_canvas_width)
        if mid_height >= mid_canvas_height and mid_width >= mid_canvas_width:
            self._mid_canvas.configure(scrollregion=(0,0,mid_width,mid_height))
        elif mid_height >= mid_canvas_height:
            self._mid_canvas.configure(scrollregion=(0,0,mid_canvas_width,mid_height))
        elif mid_width >= mid_canvas_width:
            self._mid_canvas.configure(scrollregion=(0,0,mid_width,mid_canvas_height))
        else:
            self._mid_canvas.configure(scrollregion=(0,0,mid_canvas_width,mid_canvas_height))
            