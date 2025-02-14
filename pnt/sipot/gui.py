#######################################################
############### ORG: DataCivica ##################
#######################################################
############### Author: Basem Hamza ##################
#######################################################
#######################################################

import hashlib
import json
import logging
import queue
import time
from PIL import Image
import customtkinter as ctk
import subprocess
import sys
import os
import threading
import pandas as pd
from plyer import notification
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# globaleeees

process = None
output_queue = queue.Queue()
ctk.set_appearance_mode("dark")


obligaciones = []
sujetoObligadoID = ""
organosGarantes = "FED"
idOrganosGarantes = ""
hashFileId = ""
sujeto_list = ["ele"]

# DataFream GoogleSheet
dfObligaciones = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBjluTLuI4mHVeMChWQLse08JXEUBHEhC3a3QdnEmRzTdmWbE1mec9on0NuQAlh6vHYiraYdnNTFCo/pub?gid=666140534&output=csv"
)
dfSujetoObligaciones = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBjluTLuI4mHVeMChWQLse08JXEUBHEhC3a3QdnEmRzTdmWbE1mec9on0NuQAlh6vHYiraYdnNTFCo/pub?gid=1266940376&output=csv"
)
dforganosGarantes = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBjluTLuI4mHVeMChWQLse08JXEUBHEhC3a3QdnEmRzTdmWbE1mec9on0NuQAlh6vHYiraYdnNTFCo/pub?gid=1272473086&output=csv"
)
pattern = r""


def create_hash(str):
    sha256 = hashlib.sha256()
    sha256.update(str.encode("utf-8"))
    return sha256.hexdigest()


def contains_pattern(row):
    return row.str.contains(pattern, regex=True, na=False).any()


if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

script_path = os.path.join(bundle_dir, "obligacion.py")


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


class SelectDropdown(ctk.CTkFrame):

    def __init__(self, master, items, element, sujeto_dropdown, **kwargs):
        super().__init__(master, **kwargs)
        self.element = element
        self.items = items
        self.selected_item = ctk.StringVar()
        self.sujeto_dropdown = sujeto_dropdown
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.dropdown = ctk.CTkComboBox(
            self,
            values=self.items,
            variable=self.selected_item,
            command=self.on_item_selected,
        )
        self.dropdown.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        self.dropdown.focus_set()

    def on_item_selected(self, choice):
        global organosGarantes, sujetoObligadoID, pattern, dfSujetoObligaciones, sujeto_list, idOrganosGarantes
        if self.element == "organosGarantes":

            selected_estado = choice
            filtered_df = dforganosGarantes[
                dforganosGarantes["nombreGrupo"] == selected_estado
            ]
            organosGarantes = filtered_df["code"].to_string(index=False)
            idOrganosGarantes = filtered_df["identificadorGrupo"].to_string(index=False)
            pattern = rf"\({organosGarantes}\)"
            filtered_sujeto_df = dfSujetoObligaciones[
                dfSujetoObligaciones["nombreGrupo"].str.contains(
                    pattern, regex=True, na=False
                )
            ]
            sujeto_list = filtered_sujeto_df["nombreGrupo"].tolist()
            self.sujeto_dropdown.configure(
                values=sujeto_list
            )  # Update the sujeto dropdown
            self.sujeto_dropdown.set("")  # Clear the selection
            print(f"Selected organosGarantes: ({organosGarantes})")


class MultiSelectDropdown(ctk.CTkFrame):

    def __init__(self, master, items, **kwargs):
        super().__init__(master, **kwargs)

        self.items = items
        self.selected_items = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.dropdown_button = ctk.CTkButton(
            self,
            text="Seleccionar obligaciones",
            command=self.toggle_dropdown,
            fg_color="transparent",
            hover_color="#3caa56",
        )
        self.dropdown_button.grid(
            row=0, column=0, columnspan=1, padx=0, pady=0, sticky="nsew"
        )

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, width=300, height=300, label_anchor="w"
        )
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ns")
        self.scrollable_frame.grid_remove()  # Hide initially

        self.checkboxes = []
        for i, item in enumerate(self.items):
            checkbox = ctk.CTkCheckBox(
                self.scrollable_frame,
                text=item,
                command=lambda i=i: self.on_checkbox_click(i),
                hover_color="#a256a5",
            )
            checkbox.grid(row=i, column=0, pady=5, padx=10, sticky="nsew")
            self.checkboxes.append(checkbox)

    def toggle_dropdown(self):

        if self.scrollable_frame.winfo_viewable():
            self.scrollable_frame.grid_remove()
        else:
            self.scrollable_frame.grid()

    def on_checkbox_click(self, index):
        global obligaciones
        if self.checkboxes[index].get():
            self.checkboxes[index].configure(fg_color="#3caa56")
            self.selected_items.append(self.items[index])
            filtered_df = dfObligaciones[
                dfObligaciones["nombreGrupo"].isin(self.selected_items)
            ]
            obligaciones = filtered_df["identificadorGrupo"].tolist()
        else:
            self.checkboxes[index]
            self.selected_items.remove(self.items[index])


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


