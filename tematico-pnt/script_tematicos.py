#######################################################
############### ORG: DataCivica ##################
#######################################################
############### Author: Basem Hamza ##################
#######################################################
#######################################################

import asyncio
import hashlib
import json
import logging
import os

import time
from time import sleep

import db_pnt
import nest_asyncio
import pandas as pd
from playwright._impl._errors import Error as PlaywrightError
from playwright._impl._errors import TimeoutError
from playwright.async_api import async_playwright
from getitems import getAnos, getOrgano


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
        anos,
        coleccion,
        organos,
        colaboradora,
    ):
        self.total_pages = 2000
        self.json_data = ""
        self.sort_anos = getAnos(anos)
        self.anos = self.sort_anos
        self.id_ano = [obj.get("id") for obj in self.anos]
        self.organos = getOrgano(organos)
        self.coleccion = coleccion
        self.colaboradora = colaboradora
        self.index = 0
        self.currentAno = None
        self.organos_Garantes_str = (
            ",".join(organos) if len(organos) > 0 else "Todos los organos"
        )
        self.load_state()

    def load_state(self):
        if os.path.exists(f"{self.coleccion.lower()}.json"):
            with open(f"{self.coleccion.lower()}.json", "r") as f:
                state = json.load(f)
                self.currentAno = state.get("ano")
                self.index = state.get("index", 0)

    def generate_hash(self, data):
        """Function to generate SHA-256 hash"""
        sha256 = hashlib.sha256()
        sha256.update(data.encode("utf-8"))
        return sha256.hexdigest()

    def save_state(self):
        state = {"ano": self.currentAno, "index": self.index}
        with open(f"{self.coleccion.lower()}.json", "w") as file:
            json.dump(state, file)

    async def create_json(self, res):

        if (
            f"https://backbuscadortematico.plataformadetransparencia.org.mx/api/tematico/buscador/consulta"
            in res.url
        ):

            json_data = await res.json()
            if json_data is not None:
                pages = json_data["paylod"]["paginador"]["numeroPaginas"]
                ano = json_data["paylod"]["anioFechaInicioSeleccionados"][0][
                    "nombreGrupo"
                ]
                if pages > 0:
                    self.total_pages = pages
                else:
                    self.total_pages = 0
                json_str = json.dumps(json_data)
                json_to_hash = json_data["paylod"]["datosSolr"]
                hash_key = self.generate_hash(f"{json_to_hash}")
                select_query = f"""
                        SELECT hash_key
                        FROM respaldo_tematico
                        WHERE hash_key = '{hash_key}';
                        """
                if hash_key == db_pnt.select_db(select_query):
                    logger_PNT.warning(
                        "estos datos ya estan en la base de datos no se guardaran, solo guardan local"
                    )
                else:
                    data_to_insert = (
                        self.colaboradora,
                        self.coleccion,
                        self.organos_Garantes_str,
                        ano,
                        json_str,
                        hash_key,
                    )
                    db_pnt.insert_db(data_to_insert)

                self.json_data = f"{json_data}"

            return self.json_data

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

        return f"""fetch('https://backbuscadortematico.plataformadetransparencia.org.mx/api/tematico/buscador/consulta', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json',
            'origin': 'backbuscadortematico.plataformadetransparencia.org.mx'
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

    async def makeFetch(self, page, ano):
        self.currentAno = ano.get("id")
        while self.index <= self.total_pages:
            payload = {
                "contenido": "",
                "cantidad": 200,
                "numeroPagina": self.index,
                "coleccion": self.coleccion,
                "dePaginador": True,
                "idCompartido": "",
                "filtroSeleccionado": "",
                "tipoOrdenamiento": "COINCIDENCIA",
                "sujetosObligados": {"seleccion": [], "descartado": []},
                "organosGarantes": {"seleccion": self.organos, "descartado": []},
                "anioFechaInicio": {"seleccion": [ano.get("id")], "descartado": []},
            }
            baby_Fetch = self.generate_json_js_code(payload=payload)

            await page.wait_for_timeout(500)
            await page.evaluate(baby_Fetch)
            print("networkidle")
            logger_PNT.info(
                f"desgargar JSON {self.coleccion} Ano {ano.get("ano")} organos:{self.organos_Garantes_str} index: {self.index} faltan: {self.total_pages - self.index}"
            )
            self.index += 1
            self.save_state()
            if self.index <= self.total_pages:
                self.save_state()

    async def launch_Fetch_requests(
        self,
        url,
        page,
    ):

        try:
            start_ano = 0
            if self.currentAno:
                try:
                    start_ano = self.id_ano.index(self.currentAno)
                    print(start_ano)
                except ValueError:
                    start_ano = 2015

            for i in range(start_ano, len(self.anos)):
                ano = self.anos[i]
                await page.wait_for_timeout(500)
                await self.makeFetch(page=page, ano=ano)
                if self.index >= self.total_pages:
                    self.index = 0
                    self.save_state()
                    continue

            self.currentAno = ano.get("id")
            self.save_state()

            await page.close()
        except TimeoutError:

            logger_PNT.error(f"retry {self.index}")

            await page.wait_for_timeout(5000)
            await self.launch_Fetch_requests(url=url, page=page)
        except Exception:
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
                    url="https://tematicos.plataformadetransparencia.org.mx/tematico/sueldos"
                )
            )

            elapsed_time = time.time() - start_time
            os.remove(f"{self.coleccion}.json")
            return print(f"Fetching took {elapsed_time:.2f} seconds")
        except ConnectionError as e:
            if "ERR_INTERNET_DISCONNECTED" in str(e):
                print(
                    "Unable to connect to the internet. Please check your network connection."
                )
                asyncio.run(
                    self.launch_browser(
                        url="https://tematicos.plataformadetransparencia.org.mx/tematico/sueldos"
                    )
                )

        print(f"Session end .......o_o.........o_o.......o_o........")
        sleep(7)
