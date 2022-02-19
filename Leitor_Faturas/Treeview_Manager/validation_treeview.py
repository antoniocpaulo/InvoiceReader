import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from ..Tkinter_Addins.TooltipHover import CreateToolTip

# define font types and sizes to be used by the app
LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)


def treeview_sort_column(tv, col, reverse):  # Treeview, column name, arrangement
    temp_list = [(tv.set(k, col), k) for k in tv.get_children('')]
    temp_list.sort(reverse=reverse)  # Sort by
    # rearrange items in sorted positions
    for index, (val, k) in enumerate(temp_list):  # based on sorted index movement
        tv.move(k, '', index)
        tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
        # Rewrite the title to make it the title of the reverse order
    change_row_tags(tv)


def change_row_tags(tv):
    """ change the tag when a row is shifted"""
    for k, row in enumerate(tv.get_children("")):
        if k % 2 == 0:
            tv.item(row, tags=('evenrow',))
        else:
            tv.item(row, tags=('oddrow',))


def bDown_Shift(event):
    """ shift more than one row down using mouse drag movement"""
    tv = event.widget
    select = [tv.index(s) for s in tv.selection()]
    select.append(tv.index(tv.identify_row(event.y)))
    select.sort()
    for i in range(select[0], select[-1] + 1, 1):
        tv.selection_add(tv.get_children()[i])

    change_row_tags(tv)


def bDown(event):
    """ shift one row down using mouse drag movement"""
    tv = event.widget
    if tv.identify_row(event.y) not in tv.selection():
        tv.selection_set(tv.identify_row(event.y))
        change_row_tags(tv)


def bUp(event):
    """ shift one row up using mouse drag movement"""
    tv = event.widget
    if tv.identify_row(event.y) in tv.selection():
        tv.selection_set(tv.identify_row(event.y))
        change_row_tags(tv)


def bUp_Shift(event):
    pass


def bMove(event):
    """ shift one row down using mouse drag movement"""
    tv = event.widget
    moveto = tv.index(tv.identify_row(event.y))
    for s in tv.selection():
        tv.move(s, '', moveto)
    change_row_tags(tv)


def remove_tree_selection(event):
    tv = event.widget
    if len(tv.selection()) > 0:
        tv.selection_remove(tv.selection()[0])


class DisableMixin(object):
    """ Class used to enable or disable treeview (or any other widget assuming
    it has the "state" method) status"""

    def __init__(self, **kwargs):
        super().__init__(self)
        self.bindtags = None
        self.tags = None

    def state(self, statespec=None):
        if statespec:
            e = super().state(statespec)
            if 'disabled' in e:
                self.bindtags(self.tags)
            elif '!disabled' in e:
                self.tags = self.bindtags()
                self.bindtags([None])
            return e
        else:
            return super().state()

    def disable(self):
        self.state(('disabled',))

    def enable(self):
        self.state(('!disabled',))

    def is_disabled(self):
        return 'disabled' in self.state()

    def is_enabled(self):
        return not self.is_disabled()