def send_notification(title, message):
    try:
        notification.notify(title=title, message=message, timeout=10)
    except NotImplementedError as e:
        print(f"Error: {e}")


def run_script():
    def target():
        global process, dfSujetoObligaciones, sujetoObligadoID, hashFileId
        filtered_df = dfSujetoObligaciones[
            dfSujetoObligaciones["nombreGrupo"] == sujeto.get()
        ]
        sujetoObligadoID = filtered_df["identificadorGrupo"].to_string(index=False)
        stringtohash = f"{sujetoObligadoID}".join(obligaciones)
        hashsesion = create_hash(stringtohash)
        send_notification(
            title=":(🫶):",
            message=f"empesando descargar obligaciones del sujeto {sujeto.get()}",
        )
        try:
            hashFileId = hashsesion
            save_state(
                hashsesion,
                sujetoObligadoID,
                idOrganosGarantes,
                ",".join(obligaciones),
                ano.get(),
                finalIndex.get(),
                sujeto.get(),
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
            app.after(100, enable_button)

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
            sujetoObligadoID,
            "--nombreSujeto",
            sujeto.get(),
            "--idEntidadFederativa",
            idOrganosGarantes,
            "--idObligacion",
            ", ".join(obligaciones),
            "--ano",
            ano.get(),
            "--startIndex",
            startIndex.get(),
            "--finalIndex",
            finalIndex.get(),
            "--colaboradora",
            colaboradora.get(),
            "--hashFileId",
            hashFileId,
        ]
    else:
        return [
            "python3",
            script_path,
            "--idSujetoObligado",
            sujetoObligadoID,
            "--nombreSujeto",
            sujeto.get(),
            "--idEntidadFederativa",
            idOrganosGarantes,
            "--idObligacion",
            ",".join(obligaciones),
            "--ano",
            ano.get(),
            "--startIndex",
            startIndex.get(),
            "--finalIndex",
            finalIndex.get(),
            "--colaboradora",
            colaboradora.get(),
            "--hashFileId",
            hashFileId,
        ]


