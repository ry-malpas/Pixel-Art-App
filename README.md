# Pixel Art Editor

A simple desktop pixel art editor built with Python and Tkinter. The application provides a straightforward graphical interface for drawing on a pixel grid and exporting the result as an image file.

## Features

- Draw on a 70x70 pixel grid
- Select any colour using the built-in colour chooser
- Erase individual pixels
- Clear the entire canvas with **New**
- Export artwork as PNG, JPEG, BMP, or GIF
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

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the Application**
```bash
python main.py
```

## Usage

### Drawing a Pixel
1. Click **Select Colour** and choose a colour.
2. Click the **Edit** button to enable drawing mode.
3. Click any cell on the grid to fill it with the selected colour.

### Erasing a Pixel
1. Click the **Erase** button to enable erase mode.
2. Click any cell on the grid to reset it to white.

### Starting a New Canvas
Click the **New** button to clear every cell back to white.

> **Warning:** The New button removes all drawing from the current session.

### Saving Your Artwork
1. Click the **Save** button.
2. Choose a file location, name, and format (PNG, JPEG, BMP, or GIF).
3. The current grid is exported as an image file.

## Project Structure

```
.
├── main.py
├── requirements.txt
└── README.md
```

## Code Overview

The application uses an object-oriented design with the `MainApp` class managing the user interface and grid data.

### MainApp

The `MainApp` class is responsible for:
- Creating the application window
- Building the pixel grid
- Managing drawing and erase modes
- Handling colour selection
- Exporting the grid as an image

### Grid Storage

Each pixel is represented by a Tkinter `Frame` widget stored in the `cells` list, in the same row-major order the grid was created. A cell's current colour is read directly from its background (`bg`) property when saving.

### Main Methods

| Method | Description |
|---|---|
| `On_Click()` | Colours or erases a cell depending on the active mode |
| `New_On_Click()` | Clears the entire grid back to white |
| `Save_On_Click()` | Exports the current grid as an image file |
| `Edit_On_Click()` | Enables drawing mode |
| `Erase_On_Click()` | Enables erase mode |
| `Colour_Selection_On_Click()` | Opens the colour picker and sets the active drawing colour |

## Technologies

- Python
- Tkinter
- Pillow
