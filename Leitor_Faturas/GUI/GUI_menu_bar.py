import tkinter as tk
from ..Aux_Functions.App_AuxFunctions import read_help


class MenuBar(tk.Menu):
    """ Class used to store information regarding the menu bar arrangement of the GUI interface """

    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, master=parent, *args, **kwargs)
        # create "File" menu bar entry
        file_menu = tk.Menu(self, tearoff=0)  # do not menu tear off
        file_menu.add_command(label="Abrir Fatura(s)", command=self._open_pdf_image_files)
        file_menu.add_command(label="Abrir Fatura(s) Lida(s)", command=self._load_existent_invoice_results)
        file_menu.add_command(label="Gravar Fatura(s) Validadas", command=self._prepare_save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self._on_delete)

        # create "OCR Reader" menu bar entry
        ocrReader = tk.Menu(self, tearoff=0)
        ocrReader.add_command(label="Ler Fatura(s) Aberta(s)", command=self._hook_run_tesseract_ocr)
        ocrReader.add_command(label="Eliminar Leitura Actual", command=self._hook_delete_reading)
        ocrReader.add_separator()
        ocrReader.add_command(label="Criar novo template", command=self._open_create_template)
        ocrReader.add_command(label="Alterar template existente", command=self._open_modify_template)

        # create "OCR Reader" menu bar entry
        HelpMenu = tk.Menu(self, tearoff=0)
        HelpMenu.add_command(label="Ler Ajuda", command=read_help)

        self.add_cascade(label="Ficheiro", menu=file_menu)
        self.add_cascade(label="Leitor OCR", menu=ocrReader)
        self.add_cascade(label="Ajuda", menu=HelpMenu)

        self.controller = parent
    
    def _hook_run_tesseract_ocr(self):
        self.controller.event_generate('<<HookRunOCR>>')
        
    def _hook_delete_reading(self):
        self.controller.event_generate('<<HookDeleteReading>>')
        
    def _load_existent_invoice_results(self):
        self.controller.event_generate('<<LoadExistentResults>>')
    
    def _open_create_template(self):
        self.controller.event_generate('<<OpenCreateTemplate>>')
    
    def _open_modify_template(self):
        self.controller.event_generate('<<OpenModifyTemplate>>')
    
    def _open_pdf_image_files(self):
        self.controller.event_generate('<<OpenPDForImagefiles>>')
    
    def _on_delete(self):
        self.controller.event_generate('<<CloseApp>>')
    
    def _prepare_save_file(self):
        self.controller.event_generate('<<PrepareFileSave>>')
        