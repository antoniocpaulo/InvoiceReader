import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from ..Aux_Functions.App_AuxFunctions import autoscroll

from ..Treeview_Manager.open_files_treeviews import OpenFilesTreeview
from ..Tkinter_Addins.collapsiblepane import CollapsiblePane
from ..Tkinter_Addins.TooltipHover import CreateToolTip


class OpenedFilesTree(tk.Frame):
    """ Class used to build an interface with the opened files"""

    def __init__(self, parent, main_file_path, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.collapsepane = CollapsiblePane(self, "\u2b9c", "\u2b9e")  # "<<", ">>")
        self.collapsepane.toggle()
        self.collapsepane.grid(row=0, column=0, sticky="nsew")

        self.files_per_tree = {}
        self.parent = parent

        # File Manager - Treeview
        files_tree_cols = ("ID", "file_name", "path")
        files_cols_text = ("#", "Nome Ficheiro", "Localização")
        frame1 = ttk.LabelFrame(self.collapsepane.frame, text="Fatura Abertas", labelanchor="n")
        self.files_tree = self._create_treeview(frame1, files_tree_cols, files_cols_text)
        self.files_tree.bind('<Double-Button-1>', parent.preview_file)

        # create treeview for files read by the OCR module
        frame2 = ttk.LabelFrame(self.collapsepane.frame, text="Faturas Lidas", labelanchor="n")
        self.files_read_tree = self._create_treeview(frame2, files_tree_cols, files_cols_text)
        self.files_read_tree.bind('<Double-Button-1>', lambda event: self.open_results_in_validation_frame(event,
                                                                                                           parent))

        # create treeview for files read and validated
        frame3 = ttk.LabelFrame(self.collapsepane.frame, text="Faturas Validadas", labelanchor="n")
        self.files_validated_tree = self._create_treeview(frame3, files_tree_cols + ("validated_by",),
                                                          files_cols_text + ("Validado por",))
        self.files_validated_tree.bind('<Double-Button-1>', lambda event: self.open_results_in_validation_frame(event,
                                                                                                                parent))

        frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        frame2.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame3.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Frame to hold buttons that manipulate files list
        frame4 = tk.Frame(self.collapsepane.frame, bg="white")
        frame4.grid(row=3, column=0, padx=15, pady=10, sticky="NSEW")

        # Open images for buttons
        self.o_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\open_files.png").resize((30, 30), Image.LANCZOS))
        self.o_img1 = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\open_files_saved.png").resize((30, 30), Image.LANCZOS))
        self.o_img2 = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\garbage.png").resize((30, 30), Image.LANCZOS))
        self.o_img3 = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\delete_file.png").resize((30, 30), Image.LANCZOS))

        # Create buttons
        button0 = tk.Button(frame4, image=self.o_img, relief="flat", bg="white", 
                            command=self.open_files_pdf_other)
        button1 = tk.Button(frame4, image=self.o_img1, relief="flat", bg="white", 
                            command=parent.load_existent_OCR_results)
        button2 = tk.Button(frame4, image=self.o_img2, relief="flat", bg="white", 
                            command=self.files_tree.remove_all)
        button3 = tk.Button(frame4, image=self.o_img3, relief="flat", bg="white", 
                            command=self.files_tree.remove_many)

        # Grid buttons
        button0.grid(row=0, column=0)
        button1.grid(row=0, column=1)
        button2.grid(row=0, column=2)
        button3.grid(row=0, column=3)

        CreateToolTip(button0, text="Abrir Fatura(s)")
        CreateToolTip(button1, text="Abrir Fatura(s) Validada(s)")
        CreateToolTip(button2, text="Remover Tudo")
        CreateToolTip(button3, text="Remover Fatura(s) Seleccionadas")

    @staticmethod
    def _create_treeview(frame, columns, columns_text):
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        vert_scrollbar = tk.Scrollbar(frame, orient="vertical")
        horizontal_scrollbar = tk.Scrollbar(frame, orient="horizontal")

        treeview = OpenFilesTreeview(frame, columns=columns,
                                     displaycolumns=columns,
                                     yscrollcommand=lambda f, l: autoscroll(vert_scrollbar, f, l),
                                     xscrollcommand=lambda f, l: autoscroll(horizontal_scrollbar, f, l),
                                     cols_text=columns_text)

        vert_scrollbar['command'] = treeview.yview
        horizontal_scrollbar['command'] = treeview.xview

        treeview.grid(row=0, column=0, sticky="nsew")
        vert_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        return treeview

    def move_to_read_table(self, files_idx, k=0):
        """method used to move read files from open table to read OCR invoices tables"""
        # if type(files_idx) is str:
        iid = self.files_read_tree.insert("", index="end", values=self.files_tree.item(files_idx)["values"])
        self.files_per_tree[k] = iid
        self.files_tree.delete(files_idx)

    def move_to_or_from_validated_table(self, controller, cur_invoice=0, move="to"):
        """method used to move items between the read and validated tables"""
        if move == "to":
            item = self.files_per_tree[cur_invoice]
            if item in self.files_read_tree.get_children(""):
                val_items = self.files_read_tree.item(item)["values"] + list(controller.username)
                # assign item index to files_per_tree variable = result of inserting item into list
                self.files_per_tree[cur_invoice] = self.files_validated_tree.insert('', index="end", values=val_items)
                self.files_read_tree.delete(item)
        elif move == "from":
            item = self.files_per_tree[cur_invoice]
            if item in self.files_validated_tree.get_children(""):
                val_items = self.files_validated_tree.item(item)["values"][:3]
                # assign item index to files_per_tree variable = result of inserting item into list
                self.files_per_tree[cur_invoice] = self.files_read_tree.insert('', index="end", values=val_items)
                self.files_validated_tree.delete(item)

    def open_results_in_validation_frame(self, event, parent):
        selected_file = event.widget.selection()
        result_idx = 0
        for key in self.files_per_tree.keys():
            if tuple([self.files_per_tree[key]]) == selected_file:
                result_idx = key
                break

        event.widget.selection_remove(selected_file)
        parent.validationFrame.set_current_invoice("", "", result_idx)

    def open_files_pdf_other(self):
        """ Generate event to direct to GUI_Interface function entry"""
        self.parent.controller.event_generate("<<OpenPDForImagefiles>>")

    def remove_file_from_tree(self, cur_invoice, was_validated):
        """method used to remove wanted file from tree"""
        if was_validated:
            item = self.files_per_tree[cur_invoice]
            self.files_validated_tree.delete(item) if item else None
            del self.files_per_tree[cur_invoice]
        else:
            item = self.files_per_tree[cur_invoice]
            self.files_read_tree.delete(item) if item else None
            del self.files_per_tree[cur_invoice]

        aux_dict = self.files_per_tree
        if aux_dict:
            self.files_per_tree = {}
            k = 0
            for key in aux_dict.keys():
                self.files_per_tree[k] = aux_dict[key]
                k += 1
        else:
            self.files_tree.n_rows = 1
        return

    def update_file_tree(self, list_of_files):
        # check if file has more than one page, if so split them by page and add to list_box
        # save files after OCR reading using its results - RestaurantName_NIF_NoInvoice.pdf
        if type(list_of_files) is str:
            file_name = os.path.split(list_of_files)[1]
            if not self.files_tree.search_items(file_name):
                self.files_tree.insert(parent="", index="end", text="",
                                       values=(self.files_tree.n_rows, file_name, list_of_files))

        elif type(list_of_files) is list or tuple:
            for record in list_of_files:
                file_name = os.path.split(record)[1]
                if not self.files_tree.search_items(record):
                    self.files_tree.insert(parent="", index="end", text="",
                                           values=(self.files_tree.n_rows, file_name, record))
                    self.files_tree.n_rows += 1
        return

