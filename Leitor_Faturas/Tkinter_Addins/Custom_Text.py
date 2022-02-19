import tkinter as tk


class CustomText(tk.Text):
    """A text widget with a new method, HighlightPattern

    example:

    text = CustomText()
    text.tag_configure("red",foreground="#ff0000")
    text.HighlightPattern("this should be red", "red")

    The HighlightPattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    """

    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

    def HighlightPattern(self, pattern, tag, start="1.0", end="end", regexp=True):
        """Apply the given tag to all text that matches the given pattern"""

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", end)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit", count=count, regexp=regexp)
            if index == "":
                break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")
