# Pixel Art Editor

A simple desktop pixel art editor built with Python and Tkinter. The application provides a straightforward graphical interface for drawing on a pixel grid and exporting the result as an image file.

## Features

- Draw on a resizable pixel grid (32x32 by default, adjustable up to 256x256)
- Adjustable brush size from 1x1 up to 9x9
- Select any colour using the built-in colour chooser
- Erase individual pixels
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
git clone https://github.com/your-username/your-repository.git
```

**2. Navigate to the Project**
```bash
cd your-repository
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

### Drawing a Pixel
1. Click **Color** and choose a colour.
2. Select a brush size from the **Size** dropdown.
3. Make sure the **Paint** tool is selected.
4. Click or click-and-drag on the canvas to paint.

### Erasing a Pixel
1. Click the **Erase** button to enable erase mode.
2. Click or click-and-drag on the canvas to reset cells to white.

### Zooming and Panning
- Use the zoom slider or the **+**/**-** buttons to zoom from 25% to 400%.
- Scroll with the mouse wheel or the scrollbars to pan around the canvas.

### Undoing an Action
Select **Edit > Undo** to revert the most recent paint or erase action. Up to 50 previous states are stored.

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
- Managing paint, erase, brush size, zoom, and pan state
- Handling colour selection
- Maintaining undo history
- Resizing the grid at runtime
- Exporting the grid as an image

### Grid Storage

Each pixel's colour is stored as an `(r, g, b)` tuple in the `grid_data` 2D list, indexed by row and column. The canvas is fully redrawn from `grid_data` whenever the grid changes, is panned, or is zoomed.

### Main Methods

| Method | Description |
|---|---|
| `on_click_start()` / `on_click_move()` / `on_click_end()` | Handle painting/erasing via click and drag |
| `_paint_at()` | Applies the current tool to a cell and its brush-size neighbours |
| `undo_action()` | Reverts to the previous grid snapshot |
| `new_canvas()` | Clears the entire grid back to white, after confirmation |
| `save_image()` | Exports the current grid as an image file |
| `switch_tool()` | Switches between Paint and Erase tools |
| `set_brush_size()` | Updates the active brush size |
| `pick_color()` | Opens the colour picker and sets the active drawing colour |
| `set_grid_size()` | Prompts for and applies a new grid width/height |
| `on_zoom_change()` / `zoom_in()` / `zoom_out()` | Adjust the current zoom level |
| `_redraw_all()` | Repaints the canvas from `grid_data` |

## Technologies

- Python
- Tkinter
- Pillow
