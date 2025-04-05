import keyboard

def on_hotkey():
    print("AltGr + Tab was pressed!")

# Try with AltGr
keyboard.add_hotkey('ctrl+shift+/', on_hotkey)

print("Listening for AltGr + Tab... Press ESC to quit.")
keyboard.wait('esc')
