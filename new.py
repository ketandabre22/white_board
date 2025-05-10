import customtkinter as ctk
import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import filedialog

# Setup
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Drawing states
is_drawing = False
prev_x = prev_y = 0
drawing_color = "black"
canvas_bg = "white"
line_width = 2
text_mode = False
using_eraser = False

draw_history = []
redo_stack = []
current_stroke = []

# Pen size config
pen_big = False
pen_default_size = 2
pen_big_size = 6

# Eraser size config
eraser_big = False
eraser_default_size = 10
eraser_big_size = 30

def start_drawing(event):
    global is_drawing, prev_x, prev_y
    if text_mode:
        add_text(event)
        return
    is_drawing = True
    prev_x, prev_y = event.x, event.y
    current_stroke.clear()

def draw(event):
    global prev_x, prev_y
    if is_drawing:
        x, y = event.x, event.y
        line = canvas.create_line(prev_x, prev_y, x, y,
                                  fill=drawing_color, width=line_width,
                                  capstyle=tk.ROUND, smooth=True)
        current_stroke.append(line)
        prev_x, prev_y = x, y

def stop_drawing(event):
    global is_drawing
    is_drawing = False
    if current_stroke:
        draw_history.append(current_stroke.copy())
        redo_stack.clear()
        current_stroke.clear()

def change_pen_color():
    global drawing_color, using_eraser, line_width
    color = askcolor()[1]
    if color:
        drawing_color = color
        using_eraser = False
        line_width = pen_big_size if pen_big else pen_default_size
        update_display()

def change_line_width(val):
    global line_width
    line_width = int(float(val))

def toggle_pen_size():
    global pen_big, line_width
    pen_big = not pen_big
    if not using_eraser:
        line_width = pen_big_size if pen_big else pen_default_size
    update_display()

def toggle_eraser():
    global drawing_color, line_width, using_eraser
    using_eraser = not using_eraser
    if using_eraser:
        drawing_color = canvas_bg
        line_width = eraser_big_size if eraser_big else eraser_default_size
    else:
        drawing_color = "black"
        line_width = pen_big_size if pen_big else pen_default_size
    update_display()

def toggle_eraser_size():
    global eraser_big, line_width
    eraser_big = not eraser_big
    if using_eraser:
        line_width = eraser_big_size if eraser_big else eraser_default_size
    update_display()

def update_display():
    eraser_button.configure(text="Eraser: ON" if using_eraser else "Eraser: OFF")
    eraser_size_button.configure(text=f"Eraser Size: {eraser_big_size if eraser_big else eraser_default_size}")
    pen_size_button.configure(text=f"Pen Size: {pen_big_size if pen_big else pen_default_size}")

def undo():
    if draw_history:
        stroke = draw_history.pop()
        for item in stroke:
            canvas.delete(item)
        redo_stack.append(stroke)

def redo():
    if redo_stack:
        stroke = redo_stack.pop()
        for item in stroke:
            canvas.itemconfigure(item, state='normal')
        draw_history.append(stroke)

def save_canvas():
    file = filedialog.asksaveasfilename(defaultextension=".ps", filetypes=[("PostScript", "*.ps")])
    if file:
        canvas.postscript(file=file)

def change_canvas_bg():
    global canvas_bg
    color = askcolor()[1]
    if color:
        canvas_bg = color
        canvas.config(bg=canvas_bg)

def toggle_grid():
    if hasattr(toggle_grid, "lines"):
        for line in toggle_grid.lines:
            canvas.delete(line)
        del toggle_grid.lines
    else:
        toggle_grid.lines = []
        for i in range(0, canvas.winfo_width(), 20):
            toggle_grid.lines.append(canvas.create_line(i, 0, i, canvas.winfo_height(), fill="lightgray"))
        for j in range(0, canvas.winfo_height(), 20):
            toggle_grid.lines.append(canvas.create_line(0, j, canvas.winfo_width(), j, fill="lightgray"))

def toggle_text_mode():
    global text_mode
    text_mode = not text_mode
    text_button.configure(fg_color="gray" if text_mode else "#4CAF50")

def add_text(event):
    font_size = 24
    entry = tk.Entry(canvas, font=("Arial", font_size))
    entry_window = canvas.create_window(event.x, event.y, window=entry, anchor="nw")

    def on_enter(e):
        text = entry.get()
        canvas.delete(entry_window)
        entry.destroy()
        if text:
            item = canvas.create_text(event.x, event.y, text=text, fill=drawing_color,
                                      anchor="nw", font=("Arial", font_size))
            draw_history.append([item])
            redo_stack.clear()

    entry.bind("<Return>", on_enter)
    entry.focus()

# App window
root = ctk.CTk()
root.title("Whiteboard App")

root.update_idletasks()
try:
    root.state("zoomed")
except:
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

canvas = tk.Canvas(root, bg=canvas_bg)
canvas.pack(fill="both", expand=True)

# Controls
controls = ctk.CTkFrame(root)
controls.pack(side="top", fill="x", padx=10, pady=10)

color_button = ctk.CTkButton(controls, text="Change Color", command=change_pen_color, corner_radius=20)
clear_button = ctk.CTkButton(controls, text="Clear Canvas", command=lambda: [canvas.delete("all"), draw_history.clear(), redo_stack.clear()], corner_radius=20)
pen_size_button = ctk.CTkButton(controls, text="Pen Size: 2", command=toggle_pen_size, corner_radius=20)
eraser_button = ctk.CTkButton(controls, text="Eraser: OFF", command=toggle_eraser, corner_radius=20)
eraser_size_button = ctk.CTkButton(controls, text="Eraser Size: 10", command=toggle_eraser_size, corner_radius=20)
undo_button = ctk.CTkButton(controls, text="Undo", command=undo, corner_radius=20)
redo_button = ctk.CTkButton(controls, text="Redo", command=redo, corner_radius=20)
save_button = ctk.CTkButton(controls, text="Save Drawing", command=save_canvas, corner_radius=20)
bg_button = ctk.CTkButton(controls, text="Canvas BG Color", command=change_canvas_bg, corner_radius=20)
grid_button = ctk.CTkButton(controls, text="Toggle Grid", command=toggle_grid, corner_radius=20)
text_button = ctk.CTkButton(controls, text="Text Tool", command=toggle_text_mode, corner_radius=20)

line_width_label = ctk.CTkLabel(controls, text="Line Width:")
line_width_slider = ctk.CTkSlider(controls, from_=1, to=10, command=change_line_width)
line_width_slider.set(line_width)

for widget in [
    color_button, clear_button,
    pen_size_button, eraser_button, eraser_size_button,
    undo_button, redo_button, save_button,
    bg_button, grid_button, text_button,
    line_width_label, line_width_slider
]:
    widget.pack(side="left", padx=6, pady=6)

canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<ButtonRelease-1>", stop_drawing)

update_display()
root.mainloop()