class ValidationTreeview(DisableMixin, ttk.Treeview):

    def __init__(self, parent, columns=None, col_count=0, row_count=0, main_path="", **kwargs):
        """ sub-class of treeview used in the validation frame of the GUI with specific methods
        as: add/delete rows, add/remove specific cells, shift/drag rows and cells"""
        ttk.Treeview.__init__(self, parent, columns=columns, **kwargs)
        self._master = parent
        self._tv_cols = columns
        self._t_col = None

        self.heading(column="#0", text="", anchor='w')
        self.column(column="#0", stretch=0, width=0)
        for i in self._tv_cols:
            self.heading(column=str(i), text=str(i), anchor='center')
            self.column(column=str(i), stretch=0, width=100, minwidth=80)

        for col in self._tv_cols:  # bind function to make the header sortable
            self.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self, _col, False))

        # add buttons images
        self.new_button_img = ImageTk.PhotoImage(Image.open(
            main_path + r"\bin\aux_img\add.png").resize((25, 25), Image.LANCZOS))
        self.up_img = ImageTk.PhotoImage(Image.open(
            main_path + r"\bin\aux_img\up.png").resize((25, 25), Image.LANCZOS))
        self.down_img = ImageTk.PhotoImage(Image.open(
            main_path + r"\bin\aux_img\down.png").resize((25, 25), Image.LANCZOS))
        self.del_row_img = ImageTk.PhotoImage(Image.open(
            main_path + r"\bin\aux_img\minus.png").resize((25, 25), Image.LANCZOS))
        self.up_cell_img = ImageTk.PhotoImage(Image.open(
            main_path + r"\bin\aux_img\up.png").resize((25, 25), Image.LANCZOS))
        self.down_cell_img = ImageTk.PhotoImage(Image.open(
            main_path + r"\bin\aux_img\down.png").resize((25, 25), Image.LANCZOS))
        self.add_cell_img = ImageTk.PhotoImage(Image.open(
            main_path + r"\bin\aux_img\add.png").resize((25, 25), Image.LANCZOS))
        self.del_cell_img = ImageTk.PhotoImage(Image.open(
            main_path + r"\bin\aux_img\minus.png").resize((25, 25), Image.LANCZOS))

        self._buttons_frame = tk.Frame(parent, bg="white")
        self._buttons_frame.columnconfigure(0, weight=1)
        self._labelframe_row = tk.LabelFrame(self._buttons_frame, text="Linhas:", background="white",
                                             font=SMALL_FONT, labelanchor="nw")
        self._labelframe_cells = tk.LabelFrame(self._buttons_frame, text="Células:", background="white",
                                               font=SMALL_FONT, labelanchor="nw")

        new_row_btn = tk.Button(self._labelframe_row, image=self.new_button_img, relief="flat", bg="white",
                                command=self.add_new_row)
        delete_button = tk.Button(self._labelframe_row, image=self.del_row_img, relief="flat", bg="white",
                                  command=self.delete_row)
        up_row_btn = tk.Button(self._labelframe_row, image=self.up_img, relief="flat", bg="white",
                               command=lambda: self.shift_row_up_or_down("up"))
        down_row_btn = tk.Button(self._labelframe_row, image=self.down_img, relief="flat", bg="white",
                                 command=lambda: self.shift_row_up_or_down("down"))
        empty_lbl = tk.Label(self._buttons_frame, text="", bg="white")
        new_cell_btn = tk.Button(self._labelframe_cells, image=self.add_cell_img, relief="flat", bg="white",
                                 command=lambda: self.add_delete_cell_and_shift_row("add"))
        del_cell_btn = tk.Button(self._labelframe_cells, image=self.del_cell_img, relief="flat", bg="white",
                                 command=lambda: self.add_delete_cell_and_shift_row("delete"))
        up_cell_btn = tk.Button(self._labelframe_cells, image=self.up_cell_img, relief="flat", bg="white",
                                command=lambda: self.shift_cell_up_or_down("up"))
        down_cell_btn = tk.Button(self._labelframe_cells, image=self.down_cell_img, relief="flat", bg="white",
                                  command=lambda: self.shift_cell_up_or_down("down"))

        self._buttons_frame.grid(column=col_count, row=row_count + 2, columnspan=2, sticky="nsew")
        empty_lbl.grid(row=0, column=0, sticky="nsew")
        self._labelframe_row.grid(row=0, column=1, padx=10, pady=5)
        self._labelframe_cells.grid(row=0, column=2, padx=10, pady=5)

        new_row_btn.grid(row=0, column=0, pady=5, sticky="se")
        delete_button.grid(row=0, column=1, pady=5, sticky="se")
        up_row_btn.grid(row=0, column=2, pady=5, sticky="se")
        down_row_btn.grid(row=0, column=3, pady=5, sticky="se")

        new_cell_btn.grid(row=0, column=0, pady=5, sticky="se")
        del_cell_btn.grid(row=0, column=1, pady=5, sticky="se")
        up_cell_btn.grid(row=0, column=2, pady=5, sticky="se")
        down_cell_btn.grid(row=0, column=3, pady=5, sticky="se")

        CreateToolTip(new_row_btn, text="Adicionar nova linha")
        CreateToolTip(delete_button, text="Remover linha seleccionada")
        CreateToolTip(up_row_btn, text="Mover linha para cima")
        CreateToolTip(down_row_btn, text="Mover linha para baixo")
        CreateToolTip(new_cell_btn, text="Adicionar nova célula")
        CreateToolTip(del_cell_btn, text="Remover célula")
        CreateToolTip(up_cell_btn, text="Mover célula para cima")
        CreateToolTip(down_cell_btn, text="Mover célula para baixo")

        # Bind user interactions to tree
        self.bind('<Escape>', remove_tree_selection)
        self.bind('<Button-1>', self.select_record)
        # Double-click or space the left button to enter the edit
        self.bind('<Double-1>', self.set_cell_value)
        self.bind('<space>', self.set_cell_value)
        # Select next/previous row
        self.bind("<Up>", lambda event: self.select_previous_next_row(event, "up"))
        self.bind("<Down>", lambda event: self.select_previous_next_row(event, "down"))

        self.bind("<ButtonPress-3>", bDown)
        self.bind("<ButtonRelease-3>", bUp, add='+')
        self.bind("<B3-Motion>", bMove, add='+')
        self.bind("<Shift-ButtonPress-3>", bDown_Shift, add='+')
        self.bind("<Shift-ButtonRelease-3>", bUp_Shift, add='+')

    def set_cell_value(self, event):
        """ Method that takes the Double click to enter the edit state on a given row entry"""
        t_col = ""
        item = None
        for item in self.selection():
            t_col = self.identify_column(event.x)  # column
        # get upper-left corner coordinates of tree
        tree_x = self.winfo_x()
        tree_y = self.winfo_y()

        def save_edit(event):
            if int(str(t_col).replace("#", "")) > 1:
                try:
                    result = format(float(entry_edit.get()), ".2f")
                except ValueError:
                    result = entry_edit.get()
            else: 
                result = entry_edit.get()
            self.set(item, column=t_col, value=result)
            entry_edit.destroy()
            self.focus_set()

        # create local coordinate to situate the entry text box
        x_loc = event.x + 10
        y_loc = event.y + tree_y
        if t_col:
            initial_text = self.item(item, "values")[int(str(t_col).replace("#", "")) - 1]
            entry_edit = tk.Entry(self.master, font=SMALL_FONT)
            entry_edit.insert(0, initial_text)
            entry_edit.focus_set()
            entry_edit.selection_range(0, tk.END)
            if x_loc + 80 > tree_x + self.winfo_width():
                entry_edit.place(x=x_loc - 90, y=y_loc, width=80, height=20, bordermode="outside", anchor="nw")
            else:
                entry_edit.place(x=x_loc, y=y_loc, width=80, height=20, bordermode="outside", anchor="nw")
            entry_edit.bind("<Return>", save_edit)
            entry_edit.bind("<Escape>", lambda e: entry_edit.destroy())
            entry_edit.bind("<FocusOut>", save_edit)

    def select_record(self, event):
        # Select Record
        self.focus()
        # define the number of the column selected
        self._t_col = int(str(self.identify_column(event.x)).replace("#", "")) - 1

    def add_new_row(self):
        """ add a new row to the treeview"""
        new_values = ['a alterar' for _ in self._tv_cols]
        if self.selection():
            # if selection exists, then get the number of the selected row, to add new row over it
            n_rows = self.get_children("").index(self.selection()[0])
        else:
            # if no selection is made, then add at top if no child, or at the bottom
            if len(self.get_children("")) == 0:
                n_rows = 0
            else:
                n_rows = len(self.get_children("")) - 1
        new_values = tuple(new_values)
        if len(self.get_children("")) % 2 == 0:
            self.insert('', n_rows, values=new_values, tags=('evenrow',))
        else:
            self.insert('', n_rows, values=new_values, tags=('oddrow',))
        if len(self.selection()) > 0:
            self.selection_remove(self.selection()[0])

    def delete_row(self):
        """ method used to delete the selected row/s of the tree"""
        if self:
            if self.selection():
                for record in self.selection():
                    row_idx = self.index(record)
                    self.delete(record)
                    if row_idx - 1 >= 0:
                        self.selection_set(self.get_children("")[row_idx - 1])
                    elif self.get_children(""):
                        self.selection_set(self.get_children("")[0])
                    else:
                        pass

    def delete_old_treeview_for_modified(self, old_treeview, n_rows):
        # delete all "old" treeview entries
        self.delete(*self.get_children())
        for i in range(0, n_rows):
            tree_row = [sub_list[i] for sub_list in old_treeview]
            new_values = tuple(tree_row)
            if i % 2 == 0:
                self.insert('', n_rows, values=new_values, tags=('evenrow',))
            else:
                self.insert('', n_rows, values=new_values, tags=('oddrow',))
            n_rows += 1
        return

    def add_delete_cell_and_shift_row(self, action="add"):
        """ method used to add or remove cell and shift the remaining column cells accordingly"""
        if self.selection():
            # if selection exists, then get the number of the selected row to add new cell
            old_tv = [[self.item(row, 'values')[col] for row in self.get_children("")]
                      for col in range(0, len(self._tv_cols))]
            curItem = self.selection()
            row_idx = self.index(curItem)
            max_rows = len(self.get_children(""))
            if action == "add":
                # add "" empty item to fill last tree row, so that all columns are of the same size
                for k in range(0, len(old_tv)):
                    if k != self._t_col:
                        old_tv[k].insert(max_rows, "")
                    else:
                        # insert item to sublist of selected column
                        old_tv[k].insert(row_idx, "a alterar")
                max_rows += 1
                row_idx += 1
            elif action == "delete":
                for k in range(0, len(old_tv)):
                    if k == self._t_col:
                        old_tv[k].pop(row_idx)
                        old_tv[k].insert(max_rows, "")
                row_idx -= 1
            # call function to substitute old treeview by new one
            self.delete_old_treeview_for_modified(old_tv, max_rows)
            self.selection_set(self.get_children("")[row_idx])
        return

    def select_previous_next_row(self, event, up_or_down="up"):
        """method used to select previous or next row"""
        if self:
            if self.selection():
                row_idx = self.index(self.selection())
                if up_or_down == "up" and row_idx - 1 >= 0:
                    self.selection_set(self.get_children("")[row_idx - 1])
                elif up_or_down == "down" and row_idx + 1 <= len(self.get_children("")):
                    self.selection_set(self.get_children("")[row_idx + 1])
        return

    def shift_row_up_or_down(self, up_or_down="up"):
        """ shift entire row up or down with button"""
        if self:
            rows = self.selection()
            if up_or_down == "up":
                for row in rows:
                    self.move(row, self.parent(row), self.index(row) - 1)
            elif up_or_down == "down":
                for row in reversed(rows):
                    self.move(row, self.parent(row), self.index(row) + 1)

            for k, row in enumerate(self.get_children("")):
                if k % 2 == 0:
                    self.item(row, tags=('evenrow',))
                else:
                    self.item(row, tags=('oddrow',))
        return

    @staticmethod
    def shift_sublist(test_list, start_idx, no_ele, shift_idx):
        """ Shift item in list"""
        for ele in range(no_ele):
            test_list.insert(shift_idx, test_list.pop(start_idx))
        return test_list

    def shift_cell_up_or_down(self, up_or_down="up"):
        """ shift a single cell up or down"""
        if self and self._t_col is not None:
            if self.selection():
                # compute number of rows and number of columns
                n_rows = len(self.get_children(""))
                n_cols = len(self._tv_cols)
                # create 2D list containing the entire treeview
                old_tv = [[self.item(row, 'values')[col] for row in self.get_children("")]
                          for col in range(0, n_cols)]
                row_idx = self.index(self.selection())
                if up_or_down == "up" and row_idx != 0:
                    old_tv[self._t_col] = self.shift_sublist(old_tv[self._t_col], row_idx, 1, row_idx - 1)
                    row_idx -= 1
                elif up_or_down == "down" and row_idx + 1 != n_rows:
                    old_tv[self._t_col] = self.shift_sublist(old_tv[self._t_col], row_idx, 1, row_idx + 1)
                    row_idx += 1

                # delete all "old" treeview entries
                self.delete_old_treeview_for_modified(old_tv, n_rows)
                try:
                    self.selection_set(self.get_children("")[row_idx])
                except IndexError:
                    self._master.focus_set()

    def destroy_buttons_frame(self):
        if self._buttons_frame:
            self._buttons_frame.destroy()
