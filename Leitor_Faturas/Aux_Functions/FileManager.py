import json
import os
import pdf2image
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image

from .App_AuxFunctions import message_boxes

# define font types and sizes to be used by the app
LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
MEDIUM_FONT = ("Verdana", 9)
SMALL_FONT = ("Verdana", 8)

FULL_MONTHS = {1: 'Janeiro', 2: 'Fevereiro', 3: u'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
               9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}


def create_temp_path(root_path):
    if not os.path.exists(root_path):
        os.makedirs(root_path)
        os.chdir(root_path)
    return root_path


def convert_pdf_to_images(list_of_files, home_page, all_temp_files, main_file_path):
    """convert files if in pdf format, else open selected files and compile loaded_images list"""
    images_paths = []
    # enter loop to cover all provided files by the user
    if type(list_of_files) is str:
        list_of_files = [list_of_files]

    for file_path in list_of_files:
        extension = os.path.splitext(file_path)[-1].lower()
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        # if file extension is .pdf proceed to convert the pdf files to images, and ask if user wants to save
        try:
            if extension == ".pdf":
                if len(list_of_files) > 1:
                    home_page.show_status("A converter ficheiro PDF para imagem...", "")
                else:
                    home_page.show_status("A converter ficheiros PDF para imagens...", "")

                images = pdf2image.convert_from_path(str(file_path))
                # images = pdf2image.convert_from_path(str(file_path), poppler_path=poppler_path_pdf)
                images_paths = save_converted_pdf_files_to_images(images, file_name, images_paths,
                                                                  all_temp_files, main_file_path)
            elif extension in [".jpg", ".png", ".jpeg", ".tiff", ".tif"]:
                images_paths.append(file_path)
                if file_path not in all_temp_files:
                    root_path = create_temp_path(main_file_path + "\\Imagens_de_Faturas\\")
                    shutil.copyfile(file_path, root_path + file_name + extension)
                    all_temp_files.append(root_path + file_name + extension)
            else:
                message_boxes("warning", "", "Por favor seleccione um ficheiro com formato compatível.." + "\n" +
                              "pdf ou .jpg, .png, .jpeg, .tiff, .tif")
        except pdf2image.pdf2image.PDFPageCountError:
            message_boxes("error", "PDFPageCountError",
                          "pdfinfo, which is part of poppler-utils, was unable to get the page count from the PDF file")
        except pdf2image.pdf2image.PDFInfoNotInstalledError:
            message_boxes("error", "PDFInfoNotInstalledError",
                          "pdfinfo, which is part of poppler-utils, was not found on your system")
        except pdf2image.pdf2image.PDFSyntaxError:
            message_boxes("error", "PDFSyntaxError",
                          "convert_from_path is called using strict=True and the input PDF contained a syntax error")

    home_page.show_status("Terminado!", "")
    return images_paths, all_temp_files


def load_json_file(file):
    with open(file, 'r') as opened_file:
        return json.load(opened_file)


def open_pdf_or_image_file(home_page=None, all_temp_files="", main_file_path="", last_used_filepath=""):
    """ Open a pdf or image file for editing. """
    list_of_files, all_temp_files, last_used_filepath = open_files("Seleccione a(s) Fatura(s) para ser(em) lida(s):",
                                                                   (("Ficheiros PDF", "*.pdf"),
                                                                    ("Imagens", "*.jpeg *.jpg *.png *.tiff *.tif")),
                                                                   last_used_filepath,
                                                                   True, home_page, all_temp_files, main_file_path)
    return list_of_files, all_temp_files, last_used_filepath


def open_files(title, filetypes, last_used_filepath="",
               allow_multiple=True, home_page=None, all_temp_files="", main_file_path=""):
    """ Method used to read files and store/updates variables """
    if not filetypes:
        filetypes = ("Todos os ficheiros", "*.*")

    if last_used_filepath == "":
        list_of_files = tk.filedialog.askopenfilename(title=title, filetypes=filetypes, multiple=allow_multiple)
    else:
        list_of_files = tk.filedialog.askopenfilename(initialdir=last_used_filepath, title=title,
                                                      filetypes=filetypes, multiple=allow_multiple)

    try:
        last_used_filepath = os.path.dirname(os.path.abspath(str(list_of_files[0])))
    except IndexError:
        last_used_filepath = os.path.dirname("")

    if list_of_files == "":
        answer = message_boxes("askyesno", "Não foi possível abrir o template!", "Deseja tentar novamente?")
        if answer:
            list_of_files = open_files(title, filetypes, last_used_filepath, allow_multiple,
                                       home_page, all_temp_files, main_file_path)
        else:
            return list_of_files, all_temp_files, last_used_filepath

    list_of_files, all_temp_files = convert_pdf_to_images(list_of_files, home_page,
                                                          all_temp_files, main_file_path)

    return list_of_files, all_temp_files, last_used_filepath


