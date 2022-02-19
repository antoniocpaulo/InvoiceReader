import tkinter as tk
from .template_aux_functions import read_help_movable_template, leave_movable_template


class MovableTemplateMenuBar(tk.Menu):
    """ Class used to store information regarding the menu bar arrangement of the template interface """

    def __init__(self, parent, widget, current_template, exe_file_path, validation_frame):
        tk.Menu.__init__(self, parent)
        # create "File" menu bar entry
        file_menu = tk.Menu(self, tearoff=0)  # do not menu tear off
        file_menu.add_command(label="Exit", command=lambda: leave_movable_template(widget, validation_frame))
        # create "File" menu bar entry
        help_menu = tk.Menu(self, tearoff=0)  # do not menu tear off
        help_menu.add_command(label="Ajuda", command=lambda: self._read_help(current_template))
        help_menu.add_command(label="Ver tutorial", command=self._watch_example_video)

        self.add_cascade(label="Ficheiro", menu=file_menu)
        self.add_cascade(label="Ajuda", menu=help_menu)

        self.template_help_image = None
        self._exe_file_path = exe_file_path

    def _watch_example_video(self):
        """ method used to exemplify the usage of the template top level window"""
        pass

    def _read_help(self, current_template):
        """ method used to load input file (or other source) with instructions and store its contents to tkinter
        widget - the goal is to allow the user to fully understand the purpose of the top level window"""
        self.template_help_image = None
        self.template_help_image = read_help_movable_template(current_template, self._exe_file_path)
        return
