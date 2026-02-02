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
"""The Gui class manages the visualization of benchmark data"""

import tkinter as tk
from tkinter import ttk
import jube.gui.pages as page
from jube.conf import BLUE, LIGHT_BLUE, GREY, LIGHT_GREY, WHITE


class Gui(tk.Tk):

    """The Gui displays all information of a benchmark."""

    def __init__(self, benchmark):
        super().__init__()
        self._benchmark = benchmark

        # Create necessary widgets
        self._top = tk.Frame(self, bg=BLUE)
        self._labelTop = tk.Label(self._top,
                                  text=self._benchmark.name,
                                  bg=BLUE,
                                  fg=WHITE,
                                  font=("Arial", 12))
        self._button_back = tk.Button(self._top,
                                      text="Main",
                                      command=self.open_main_page,
                                      bg=LIGHT_BLUE,
                                      bd=0,
                                      highlightthickness=0,
                                      activebackground=BLUE,
                                      activeforeground=WHITE,
                                      cursor="hand2",
                                      font=("Arial", 12))
        self._labelBottom = tk.Label(self,
                                     text="JUBE-Version: "+self._benchmark.version,
                                     bg=BLUE,
                                     fg=WHITE,
                                     font=("Arial", 12))
        self._canvas = tk.Canvas(self,
                                 bg=WHITE,
                                 highlightthickness=0)
        self._scrollbar_y = tk.Scrollbar(self,
                                         orient="vertical",
                                         command=self._canvas.yview)
        self._main_frame = page.MainPage(self._canvas, self._benchmark)

        # Configure gui options
        self.title("JUBE")
        self.option_add("*Font", "Arial 11")
        self.minsize(width=self._top.winfo_reqwidth() if self._top.winfo_reqwidth() > 800 else 800,
                     height=400)

        # Configure the style of ttk Widgets
        self._style = ttk.Style()
        self._style.theme_use("clam")

        # Configure the style for a ttk.Treeview
        self._style.map("Treeview.Heading",
                        background=[("pressed", "!focus", LIGHT_BLUE),
                                    ("active", LIGHT_BLUE),
                                    ("disabled", LIGHT_BLUE)])
        self._style.layout("Custom.Treeview",
                           [("Treeview.treearea", {"sticky": "nswe"})])
        self._style.configure("Custom.Treeview.Heading",
                              background=LIGHT_BLUE,
                              activebackground=LIGHT_BLUE,
                              bordercolor=BLUE,
                              font=("Arial", 11))
        self._style.configure("Grey.Custom.Treeview",
                              background=GREY)
        self._style.configure("LightGrey.Custom.Treeview",
                              background=LIGHT_GREY)

        # Configure the style for a ttk.Notebook
        self._style.configure("TNotebook",
                              background=WHITE,
                              bordercolor="grey")
        self._style.configure("TNotebook.Tab",
                              background=GREY,
                              bordercolor="grey",
                              font=("Arial", 11, "bold"))
        self._style.map("TNotebook.Tab",
                        background=[("selected", WHITE)])
        self._style.configure("Grey.TNotebook",
                              background=GREY,
                              bordercolor="grey")
        self._style.configure("Grey.TNotebook.Tab",
                              background=GREY,
                              bordercolor="grey",
                              font=("Arial", 11))
        self._style.map("Grey.TNotebook.Tab",
                        background=[("selected", LIGHT_GREY)])

        self.place_widgets()

    def place_widgets(self):
        """Places all tkinter widgets in the gui layout"""
        self.bind("<Configure>", self.configure_scrollregion)
        self._top.pack(fill="x")
        self._labelTop.pack(side="right", fill="both", expand="True")
        self._button_back.pack(side="left", fill="both")
        self._labelBottom.pack(fill="x", side="bottom")
        self._scrollbar_y.pack(side="right", fill="y")
        self._canvas.configure(yscrollcommand=self._scrollbar_y.set)
        self._canvas.create_window((0, 0),
                                   window=self._main_frame,
                                   anchor="nw",
                                   tags="main")
        self._canvas.pack(side="left", fill="both", expand=True)

    def configure_scrollregion(self, event=None):
        """Event Handler that is used if the the window size is changed.
        It configures the scrollregion so that the scrollbars work properly"""
        self.minsize(width=self._top.winfo_reqwidth() if self._top.winfo_reqwidth() > 800 else 800,
                     height=400)
        main_height = self._main_frame.winfo_reqheight()
        canvas_height = self._canvas.winfo_height()
        canvas_width = self._canvas.winfo_width()

        # Configure height of the main page
        if not isinstance(self._main_frame, page.MainPage):
            main_height = canvas_height
        self._canvas.itemconfig("main",
                                width=canvas_width,
                                height=canvas_height if canvas_height >= main_height else main_height)

        # Configure the height of the canvas and the scrollregion of its scrollbars
        if main_height > canvas_height:
            self._canvas.configure(scrollregion=(
                0, 0, canvas_width, main_height))
            self._scrollbar_y.pack(side="right", fill="y")
        else:
            self._canvas.configure(scrollregion=(
                0, 0, canvas_width, canvas_height))
            self._scrollbar_y.pack_forget()

    def open_step_page(self, name):
        """Opens a new step page"""
        self._canvas.delete("all")
        for step in self._benchmark.steps.values():
            if name == step.name:
                self._main_frame = page.StepPage(
                    self._canvas, step, self._benchmark)
                self._canvas.create_window((0, 0),
                                           window=self._main_frame,
                                           anchor="nw",
                                           tags="main")
                self.configure_scrollregion()
                break

    def open_wp_page(self, iid):
        """Opens a new workpackage page"""
        self._canvas.delete("all")
        for wp in [wp for wplist in self._benchmark.workpackages.values() for wp in wplist]:
            if iid == wp.id:
                self._main_frame = page.WorkpackagePage(self._canvas, wp)
                self._canvas.create_window((0, 0),
                                           window=self._main_frame,
                                           anchor="nw",
                                           tags="main")
                self.configure_scrollregion()
                break

    def open_main_page(self):
        """Opens the main page"""
        self._canvas.delete("all")
        self._main_frame = page.MainPage(self._canvas, self._benchmark)
        self._canvas.create_window((0, 0),
                                   window=self._main_frame,
                                   anchor="nw",
                                   tags="main")
        self.configure_scrollregion()
