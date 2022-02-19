import tkinter as tk
from PIL import Image, ImageTk
from .utils import get_resized_img


class DefineMovingTemplateEnd(object):

    def __init__(self, parent, invoice_path):
        self.parent = parent
        self.tip_window = tk.Toplevel(self.parent, bg="white")
        self.tip_window.title("Por favor defina o fim da tabela dos produtos da referência:")

        # create dictionary with coordinates to keep track of them
        self._drag_data = {"x": 0, "y": 0}
        self.__line_y = None
        self.__user_line = None
        self.line_y_ratio = tk.StringVar()
        self.__temp_pil_img = None
        self.__temp_resized_pil_img = None
        self._img_width = None
        self._img_height = None
        self.__temp_img = None
        self.canvas = None

        # load image and resize it to make sure it fits in the user screen
        self.__temp_pil_img = Image.open(invoice_path)
        self.__temp_resized_pil_img = get_resized_img(self.__temp_pil_img, int(0.45 * 1500), 1500)
        self._img_width = self.__temp_resized_pil_img.size[0]
        self._img_height = self.__temp_resized_pil_img.size[1]
        self.temp_img = ImageTk.PhotoImage(self.__temp_resized_pil_img)

        self.tip_window.geometry("{}x{}".format(self._img_width, self._img_height))

        # create canvas widget to show image and allow for drawing of rectangles
        self.canvas = tk.Canvas(self.tip_window, width=self._img_width, height=self._img_height, bg="white")
        self.container = self.canvas.create_rectangle((0, 0, self._img_width, self._img_height), width=0)
        self._image_id = self.canvas.create_image(0, 0, image=self.temp_img, anchor="nw")
        self.canvas.lower(self._image_id)  # set image into background
        self.canvas.image_tk = self.temp_img  # keep an extra reference to prevent garbage-collection

        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonRelease-1>", self.__draw_general)

        # bind drag and drop movement to canvas
        self.canvas.bind("<ButtonPress-1>", self.__drag_start)
        self.canvas.bind("<B1-Motion>", self.__drag)
        self.canvas.bind("<Delete>", self.__delete_line)
        self.canvas.bind("<Configure>", self.__fit_image)

    def __add_horizontal_line(self, event):
        """Add horizontal line"""
        x2 = self._img_width - event.x
        self.line_y_ratio.set(str(event.y / self._img_height))
        self.__user_line = self.canvas.create_line(event.x, event.y, x2, event.y, fill="red")

    def __delete_line(self):
        """ method used to delete horizontal line if existent"""
        self.canvas.delete(self.__user_line) if self.__user_line else None
        return

    def __draw_general(self, event):
        """ method used to select the correct binding"""
        # the if-else statement should only allow for a single line to be added on canvas
        if self.outside(event.x, event.y):
            return  # registe only if coordinates inside image

        if self.__user_line:
            self.__drag_stop(event)
        else:
            self.__add_horizontal_line(event)

    def __drag_start(self, event):
        """Beginning drag of an object"""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def __drag_stop(self, event):
        """End drag of an object"""
        # update line y coordinates for further referencing
        self.__line_y = self._drag_data["y"]
        self.line_y_ratio.set(str(self.__line_y / self._img_height))
        # reset the drag information
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def __drag(self, event):
        """Handle dragging of an object"""
        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        # move the object the appropriate amount
        if self.__user_line:
            self.canvas.move(self.__user_line, delta_x, delta_y)
        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def __fit_image(self, event=None):
        """Fit image inside application window on resize."""
        if event is not None and event.widget is self.canvas:
            # size changed; update image
            self.tip_window.config(width=event.width, height=event.height)
            self.__show_image(event.width, event.height)

    def hide_window(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

    def outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def __show_image(self, width, height):
        """ method used to show resized image"""
        self.canvas.delete("all")
        # resize original image
        self.__temp_resized_pil_img = get_resized_img(self.__temp_pil_img, width, height)
        self.__temp_img = ImageTk.PhotoImage(self.__temp_resized_pil_img)
        # determine new width and height
        self._img_width = self.__temp_resized_pil_img.size[0]
        self._img_height = self.__temp_resized_pil_img.size[1]
        # create add scaled image to canvas
        self.canvas.create_image(0, 0, image=self.__temp_img, anchor="nw")
        self.canvas.pack(fill="both", expand=True)

        if self.__user_line:
            line_y = float(self.line_y_ratio.get()) * self._img_height
            self.__user_line = self.canvas.create_line(0, line_y, self._img_width, line_y, fill="red")
