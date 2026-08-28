from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw
import tkinter.colorchooser
import tkinter as tk


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main App")

        cell_size = 15
        grid_width = 70
        grid_height = 70

        # Store these so Save_On_Click can use them later
        self.cell_size = cell_size
        self.grid_width = grid_width
        self.grid_height = grid_height

        self.colour_selecter = tk.colorchooser.Chooser(self.root)
        self.colour_selected = None
        self.is_edit_selected = False
        self.is_erase_selected = False

        # Add bg="white" to Canvas for proper event handling
        self.drawing_grid = Canvas(self.root, bg="white") 
        self.drawing_grid.grid(column=0, row=0, sticky=(N, E, S, W))

        self.cells = []
        for x in range(0, grid_height):
            for y in range(0, grid_width):
                cell = Frame(self.drawing_grid, width=cell_size, height=cell_size, 
                           bg="white", highlightbackground="black", 
                           highlightcolor="black", highlightthickness=1)
                cell.grid(column=y, row=x)
                cell.bind('<Button-1>', self.On_Click)
                self.cells.append(cell)

        control_frame = Frame(self.root, height=cell_size)
        control_frame.grid(column=0, row=1, sticky=(N,E,S,W))

        new_button = Button(control_frame, text="New", command=self.New_On_Click)
        new_button.grid(column=0, row=0, columnspan=2, sticky=(N, E, S, W), padx=5, pady=5)

        save_button = Button(control_frame, text="Save", command=self.Save_On_Click)
        save_button.grid(column=2, row=0, columnspan=2, sticky=(N, E, S, W), padx=5, pady=5)

        edit_button = Button(control_frame, text="Edit", command=self.Edit_On_Click)
        edit_button.grid(column=8, row=0, columnspan=2, sticky=(N, E, S, W), padx=5, pady=5)

        erase_button = Button(control_frame, text="Erase", command=self.Erase_On_Click)
        erase_button.grid(column=10, row=0, columnspan=2, sticky=(N, E, S, W), padx=5, pady=5)

        self.colour_canvas = Frame(control_frame, borderwidth=2, relief='raised', bg="white")
        self.colour_canvas.grid(column=15, row=0, sticky=(N, E, S, W), padx=4, pady=4)

        colour_select_button = Button(control_frame, text="Select Colour", command=self.Colour_Selection_On_Click)
        colour_select_button.grid(column=17, row=0, columnspan=3, sticky=(N, E, S, W), padx=5, pady=5)

        cols, rows = control_frame.grid_size()
        for col in range(cols):
            control_frame.columnconfigure(col, minsize=cell_size)
        control_frame.rowconfigure(0, minsize=cell_size)

    def On_Click(self, event):
        widget = event.widget
        index = self.cells.index(widget)
        selected_cell = self.cells[index]

        if self.is_erase_selected:
            selected_cell.configure(bg="white")

        if self.is_edit_selected and self.colour_selected is not None:
            selected_cell.configure(bg=self.colour_selected)

    def New_On_Click(self):
        for cell in self.cells:
            cell.configure(bg="white")
        self.colour_selected = None
        self.is_edit_selected = False
        self.is_erase_selected = False
        self.colour_canvas.configure(bg="white")

    def Save_On_Click(self):
        # ask the user where to save and what format to use
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg"),
                       ("Bitmap image", "*.bmp"), ("GIF image", "*.gif"),
                       ("All files", "*.*")]
        )

        if not file_path:
            return

        # build a PIL image the same pixel size as the grid
        image_width = self.grid_width * self.cell_size
        image_height = self.grid_height * self.cell_size
        image = Image.new("RGB", (image_width, image_height), "white")
        draw = ImageDraw.Draw(image)

        # walk the cells in the same order they were created (row-major)
        for index, cell in enumerate(self.cells):
            row = index // self.grid_width
            col = index % self.grid_width

            x0 = col * self.cell_size
            y0 = row * self.cell_size
            x1 = x0 + self.cell_size
            y1 = y0 + self.cell_size

            colour = cell.cget("bg")
            draw.rectangle([x0, y0, x1, y1], fill=colour)

        image.save(file_path)

    def Edit_On_Click(self):
        self.is_edit_selected = True
        self.is_erase_selected = False

    def Erase_On_Click(self):
        self.is_erase_selected = True
        self.is_edit_selected = False

    def Colour_Selection_On_Click(self):
        Colour_Sel = self.colour_selecter.show()
        selected = Colour_Sel[1]
        if selected is not None:
            self.colour_selected = selected
            self.colour_canvas.configure(bg=selected)


root = Tk()
MainApp(root)
root.mainloop()
