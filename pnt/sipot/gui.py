#######################################################
############### ORG: DataCivica ##################
#######################################################
############### Author: Basem Hamza ##################
#######################################################
#######################################################

import json
import logging
import queue
from tkinter import filedialog
from PIL import Image

import customtkinter as ctk
import subprocess
import sys
import os
import threading
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

output_queue = queue.Queue()
process = None

if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

script_path = os.path.join(bundle_dir, "obligacion.py")


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


def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        read_file(file_path)


def read_file(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
            for index, row in df.iterrows():
                run_script_with_params(row)
        else:
            output_text.insert(ctk.END, "Unsupported file format\n")
            output_text.see(ctk.END)
            return
    except Exception as e:
        output_text.insert(ctk.END, f"Error reading file: {str(e)}\n")
        output_text.see(ctk.END)


def run_script_with_params(row):
    def target():
        global process
        try:
            print(f"Bundle directory: {bundle_dir}")
            save_state(
                row.idSujetoObligado,
                row.idEntidadFederativa,
                row.idObligacion,
                row.ano,
                row.finalIndex,
                row.colaboradora,
            )
            command = build_command(row)
            print(f"Running command: {command}")  # Debugging statement
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            for stdout_line in iter(process.stdout.readline, ""):
                output_queue.put(stdout_line)
            for stderr_line in iter(process.stderr.readline, ""):
                output_queue.put(stderr_line)
            process.stdout.close()
            process.stderr.close()
            process.wait()
        except Exception as e:
            output_queue.put(str(e))
        finally:
            app.after(0, enable_button)

    def enable_button():
        run_button.configure(state=ctk.NORMAL)
        resume_button.configure(state=ctk.NORMAL)

    run_button.configure(state=ctk.DISABLED)
    resume_button.configure(state=ctk.DISABLED)
    thread = threading.Thread(target=target)
    thread.start()
    app.after(100, process_queue)


def build_command(row):
    if sys.platform == "win32":
        return [
            "python",
            script_path,
            "--idSujetoObligado",
            row.idSujetoObligado,
            "--idEntidadFederativa",
            row.idEntidadFederativa,
            "--idObligacion",
            row.idObligacion,
            "--ano",
            row.ano,
            "--startIndex",
            row.startIndex,
            "--finalIndex",
            row.finalIndex,
            "--colaboradora",
            row.colaboradora,
        ]
    else:
        return [
            "python3",
            script_path,
            "--idSujetoObligado",
            row.idSujetoObligado,
            "--idEntidadFederativa",
            row.idEntidadFederativa,
            "--idObligacion",
            row.idObligacion,
            "--ano",
            row.ano,
            "--startIndex",
            row.startIndex,
            "--finalIndex",
            row.finalIndex,
            "--colaboradora",
            row.colaboradora,
        ]


def run_script():
    def target():
        global process
        try:
            print(f"Bundle directory: {bundle_dir}")
            print(f"Contents of bundle directory: {os.listdir(bundle_dir)}")
            save_state(
                sujeto.get(),
                entidad.get(),
                obligacion.get(),
                ano.get(),
                finalIndex.get(),
                colaboradora.get(),
            )
            command = build_command_from_entries()
            print(f"Running command: {command}")  # Debugging statement
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            for stdout_line in iter(process.stdout.readline, ""):
                output_queue.put(stdout_line)
            for stderr_line in iter(process.stderr.readline, ""):
                output_queue.put(stderr_line)
            process.stdout.close()
            process.stderr.close()
            process.wait()
        except Exception as e:
            output_queue.put(str(e))
        finally:
            app.after(0, enable_button)

    def enable_button():
        run_button.configure(state=ctk.NORMAL)
        resume_button.configure(state=ctk.NORMAL)

    run_button.configure(state=ctk.DISABLED)
    resume_button.configure(state=ctk.DISABLED)
    thread = threading.Thread(target=target)
    thread.start()
    app.after(100, process_queue)


def build_command_from_entries():
    if sys.platform == "win32":
        return [
            "python",
            script_path,
            "--idSujetoObligado",
            sujeto.get(),
            "--idEntidadFederativa",
            entidad.get(),
            "--idObligacion",
            obligacion.get(),
            "--ano",
            ano.get(),
            "--startIndex",
            startIndex.get(),
            "--finalIndex",
            finalIndex.get(),
            "--colaboradora",
            colaboradora.get(),
        ]
    else:
        return [
            "python3",
            script_path,
            "--idSujetoObligado",
            sujeto.get(),
            "--idEntidadFederativa",
            entidad.get(),
            "--idObligacion",
            obligacion.get(),
            "--ano",
            ano.get(),
            "--startIndex",
            startIndex.get(),
            "--finalIndex",
            finalIndex.get(),
            "--colaboradora",
            colaboradora.get(),
        ]


def load_state() -> int:
    global process

    def enable_button():
        run_button.configure(state=ctk.NORMAL)
        resume_button.configure(state=ctk.NORMAL)

    run_button.configure(state=ctk.DISABLED)
    resume_button.configure(state=ctk.DISABLED)
    try:
        with open(f"{sujeto.get()}_session.json", "r") as f:
            state = json.load(f)
            command = build_command_from_state(state)
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            print(f"Running command: {command}")
            for stdout_line in iter(process.stdout.readline, ""):
                output_queue.put(stdout_line)
            for stderr_line in iter(process.stderr.readline, ""):
                output_queue.put(stderr_line)
            process.stdout.close()
            process.stderr.close()
            process.wait()
    except Exception as e:
        output_queue.put(str(e))
    except FileNotFoundError:
        return 0
    finally:
        app.after(0, enable_button)


def build_command_from_state(state):
    if sys.platform == "win32":
        return [
            "python",
            script_path,
            "--idSujetoObligado",
            state["sujeto"],
            "--idEntidadFederativa",
            state["entidad"],
            "--idObligacion",
            state["obligacion"],
            "--ano",
            state["ano"],
            "--finalIndex",
            state["finalIndex"],
            "--colaboradora",
            state["colaboradora"],
        ]
    else:
        return [
            "python3",
            script_path,
            "--idSujetoObligado",
            state["sujeto"],
            "--idEntidadFederativa",
            state["entidad"],
            "--idObligacion",
            state["obligacion"],
            "--ano",
            state["ano"],
            "--finalIndex",
            state["finalIndex"],
            "--colaboradora",
            state["colaboradora"],
        ]


def on_button_click():
    thread = threading.Thread(target=run_script)
    thread.start()
    app.after(100, process_queue)


def on_session():
    thread = threading.Thread(target=load_state)
    thread.start()
    app.after(100, process_queue)


def on_closing():
    global process
    if process:
        process.terminate()
        process.wait()
    observer.stop()
    observer.join()
    app.destroy()


def on_closing_button():
    global process
    if process:
        process.terminate()
        process.wait()


def on_iniciar_nuevo_button():
    global process
    subprocess.Popen(
        ["rm", f"{sujeto.get()}state.json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def save_state(sujeto, entidad, Obligacion, ano, finalIndex, colaboradora) -> int:
    state = {
        "sujeto": sujeto,
        "entidad": entidad,
        "obligacion": Obligacion,
        "ano": ano,
        "finalIndex": finalIndex,
        "colaboradora": colaboradora,
    }
    with open(f"{sujeto}_session.json", "w") as f:
        json.dump(state, f)


def process_queue():
    try:
        while True:
            output = output_queue.get_nowait()
            output_text.insert(ctk.END, output)
            output_text.see(ctk.END)
    except queue.Empty:
        pass
    finally:
        app.after(100, process_queue)


app = ctk.CTk()
app.title("Respaldo de Obligaciones PNT")


def center_window(app, width, height):
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    app.geometry(f"{width}x{height}+{x}+{y}")


center_window(app, 700, 900)

logo_path = os.path.join(bundle_dir, "logo.png")
image = ctk.CTkImage(Image.open(logo_path), size=(50, 50))
image_label = ctk.CTkLabel(app, image=image, text="")
image_label.grid(row=0, column=0, columnspan=3, pady=10)

label = ctk.CTkLabel(app, text="Colaboradora", anchor="w")
label.grid(row=1, column=0, pady=10, padx=50, sticky="nsew")
colaboradora = ctk.CTkEntry(
    app, width=300, border_color="#a256a5", placeholder_text="Jorge Alberto"
)
colaboradora.grid(row=1, column=1, pady=10, padx=50, sticky="nsew")

label = ctk.CTkLabel(app, text="Identificador Sujeto Obligado", anchor="w")
label.grid(row=2, column=0, pady=10, padx=50, sticky="nsew")
sujeto = ctk.CTkEntry(
    app, width=300, border_color="#a256a5", placeholder_text="Ej0QcqjZqYSP04SKbKxVCw=="
)
sujeto.grid(row=2, column=1, columnspan=2, pady=3, padx=50, sticky="nsew")

label = ctk.CTkLabel(app, text="Identificador de entidad federal", anchor="w")
label.grid(row=3, column=0, pady=10, padx=50, sticky="nsew")
entidad = ctk.CTkEntry(
    app, width=300, border_color="#a256a5", placeholder_text="LBP8NmL5Gofq6T_pb6W9nw=="
)
entidad.grid(row=3, column=1, columnspan=2, pady=3, padx=50, sticky="nsew")

label = ctk.CTkLabel(app, text="Identificador de obligacion", anchor="w")
label.grid(row=4, column=0, pady=10, padx=50, sticky="nsew")
obligacion = ctk.CTkEntry(
    app, width=300, border_color="#a256a5", placeholder_text="LBP8NmL5Gofq6T_pb6W9nw=="
)
obligacion.grid(row=4, column=1, columnspan=2, pady=3, padx=50, sticky="nsew")

label = ctk.CTkLabel(app, text="Año", anchor="w")
label.grid(row=5, column=0, pady=10, padx=50, sticky="nsew")
ano = ctk.CTkEntry(app, width=300, border_color="#a256a5", placeholder_text="2024")
ano.grid(row=5, column=1, columnspan=2, pady=3, padx=50, sticky="nsew")

label = ctk.CTkLabel(app, text="Index de empezar", anchor="w")
label.grid(row=6, column=0, pady=10, columnspan=1, padx=50, sticky="nsew")
startIndex = ctk.CTkEntry(app, width=300, border_color="#a256a5", placeholder_text="0")
startIndex.grid(row=6, column=1, columnspan=2, padx=50, pady=3, sticky="nsew")

label = ctk.CTkLabel(app, text="Index de terminar", anchor="w")
label.grid(row=7, column=0, pady=10, columnspan=1, padx=50, sticky="nsew")
finalIndex = ctk.CTkEntry(app, width=300, border_color="#a256a5", placeholder_text="0")
finalIndex.grid(row=7, column=1, columnspan=2, padx=50, pady=3, sticky="nsew")

nuevo_registro_button = ctk.CTkButton(
    app,
    text="Iniciar nuevo respaldo",
    command=on_iniciar_nuevo_button,
    fg_color=("#ffffff", "#3caa56"),
    hover_color="#a256a5",
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
nuevo_registro_button.grid(row=8, column=0, padx=50, pady=20, sticky="nsew")

run_button = ctk.CTkButton(
    app,
    text="Ejecutar Script :D",
    command=run_script,
    fg_color=("#ffffff", "#a256a5"),
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
run_button.grid(row=8, column=1, padx=50, pady=20, sticky="nsew")

stop_button = ctk.CTkButton(
    app,
    text="Stop",
    command=on_closing_button,
    fg_color=("#ffffff", "#a256a5"),
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
stop_button.grid(row=9, column=0, padx=50, pady=20, sticky="nsew")

resume_button = ctk.CTkButton(
    app,
    text="Resume",
    command=on_session,
    fg_color=("#ffffff", "#a256a5"),
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
resume_button.grid(row=9, column=1, padx=50, pady=20, sticky="nsew")

upload_button = ctk.CTkButton(app, text="Ejecutar CSV", command=upload_file)
upload_button.grid(row=10, column=0, columnspan=2, pady=20, sticky="nsew")

output_text = ctk.CTkTextbox(app, width=500, height=200)
output_text.grid(row=11, column=0, columnspan=2, padx=50, pady=15, sticky="nsew")

app.protocol("WM_DELETE_WINDOW", on_closing)

text_handler = TextBoxHandler(output_text)
logging.getLogger().addHandler(text_handler)

log_file = "download_files_PNT.log"
event_handler = LogFileHandler(output_text, log_file)
observer = Observer()
observer.schedule(event_handler, path=".", recursive=False)
observer.start()


def update_gui():
    app.update_idletasks()
    app.after(100, update_gui)


app.after(100, update_gui)
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.mainloop()

observer.stop()
observer.join()
