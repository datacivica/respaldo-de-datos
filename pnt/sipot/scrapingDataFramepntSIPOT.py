#######################################################
############### ORG: DataCivica ##################
#######################################################
############### Author: Basem Hamza ##################
#######################################################
#######################################################

import asyncio

# from datetime import datetime
import hashlib
import json
import logging
import os
import random

# import subprocess
import sys
import time
from time import sleep

import aiofiles as aiof
import db_pnt
import nest_asyncio
import pandas as pd
from playwright._impl._errors import Error as PlaywrightError
from playwright._impl._errors import TimeoutError
from playwright.async_api import async_playwright
from plyer import notification

# import psycopg2
# from psycopg2 import sql
# from dotenv import load_dotenv


#######################################################
############### logging basic Config ##################
#######################################################
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# download files logs
logger_PNT = logging.getLogger("download_files_PNT_logger")
file_download_handler = logging.FileHandler("download_files_PNT.log")
file_download_handler.setLevel(logging.INFO)
file_download_handler.setFormatter(formatter)
logger_PNT.addHandler(file_download_handler)

#######################################################
#######################################################
############ ... async fetch PNT ...###############
#######################################################
#######################################################
nest_asyncio.apply()
listObligacion = []


class ScrapingDataFramePnt:
    def __init__(
        self,
        id_sujeto_obligado,
        nombre_del_sujeto,
        ano_de_empezar,
        ano_de_terminal,
        obligacion,
        colaboradora,
        hash_file_id,
    ):
        self.total_pages = self.load_state_progress()
        self.json_data = ""
        self.id_sujeto_obligado = id_sujeto_obligado.split(",")
        self.nombre_del_sujeto = nombre_del_sujeto
        self.id_obligacion_optional = obligacion
        self.hash_file_id = hash_file_id
        self.id_obligacion = []

        if self.id_obligacion_optional:
            list_obligacion_optional = self.id_obligacion_optional.split(",")
            self.id_obligacion.extend(list_obligacion_optional)
        else:
            self.id_obligacion = []

        self.index = 0
        self.search_size = 100
        self.ano_de_empezar = ano_de_empezar
        self.ano_de_terminal = ano_de_terminal
        self.colaboradora = colaboradora
        self.registros_sujeto = None
        self.load_state()

    def send_notification(self, title, message):
        """Function to make notification"""
        try:
            if notification.notify:
                notification.notify(title=title, message=message, timeout=5)

        except NotImplementedError as e:
            print(f"Error: {e}")

    def generate_hash(self, data):
        """Function to generate SHA-256 hash"""
        sha256 = hashlib.sha256()
        sha256.update(data.encode("utf-8"))
        return sha256.hexdigest()

    def load_state(self):
        if os.path.exists(f"{self.hash_file_id}_state.json"):
            with open(f"{self.hash_file_id}_state.json", "r") as file:
                state = json.load(file)
                self.registros_sujeto = state.get("registros_sujeto")
                self.index = state.get("index", 0)

    def save_state(self):
        state = {"registros_sujeto": self.registros_sujeto, "index": self.index}
        with open(f"{self.hash_file_id}_state.json", "w") as file:
            json.dump(state, file)

    def load_state_progress(self):
        """Load state_progress state from .json file"""
        try:
            path_file = f"progress.json"
            with open(path_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state["final_index"]
        except FileNotFoundError:
            return 1

    def save_state_progress(self):
        """Save"""
        state = {"index": self.index, "final_index": self.total_pages}
        path_file = "progress.json"
        with open(path_file, "w", encoding="utf-8") as f:
            json.dump(state, f)

    #  create json file from response
    async def create_json(self, res):
        if (
            f"https://backbuscadorinteligente.plataformadetransparencia.org.mx/api/buscadorinteligente/buscador/consulta"
            not in res.url
        ):
            return

        if "consultaTotal" in res.url:
            return

        json_data = await res.json()

        if json_data is None:
            return ""

        sujetos_obligados = json_data.get("paylod", {}).get(
            "sujetosObligadosSeleccionados"
        )

        if sujetos_obligados:
            self.nombre_del_sujeto = sujetos_obligados[0].get("nombreGrupo")
        else:
            self.send_notification(
                title="Advertencia",
                message="No se encontraron obligados para sujetos",
            )

        obligacionesTransparencia = json_data["paylod"][
            "obligacionesTransparenciaSeleccionados"
        ]
        obligacionesTransparencia_list = [
            item["nombreGrupo"] for item in obligacionesTransparencia
        ]
        total_page_from_json = json_data["paylod"]["paginador"][
            "numeroPaginas"
        ]
        self.total_pages = (
            int(total_page_from_json) if total_page_from_json else 0
        )
        if not os.path.exists(f"output_PNT_SIPOT/{self.nombre_del_sujeto}"):
            os.mkdir(f"output_PNT_SIPOT/{self.nombre_del_sujeto}")
        if not os.path.exists(
            f"output_PNT_SIPOT/{self.nombre_del_sujeto}/{self.ano_de_empezar}_{self.ano_de_terminal}"
        ):
            os.mkdir(
                f"output_PNT_SIPOT/{self.nombre_del_sujeto}/{self.ano_de_empezar}_{self.ano_de_terminal}"
            )

        if not os.path.exists(
            f"output_PNT_SIPOT/{self.nombre_del_sujeto}/{self.ano_de_empezar}_{self.ano_de_terminal}/obligaciones_de_transparencia"
        ):
            os.mkdir(
                f"output_PNT_SIPOT/{self.nombre_del_sujeto}/{self.ano_de_empezar}_{self.ano_de_terminal}/obligaciones_de_transparencia"
            )
        if not os.path.exists(
            f"output_PNT_SIPOT/{self.nombre_del_sujeto}/{self.ano_de_empezar}_{self.ano_de_terminal}/obligaciones_de_transparencia/{self.hash_file_id}"
        ):
            os.mkdir(
                f"output_PNT_SIPOT/{self.nombre_del_sujeto}/{self.ano_de_empezar}_{self.ano_de_terminal}/obligaciones_de_transparencia/{self.hash_file_id}"
            )

        filename = f"output_PNT_SIPOT/{self.nombre_del_sujeto}/{self.ano_de_empezar}_{self.ano_de_terminal}/obligaciones_de_transparencia/{self.hash_file_id}/{self.nombre_del_sujeto.replace(' ', '_')}_{self.index}_.json"
        json_str = json.dumps(json_data)
        json_to_hash = json_data["paylod"]["resultado"]["informacion"]
        hash_key = self.generate_hash(f"{json_to_hash}")
        select_query = f"""
            SELECT hash_key
            FROM progresos_respaldo
            WHERE hash_key = '{hash_key}';
            """
        if hash_key == db_pnt.select_db(select_query):
            self.send_notification(
                title="Advertencia",
                message="estos datos ya estan en la base de datos no se guardaran, solo guardan local",
            )
            # return
        else:
            data_to_insert = (
                self.colaboradora,
                self.registros_sujeto,
                self.nombre_del_sujeto,
                self.id_obligacion,
                "|".join(obligacionesTransparencia_list),
                self.index,
                json_str,
                hash_key,
            )
            db_pnt.insert_db(data_to_insert)
        async with aiof.open(filename, "w") as out:
            await out.write(json_str)
            await out.flush()
            await out.close()

        self.json_data = f"{json_data}"

        return self.json_data

    #  generate json for Convert Python booleans to JavaScript booleans
    def generate_json_js_code(self, payload):
        def convert_booleans(obj):
            if isinstance(obj, bool):
                return "true" if obj else "false"
            elif isinstance(obj, dict):
                return {k: convert_booleans(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_booleans(item) for item in obj]
            else:
                return obj

        converted_payload = convert_booleans(payload)

        return f"""fetch('https://backbuscadorinteligente.plataformadetransparencia.org.mx/api/buscadorinteligente/buscador/consulta', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json',
            'origin': 'buscador.plataformadetransparencia.org.mx'
        }},
        body: JSON.stringify({converted_payload}) // Your JSON payload
        }})
        .then(response => response.json())
        .then(data => {{
        console.log('Success:', data);
        }})
        .catch(error => {{
        console.error('Error:', error);
        }});"""

    async def makeFetch(self, page, sujeto):
        global sujetoUniqo
        self.registros_sujeto = sujeto
        # self.save_state_sujeto()
        # self.load_state_sujeto()
        while self.index <= self.total_pages:
            payload = {
                "contenido": "20*",
                "idCompartido": "",
                "comboEncabezado": False,
                "numeroPagina": self.index,
                "temas": {"seleccion": [], "descartado": []},
                "cantidad": self.search_size,
                "dePaginador": True,
                "folio": "",
                "expediente": "",
                "detalleBusqueda": "",
                "filtroSeleccionado": "",
                "tipoOrdenamiento": 1,
                "coleccion": "SIPOT",
                "sujetosObligados": {
                    "seleccion": [self.registros_sujeto],
                    "descartado": [],
                },
                "organosGarantes": {
                    "seleccion": [],
                    "descartado": [],
                },
                "subtemas": {"seleccion": [], "descartado": []},
                "fechaResolucion": {
                    "fechaInicial": "",
                    "fechaFinal": "",
                    "cantidad": 0,
                },
                "fechaResolucionSeleccionado": {
                    "fechaInicial": "",
                    "fechaFinal": "",
                    "cantidad": 0,
                },
                "fechaRecepcion": {
                    "fechaInicial": "",
                    "fechaFinal": "",
                    "cantidad": 0,
                },
                "fechaRecepcionSeleccionado": {"seleccion": [], "descartado": []},
                "fechaInicio": {
                    "fechaInicial": f"01/01/{self.ano_de_empezar} 00:00",
                    "fechaFinal": f"31/12/{self.ano_de_terminal} 23:59",
                },
                "fechaInicioSeleccionado": {
                    "fechaInicial": "",
                    "fechaFinal": "",
                    "cantidad": 0,
                },
                "fechaInterposicion": {
                    "fechaInicial": "",
                    "fechaFinal": "",
                    "cantidad": 0,
                },
                "fechaInterposicionSeleccionado": {
                    "fechaInicial": "",
                    "fechaFinal": "",
                    "cantidad": 0,
                },
                "anioQueja": {"seleccion": [], "descartado": []},
                "sentidoResolucion": {"seleccion": [], "descartado": []},
                "obligacionesTransparencia": {
                    "seleccion": self.id_obligacion,
                    "descartado": [],
                },
                "obligacionesTransparenciaLocales": {
                    "seleccion": [],
                    "descartado": [],
                },
                "anioSolicitud": {"seleccion": [], "descartado": []},
                "tipoRespuesta": {"seleccion": [], "descartado": []},
            }
            baby_Fetch = self.generate_json_js_code(payload=payload)
            await page.wait_for_timeout(500)
            await page.evaluate(baby_Fetch)
            await page.wait_for_load_state("networkidle", timeout=60**3)
            await page.wait_for_timeout(700)
            logger_PNT.info(
                f"desgargar JSON for {self.nombre_del_sujeto}\n index: {self.index} faltan: {self.total_pages - self.index}"
            )
            print(
                f"desgargar JSON for {self.nombre_del_sujeto} index: {self.index} faltan: {self.total_pages - self.index}"
            )
            sys.stdout.flush()
            self.index += 1
            if self.index <= self.total_pages:
                self.save_state_progress()
                self.save_state()

    async def launch_Fetch_requests(
        self,
        url,
        page,
    ):
        try:
            start_index = 0
            if self.registros_sujeto:
                try:
                    start_index = self.id_sujeto_obligado.index(self.registros_sujeto)
                except ValueError:
                    start_index = 0

            for i in range(start_index, len(self.id_sujeto_obligado)):
                sujeto = self.id_sujeto_obligado[i]
                await self.makeFetch(page=page, sujeto=sujeto)

                if self.index > self.total_pages:
                    self.index = 0
                    self.save_state()

                self.registros_sujeto = sujeto
                self.save_state()

            await page.close()
            self.send_notification(
                title="Terminaste descargar",
                message="felicidades terminaste descargar este sesion elige otros opiciones en el app para empezar de nuevo",
            )
        except TimeoutError:

            logger_PNT.error(f"retry {self.index}")

            await page.wait_for_timeout(5000)
            await self.launch_Fetch_requests(url=url, page=page)
        except Exception:
            self.send_notification(
                title="advertencia",
                message=f"hay problema en servidor de PNT pagina {self.index} re intanto de nuevo ",
            )
            logger_PNT.warning(
                f" retry {self.index} ---Exception Error Page.evaluate makeFetch()"
            )
            await page.wait_for_timeout(5000)
            await self.launch_Fetch_requests(url=url, page=page)

    async def handle_load(self):
        if self.index > 1:
            self.index -= 2
            self.save_state()

    # Function for starting the browser
    async def launch_browser(self, url):

        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    headless=False,
                    timeout=10**6,
                )
                context = await browser.new_context(
                    viewport={"width": 1440, "height": 900}
                )
                page = await context.new_page()

                async def handle_response(res):
                    datajson = await self.create_json(res=res)
                    return datajson

                page.on("load", await self.handle_load())  # type: ignore
                page.on(
                    "response",
                    lambda res: asyncio.ensure_future(handle_response(res=res)),  # type: ignore
                )

                await page.goto(url, timeout=0, wait_until="load")
                await page.wait_for_timeout(3500)
                return await self.launch_Fetch_requests(
                    url=url,
                    page=page,
                )

            except PlaywrightError:
                self.send_notification(
                    title="PlaywrightError",
                    message="La pestaña o navegador web se cerró",
                )
                logger_PNT.error(
                    f" stop {self.index} ---PlaywrightError Error page was closed"
                )

    def main(self) -> None:
        #######################################################
        #######################################################
        logging.basicConfig(level=logging.INFO)

        if not os.path.exists(f"output_PNT_SIPOT"):
            os.mkdir(f"output_PNT_SIPOT")
        db_pnt.create_db()
        try:
            start_time = time.time()
            asyncio.run(
                self.launch_browser(
                    url="https://buscador.plataformadetransparencia.org.mx/buscador/temas"
                )
            )

            elapsed_time = time.time() - start_time
            return print(f"Fetching took {elapsed_time:.2f} seconds")
        except ConnectionError as e:
            if "ERR_INTERNET_DISCONNECTED" in str(e):
                print(
                    "Unable to connect to the internet. Please check your network connection."
                )
                self.send_notification(
                    title="ERR_INTERNET_DISCONNECTED",
                    message="Unable to connect to the internet. Please check your network connection.",
                )
                asyncio.run(
                    self.launch_browser(
                        url="https://buscador.plataformadetransparencia.org.mx/buscador/temas"
                    )
                )

        print(f"Session end .......o_o.........o_o.......o_o........")
        self.send_notification(
            title="Terminaste descargar",
            message="felicidades terminaste descargar este sesion elige otros opiciones en el app para empezar de nuevo",
        )
        sleep(7)
