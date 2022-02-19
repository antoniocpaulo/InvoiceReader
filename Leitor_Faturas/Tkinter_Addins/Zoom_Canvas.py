import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class ZoomCanvas:
    def __init__(self, root, path):

        self.frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        xscrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky="ew")
        yscrollbar = ttk.Scrollbar(self.frame)
        yscrollbar.grid(row=0, column=1, sticky="ns")
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.frame, bd=0, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set,
                                xscrollincrement=10, yscrollincrement=10)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.scale = 1.0
        self.orig_img = Image.open(path)
        self.img = None
        self.img_id = None
        # draw the initial image at 1x scale
        self.redraw()

        self.canvas.bind("<Button 3>", self.grab)
        self.canvas.bind("<B3-Motion>", self.drag)
        root.bind("<MouseWheel>", self.zoom)

        # ... rest of init, bind buttons, pack frame

    def grab(self, event):
        self._y = event.y
        self._x = event.x

    def drag(self, event):
        if (self._y - event.y < 0):
            self.canvas.yview("scroll", -1, "units")
        elif (self._y - event.y > 0):
            self.canvas.yview("scroll", 1, "units")
        if (self._x - event.x < 0):
            self.canvas.xview("scroll", -1, "units")
        elif (self._x - event.x > 0):
            self.canvas.xview("scroll", 1, "units")
        self._x = event.x
        self._y = event.y

    def zoom(self, event):
        if event.num == 4 or event.delta == 120:
            self.scale *= 2
        elif event.num == 5 or event.delta == -120:
            self.scale *= 0.5
        self.redraw(event.x, event.y)

    def redraw(self, x=0, y=0):
        if self.img_id: self.canvas.delete(self.img_id)
        iw, ih = self.orig_img.size
        # calculate crop rect
        cw, ch = iw / self.scale, ih / self.scale
        if cw > iw or ch > ih:
            cw = iw
            ch = ih
        # crop it
        _x = int(iw / 2 - cw / 2)
        _y = int(ih / 2 - ch / 2)
        tmp = self.orig_img.crop((_x, _y, _x + int(cw), _y + int(ch)))
        size = int(cw * self.scale), int(ch * self.scale)
        # draw
        self.img = ImageTk.PhotoImage(tmp.resize(size))
        self.img_id = self.canvas.create_image(x, y, image=self.img)
