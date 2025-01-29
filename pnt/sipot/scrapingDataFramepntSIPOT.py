#######################################################
############### ORG: DataCivica ##################
#######################################################
############### Author: Basem Hamza ##################
#######################################################
#######################################################

# from datetime import datetime
import hashlib
import json
import logging

# import subprocess
import sys
from time import sleep
import time
import pandas as pd
import asyncio
import db_pnt
import nest_asyncio
from playwright.async_api import async_playwright
import os
import random
from playwright._impl._errors import Error as PlaywrightError
from playwright._impl._errors import TimeoutError
from playwright._impl._errors import Error as PlaywrightError
import aiofiles as aiof

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
listObligacion = list()


class ScrapingDataFramePnt:
    def __init__(
        self,
        idSujetoObligado,
        endidad,
        ano,
        obligacion,
        index,
        finalIndex,
        colaboradora,
    ):
        self.finalIndex = None
        if finalIndex and finalIndex.isdigit():
            self.finalIndex = int(finalIndex)
        self.total_pages = 100000 if self.finalIndex is None else self.finalIndex
        self.jsonData = ""
        self.idSujetoObligado = idSujetoObligado
        self.idObligcaionOptional = obligacion
        self.idObligcaion = list()
        if self.idObligcaionOptional:
            listObligacionOptional = self.idObligcaionOptional.split(",")
            # if type(listObligacionOptional) == list:
            #     for Obliga in listObligacionOptional:
            #         self.idObligcaion.extend(Obliga)
            self.idObligcaion.extend(listObligacionOptional)
        else:
            self.idObligcaion = []

        self.index = self.load_state()
        if index and index.isdigit():
            index = int(index)
            if index > self.index:
                self.index = index
        self.search_size = 100
        self.endidad = endidad
        self.ano = ano
        self.colaboradora = colaboradora

    # Function to generate SHA-256 hash
    def generate_hash(self, data):
        encoded_data = data.encode("utf-8")
        hash_object = hashlib.sha256()
        hash_object.update(encoded_data)
        hash_hex = hash_object.hexdigest()
        return hash_hex

    def load_state(self) -> int:
        try:
            path_file = f"{self.idSujetoObligado}_state.json"
            with open(path_file, "r") as f:
                state = json.load(f)
                return state["index"]
        except FileNotFoundError:
            return 0

    #  save index page
    def save_state(self) -> int:
        state = {"index": self.index}
        path_file = f"{self.idSujetoObligado}_state.json"
        with open(path_file, "w") as f:
            json.dump(state, f)

    #  create json file from response
    async def create_json(self, res):
        if not os.path.exists(f"output_PNT_SIPOT/{self.idSujetoObligado}"):
            os.mkdir(f"output_PNT_SIPOT/{self.idSujetoObligado}")
            os.mkdir(f"output_PNT_SIPOT/{self.idSujetoObligado}/{self.ano}")
        if (
            f"https://backbuscadorinteligente.plataformadetransparencia.org.mx/api/buscadorinteligente/buscador/consulta"
            in res.url
        ):
            if "consultaTotal" not in res.url:
                json_data = await res.json()
                if json_data is not None:
                    self.idSujetoNombre = json_data["paylod"][
                        "sujetosObligadosSeleccionados"
                    ][0]["nombreGrupo"]
                    organosGarantes = json_data["paylod"][
                        "organosGarantesSeleccionados"
                    ][0]["nombreGrupo"]
                    obligacionesTransparencia = json_data["paylod"][
                        "obligacionesTransparenciaSeleccionados"
                    ][0]["nombreGrupo"]
                    total_page_from_json = json_data["paylod"]["paginador"][
                        "numeroPaginas"
                    ]
                    self.total_pages = (
                        total_page_from_json
                        if self.finalIndex is None
                        or total_page_from_json < self.finalIndex
                        else self.finalIndex
                    )
                    if self.index > json_data["paylod"]["paginador"]["numeroPaginas"]:
                        sys.exit(
                            """
                            termiaste la descarga para este sujeto obligado y para este obligacion 
                            por favor cambia el index si estan descargando mismas obligacion o 
                            connecta con el groupo de resplado ticnico para mas informacion
                            """
                        )
                if not os.path.exists(
                    f"output_PNT_SIPOT/{self.idSujetoObligado}/{self.ano}/{obligacionesTransparencia.replace(' ', '_') }"
                ):
                    os.mkdir(
                        f"output_PNT_SIPOT/{self.idSujetoObligado}/{self.ano}/{obligacionesTransparencia.replace(' ', '_') }"
                    )
                filename = f"output_PNT_SIPOT/{self.idSujetoObligado}/{self.ano}/{obligacionesTransparencia.replace(' ', '_')}/{self.idSujetoNombre.replace(' ', '_')}_{self.index}_.json"
                json_str = json.dumps(json_data)
                json_to_hash = json_data["paylod"]["resultado"]["informacion"]
                select_query = f"""
                    SELECT hash_key
                    FROM progresos_respaldo
                    WHERE identificador_sujetosobligados = '{self.idSujetoObligado}' AND index_actual = {self.index};
                    """
                hash_key = self.generate_hash(f"{json_to_hash}")
                if hash_key == db_pnt.select_db(select_query):
                    sys.exit(
                        """
                            estos datos ya estan en la base de datos no se guardaran
                            revisa la google sheet para mas informacion 
                            o 
                            connecta con el groupo de resplado ticnico para mas informacion
                             
                        """
                    )
                    return
                else:

                    async with aiof.open(filename, "w") as out:
                        await out.write(json_str)
                        await out.flush()
                        data_to_insert = (
                            self.colaboradora,
                            self.idSujetoObligado,
                            self.idSujetoNombre,
                            self.endidad,
                            organosGarantes,
                            self.idObligcaion,
                            obligacionesTransparencia,
                            self.index,
                            self.total_pages,
                            json_str,
                            hash_key,
                        )
                        db_pnt.insert_db(data_to_insert)

                    self.index += 1

                self.jsonData = f"{json_data}"

                self.save_state()
                return self.jsonData

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

    async def makeAjax(self, page):

        for self.index in range(self.index, self.total_pages):
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
                    "seleccion": [self.idSujetoObligado],
                    "descartado": [],
                },
                "organosGarantes": {
                    "seleccion": [self.endidad],
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
                    "fechaInicial": f"01/01/{self.ano} 00:00",
                    "fechaFinal": f"31/12/{self.ano} 00:00",
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
                    "seleccion": self.idObligcaion,
                    "descartado": [],
                },
                "obligacionesTransparenciaLocales": {
                    "seleccion": [],
                    "descartado": [],
                },
                "anioSolicitud": {"seleccion": [], "descartado": []},
                "tipoRespuesta": {"seleccion": [], "descartado": []},
            }
            baby_ajax = self.generate_json_js_code(payload=payload)
            await page.wait_for_timeout(500)
            await page.evaluate(baby_ajax)
            await page.wait_for_load_state("networkidle", timeout=60**3)
            await page.wait_for_timeout(700)
            logger_PNT.info(
                f"desgargar JSON for {self.idSujetoNombre}\n index: {self.index} faltan: {self.total_pages - self.index}"
            )
            print(
                f"desgargar JSON for {self.idSujetoNombre} index: {self.index} faltan: {self.total_pages - self.index}"
            )
            sys.stdout.flush()

    async def launch_Ajax_requests(
        self,
        url,
        page,
    ) -> pd.DataFrame:

        try:
            sleep(1)
            await self.makeAjax(page=page)
            await page.pause()
        except TimeoutError:

            logger_PNT.error(f"retry {self.index}")

            await page.wait_for_timeout(5000)
            await self.launch_Ajax_requests(url=url, page=page)
        except Exception:
            logger_PNT.error(
                f" retry {self.index} ---Exception Error Page.evaluate makeAjax()"
            )
            await page.wait_for_timeout(5000)
            await self.launch_Ajax_requests(url=url, page=page)

    # Function for starting the browser
    async def launch_browser(self, url) -> pd.DataFrame:

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

                page.on(
                    "response",
                    lambda res: asyncio.ensure_future(handle_response(res=res)),
                )
                await page.goto(url, timeout=0, wait_until="load")
                await page.wait_for_timeout(3500)
                return await self.launch_Ajax_requests(
                    url=url,
                    page=page,
                )

            except PlaywrightError:
                logger_PNT.error(
                    f" stop {self.index} ---PlaywrightError Error page was closed"
                )
                return self.launch_Ajax_requests(
                    url=url,
                    page=page,
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
                attempt += 1
                logger_PNT.warning(f"Error (attempt {attempt}): {e}")
                sleep_time = 720 * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                print(f"Retrying  in {sleep_time:.2f} seconds...")
                sleep(sleep_time)
                asyncio.run(
                    self.fetch_batch_urls(
                        url="https://buscador.plataformadetransparencia.org.mx/buscador/temas"
                    )
                )
        print(f"Session end .......o_o.........o_o.......o_o........")
        sleep(7)
