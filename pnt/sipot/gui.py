#######################################################
############### ORG: DataCivica ##################
#######################################################
############### Author: Basem Hamza ##################
#######################################################
#######################################################

import hashlib
import json
import logging
import os
import queue
import re
import subprocess
import sys
import threading

import components.select_classes as select_classes
import customtkinter as ctk
import pandas as pd
from PIL import Image
from plyer import notification
from watchdog.observers import Observer

# globaleeees

process = None
output_queue = queue.Queue()
ctk.set_appearance_mode("dark")


obligaciones = []
sujetoObligadoID = ""
organosGarantes = []
sujetos = [""]
idOrganosGarantes = ""
hashFileId = ""
sujeto_list = ["ele"]
nombres_sujetos = ["ele"]

# DataFream GoogleSheet
df_ong = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBjluTLuI4mHVeMChWQLse08JXEUBHEhC3a3QdnEmRzTdmWbE1mec9on0NuQAlh6vHYiraYdnNTFCo/pub?gid=1266940376&output=csv"
)
dfObligaciones = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBjluTLuI4mHVeMChWQLse08JXEUBHEhC3a3QdnEmRzTdmWbE1mec9on0NuQAlh6vHYiraYdnNTFCo/pub?gid=666140534&output=csv"
)
dfSujetoObligaciones = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBjluTLuI4mHVeMChWQLse08JXEUBHEhC3a3QdnEmRzTdmWbE1mec9on0NuQAlh6vHYiraYdnNTFCo/pub?gid=1266940376&output=csv"
)
dforganosGarantes = pd.read_csv(
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBjluTLuI4mHVeMChWQLse08JXEUBHEhC3a3QdnEmRzTdmWbE1mec9on0NuQAlh6vHYiraYdnNTFCo/pub?gid=1272473086&output=csv"
)
filtered_df_organos_sujeto = df_ong
pattern = r""


class MultiSelectDropdownFed(ctk.CTkFrame):

    def __init__(self, master, type, items, df, df2, sujeto_list, ong, **kwargs):
        super().__init__(master, **kwargs)
        self.dfObligaciones = df
        self.ong = ong
        self.df2 = df2
        self.items = items
        self.type = type
        self.selected_items = []
        self.sujeto_list = sujeto_list
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, width=200, height=275, label_anchor="w"
        )
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ns")

        self.checkboxes = []
        self.update_checkboxes()

    def update_checkboxes(self):
        global obligaciones
        for checkbox in self.checkboxes:
            checkbox.destroy()
        self.checkboxes = []
        for i, item in enumerate(self.items):
            checkbox = ctk.CTkCheckBox(
                self.scrollable_frame,
                text=item,
                command=lambda i=i: self.on_checkbox_click(i),
                hover_color="#a256a5",
            )
            checkbox.grid(row=i, column=0, pady=5, padx=10, sticky="ns")
            self.checkboxes.append(checkbox)

    def toggle_dropdown(self):

        if self.scrollable_frame.winfo_viewable():
            self.scrollable_frame.grid_remove()
        else:
            self.scrollable_frame.grid()

    def on_checkbox_click(self, index):
        global organosGarantes
        print(f"from the fed ONG {self.ong.get()}")
        if self.checkboxes[index].get():
            self.checkboxes[index].configure(fg_color="#3caa56")
            self.selected_items.append(self.items[index])
            print(f"from the fed{self.selected_items}")
            organosGarantes = self.selected_items
            nombres_organo = self.dfObligaciones[
                self.dfObligaciones["nombreGrupo"].isin(organosGarantes)
            ]
            code = nombres_organo["code"].tolist()
            print("from the fed" % code)
            filter_name_sujetos_ong = self.df2[self.df2["ong"] == self.ong.get()]
            filter_name_sujetos = filter_name_sujetos_ong[
                filter_name_sujetos_ong["nombreGrupo"].str.contains("|".join(code))
            ]

            nombres_sujeto = filter_name_sujetos["nombreGrupo"].sort_values().tolist()
            self.sujeto_list.items = nombres_sujeto
            sujeto.update_checkboxes()
        else:
            self.checkboxes[index]
            self.selected_items.remove(self.items[index])
            organosGarantes = self.selected_items
            nombres_organo = self.dfObligaciones[
                self.dfObligaciones["nombreGrupo"].isin(organosGarantes)
            ]
            code = nombres_organo["code"].tolist()
            print("from the fed" % code)
            filter_name_sujetos_ong = self.df2[self.df2["ong"] == self.ong.get()]
            filter_name_sujetos = filter_name_sujetos_ong[
                filter_name_sujetos_ong["nombreGrupo"].str.contains("|".join(code))
            ]

            nombres_sujeto = filter_name_sujetos["nombreGrupo"].sort_values().tolist()
            self.sujeto_list.items = nombres_sujeto
            sujeto.update_checkboxes()


