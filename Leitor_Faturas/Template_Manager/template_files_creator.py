import os
import pandas
import random
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from ..Aux_Functions.App_AuxFunctions import autoscroll, message_boxes
from .utils import NORM_FONT, SMALL_FONT
from .utils import admissible_var_description, get_resized_img
from .templates_treeview import TemplatesTreeview
from ..Tkinter_Addins.TooltipHover import CreateToolTip
from ..Tkinter_Addins.hover_button import HoverButton


class TemplateCreator(tk.Toplevel):

    def __init__(self, parent=None, edit_or_new="new", main_file_path="", template_path="", tk_colors=None,
                 existing_roi_templates=None, template_paths=None, **kwargs):
        tk.Toplevel.__init__(self, master=parent, bg="white", **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.destroy_window)
        self.attributes('-transparentcolor', '#60b26c')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.parent = parent
        self.__edit_or_new = edit_or_new
        self.tk_colors = tk_colors

        self.template_title = tk.StringVar(self, "")

        # use parent window dimensions to resize template image
        self.__w_height = parent.winfo_height()
        self.__w_width = parent.winfo_width()
        self.__factor_resize = 0.6
        self.geometry("+%d+%d" % (int(self.__w_width / 3), int(self.__w_height / 3)))

        # set auxiliary variables
        self.__main_path = main_file_path
        self.roi = []
        self.__var_type = ""
        self.__var_name = ""
        self.__var_description = ""
        self.canvas = None
        self.container = None
        self._image_id = None
        self.temp_img = None
        self.img_width = None
        self.img_height = None
        self._aux_top = None
        self._expanding_rectangle = None
        self._expanding_rectangle_color = ""
        self.modifying_existent_rectangle = None
        self.identified_row = None
        self.__abort_rectangle_creation = False
        self.rectangles_list = []
        self.rectangles_colors_list = []
        self.__filter = Image.ANTIALIAS

        # load image and resize it to make sure it fits in the user screen
        if self.__edit_or_new == "edit":
            self.existing_roi_templates = existing_roi_templates
            self.existing_templates_paths = template_paths
            self.template_path = self.existing_templates_paths[list(self.existing_templates_paths.keys())[0]]
            self.__temp_pil_img = get_resized_img(Image.open(self.template_path),
                                                  int(self.__factor_resize * self.__w_width),
                                                  int(self.__factor_resize * self.__w_height))
        else:
            self.template_path = template_path
            self.__temp_pil_img = get_resized_img(Image.open(self.template_path),
                                                  int(self.__factor_resize * self.__w_width),
                                                  int(self.__factor_resize * self.__w_height))

        # create canvas widget to show image and allow for drawing of rectangles
        self.create_canvas()

        # ask user to set template name
        self.__set_template_name(self.__w_width / 2 - 40, self.__w_height / 2 - 20)

        # create treeview to hold the information for the user
        self.tree_frame_holder = tk.Frame(self, bg="white")
        self.tree_frame_holder.columnconfigure(0, weight=1)
        self.tree_frame_holder.rowconfigure(3, weight=1)
        self.tree_frame_holder.grid(row=0, column=1, sticky="nsew")
        self._vsb = ttk.Scrollbar(self.tree_frame_holder, orient="vertical")
        self.roi_tree = TemplatesTreeview(self.tree_frame_holder, height=15,
                                          yscrollcommand=lambda f, l: autoscroll(self._vsb, f, l))
        self._vsb['command'] = self.roi_tree.yview

        self.roi_tree.bind("<Motion>", self.identify_hover_row)
        self.roi_tree.bind('<Double-1>', self._change_tree_entry)
        self.roi_tree.tag_configure('oddrow', background="white")
        self.roi_tree.tag_configure('evenrow', background="gray80")
        self.roi_tree.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self._vsb.grid(row=1, column=1, sticky="ns")

        # build frame to hold template buttons
        buttons_frame = tk.Frame(self.tree_frame_holder, bd=0, bg="white")
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky="e", pady=10)

        empty_lbl = tk.Label(self.tree_frame_holder, text="", bg="light steel blue")
        empty_lbl.grid(row=3, column=0, columnspan=2, sticky="nsew")

        # delete last rectangle from canvas and ROI
        self.del_sel_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\cell_delete.png").resize((30, 30), Image.LANCZOS))
        button_del_selected = tk.Button(buttons_frame, image=self.del_sel_img, relief="flat", bg="white",
                                        command=self.__delete_selected)
        button_del_selected.grid(row=0, column=0, sticky="e")

        # delete last rectangle from canvas and ROI
        self.del_last_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\garbage.png").resize((30, 30), Image.LANCZOS))
        button_del_last = tk.Button(buttons_frame, image=self.del_last_img, relief="flat", bg="white",
                                    command=self.__delete_last_figure)
        button_del_last.grid(row=0, column=1, sticky="e")

        # delete all rectangles from canvas and reset ROI
        self.del_all_img = ImageTk.PhotoImage(
            Image.open(main_file_path + r"\bin\aux_img\delete.png").resize((30, 30), Image.LANCZOS))
        button_del_all = tk.Button(buttons_frame, image=self.del_all_img, relief="flat", bg="white",
                                   command=self.__delete_all_figures)
        button_del_all.grid(row=0, column=2, sticky="e")

        if self.__edit_or_new == "edit":
            title_frame = tk.Frame(self.tree_frame_holder, bg="white")
            title_frame.grid(row=0, column=0, padx=10, pady=15)
            title_label = tk.Label(title_frame, text="Tabela Resumo de Template: ", bd=1, bg="white",
                                   font=("Verdana", "10", "bold"))
            title_label.grid(row=0, column=0, padx=5)

            self.template_combolist = ttk.Combobox(title_frame, value=list(self.existing_roi_templates.keys()),
                                                   font=NORM_FONT, state="readonly", justify="center")
            self.template_combolist.current(0)
            self.template_combolist.configure(width=len(max(list(self.existing_roi_templates.keys()), key=len)))
            self.template_combolist.bind("<<ComboboxSelected>>", self.grab_chosen_template)
            self.template_combolist.grid(row=0, column=1, padx=5)

            # fill existing roi data
            self.add_editable_data(self.existing_roi_templates[list(template_paths.keys())[0]])
            # edit template name button
            self.save_roi_img = ImageTk.PhotoImage(
                Image.open(main_file_path + r"\bin\aux_img\save.png").resize((30, 30), Image.LANCZOS))
            button_save_roi = tk.Button(buttons_frame, image=self.save_roi_img, relief="flat", bg="white",
                                        command=self.__save_roi_changes)
            button_save_roi.grid(row=0, column=3, sticky="e")
            CreateToolTip(button_save_roi, text="Gravar Edição de Template")
        else:
            title_label = tk.Label(self.tree_frame_holder, text="Tabela Resumo de Template", bd=1, bg="white",
                                   font=("Verdana", "10", "bold"))
            title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=15)

            # edit template name button
            self.edit_name_img = ImageTk.PhotoImage(
                Image.open(main_file_path + r"\bin\aux_img\edit_name.png").resize((30, 30), Image.LANCZOS))
            button_name = tk.Button(buttons_frame, image=self.edit_name_img, relief="flat", bg="white",
                                    command=lambda: self.__set_template_name(parent.winfo_x() + self.img_width / 2,
                                                                             parent.winfo_y() + self.img_height / 2))
            button_name.grid(row=0, column=3, sticky="e")
            CreateToolTip(button_name, text="Editar Nome Template")

        # Assign floating labels to buttons with images
        CreateToolTip(button_del_selected, text="Apagar Entrada Seleccionada")
        CreateToolTip(button_del_last, text="Apagar Última Entrada")
        CreateToolTip(button_del_all, text="Apagar Todas as Entradas")

    def _add_point_coordinates(self, event):
        """method used to add initial point coordinates to holding list and to start motion event"""
        if self.outside(event.x, event.y) or self.inside_other_rectangle(event.x, event.y):
            return  # register only if coordinates inside image and outside other rectangles

        else:
            self._expanding_rectangle_color = random.choice(self.tk_colors)
            self._expanding_rectangle = self.canvas.create_rectangle(event.x, event.y, event.x + 1, event.y + 1,
                                                                     fill=self._expanding_rectangle_color)
        return

    def add_editable_data(self, template_roi):
        self.roi = template_roi
        for k, row in enumerate(template_roi):
            x1, y1 = float(template_roi[k][0][0]), float(template_roi[k][0][1])
            x2, y2 = float(template_roi[k][1][0]), float(template_roi[k][1][1])

            # self.roi.append([x1, y1, x2, y2, template_roi[k][2], template_roi[k][3], template_roi[k][4]])
            add_values = [x1, y1, x2, y2, template_roi[k][4]]
            if len(self.roi_tree.get_children("")) % 2 == 0:
                self.roi_tree.insert('', len(self.roi_tree.get_children('')),
                                     values=tuple(add_values), tags=('evenrow',))
            else:
                self.roi_tree.insert('', len(self.roi_tree.get_children('')),
                                     values=tuple(add_values), tags=('oddrow',))
            x1 = int(float(x1) * self.img_width)
            y1 = int(float(y1) * self.img_height)
            x2 = int(float(x2) * self.img_width)
            y2 = int(float(y2) * self.img_height)
            random_color = random.choice(self.tk_colors)
            self.rectangles_colors_list.append(random_color)
            self.rectangles_list.append(self.canvas.create_rectangle(x1, y1, x2, y2, outline=random_color, width=2))

    def _build_entry_rectangle(self, event=None):
        """method used to complete creation of rectangle, to fill the variable parameters and build the roi variable"""

        if self.modifying_existent_rectangle and self.rectangles_list:
            idx = self.rectangles_list.index(self.modifying_existent_rectangle)
            old_type, old_name, old_description = self.roi[idx][2:]
            x1, y1, x2, y2 = self.canvas.coords(self.modifying_existent_rectangle)
            self.roi[idx] = [(round(x1 / self.img_width, 4), round(y1 / self.img_height, 4)),
                             (round(x2 / self.img_width, 4), round(y2 / self.img_height, 4)),
                             old_type, old_name, old_description]
            self.roi_tree.edit_row([round(x1 / self.img_width, 4), round(y1 / self.img_height, 4),
                                    round(x2 / self.img_width, 4), round(y2 / self.img_height, 4),
                                    old_description], idx)
            self.modifying_existent_rectangle = None
            # restore binding events of canvas widget
            self.canvas.unbind('<Motion>')
            self.canvas.unbind('<FocusOut>')
            self.canvas.bind("<ButtonPress-1>", self._add_point_coordinates)
        else:
            if self.outside(event.x, event.y) or self.inside_other_rectangle(event.x, event.y) or \
                    not self._expanding_rectangle:
                return  # register only if coordinates inside image and outside other rectangles

            x1, y1, _, _ = self.canvas.coords(self._expanding_rectangle)
            x2, y2 = event.x, event.y
            if x1 != x2 and y1 != y2:
                if self._expanding_rectangle:
                    self.canvas.delete(self._expanding_rectangle)
                    self._expanding_rectangle = None
                self.rectangles_list.append(self.canvas.create_rectangle(x1, y1, x2, y2,
                                                                         outline=self._expanding_rectangle_color,
                                                                         width=2))
                self.rectangles_colors_list.append(self._expanding_rectangle_color)
                self.__set_template_var(x1, y1, "Seleccione a Variável: ", list(admissible_var_description.keys()))
                self.parent.wait_window(self._aux_top)
                self._aux_top = None
                self._expanding_rectangle = None
                # check if user wants to abort rectangle creation
                if not self.__abort_rectangle_creation:
                    self.roi.append([(round(x1 / self.img_width, 4), round(y1 / self.img_height, 4)),
                                     (round(x2 / self.img_width, 4), round(y2 / self.img_height, 4)),
                                     self.__var_type, self.__var_name, self.__var_description])
                    add_values = [round(x1 / self.img_width, 4), round(y1 / self.img_height, 4),
                                  round(x2 / self.img_width, 4), round(y2 / self.img_height, 4),
                                  self.__var_description]

                    if len(self.roi_tree.get_children("")) % 2 == 0:
                        self.roi_tree.insert('', len(self.roi_tree.get_children('')),
                                             values=tuple(add_values), tags=('evenrow',))
                    else:
                        self.roi_tree.insert('', len(self.roi_tree.get_children('')),
                                             values=tuple(add_values), tags=('oddrow',))
                else:
                    self.__abort_rectangle_creation = False
                    self.canvas.delete(self.rectangles_list[-1])
                    del self.rectangles_list[-1]
                    del self.rectangles_colors_list[-1]
            else:
                # if the corners coordinates are the same, erase the dot
                self.canvas.delete(self._expanding_rectangle)
                self._expanding_rectangle = None
        self.modifying_existent_rectangle = None
        return

    def _change_tree_entry(self, event):
        """method used to change entry in ROI tree and to update ROI"""
        self.roi_tree.set_cell_value(event, self, self.roi, self.tree_frame_holder)

    def create_canvas(self):
        """method used to create canvas with image"""
        self.img_width = self.__temp_pil_img.size[0]
        self.img_height = self.__temp_pil_img.size[1]
        self.temp_img = ImageTk.PhotoImage(self.__temp_pil_img)

        self.canvas = tk.Canvas(self, width=self.img_width, height=self.img_height, bg="white")
        self.container = self.canvas.create_rectangle((0, 0, self.img_width, self.img_height), width=0)
        self._image_id = self.canvas.create_image(0, 0, image=self.temp_img, anchor="nw")
        self.canvas.lower(self._image_id)  # set image into background
        self.canvas.image_tk = self.temp_img  # keep an extra reference to prevent garbage-collection

        self.canvas.bind("<ButtonPress-1>", self._add_point_coordinates)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<Enter>", self._set_canvas_focus)
        self.canvas.bind("<ButtonRelease-1>", self._build_entry_rectangle)
        self.canvas.bind("<ButtonRelease-3>", self._show_rectangle_options)
        self.canvas.bind('<Configure>', self.resize_canvas_image)

        self.canvas.grid(row=0, column=0, sticky="nsew")

    def __delete_all_figures(self):
        """method used to delete all figures from canvas and reset ROI variable"""
        if self.rectangles_list:
            for k, rectangle in enumerate(self.rectangles_list):
                self.canvas.delete(rectangle)  # Deletes the rectangle from canvas
            self.rectangles_list = []  # removes reference from rectangles list
            self.roi = []  # removes line from ROI list
            self.rectangles_colors_list = []
        if len(self.roi_tree.get_children()) > 0:
            for item in self.roi_tree.get_children():
                self.roi_tree.delete(item)
        return

    def __delete_last_figure(self):
        """method used to delete the last figure from canvas and to clear it from ROI"""
        if self.rectangles_list:
            self.canvas.delete(self.rectangles_list[-1])
            del self.rectangles_list[-1]  # removes reference from rectangles list
            del self.roi[-1]  # removes line from ROI list
            del self.rectangles_colors_list[-1]  # remove color of rectangle from list
            self.roi_tree.delete(list(self.roi_tree.get_children())[-1])
            self.roi_tree.edit_row_tag()  # re-organize row tags
        return

    def __delete_rectangle(self):
        """method used to delete rectangle from canvas and treeview as requested by user"""
        self.more_rectangle.place_forget()
        self.more_rectangle = None

        idx = self.rectangles_list.index(self.modifying_existent_rectangle)
        self.canvas.delete(self.modifying_existent_rectangle)  # Deletes the rectangle from canvas
        del self.rectangles_list[idx]  # removes reference from rectangles list
        del self.roi[idx]  # removes line from ROI list
        del self.rectangles_colors_list[idx]  # removes color from rectangles list
        self.roi_tree.delete(list(self.roi_tree.get_children())[idx])
        self.roi_tree.edit_row_tag()  # re-organize row tags
        self.modifying_existent_rectangle = None

    def __delete_selected(self):
        if self.roi_tree.selection():
            for record in self.roi_tree.selection():
                row_idx = self.roi_tree.index(record)
                self.canvas.delete(self.rectangles_list[row_idx])
                del self.rectangles_list[row_idx]  # removes reference from rectangles list
                del self.roi[row_idx]  # removes line from ROI list
                del self.rectangles_colors_list[row_idx]  # removes reference from rectangles list
                self.roi_tree.delete(record)
                if row_idx - 1 >= 0:
                    self.roi_tree.selection_set(self.roi_tree.get_children("")[row_idx - 1])
                elif self.roi_tree.get_children(""):
                    self.roi_tree.selection_set(self.roi_tree.get_children("")[0])
                else:
                    pass
        self.roi_tree.edit_row_tag()  # re-organize row tags
        return

    def destroy_window(self):
        answer = message_boxes("askyesno", "Sair do Editor?",
                               "Tem a certeza que deseja fechar o editor de template?")
        if answer == 1:
            if len(self.roi_tree.get_children("")) > 0:
                # aks if user wants to save roi results and close window
                answer = message_boxes("askyesno", "Gravar Alterações?", "Pretende gravar alterações?")
                if answer == 1 and self.__edit_or_new == "new":
                    self.save_roi_results()
                elif answer == 1 and self.__edit_or_new == "edit":
                    self.__save_roi_changes()
            if self:
                self.destroy()
        else:
            self.attributes('-topmost', 1)
            self.attributes('-topmost', 0)
            return

    def __edit_rectangle(self, event):
        self.more_rectangle.place_forget()
        self.more_rectangle = None
        self.__backup_rectangle_coords = self.canvas.coords(self.modifying_existent_rectangle)
        self.canvas.bind('<Motion>', self.__edit_rectangle_motion)
        self.canvas.bind('<FocusOut>', self.__restore_rectangle_coords)
        self.canvas.unbind("<ButtonPress-1>")

    def __edit_rectangle_motion(self, event):
        """method used to change coordinates of rectangle being modified"""
        if self.modifying_existent_rectangle:
            bbox = self.canvas.coords(self.modifying_existent_rectangle)
            self.canvas.coords(self.modifying_existent_rectangle, bbox[0], bbox[1], event.x, event.y)

    def grab_chosen_template(self, event):
        """method used to select other template"""
        self.template_title.set(self.template_combolist.get())
        self.title("Editor de template - " + self.template_title.get())
        self.update_existing_roi()

    def identify_hover_row(self, event=None):
        """static method used to identify the row and corresponding rectangle which the user is hovering on"""
        # change all border width to default
        for rectangle in self.rectangles_list:
            self.canvas.itemconfig(rectangle, width=2)
        self.identified_row = None
        # identity the event widget
        tree = event.widget
        item = tree.identify_row(event.y)
        # determine the row number of the identified row
        if item:
            tree_rows = list(tree.get_children(""))
            self.identified_row = tree_rows.index(item)
            # increase border width of rectangle corresponding to current treeview row
            self.canvas.itemconfig(self.rectangles_list[self.identified_row], width=4)
        else:
            return

    def inside_other_rectangle(self, x, y):
        """check if coordinates are inside other rectangles"""
        if len(self.rectangles_list) < 1:
            self.modifying_existent_rectangle = None
            return False
        else:
            for rectangle in self.rectangles_list:
                bbox = self.canvas.coords(rectangle)  # get rectangle area
                if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                    self.modifying_existent_rectangle = rectangle
                    return True
            return False

    def on_move_press(self, event):
        """method used to draw a temporary rectangle after the first click and while the second rectangle corner is
                not defined """
        if self._expanding_rectangle:
            x1, y1, _, _ = self.canvas.coords(self._expanding_rectangle)
            self.canvas.coords(self._expanding_rectangle, x1, y1, event.x, event.y)
        else:
            self.modifying_existent_rectangle = None
            self._expanding_rectangle = None
        return

    def outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def resize_canvas_image(self, event):
        """method used to resize canvas image and update dimensions"""
        self.temp_img = ImageTk.PhotoImage(master=self.canvas,
                                           image=Image.open(self.template_path).resize(
                                               (int(self.canvas.winfo_width()),
                                                int(self.canvas.winfo_height())), self.__filter))
        self._image_id = self.canvas.create_image(0, 0, anchor='nw', image=self.temp_img)
        self.img_width = self.temp_img.width()
        self.img_height = self.temp_img.height()

        # method used to redraw existing rectangles into their new positions
        if self.rectangles_list:
            for k, rectangle in enumerate(self.rectangles_list):
                x1 = int(float(self.roi[k][0][0]) * self.img_width)
                y1 = int(float(self.roi[k][0][1]) * self.img_height)
                x2 = int(float(self.roi[k][1][0]) * self.img_width)
                y2 = int(float(self.roi[k][1][1]) * self.img_height)
                self.rectangles_list[k] = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                                       outline=self.rectangles_colors_list[k],
                                                                       width=2)
        return

    def __restore_rectangle_coords(self, event):
        """method used to restore coordinates of rectangle before user left canvas widget"""
        bbox = self.__backup_rectangle_coords
        self.canvas.coords(self.modifying_existent_rectangle, bbox[0], bbox[1], bbox[2], bbox[3])
        self.__backup_rectangle_coords = None
        self.modifying_existent_rectangle = None
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<FocusOut>')

    def save_roi_results(self):
        """method used to store roi data into templates file"""
        if os.path.exists(self.__main_path + r'\bin\Templates\Template_List.csv'):
            new_name = self.__main_path + r'\bin\Templates\Template_List_old.csv'
            old_name = self.__main_path + r'\bin\Templates\Template_List.csv'
            try:
                os.rename(old_name, new_name)
            except FileExistsError:
                os.remove(new_name)
                os.rename(old_name, new_name)

            csv_input = pandas.read_csv(new_name)
            csv_input[self.template_title.get()] = self.roi
            csv_input.to_csv(old_name, index=False, encoding='latin')
            os.remove(new_name)

        elif self.roi:
            save_roi_path = self.__main_path + "\\bin\\Templates\\" + self.template_title.get() + ".txt"
            with open(save_roi_path, "w") as f:
                for line in self.roi:
                    f.write(str(line))
                    f.write('\n')
        return

    def __save_roi_changes(self):
        """method used in edit mode to save changes made to existing roi"""
        self.existing_roi_templates[self.template_title.get()] = self.roi

    def _set_canvas_focus(self, event):
        self.canvas.focus_set()

    def _set_name_focus(self, event):
        self._name_entry.focus_set()

    def __set_template_var(self, x, y, label_text, invoice_list):

        def set_variable(event):
            """ modify variable name/type as per user definition"""
            combo_box = event.widget

            self.__var_description = combo_box.get()
            self.__var_type = admissible_var_description[self.__var_description][0]
            self.__var_name = admissible_var_description[self.__var_description][1]

            if combo_box:
                combo_box.destroy()
                self._aux_top.destroy()
            return

        def cancel_rectangle():
            """cancel creation of rectangle"""
            self._aux_top.destroy()
            self.__abort_rectangle_creation = True
            return

        self._aux_top = tk.Toplevel(self, bg="white")
        self._aux_top.columnconfigure(0, weight=1)
        self._aux_top.geometry("+%d+%d" % (x + self.winfo_x(), y + self.winfo_y()))
        self._aux_top.iconbitmap(self._aux_top, default=self.__main_path + r"\bin\aux_img\icon2.ico")
        top_label = tk.Label(self._aux_top, text=label_text, font=NORM_FONT, bg="white")
        top_label.grid(row=0, column=0)
        combo_list = ttk.Combobox(self._aux_top, value=invoice_list, font=NORM_FONT, state="readonly")
        combo_list.current(0)
        combo_list.bind("<<ComboboxSelected>>", set_variable)
        combo_list.grid(row=0, column=1)
        cancel_button = tk.Button(self._aux_top, text="Cancel", relief="raised", bg="white", font=NORM_FONT,
                                  anchor="c", command=cancel_rectangle)
        cancel_button.grid(row=1, column=1, padx=5, pady=5, sticky="e")

        return

    def __set_template_name(self, x, y):
        """Method used to define the name of the template"""
        self.canvas.unbind("<Enter>")  # unbind focus on canvas so that it won't remove focus from name toplevel

        top = tk.Toplevel(self, bg="white")
        top.geometry("+%d+%d" % (x, y))
        top.columnconfigure((0, 1), weight=1)
        top.iconbitmap(top, default=self.__main_path + r"\bin\aux_img\icon2.ico")
        top.attributes('-topmost', 1)

        top_label = tk.Label(top, text="Defina o Nome do Template:", font=NORM_FONT, bg="white")
        top_label.grid(row=0, column=0, columnspan=2, sticky="nsew")

        if self.__edit_or_new == "new":
            self._name_entry = ttk.Entry(top, font="Verdana 11", width=40)
            if self.template_title.get() == "":
                self._name_entry.insert(0, "Nome Template")
            else:
                self._name_entry.insert(0, self.template_title.get())
            self._name_entry.selection_range(0, tk.END)
        elif self.__edit_or_new == "edit":
            self._name_entry = ttk.Combobox(top, value=list(self.existing_roi_templates.keys()), font=NORM_FONT,
                                            state="readonly", justify="center")
            self._name_entry.current(0)

        self._name_entry.focus_set()
        self._name_entry.grid(row=1, column=0, columnspan=2, sticky="nsew")

        ok_btn = tk.Button(top, text="OK", bg="steel blue", font="Verdana 9 bold",
                           fg="white", width=8, command=lambda: self.set_template_name_var(None, top))
        cancel_btn = tk.Button(top, text="Cancelar", bg="light steel blue", fg="black",
                               font="Verdana 9 bold", width=13, command=top.destroy)
        ok_btn.grid(row=2, column=0, pady=5, padx=5, sticky="e")
        cancel_btn.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        top.bind("<Enter>", self._set_name_focus)
        top.bind("<Return>", lambda e: self.set_template_name_var(e, top))

    def set_template_name_var(self, event=None, top=None):
        # define name of template to be stored
        self.template_title.set(self._name_entry.get())
        self.title("Editor de template - " + self.template_title.get())
        if self.__edit_or_new == "edit":
            self.template_combolist.current(list(self.existing_roi_templates.keys()).index(self.template_title.get()))
            self.update_existing_roi()
        top.attributes('-topmost', 0)
        top.destroy()
        self.lift()
        self.canvas.bind("<Enter>", self._set_canvas_focus)  # restore binding of focus on canvas

    def _show_rectangle_options(self, event=None):
        """method used to allow user to perform changes in current rectangle"""
        if self.inside_other_rectangle(event.x, event.y):  # check if click is inside rectangle
            self.more_rectangle = tk.Frame(self.canvas, bd=2, bg="white")
            del_button = HoverButton(self.more_rectangle, text="Apagar Rectângulo", bd=0, bg="white", font=SMALL_FONT,
                                     justify=tk.LEFT, relief=tk.FLAT, activebackground="light steel blue",
                                     command=self.__delete_rectangle)
            edit_button = HoverButton(self.more_rectangle, text="Editar Rectângulo", bd=0, bg="white", font=SMALL_FONT,
                                      justify=tk.LEFT, relief=tk.FLAT, activebackground="light steel blue",
                                      command=lambda: self.__edit_rectangle(event))

            self.more_rectangle.place(x=event.x, y=event.y)
            del_button.grid(row=0, column=0)
            edit_button.grid(row=1, column=0)

    def update_existing_roi(self):
        """method used to update existing roi, as the user selects another template"""
        # if in edit mode, as new template is selected, clear all rectangles, roi and tree rows and fill with new
        self.__delete_all_figures()
        self.template_path = self.existing_templates_paths[self.template_title.get()]
        self.__temp_pil_img = get_resized_img(Image.open(self.template_path),
                                              int(self.__factor_resize * self.__w_width),
                                              int(self.__factor_resize * self.__w_height))
        if self.canvas:
            self.canvas.destroy()

        # rebuild canvas widget
        self.create_canvas()

        self.add_editable_data(self.existing_roi_templates[self.template_title.get()])
