import tkinter as tk
from ttkthemes import ThemedTk # Use ThemedTk instead of standard tk.Tk
from gui_main import TrackerApp

if __name__ == '__main__':
    # Initialize the main window using ThemedTk for UI enhancement
    root = ThemedTk()
    
    # Apply a modern theme (e.g., 'scidblue', 'arc', 'plastik')
    root.set_theme("scidblue")
    
    # Set a minimum size for a better look
    root.geometry("850x550")
    root.minsize(850, 550) 
    
    app = TrackerApp(root)
    root.mainloop()