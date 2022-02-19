# Importing Important Libraries
import sqlite3
import bcrypt
import tkinter as tk
import re
from tkinter import ttk
from PIL import Image, ImageTk
from ..Tkinter_Addins.TooltipHover import CreateToolTip

normal_font = ("Verdana", "10")
administrator_password = "*LeiTor_2021.FatUras!"


def _update_check_status(parent, image, row, column, text, text_color):
    widget = tk.Label(parent, image=image, bg="white")
    widget.grid(row=row, column=column, padx=5, sticky="w")
    CreateToolTip(widget, text=text, fg=text_color)


def check_username(test, tw, ok_image, error_image, row, column, db=None, flag="new_user"):
    """method used to check if the input username is alpha-numeric"""
    if test == "" or not re.match(r'^[A-Za-z0-9_]+$', test):
        _update_check_status(tw, error_image, row, column, "Caractéres especiais não permitidos (excepto '_')!", "red")
        return False
    elif flag == "new_user" and db:
        if not db.searchData(test):
            _update_check_status(tw, error_image, row, column, "Nome de utilizador já existente!", "red")
            return False
        else:
            _update_check_status(tw, ok_image, row, column, "OK", "dark green")
            return True
    elif flag == "existing_user" and db:
        if not db.searchData(test):
            _update_check_status(tw, ok_image, row, column, "OK", "dark green")
            return True
        else:
            _update_check_status(tw, error_image, row, column, "Utilizador não encontrado!", "red")
            return False
    else:
        _update_check_status(tw, ok_image, row, column, "OK", "dark green")
        return True


def check_password(test, tw, error_image, ok_image, row, column):
    """method used to check if the password is filled"""
    if test == "":
        _update_check_status(tw, error_image, row, column, "", "red")
        return False
    else:
        _update_check_status(tw, ok_image, row, column, "", "dark green")
        return True


class Database:
    """
     Database Class for sqlite3
     :params conn — sqlite3Connection
     :params curr — cursor
    """

    def __init__(self, exe_file_path):
        try:
            self.conn = sqlite3.connect(exe_file_path + r"\bin\db_login\login.db")
            # try to open database
            self.curr = self.conn.cursor()
        except:
            pass

    def createTable(self):
        """Method for Creating Table in Database"""
        create_table_query = """
                            CREATE TABLE IF NOT EXISTS cred(
                            id Integer PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL,
                            name_user TEXT NOT NULL,
                            employee_id TEXT NOT NULL,
                            permission_level TEXT NOT NULL
                            );
                            """
        self.curr.execute(create_table_query)
        self.conn.commit()

    def insertData(self, data):
        """Method for Inserting Data in Table in Database"""
        insert_query = """
                    INSERT INTO cred(username, password, name_user, employee_id, permission_level)
                    VALUES(?, ?, ?, ?, ?);
                    """
        data = (data,) if type(data) is not tuple else data
        self.curr.execute(insert_query, data)
        self.conn.commit()

    def searchData(self, data):
        """Method for Searching Data in Table in Database """
        search_query = """
                    SELECT * FROM cred WHERE username = (?);
                    """
        data = (data,) if type(data) is not tuple else data
        self.curr.execute(search_query, data)
        rows = self.curr.fetchall()
        return True if not rows else False

    def search_employee_id(self, data):
        """Method for Searching for Number of Employee in Table in Database """
        search_query = """
                    SELECT * FROM cred WHERE employee_id = (?);
                    """
        data = (data,) if type(data) is not tuple else data
        self.curr.execute(search_query, data)
        rows = self.curr.fetchall()
        return True if not rows else False

    def change_password(self, data):
        """Method used for updating a user password, as per user request"""
        change_query = """
                        UPDATE cred SET password = (?) WHERE username = (?)
                        """
        data = (data,) if type(data) is not tuple else data
        self.curr.execute(change_query, data)
        rows = self.curr.fetchall()
        return True if not rows else False

    def validateData(self, data, inputData):
        """Method for Validating Data Table in Database"""
        validate_data = """
                        SELECT * FROM cred WHERE username = (?);
                        """
        data = (data,) if type(data) is not tuple else data
        self.curr.execute(validate_data, data)
        row = self.curr.fetchall()
        try:
            if row[0][1] == inputData[0]:
                if row[0][2] == bcrypt.hashpw(inputData[1].encode(), row[0][2]):
                    return [True, row[0][1], row[0][5]]
                else:
                    return [False, "", ""]
        except IndexError:
            return [False, "", ""]


