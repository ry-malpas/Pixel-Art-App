# Pixel Art Editor

A simple desktop pixel art editor built with Python and Tkinter. The application provides a straightforward graphical interface for drawing on a pixel grid, using freehand and shape tools, and exporting the result as an image file.

## Features

- Draw on a resizable pixel grid (32x32 by default, adjustable up to 256x256)
- Freehand **Paint** and **Erase** tools
- **Line**, **Square**, and **Diamond** shape tools with a live preview while dragging
- Lines drawn with **Bresenham's line algorithm** for clean, gap-free pixel lines
- Adjustable brush size from 1x1 up to 9x9 (applies to freehand drawing and shape outlines)
- Select any colour using the built-in colour chooser
- Zoom in and out (25% to 400%) with a slider, buttons, or mouse wheel
- Undo up to 50 previous actions
- Clear the entire canvas with **New Canvas** (with confirmation prompt)
- Export artwork as PNG or JPEG
- Simple graphical user interface
- Only one external package required (Pillow)

## Requirements

- Python 3.x
- Tkinter
- Pillow

> Tkinter is included with most standard Python installations.

## Installation

**1. Clone the Repository**
```bash
git clone https://github.com/ry-malpas/Pixel-Art-App.git
```

**2. Navigate to the Project**
```bash
cd Pixel-Art-App
```

**3. Create and Activate a Virtual Environment**
```bash
python -m venv venv
```

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

> Pillow is installed inside this virtual environment to keep it isolated from your system Python packages.

**4. Install Dependencies**
```bash
pip install -r requirements.txt
```

**5. Run the Application**
```bash
python main.py
```

> Remember to activate the virtual environment (step 3) each time before running the app in a new terminal session.

## Usage

### Tools

| Tool | Behaviour |
|---|---|
| **Paint** | Click or click-and-drag to paint cells in the selected colour |
| **Erase** | Click or click-and-drag to reset cells to white |
| **Line** | Click and drag between two points to draw a straight line |
| **Square** | Click and drag to set opposite corners of a square/rectangle outline |
| **Diamond** | Click and drag to set opposite corners of the diamond's bounding box |

The active tool is shown in the status bar.

### Drawing a Pixel
1. Click **Color** and choose a colour.
2. Select a brush size from the **Size** dropdown.
3. Make sure the **Paint** tool is selected.
4. Click or click-and-drag on the canvas to paint.

### Drawing Shapes
1. Click **Color** and choose a colour.
2. Select a brush size from the **Size** dropdown (this sets the outline thickness).
3. Select the **Line**, **Square**, or **Diamond** tool.
4. Click and hold at the starting point, then drag to the end point.
5. A live preview follows the cursor; release the mouse button to commit the shape.

> - Shapes are outlines only (not filled).
> - Start and end points are clamped to the grid, so you can drag past the edge of the canvas.
> - Each shape is a single undo step.
> - Switching tools mid-drag cancels any shape in progress.

### Erasing a Pixel
1. Click the **Erase** button to enable erase mode.
2. Click or click-and-drag on the canvas to reset cells to white.

