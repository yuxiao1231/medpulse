import tkinter as tk

class CustomCheckbox(tk.Canvas):
    """A custom checkbox using Canvas to ensure it always looks like a distinct white box.
    This solves the issue with native ttk.Checkbutton on Windows where it uses native
    colors and can be hard to read when unchecked.
    """
    
    def __init__(self, master, text, variable, bg="#ffffff", fg="#000000", select_color="#0078D7", **kwargs):
        super().__init__(master, bg=bg, highlightthickness=0, height=24, **kwargs)
        self.variable = variable
        self.text = text
        self.bg = bg
        self.fg = fg
        self.select_color = select_color
        
        # Draw the box
        self.box = self.create_rectangle(2, 4, 18, 20, fill="white", outline="#999999", width=1.5)
        # Draw the checkmark (hidden initially)
        self.check = self.create_line(5, 12, 9, 16, 15, 6, fill=self.select_color, width=2.5, state="hidden")
        # Draw the text
        self.label = self.create_text(26, 12, text=self.text, fill=self.fg, anchor="w", font=("Segoe UI", 10))
        
        self.bind("<Button-1>", self.toggle)
        self.variable.trace_add("write", self.update_view)
        
        # Calculate appropriate width
        self.update_idletasks()
        bbox = self.bbox(self.label)
        if bbox:
            self.configure(width=bbox[2] + 10)
        else:
            self.configure(width=200)
            
        self.update_view()

    def toggle(self, event=None):
        current = self.variable.get()
        self.variable.set(not current)
        
    def update_view(self, *args):
        try:
            val = self.variable.get()
            if val:
                self.itemconfig(self.check, state="normal")
                self.itemconfig(self.box, outline=self.select_color, width=1.5)
            else:
                self.itemconfig(self.check, state="hidden")
                self.itemconfig(self.box, outline="#999999", width=1.5)
        except tk.TclError:
            pass
