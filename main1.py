import cv2
import os
from tkinter import Tk, Button, filedialog, messagebox

class VideoFrameExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Frame Extractor")

        # Output directory
        self.output_dir = 'C:\\Users\\Admin\\Desktop\\NumberPlate'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Create Select Video Button
        self.select_video_button = Button(root, text="Select Video", command=self.select_video)
        self.select_video_button.pack(pady=20)

    def select_video(self):
        """Let the user select a video file and start frame extraction."""
        video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])

        if video_path:
            self.process_video(video_path)
        else:
            messagebox.showwarning("No Video Selected", "Please select a video file to proceed.")

    def process_video(self, video_path):
        """Process the selected video and extract frames."""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            messagebox.showerror("Error", "Couldn't open the video.")
            return

        frame_count = 10  # Initial frame count

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame_count += 1

            # Save every 30th frame
            if frame_count % 30 == 0:
                image_filename = os.path.join(self.output_dir, f"frame_{frame_count}.jpg")
                cv2.imwrite(image_filename, frame)
                print(f"Captured image: {image_filename}")

            # Display video frame (optional)
            cv2.imshow('Video Frame', frame)

            # Exit when the user presses 'Esc'
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

        messagebox.showinfo("Success", "Video processing complete. Frames saved to the output directory.")

# Set up Tkinter
if __name__ == "__main__":
    root = Tk()
    app = VideoFrameExtractor(root)
    root.mainloop()
