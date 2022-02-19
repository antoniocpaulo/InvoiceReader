import tkinter as tk
import datetime as dt
from tkinter import ttk
from PIL import Image, ImageTk
from ..Database.login_database import Database, ChangePassword, Register, Login
from ..Aux_Functions.App_AuxFunctions import message_boxes
from ..Aux_Functions.FileManager import FULL_MONTHS, NORM_FONT
from .GUI_HomePage import HomePage


class StartPage(tk.Frame):
    """ Class used as a welcome screen and to ask for user credentials - store information in validated invoices"""

    def __init__(self, parent, controller):
        self.parent = parent
        self.tip_window = None
        self.permission_level = None
        self.__password_entry = None
        self.username_entry = None
        self.__show_hide_btn = None
        self.background_image = None
        self.__last_username = ""
        self.__last_password = ""
        self.canvas_image = None
        
        self._main_file_path = controller.main_file_path
        self._exe_file_path = controller.exe_file_path
        
        self.password_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\password.png").resize((35, 35), Image.LANCZOS))
        self.user_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\user.png").resize((35, 35), Image.LANCZOS))
        self.show_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\show.png").resize((20, 20), Image.LANCZOS))
        self.hide_img = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\hide.png").resize((20, 20), Image.LANCZOS))

        # open database credentials file
        self.db = Database(self._exe_file_path)
        self.db.createTable()

        tk.Frame.__init__(self, parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.background_canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(),
                                           highlightthickness=0)
        self.height = self.winfo_screenheight()
        self.width = self.winfo_screenwidth()
        self.background_canvas.grid(row=0, column=0, sticky="nsew")

        self.login_frame = tk.Frame(self.background_canvas, bg="white")
        self.login_frame.columnconfigure(1, weight=1)

        # disable parent menu bar
        controller.menu_bar.entryconfig("Ficheiro", state="disabled")
        controller.menu_bar.entryconfig("Leitor OCR", state="disabled")
        # proceed to log in
        self.on_enter(controller)

        self.update_idletasks()

        self.canvas_header = self.background_canvas.create_text(self.winfo_screenwidth() // 2,
                                                                int(self.winfo_screenheight() * 0.08),
                                                                text="LEITOR DE FATURAS",
                                                                font=("MS Gothic", 40, "bold"), fill="DodgerBlue4",
                                                                anchor="center")

        date = dt.datetime.now()
        self.canvas_date = self.background_canvas.create_text(self.winfo_screenwidth() // 2,
                                                              int(self.winfo_screenheight() * 0.16),
                                                              text="{} {} {}".format(date.day,
                                                                                     FULL_MONTHS[int(date.month)],
                                                                                     date.year),
                                                              font=("MS Gothic", 20, "bold"), fill="DodgerBlue4",
                                                              anchor="center")

        self.canvas_login_frame = self.background_canvas.create_window(
            self.winfo_screenwidth() // 2, int(self.winfo_screenheight() * 0.5),
            window=self.login_frame, width=self.login_frame.winfo_reqwidth(), anchor="center")

        self.canvas_version = self.background_canvas.create_text(self.winfo_screenwidth() // 2,
                                                                 int(self.winfo_screenheight() * 0.94),
                                                                 text="v1.0",
                                                                 font=("MS Gothic", 18, "bold"), fill="DodgerBlue4",
                                                                 anchor="center")

        self.background_canvas.addtag_all("all")
        self.bind("<Configure>", self.add_background_image)

    def add_background_image(self, event):
        if self.winfo_width() == 1 and self.winfo_height() == 1:
            width = self.winfo_screenwidth()
            height = self.winfo_screenheight()
        else:
            width = self.winfo_width()
            height = self.winfo_height()

        self.background_canvas.config(width=width, height=height)
        self.background_image = None

        self.background_image = ImageTk.PhotoImage(
            Image.open(self._main_file_path + r"\bin\aux_img\background9.png").resize((width, height), Image.LANCZOS))
        self.canvas_image = self.background_canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        self.background_canvas.scale("all", 0, 0, float(event.width) / self.width, float(event.height) / self.height)
        self.background_canvas.itemconfig(self.canvas_login_frame, width=self.login_frame.winfo_reqwidth())

        self.height = event.height
        self.width = event.width

    def on_enter(self, controller):
        """method used to ask the user for its credentials and/or to add a new user"""
        in_frame = tk.Frame(self.login_frame, bg="white")
        username_label = tk.Label(in_frame, image=self.user_img, bg="white", anchor="e")
        password_label = tk.Label(in_frame, image=self.password_img, bg="white", anchor="e")

        self.username_entry = ttk.Entry(in_frame, font="Verdana 11", width=40)
        self.username_entry.insert(0, "Utilizador") if self.__last_username == "" else self.username_entry.insert(
            0, self.__last_username)

        self.username_entry.selection_range(0, tk.END)

        pass_frame = tk.Frame(in_frame, bg="white")
        self.__password_entry = ttk.Entry(pass_frame, show="\u2022", font="Verdana 11", width=40)
        self.__show_hide_btn = tk.Button(pass_frame, image=self.show_img, command=self._toggle_password)
        if self.__last_password == "":
            self.__password_entry.insert(0, "Palavra-Passe")
        else:
            self.__password_entry.insert(0, self.__last_password)
        # GRIDs
        in_frame.grid(row=0, column=0, columnspan=3, padx=30, pady=30, sticky="new")
        username_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2, sticky="w")
        password_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        pass_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="w")
        self.__password_entry.grid(row=0, column=0, sticky="w")
        self.__password_entry.bind("<Return>", lambda e: self.new_login(e, controller))
        self.__show_hide_btn.grid(row=0, column=1, sticky="w")

        login_btn = tk.Button(self.login_frame, text="Login", bg="steel blue", font="Verdana 11 bold",
                              fg="white", width=15, command=lambda: self.new_login(None, controller))
        change_pass_btn = tk.Button(self.login_frame, text="Alterar Palavra-passe", bg="light steel blue", fg="black",
                                    font=NORM_FONT, width=23, command=lambda: self.change_password(controller))
        register_btn = tk.Button(self.login_frame, text="Registar Novo Utilizador", bg="light steel blue", fg="black",
                                 font=NORM_FONT, width=23, command=lambda: self.register_menu(controller))
        login_btn.grid(row=1, column=0, columnspan=3, pady=15)
        change_pass_btn.grid(row=2, column=0, columnspan=3, pady=5)
        register_btn.grid(row=3, column=0, columnspan=3, pady=5)
        empty_label = tk.Label(self.login_frame, text=" ", bg="white")
        empty_label.grid(row=4, column=0, columnspan=3, pady=10)

    def new_login(self, event, controller):
        if self.username_entry.get() != "" and self.__password_entry.get() != "":
            login = Login(self.username_entry.get(), self.__password_entry.get())
            match, username, permission_level = login.validate(self.db)
            if match:
                controller.username = username
                controller.user_permission = permission_level
                self.unbind("<Configure>")
                controller.menu_bar.entryconfig("Ficheiro", state="normal")
                controller.menu_bar.entryconfig("Leitor OCR", state="normal")
                controller.show_frame(HomePage)
            else:
                message_boxes("warning", "Credenciais Login", "Utilizador ou palavra-passe não encontrados!")
                self.on_enter(controller)
                return

    def change_password(self, controller):
        change_pass = ChangePassword(self, self.db, self._main_file_path)
        self.parent.wait_window(change_pass.tip_window)
        if change_pass.success:
            message_boxes("info", "Nova palavra-passe", "Palavra-passe alterada com sucesso!")
            self.on_enter(controller)
        else:
            message_boxes("warning", "Nova palavra-passe", "Palavra-passe não alterada!")

    def register_menu(self, controller):
        register = Register(self, self._main_file_path, self.db)
        register.new_register()
        self.parent.wait_window(register.tip_window)
        if register.success is None:
            return
        elif not register.success:
            message_boxes("warning", "Utilizador Existente", "O nome de utilizador já existe!")
        else:
            message_boxes("info", "Novo Registo", "Utilizador registado com sucesso!")
            self.on_enter(controller)
            return

    def _toggle_password(self):
        if self.__show_hide_btn.cget("image") == str(self.show_img):
            self.__show_hide_btn.config(image=self.hide_img)
            self.__password_entry.config(show="")
        else:
            self.__show_hide_btn.config(image=self.show_img)
            self.__password_entry.config(show="\u2022")