class MultiSelectDropdown(ctk.CTkFrame):

    def __init__(self, master, type, items, df, **kwargs):
        super().__init__(master, **kwargs)
        self.dfObligaciones = df
        self.items = items
        self.type = type
        self.selected_items = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, height=275, label_anchor="w"
        )
        if self.type == "sujetos":
            self.scrollable_frame.grid(row=1, column=0, padx=50, pady=5, sticky="e")

        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        self.checkboxes = []
        self.update_checkboxes()

    def update_checkboxes(self):
        global obligaciones
        for checkbox in self.checkboxes:
            checkbox.destroy()
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
            if self.type == "obligaciones":
                self.checkboxes[i].configure(fg_color="#3caa56")
                self.checkboxes[i]._check_state = True
                self.selected_items.append(self.items[i])
                filtered_df = self.dfObligaciones[
                    self.dfObligaciones["nombreGrupo"].isin(self.selected_items)
                ]
                obligaciones = filtered_df["identificadorGrupo"].tolist()

    def toggle_dropdown(self):

        if self.scrollable_frame.winfo_viewable():
            self.scrollable_frame.grid_remove()
        else:
            self.scrollable_frame.grid()

    def on_checkbox_click(self, index):
        global obligaciones, sujetos
        # if self.type == "obligaciones":
        #     # if self.checkboxes[index].get():
        #     self.checkboxes[index].configure(fg_color="#3caa56")
        #     self.selected_items.append(self.items[index])
        #     filtered_df = self.dfObligaciones[
        #         self.dfObligaciones["nombreGrupo"].isin(self.selected_items)
        #     ]
        #     obligaciones = filtered_df["identificadorGrupo"].tolist()
        #     print(obligaciones)
        # else:
        #     self.checkboxes[index]
        #     self.selected_items.remove(self.items[index])
        if self.type == "sujetos":
            if self.checkboxes[index].get():
                self.checkboxes[index].configure(fg_color="#3caa56")
                self.selected_items.append(self.items[index])
                sujetos = self.selected_items
            else:
                self.checkboxes[index]
                self.selected_items.remove(self.items[index])


def create_hash(textToHash: str):
    sha256 = hashlib.sha256()
    sha256.update(textToHash.encode("utf-8"))
    return sha256.hexdigest()


def contains_pattern(row):
    return row.str.contains(pattern, regex=True, na=False).any()


bundle_dir = os.path.dirname(os.path.abspath(__file__))

script_path = os.path.join(bundle_dir, "obligacion.py")


def send_notification(title, message):
    try:
        if notification.notify:
            notification.notify(title=title, message=message, timeout=10)

    except NotImplementedError as e:
        print(f"Error: {e}")


