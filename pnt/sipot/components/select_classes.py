import json
import threading
import time
import logging

import customtkinter as ctk
from watchdog.events import FileSystemEventHandler


class ProgressBar(ctk.CTkFrame):

    def __init__(self, master, json_file_path, **kwargs):
        super().__init__(master, **kwargs)

        self.json_file_path = json_file_path

        # Configure grid layout for the progress bar section
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.progress_bar = ctk.CTkProgressBar(
            self, width=300, height=30, progress_color="#3caa56"
        )
        self.progress_bar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.progress_label = ctk.CTkLabel(self, text="Progreso: 0%")
        self.progress_label.grid(row=1, column=0, pady=5)

        # Start the progress update thread
        self.update_thread = threading.Thread(target=self.update_progress)
        self.update_thread.daemon = True
        self.update_thread.start()

    def update_progress(self):
        while True:
            try:
                with open(self.json_file_path, "r") as file:
                    data = json.load(file)
                    index = data.get("index", 0)
                    final_index = data.get("final_index", 1)

                    if final_index > 0:
                        progress = index / final_index
                    else:
                        progress = 0

                    self.update_progress_bar(progress)

            except Exception as e:
                print(f"Error reading JSON file: {e}")

            time.sleep(1)  # Update every second

    def update_progress_bar(self, progress):
        self.progress_bar.set(progress)
        if int(progress * 100) == 100:
            self.progress_label.configure(
                text=f"Progreso: termiaste la descarga para este sujeto obligado{int(progress * 100)}%"
            )
        self.progress_label.configure(text=f"Progreso: {int(progress * 100)}%")


class TextBoxHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(ctk.END, msg + "\n")
        self.text_widget.see(ctk.END)


class LogFileHandler(FileSystemEventHandler):
    def __init__(self, text_widget, log_file):
        super().__init__()
        self.text_widget = text_widget
        self.log_file = log_file
        self.last_position = 0

    def on_modified(self, event):
        if event.src_path == self.log_file:
            self.update_text_widget()

    def update_text_widget(self):
        with open(self.log_file, "r") as file:
            file.seek(self.last_position)
            new_lines = file.read()
            if new_lines:
                self.text_widget.insert(ctk.END, new_lines)
                self.text_widget.see(ctk.END)
                self.last_position = file.tell()
