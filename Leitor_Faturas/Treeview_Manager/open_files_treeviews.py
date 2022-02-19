from datetime import datetime
from tkinter import ttk
import os


def remove_tree_selection(event):
    tv = event.widget
    if len(tv.selection()) > 0:
        tv.selection_remove(tv.selection()[0])


def treeview_sort_column(tv, col, reverse):  # Treeview, column name, arrangement
    temp_list = [(tv.set(k, col), k) for k in tv.get_children('')]
    temp_list.sort(reverse=reverse)  # Sort by
    # rearrange items in sorted positions
    for index, (val, k) in enumerate(temp_list):  # based on sorted index movement
        tv.move(k, '', index)
        tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
        # Rewrite the title to make it the title of the reverse order


def open_file_in_windows(tv, cur_item):
    # associate to specific keyboard key
    os.popen(tv.item(cur_item)['values'][0])
    tv.selection_remove(cur_item)


class FilesDirectoryTree(ttk.Treeview):

    def __init__(self, parent, columns=None, columns_text=None, **kwargs):

        ttk.Treeview.__init__(self, master=parent, columns=columns, **kwargs)

        self.heading(column="#0", text=columns_text[0], anchor='center')
        self.heading(column="date", text=columns_text[1], anchor='center')
        self.column(column="date", stretch=0, width=100)
        self.heading(column="size", text=columns_text[2], anchor='center')
        self.column(column="size", stretch=0, width=60)

        # add column sorting possibility to treeview
        for i, col in enumerate(columns[1:]):  # bind function to make the header sortable
            self.heading(col, text=columns_text[i],
                         command=lambda _col=col: treeview_sort_column(self, _col, False), anchor='center')

        self.populate_roots()
        self.bind('<<TreeviewOpen>>', self.update_tree)
        self.bind('<Escape>', remove_tree_selection)
        self.bind('<Double-Button-1>', self.change_dir_or_open_file)

    def populate_tree(self, node):
        # method used to populate the file browser tree
        if self.set(node, "type") != 'directory':
            return

        path = self.set(node, "fullpath")
        self.delete(*self.get_children(node))

        # for p in special_dirs + os.listdir(path):
        for p in os.listdir(path):
            parent_type = None
            p = os.path.join(path, p).replace('\\', '/')
            if os.path.isdir(p):
                parent_type = "directory"
            elif os.path.isfile(p):
                parent_type = "file"

            file_name = os.path.split(p)[1]
            id_node = self.insert(node, "end", text=file_name, values=[p, parent_type])

            if parent_type == 'directory':
                if file_name not in ('.', '..'):
                    self.insert(id_node, 0, text="dummy")
                    self.item(id_node, text=file_name)
            elif parent_type == 'file':
                mod_date = os.stat(p).st_mtime
                mod_date = datetime.fromtimestamp(mod_date).strftime('%d.%m.%Y %H:%M')
                self.set(id_node, "date", mod_date)
                size = os.stat(p).st_size / (1024 * 1024)
                self.set(id_node, "size", "%.2f Mb" % size)

    def populate_roots(self):
        # populate tree rows when new parent is defined
        directory = os.path.abspath('.').replace('\\', '/')
        node = self.insert('', 'end', text=directory, open=True, values=[directory, "directory"])
        self.populate_tree(node)

    def update_tree(self, event):
        self.populate_tree(self.focus())

    def change_dir_or_open_file(self, event):
        node = self.focus()
        parent_type = None
        path = os.path.abspath(self.set(node, "fullpath"))
        if os.path.isdir(path):
            parent_type = "directory"
        elif os.path.isfile(path):
            parent_type = "file"

        if parent_type == 'directory':
            if self.parent(node):
                self.change_dir(node)
            elif self.parent:
                self.change_dir_up(node)
        elif parent_type == 'file':
            open_file_in_windows(self, node)

    def change_dir(self, node):
        # change directory to parent's child
        if self.parent(node):
            path = os.path.abspath(self.set(node, "fullpath"))
            if os.path.isdir(path):
                os.chdir(path)
                self.delete(self.get_children(''))
                self.populate_roots()

    def change_dir_up(self, node):
        # change directory to parent's of parent
        path = os.path.dirname(os.path.abspath(self.set(node, "fullpath")))
        if os.path.isdir(path):
            os.chdir(path)
            self.delete(self.get_children(''))
            self.populate_roots()


class OpenFilesTreeview(ttk.Treeview):

    def __init__(self, parent, columns=None, cols_text=None, **kwargs):
        ttk.Treeview.__init__(self, master=parent, columns=columns, **kwargs)

        self._tv_cols = columns
        self.n_rows = 1

        self.heading(column="#0", text="", anchor="center")
        self.column(column="#0", stretch=0, width=0)

        # add column sorting possibility to treeview
        for i, col in enumerate(self._tv_cols):  # bind function to make the header sortable
            self.heading(col, text=cols_text[i], anchor="center",
                         command=lambda _col=col: treeview_sort_column(self, _col, False))

        self.column(column="ID", width=20, stretch=0)
        self.column(column="file_name", anchor='w', stretch=1, width=100)
        self.column(column="path", anchor='w', width=150, stretch=1)
        if len(self._tv_cols) > 3:
            self.column(column="validated_by", stretch=0, width=80)

        # self.files_tree.bind('<<TreeviewOpen>>', self.open_tree_file)
        self.bind('<Button-1>', self.select_record)
        self.bind('<Escape>', remove_tree_selection)
        self.bind('<Delete>', self.delete_selection)

    def delete_selection(self, event):
        if self.focus():
            row_idx = self.index(self.focus())
            self.delete(self.focus())
            if row_idx - 1 >= 0:
                self.selection_set(self.get_children("")[row_idx - 1])
            elif self.get_children(""):
                self.selection_set(self.get_children("")[0])

    def reorganize_row_ids(self):
        """method used to reorganize the row ids"""
        if self.get_children(""):
            # store old treeview into variable
            old_treeview = [[self.item(row, 'values')[col] for row in self.get_children("")]
                            for col in range(1, len(self._tv_cols))]
            tv_len = len(self.get_children(""))
            self.delete(*self.get_children())
            for i in range(0, tv_len):
                tree_row = [i + 1] + [sub_list[i] for sub_list in old_treeview]
                new_values = tuple(tree_row)
                self.insert('', i, values=new_values)

            self.n_rows = len(self.get_children("")) + 1


    def remove_all(self):
        # Remove all records
        if self.get_children():
            self.delete(*self.get_children())
            self.n_rows = 0

    def remove_many(self):
        # Remove many selected
        if self.selection():
            for record in self.selection():
                self.delete(record)
                self.n_rows = self.n_rows - 1 if self.n_rows > 0 else self.n_rows

    def select_record(self, event):
        # Select Record
        if self.focus():
            self.item(self.focus(), 'values')

    def search_items(self, compare_value):
        children = self.get_children('')
        for child in children:
            values = self.item(child, 'values')
            if compare_value == values[2]:
                return True
        return False