def prepare_file_save(validation_frame, exe_file_path, save_all=False, to_quit=True):
    """function used to:
        1 - retrieve all files from validation tree and save them to a folder selected by the user
        2 - build the file where the validated results are to be stored
    """
    if save_all:
        files_to_save = []
        images_to_save = []
        files_names = []
        # run through all OCR results and check if invoice is validated, if so add it to files to be saved
        if validation_frame.OCR_results:
            for result in validation_frame.OCR_results:
                if result[4]:  # is validated
                    files_to_save.append(result)  # result[1])  # OCR results
                    images_to_save.append(result[2])  # image path
                    files_names.append(result[5])  # file name
        else:  # results not existent
            message_boxes("warning", "Gravar Faturas", "Faturas validadas inexistentes, pedido não concretizado")
            return
    else:
        current_invoice = validation_frame.current_invoice
        files_to_save = validation_frame.OCR_results[current_invoice]  # [1]
        images_to_save = validation_frame.OCR_results[current_invoice][2]
        files_names = validation_frame.OCR_results[current_invoice][5]

    # Save image files to pdf's and validated OCR results - store them in user specified directory
    save_ocr_results_to_directory(images_to_save, files_to_save, files_names, exe_file_path)

    # ask if user wants to delete saved invoices, only if app is not quitting next
    if not to_quit:
        answer = message_boxes("askyesno", "Eliminar Fatura Gravada?", "Quer eliminar a(s) fatura(s) gravada(s)?")
        if answer:
            if save_all:
                for k, result in enumerate(validation_frame.OCR_results):
                    if result[4]:  # if invoice is validated
                        validation_frame.delete_reading()
            else:
                validation_frame.delete_reading()
    return


def save_converted_pdf_files_to_images(images, file_name, images_paths, all_temp_files, main_file_path):
    """ save the images resultant from the pdf files to the temporary file path
        compiles a new directory if non-existent to store temporary pdf_files"""

    root_path = create_temp_path(main_file_path + "\\Imagens_de_Faturas\\")

    if not type(images) is list or (type(images) is list and len(images) == 1):
        image_path = f'{root_path}{file_name}.tiff'
        images[0].save(image_path, 'TIFF') if type(images) is list else images.save(image_path, 'TIFF')
        images_paths.append(image_path)
        if image_path not in all_temp_files:
            all_temp_files.append(image_path)
    else:  # conditional for multi-page pdfs
        for i in range(len(images)):
            image_path = f'{root_path}{file_name}_{i}.tiff'
            images[i].save(image_path, 'TIFF')
            images_paths.append(image_path)
            if image_path not in all_temp_files:
                all_temp_files.append(image_path)

    return images_paths


def save_ocr_results_to_directory(images_paths, files_to_save, files_names, exec_file_path):
    """ save convert pdf files to windows directory"""
    if not os.path.exists(exec_file_path + r'\Ficheiros_Exportados'):
        os.makedirs(exec_file_path + r'\Ficheiros_Exportados')
    dir_name = filedialog.askdirectory(title="Defina directório para armanezamento de ficheiros:",
                                       initialdir=exec_file_path + r'\Ficheiros_Exportados')
    for k, img_file in enumerate(images_paths):
        if type(files_names) is list:
            only_name = files_names[k][0:files_names[k].find(".")]
            file_path = dir_name + "/" + only_name
            save_result = files_to_save[k]
            img_file = img_file[0]
        else:
            only_name = files_names[0:files_names.find(".")]
            file_path = dir_name + "/" + only_name
            save_result = files_to_save
        if os.path.exists(file_path + ".pdf"):
            answer = message_boxes("askyesno", "Subtituir ficheiro?", "Quer substituir o ficheiro existente?")
            if answer == 0:
                continue
        pil_image = Image.open(img_file)
        pil_image.save(file_path + ".pdf", format="pdf")
        # Serialize data into file:
        with open(file_path + ".json", 'w') as f:
            json.dump(save_result, f, indent=2)
    return
