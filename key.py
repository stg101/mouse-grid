import tkinter as tk
import time
import pyautogui # For clicking, moving, and screen size

# --- Configuration ---
# Main Grid Keys (Example: 23 rows, 23 columns)
ROW_KEYS = "QWERTASDFGZXCVBYUIOPHJK"
COL_KEYS = "YUIOPHJKLNMQWERTASDFGZX"

# Sub-Grid Selection Keys (24 unique letters for a 6 rows x 4 columns grid)
# Using alphabetical order for simplicity. Ensure no numbers are used.
SUB_GRID_SELECT_KEYS = "ABCDEFGHIJKLMNOPQRSTUVWX"
# Define the sub-grid dimensions explicitly (<<< CHANGED HERE >>>)
SUB_GRID_ROWS = 6 # Now 6 rows
SUB_GRID_COLS = 4 # Now 4 columns
if len(SUB_GRID_SELECT_KEYS) != SUB_GRID_ROWS * SUB_GRID_COLS:
    print(f"Warning: SUB_GRID_SELECT_KEYS length ({len(SUB_GRID_SELECT_KEYS)}) "
          f"doesn't match SUB_GRID_ROWS*COLS ({SUB_GRID_ROWS*SUB_GRID_COLS}). Adjust keys or dimensions.")
    # You might want to raise an error or adjust dimensions/keys here

# Appearance
GRID_ALPHA = 0.5
GRID_BG = 'black'
LABEL_COLOR = "white"
LABEL_FONT = ("Arial", 10, "bold")
SUB_LABEL_COLOR = "yellow"
SUB_LABEL_FONT = ("Arial", 9, "bold")
HIGHLIGHT_COLOR = "red"
HIGHLIGHT_RADIUS = 10

# --- Global State ---
input_sequence = "" # Still needed for the main grid selection
grid_points = {} # Stores { "MAIN_LABEL": (cx, cy, x_min, y_min, x_max, y_max) }
sub_grid_points = {} # Stores { "SUB_SELECT_KEY": (x, y) }
selected_main_cell_bounds = None # Stores (x_min, y_min, x_max, y_max) of the chosen main cell

# Selection Mode Constants
MODE_MAIN_GRID = "main"
MODE_SUB_GRID = "sub"
selection_mode = MODE_MAIN_GRID # Start in main grid selection mode

########################################

def float_range(start, stop=None, step=1.0):
    # Helper for floating point ranges (used for drawing grid lines)
    if stop is None:
        stop = start
        start = 0.0
    current = start
    while (step > 0 and current < stop) or (step < 0 and current > stop):
        yield round(current, 10)
        current += step

def calculate_and_draw_main_grid(canvas, screen_width, screen_height):
    """Calculates main grid points/bounds, stores them, and draws labels/lines."""
    global grid_points

    print("Calculating and drawing MAIN grid...")
    grid_points = {}
    num_rows = len(ROW_KEYS)
    num_cols = len(COL_KEYS)
    line_color = "white"
    line_width = 1

    x_spacing = screen_width / num_cols
    y_spacing = screen_height / num_rows
    half_x_spacing = x_spacing / 2
    half_y_spacing = y_spacing / 2

    canvas.delete("all")

    for x in float_range(0, screen_width + 1, x_spacing):
        canvas.create_line(int(x), 0, int(x), screen_height, fill=line_color, width=line_width, tags="gridline")
    for y in float_range(0, screen_height + 1, y_spacing):
        canvas.create_line(0, int(y), screen_width, int(y), fill=line_color, width=line_width, tags="gridline")

    for r_idx, r_key in enumerate(ROW_KEYS):
        for c_idx, c_key in enumerate(COL_KEYS):
            label = r_key.upper() + c_key.upper()
            cx = x_spacing * (c_idx + 0.5)
            cy = y_spacing * (r_idx + 0.5)
            x_min = cx - half_x_spacing
            y_min = cy - half_y_spacing
            x_max = cx + half_x_spacing
            y_max = cy + half_y_spacing
            grid_points[label] = (int(cx), int(cy), int(x_min), int(y_min), int(x_max), int(y_max))
            canvas.create_text(int(cx), int(cy), text=label, fill=LABEL_COLOR, font=LABEL_FONT, tags="labels")

    print(f"Calculated and drew {len(grid_points)} main grid labels and lines.")

