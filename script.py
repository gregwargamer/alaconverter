import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import re
import platform


def sanitize_filename(filename):
    """
    Remove or replace invalid characters for filenames.

    Args:
        filename (str): Input filename to sanitize

    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', filename or 'Unknown')


def get_ffprobe_metadata(file_path, tag):
    """
    Extract metadata from a file using ffprobe.

    Args:
        file_path (str): Path to the audio file
        tag (str): Metadata tag to extract (e.g., 'artist', 'album')

    Returns:
        str: Extracted metadata or default value
    """
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
        return sanitize_filename(metadata) if metadata else None
    except Exception:
        return None


def convert_flac_to_alac(input_paths, output_base_path):
    """
    Convert FLAC files to ALAC with organized folder structure.

    Args:
        input_paths (list): List of paths to input FLAC files or directories
        output_base_path (str): Base output directory for converted files
    """
    # Collect all FLAC files
    flac_files = []
    for input_path in input_paths:
        if os.path.isfile(input_path) and input_path.lower().endswith('.flac'):
            flac_files.append(input_path)
        elif os.path.isdir(input_path):
            for root, _, files in os.walk(input_path):
                flac_files.extend([
                    os.path.join(root, file)
                    for file in files
                    if file.lower().endswith('.flac')
                ])

    # Conversion process
    converted_count = 0
    failed_count = 0

    for flac_file in flac_files:
        try:
            # Extract metadata
            artist = get_ffprobe_metadata(flac_file, 'artist') or 'Unknown_Artist'
            album = get_ffprobe_metadata(flac_file, 'album') or 'Unknown_Album'

            # Create output directory
            output_dir = os.path.join(output_base_path, artist, album)
            os.makedirs(output_dir, exist_ok=True)

            # Define output filename
            output_filename = os.path.splitext(os.path.basename(flac_file))[0] + '.m4a'
            output_file = os.path.join(output_dir, output_filename)

            # Skip if file already exists
            if os.path.exists(output_file):
                print(f"Skipping already converted file: {output_file}")
                continue

            # Convert using FFmpeg
            subprocess.run([
                'ffmpeg',
                '-i', flac_file,
                '-c:a', 'alac',
                '-ar', '44100',
                '-sample_fmt', 's16p',
                output_file
            ], check=True)

            converted_count += 1
            print(f"Converted: {flac_file} -> {output_file}")

        except subprocess.CalledProcessError:
            failed_count += 1
            print(f"Failed to convert: {flac_file}")

    return converted_count, failed_count


def select_input_and_convert():
    """
    Open file/folder selection dialogs and perform conversion.
    """
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Ensure window is on top (cross-platform approach)
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)

    # Select input FLAC files or directories
    input_paths = filedialog.askopenfilenames(
        title="Select FLAC Files",
        filetypes=[("FLAC files", "*.flac"), ("All directories", "*")],
        multiple=True
    )

    # If no files selected, also allow directory selection
    if not input_paths:
        input_path = filedialog.askdirectory(title="Select FLAC Folder")
        input_paths = [input_path] if input_path else []

    # Exit if no input selected
    if not input_paths:
        messagebox.showinfo("Info", "No files or folders selected.")
        return

    # Select output directory
    output_path = filedialog.askdirectory(title="Select Output Folder")
    if not output_path:
        messagebox.showinfo("Info", "No output folder selected.")
        return

    # Perform conversion
    converted_count, failed_count = convert_flac_to_alac(input_paths, output_path)

    # Show results
    messagebox.showinfo(
        "Conversion Complete",
        f"Conversion finished:\n"
        f"Converted files: {converted_count}\n"
        f"Failed conversions: {failed_count}"
    )


def main():
    # Run the conversion dialog
    select_input_and_convert()


if __name__ == "__main__":
    main()