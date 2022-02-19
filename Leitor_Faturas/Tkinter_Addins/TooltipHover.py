import tkinter as tk


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info', command=None, extra_command=None):
        self.waittime = 200     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
        self._command = command
        self._extra_command = extra_command

    def click(self, event):
        if self._extra_command:
            self._command(self._extra_command)
        else:
            self._command()

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def check_if_is_outside_screen(self, event):
        # check if box is going to end up outside the screen
        tw_width_bottom_x_corner = self.widget.winfo_rootx() + self.tw.winfo_width()
        if tw_width_bottom_x_corner >= self.widget.winfo_screenwidth():
            self.tw.wm_geometry('%dx%d+%d+%d' % (self.tw.winfo_width(), self.tw.winfo_height(), 
                                                 self.tw.winfo_rootx() - self.tw.winfo_width(),
                                                 self.tw.winfo_rooty()
                                                 ))
            self.tw.unbind("<Configure>")

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 27
        y += self.widget.winfo_rooty() + 17
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            self.tw.tk.call("::tk::unsupported::MacWindowStyle",
                            "style", self.tw._w,
                            "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

        self.tw.bind("<Configure>", self.check_if_is_outside_screen)

        if self._command is not None:
            self.widget.unbind("<Return>")
            self.widget.bind("<Return>", self.click)
            self.widget.bind('<ButtonRelease-1>', self.click)
        

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()



# def CreateToolTip(widget, text, fg="black"):
#     toolTip = ToolTip(widget, fg=fg)

#     def enter(event):
#         toolTip.showtip(text)

#     def leave(event):
#         toolTip.hidetip()

#     widget.bind('<Enter>', enter, add="+")
#     widget.bind('<Leave>', leave, add="+")
#     widget.bind('<ButtonRelease-1>', leave, add="+")


# class ToolTip(object):

#     def __init__(self, widget, fg="black"):
#         self.widget = widget
#         self.tip_window = None
#         self.id = None
#         self.x = self.y = 0
#         self.text = ""
#         self.fg = fg

#     def showtip(self, text):
#         """Display text in tooltip window"""
#         self.text = text
#         if self.tip_window or not self.text:
#             return
#         x, y, cx, cy = self.widget.bbox("insert")
#         x = x + self.widget.winfo_rootx() + 27
#         y = y + cy + self.widget.winfo_rooty() + 17
#         self.tip_window = tw = tk.Toplevel(self.widget)
#         tw.wm_overrideredirect(1)
#         tw.wm_geometry("+%d+%d" % (x, y))
#         try:
#             # For Mac OS
#             tw.tk.call("::tk::unsupported::MacWindowStyle",
#                        "style", tw._w,
#                        "help", "noActivates")
#         except tk.TclError:
#             pass
#         label = tk.Label(tw, text=self.text, justify=tk.LEFT, fg=self.fg,
#                          background="white", relief=tk.SOLID, borderwidth=1,
#                          font=("verdana", "8", "normal"))
#         label.pack(ipadx=1)

#         self.tip_window.update_idletasks()
#         self.check_if_is_outside_screen()

#     def check_if_is_outside_screen(self):
#         # check if box is going to end up outside the screen
#         tw_width_bottom_x_corner = self.tip_window.winfo_rootx() + self.tip_window.winfo_width()
#         if tw_width_bottom_x_corner >= self.widget.winfo_screenwidth():
#             x = self.tip_window.winfo_rootx() - self.tip_window.winfo_width()
#             self.tip_window.wm_geometry('%dx%d+%d+%d' % (self.tip_window.winfo_width(),
#                                                          self.tip_window.winfo_height(),
#                                                          x,
#                                                          self.tip_window.winfo_rooty()))

#     def hidetip(self):
#         tw = self.tip_window
#         self.tip_window = None
#         if tw:
#             tw.destroy()

# class HoverInfo(tk.Menu):
#
#     def __init__(self, parent, text, command=None):
#         self._com = command
#         tk.Menu.__init__(self, parent, tearoff=0)
#         if not isinstance(text, str):
#             raise TypeError('Trying to initialise a Hover Menu with a non string type: ' + text.__class__.__name__)
#         toktext = re.split('\n', text)
#         for t in toktext:
#             self.add_command(label=t)
#
#         self._displayed = False
#         self.master.bind("<Enter>", self.Display)
#         self.master.bind("<Leave>", self.Remove)
#
#     def __del__(self):
#         self.master.unbind("<Enter>")
#         self.master.unbind("<Leave>")
#
#     def Display(self, event):
#         if not self._displayed:
#             self._displayed = True
#             self.post(event.x_root, event.y_root)
#         if self._com is not None:
#             self.master.unbind_all("<Return>")
#             self.master.bind_all("<Return>", self.Click)
#
#     def Remove(self, event):
#         if self._displayed:
#             self._displayed = False
#             self.unpost()
#         if self._com is not None:
#             self.unbind_all("<Return>")
#
#     def Click(self, event):
#         self._com()
#
#
# from Tkinter import *
# from HoverInfo import HoverInfo
# class MyApp(Frame):
#    def __init__(self, parent=None):
#       Frame.__init__(self, parent)
#       self.grid()
#       self.lbl = Label(self, text='testing')
#       self.lbl.grid()
#
#       self.hover = HoverInfo(self, 'while hovering press return \n for an exciting msg', self.HelloWorld)
#
#    def HelloWorld(self):
#       print('Hello World')
#
# app = MyApp()
# app.master.title('test')
# app.mainloop()