def draw_sub_grid(canvas, x_min, y_min, x_max, y_max):
    """Clears main grid visuals and draws the sub-grid with single-letter labels."""
    global sub_grid_points

    print(f"Drawing SUB grid ({SUB_GRID_ROWS} rows x {SUB_GRID_COLS} cols) within bounds: ({x_min},{y_min}) to ({x_max},{y_max})")
    sub_grid_points = {} # Clear previous sub-grid points

    # Clear main grid elements
    canvas.delete("labels")
    canvas.delete("gridline")

    sub_width = x_max - x_min
    sub_height = y_max - y_min

    # Calculate spacing within the sub-grid area based on defined dimensions
    # These calculations now use the swapped SUB_GRID_COLS and SUB_GRID_ROWS
    sub_x_spacing = sub_width / SUB_GRID_COLS
    sub_y_spacing = sub_height / SUB_GRID_ROWS

    select_key_index = 0 # Index into SUB_GRID_SELECT_KEYS

    # Calculate positions and draw labels using the defined grid structure
    # The loops now reflect 6 rows and 4 columns
    for r_idx in range(SUB_GRID_ROWS): # Outer loop iterates 6 times (rows)
        for c_idx in range(SUB_GRID_COLS): # Inner loop iterates 4 times (columns)
            if select_key_index < len(SUB_GRID_SELECT_KEYS):
                sub_label = SUB_GRID_SELECT_KEYS[select_key_index] # Get the single letter

                # Calculate center point *relative* to the sub-grid top-left
                sub_cx = x_min + sub_x_spacing * (c_idx + 0.5)
                sub_cy = y_min + sub_y_spacing * (r_idx + 0.5)

                sub_grid_points[sub_label] = (int(sub_cx), int(sub_cy))

                # Draw the single-letter sub-label text
                canvas.create_text(int(sub_cx), int(sub_cy), text=sub_label, fill=SUB_LABEL_COLOR, font=SUB_LABEL_FONT, tags="sub_labels")

                select_key_index += 1
            else:
                # Stop if we have more grid positions than keys defined
                print("Warning: Ran out of sub-grid keys before filling all positions.")
                break
        if select_key_index >= len(SUB_GRID_SELECT_KEYS):
            break


    # Optionally draw sub-grid lines
    line_color = "grey"
    # Draw vertical lines (separating columns)
    for i in range(1, SUB_GRID_COLS): # Loops 3 times for 4 columns
        x = x_min + i * sub_x_spacing
        canvas.create_line(int(x), y_min, int(x), y_max, fill=line_color, width=1, tags="sub_gridline")
    # Draw horizontal lines (separating rows)
    for i in range(1, SUB_GRID_ROWS): # Loops 5 times for 6 rows
        y = y_min + i * sub_y_spacing
        canvas.create_line(x_min, int(y), x_max, int(y), fill=line_color, width=1, tags="sub_gridline")


    print(f"Drew {len(sub_grid_points)} sub grid labels using keys: {SUB_GRID_SELECT_KEYS[:len(sub_grid_points)]}")


def move_mouse(target_x, target_y):
    """Moves the mouse to the target coordinates."""
    try:
        print(f"*** Executing pyautogui.moveTo({target_x}, {target_y}) ***")
        pyautogui.moveTo(target_x, target_y)
        print("*** Move executed. ***")
    except Exception as e:
        print(f"!!! Error during pyautogui.moveTo: {e} !!!")