def load_state() -> int:
    global process

    def enable_button():
        run_button.configure(state=ctk.NORMAL)
        resume_button.configure(state=ctk.NORMAL)

    run_button.configure(state=ctk.DISABLED)
    resume_button.configure(state=ctk.DISABLED)
    try:
        sesion_path = []
        with open(f"continuar_proceso.json", "r") as f:
            state = json.load(f)
            sesion_path.append(state["sesion"])
        print(sesion_path)
        with open(f"{''.join(sesion_path)}", "r") as f:
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
            send_notification(
                title="continuar",
                message=f"descargando obligaciones del sujeto {state['nombreSujeto']} ",
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
            state["IDsujeto"],
            "--idEntidadFederativa",
            state["entidad"],
            "--idObligacion",
            state["obligacion"],
            "--ano",
            state["ano"],
            "--finalIndex",
            state["finalIndex"],
            "--nombreSujeto",
            state["nombreSujeto"],
            "--colaboradora",
            state["colaboradora"],
            "--hashFileId",
            state["hashFileId"],
        ]
    else:
        return [
            "python3",
            script_path,
            "--idSujetoObligado",
            state["IDsujeto"],
            "--idEntidadFederativa",
            state["entidad"],
            "--idObligacion",
            state["obligacion"],
            "--ano",
            state["ano"],
            "--finalIndex",
            state["finalIndex"],
            "--nombreSujeto",
            state["nombreSujeto"],
            "--colaboradora",
            state["colaboradora"],
            "--hashFileId",
            state["hashFileId"],
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
    # global process
    # subprocess.Popen(
    #     ["rm", f"{sujeto.get()}_state.json"],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    # )
    state = {"index": 0, "final_index": 10}
    path_file = f"progress.json"
    with open(path_file, "w") as f:
        json.dump(state, f)


def save_state(
    hash, IDsujeto, entidad, Obligacion, ano, finalIndex, nombreSujeto, colaboradora
) -> int:
    state = {
        "hashFileId": hash,
        "IDsujeto": IDsujeto,
        "entidad": entidad,
        "obligacion": Obligacion,
        "ano": ano,
        "finalIndex": finalIndex,
        "nombreSujeto": nombreSujeto,
        "colaboradora": colaboradora,
    }

    with open(f"{hash}.json", "w") as f:
        json.dump(state, f)
        f.close()

    sesion_para_continuar = {"sesion": f"{hash}.json"}
    with open("continuar_proceso.json", "w") as f:
        json.dump(sesion_para_continuar, f)
        f.close()


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


def center_window(app, width, height):
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    app.geometry(f"{width}x{height}+{x}+{y}")


def update_gui():
    app.update_idletasks()
    app.after(100, update_gui)


app = ctk.CTk()
app.title("Respaldo de Obligaciones PNT")


center_window(app, 1300, 750)
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
label.grid(row=3, column=0, pady=10, padx=50, sticky="nsew")

sujeto = ctk.CTkComboBox(app, values=[])
sujeto.grid(row=3, column=1, columnspan=2, pady=10, padx=50, sticky="nsew")
sujeto.set("")
label = ctk.CTkLabel(app, text="Identificador de entidad federal", anchor="w")

label.grid(row=2, column=0, pady=10, padx=50, sticky="nsew")

entidad_list = dforganosGarantes["nombreGrupo"].tolist()
entidad = SelectDropdown(app, entidad_list, "organosGarantes", sujeto)
entidad.grid(row=2, column=1, columnspan=2, pady=3, padx=50, sticky="nsew")

label = ctk.CTkLabel(app, text="Identificador de obligacion", anchor="w")
label.grid(row=4, column=0, pady=10, padx=50, sticky="nsew")

new_dfObligaciones = dfObligaciones.dropna(subset=["default"])
nombres = new_dfObligaciones["nombreGrupo"].tolist()
multi_select_listbox = MultiSelectDropdown(app, nombres)
multi_select_listbox.grid(row=4, column=1, columnspan=2, padx=50, pady=3, sticky="nsew")

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


run_button = ctk.CTkButton(
    app,
    text="Empezar sesión",
    command=run_script,
    fg_color=("#ffffff", "#a256a5"),
    hover_color="#3caa56",
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
run_button.grid(row=9, column=0, columnspan=2, padx=50, pady=20, sticky="nsew")

stop_button = ctk.CTkButton(
    app,
    text="Pausar sesión",
    command=on_closing_button,
    fg_color=("#ffffff", "#a256a5"),
    hover_color="red",
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
stop_button.grid(row=10, column=0, padx=50, pady=20, sticky="nsew")

resume_button = ctk.CTkButton(
    app,
    text="Continuar sesión",
    command=on_session,
    fg_color=("#ffffff", "#a256a5"),
    hover_color="#3caa56",
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
resume_button.grid(row=10, column=1, padx=50, pady=20, sticky="nsew")

progress_bar = ProgressBar(app, json_file_path="progress.json")
progress_bar.grid(row=11, column=0, columnspan=4, pady=20, sticky="nsew")

output_text = ctk.CTkTextbox(app, width=500, height=400)
output_text.grid(
    row=0, column=2, rowspan=12, columnspan=3, padx=50, pady=15, sticky="ew"
)


app.protocol("WM_DELETE_WINDOW", on_closing)

text_handler = TextBoxHandler(output_text)
logging.getLogger().addHandler(text_handler)
log_file = "download_files_PNT.log"
event_handler = LogFileHandler(output_text, log_file)
observer = Observer()
observer.schedule(event_handler, path=".", recursive=False)
observer.start()
app.after(100, update_gui)
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(4, weight=1)
app.mainloop()

observer.stop()
observer.join()
