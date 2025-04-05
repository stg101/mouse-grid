
import tkinter as tk

# --- Configuration ---
ROW_KEYS = "QWERTASDFGZXCVB" # Keys defining Rows (e.g., Q*, W*, E*...)
COL_KEYS = "YUIOPHJKL;NM,./" # Keys defining Columns (e.g., *H, *J, *K...)

# Appearance
GRID_ALPHA = 0.5       # Transparency (0.0=invisible, 1.0=opaque) - Set in original code
GRID_BG = 'black'      # Background of the overlay window - Set in original code
LABEL_COLOR = "white"
LABEL_FONT = ("Arial", 12, "bold") # Increased font size
HIGHLIGHT_COLOR = "red"
HIGHLIGHT_RADIUS = 12  # Slightly bigger highlight

# --- Global State (Simpler integration, less ideal than a class) ---
input_sequence = ""
grid_points = {} # Dictionary to store { "label": (x, y) }
highlight_oval_id = None

########################################

last_key = None
last_press_timestamp = None
grid_open = False

def on_key(event):
    global last_key, last_press_timestamp, grid_open
    print(f"Key pressed: {event.keysym}")
    if event.keysym == "Escape":
        root.destroy()

    if (last_press_timestamp is not None
        and event.time - last_press_timestamp < 400
        and last_key == 'ISO_Level3_Shift'
        and event.keysym == 'Tab'):
        grid_open = True

    last_key = event.keysym
    last_press_timestamp = event.time
    print(grid_open)
    print(event.time)

def calculate_and_draw_labels(canvas, screen_width, screen_height):
    """Calculates grid points, stores them, and draws labels."""
    global grid_points # Modify global dictionary

    print("Calculating and drawing labels...")
    grid_points = {} # Clear previous points
    num_rows = len(ROW_KEYS)
    num_cols = len(COL_KEYS)
    line_color = "white"
    line_width = 1

    # Calculate spacing
    x_spacing = screen_width / (num_cols)
    y_spacing = screen_height / (num_rows)
    half_x_spacing = x_spacing / 2
    half_y_spacing = y_spacing / 2

    # Clear only old labels and highlights if they exist
    canvas.delete("labels")
    canvas.delete("highlight") # Ensure no old highlight persists
    canvas.delete("gridline")

    for r_idx, r_key in enumerate(ROW_KEYS):
        for c_idx, c_key in enumerate(COL_KEYS):
            label = r_key.upper() + c_key.upper()
            x = int(x_spacing * (c_idx + 1) - half_x_spacing)
            y = int(y_spacing * (r_idx + 1) - half_y_spacing)
            grid_points[label] = (x, y)
            # Draw the uppercase label text with a specific tag
            canvas.create_text(x, y, text=label, fill=LABEL_COLOR, font=LABEL_FONT, tags="labels")

    for x in range(0, screen_width, int(x_spacing)):
        canvas.create_line(x, 0, x, screen_height, fill=line_color, width=line_width, tags="gridline")
    for y in range(0, screen_height, int(y_spacing)):
        canvas.create_line(0, y, screen_width, y, fill=line_color, width=line_width, tags="gridline")

    print(f"Calculated and drew {len(grid_points)} labels.")


root = tk.Tk()
root.attributes('-fullscreen', True)
root.wait_visibility(root) # Wait for window manager interaction
root.wm_attributes("-alpha", 0.5) # Set transparency
root.attributes("-topmost", True) # Keep window on top

try:
    screen_width, screen_height = pyautogui.size()
    print(f"Using pyautogui screen size: {screen_width}x{screen_height}")
except Exception as e:
    print(f"Pyautogui size failed ({e}), using Tkinter fallback.")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    print(f"Using Tkinter screen size: {screen_width}x{screen_height}")


canvas = tk.Canvas(root, width=screen_width, height=screen_height,
                   bg=GRID_BG, highlightthickness=0)
canvas.pack()
calculate_and_draw_labels(canvas, screen_width, screen_height)


root.bind("<Key>", on_key)
root.mainloop()

