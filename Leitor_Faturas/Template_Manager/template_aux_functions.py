import os
import tkinter as tk
from PIL import Image, ImageTk

from ..Aux_Functions.FileManager import open_files
from ..OCR_Reader import Read_load
from ..Tkinter_Addins.Custom_Text import CustomText
from .template_files_creator import TemplateCreator


def get_template_file_path(template_name, exec_file_path, from_movable_help=False):
    """ get all the templates from the template directory path"""
    template_path = ""
    template_dir_path = exec_file_path + r'\bin\Templates' if not from_movable_help else \
        exec_file_path + r'\bin\Templates\Movable_Examples'

    if len(os.listdir(template_dir_path)) != 0:
        for f in os.listdir(template_dir_path):
            file_name = str(os.path.split(f)[1]).split(".")[0].lower()
            if template_name.lower() == file_name:
                template_path = os.path.join(template_dir_path, f)
                break
    return template_path


def leave_movable_template(widget, validation_frame):
    # function used to kill the movable window and get the movable line coordinates
    validation_frame.new_line_y = widget.line_y_ratio.get()
    widget.hide_window()


def open_create_template(new_or_select, app, home_page, all_temp_files, main_file_path, exe_file_path, roi_templates,
                         template_paths):
    """ Create a new invoice template or editing the already defined"""
    if new_or_select == "new":
        template_file, all_temp_files, _ = open_files("Seleccione o Template de Fatura:",
                                                      (("Imagem", "*.jpeg *.jpg *.png *.tiff *.tif"),
                                                       ("Ficheiro PDF", "*.pdf"),
                                                       ("Todos", "*.*")), "",
                                                      False,
                                                      home_page, all_temp_files, main_file_path)

        template_file = template_file[0] if type(template_file) is list else template_file

        if template_file:
            TemplateCreator(app, "new", exe_file_path, template_file, Read_load.tk_colors, _, _)
    elif new_or_select == "modify":
        TemplateCreator(app, "edit", exe_file_path, None, Read_load.tk_colors, roi_templates, template_paths)
    return all_temp_files


def read_help_movable_template(template_name, exec_file_path):
    win = tk.Toplevel(bg="white")
    win.title("Ajuda")
    about = """
    Funcionalidade utilizada para definir a linha de referência do template em utilização (ver figura).
    Ao ser definida a linha de referência, a ferramenta ficará melhor habilitada para apresentar leituras correctas.

    O procedimento a utilizar para definir a referência é o seguinte:
    1- Clique no ponto do lado esquerdo onde a linha inicia;
    2- Clique no ponto do lado direito onde a linha termina;
    3- Deverá ser criada automaticamente uma linha a vermelho que será colocada sobre o template
    4- Caso a linha seja apresentada, o utilizador pode fechar o menu.

    Se tiver problemas, por favor contacte por email os seus responsáveis.
    """

    win.rowconfigure(0, weight=1)
    win.columnconfigure(0, weight=1)
    t = CustomText(win, wrap="word", width=100, borderwidth=0, font=("Verdana", 11))
    t.tag_configure("blue", foreground="blue")
    t.grid(row=0, column=1, sticky="nsew")
    t.insert(tk.END, about)
    scroll = tk.Scrollbar(win)
    t.configure(yscrollcommand=scroll.set)
    scroll.config(command=t.yview)
    scroll.grid(row=0, column=2, sticky="ns")
    t.HighlightPattern("^.*? - ", "blue")

    # add image with template to exemplify the movable template function
    template_path = get_template_file_path(template_name, exec_file_path, True)
    template_image = ImageTk.PhotoImage(Image.open(template_path).resize((414, 585), Image.LANCZOS))
    # create canvas widget to show image and allow for drawing of rectangles
    template_label = tk.Label(win, image=template_image, bg="white")
    template_label.grid(row=0, column=0, pady=5, sticky="nsew")

    close_btn = tk.Button(win, text='Fechar', font=("Verdana", 10), command=win.destroy)
    close_btn.grid(row=1, column=0, columnspan=3, pady=5)

    return template_image


def roi_row_parser(template_fields):
    """Function used to convert roi into usable list"""
    clean_list = []
    for row in template_fields:
        aux_list = []
        split_row = row.split(",")
        for entry in split_row:
            if entry != "":
                entry = entry.replace("[", "").replace("]", "").replace(",", "").replace(";", "").replace(
                    "(", "").replace(")", "").replace("\"", "").replace("\n", "").replace("'", "")
                aux_list.append(entry.strip())

        # aggregate each entry in row to a list: [(x1,y1),(x2,y2),var_type,var_name, Name to be Shown]
        clean_list.append([(aux_list[0], aux_list[1]), (aux_list[2], aux_list[3]), aux_list[4],
                           aux_list[5], aux_list[6]])
    return clean_list
