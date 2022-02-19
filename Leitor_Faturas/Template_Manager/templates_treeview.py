import tkinter as tk
from tkinter import ttk
from .utils import NORM_FONT, admissible_var_description


class TemplatesTreeview(ttk.Treeview):

    def __init__(self, parent, **kwargs):

        columns = ('x1', 'y1', 'x2', 'y2', 'var_description')
        cols_text = ('X1', 'Y1', 'X2', 'Y2', 'Descrição Variável')
        col_width = (80, 80, 80, 80, 150)

        ttk.Treeview.__init__(self, master=parent, columns=columns, selectmode='browse', **kwargs)

        self.tv_cols = columns
        self.n_rows = 1

        self.heading(column="#0", text="", anchor="center")
        self.column(column="#0", stretch=0, width=0)

        for i, col in enumerate(self.tv_cols):
            self.heading(col, text=cols_text[i], anchor="c")
            self.column(column=columns[i], width=col_width[i], minwidth=col_width[i] - 20, stretch=0, anchor="center")

        self.bind('<Button-1>', self.select_record)
        self.bind('<Escape>', self.remove_tree_selection)
        self.bind('<Delete>', self.delete_selection)

    def delete_selection(self, event):
        if self.focus():
            row_idx = self.index(self.focus())
            self.delete(self.focus())
            if row_idx - 1 >= 0:
                self.selection_set(self.get_children("")[row_idx - 1])
            elif self.get_children(""):
                self.selection_set(self.get_children("")[0])

    def edit_row(self, roi_line, row_idx):
        """method used to edit row of treeview"""
        row_id = list(self.get_children(""))[row_idx]
        for k, col in enumerate(self.tv_cols):
            self.set(row_id, column=col, value=roi_line[k])
        return

    def edit_row_tag(self):
        """method used to re-tag exisiting rows"""
        for k, row in enumerate(self.get_children("")):
            if k % 2 == 0:
                self.item(row, tags=('evenrow',))
            else:
                self.item(row, tags=('oddrow',))

    @staticmethod
    def remove_tree_selection(event):
        tv = event.widget
        if len(tv.selection()) > 0:
            tv.selection_remove(tv.selection()[0])

    def select_record(self, event):
        # Select Record
        if self.focus():
            self.item(self.focus(), 'values')

    def set_cell_value(self, event, parent, roi, parent_frame):
        """ Method that takes the Double click to enter the edit state on a given row entry"""
        item = self.selection()
        t_col = self.identify_column(event.x)  # column
        t_row = self.identify_row(event.y)  # row
        # get upper-left corner coordinates of tree
        tree_x = parent_frame.winfo_x()
        tree_y = parent_frame.winfo_y() + self.winfo_y()

        # convert iid to row/column number
        row_number = list(self.get_children("")).index(t_row) if t_row else None
        col_number = int(str(t_col).replace("#", "")) if t_col else None

        def save_edit_combobox(event):
            self.set(item, column=t_col, value=combo_list.get())
            parent.roi[row_number][col_number - 1] = combo_list.get()  # modify roi variable descrition with user change
            parent.roi[row_number][col_number - 3] = admissible_var_description[combo_list.get()][0]  # change var type
            parent.roi[row_number][col_number - 2] = admissible_var_description[combo_list.get()][1]  # change var name
            # destroy combobox entry
            combo_list.destroy()

        def save_edit_spinbox(event):
            self.set(item, column=t_col, value=float(spinbox_var.get()))
            # modify roi row coordinates with user change
            parent.roi[row_number][col_number - 1] = float(spinbox_var.get())
            spinbox.destroy()

        def update_rectangle_coords(a, b, c):
            rectangle = parent.rectangles_list[row_number]
            x1, y1, x2, y2 = parent.canvas.coords(rectangle)
            if not spinbox_var.get():
                return
            try:
                if col_number == 1:
                    parent.canvas.coords(rectangle, int(float(spinbox_var.get()) * parent.img_width), y1, x2, y2)
                elif col_number == 2:
                    parent.canvas.coords(rectangle, x1, int(float(spinbox_var.get()) * parent.img_height), x2, y2)
                elif col_number == 3:
                    parent.canvas.coords(rectangle, x1, y1, int(float(spinbox_var.get()) * parent.img_width), y2)
                elif col_number == 4:
                    parent.canvas.coords(rectangle, x1, y1, x2, int(float(spinbox_var.get()) * parent.img_height))
            except ValueError:
                return
            return

        # create local coordinate to situate the entry text box
        x_loc = tree_x + event.x + 10
        y_loc = event.y + tree_y
        if t_col and t_row and col_number == 5:
            combo_list = ttk.Combobox(parent, value=list(admissible_var_description.keys()),
                                      font=NORM_FONT, state="readonly")
            combo_list.current(0)
            combo_list.place(x=x_loc, y=y_loc, anchor="nw")
            combo_list.bind("<<ComboboxSelected>>", save_edit_combobox)
            combo_list.bind("<Return>", save_edit_combobox)
            combo_list.bind("<FocusOut>", save_edit_combobox)
            combo_list.bind("<Escape>", lambda e: combo_list.destroy())
            combo_list.bind("<Leave>", lambda e: combo_list.destroy())

        elif t_col and t_row:
            spinbox_var = tk.StringVar(value=self.item(item, "values")[col_number - 1])
            spinbox = ttk.Spinbox(parent, format="%.4f", increment=0.0001, from_=0.0000, to=1.0000,
                                  textvariable=spinbox_var, wrap=True, font="Verdana 9", width=8)
            spinbox.place(x=x_loc, y=y_loc, anchor="nw")
            spinbox.bind("<Return>", save_edit_spinbox)
            spinbox.bind("<FocusOut>", save_edit_spinbox)
            spinbox.bind("<Escape>", lambda e: spinbox.destroy())
            spinbox.bind("<Leave>", lambda e: spinbox.destroy())
            spinbox_var.trace('w', update_rectangle_coords)
        else:
            self.focus_set()