def run_script():
    def target():
        global process, dfSujetoObligaciones, sujetoObligadoID, hashFileId
        filtered_df = dfSujetoObligaciones[
            dfSujetoObligaciones["nombreGrupo"].isin(sujetos)
        ]
        filtered_df_organos = dfSujetoObligaciones[
            dfSujetoObligaciones["nombreGrupo"].isin(sujetos)
        ]
        sujetoObligadoID = filtered_df["identificadorGrupo"].tolist()
        stringtohash = f"{sujetoObligadoID}".join(obligaciones)
        hashsesion = create_hash(stringtohash)
        send_notification(
            title=":(🫶):",
            message=f"empesando descargar obligaciones ",
        )
        try:
            hashFileId = hashsesion
            print(hashFileId)
            save_state(
                hashsesion,
                sujetoObligadoID,
                ",".join(obligaciones),
                ano_de_empezar.get(),
                ano_de_terminal.get(),
                sujetos,
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
            if process.stdout and process.stderr:
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
    return [
        "python3" if sys.platform != "win32" else "python",
        script_path,
        "--idSujetoObligado",
        ",".join(sujetoObligadoID),
        "--nombreSujeto",
        "|".join(sorted(sujetos)),
        "--idObligacion",
        ",".join(obligaciones),
        "--ano_de_empezar",
        ano_de_empezar.get(),
        "--ano_de_terminal",
        ano_de_terminal.get(),
        "--colaboradora",
        colaboradora.get(),
        "--hashFileId",
        hashFileId,
    ]


def load_state():
    global process

    def enable_button():
        run_button.configure(state=ctk.NORMAL)
        resume_button.configure(state=ctk.NORMAL)

    run_button.configure(state=ctk.DISABLED)
    resume_button.configure(state=ctk.DISABLED)
    try:
        sesion_path = []
        with open("continuar_proceso.json", "r", encoding="utf-8") as f:
            state = json.load(f)
            sesion_path.append(state["sesion"])
        print(sesion_path)
        with open(f"{''.join(sesion_path)}", "r", encoding="utf-8") as f:
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
            if process.stdout and process.stderr:
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


def build_command_from_state(state):

    return [
        "python3" if sys.platform != "win32" else "python",
        script_path,
        "--idSujetoObligado",
        ",".join(state["IDsujeto"]),
        "--idObligacion",
        state["obligacion"],
        "--ano_de_empezar",
        state["ano_de_empezar"],
        "--ano_de_terminal",
        state["ano_de_terminal"],
        "--nombreSujeto",
        "|".join(state["nombreSujeto"]),
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


def save_state(
    hash,
    IDsujeto,
    Obligacion,
    ano_de_empezar,
    ano_de_terminal,
    nombreSujeto,
    colaboradora,
):
    state = {
        "hashFileId": hash,
        "IDsujeto": IDsujeto,
        "obligacion": Obligacion,
        "ano_de_empezar": ano_de_empezar,
        "ano_de_terminal": ano_de_terminal,
        "nombreSujeto": nombreSujeto,
        "colaboradora": colaboradora,
    }

    with open(f"{hash}.json", "w", encoding="utf-8") as f:
        json.dump(state, f)
        f.close()

    sesion_para_continuar = {"sesion": f"{hash}.json"}
    with open("continuar_proceso.json", "w", encoding="utf-8") as f:
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


ong = ""


def update_dropdown(*args):
    global filtered_df_organos_sujeto, ong
    ong_name = colaboradora.get()

    ong_name = ong_name.lower()
    ong = ong_name
    filtered_df = df_ong[df_ong["ong"] == f"{ong_name}"]
    filtered_df_organos_sujeto = filtered_df
    nombres_sujeto = filtered_df["nombreGrupo"].sort_values().tolist()

    sujeto.items = nombres_sujeto
    pattern = re.compile(r"\((\w{2,4})\)$")

    # Extract matches
    matches = [
        match.group(1)
        for string in nombres_sujeto
        for match in pattern.finditer(string)
    ]
    print(matches, flush=True)
    uinque_matches = list(matches)
    filtered_df_organos = dforganosGarantes[
        dforganosGarantes["code"].isin(uinque_matches)
    ]
    nombres_organo = filtered_df_organos["nombreGrupo"].tolist()
    entidad.items = nombres_organo
    print(f"Filtered items: {nombres_organo}")

    print(f"Filtered items: {nombres_sujeto}")
    sujeto.update_checkboxes()
    entidad.update_checkboxes()


app = ctk.CTk()
app.title("Respaldo de Obligaciones PNT")


center_window(app, 1300, 800)
# logo_path = os.path.join(bundle_dir, "logo.png")
# image = ctk.CTkImage(Image.open(logo_path), size=(50, 50))
# image_label = ctk.CTkLabel(app, image=image, text="")
# image_label.grid(row=0, column=0, columnspan=3, pady=10)

label = ctk.CTkLabel(app, text="Colaboradora (ONG)", anchor="e")
label.grid(row=0, column=0, pady=10, padx=50, sticky="nsew")
colaboradora = ctk.CTkEntry(
    app, width=300, border_color="#a256a5", placeholder_text="nombre de la orgnicacion"
)
colaboradora.grid(row=0, column=1, pady=10, padx=50, sticky="ew")
colaboradora_var = ctk.StringVar()
colaboradora.configure(textvariable=colaboradora_var)
colaboradora_var.trace_add("write", update_dropdown)

nombres_sujeto = [
    "Elegí primero al colaborador para ver el listado de\n(**sujetos obligado**)"
]
sujeto = MultiSelectDropdown(app, "sujetos", nombres_sujeto, filtered_df_organos_sujeto)
sujeto.grid(row=3, column=0, columnspan=2, pady=0, padx=40, sticky="nsew")
nombres_organo = [
    "Elegí primero\nal colaborador\npara ver el listado de\n(**entidad federativa**)"
]
entidad = MultiSelectDropdownFed(
    app,
    "organosGarantes",
    nombres_organo,
    dforganosGarantes,
    filtered_df_organos_sujeto,
    sujeto_list=sujeto,
    ong=colaboradora,
)
entidad.grid(row=1, column=0, pady=3, padx=40, sticky="nsw")

new_dfObligaciones = dfObligaciones.dropna(subset=["default"])
nombres = new_dfObligaciones["nombreGrupo"].tolist()
multi_select_listbox = MultiSelectDropdown(app, "obligaciones", nombres, dfObligaciones)
multi_select_listbox.grid(row=1, column=1, padx=1, pady=3, sticky="nsew")

# label = ctk.CTkLabel(app, text="Año", anchor="w")
# label.grid(row=5, column=0, pady=10, padx=50, sticky="nsew")
ano_de_empezar = ctk.CTkEntry(
    app, width=300, border_color="#a256a5", placeholder_text="desde el Año ej: 2015"
)
ano_de_empezar.grid(row=5, column=0, pady=3, padx=50, sticky="nsew")

ano_de_terminal = ctk.CTkEntry(
    app, width=300, border_color="#a256a5", placeholder_text="hasta el Año ej: 2024"
)
ano_de_terminal.grid(row=5, column=1, padx=50, pady=3, sticky="nsew")

output_text = ctk.CTkTextbox(app, width=500, height=300)
output_text.grid(
    row=1, column=2, rowspan=2, columnspan=3, padx=50, pady=5, sticky="nsew"
)
progress_bar = select_classes.ProgressBar(app, json_file_path="progress.json")
progress_bar.grid(row=3, column=2, columnspan=3, padx=20, pady=10, sticky="sew")

run_button = ctk.CTkButton(
    app,
    text="Empezar sesión",
    command=run_script,
    fg_color=("#ffffff", "#a256a5"),
    hover_color="#3caa56",
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
run_button.grid(row=4, column=2, columnspan=3, padx=20, pady=5, sticky="ew")

stop_button = ctk.CTkButton(
    app,
    text="Pausar sesión",
    command=on_closing_button,
    fg_color=("#ffffff", "#a256a5"),
    hover_color="red",
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
stop_button.grid(row=5, column=2, padx=20, pady=10, sticky="ew")

resume_button = ctk.CTkButton(
    app,
    text="Continuar sesión",
    command=on_session,
    fg_color=("#ffffff", "#a256a5"),
    hover_color="#3caa56",
    text_color_disabled="#DCDCDC",
    corner_radius=5,
)
resume_button.grid(row=5, column=3, columnspan=2, padx=20, pady=10, sticky="ew")


app.protocol("WM_DELETE_WINDOW", on_closing)

text_handler = select_classes.TextBoxHandler(output_text)
logging.getLogger().addHandler(text_handler)
LOG_FILE = "download_files_PNT.log"
event_handler = select_classes.LogFileHandler(output_text, LOG_FILE)
observer = Observer()
observer.schedule(event_handler, path=".", recursive=False)
observer.start()
app.after(100, update_gui)
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(4, weight=1)
app.mainloop()

observer.stop()
observer.join()
