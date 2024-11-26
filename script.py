import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Listbox, Scrollbar, Button
import subprocess
import json

class FlacConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter")
        self.root.geometry("600x600")

        # Input Folders and Files
        self.input_folders = []
        self.selected_files = []

        # Output Folder
        self.output_folder = None

        # Create UI
        self.create_ui()

        # Variable to track if the list window is open
        self.list_window_open = False

    def create_ui(self):
        # Input Folders and Files Frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=10, pady=10, fill=tk.X)

        # Add Folders Button
        add_folder_btn = tk.Button(input_frame, text="Add Input Folders", command=self.add_input_folder)
        add_folder_btn.pack(side=tk.LEFT, padx=5)

        # Add Files Button
        add_files_btn = tk.Button(input_frame, text="Add Input Files", command=self.add_input_files)
        add_files_btn.pack(side=tk.LEFT, padx=5)

        # Remove Selected Button
        remove_sel_btn = tk.Button(input_frame, text="Remove Selected", command=self.remove_selected)
        remove_sel_btn.pack(side=tk.LEFT, padx=5)

        # Listbox to show input folders and files
        self.folder_listbox = tk.Listbox(self.root, width=80, height=10)
        self.folder_listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Button to open list window
        open_list_window_btn = tk.Button(input_frame, text="Open List Window", command=self.open_list_window)
        open_list_window_btn.pack(side=tk.LEFT, padx=5)

        # Output Folder Frame
        output_frame = tk.Frame(self.root)
        output_frame.pack(padx=10, pady=10, fill=tk.X)

        # Output Folder Label
        self.output_label = tk.Label(output_frame, text="Output Folder: Not Selected", width=40)
        self.output_label.pack(side=tk.LEFT, padx=5)

        # Select Output Folder Button
        output_btn = tk.Button(output_frame, text="Select Output Folder", command=self.select_output_folder)
        output_btn.pack(side=tk.LEFT, padx=5)

        # Convert Button
        convert_btn = tk.Button(self.root, text="Start Conversion", command=self.start_conversion)
        convert_btn.pack(pady=10)

        # Log Window
        self.log_text = tk.Text(self.root, width=80, height=10)
        self.log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def add_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder with Audio Files")
        if folder:
            if folder not in self.input_folders:
                self.input_folders.append(folder)
                self.update_listbox()
                print(f"Added folder: {folder}")
                self.update_list_window()

    def add_input_files(self):
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[("Audio files", "*.flac *.wav *.m4a")]
        )
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.update_listbox()
                    print(f"Added file: {file}")
                    self.update_list_window()

    def remove_selected(self):
        selection = self.folder_listbox.curselection()
        if selection:
            index = selection[0]
            item = self.folder_listbox.get(index)
            if item.startswith("Folder: "):
                folder = item[len("Folder: "):]
                if folder in self.input_folders:
                    self.input_folders.remove(folder)
                    print(f"Removed folder: {folder}")
            elif item.startswith("File: "):
                file = item[len("File: "):]
                if file in self.selected_files:
                    self.selected_files.remove(file)
                    print(f"Removed file: {file}")
            self.folder_listbox.delete(index)
            self.update_list_window()

    def update_listbox(self):
        self.folder_listbox.delete(0, tk.END)
        for folder in self.input_folders:
            self.folder_listbox.insert(tk.END, f"Folder: {folder}")
        for file in self.selected_files:
            self.folder_listbox.insert(tk.END, f"File: {file}")

    def open_list_window(self):
        if not self.list_window_open:
            self.list_window = Toplevel(self.root)
            self.list_window.title("Selected Folders and Files")
            self.list_window.geometry("400x300")

            # Listbox for selected items
            self.listbox = Listbox(self.list_window, width=50, height=15)
            self.listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Update the listbox with current inputs
            self.update_list_window()

            # Button to close the window
            close_btn = Button(self.list_window, text="Close", command=self.close_list_window)
            close_btn.pack(pady=5)

            self.list_window_open = True

    def update_list_window(self):
        if self.list_window_open:
            self.listbox.delete(0, tk.END)
            for folder in self.input_folders:
                self.listbox.insert(tk.END, f"Folder: {folder}")
            for file in self.selected_files:
                self.listbox.insert(tk.END, f"File: {file}")

    def close_list_window(self):
        self.list_window.destroy()
        self.list_window_open = False

    def select_output_folder(self):
        output_folder = filedialog.askdirectory(title="Select Output Folder for Converted Files")
        if output_folder:
            self.output_folder = output_folder
            folder_name = os.path.basename(output_folder)
            if len(folder_name) > 20:
                folder_name = f"{folder_name[:10]}...{folder_name[-7:]}"
            self.output_label.config(text=f"Output Folder: {folder_name}")
            print(f"Selected output folder: {output_folder}")

    def get_audio_info(self, file_path):
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet',
                 '-show_streams',
                 '-select_streams', 'a:0',
                 '-of', 'json',
                 file_path],
                capture_output=True,
                text=True
            )
            data = json.loads(result.stdout)
            if 'streams' in data and len(data['streams']) > 0:
                stream = data['streams'][0]
                codec = stream.get('codec_name', 'unknown')
                sample_rate = stream.get('sample_rate', 'unknown')
                return {'codec': codec, 'sample_rate': sample_rate}
            else:
                return {'codec': 'unknown', 'sample_rate': 'unknown'}
        except Exception as e:
            self.log_text.insert(tk.END, f"Error getting audio info for {file_path}: {e}\n")
            return {'codec': 'unknown', 'sample_rate': 'unknown'}

    def process_file(self, audio_file, output_base_path):
        info = self.get_audio_info(audio_file)
        if info['codec'] == 'alac':
            if info['sample_rate'] != '44100':
                self.resample_alac(audio_file, output_base_path)
            else:
                self.log_text.insert(tk.END, f"Skipping {audio_file}, already ALAC at 44.1 kHz\n")
        else:
            self.convert_to_alac(audio_file, output_base_path)

    def resample_alac(self, audio_file, output_base_path):
        artist = self.get_ffprobe_metadata(audio_file, 'artist') or 'Unknown_Artist'
        album = self.get_ffprobe_metadata(audio_file, 'album') or 'Unknown_Album'
        output_dir = os.path.join(output_base_path, artist, album)
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.splitext(os.path.basename(audio_file))[0] + '.m4a'
        output_file = os.path.join(output_dir, output_filename)
        if os.path.exists(output_file):
            self.log_text.insert(tk.END, f"Skipping already processed file: {output_file}\n")
            return
        try:
            subprocess.run([
                'ffmpeg',
                '-i', audio_file,
                '-c:a', 'alac',
                '-ar', '44100',
                '-sample_fmt', 's16p',
                output_file
            ], check=True)
            self.log_text.insert(tk.END, f"Resampled: {audio_file} -> {output_file}\n")
        except subprocess.CalledProcessError as e:
            self.log_text.insert(tk.END, f"Error resampling {audio_file}: {e}\n")

    def convert_to_alac(self, audio_file, output_base_path):
        artist = self.get_ffprobe_metadata(audio_file, 'artist') or 'Unknown_Artist'
        album = self.get_ffprobe_metadata(audio_file, 'album') or 'Unknown_Album'
        output_dir = os.path.join(output_base_path, artist, album)
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.splitext(os.path.basename(audio_file))[0] + '.m4a'
        output_file = os.path.join(output_dir, output_filename)
        if os.path.exists(output_file):
            self.log_text.insert(tk.END, f"Skipping already converted file: {output_file}\n")
            return
        try:
            subprocess.run([
                'ffmpeg',
                '-i', audio_file,
                '-c:a', 'alac',
                '-ar', '44100',
                '-sample_fmt', 's16p',
                output_file
            ], check=True)
            self.log_text.insert(tk.END, f"Converted: {audio_file} -> {output_file}\n")
        except subprocess.CalledProcessError as e:
            self.log_text.insert(tk.END, f"Error converting {audio_file}: {e}\n")

    def get_ffprobe_metadata(self, file_path, tag):
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet',
                 f'-show_entries', f'format_tags={tag}',
                 '-of', 'default=nw=1:nk=1',
                 file_path],
                capture_output=True,
                text=True
            )
            metadata = result.stdout.strip()
            return metadata if metadata else None
        except Exception:
            return None

    def start_conversion(self):
        if not self.input_folders and not self.selected_files:
            messagebox.showerror("Error", "Please add at least one input folder or file")
            return

        if not self.output_folder:
            messagebox.showerror("Error", "Please select an output folder")
            return

        input_paths = self.input_folders + self.selected_files
        converted_count = 0
        failed_count = 0

        for path in input_paths:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(('.flac', '.wav', '.m4a')) and not file.startswith('._'):
                            audio_file = os.path.join(root, file)
                            try:
                                self.process_file(audio_file, self.output_folder)
                                converted_count += 1
                            except Exception as e:
                                self.log_text.insert(tk.END, f"Error processing {audio_file}: {e}\n")
                                failed_count += 1
            elif os.path.isfile(path) and path.lower().endswith(('.flac', '.wav', '.m4a')) and not path.startswith('._'):
                try:
                    self.process_file(path, self.output_folder)
                    converted_count += 1
                except Exception as e:
                    self.log_text.insert(tk.END, f"Error processing {path}: {e}\n")
                    failed_count += 1

        messagebox.showinfo(
            "Conversion Complete",
            f"Conversion finished:\n"
            f"Processed files: {converted_count}\n"
            f"Failed operations: {failed_count}"
        )

def main():
    root = tk.Tk()
    app = FlacConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()