class ChangePassword:

    def __init__(self, parent, db, main_file_path):
        self.parent = parent
        self._x = parent.winfo_screenwidth() / 2 - 350 / 2
        self._y = parent.winfo_screenheight() / 2 - 180 / 2

        self.db = db
        self.success = None
        self._hashed = None

        # create top level window
        self.tip_window = tw = tk.Toplevel(parent, bg="white")
        tw.wm_geometry(f'{400}x{250}+{int(self._x)}+{int(self._y)}')
        tw.resizable(False, False)
        tw.columnconfigure((0, 1), weight=1)
        tw.protocol("WM_DELETE_WINDOW", self._on_close)

        # bind entry widget to remember_focus method
        tw.bind_class("TEntry", "<FocusOut>", self._remember_focus)

        # create images
        self.error_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\error.png").resize((15, 15), Image.LANCZOS))
        self.ok_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\validate.png").resize((15, 15), Image.LANCZOS))
        self.show_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\show.png").resize((15, 15), Image.LANCZOS))
        self.hide_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\hide.png").resize((15, 15), Image.LANCZOS))

        # create variables
        self._old_attributes_check = False
        self._new_password_check = False
        self._username_image = None
        self._old_password_image = None

        self._username = tk.StringVar()
        self._old_password = tk.StringVar()
        self._new_password = tk.StringVar()
        self._new_password_2 = tk.StringVar()

        # create labels
        change_pass_label = tk.Label(tw, text="Alterar Palavra-passe", font=("Verdana", "11", "bold"),
                                     bg="light steel blue", fg="black")

        username_label = tk.Label(tw, text="Utilizador", font=normal_font, bg="white", fg="black")
        old_pass_label = tk.Label(tw, text="Palavra-passe Antiga", font=normal_font, bg="white", fg="black")
        new_pass_label = tk.Label(tw, text="Nova Palavra-passe", font=normal_font, bg="white", fg="black")
        new_pass_label2 = tk.Label(tw, text="Confirmar Palavra-passe", font=normal_font, bg="white", fg="black")

        # create entry widgets
        self._username_entry = ttk.Entry(tw, textvariable=self._username, font=normal_font)
        pass_frame = tk.Frame(tw, bg="white")
        self._old_pass_entry = ttk.Entry(pass_frame, textvariable=self._old_password, show="\u2022", font=normal_font)
        pass_frame1 = tk.Frame(tw, bg="white")
        self._new_pass_entry = ttk.Entry(pass_frame1, textvariable=self._new_password, show="\u2022",
                                         font=normal_font)
        pass_frame2 = tk.Frame(tw, bg="white")
        self._new_pass2_entry = ttk.Entry(pass_frame2, textvariable=self._new_password_2, show="\u2022",
                                          font=normal_font)

        # create password entry show/hide buttons
        self._show_hide_old_btn = tk.Button(pass_frame, image=self.show_img)
        self._show_hide_new_btn = tk.Button(pass_frame1, image=self.show_img)
        self._show_hide_new2_btn = tk.Button(pass_frame2, image=self.show_img)
        self._show_hide_old_btn.bind("<ButtonRelease-1>", lambda event: self._toggle_password(event, "old"))
        self._show_hide_new_btn.bind("<ButtonRelease-1>", lambda event: self._toggle_password(event, "new"))
        self._show_hide_new2_btn.bind("<ButtonRelease-1>", lambda event: self._toggle_password(event, "new2"))

        # grid system
        change_pass_label.grid(row=0, column=0, pady=15, columnspan=3, sticky="nsew")
        username_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        old_pass_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        new_pass_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        new_pass_label2.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self._username_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky="w")
        pass_frame.grid(row=2, column=1, columnspan=2, pady=5, sticky="w")
        self._old_pass_entry.grid(row=0, column=0, sticky="w")
        self._show_hide_old_btn.grid(row=0, column=1, sticky="w")
        pass_frame1.grid(row=3, column=1, columnspan=2, pady=5, sticky="w")
        self._new_pass_entry.grid(row=0, column=0, sticky="w")
        self._show_hide_new_btn.grid(row=0, column=1, sticky="w")
        pass_frame2.grid(row=4, column=1, columnspan=2, pady=5, sticky="w")
        self._new_pass2_entry.grid(row=0, column=0, sticky="w")
        self._show_hide_new2_btn.grid(row=0, column=1, sticky="w")

        # create local frame to store buttons
        local_frame = tk.Frame(tw, bg="white")
        next_btn = tk.Button(local_frame, text="Validar", bg="steel blue", font="Verdana 10 bold",
                             fg="white", width=10, command=self._validate_change)
        cancel_btn = tk.Button(local_frame, text="Cancelar", bg="steel blue", font="Verdana 10 bold",
                               fg="white", width=10, command=self._on_close)
        local_frame.grid(row=5, column=0, columnspan=3, pady=15, sticky="nsew")
        local_frame.columnconfigure((0, 1), weight=1)
        next_btn.grid(row=0, column=0, padx=5, sticky="e")
        cancel_btn.grid(row=0, column=1, padx=5, sticky="w")

    def _check_old_attributes(self):
        """check if username and old_password exist in database"""
        user_check = check_username(self._username.get(), self.tip_window, self.ok_img, self.error_img, 1, 3, self.db,
                                    "existing_user")
        pass_check = check_password(self._old_password.get(), self.tip_window, self.error_img, self.ok_img, 2, 3)

        if user_check and pass_check:
            # check if username exists and matches the specified password inside the database
            if self.db.validateData(self._username.get(), [self._username.get(), self._old_password.get()]):
                _update_check_status(self.tip_window, self.ok_img, 1, 3, "OK", "dark green")
                _update_check_status(self.tip_window, self.ok_img, 2, 3, "OK", "dark green")
                self._old_attributes_check = True
            else:
                _update_check_status(self.tip_window, self.error_img, 1, 3,
                                     "Utilizador e palavra-passe não correspondentes!", "red")
                _update_check_status(self.tip_window, self.error_img, 2, 3,
                                     "Utilizador e palavra-passe não correspondentes!", "red")
                self._old_attributes_check = False

    def _match_new_passwords(self):
        """check if new passwords are equal and that they are different from the old password"""
        if self._new_password.get() == self._new_password_2.get() and \
                self._new_password.get() != self._old_password.get() and \
                self._new_password_2.get() != self._old_password.get() and self._old_password.get() != "":
            _update_check_status(self.tip_window, self.ok_img, 3, 3, "OK!", "dark green")
            self._new_password_check = True
        else:
            _update_check_status(self.tip_window, self.error_img, 3, 3, "Palavra-passe idêntica à antiga!", "red")

    def _remember_focus(self, event):
        if not self._old_attributes_check:
            self._check_old_attributes() if self._username.get() != "" and self._old_password.get() != "" else ""
        if not self._new_password_check:
            self._match_new_passwords() if self._new_password.get() != "" and \
                                           self._new_password_2.get() != "" else ""

    def _toggle_password(self, event, identifier):
        if event.widget.cget("image") == str(self.show_img):
            event.widget.config(image=self.hide_img)
            if identifier == "old":
                self._old_pass_entry.config(show="")
            elif identifier == "new":
                self._new_pass_entry.config(show="")
            elif identifier == "new2":
                self._new_pass2_entry.config(show="")
        else:
            event.widget.config(image=self.show_img)
            if identifier == "old":
                self._old_pass_entry.config(show="\u2022")
            elif identifier == "new":
                self._new_pass_entry.config(show="\u2022")
            elif identifier == "new2":
                self._new_pass2_entry.config(show="\u2022")

    def _validate_change(self):
        if self._old_attributes_check and self._new_password_check:
            self._salt = bcrypt.gensalt()
            self._hashed = bcrypt.hashpw(self._new_password.get().encode(), self._salt)
            self.success = self.db.change_password((self._hashed, self._username.get()))
            self._on_close()

    def _on_close(self):
        """method used to kill the top level window with the credentials request"""
        tw = self.tip_window
        tw.unbind_class("TEntry", "<FocusOut>")
        self.tip_window = None
        if tw:
            tw.destroy()


