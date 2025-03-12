import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import cv2
import numpy as np
import os
from pathlib import Path
import threading
import subprocess

class WebpToMP4Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("WebP to MP4 Converter with Frame Blending")
        self.root.geometry("800x600")
        
        self.files = []
        self.paused = False
        self.stopped = False
        self.conversion_thread = None
        
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(self.btn_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Select Output Folder", command=self.select_output_folder).pack(side=tk.LEFT, padx=5)
        self.convert_btn = ttk.Button(self.btn_frame, text="Convert", command=self.start_conversion)
        self.convert_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn = ttk.Button(self.btn_frame, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(self.btn_frame, text="Stop", command=self.stop_conversion, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.files_frame = ttk.Frame(self.main_frame)
        self.files_frame.grid(row=1, column=0, sticky="nsew")
        
        self.listbox = tk.Listbox(self.files_frame, selectmode=tk.EXTENDED)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.files_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready")
        self.status_label.pack()
        
        self.output_folder = None
        
        self.debug_frame = ttk.LabelFrame(self.main_frame, text="Debug Log", padding="5")
        self.debug_frame.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        
        self.debug_text = tk.Text(self.debug_frame, height=6, width=50)
        self.debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        debug_scrollbar = ttk.Scrollbar(self.debug_frame, orient=tk.VERTICAL, command=self.debug_text.yview)
        debug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.debug_text.configure(yscrollcommand=debug_scrollbar.set)
        
        self.main_frame.rowconfigure(1, weight=3)
        self.main_frame.rowconfigure(3, weight=1)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("WebP files", "*.webp")], title="Select WebP Files")
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.listbox.insert(tk.END, os.path.basename(file))

    def remove_selected(self):
        selected = self.listbox.curselection()
        for index in reversed(selected):
            self.listbox.delete(index)
            self.files.pop(index)

    def clear_all(self):
        self.listbox.delete(0, tk.END)
        self.files.clear()

    def select_output_folder(self):
        self.output_folder = filedialog.askdirectory(title="Select Output Folder")
        if self.output_folder:
            self.status_label.config(text=f"Output folder: {self.output_folder}")

    def webp_to_mp4(self, input_path, output_path, fps=16, interpolation_factor=4):
        try:
            # Load WebP animation
            webp = Image.open(input_path)
            if not webp.is_animated:
                raise ValueError("Input is not an animated WebP file")
            
            width, height = webp.size
            frames = []
            for frame_idx in range(webp.n_frames):
                webp.seek(frame_idx)
                frame = cv2.cvtColor(np.array(webp), cv2.COLOR_RGB2BGR)
                frames.append(frame)

            # Write temporary AVI with interpolated frames
            temp_output = "temp_output.avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(temp_output, fourcc, fps * interpolation_factor, (width, height))
            if not out.isOpened():
                raise RuntimeError("Failed to initialize VideoWriter")

            try:
                prev_frame = frames[0]
                out.write(prev_frame)
                for next_frame in frames[1:]:
                    # Interpolate between frames
                    for i in range(1, interpolation_factor):
                        alpha = i / interpolation_factor
                        interpolated_frame = cv2.addWeighted(prev_frame, 1 - alpha, next_frame, alpha, 0)
                        out.write(interpolated_frame)
                    out.write(next_frame)
                    prev_frame = next_frame
            finally:
                out.release()

            # Convert to MP4 with FFmpeg using hardcoded path
            ffmpeg_path = r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"  # Adjust if your path differs
            subprocess.run([
                ffmpeg_path, '-i', temp_output,
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k', '-y',
                output_path
            ], check=True, capture_output=True, text=True)

            # Clean up
            if os.path.exists(temp_output):
                os.remove(temp_output)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error converting {os.path.basename(input_path)}: {str(e)}")
            return False

    def log_debug(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.debug_text.see(tk.END)
        self.root.update_idletasks()

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.configure(text="Resume" if self.paused else "Pause")
        self.log_debug("Conversion paused" if self.paused else "Conversion resumed")

    def stop_conversion(self):
        self.stopped = True
        self.log_debug("Stopping conversion...")

    def start_conversion(self):
        if not self.files:
            messagebox.showwarning("Warning", "No files selected!")
            return
        if not self.output_folder:
            messagebox.showwarning("Warning", "No output folder selected!")
            return
        
        self.stopped = False
        self.paused = False
        
        self.convert_btn.configure(state=tk.DISABLED)
        self.pause_btn.configure(state=tk.NORMAL, text="Pause")
        self.stop_btn.configure(state=tk.NORMAL)
        
        self.conversion_thread = threading.Thread(target=self.convert_files, daemon=True)
        self.conversion_thread.start()

    def convert_files(self):
        total_files = len(self.files)
        successful = 0
        
        try:
            for i, input_file in enumerate(self.files):
                if self.stopped:
                    self.log_debug("Conversion stopped by user")
                    break
                while self.paused:
                    if self.stopped:
                        break
                    self.root.update_idletasks()
                    continue
                
                progress = (i / total_files) * 100
                self.progress_var.set(progress)
                current_file = os.path.basename(input_file)
                self.status_label.config(text=f"Converting: {current_file}")
                self.log_debug(f"Starting conversion of {current_file}")
                
                output_file = os.path.join(self.output_folder, Path(input_file).stem + ".mp4")
                
                if self.webp_to_mp4(input_file, output_file):
                    successful += 1
                    self.log_debug(f"Successfully converted {current_file}")
                else:
                    self.log_debug(f"Failed to convert {current_file}")
        
        finally:
            self.convert_btn.configure(state=tk.NORMAL)
            self.pause_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.DISABLED)
            self.progress_var.set(100)
            status = "Stopped" if self.stopped else "Completed"
            self.status_label.config(text=f"{status}! Successfully converted {successful}/{total_files} files.")
            self.log_debug(f"Conversion {status.lower()}. {successful}/{total_files} files converted.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WebpToMP4Converter(root)
    root.mainloop()