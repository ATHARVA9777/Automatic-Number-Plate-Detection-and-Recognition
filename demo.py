import os
import subprocess
from tkinter import Tk, Button, Label, messagebox, filedialog, ttk
import threading
import cv2
from karanpatil import detect_text_from_images


class ScriptRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Plate Detection")
        self.root.geometry("1000x600")

        # Create a canvas to apply a custom background
        self.canvas = tk.Canvas(self.root, bg="#c7e8e4", height=600, width=1000)
        self.canvas.pack(fill="both", expand=True)

        # Create a frame to hold two sections: left and right
        self.main_frame = ttk.Frame(self.canvas, padding=10)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Left frame (for buttons and treeview)
        self.left_frame = ttk.Frame(self.main_frame, width=500, height=600, padding=10)
        self.left_frame.grid(row=0, column=0, padx=10)

        # Right frame (for displaying traffic rules and detected texts)
        self.right_frame = ttk.Frame(self.main_frame, width=500, height=600, padding=10, relief="sunken")
        self.right_frame.grid(row=0, column=1, padx=10)

        # Header section
        self.header_frame = Label(self.left_frame, text="Number Plate Detection System", font=("Arial", 18, "bold"),
                                  bg="#4CAF50", fg="white", pady=20)
        self.header_frame.pack(fill="both", padx=10)

        # Buttons for each script with improved styling
        self.run_main_button = Button(self.left_frame, text="SELECT THE VIDEO ", command=self.run_main_script, width=25,
                                      bg="#4CAF50", fg="white", font=("Arial", 12), relief="flat")
        self.run_main_button.pack(pady=10)
        self.run_main_button.bind("<Enter>", self.on_hover_in_button)
        self.run_main_button.bind("<Leave>", self.on_hover_out_button)

        self.run_image_cleanup_button = Button(self.left_frame, text="DELETE IMG FROM FOLDER ",
                                               command=self.run_image_cleanup_script, width=25, bg="#FF5722",
                                               fg="white", font=("Arial", 12), relief="flat")
        self.run_image_cleanup_button.pack(pady=10)
        self.run_image_cleanup_button.bind("<Enter>", self.on_hover_in_button)
        self.run_image_cleanup_button.bind("<Leave>", self.on_hover_out_button)

        self.run_ocr_button = Button(self.left_frame, text="DETECT NUMBERPLATE ", command=self.run_ocr_script, width=25,
                                     bg="#2196F3", fg="white", font=("Arial", 12), relief="flat")
        self.run_ocr_button.pack(pady=10)
        self.run_ocr_button.bind("<Enter>", self.on_hover_in_button)
        self.run_ocr_button.bind("<Leave>", self.on_hover_out_button)

        self.show_text_button = Button(self.left_frame, text="Show Detected Texts", command=self.show_detected_texts,
                                       width=25, bg="#9C27B0", fg="white", font=("Arial", 12), relief="flat")
        self.show_text_button.pack(pady=10)
        self.show_text_button.bind("<Enter>", self.on_hover_in_button)
        self.show_text_button.bind("<Leave>", self.on_hover_out_button)

        # Treeview to display detected texts in a table format
        self.tree = ttk.Treeview(self.left_frame, columns=("Image", "Detected Text"), show="headings", height=10)
        self.tree.heading("Image", text="Image")
        self.tree.heading("Detected Text", text="Detected Text")
        self.tree.pack(pady=20)

        # Footer section for traffic rules (in the right section)
        self.traffic_rules_label = Label(self.right_frame, text=self.get_traffic_rules(), font=("Arial", 12),
                                         bg="#f0f0f0", fg="black", justify="left", anchor="w", padx=10)
        self.traffic_rules_label.pack(pady=20)

        # Placeholder for detected texts
        self.detected_texts = []

    def get_traffic_rules(self):
        """Return the formatted string of traffic rules."""
        rules = """
        RULES:-
        
1. Speed Limits:
  - Urban areas: 50 km/h
  - Rural areas: 60-80 km/h
  - Highways: 80-100 km/h
  
2. Seat Belts:
  - Mandatory for front seat passengers
  
3. Helmet Use:
  - Mandatory for two-wheeler riders and pillion passengers.
  
4. No Drunk Driving:
  - BAC limit: 0.03%

5. Obey Traffic Signals:
  - Stop at red lights
  - Proceed at green lights
  
6. Use of Indicators:
  - Always use indicators when turning or changing lanes
  
7. No Mobile Phones While Driving:
  - Prohibited without hands-free devices

8. Pedestrian Rules:
  - Give priority to pedestrians at zebra crossings
  - Use designated walking areas
        """
        return rules

    def run_main_script(self):
        """Run the main1.py script to extract frames from the video."""
        try:
            subprocess.run(["python", "main1.py"], check=True)
            messagebox.showinfo("Success", "main1.py executed successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error while running main1.py:\n{e}")

    def run_image_cleanup_script(self):
        """Run the imgdeletetyolo.py script to delete unused images."""
        try:
            subprocess.run(["python", "imgdeletetyolo.py"], check=True)
            messagebox.showinfo("Success", "imgdeletetyolo.py executed successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error while running imgdeletetyolo.py:\n{e}")

    def run_ocr_script(self):
        """Run the karanpatil.py script to detect and get number plates."""
        try:
            folder_path = "C:\\Users\\Admin\\Desktop\\NumberPlate"  # Update path as needed
            # Start the detection process in a separate thread
            threading.Thread(target=self.detect_and_display, args=(folder_path,)).start()
        except Exception as e:
            messagebox.showerror("Error", f"Error while running karanpatil.py:\n{e}")

    def detect_and_display(self, folder_path):
        """Detect text and display both images and text in the table."""
        self.detected_texts = detect_text_from_images(folder_path)

        # Update the table with detected texts
        self.show_detected_texts()

    def show_detected_texts(self):
        """Display the detected texts in a table format."""
        # Clear previous results in the table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Add detected texts to the table
        for image, text in self.detected_texts:
            self.tree.insert("", "end", values=(image, text))

    def on_hover_in_button(self, event):
        event.widget.config(bg="#FFC107")

    def on_hover_out_button(self, event):
        event.widget.config(
            bg="#4CAF50" if event.widget == self.run_main_button else "#FF5722" if event.widget == self.run_image_cleanup_button else "#2196F3" if event.widget == self.run_ocr_button else "#9C27B0")


# Initialize Tkinter App
if __name__ == "__main__":
    import tkinter as tk  # Ensure tkinter is imported here

    root = Tk()
    app = ScriptRunnerApp(root)
    root.mainloop()