def on_key(event, root, canvas):
    """Handles key presses for main grid or sub-grid selection."""
    global input_sequence, grid_points, sub_grid_points, selection_mode, selected_main_cell_bounds

    key_sym = event.keysym
    key_char = event.char.upper() # Use char for letters, convert to upper

    print(f"--- KeyPress: keysym='{key_sym}', char='{key_char}', Mode='{selection_mode}', Seq='{input_sequence}' ---")

    if key_sym == 'Escape':
        print("Escape pressed. Destroying window.")
        root.destroy()
        return

    # Use the uppercase character for checking, if it's an alphabet character
    key_to_check = key_char if key_char and key_char.isalpha() else ""

    if not key_to_check:
        print("Ignoring non-alpha/non-relevant key.")
        return

    # --- Main Grid Selection Logic (Requires 2 keys) ---
    if selection_mode == MODE_MAIN_GRID:
        is_row_key = key_to_check in ROW_KEYS
        is_col_key = key_to_check in COL_KEYS

        if len(input_sequence) == 0:
            if is_row_key:
                input_sequence = key_to_check
                print(f"Main Grid: First key '{key_to_check}' accepted.")
            else:
                print(f"Main Grid: Invalid first key '{key_to_check}'. Needs row key from [{ROW_KEYS}].")
                input_sequence = ""

        elif len(input_sequence) == 1:
            if is_col_key:
                input_sequence += key_to_check
                target_label = input_sequence
                print(f"Main Grid: Second key '{key_to_check}' accepted. Target Cell: '{target_label}'")

                if target_label in grid_points:
                    cx, cy, x_min, y_min, x_max, y_max = grid_points[target_label]
                    selected_main_cell_bounds = (x_min, y_min, x_max, y_max)
                    print(f"Main Cell '{target_label}' bounds: ({x_min},{y_min}) to ({x_max},{y_max})")

                    draw_sub_grid(canvas, x_min, y_min, x_max, y_max)
                    selection_mode = MODE_SUB_GRID
                    input_sequence = "" # Reset sequence for next operation (which is now sub-grid)
                    print(f"--> Switched to SUB_GRID selection mode. Press a key from [{SUB_GRID_SELECT_KEYS}]")

                else:
                    print(f"Error: Main Grid Target label '{target_label}' not found.")
                    input_sequence = ""
                    selection_mode = MODE_MAIN_GRID

            else: # Invalid second key for main grid
                print(f"Main Grid: Invalid second key '{key_to_check}'. Needs col key from [{COL_KEYS}]. Resetting.")
                input_sequence = ""
        # No 'else' needed here as sequence length is handled

    # --- Sub-Grid Selection Logic (Requires 1 key) ---
    elif selection_mode == MODE_SUB_GRID:
        # Check if the single pressed key is one of the valid sub-grid selection keys
        if key_to_check in SUB_GRID_SELECT_KEYS:
            target_sub_label = key_to_check # The key itself is the label
            print(f"Sub Grid: Key '{target_sub_label}' accepted.")

            if target_sub_label in sub_grid_points:
                target_x, target_y = sub_grid_points[target_sub_label]
                print(f"Final Coordinates for '{target_sub_label}': ({target_x}, {target_y})")

                print("Withdrawing window...")
                root.withdraw()

                # Schedule mouse move and window destruction
                root.after(50, lambda: move_mouse(target_x, target_y))
                root.after(150, root.destroy)

                # Reset state (though window will close)
                input_sequence = ""
                selection_mode = MODE_MAIN_GRID

            else:
                # This case should ideally not happen if draw_sub_grid worked correctly
                print(f"Error: Sub Grid Key '{target_sub_label}' pressed but not found in sub_grid_points.")
                # Stay in sub-grid mode, wait for another valid key
        else:
            print(f"Sub Grid: Invalid key '{key_to_check}'. Waiting for a key from [{SUB_GRID_SELECT_KEYS}]")
            # Stay in sub-grid mode and wait

# --- Main Execution ---
root = tk.Tk()
root.attributes('-fullscreen', True)
root.wait_visibility(root)
root.wm_attributes("-alpha", GRID_ALPHA)
root.attributes("-topmost", True)

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

calculate_and_draw_main_grid(canvas, screen_width, screen_height)

root.bind('<Key>', lambda event: on_key(event, root, canvas))

print("\n--- Ready for Input ---")
print(f"Mode: {selection_mode}")
print(f"Main Row Keys: {ROW_KEYS}")
print(f"Main Col Keys: {COL_KEYS}")
print(f"Sub-Grid Select Keys ({SUB_GRID_ROWS} rows x {SUB_GRID_COLS} cols): {SUB_GRID_SELECT_KEYS}") # Updated print statement

root.mainloop()
