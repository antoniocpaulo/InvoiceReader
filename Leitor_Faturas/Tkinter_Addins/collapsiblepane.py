# Implementation of Collapsible Pane container

# importing tkinter and ttk modules
import tkinter as tk
from tkinter import ttk
from .TooltipHover import CreateToolTip


class CollapsiblePane(tk.Frame):
    """
     -----USAGE-----
    collapsiblePane = CollapsiblePane(parent,
                          expanded_text =[string],
                          collapsed_text =[string])

    collapsiblePane.pack()
    button = Button(collapsiblePane.frame).pack()
    """

    def __init__(self, parent, expanded_text="<<",
                 collapsed_text=">>"):

        tk.Frame.__init__(self, parent, background="white")

        # These are the class variables
        self.parent = parent
        self._expanded_text = expanded_text
        self._collapsed_text = collapsed_text
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Tkinter variable storing integer value
        self._variable = tk.IntVar()

        # Checkbutton is created but will behave as Button cause in style, Button is passed
        # main reason to do this is Button do not support variable option but checkbutton do
        self._button = ttk.Checkbutton(self, variable=self._variable, width=2, command=self._activate, style="TButton")
        CreateToolTip(self._button, text="Colapsar/Expandir")
        self._button.grid(row=0, column=1, sticky="ne")

        # Add separator
        # self._separator = ttk.Separator(self, orient="horizontal")
        # self._separator.grid(row=0, column=1, sticky="we")

        self.frame = tk.Frame(self, background="white")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure((0, 1, 2), weight=1)

        # This will call activate function of class
        self._activate()

    def _activate(self):
        if not self._variable.get():

            # As soon as button is pressed it removes this widget but is not destroyed means can be displayed again
            self.frame.grid_forget()
            # This will change the text of the checkbutton
            self._button.configure(text=self._collapsed_text)

        elif self._variable.get():
            # increasing the frame area so new widgets could reside in this container
            self.frame.grid(row=0, column=0, sticky="nsew")
            self._button.configure(text=self._expanded_text)

    def toggle(self):
        """Switches the label frame to the opposite state."""
        self._variable.set(not self._variable.get())
        self._activate()
