from tkinter import ttk
from jube.conf import BLUE, LIGHT_BLUE, GREY, LIGHT_GREY, WHITE, BLACK

class SortableTreeview(ttk.Treeview):
    """
    A Treeview in whose columns are sortable

    Attributes
    -----------
    columns: List[str]
    sort_column: str
    heading_clicked: Boolean

    Methods
    ------------
    sort_by_column(col, descending)
    on_header_click(event)
    insert(*args, **kwargs)
    add_tags()
    on_heading_motion(event)
    """
    def __init__(self, parent, columns, *args, **kwargs):
        """
        Constructs a sortable treeview

        Parameters
        -----------
        parent: tk.Widget
        columns: List[str]
        *args
        **kwargs
        """
        super().__init__(parent, columns=columns, *args, **kwargs)
        self.columns = columns
        for col in self.columns:
            self.heading(col, text=col)
            self.column(col, width=125, anchor="w")
        self.sort_column = self.columns[0]
        self.heading_clicked = True
        self.bind("<Button-1>", self.on_header_click)
        self.bind("<Motion>", self.on_heading_motion)

    def sort_by_column(self, col, descending=False):
        """
        Sorts the data in col descending/ascending

        Parameters
        -----------
        col: str
        descending: Boolean
        """
        data = [(self.set(child, col), child) for child in self.get_children('')]
        data.sort(reverse=not descending, key=lambda x: x[0][1:-1] if x[0] else x[0])
        for index, (val, child) in enumerate(data):
            self.move(child, '', index)
        self.sort_column = col

        for column in self.columns:
            if column == col:
                if descending:
                    self.heading(column, text=str(column)+"   ▾")
                else:
                    self.heading(column, text=str(column)+"   ▴")
            else:
                self.heading(column, text=str(column))

    def on_header_click(self, event):
        """
        Event Handler that is used if the user clicks on a heading to sort the data by a column

        Parameters
        -----------
        event: tk.Event
        """
        region = self.identify_region(event.x, event.y)
        if region == "heading":
            col = self.identify_column(event.x)
            if col:
                col = self.columns[int(col.lstrip('#')) - 1]
                if self.sort_column == col and self.heading_clicked:
                    self.heading_clicked = False
                    self.sort_by_column(col, self.heading_clicked)
                else:
                    self.heading_clicked = True
                    self.sort_by_column(col, self.heading_clicked)
        self.add_tags()

    def insert(self, *args, **kwargs):
        """
        Inserts a new row into the treeview
        """
        iid = super().insert(*args, **kwargs)
        self.sort_by_column(self.sort_column, self.heading_clicked)
        self.add_tags()
        return iid

    def add_tags(self):
        """
        Creates alternating row colors
        """
        if self["style"] == "Custom.Treeview":
            self.tag_configure("even", background = LIGHT_GREY)
            self.tag_configure("odd", background = GREY)
        elif self["style"] == "Grey.Custom.Treeview":
            self.tag_configure("even", background = LIGHT_GREY)
            self.tag_configure("odd", background = WHITE)
        else:
            self.tag_configure("even", background = WHITE)
            self.tag_configure("odd", background = GREY)

        for i, child_iid in enumerate(self.get_children()):
            if i % 2 == 0:
                self.item(child_iid, tags = "even")
            else:
                self.item(child_iid, tags = "odd")

    def on_heading_motion(self, event):
        """
        Event Handler that is used if the user hovers the mouse over the treeview

        Parameters
        -----------
        event: tk.Event
        """
        if self.identify_region(event.x, event.y) == "heading":
            self.config(cursor="hand2")
        else:
            self.config(cursor="")