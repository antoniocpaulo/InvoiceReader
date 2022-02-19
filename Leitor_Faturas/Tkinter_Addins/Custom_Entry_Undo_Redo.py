import tkinter as tk


class CEntry(tk.Entry):
    def __init__(self, parent, *args, **kwargs):
        tk.Entry.__init__(self, parent, *args, **kwargs)

        self.changes = [""]
        self.steps = int()
        self.parent = parent

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Cortar")
        self.context_menu.add_command(label="Copiar")
        self.context_menu.add_command(label="Colar")

        self.bind("<Button-3>", self.popup)
        self.bind("<Return>", self._set_focus_on_parent)
        self.bind("<Control-z>", self.undo)
        self.bind("<Control-y>", self.redo)

        self.bind("<Key>", self.add_changes)

    def popup(self, event):
        self.context_menu.post(event.x_root, event.y_root)
        self.context_menu.entryconfigure("Cortar", command=lambda: self.event_generate("<<Cut>>"))
        self.context_menu.entryconfigure("Copiar", command=lambda: self.event_generate("<<Copy>>"))
        self.context_menu.entryconfigure("Colar", command=lambda: self.event_generate("<<Paste>>"))

    def undo(self, event=None):
        if self.steps > 0:
            self.steps -= 1
            self.delete(0, tk.END)
            self.insert(tk.END, self.changes[self.steps])

    def redo(self, event=None):
        if self.steps < len(self.changes):
            self.delete(0, tk.END)
            self.insert(tk.END, self.changes[self.steps])
            self.steps += 1

    def add_changes(self, event=None):
        if self.get() != self.changes[-1]:
            self.changes.append(self.get())
            self.steps += 1

    def _set_focus_on_parent(self, event=None):
        self.parent.focus_set()
