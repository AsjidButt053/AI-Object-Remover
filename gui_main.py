

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import os

# Import your existing modules
from file_manager import FileManager
from ai_engine import AIEngine
from interactive_selector import InteractiveSelector

class CleanSweepGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CleanSweep AI - Advanced Object Remover")
        self.root.geometry("1100x750")
        self.root.configure(bg="#2c3e50") # Dark Blue-Grey Theme

        # Initialize Backend
        self.fm = FileManager()
        self.ai = AIEngine(target_label="manual") 
        self.selector = InteractiveSelector()
        
        self.current_image_path = None
        self.original_cv2 = None
        self.processed_cv2 = None
        
        self._setup_ui()

    def _setup_ui(self):
        """Builds the modern UI Layout"""
        # --- HEADER ---
        header_frame = tk.Frame(self.root, bg="#34495e", height=60)
        header_frame.pack(fill="x")
        title_label = tk.Label(header_frame, text="CleanSweep AI Project", font=("Segoe UI", 20, "bold"), bg="#34495e", fg="white")
        title_label.pack(pady=10)

        # --- LEFT PANEL (CONTROLS) ---
        control_panel = tk.Frame(self.root, bg="#ecf0f1", width=250)
        control_panel.pack(side="left", fill="y", padx=10, pady=10)

        # 1. Load Button
        btn_load = tk.Button(control_panel, text="📂 Load Image", command=self.load_image, 
                             bg="#2980b9", fg="white", font=("Arial", 12), height=2, width=20)
        btn_load.pack(pady=20)

        # 2. Mode Selection
        lbl_mode = tk.Label(control_panel, text="Select Mode:", bg="#ecf0f1", font=("Arial", 11, "bold"))
        lbl_mode.pack(pady=(10, 5))
        
        self.mode_var = tk.StringVar(value="Manual")
        modes = [("Manual Brush (Interactive)", "Manual"), ("Auto Remove (All People)", "person"), ("Auto Remove (All Cars)", "car")]
        
        for text, val in modes:
            tk.Radiobutton(control_panel, text=text, variable=self.mode_var, value=val, 
                           bg="#ecf0f1", anchor="w").pack(fill="x", padx=20)

        # 3. Process Button
        self.btn_process = tk.Button(control_panel, text="✨ Run AI Removal", command=self.start_processing_thread, 
                                bg="#27ae60", fg="white", font=("Arial", 12, "bold"), height=2, width=20, state="disabled")
        self.btn_process.pack(pady=30)

        # 4. Status Label
        self.status_label = tk.Label(control_panel, text="Ready", bg="#ecf0f1", fg="#7f8c8d", wraplength=200)
        self.status_label.pack(side="bottom", pady=20)

        # --- RIGHT PANEL (IMAGE DISPLAY) ---
        self.image_area = tk.Frame(self.root, bg="#2c3e50")
        self.image_area.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        
        self.canvas_label = tk.Label(self.image_area, text="No Image Loaded", bg="#34495e", fg="white", font=("Arial", 14))
        self.canvas_label.pack(expand=True)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png")])
        if not file_path:
            return

        self.current_image_path = file_path
        self.original_cv2 = cv2.imread(file_path)
        
        self.display_image(self.original_cv2)
        self.btn_process.config(state="normal")
        self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")

    def display_image(self, cv_img):
        """Convert CV2 image to Tkinter Format and Display"""
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img_rgb)
        
        # Resize to fit window while keeping aspect ratio
        w_box, h_box = 800, 600
        im_pil.thumbnail((w_box, h_box))
        
        img_tk = ImageTk.PhotoImage(im_pil)
        
        self.canvas_label.config(image=img_tk, text="")
        self.canvas_label.image = img_tk  # Keep reference

    def start_processing_thread(self):
        """Runs AI in a separate thread so GUI doesn't freeze"""
        self.btn_process.config(state="disabled", text="Processing...")
        self.status_label.config(text="AI is running... Please wait.")
        
        thread = threading.Thread(target=self.run_ai_logic)
        thread.start()

    def run_ai_logic(self):
        mode = self.mode_var.get()
        cleaned_image = None
        
        try:
            if mode == "Manual":
                # For manual, we must run the selector on the Main Thread or handle carefully.
                # Since selector opens a new CV2 window, it works fine from here.
                self.status_label.config(text="Draw on the popup window, then press ENTER.")
                mask = self.selector.select_object(self.current_image_path)
                
                if mask is not None:
                    self.status_label.config(text="Inpainting...")
                    cleaned_image = self.ai.remove_with_mask(self.current_image_path, mask)
                else:
                    self.status_label.config(text="Selection Cancelled.")
            
            else:
                # Auto Mode (YOLO)
                self.ai.target_label = mode
                self.status_label.config(text=f"Detecting {mode}s...")
                cleaned_image, conf = self.ai.process_image(self.current_image_path)
                
                if conf == 0:
                    messagebox.showwarning("Not Found", f"No {mode} detected in this image.")

            if cleaned_image is not None:
                self.processed_cv2 = cleaned_image
                # Save it
                filename = os.path.basename(self.current_image_path)
                save_path = self.fm.save_image(cleaned_image, filename)
                self.fm.log_operation(filename, mode, 1.0, True)
                
                # Update UI
                self.root.after(0, self.show_result)

        except Exception as e:
            print(e)
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        self.root.after(0, self.reset_buttons)

    def show_result(self):
        self.display_image(self.processed_cv2)
        self.status_label.config(text="Success! Image Saved.")
        messagebox.showinfo("Done", "Object Removed Successfully!")

    def reset_buttons(self):
        self.btn_process.config(state="normal", text="✨ Run AI Removal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CleanSweepGUI(root)
    root.mainloop()