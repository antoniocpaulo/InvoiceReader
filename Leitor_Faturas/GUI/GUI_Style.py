from tkinter import ttk


class GuiStyle(ttk.Style):

    def __init__(self, *args, **kwargs):
        ttk.Style.__init__(self, *args, **kwargs)
        # Pick a theme
        self.theme_use("default")
        # Configure TREEVIEW
        self.configure("Treeview", background="white", foreground="black", rowheight=20,
                       fieldbackground="white", highlightthickness=0, bd=0, borderthickness=0)
        self.configure("Treeview.Heading", background="light steel blue", foreground="black", fieldbackground="white",
                       highlightthickness=0, bd=0, borderthickness=0)
        self.map('Treeview', background=[('selected', 'steel blue')],
                 foreground=[('selected', 'white')], highlightthickness=[('selected', 0)])
        self.map('Treeview.Heading', background=[('active', 'steel blue')], foreground=[('active', 'white')])

        # Configure NOTEBOOK
        self.configure("TNotebook", background="white", foreground="black", fieldbackground="white",
                       highlightthickness=0, bd=0)
        self.configure("TNotebook.Tab", background="steel blue", foreground="white",
                       fieldbackground="white", highlightthickness=0, bd=0)
        self.map('TNotebook.Tab', background=[('selected', 'white')], highlightthickness=[('selected', 1)],
                 foreground=[('selected', 'black')])

        # Configure LABELFRAME
        self.configure("TLabelframe", background="white", foreground="black", fieldbackground="white",
                       highlightthickness=0, labelmargins=4, labeloutside=True)
        self.configure("TLabelframe.Label", background="white", foreground="black", font=("Verdana", 9))

        # Configure COMBOBOX
        self.map('TCombobox', fieldbackground=[('readonly', 'white')])
        self.map('TCombobox', selectbackground=[('readonly', 'white')])
        self.map('TCombobox', selectforeground=[('readonly', 'black')])

        # Configure SCROLLBAR
        self.configure("Horizontal.TScrollbar", gripcount=0,
                       background="light steel blue", lightcolor="light steel blue",
                       troughcolor="steel blue", arrowcolor="black")
        self.configure("Vertical.TScrollbar", gripcount=0,
                       background="light steel blue", lightcolor="light steel blue",
                       troughcolor="steel blue", arrowcolor="black")

        # Configure SEPARATOR
        self.configure("TSeparator", background="black")

        # Configure CHECKBUTTON
        self.configure("TButton", background="light steel blue")

        # Configure Entry
        self.configure("TEntry", foreground="black", fieldbackground='white')
        self.map('TEntry', fieldbackground=[('focus', 'light steel blue')], foreground=[('focus', 'white')])

        """MUDAR O ESTILO DAS COMBOBOX, eventualmente mudar tambem as labels ou botoes
        Esquema de cores a decidir para melhorar o aspecto
        Alterar tambem o formato da barra do menu principal"""

# app_width = 1300
# app_height = 800

# screen_height = app.winfo_screenheight()
# screen_width = app.winfo_screenwidth()

# x_nw_corner = (screen_width / 2) - (app_width / 2)
# y_nw_corner = (screen_height / 2) - (app_height / 2)

# app.attributes("-fullscreen", 2)
# app.geometry(f'{app_width}x{app_height}+{int(x_nw_corner)}+{int(y_nw_corner)}')
