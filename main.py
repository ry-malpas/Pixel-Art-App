import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw

class PixelEditorApp:
    SHAPE_TOOLS = ('line', 'square', 'diamond')

    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Editor")
        self.root.geometry("900x800")
        
        self.cell_size = 20
        self.grid_w = 32
        self.grid_h = 32
        self.total_width = self.grid_w * self.cell_size
        self.total_height = self.grid_h * self.cell_size
        
        self.grid_data = [[(255, 255, 255) for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        
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
        
        self.shape_start = None
        self.shape_current = None
        
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

        tool_frame2 = ttk.Frame(left_panel)
        tool_frame2.pack(fill=tk.X, pady=(0, 5))

        self.btn_line = ttk.Button(tool_frame2, text="Line", command=lambda: self.switch_tool('line'))
        self.btn_line.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        self.btn_square = ttk.Button(tool_frame2, text="Square", command=lambda: self.switch_tool('square'))
        self.btn_square.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        self.btn_diamond = ttk.Button(tool_frame2, text="Diamond", command=lambda: self.switch_tool('diamond'))
        self.btn_diamond.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)


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
            bd=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scroll_x_scrollbar.config(command=self.on_scroll_x)
        self.scroll_y_scrollbar.config(command=self.on_scroll_y)


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
        self.shape_start = None
        self.shape_current = None
        self.drag_start = None

        self.current_tool = tool_name
        
        self.btn_edit.config(state='normal')
        self.btn_erase.config(state='normal')
        self.btn_line.config(state='normal')
        self.btn_square.config(state='normal')
        self.btn_diamond.config(state='normal')
        
        if tool_name == 'edit':
            self.update_status(f"Tool: Paint (Size: {self.brush_size}, Color: {self.selected_hex.upper()})")
        elif tool_name == 'erase':
            self.update_status("Erase tool selected (paints white)")
        elif tool_name == 'line':
            self.update_status(f"Line tool: click & drag between two points (Size: {self.brush_size})")
        elif tool_name == 'square':
            self.update_status(f"Square tool: click & drag to set opposite corners (Size: {self.brush_size})")
        elif tool_name == 'diamond':
            self.update_status(f"Diamond tool: click & drag to set opposite corners (Size: {self.brush_size})")

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
                                  f"Enter number of tiles (current: {self.grid_w})",
                                  initialvalue=self.grid_w,
                                  minvalue=8)
        
        if new_width and 0 < new_width <= 256:
            new_height = tk.simpledialog.askinteger("Grid Height", 
                                          f"Enter number of tiles (current: {self.grid_h})",
                                          initialvalue=self.grid_h,
                                          minvalue=8)
            
            if new_height and 0 < new_height <= 256:
                self.grid_w = new_width
                self.grid_h = new_height
                
                self.total_width = self.grid_w * self.cell_size
                self.total_height = self.grid_h * self.cell_size
                
                max_brush_size = min(self.grid_w, self.grid_h)
                if self.brush_size > max_brush_size:
                    self.brush_size = max_brush_size
                
                self.grid_data = [[(255, 255, 255) for _ in range(self.grid_w)] 
                                  for _ in range(self.grid_h)]
                self.undo_stack = []
                
                self._redraw_all()
                
                self.update_status(f"Grid resized: {self.grid_w}×{self.grid_h}")


    def show_about(self):
        messagebox.showinfo("About", "Pixel Editor\nBrush, Line, Diamond & Square tools with Undo")

    def _redraw_all(self):
        self.canvas.delete('all')
        
        for r in range(self.grid_h):
            for c in range(self.grid_w):
                color_tuple = self.grid_data[r][c]
                hex_color = self.rgb_to_hex(color_tuple[0], color_tuple[1], color_tuple[2])
                
                x0, y0 = c * self.cell_size * self.zoom_level + self.scroll_x, r * self.cell_size * self.zoom_level + self.scroll_y
                x1, y1 = (c + 1) * self.cell_size * self.zoom_level + self.scroll_x, (r + 1) * self.cell_size * self.zoom_level + self.scroll_y
                
                self.canvas.create_rectangle(
                    x0, y0, x1 - 1, y1 - 1,
                    fill=hex_color,
                    outline=''
                )
        
        self._update_scrollbars()

    def _event_to_cell(self, event):
        col = int((event.x - self.scroll_x) / (self.cell_size * self.zoom_level))
        row = int((event.y - self.scroll_y) / (self.cell_size * self.zoom_level))
        return row, col

    def _clamp_cell(self, row, col):
        row = max(0, min(row, self.grid_h - 1))
        col = max(0, min(col, self.grid_w - 1))
        return row, col

    def _bresenham_line(self, r0, c0, r1, c1):
        cells = []
        x0, y0 = c0, r0
        x1, y1 = c1, r1
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        while True:
            cells.append((y0, x0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

        return cells

    def _rect_outline_cells(self, r0, c0, r1, c1):
        top = min(r0, r1)
        bottom = max(r0, r1)
        left = min(c0, c1)
        right = max(c0, c1)

        cells = []
        for c in range(left, right + 1):
            cells.append((top, c))
            cells.append((bottom, c))
        for r in range(top, bottom + 1):
            cells.append((r, left))
            cells.append((r, right))

        return cells

    def _diamond_outline_cells(self, r0, c0, r1, c1):
        top = min(r0, r1)
        bottom = max(r0, r1)
        left = min(c0, c1)
        right = max(c0, c1)
        mid_r = (top + bottom) // 2
        mid_c = (left + right) // 2

        cells = []
        cells += self._bresenham_line(top, mid_c, mid_r, left)
        cells += self._bresenham_line(top, mid_c, mid_r, right)
        cells += self._bresenham_line(bottom, mid_c, mid_r, left)
        cells += self._bresenham_line(bottom, mid_c, mid_r, right)
        return cells

    def _get_shape_base_cells(self, tool, start, end):
        r0, c0 = start
        r1, c1 = end
        if tool == 'line':
            return self._bresenham_line(r0, c0, r1, c1)
        elif tool == 'square':
            return self._rect_outline_cells(r0, c0, r1, c1)
        elif tool == 'diamond':
            return self._diamond_outline_cells(r0, c0, r1, c1)
        return []

    def _apply_brush(self, base_cells):
        offsets = self._get_brush_offsets()
        cells = set()
        for (row, col) in base_cells:
            for dx, dy in offsets:
                r = row + dy
                c = col + dx
                if 0 <= r < self.grid_h and 0 <= c < self.grid_w:
                    cells.add((r, c))
        return cells

    def _draw_shape_preview(self, start, end):
        base_cells = self._get_shape_base_cells(self.current_tool, start, end)
        preview_cells = self._apply_brush(base_cells)
        hex_color = self.selected_hex

        for (row, col) in preview_cells:
            x0 = col * self.cell_size * self.zoom_level + self.scroll_x
            y0 = row * self.cell_size * self.zoom_level + self.scroll_y
            x1 = (col + 1) * self.cell_size * self.zoom_level + self.scroll_x
            y1 = (row + 1) * self.cell_size * self.zoom_level + self.scroll_y

            self.canvas.create_rectangle(
                x0, y0, x1 - 1, y1 - 1,
                fill=hex_color,
                outline=''
            )

    def _commit_shape(self, start, end):
        base_cells = self._get_shape_base_cells(self.current_tool, start, end)
        final_cells = self._apply_brush(base_cells)

        for (row, col) in final_cells:
            self.grid_data[row][col] = self.selected_color

    def on_click_start(self, event):
        row, col = self._event_to_cell(event)

        if self.current_tool in self.SHAPE_TOOLS:
            row, col = self._clamp_cell(row, col)

            self.undo_stack.append(self.get_grid_snapshot())
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)

            self.shape_start = (row, col)
            self.shape_current = (row, col)

            self._redraw_all()
            self._draw_shape_preview(self.shape_start, self.shape_current)
            return

        if not self.drag_start:
            self.undo_stack.append(self.get_grid_snapshot())
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
                
        self.drag_start = (row, col)
        
        self._paint_at(col, row)
        
        self._redraw_all()
    
    def on_click_move(self, event):
        row, col = self._event_to_cell(event)

        if self.current_tool in self.SHAPE_TOOLS:
            if self.shape_start is not None:
                row, col = self._clamp_cell(row, col)
                self.shape_current = (row, col)
                self._redraw_all()
                self._draw_shape_preview(self.shape_start, self.shape_current)
            return

        if 0 <= row < self.grid_h and 0 <= col < self.grid_w:
            if (self.drag_start is not None):
                prev_col = self.drag_start[1]
                prev_row = self.drag_start[0]
                
                if col != prev_col or row != prev_row:
                    self._paint_at(col, row)
                    self._redraw_all()


    def on_click_end(self, event):
        if self.current_tool in self.SHAPE_TOOLS:
            if self.shape_start is not None and self.shape_current is not None:
                self._commit_shape(self.shape_start, self.shape_current)
            self.shape_start = None
            self.shape_current = None
            self._redraw_all()
            self.update_status(f"{self.current_tool.capitalize()} drawn")
            return

        self.drag_start = None
    
    def _get_brush_offsets(self):
        start_offset = -(self.brush_size - 1) // 2
        cells = []
        
        for dx in range(start_offset, start_offset + self.brush_size):
            for dy in range(start_offset, start_offset + self.brush_size):
                cells.append((dx, dy))
        
        return cells

    def _paint_at(self, col, row):
        if not (0 <= row < self.grid_h and 0 <= col < self.grid_w):
            return
        
        cells = self._get_brush_offsets()
        
        for dx, dy in cells:
            new_col = col + dx
            new_row = row + dy
            
            if 0 <= new_row < self.grid_h and 0 <= new_col < self.grid_w:
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
            self.shape_start = None
            self.shape_current = None
            
            self.undo_stack = []
            
            self.grid_data = [[(255, 255, 255) for _ in range(self.grid_w)] 
                              for _ in range(self.grid_h)]
            
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
            
            for r in range(self.grid_h):
                for c in range(self.grid_w):
                    color_tuple = self.grid_data[r][c]
                    
                    x0, y0 = c * self.cell_size, r * self.cell_size
                    x1, y1 = (c + 1) * self.cell_size, (r + 1) * self.cell_size
                    
                    draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=color_tuple[:3])
                
            img.save(file_path)
            self.update_status(f"Saved: {file_path}")
            


    def _clamp_offset(self, offset, content, view):
        if content <= view:
            return 0
        return max(view - content, min(0, offset))

    def on_scroll_x(self, *args):
        content_w = self.total_width * self.zoom_level
        view_w = max(self.canvas.winfo_width(), 1)
        
        if args[0] == 'moveto':
            self.scroll_x = -float(args[1]) * content_w
        elif args[0] == 'scroll':
            step = self.cell_size * self.zoom_level
            self.scroll_x -= float(args[1]) * step
        
        self.scroll_x = self._clamp_offset(self.scroll_x, content_w, view_w)
        self._redraw_all()

    def on_scroll_y(self, *args):
        content_h = self.total_height * self.zoom_level
        view_h = max(self.canvas.winfo_height(), 1)
        
        if args[0] == 'moveto':
            self.scroll_y = -float(args[1]) * content_h
        elif args[0] == 'scroll':
            step = self.cell_size * self.zoom_level
            self.scroll_y -= float(args[1]) * step
        
        self.scroll_y = self._clamp_offset(self.scroll_y, content_h, view_h)
        self._redraw_all()

    def _update_scrollbars(self):
        content_w = self.total_width * self.zoom_level
        content_h = self.total_height * self.zoom_level
        view_w = max(self.canvas.winfo_width(), 1)
        view_h = max(self.canvas.winfo_height(), 1)
        
        if content_w <= view_w:
            self.scroll_x_scrollbar.set(0, 1)
        else:
            first = -self.scroll_x / content_w
            last = (view_w - self.scroll_x) / content_w
            self.scroll_x_scrollbar.set(first, last)
        
        if content_h <= view_h:
            self.scroll_y_scrollbar.set(0, 1)
        else:
            first = -self.scroll_y / content_h
            last = (view_h - self.scroll_y) / content_h
            self.scroll_y_scrollbar.set(first, last)

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
        step = self.cell_size * self.zoom_level
        
        if event.num == 4 or event.delta > 0:
            self.scroll_y += step
        else:
            self.scroll_y -= step
        
        content_h = self.total_height * self.zoom_level
        view_h = max(self.canvas.winfo_height(), 1)
        self.scroll_y = self._clamp_offset(self.scroll_y, content_h, view_h)
        
        self._redraw_all()

    def save_settings(self):
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Settings File", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            import json
            settings = {
                'grid_width': self.grid_w,
                'grid_height': self.grid_h,
                'cell_size': self.cell_size,
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
    root.update_idletasks()
    app._redraw_all()
    root.mainloop()