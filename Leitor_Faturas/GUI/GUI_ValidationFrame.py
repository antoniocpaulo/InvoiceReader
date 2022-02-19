import copy
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from ..Aux_Functions.App_AuxFunctions import autoscroll, message_boxes
from ..Aux_Functions.FileManager import NORM_FONT

from ..OCR_Reader.TrafficLightValidation import TrafficLightCheck
from ..OCR_Reader import Read_load

from ..Template_Manager.template_aux_functions import get_template_file_path, roi_row_parser

from ..Tkinter_Addins.Custom_Entry_Undo_Redo import CEntry
from ..Tkinter_Addins.collapsiblepane import CollapsiblePane
from ..Tkinter_Addins.TooltipHover import CreateToolTip
from ..Tkinter_Addins.Scrolled_Window_Class import VerticalScrolledFrame

from ..Treeview_Manager.validation_treeview import ValidationTreeview


class ValidationFrame(tk.Frame):

    def __init__(self, home_panel, parent, **kwargs):
        tk.Frame.__init__(self, master=home_panel, background="white", **kwargs)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.parent = parent
        self._main_file_path = self.parent.controller.main_file_path
        self._exe_file_path = self.parent.controller.exe_file_path
        self._app_icon_path = self.parent.controller.app_icon_path

        self.my_labels = []  # list the no. of labels required by the roi input
        self.my_entries = []  # list the no. of entries required by the roi input
        self.my_frames = []  # list to hold the encapsulating frames that provide color to  the entries
        self.template_list = []  # list the available templates
        self.template_nif = []  # list the templates nif
        self.template_refs = []
        self.table_cols = None  # list to hold the equivalent result variable to the column name
        self.entries_labels = None  # list to hold the equivalent result variable to the label name
        self.nif_label = tk.StringVar()
        self.OCR_results = []
        self.current_invoice = None
        self.current_invoice_name = tk.StringVar()
        self._vsb = None
        self._hsb = None
        self.val_tree = None
        self.val_tree_cols = []
        self.roi = {}
        self.template_paths = {}  # dictionary that holds the paths to all available template images
        self.OCR_backup = []
        self._temp_img = None
        self._sample_label = None
        self.tip_window = None
        self.new_line_y = 0
        self.my_frame = None
        self.my_label = None
        self.my_entry = None
        self.focused_entry = []

        # Icons used in buttons
        self.o_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\rewind-1.png").resize((30, 30), Image.LANCZOS))
        self.o_img1 = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\more.png").resize((30, 30), Image.LANCZOS))
        self.o_img2 = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\OK.png").resize((30, 30), Image.LANCZOS))
        self.o_img3 = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\fast_forward-1.png").resize((30, 30), Image.LANCZOS))
        self.o_img4 = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\undo.png").resize((30, 30), Image.LANCZOS))
        self.o_img5 = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\redo.png").resize((30, 30), Image.LANCZOS))
        self.o_img6 = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\delete_file.png").resize((30, 30), Image.LANCZOS))
        self.save_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\save.png").resize((30, 30), Image.LANCZOS))
        self.del_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\garbage.png").resize((30, 30), Image.LANCZOS))
        # Highlight images if entry is in right format or not
        self.error_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\error.png").resize((15, 15), Image.LANCZOS))
        self.ok_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\validate.png").resize((15, 15), Image.LANCZOS))

        # Create frame to store the different entries and labels
        self.frame1 = VerticalScrolledFrame(self)
        self.traffic_collapsepane = CollapsiblePane(self.frame1, "\u2b9f", "\u2b9d")
        self.traffic_check_frame = TrafficLightCheck(self.traffic_collapsepane.frame,
                                                     self._main_file_path, borderwidth=1, relief="ridge")
        self.traffic_check_frame.grid(row=0, column=0, sticky="nsew")
        # call get_roi function to retrieve available templates
        self.get_available_templates()
        # add labels and entry widgets for the first loaded template
        self.create_entries_labels(self.template_list[0])
        self.nif_label.set("NIF: " + str(self.template_nif[0]))

        # create dropdown list to hold available templates
        frame0 = tk.Frame(self, borderwidth=1, relief="ridge", bg="light steel blue")
        frame0.columnconfigure((2, 4), weight=1)
        space_holder1 = tk.Label(frame0, text="", bg="light steel blue")
        space_holder2 = tk.Label(frame0, text="", bg="light steel blue")
        entry_template = tk.Label(frame0, text="Selecionar Template:", font=NORM_FONT, bg="light steel blue")
        template_nif_lbl = tk.Label(frame0, textvariable=self.nif_label, font=NORM_FONT, bg="light steel blue")
        self.template_combo_list = ttk.Combobox(frame0, value=self.template_list, font=NORM_FONT, state="readonly",
                                                justify="center")
        self.template_combo_list.current(0)
        self.template_combo_list.configure(width=len(max(self.template_list, key=len)))
        self.template_combo_list.bind("<<ComboboxSelected>>", self.grab_current_template)

        self.prev_temp_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\preview_file.png").resize((30, 30), Image.LANCZOS))
        self.play_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\play.png").resize((30, 30), Image.LANCZOS))

        # Run selected files through OCR
        self.run_selected = tk.Button(frame0, image=self.play_img, relief="flat", bg="light steel blue",
                                      command=self.hook_to_run_tesseract_ocr)
        preview_template = tk.Button(frame0, image=self.prev_temp_img, relief="flat", bg="light steel blue",
                                     command=self.show_template_img)
        preview_template.bind("<Enter>", self.show_template_sample_img)
        preview_template.bind("<Leave>", self.hide_template_sample_img)

        frame0.grid(row=0, column=0, columnspan=3, pady=10, sticky="new")
        entry_template.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.template_combo_list.grid(row=0, column=1, pady=5, sticky="w")
        space_holder1.grid(row=0, column=2, sticky="ew")
        template_nif_lbl.grid(row=0, column=3, pady=5, padx=10, sticky="ew")
        space_holder2.grid(row=0, column=4, sticky="ew")
        preview_template.grid(row=0, column=5, padx=10, pady=5, sticky="e")
        self.run_selected.grid(row=0, column=6, padx=10, pady=5, sticky="e")

        # Grid Frame 1 (holder of labels and entries of ROI) to screen
        self.frame1.grid(row=1, column=0, pady=10, sticky="nsew")

        # Bind focus-in to all modified entry widgets - enable and disable undo/redo
        self.frame1.interior.bind_class("Entry", "<FocusOut>", self.remember_focus)

        # Create Frame to store buttons to allow the user to move forward or backward or store validated results
        frame2 = tk.Frame(self, bg="white")
        self.prev_invoice = tk.Button(frame2, image=self.o_img, relief="flat", bg="white")
        self.ok_invoice = tk.Button(frame2, image=self.o_img2, relief="flat", bg="white",
                                    command=self.store_validated_entries)
        self.next_invoice = tk.Button(frame2, image=self.o_img3, relief="flat", bg="white")
        self.undo = tk.Button(frame2, image=self.o_img4, relief="flat", bg="white", command=self.undo_actions)
        self.redo = tk.Button(frame2, image=self.o_img5, relief="flat", bg="white", command=self.redo_actions)
        self.clear_button = tk.Button(frame2, image=self.o_img6, relief="flat", bg="white",
                                      command=self.clear_all_entries)
        self.clear_button["state"] = "disabled"

        self.save_button = tk.Button(frame2, image=self.save_img, relief="flat", bg="white",
                                     command=self._prepare_file_save)

        self.del_button = tk.Button(frame2, image=self.del_img, relief="flat", bg="white",
                                    command=self.delete_reading)
        self.del_button["state"] = "disabled"

        self.more_invoice = tk.Menubutton(frame2, image=self.o_img1, relief="flat", bg="white")
        self.more_invoice.menu = tk.Menu(self.more_invoice, tearoff=0)
        self.more_invoice["menu"] = self.more_invoice.menu
        self.more_invoice.menu.add_command(label="Abrir Resultados Originais da Leitura",
                                           command=self.load_original_results)
        self.more_invoice.menu.add_command(label="Editar Resultados Validados", command=self.edit_validated_results)
        self.more_invoice.menu.add_command(label="Ir para fatura número", command=self.choose_current_invoice)

        # start with next/previous invoice buttons disabled
        self.next_invoice["state"] = "disabled"
        self.more_invoice["state"] = "disabled"
        self.ok_invoice["state"] = "disabled"
        self.prev_invoice["state"] = "disabled"
        self.save_button["state"] = "disabled"
        self.undo["state"] = "normal"
        self.redo["state"] = "normal"

        frame2.grid(row=2, column=0, columnspan=2, sticky="sew")
        frame2.columnconfigure(2, weight=1)
        self.current_invoice_name.set("")
        frame2_label = tk.Label(frame2, textvariable=self.current_invoice_name, bg="white", anchor="center",
                                font=NORM_FONT)
        self.undo.grid(row=0, column=0, pady=10, padx=5, sticky="sw")
        self.redo.grid(row=0, column=1, pady=10, padx=5, sticky="sw")
        frame2_label.grid(row=0, column=2, sticky="nsew")
        self.prev_invoice.grid(row=0, column=3, pady=10, padx=5, sticky="se")
        self.clear_button.grid(row=0, column=4, pady=10, padx=5, sticky="se")
        self.del_button.grid(row=0, column=5, pady=10, padx=5, sticky="se")
        self.more_invoice.grid(row=0, column=6, pady=10, padx=5, sticky="nsew")
        self.save_button.grid(row=0, column=7, pady=10, padx=5, sticky="se")
        self.ok_invoice.grid(row=0, column=8, pady=10, padx=5, sticky="se")
        self.next_invoice.grid(row=0, column=9, pady=10, padx=5, sticky="se")

        # Assign floating labels to buttons with images
        CreateToolTip(self.run_selected, text="Correr Leitor Faturas", 
                      command=self.hook_to_run_tesseract_ocr)
        CreateToolTip(self.clear_button, text="Limpar Entradas")
        CreateToolTip(self.prev_invoice, text="Fatura Anterior", 
                      command=self.next_or_previous_invoice, extra_command="previous")
        CreateToolTip(self.del_button, text="Apagar Leitura")
        CreateToolTip(self.save_button, text="Gravar Leitura Validada")
        CreateToolTip(self.more_invoice, text="Mais")
        CreateToolTip(self.undo, text="Desfazer")
        CreateToolTip(self.redo, text="Refazer")
        CreateToolTip(self.ok_invoice, text="Validar")
        CreateToolTip(self.next_invoice, text="Próxima Fatura", 
                      command=self.next_or_previous_invoice, extra_command="next")

    def change_entries_table_state(self, change_from="normal"):
        """method used to change state of entries and table"""

        if change_from == "normal":
            if self.my_entries[0]["state"] == "normal":
                for n in range(0, len(self.my_entries)):
                    self.my_entries[n]["state"] = "disabled"
            if self.val_tree_cols:  # if variable holding treeview columns is not empty
                if self.val_tree.is_enabled():
                    self.val_tree.disable()  # enable validation tree if it is disabled
        elif change_from == "disabled":
            # if invoice is not validated then check if entry widgets are disabled, and enable them
            if self.my_entries[0]["state"] == "disabled":
                for n in range(0, len(self.my_entries)):
                    self.my_entries[n]["state"] = "normal"
            if self.val_tree_cols:  # if variable holding treeview columns is not empty
                if self.val_tree.is_disabled():
                    self.val_tree.enable()  # enable validation tree if it is disabled
        return

    def create_entries_labels(self, template):
        """method used to create automatically as many entries and labels as required"""
        count, col_count, k = 0, 0, 0

        columns_roi = []
        self.table_cols = []
        self.entries_labels = []
        while k < len(self.roi[template]):
            row = self.roi[template][k]
            if "list" in row[2] or "text_table" in row[2]:
                while "list" in self.roi[template][k][2] or "text_table" in self.roi[template][k][2]:
                    columns_roi.append(str(self.roi[template][k][4]))
                    self.table_cols.append(str(self.roi[template][k][3]))
                    k += 1
                count, col_count = self.create_editable_tree(columns_roi, count, col_count)
                continue

            if row[2] != "neglect":
                self.entries_labels.append(str(row[3]))
                self.my_label = tk.Label(self.frame1.interior, text=str(row[4]),
                                         bg="white", fg="black", font=NORM_FONT)
                self.my_frame = tk.Frame(self.frame1.interior, background=Read_load.tk_colors[k])
                self.my_frame.columnconfigure(0, weight=1)
                self.my_entry = CEntry(self.my_frame, text="", font=NORM_FONT, bd=0)

                self.my_label.grid(row=count, column=col_count, pady=5, padx=3, sticky="ew")
                self.my_frame.grid(row=count, column=col_count + 1, pady=5, padx=3, sticky="ew")
                self.my_entry.grid(row=0, column=0, pady=1, padx=1, sticky="ew")

                self.my_labels.append(self.my_label)
                self.my_frames.append(self.my_frame)
                self.my_entries.append(self.my_entry)
                count += 1
            k += 1

        self.traffic_collapsepane.grid(row=count, column=col_count, columnspan=2, sticky="nsew")

    def create_editable_tree(self, columns_roi, row_count, col_count):
        """ Create Treeview using the roi columns, to store invoice data into a table format"""
        self._vsb = ttk.Scrollbar(self.frame1.interior, orient="vertical")
        self._hsb = ttk.Scrollbar(self.frame1.interior, orient="horizontal")

        self.val_tree_cols = columns_roi
        self.val_tree = ValidationTreeview(self.frame1.interior, columns=self.val_tree_cols,
                                           displaycolumns=self.val_tree_cols,
                                           yscrollcommand=lambda f, l: autoscroll(self._vsb, f, l),
                                           xscrollcommand=lambda f, l: autoscroll(self._hsb, f, l),
                                           row_count=row_count, col_count=col_count,
                                           main_path=self._main_file_path)

        self.val_tree.bind("<FocusOut>", self.remember_focus_tree)
        self._vsb['command'] = self.val_tree.yview
        self._hsb['command'] = self.val_tree.xview

        self.val_tree.tag_configure('oddrow', background="white")
        self.val_tree.tag_configure('evenrow', background="gray80")

        # Arrange the tree and its scrollbars in the top level
        self.val_tree.grid(column=col_count, row=row_count, columnspan=col_count + 2, pady=5, sticky='nsew')
        self._vsb.grid(column=col_count + 2, row=row_count, sticky='ns')
        self._hsb.grid(column=col_count, row=row_count + 1, columnspan=col_count + 2, sticky='ew')

        return row_count + 3, col_count

    def choose_current_invoice(self):
        """ method used to allow the user to select the current invoice"""
        x = self.winfo_x()
        y = self.winfo_y()

        top = tk.Toplevel(self)
        top.geometry("+%d+%d" % (x + 100, y + 200))
        top.iconbitmap(top, default=self._app_icon_path)
        top_label = tk.Label(top, text="Selecione a fatura pretendida:", font=NORM_FONT)
        top_label.grid(row=0, column=0)
        invoice_list = list(range(1, len(self.OCR_results) + 1))
        combo_list = ttk.Combobox(top, value=invoice_list, font=NORM_FONT, state="readonly", width=10)
        combo_list.current(0)
        combo_list.bind("<<ComboboxSelected>>", lambda event: self.set_current_invoice(event, top))
        combo_list.grid(row=0, column=1)

    def clear_all_entries(self):
        """method used to clear all validation entries"""
        for i in range(0, len(self.my_entries)):
            self.my_entries[i].delete(0, tk.END)
        self.clear_button["state"] = "disabled"
        if self.val_tree:
            self.val_tree.delete(*self.val_tree.get_children())

    def delete_reading(self):
        """method used to delete current invoice from OCR results"""
        # check if current file is validated
        was_validated = True if self.OCR_results[self.current_invoice][4] else False

        # delete file from its stored location
        del self.OCR_results[self.current_invoice]
        del self.OCR_backup[self.current_invoice]

        # update variable containing length of OCR results
        self.parent.len_ocr_results = len(self.OCR_results)

        # remove file from whichever tree it is stored and delete item from tracking dictionary
        self.parent.opened_files_tree.remove_file_from_tree(self.current_invoice, was_validated)
        self.current_invoice_name.set("")

        if self.current_invoice >= 1:
            self.current_invoice -= 1
        elif self.current_invoice == 0 and len(self.OCR_results) == 0:
            self.clear_all_entries()
            self.parent.imageFrame.show_image(file_path="", load_backup=True)
            return

        self.next_or_previous_invoice("user_choice")
        return

    def do_checks_update(self, check_results):
        """method used to provide initial input, if the OCR readings are incomplete"""
        if check_results[1]:
            try:
                self.OCR_results[self.current_invoice][1]["invoice_subtotal"] = check_results[0]
                if "invoice_subtotal" in self.entries_labels:
                    idx = self.entries_labels.index("invoice_subtotal")
                    self.my_entries[idx].delete(0, tk.END)
                    self.my_entries[idx].insert(0, check_results[0])
            except KeyError:
                pass
        if check_results[3]:
            try:
                self.OCR_results[self.current_invoice][1]["total_tax"] = check_results[2]
                if "total_tax" in self.entries_labels:
                    idx = self.entries_labels.index("total_tax")
                    self.my_entries[idx].delete(0, tk.END)
                    self.my_entries[idx].insert(0, check_results[2])
            except KeyError:
                pass
        if check_results[5]:
            try:
                self.OCR_results[self.current_invoice][1]["invoice_total"] = check_results[4]
                if "invoice_total" in self.entries_labels:
                    idx = self.entries_labels.index("invoice_total")
                    self.my_entries[idx].delete(0, tk.END)
                    self.my_entries[idx].insert(0, check_results[4])
            except KeyError:
                pass

    def edit_validated_results(self):
        """ method used to allow the user to update the results again, once they are validated"""
        self.OCR_results[self.current_invoice][4] = False
        # disable saving the validated file
        self.save_button["state"] = "disabled"
        self.ok_invoice["state"] = "normal"
        if self.val_tree.is_disabled():
            self.val_tree.enable()  # enable validation tree if it is disabled
        for n in range(0, len(self.my_entries)):
            self.my_entries[n]["state"] = "normal"
        # send the file from validated tree to the read tree
        self.parent.opened_files_tree.move_to_or_from_validated_table(self.parent.controller,
                                                                      self.current_invoice, move="from")
        check_results = self.traffic_check_frame.do_checks(self.OCR_results[self.current_invoice][1])
        self.do_checks_update(check_results)
        self.update_entries_labels_with_OCR_results(self.current_invoice)

    def first_results_load(self, cur_invoice=0, only_enable_buttons=True):
        """ Method to update status of validation buttons and to load the first set of results to screen"""
        self.clear_button["state"] = "normal"
        self.del_button["state"] = "normal"
        self.more_invoice["state"] = "normal"
        self.ok_invoice["state"] = "normal"

        if (len(self.OCR_results) > 1 and cur_invoice == 0) or cur_invoice < len(self.OCR_results):
            self.next_invoice["state"] = "normal"
        else:
            self.next_invoice["state"] = "disabled"

        self.prev_invoice["state"] = "normal" if len(self.OCR_results) > 1 and cur_invoice > 0 else "disabled"

        if not only_enable_buttons:
            # load first invoice results to validation frame
            self.current_invoice = cur_invoice
            check_results = self.traffic_check_frame.do_checks(self.OCR_results[self.current_invoice][1])
            self.do_checks_update(check_results)
            self.update_entries_labels_with_OCR_results(self.current_invoice)
        return

    def get_available_templates(self):
        """open csv file where templates are stored and get information - store owner, template fields"""
        roi_holder = Read_load.get_roi(self._exe_file_path)
        for k, key in enumerate(roi_holder):
            # append names of
            self.template_list.append(key)
            # first line of loaded csv file contains NIF retailer
            self.template_nif.append(roi_holder[key][0])
            # 2nd and 3rd lines hold correspondence between product references
            self.template_refs.append(roi_holder[key][1:3])
            # 4th line onwards, contains data regarding the template definition
            self.roi[key] = roi_row_parser(roi_holder[key][3:])
            # add paths of every template to a dictionary
            self.template_paths[key] = get_template_file_path(self.template_list[k], self._exe_file_path)
        return

    def grab_current_template(self, event):
        """get current template from template list"""
        self.update_entries_labels(self.template_combo_list.get())
        # set all traffic lights to yellow
        self.traffic_check_frame.load_initial_status()
        # show template image
        self.show_template_img()

    def hide_template_sample_img(self, event):
        """method used to kill the top level window with the chosen template"""
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

    def hook_to_run_tesseract_ocr(self):
        self.parent.controller.event_generate('<<HookRunOCR>>', when="now")

    def load_original_results(self):
        """ This method allows the user to get the backup OCR results of a given invoice and rewrite the
         into the variable holding the current results"""
        yes_or_no = message_boxes("askyesno", "Carregar resultados originais de leitura?",
                                  "Os resultados actuais serão subsituídos pelos anteriors.")
        if yes_or_no:
            self.OCR_results[self.current_invoice][1] = copy.deepcopy(self.OCR_backup[self.current_invoice][1])
            if self.OCR_results[self.current_invoice][4]:
                # send the file from validated tree to the read tree
                self.parent.opened_files_tree.move_to_or_from_validated_table(self.parent.controller,
                                                                              self.current_invoice, move="from")
            self.OCR_results[self.current_invoice][4] = False
            self.save_button["state"] = "disabled"  # disable saving the validated file
            self.ok_invoice["state"] = "normal"
            check_results = self.traffic_check_frame.do_checks(self.OCR_results[self.current_invoice][1])
            self.do_checks_update(check_results)
            self.update_entries_labels_with_OCR_results(self.current_invoice)
            self.clear_button["state"] = "normal"
            self.del_button["state"] = "normal"
        return

    def load_results_after_changes(self):
        """method used to finalize changes made from "next_or_previous_invoice" method"""
        # show resulting image retrieved from OCR
        self.parent.imageFrame.show_image(self.OCR_results[self.current_invoice][2])
        # re-run checks on new invoice to assess its status
        check_results = self.traffic_check_frame.do_checks(self.OCR_results[self.current_invoice][1])
        self.do_checks_update(check_results)
        self.update_entries_labels_with_OCR_results(self.current_invoice)
        self.clear_button["state"] = "normal"
        self.del_button["state"] = "normal"
        return

    def next_or_previous_invoice(self, option, old_invoice=""):
        """ Method used to enable or disable the "next" / "previous" invoice buttons, taking into account the user's
        request. After updating the button status it proceeds to load the invoice data and show it.
        :param option: move to previous or next invoice
        :param old_invoice: variable containing the old invoice number, to avoid replacing invoice results
        :return: None
        """

        # save current results before changing invoice
        if not self.OCR_results[self.current_invoice][4] and old_invoice == "" and option != "user_choice":
            self.save_results(self.current_invoice)
        elif old_invoice != "" and option == "user_choice":
            self.save_results(old_invoice)

        if option == "user_choice" and len(self.OCR_results) >= 1:
            self.next_invoice["state"] = "disabled" if self.current_invoice + 1 >= len(self.OCR_results) else "normal"
            self.prev_invoice["state"] = "normal" if self.current_invoice - 1 >= 0 else "disabled"
            self.load_results_after_changes()
            return
        elif len(self.OCR_results) <= 1:
            return
        elif option == "enable_next":
            self.next_invoice["state"] = "normal"
        else:
            if option == "next":
                self.current_invoice += 1
                if self.current_invoice + 1 >= len(self.OCR_results):
                    self.next_invoice["state"] = "disabled"
                    self.prev_invoice["state"] = "normal" if self.current_invoice - 1 >= 0 else "disabled"
                else:
                    self.next_invoice["state"] = "normal"
                    self.prev_invoice["state"] = "normal" if self.current_invoice - 1 >= 0 else "disabled"
            elif option == "previous":
                self.current_invoice -= 1
                if self.current_invoice - 1 >= 0:
                    self.prev_invoice["state"] = "normal"
                    self.next_invoice["state"] = "disabled" if self.current_invoice + 1 >= len(self.OCR_results
                                                                                               ) else "normal"
                elif self.current_invoice - 1 < 0:
                    self.prev_invoice["state"] = "disabled"
                    self.next_invoice["state"] = "disabled" if self.current_invoice + 1 >= len(self.OCR_results
                                                                                               ) else "normal"

            self.load_results_after_changes()
            return

    def _prepare_file_save(self):
        self.event_generate("<<PrepareValidationSave>>")

    def remember_focus(self, event):
        """ method used to store information on the last 15 entries, so that on can do undo/redo as pretended
        if list has more than 15 entries, than start to remove the first item and add in the end the new widget"""
        if self.current_invoice is not None:  # only enters if the first results have been loaded
            if len(self.focused_entry) < 15:
                if event.widget not in self.focused_entry:
                    self.focused_entry.append(event.widget)
            else:
                self.focused_entry.pop(0)
                self.focused_entry.append(event.widget)

            # save change made on entry
            self.save_results(self.current_invoice)
            # perform invoice checks
            check_results = self.traffic_check_frame.do_checks(self.OCR_results[self.current_invoice][1])
            self.do_checks_update(check_results)

    def remember_focus_tree(self, event):
        """use event to check which entry was modified and if a check can be run on it"""
        if self.current_invoice is not None and self.val_tree:
            # save change made on the treeview
            self.save_results(self.current_invoice)
            # perform invoice checks
            check_results = self.traffic_check_frame.do_checks(self.OCR_results[self.current_invoice][1])
            self.do_checks_update(check_results)

    def redo_actions(self):
        """ redo actions on last 15 user edited entries"""
        if len(self.focused_entry) == 1:
            try:
                self.focused_entry[0].redo()
            except AttributeError:
                pass
        else:
            k = len(self.focused_entry) - 1
            cur_widget = None
            flag = False
            while k >= 0:
                cur_widget = self.focused_entry[k]
                try:
                    if cur_widget.steps <= len(cur_widget.changes) - 1:
                        flag = True
                        break
                    k -= 1
                except AttributeError:
                    k -= 1

            if cur_widget and flag:
                cur_widget.focus_set()
                cur_widget.redo()

    def undo_actions(self):
        """ undo actions on last 15 user edited entries"""
        if len(self.focused_entry) == 1:
            try:
                self.focused_entry[0].undo()
            except AttributeError:
                pass
        else:
            k = len(self.focused_entry) - 1
            cur_widget = None
            flag = False
            while k >= 0:
                cur_widget = self.focused_entry[k]
                try:
                    if cur_widget.steps >= 1:
                        flag = True
                        break
                    k -= 1
                except AttributeError:
                    k -= 1

            if cur_widget and flag:
                cur_widget.focus_set()
                cur_widget.undo()

    def update_entries_labels_with_OCR_results(self, cur_invoice=0):
        """method to update both the entries and tree (if existent) with OCR results
        OCR_results[cur_invoice][0] - invoice number, OCR_results[cur_invoice][1] - OCR results
        OCR_results[cur_invoice][2] - OCR image path, OCR_results[cur_invoice][3] - template used
        OCR_results[cur_invoice][4] - is validated (True/False), OCR_results[cur_invoice][5] - File Name
        """
        # set name of current invoice to label using its textvar
        file_name = str(self.OCR_results[cur_invoice][5])
        self.current_invoice_name.set(file_name[0:file_name.find(".")])

        # if the current template is different from the one used to read the invoice, change it
        if self.template_combo_list.get() != self.OCR_results[cur_invoice][3]:
            self.template_combo_list.current(self.template_list.index(self.OCR_results[cur_invoice][3]))
            self.update_entries_labels(self.OCR_results[cur_invoice][3])

        # if invoice is not validated change table status from disabled to normal and update save button status
        if not self.OCR_results[cur_invoice][4]:
            self.change_entries_table_state("disabled")
            self.save_button["state"] = "disabled"
            self.ok_invoice["state"] = "normal"
        else:
            self.change_entries_table_state("normal")
            self.save_button["state"] = "normal"
            self.ok_invoice["state"] = "disabled"

        k = 0
        table_values = []
        while k < len(self.OCR_results[cur_invoice][1]):
            key = list(self.OCR_results[cur_invoice][1])[k]
            if key in self.entries_labels:
                idx = self.entries_labels.index(key)
                self.my_entries[idx].delete(0, tk.END)
                if type(self.OCR_results[cur_invoice][1][key]) is list:
                    self.my_entries[idx].insert(0, ", ".join(map(str, self.OCR_results[cur_invoice][1][key])))
                elif self.OCR_results[cur_invoice][1][key] is None:
                    self.my_entries[idx].insert(0, "")
                else:
                    self.my_entries[idx].insert(0, self.OCR_results[cur_invoice][1][key])
            elif key in self.table_cols:  # table_cols will always exist since it is initialized in __init__
                self.val_tree.delete(*self.val_tree.get_children())
                n_rows = 0
                while key in self.table_cols:
                    table_values.append(self.OCR_results[cur_invoice][1][key])
                    k += 1
                    key = list(self.OCR_results[cur_invoice][1])[k]
                    continue
                k -= 1
                max_length = max(len(sub_list) if sub_list is not None and type(sub_list) is list else 0 for
                                 sub_list in table_values)
                if max_length <= 1:  # if the results matrix contains only a single line of readings
                    new_values = []
                    for item in table_values:
                        if item:
                            new_values.append(item[0]) if len(item) > 0 else new_values.append(item)
                        else:
                            new_values.append("")
                    self.val_tree.insert('', n_rows, values=tuple(new_values))
                else:
                    for sub_list in table_values:  # for each item in the list
                        sub_list = [] if type(sub_list) is str else sub_list
                        while len(sub_list) < max_length:  # while the item length is smaller than max_length
                            sub_list.append("")  # append empty to the item
                    for i in range(0, max_length):
                        tree_row = [sub_list[i] if type(sub_list) is not str else sub_list for sub_list in table_values]
                        new_values = tuple(tree_row)
                        if i % 2 == 0:
                            self.val_tree.insert('', n_rows, values=new_values, tags=('evenrow',))
                        else:
                            self.val_tree.insert('', n_rows, values=new_values, tags=('oddrow',))
                        n_rows += 1
            k += 1

        return

    def update_entries_labels(self, template):
        """use method to remove the already created entries and create new for newly selected template"""
        for n in range(0, len(self.my_labels)):
            self.my_labels[n].grid_forget()
            self.my_frames[n].grid_forget()
            self.my_entries[n].grid_forget()
            self.nif_label.set("")
        if self.val_tree_cols:
            self.val_tree.destroy_buttons_frame()
            self.val_tree.destroy()
            self._vsb.destroy()
            self._hsb.destroy()

        # delete all items from list
        self.my_labels.clear()
        self.my_frames.clear()
        self.my_entries.clear()

        self.create_entries_labels(template)
        self.nif_label.set("NIF: " + str(self.template_nif[self.template_list.index(template)]))
        self.clear_button["state"] = "disabled"
        self.del_button["state"] = "disabled"

    def save_results(self, cur_invoice):
        """ Method used to save the results before the next action"""

        # if invoice is validated, change state to normal to retrieve data from entry boxes
        if not self.OCR_results[cur_invoice][4]:
            self.change_entries_table_state("disabled")
            self.save_button["state"] = "disabled"
            self.ok_invoice["state"] = "normal"
        else:
            # if invoice is validated, change state back to disabled after retrieving data from entry boxes
            self.change_entries_table_state("normal")
            self.save_button["state"] = "normal"
            self.ok_invoice["state"] = "disabled"

        # only save results if current invoice is the same used as the one in the OCR reading
        if self.template_combo_list.get() == self.OCR_results[cur_invoice][3]:
            first_test = True
            for key in self.OCR_results[cur_invoice][1]:
                if key in self.entries_labels:
                    idx = self.entries_labels.index(key)
                    # get data stored in entry widgets and update according to dict key
                    self.OCR_results[cur_invoice][1][key] = self.my_entries[idx].get()
                elif key in self.table_cols and first_test:
                    # ensure that these variables are not computed again
                    first_test = False
                    tree_rows = list(self.val_tree.get_children(""))
                    for k, col in enumerate(self.table_cols):
                        self.OCR_results[cur_invoice][1][col] = [self.val_tree.item(row, 'values')[k] for row in
                                                                 tree_rows]

    def set_current_invoice(self, event, top_window, from_tree=""):
        """ change current invoice to that specified by the user """
        try:
            old_invoice = self.current_invoice if int(self.current_invoice) < len(self.OCR_results) else ""
        # if current_invoice variable has not yet been defined, then proceed, as this situation will occur only when
        # file is loaded from an outside directory and no other invoice results have been read by the tool
        except TypeError:
            old_invoice = ""
        if from_tree == "":
            combo_box = event.widget
            self.current_invoice = int(combo_box.get()) - 1
        else:
            self.current_invoice = from_tree
        if top_window:
            top_window.destroy()
        self.next_or_previous_invoice("user_choice", old_invoice)

    def store_validated_entries(self):
        """ method used to store the user validated data back into the main OCR_results variable
            if user wants to retrieve the original values, he/she may do so using OCR_backup.
            """
        
        # change invoice status to -> is validated - acts as flag when showing entries (normal or disabled)
        # and as flag if user wants to export all invoices, without them being validated
        self.OCR_results[self.current_invoice][4] = True
        # enable saving the validated file
        self.save_button["state"] = "normal"
        self.ok_invoice["state"] = "disabled"
        # call method to update OCR results
        self.save_results(self.current_invoice)
        # disable both the entries and (if existent) the validation tree
        for n in range(0, len(self.my_entries)):
            self.my_entries[n]["state"] = "disabled"
        if self.val_tree_cols:
            self.val_tree.disable()
        # send the file from the read treeview to the validated treeview
        self.parent.opened_files_tree.move_to_or_from_validated_table(self.parent.controller,
                                                                      self.current_invoice, move="to")

        return

    def show_template_img(self):
        """ method used to show the template image as a preview"""
        template_path = get_template_file_path(self.template_combo_list.get(), self._exe_file_path)
        self.parent.imageFrame.show_image(template_path)
        return None

    def show_template_sample_img(self, event):
        """method used to show top level window with a preview of the chosen template
        the top level window is created when the user hovers the mouse over the preview template button"""
        template_path = get_template_file_path(self.template_combo_list.get(), self._exe_file_path)
        if template_path:
            self._temp_img = ImageTk.PhotoImage(Image.open(template_path).resize((414, 585), Image.LANCZOS))
            x = self.winfo_rootx() + self.winfo_width() // 5
            y = self.winfo_rooty() + self.winfo_height() // 10
            self.tip_window = tw = tk.Toplevel(self)
            tw.wm_geometry("+%d+%d" % (x, y))
            self._sample_label = tk.Label(tw, image=self._temp_img)
            self._sample_label.grid(row=0, column=0, sticky="nsew")
        else:  # template not found
            message_boxes("error", "Nome Template: {}".format(str(self.template_combo_list.get())),
                          "Por favor, verique se o nome do ficheiro imagem do template coincide com o do ficheiro csv!")
        return
