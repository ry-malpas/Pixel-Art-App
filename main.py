import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw

class PixelEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Editor")
        self.root.geometry("900x800")
        
        self.CELL_SIZE = 20
        self.GRID_W = 32
        self.GRID_H = 32
        self.total_width = self.GRID_W * self.CELL_SIZE
        self.total_height = self.GRID_H * self.CELL_SIZE
        
        self.grid_data = [[(255, 255, 255) for _ in range(self.GRID_W)] for _ in range(self.GRID_H)]
        
        self.undo_stack = []
        self.max_history = 50
        
        self.current_tool = 'edit'     
        self.selected_color = (0, 0, 0)   
        self.selected_hex = "#000000"
        
        self.brush_size = 1
        self.drag_start = None           
        self.last_paint_position = (-1, -1)
        self.zoom_level = 1.0
        self.scroll_x = 0
        self.scroll_y = 0
        
        self.setup_ui()
        self.setup_menu()

    def rgb_to_hex(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)


        left_panel = ttk.LabelFrame(main_frame, text="Tools & Settings", padding=(2, 5))
        left_panel.grid(row=0, column=0, sticky="nsew")


        brush_frame = ttk.LabelFrame(left_panel, text="Brush Options", padding=(2, 3))
        brush_frame.pack(fill=tk.X, pady=(2, 5))
        
        brush_type_label = ttk.Label(brush_frame, text="Size:")
        brush_type_label.pack(side=tk.LEFT, padx=5)


        self.brush_var = tk.StringVar()
        self.brush_var.set("1")


        self.brush_combo = ttk.Combobox(
            brush_frame, 
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
            textvariable=self.brush_var,
            state="readonly",
            width=10
        )
        
        self.brush_combo.bind("<<ComboboxSelected>>", lambda event: self.set_brush_size(self.brush_var.get()))
        self.brush_combo.pack(side=tk.LEFT, padx=2)


        color_frame = ttk.Frame(left_panel)
        color_frame.pack(fill=tk.X, pady=(2, 5))
        
        ttk.Label(color_frame, text="Color:").pack(side=tk.LEFT, padx=2)
        self.color_btn = ttk.Button(
            color_frame, 
            text=self.selected_hex.upper(),
            command=self.pick_color,
            width=15
        )
        self.color_btn.pack(side=tk.LEFT, padx=5)


        tool_frame = ttk.Frame(left_panel)
        tool_frame.pack(fill=tk.X, pady=5)
        
        self.btn_edit = ttk.Button(tool_frame, text="Paint", command=lambda: self.switch_tool('edit'))
        self.btn_edit.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.btn_erase = ttk.Button(tool_frame, text="Erase", command=lambda: self.switch_tool('erase'))
        self.btn_erase.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)


        zoom_frame = ttk.LabelFrame(left_panel, text="View Options", padding=(2, 3))
        zoom_frame.pack(fill=tk.X, pady=(2, 5))
        
        self.zoom_var = tk.StringVar()
        self.zoom_var.set("100%")
        
        self.zoom_slider = ttk.Scale(
            zoom_frame, 
            from_=25, to=400, 
            length=150,
            orient=tk.HORIZONTAL,
            command=self.on_zoom_change
        )
        self.zoom_slider.pack(side=tk.LEFT, padx=5)


        self.btn_zoom_in = ttk.Button(zoom_frame, text="+", width=3, command=self.zoom_in)
        self.btn_zoom_in.pack(side=tk.LEFT, padx=2)
        
        self.btn_zoom_out = ttk.Button(zoom_frame, text="-", width=3, command=self.zoom_out)
        self.btn_zoom_out.pack(side=tk.LEFT, padx=2)


        self.canvas_container = tk.Frame(main_frame)
        self.canvas_container.grid(row=0, column=1, sticky="nsew")
        
        self.scroll_x_scrollbar = ttk.Scrollbar(self.canvas_container, orient=tk.HORIZONTAL)
        self.scroll_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.scroll_y_scrollbar = ttk.Scrollbar(self.canvas_container)
        self.scroll_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(
            self.canvas_container, 
            width=self.total_width * self.zoom_level, 
            height=self.total_height * self.zoom_level, 
            bg='#e0e0e0', 
            highlightthickness=2,
            highlightbackground='#888888',
            bd=0,
            xscrollcommand=self.scroll_x_scrollbar.set,
            yscrollcommand=self.scroll_y_scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scroll_x_scrollbar.config(command=lambda arg: self.scroll_x(arg))
        self.scroll_y_scrollbar.config(command=lambda arg: self.scroll_y(arg))


        self.canvas.bind("<Button-1>", self.on_click_start)   
        self.canvas.bind("<B1-Motion>", self.on_click_move)   
        self.canvas.bind("<ButtonRelease-1>", self.on_click_end)   
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)



        self.status_var = tk.StringVar()
        self.status_var.set("Click & drag to paint")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")



    def switch_tool(self, tool_name):
        self.current_tool = tool_name
        
        self.btn_edit.config(state='normal')
        self.btn_erase.config(state='normal')
        
        if tool_name == 'edit':
            self.update_status(f"Tool: Paint (Size: {self.brush_size}, Color: {self.selected_hex.upper()})")
        else:
            self.update_status("Erase tool selected (paints white)")

    def set_brush_size(self, size_str):
        try:
            self.brush_size = int(size_str)
        except ValueError:
            pass
        
        if self.brush_size == 1:
            self.update_status("Single pixel brush")
        else:
            self.update_status(f"Brush Size: {self.brush_size}×{self.brush_size}")

    def pick_color(self):
        result = colorchooser.askcolor(color=self.selected_color, title="Pick Color")
        
        if result and result[0] is not None:
            try:
                hex_str = result[1].lower()
                self.selected_hex = hex_str
                
                color_tuple_str = hex_str.lstrip('#')
                r = int(color_tuple_str[0:2], 16)
                g = int(color_tuple_str[2:4], 16)
                b = int(color_tuple_str[4:6], 16)
                self.selected_color = (r, g, b)
                
                self.color_btn.config(text=self.selected_hex.upper())
            except (IndexError, ValueError):
                self.selected_color = (0, 0, 0)
                self.selected_hex = "#000000"
                self.color_btn.config(text="#000000")


    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Canvas", command=self.new_canvas)
        file_menu.add_command(label="Save...", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)


        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo_action)
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear All", command=self.new_canvas)


        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Grid Size...", command=self.set_grid_size)
        settings_menu.add_separator()
        settings_menu.add_command(label="About", command=self.show_about)

    def set_grid_size(self):
        new_width = tk.simpledialog.askinteger("Grid Width", 
                                  f"Enter number of tiles (current: {self.GRID_W})",
                                  initialvalue=self.GRID_W,
                                  minvalue=8)
        
        if new_width and 0 < new_width <= 256:
            new_height = tk.simpledialog.askinteger("Grid Height", 
                                          f"Enter number of tiles (current: {self.GRID_H})",
                                          initialvalue=self.GRID_H,
                                          minvalue=8)
            
            if new_height and 0 < new_height <= 256:
                self.GRID_W = new_width
                self.GRID_H = new_height
                
                self.total_width = self.GRID_W * self.CELL_SIZE
                self.total_height = self.GRID_H * self.CELL_SIZE
                
                max_brush_size = min(self.GRID_W, self.GRID_H)
                if self.brush_size > max_brush_size:
                    self.brush_size = max_brush_size
                
                self.grid_data = [[(255, 255, 255) for _ in range(self.GRID_W)] 
                                  for _ in range(self.GRID_H)]
                self.undo_stack = []
                
                self._redraw_all()
                
                self.update_status(f"Grid resized: {self.GRID_W}×{self.GRID_H}")


    def show_about(self):
        messagebox.showinfo("About", "Pixel Editor\nSingle Pixel Brush with Undo")

    def _redraw_all(self):
        self.canvas.delete('all')
        
        for r in range(self.GRID_H):
            for c in range(self.GRID_W):
                color_tuple = self.grid_data[r][c]
                hex_color = self.rgb_to_hex(color_tuple[0], color_tuple[1], color_tuple[2])
                
                x0, y0 = c * self.CELL_SIZE * self.zoom_level + self.scroll_x, r * self.CELL_SIZE * self.zoom_level + self.scroll_y
                x1, y1 = (c + 1) * self.CELL_SIZE * self.zoom_level + self.scroll_x, (r + 1) * self.CELL_SIZE * self.zoom_level + self.scroll_y
                
                self.canvas.create_rectangle(
                    x0, y0, x1 - 1, y1 - 1,
                    fill=hex_color,
                    outline=''
                )

    def on_click_start(self, event):
        col = int((event.x - self.scroll_x) / (self.CELL_SIZE * self.zoom_level))
        row = int((event.y - self.scroll_y) / (self.CELL_SIZE * self.zoom_level))
        
        if not self.drag_start:
            self.undo_stack.append(self.get_grid_snapshot())
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
                
        self.drag_start = (row, col)
        
        self._paint_at(col, row)
        
        self._redraw_all()
    
    def on_click_move(self, event):
        col = int((event.x - self.scroll_x) / (self.CELL_SIZE * self.zoom_level))
        row = int((event.y - self.scroll_y) / (self.CELL_SIZE * self.zoom_level))
        
        if 0 <= row < self.GRID_H and 0 <= col < self.GRID_W:
            if (self.drag_start is not None):
                prev_col = self.drag_start[1]
                prev_row = self.drag_start[0]
                
                if col != prev_col or row != prev_row:
                    self._paint_at(col, row)
                    self._redraw_all()


    def on_click_end(self, event):
        self.drag_start = None
    
    def _get_brush_offsets(self):
        start_offset = -(self.brush_size - 1) // 2
        cells = []
        
        for dx in range(start_offset, start_offset + self.brush_size):
            for dy in range(start_offset, start_offset + self.brush_size):
                cells.append((dx, dy))
        
        return cells

    def _paint_at(self, col, row):
        if not (0 <= row < self.GRID_H and 0 <= col < self.GRID_W):
            return
        
        cells = self._get_brush_offsets()
        
        for dx, dy in cells:
            new_col = col + dx
            new_row = row + dy
            
            if 0 <= new_row < self.GRID_H and 0 <= new_col < self.GRID_W:
                old_color = self.grid_data[new_row][new_col]
                
                if self.current_tool == 'edit':
                    new_color = self.selected_color
                else:
                    new_color = (255, 255, 255)
                    
                if old_color != new_color:
                    self.grid_data[new_row][new_col] = new_color


    def undo_action(self):
        if self.undo_stack:
            snapshot = self.undo_stack.pop()
            self.grid_data = [list(row) for row in snapshot]
            self._redraw_all()
            self.update_status("Undo applied")


    def get_grid_snapshot(self):
        return [[tuple(col) for col in row] 
                for row in self.grid_data]

    
    def new_canvas(self):
        confirm = messagebox.askyesno("Discard?", "Unsaved changes will be lost.")
        if confirm:
            self.drag_start = None
            
            self.undo_stack = []
            
            self.grid_data = [[(255, 255, 255) for _ in range(self.GRID_W)] 
                              for _ in range(self.GRID_H)]
            
            self.brush_size = 1
            self.brush_var.set("1")
            
            self.selected_color = (255, 255, 255)
            self.selected_hex = "#ffffff"
            self.color_btn.config(text="#FFFFFF")
            
            self.switch_tool('edit')
            
            self._redraw_all()
            
            self.update_status("Canvas cleared")


    def save_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")]
        )
        
        if file_path:
            img = Image.new("RGB", (self.total_width, self.total_height))
            draw = ImageDraw.Draw(img)
            
            for r in range(self.GRID_H):
                for c in range(self.GRID_W):
                    color_tuple = self.grid_data[r][c]
                    
                    x0, y0 = c * self.CELL_SIZE, r * self.CELL_SIZE
                    x1, y1 = (c + 1) * self.CELL_SIZE, (r + 1) * self.CELL_SIZE
                    
                    draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=color_tuple[:3])
                
            img.save(file_path, format='PNG')
            self.update_status(f"Saved: {file_path}")


    def scroll_x(self, arg):
        self.scroll_x = int(arg)

    def scroll_y(self, arg):
        self.scroll_y = int(arg)

    def on_zoom_change(self, value):
        percentage = float(value.split('%')[0])
        new_zoom = percentage / 100.0
        if new_zoom < 0.25 or new_zoom > 4:
            return
        
        old_scroll_x = self.scroll_x
        old_scroll_y = self.scroll_y
        
        self.zoom_level = new_zoom
        
        new_scroll_x = old_scroll_x * (1 - self.zoom_level / new_zoom)
        new_scroll_y = old_scroll_y * (1 - self.zoom_level / new_zoom)
        
        self.scroll_x = max(0, min(new_scroll_x, self.total_width * self.zoom_level - 40))
        self.scroll_y = max(0, min(new_scroll_y, self.total_height * self.zoom_level - 40))
        
        self._redraw_all()

    def zoom_in(self):
        new_zoom = self.zoom_level + 0.1
        if new_zoom <= 4:
            self.on_zoom_change(f"{new_zoom * 100}%")

    def zoom_out(self):
        new_zoom = self.zoom_level - 0.1
        if new_zoom >= 0.25:
            self.on_zoom_change(f"{new_zoom * 100}%")

    def on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.scroll_y -= 20
        else:
            self.scroll_y += 20
        
        self.scroll_x = max(0, min(self.scroll_x, self.total_width * self.zoom_level - 40))
        self.scroll_y = max(0, min(self.scroll_y, self.total_height * self.zoom_level - 40))
        
        self._redraw_all()

    def save_settings(self):
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Settings File", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            import json
            settings = {
                'grid_width': self.GRID_W,
                'grid_height': self.GRID_H,
                'cell_size': self.CELL_SIZE,
                'brush_size': self.brush_size,
                'zoom_level': self.zoom_level,
                'scroll_x': self.scroll_x,
                'scroll_y': self.scroll_y,
            }
            try:
                with open(file_path, 'w') as f:
                    json.dump(settings, f)
                self.update_status("Settings saved")
            except Exception as e:
                self.update_status(f"Error saving settings: {e}")


    def update_status(self, message):
        self.status_var.set(message)


if __name__ == "__main__":
    root = tk.Tk()
    app = PixelEditorApp(root)
    app._redraw_all()
    root.mainloop()
