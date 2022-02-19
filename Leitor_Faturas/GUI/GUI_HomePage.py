import copy
import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image
from queue import Queue

from .GUI_OpenFilesTree import OpenedFilesTree
from .GUI_ImageFrame import ImageFrame
from .GUI_ValidationFrame import ValidationFrame
from ..Aux_Functions.App_AuxFunctions import message_boxes
from ..Aux_Functions.FileManager import convert_pdf_to_images, load_json_file, \
    save_converted_pdf_files_to_images, open_pdf_or_image_file
from ..OCR_Reader import Read_load
from ..Template_Manager.template_aux_functions import get_template_file_path, leave_movable_template
from ..Template_Manager.movable_template import DefineMovingTemplateEnd
from ..Template_Manager.movable_template_menu import MovableTemplateMenuBar


class HomePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, master=parent, bg="white")
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        # THREADING VARIABLES
        self.running = True
        self.dead = False
        self.queue = None
        self.queueStop = None
        self.ocr_reader = None
        self.controller = controller
        self._cur_invoice = 0
        self._len_images = 0
        self.len_ocr_results = 0
        self._enter_if = False
        self._files_idx = []
        self._current_run = []

        home_panel = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="white", sashrelief=tk.RAISED, sashpad=2)
        home_panel.configure()
        self.opened_files_tree = OpenedFilesTree(self, controller.main_file_path)
        self.imageFrame = ImageFrame(home_panel, controller.main_file_path)
        self.validationFrame = ValidationFrame(home_panel, self)

        # the other options for stretch are "first", "last", "middle" or "never"
        home_panel.add(self.imageFrame, padx=5, sticky="nsew", stretch="always")
        home_panel.add(self.validationFrame, padx=10, sticky="nsew", stretch="always")

        separator_1 = ttk.Separator(self, orient='vertical')

        # add status bar
        self.status_bar_frame = tk.Frame(self, bd=1, relief="sunken", bg="light steel blue")
        self.status_bar_frame.columnconfigure((0, 1), weight=1)
        self.status_bar_left = tk.Label(self.status_bar_frame, text="", padx=5, bg="light steel blue")
        self.status_bar_right = tk.Label(self.status_bar_frame, text="Página Inicial", padx=5, bg="light steel blue")
        self.status_bar_left.grid(row=0, column=0, sticky="w")
        self.status_bar_right.grid(row=0, column=1, sticky="e")

        self.opened_files_tree.grid(row=0, column=0, padx=5, sticky="nsew")
        separator_1.grid(row=0, column=1, sticky="ns")
        home_panel.grid(row=0, column=2, sticky="nsew")
        self.status_bar_frame.grid(row=1, column=0, columnspan=3, sticky="wes")

    def after_OCR_readings(self):
        """Method used to update status bar and perform a deep copy of OCR results"""
        # update methods if OCR were determined
        if self._enter_if:
            self.show_status("Fim de Leitura OCR", "Página Inicial")
            self.controller.update_idletasks()  # update displayed info on screen
            self.validationFrame.run_selected["state"] = "normal"
            self.len_ocr_results = len(self.validationFrame.OCR_results)
            # store OCR results into backup list
            if self.validationFrame.OCR_backup:
                for item in self._current_run:
                    self.validationFrame.OCR_backup.append(copy.deepcopy(item))
            else:
                self.validationFrame.OCR_backup = copy.deepcopy(self._current_run)
            self._current_run = []
            return
        else:
            message_boxes("warning", "", "Nenhuma fatura foi lida, por favor tente novamente...")
            return

    def check_queue(self):
        if not self.queue.empty():
            k, results, result_image, template, file_name = self.queue.get()
            if results == "error":
                # send error message and jump to next ocr reader invoice if error while reading invoice image appears
                message_boxes("error", "Formato de imagem da Fatura", result_image)
            else:
                # transform cv2 image to PIL
                result_image_pil = Image.fromarray(result_image)
                image_path = save_converted_pdf_files_to_images(result_image_pil,
                                                                os.path.splitext(os.path.basename(file_name))[0],
                                                                [], self.controller.all_temp_files,
                                                                self.controller.main_file_path)

                # send file identifier tag and index to "Read Invoices" Tree
                self.opened_files_tree.move_to_read_table(self._files_idx[int(k)], int(k + self.len_ocr_results))
                # append to array containing OCR results
                res = [int(k + self.len_ocr_results), results, image_path, template, False, file_name]
                self.validationFrame.OCR_results.append(res)
                self._current_run.append(res)
                if k == 0 and self.len_ocr_results == 0:
                    self.validationFrame.first_results_load(self._cur_invoice, False)
                    # plot initial invoice searched image
                    self.imageFrame.show_image(self.validationFrame.OCR_results[self._cur_invoice][2])
                else:
                    self.validationFrame.first_results_load(self._cur_invoice, True)

            # update displayed info on screen
            if k + 2 <= self._len_images:
                current_status = "A ler a fatura: " + str(k + 2) + " de " + str(self._len_images) + "..."
                self.show_status(current_status, "A correr o procedimento OCR...")
                self.controller.update_idletasks()
            self.queue.task_done()
        if not self.ocr_reader.running:
            self.running = False
            self.ocr_reader.stop()
            self.check_thread_dead()
        if self.running:
            self.controller.after(100, self.check_queue)

    def check_thread_dead(self):
        if self.queueStop.empty() and not self.dead:
            self.controller.after(100, self.check_thread_dead)
            return
        self.queueStop.get()
        self.dead = True
        self.ocr_reader.join()
        self.after_OCR_readings()

    def load_existent_OCR_results(self):
        """function used to load previously read OCR results, to apply further modifications"""
        list_of_files = tk.filedialog.askopenfilename(title="Seleccione o(s) ficheiro(s) para ser(em) carregado(s):",
                                                      filetypes=(("Ficheiros JSON", "*.json"),
                                                                 ("Todos os ficheiros", "*.*")), multiple=True)
        for k, f in enumerate(list_of_files):
            read_file = load_json_file(f)
            # change id of loaded file, to cope with current readings
            read_file[0] = int(k + len(self.validationFrame.OCR_results))
            # change status from a validated invoice to a read (editable) invoice
            read_file[4] = False
            # add loaded file to list of file indexes
            self._files_idx.append(int(k + len(self.validationFrame.OCR_results)))

            # if self.opened_files_tree.files_tree.n_rows > 0:  # update the number of rows and respective numeration
            #     self.opened_files_tree.files_tree.reorganize_row_ids()  # update file numeration

            # check if previously saved image exists, if not use pdf (if existent, convert it to .tiff and change path)
            if not os.path.exists(read_file[2][0]):
                file_name = os.path.splitext(os.path.basename(read_file[5]))[0]
                if os.path.exists(os.path.dirname(f) + "/" + file_name + ".pdf"):
                    read_file[2], _ = convert_pdf_to_images(os.path.dirname(f) + "/" + file_name + ".pdf", self,
                                                            self.controller.all_temp_files,
                                                            self.controller.main_file_path)
                else:
                    title = "Seleccione o ficheiro PDF que deu origem à leitura em questão:"
                    pdf_file = tk.filedialog.askopenfilename(title=title, filetypes=(("Ficheiros PDF", "*.pdf"),),
                                                             multiple=False)
                    if pdf_file:
                        read_file[2], _ = convert_pdf_to_images(pdf_file, self, self.controller.all_temp_files,
                                                                self.controller.main_file_path)
                    else:
                        read_file[2] = self.controller.main_file_path + r"\bin\aux_img\background6.jpg"
                        message_boxes("info", "Imagem da Leitura",
                                      "Ficheiro não seleccionado, será utilizado um ficheiro standard.")

            if not self.validationFrame.OCR_results:  # if OCR results list is empty
                self.validationFrame.OCR_results.append(read_file)  # add loaded file to OCR results list
                self.validationFrame.first_results_load(cur_invoice=read_file[0], only_enable_buttons=False)
                self.imageFrame.show_image(self.validationFrame.OCR_results[read_file[0]][2])
            else:
                self.validationFrame.OCR_results.append(read_file)

            # values to be added to read files tree - File Index, File Name, Image File Path
            item_values = (self.opened_files_tree.files_tree.n_rows, read_file[5], read_file[2])
            iid = self.opened_files_tree.files_read_tree.insert('', index="end", values=item_values)
            self.opened_files_tree.files_per_tree[k] = iid  # add loaded file tree id to list with file id's

            # append a deep copy to the OCR Backup list variable
            self.validationFrame.OCR_backup.append(copy.deepcopy(read_file))
        return

    def ocr_thread_initializer(self, list_images, list_fnames, cur_template, template_paths, roi_templates):
        """Method used to initialize the OCR results procedure multiple threads"""
        self.running = True
        self.dead = False
        self.queue = Queue()
        self.queueStop = Queue()
        self._len_images = len(list_images)
        self.setup_thread(list_images, list_fnames, cur_template, template_paths, roi_templates)
        self.controller.after(100, self.check_queue)

    def setup_thread(self, list_images, list_fnames, cur_template, template_paths, roi_templates):
        """Method used to setup the different threads and to start it"""
        # update displayed info on screen
        current_status = "A ler a fatura: 1 de " + str(self._len_images) + "..."
        self.show_status(current_status, "A correr o procedimento OCR...")
        self.controller.update_idletasks()
        self.ocr_reader = Read_load.OcrReaderThread(self.queue, self.queueStop,
                                                    list_images, list_fnames, cur_template, template_paths,
                                                    roi_templates, self.controller.exe_file_path, daemon=True)
        self.ocr_reader.start()

    def run_tesseract_ocr(self, files_idx):
        # Run Tesseract OCR on user selected invoices and store the results for later validation
        # conversion of files_idx to range if it is not one when provided as input
        self._files_idx = []
        if type(files_idx) is not list and type(files_idx) is not tuple:
            files_idx = [files_idx]
        if len(self.opened_files_tree.files_tree.get_children("")) != 0 and not files_idx:
            # if user does not select anything, get all items and run them through OCR
            idx_files = list(self.opened_files_tree.files_tree.get_children(""))
            self.run_tesseract_ocr(idx_files)
            return None
        elif not files_idx:
            message_boxes("error", "", "Por favor abra os ficheiros antes de proceder com a leitura!")
            return None

        # retrieve number of invoices existent in OCR_Results variable
        self._cur_invoice = len(self.validationFrame.OCR_results)

        # create flag to make sure that the different methods are updated only if OCR results are calculated
        self._enter_if = False
        templates_roi = []
        template_paths = []
        # get the images selected by the user to be read with OCR
        list_images_paths = [self.opened_files_tree.files_tree.item(idx, 'values')[2] for idx in files_idx]
        # get files names
        list_images_names = [self.opened_files_tree.files_tree.item(idx, 'values')[1] for idx in files_idx]

        # Get selected files from files tree and de-select them
        if self.opened_files_tree.files_tree.selection():
            self.opened_files_tree.files_tree.selection_remove(self.opened_files_tree.files_tree.selection())

        # get roi information from app
        cur_template = self.validationFrame.template_combo_list.get()
        roi_template = self.validationFrame.roi[cur_template]
        template_path = get_template_file_path(cur_template, self.controller.exe_file_path)
        # check if roi has a 'neglect' entry in it - flag to state that the template is not frozen
        has_neglect = True if "neglect" in [row[2] for row in roi_template] else False

        if list_images_paths and template_path != "":
            self._enter_if = True
            for image_file in list_images_paths:
                # re-initialize the movable line coordinates, for the case that it has already been modified
                self.validationFrame.new_line_y = 0
                if has_neglect:
                    # class used to ask user for end line position and to modify the template used in the OCR reading
                    self.use_movable_template_end(image_file, cur_template)

                # check if a new y coordinate was provided, if so re-calculate ROI and select correct template
                if self.validationFrame.new_line_y:
                    mod_roi_template, template_path = Read_load.get_correct_template(
                        roi_template, self.validationFrame.new_line_y, template_path)
                else:
                    mod_roi_template = [row for row in roi_template if row[2] != "neglect"]

                templates_roi.append(mod_roi_template)
                template_paths.append(template_path)

        elif template_path == "":
            return message_boxes("warning", "", "Por favor selecione um template antes de proceder...")
        elif not self._enter_if:
            message_boxes("warning", "", "Por favor selecione uma fatura antes de proceder com a leitura...")
            list_of_files, _all_temp_files, last_used_filepath = \
                open_pdf_or_image_file(self, self.controller.all_temp_files, self.controller.main_file_path,
                                       self.controller.last_used_filepath)
            self.controller.all_temp_files = _all_temp_files
            self.controller.last_used_filepath = last_used_filepath
            self.opened_files_tree.update_file_tree(list_of_files)
            self.run_tesseract_ocr("")
            return None

        if self._enter_if:
            self._files_idx = files_idx
            self.validationFrame.run_selected["state"] = "disabled"
            self.ocr_thread_initializer(list_images_paths, list_images_names, cur_template,
                                        template_paths, templates_roi)

    def preview_file(self, event):
        # method to allow the user to preview the selected invoice
        # retrieve form the files_tree the selected invoice
        selected = event.widget.focus()
        if selected != "":
            file_path = event.widget.item(selected, 'values')[2]
            self.imageFrame.show_image(file_path)

    def show_status(self, left_label_input, right_label_input):
        # update messages shown in 'show_status' bar
        if left_label_input != "" and right_label_input != "":
            self.status_bar_left.config(text=left_label_input)
            self.status_bar_right.config(text=right_label_input)
        elif left_label_input != "":
            self.status_bar_left.config(text=left_label_input)
        elif right_label_input != "":
            self.status_bar_right.config(text=right_label_input)

        self.controller.update_idletasks()

    def use_movable_template_end(self, image_file, current_template):
        movable_template = DefineMovingTemplateEnd(self.controller, image_file)
        menu_bar = MovableTemplateMenuBar(movable_template.tip_window, movable_template,
                                          current_template, self.controller.exe_file_path,
                                          self.validationFrame)
        movable_template.tip_window['menu'] = menu_bar
        movable_template.tip_window.protocol("WM_DELETE_WINDOW",
                                             lambda: leave_movable_template(movable_template,
                                                                            self.validationFrame))
        self.controller.wait_window(movable_template.tip_window)