class Login:
    """
        Class for Login
        @param username
        @param password
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def validate(self, db):
        data = (self.username,)
        inputData = (self.username, self.password,)
        match, username, permission_level = db.validateData(data, inputData)
        if match:
            return [True, username, permission_level]  # success login
        else:
            return [False, "", ""]  # wrong credentials


class Register(object):

    def __init__(self, parent, main_file_path, db):
        self.parent = parent
        self._main_file_path = main_file_path
        self._x = parent.winfo_screenwidth() / 2 - 350 / 2
        self._y = parent.winfo_screenheight() / 2 - 180 / 2
        self.db = db

        # create top level window
        self.tip_window = tw = tk.Toplevel(parent, bg="white")
        tw.wm_geometry(f'{420}x{280}+{int(self._x)}+{int(self._y)}')
        tw.resizable(False, False)
        tw.columnconfigure((0, 1), weight=1)
        tw.protocol("WM_DELETE_WINDOW", self._on_close)

        # create images
        self.error_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\error.png").resize((15, 15), Image.LANCZOS))
        self.ok_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\validate.png").resize((15, 15), Image.LANCZOS))
        self.show_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\show.png").resize((15, 15), Image.LANCZOS))
        self.hide_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\hide.png").resize((15, 15), Image.LANCZOS))

        # create entry holder variables
        self._name_user_entry = None
        self._employee_id_entry = None
        self._permission_level_box = None
        self._username_entry = None
        self._password_entry = None
        self._error_label = None
        self._show_hide_btn = None

        # holder checks
        self._all_checks = False
        self._name_check = None
        self._check_employee = None
        self._username_check = None
        self._password_check = None
        self._permission_check = True

        # holder validated or not images
        self._name_image = None
        self._employee_image = None
        self._username_image = None
        self._password_image = None
        self._permission_image = None

        # define class variables
        self.success = None
        self._next_btn = None
        self._name_user = tk.StringVar()
        self._employee_id = tk.IntVar()
        self._username = tk.StringVar()
        self._password = tk.StringVar()
        self._permission_level = True
        self._salt = None
        self._hashed = None

    def new_register(self, username="", user_password=""):
        tw = self.tip_window
        tw.bind_class("TEntry", "<FocusOut>", self._remember_focus)
        credentials_label = tk.Label(tw, text="Registar novo utilizador", font=("Verdana", "11", "bold"),
                                     bg="light steel blue", fg="black")
        name_user_label = tk.Label(tw, text="Nome", font=normal_font, bg="white", fg="black")
        employee_id_label = tk.Label(tw, text="Número Mecanográfico", font=normal_font, bg="white", fg="black")
        permission_label = tk.Label(tw, text="Nível de Permissão", font=normal_font, bg="white", fg="black")
        username_label = tk.Label(tw, text="Nome de Utilizador", font=normal_font, bg="white", fg="black")
        password_label = tk.Label(tw, text="Palavra-passe", font=normal_font, bg="white", fg="black")

        self._name_user_entry = ttk.Entry(tw, textvariable=self._name_user, font=normal_font)
        self._name_user_entry.focus_set()
        self._employee_id_entry = ttk.Entry(tw, textvariable=self._employee_id, font=normal_font)
        self._permission_level_box = ttk.Combobox(tw, value=["Utilizador", "Administrator"], font=normal_font,
                                                  state="readonly")
        self._permission_level_box.current(0)
        self._permission_level_box.bind("<<ComboboxSelected>>", self._grab_permission_level)
        self._grab_permission_level()
        self._username_entry = ttk.Entry(tw, textvariable=self._username, font=normal_font)
        self._username_entry.insert(0, username)
        # create password frame to hold both entry and image
        pass_frame = tk.Frame(tw, bg="white")
        self._password_entry = ttk.Entry(pass_frame, textvariable=self._password, show="\u2022", font=normal_font)
        self._password_entry.insert(0, user_password)
        self._show_hide_btn = tk.Button(pass_frame, image=self.show_img, command=self._toggle_password)

        # GRID system
        credentials_label.grid(row=0, column=0, pady=15, columnspan=3, sticky="nsew")
        name_user_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        employee_id_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        permission_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        username_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        password_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self._name_user_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky="w")
        self._employee_id_entry.grid(row=2, column=1, columnspan=2, pady=5, sticky="w")
        self._permission_level_box.grid(row=3, column=1, columnspan=2, pady=5, sticky="w")
        self._username_entry.grid(row=4, column=1, columnspan=2, pady=5, sticky="w")
        pass_frame.grid(row=5, column=1, columnspan=2, pady=5, sticky="w")
        self._password_entry.grid(row=0, column=0, sticky="w")
        self._show_hide_btn.grid(row=0, column=1, sticky="w")

        # Create buttons inside frame
        local_frame = tk.Frame(tw, bg="white")
        self._next_btn = tk.Button(local_frame, text="Registar", bg="steel blue", font="Verdana 10 bold",
                                   fg="white", width=10, command=self._check_all_ok)
        cancel_btn = tk.Button(local_frame, text="Cancelar", bg="steel blue", font="Verdana 10 bold",
                               fg="white", width=10, command=self._on_close)
        local_frame.grid(row=6, column=0, columnspan=3, pady=20, sticky="nsew")
        local_frame.columnconfigure((0, 1), weight=1)
        self._next_btn.grid(row=0, column=0, padx=5, sticky="e")
        cancel_btn.grid(row=0, column=1, padx=5, sticky="w")

    def _add_record(self):
        """method used to add record to database"""
        if self.db.searchData(self._username.get()):
            data = (self._username.get(), self._hashed, self._name_user.get(), self._employee_id.get(),
                    self._permission_level)
            self.db.insertData(data)
            self.success = True
            self._on_close()
        else:
            self.success = False

    def _check_all_ok(self, event=None):
        self._remember_focus()
        if self._name_check and self._check_employee and self._username_check and self._password_check and \
                self._permission_check:
            self._salt = bcrypt.gensalt()
            self._hashed = bcrypt.hashpw(self._password.get().encode(), self._salt)
            self._add_record()

    def _check_name(self):
        """method used to check if the name contains only letters and or spaces"""
        self._name_user.get()
        valid = [True if char.isalpha() or char.isspace() else False for char in self._name_user.get()]
        if self._name_user.get() == "" or False in valid:
            _update_check_status(self.tip_window, self.error_img, 1, 2, "", "red")
            self._name_check = False
        else:
            _update_check_status(self.tip_window, self.ok_img, 1, 2, "", "dark green")
            self._name_check = True

    def _check_employee_id(self):
        """method used to check if the employee id contain only numbers"""
        try:
            test = int(self._employee_id.get())
        except ValueError:
            _update_check_status(self.tip_window, self.error_img, 2, 2, "Definir número!", "red")
            self._check_employee = False
        else:
            if test != 0:
                # search in database if employee ID already exists
                if self.db.search_employee_id(test):
                    _update_check_status(self.tip_window, self.ok_img, 2, 2, "OK", "dark green")
                    self._check_employee = True
                else:
                    _update_check_status(self.tip_window, self.error_img, 2, 2,
                                         "Número Mecanográfico já existente!", "red")
                    self._check_employee = False

    def _grab_permission_level(self, event=None):
        """get current template from permission level list"""
        self._permission_level = self._permission_level_box.get()
        if self._permission_level == "Administrator":
            self._permission_check = self._get_admin_privileges()
            if not self._permission_check:
                _update_check_status(self.tip_window, self.error_img, 3, 2, "Permissão não atribuída!", "red")
                self._permission_check = False
            else:
                _update_check_status(self.tip_window, self.ok_img, 3, 2, "Permissão atribuída!", "dark green")
        else:
            self._permission_image.grid_forget() if self._permission_image else False
            _update_check_status(self.tip_window, self.ok_img, 3, 2, "Permissão atribuída!", "dark green")
            self._permission_check = True

    def _get_admin_privileges(self):
        admin = AdministratorPrivileges(self.tip_window, self._x, self._y, self._main_file_path)
        self.parent.wait_window(admin.admin_tw)
        return admin.validation_ok

    def _remember_focus(self, event=None):
        if not self.success:
            self._check_name() if self._name_user.get() != "" else ""
            if self._password.get() not in ["", "Palavra-passe"]:
                self._password_check = check_password(self._password.get(), self.tip_window, self.error_img,
                                                      self.ok_img, 5, 2)
            if self._username.get() not in ["", "Utilizador"]:
                self._username_check = check_username(self._username.get(), self.tip_window, self.ok_img,
                                                      self.error_img, 4, 2, self.db, "new_user")
            self._check_employee_id() if self._employee_id.get() != "" else ""

    def _toggle_password(self):
        if self._show_hide_btn.cget("image") == str(self.show_img):
            self._show_hide_btn.config(image=self.hide_img)
            self._password_entry.config(show="")
        else:
            self._show_hide_btn.config(image=self.show_img)
            self._password_entry.config(show="\u2022")

    def _on_close(self):
        """method used to kill the top level window with the credentials request"""
        tw = self.tip_window
        tw.unbind_class("TEntry", "<FocusOut>")
        self.tip_window = None
        if tw:
            tw.destroy()


class AdministratorPrivileges(object):

    def __init__(self, parent, x, y, main_file_path):

        self.admin_tw = tw = tk.Toplevel(parent, bg="white")
        self.admin_tw.wm_geometry(f'{300}x{180}+{int(x)}+{int(y)}')
        self.admin_tw.resizable(False, False)
        self.admin_tw.columnconfigure((0, 1, 2), weight=1)
        self.admin_tw.protocol("WM_DELETE_WINDOW", self._admin_on_close)

        # load show or hide button images
        self.show_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\show.png").resize((15, 15), Image.LANCZOS))
        self.hide_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\hide.png").resize((15, 15), Image.LANCZOS))
        self.password_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\password.png").resize((20, 20), Image.LANCZOS))
        self.user_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\user.png").resize((20, 20), Image.LANCZOS))

        self.validation_ok = False
        self._admin_user = tk.StringVar()
        self._admin_password = tk.StringVar()

        administrator_label = tk.Label(tw, text="Login Administrador", font=("Verdana", "10", "bold"),
                                       bg="white", fg="navy")
        admin_user = tk.Label(tw, image=self.user_img, bg="white")
        admin_password = tk.Label(tw, image=self.password_img, bg="white")
        self._admin_user_entry = tk.Entry(tw, textvariable=self._admin_user, font=normal_font)
        self._admin_user_entry.focus_set()
        pass_frame = tk.Frame(tw, bg="white")
        self._admin_pass_entry = tk.Entry(pass_frame, textvariable=self._admin_password,
                                          show="\u2022", font=normal_font)
        self._show_hide_btn = tk.Button(pass_frame, image=self.show_img, command=self._toggle_password)

        administrator_label.grid(row=0, column=0, padx=10, pady=5, columnspan=3, sticky="nsew")
        admin_user.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self._admin_user_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky="w")
        admin_password.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        pass_frame.grid(row=2, column=1, columnspan=2, pady=5, sticky="w")
        self._admin_pass_entry.grid(row=0, column=0, sticky="w")
        self._show_hide_btn.grid(row=0, column=1, sticky="w")

        local_frame = tk.Frame(tw, bg="white")
        next_btn = tk.Button(local_frame, text="Validar", bg="white", font=normal_font, fg="navy",
                             command=lambda: self._validate_admin())
        cancel_btn = tk.Button(local_frame, text="Cancelar", bg="white", font=normal_font,
                               command=self._admin_on_close)
        local_frame.grid(row=3, column=0, columnspan=3, pady=20, sticky="nsew")
        local_frame.columnconfigure((0, 1), weight=1)
        next_btn.grid(row=0, column=0, padx=10, sticky="e")
        cancel_btn.grid(row=0, column=1, padx=10, sticky="w")

    def _admin_on_close(self):
        """method used to kill the top level window with the credentials request"""
        tw = self.admin_tw
        self.admin_tw = None
        if tw:
            tw.destroy()

    def _toggle_password(self):
        if self._show_hide_btn.cget("image") == str(self.show_img):
            self._show_hide_btn.config(image=self.hide_img)
            self._admin_pass_entry.config(show="")
        else:
            self._show_hide_btn.config(image=self.show_img)
            self._admin_pass_entry.config(show="\u2022")

    def _validate_admin(self):
        if self._admin_user.get() == "admin" and self._admin_password.get() == administrator_password:
            self.validation_ok = True
            self._admin_on_close()
        else:
            self.validation_ok = False
