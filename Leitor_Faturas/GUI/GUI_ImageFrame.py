import tkinter as tk
from PIL import Image, ImageTk
from ..Aux_Functions.App_AuxFunctions import message_boxes
from ..Tkinter_Addins.CanvasImageClass import CanvasImage
from ..Tkinter_Addins.TooltipHover import CreateToolTip


class ImageFrame(tk.Frame):

    def __init__(self, parent, main_file_path, **kwargs):
        tk.Frame.__init__(self, master=parent, bg="white", **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.backup_path = main_file_path + r"\bin\aux_img\background6.jpg"
        self.canvas_image = CanvasImage(self, path=self.backup_path)
        self.canvas_image.grid(row=0, column=0, sticky="nsew")

        frame1 = tk.Frame(self, bg="white")
        self.o_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\zoom_in.png").resize((30, 30), Image.LANCZOS))
        self.o_img1 = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\delete.png").resize((30, 30), Image.LANCZOS))
        self.o_img2 = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\zoom_fit.png").resize((30, 30), Image.LANCZOS))
        self.o_img3 = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\zoom_out.png").resize((30, 30), Image.LANCZOS))

        zoom_in = tk.Button(frame1, image=self.o_img, relief="flat", bg="white",
                            command=lambda: self.canvas_image.zoom("in"))
        delete_img = tk.Button(frame1, image=self.o_img1, relief="flat", bg="white", fg="red",
                               command=lambda: self.canvas_image.canvas.grid_forget())
        # command=self.frame0.grid_forget)
        zoom_fit = tk.Button(frame1, image=self.o_img2, relief="flat", bg="white",
                             command=self.fit_canvas_image)
        zoom_out = tk.Button(frame1, image=self.o_img3, relief="flat", bg="white",
                             command=lambda: self.canvas_image.zoom("out"))

        frame1.grid(row=1, column=0, sticky="se")
        zoom_in.grid(row=0, column=0, pady=10, padx=5, sticky="se")
        delete_img.grid(row=0, column=1, pady=10, padx=5, sticky="se")
        zoom_fit.grid(row=0, column=2, pady=10, padx=5, sticky="se")
        zoom_out.grid(row=0, column=3, pady=10, padx=5, sticky="se")

        CreateToolTip(zoom_in, text="Aumentar")
        CreateToolTip(delete_img, text="Remover Imagem")
        CreateToolTip(zoom_fit, text="Ajustar Imagem")
        CreateToolTip(zoom_out, text="Diminuir")

    def fit_canvas_image(self):
        if self.canvas_image:
            self.canvas_image.fit()
        else:
            return

    def show_image(self, file_path="", load_backup=False):
        """method to show image using canvas"""
        if load_backup:
            file_path = self.backup_path
        if file_path != "":
            if type(file_path) is list:
                file_path = file_path[0]
            if self.canvas_image:
                try:
                    self.canvas_image.destroy()
                except AttributeError:
                    pass
            self.canvas_image = CanvasImage(self, path=file_path)
            self.canvas_image.grid(row=0, column=0, sticky="nsew")
            self.update_idletasks()
            self.canvas_image.fit()
        else:
            message_boxes("error", "Erro Template", "Falha no carregamento do template, verifique se está disponível.")
