import tkinter as tk
import time
import pyautogui # For clicking and screen size

# --- Configuration ---
ROW_KEYS = "QWERTASDFGZXCVB" # Keys defining Rows (e.g., Q*, W*, E*...)
COL_KEYS = "YUIOPHJKLNM" # Keys defining Columns (e.g., *H, *J, *K...)

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

def click(target_x, target_y):
    try:
        print(f"*** Executing pyautogui.click({target_x}, {target_y}) ***")
        pyautogui.click(target_x, target_y)
        print("*** Click executed. ***")
    except Exception as e:
        print(f"!!! Error during pyautogui.click: {e} !!!")
        # Optionally show window again if click fails
        # root.deiconify()
        # root.focus_force()

def move(target_x, target_y):
    try:
        print(f"*** Executing pyautogui.moveTo({target_x}, {target_y}) ***")
        pyautogui.moveTo(target_x, target_y)
        print("*** Move executed. ***")
    except Exception as e:
        print(f"!!! Error during pyautogui.moveTo: {e} !!!")

def on_key(event, root, canvas):
    """Handles key presses for coordinate input, clicking, or closing."""
    global input_sequence, grid_points, highlight_oval_id, handler # Access global state

    key_sym = event.keysym
    key_char = event.char.upper() # Use char for letters, convert to upper

    print(f"--- KeyPress: keysym='{key_sym}', char='{key_char}', Current sequence='{input_sequence}' ---")

    if key_sym == 'Escape':
        print("Escape pressed. Destroying window.")
        root.destroy()
        return

    key_to_check = key_char if key_char and key_char.isalpha() else "" # Only consider alpha chars

    if not key_to_check: # Ignore non-alpha keys (like Shift, Ctrl etc.) for sequence
        print("Ignoring non-alpha key for sequence.")
        return

    is_row_key = key_to_check in ROW_KEYS
    is_col_key = key_to_check in COL_KEYS

    # --- Input Sequence Logic ---
    if len(input_sequence) == 0:
        if is_row_key:
            input_sequence = key_to_check
            print(f"First key '{key_to_check}' accepted.")
        else:
            print(f"Invalid first key '{key_to_check}'.")
            input_sequence = "" # Reset

    elif len(input_sequence) == 1:
        if is_col_key:
            input_sequence += key_to_check
            target_label = input_sequence # Already uppercase
            print(f"Second key '{key_to_check}' accepted. Target: '{target_label}'")

            if target_label in grid_points:
                target_x, target_y = grid_points[target_label]
                print(f"Coordinates for '{target_label}': ({target_x}, {target_y})")

                print("Withdrawing window...")
                root.withdraw()
                root.after(50, lambda: move(target_x, target_y))
                input_sequence = ""
            else: # Should not happen if keys are validated
                print(f"Error: Target label '{target_label}' somehow invalid.")
                input_sequence = ""

        else: # Invalid second key
            print(f"Invalid second key '{key_to_check}'. Resetting.")
            input_sequence = ""

        root.after(50, root.destroy)
    else: # Sequence already complete, reset on new key press
         print("Sequence already complete or > 1 key. Resetting.")
         input_sequence = ""
         update_highlight(canvas) # Clear highlight
         # Treat the current valid key as the potential start of a new sequence?
         if is_row_key:
             input_sequence = key_to_check
             print(f"Starting new sequence with '{key_to_check}'.")
         else:
             print(f"Invalid key '{key_to_check}' to start new sequence.")


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


root.bind('<Key>', lambda event: on_key(event, root, canvas))
root.mainloop()