### Zooming and Panning
- Use the zoom slider or the **+**/**-** buttons to zoom from 25% to 400%.
- Scroll with the mouse wheel or the scrollbars to pan around the canvas.

### Undoing an Action
Select **Edit > Undo** to revert the most recent paint, erase, or shape action. Up to 50 previous states are stored.

### Resizing the Grid
Select **Settings > Grid Size...** and enter a new width and height (8–256 tiles). Resizing clears the current canvas and undo history.

### Starting a New Canvas
Select **File > New Canvas** (or **Edit > Clear All**) to clear every cell back to white. You will be asked to confirm first.

> **Warning:** New Canvas removes all drawing from the current session and cannot be undone.

### Saving Your Artwork
1. Select **File > Save...**.
2. Choose a file location and name (PNG or JPEG).
3. The current grid is exported as an image file.

## Project Structure

```
.
├── main.py
├── requirements.txt
└── README.md
```

## Code Overview

The application uses an object-oriented design with the `PixelEditorApp` class managing the user interface and grid data.

### PixelEditorApp

The `PixelEditorApp` class is responsible for:
- Creating the application window and menu bar
- Rendering the pixel grid on a single Canvas
- Managing paint, erase, shape tool, brush size, zoom, and pan state
- Calculating shape outlines (line, square, diamond) and previewing them live
- Handling colour selection
- Maintaining undo history
- Resizing the grid at runtime
- Exporting the grid as an image

### Grid Storage

Each pixel's colour is stored as an `(r, g, b)` tuple in the `grid_data` 2D list, indexed by row and column. The canvas is fully redrawn from `grid_data` whenever the grid changes, is panned, or is zoomed.

### Shape Tools and Bresenham's Line Algorithm

Every shape tool works in three steps:

1. **Base cells** – `_get_shape_base_cells()` returns the list of `(row, col)` cells that make up a 1-pixel-wide outline between the drag start and the current cursor position.
2. **Brush expansion** – `_apply_brush()` expands each base cell by the current brush size and clips the result to the grid, giving a set of unique cells (so overlapping brush areas are only painted once).
3. **Preview / commit** – while dragging, `_draw_shape_preview()` draws the cells on top of a fresh redraw without touching `grid_data`. On mouse release, `_commit_shape()` writes the cells into `grid_data`.

**Bresenham's line algorithm** (`_bresenham_line()`) is used to generate the base cells for the **Line** tool and for each edge of the **Diamond** tool. It walks from the start cell to the end cell one step at a time, using only integer arithmetic:

- `dx` is the absolute horizontal distance and `dy` is the negative absolute vertical distance.
- `sx` / `sy` are the step directions (+1 or -1) on each axis.
- An error term (`err = dx + dy`) tracks how far the current cell is from the ideal line. At each step, `2 * err` is compared against `dy` and `dx` to decide whether to step in x, y, or both.
- This handles all octants (steep, shallow, and diagonal lines in any direction) and produces a continuous line with no gaps and no floating-point arithmetic.

How each shape builds its base cells:

| Shape | Method | Approach |
|---|---|---|
| Line | `_bresenham_line()` | A single Bresenham line from start to end |
| Square | `_rect_outline_cells()` | Iterates the top, bottom, left, and right edges of the bounding box (no Bresenham needed as edges are axis-aligned) |
| Diamond | `_diamond_outline_cells()` | Four Bresenham lines connecting the midpoints of each side of the bounding box |

For the diamond, the midpoints are calculated with integer division, so the shape is slightly asymmetric when the bounding box has an even width or height.

### Undo Behaviour

A snapshot of `grid_data` is pushed to `undo_stack` when a paint stroke starts or a shape drag starts (capped at `max_history`, 50 by default). Because shapes only modify `grid_data` on mouse release, a shape is always exactly one undo step.

### Main Methods

| Method | Description |
|---|---|
| `on_click_start()` / `on_click_move()` / `on_click_end()` | Handle painting/erasing and shape drawing via click and drag |
| `_paint_at()` | Applies the current tool to a cell and its brush-size neighbours |
| `_event_to_cell()` | Converts mouse coordinates to a `(row, col)` cell, accounting for zoom and scroll |
| `_clamp_cell()` | Clamps a cell to the grid bounds (used for shape endpoints) |
| `_bresenham_line()` | Returns the cells along a line between two points using Bresenham's algorithm |
| `_rect_outline_cells()` | Returns the outline cells of a rectangle between two corners |
| `_diamond_outline_cells()` | Returns the outline cells of a diamond inscribed in a bounding box |
| `_get_shape_base_cells()` | Dispatches to the correct outline generator for the active shape tool |
| `_get_brush_offsets()` | Returns the cell offsets covered by the current brush size |
| `_apply_brush()` | Expands base cells by the brush size and clips them to the grid |
| `_draw_shape_preview()` | Draws the in-progress shape on the canvas without modifying `grid_data` |
| `_commit_shape()` | Writes the finished shape into `grid_data` |
| `undo_action()` | Reverts to the previous grid snapshot |
| `new_canvas()` | Clears the entire grid back to white, after confirmation |
| `save_image()` | Exports the current grid as an image file |
| `switch_tool()` | Switches between Paint, Erase, Line, Square, and Diamond tools and cancels any shape in progress |
| `set_brush_size()` | Updates the active brush size |
| `pick_color()` | Opens the colour picker and sets the active drawing colour |
| `set_grid_size()` | Prompts for and applies a new grid width/height |
| `on_zoom_change()` / `zoom_in()` / `zoom_out()` | Adjust the current zoom level |
| `_redraw_all()` | Repaints the canvas from `grid_data` |

## Technologies

- Python
- Tkinter
- Pillow
