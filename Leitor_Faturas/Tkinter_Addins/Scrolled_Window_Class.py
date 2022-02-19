import tkinter as tk
from tkinter import ttk


class AutoScrollbar(ttk.Scrollbar):
    """ A scrollbar that hides itself if it's not needed. Works only for grid geometry manager """

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        raise tk.TclError('Cannot use place with the widget ' + self.__class__.__name__)


class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """

    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, master=parent, background="white", *args, **kw)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = AutoScrollbar(self, orient="vertical")
        vscrollbar.grid(column=1, row=0, padx=5, sticky='ns')  # .pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self._canvas = tk.Canvas(self, bg="white", bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        self._canvas.grid(row=0, column=0, padx=5, sticky="nsew")  # .pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=self._canvas.yview)

        # reset the view
        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(self._canvas, background="white")
        self.interior.columnconfigure(0, weight=1)
        self.interior.columnconfigure(1, weight=2)
        interior_id = self._canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self._canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self._canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self._canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self._canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self._canvas.itemconfigure(interior_id, width=self._canvas.winfo_width())

        self._canvas.bind('<Configure>', _configure_canvas)
        self._canvas.bind('<Enter>', self._bound_to_mousewheel)
        self._canvas.bind('<Leave>', self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self._canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if self.interior.winfo_reqheight() > self._canvas.winfo_height():
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

